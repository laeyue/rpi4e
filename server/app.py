from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import eventlet
import os

# Patch standard library for eventlet
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store connected clients and Pis
connected_clients = []
connected_pis = set()
socket_to_pi = {}

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    # Send status of all currently connected Pis to the new client
    for pi_id in connected_pis:
        emit('pi_status', {'pi_id': pi_id, 'status': 'online'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')
    # Clean up if it was a Pi
    if request.sid in socket_to_pi:
        pi_id = socket_to_pi[request.sid]
        del socket_to_pi[request.sid]
        
        # Check if any other socket is still connected for this Pi ID
        is_still_connected = False
        for sid, pid in socket_to_pi.items():
            if pid == pi_id:
                is_still_connected = True
                break
        
        if not is_still_connected:
            connected_pis.discard(pi_id)
            print(f"Pi disconnected: {pi_id}")
            emit('pi_status', {'pi_id': pi_id, 'status': 'offline'}, broadcast=True)
        else:
            print(f"Pi {pi_id} still has active connections (e.g. bridge)")

@socketio.on('register_pi')
def handle_register_pi(data):
    """Register a Pi client to a room"""
    pi_id = data.get('pi_id')
    if pi_id:
        join_room(pi_id)
        # Track this Pi
        socket_to_pi[request.sid] = pi_id
        connected_pis.add(pi_id)
        
        print(f"Registered Pi: {pi_id}")
        # Notify browsers that a Pi is online/ready for control
        emit('pi_status', {'pi_id': pi_id, 'status': 'online'}, broadcast=True)

@socketio.on('control_pi')
def handle_control_pi(data):
    """Send control command to a specific Pi"""
    pi_id = data.get('pi_id')
    command = data.get('command')
    if pi_id and command:
        print(f"Sending command {command} to {pi_id}")
        emit('command_received', {'command': command}, room=pi_id)

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
    # print(f"Received update from Pi: {data.get('pi_id', 'unknown')}")
    
    # Broadcast to all connected browser clients
    emit('browser_feed', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask-SocketIO server on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
