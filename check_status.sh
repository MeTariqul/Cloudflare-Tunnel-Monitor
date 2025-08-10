#!/bin/bash

# Script to check the status of the tunnel monitor

echo "Checking Cloudflare Tunnel Monitor status..."

# Check if running as a background process
if [ -f "tunnel_monitor.pid" ]; then
    PID=$(cat tunnel_monitor.pid)
    
    if ps -p "$PID" > /dev/null; then
        echo "✅ Tunnel monitor is running as a background process with PID: $PID"
        
        # Check how long it's been running
        if command -v ps -o etime= -p "$PID" &> /dev/null; then
            RUNTIME=$(ps -o etime= -p "$PID")
            echo "   Running time: $RUNTIME"
        fi
    else
        echo "❌ Tunnel monitor is not running, but PID file exists."
        echo "   The process with PID $PID is no longer active."
        echo "   You may want to remove the stale PID file: rm tunnel_monitor.pid"
    fi
fi

# Check if running in a screen session
if command -v screen &> /dev/null; then
    if screen -list | grep -q "tunnel_monitor"; then
        echo "✅ Tunnel monitor is running in a screen session"
        echo "   To attach to it, use: screen -r tunnel_monitor"
    fi
fi

# Check if running in a tmux session
if command -v tmux &> /dev/null; then
    if tmux has-session -t tunnel_monitor 2>/dev/null; then
        echo "✅ Tunnel monitor is running in a tmux session"
        echo "   To attach to it, use: tmux attach -t tunnel_monitor"
    fi
fi

# Check if running as a systemd service
if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet tunnel-monitor; then
        echo "✅ Tunnel monitor is running as a systemd service"
        echo "   Status: $(systemctl is-active tunnel-monitor)"
        echo "   To view detailed status: sudo systemctl status tunnel-monitor"
        echo "   To view logs: sudo journalctl -u tunnel-monitor -f"
    elif systemctl is-enabled --quiet tunnel-monitor 2>/dev/null; then
        echo "❌ Tunnel monitor service is enabled but not running"
        echo "   To start it: sudo systemctl start tunnel-monitor"
        echo "   To check for errors: sudo systemctl status tunnel-monitor"
    fi
fi

# Check for running Python processes
PYTHON_PIDS=$(pgrep -f "python.*tunnel_monitor_selenium.py")
if [ -n "$PYTHON_PIDS" ]; then
    echo "✅ Found tunnel monitor Python processes:"
    for PID in $PYTHON_PIDS; do
        echo "   PID: $PID"
        if command -v ps -o etime= -p "$PID" &> /dev/null; then
            RUNTIME=$(ps -o etime= -p "$PID")
            echo "   Running time: $RUNTIME"
        fi
    done
fi

# Check for running cloudflared processes
CLOUDFLARED_PIDS=$(pgrep -f "cloudflared.*tunnel")
if [ -n "$CLOUDFLARED_PIDS" ]; then
    echo "✅ Found cloudflared tunnel processes:"
    for PID in $CLOUDFLARED_PIDS; do
        echo "   PID: $PID"
        if command -v ps -o etime= -p "$PID" &> /dev/null; then
            RUNTIME=$(ps -o etime= -p "$PID")
            echo "   Running time: $RUNTIME"
        fi
        
        # Try to get the command line to see the URL
        if [ -f "/proc/$PID/cmdline" ]; then
            CMDLINE=$(tr '\0' ' ' < /proc/$PID/cmdline)
            echo "   Command: $CMDLINE"
        fi
    done
else
    echo "❌ No cloudflared tunnel processes found"
fi

# Check for recent log files
if [ -d "logs" ]; then
    RECENT_LOGS=$(find logs -name "tunnel_monitor_*.log" -type f -mtime -1 | sort -r)
    if [ -n "$RECENT_LOGS" ]; then
        echo "✅ Recent log files found:"
        for LOG in $RECENT_LOGS; do
            echo "   $LOG"
            echo "   Last few lines:"
            tail -n 5 "$LOG" | sed 's/^/     /'
            echo ""
        done
    else
        echo "❌ No recent log files found in the logs directory"
    fi
fi

# If nothing is running, provide instructions
if [ -z "$PYTHON_PIDS" ] && [ -z "$CLOUDFLARED_PIDS" ] && \
   ! screen -list | grep -q "tunnel_monitor" && \
   ! tmux has-session -t tunnel_monitor 2>/dev/null && \
   ! (command -v systemctl &> /dev/null && systemctl is-active --quiet tunnel-monitor); then
    echo "❌ Tunnel monitor is not running"
    echo ""
    echo "To start it, use one of these methods:"
    echo "1. Run directly: ./run_tunnel_monitor_ssh.sh"
    echo "2. Run in screen: ./run_in_screen.sh"
    echo "3. Run in tmux: ./run_in_tmux.sh"
    echo "4. Run in background: ./run_in_background.sh"
    echo "5. Run as a service: sudo systemctl start tunnel-monitor"
fi

echo "Status check completed."