#!/bin/bash

# Script to update the retry settings in the tunnel monitor script

# Check if arguments were provided
if [ $# -ne 2 ]; then
    echo "Error: Please provide both retry count and retry delay"
    echo "Usage: $0 <retry_count> <retry_delay_seconds>"
    echo "Example: $0 3 5"
    exit 1
fi

# Get the retry count and delay from the command line arguments
RETRY_COUNT="$1"
RETRY_DELAY="$2"

# Validate that the retry count is a positive number
if ! [[ "$RETRY_COUNT" =~ ^[0-9]+$ ]]; then
    echo "Error: Retry count must be a positive number"
    exit 1
fi

# Validate that the retry delay is a positive number
if ! [[ "$RETRY_DELAY" =~ ^[0-9]+$ ]]; then
    echo "Error: Retry delay must be a positive number"
    exit 1
fi

echo "Updating retry settings to: $RETRY_COUNT attempts with $RETRY_DELAY seconds delay"

# Update the retry settings in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(MAX_RETRIES = \).*|\1$RETRY_COUNT|" tunnel_monitor_selenium.py
    sed -i '' "s|\(RETRY_DELAY = \).*|\1$RETRY_DELAY|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(MAX_RETRIES = \).*|\1$RETRY_COUNT|" tunnel_monitor_selenium.py
    sed -i "s|\(RETRY_DELAY = \).*|\1$RETRY_DELAY|" tunnel_monitor_selenium.py
fi

echo "Retry settings updated successfully."
echo "The tunnel monitor will now retry $RETRY_COUNT times with $RETRY_DELAY seconds delay between attempts"