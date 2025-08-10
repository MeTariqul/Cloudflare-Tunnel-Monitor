#!/bin/bash

# Script to test cloudflared functionality

echo "Testing cloudflared functionality..."

# Check if a URL was provided
if [ -z "$1" ]; then
    echo "Using default URL: http://localhost:8080"
    URL="http://localhost:8080"
else
    echo "Using provided URL: $1"
    URL="$1"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Install dependencies
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install requests
else
    echo "Using existing virtual environment..."
    source venv/bin/activate
fi

# Run the test script
echo "Running cloudflared test..."
echo ""
python test_cloudflared.py "$URL"

# Deactivate virtual environment
deactivate