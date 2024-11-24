from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import secrets

app = Flask(__name__)
CORS(app)

# Yapılandırma
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Güvenli bir anahtar belirleyin
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///storage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Sabit kullanıcı bilgileri
ADMIN_USERNAME = "kenanpesi"  # İstediğiniz kullanıcı adını girin
ADMIN_PASSWORD = "your-password-here"  # İstediğiniz şifreyi girin
API_KEY = "your-api-key-here"  # İstediğiniz API anahtarını girin

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Dosya modeli
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)

# Veritabanını oluştur
def init_db():
    with app.app_context():
        db.create_all()

init_db()

# Giriş kontrolü
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Login sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Geçersiz kullanıcı adı veya şifre')
    
    return render_template('login.html')

# Çıkış
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Ana sayfa
@app.route('/')
@login_required
def home():
    files = File.query.order_by(File.upload_date.desc()).all()
    return render_template('index.html', files=files)

# Dosya yükleme (API key ile)
@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != API_KEY:
        return jsonify({'error': 'Geçersiz API anahtarı'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    if file:
        # Güvenli dosya adı oluştur
        filename = secrets.token_hex(8) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Dosya bilgilerini veritabanına kaydet
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_size=os.path.getsize(file_path)
        )
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Dosya başarıyla yüklendi',
            'filename': filename
        })

# Dosya indirme
@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
