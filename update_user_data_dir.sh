#!/bin/bash

# Script to update the Chrome user data directory

echo "Updating Chrome user data directory..."

# Check if a directory was provided
if [ -z "$1" ]; then
    echo "No directory provided. Will use default or prompt for input."
    DIR_PATH=""
else
    echo "Using provided directory: $1"
    DIR_PATH="$1"
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Using existing virtual environment..."
fi

# Activate virtual environment
source venv/bin/activate

# Run the update script
if [ -z "$DIR_PATH" ]; then
    python update_user_data_dir.py
else
    python update_user_data_dir.py "$DIR_PATH"
fi

# Deactivate virtual environment
deactivate