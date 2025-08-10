#!/bin/bash

echo "Starting Cloudflare Tunnel Monitor Web UI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if web_ui directory exists
if [ ! -d "web_ui" ]; then
    echo "web_ui directory not found. Please make sure you're running this script from the correct location."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install -r web_ui/requirements.txt

# Start the web UI
echo "Starting web UI..."
cd web_ui
python3 app.py

# Deactivate virtual environment when done (this will only execute if app.py exits)
cd ..
deactivate