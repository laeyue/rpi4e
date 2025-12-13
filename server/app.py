from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import eventlet

# Patch standard library for eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store connected clients
connected_clients = []

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')

@socketio.on('pi_update')
def handle_pi_update(data):
    """
    Receive video frame and detection data from Raspberry Pi
    Expected data format:
    {
        'image': 'base64_encoded_jpeg_string',
        'detections': [
            {'label': 'person', 'x': 100, 'y': 150, 'width': 200, 'height': 300, 'confidence': 0.85},
            ...
        ],
        'timestamp': '2025-12-13T10:30:00',
        'pi_id': 'pi_001'
    }
    """
    print(f"Received update from Pi: {data.get('pi_id', 'unknown')}")
    
    # Broadcast to all connected browser clients
    emit('browser_feed', data, broadcast=True)

if __name__ == '__main__':
    print("Starting Flask-SocketIO server on port 5000...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
