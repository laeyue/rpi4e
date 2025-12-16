import cv2
import socketio
import base64
import time
import json
import os
import urllib.request
from datetime import datetime
import numpy as np

# Configuration
SERVER_URL = "https://edge.studentio.xyz"  # Change to your server IP/domain
PI_ID = "pi_001"  # Unique identifier for this Raspberry Pi
CAMERA_INDEX = 0  # USB Camera index (usually 0 for first camera)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS_TARGET = 10  # Target frames per second to send

# Model Configuration (OpenCV DNN - MobileNet SSD)
MODEL_DIR = "models"
PROTO_URL = "https://raw.githubusercontent.com/djmv/MobilNet_SSD_opencv/master/MobileNetSSD_deploy.prototxt"
MODEL_URL = "https://github.com/djmv/MobilNet_SSD_opencv/raw/master/MobileNetSSD_deploy.caffemodel"
PROTO_FILENAME = "MobileNetSSD_deploy.prototxt"
MODEL_FILENAME = "MobileNetSSD_deploy.caffemodel"
CONFIDENCE_THRESHOLD = 0.5

# Initialize SocketIO client
sio = socketio.Client()

# Global control flag
is_running = True

@sio.event
def command_received(data):
    """Handle control commands from server"""
    global is_running
    command = data.get('command')
    print(f"📥 Received command: {command}")
    
    if command == 'start':
        is_running = True
        print("▶️ Resuming stream")
    elif command == 'stop':
        is_running = False
        print("⏸️ Pausing stream")

def download_model():
    """Download the Caffe model if not present"""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    proto_path = os.path.join(MODEL_DIR, PROTO_FILENAME)
    model_path = os.path.join(MODEL_DIR, MODEL_FILENAME)

    if not os.path.exists(proto_path):
        print("📥 Downloading model architecture...")
        urllib.request.urlretrieve(PROTO_URL, proto_path)

    if not os.path.exists(model_path):
        print("📥 Downloading model weights...")
        urllib.request.urlretrieve(MODEL_URL, model_path)
        print("✅ Model downloaded successfully")
    else:
        print("✅ Model already exists")


def load_model():
    """Load OpenCV DNN model"""
    download_model()
    try:
        proto_path = os.path.join(MODEL_DIR, PROTO_FILENAME)
        model_path = os.path.join(MODEL_DIR, MODEL_FILENAME)
        net = cv2.dnn.readNetFromCaffe(proto_path, model_path)
        print("🧠 OpenCV DNN model loaded successfully")
        return net
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None


def inference(net, frame):
    """
    Run OpenCV DNN inference on the frame and detect humans
    """
    if net is None:
        return []
    
    h, w = frame.shape[:2]
    # MobileNet SSD expects 300x300 input
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    
    results = []
    # Loop over detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_THRESHOLD:
            idx = int(detections[0, 0, i, 1])
            # Class 15 is Person in MobileNet SSD (Caffe/VOC)
            if idx == 15: 
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Ensure coordinates are within frame
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)
                
                results.append({
                    'label': 'person',
                    'x': int(startX),
                    'y': int(startY),
                    'width': int(endX - startX),
                    'height': int(endY - startY),
                    'confidence': float(confidence)
                })
    return results


def compress_frame(frame, quality=85):
    """
    Compress frame to JPEG and encode as base64
    
    Args:
        frame: numpy array representing the video frame
        quality: JPEG quality (0-100)
    
    Returns:
        base64 encoded JPEG string
    """
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return jpg_as_text


@sio.event
def connect():
    """Handle successful connection to server"""
    print(f"✅ Connected to server: {SERVER_URL}")
    print(f"🆔 Pi ID: {PI_ID}")
    sio.emit('register_pi', {'pi_id': PI_ID})


@sio.event
def disconnect():
    """Handle disconnection from server"""
    print("❌ Disconnected from server")


@sio.event
def connect_error(data):
    """Handle connection error"""
    print(f"⚠️ Connection failed: {data}")


def main():
    """Main loop for capturing and streaming video"""
    print("🚀 Starting Raspberry Pi Client...")
    print(f"📹 Attempting to open camera {CAMERA_INDEX}")
    
    # Initialize camera
    cap = cv2.VideoCapture(CAMERA_INDEX)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera")
        print("💡 Make sure your USB camera is connected")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    
    print(f"✅ Camera opened successfully")
    print(f"📐 Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")
    
    # Load Model
    net = load_model()
    
    # Connect to server
    print(f"🔌 Connecting to server: {SERVER_URL}")
    while not sio.connected:
        try:
            sio.connect(SERVER_URL, wait_timeout=10)
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("⏳ Retrying in 5 seconds... (Press Ctrl+C to stop)")
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                cap.release()
                return
    
    # Frame timing
    frame_interval = 1.0 / FPS_TARGET
    last_frame_time = time.time()
    frame_count = 0
    
    print(f"🎬 Starting video stream at {FPS_TARGET} FPS...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Check if running
            if not is_running:
                time.sleep(1)
                continue

            # Read frame from camera
            ret, frame = cap.read()
            
            if not ret:
                print("⚠️ Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            # Control frame rate
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                continue
            
            last_frame_time = current_time
            frame_count += 1
            
            # Run object detection
            detections = inference(net, frame)
            
            # Compress frame to JPEG/Base64
            base64_image = compress_frame(frame)
            
            # Prepare data packet
            data = {
                'image': base64_image,
                'detections': detections,
                'timestamp': datetime.now().isoformat(),
                'pi_id': PI_ID,
                'frame_number': frame_count
            }
            
            # Send to server
            try:
                sio.emit('pi_update', data)
                
                # Print status every 30 frames
                if frame_count % 30 == 0:
                    print(f"📤 Sent frame {frame_count} with {len(detections)} detections")
            except Exception as e:
                print(f"⚠️ Failed to send frame: {e}")
            
            # Optional: Display local preview (comment out for headless Pi)
            # Uncomment the following lines if you want to see the video on the Pi
            # for detection in detections:
            #     x, y, w, h = detection['x'], detection['y'], detection['width'], detection['height']
            #     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            #     label = f"{detection['label']} {detection['confidence']:.2f}"
            #     cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # 
            # cv2.imshow('Local Preview', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping client...")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        sio.disconnect()
        print("✅ Client stopped successfully")


if __name__ == "__main__":
    main()
