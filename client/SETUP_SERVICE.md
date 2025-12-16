# Raspberry Pi Bridge Service Setup

This guide explains how to set up the `bridge.py` script to run automatically at boot. This bridge connects to the server and manages the main object detection script (`main.py`), allowing you to start/stop it remotely.

## 1. Prerequisites

Ensure you have completed the basic setup in `SETUP_RASPI.md` and that `main.py` runs correctly when executed manually.

## 2. Install the Service

1.  **Copy the service file to the systemd directory:**
    ```bash
    sudo cp rpi-bridge.service /etc/systemd/system/
    ```

2.  **Edit the service file (if needed):**
    Check if your username is `pi` and the path is `/home/pi/rpimode/client`. If you cloned the repo somewhere else or have a different username (e.g., `laeyue`), you need to edit the file:
    ```bash
    sudo nano /etc/systemd/system/rpi-bridge.service
    ```
    *Change `User=pi` to `User=laeyue` (or your username)*
    *Change `/home/pi/...` to `/home/laeyue/...`*

3.  **Reload systemd daemon:**
    ```bash
    sudo systemctl daemon-reload
    ```

4.  **Enable the service to start at boot:**
    ```bash
    sudo systemctl enable rpi-bridge.service
    ```

5.  **Start the service immediately:**
    ```bash
    sudo systemctl start rpi-bridge.service
    ```

## 3. Verify Status

Check if the bridge is running:
```bash
sudo systemctl status rpi-bridge.service
```

You should see "Active: active (running)".

## 4. Usage

Now, when you go to the web dashboard:
*   **Click "Start":** The bridge will launch `main.py`.
*   **Click "Stop":** The bridge will kill the `main.py` process.

## 5. Viewing Logs

To see what the bridge (and the main script) is doing:
```bash
journalctl -u rpi-bridge.service -f
```
