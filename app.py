#!/usr/bin/env python3
"""
Cloudflare Tunnel Monitor - All-in-One Application
A comprehensive solution for automatically creating and monitoring Cloudflare Tunnels
with embedded web interface, real-time monitoring, and ping analytics.

Author: Tariqul Islam
Repository: https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
Version: 2.0.0 (Consolidated)
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
import platform
import logging
import socket
from pathlib import Path

# Flask imports
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
from datetime import datetime as dt

# Embedded HTML Templates (to reduce file count)
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Cloudflare Tunnel Monitor{% endblock %}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #34495e;
            --accent-color: #3498db;
            --accent-hover: #2980b9;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --error-color: #e74c3c;
            --light-color: #ecf0f1;
            --text-color: #333333;
            --text-light: #7f8c8d;
            --border-color: #bdc3c7;
            --bg-color: #f5f5f5;
            --card-bg: #ffffff;
            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 2rem;
            --border-radius-sm: 4px;
            --border-radius-md: 8px;
            --border-radius-lg: 12px;
            --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
            --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12);
            --shadow-lg: 0 10px 20px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.1);
            --gradient-bg: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-card: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--gradient-bg);
            color: var(--text-color);
            line-height: 1.6;
            font-size: 16px;
            overflow-x: hidden;
            position: relative;
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(52, 152, 219, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(46, 204, 113, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(155, 89, 182, 0.05) 0%, transparent 50%);
            animation: floatingOrbs 20s ease-in-out infinite;
            pointer-events: none;
            z-index: -1;
        }
        
        @keyframes floatingOrbs {
            0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.7; }
            33% { transform: translateY(-30px) rotate(120deg); opacity: 0.9; }
            66% { transform: translateY(-60px) rotate(240deg); opacity: 0.5; }
        }
        
        .container {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 var(--spacing-sm);
            width: 100%;
        }
        
        @media (min-width: 768px) {
            .container {
                padding: 0 var(--spacing-md);
            }
        }
        
        @media (min-width: 1200px) {
            .container {
                padding: 0 var(--spacing-lg);
            }
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--spacing-md) var(--spacing-lg);
            background: var(--gradient-card);
            box-shadow: var(--shadow-md);
            border-radius: var(--border-radius-lg);
            margin: var(--spacing-md) 0 var(--spacing-xl);
            position: relative;
        }
        
        @media (max-width: 768px) {
            .header {
                flex-direction: column;
                gap: var(--spacing-md);
                padding: var(--spacing-md);
            }
        }
        
        .logo h1 {
            color: var(--primary-color);
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
        }
        
        .logo h1 i {
            margin-right: var(--spacing-sm);
            color: var(--accent-color);
        }
        
        @media (min-width: 768px) {
            .logo h1 {
                font-size: 1.75rem;
            }
        }
        
        nav {
            display: flex;
            gap: var(--spacing-md);
        }
        
        nav a {
            color: var(--text-color);
            text-decoration: none;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--border-radius-md);
            transition: all 0.3s ease;
            font-weight: 500;
            display: flex;
            align-items: center;
        }
        
        nav a:hover, nav a.active {
            background: var(--accent-color);
            color: white;
            transform: translateY(-1px);
        }
        
        nav a i {
            margin-right: var(--spacing-xs);
        }
        
        @media (max-width: 768px) {
            nav {
                flex-wrap: wrap;
                justify-content: center;
            }
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: 1fr;
            gap: var(--spacing-md);
            width: 100%;
            max-width: 100%;
            overflow-x: hidden;
            margin-bottom: var(--spacing-xl);
        }
        
        @media (min-width: 768px) {
            .dashboard {
                grid-template-columns: repeat(2, 1fr);
                gap: var(--spacing-lg);
            }
        }
        
        @media (min-width: 1024px) {
            .dashboard {
                grid-template-columns: repeat(12, 1fr);
            }
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.25);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: var(--border-radius-lg);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            padding: var(--spacing-md);
            width: 100%;
            overflow: hidden;
            position: relative;
            transition: all 0.3s ease;
        }
        
        @media (min-width: 768px) {
            .panel {
                padding: var(--spacing-lg);
            }
        }
        
        .panel:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg), 0 0 20px rgba(52, 152, 219, 0.3);
            border-color: rgba(52, 152, 219, 0.3);
        }
        
        .control-panel {
            grid-column: 1 / -1;
        }
        
        @media (min-width: 768px) {
            .stats-panel {
                grid-column: span 1;
            }
            
            .tunnel-info-panel {
                grid-column: span 1;
            }
        }
        
        @media (min-width: 1024px) {
            .stats-panel {
                grid-column: span 6;
            }
            
            .tunnel-info-panel {
                grid-column: span 6;
            }
            
            .ping-chart-panel, .logs-panel {
                grid-column: span 12;
            }
        }
        
        .panel h2 {
            font-size: 1.125rem;
            color: var(--primary-color);
            margin-bottom: var(--spacing-md);
            padding-bottom: var(--spacing-sm);
            border-bottom: 2px solid var(--light-color);
            display: flex;
            align-items: center;
            position: relative;
        }
        
        @media (min-width: 768px) {
            .panel h2 {
                font-size: 1.25rem;
            }
        }
        
        .panel h2::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 40px;
            height: 2px;
            background-color: var(--accent-color);
            border-radius: 1px;
        }
        
        .panel h2 i {
            margin-right: var(--spacing-sm);
            color: var(--accent-color);
            background: rgba(52, 152, 219, 0.1);
            padding: var(--spacing-xs);
            border-radius: var(--border-radius-sm);
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--border-radius-md);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            font-size: 1rem;
            text-decoration: none;
            position: relative;
            overflow: hidden;
            min-height: 48px;
            min-width: 120px;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            background: none;
            outline: none;
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
            margin-right: var(--spacing-sm);
            margin-bottom: var(--spacing-sm);
        }
        
        .btn i {
            margin-right: var(--spacing-sm);
        }
        
        .btn-primary {
            background: var(--gradient-primary);
            color: white;
            border: none;
            box-shadow: var(--shadow-md);
        }
        
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg), 0 0 20px rgba(52, 152, 219, 0.6);
            background: linear-gradient(135deg, #5a6fd8 0%, #6b5b95 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border: none;
            box-shadow: var(--shadow-md);
        }
        
        .btn-danger:hover:not(:disabled) {
            transform: translateY(-3px);
            box-shadow: var(--shadow-lg), 0 0 20px rgba(231, 76, 60, 0.6);
            background: linear-gradient(135deg, #e056fd 0%, #ef4e7b 100%);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }
        
        .button-group {
            display: flex;
            gap: var(--spacing-sm);
            flex-wrap: wrap;
            align-items: center;
            justify-content: flex-start;
            margin-bottom: var(--spacing-md);
        }
        
        @media (max-width: 576px) {
            .button-group {
                flex-direction: column;
                width: 100%;
            }
            
            .button-group .btn {
                width: 100%;
                justify-content: center;
            }
        }
        
        .status-indicators {
            display: flex;
            flex-direction: column;
            gap: var(--spacing-md);
            margin-top: var(--spacing-md);
        }
        
        @media (min-width: 768px) {
            .status-indicators {
                flex-direction: row;
                flex-wrap: wrap;
                gap: var(--spacing-lg);
            }
        }
        
        .status-item {
            display: flex;
            align-items: center;
            padding: var(--spacing-sm) var(--spacing-md);
            background-color: rgba(236, 240, 241, 0.3);
            border-radius: var(--border-radius-md);
            border: 1px solid rgba(189, 195, 199, 0.3);
            transition: all 0.3s ease;
            min-height: 44px;
        }
        
        .status-item:hover {
            background-color: rgba(236, 240, 241, 0.5);
            border-color: rgba(189, 195, 199, 0.5);
            transform: translateY(-1px);
        }
        
        .status-indicator {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: var(--spacing-sm);
            position: relative;
            flex-shrink: 0;
            transition: all 0.3s ease;
        }
        
        .status-indicator::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            opacity: 0.3;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.3; }
            50% { transform: scale(1.2); opacity: 0.1; }
            100% { transform: scale(1); opacity: 0.3; }
        }
        
        .status-indicator.running {
            background: radial-gradient(circle, #50d890 0%, #27ae60 100%);
            box-shadow: 0 0 15px rgba(46, 204, 113, 0.6);
        }
        
        .status-indicator.running::after {
            background: radial-gradient(circle, #50d890 0%, #27ae60 100%);
        }
        
        .status-indicator.stopped {
            background: radial-gradient(circle, #ff6b9d 0%, #e74c3c 100%);
            box-shadow: 0 0 15px rgba(231, 76, 60, 0.6);
        }
        
        .status-indicator.stopped::after {
            background: radial-gradient(circle, #ff6b9d 0%, #e74c3c 100%);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: var(--spacing-md);
        }
        
        .stat-item {
            text-align: center;
            padding: var(--spacing-md);
            background: rgba(52, 152, 219, 0.1);
            border-radius: var(--border-radius-md);
            transition: all 0.3s ease;
        }
        
        .stat-item:hover {
            background: rgba(52, 152, 219, 0.15);
            transform: translateY(-2px);
        }
        
        .stat-value {
            display: block;
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent-color);
            margin-bottom: var(--spacing-xs);
        }
        
        .stat-label {
            font-size: 0.875rem;
            color: var(--secondary-color);
        }
        
        .url-display {
            display: flex;
            gap: var(--spacing-sm);
            align-items: center;
            margin-top: var(--spacing-md);
        }
        
        .url-display input {
            flex: 1;
            padding: var(--spacing-md);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-md);
            font-size: 1rem;
            transition: border-color 0.3s;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .url-display input:focus {
            border-color: var(--accent-color);
            outline: none;
        }
        
        @media (max-width: 576px) {
            .url-display {
                flex-direction: column;
            }
            
            .url-display input {
                width: 100%;
            }
        }
        
        .chart-container {
            height: 300px;
            margin-top: var(--spacing-md);
            background: linear-gradient(135deg, 
                var(--card-bg) 0%, 
                rgba(52, 152, 219, 0.03) 30%, 
                var(--card-bg) 70%, 
                rgba(46, 204, 113, 0.03) 100%);
            border-radius: var(--border-radius-lg);
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-md);
            position: relative;
        }
        
        .logs-container {
            background: rgba(248, 249, 250, 0.9);
            border-radius: var(--border-radius-md);
            padding: var(--spacing-md);
            max-height: 300px;
            overflow-y: auto;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.875rem;
            line-height: 1.4;
        }
        
        .log-entry {
            margin-bottom: var(--spacing-xs);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--border-radius-sm);
            word-wrap: break-word;
        }
        
        .log-entry.error {
            background: rgba(231, 76, 60, 0.1);
            color: #c0392b;
            border-left: 3px solid var(--error-color);
        }
        
        .log-entry.success {
            background: rgba(46, 204, 113, 0.1);
            color: #27ae60;
            border-left: 3px solid var(--success-color);
        }
        
        .log-entry.warning {
            background: rgba(243, 156, 18, 0.1);
            color: #d35400;
            border-left: 3px solid var(--warning-color);
        }
        
        .form-group {
            margin-bottom: var(--spacing-lg);
        }
        
        .form-group label {
            display: block;
            margin-bottom: var(--spacing-xs);
            font-weight: 500;
            color: var(--text-color);
        }
        
        .form-group input, .form-group select {
            width: 100%;
            padding: var(--spacing-md);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius-md);
            font-size: 1rem;
            transition: border-color 0.3s;
            background: rgba(255, 255, 255, 0.9);
        }
        
        .form-group input:focus, .form-group select:focus {
            border-color: var(--accent-color);
            outline: none;
        }
        
        .alert {
            padding: var(--spacing-md);
            border-radius: var(--border-radius-md);
            margin-bottom: var(--spacing-lg);
            display: flex;
            align-items: flex-start;
            animation: slideInFromTop 0.3s ease-out;
        }
        
        @keyframes slideInFromTop {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .alert-success {
            background-color: rgba(46, 204, 113, 0.15);
            border-left: 4px solid var(--success-color);
            color: #27ae60;
        }
        
        .alert-error {
            background-color: rgba(231, 76, 60, 0.15);
            border-left: 4px solid var(--error-color);
            color: #c0392b;
        }
        
        /* Responsive utilities */
        @media (max-width: 480px) {
            .container {
                padding: 0 var(--spacing-xs);
            }
            
            .panel {
                padding: var(--spacing-sm);
            }
            
            .logo h1 {
                font-size: 1.25rem;
            }
            
            .btn {
                padding: var(--spacing-sm) var(--spacing-md);
                min-width: 100px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-cloud"></i> Cloudflare Tunnel Monitor</h1>
            <nav>
                <a href="/" style="margin-right: 15px;">Dashboard</a>
                <a href="/settings">Settings</a>
            </nav>
        </header>
        <main>{% block content %}{% endblock %}</main>
    </div>
    <script>window.socket = io(); {% block scripts %}{% endblock %}</script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', 
'''<div class="dashboard">
    <div class="panel">
        <h2>Tunnel Control</h2>
        <button id="start-btn" class="btn btn-primary" onclick="startTunnel()">Start Tunnel</button>
        <button id="stop-btn" class="btn btn-danger" onclick="stopTunnel()" disabled>Stop Tunnel</button>
        <div style="margin-top: 15px;">
            <div><span class="status-indicator" id="tunnel-status"></span>Tunnel: <span id="tunnel-text">Stopped</span></div>
            <div><span class="status-indicator" id="internet-status"></span>Internet: <span id="internet-text">Checking...</span></div>
        </div>
    </div>
    <div class="panel">
        <h2>Tunnel URL</h2>
        <input type="text" id="tunnel-url" value="Not available" readonly style="width: 100%; padding: 10px;">
        <button class="btn btn-primary" onclick="copyUrl()" style="margin-top: 10px;">Copy URL</button>
    </div>
</div>''').replace('{% block scripts %}{% endblock %}', 
'''async function startTunnel() {
    const response = await fetch('/api/start', {method: 'POST'});
    const data = await response.json();
    if (data.status === 'success') updateStatus('Running');
}
async function stopTunnel() {
    const response = await fetch('/api/stop', {method: 'POST'});
    const data = await response.json();
    if (data.status === 'success') updateStatus('Stopped');
}
function updateStatus(status) {
    document.getElementById('tunnel-text').textContent = status;
    const indicator = document.getElementById('tunnel-status');
    indicator.className = status === 'Running' ? 'status-indicator running' : 'status-indicator stopped';
    document.getElementById('start-btn').disabled = status === 'Running';
    document.getElementById('stop-btn').disabled = status !== 'Running';
}
function copyUrl() {
    const url = document.getElementById('tunnel-url').value;
    if (url !== 'Not available') navigator.clipboard.writeText(url);
}
socket.on('tunnel_url', (data) => document.getElementById('tunnel-url').value = data.url);''')

SETTINGS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', 
'''<div class="panel">
    <h2><i class="fas fa-cog"></i> Configuration Settings</h2>
    <form onsubmit="saveSettings(event)">
        <div class="form-group">
            <label>Tunnel URL:</label>
            <input type="url" name="tunnel_url" value="{{ config.tunnel_url }}" required>
        </div>
        <div class="form-group">
            <label>Check Interval (seconds):</label>
            <input type="number" name="check_interval" value="{{ config.check_interval }}" min="10" max="300" required>
        </div>
        <div class="form-group">
            <label>Max Retries:</label>
            <input type="number" name="max_retries" value="{{ config.max_retries }}" min="1" max="10" required>
        </div>
        <div class="form-group">
            <label>Ping Test URL:</label>
            <input type="text" name="ping_test_url" value="{{ config.ping_test_url }}" required>
        </div>
        <div class="form-group">
            <label><input type="checkbox" name="debug_mode" {% if config.debug_mode %}checked{% endif %}> Debug Mode</label>
        </div>
        <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Save Settings</button>
        <button type="button" class="btn btn-danger" onclick="resetSettings()"><i class="fas fa-undo"></i> Reset</button>
    </form>
</div>''').replace('{% block scripts %}{% endblock %}', 
'''async function saveSettings(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const settings = Object.fromEntries(formData);
    settings.debug_mode = formData.has('debug_mode');
    const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(settings)
    });
    const result = await response.json();
    alert(result.status === 'success' ? 'Settings saved!' : 'Error: ' + result.message);
}
async function resetSettings() {
    if (confirm('Reset all settings?')) {
        const response = await fetch('/api/settings/reset', {method: 'POST'});
        const result = await response.json();
        if (result.status === 'success') location.reload();
    }
}''')

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log_file = os.path.join(logs_dir, f'tunnel_monitor_web_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger('tunnel_monitor_web')
logger.info(f"Logging to {log_file}")

# Default configuration
DEFAULT_CONFIG = {
    "tunnel_url": "http://localhost:8080",  # URL to expose via Cloudflare Tunnel
    "cloudflared_path": None,  # Path to cloudflared executable (None for auto-detection)
    "check_interval": 60,  # How often to check internet connection (seconds)
    "max_retries": 3,  # Maximum number of retries when internet connection is lost
    "retry_delay": 5,  # Delay between retries (seconds)
    "debug_mode": False,  # Enable debug mode
    "github_repo": "https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git",  # GitHub repository URL
    "ping_test_url": "1.1.1.1"  # URL to ping for connectivity test
}

# Statistics
STATS = {
    "start_time": None,  # When the monitor was started
    "total_uptime": 0,  # Total uptime in seconds
    "tunnel_starts": 0,  # Number of times the tunnel was started
    "internet_disconnects": 0,  # Number of internet disconnections
    "last_check": None,  # Last time the internet was checked
    "current_status": "Stopped",  # Current status of the tunnel
    "last_tunnel_url": None  # Last tunnel URL
}

# Global variables
tunnel_process = None
stop_event = threading.Event()
log_queue = queue.Queue()
config_file = "tunnel_monitor_config.json"

# Initialize Flask app with enhanced security
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Auto-open browser flag
auto_open_browser = True

# Ping data
ping_data = {
    "last_ping_time": None,
    "ping_history": [],
    "max_history_points": 60  # Store 1 minute of data (assuming 1 ping per second)
}

# Determine the base directory
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as script
    BASE_DIR = Path(__file__).parent

# Utility functions
def log(message, level="info"):
    """Log a message to the console and the log queue"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "level": level
    }
    log_queue.put(log_entry)
    
    # Also log to the logger
    if level == "error":
        logger.error(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "success":
        logger.info(f"SUCCESS: {message}")
    elif level == "debug":
        logger.debug(message)
    else:
        logger.info(message)

def load_config():
    """Load configuration from file or create default"""
    config_path = os.path.join(BASE_DIR, config_file)
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Update with any missing default values
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                log(f"Configuration loaded from {config_path}")
                return config
    except Exception as e:
        log(f"Error loading configuration: {e}", level="error")
    
    # Create default configuration
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    return config

def save_config(config):
    """Save configuration to file with backup"""
    config_path = os.path.join(BASE_DIR, config_file)
    backup_dir = os.path.join(BASE_DIR, 'config_backups')
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # Create a backup of the current config if it exists
        if os.path.exists(config_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"config_backup_{timestamp}.json")
            try:
                with open(config_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                log(f"Configuration backup created at {backup_path}")
            except Exception as e:
                log(f"Error creating configuration backup: {e}", level="warning")
        
        # Save the new configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        log(f"Configuration saved to {config_path}", level="success")
        
        # Clean up old backups (keep only the 5 most recent)
        try:
            backups = sorted([
                os.path.join(backup_dir, f) for f in os.listdir(backup_dir)
                if f.startswith("config_backup_") and f.endswith(".json")
            ], key=os.path.getmtime)
            
            for old_backup in backups[:-5]:
                os.remove(old_backup)
                log(f"Removed old backup: {old_backup}", level="debug")
        except Exception as e:
            log(f"Error cleaning up old backups: {e}", level="warning")
            
    except Exception as e:
        log(f"Error saving configuration: {e}", level="error")

def reset_config():
    """Reset configuration to default values"""
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    log("Configuration reset to default values", level="success")
    return config

def ping_host(host="1.1.1.1", timeout=1000):
    """Ping a host and return the response time in milliseconds
    
    Args:
        host (str): The host to ping
        timeout (int): Timeout in milliseconds
        
    Returns:
        float or None: Response time in milliseconds if successful, None if failed
    """
    # Determine the appropriate ping command based on the OS
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    
    # On Linux/Mac, timeout is in seconds, on Windows it's in milliseconds
    timeout_value = str(timeout) if platform.system().lower() == "windows" else str(timeout / 1000)
    
    try:
        # Hide the console output
        with open(os.devnull, 'w') as DEVNULL:
            # Run the ping command and capture output
            output = subprocess.check_output(
                ["ping", param, "1", timeout_param, timeout_value, host],
                stderr=DEVNULL,
                universal_newlines=True
            )
            
            # Parse the output to extract the time
            if platform.system().lower() == "windows":
                # Windows format: "Reply from 1.1.1.1: bytes=32 time=15ms TTL=57"
                match = re.search(r"time=([0-9]+)ms", output)
            else:
                # Linux/Mac format: "64 bytes from 1.1.1.1: icmp_seq=1 ttl=57 time=14.5 ms"
                match = re.search(r"time=([0-9.]+) ms", output)
                
            if match:
                return float(match.group(1))
            return 0.0  # Successful ping but couldn't parse time
    except subprocess.CalledProcessError:
        # Ping failed
        return None
    except Exception as e:
        logger.error(f"Error pinging {host}: {e}")
        return None

def internet_available():
    """Check if internet connection is available"""
    try:
        # Try to ping Cloudflare's DNS
        result = ping_host("1.1.1.1", 3000)
        return result is not None
    except:
        # Fallback to HTTP request if ping fails
        try:
            requests.get("https://1.1.1.1", timeout=3)
            return True
        except:
            return False

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
            if tunnel_process and tunnel_process.stdout:
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
                        
                        # Emit the tunnel URL to connected clients
                        socketio.emit('tunnel_url', {'url': tunnel_url})
        
        # Start the monitoring thread
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return tunnel_process
    except Exception as e:
        log(f"Error starting cloudflared: {e}", level="error")
        return None

def stop_tunnel():
    """Stop the cloudflared tunnel process"""
    global tunnel_process
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
            log(f"Error stopping cloudflared: {e}", level="error")
            # Force kill if normal termination fails
            try:
                if os.name == 'nt':  # Windows
                    os.system(f"taskkill /F /PID {tunnel_process.pid}")
                else:  # Linux/Mac
                    os.kill(tunnel_process.pid, signal.SIGKILL)
                log("Cloudflared tunnel force-stopped", level="warning")
            except:
                pass
        tunnel_process = None
        STATS["current_status"] = "Stopped"

def monitor_thread_func(config):
    """Main monitoring thread function"""
    global tunnel_process
    
    STATS["start_time"] = datetime.now()
    retry_count = 0
    
    while not stop_event.is_set():
        # Check internet connection
        if internet_available():
            # If tunnel is not running, start it
            if tunnel_process is None or tunnel_process.poll() is not None:
                # Reset retry count on successful internet connection
                retry_count = 0
                tunnel_process = run_tunnel(config)
        else:
            # Internet is down
            log("Internet connection lost", level="warning")
            STATS["internet_disconnects"] += 1
            
            # Stop the tunnel if it's running
            if tunnel_process and tunnel_process.poll() is None:
                stop_tunnel()
            
            # Retry with backoff
            retry_count += 1
            if retry_count <= config["max_retries"]:
                retry_delay = config["retry_delay"] * retry_count
                log(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{config['max_retries']})")
                
                # Wait for the retry delay, checking for stop event
                for _ in range(retry_delay):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
            else:
                log(f"Maximum retries ({config['max_retries']}) exceeded. Waiting for internet connection...")
                # Wait for internet to come back
                while not internet_available() and not stop_event.is_set():
                    time.sleep(config["check_interval"])
                
                # Reset retry count when internet is back
                if not stop_event.is_set():
                    log("Internet connection restored", level="success")
                    retry_count = 0
        
        # Update uptime
        if STATS["start_time"]:
            STATS["total_uptime"] = (datetime.now() - STATS["start_time"]).total_seconds()
        
        # Wait for the check interval
        for _ in range(config["check_interval"]):
            if stop_event.is_set():
                break
            time.sleep(1)

def cleanup():
    """Clean up resources before exiting"""
    stop_tunnel()

# Flask routes
@app.route('/')
def index():
    """Render the main dashboard page"""
    config = load_config()
    return render_template_string(DASHBOARD_TEMPLATE, config=config, stats=STATS, current_year=dt.now().year)

@app.route('/ping_test')
def ping_test():
    """Ping a host and return the result"""
    config = load_config()
    host = request.args.get('host', config.get('ping_test_url', '1.1.1.1'))
    result = ping_host(host)
    
    # Update ping history
    timestamp = datetime.now().strftime("%H:%M:%S")
    ping_data["last_ping_time"] = timestamp
    
    if result is not None:
        ping_data["ping_history"].append({
            "timestamp": timestamp,
            "ping_time": result
        })
        
        # Keep only the last minute of ping results
        if len(ping_data["ping_history"]) > ping_data["max_history_points"]:
            ping_data["ping_history"].pop(0)
        
        # Calculate statistics
        ping_values = [p["ping_time"] for p in ping_data["ping_history"]]
        avg_ping = sum(ping_values) / len(ping_values) if ping_values else 0
        min_ping = min(ping_values) if ping_values else 0
        max_ping = max(ping_values) if ping_values else 0
        
        return jsonify({
            "success": True,
            "ping": result,
            "timestamp": timestamp,
            "host": host,
            "stats": {
                "avg": round(avg_ping, 2),
                "min": round(min_ping, 2),
                "max": round(max_ping, 2),
                "count": len(ping_values)
            }
        })
    else:
        return jsonify({
            "success": False,
            "error": "Ping failed",
            "timestamp": timestamp,
            "host": host
        })

@app.route('/settings')
def settings():
    """Settings page"""
    config = load_config()
    return render_template_string(SETTINGS_TEMPLATE, config=config, current_year=dt.now().year)

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the tunnel monitor"""
    global stop_event
    config = load_config()
    
    if tunnel_process and tunnel_process.poll() is None:
        return jsonify({"status": "error", "message": "Tunnel is already running"})
    
    # Reset the stop event
    stop_event.clear()
    
    # Start the monitor thread
    monitor_thread = threading.Thread(target=monitor_thread_func, args=(config,))
    monitor_thread.daemon = True
    monitor_thread.start()
    
    log("Monitor started", level="success")
    return jsonify({"status": "success", "message": "Tunnel monitor started"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the tunnel monitor"""
    global stop_event
    
    # Set the stop event to signal threads to exit
    stop_event.set()
    
    # Stop the tunnel
    stop_tunnel()
    
    log("Monitor stopped", level="warning")
    return jsonify({"status": "success", "message": "Tunnel monitor stopped"})

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or save settings"""
    config = load_config()
    
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.get_json()
            
            # Update configuration with JSON data
            config["tunnel_url"] = data.get("tunnel_url", config["tunnel_url"])
            config["check_interval"] = int(data.get("check_interval", config["check_interval"]))
            config["max_retries"] = int(data.get("max_retries", config["max_retries"]))
            config["retry_delay"] = int(data.get("retry_delay", config["retry_delay"]))
            config["ping_test_url"] = data.get("ping_test_url", config["ping_test_url"])
            config["debug_mode"] = data.get("debug_mode", config["debug_mode"])
            
            # Save the updated configuration
            save_config(config)
            
            return jsonify({"status": "success", "message": "Settings saved successfully"})
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return jsonify({"status": "error", "message": str(e)})
    else:
        # Return current settings
        return jsonify(config)

@app.route('/api/settings/reset', methods=['POST'])
def api_reset_settings():
    """Reset settings to defaults"""
    config = reset_config()
    return jsonify({"status": "success", "message": "Settings reset to defaults"})

@app.route('/api/stats')
def api_stats():
    """Get current statistics"""
    # Update uptime if the monitor is running
    if STATS["start_time"]:
        STATS["total_uptime"] = (datetime.now() - STATS["start_time"]).total_seconds()
    
    return jsonify(STATS)

@app.route('/api/logs')
def api_logs():
    """Get logs"""
    logs = []
    while not log_queue.empty():
        try:
            logs.append(log_queue.get_nowait())
        except queue.Empty:
            break
    
    return jsonify(logs)

@app.route('/api/ping')
def api_ping():
    """Get current ping data with statistics"""
    global ping_data
    
    # If ping monitoring hasn't started yet, return None
    if ping_data["last_ping_time"] is None:
        return jsonify({"last_ping_time": None, "ping_history": [], "stats": None})
    
    # Calculate statistics from ping history
    stats = calculate_ping_stats(ping_data["ping_history"])
    
    return jsonify({
        "last_ping_time": ping_data["last_ping_time"],
        "ping_history": ping_data["ping_history"],
        "stats": stats
    })

def calculate_ping_stats(ping_history):
    """Calculate statistics from ping history"""
    if not ping_history:
        return {
            "avg": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }
    
    ping_times = [entry["ping_time"] for entry in ping_history if "ping_time" in entry]
    
    if not ping_times:
        return {
            "avg": 0,
            "min": 0,
            "max": 0,
            "count": 0
        }
    
    return {
        "avg": sum(ping_times) / len(ping_times),
        "min": min(ping_times),
        "max": max(ping_times),
        "count": len(ping_times)
    }

# Global ping monitor thread
ping_monitor_running = False
ping_monitor_thread_instance = None
internet_monitor_running = False
internet_monitor_thread_instance = None

def start_independent_ping_monitor():
    """Start ping monitoring independent of tunnel status"""
    global ping_monitor_running, ping_monitor_thread_instance
    
    if not ping_monitor_running:
        ping_monitor_running = True
        ping_monitor_thread_instance = threading.Thread(target=independent_ping_monitor_thread)
        ping_monitor_thread_instance.daemon = True
        ping_monitor_thread_instance.start()
        log("Independent ping monitor started", level="info")

def start_independent_internet_monitor():
    """Start internet monitoring independent of tunnel status"""
    global internet_monitor_running, internet_monitor_thread_instance
    
    if not internet_monitor_running:
        internet_monitor_running = True
        internet_monitor_thread_instance = threading.Thread(target=independent_internet_monitor_thread)
        internet_monitor_thread_instance.daemon = True
        internet_monitor_thread_instance.start()
        log("Independent internet monitor started", level="info")

def independent_ping_monitor_thread():
    """Independent ping monitoring thread that runs continuously"""
    global ping_data, ping_monitor_running
    
    max_history_size = ping_data["max_history_points"]
    
    while ping_monitor_running:
        try:
            # Get the current ping time using the configured ping_test_url
            config = load_config()
            ping_url = config.get("ping_test_url", "1.1.1.1")
            ping_time = ping_host(ping_url)
            
            # Update ping data
            ping_data["last_ping_time"] = ping_time
            
            # Add to history and maintain max size
            current_time = time.time()  # Unix timestamp
            ping_data["ping_history"].append({"timestamp": current_time, "ping_time": ping_time})
            if len(ping_data["ping_history"]) > max_history_size:
                ping_data["ping_history"].pop(0)
            
            # Calculate statistics
            stats = calculate_ping_stats(ping_data["ping_history"])
            
            # Emit the ping data to all connected clients
            socketio.emit('ping_data', {
                'last_ping_time': ping_time,
                'ping_history': ping_data["ping_history"],
                'stats': stats
            })
            
            # Wait for 1 second before the next ping
            for _ in range(10):  # Check ping_monitor_running every 0.1 seconds
                if not ping_monitor_running:
                    break
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in ping monitor thread: {e}")
            time.sleep(1)

def independent_internet_monitor_thread():
    """Independent internet monitoring thread that runs continuously"""
    global internet_monitor_running
    
    while internet_monitor_running:
        try:
            # Check internet connection
            is_connected = internet_available()
            
            # Emit the internet status to all connected clients
            socketio.emit('internet_status', {'status': is_connected})
            
            # Wait for 5 seconds before the next check
            for _ in range(50):  # Check internet_monitor_running every 0.1 seconds
                if not internet_monitor_running:
                    break
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in internet monitor thread: {e}")
            time.sleep(5)

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('status', {'status': STATS["current_status"]})
    if STATS["last_tunnel_url"]:
        emit('tunnel_url', {'url': STATS["last_tunnel_url"]})
    
    # Send current internet status
    is_connected = internet_available()
    emit('internet_status', {'status': is_connected})
    
    # Send current ping data if available
    global ping_data
    if ping_data["last_ping_time"] is not None:
        # Calculate statistics
        stats = calculate_ping_stats(ping_data["ping_history"])
        
        emit('ping_data', {
            'last_ping_time': ping_data["last_ping_time"],
            'ping_history': ping_data["ping_history"],
            'stats': stats
        })

# Main function
def main():
    """Main function"""
    try:
        # Load configuration
        config = load_config()
        
        # Start independent monitoring threads
        start_independent_ping_monitor()
        start_independent_internet_monitor()
        
        # Get available port
        port = 5000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while port < 5100:
            try:
                s.bind(('0.0.0.0', port))
                s.close()
                break
            except socket.error:
                port += 1
                # If we've tried 100 ports and none are available, use a random high port
                if port >= 5100:
                    import random
                    port = random.randint(8000, 9000)
        
        # Start the web server
        host = '0.0.0.0'  # Listen on all interfaces
        log(f"Starting web server on http://{host}:{port}")
        
        # Check if auto_open_browser is enabled via environment variable
        global auto_open_browser
        auto_open_browser = os.environ.get('FLASK_AUTO_OPEN_BROWSER', '1') == '1'
        
        # Auto-open browser
        if auto_open_browser:
            import webbrowser
            url = f"http://localhost:{port}"
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()
            log(f"Opening browser to {url}")
            log(f"Access from other devices: http://{socket.gethostbyname(socket.gethostname())}:{port}")
        
        socketio.run(app, host=host, port=port, debug=config["debug_mode"])
    except KeyboardInterrupt:
        log("Shutting down...", level="warning")
        # Stop independent monitors
        global ping_monitor_running, internet_monitor_running
        ping_monitor_running = False
        internet_monitor_running = False
    except Exception as e:
        log(f"Error: {e}", level="error")
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    main()