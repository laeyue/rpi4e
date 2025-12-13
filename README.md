# Raspberry Pi Object Detection Hub

A hub-and-spoke architecture for streaming video from multiple Raspberry Pi devices to a central server with real-time object detection visualization.

## 🏗️ Architecture

```
┌─────────────┐
│ Raspberry Pi│──┐
│  (Client)   │  │
└─────────────┘  │
                 │
┌─────────────┐  │    ┌─────────────┐      ┌─────────────┐
│ Raspberry Pi│──┼───→│   Server    │◄────→│   Browser   │
│  (Client)   │  │    │    (Hub)    │      │  Dashboard  │
└─────────────┘  │    └─────────────┘      └─────────────┘
                 │
┌─────────────┐  │
│ Raspberry Pi│──┘
│  (Client)   │
└─────────────┘
```

## 📁 Project Structure

```
rpimode/
├── server/                 # Central hub server
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py             # Flask-SocketIO server
│   └── templates/
│       └── index.html     # Web dashboard
├── client/                # Raspberry Pi client
│   ├── main.py            # Video capture & streaming
│   ├── requirements.txt
│   └── README.md
└── docker-compose.yml     # Docker deployment config
```

## 🚀 Quick Start

### 1. Deploy the Server (Hub)

Using Docker Compose (recommended):
```bash
docker-compose up -d
```

Or run directly:
```bash
cd server
pip install -r requirements.txt
python app.py
```

Access the dashboard at: `http://localhost` (or port 80)

### 2. Setup Raspberry Pi Clients

On each Raspberry Pi:

```bash
cd client
pip install -r requirements.txt
```

Edit `main.py` to set your server URL:
```python
SERVER_URL = "http://your-server-ip:5000"
PI_ID = "pi_001"  # Unique ID for each Pi
```

Run the client:
```bash
python main.py
```

## 🎯 Features

### Server (Hub)
- Flask-SocketIO server for real-time communication
- Web dashboard with live video feeds
- Client-side rendering of bounding boxes
- Multiple Pi feed support
- FPS and latency monitoring
- Docker deployment ready

### Client (Raspberry Pi)
- USB camera capture with OpenCV
- Configurable video resolution and FPS
- Base64 JPEG compression for streaming
- Placeholder for TFLite object detection
- Automatic reconnection
- Low latency (~100-300ms)

## 🔧 Configuration

### Server Configuration (`server/app.py`)
- Port: 5000 (mapped to 80 in Docker)
- CORS: Enabled for all origins
- Async mode: eventlet

### Client Configuration (`client/main.py`)
- `SERVER_URL`: Server address
- `PI_ID`: Unique identifier for each Pi
- `CAMERA_INDEX`: USB camera device (usually 0)
- `FRAME_WIDTH/HEIGHT`: Resolution (default 640x480)
- `FPS_TARGET`: Streaming rate (default 10 FPS)

## 📦 Data Format

Frames sent from Pi to Server:
```json
{
    "image": "base64_encoded_jpeg",
    "detections": [
        {
            "label": "person",
            "x": 100,
            "y": 150,
            "width": 200,
            "height": 300,
            "confidence": 0.85
        }
    ],
    "timestamp": "2025-12-13T10:30:00",
    "pi_id": "pi_001",
    "frame_number": 1234
}
```

## 🤖 Adding Real Object Detection

Currently, the client uses dummy detection data. To integrate TFLite:

1. **Download a model:**
```bash
cd client/models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
```

2. **Install TFLite:**
```bash
pip install tflite-runtime
```

3. **Update `main.py`:**
   - Implement `load_tflite_model()`
   - Replace `dummy_tflite_inference()` with real inference

## 🐳 Docker Deployment

Build and run:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop:
```bash
docker-compose down
```

## 🔍 Troubleshooting

**Server not accessible:**
- Check firewall: Allow port 80/5000
- Verify Docker is running: `docker ps`

**Pi can't connect:**
- Test server connectivity: `ping server-ip`
- Check SERVER_URL in client code
- Verify server is running

**No camera feed:**
- List cameras: `ls /dev/video*`
- Test camera: `v4l2-ctl --list-devices`
- Try different CAMERA_INDEX

**High latency:**
- Reduce FPS_TARGET
- Lower resolution
- Check network bandwidth

## 📊 Performance Tips

- **Resolution**: 640x480 is balanced; use 320x240 for low bandwidth
- **FPS**: 10 FPS is good for monitoring; 5 FPS for multiple Pis
- **JPEG Quality**: Default 85%; lower to 70% for bandwidth savings
- **Model**: Use quantized TFLite models for Raspberry Pi

## 🛠️ Tech Stack

**Server:**
- Flask + Flask-SocketIO
- Eventlet (async)
- HTML5 Canvas
- Socket.IO client

**Client:**
- OpenCV (camera capture)
- Python-SocketIO
- NumPy
- (Optional) TFLite for inference

## 📝 License

MIT License - feel free to modify and use for your projects!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Multiple camera feeds on dashboard
- Recording/playback functionality
- Alert system for specific detections
- Database storage for events
- MQTT integration option
- Hardware acceleration (Coral TPU, etc.)

## 📧 Support

For issues or questions, please open a GitHub issue.
