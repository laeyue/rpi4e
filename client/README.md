# Raspberry Pi Client

This is the client application that runs on each Raspberry Pi device. It captures video from a USB camera, performs object detection (placeholder for now), and streams the results to the central hub server.

## Hardware Requirements

- Raspberry Pi (3B+, 4, or 5 recommended)
- USB Camera (any UVC-compatible webcam)
- Network connection to the server

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the server URL in `main.py`:
```python
SERVER_URL = "http://your-server-ip:5000"
PI_ID = "pi_001"  # Give each Pi a unique ID
```

## Usage

Run the client:
```bash
python main.py
```

The client will:
- Connect to the USB camera
- Connect to the server via SocketIO
- Stream video frames at 10 FPS (configurable)
- Send dummy detection data (ready for TFLite integration)

## Adding Real Object Detection

To integrate a real TFLite model:

1. Download a TFLite model (e.g., MobileNet SSD):
```bash
mkdir models
cd models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
```

2. Install TFLite runtime:
```bash
pip install tflite-runtime
```

3. Update the `load_tflite_model()` and `dummy_tflite_inference()` functions in `main.py` to use the actual model.

## Configuration

Key parameters in `main.py`:
- `SERVER_URL`: Server address
- `PI_ID`: Unique identifier for this Pi
- `CAMERA_INDEX`: USB camera index (usually 0)
- `FRAME_WIDTH`, `FRAME_HEIGHT`: Video resolution
- `FPS_TARGET`: Frames per second to send

## Troubleshooting

**Camera not found:**
- Check USB connection: `ls /dev/video*`
- Test camera: `v4l2-ctl --list-devices`

**Can't connect to server:**
- Verify server is running
- Check firewall settings
- Confirm SERVER_URL is correct

**Low FPS:**
- Reduce resolution
- Lower FPS_TARGET
- Check network bandwidth
