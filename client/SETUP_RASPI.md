# Raspberry Pi Setup Guide

Most Raspberry Pi OS versions come with Python 3 pre-installed. Follow these steps to set up your environment for the client application.

## 1. Update System
First, ensure your package lists and installed packages are up to date.
```bash
sudo apt update
sudo apt upgrade -y
```

## 2. Check Python Version
Check if Python 3 is installed (should be 3.7 or newer).
```bash
python3 --version
```

## 3. Install System Dependencies
OpenCV and other libraries require some system-level packages that might not be installed by default on the "Lite" version of Raspberry Pi OS.

```bash
# Install pip and venv if missing
sudo apt install -y python3-pip python3-venv

# Install libraries required by OpenCV (Updated for Raspberry Pi OS Bookworm/Newer)
# Note: If you are on an older OS and these fail, try: libgl1-mesa-glx libatlas-base-dev
sudo apt install -y libgl1 libglib2.0-0 libopenblas-dev
```

## 4. Set Up Virtual Environment (Recommended)
It's best practice to use a virtual environment to avoid conflicts with system packages.

```bash
# Navigate to the client directory
cd rpimode/client

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the environment
source venv/bin/activate
```
*Note: You will need to run `source venv/bin/activate` every time you open a new terminal to work on this project.*

## 5. Install Python Libraries
With the virtual environment activated, install the project dependencies.

```bash
pip install -r requirements.txt
```

## 6. Run the Client
Now you are ready to run the client script.

```bash
python main.py
```

## Troubleshooting

### "No module named cv2"
If you get this error even after installing requirements, try installing the headless version of OpenCV which avoids some GUI dependencies:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### "Externally Managed Environment" error
If you see this error when trying to use `pip` without a virtual environment, it's because newer Raspberry Pi OS versions enforce PEP 668. **Solution:** Use the virtual environment steps above (Step 4).
