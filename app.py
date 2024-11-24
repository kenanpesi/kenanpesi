from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')

# PostgreSQL bağlantısı URL'ini ayarla
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    access_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class SystemInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100))
    os = db.Column(db.String(100))
    cpu_percent = db.Column(db.Float)
    memory_percent = db.Column(db.Float)
    disk_usage = db.Column(db.Float)
    ip_address = db.Column(db.String(50))
    last_update = db.Column(db.DateTime, default=datetime.datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Veritabanı tablolarını oluştur
def init_db():
    with app.app_context():
        db.create_all()
        # Admin kullanıcısını kontrol et ve oluştur
        admin_username = os.environ.get('ADMIN_USERNAME', "muradsayagi")
        admin = User.query.filter_by(username=admin_username).first()
        if not admin:
            admin = User(
                username=admin_username,
                password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', "eldos"))
            )
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f"Admin kullanıcısı oluşturuldu: {admin_username}")

# Uygulama başladığında veritabanını başlat
init_db()

# Sabit admin kullanıcı bilgileri
ADMIN_USERNAME = "muradsayagi"  # Railway'de environment variable olarak ayarlayın
ADMIN_PASSWORD = "eldos"  # Railway'de environment variable olarak ayarlayın

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            app.logger.info(f"Giriş denemesi: {username}")
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                
                # Erişim logunu kaydet
                try:
                    log = AccessLog(ip_address=request.remote_addr, user_id=user.id)
                    db.session.add(log)
                    db.session.commit()
                    app.logger.info(f"Başarılı giriş: {username} from {request.remote_addr}")
                except Exception as e:
                    app.logger.error(f"Log kayıt hatası: {str(e)}")
                
                return redirect(url_for('dashboard'))
            
            app.logger.warning(f"Başarısız giriş denemesi: {username}")
            flash('Kullanıcı adı veya şifre hatalı!')
        return render_template('login.html')
    except Exception as e:
        app.logger.error(f"Login hatası: {str(e)}")
        return f"Giriş işlemi sırasında hata: {str(e)}", 500

@app.route('/update_system_info', methods=['POST'])
@login_required
def update_system_info():
    try:
        data = request.get_json()
        system_info = SystemInfo(
            hostname=data.get('hostname'),
            os=data.get('os'),
            cpu_percent=data.get('cpu_percent'),
            memory_percent=data.get('memory_percent'),
            disk_usage=data.get('disk_usage'),
            ip_address=data.get('ip_address'),
            last_update=datetime.datetime.strptime(data.get('last_update'), '%Y-%m-%d %H:%M:%S')
        )
        db.session.add(system_info)
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        app.logger.error(f"Sistem bilgisi güncellenirken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Son erişimleri getir
        access_logs = AccessLog.query.filter_by(user_id=current_user.id).order_by(AccessLog.access_time.desc()).limit(10)
        
        # Son sistem bilgisini getir
        system_info = SystemInfo.query.order_by(SystemInfo.last_update.desc()).first()
        
        return render_template('dashboard.html', 
                             access_logs=access_logs,
                             system_info=system_info)
    except Exception as e:
        app.logger.error(f"Dashboard hatası: {str(e)}")
        return f"Bir hata oluştu: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
