#!/usr/bin/env python3
"""
Cloudflare Tunnel Monitor - Enhanced All-in-One Application
A comprehensive solution for automatically creating and monitoring Cloudflare Tunnels
with advanced web interface, real-time monitoring, ping analytics, and QR code generation.

Features:
- Live Ping Monitor with real-time charts
- Auto-generating QR codes for tunnel URLs
- Advanced network diagnostics
- Responsive mobile-first design
- Real-time WebSocket updates
- Enhanced security monitoring
- System resource monitoring
- Multi-theme support

Author: Tariqul Islam
Repository: https://github.com/MeTariqul/Cloudflare-Tunnel-Monitor.git
Version: 3.0.0 (Enhanced Redesign)
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
import psutil  # For system monitoring
import base64
import io
import hashlib
import urllib.parse
from typing import Dict, List, Optional, Any

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
    <title>Cloudflare Tunnel Monitor v3.0 - Enhanced Dashboard</title>
    <script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            /* Neon Black/White Color Scheme */
            --primary-gradient: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            --secondary-gradient: linear-gradient(145deg, #00ffff, #0080ff);
            --success-gradient: linear-gradient(45deg, #00ff00, #00cc00);
            --danger-gradient: linear-gradient(45deg, #ff0080, #ff0040);
            --warning-gradient: linear-gradient(45deg, #ffff00, #ff8000);
            --neon-cyan: #00ffff;
            --neon-green: #00ff00;
            --neon-pink: #ff0080;
            --neon-yellow: #ffff00;
            --glass-bg: rgba(0, 0, 0, 0.8);
            --glass-border: rgba(0, 255, 255, 0.3);
            --text-primary: #ffffff;
            --text-light: rgba(255, 255, 255, 0.9);
            --text-neon: #00ffff;
            --shadow-light: 0 8px 32px rgba(0, 255, 255, 0.2);
            --shadow-heavy: 0 20px 40px rgba(0, 255, 255, 0.4);
            --shadow-neon: 0 0 20px currentColor;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%);
            min-height: 100vh;
            color: var(--text-primary);
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
            background: radial-gradient(circle at 20% 80%, rgba(0, 255, 255, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 20%, rgba(255, 0, 128, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 40% 40%, rgba(0, 255, 0, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }

        .theme-switcher {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border-radius: 50px;
            padding: 10px;
            border: 1px solid var(--glass-border);
        }

        .theme-btn {
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            padding: 8px 12px;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 2px;
        }

        .theme-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: scale(1.1);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 30px;
            border: 2px solid var(--neon-cyan);
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), inset 0 0 30px rgba(0, 255, 255, 0.1);
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.05), transparent);
            transform: rotate(45deg);
            animation: headerShimmer 6s infinite;
        }

        @keyframes headerShimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }

        .header h1 {
            font-size: 2.8rem;
            margin-bottom: 10px;
            color: var(--neon-cyan);
            text-shadow: 0 0 20px currentColor, 0 0 40px currentColor;
            position: relative;
            z-index: 1;
            font-weight: 700;
        }

        .header .version {
            color: #ffd700;
            font-size: 0.8rem;
            font-weight: normal;
        }

        .header p {
            font-size: 1.2rem;
            color: var(--text-light);
            margin-bottom: 20px;
            position: relative;
            z-index: 1;
        }

        .panel {
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 25px;
            border: 2px solid var(--neon-cyan);
            margin-bottom: 20px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-light), inset 0 0 20px rgba(0, 255, 255, 0.1);
        }

        .panel:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-heavy), 0 0 30px var(--neon-cyan);
            border-color: var(--neon-green);
        }

        .panel h2 {
            color: var(--neon-cyan) !important;
            text-shadow: 0 0 10px currentColor;
            border-bottom: 2px solid var(--neon-cyan);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .btn {
            background: linear-gradient(45deg, #000000, #1a1a1a);
            color: var(--neon-cyan);
            border: 2px solid var(--neon-cyan);
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            margin: 5px;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            text-shadow: 0 0 5px currentColor;
            font-weight: 600;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 25px var(--neon-cyan), 0 4px 15px rgba(0, 0, 0, 0.3);
            background: var(--neon-cyan);
            color: #000000;
            text-shadow: none;
        }

        .btn.danger {
            color: var(--neon-pink);
            border-color: var(--neon-pink);
            box-shadow: 0 0 15px rgba(255, 0, 128, 0.3);
        }

        .btn.danger:hover {
            background: var(--neon-pink);
            box-shadow: 0 0 25px var(--neon-pink), 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .btn.warning {
            color: var(--neon-yellow);
            border-color: var(--neon-yellow);
            box-shadow: 0 0 15px rgba(255, 255, 0, 0.3);
        }

        .btn.warning:hover {
            background: var(--neon-yellow);
            box-shadow: 0 0 25px var(--neon-yellow), 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .btn.secondary {
            color: #ffffff;
            border-color: #ffffff;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
        }

        .btn.secondary:hover {
            background: #ffffff;
            color: #000000;
            box-shadow: 0 0 25px #ffffff, 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            display: inline-block;
        }

        .status-indicator.running {
            background: var(--neon-green);
            animation: pulse 2s infinite;
            box-shadow: 0 0 10px var(--neon-green);
        }

        .status-indicator.stopped {
            background: var(--neon-pink);
            box-shadow: 0 0 10px var(--neon-pink);
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7), 0 0 10px currentColor; }
            70% { box-shadow: 0 0 0 10px rgba(0, 255, 0, 0), 0 0 20px currentColor; }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 0, 0), 0 0 10px currentColor; }
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2.2rem;
            }
            
            .theme-switcher {
                top: 10px;
                right: 10px;
            }
        }

        /* Dark theme */
        body.dark-theme {
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        }

        body.dark-theme .panel {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        body.dark-theme .btn {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        /* Light theme */
        body.light-theme {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
        }

        body.light-theme .panel {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(0, 0, 0, 0.1);
            color: #333;
        }

        body.light-theme .header h1,
        body.light-theme h2,
        body.light-theme h3 {
            color: #333;
        }

        body.light-theme .input-group input,
        body.light-theme .input-group select,
        body.light-theme .input-group textarea {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            border: 1px solid #ddd;
        }

        body.light-theme .input-group label {
            color: #333;
        }

        body.light-theme .btn {
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        /* Theme switcher in settings */
        .theme-switcher-settings button.active {
            background: var(--success-gradient) !important;
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
        }

        .notification {
            position: fixed;
            top: 80px;
            right: 20px;
            background: var(--success-gradient);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: var(--shadow-light);
            z-index: 1500;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            font-weight: 500;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.error {
            background: var(--danger-gradient);
        }

        .notification.warning {
            background: var(--warning-gradient);
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1><i class="fas fa-cloud"></i> Cloudflare Tunnel Monitor <span class="version">v3.0</span></h1>
            <p>Enhanced Real-time Dashboard with Advanced Features</p>
            <nav style="margin-top: 15px;">
                <a href="/" class="btn secondary" style="text-decoration: none; margin: 0 5px;">
                    <i class="fas fa-tachometer-alt"></i> Dashboard
                </a>
                <a href="/settings" class="btn secondary" style="text-decoration: none; margin: 0 5px;">
                    <i class="fas fa-cog"></i> Settings
                </a>
            </nav>
        </header>
        <main>{% block content %}{% endblock %}</main>
    </div>
    
    <script>
        // Theme management (removed - only default mode)
        // Notification system
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'exclamation'}"></i> ${message}`;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.classList.add('show'), 100);
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }
        
        // Socket.IO initialization
        window.socket = io();
        
        {% block scripts %}{% endblock %}
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', 
'''<div class="dashboard">
    <!-- Live Ping Monitor Panel - NEW PROMINENT SECTION -->
    <div class="panel live-ping-monitor">
        <h2><i class="fas fa-heartbeat"></i> Live Ping Monitor</h2>
        <div class="live-ping-display">
            <div class="ping-current">
                <div class="ping-label">Current Ping</div>
                <div class="ping-value-large" id="live-ping-current">--ms</div>
                <div class="ping-status-text" id="live-ping-status">Initializing...</div>
            </div>
            <div class="ping-stats-grid">
                <div class="ping-stat">
                    <div class="stat-label">Average</div>
                    <div class="stat-value" id="live-ping-avg">--ms</div>
                </div>
                <div class="ping-stat">
                    <div class="stat-label">Minimum</div>
                    <div class="stat-value" id="live-ping-min">--ms</div>
                </div>
                <div class="ping-stat">
                    <div class="stat-label">Maximum</div>
                    <div class="stat-value" id="live-ping-max">--ms</div>
                </div>
                <div class="ping-stat">
                    <div class="stat-label">Packets</div>
                    <div class="stat-value" id="live-ping-count">0</div>
                </div>
            </div>
        </div>
        <div class="ping-chart-mini">
            <canvas id="livePingChart" width="400" height="100"></canvas>
        </div>
    </div>
    
    <!-- Data Transfer Monitor Panel - NEW SECTION -->
    <div class="panel data-transfer-monitor">
        <h2><i class="fas fa-exchange-alt"></i> Data Transfer Monitor</h2>
        <div class="transfer-display">
            <div class="transfer-totals">
                <div class="transfer-total upload">
                    <div class="transfer-icon"><i class="fas fa-upload"></i></div>
                    <div class="transfer-info">
                        <div class="transfer-label">Total Upload</div>
                        <div class="transfer-value" id="total-upload">-- GB</div>
                    </div>
                </div>
                <div class="transfer-total download">
                    <div class="transfer-icon"><i class="fas fa-download"></i></div>
                    <div class="transfer-info">
                        <div class="transfer-label">Total Download</div>
                        <div class="transfer-value" id="total-download">-- GB</div>
                    </div>
                </div>
            </div>
            <div class="transfer-speeds">
                <div class="speed-display">
                    <div class="speed-current upload">
                        <div class="speed-label"><i class="fas fa-arrow-up"></i> Upload Speed</div>
                        <div class="speed-value" id="current-upload-speed">-- KB/s</div>
                    </div>
                    <div class="speed-current download">
                        <div class="speed-label"><i class="fas fa-arrow-down"></i> Download Speed</div>
                        <div class="speed-value" id="current-download-speed">-- KB/s</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="transfer-chart">
            <canvas id="transferChart" width="400" height="120"></canvas>
        </div>
    </div>
    
    <div class="panel">
        <h2><i class="fas fa-power-off"></i> Tunnel Control</h2>
        <button id="start-btn" class="btn" onclick="startTunnel()"><i class="fas fa-play"></i> Start Tunnel</button>
        <button id="stop-btn" class="btn danger" onclick="stopTunnel()" disabled><i class="fas fa-stop"></i> Stop Tunnel</button>
        <div style="margin-top: 15px;">
            <div style="margin-bottom: 8px;"><span class="status-indicator" id="tunnel-status"></span>Tunnel: <span id="tunnel-text" style="color: var(--text-light); font-weight: 600;">Stopped</span></div>
            <div><span class="status-indicator" id="internet-status"></span>Internet: <span id="internet-text" style="color: var(--text-light); font-weight: 600;">Checking...</span></div>
        </div>
    </div>
    

    <div class="panel">
        <h2><i class="fas fa-link"></i> Tunnel URL</h2>
        <input type="text" id="tunnel-url" value="Not available" readonly style="width: 100%; padding: 12px; border-radius: 8px; border: 2px solid var(--neon-cyan); background: rgba(0, 0, 0, 0.8); color: var(--neon-cyan); font-size: 1rem; text-shadow: 0 0 5px currentColor;">
        <button class="btn" onclick="copyUrl()" style="margin-top: 15px;"><i class="fas fa-copy"></i> Copy URL</button>
    </div>
</div>

<style>
/* Data Transfer Monitor Styles */
.data-transfer-monitor {
    background: rgba(0, 0, 0, 0.95);
    color: white;
    border: 2px solid var(--neon-green);
    box-shadow: 0 0 30px rgba(0, 255, 0, 0.5), inset 0 0 20px rgba(0, 255, 0, 0.1);
}

.data-transfer-monitor h2 {
    color: var(--neon-green) !important;
    border-bottom-color: var(--neon-green);
    text-shadow: 0 0 15px currentColor;
}

.transfer-display {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
    margin-bottom: 20px;
}

@media (max-width: 768px) {
    .transfer-display {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

.transfer-totals {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.transfer-total {
    display: flex;
    align-items: center;
    padding: 15px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid;
    box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.1);
}

.transfer-total.upload {
    border-color: var(--neon-cyan);
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(0, 255, 255, 0.1);
}

.transfer-total.download {
    border-color: var(--neon-pink);
    box-shadow: 0 0 15px rgba(255, 0, 128, 0.3), inset 0 0 15px rgba(255, 0, 128, 0.1);
}

.transfer-icon {
    font-size: 2rem;
    margin-right: 15px;
    padding: 10px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

.upload .transfer-icon {
    color: var(--neon-cyan);
    text-shadow: 0 0 10px currentColor;
}

.download .transfer-icon {
    color: var(--neon-pink);
    text-shadow: 0 0 10px currentColor;
}

.transfer-info {
    flex: 1;
}

.transfer-label {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.transfer-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: white;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.transfer-speeds {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.speed-display {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.speed-current {
    text-align: center;
    padding: 20px;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid;
    box-shadow: inset 0 0 15px rgba(255, 255, 255, 0.1);
}

.speed-current.upload {
    border-color: var(--neon-cyan);
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3), inset 0 0 15px rgba(0, 255, 255, 0.1);
}

.speed-current.download {
    border-color: var(--neon-pink);
    box-shadow: 0 0 15px rgba(255, 0, 128, 0.3), inset 0 0 15px rgba(255, 0, 128, 0.1);
}

.speed-label {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.upload .speed-label {
    color: var(--neon-cyan);
    text-shadow: 0 0 5px currentColor;
}

.download .speed-label {
    color: var(--neon-pink);
    text-shadow: 0 0 5px currentColor;
}

.speed-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
    transition: all 0.3s ease;
}

.speed-value.updating {
    animation: livePulse 0.6s ease-in-out;
}

.transfer-chart {
    background: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    padding: 15px;
    height: 140px;
    border: 1px solid var(--neon-green);
    box-shadow: inset 0 0 15px rgba(0, 255, 0, 0.2);
}

.transfer-chart canvas {
    width: 100% !important;
    height: 100% !important;
}

/* Live Ping Monitor Styles */
.live-ping-monitor {
    background: rgba(0, 0, 0, 0.95);
    color: white;
    border: 2px solid var(--neon-cyan);
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(0, 255, 255, 0.1);
}

.live-ping-monitor h2 {
    color: var(--neon-cyan) !important;
    border-bottom-color: var(--neon-cyan);
    text-shadow: 0 0 15px currentColor;
}

.live-ping-display {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 30px;
    margin-bottom: 20px;
}

@media (max-width: 768px) {
    .live-ping-display {
        grid-template-columns: 1fr;
        gap: 20px;
    }
}

.ping-current {
    text-align: center;
    padding: 20px;
    background: rgba(0, 255, 255, 0.1);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid var(--neon-cyan);
    box-shadow: inset 0 0 20px rgba(0, 255, 255, 0.2);
}

.ping-label {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.ping-value-large {
    font-size: 3rem;
    font-weight: bold;
    line-height: 1;
    margin-bottom: 10px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.ping-value-large.excellent { color: var(--neon-green); text-shadow: 0 0 15px currentColor; }
.ping-value-large.good { color: var(--neon-cyan); text-shadow: 0 0 15px currentColor; }
.ping-value-large.fair { color: var(--neon-yellow); text-shadow: 0 0 15px currentColor; }
.ping-value-large.poor { color: var(--neon-pink); text-shadow: 0 0 15px currentColor; }

.ping-status-text {
    font-size: 0.9rem;
    opacity: 0.9;
    font-weight: 500;
}

.ping-stats-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
}

@media (max-width: 480px) {
    .ping-stats-grid {
        grid-template-columns: 1fr;
    }
}

.ping-stat {
    background: rgba(0, 0, 0, 0.5);
    padding: 15px;
    border-radius: 8px;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}

.stat-label {
    font-size: 0.8rem;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 5px;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
}

.ping-chart-mini {
    background: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    padding: 15px;
    height: 120px;
    border: 1px solid var(--neon-cyan);
    box-shadow: inset 0 0 15px rgba(0, 255, 255, 0.2);
}

.ping-chart-mini canvas {
    width: 100% !important;
    height: 100% !important;
}

/* Enhanced Panel Styles */
.panel {
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.panel:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Enhanced Button Styles */
.btn {
    transition: all 0.3s ease;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn i {
    font-size: 0.9rem;
}

/* Pulse Animation for Live Updates */
@keyframes livePulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.ping-value-large.updating {
    animation: livePulse 0.6s ease-in-out;
}

/* Status Indicator Enhancements */
.status-indicator {
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 currentColor; }
    70% { box-shadow: 0 0 0 10px transparent; }
    100% { box-shadow: 0 0 0 0 transparent; }
}
</style>''').replace('{% block scripts %}{% endblock %}', 
'''// Live Ping Monitor JavaScript
let livePingChart = null;
let transferChart = null;
let pingDataBuffer = [];
const maxDataPoints = 30;

// Initialize Live Ping Chart
function initLivePingChart() {
    const ctx = document.getElementById('livePingChart').getContext('2d');
    livePingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Ping (ms)',
                data: [],
                borderColor: 'rgba(255, 255, 255, 0.8)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            scales: {
                x: { display: false },
                y: {
                    display: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: { size: 10 }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white'
                }
            }
        }
    });
}

// Initialize Transfer Chart
function initTransferChart() {
    const ctx = document.getElementById('transferChart').getContext('2d');
    transferChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Upload Speed',
                    data: [],
                    borderColor: '#00ffff',
                    backgroundColor: 'rgba(0, 255, 255, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                },
                {
                    label: 'Download Speed',
                    data: [],
                    borderColor: '#ff0080',
                    backgroundColor: 'rgba(255, 0, 128, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            scales: {
                x: { 
                    display: false
                },
                y: {
                    display: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { 
                        color: 'rgba(255, 255, 255, 0.7)',
                        font: { size: 10 },
                        callback: function(value) {
                            return formatBytesForChart(value) + '/s';
                        }
                    }
                }
            },
            plugins: {
                legend: { 
                    display: true,
                    labels: {
                        color: 'white',
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatBytesForChart(context.parsed.y) + '/s';
                        }
                    }
                }
            }
        }
    });
}

// Format bytes for chart display
function formatBytesForChart(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Update Data Transfer Monitor
function updateDataTransferMonitor(networkData) {
    // Update total transfer amounts
    const totalUpload = document.getElementById('total-upload');
    const totalDownload = document.getElementById('total-download');
    const currentUploadSpeed = document.getElementById('current-upload-speed');
    const currentDownloadSpeed = document.getElementById('current-download-speed');
    
    if (totalUpload && networkData.total_sent_formatted) {
        totalUpload.textContent = networkData.total_sent_formatted;
    }
    
    if (totalDownload && networkData.total_recv_formatted) {
        totalDownload.textContent = networkData.total_recv_formatted;
    }
    
    // Update current speeds with animation
    if (currentUploadSpeed && networkData.upload_speed_formatted) {
        currentUploadSpeed.textContent = networkData.upload_speed_formatted;
        currentUploadSpeed.classList.add('updating');
        setTimeout(() => currentUploadSpeed.classList.remove('updating'), 600);
    }
    
    if (currentDownloadSpeed && networkData.download_speed_formatted) {
        currentDownloadSpeed.textContent = networkData.download_speed_formatted;
        currentDownloadSpeed.classList.add('updating');
        setTimeout(() => currentDownloadSpeed.classList.remove('updating'), 600);
    }
    
    // Update transfer chart
    if (transferChart && networkData.transfer_history) {
        updateTransferChart(networkData.transfer_history);
    }
}

function updateTransferChart(transferHistory) {
    if (!transferChart || !transferHistory.length) return;
    
    // Keep only last 20 data points for the chart
    const recentData = transferHistory.slice(-20);
    
    transferChart.data.labels = recentData.map((_, index) => index);
    transferChart.data.datasets[0].data = recentData.map(entry => entry.upload_speed || 0);
    transferChart.data.datasets[1].data = recentData.map(entry => entry.download_speed || 0);
    transferChart.update('none');
}

// Update Live Ping Display
function updateLivePingMonitor(pingData) {
    const currentPing = pingData.last_ping_time;
    const stats = pingData.stats || {};
    
    // Update current ping with animation
    const currentElement = document.getElementById('live-ping-current');
    if (currentElement && currentPing !== null) {
        currentElement.textContent = currentPing.toFixed(1) + 'ms';
        currentElement.classList.add('updating');
        setTimeout(() => currentElement.classList.remove('updating'), 600);
        
        // Color coding based on ping quality
        currentElement.className = 'ping-value-large updating ' + getPingQuality(currentPing);
        
        // Update status text
        const statusElement = document.getElementById('live-ping-status');
        if (statusElement) {
            statusElement.textContent = getPingStatusText(currentPing);
        }
    }
    
    // Update statistics
    updatePingStat('live-ping-avg', stats.avg);
    updatePingStat('live-ping-min', stats.min);
    updatePingStat('live-ping-max', stats.max);
    updatePingStat('live-ping-count', stats.count);
    
    // Update mini chart
    if (livePingChart && pingData.ping_history) {
        updateLivePingChart(pingData.ping_history);
    }
}

function updatePingStat(elementId, value) {
    const element = document.getElementById(elementId);
    if (element && value !== undefined) {
        if (elementId === 'live-ping-count') {
            element.textContent = value;
        } else {
            element.textContent = value.toFixed(1) + 'ms';
        }
    }
}

function getPingQuality(ping) {
    if (ping < 30) return 'excellent';
    if (ping < 60) return 'good';
    if (ping < 120) return 'fair';
    return 'poor';
}

function getPingStatusText(ping) {
    if (ping < 30) return 'Excellent Connection';
    if (ping < 60) return 'Good Connection';
    if (ping < 120) return 'Fair Connection';
    return 'Poor Connection';
}

function updateLivePingChart(pingHistory) {
    if (!livePingChart || !pingHistory.length) return;
    
    // Keep only last 30 data points for the mini chart
    const recentData = pingHistory.slice(-maxDataPoints);
    
    livePingChart.data.labels = recentData.map((_, index) => index);
    livePingChart.data.datasets[0].data = recentData.map(entry => entry.ping_time || 0);
    livePingChart.update('none');
}

// Socket.IO event listeners for live updates
if (typeof io !== 'undefined') {
    const socket = io();
    
    socket.on('ping_data', (data) => {
        updateLivePingMonitor(data);
    });
    
    socket.on('network_data', (data) => {
        updateDataTransferMonitor(data);
    });
    
    socket.on('connect', () => {
        console.log('Connected to live monitoring');
        document.getElementById('live-ping-status').textContent = 'Connecting...';
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from live monitoring');
        document.getElementById('live-ping-status').textContent = 'Disconnected';
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    initLivePingChart();
    initTransferChart();
    
    // Fetch initial ping data
    fetch('/api/ping')
        .then(response => response.json())
        .then(data => {
            if (data.ping_history && data.ping_history.length > 0) {
                updateLivePingMonitor(data);
            }
        })
        .catch(error => console.error('Error fetching initial ping data:', error));
    
    // Fetch initial network data
    fetch('/api/network-data')
        .then(response => response.json())
        .then(data => {
            updateDataTransferMonitor(data);
        })
        .catch(error => console.error('Error fetching initial network data:', error));
});

// Existing tunnel control functions
async function startTunnel() {
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
    if (url !== 'Not available') {
        navigator.clipboard.writeText(url).then(() => {
            // Show success feedback
            const button = event.target;
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            button.style.backgroundColor = '#2ecc71';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.backgroundColor = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy URL:', err);
        });
    }
}



// Socket listeners for tunnel status
if (typeof io !== 'undefined') {
    const socket = io();
    socket.on('tunnel_url', (data) => {
        document.getElementById('tunnel-url').value = data.url;
    });
    
    socket.on('tunnel_status', (data) => {
        updateStatus(data.status === 'running' ? 'Running' : 'Stopped');
    });
    
    socket.on('internet_status', (data) => {
        const internetText = document.getElementById('internet-text');
        const internetIndicator = document.getElementById('internet-status');
        
        if (data.status) {
            internetText.textContent = 'Connected';
            internetIndicator.className = 'status-indicator running';
        } else {
            internetText.textContent = 'Disconnected';
            internetIndicator.className = 'status-indicator stopped';
        }
    });
}

''')

SETTINGS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', 
'''<!-- Live Log Monitor -->
<div class="panel">
    <h2 style="color: var(--neon-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;"><i class="fas fa-file-alt" style="color: var(--neon-yellow);"></i> Live Log Monitor</h2>
    <div class="log-controls" style="margin-bottom: 15px; display: flex; gap: 10px; flex-wrap: wrap;">
        <button class="btn" onclick="toggleLogMonitoring()" id="log-toggle-btn"><i class="fas fa-play"></i> Start Monitoring</button>
        <button class="btn secondary" onclick="clearLogDisplay()"><i class="fas fa-eraser"></i> Clear Display</button>
        <button class="btn warning" onclick="downloadLogs()"><i class="fas fa-download"></i> Download Logs</button>
        <select id="log-level-filter" style="padding: 8px; border-radius: 5px; background: rgba(0, 0, 0, 0.8); color: var(--neon-cyan); border: 2px solid var(--neon-cyan);">
            <option value="all">All Levels</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
            <option value="success">Success</option>
        </select>
    </div>
    <div class="log-display" id="log-display" style="background: rgba(0, 0, 0, 0.9); border-radius: 10px; padding: 15px; height: 400px; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 0.9rem; color: var(--neon-green); border: 2px solid var(--neon-cyan); box-shadow: inset 0 0 20px rgba(0, 255, 255, 0.1);">
        <div class="log-entry" style="opacity: 0.7;">Log monitoring stopped. Click 'Start Monitoring' to begin...</div>
    </div>
</div>

<!-- Tunnel Configuration -->
<div class="panel">
    <h2 style="color: var(--neon-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;"><i class="fas fa-cog" style="color: var(--neon-yellow);"></i> Tunnel Configuration</h2>
    <form onsubmit="saveSettings(event)">
        <div class="config-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; margin-bottom: 25px;">
            <div class="config-section" style="background: rgba(0, 255, 255, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-cyan);">
                <h3 style="color: var(--neon-cyan); margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-network-wired"></i> Network Settings</h3>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Tunnel URL:</label>
                    <input type="url" name="tunnel_url" value="{{ config.tunnel_url }}" placeholder="http://localhost:8080" style="width: 100%; padding: 12px; border: 2px solid var(--neon-cyan); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-cyan); font-size: 0.95rem;">
                </div>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Ping Test URL:</label>
                    <input type="text" name="ping_test_url" value="{{ config.ping_test_url }}" placeholder="1.1.1.1" style="width: 100%; padding: 12px; border: 2px solid var(--neon-cyan); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-cyan); font-size: 0.95rem;">
                </div>
            </div>
            <div class="config-section" style="background: rgba(0, 255, 0, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-green);">
                <h3 style="color: var(--neon-green); margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-clock"></i> Timing Settings</h3>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Check Interval (seconds):</label>
                    <input type="number" name="check_interval" value="{{ config.check_interval }}" min="1" max="3600" style="width: 100%; padding: 12px; border: 2px solid var(--neon-green); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-green); font-size: 0.95rem;">
                </div>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Retry Delay (seconds):</label>
                    <input type="number" name="retry_delay" value="{{ config.retry_delay }}" min="1" max="60" style="width: 100%; padding: 12px; border: 2px solid var(--neon-green); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-green); font-size: 0.95rem;">
                </div>
            </div>
            <div class="config-section" style="background: rgba(255, 0, 128, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-pink);">
                <h3 style="color: var(--neon-pink); margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-shield-alt"></i> Reliability Settings</h3>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Max Retries:</label>
                    <input type="number" name="max_retries" value="{{ config.max_retries }}" min="1" style="width: 100%; padding: 12px; border: 2px solid var(--neon-pink); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-pink); font-size: 0.95rem;">
                </div>
                <div class="input-group">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Debug Mode:</label>
                    <select name="debug_mode" style="width: 100%; padding: 12px; border: 2px solid var(--neon-pink); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-pink); font-size: 0.95rem;">
                        <option value="true" {{ 'selected' if config.debug_mode else '' }}>Enabled</option>
                        <option value="false" {{ 'selected' if not config.debug_mode else '' }}>Disabled</option>
                    </select>
                </div>
            </div>
            <div class="config-section" style="background: rgba(255, 255, 0, 0.05); padding: 20px; border-radius: 15px; border: 1px solid var(--neon-yellow);">
                <h3 style="color: var(--neon-yellow); margin-bottom: 15px; font-size: 1.1rem;"><i class="fas fa-save"></i> URL Storage Settings</h3>
                <div class="input-group" style="margin-bottom: 15px;">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Tunnel URLs Save Directory:</label>
                    <input type="text" name="tunnel_urls_save_directory" value="{{ config.tunnel_urls_save_directory }}" placeholder="d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)" style="width: 100%; padding: 12px; border: 2px solid var(--neon-yellow); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-yellow); font-size: 0.95rem;">
                    <small style="color: var(--text-light); opacity: 0.8; font-size: 0.85rem; margin-top: 5px; display: block;">Directory where tunnel URLs will be saved. Use full path (e.g., D:\\MyFolder\\Tunnels)</small>
                </div>
                <div class="input-group">
                    <label style="color: var(--text-light); display: block; margin-bottom: 5px; font-weight: 500;">Tunnel URLs Filename:</label>
                    <input type="text" name="tunnel_urls_filename" value="{{ config.tunnel_urls_filename }}" placeholder="tunnel_urls.txt" style="width: 100%; padding: 12px; border: 2px solid var(--neon-yellow); border-radius: 8px; background: rgba(0, 0, 0, 0.8); color: var(--neon-yellow); font-size: 0.95rem;">
                    <small style="color: var(--text-light); opacity: 0.8; font-size: 0.85rem; margin-top: 5px; display: block;">Filename for saving tunnel URLs. Format: Local URL - Date - Time - Generated URL</small>
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 30px;">
            <button type="submit" class="btn" style="margin-right: 15px; padding: 15px 30px; font-size: 1.1rem;"><i class="fas fa-save"></i> Save Configuration</button>
            <button type="button" class="btn secondary" onclick="resetSettings()" style="padding: 15px 30px; font-size: 1.1rem;"><i class="fas fa-undo"></i> Reset to Defaults</button>
        </div>
    </form>
</div>

<!-- System Information -->
<div class="panel">
    <h2 style="color: var(--neon-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;"><i class="fas fa-info-circle" style="color: var(--neon-yellow);"></i> System Information</h2>
    <div class="system-info-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px;">
        <div class="info-card" style="background: rgba(0, 255, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid var(--neon-cyan); box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);">
            <h4 style="color: var(--neon-cyan); margin-bottom: 10px; font-size: 1rem;">Application Version</h4>
            <p style="color: white; font-size: 1.2rem; font-weight: 600;">v3.0 Neon</p>
        </div>
        <div class="info-card" style="background: rgba(0, 255, 0, 0.1); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid var(--neon-green); box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);">
            <h4 style="color: var(--neon-green); margin-bottom: 10px; font-size: 1rem;">Python Version</h4>
            <p style="color: white; font-size: 1.2rem; font-weight: 600;" id="python-version">Loading...</p>
        </div>
        <div class="info-card" style="background: rgba(255, 0, 128, 0.1); padding: 20px; border-radius: 15px; text-align: center; border: 2px solid var(--neon-pink); box-shadow: 0 0 15px rgba(255, 0, 128, 0.3);">
            <h4 style="color: var(--neon-pink); margin-bottom: 10px; font-size: 1rem;">Server Status</h4>
            <p style="color: var(--neon-green); font-size: 1.2rem; font-weight: 600; text-shadow: 0 0 10px currentColor;">Running</p>
        </div>
    </div>
</div>

<!-- Advanced Options -->
<div class="panel">
    <h2 style="color: var(--neon-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;"><i class="fas fa-tools" style="color: var(--neon-yellow);"></i> Advanced Options</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
        <button class="btn warning" onclick="downloadConfig()"><i class="fas fa-download"></i> Download Config</button>
        <button class="btn danger" onclick="clearLogs()"><i class="fas fa-trash"></i> Clear All Logs</button>
        <button class="btn secondary" onclick="exportSettings()"><i class="fas fa-file-export"></i> Export Settings</button>
        <button class="btn" onclick="restartApplication()"><i class="fas fa-redo"></i> Restart App</button>
        <button class="btn secondary" onclick="viewTunnelUrls()"><i class="fas fa-list"></i> View Saved URLs</button>
        <button class="btn warning" onclick="downloadTunnelUrls()"><i class="fas fa-download"></i> Download URLs</button>
        <button class="btn" onclick="openSaveDirectory()"><i class="fas fa-folder-open"></i> Open Directory</button>
    </div>
</div>

<!-- Saved Tunnel URLs -->
<div class="panel" id="tunnel-urls-panel" style="display: none;">
    <h2 style="color: var(--neon-cyan); margin-bottom: 20px; display: flex; align-items: center; gap: 10px;"><i class="fas fa-link" style="color: var(--neon-green);"></i> Saved Tunnel URLs</h2>
    <div id="tunnel-urls-content">
        <p style="color: var(--text-light); text-align: center; padding: 20px;">Loading...</p>
    </div>
    <div style="text-align: center; margin-top: 15px;">
        <button class="btn secondary" onclick="hideTunnelUrls()"><i class="fas fa-times"></i> Close</button>
        <button class="btn warning" onclick="refreshTunnelUrls()"><i class="fas fa-refresh"></i> Refresh</button>
    </div>
</div>''').replace('{% block scripts %}{% endblock %}', 
'''// Live Log Monitoring
let logMonitoringActive = false;
let logSocket;
let logUpdateInterval;

function toggleLogMonitoring() {
    const btn = document.getElementById('log-toggle-btn');
    const display = document.getElementById('log-display');
    
    if (!logMonitoringActive) {
        // Start monitoring
        logMonitoringActive = true;
        btn.innerHTML = '<i class="fas fa-stop"></i> Stop Monitoring';
        btn.className = 'btn danger';
        
        display.innerHTML = '<div class="log-entry" style="color: var(--neon-green);">📡 Log monitoring started...</div>';
        
        // Start fetching logs
        startLogFetching();
        showNotification('Live log monitoring started', 'success');
    } else {
        // Stop monitoring
        logMonitoringActive = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Start Monitoring';
        btn.className = 'btn';
        
        if (logUpdateInterval) {
            clearInterval(logUpdateInterval);
        }
        
        display.innerHTML += '<div class="log-entry" style="color: var(--neon-pink);">📡 Log monitoring stopped.</div>';
        showNotification('Live log monitoring stopped', 'warning');
    }
}

function startLogFetching() {
    // Fetch logs every 2 seconds
    logUpdateInterval = setInterval(function() {
        if (logMonitoringActive) {
            fetch('/api/logs')
                .then(response => response.json())
                .then(logs => {
                    updateLogDisplay(logs);
                })
                .catch(error => {
                    console.error('Error fetching logs:', error);
                });
        }
    }, 2000);
}

function updateLogDisplay(logs) {
    const display = document.getElementById('log-display');
    const filter = document.getElementById('log-level-filter').value;
    
    logs.forEach(log => {
        if (filter === 'all' || log.level === filter) {
            const logEntry = document.createElement('div');
            logEntry.className = 'log-entry';
            
            const levelColor = {
                'info': 'var(--neon-cyan)',
                'success': 'var(--neon-green)',
                'warning': 'var(--neon-yellow)',
                'error': 'var(--neon-pink)',
                'debug': '#888888'
            }[log.level] || '#ffffff';
            
            const levelIcon = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'debug': '🐛'
            }[log.level] || '📝';
            
            logEntry.style.cssText = `
                color: ${levelColor};
                margin-bottom: 5px;
                padding: 8px;
                border-left: 3px solid ${levelColor};
                background: rgba(0, 0, 0, 0.3);
                border-radius: 5px;
                font-size: 0.85rem;
                line-height: 1.4;
                text-shadow: 0 0 5px currentColor;
            `;
            
            logEntry.innerHTML = `${levelIcon} [${log.timestamp}] ${log.message}`;
            display.appendChild(logEntry);
        }
    });
    
    // Auto-scroll to bottom
    display.scrollTop = display.scrollHeight;
    
    // Limit log entries to prevent memory issues
    const entries = display.querySelectorAll('.log-entry');
    if (entries.length > 500) {
        for (let i = 0; i < 100; i++) {
            if (entries[i] && entries[i].parentNode) {
                entries[i].parentNode.removeChild(entries[i]);
            }
        }
    }
}

function clearLogDisplay() {
    document.getElementById('log-display').innerHTML = '<div class="log-entry" style="opacity: 0.7;">Log display cleared.</div>';
    showNotification('Log display cleared', 'success');
}

function downloadLogs() {
    fetch('/api/download-logs')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tunnel_monitor_logs_' + new Date().toISOString().split('T')[0] + '.txt';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Logs downloaded successfully', 'success');
        })
        .catch(error => {
            console.error('Error downloading logs:', error);
            showNotification('Failed to download logs', 'error');
        });
}

// Settings management
async function saveSettings(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const settings = Object.fromEntries(formData);
    
    // Convert boolean strings to actual booleans
    if (settings.debug_mode) {
        settings.debug_mode = settings.debug_mode === 'true';
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(settings)
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification('Settings saved successfully!', 'success');
        } else {
            showNotification('Error: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Failed to save settings', 'error');
    }
}

async function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
        try {
            const response = await fetch('/api/settings/reset', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                showNotification('Settings reset to defaults', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('Error: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error resetting settings:', error);
            showNotification('Failed to reset settings', 'error');
        }
    }
}

async function downloadConfig() {
    try {
        const response = await fetch('/api/download-config');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tunnel_monitor_config.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Configuration downloaded', 'success');
        } else {
            showNotification('Failed to download configuration', 'error');
        }
    } catch (error) {
        console.error('Error downloading config:', error);
        showNotification('Failed to download configuration', 'error');
    }
}

async function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        try {
            const response = await fetch('/api/clear-logs', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                showNotification('Logs cleared successfully', 'success');
                clearLogDisplay();
            } else {
                showNotification('Error: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
            showNotification('Failed to clear logs', 'error');
        }
    }
}

function exportSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            const dataStr = JSON.stringify(data, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'settings_export_' + new Date().toISOString().split('T')[0] + '.json';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            showNotification('Settings exported successfully', 'success');
        })
        .catch(error => {
            console.error('Error exporting settings:', error);
            showNotification('Failed to export settings', 'error');
        });
}

async function restartApplication() {
    if (confirm('Are you sure you want to restart the application? This will briefly interrupt service.')) {
        try {
            const response = await fetch('/api/restart', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'success') {
                showNotification('Application restart initiated...', 'warning');
                setTimeout(() => {
                    window.location.reload();
                }, 3000);
            } else {
                showNotification('Error: ' + result.message, 'error');
            }
        } catch (error) {
            console.error('Error restarting application:', error);
            showNotification('Failed to restart application', 'error');
        }
    }
}

// Tunnel URLs management functions
async function viewTunnelUrls() {
    try {
        const response = await fetch('/api/tunnel-urls');
        const result = await response.json();
        
        if (result.status === 'success') {
            const panel = document.getElementById('tunnel-urls-panel');
            const content = document.getElementById('tunnel-urls-content');
            
            if (result.tunnel_urls.length === 0) {
                content.innerHTML = `
                    <div style="text-align: center; padding: 30px; color: var(--text-light); opacity: 0.8;">
                        <i class="fas fa-link" style="font-size: 3rem; margin-bottom: 15px; color: var(--neon-cyan);"></i>
                        <h3>No Tunnel URLs Saved Yet</h3>
                        <p>Start a tunnel to automatically save URLs with timestamps.</p>
                        <small>Directory: ${result.save_directory}</small><br>
                        <small>Filename: ${result.filename}</small>
                    </div>
                `;
            } else {
                let urlsHtml = `
                    <div style="margin-bottom: 15px; display: flex; justify-content: between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div style="color: var(--neon-green); font-weight: 600;">
                            <i class="fas fa-database"></i> Total URLs: ${result.total_count}
                        </div>
                        <div style="color: var(--text-light); font-size: 0.9rem; opacity: 0.8;">
                            Directory: ${result.save_directory}<br>
                            File: ${result.filename}
                        </div>
                    </div>
                    <div style="max-height: 400px; overflow-y: auto; background: rgba(0, 0, 0, 0.5); border-radius: 10px; padding: 15px;">
                `;
                
                result.tunnel_urls.reverse().forEach((entry, index) => {
                    urlsHtml += `
                        <div style="
                            margin-bottom: 15px; 
                            padding: 15px; 
                            background: rgba(0, 255, 255, 0.1); 
                            border-radius: 10px; 
                            border-left: 4px solid var(--neon-cyan);
                            border: 1px solid rgba(0, 255, 255, 0.3);
                        ">
                            <div style="display: grid; grid-template-columns: auto 1fr auto; gap: 15px; align-items: center;">
                                <div style="color: var(--neon-yellow); font-weight: 600;">
                                    <i class="fas fa-calendar"></i> ${entry.date}
                                </div>
                                <div style="color: var(--neon-cyan); font-weight: 600;">
                                    <i class="fas fa-clock"></i> ${entry.time}
                                </div>
                                <div style="display: flex; gap: 10px;">
                                    <button class="btn secondary" onclick="copyToClipboard('${entry.generated_url}')" style="padding: 6px 10px; font-size: 0.8rem;">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>
                            </div>
                            <div style="margin-top: 10px;">
                                <div style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 5px; opacity: 0.8;">
                                    <i class="fas fa-home"></i> Local URL:
                                </div>
                                <div style="color: var(--neon-green); font-family: monospace; margin-bottom: 10px; padding: 8px; background: rgba(0, 255, 0, 0.1); border-radius: 5px;">
                                    ${entry.local_url}
                                </div>
                                <div style="color: var(--text-light); font-size: 0.9rem; margin-bottom: 5px; opacity: 0.8;">
                                    <i class="fas fa-external-link-alt"></i> Generated Tunnel URL:
                                </div>
                                <div style="color: var(--neon-pink); font-family: monospace; padding: 8px; background: rgba(255, 0, 128, 0.1); border-radius: 5px;">
                                    <a href="${entry.generated_url}" target="_blank" style="color: var(--neon-pink); text-decoration: none; word-break: break-all;">
                                        ${entry.generated_url}
                                    </a>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                urlsHtml += '</div>';
                content.innerHTML = urlsHtml;
            }
            
            panel.style.display = 'block';
            panel.scrollIntoView({ behavior: 'smooth' });
            showNotification('Tunnel URLs loaded successfully', 'success');
        } else {
            showNotification('Error: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error loading tunnel URLs:', error);
        showNotification('Failed to load tunnel URLs', 'error');
    }
}

function hideTunnelUrls() {
    document.getElementById('tunnel-urls-panel').style.display = 'none';
}

function refreshTunnelUrls() {
    viewTunnelUrls();
}

async function downloadTunnelUrls() {
    try {
        const response = await fetch('/api/download-tunnel-urls');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tunnel_urls_${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showNotification('Tunnel URLs downloaded successfully', 'success');
        } else {
            const result = await response.json();
            showNotification('Error: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error downloading tunnel URLs:', error);
        showNotification('Failed to download tunnel URLs', 'error');
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('URL copied to clipboard', 'success');
    }).catch(err => {
        console.error('Failed to copy URL:', err);
        showNotification('Failed to copy URL', 'error');
    });
}

async function openSaveDirectory() {
    try {
        const response = await fetch('/api/open-save-directory', { method: 'POST' });
        const result = await response.json();
        
        if (result.status === 'success') {
            showNotification('Directory opened successfully', 'success');
        } else {
            showNotification('Error: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error opening directory:', error);
        showNotification('Failed to open directory', 'error');
    }
}

// Notification system with neon styling
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const colors = {
        'success': 'var(--neon-green)',
        'error': 'var(--neon-pink)',
        'warning': 'var(--neon-yellow)',
        'info': 'var(--neon-cyan)'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        color: ${colors[type] || colors.success};
        padding: 15px 20px;
        border-radius: 10px;
        border: 2px solid ${colors[type] || colors.success};
        box-shadow: 0 0 20px ${colors[type] || colors.success};
        z-index: 1500;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        font-weight: 500;
        backdrop-filter: blur(10px);
        text-shadow: 0 0 10px currentColor;
    `;
    notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : type === 'warning' ? 'exclamation' : 'info'}"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => notification.style.transform = 'translateX(0)', 100);
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Load system information
    fetch('/api/system-info')
        .then(response => response.json())
        .then(data => {
            if (data.python_version) {
                document.getElementById('python-version').textContent = data.python_version;
            }
        })
        .catch(error => console.error('Error loading system info:', error));
        
    // Set up log level filter change handler
    document.getElementById('log-level-filter').addEventListener('change', function() {
        if (logMonitoringActive) {
            clearLogDisplay();
            showNotification('Log filter updated', 'info');
        }
    });
});''')

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
    "ping_test_url": "1.1.1.1",  # URL to ping for connectivity test
    "tunnel_urls_save_directory": "d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)",  # Directory to save tunnel URLs
    "tunnel_urls_filename": "tunnel_urls.txt"  # Filename for saving tunnel URLs
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

# Network data transfer monitoring
network_data = {
    "total_bytes_sent": 0,
    "total_bytes_recv": 0,
    "current_upload_speed": 0,
    "current_download_speed": 0,
    "transfer_history": [],
    "max_history_points": 60,  # Store 1 minute of data
    "last_measurement": None
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
    # Windows ping command parameters
    param = "-n"
    timeout_param = "-w"
    timeout_value = str(timeout)
    
    try:
        # Hide the console output
        with open(os.devnull, 'w') as DEVNULL:
            # Run the ping command and capture output
            output = subprocess.check_output(
                ["ping", param, "1", timeout_param, timeout_value, host],
                stderr=DEVNULL,
                universal_newlines=True
            )
            
            # Parse the output to extract the time (Windows format)
            # Windows format: "Reply from 1.1.1.1: bytes=32 time=15ms TTL=57"
            match = re.search(r"time=([0-9]+)ms", output)
                
            if match:
                return float(match.group(1))
            return 0.0  # Successful ping but couldn't parse time
    except subprocess.CalledProcessError:
        # Ping failed
        return None
    except Exception as e:
        logger.error(f"Error pinging {host}: {e}")
        return None

def get_network_io_stats():
    """Get current network I/O statistics"""
    try:
        stats = psutil.net_io_counters()
        return {
            "bytes_sent": stats.bytes_sent,
            "bytes_recv": stats.bytes_recv,
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv
        }
    except Exception as e:
        logger.error(f"Error getting network stats: {e}")
        return None

def format_bytes(bytes_value):
    """Format bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"

def calculate_transfer_speed(current_stats, previous_stats, time_diff):
    """Calculate transfer speeds in bytes per second"""
    if not current_stats or not previous_stats or time_diff <= 0:
        return 0, 0
    
    upload_speed = (current_stats["bytes_sent"] - previous_stats["bytes_sent"]) / time_diff
    download_speed = (current_stats["bytes_recv"] - previous_stats["bytes_recv"]) / time_diff
    
    return max(0, upload_speed), max(0, download_speed)

def save_tunnel_url(tunnel_url, config):
    """Save tunnel URL to file with enhanced format: Local link - Date - Time - Generated link"""
    try:
        save_directory = config.get("tunnel_urls_save_directory", "d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)")
        filename = config.get("tunnel_urls_filename", "tunnel_urls.txt")
        
        # Create the full save path
        save_path = os.path.join(save_directory, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        
        # Get the local URL from config
        local_url = config.get("tunnel_url", "http://localhost:8080")
        
        # Format the entry with enhanced format: Local link - Date - Time - Generated link
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        entry = f"{local_url} - {date_str} - {time_str} - {tunnel_url}\n"
        
        # Append to file
        with open(save_path, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        log(f"Tunnel URL saved to {save_path} with format: Local - Date - Time - Generated", level="info")
        return True
        
    except Exception as e:
        log(f"Error saving tunnel URL: {e}", level="error")
        return False

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
    
    # Determine the cloudflared executable (Windows)
    cloudflared_cmd = config["cloudflared_path"]
    if not cloudflared_cmd or not os.path.exists(cloudflared_cmd):
        # Try using the system-installed cloudflared
        cloudflared_cmd = "cloudflared.exe"
    
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
                        
                        # Save tunnel URL to file
                        save_tunnel_url(tunnel_url, config)
                        
                        # Emit the tunnel URL to connected clients
                        socketio.emit('tunnel_url', {'url': tunnel_url})
                        
                        log(f"Tunnel URL detected and saved: {tunnel_url}", level="success")
        
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
            # Windows process termination
            tunnel_process.terminate()
            tunnel_process.wait(timeout=5)
            log("Cloudflared tunnel stopped", level="success")
        except Exception as e:
            log(f"Error stopping cloudflared: {e}", level="error")
            # Force kill if normal termination fails
            try:
                os.system(f"taskkill /F /PID {tunnel_process.pid}")
                log("Cloudflared tunnel force-stopped", level="warning")
            except:
                pass
        tunnel_process = None
        
    # Always update status and emit to clients
    STATS["current_status"] = "Stopped"
    socketio.emit('tunnel_status', {'status': 'stopped'})
    log("Tunnel status updated to Stopped", level="info")

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
                
                # Update tunnel status and emit to clients
                if tunnel_process:
                    STATS["current_status"] = "Running"
                    socketio.emit('tunnel_status', {'status': 'running'})
                    log("Tunnel started and status updated", level="success")
            else:
                # Tunnel is running, ensure status is correct
                if STATS["current_status"] != "Running":
                    STATS["current_status"] = "Running"
                    socketio.emit('tunnel_status', {'status': 'running'})
                    log("Tunnel status corrected to Running", level="info")
        else:
            # Internet is down
            log("Internet connection lost", level="warning")
            STATS["internet_disconnects"] += 1
            
            # Stop the tunnel if it's running and update status
            if tunnel_process and tunnel_process.poll() is None:
                stop_tunnel()
            
            # Ensure status is updated to stopped
            if STATS["current_status"] != "Stopped":
                STATS["current_status"] = "Stopped"
                socketio.emit('tunnel_status', {'status': 'stopped'})
                log("Tunnel status updated to Stopped", level="warning")
            
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
    
    # Update status immediately and emit to clients
    STATS["current_status"] = "Starting"
    socketio.emit('tunnel_status', {'status': 'starting'})
    
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
    
    # Update status and emit to clients
    STATS["current_status"] = "Stopped"
    socketio.emit('tunnel_status', {'status': 'stopped'})
    
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
            config["tunnel_urls_save_directory"] = data.get("tunnel_urls_save_directory", config["tunnel_urls_save_directory"])
            config["tunnel_urls_filename"] = data.get("tunnel_urls_filename", config["tunnel_urls_filename"])
            
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

@app.route('/api/tunnel-urls')
def api_tunnel_urls():
    """Get saved tunnel URLs"""
    try:
        config = load_config()
        save_directory = config.get("tunnel_urls_save_directory", "d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)")
        filename = config.get("tunnel_urls_filename", "tunnel_urls.txt")
        save_path = os.path.join(save_directory, filename)
        
        tunnel_urls = []
        if os.path.exists(save_path):
            with open(save_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and ' - ' in line:
                        # Parse the enhanced format: Local URL - Date - Time - Generated URL
                        try:
                            parts = line.split(' - ')
                            if len(parts) >= 4:
                                local_url = parts[0].strip()
                                date = parts[1].strip()
                                time = parts[2].strip()
                                generated_url = ' - '.join(parts[3:]).strip()  # Handle URLs with dashes
                                
                                tunnel_urls.append({
                                    'local_url': local_url,
                                    'date': date,
                                    'time': time,
                                    'generated_url': generated_url,
                                    'full_entry': line
                                })
                        except Exception as parse_error:
                            logger.warning(f"Error parsing tunnel URL line: {line} - {parse_error}")
        
        return jsonify({
            'status': 'success',
            'tunnel_urls': tunnel_urls,
            'save_path': save_path,
            'save_directory': save_directory,
            'filename': filename,
            'total_count': len(tunnel_urls)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/download-tunnel-urls')
def api_download_tunnel_urls():
    """Download saved tunnel URLs file"""
    try:
        config = load_config()
        save_directory = config.get("tunnel_urls_save_directory", "d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)")
        filename = config.get("tunnel_urls_filename", "tunnel_urls.txt")
        save_path = os.path.join(save_directory, filename)
        
        if not os.path.exists(save_path):
            return jsonify({'status': 'error', 'message': 'Tunnel URLs file not found'}), 404
        
        from flask import send_file
        return send_file(
            save_path,
            as_attachment=True,
            download_name=f'tunnel_urls_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/open-save-directory', methods=['POST'])
def api_open_save_directory():
    """Open the tunnel URLs save directory in file explorer"""
    try:
        config = load_config()
        save_directory = config.get("tunnel_urls_save_directory", "d:\\Project\\Git Hub\\cloudflare_tunnel_monitor(Windows)")
        
        # Check if directory exists, create if not
        if not os.path.exists(save_directory):
            os.makedirs(save_directory, exist_ok=True)
            log(f"Created directory: {save_directory}", level="info")
        
        # Open directory in file explorer (Windows only)
        os.startfile(save_directory)
        
        log(f"Opened directory: {save_directory}", level="info")
        return jsonify({
            'status': 'success',
            'message': f'Directory opened: {save_directory}',
            'directory': save_directory
        })
        
    except Exception as e:
        log(f"Error opening directory: {e}", level="error")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system-stats')
def get_system_stats():
    """Get current system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        uptime = time.time() - psutil.boot_time()
        
        return jsonify({
            'status': 'success',
            'cpu': cpu_percent,
            'memory': memory.percent,
            'uptime': uptime
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/network-diagnostics', methods=['POST'])
def network_diagnostics():
    """Run network diagnostics"""
    try:
        config = load_config()
        # Basic network checks
        results = {
            'ping_test': ping_host(config.get('ping_test_url', '1.1.1.1')),
            'dns_test': ping_host('8.8.8.8'),
            'tunnel_status': 'running' if tunnel_process and tunnel_process.poll() is None else 'stopped'
        }
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/download-config')
def api_download_config():
    """Download current configuration file"""
    try:
        config = load_config()
        response = jsonify(config)
        response.headers['Content-Disposition'] = 'attachment; filename=tunnel_monitor_config.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clear-logs', methods=['POST'])
def api_clear_logs():
    """Clear application logs"""
    try:
        # Clear the log queue
        while not log_queue.empty():
            try:
                log_queue.get_nowait()
            except queue.Empty:
                break
        
        # Also clear log files if they exist
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if os.path.exists(logs_dir):
            for filename in os.listdir(logs_dir):
                if filename.endswith('.log'):
                    log_file_path = os.path.join(logs_dir, filename)
                    try:
                        with open(log_file_path, 'w') as f:
                            f.write('')  # Clear the file content
                    except Exception as e:
                        logger.warning(f"Could not clear log file {filename}: {e}")
        
        log("Application logs cleared", level="info")
        return jsonify({'status': 'success', 'message': 'Logs cleared successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/download-logs')
def api_download_logs():
    """Download log files as a text file"""
    try:
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        log_content = []
        
        # Read current log files
        if os.path.exists(logs_dir):
            for filename in sorted(os.listdir(logs_dir)):
                if filename.endswith('.log'):
                    log_file_path = os.path.join(logs_dir, filename)
                    try:
                        with open(log_file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            if content:
                                log_content.append(f"=== {filename} ===")
                                log_content.append(content)
                                log_content.append("")
                    except Exception as e:
                        log_content.append(f"Error reading {filename}: {str(e)}")
        
        # Add current session logs from queue
        session_logs = []
        temp_queue = queue.Queue()
        while not log_queue.empty():
            try:
                log_entry = log_queue.get_nowait()
                session_logs.append(f"[{log_entry['timestamp']}] {log_entry['level'].upper()}: {log_entry['message']}")
                temp_queue.put(log_entry)  # Keep for the original queue
            except queue.Empty:
                break
        
        # Restore the queue
        while not temp_queue.empty():
            log_queue.put(temp_queue.get_nowait())
        
        if session_logs:
            log_content.append("=== Current Session Logs ===")
            log_content.extend(session_logs)
        
        if not log_content:
            log_content = ["No logs available"]
        
        log_text = "\n".join(log_content)
        
        from flask import Response
        return Response(
            log_text,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename=tunnel_monitor_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'}
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system-info')
def api_system_info():
    """Get system information"""
    try:
        import sys
        import platform
        
        return jsonify({
            'status': 'success',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': platform.system(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
            'app_version': '3.0 Enhanced'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def api_restart():
    """Restart the application"""
    try:
        import threading
        import sys
        import os
        
        def restart_app():
            # Give time for response to be sent
            time.sleep(2)
            try:
                # Windows application restart
                os.system('taskkill /F /IM python.exe')
                time.sleep(1)
                os.system(f'start cmd /c "cd /d {os.getcwd()} && python app.py"')
            except Exception as e:
                logger.error(f"Restart failed: {e}")
        
        # Start restart in background thread
        restart_thread = threading.Thread(target=restart_app)
        restart_thread.daemon = True
        restart_thread.start()
        
        log("Application restart initiated", level="info")
        return jsonify({'status': 'success', 'message': 'Application restart initiated'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

@app.route('/api/network-data')
def api_network_data():
    """Get current network transfer data with statistics"""
    global network_data
    
    # Get current network stats
    current_stats = get_network_io_stats()
    current_time = time.time()
    
    if current_stats and network_data["last_measurement"]:
        # Calculate speeds
        time_diff = current_time - network_data["last_measurement"]["timestamp"]
        if time_diff > 0:
            upload_speed, download_speed = calculate_transfer_speed(
                current_stats, 
                network_data["last_measurement"]["stats"], 
                time_diff
            )
            
            # Update current speeds
            network_data["current_upload_speed"] = upload_speed
            network_data["current_download_speed"] = download_speed
            
            # Add to history
            network_data["transfer_history"].append({
                "timestamp": current_time,
                "upload_speed": upload_speed,
                "download_speed": download_speed,
                "total_sent": current_stats["bytes_sent"],
                "total_recv": current_stats["bytes_recv"]
            })
            
            # Maintain history size
            if len(network_data["transfer_history"]) > network_data["max_history_points"]:
                network_data["transfer_history"].pop(0)
    
    # Update total bytes and last measurement
    if current_stats:
        network_data["total_bytes_sent"] = current_stats["bytes_sent"]
        network_data["total_bytes_recv"] = current_stats["bytes_recv"]
        network_data["last_measurement"] = {
            "timestamp": current_time,
            "stats": current_stats
        }
    
    return jsonify({
        "total_sent": network_data["total_bytes_sent"],
        "total_recv": network_data["total_bytes_recv"],
        "total_sent_formatted": format_bytes(network_data["total_bytes_sent"]),
        "total_recv_formatted": format_bytes(network_data["total_bytes_recv"]),
        "current_upload_speed": network_data["current_upload_speed"],
        "current_download_speed": network_data["current_download_speed"],
        "upload_speed_formatted": format_bytes(network_data["current_upload_speed"]) + "/s",
        "download_speed_formatted": format_bytes(network_data["current_download_speed"]) + "/s",
        "transfer_history": network_data["transfer_history"][-20:] if network_data["transfer_history"] else []  # Last 20 points for chart
    })

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

# Global monitoring threads
ping_monitor_running = False
ping_monitor_thread_instance = None
internet_monitor_running = False
internet_monitor_thread_instance = None
network_monitor_running = False
network_monitor_thread_instance = None
status_monitor_running = False
status_monitor_thread_instance = None

def start_independent_ping_monitor():
    """Start ping monitoring independent of tunnel status"""
    global ping_monitor_running, ping_monitor_thread_instance
    
    if not ping_monitor_running:
        ping_monitor_running = True
        ping_monitor_thread_instance = threading.Thread(target=independent_ping_monitor_thread)
        ping_monitor_thread_instance.daemon = True
        ping_monitor_thread_instance.start()
        log("Independent ping monitor started", level="info")
        
        # Start a watchdog thread to monitor the ping monitor
        watchdog_thread = threading.Thread(target=ping_monitor_watchdog)
        watchdog_thread.daemon = True
        watchdog_thread.start()
        log("Ping monitor watchdog started", level="info")

def ping_monitor_watchdog():
    """Watchdog thread to ensure ping monitor never stops"""
    global ping_monitor_running, ping_monitor_thread_instance
    
    while ping_monitor_running:
        try:
            # Check if ping monitor thread is still alive
            if ping_monitor_thread_instance and not ping_monitor_thread_instance.is_alive():
                log("Ping monitor thread died, restarting...", level="warning")
                
                # Restart the ping monitor thread
                ping_monitor_thread_instance = threading.Thread(target=independent_ping_monitor_thread)
                ping_monitor_thread_instance.daemon = True
                ping_monitor_thread_instance.start()
                log("Ping monitor thread restarted", level="success")
            
            # Check every 10 seconds
            for i in range(100):  # 10 seconds with monitoring check
                if not ping_monitor_running:
                    break
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in ping monitor watchdog: {e}")
            time.sleep(5)
    
    log("Ping monitor watchdog stopped", level="info")

def start_independent_status_monitor():
    """Start status monitoring independent of other monitoring"""
    global status_monitor_running, status_monitor_thread_instance
    
    if not status_monitor_running:
        status_monitor_running = True
        status_monitor_thread_instance = threading.Thread(target=independent_status_monitor_thread)
        status_monitor_thread_instance.daemon = True
        status_monitor_thread_instance.start()
        log("Independent status monitor started", level="info")

def independent_status_monitor_thread():
    """Independent status monitoring thread that ensures UI sync"""
    global status_monitor_running, tunnel_process
    
    while status_monitor_running:
        try:
            # Check actual tunnel process status
            actual_status = "Stopped"
            if tunnel_process and tunnel_process.poll() is None:
                actual_status = "Running"
            
            # Update STATS if there's a mismatch
            if STATS["current_status"] != actual_status:
                STATS["current_status"] = actual_status
                status_value = 'running' if actual_status == "Running" else 'stopped'
                
                # Emit status update to all connected clients
                socketio.emit('tunnel_status', {'status': status_value})
                log(f"Status synchronized: {actual_status}", level="info")
            
            # Check every 5 seconds
            for i in range(50):  # 5 seconds with monitoring check
                if not status_monitor_running:
                    break
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error in status monitor thread: {e}")
            time.sleep(5)
    
    log("Status monitor thread stopped", level="info")

def start_independent_network_monitor():
    """Start network monitoring independent of tunnel status"""
    global network_monitor_running, network_monitor_thread_instance
    
    if not network_monitor_running:
        network_monitor_running = True
        network_monitor_thread_instance = threading.Thread(target=independent_network_monitor_thread)
        network_monitor_thread_instance.daemon = True
        network_monitor_thread_instance.start()
        log("Independent network monitor started", level="info")

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
    consecutive_failures = 0
    max_consecutive_failures = 5
    
    while ping_monitor_running:
        try:
            # Get the current ping time using the configured ping_test_url
            config = load_config()
            ping_url = config.get("ping_test_url", "1.1.1.1")
            ping_time = ping_host(ping_url, timeout=3000)  # 3 second timeout
            
            if ping_time is not None:
                # Successful ping - reset failure counter
                consecutive_failures = 0
                
                # Update ping data
                ping_data["last_ping_time"] = ping_time
                
                # Add to history and maintain max size
                current_time = time.time()  # Timestamp
                ping_data["ping_history"].append({"timestamp": current_time, "ping_time": ping_time})
                if len(ping_data["ping_history"]) > max_history_size:
                    ping_data["ping_history"].pop(0)
                
                # Calculate statistics
                stats = calculate_ping_stats(ping_data["ping_history"])
                
                # Emit the ping data to all connected clients
                try:
                    socketio.emit('ping_data', {
                        'last_ping_time': ping_time,
                        'ping_history': ping_data["ping_history"],
                        'stats': stats
                    })
                except Exception as emit_error:
                    logger.warning(f"Error emitting ping data: {emit_error}")
            else:
                # Failed ping - increment failure counter
                consecutive_failures += 1
                logger.warning(f"Ping failed to {ping_url} (failure {consecutive_failures}/{max_consecutive_failures})")
                
                # If too many consecutive failures, try alternative hosts
                if consecutive_failures >= max_consecutive_failures:
                    alternative_hosts = ["8.8.8.8", "1.1.1.1", "8.8.4.4", "1.0.0.1"]
                    for alt_host in alternative_hosts:
                        if alt_host != ping_url:
                            alt_ping = ping_host(alt_host, timeout=3000)
                            if alt_ping is not None:
                                logger.info(f"Switched to alternative ping host: {alt_host}")
                                ping_time = alt_ping
                                ping_data["last_ping_time"] = ping_time
                                
                                # Add to history
                                current_time = time.time()
                                ping_data["ping_history"].append({"timestamp": current_time, "ping_time": ping_time})
                                if len(ping_data["ping_history"]) > max_history_size:
                                    ping_data["ping_history"].pop(0)
                                
                                # Calculate statistics and emit
                                stats = calculate_ping_stats(ping_data["ping_history"])
                                try:
                                    socketio.emit('ping_data', {
                                        'last_ping_time': ping_time,
                                        'ping_history': ping_data["ping_history"],
                                        'stats': stats
                                    })
                                except Exception as emit_error:
                                    logger.warning(f"Error emitting ping data: {emit_error}")
                                
                                consecutive_failures = 0  # Reset failure counter
                                break
            
            # Wait for 1 second before the next ping, but check running status frequently
            for i in range(10):  # Check ping_monitor_running every 0.1 seconds
                if not ping_monitor_running:
                    break
                time.sleep(0.1)
                
        except Exception as e:
            consecutive_failures += 1
            logger.error(f"Error in ping monitor thread: {e}")
            
            # If we have too many errors, wait longer before retrying
            if consecutive_failures >= max_consecutive_failures:
                logger.error(f"Too many ping failures ({consecutive_failures}), waiting 5 seconds...")
                for i in range(50):  # 5 seconds with monitoring check
                    if not ping_monitor_running:
                        break
                    time.sleep(0.1)
            else:
                # Normal error delay
                for i in range(10):  # 1 second with monitoring check
                    if not ping_monitor_running:
                        break
                    time.sleep(0.1)
    
    logger.info("Ping monitor thread stopped")

def independent_network_monitor_thread():
    """Independent network monitoring thread that runs continuously"""
    global network_data, network_monitor_running
    
    # Initialize first measurement
    initial_stats = get_network_io_stats()
    if initial_stats:
        network_data["last_measurement"] = {
            "timestamp": time.time(),
            "stats": initial_stats
        }
        network_data["total_bytes_sent"] = initial_stats["bytes_sent"]
        network_data["total_bytes_recv"] = initial_stats["bytes_recv"]
    
    while network_monitor_running:
        try:
            # Get current network stats
            current_stats = get_network_io_stats()
            current_time = time.time()
            
            if current_stats and network_data["last_measurement"]:
                # Calculate speeds
                time_diff = current_time - network_data["last_measurement"]["timestamp"]
                if time_diff > 0:
                    upload_speed, download_speed = calculate_transfer_speed(
                        current_stats, 
                        network_data["last_measurement"]["stats"], 
                        time_diff
                    )
                    
                    # Update current speeds
                    network_data["current_upload_speed"] = upload_speed
                    network_data["current_download_speed"] = download_speed
                    
                    # Add to history
                    network_data["transfer_history"].append({
                        "timestamp": current_time,
                        "upload_speed": upload_speed,
                        "download_speed": download_speed,
                        "total_sent": current_stats["bytes_sent"],
                        "total_recv": current_stats["bytes_recv"]
                    })
                    
                    # Maintain history size
                    if len(network_data["transfer_history"]) > network_data["max_history_points"]:
                        network_data["transfer_history"].pop(0)
                    
                    # Update totals
                    network_data["total_bytes_sent"] = current_stats["bytes_sent"]
                    network_data["total_bytes_recv"] = current_stats["bytes_recv"]
                    
                    # Emit the network data to all connected clients
                    socketio.emit('network_data', {
                        'total_sent': network_data["total_bytes_sent"],
                        'total_recv': network_data["total_bytes_recv"],
                        'total_sent_formatted': format_bytes(network_data["total_bytes_sent"]),
                        'total_recv_formatted': format_bytes(network_data["total_bytes_recv"]),
                        'current_upload_speed': upload_speed,
                        'current_download_speed': download_speed,
                        'upload_speed_formatted': format_bytes(upload_speed) + "/s",
                        'download_speed_formatted': format_bytes(download_speed) + "/s",
                        'transfer_history': network_data["transfer_history"][-20:] if network_data["transfer_history"] else []
                    })
                    
                    # Update last measurement
                    network_data["last_measurement"] = {
                        "timestamp": current_time,
                        "stats": current_stats
                    }
            
            # Wait for 2 seconds before the next measurement
            for _ in range(20):  # Check network_monitor_running every 0.1 seconds
                if not network_monitor_running:
                    break
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in network monitor thread: {e}")
            time.sleep(2)

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
    # Send current tunnel status
    current_status = 'running' if STATS["current_status"] == "Running" else 'stopped'
    emit('tunnel_status', {'status': current_status})
    
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
    
    # Send current network data if available
    global network_data
    if network_data["total_bytes_sent"] > 0 or network_data["total_bytes_recv"] > 0:
        emit('network_data', {
            'total_sent': network_data["total_bytes_sent"],
            'total_recv': network_data["total_bytes_recv"],
            'total_sent_formatted': format_bytes(network_data["total_bytes_sent"]),
            'total_recv_formatted': format_bytes(network_data["total_bytes_recv"]),
            'current_upload_speed': network_data["current_upload_speed"],
            'current_download_speed': network_data["current_download_speed"],
            'upload_speed_formatted': format_bytes(network_data["current_upload_speed"]) + "/s",
            'download_speed_formatted': format_bytes(network_data["current_download_speed"]) + "/s",
            'transfer_history': network_data["transfer_history"][-20:] if network_data["transfer_history"] else []
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
        start_independent_network_monitor()
        start_independent_status_monitor()
        
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
        global ping_monitor_running, internet_monitor_running, network_monitor_running, status_monitor_running
        ping_monitor_running = False
        internet_monitor_running = False
        network_monitor_running = False
        status_monitor_running = False
    except Exception as e:
        log(f"Error: {e}", level="error")
    finally:
        # Clean up resources
        cleanup()

if __name__ == "__main__":
    main()