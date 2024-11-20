from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# PostgreSQL bağlantı ayarları
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mesaj modeli
class Message(db.Model):
    __tablename__ = 'messages'  # Tablo adını açıkça belirtiyoruz
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }

# Veritabanı tablolarını oluştur
def init_db():
    with app.app_context():
        db.drop_all()  # Mevcut tabloları sil
        db.create_all()  # Tabloları yeniden oluştur
        print("Veritabanı tabloları oluşturuldu!")

# Uygulama başladığında tabloları oluştur
init_db()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Global Chat</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                color: #2d3748;
            }

            .container {
                width: 100%;
                max-width: 800px;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                padding: 24px;
                margin-top: 20px;
            }

            h1 {
                color: white;
                text-align: center;
                margin-bottom: 20px;
                font-size: 2.5rem;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            }

            #messages {
                height: 500px;
                overflow-y: auto;
                padding: 16px;
                margin-bottom: 24px;
                background: white;
                border-radius: 12px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
            }

            .message {
                margin-bottom: 16px;
                padding: 12px 16px;
                border-radius: 12px;
                background: #f7fafc;
                border-left: 4px solid #667eea;
                animation: fadeIn 0.3s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .message:hover {
                background: #edf2f7;
                transition: background 0.2s ease;
            }

            .message strong {
                color: #4a5568;
                font-weight: 600;
            }

            .message .time {
                color: #718096;
                font-size: 0.85em;
                margin-top: 4px;
            }

            .input-group {
                display: flex;
                flex-direction: column;
                gap: 12px;
                margin-top: 16px;
            }

            input[type="text"] {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 1rem;
                transition: all 0.2s ease;
                background: white;
            }

            input[type="text"]:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            #name {
                width: 100%;
            }

            .send-group {
                display: flex;
                gap: 12px;
            }

            #message {
                flex-grow: 1;
            }

            button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 1rem;
            }

            button:hover {
                background: #5a67d8;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            button:active {
                transform: translateY(0);
                box-shadow: none;
            }

            /* Scrollbar tasarımı */
            #messages::-webkit-scrollbar {
                width: 8px;
            }

            #messages::-webkit-scrollbar-track {
                background: #f7fafc;
                border-radius: 4px;
            }

            #messages::-webkit-scrollbar-thumb {
                background: #cbd5e0;
                border-radius: 4px;
            }

            #messages::-webkit-scrollbar-thumb:hover {
                background: #a0aec0;
            }

            /* Mobil uyumluluk */
            @media (max-width: 640px) {
                .container {
                    padding: 16px;
                }

                #messages {
                    height: 400px;
                }

                button {
                    padding: 12px 16px;
                }
            }
        </style>
    </head>
    <body>
        <h1>Global Chat</h1>
        <div class="container">
            <div id="messages"></div>
            <div class="input-group">
                <input type="text" id="name" placeholder="İsminiz" />
                <div class="send-group">
                    <input type="text" id="message" placeholder="Mesajınız" />
                    <button onclick="sendMessage()">Gönder</button>
                </div>
            </div>
        </div>

        <script>
            function loadMessages() {
                fetch('/messages')
                    .then(response => response.json())
                    .then(data => {
                        const messagesDiv = document.getElementById('messages');
                        messagesDiv.innerHTML = '';
                        data.forEach(msg => {
                            const messageDiv = document.createElement('div');
                            messageDiv.className = 'message';
                            messageDiv.innerHTML = `
                                <strong>${msg.name}</strong>
                                <div>${msg.message}</div>
                                <div class="time">${new Date(msg.timestamp).toLocaleString('tr-TR')}</div>
                            `;
                            messagesDiv.appendChild(messageDiv);
                        });
                        // Sadece yeni mesaj geldiğinde scroll yapılması için kontrol
                        if (messagesDiv.scrollTop + messagesDiv.clientHeight >= messagesDiv.scrollHeight - 100) {
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        }
                    });
            }

            function sendMessage() {
                const name = document.getElementById('name').value.trim();
                const message = document.getElementById('message').value.trim();
                
                if (!name || !message) {
                    alert('Lütfen isim ve mesaj giriniz!');
                    return;
                }

                const button = document.querySelector('button');
                button.disabled = true;
                button.style.opacity = '0.7';

                fetch('/messages', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        message: message
                    }),
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        alert('Hata: ' + data.error);
                        return;
                    }
                    document.getElementById('message').value = '';
                    loadMessages();
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Mesaj gönderilemedi. Lütfen tekrar deneyin.');
                })
                .finally(() => {
                    button.disabled = false;
                    button.style.opacity = '1';
                });
            }

            // Enter tuşu ile mesaj gönderme
            document.getElementById('message').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // İsim kaydetme
            const savedName = localStorage.getItem('chatName');
            if (savedName) {
                document.getElementById('name').value = savedName;
            }
            document.getElementById('name').addEventListener('change', function(e) {
                localStorage.setItem('chatName', e.target.value);
            });

            // İlk yükleme ve periyodik güncelleme
            loadMessages();
            setInterval(loadMessages, 3000);
        </script>
    </body>
    </html>
    """

@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        # Son 100 mesajı getir ve tarihe göre sırala
        messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
        # Mesajları JSON formatına çevir
        return jsonify([message.to_dict() for message in messages])
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify([])  # Hata durumunda boş liste dön

@app.route('/messages', methods=['POST'])
def post_message():
    try:
        data = request.json
        if not data or 'name' not in data or 'message' not in data:
            return jsonify({'error': 'Name and message are required'}), 400

        message = Message(
            name=data['name'],
            message=data['message']
        )
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict())
    except Exception as e:
        print(f"Mesaj gönderme hatası: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Message could not be sent'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
