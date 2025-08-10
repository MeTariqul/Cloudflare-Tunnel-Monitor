#!/bin/bash

# Script to stop the tunnel monitor running in the background

echo "Stopping Cloudflare Tunnel Monitor running in the background..."

# Check if PID file exists
if [ -f "tunnel_monitor.pid" ]; then
    PID=$(cat tunnel_monitor.pid)
    
    # Check if the process is still running
    if ps -p "$PID" > /dev/null; then
        echo "Stopping process with PID: $PID"
        kill "$PID"
        
        # Wait for the process to terminate
        echo "Waiting for the process to terminate..."
        for i in {1..5}; do
            if ! ps -p "$PID" > /dev/null; then
                echo "Process terminated successfully."
                rm tunnel_monitor.pid
                exit 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null; then
            echo "Process still running. Forcing termination..."
            kill -9 "$PID"
            if ! ps -p "$PID" > /dev/null; then
                echo "Process terminated successfully."
                rm tunnel_monitor.pid
                exit 0
            else
                echo "Failed to terminate process. Please check manually."
                exit 1
            fi
        fi
    else
        echo "Process with PID $PID is not running."
        rm tunnel_monitor.pid
    fi
else
    echo "PID file not found. The tunnel monitor may not be running in the background."
    
    # Try to find the process by name
    echo "Trying to find the process by name..."
    PIDS=$(pgrep -f "python.*tunnel_monitor_selenium.py")
    
    if [ -n "$PIDS" ]; then
        echo "Found processes: $PIDS"
        echo "Stopping processes..."
        
        for PID in $PIDS; do
            echo "Stopping process with PID: $PID"
            kill "$PID"
        done
        
        echo "Processes stopped."
    else
        echo "No tunnel monitor processes found."
    fi
fi

# Also check for cloudflared processes
echo "Checking for cloudflared processes..."
CLOUDFLARED_PIDS=$(pgrep -f "cloudflared.*tunnel")

if [ -n "$CLOUDFLARED_PIDS" ]; then
    echo "Found cloudflared processes: $CLOUDFLARED_PIDS"
    echo "Stopping cloudflared processes..."
    
    for PID in $CLOUDFLARED_PIDS; do
        echo "Stopping cloudflared process with PID: $PID"
        kill "$PID"
    done
    
    echo "Cloudflared processes stopped."
else
    echo "No cloudflared processes found."
fi

echo "Done."