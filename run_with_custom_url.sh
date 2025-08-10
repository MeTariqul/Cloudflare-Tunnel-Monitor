#!/bin/bash

# Script to run the tunnel monitor with a custom URL

# Check if a URL was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a URL to tunnel"
    echo "Usage: $0 <url>"
    echo "Example: $0 http://localhost:8080"
    exit 1
fi

# Get the URL from the command line argument
URL="$1"

echo "Starting Cloudflare Tunnel Monitor with custom URL: $URL"

# Create a temporary copy of the script with the custom URL
TEMP_SCRIPT="tunnel_monitor_custom.py"

# Copy the original script
cp tunnel_monitor_selenium.py "$TEMP_SCRIPT"

# Update the URL in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(TUNNEL_URL = \).*|\1\"$URL\"|" "$TEMP_SCRIPT"
    sed -i '' "s|\(\[cloudflared_cmd, \"tunnel\", \"--url\", \).*\]|\1\"$URL\"]|" "$TEMP_SCRIPT"
else
    # Linux version of sed
    sed -i "s|\(TUNNEL_URL = \).*|\1\"$URL\"|" "$TEMP_SCRIPT"
    sed -i "s|\(\[cloudflared_cmd, \"tunnel\", \"--url\", \).*\]|\1\"$URL\"]|" "$TEMP_SCRIPT"
fi

echo "Updated script with custom URL"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Install dependencies
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Using existing virtual environment..."
    source venv/bin/activate
fi

# Run the modified script
echo "Running tunnel monitor with custom URL..."
echo ""
echo "IMPORTANT: You will need to scan the QR code to authenticate WhatsApp Web"
echo "when the browser window opens."
echo ""
python "$TEMP_SCRIPT"

# Clean up
rm "$TEMP_SCRIPT"

# Deactivate virtual environment
deactivate