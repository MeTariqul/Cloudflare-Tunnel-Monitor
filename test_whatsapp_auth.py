#!/usr/bin/env python3

"""
Test script for WhatsApp Web authentication

This script opens WhatsApp Web and allows you to scan the QR code to authenticate.
It's useful for testing if the WhatsApp Web authentication is working properly
before running the full tunnel monitor script.
"""

import os
import sys
import time
import platform
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
HEADLESS_MODE = False  # Set to False to see the browser window
QR_TIMEOUT = 60  # Seconds to wait for QR code scanning

# Determine the default Chrome path based on the operating system
if platform.system() == "Windows":
    DEFAULT_CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
elif platform.system() == "Darwin":  # macOS
    DEFAULT_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else:  # Linux
    DEFAULT_CHROME_PATH = "/usr/bin/google-chrome"

# Use the default Chrome path or allow it to be specified as a command-line argument
CHROME_PATH = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHROME_PATH

def setup_driver():
    """Set up and return a Chrome WebDriver instance"""
    print(f"Using Chrome at: {CHROME_PATH}")
    
    options = uc.ChromeOptions()
    options.binary_location = CHROME_PATH
    
    if HEADLESS_MODE:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    
    # Add user data directory to persist WhatsApp Web session
    user_data_dir = os.path.join(os.getcwd(), "whatsapp_user_data")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    print("Initializing Chrome WebDriver...")
    driver = uc.Chrome(options=options)
    return driver

def test_whatsapp_auth():
    """Test WhatsApp Web authentication"""
    driver = None
    try:
        driver = setup_driver()
        
        print("Opening WhatsApp Web...")
        driver.get("https://web.whatsapp.com/")
        
        # Wait for QR code or main WhatsApp interface
        print(f"Waiting for QR code or WhatsApp interface (timeout: {QR_TIMEOUT} seconds)...")
        
        # Check if already authenticated
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            print("\n✅ Already authenticated to WhatsApp Web!")
            print("You can now run the tunnel monitor script.")
            return True
        except:
            # Not authenticated yet, look for QR code
            try:
                qr_code = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//canvas'))
                )
                print("\n⚠️ QR code detected. Please scan it with your WhatsApp mobile app.")
                
                if HEADLESS_MODE:
                    # Save QR code as image in headless mode
                    print("Saving QR code as 'whatsapp_qr.png'...")
                    qr_code.screenshot("whatsapp_qr.png")
                    print("Please scan the QR code image with your WhatsApp mobile app.")
                
                # Wait for authentication to complete
                WebDriverWait(driver, QR_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )
                print("\n✅ Successfully authenticated to WhatsApp Web!")
                print("You can now run the tunnel monitor script.")
                return True
            except:
                print("\n❌ Authentication failed or timed out.")
                print("Please try again or check your internet connection.")
                return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()

if __name__ == "__main__":
    print("=== WhatsApp Web Authentication Test ===")
    print("This script will open WhatsApp Web and allow you to scan the QR code.")
    print("It's useful for testing if the WhatsApp Web authentication is working properly.")
    print("\nPress Ctrl+C at any time to exit.")
    print("\nStarting test...")
    
    try:
        test_whatsapp_auth()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    
    print("\nTest completed.")