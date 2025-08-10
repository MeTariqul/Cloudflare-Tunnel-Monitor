#!/bin/bash

# Script to update the Chrome path in the tunnel monitor script

# Check if a Chrome path was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide the path to Chrome/Chromium"
    echo "Usage: $0 <chrome_path>"
    echo "Example: $0 /usr/bin/chromium-browser"
    exit 1
fi

# Get the Chrome path from the command line argument
CHROME_PATH="$1"

# Check if the Chrome path exists
if [ ! -f "$CHROME_PATH" ]; then
    echo "Warning: The specified Chrome path does not exist: $CHROME_PATH"
    echo "Do you want to continue anyway? (y/n)"
    read -r response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        echo "Operation cancelled."
        exit 1
    fi
fi

echo "Updating Chrome path to: $CHROME_PATH"

# Update the Chrome path in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(CHROME_PATH = \).*|\1\"$CHROME_PATH\"|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(CHROME_PATH = \).*|\1\"$CHROME_PATH\"|" tunnel_monitor_selenium.py
fi

echo "Chrome path updated successfully."
echo "The tunnel monitor will now use Chrome at: $CHROME_PATH"