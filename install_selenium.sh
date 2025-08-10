#!/bin/bash

# Exit on error
set -e

echo "===== Installing Cloudflare Tunnel Monitor with WhatsApp Web Automation ====="

# Update package lists
echo "Updating package lists..."
sudo apt update

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv wget unzip xvfb

# Install Chrome and ChromeDriver dependencies
echo "Installing Chrome dependencies..."
sudo apt install -y libxss1 libappindicator1 libindicator7 fonts-liberation xdg-utils
sudo apt install -y libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcairo2 libcups2 libgbm1 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 libxrandr2

# Install Chrome browser
echo "Installing Chrome browser..."
if ! command -v google-chrome &> /dev/null && ! command -v google-chrome-stable &> /dev/null; then
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt update
    sudo apt install -y google-chrome-stable
else
    echo "Chrome is already installed"
fi

# Install cloudflared
echo "Installing cloudflared..."
if ! command -v cloudflared &> /dev/null; then
    echo "Downloading cloudflared..."
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb
    
    # Also download the executable version for direct use
    curl -L --output cloudflared-linux-amd64 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared-linux-amd64
else
    echo "cloudflared is already installed"
    # Still download the executable version for direct use
    curl -L --output cloudflared-linux-amd64 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared-linux-amd64
fi

# Create installation directory
echo "Creating installation directory..."
sudo mkdir -p /opt/cloudflare_tunnel_monitor

# Copy files
echo "Copying files..."
sudo cp tunnel_monitor_selenium.py /opt/cloudflare_tunnel_monitor/
sudo cp cloudflared-linux-amd64 /opt/cloudflare_tunnel_monitor/

# Create service file for the Selenium version
echo "Creating service file..."
cat > tunnel-monitor-selenium.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel Monitor with WhatsApp Web Automation
After=network.target

[Service]
Environment="DISPLAY=:99"
Environment="HEADLESS=true"
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -ac
ExecStart=/opt/cloudflare_tunnel_monitor/venv/bin/python /opt/cloudflare_tunnel_monitor/tunnel_monitor_selenium.py
Restart=always
User=root
WorkingDirectory=/opt/cloudflare_tunnel_monitor

[Install]
WantedBy=multi-user.target
EOF

sudo cp tunnel-monitor-selenium.service /etc/systemd/system/

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
sudo python3 -m venv /opt/cloudflare_tunnel_monitor/venv
sudo /opt/cloudflare_tunnel_monitor/venv/bin/pip install requests selenium undetected-chromedriver

# Set permissions
echo "Setting permissions..."
sudo chmod +x /opt/cloudflare_tunnel_monitor/tunnel_monitor_selenium.py

# Create a run script for manual execution
cat > run_tunnel_monitor.sh << 'EOF'
#!/bin/bash

# Change to the installation directory
cd /opt/cloudflare_tunnel_monitor

# Activate the virtual environment
source venv/bin/activate

# Run the tunnel monitor
python tunnel_monitor_selenium.py
EOF

chmod +x run_tunnel_monitor.sh
sudo cp run_tunnel_monitor.sh /opt/cloudflare_tunnel_monitor/

# Enable service
echo "Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable tunnel-monitor-selenium

echo "===== Installation Complete ====="
echo ""
echo "IMPORTANT: Before starting the service, edit /opt/cloudflare_tunnel_monitor/tunnel_monitor_selenium.py"
echo "and update the WHATSAPP_CONTACT and TUNNEL_URL variables."
echo ""
echo "To run manually (with visible browser for QR code scanning):"
echo "  sudo /opt/cloudflare_tunnel_monitor/run_tunnel_monitor.sh"
echo ""
echo "To start as a service (headless mode):"
echo "  sudo systemctl start tunnel-monitor-selenium"
echo "To check status:"
echo "  sudo systemctl status tunnel-monitor-selenium"
echo "To view logs:"
echo "  sudo journalctl -u tunnel-monitor-selenium -f"