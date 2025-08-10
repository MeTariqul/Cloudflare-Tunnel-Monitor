#!/bin/bash

# Script to run the tunnel monitor in a tmux session for persistent operation

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: 'tmux' is not installed. Please install it first:"
    echo "sudo apt update && sudo apt install tmux"
    exit 1
fi

# Create a new detached tmux session running the tunnel monitor
echo "Starting Cloudflare Tunnel Monitor in a tmux session..."

# Check if the session already exists
if tmux has-session -t tunnel_monitor 2>/dev/null; then
    echo "A 'tunnel_monitor' tmux session is already running."
    echo "To attach to it, use: tmux attach -t tunnel_monitor"
    echo "To terminate it, use: tmux kill-session -t tunnel_monitor"
    exit 1
fi

# Start a new tmux session
tmux new-session -d -s tunnel_monitor "cd $(pwd) && ./run_tunnel_monitor_ssh.sh; bash"

echo "Tunnel monitor started in a detached tmux session named 'tunnel_monitor'."
echo ""
echo "To view the tunnel monitor (and scan QR code if needed):"
echo "  tmux attach -t tunnel_monitor"
echo ""
echo "To detach from the session (keep it running in background):"
echo "  Press Ctrl+B, then D"
echo ""
echo "To terminate the session:"
echo "  tmux kill-session -t tunnel_monitor"
echo ""
echo "The tunnel monitor will continue running even after you log out."