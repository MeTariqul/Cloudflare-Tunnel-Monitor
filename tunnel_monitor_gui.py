#!/usr/bin/env python3

"""
Cloudflare Tunnel Monitor GUI

A graphical user interface for the Cloudflare Tunnel Monitor.
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
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import qrcode
from PIL import Image, ImageTk

# Default configuration
DEFAULT_CONFIG = {
    "tunnel_url": "http://192.168.100.1:8096/",  # Default tunnel URL
    "chrome_path": None,  # Chrome browser path
    "cloudflared_path": None,  # Cloudflared executable path
    "user_data_dir": os.path.join(os.getcwd(), "chrome_user_data"),  # Chrome user data directory
    "check_interval": 5,  # Internet check interval in seconds
    "max_retries": 3,  # Maximum number of retries
    "retry_delay": 5,  # Delay between retries in seconds
    "ping_test_url": "1.1.1.1",  # URL or IP to ping for connectivity tests
    "debug_mode": False,  # Debug mode
    "headless_mode": False,  # Headless mode
}

# Statistics
STATS = {
    "tunnel_starts": 0,  # Number of times tunnel was started
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

# GUI colors - Modern color scheme with better contrast
COLORS = {
    "bg_dark": "#1E293B",  # Darker background for main areas
    "bg_light": "#334155",  # Lighter background for content areas
    "bg_input": "#475569",  # Background for input fields
    "text": "#F1F5F9",      # Primary text color
    "text_secondary": "#CBD5E1",  # Secondary text color
    "accent": "#38BDF8",    # Primary accent color
    "accent_hover": "#0EA5E9",  # Accent color on hover
    "success": "#4ADE80",   # Success indicators
    "warning": "#FACC15",   # Warning indicators
    "error": "#F87171",     # Error indicators
    "button": "#0284C7",    # Button color
    "button_hover": "#0369A1",  # Button hover color
    "border": "#64748B",    # Border color
    "highlight": "#7DD3FC",  # Highlight color
}

# Load configuration
def load_config():
    """Load configuration from file"""
    config = DEFAULT_CONFIG.copy()
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                saved_config = json.load(f)
                config.update(saved_config)
            log(f"Configuration loaded from {config_file}")
    except Exception as e:
        log(f"Error loading configuration: {e}", level="error")
    return config

# Save configuration
def save_config(config):
    """Save configuration to file"""
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        log(f"Configuration saved to {config_file}")
        return True
    except Exception as e:
        log(f"Error saving configuration: {e}", level="error")
        return False

# Logging function
def log(message, level="info"):
    """Add a log message to the queue"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "level": level
    }
    log_queue.put(log_entry)
    print(f"[{timestamp}] [{level.upper()}] {message}")

# Setup Chrome WebDriver
def setup_driver(config):
    """Set up and return a Chrome WebDriver with undetected_chromedriver"""
    global driver
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        # Set user data directory
        if config["user_data_dir"]:
            os.makedirs(config["user_data_dir"], exist_ok=True)
            options.add_argument(f"--user-data-dir={config['user_data_dir']}")
        
        # For headless mode
        if config["headless_mode"]:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
        
        # Use custom Chrome path if specified
        if config["chrome_path"]:
            log(f"Using Chrome binary at: {config['chrome_path']}")
            options.binary_location = config["chrome_path"]
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
                    log(f"Using Chrome binary at: {path}")
                    options.binary_location = path
                    break
        
        driver = uc.Chrome(options=options)
        log("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        log(f"Error setting up Chrome driver: {e}", level="error")
        return None

# Check internet connection
def internet_available():
    """Check if internet connection is available"""
    try:
        requests.get("https://1.1.1.1", timeout=3)
        return True
    except:
        return False

# Ping test function
def ping_test(host=None):
    """Test connectivity to a host"""
    if host is None:
        host = "1.1.1.1"
    
    try:
        response = requests.get(f"http://{host}", timeout=3)
        return response.status_code < 400
    except:
        return False
    
            # Wait for the user to scan the QR code and for WhatsApp to load
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
                )
                log("Successfully logged in to WhatsApp Web", level="success")
            except TimeoutException:
                log("Timeout waiting for WhatsApp Web to load", level="error")
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
            log(f"Contact '{config['whatsapp_contact']}' not found", level="error")
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

# Run Cloudflared tunnel
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
                    
                        # Log the new tunnel URL
                    log(f"New tunnel URL: {tunnel_url}", level="success")
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return tunnel_process
    except Exception as e:
        log(f"Error starting cloudflared: {e}", level="error")
        return None

# Stop the tunnel
def stop_tunnel():
    """Stop the cloudflared tunnel process"""
    global tunnel_process, stop_event
    
    stop_event.set()
    
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
            log(f"Error stopping tunnel: {e}", level="error")
            try:
                if os.name == 'nt':  # Windows
                    os.system(f"taskkill /F /PID {tunnel_process.pid}")
                else:  # Linux/Mac
                    os.kill(tunnel_process.pid, signal.SIGKILL)
                log("Tunnel process forcefully terminated", level="warning")
            except:
                pass
        
        tunnel_process = None
    
    STATS["current_status"] = "Stopped"
    stop_event.clear()

# Monitor thread function
def monitor_thread_func(config, update_callback):
    """Thread function to monitor internet and run tunnel"""
    global stop_event
    
    log("Monitor thread started")
    STATS["start_time"] = datetime.now()
    STATS["last_check_time"] = datetime.now()
    
    # Initialize retry counter
    retry_count = 0
    max_retries = int(config["max_retries"])
    retry_delay = int(config["retry_delay"])
    check_interval = int(config["check_interval"])
    
    while not stop_event.is_set():
        try:
            # Update last check time
            STATS["last_check_time"] = datetime.now()
            
            # Check internet connection
            internet_connected = internet_available()
            
            if internet_connected:
                # Reset retry counter when internet is available
                retry_count = 0
                
                # Start tunnel if not running
                if STATS["current_status"] != "Running":
                    log("Internet connection available. Starting tunnel...", level="success")
                    run_tunnel(config)
                
                # Update statistics
                if STATS["start_time"]:
                    current_time = datetime.now()
                    STATS["total_uptime"] = (current_time - STATS["start_time"]).total_seconds()
            else:
                # Handle internet disconnection
                if STATS["current_status"] == "Running":
                    log("Internet disconnected", level="warning")
                    STATS["internet_disconnects"] += 1
                    stop_tunnel()
                else:
                    # Implement retry logic with backoff
                    retry_count += 1
                    if retry_count <= max_retries:
                        log(f"No internet connection. Retry {retry_count}/{max_retries}...", level="warning")
                    else:
                        log("Max retries reached. Waiting for next check interval...", level="warning")
                        retry_count = max_retries  # Cap at max to prevent overflow
            
            # Call the update callback to refresh the UI more frequently
            if update_callback:
                update_callback()
            
            # More responsive sleep that updates UI periodically
            sleep_interval = retry_delay if not internet_connected and retry_count < max_retries else check_interval
            for _ in range(sleep_interval):
                if stop_event.is_set():
                    break
                time.sleep(1)
                
                # Update UI every second for more responsive feel
                if _ % 5 == 0 and update_callback:  # Update every 5 seconds during wait
                    update_callback()
        
        except Exception as e:
            log(f"Error in monitor thread: {e}", level="error")
            # Prevent CPU spinning in case of repeated errors
            time.sleep(5)
    
    log("Monitor thread stopped", level="warning")

# Clean up resources
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

# Main GUI class
class TunnelMonitorGUI(tk.Tk):
    def on_resize(self, event):
        """Handle window resize events for responsive layout"""
        # Only respond to the root window's resize events
        if event.widget == self:
            # Update layout if needed based on new window size
            width = event.width
            height = event.height
            
            # You can adjust layouts based on window size here
            # For example, change column widths, font sizes, etc.
            pass
    def __init__(self):
        super().__init__()
        
        self.title("Cloudflare Tunnel Monitor")
        self.geometry("1000x750")
        self.minsize(800, 600)  # Set minimum window size for responsiveness
        self.configure(bg=COLORS["bg_dark"])
        
        # Load configuration
        self.config = load_config()
        
        # Set icon
        try:
            self.iconbitmap("icon.ico")
        except:
            pass
        
        # Create a style for ttk widgets
        self.style = ttk.Style(self)
        
        # Configure the theme
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure styles for different widget types
        self.style.configure("TFrame", background=COLORS["bg_dark"])
        self.style.configure("ContentFrame.TFrame", background=COLORS["bg_light"], relief="flat", borderwidth=0)
        
        self.style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text"], font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground=COLORS["accent"], background=COLORS["bg_light"])
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 12, "bold"), foreground=COLORS["text"])
        self.style.configure("Status.TLabel", font=("Segoe UI", 10), foreground=COLORS["text_secondary"], background=COLORS["bg_light"])
        
        self.style.configure("TButton", 
                          background=COLORS["button"], 
                          foreground=COLORS["text"],
                          borderwidth=1,
                          focusthickness=3,
                          focuscolor=COLORS["accent"],
                          font=("Segoe UI", 10))
        self.style.map("TButton",
                     background=[('active', COLORS["button_hover"])],
                     foreground=[('active', COLORS["text"])])
        
        self.style.configure("Accent.TButton", 
                          background=COLORS["accent"], 
                          foreground=COLORS["text"])  
        self.style.map("Accent.TButton",
                     background=[('active', COLORS["accent_hover"])],
                     foreground=[('active', COLORS["text"])])
        
        self.style.configure("TEntry", 
                          fieldbackground=COLORS["bg_input"], 
                          foreground=COLORS["text"],
                          bordercolor=COLORS["border"],
                          lightcolor=COLORS["border"],
                          darkcolor=COLORS["border"],
                          borderwidth=1,
                          font=("Segoe UI", 10))
        
        self.style.configure("TCheckbutton", 
                          background=COLORS["bg_light"], 
                          foreground=COLORS["text"],
                          font=("Segoe UI", 10))
        self.style.map("TCheckbutton",
                     background=[('active', COLORS["bg_light"])],
                     foreground=[('active', COLORS["accent"])])
        
        self.style.configure("TNotebook", 
                          background=COLORS["bg_dark"],
                          tabmargins=[2, 5, 2, 0],
                          tabposition='n')
        
        self.style.configure("TNotebook.Tab", 
                          background=COLORS["bg_light"], 
                          foreground=COLORS["text"],
                          padding=[10, 5],
                          font=("Segoe UI", 10))
        
        self.style.map("TNotebook.Tab",
                     background=[('selected', COLORS["accent"])],
                     foreground=[('selected', COLORS["text"])])
        
        # Create the main frame with padding
        self.main_frame = ttk.Frame(self, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook, style="TFrame")
        self.settings_tab = ttk.Frame(self.notebook, style="TFrame")
        self.logs_tab = ttk.Frame(self.notebook, style="TFrame")
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.settings_tab, text="Settings")
        self.notebook.add(self.logs_tab, text="Logs")
        
        # Initialize the tabs
        self.init_dashboard_tab()
        self.init_settings_tab()
        self.init_logs_tab()
        
        # Create a status bar
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=COLORS["bg_light"], fg=COLORS["text_secondary"],
                                  font=("Segoe UI", 9), padx=10, pady=3)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize the monitor thread
        self.monitor_thread = None
        
        # Set up log processing
        self.after(100, self.process_logs)
        
        # Set up periodic UI updates
        self.after(1000, self.update_stats)
        
        # Bind the close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Bind resize event for responsive layout
        self.bind("<Configure>", self.on_resize)
    
    def init_dashboard_tab(self):
        """Initialize the dashboard tab"""
        # Main container with padding
        main_container = ttk.Frame(self.dashboard_tab, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configure grid layout for responsiveness
        main_container.columnconfigure(0, weight=1)  # Left column expands
        main_container.columnconfigure(1, weight=1)  # Right column expands
        main_container.rowconfigure(1, weight=1)     # Stats row expands
        
        # Top section - Control Panel
        control_panel = ttk.Frame(main_container, style="ContentFrame.TFrame")
        control_panel.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5, ipady=10, ipadx=10)
        
        # Header for control panel
        ttk.Label(control_panel, text="Tunnel Control", style="Header.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
        
        # Button frame with better spacing
        button_frame = ttk.Frame(control_panel, style="ContentFrame.TFrame")
        button_frame.pack(fill="x", padx=15, pady=5)
        
        # Control buttons with improved styling
        self.start_button = ttk.Button(button_frame, text="▶ Start Tunnel", command=self.start_monitor, style="Accent.TButton")
        self.start_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="■ Stop Tunnel", command=self.stop_monitor)
        self.stop_button.pack(side="left", padx=(0, 10))
        self.stop_button.config(state=tk.DISABLED)
        
        self.test_whatsapp_button = ttk.Button(button_frame, text="✉ Test WhatsApp", command=self.test_whatsapp)
        self.test_whatsapp_button.pack(side="left")
        
        # Status indicators frame
        status_frame = ttk.Frame(control_panel, style="ContentFrame.TFrame")
        status_frame.pack(fill="x", padx=15, pady=10)
        
        # Create two columns for status indicators
        status_frame.columnconfigure(0, weight=1)
        status_frame.columnconfigure(1, weight=1)
        
        # Tunnel status with improved indicator
        tunnel_status_frame = ttk.Frame(status_frame, style="ContentFrame.TFrame")
        tunnel_status_frame.grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(tunnel_status_frame, text="Tunnel Status:", style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        
        self.status_indicator = tk.Canvas(tunnel_status_frame, width=16, height=16, bg=COLORS["bg_light"], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=5)
        self.status_indicator.create_oval(2, 2, 14, 14, fill=COLORS["error"], outline="")
        
        self.status_label = ttk.Label(tunnel_status_frame, text="Stopped", style="Status.TLabel")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Internet status with improved indicator
        internet_status_frame = ttk.Frame(status_frame, style="ContentFrame.TFrame")
        internet_status_frame.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(internet_status_frame, text="Internet Status:", style="Status.TLabel").pack(side=tk.LEFT, padx=5)
        
        self.internet_indicator = tk.Canvas(internet_status_frame, width=16, height=16, bg=COLORS["bg_light"], highlightthickness=0)
        self.internet_indicator.pack(side=tk.LEFT, padx=5)
        self.internet_indicator.create_oval(2, 2, 14, 14, fill=COLORS["error"], outline="")
        
        self.internet_label = ttk.Label(internet_status_frame, text="Disconnected", style="Status.TLabel")
        self.internet_label.pack(side=tk.LEFT, padx=5)
        
        # Left section - Statistics Panel
        stats_panel = ttk.Frame(main_container, style="ContentFrame.TFrame")
        stats_panel.grid(row=1, column=0, sticky="nsew", padx=5, pady=5, ipady=10, ipadx=10)
        
        # Header for statistics
        ttk.Label(stats_panel, text="Statistics", style="Header.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
        
        # Statistics grid with better spacing
        stats_grid = ttk.Frame(stats_panel, style="ContentFrame.TFrame")
        stats_grid.pack(fill="x", padx=15, pady=5)
        
        # Configure grid for statistics
        for i in range(2):
            stats_grid.columnconfigure(i, weight=1)
        
        # Statistics with improved styling
        row = 0
        # Tunnel starts
        ttk.Label(stats_grid, text="Tunnel Starts:", style="Status.TLabel").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        self.tunnel_starts_label = ttk.Label(stats_grid, text="0", foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.tunnel_starts_label.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        
        # Messages sent
        row += 1
        ttk.Label(stats_grid, text="Messages Sent:", style="Status.TLabel").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        self.messages_sent_label = ttk.Label(stats_grid, text="0", foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.messages_sent_label.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        
        # Internet disconnects
        row += 1
        ttk.Label(stats_grid, text="Internet Disconnects:", style="Status.TLabel").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        self.internet_disconnects_label = ttk.Label(stats_grid, text="0", foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.internet_disconnects_label.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        
        # Uptime
        row += 1
        ttk.Label(stats_grid, text="Uptime:", style="Status.TLabel").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        self.uptime_label = ttk.Label(stats_grid, text="00:00:00", foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.uptime_label.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        
        # Last check time
        row += 1
        ttk.Label(stats_grid, text="Last Check:", style="Status.TLabel").grid(row=row, column=0, padx=5, pady=8, sticky="w")
        self.last_check_label = ttk.Label(stats_grid, text="N/A", foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.last_check_label.grid(row=row, column=1, padx=5, pady=8, sticky="w")
        
        # Right section - Tunnel Info Panel
        info_panel = ttk.Frame(main_container, style="ContentFrame.TFrame")
        info_panel.grid(row=1, column=1, sticky="nsew", padx=5, pady=5, ipady=10, ipadx=10)
        
        # Header for tunnel info
        ttk.Label(info_panel, text="Tunnel Information", style="Header.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tunnel URL section
        url_frame = ttk.Frame(info_panel, style="ContentFrame.TFrame")
        url_frame.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(url_frame, text="Current Tunnel URL:", style="Subheader.TLabel").pack(anchor="w", pady=(5, 8))
        
        # URL display with copy button
        url_display_frame = ttk.Frame(url_frame, style="ContentFrame.TFrame")
        url_display_frame.pack(fill="x", pady=5)
        
        self.tunnel_url_var = tk.StringVar(value="Not available")
        self.tunnel_url_entry = ttk.Entry(url_display_frame, textvariable=self.tunnel_url_var, width=40, state="readonly")
        self.tunnel_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.copy_url_button = ttk.Button(url_display_frame, text="Copy URL", command=self.copy_tunnel_url)
        self.copy_url_button.pack(side="right")
        
        # QR Code placeholder (for future implementation)
        qr_frame = ttk.Frame(info_panel, style="ContentFrame.TFrame")
        qr_frame.pack(fill="x", padx=15, pady=15)
        
        ttk.Label(qr_frame, text="Scan QR Code to Access Tunnel:", style="Subheader.TLabel").pack(anchor="w", pady=(5, 8))
        
        # Placeholder for QR code
        self.qr_placeholder = tk.Canvas(qr_frame, width=150, height=150, bg=COLORS["bg_input"])
        self.qr_placeholder.pack(pady=10)
        self.qr_placeholder.create_text(75, 75, text="QR Code\nPlaceholder", fill=COLORS["text_secondary"])
        
        # WhatsApp information
        whatsapp_frame = ttk.Frame(info_panel, style="ContentFrame.TFrame")
        whatsapp_frame.pack(fill="x", padx=15, pady=5)
        
        ttk.Label(whatsapp_frame, text="WhatsApp Configuration:", style="Subheader.TLabel").pack(anchor="w", pady=(5, 8))
        
        contact_frame = ttk.Frame(whatsapp_frame, style="ContentFrame.TFrame")
        contact_frame.pack(fill="x", pady=5)
        
        ttk.Label(contact_frame, text="Contact:", style="Status.TLabel").pack(side="left", padx=5)
        self.contact_label = ttk.Label(contact_frame, text=self.config["whatsapp_contact"], foreground=COLORS["accent"], font=("Segoe UI", 10, "bold"))
        self.contact_label.pack(side="left", padx=5)
    
    def init_settings_tab(self):
        """Initialize the settings tab"""
        # Create a main container frame with padding
        main_container = ttk.Frame(self.settings_tab, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configure grid layout for responsiveness
        main_container.columnconfigure(0, weight=1)  # Make the column expandable
        main_container.rowconfigure(3, weight=1)     # Make the row expandable
        
        # Create scrollable frame for settings
        canvas = tk.Canvas(main_container, bg=COLORS["bg_dark"], highlightthickness=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create a frame for the settings inside the canvas
        settings_frame = ttk.Frame(canvas, style="ContentFrame.TFrame")
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        
        # Configure the settings frame grid
        settings_frame.columnconfigure(1, weight=1)  # Make the second column expandable
        
        # WhatsApp settings section
        whatsapp_section = ttk.Frame(settings_frame, style="ContentFrame.TFrame")
        whatsapp_section.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        ttk.Label(whatsapp_section, text="WhatsApp Settings", style="Header.TLabel").pack(anchor="w", padx=10, pady=10)
        
        whatsapp_form = ttk.Frame(whatsapp_section, style="ContentFrame.TFrame")
        whatsapp_form.pack(fill="x", padx=10, pady=5)
        
        # Configure the form grid
        whatsapp_form.columnconfigure(1, weight=1)
        
        # WhatsApp Contact
        ttk.Label(whatsapp_form, text="WhatsApp Contact:", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.whatsapp_contact_var = tk.StringVar(value=self.config["whatsapp_contact"])
        self.whatsapp_contact_entry = ttk.Entry(whatsapp_form, textvariable=self.whatsapp_contact_var)
        self.whatsapp_contact_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        # Message Template
        ttk.Label(whatsapp_form, text="Message Template:", style="Status.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.message_template_var = tk.StringVar(value=self.config["message_template"])
        self.message_template_entry = ttk.Entry(whatsapp_form, textvariable=self.message_template_var)
        self.message_template_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        # Help text
        help_text = ttk.Label(whatsapp_form, text="Use {timestamp} and {link} as placeholders", 
                            foreground=COLORS["text_secondary"], font=("Segoe UI", 9, "italic"))
        help_text.grid(row=2, column=1, padx=5, pady=(0, 8), sticky="w")
        
        # Tunnel settings section
        tunnel_section = ttk.Frame(settings_frame, style="ContentFrame.TFrame")
        tunnel_section.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        ttk.Label(tunnel_section, text="Tunnel Settings", style="Header.TLabel").pack(anchor="w", padx=10, pady=10)
        
        tunnel_form = ttk.Frame(tunnel_section, style="ContentFrame.TFrame")
        tunnel_form.pack(fill="x", padx=10, pady=5)
        
        # Configure the form grid
        tunnel_form.columnconfigure(1, weight=1)
        
        # Tunnel URL
        ttk.Label(tunnel_form, text="Tunnel URL:", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.tunnel_url_config_var = tk.StringVar(value=self.config["tunnel_url"])
        self.tunnel_url_config_entry = ttk.Entry(tunnel_form, textvariable=self.tunnel_url_config_var)
        self.tunnel_url_config_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=8, sticky="ew")
        
        # Cloudflared Path
        ttk.Label(tunnel_form, text="Cloudflared Path:", style="Status.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.cloudflared_path_var = tk.StringVar(value=self.config["cloudflared_path"] or "")
        self.cloudflared_path_entry = ttk.Entry(tunnel_form, textvariable=self.cloudflared_path_var)
        self.cloudflared_path_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        self.browse_cloudflared_button = ttk.Button(tunnel_form, text="Browse", command=lambda: self.browse_file(self.cloudflared_path_var))
        self.browse_cloudflared_button.grid(row=1, column=2, padx=5, pady=8)
        
        # Chrome settings section
        chrome_section = ttk.Frame(settings_frame, style="ContentFrame.TFrame")
        chrome_section.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        ttk.Label(chrome_section, text="Chrome Settings", style="Header.TLabel").pack(anchor="w", padx=10, pady=10)
        
        chrome_form = ttk.Frame(chrome_section, style="ContentFrame.TFrame")
        chrome_form.pack(fill="x", padx=10, pady=5)
        
        # Configure the form grid
        chrome_form.columnconfigure(1, weight=1)
        
        # Chrome Path
        ttk.Label(chrome_form, text="Chrome Path:", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.chrome_path_var = tk.StringVar(value=self.config["chrome_path"] or "")
        self.chrome_path_entry = ttk.Entry(chrome_form, textvariable=self.chrome_path_var)
        self.chrome_path_entry.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        self.browse_chrome_button = ttk.Button(chrome_form, text="Browse", command=lambda: self.browse_file(self.chrome_path_var))
        self.browse_chrome_button.grid(row=0, column=2, padx=5, pady=8)
        
        # User Data Directory
        ttk.Label(chrome_form, text="User Data Directory:", style="Status.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.user_data_dir_var = tk.StringVar(value=self.config["user_data_dir"] or "")
        self.user_data_dir_entry = ttk.Entry(chrome_form, textvariable=self.user_data_dir_var)
        self.user_data_dir_entry.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        self.browse_user_data_dir_button = ttk.Button(chrome_form, text="Browse", command=lambda: self.browse_directory(self.user_data_dir_var))
        self.browse_user_data_dir_button.grid(row=1, column=2, padx=5, pady=8)
        
        # Other settings section
        other_section = ttk.Frame(settings_frame, style="ContentFrame.TFrame")
        other_section.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=10)
        
        ttk.Label(other_section, text="Other Settings", style="Header.TLabel").pack(anchor="w", padx=10, pady=10)
        
        other_form = ttk.Frame(other_section, style="ContentFrame.TFrame")
        other_form.pack(fill="x", padx=10, pady=5)
        
        # Configure the form grid
        other_form.columnconfigure(1, weight=1)
        
        # Check Interval
        ttk.Label(other_form, text="Check Interval (seconds):", style="Status.TLabel").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.check_interval_var = tk.StringVar(value=str(self.config["check_interval"]))
        self.check_interval_entry = ttk.Entry(other_form, textvariable=self.check_interval_var, width=10)
        self.check_interval_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        # Max Retries
        ttk.Label(other_form, text="Max Retries:", style="Status.TLabel").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.max_retries_var = tk.StringVar(value=str(self.config["max_retries"]))
        self.max_retries_entry = ttk.Entry(other_form, textvariable=self.max_retries_var, width=10)
        self.max_retries_entry.grid(row=1, column=1, padx=5, pady=8, sticky="w")
        
        # Retry Delay
        ttk.Label(other_form, text="Retry Delay (seconds):", style="Status.TLabel").grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.retry_delay_var = tk.StringVar(value=str(self.config["retry_delay"]))
        self.retry_delay_entry = ttk.Entry(other_form, textvariable=self.retry_delay_var, width=10)
        self.retry_delay_entry.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        
        # Checkboxes frame
        checkbox_frame = ttk.Frame(other_form)
        checkbox_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=8, sticky="w")
        
        # Checkboxes for boolean settings
        self.debug_mode_var = tk.BooleanVar(value=self.config["debug_mode"])
        self.debug_mode_check = ttk.Checkbutton(checkbox_frame, text="Debug Mode", variable=self.debug_mode_var, style="TCheckbutton")
        self.debug_mode_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.headless_mode_var = tk.BooleanVar(value=self.config["headless_mode"])
        self.headless_mode_check = ttk.Checkbutton(checkbox_frame, text="Headless Mode", variable=self.headless_mode_var, style="TCheckbutton")
        self.headless_mode_check.pack(side=tk.LEFT)
        
        # Save button container
        save_button_container = ttk.Frame(settings_frame)
        save_button_container.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=20)
        save_button_container.columnconfigure(0, weight=1)
        
        # Save button
        self.save_button = ttk.Button(save_button_container, text="Save Settings", command=self.save_settings, style="Accent.TButton")
        self.save_button.grid(row=0, column=0)
    
    def init_logs_tab(self):
        """Initialize the logs tab"""
        # Create a frame for the logs
        logs_frame = ttk.Frame(self.logs_tab)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure the logs frame to be responsive
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(1, weight=1)
        
        # Log display header
        ttk.Label(logs_frame, text="Logs", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=10)
        
        # Create a scrolled text widget for logs
        self.log_text = scrolledtext.ScrolledText(logs_frame, bg=COLORS["bg_light"], fg=COLORS["text"])
        self.log_text.grid(row=1, column=0, sticky="nsew")
        self.log_text.config(state=tk.DISABLED)
        
        # Buttons for log actions
        button_frame = ttk.Frame(logs_frame)
        button_frame.grid(row=2, column=0, sticky="w", pady=10)
        
        self.clear_logs_button = ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs, style="TButton")
        self.clear_logs_button.pack(side=tk.LEFT, padx=5)
        
        self.save_logs_button = ttk.Button(button_frame, text="Save Logs", command=self.save_logs, style="TButton")
        self.save_logs_button.pack(side=tk.LEFT, padx=5)
    
    def start_monitor(self):
        """Start the monitor thread"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            log("Monitor is already running")
            return
        
        # Update the UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_indicator.itemconfig(1, fill=COLORS["success"])
        self.status_label.config(text="Starting...")
        
        # Reset the stop event
        stop_event.clear()
        
        # Start the monitor thread
        self.monitor_thread = threading.Thread(target=monitor_thread_func, args=(self.config, self.update_stats))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        log("Monitor started", level="success")
    
    def stop_monitor(self):
        """Stop the monitor thread"""
        # Set the stop event
        stop_event.set()
        
        # Update the UI
        self.stop_button.config(state=tk.DISABLED)
        self.status_indicator.itemconfig(1, fill=COLORS["warning"])
        self.status_label.config(text="Stopping...")
        
        # Stop the tunnel
        stop_tunnel()
        
        # Wait for the thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Update the UI
        self.start_button.config(state=tk.NORMAL)
        self.status_indicator.itemconfig(1, fill=COLORS["error"])
        self.status_label.config(text="Stopped")
        
        log("Monitor stopped", level="warning")
    
    def test_whatsapp(self):
        """Test WhatsApp message sending"""
        # Create a test message
        test_message = "🔄 Test message from Cloudflare Tunnel Monitor"
        
        # Try to send the message
        threading.Thread(target=lambda: send_whatsapp(test_message, self.config)).start()
    
    def save_settings(self):
        """Save the settings from the UI to the configuration"""
        try:
            # Get values from the UI
            self.config["whatsapp_contact"] = self.whatsapp_contact_var.get()
            self.config["message_template"] = self.message_template_var.get()
            self.config["tunnel_url"] = self.tunnel_url_config_var.get()
            self.config["cloudflared_path"] = self.cloudflared_path_var.get() or None
            self.config["chrome_path"] = self.chrome_path_var.get() or None
            self.config["user_data_dir"] = self.user_data_dir_var.get() or None
            
            # Validate numeric values
            try:
                self.config["check_interval"] = int(self.check_interval_var.get())
                if self.config["check_interval"] < 1:
                    raise ValueError("Check interval must be at least 1 second")
            except ValueError as e:
                messagebox.showerror("Invalid Value", f"Check interval: {str(e)}")
                return
            
            try:
                self.config["max_retries"] = int(self.max_retries_var.get())
                if self.config["max_retries"] < 0:
                    raise ValueError("Max retries must be a non-negative integer")
            except ValueError as e:
                messagebox.showerror("Invalid Value", f"Max retries: {str(e)}")
                return
            
            try:
                self.config["retry_delay"] = int(self.retry_delay_var.get())
                if self.config["retry_delay"] < 1:
                    raise ValueError("Retry delay must be at least 1 second")
            except ValueError as e:
                messagebox.showerror("Invalid Value", f"Retry delay: {str(e)}")
                return
            
            # Boolean values
            self.config["debug_mode"] = self.debug_mode_var.get()
            self.config["headless_mode"] = self.headless_mode_var.get()
            
            # Save the configuration
            if save_config(self.config):
                messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
                
                # Update the contact label in the dashboard
                self.contact_label.config(text=self.config["whatsapp_contact"])
            else:
                messagebox.showerror("Error", "Failed to save settings.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving settings: {str(e)}")
    
    def browse_file(self, var):
        """Browse for a file and update the variable"""
        filename = filedialog.askopenfilename()
        if filename:
            var.set(filename)
    
    def browse_directory(self, var):
        """Browse for a directory and update the variable"""
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)
    
    def copy_tunnel_url(self):
        """Copy the tunnel URL to the clipboard"""
        url = self.tunnel_url_var.get()
        if url and url != "Not available":
            self.clipboard_clear()
            self.clipboard_append(url)
            self.status_bar.config(text="Tunnel URL copied to clipboard")
            self.after(3000, lambda: self.status_bar.config(text="Ready"))
    
    def clear_logs(self):
        """Clear the log display"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_logs(self):
        """Save the logs to a file"""
        filename = filedialog.asksaveasfilename(defaultextension=".log",
                                              filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.status_bar.config(text=f"Logs saved to {filename}")
                self.after(3000, lambda: self.status_bar.config(text="Ready"))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {str(e)}")
    
    def process_logs(self):
        """Process logs from the queue and update the log display"""
        while not log_queue.empty():
            try:
                log_entry = log_queue.get_nowait()
                
                # Format the log entry
                timestamp = log_entry["timestamp"]
                level = log_entry["level"]
                message = log_entry["message"]
                
                # Determine the tag based on the log level
                if level == "error":
                    tag = "error"
                elif level == "warning":
                    tag = "warning"
                elif level == "success":
                    tag = "success"
                elif level == "debug":
                    tag = "debug"
                else:
                    tag = "info"
                
                # Add the log entry to the display
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
                self.log_text.insert(tk.END, f"[{level.upper()}] ", tag)
                self.log_text.insert(tk.END, f"{message}\n", "message")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
                
                # Configure tags for different log levels
                self.log_text.tag_configure("timestamp", foreground="#88C0D0")
                self.log_text.tag_configure("error", foreground=COLORS["error"])
                self.log_text.tag_configure("warning", foreground=COLORS["warning"])
                self.log_text.tag_configure("success", foreground=COLORS["success"])
                self.log_text.tag_configure("info", foreground=COLORS["text"])
                self.log_text.tag_configure("debug", foreground="#81A1C1")
                self.log_text.tag_configure("message", foreground=COLORS["text"])
            except queue.Empty:
                break
        
        # Schedule the next check
        self.after(100, self.process_logs)
    
    def update_stats(self):
        """Update the statistics display"""
        # Update statistics labels
        self.tunnel_starts_label.config(text=str(STATS["tunnel_starts"]))
        self.messages_sent_label.config(text=str(STATS["messages_sent"]))
        self.internet_disconnects_label.config(text=str(STATS["internet_disconnects"]))
        
        # Format uptime
        uptime_seconds = int(STATS["total_uptime"])
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.uptime_label.config(text=uptime_str)
        
        # Update tunnel URL
        if STATS["last_tunnel_url"]:
            tunnel_url = STATS["last_tunnel_url"]
            self.tunnel_url_var.set(tunnel_url)
            self.tunnel_url_entry.config(foreground=COLORS["accent"])
            
            # Generate and display QR code for the tunnel URL
            self.qr_placeholder.delete("all")
            
            # Generate QR code
            qr_image = self.generate_qr_code(tunnel_url)
            
            if qr_image:
                # Display the QR code on the canvas
                self.qr_placeholder.create_image(75, 75, image=qr_image)
                
                # Add a border around the QR code
                self.qr_placeholder.create_rectangle(5, 5, 145, 145, outline=COLORS["border"], width=2)
                
                # Add a small label below the QR code
                self.qr_placeholder.create_text(75, 140, text="Scan to access tunnel", 
                                              fill=COLORS["accent"], font=("Segoe UI", 8))
            else:
                # Fallback if QR code generation fails
                self.qr_placeholder.create_rectangle(5, 5, 145, 145, fill=COLORS["bg_input"], outline=COLORS["border"])
                self.qr_placeholder.create_text(75, 75, text=f"Tunnel URL:\n{tunnel_url[:20]}...", 
                                              fill=COLORS["accent"], width=140, justify="center")
        else:
            self.tunnel_url_var.set("Not available")
            self.tunnel_url_entry.config(foreground=COLORS["text_secondary"])
            
            # Reset QR code placeholder
            self.qr_placeholder.delete("all")
            self.qr_placeholder.create_rectangle(5, 5, 145, 145, fill=COLORS["bg_input"], outline=COLORS["border"])
            self.qr_placeholder.create_text(75, 75, text="No Tunnel URL\nAvailable", fill=COLORS["text_secondary"])
        
        # Update last check time
        if "last_check_time" in STATS and STATS["last_check_time"]:
            last_check = STATS["last_check_time"].strftime("%H:%M:%S")
            self.last_check_label.config(text=last_check)
        else:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.last_check_label.config(text=current_time)
        
        # Update status indicator with improved visual feedback
        if STATS["current_status"] == "Running":
            self.status_indicator.itemconfig(1, fill=COLORS["success"])
            self.status_label.config(text="Running", foreground=COLORS["success"])
            # Add pulsing effect for running tunnel
            self.pulse_indicator(self.status_indicator)
        elif STATS["current_status"] == "Stopping":
            self.status_indicator.itemconfig(1, fill=COLORS["warning"])
            self.status_label.config(text="Stopping...", foreground=COLORS["warning"])
        else:
            self.status_indicator.itemconfig(1, fill=COLORS["error"])
            self.status_label.config(text="Stopped", foreground=COLORS["error"])
            # Remove any pulse effect
            self.status_indicator.delete("pulse")
        
        # Update internet status with improved visual feedback
        internet_connected = internet_available()
        if internet_connected:
            self.internet_indicator.itemconfig(1, fill=COLORS["success"])
            self.internet_label.config(text="Connected", foreground=COLORS["success"])
            # Add subtle pulse for connected internet
            self.pulse_indicator(self.internet_indicator, intensity=0.7)
        else:
            self.internet_indicator.itemconfig(1, fill=COLORS["warning"])
            self.internet_label.config(text="Disconnected", foreground=COLORS["warning"])
            # Remove any pulse effect
            self.internet_indicator.delete("pulse")
        
        # Schedule the next update
        self.after(1000, self.update_stats)
    
    def generate_qr_code(self, url):
        """Generate a QR code for the given URL"""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data to the QR code
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create an image from the QR Code instance
            img = qr.make_image(fill_color=COLORS["text"], back_color=COLORS["bg_input"])
            
            # Resize the image to fit the canvas
            img = img.resize((140, 140))
            
            # Convert to PhotoImage for Tkinter
            photo_img = ImageTk.PhotoImage(img)
            
            # Store reference to prevent garbage collection
            self.qr_image = photo_img
            
            return photo_img
        except Exception as e:
            log(f"Error generating QR code: {e}", level="error")
            return None
    
    def pulse_indicator(self, indicator, intensity=1.0):
        """Create a subtle pulsing effect for active indicators"""
        # Only pulse if not already pulsing (check tag)
        if not indicator.find_withtag("pulse"):
            # Create a slightly larger halo around the indicator
            indicator.create_oval(0, 0, 16, 16, 
                                 fill="", outline=COLORS["success"], 
                                 width=1.5, tags="pulse")
            
            # Animate the pulse
            def _pulse(step=0, growing=True):
                # Stop pulsing if indicator is not showing success anymore
                if indicator.itemcget(1, "fill") != COLORS["success"]:
                    indicator.delete("pulse")
                    return
                
                # Calculate pulse size
                if growing:
                    size = 0.5 + (step * 0.05 * intensity)
                    if size >= 1.0:
                        growing = False
                else:
                    size = 1.0 - (step * 0.05 * intensity)
                    if size <= 0.5:
                        growing = True
                        step = 0
                
                # Update pulse appearance
                indicator.itemconfig("pulse", width=size)
                
                # Continue pulsing
                self.after(100, lambda: _pulse(step + 1, growing))
            
            # Start the pulse animation
            _pulse()
    
    def on_close(self):
        """Handle the window close event"""
        if messagebox.askokcancel("Quit", "Do you want to quit? This will stop the tunnel if it's running."):
            # Stop the monitor thread
            stop_event.set()
            
            # Clean up resources
            cleanup()
            
            # Destroy the window
            self.destroy()

# Main function
def main():
    """Main function"""
    try:
        # Create and run the GUI
        app = TunnelMonitorGUI()
        app.mainloop()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    main()