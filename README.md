# 🌐 Cloudflare Tunnel Monitor

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#)  

<<<<<<< HEAD
🚀 **Cloudflare Tunnel Monitor** is a cross-platform tool that helps you:  
- Automatically manage & monitor Cloudflare Tunnels  
- Auto-restart tunnels if they disconnect  
- Visualize real-time latency (avg/min/max) with a simple dashboard  
- Run via **Web UI** or lightweight **Desktop GUI**  
=======
A robust, production-ready solution for automatically creating and monitoring Cloudflare Tunnels. This tool provides seamless exposure of local services to the internet with continuous connectivity monitoring and automatic tunnel restoration if connections drop. Available with both web-based and desktop interfaces for flexible management.

## 🚀 Key Features

- **Automated Tunnel Management**: Creates and maintains Cloudflare Tunnels with zero manual intervention
- **Intelligent Connection Monitoring**: Continuously checks internet connectivity and automatically restarts tunnels when needed
- **Real-time Ping Analytics**: Monitors and visualizes network latency to configurable endpoints with comprehensive statistics (average, minimum, maximum, and count) and real-time visualization
- **Dual Interface Options**:
  - Modern, responsive web UI accessible from any device
  - Native desktop GUI for local management
- **Cross-Platform Compatibility**: Runs on Windows, Linux, and macOS
- **Production-Ready**: Can operate as a background service for 24/7 deployment
- **Smart Resource Management**: Optimized for minimal system resource usage

## 🖥️ Interface Options

### Web UI (Recommended)

The web interface provides a modern, responsive dashboard accessible from any device:

- Real-time statistics with WebSocket updates
- Comprehensive settings management
- QR code generation for easy tunnel URL sharing
- Mobile-friendly responsive design

### Desktop GUI

The native desktop application offers:

- Lightweight graphical interface
- System tray integration
- Local configuration management
- Real-time monitoring

## 🛠️ Quick Setup

### Prerequisites

- Python 3.7 or higher
- Cloudflared (Cloudflare Tunnel client)

### Windows Installation

```bash
# Clone the repository
git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
cd Cloudflare-Tunnel-Monitor

# Run the setup script
start_web_ui.bat
```

### Linux/macOS Installation

```bash
# Clone the repository
git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
cd Cloudflare-Tunnel-Monitor

# Make scripts executable
chmod +x make_all_scripts_executable.sh
./make_all_scripts_executable.sh

# Install dependencies and start the web UI
pip install -r web_ui/requirements.txt
python web_ui/app.py
```

## 📊 Dashboard

The dashboard provides real-time monitoring of:

- Tunnel status and URL
- Internet connectivity
- Ping latency with historical data visualization
  - Live ping measurements to configurable endpoints
  - Comprehensive statistics dashboard showing average, minimum, maximum ping times and total ping count
  - Interactive visual graph showing ping trends over time with color-coded performance indicators
- Uptime statistics and tunnel reliability metrics

## ⚙️ Configuration

The application can be configured through the settings interface or by directly editing the `tunnel_monitor_config.json` file:

```json
{
  "tunnel_url": "http://localhost:8080",
  "check_interval": 60,
  "max_retries": 3,
  "retry_delay": 5,
  "debug_mode": false,
  "ping_test_url": "1.1.1.1"
}
```

**Note:** The default tunnel URL is set to `http://localhost:8080`. You can change this through the web interface settings or by editing the configuration file.

## 🔧 Advanced Usage

### Running as a System Service

For 24/7 operation, you can configure the application to run as a system service:

#### Windows (using NSSM)

See [SSH_SERVER_SETUP.md](SSH_SERVER_SETUP.md) for detailed instructions.

#### Linux (using Systemd)

Create a service file at `/etc/systemd/system/cloudflare-tunnel-monitor.service`:

```ini
[Unit]
Description=Cloudflare Tunnel Monitor
After=network.target

[Service]
User=<your-username>
WorkingDirectory=/path/to/cloudflare_tunnel_monitor
ExecStart=/usr/bin/python3 web_ui/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable cloudflare-tunnel-monitor
sudo systemctl start cloudflare-tunnel-monitor
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Credits

- **Lead Developer**: [Tariqul Islam](https://github.com/MeTariqul)
- **Contributors**: 
  - All the open-source contributors who have helped improve this project
- **Technologies**:
  - [Cloudflare](https://www.cloudflare.com/) for their excellent tunneling technology
  - [Flask](https://flask.palletsprojects.com/) web framework
  - [Socket.IO](https://socket.io/) for real-time communication
  - [Chart.js](https://www.chartjs.org/) for data visualization
>>>>>>> 567a50f (Major project consolidation and improvements)

---

## ✨ Features
- Automated Cloudflare Tunnel management  
- Smart monitoring & auto-restart  
- Real-time ping statistics (average, min, max, count)  
- Web dashboard + Desktop GUI  
- Cross-platform: Windows, Linux, macOS  
- Lightweight and reliable for 24/7 uptime  

---

## 📥 Installation & Usage

### 🔹 Windows
```bash
# Clone the repo
git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
cd Cloudflare-Tunnel-Monitor

# Start the Web UI
start_web_ui.bat