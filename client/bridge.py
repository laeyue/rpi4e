import socketio
import time
import subprocess
import os
import signal
import sys

# Configuration
SERVER_URL = "https://edge.studentio.xyz"
PI_ID = "pi1"

# Initialize SocketIO client
sio = socketio.Client()

# Store the process ID of the main script
main_process = None

def start_main_script():
    """Start the main object detection script"""
    global main_process
    if main_process is None:
        print("🚀 Starting main detection script...")
        # Run main.py as a subprocess
        # Using sys.executable ensures we use the same python interpreter (venv)
        main_process = subprocess.Popen([sys.executable, "main.py"])
        print(f"✅ Main script started with PID: {main_process.pid}")
    else:
        print("⚠️ Main script is already running")

def stop_main_script():
    """Stop the main object detection script"""
    global main_process
    if main_process:
        print("🛑 Stopping main detection script...")
        # Send SIGTERM to the subprocess
        main_process.terminate()
        try:
            main_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            main_process.kill()
        
        main_process = None
        print("✅ Main script stopped")
    else:
        print("⚠️ Main script is not running")

@sio.event
def connect():
    """Handle connection to server"""
    print(f"✅ Bridge connected to server: {SERVER_URL}")
    # Register as the controller for this Pi
    sio.emit('register_pi', {'pi_id': PI_ID})

@sio.event
def disconnect():
    print("❌ Bridge disconnected from server")

@sio.event
def command_received(data):
    """Handle control commands"""
    command = data.get('command')
    print(f"📥 Bridge received command: {command}")
    
    if command == 'start':
        start_main_script()
    elif command == 'stop':
        stop_main_script()
    elif command == 'restart':
        stop_main_script()
        time.sleep(2)
        start_main_script()
    elif command == 'add_wifi':
        ssid = data.get('ssid')
        password = data.get('password')
        if ssid and password:
            add_wifi_network(ssid, password)

def add_wifi_network(ssid, password):
    """Add a new Wi-Fi network to wpa_supplicant"""
    print(f"📶 Adding new Wi-Fi network: {ssid}")
    try:
        # Create wpa_supplicant entry
        # We use wpa_passphrase to generate the config block
        cmd = f'wpa_passphrase "{ssid}" "{password}" | sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null'
        subprocess.run(cmd, shell=True, check=True)
        
        # Reconfigure wpa_supplicant to pick up changes
        subprocess.run('sudo wpa_cli -i wlan0 reconfigure', shell=True, check=True)
        print(f"✅ Successfully added network: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add Wi-Fi network: {e}")

def main():
    print("🌉 Starting Bridge Service...")
    print(f"🆔 Managing Pi ID: {PI_ID}")
    
    # Connect to server with retry logic
    while True:
        try:
            if not sio.connected:
                sio.connect(SERVER_URL, wait_timeout=10)
                print("✅ Connected and waiting for commands...")
            sio.wait()
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nExiting bridge service...")
        stop_main_script()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    main()
