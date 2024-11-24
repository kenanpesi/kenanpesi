from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import secrets

app = Flask(__name__)
CORS(app)

# Yapılandırma
app.config['SECRET_KEY'] = secrets.token_hex(16)
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///storage.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Upload klasörünü oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Kullanıcı modeli
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.api_key = secrets.token_hex(32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Dosya modeli
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Veritabanını oluştur
def init_db():
    with app.app_context():
        db.create_all()

init_db()

# Ana sayfa
@app.route('/')
def home():
    files = File.query.order_by(File.upload_date.desc()).all()
    return render_template('index.html', files=files)

# Kullanıcı kaydı (sadece bir kullanıcı için)
@app.route('/register', methods=['POST'])
def register():
    if User.query.first() is not None:
        return jsonify({'error': 'Registration is closed'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User()
    user.username = username
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'api_key': user.api_key
    })

# Dosya yükleme (API key ile)
@app.route('/upload', methods=['POST'])
def upload_file():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'No API key provided'}), 401
    
    user = User.query.filter_by(api_key=api_key).first()
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Güvenli dosya adı oluştur
        filename = secrets.token_hex(8) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Dosya bilgilerini veritabanına kaydet
        file_record = File(
            filename=filename,
            original_filename=file.filename,
            file_size=os.path.getsize(file_path),
            user_id=user.id
        )
        db.session.add(file_record)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename
        })

# Dosya indirme
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
