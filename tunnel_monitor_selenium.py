import subprocess
import re
import time
import os
import signal
import sys
import requests
from datetime import datetime
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# WhatsApp contact name to send messages to
WHATSAPP_CONTACT = "Your Contact Name"  # Change this to your contact name

# URL to tunnel
TUNNEL_URL = "http://localhost:8080"  # Change this to your local service URL

# Path to Chrome browser (if not in standard location)
CHROME_PATH = None  # Set this if Chrome is in a non-standard location

# Global driver variable
driver = None

def setup_driver():
    """Set up and return a Chrome WebDriver with undetected_chromedriver"""
    global driver
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # For headless server environments
    if os.environ.get("HEADLESS", "False").lower() == "true":
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
    
    # Use custom Chrome path if specified
    if CHROME_PATH:
        print(f"Using Chrome binary at: {CHROME_PATH}")
        options.binary_location = CHROME_PATH
    else:
        # Try to find Chrome in common locations
        chrome_paths = [
            # Linux paths
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            # Windows paths
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"Using Chrome binary at: {path}")
                options.binary_location = path
                break
    
    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("Make sure Chrome is installed on your system.")
        sys.exit(1)

def send_whatsapp(msg):
    """Send a WhatsApp message using WhatsApp Web"""
    global driver
    
    try:
        if driver is None:
            driver = setup_driver()
            
            # Navigate to WhatsApp Web
            driver.get("https://web.whatsapp.com/")
            print("Please scan the QR code to log in to WhatsApp Web...")
            
            # Wait for the user to scan the QR code and for WhatsApp to load
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                print("Successfully logged in to WhatsApp Web")
            except TimeoutException:
                print("Timeout waiting for WhatsApp Web to load. Please try again.")
                driver.quit()
                driver = None
                return False
        
        # Search for the contact
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.clear()
        search_box.send_keys(WHATSAPP_CONTACT)
        time.sleep(2)
        
        # Click on the contact
        try:
            contact = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[@title="{WHATSAPP_CONTACT}"]'))
            )
            contact.click()
            time.sleep(1)
        except TimeoutException:
            print(f"Contact '{WHATSAPP_CONTACT}' not found. Please check the contact name.")
            return False
        
        # Find the message input box and send the message
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.clear()
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
        
        print(f"✅ Sent WhatsApp message: {msg}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp send failed: {e}")
        # If there's an error, try to reset the driver
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
        return False

def internet_available():
    """Check if internet connection is available"""
    try:
        requests.get("https://1.1.1.1", timeout=3)
        return True
    except:
        return False

def run_tunnel():
    """Run cloudflared tunnel and return the process"""
    # Determine the cloudflared executable name based on OS
    if os.name == 'nt':  # Windows
        cloudflared_cmd = "cloudflared-windows-amd64_2.exe"
    else:  # Linux/Mac
        cloudflared_cmd = "cloudflared-linux-amd64"
    
    # Check if the executable exists in the current directory
    if not os.path.exists(cloudflared_cmd):
        # Try using the system-installed cloudflared
        cloudflared_cmd = "cloudflared"
    
    # Start the cloudflared process
    process = subprocess.Popen(
        [cloudflared_cmd, "tunnel", "--url", "http://192.168.100.1:8096/web/#/home.html"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    # Monitor the output for the tunnel URL
    tunnel_url = None
    for line in process.stdout:
        line = line.strip()
        print(line)
        
        # Look for the tunnel URL in the output
        match = re.search(r"https://[-\w]+\.trycloudflare\.com", line)
        if match and not tunnel_url:
            tunnel_url = match.group(0)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🌐 New Tunnel Link ({timestamp}):\n{tunnel_url}"
            send_whatsapp(message)
    
    return process

def main():
    """Main function to run the tunnel monitor"""
    global driver
    
    print("Starting Cloudflare Tunnel Monitor with WhatsApp Web notifications")
    print(f"Messages will be sent to: {WHATSAPP_CONTACT}")
    print("Press Ctrl+C to exit")
    
    # Set up the WebDriver for WhatsApp Web
    try:
        driver = setup_driver()
        
        # Navigate to WhatsApp Web and wait for login
        driver.get("https://web.whatsapp.com/")
        print("\n===========================================================")
        print("IMPORTANT: Please scan the QR code to log in to WhatsApp Web")
        print("===========================================================\n")
        
        # Wait for the user to scan the QR code
        try:
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            print("Successfully logged in to WhatsApp Web")
        except TimeoutException:
            print("Timeout waiting for WhatsApp Web login. Exiting.")
            driver.quit()
            return
        
        # Main loop to monitor internet and run tunnel
        while True:
            if internet_available():
                print("Internet connection available. Starting tunnel...")
                proc = run_tunnel()
                
                # Monitor internet connection while tunnel is running
                while internet_available():
                    time.sleep(5)
                
                # Internet connection lost, terminate the tunnel process
                print("⚠ Internet disconnected — terminating tunnel...")
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                except:
                    pass
            else:
                print("No internet connection. Waiting...")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nExiting Cloudflare Tunnel Monitor...")
    finally:
        # Clean up
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()