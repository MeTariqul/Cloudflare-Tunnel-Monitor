#!/bin/bash

# Script to run the Cloudflare Tunnel Monitor on an SSH server

echo "Starting Cloudflare Tunnel Monitor with WhatsApp Web notifications..."

# Check if virtual environment exists, if not create it
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

# Run the tunnel monitor
echo "Running tunnel monitor..."
echo ""
echo "IMPORTANT: You will need to scan the QR code to authenticate WhatsApp Web"
echo "when the browser window opens."
echo ""
echo "NOTE: If using cloudflared with a URL parameter, avoid hash fragments (#)"
echo "or special characters. Use simple URL formats like:"
echo "http://192.168.100.1:8096/web/ instead of http://192.168.100.1:8096/web/#/home.html"
echo ""
python tunnel_monitor_selenium.py

# Deactivate virtual environment when done
deactivate