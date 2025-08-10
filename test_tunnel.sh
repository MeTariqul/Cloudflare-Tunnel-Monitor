#!/bin/bash

# Script to test Cloudflare tunnel without WhatsApp integration

echo "Testing Cloudflare tunnel..."

# Determine the cloudflared executable
if [ -f "cloudflared-linux-amd64" ]; then
    CLOUDFLARED="./cloudflared-linux-amd64"
elif command -v cloudflared &> /dev/null; then
    CLOUDFLARED="cloudflared"
else
    echo "Error: cloudflared not found. Please install it first."
    echo "You can download it using:"
    echo "curl -L --output cloudflared-linux-amd64 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
    echo "chmod +x cloudflared-linux-amd64"
    exit 1
fi

# Default URL to tunnel
URL="http://localhost:8080"

# Check if a URL was provided as an argument
if [ $# -eq 1 ]; then
    URL="$1"
    echo "Using provided URL: $URL"
else
    echo "Using default URL: $URL"
    echo "You can specify a different URL as an argument: ./test_tunnel.sh http://your-service-url"
fi

echo "Starting Cloudflare tunnel to $URL..."
echo "Press Ctrl+C to stop the tunnel"

# Run the tunnel
$CLOUDFLARED tunnel --url "$URL"