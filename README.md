# MuradSayagi Remote Access Tool

A WebSocket-based remote system management tool with a hacker-themed interface.

## Features

- Real-time system monitoring
- Remote screenshot capture
- File system browsing
- System information display
- WebSocket-based communication
- Modern hacker-themed UI

## Quick Start

1. Download `RemoteAccess.exe` from releases
2. Run the executable on the target Windows system
3. Access the control panel at: https://kenanpeyser.up.railway.app

## Security

- API Key Authentication
- Encrypted WebSocket Communication (WSS)
- Limited Command Execution

## Technical Details

- Server: Flask + Flask-SocketIO
- Client: Python + WebSockets
- Interface: HTML5 + Bootstrap
- Deployment: Railway Platform

## Development

### Requirements
```bash
pip install -r requirements.txt
```

### Build
```bash
python build.py
```

## Disclaimer

This tool is for educational purposes only. Use responsibly and only on systems you own or have permission to access.
