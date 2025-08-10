import subprocess
import re
import time
import requests
import os
import signal

# Twilio WhatsApp Config
TWILIO_SID = "your_twilio_sid"
TWILIO_AUTH = "your_twilio_auth"
WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio sandbox
WHATSAPP_TO = "whatsapp:+8801XXXXXXXXX"  # Your number

def send_whatsapp(msg):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    data = {"From": WHATSAPP_FROM, "To": WHATSAPP_TO, "Body": msg}
    try:
        requests.post(url, data=data, auth=(TWILIO_SID, TWILIO_AUTH))
        print(f"✅ Sent WhatsApp: {msg}")
    except Exception as e:
        print(f"❌ WhatsApp send failed: {e}")

def internet_available():
    try:
        requests.get("https://1.1.1.1", timeout=3)
        return True
    except:
        return False

def run_tunnel():
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        print(line.strip())
        match = re.search(r"https://[-\w]+\.trycloudflare\.com", line)
        if match:
            send_whatsapp(f"New Tunnel Link: {match.group(0)}")
    return process

def main():
    while True:
        if internet_available():
            proc = run_tunnel()
            while internet_available():
                time.sleep(5)
            os.kill(proc.pid, signal.SIGTERM)
            print("⚠ Internet disconnected — restarting tunnel...")
        else:
            time.sleep(5)

if __name__ == "__main__":
    main()