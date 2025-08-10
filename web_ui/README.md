# Cloudflare Tunnel Monitor - Web UI

A modern web-based interface for the Cloudflare Tunnel Monitor, providing a user-friendly dashboard to control and monitor your Cloudflare tunnels.

## Features

- **Dashboard**: Real-time monitoring of tunnel status, internet connectivity, and statistics
- **Settings Management**: Configure WhatsApp integration, tunnel settings, and more
- **Logs Viewer**: View and filter logs by type (info, success, warning, error, debug)
- **Responsive Design**: Works on desktop and mobile devices
- **Cross-Platform**: Compatible with Windows and Ubuntu/Linux

## Requirements

- Python 3.7 or higher
- Flask and Flask-SocketIO for the web server
- Selenium and undetected-chromedriver for WhatsApp integration
- A modern web browser (Chrome, Firefox, Edge, etc.)
- Cloudflared executable (same as the original Cloudflare Tunnel Monitor)

## Installation

### 1. Install Python Dependencies

```bash
pip install flask flask-socketio selenium undetected-chromedriver requests
```

### 2. Ensure Cloudflared is Installed

Follow the same installation instructions as in the main README for installing cloudflared based on your operating system.

### 3. Start the Web UI

```bash
python app.py
```

The web interface will be available at http://localhost:5000 by default.

## Usage

### Dashboard

The dashboard provides a real-time overview of your tunnel:

- **Tunnel Control**: Start and stop the tunnel
- **Status Indicators**: Monitor tunnel and internet status
- **Statistics**: View tunnel starts, messages sent, internet disconnects, and uptime
- **Tunnel URL**: View and copy the current tunnel URL
- **QR Code**: Scan to quickly access the tunnel URL on mobile devices
- **WhatsApp Testing**: Test WhatsApp message sending
- **Recent Activity**: View the most recent log entries

### Settings

Configure all aspects of the Cloudflare Tunnel Monitor:

- **WhatsApp Settings**: Contact and message template
- **Tunnel Settings**: Default URL and cloudflared path
- **Browser Settings**: Chrome path, user data directory, and headless mode
- **Connection Settings**: Check interval, max retries, and retry delay
- **Advanced Settings**: Debug mode

### Logs

View and manage application logs:

- **Filter Logs**: Filter by log level (info, success, warning, error, debug)
- **Clear Logs**: Remove all logs
- **Export Logs**: Download logs as a text file
- **Auto-Scroll**: Toggle automatic scrolling to the newest logs

## Customization

The web UI uses a classic color scheme by default, but you can customize it by modifying the CSS files in the `static/css` directory.

## Troubleshooting

### WhatsApp Integration

- If WhatsApp integration is not working, ensure you have scanned the QR code at least once to authenticate
- Check that the Chrome path and user data directory are correctly configured
- Try running in non-headless mode for initial setup

### Tunnel Issues

- Verify that cloudflared is correctly installed and the path is properly configured
- Check the logs for any error messages related to cloudflared
- Ensure you have a working internet connection

## License

This project is licensed under the same terms as the original Cloudflare Tunnel Monitor.