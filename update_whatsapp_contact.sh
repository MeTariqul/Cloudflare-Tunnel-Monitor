#!/bin/bash

# Script to update the WhatsApp contact name in the tunnel monitor script

# Check if a contact name was provided
if [ $# -ne 1 ]; then
    echo "Error: Please provide a WhatsApp contact name"
    echo "Usage: $0 <contact_name>"
    echo "Example: $0 \"John Doe\""
    exit 1
fi

# Get the contact name from the command line argument
CONTACT_NAME="$1"

echo "Updating WhatsApp contact name to: $CONTACT_NAME"

# Update the contact name in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(WHATSAPP_CONTACT = \).*|\1\"$CONTACT_NAME\"|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(WHATSAPP_CONTACT = \).*|\1\"$CONTACT_NAME\"|" tunnel_monitor_selenium.py
fi

echo "WhatsApp contact name updated successfully."
echo "The tunnel monitor will now send messages to: $CONTACT_NAME"