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

SERVER_URL = os.getenv("SERVER_URL", "https://kenanpeyser.up.railway.app")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "wss://kenanpeyser.up.railway.app/ws")
CLIENT_ID = socket.gethostname()
API_KEY = os.getenv("API_KEY")  # API key should be set as environment variable

if not API_KEY:
    logging.error("API_KEY environment variable is not set")
    sys.exit(1)

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
    retry_count = 0
    max_retries = 5
    retry_delay = 5  # seconds

    while True:
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                logging.info(f"Connected to WebSocket server: {WEBSOCKET_URL}")
                retry_count = 0  # Reset retry count on successful connection
                
                await websocket.send(json.dumps({
                    "type": "register",
                    "client_id": CLIENT_ID,
                    "api_key": API_KEY
                }))
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if data["type"] == "command":
                            response = None
                            if data["command"] == "status":
                                response = get_system_info()
                            elif data["command"] == "screenshot":
                                response = take_screenshot()
                            elif data["command"] == "files":
                                path = data.get("path", ".")
                                response = list_files(path)
                            
                            if response:
                                await websocket.send(json.dumps({
                                    "type": "response",
                                    "client_id": CLIENT_ID,
                                    "data": response
                                }))
                    except json.JSONDecodeError as e:
                        logging.error(f"Invalid JSON message received: {e}")
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
                        
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
            retry_count += 1
            if retry_count > max_retries:
                logging.error(f"Failed to connect after {max_retries} attempts. Exiting.")
                sys.exit(1)
            
            logging.warning(f"Connection failed (attempt {retry_count}/{max_retries}): {e}")
            await asyncio.sleep(retry_delay)
            
        except Exception as e:
            logging.error(f"Unexpected error in websocket client: {e}")
            await asyncio.sleep(retry_delay)

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
