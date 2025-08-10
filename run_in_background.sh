#!/bin/bash

# Script to run the tunnel monitor in the background using nohup

echo "Starting Cloudflare Tunnel Monitor in the background..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Install dependencies
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Get current timestamp for log file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/tunnel_monitor_$TIMESTAMP.log"

# Run the tunnel monitor in the background
echo "Running tunnel monitor in the background..."
echo "Log file: $LOG_FILE"

# Activate virtual environment and run the script with nohup
nohup bash -c "source venv/bin/activate && python tunnel_monitor_selenium.py" > "$LOG_FILE" 2>&1 &

# Save the process ID
PID=$!
echo "$PID" > tunnel_monitor.pid

echo "Tunnel monitor started with PID: $PID"
echo "To view the logs: tail -f $LOG_FILE"
echo "To stop the process: kill $(cat tunnel_monitor.pid)"