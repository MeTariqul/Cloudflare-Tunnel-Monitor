# 🌐 Cloudflare Tunnel Monitor v3.0 - Neon Edition

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()

> **Advanced Real-time Cloudflare Tunnel Monitoring Dashboard with Enhanced Neon UI**

A comprehensive, production-ready solution for automatically creating, monitoring, and managing Cloudflare Tunnels with an advanced web interface featuring real-time analytics, data transfer monitoring, live ping analysis, and stunning neon-themed visualizations.

## ✨ **Key Features**

### 🚀 **Core Functionality**
- **🔄 Automatic Tunnel Management**: Smart tunnel creation, monitoring, and restart on connection loss
- **📊 Real-time Dashboard**: Live monitoring with WebSocket updates and neon-themed UI
- **📈 Data Transfer Monitor**: Real-time network usage tracking with upload/download speeds
- **🏓 Live Ping Analytics**: Continuous ping monitoring with quality indicators and charts
- **📝 Live Log Monitoring**: Real-time log viewing with filtering and download capabilities
- **💾 Auto-Save URLs**: Automatic tunnel URL saving with timestamps and custom locations
- **⚙️ Advanced Settings**: Comprehensive configuration management with backup system

### 🎨 **Enhanced User Experience**
- **🌟 Neon UI Theme**: Cyberpunk-inspired black/white/neon design with glassmorphism effects
- **📱 Responsive Design**: Mobile-first approach with touch-friendly controls
- **🔄 Real-time Updates**: WebSocket-powered live data updates without page refresh
- **📊 Interactive Charts**: Beautiful Chart.js visualizations for ping and transfer data
- **🎯 Smart Notifications**: Toast notifications with neon styling for all actions

### 🛠️ **Technical Excellence**
- **🔧 Smart Auto-Setup**: Intelligent Python/venv detection and dependency management
- **🛡️ Robust Monitoring**: Multi-threaded monitoring with automatic recovery
- **💾 Configuration Backup**: Automatic config backups with version management
- **🌐 Cross-Platform**: Full Windows, Linux, and macOS support
- **⚡ High Performance**: Optimized for minimal resource usage

## 🚀 **Quick Start**

### **Option 1: Smart Launcher (Recommended)**

1. **Clone Repository**
   ```bash
   git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
   cd Cloudflare-Tunnel-Monitor
   ```

2. **Run Smart Launcher**
   ```bash
   # Windows
   launcher.bat
   
   # Linux/macOS
   chmod +x launcher.sh && ./launcher.sh
   ```

3. **Access Dashboard**
   - Open automatically in browser: `http://localhost:5000`
   - Or access manually at the displayed URL

### **Option 2: Manual Setup**

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Cloudflared**
   ```bash
   # Windows (using winget)
   winget install cloudflare.cloudflared
   
   # macOS (using Homebrew)
   brew install cloudflared
   
   # Linux (using package manager)
   # See: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

## 📋 **Requirements**

### **System Requirements**
- **Python**: 3.7 or higher
- **OS**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 100MB for application + space for logs and backups

### **Dependencies**
```
Flask>=2.0.0
Flask-SocketIO>=5.0.0
requests>=2.28.0
psutil>=5.9.0
gevent>=21.12.0
python-socketio>=5.0.0
```

## 🎛️ **Dashboard Features**

### **📊 Main Dashboard**
- **Live Ping Monitor**: Real-time ping tracking with quality indicators
- **Data Transfer Monitor**: Network usage with upload/download speeds
- **Tunnel Control**: Start/stop tunnel with status indicators
- **URL Management**: Copy tunnel URLs and access history

### **⚙️ Settings Page**
- **Network Configuration**: Tunnel URL and ping test settings
- **Timing Controls**: Check intervals and retry configurations
- **URL Storage**: Custom save locations and file management
- **Advanced Options**: Configuration backup, log management, system info

### **📈 Real-time Analytics**
- **Ping Charts**: Live ping response time visualization
- **Transfer Graphs**: Real-time upload/download speed charts
- **Status Monitoring**: Automatic tunnel and internet status tracking
- **Log Streaming**: Live log viewing with filtering and search

## 🔧 **Configuration**

### **Default Settings**
```json
{
  "tunnel_url": "http://localhost:8080",
  "check_interval": 60,
  "max_retries": 3,
  "retry_delay": 5,
  "ping_test_url": "1.1.1.1",
  "tunnel_urls_save_directory": "./",
  "tunnel_urls_filename": "tunnel_urls.txt",
  "debug_mode": false
}
```

### **URL Auto-Save Format**
```
http://localhost:8080 - 2025-09-14 - 13:19:00 - https://abc123.trycloudflare.com
```

## 📁 **Project Structure**

```
Cloudflare-Tunnel-Monitor/
├── 📄 app.py                    # Main application (all-in-one)
├── 📄 launcher.bat             # Smart Windows launcher
├── 📄 requirements.txt         # Python dependencies
├── 📄 tunnel_monitor_config.json # Configuration file
├── 📁 logs/                    # Application logs
├── 📁 config_backups/          # Configuration backups
└── 📄 README.md               # This file
```

## 🌟 **Advanced Features**

### **🔄 Smart Monitoring**
- **Multi-threaded Architecture**: Independent monitoring threads for ping, network, and status
- **Automatic Recovery**: Self-healing system with watchdog threads
- **Intelligent Fallback**: Alternative ping hosts and retry mechanisms
- **Status Synchronization**: Real-time UI sync with actual tunnel state

### **💾 Data Management**
- **Auto-Save URLs**: Every tunnel URL saved with timestamp
- **Configuration Backup**: Automatic config versioning with cleanup
- **Log Management**: Rotating logs with download and clear options
- **Export Features**: Download configs, logs, and URL history

### **🎨 UI/UX Excellence**
- **Neon Theme**: Cyberpunk-inspired design with cyan, green, pink, and yellow accents
- **Glassmorphism**: Beautiful backdrop blur effects and transparency
- **Responsive Grid**: Mobile-first design that works on all devices
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Toast Notifications**: Beautiful feedback for all user actions

## 🚀 **API Endpoints**

### **Core Operations**
- `POST /api/start` - Start tunnel monitoring
- `POST /api/stop` - Stop tunnel monitoring
- `GET /api/ping` - Get current ping data
- `GET /api/network-data` - Get network transfer data

### **Configuration**
- `GET/POST /api/settings` - Get/update settings
- `POST /api/settings/reset` - Reset to defaults
- `GET /api/download-config` - Download configuration

### **Data Management**
- `GET /api/tunnel-urls` - Get saved tunnel URLs
- `GET /api/download-tunnel-urls` - Download URL history
- `POST /api/open-save-directory` - Open save directory
- `GET /api/logs` - Get application logs
- `POST /api/clear-logs` - Clear all logs

## 🛠️ **Development**

### **Setting up Development Environment**
```bash
# Clone repository
git clone https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
cd Cloudflare-Tunnel-Monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python app.py
```

### **Building for Production**
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production settings
export FLASK_ENV=production  # Linux/macOS
# or
set FLASK_ENV=production     # Windows
python app.py
```

## 📊 **Performance**

- **Memory Usage**: ~50-100MB typical usage
- **CPU Usage**: <5% on modern systems
- **Network Impact**: Minimal (ping tests + tunnel management)
- **Response Time**: <100ms for most operations
- **Concurrent Users**: Supports multiple simultaneous connections

## 🔒 **Security**

- **Local Access**: Runs on localhost by default
- **No External Dependencies**: Core functionality works offline
- **Config Validation**: Input sanitization and validation
- **Safe File Operations**: Protected file access and manipulation
- **Error Handling**: Comprehensive error management without exposure

## 🐛 **Troubleshooting**

### **Common Issues**

**Tunnel won't start:**
```bash
# Check if cloudflared is installed
cloudflared --version

# Verify network connectivity
ping 1.1.1.1

# Check application logs
python app.py  # Look for error messages
```

**Status not updating:**
- Refresh the browser page
- Check if WebSocket connection is established
- Verify no firewall blocking local connections

**Permission errors:**
- Run as administrator (Windows) or with sudo (Linux/macOS)
- Check file/directory permissions
- Verify write access to application directory

## 📝 **Changelog**

### **v3.0.0 - Neon Edition** (Latest)
- ✨ Complete neon UI redesign with cyberpunk theme
- 📊 Added real-time data transfer monitoring
- 🏓 Enhanced live ping analytics with charts
- 💾 Automatic tunnel URL saving with custom locations
- 🔧 Smart launcher with auto-setup capabilities
- 🛡️ Robust multi-threaded monitoring system
- 📱 Mobile-first responsive design
- 🌟 WebSocket real-time updates
- ⚙️ Advanced configuration management
- 📈 Interactive Chart.js visualizations

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 **Author**

**Tariqul Islam**
- GitHub: [@MeTariqul](https://github.com/MeTariqul)
- Repository: [Cloudflare-Tunnel-Monitor](https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor)

## 🙏 **Acknowledgments**

- [Cloudflare](https://www.cloudflare.com/) for the amazing tunnel technology
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Chart.js](https://www.chartjs.org/) for beautiful visualizations
- [Socket.IO](https://socket.io/) for real-time communication

---

<div align="center">

**⭐ Star this repository if you find it helpful! ⭐**

[🐛 Report Bug](https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor/issues) • [✨ Request Feature](https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor/issues) • [📖 Documentation](https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor/wiki)

</div>