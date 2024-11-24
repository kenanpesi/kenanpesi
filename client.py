import socket
import platform
import requests
import time
import os
import sys
import subprocess
import json
from datetime import datetime

SERVER_URL = "http://localhost:5000"  # Sunucu adresi
HOSTNAME = socket.gethostname()

def connect_to_server():
    try:
        response = requests.post(
            f"{SERVER_URL}/client/connect",
            json={"hostname": HOSTNAME}
        )
        return response.json()["status"] == "success"
    except:
        return False

def main():
    print(f"[*] {HOSTNAME} için uzak bağlantı başlatılıyor...")
    print(f"[*] Sunucu: {SERVER_URL}")
    
    while True:
        if connect_to_server():
            print(f"[+] Sunucuya bağlandı: {datetime.now()}")
        else:
            print(f"[-] Sunucuya bağlanılamadı: {datetime.now()}")
        
        time.sleep(5)  # 5 saniye bekle

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Program sonlandırılıyor...")
        sys.exit(0)
