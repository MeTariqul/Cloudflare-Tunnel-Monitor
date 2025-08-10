#!/bin/bash

# Script to set up the tunnel monitor as a systemd service

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Please run with: sudo $0"
    exit 1
fi

echo "Setting up Cloudflare Tunnel Monitor as a systemd service..."

# Get the current directory
CURRENT_DIR=$(pwd)

# Get the current user
CURRENT_USER=$(logname || echo "$SUDO_USER")
if [ -z "$CURRENT_USER" ]; then
    echo "Warning: Could not determine the current user. Using 'root' as the user."
    CURRENT_USER="root"
fi

echo "Using user: $CURRENT_USER"
echo "Using directory: $CURRENT_DIR"

# Create the service file
cat > /etc/systemd/system/tunnel-monitor.service << EOF
[Unit]
Description=Cloudflare Tunnel Monitor with WhatsApp Web
After=network.target

[Service]
User=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/tunnel_monitor_selenium.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at /etc/systemd/system/tunnel-monitor.service"

# Check if virtual environment exists
if [ ! -d "$CURRENT_DIR/venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$CURRENT_DIR/venv"
    
    # Install dependencies
    echo "Installing dependencies..."
    "$CURRENT_DIR/venv/bin/pip" install -r "$CURRENT_DIR/requirements.txt"
else
    echo "Using existing virtual environment"
fi

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable the service
echo "Enabling the service..."
systemctl enable tunnel-monitor.service

echo "\nSetup completed successfully!"
echo "\nIMPORTANT: Before starting the service, make sure you have:"
echo "1. Updated the configuration in tunnel_monitor_selenium.py"
echo "2. Authenticated WhatsApp Web by running the script manually first"
echo "\nTo start the service: sudo systemctl start tunnel-monitor"
echo "To check status: sudo systemctl status tunnel-monitor"
echo "To view logs: sudo journalctl -u tunnel-monitor -f"
echo "To stop the service: sudo systemctl stop tunnel-monitor"