#!/bin/bash

# Script to update the cloudflared path in the tunnel monitor script

# Check if a cloudflared path was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide the path to cloudflared"
    echo "Usage: $0 <cloudflared_path>"
    echo "Example: $0 /usr/local/bin/cloudflared"
    exit 1
fi

# Get the cloudflared path from the command line argument
CLOUDFLARED_PATH="$1"

# Check if the cloudflared path exists
if [ ! -f "$CLOUDFLARED_PATH" ]; then
    echo "Warning: The specified cloudflared path does not exist: $CLOUDFLARED_PATH"
    echo "Do you want to continue anyway? (y/n)"
    read -r response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        echo "Operation cancelled."
        exit 1
    fi
fi

echo "Updating cloudflared path to: $CLOUDFLARED_PATH"

# Update the cloudflared path in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(CLOUDFLARED_PATH = \).*|\1\"$CLOUDFLARED_PATH\"|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(CLOUDFLARED_PATH = \).*|\1\"$CLOUDFLARED_PATH\"|" tunnel_monitor_selenium.py
fi

echo "cloudflared path updated successfully."
echo "The tunnel monitor will now use cloudflared at: $CLOUDFLARED_PATH"