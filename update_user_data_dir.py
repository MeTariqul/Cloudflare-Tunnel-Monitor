#!/usr/bin/env python3

"""
Update Chrome User Data Directory Script

This script updates the USER_DATA_DIR variable in the tunnel_monitor_selenium.py file.
The user data directory is where Chrome stores profile data, including WhatsApp Web sessions.
"""

import os
import sys
import re
import platform

# The main script file
SCRIPT_FILE = "tunnel_monitor_selenium.py"

def validate_directory(directory):
    """Validate that the directory exists or can be created"""
    if not directory:
        print("❌ Error: Directory path cannot be empty")
        return False
    
    # Check if directory exists
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            print(f"❌ Error: {directory} exists but is not a directory")
            return False
        print(f"✅ Directory exists: {directory}")
    else:
        try:
            # Try to create the directory
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory: {str(e)}")
            return False
    
    return True

def update_user_data_dir(new_dir):
    """Update the USER_DATA_DIR variable in the script"""
    if not os.path.isfile(SCRIPT_FILE):
        print(f"❌ Error: Script file {SCRIPT_FILE} not found")
        return False
    
    # Read the script file
    with open(SCRIPT_FILE, 'r') as file:
        content = file.read()
    
    # Find the USER_DATA_DIR variable
    user_data_dir_pattern = r'USER_DATA_DIR\s*=\s*[\'"](.+?)[\'"](\s*#.*)?$'
    match = re.search(user_data_dir_pattern, content, re.MULTILINE)
    
    if not match:
        print("❌ Error: USER_DATA_DIR variable not found in the script")
        return False
    
    current_dir = match.group(1)
    print(f"Current USER_DATA_DIR: {current_dir}")
    
    # Escape backslashes for Windows paths in the replacement string
    if platform.system() == "Windows":
        new_dir_escaped = new_dir.replace('\\', '\\\\')
    else:
        new_dir_escaped = new_dir
    
    # Replace the USER_DATA_DIR value
    new_content = re.sub(
        user_data_dir_pattern,
        f'USER_DATA_DIR = "{new_dir_escaped}"{match.group(2) if match.group(2) else ""}',
        content,
        flags=re.MULTILINE
    )
    
    # Write the updated content back to the file
    with open(SCRIPT_FILE, 'w') as file:
        file.write(new_content)
    
    print(f"✅ Updated USER_DATA_DIR to: {new_dir}")
    return True

def main():
    """Main function"""
    print("=== Update Chrome User Data Directory ===\n")
    
    # Get the new directory from command line argument or prompt user
    if len(sys.argv) > 1:
        new_dir = sys.argv[1]
    else:
        # Suggest a default directory based on the OS
        if platform.system() == "Windows":
            default_dir = os.path.join(os.getcwd(), "chrome_user_data")
        elif platform.system() == "Darwin":  # macOS
            default_dir = os.path.expanduser("~/Library/Application Support/Chrome/TunnelMonitor")
        else:  # Linux
            default_dir = os.path.expanduser("~/.config/chrome-tunnel-monitor")
        
        print(f"Suggested directory: {default_dir}")
        new_dir = input("Enter new Chrome user data directory (or press Enter for suggested): ").strip()
        
        if not new_dir:
            new_dir = default_dir
    
    # Validate the directory
    if not validate_directory(new_dir):
        return 1
    
    # Update the script
    if update_user_data_dir(new_dir):
        print("\n✅ Chrome user data directory updated successfully")
        print("This directory will be used to store WhatsApp Web session data")
        return 0
    else:
        print("\n❌ Failed to update Chrome user data directory")
        return 1

if __name__ == "__main__":
    sys.exit(main())