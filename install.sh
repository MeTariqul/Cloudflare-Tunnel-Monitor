#!/bin/bash

# Exit on error
set -e

echo "===== Installing Cloudflare Tunnel Monitor ====="

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv

# Install cloudflared
echo "Installing cloudflared..."
if ! command -v cloudflared &> /dev/null; then
    echo "Downloading cloudflared..."
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
else
    echo "cloudflared is already installed"
fi

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p /opt/cloudflare_tunnel_monitor

# Copy files
echo "Copying files..."
sudo cp tunnel_monitor.py /opt/cloudflare_tunnel_monitor/
sudo cp tunnel-monitor.service /etc/systemd/system/

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
sudo python3 -m venv /opt/cloudflare_tunnel_monitor/venv
sudo /opt/cloudflare_tunnel_monitor/venv/bin/pip install requests

# Update service file to use venv
echo "Updating service file..."
sudo sed -i 's|ExecStart=/usr/bin/python3 /opt/cloudflare_tunnel_monitor/tunnel_monitor.py|ExecStart=/opt/cloudflare_tunnel_monitor/venv/bin/python /opt/cloudflare_tunnel_monitor/tunnel_monitor.py|g' /etc/systemd/system/tunnel-monitor.service

# Set permissions
echo "Setting permissions..."
sudo chmod +x /opt/cloudflare_tunnel_monitor/tunnel_monitor.py

# Enable and start service
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable tunnel-monitor

echo "===== Installation Complete ====="
echo "To start the service, run: sudo systemctl start tunnel-monitor"
echo "To check status, run: sudo systemctl status tunnel-monitor"
echo "To view logs, run: sudo journalctl -u tunnel-monitor -f"
echo ""
echo "IMPORTANT: Before starting the service, edit /opt/cloudflare_tunnel_monitor/tunnel_monitor.py"
echo "and update the Twilio credentials and WhatsApp numbers."