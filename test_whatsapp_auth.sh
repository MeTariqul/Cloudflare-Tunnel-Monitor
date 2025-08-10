#!/bin/bash

# Script to test WhatsApp Web authentication

echo "Testing WhatsApp Web authentication..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Install dependencies
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Using existing virtual environment..."
    source venv/bin/activate
fi

# Run the test script
echo "Running WhatsApp Web authentication test..."
echo ""
python test_whatsapp_auth.py

# Deactivate virtual environment
deactivate