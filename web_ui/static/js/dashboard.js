/**
 * Dashboard JavaScript for Cloudflare Tunnel Monitor
 */

// Socket.IO connection is initialized in common.js

// DOM Elements
const startButton = document.getElementById('start-button');
const stopButton = document.getElementById('stop-button');
const tunnelStatusIndicator = document.getElementById('tunnel-status-indicator');
const tunnelStatusText = document.getElementById('tunnel-status-text');
const internetStatusIndicator = document.getElementById('internet-status-indicator');
const internetStatusText = document.getElementById('internet-status-text');
const pingValueElement = document.getElementById('ping-value');
const tunnelStartsElement = document.getElementById('tunnel-starts');
const internetDisconnectsElement = document.getElementById('internet-disconnects');
const uptimeElement = document.getElementById('uptime');
const lastCheckElement = document.getElementById('last-check');
const tunnelUrlElement = document.getElementById('tunnel-url');
const copyUrlButton = document.getElementById('copy-url-button');
const qrcodeContainer = document.getElementById('qrcode');
const recentLogsContainer = document.getElementById('recent-logs-container');
const pingChartCanvas = document.getElementById('ping-chart');
// WhatsApp-related elements removed

// QR Code instance
let qrcode = null;

// Ping Chart instance
let pingChart = null;
let pingData = {
    labels: [],
    datasets: [{
        label: 'Ping (ms)',
        data: [],
        borderColor: 'rgb(52, 152, 219)',
        backgroundColor: 'rgba(52, 152, 219, 0.2)',
        borderWidth: 2,
        tension: 0.2,
        fill: true
    },
    {
        label: 'Average',
        data: [],
        borderColor: 'rgb(46, 204, 113)',
        borderWidth: 1,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false
    }]
};

// Ping statistics
let pingStats = {
    avg: 0,
    min: 0,
    max: 0,
    count: 0
};

// Ping Chart configuration
const pingChartConfig = {
    type: 'line',
    data: pingData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 500
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Milliseconds'
                },
                ticks: {
                    callback: function(value) {
                        return value + ' ms';
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Time'
                },
                ticks: {
                    maxTicksLimit: 10,
                    maxRotation: 0
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return context.parsed.y + ' ms';
                    }
                }
            }
        }
    }
};

// Initialize the dashboard
function initDashboard() {
    // Set up button event listeners
    startButton.addEventListener('click', startTunnel);
    stopButton.addEventListener('click', stopTunnel);
    copyUrlButton.addEventListener('click', copyTunnelUrl);
    
    // Initialize ping chart
    if (pingChartCanvas) {
        pingChart = new Chart(pingChartCanvas, pingChartConfig);
    }
    
    // Set up Socket.IO event listeners
    socket.on('connect', () => {
        console.log('Connected to server');
        // Fetch initial ping data
        fetchPingData();
    });
    
    socket.on('status', (data) => {
        updateStatus(data.status);
    });
    
    socket.on('tunnel_url', (data) => {
        updateTunnelUrl(data.url);
    });
    
    socket.on('internet_status', (data) => {
        updateInternetStatus(data.status);
    });
    
    socket.on('ping_data', (data) => {
        updatePingData(data);
    });
    
    // Start periodic updates
    fetchStats();
    fetchLogs();
    setInterval(fetchStats, 5000); // Update stats every 5 seconds
    setInterval(fetchLogs, 2000);  // Update logs every 2 seconds
    setInterval(fetchPingData, 5000); // Update ping data every 5 seconds
}

// Start the tunnel
function startTunnel() {
    startButton.disabled = true;
    startButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
    
    fetch('/api/start', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateStatus('Running');
            startButton.disabled = true;
            stopButton.disabled = false;
        } else {
            showAlert(data.message, 'error');
            startButton.disabled = false;
        }
        startButton.innerHTML = '<i class="fas fa-play"></i> Start Tunnel';
    })
    .catch(error => {
        console.error('Error starting tunnel:', error);
        showAlert('Failed to start tunnel', 'error');
        startButton.disabled = false;
        startButton.innerHTML = '<i class="fas fa-play"></i> Start Tunnel';
    });
}

// Stop the tunnel
function stopTunnel() {
    stopButton.disabled = true;
    stopButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';
    
    fetch('/api/stop', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateStatus('Stopped');
            startButton.disabled = false;
            stopButton.disabled = true;
        } else {
            showAlert(data.message, 'error');
            stopButton.disabled = false;
        }
        stopButton.innerHTML = '<i class="fas fa-stop"></i> Stop Tunnel';
    })
    .catch(error => {
        console.error('Error stopping tunnel:', error);
        showAlert('Failed to stop tunnel', 'error');
        stopButton.disabled = false;
        stopButton.innerHTML = '<i class="fas fa-stop"></i> Stop Tunnel';
    });
}

// WhatsApp test function removed

// Copy tunnel URL to clipboard
function copyTunnelUrl() {
    const url = tunnelUrlElement.value;
    if (url && url !== 'Not available') {
        navigator.clipboard.writeText(url)
            .then(() => {
                showAlert('URL copied to clipboard', 'success');
                copyUrlButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    copyUrlButton.innerHTML = '<i class="fas fa-copy"></i> Copy URL';
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy URL:', err);
                showAlert('Failed to copy URL', 'error');
            });
    }
}

// Update tunnel status
function updateStatus(status) {
    tunnelStatusText.textContent = status;
    
    if (status === 'Running') {
        tunnelStatusIndicator.className = 'status-indicator running';
        startButton.disabled = true;
        stopButton.disabled = false;
    } else if (status === 'Stopped') {
        tunnelStatusIndicator.className = 'status-indicator stopped';
        startButton.disabled = false;
        stopButton.disabled = true;
        // Clear tunnel URL
        tunnelUrlElement.value = 'Not available';
        // Clear QR code
        qrcodeContainer.innerHTML = '<div class="qrcode-placeholder">QR Code will appear when tunnel is active</div>';
    } else {
        tunnelStatusIndicator.className = 'status-indicator warning';
    }
}

// Update internet status
function updateInternetStatus(status) {
    internetStatusText.textContent = status ? 'Connected' : 'Disconnected';
    internetStatusIndicator.className = status ? 'status-indicator running' : 'status-indicator stopped';
}

// Update tunnel URL and generate QR code
function updateTunnelUrl(url) {
    if (!url) return;
    
    tunnelUrlElement.value = url;
    
    // Generate QR code
    qrcodeContainer.innerHTML = '';
    qrcode = new QRCode(qrcodeContainer, {
        text: url,
        width: 150,
        height: 150,
        colorDark: '#2c3e50',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });
}

// Fetch statistics from the server
function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(stats => {
            // Update statistics
    tunnelStartsElement.textContent = stats.tunnel_starts;
    internetDisconnectsElement.textContent = stats.internet_disconnects;
    
    // Update uptime
    if (stats.total_uptime) {
        uptimeElement.textContent = formatUptime(stats.total_uptime);
    }
    
    // Update status
    updateStatus(stats.current_status);
    
    // Update tunnel URL if available
    if (stats.last_tunnel_url) {
        updateTunnelUrl(stats.last_tunnel_url);
    }
    
    // Update last check time
    lastCheckElement.textContent = new Date().toLocaleTimeString();
        })
        .catch(error => {
            console.error('Error fetching stats:', error);
        });
}

// Fetch logs from the server
function fetchLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(logs => {
            if (logs.length > 0) {
                // Clear placeholder if present
                const placeholder = recentLogsContainer.querySelector('.placeholder');
                if (placeholder) {
                    recentLogsContainer.innerHTML = '';
                }
                
                // Add new logs
                logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry ${log.level}`;
                    logEntry.innerHTML = `<span class="log-timestamp">[${log.timestamp}]</span> ${log.message}`;
                    recentLogsContainer.appendChild(logEntry);
                });
                
                // Limit to 10 most recent logs
                const entries = recentLogsContainer.querySelectorAll('.log-entry');
                if (entries.length > 10) {
                    for (let i = 0; i < entries.length - 10; i++) {
                        recentLogsContainer.removeChild(entries[i]);
                    }
                }
                
                // Scroll to bottom
                recentLogsContainer.scrollTop = recentLogsContainer.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
        });
}

// Format uptime in HH:MM:SS
function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        secs.toString().padStart(2, '0')
    ].join(':');
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="close-btn" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    document.querySelector('main').insertBefore(alertElement, document.querySelector('main').firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertElement.parentNode) {
            alertElement.remove();
        }
    }, 5000);
}

// Fetch ping data from the server
function fetchPingData() {
    fetch('/api/ping')
        .then(response => response.json())
        .then(data => {
            if (data && data.last_ping_time !== null) {
                updatePingData(data);
            }
        })
        .catch(error => {
            console.error('Error fetching ping data:', error);
        });
}

// Update ping data display
function updatePingData(data) {
    // Update the ping value display
    if (data.last_ping_time !== null) {
        pingValueElement.textContent = data.last_ping_time + ' ms';
        
        // Add color class based on ping value
        pingValueElement.className = 'ping-value';
        if (data.last_ping_time < 50) {
            pingValueElement.classList.add('excellent');
        } else if (data.last_ping_time < 100) {
            pingValueElement.classList.add('good');
        } else if (data.last_ping_time < 200) {
            pingValueElement.classList.add('fair');
        } else {
            pingValueElement.classList.add('poor');
        }
    } else {
        pingValueElement.textContent = 'Unavailable';
        pingValueElement.className = 'ping-value unavailable';
    }
    
    // Update ping statistics if available
    if (data.stats) {
        pingStats = data.stats;
        
        // Add statistics to the dashboard
        const statsContainer = document.getElementById('ping-stats-container');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Avg:</span>
                    <span class="stat-value">${pingStats.avg.toFixed(1)} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Min:</span>
                    <span class="stat-value">${pingStats.min} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Max:</span>
                    <span class="stat-value">${pingStats.max} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Count:</span>
                    <span class="stat-value">${pingStats.count}</span>
                </div>
            `;
        }
    }
    
    // Update the ping chart if we have history data
    if (pingChart && data.ping_history && data.ping_history.length > 0) {
        // Reset data for the last minute view
        pingData.labels = [];
        pingData.datasets[0].data = [];
        pingData.datasets[1].data = [];
        
        // Add new data points
        data.ping_history.forEach(item => {
            const time = new Date(item.timestamp * 1000).toLocaleTimeString();
            pingData.labels.push(time);
            pingData.datasets[0].data.push(item.ping_time);
            
            // Add average line if we have stats
            if (data.stats && data.stats.avg) {
                pingData.datasets[1].data.push(data.stats.avg);
            }
        });
        
        // Update the chart
        pingChart.update();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initDashboard);