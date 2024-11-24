from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-buraya')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Veritabanı tablolarını oluştur
with app.app_context():
    db.create_all()

# Sabit admin kullanıcı bilgileri
ADMIN_USERNAME = "muradsayagi"  # Railway'de environment variable olarak ayarlayın
ADMIN_PASSWORD = "eldos"  # Railway'de environment variable olarak ayarlayın

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    access_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
            
            # Admin kullanıcı kontrolü
            if username == os.environ.get('ADMIN_USERNAME', ADMIN_USERNAME):
                user = User.query.filter_by(username=username).first()
                
                if not user:
                    # İlk giriş ise admin kullanıcısını oluştur
                    try:
                        user = User(username=username, 
                                  password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD', ADMIN_PASSWORD)))
                        db.session.add(user)
                        db.session.commit()
                        app.logger.info(f"Yeni admin kullanıcısı oluşturuldu: {username}")
                    except Exception as e:
                        app.logger.error(f"Kullanıcı oluşturma hatası: {str(e)}")
                        return f"Kullanıcı oluşturulurken hata: {str(e)}", 500
                
                if check_password_hash(user.password_hash, password):
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

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Son erişimleri getir
        access_logs = AccessLog.query.filter_by(user_id=current_user.id).order_by(AccessLog.access_time.desc()).limit(10)
        return render_template('dashboard.html', access_logs=access_logs)
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
