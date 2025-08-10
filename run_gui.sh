#!/bin/bash

echo "Starting Cloudflare Tunnel Monitor GUI..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.6 or higher."
    read -p "Press Enter to continue..."
    exit 1
fi

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        read -p "Press Enter to continue..."
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
pip show selenium &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install selenium undetected-chromedriver requests
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        read -p "Press Enter to continue..."
        exit 1
    fi
fi

# Run the GUI application
echo "Starting GUI application..."
python3 tunnel_monitor_gui.py

# Deactivate virtual environment
deactivate

read -p "Press Enter to continue..."