#!/usr/bin/env python3

"""
Test script for cloudflared functionality

This script tests if cloudflared is working properly by creating a simple tunnel
without the WhatsApp integration. It's useful for testing if cloudflared is
configured correctly before running the full tunnel monitor script.
"""

import os
import sys
import time
import subprocess
import platform
import signal
import re

# Default URL to tunnel
DEFAULT_TUNNEL_URL = "http://localhost:8080"

# Determine the default cloudflared path based on the operating system
if platform.system() == "Windows":
    DEFAULT_CLOUDFLARED_PATH = os.path.join(os.getcwd(), "cloudflared.exe")
elif platform.system() == "Darwin":  # macOS
    DEFAULT_CLOUDFLARED_PATH = "/usr/local/bin/cloudflared"
else:  # Linux
    DEFAULT_CLOUDFLARED_PATH = "/usr/local/bin/cloudflared"

# Use command line arguments or defaults
TUNNEL_URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TUNNEL_URL
CLOUDFLARED_PATH = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CLOUDFLARED_PATH

# Check if cloudflared exists at the specified path
def check_cloudflared():
    """Check if cloudflared exists and is executable"""
    if not os.path.isfile(CLOUDFLARED_PATH):
        print(f"❌ Error: cloudflared not found at {CLOUDFLARED_PATH}")
        print("Please install cloudflared or provide the correct path.")
        return False
    
    # Check if cloudflared is executable
    if not os.access(CLOUDFLARED_PATH, os.X_OK) and platform.system() != "Windows":
        print(f"❌ Error: cloudflared at {CLOUDFLARED_PATH} is not executable")
        print(f"Run: chmod +x {CLOUDFLARED_PATH}")
        return False
    
    # Check cloudflared version
    try:
        version_output = subprocess.check_output([CLOUDFLARED_PATH, "version"], 
                                               stderr=subprocess.STDOUT,
                                               universal_newlines=True)
        print(f"✅ cloudflared version: {version_output.strip()}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"❌ Error running cloudflared: {str(e)}")
        return False

# Run cloudflared tunnel
def run_tunnel():
    """Run cloudflared tunnel and extract the tunnel URL"""
    print(f"Starting cloudflared tunnel to {TUNNEL_URL}...")
    
    # Prepare the command
    cmd = [CLOUDFLARED_PATH, "tunnel", "--url", TUNNEL_URL]
    
    # Start the process
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("Waiting for tunnel to be established...")
        tunnel_url = None
        start_time = time.time()
        timeout = 30  # seconds
        
        # Read output line by line
        for line in iter(process.stdout.readline, ""):
            print(line.strip())
            
            # Look for the tunnel URL in the output
            if "https://" in line and "trycloudflare.com" in line:
                match = re.search(r'(https://[\w.-]+\.trycloudflare\.com)', line)
                if match:
                    tunnel_url = match.group(1)
                    print(f"\n✅ Tunnel established! URL: {tunnel_url}")
                    break
            
            # Check for timeout
            if time.time() - start_time > timeout:
                print("\n❌ Timeout waiting for tunnel URL")
                break
        
        # Keep the tunnel running for a while
        if tunnel_url:
            print("\nTunnel is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping tunnel...")
        else:
            print("\n❌ Failed to establish tunnel")
        
        # Terminate the process
        if platform.system() == "Windows":
            process.terminate()
        else:
            os.kill(process.pid, signal.SIGTERM)
        
        process.wait(timeout=5)
        print("Tunnel stopped.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== cloudflared Tunnel Test ===")
    print(f"URL to tunnel: {TUNNEL_URL}")
    print(f"cloudflared path: {CLOUDFLARED_PATH}")
    print("\nThis script will test if cloudflared is working properly.")
    print("Press Ctrl+C at any time to stop the tunnel.")
    print("\nStarting test...")
    
    if check_cloudflared():
        run_tunnel()
    
    print("\nTest completed.")