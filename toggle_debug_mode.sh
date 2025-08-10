#!/bin/bash

# Script to toggle debug mode in the tunnel monitor script

# Check if the script exists
if [ ! -f "tunnel_monitor_selenium.py" ]; then
    echo "Error: tunnel_monitor_selenium.py not found"
    exit 1
fi

# Check the current debug mode setting
CURRENT_DEBUG=$(grep "DEBUG_MODE = " tunnel_monitor_selenium.py | awk '{print $3}')

# Toggle the debug mode
if [ "$CURRENT_DEBUG" == "True" ]; then
    NEW_DEBUG="False"
    echo "Turning DEBUG MODE OFF"
else
    NEW_DEBUG="True"
    echo "Turning DEBUG MODE ON"
fi

# Update the debug mode in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(DEBUG_MODE = \).*|\1$NEW_DEBUG|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(DEBUG_MODE = \).*|\1$NEW_DEBUG|" tunnel_monitor_selenium.py
fi

echo "Debug mode updated successfully."

if [ "$NEW_DEBUG" == "True" ]; then
    echo "The tunnel monitor will now run in debug mode with additional logging."
    echo "This will help diagnose issues but may generate larger log files."
else
    echo "The tunnel monitor will now run in normal mode with standard logging."
fi