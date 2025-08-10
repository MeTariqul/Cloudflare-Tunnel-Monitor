#!/bin/bash

# Script to run the tunnel monitor in a screen session for persistent operation

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo "Error: 'screen' is not installed. Please install it first:"
    echo "sudo apt update && sudo apt install screen"
    exit 1
fi

# Create a new detached screen session running the tunnel monitor
echo "Starting Cloudflare Tunnel Monitor in a screen session..."

# Check if the session already exists
if screen -list | grep -q "tunnel_monitor"; then
    echo "A 'tunnel_monitor' screen session is already running."
    echo "To attach to it, use: screen -r tunnel_monitor"
    echo "To terminate it, use: screen -S tunnel_monitor -X quit"
    exit 1
fi

# Start a new screen session
screen -dmS tunnel_monitor bash -c "cd $(pwd) && ./run_tunnel_monitor_ssh.sh; exec bash"

echo "Tunnel monitor started in a detached screen session named 'tunnel_monitor'."
echo ""
echo "To view the tunnel monitor (and scan QR code if needed):"
echo "  screen -r tunnel_monitor"
echo ""
echo "To detach from the session (keep it running in background):"
echo "  Press Ctrl+A, then D"
echo ""
echo "To terminate the session:"
echo "  screen -S tunnel_monitor -X quit"
echo ""
echo "The tunnel monitor will continue running even after you log out."