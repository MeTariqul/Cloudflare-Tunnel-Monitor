#!/bin/bash

# Script to toggle headless mode in the tunnel monitor script

# Check if the script exists
if [ ! -f "tunnel_monitor_selenium.py" ]; then
    echo "Error: tunnel_monitor_selenium.py not found"
    exit 1
fi

# Check the current headless mode setting
CURRENT_HEADLESS=$(grep "HEADLESS_MODE = " tunnel_monitor_selenium.py | awk '{print $3}')

# Toggle the headless mode
if [ "$CURRENT_HEADLESS" == "True" ]; then
    NEW_HEADLESS="False"
    echo "Turning HEADLESS MODE OFF"
    echo "Chrome will now run with a visible browser window"
else
    NEW_HEADLESS="True"
    echo "Turning HEADLESS MODE ON"
    echo "Chrome will now run in headless mode (no visible window)"
fi

# Update the headless mode in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(HEADLESS_MODE = \).*|\1$NEW_HEADLESS|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(HEADLESS_MODE = \).*|\1$NEW_HEADLESS|" tunnel_monitor_selenium.py
fi

echo "Headless mode updated successfully."

if [ "$NEW_HEADLESS" == "True" ]; then
    echo "IMPORTANT: In headless mode, you'll need to scan the QR code from the saved image."
    echo "The QR code will be saved as 'whatsapp_qr.png' in the current directory."
else
    echo "IMPORTANT: With headless mode off, you'll need to scan the QR code from the browser window."
    echo "Make sure you have a display connected or are using X forwarding if running remotely."
fi