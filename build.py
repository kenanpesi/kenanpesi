import PyInstaller.__main__
import os

def build_exe():
    PyInstaller.__main__.run([
        'client.py',
        '--onefile',
        '--noconsole',
        '--name=RemoteAccess',
        '--hidden-import=flask',
        '--hidden-import=psutil',
        '--icon=NONE'
    ])

if __name__ == "__main__":
    build_exe()
