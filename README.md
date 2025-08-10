# Cloudflare Tunnel Monitor

A comprehensive solution for automatically creating and monitoring Cloudflare Tunnels to expose local services to the internet. This tool monitors internet connectivity, automatically restarts tunnels if connections drop, and can send tunnel URLs via WhatsApp. It offers both a desktop GUI and a web-based UI for easy configuration and monitoring.

## Features

- **Automatic Tunnel Creation**: Creates Cloudflare Tunnels to securely expose local services
- **Connection Monitoring**: Continuously checks internet connectivity and restarts tunnels when needed
- **WhatsApp Integration**: Sends tunnel URLs via WhatsApp Web (requires authentication)
- **Multiple Interfaces**:
  - Command-line interface for server environments
  - Desktop GUI for easy local management
  - Web UI for remote access from any device
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **System Service**: Can run as a background service for 24/7 operation
- **Utility Scripts**: Includes scripts for easy configuration and management

## Available Versions

1. **Web UI Version** (`web_ui/app.py`) - **Recommended**
   - Modern web-based interface accessible from any browser
   - Responsive design works on desktop and mobile devices
   - Real-time updates using WebSockets
   - Complete dashboard with settings management and logs viewer
   - Uses WhatsApp Web for sending tunnel URLs

2. **Desktop GUI Version** (`tunnel_monitor_gui.py`)
   - Native graphical user interface for easy configuration
   - Provides real-time statistics and status information
   - Includes configuration management and logging features
   - Uses WhatsApp Web for sending tunnel URLs

3. **Selenium-based CLI Version** (`tunnel_monitor_selenium.py`)
   - Command-line interface for server environments
   - Uses WhatsApp Web automation to send messages
   - No external service required (free)
   - Requires Chrome browser and QR code scanning for initial setup

4. **Twilio-based Version** (`tunnel_monitor.py`) - **Legacy**
   - Uses Twilio API to send WhatsApp messages
   - Requires a Twilio account (paid service)
   - Simpler setup, no browser dependencies

## Quick Start Guide

### Prerequisites

1. **Python 3.7+**: Make sure Python 3.7 or higher is installed
2. **Chrome Browser**: Required for WhatsApp Web integration
3. **Cloudflared**: The Cloudflare Tunnel client

### Installation

#### Linux/Ubuntu

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
   cd Cloudflare-Tunnel-Monitor
   ```

2. **Make scripts executable**:
   ```bash
   chmod +x make_all_scripts_executable.sh
   ./make_all_scripts_executable.sh
   ```

3. **Download Cloudflared**:
   ```bash
   ./download_cloudflared.sh
   ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application (Linux/Ubuntu)

#### Option 1: Web UI (Recommended)

```bash
./start_web_ui.sh
```

Then open your browser and navigate to http://localhost:5000

#### Option 2: Desktop GUI

```bash
./run_gui.sh
```

#### Option 3: Command Line

```bash
./run_in_background.sh
```

#### Option 4: As a System Service

```bash
./setup_systemd_service.sh
sudo systemctl start tunnel-monitor
```

#### Windows

1. **Clone the repository**:
   ```
   git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
   cd Cloudflare-Tunnel-Monitor
   ```

2. **Download Cloudflared**:
   ```
   download_cloudflared_windows.bat
   ```
   Or download manually from [Cloudflare's GitHub](https://github.com/cloudflare/cloudflared/releases)

3. **Install Python dependencies**:
   ```
   pip install -r requirements.txt
   ```

### Running the Application (Windows)

#### Option 1: Web UI (Recommended)

```
start_web_ui.bat
```

Then open your browser and navigate to http://localhost:5000

#### Option 2: Desktop GUI

```
run_gui.bat
```

#### Option 3: Command Line

```
run_tunnel_monitor_venv.bat
```

#### Option 4: With Custom Settings

You can use utility scripts to configure the application before running:

```
update_whatsapp_contact.bat "Contact Name"
update_tunnel_url.bat http://localhost:8080
update_chrome_path.bat "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## Configuration

### Using the Web UI or Desktop GUI

1. Open the application
2. Navigate to the Settings page
3. Configure the following settings:
   - **WhatsApp Contact**: The contact name or phone number to send messages to
   - **Tunnel URL**: The local service URL to expose (e.g., http://localhost:8080)
   - **Chrome Path**: Path to Chrome browser (if not in standard location)
   - **Cloudflared Path**: Path to cloudflared executable (if not in standard location)
   - **Other Settings**: Check interval, retry settings, etc.

### Using Configuration Scripts

The project includes utility scripts for quick configuration:

#### Windows
```
update_whatsapp_contact.bat "Contact Name"
update_tunnel_url.bat http://localhost:8080
update_chrome_path.bat "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

#### Linux/Ubuntu
```bash
./update_whatsapp_contact.sh "Contact Name"
./update_tunnel_url.sh http://localhost:8080
./update_chrome_path.sh /usr/bin/google-chrome
```

## WhatsApp Integration

The application uses WhatsApp Web to send tunnel URLs. This requires a one-time authentication:

1. Start the application
2. When prompted, scan the QR code with your WhatsApp mobile app
3. Once authenticated, the session will be saved for future use

**Note**: If you're running in headless mode (e.g., on a server), you'll need to authenticate at least once in non-headless mode. Use the `test_whatsapp_auth.sh` or `test_whatsapp_auth.bat` script for this purpose.

## Service Management (Linux)

```bash
# Check status
sudo systemctl status tunnel-monitor

# View logs
sudo journalctl -u tunnel-monitor -f

# Start/stop/restart
sudo systemctl start tunnel-monitor
sudo systemctl stop tunnel-monitor
sudo systemctl restart tunnel-monitor

# Enable/disable at boot
sudo systemctl enable tunnel-monitor
sudo systemctl disable tunnel-monitor
```

## Utility Scripts

This project includes several utility scripts to help you configure and manage the tunnel monitor:

### Configuration Scripts

| Windows (.bat) | Linux/Unix (.sh) | Description |
|----------------|------------------|-------------|
| `update_whatsapp_contact.bat` | `update_whatsapp_contact.sh` | Update the WhatsApp contact name or number |
| `update_tunnel_url.bat` | `update_tunnel_url.sh` | Update the default tunnel URL |
| `update_chrome_path.bat` | `update_chrome_path.sh` | Update the Chrome browser path |
| `update_cloudflared_path.bat` | `update_cloudflared_path.sh` | Update the cloudflared executable path |
| `update_message_template.bat` | `update_message_template.sh` | Update the WhatsApp message template |
| `update_check_interval.bat` | `update_check_interval.sh` | Update the internet check interval in seconds |
| `update_retry_settings.bat` | `update_retry_settings.sh` | Update the retry count and delay |
| `update_user_data_dir.bat` | `update_user_data_dir.sh` | Update the Chrome user data directory |

### Control Scripts

| Windows (.bat) | Linux/Unix (.sh) | Description |
|----------------|------------------|-------------|
| `run_tunnel_monitor_venv.bat` | `run_in_background.sh` | Run the tunnel monitor in the background |
| `run_gui.bat` | `run_gui.sh` | Run the desktop GUI version |
| `start_web_ui.bat` | `start_web_ui.sh` | Run the web UI version |
| `check_status.bat` | `check_status.sh` | Check the status of the tunnel monitor |
| `run_with_custom_url.bat` | `run_with_custom_url.sh` | Run with a custom URL |

### Testing and Utility Scripts

| Windows (.bat) | Linux/Unix (.sh) | Description |
|----------------|------------------|-------------|
| `test_whatsapp_auth.bat` | `test_whatsapp_auth.sh` | Test WhatsApp Web authentication |
| `test_cloudflared.bat` | `test_cloudflared.sh` | Test cloudflared functionality |
| `toggle_debug_mode.bat` | `toggle_debug_mode.sh` | Toggle debug mode on/off |
| `toggle_headless_mode.bat` | `toggle_headless_mode.sh` | Toggle headless mode on/off |
| - | `make_all_scripts_executable.sh` | Make all shell scripts executable |

## Troubleshooting

### WhatsApp Integration Issues

1. **Authentication Failed**: 
   - Make sure you've scanned the QR code with your WhatsApp mobile app
   - Try running `test_whatsapp_auth.bat` or `test_whatsapp_auth.sh` to test authentication separately
   - Ensure Chrome is properly installed and accessible

2. **Contact Not Found**: 
   - Verify the contact name/number exactly matches what's in your WhatsApp contacts
   - For phone numbers, include the country code (e.g., +1234567890)
   - Try using the phone number instead of the contact name

3. **Browser Issues**: 
   - Try updating Chrome to the latest version
   - Specify the Chrome path manually using the update scripts
   - Toggle headless mode off for debugging: `toggle_headless_mode.bat` or `toggle_headless_mode.sh`

### Tunnel Issues

1. **Cloudflared Not Found**: 
   - Make sure cloudflared is installed and the path is correctly configured
   - Run `test_cloudflared.bat` or `test_cloudflared.sh` to test cloudflared separately

2. **Permission Denied**: 
   - On Linux, make sure cloudflared has execute permissions: `chmod +x cloudflared-linux-amd64`
   - Try running with elevated privileges (admin/sudo)

3. **Connection Errors**: 
   - Check your internet connection
   - Verify firewall settings aren't blocking cloudflared
   - Ensure the local service you're tunneling to is actually running
## Advanced Usage

### Custom Message Templates

You can customize the WhatsApp message template using the following variables:
- `{link}`: The tunnel URL
- `{timestamp}`: Current date and time

Example:
```
update_message_template.bat "Your tunnel is ready! Access it at: {link} (created at {timestamp})"
```

### Headless Mode

For server environments, you can run in headless mode (no visible browser window):

```bash
# Enable headless mode
./toggle_headless_mode.sh

# First authenticate WhatsApp Web (requires GUI access)
./test_whatsapp_auth.sh

# Then run in background
./run_in_background.sh
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Cloudflare](https://www.cloudflare.com/) for the Cloudflare Tunnel service
- [Selenium](https://www.selenium.dev/) for browser automation
- [Flask](https://flask.palletsprojects.com/) for the web interface

### Windows Scripts (.bat)

- **check_status.bat**: Check the status of the tunnel monitor on Windows
- **run_with_custom_url.bat**: Run the tunnel monitor with a custom URL (e.g., `run_with_custom_url.bat http://localhost:8080`)
- **update_whatsapp_contact.bat**: Update the WhatsApp contact name (e.g., `update_whatsapp_contact.bat "John Doe"`)
- **update_tunnel_url.bat**: Update the default tunnel URL (e.g., `update_tunnel_url.bat http://localhost:8080`)
- **update_chrome_path.bat**: Update the Chrome browser path (e.g., `update_chrome_path.bat "C:\Program Files\Google\Chrome\Application\chrome.exe"`)
- **update_cloudflared_path.bat**: Update the cloudflared executable path (e.g., `update_cloudflared_path.bat "C:\Users\username\cloudflared.exe"`)
- **update_message_template.bat**: Update the WhatsApp message template (e.g., `update_message_template.bat "Your tunnel link is: {link}"`)
- **update_check_interval.bat**: Update the internet check interval in seconds (e.g., `update_check_interval.bat 30`)
- **update_retry_settings.bat**: Update the retry count and delay (e.g., `update_retry_settings.bat 3 5`)
- **toggle_debug_mode.bat**: Toggle debug mode on/off
- **toggle_headless_mode.bat**: Toggle headless mode on/off for Chrome
- **make_all_scripts_executable.bat**: Creates a shell script to make all .sh files executable when transferred to Linux
- **download_cloudflared_windows.bat**: Automatically downloads the latest cloudflared executable for Windows
- **test_whatsapp_auth.bat**: Test WhatsApp Web authentication without running the full tunnel monitor
- **test_cloudflared.bat**: Test cloudflared functionality without running the full tunnel monitor
- **update_user_data_dir.bat**: Update the Chrome user data directory where WhatsApp Web session is stored
- **run_gui.bat**: Run the desktop GUI version of the tunnel monitor
- **start_web_ui.bat**: Run the web-based UI version of the tunnel monitor

## Desktop GUI Application

The desktop GUI application provides an easy-to-use interface for configuring and monitoring the Cloudflare Tunnel. It includes the following features:

### Dashboard

- **Tunnel Control**: Start and stop the tunnel with a single click
- **Status Indicators**: Visual indicators for tunnel status and internet connectivity
- **Statistics**: Real-time statistics including tunnel starts, messages sent, internet disconnects, and uptime
- **Current Tunnel URL**: Display and copy the current tunnel URL
- **Test WhatsApp**: Test WhatsApp message sending without starting the tunnel

### Settings

- **WhatsApp Settings**: Configure WhatsApp contact and message template
- **Tunnel Settings**: Set the tunnel URL and cloudflared path
- **Chrome Settings**: Configure Chrome browser path and user data directory
- **Other Settings**: Adjust check interval, retry settings, debug mode, and headless mode

### Logs

- **Real-time Logging**: View detailed logs of all operations
- **Log Management**: Clear logs or save them to a file for troubleshooting

### Running the Desktop GUI

```bash
# On Linux/macOS
./run_gui.sh

# On Windows
run_gui.bat
```

## Web UI Application

The web-based UI provides a modern, responsive interface for configuring and monitoring the Cloudflare Tunnel from any device with a web browser. It includes the following features:

### Dashboard

- **Tunnel Control**: Start and stop the tunnel with a single click
- **Status Indicators**: Visual indicators for tunnel status and internet connectivity
- **Statistics**: Real-time statistics including tunnel starts, messages sent, internet disconnects, and uptime
- **Current Tunnel URL**: Display and copy the current tunnel URL
- **QR Code**: Scan to quickly access the tunnel URL on mobile devices
- **Test WhatsApp**: Test WhatsApp message sending without starting the tunnel
- **Recent Activity**: View the most recent log entries

### Settings

- **WhatsApp Settings**: Configure WhatsApp contact and message template
- **Tunnel Settings**: Set the tunnel URL and cloudflared path
- **Browser Settings**: Configure Chrome browser path and user data directory
- **Connection Settings**: Adjust check interval, retry settings
- **Advanced Settings**: Configure debug mode and headless mode

### Logs

- **Real-time Logging**: View detailed logs of all operations
- **Log Filtering**: Filter logs by level (info, success, warning, error, debug)
- **Log Management**: Clear logs or export them to a file for troubleshooting
- **Auto-Scroll**: Toggle automatic scrolling to the newest logs

### Running the Web UI

```bash
# On Linux/macOS
./start_web_ui.sh

# On Windows
start_web_ui.bat
```

Then open your browser and navigate to http://localhost:5000

## Troubleshooting

### WhatsApp Web Authentication

- If running as a service, you must first authenticate WhatsApp Web by running the script manually
- Authentication may expire periodically, requiring re-scanning the QR code
- If running in headless mode, temporarily switch to non-headless mode for authentication
- You can test WhatsApp Web authentication separately using the provided test scripts:
  ```bash
  # On Linux/macOS
  ./test_whatsapp_auth.sh
  
  # On Windows
  test_whatsapp_auth.bat
  ```

### Cloudflared Issues

- Ensure cloudflared is properly installed and accessible
- Check that the URL format is correct (avoid hash fragments or special characters)
- For permission issues, run with sudo or as root
- You can test cloudflared functionality separately using the provided test scripts:
  ```bash
  # On Linux/macOS
  ./test_cloudflared.sh [url]
  
  # On Windows
  test_cloudflared.bat [url]
  ```
  If no URL is provided, it defaults to http://localhost:8080

### Chrome/Selenium Issues

- Ensure Chrome is installed and the path is correct
- Install missing dependencies if Chrome fails to start
- For "Chrome crashed" errors, try updating Chrome or using a different version

## License

This project is open source and available under the MIT License.