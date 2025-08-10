#!/bin/bash

# Script to update the WhatsApp message template in the tunnel monitor script

# Check if a message template was provided
if [ $# -lt 1 ]; then
    echo "Error: Please provide a message template"
    echo "Usage: $0 <message_template>"
    echo "Example: $0 \"Your tunnel link is: {link}\""
    echo "Note: Use {link} as a placeholder for the tunnel URL"
    exit 1
fi

# Get the message template from the command line arguments
# This allows for spaces in the template
MESSAGE_TEMPLATE="$*"

# Check if the template contains the {link} placeholder
if [[ ! "$MESSAGE_TEMPLATE" == *"{link}"* ]]; then
    echo "Warning: Your message template does not contain the {link} placeholder."
    echo "The tunnel URL will not be included in the message."
    echo "Do you want to continue? (y/n)"
    read -r response
    if [[ "$response" != "y" && "$response" != "Y" ]]; then
        echo "Operation cancelled."
        exit 1
    fi
fi

echo "Updating WhatsApp message template to: $MESSAGE_TEMPLATE"

# Escape special characters for sed
ESCAPED_TEMPLATE=$(echo "$MESSAGE_TEMPLATE" | sed 's/[\&/]/\\&/g')

# Update the message template in the script
if [ "$(uname)" == "Darwin" ]; then
    # macOS version of sed
    sed -i '' "s|\(MESSAGE_TEMPLATE = \).*|\1\"$ESCAPED_TEMPLATE\"|" tunnel_monitor_selenium.py
else
    # Linux version of sed
    sed -i "s|\(MESSAGE_TEMPLATE = \).*|\1\"$ESCAPED_TEMPLATE\"|" tunnel_monitor_selenium.py
fi

echo "WhatsApp message template updated successfully."
echo "The tunnel monitor will now send messages with the template: $MESSAGE_TEMPLATE"