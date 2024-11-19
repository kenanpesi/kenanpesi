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
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f0f2f5;
            }
            #messages {
                height: 400px;
                overflow-y: auto;
                border: 1px solid #ccc;
                padding: 10px;
                margin-bottom: 20px;
                background-color: white;
                border-radius: 8px;
            }
            .message {
                margin-bottom: 10px;
                padding: 8px;
                border-radius: 8px;
                background-color: #e9ecef;
            }
            .message .time {
                color: #666;
                font-size: 0.8em;
            }
            input[type="text"] {
                width: 70%;
                padding: 8px;
                margin-right: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 8px 15px;
                background-color: #0084ff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0066cc;
            }
            #name {
                width: 30%;
                margin-bottom: 10px;
            }
            #message {
                width: 60%;
            }
        </style>
    </head>
    <body>
        <h1>Global Chat</h1>
        <div id="messages"></div>
        <div>
            <input type="text" id="name" placeholder="İsminiz" />
            <br>
            <input type="text" id="message" placeholder="Mesajınız" />
            <button onclick="sendMessage()">Gönder</button>
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
                                <strong>${msg.name}:</strong> ${msg.message}
                                <div class="time">${new Date(msg.timestamp).toLocaleString()}</div>
                            `;
                            messagesDiv.appendChild(messageDiv);
                        });
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    });
            }

            function sendMessage() {
                const name = document.getElementById('name').value;
                const message = document.getElementById('message').value;
                
                if (!name || !message) {
                    alert('Lütfen isim ve mesaj giriniz!');
                    return;
                }

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
                });
            }

            // Enter tuşu ile mesaj gönderme
            document.getElementById('message').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
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
