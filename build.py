import PyInstaller.__main__
import os

# Gerekli paketleri yükle
os.system('pip install -r client_requirements.txt')

# PyInstaller komutları
PyInstaller.__main__.run([
    'client.py',
    '--onefile',
    '--hidden-import=PIL',
    '--hidden-import=PIL._imaging',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageGrab',
    '--hidden-import=websockets',
    '--hidden-import=websockets.legacy',
    '--hidden-import=websockets.legacy.client',
    '--hidden-import=websockets.legacy.protocol',
    '--hidden-import=requests',
    '--hidden-import=psutil',
    '--hidden-import=cryptography',
    '--hidden-import=python-dotenv',
    '--hidden-import=asyncio',
    '--hidden-import=gevent',
    '--hidden-import=engineio',
    '--hidden-import=socketio',
    '--name=MuradSayagi'
])

if __name__ == "__main__":
    PyInstaller.__main__.run([
        'client.py',
        '--onefile',
        '--hidden-import=PIL',
        '--hidden-import=PIL._imaging',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageGrab',
        '--hidden-import=websockets',
        '--hidden-import=websockets.legacy',
        '--hidden-import=websockets.legacy.client',
        '--hidden-import=websockets.legacy.protocol',
        '--hidden-import=requests',
        '--hidden-import=psutil',
        '--hidden-import=cryptography',
        '--hidden-import=python-dotenv',
        '--hidden-import=asyncio',
        '--hidden-import=gevent',
        '--hidden-import=engineio',
        '--hidden-import=socketio',
        '--name=MuradSayagi'
    ])
