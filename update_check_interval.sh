#!/bin/bash

# Script to update the internet check interval in the tunnel monitor script

# Check if an interval was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a check interval in seconds"
    echo "Usage: $0 <interval_seconds>"
    echo "Example: $0 30"
    exit 1
fi

# Get the interval from the command line argument
INTERVAL="$1"

# Validate that the interval is a positive number
if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]]; then
    echo "Error: Interval must be a positive number"
    exit 1
fi

echo "Updating internet check interval to: $INTERVAL seconds"

# Update the interval in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(CHECK_INTERVAL = \).*|\1$INTERVAL|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(CHECK_INTERVAL = \).*|\1$INTERVAL|" tunnel_monitor_selenium.py
fi

echo "Internet check interval updated successfully."
echo "The tunnel monitor will now check internet connectivity every $INTERVAL seconds"