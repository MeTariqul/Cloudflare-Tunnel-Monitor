#!/bin/bash

# Script to update the tunnel URL in the tunnel monitor script

# Check if a URL was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a URL to tunnel"
    echo "Usage: $0 <url>"
    echo "Example: $0 http://localhost:8080"
    exit 1
fi

# Get the URL from the command line argument
URL="$1"

echo "Updating tunnel URL to: $URL"

# Update the URL in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(TUNNEL_URL = \).*|\1\"$URL\"|" tunnel_monitor_selenium.py
    sed -i '' "s|\(\[cloudflared_cmd, \"tunnel\", \"--url\", \).*\]|\1\"$URL\"]|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(TUNNEL_URL = \).*|\1\"$URL\"|" tunnel_monitor_selenium.py
    sed -i "s|\(\[cloudflared_cmd, \"tunnel\", \"--url\", \).*\]|\1\"$URL\"]|" tunnel_monitor_selenium.py
fi

echo "Tunnel URL updated successfully."
echo "The tunnel monitor will now create a tunnel to: $URL"