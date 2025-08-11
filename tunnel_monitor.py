import subprocess
import re
import time
import requests
import os
import signal

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
            print(f"✅ New Tunnel Link: {match.group(0)}")
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