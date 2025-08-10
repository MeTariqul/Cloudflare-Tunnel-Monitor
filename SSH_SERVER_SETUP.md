# Setting Up Cloudflare Tunnel Monitor on an SSH Server

This guide provides step-by-step instructions for setting up and running the Cloudflare Tunnel Monitor on an SSH server.

## Prerequisites

- SSH access to a Linux server (Ubuntu recommended)
- Python 3.6 or higher installed on the server
- Chrome or Chromium browser installed (for WhatsApp Web automation)
- Basic knowledge of Linux commands

## Step 1: Transfer Files to the Server

First, transfer the necessary files to your SSH server using SCP or SFTP:

```bash
scp -r cloudflare_tunnel_monitor/ user@your-server-ip:~/
```

Alternatively, you can clone the repository directly on the server:

```bash
git clone https://github.com/yourusername/cloudflare_tunnel_monitor.git
```

## Step 2: Make Scripts Executable

SSH into your server and make the scripts executable:

```bash
ssh user@your-server-ip
cd cloudflare_tunnel_monitor
chmod +x *.sh
```

## Step 3: Download Cloudflared

Download the Linux version of cloudflared:

```bash
curl -L --output cloudflared-linux-amd64.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

Alternatively, download the executable directly:

```bash
curl -L --output cloudflared-linux-amd64 https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
```

## Step 4: Update Configuration

Edit the `tunnel_monitor_selenium.py` file to update the configuration:

```bash
nano tunnel_monitor_selenium.py
```

Update the following variables:

- `WHATSAPP_CONTACT`: Set to the name of your WhatsApp contact
- `TUNNEL_URL`: Set to the URL of your local service (e.g., `http://localhost:8080`)
- If needed, update the `cloudflared_cmd` in the `run_tunnel()` function to match your setup

## Step 5: Run the Monitor

You have several options for running the tunnel monitor:

### Option 1: Run Directly

Run the script directly with the virtual environment:

```bash
./run_tunnel_monitor_ssh.sh
```

This will create a virtual environment, install dependencies, and run the script. You'll need to scan the QR code to authenticate WhatsApp Web.

### Option 2: Activate Environment Separately

Activate the virtual environment and run the script separately:

```bash
source activate_venv_ssh.sh
python tunnel_monitor_selenium.py
```

### Option 3: Run as a Background Service

To run the script in the background and keep it running after you log out:

```bash
nohup python tunnel_monitor_selenium.py > tunnel_monitor.log 2>&1 &
```

You can check the log file to monitor progress:

```bash
tail -f tunnel_monitor.log
```

### Option 4: Set Up as a Systemd Service

For a more robust solution, set up a systemd service:

1. Create a service file:

```bash
sudo nano /etc/systemd/system/tunnel-monitor.service
```

2. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=Cloudflare Tunnel Monitor with WhatsApp Web
After=network.target

[Service]
User=your-username
WorkingDirectory=/home/your-username/cloudflare_tunnel_monitor
ExecStart=/home/your-username/cloudflare_tunnel_monitor/venv/bin/python /home/your-username/cloudflare_tunnel_monitor/tunnel_monitor_selenium.py
Restart=always
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tunnel-monitor
sudo systemctl start tunnel-monitor
```

4. Check the service status:

```bash
sudo systemctl status tunnel-monitor
```

5. View logs:

```bash
sudo journalctl -u tunnel-monitor -f
```

## Troubleshooting

### WhatsApp Authentication

- For the first run, you must authenticate WhatsApp Web by scanning the QR code
- If running as a service, run the script manually first to authenticate
- Authentication may expire periodically, requiring re-scanning the QR code

### Cloudflared Issues

- If you get a `FileNotFoundError` for cloudflared, check the path in the script
- Make sure the cloudflared executable has execute permissions
- Check that the URL format is correct (avoid hash fragments or special characters)
- Try simplifying the URL (e.g., use `http://192.168.100.1:8096/web/` instead of `http://192.168.100.1:8096/web/#/home.html`)

### Chrome Not Found

- If Chrome is not found, install it or specify the path in the script:

```bash
sudo apt update
sudo apt install chromium-browser
```

Then update the `CHROME_PATH` variable in the script:

```python
CHROME_PATH = "/usr/bin/chromium-browser"
```

### Headless Mode Issues

If you're running in headless mode and having issues:

1. Install Xvfb for virtual display:

```bash
sudo apt install xvfb
```

2. Run with a virtual display:

```bash
xvfb-run python tunnel_monitor_selenium.py
```

Or update the service file to use Xvfb.

## Keeping the Script Running

To ensure the script keeps running even after SSH disconnection:

1. Use `screen` or `tmux`:

```bash
screen -S tunnel
./run_tunnel_monitor_ssh.sh
# Press Ctrl+A, D to detach
# To reattach: screen -r tunnel
```

2. Use `nohup` as mentioned earlier

3. Set up a systemd service as described above (recommended)

## Conclusion

Your Cloudflare Tunnel Monitor should now be running on your SSH server. It will automatically create a tunnel to your specified service, monitor the internet connection, and send the tunnel URL via WhatsApp when the tunnel is established.