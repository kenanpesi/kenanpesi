from server import socketio, app

# Gunicorn için WSGI application
application = socketio.middleware(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
