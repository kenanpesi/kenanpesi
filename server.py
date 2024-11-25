from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import logging
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

API_KEY = "K3N4N_P3YS3R_S3CR3T_K3Y"
connected_clients = {}

logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    if request.headers.get('X-API-Key') != API_KEY:
        return {"error": "Unauthorized"}, 401
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected to WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    # İstemci bağlantısı kesildiğinde listeden çıkar
    for client_id, client in list(connected_clients.items()):
        if client.get('socket_id') == request.sid:
            del connected_clients[client_id]
            emit('client_disconnected', {'client_id': client_id}, broadcast=True)
            logging.info(f'Client disconnected: {client_id}')
            break

@socketio.on('register')
def handle_register(data):
    try:
        if data.get('api_key') != API_KEY:
            return
        
        client_id = data.get('client_id')
        if client_id:
            connected_clients[client_id] = {
                'socket_id': request.sid,
                'info': {}
            }
            emit('client_list', {'clients': list(connected_clients.keys())}, broadcast=True)
            logging.info(f'Client registered: {client_id}')
    except Exception as e:
        logging.error(f'Error in handle_register: {e}')

@socketio.on('command')
def handle_command(data):
    try:
        client_id = data.get('client_id')
        command = data.get('command')
        
        if client_id in connected_clients:
            client_socket_id = connected_clients[client_id]['socket_id']
            
            # Komut ve parametreleri ilet
            command_data = {
                'type': 'command',
                'command': command
            }
            
            # Dosya komutları için path parametresini ekle
            if command == 'files' and 'path' in data:
                command_data['path'] = data['path']
            
            emit('message', command_data, room=client_socket_id)
            logging.info(f'Command sent to {client_id}: {command}')
    except Exception as e:
        logging.error(f'Error in handle_command: {e}')

@socketio.on('response')
def handle_response(data):
    try:
        # Yanıtı tüm bağlı istemcilere ilet
        emit('message', data, broadcast=True)
        logging.info(f'Response broadcasted: {data.get("command")}')
    except Exception as e:
        logging.error(f'Error in handle_response: {e}')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
