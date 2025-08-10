#!/usr/bin/env python3

"""
Cloudflare Tunnel Monitor Web UI

A web-based user interface for the Cloudflare Tunnel Monitor with WhatsApp integration.
This application allows users to configure settings, start/stop the tunnel, and view statistics.
"""

import subprocess
import re
import time
import os
import signal
import sys
import threading
import queue
import json
import requests
from datetime import datetime
import platform
import logging
import socket
from pathlib import Path

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit

# Selenium imports for WhatsApp Web
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tunnel_monitor_web.log')
    ]
)
logger = logging.getLogger('tunnel_monitor_web')

# Default configuration
DEFAULT_CONFIG = {
    "whatsapp_contact": "+8801629866954",  # Default WhatsApp contact
    "tunnel_url": "http://192.168.100.1:8096/",  # Default tunnel URL
    "chrome_path": None,  # Chrome browser path
    "cloudflared_path": None,  # Cloudflared executable path
    "user_data_dir": os.path.join(os.getcwd(), "chrome_user_data"),  # Chrome user data directory
    "check_interval": 5,  # Internet check interval in seconds
    "max_retries": 3,  # Maximum number of retries
    "retry_delay": 5,  # Delay between retries in seconds
    "message_template": "🌐 New Tunnel Link ({timestamp}):\n{link}",  # Message template
    "debug_mode": False,  # Debug mode
    "headless_mode": False,  # Headless mode
}

# Statistics
STATS = {
    "tunnel_starts": 0,  # Number of times tunnel was started
    "messages_sent": 0,  # Number of WhatsApp messages sent
    "internet_disconnects": 0,  # Number of internet disconnections
    "last_tunnel_url": None,  # Last tunnel URL
    "start_time": None,  # Start time of the application
    "total_uptime": 0,  # Total uptime in seconds
    "current_status": "Stopped",  # Current status of the tunnel
}

# Global variables
driver = None
tunnel_process = None
stop_event = threading.Event()
log_queue = queue.Queue()
config_file = "tunnel_monitor_config.json"

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)

# Ping data
ping_data = {
    "last_ping_time": None,
    "ping_history": []
}

# Determine the base directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Utility functions
def log(message, level="info"):
    """Log a message to the console and the log queue"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "level": level
    }
    log_queue.put(log_entry)
    
    # Also log to the logger
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "success":
        logger.info(f"SUCCESS: {message}")
    elif level == "debug":
        logger.debug(message)
    else:
        logger.info(message)

def load_config():
    """Load configuration from file or create default"""
    config_path = os.path.join(BASE_DIR, config_file)
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Update with any missing default values
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                log(f"Configuration loaded from {config_path}")
                return config
    except Exception as e:
        log(f"Error loading configuration: {e}", level="error")
    
    # Create default configuration
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    return config

def save_config(config):
    """Save configuration to file"""
    config_path = os.path.join(BASE_DIR, config_file)
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        log(f"Configuration saved to {config_path}")
    except Exception as e:
        log(f"Error saving configuration: {e}", level="error")

def reset_config():
    """Reset configuration to default values"""
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    log("Configuration reset to default values", level="success")
    return config

def ping_host(host="1.1.1.1", timeout=1000):
    """Ping a host and return the response time in milliseconds
    
    Args:
        host (str): The host to ping
        timeout (int): Timeout in milliseconds
        
    Returns:
        float or None: Response time in milliseconds if successful, None if failed
    """
    # Determine the appropriate ping command based on the OS
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    
    # On Linux/Mac, timeout is in seconds, on Windows it's in milliseconds
    timeout_value = str(timeout) if platform.system().lower() == "windows" else str(timeout / 1000)
    
    try:
        # Hide the console output
        with open(os.devnull, 'w') as DEVNULL:
            # Run the ping command and capture output
            output = subprocess.check_output(
                ["ping", param, "1", timeout_param, timeout_value, host],
                stderr=DEVNULL,
                universal_newlines=True
            )
            
            # Parse the output to extract the time
            if platform.system().lower() == "windows":
                # Windows format: "Reply from 1.1.1.1: bytes=32 time=15ms TTL=57"
                match = re.search(r"time=([0-9]+)ms", output)
            else:
                # Linux/Mac format: "64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=14.5 ms"
                match = re.search(r"time=([0-9.]+) ms", output)
                
            if match:
                return float(match.group(1))
            return 0.0  # Successful ping but couldn't parse time
    except subprocess.CalledProcessError:
        # Ping failed
        return None
    except Exception as e:
        logger.error(f"Error pinging {host}: {e}")
        return None

def internet_available():
    """Check if internet connection is available"""
    try:
        # Try to ping Cloudflare's DNS
        result = ping_host("1.1.1.1", 3000)
        return result is not None
    except:
        # Fallback to HTTP request if ping fails
        try:
            requests.get("https://1.1.1.1", timeout=3)
            return True
        except:
            return False

def setup_driver(config):
    """Set up and return a Chrome WebDriver with undetected_chromedriver"""
    global driver
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # For headless mode
    if config["headless_mode"]:
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
    
    # Use custom Chrome path if specified
    if config["chrome_path"] and os.path.exists(config["chrome_path"]):
        log(f"Using Chrome binary at: {config['chrome_path']}")
        options.binary_location = config["chrome_path"]
    
    # Use custom user data directory if specified
    if config["user_data_dir"]:
        user_data_dir = config["user_data_dir"]
        if not os.path.isabs(user_data_dir):
            user_data_dir = os.path.join(BASE_DIR, user_data_dir)
        
        # Ensure the directory exists
        os.makedirs(user_data_dir, exist_ok=True)
        
        log(f"Using Chrome user data directory: {user_data_dir}")
        options.add_argument(f"--user-data-dir={user_data_dir}")
    
    try:
        driver = uc.Chrome(options=options)
        return driver
    except Exception as e:
        log(f"Error setting up Chrome driver: {e}", level="error")
        log("Make sure Chrome is installed on your system.")
        return None

def send_whatsapp(msg, config):
    """Send a WhatsApp message using WhatsApp Web"""
    global driver
    
    try:
        if driver is None:
            driver = setup_driver(config)
            if driver is None:
                return False
            
            # Navigate to WhatsApp Web
            driver.get("https://web.whatsapp.com/")
            log("Please scan the QR code to log in to WhatsApp Web...")
            
            # Wait for the user to scan the QR code and for WhatsApp to load
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                log("Successfully logged in to WhatsApp Web", level="success")
            except TimeoutException:
                log("Timeout waiting for WhatsApp Web to load. Please try again.", level="error")
                driver.quit()
                driver = None
                return False
        
        # Search for the contact
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.clear()
        search_box.send_keys(config["whatsapp_contact"])
        time.sleep(2)
        
        # Click on the contact
        try:
            contact = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f'//span[@title="{config["whatsapp_contact"]}"]'))
            )
            contact.click()
            time.sleep(1)
        except TimeoutException:
            log(f"Contact '{config['whatsapp_contact']}' not found. Please check the contact name.", level="error")
            return False
        
        # Find the message input box and send the message
        message_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        message_box.clear()
        message_box.send_keys(msg)
        message_box.send_keys(Keys.ENTER)
        
        log(f"Sent WhatsApp message: {msg}", level="success")
        STATS["messages_sent"] += 1
        return True
    except Exception as e:
        log(f"WhatsApp send failed: {e}", level="error")
        # If there's an error, try to reset the driver
        if driver:
            try:
                driver.quit()
            except:
                pass
            driver = None
        return False

def run_tunnel(config):
    """Run cloudflared tunnel and return the process"""
    global tunnel_process
    
    # Determine the cloudflared executable
    cloudflared_cmd = config["cloudflared_path"]
    if not cloudflared_cmd or not os.path.exists(cloudflared_cmd):
        # Try using the system-installed cloudflared
        if os.name == 'nt':  # Windows
            cloudflared_cmd = "cloudflared.exe"
        else:  # Linux/Mac
            cloudflared_cmd = "cloudflared"
    
    log(f"Starting cloudflared tunnel to {config['tunnel_url']}")
    
    # Start the cloudflared process
    try:
        tunnel_process = subprocess.Popen(
            [cloudflared_cmd, "tunnel", "--url", config['tunnel_url']],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            bufsize=1, universal_newlines=True
        )
        
        STATS["tunnel_starts"] += 1
        STATS["current_status"] = "Running"
        
        # Create a thread to monitor the output
        def monitor_output():
            tunnel_url = None
            for line in iter(tunnel_process.stdout.readline, ''):
                if stop_event.is_set():
                    break
                    
                line = line.strip()
                log(f"Cloudflared: {line}", level="debug" if config["debug_mode"] else "info")
                
                # Look for the tunnel URL in the output
                match = re.search(r"https://[-\w]+\.trycloudflare\.com", line)
                if match and not tunnel_url:
                    tunnel_url = match.group(0)
                    STATS["last_tunnel_url"] = tunnel_url
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Format the message using the template
                    message = config["message_template"].format(
                        timestamp=timestamp,
                        link=tunnel_url
                    )
                    
                    # Send the message via WhatsApp
                    send_whatsapp(message, config)
                    
                    # Emit the tunnel URL to connected clients
                    socketio.emit('tunnel_url', {'url': tunnel_url})
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return tunnel_process
    except Exception as e:
        log(f"Error starting cloudflared: {e}", level="error")
        return None

def stop_tunnel():
    """Stop the cloudflared tunnel process"""
    global tunnel_process
    if tunnel_process:
        log("Stopping cloudflared tunnel...")
        try:
            if os.name == 'nt':  # Windows
                tunnel_process.terminate()
            else:  # Linux/Mac
                os.kill(tunnel_process.pid, signal.SIGTERM)
            tunnel_process.wait(timeout=5)
            log("Cloudflared tunnel stopped", level="success")
        except Exception as e:
            log(f"Error stopping cloudflared: {e}", level="error")
            # Force kill if normal termination fails
            try:
                if os.name == 'nt':  # Windows
                    os.system(f"taskkill /F /PID {tunnel_process.pid}")
                else:  # Linux/Mac
                    os.kill(tunnel_process.pid, signal.SIGKILL)
                log("Cloudflared tunnel force-stopped", level="warning")
            except:
                pass
        tunnel_process = None
        STATS["current_status"] = "Stopped"

def ping_monitor_thread():
    """Thread function to monitor ping and emit data to clients"""
    global ping_data
    
    # Keep track of the last 60 ping times (1 minute at 1 ping per second)
    max_history_size = 60
    
    while not stop_event.is_set():
        # Get the current ping time
        ping_time = ping_host("1.1.1.1")
        
        # Update ping data
        ping_data["last_ping_time"] = ping_time
        
        # Add to history and maintain max size
        current_time = time.time()  # Unix timestamp
        ping_data["ping_history"].append({"timestamp": current_time, "ping_time": ping_time})
        if len(ping_data["ping_history"]) > max_history_size:
            ping_data["ping_history"].pop(0)
        
        # Emit the ping data to all connected clients
        socketio.emit('ping_data', {
            'last_ping_time': ping_time,
            'ping_history': [ping_data["ping_history"][-1]]  # Just send the latest entry
        })
        
        # Wait for 1 second before the next ping
        for _ in range(10):  # Check stop_event every 0.1 seconds
            if stop_event.is_set():
                break
            time.sleep(0.1)

def monitor_thread_func(config):
    """Main monitoring thread function"""
    global tunnel_process
    
    STATS["start_time"] = datetime.now()
    retry_count = 0
    
    # Start the ping monitor thread
    ping_thread = threading.Thread(target=ping_monitor_thread)
    ping_thread.daemon = True
    ping_thread.start()
    
    while not stop_event.is_set():
        # Check internet connection
        if internet_available():
            # If tunnel is not running, start it
            if tunnel_process is None or tunnel_process.poll() is not None:
                # Reset retry count on successful internet connection
                retry_count = 0
                tunnel_process = run_tunnel(config)
        else:
            # Internet is down
            log("Internet connection lost", level="warning")
            STATS["internet_disconnects"] += 1
            
            # Stop the tunnel if it's running
            if tunnel_process and tunnel_process.poll() is None:
                stop_tunnel()
            
            # Retry with backoff
            retry_count += 1
            if retry_count <= config["max_retries"]:
                retry_delay = config["retry_delay"] * retry_count
                log(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{config['max_retries']})")
                
                # Wait for the retry delay, checking for stop event
                for _ in range(retry_delay):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
            else:
                log(f"Maximum retries ({config['max_retries']}) exceeded. Waiting for internet connection...")
                # Wait for internet to come back
                while not internet_available() and not stop_event.is_set():
                    time.sleep(config["check_interval"])
                
                # Reset retry count when internet is back
                if not stop_event.is_set():
                    log("Internet connection restored", level="success")
                    retry_count = 0
        
        # Update uptime
        if STATS["start_time"]:
            STATS["total_uptime"] = (datetime.now() - STATS["start_time"]).total_seconds()
        
        # Wait for the check interval
        for _ in range(config["check_interval"]):
            if stop_event.is_set():
                break
            time.sleep(1)

def cleanup():
    """Clean up resources before exiting"""
    stop_tunnel()
    
    global driver
    if driver:
        try:
            log("Closing Chrome WebDriver...")
            driver.quit()
        except:
            pass
        driver = None

# Flask routes
@app.route('/')
def index():
    """Render the main dashboard page"""
    config = load_config()
    return render_template('index.html', config=config, stats=STATS)

@app.route('/settings')
def settings():
    """Render the settings page"""
    config = load_config()
    return render_template('settings.html', config=config)

@app.route('/logs')
def logs():
    """Render the logs page"""
    return render_template('logs.html')

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the tunnel monitor"""
    global stop_event
    config = load_config()
    
    if tunnel_process and tunnel_process.poll() is None:
        return jsonify({"status": "error", "message": "Tunnel is already running"})
    
    # Reset the stop event
    stop_event.clear()
    
    # Start the monitor thread
    monitor_thread = threading.Thread(target=monitor_thread_func, args=(config,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    log("Monitor started", level="success")
    return jsonify({"status": "success", "message": "Tunnel monitor started"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the tunnel monitor"""
    global stop_event
    
    # Set the stop event to signal threads to exit
    stop_event.set()
    
    # Stop the tunnel
    stop_tunnel()
    
    log("Monitor stopped", level="warning")
    return jsonify({"status": "success", "message": "Tunnel monitor stopped"})

@app.route('/api/test_whatsapp', methods=['POST'])
def api_test_whatsapp():
    """Test WhatsApp message sending"""
    config = load_config()
    
    # Send a test message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"🧪 Test Message ({timestamp})"
    
    if send_whatsapp(message, config):
        return jsonify({"status": "success", "message": "Test message sent successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to send test message"})

@app.route('/api/save_settings', methods=['POST'])
def api_save_settings():
    """Save settings"""
    config = load_config()
    
    # Update configuration with form data
    config["whatsapp_contact"] = request.form.get("whatsapp_contact", config["whatsapp_contact"])
    config["tunnel_url"] = request.form.get("tunnel_url", config["tunnel_url"])
    config["chrome_path"] = request.form.get("chrome_path", config["chrome_path"])
    config["cloudflared_path"] = request.form.get("cloudflared_path", config["cloudflared_path"])
    config["user_data_dir"] = request.form.get("user_data_dir", config["user_data_dir"])
    config["check_interval"] = int(request.form.get("check_interval", config["check_interval"]))
    config["max_retries"] = int(request.form.get("max_retries", config["max_retries"]))
    config["retry_delay"] = int(request.form.get("retry_delay", config["retry_delay"]))
    config["message_template"] = request.form.get("message_template", config["message_template"])
    config["debug_mode"] = request.form.get("debug_mode") == "on"
    config["headless_mode"] = request.form.get("headless_mode") == "on"
    
    # Save the updated configuration
    save_config(config)
    
    flash("Settings saved successfully", "success")
    return redirect(url_for('settings'))

@app.route('/api/stats')
def api_stats():
    """Get current statistics"""
    # Update uptime if the monitor is running
    if STATS["start_time"]:
        STATS["total_uptime"] = (datetime.now() - STATS["start_time"]).total_seconds()
    
    return jsonify(STATS)

@app.route('/api/logs')
def api_logs():
    """Get logs"""
    logs = []
    while not log_queue.empty():
        try:
            logs.append(log_queue.get_nowait())
        except queue.Empty:
            break
    
    return jsonify(logs)

@app.route('/api/settings')
def api_settings():
    """Get current settings"""
    config = load_config()
    return jsonify(config)

@app.route('/api/settings', methods=['POST'])
def api_settings_update():
    """Update settings via JSON"""
    config = load_config()
    
    # Get JSON data from request
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"})
    
    # Update configuration with JSON data
    for key in data:
        if key in config:
            config[key] = data[key]
    
    # Save the updated configuration
    save_config(config)
    
    return jsonify({"status": "success", "message": "Settings saved successfully"})

@app.route('/api/settings/reset', methods=['POST'])
def api_settings_reset():
    """Reset settings to default values"""
    # Create default configuration
    config = DEFAULT_CONFIG.copy()
    
    # Save the default configuration
    save_config(config)
    
    log("Settings reset to defaults", level="warning")
    return jsonify({"status": "success", "message": "Settings reset to defaults"})

@app.route('/api/ping')
def api_ping():
    """Get current ping data"""
    global ping_data
    
    # If ping monitoring hasn't started yet, return None
    if ping_data["last_ping_time"] is None:
        return jsonify({"last_ping_time": None, "ping_history": []})
    
    return jsonify({
        "last_ping_time": ping_data["last_ping_time"],
        "ping_history": ping_data["ping_history"]
    })

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'status': STATS["current_status"]})
    if STATS["last_tunnel_url"]:
        emit('tunnel_url', {'url': STATS["last_tunnel_url"]})
    
    # Send current internet status
    is_connected = internet_available()
    emit('internet_status', {'status': is_connected})
    
    # Send current ping data if available
    global ping_data
    if ping_data["last_ping_time"] is not None:
        emit('ping_data', {
            'last_ping_time': ping_data["last_ping_time"],
            'ping_history': ping_data["ping_history"]
        })

# Main function
def main():
    """Main function"""
    try:
        # Load configuration
        config = load_config()
        
        # Get available port
        port = 5000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while port < 5100:
            try:
                s.bind(('localhost', port))
                s.close()
                break
            except socket.error:
                port += 1
        
        # Start the web server
        host = '0.0.0.0'  # Listen on all interfaces
        log(f"Starting web server on http://{host}:{port}")
        socketio.run(app, host=host, port=port, debug=config["debug_mode"])
    except Exception as e:
        log(f"Error: {e}", level="error")
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    main()