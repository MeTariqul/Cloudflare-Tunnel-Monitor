/**
 * Dashboard JavaScript for Cloudflare Tunnel Monitor
 * Modern ES6+ implementation with enhanced error handling
 */

// Dashboard class for better organization
class Dashboard {
    constructor() {
        this.socket = window.socket;
        this.qrcode = null;
        this.pingChart = null;
        this.pingStats = {
            avg: 0,
            min: 0,
            max: 0,
            count: 0
        };
        this.elements = {};
        this.chartConfig = this.getChartConfig();
        this.init();
    }

    // Initialize dashboard
    init() {
        try {
            this.cacheElements();
            this.setupEventListeners();
            this.initializePingChart();
            this.setupSocketListeners();
            this.startPeriodicUpdates();
        } catch (error) {
            console.error('Error initializing dashboard:', error);
            this.showAlert('Failed to initialize dashboard', 'error');
        }
    }

    // Cache DOM elements for better performance
    cacheElements() {
        this.elements = {
            startButton: document.getElementById('start-button'),
            stopButton: document.getElementById('stop-button'),
            tunnelStatusIndicator: document.getElementById('tunnel-status-indicator'),
            tunnelStatusText: document.getElementById('tunnel-status-text'),
            internetStatusIndicator: document.getElementById('internet-status-indicator'),
            internetStatusText: document.getElementById('internet-status-text'),
            pingValue: document.getElementById('ping-value'),
            tunnelStarts: document.getElementById('tunnel-starts'),
            internetDisconnects: document.getElementById('internet-disconnects'),
            uptime: document.getElementById('uptime'),
            lastCheck: document.getElementById('last-check'),
            tunnelUrl: document.getElementById('tunnel-url'),
            copyUrlButton: document.getElementById('copy-url-button'),
            qrcodeContainer: document.getElementById('qrcode'),
            recentLogsContainer: document.getElementById('recent-logs-container'),
            pingChartCanvas: document.getElementById('ping-chart'),
            pingStatsContainer: document.getElementById('ping-stats-container')
        };

        // Validate required elements
        const requiredElements = ['startButton', 'stopButton', 'tunnelStatusIndicator', 'tunnelStatusText'];
        for (const elementName of requiredElements) {
            if (!this.elements[elementName]) {
                throw new Error(`Required element '${elementName}' not found`);
            }
        }
    }

    // Setup event listeners
    setupEventListeners() {
        this.elements.startButton.addEventListener('click', () => this.startTunnel());
        this.elements.stopButton.addEventListener('click', () => this.stopTunnel());
        this.elements.copyUrlButton.addEventListener('click', () => this.copyTunnelUrl());
        
        // Add keyboard support for accessibility
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 's':
                        event.preventDefault();
                        this.startTunnel();
                        break;
                    case 'x':
                        event.preventDefault();
                        this.stopTunnel();
                        break;
                }
            }
        });
    }

    // Initialize ping chart
    initializePingChart() {
        if (this.elements.pingChartCanvas) {
            this.pingChart = new Chart(this.elements.pingChartCanvas, this.chartConfig);
        }
    }

    // Get chart configuration
    getChartConfig() {
        return {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Ping (ms)',
                    data: [],
                    borderColor: 'rgba(52, 152, 219, 1)',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 2,
                    pointHoverRadius: 6,
                    pointBackgroundColor: 'rgba(52, 152, 219, 1)',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointHoverBackgroundColor: 'rgba(52, 152, 219, 1)',
                    pointHoverBorderColor: '#ffffff',
                    cubicInterpolationMode: 'monotone'
                }, {
                    label: 'Average',
                    data: [],
                    borderColor: 'rgba(46, 204, 113, 0.8)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [8, 4],
                    pointRadius: 0,
                    fill: false,
                    tension: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            callback: (value) => `${value} ms`,
                            maxTicksLimit: 8
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time (Last 60 seconds)',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        ticks: {
                            maxTicksLimit: 8,
                            maxRotation: 0,
                            callback: function(value, index) {
                                // Show only every few labels to avoid crowding
                                if (index % Math.ceil(this.chart.data.labels.length / 6) === 0) {
                                    return this.chart.data.labels[index];
                                }
                                return '';
                            }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 11
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: (context) => {
                                if (context.datasetIndex === 0) {
                                    return `Ping: ${context.parsed.y} ms`;
                                } else {
                                    return `Average: ${context.parsed.y.toFixed(1)} ms`;
                                }
                            }
                        }
                    }
                }
            }
        };
    }

    // Setup Socket.IO event listeners
    setupSocketListeners() {
        if (this.socket) {
            this.socket.on('connect', () => {
                console.log('Connected to server');
                this.fetchPingData();
            });
            
            this.socket.on('status', (data) => {
                this.updateStatus(data.status);
            });
            
            this.socket.on('tunnel_url', (data) => {
                this.updateTunnelUrl(data.url);
            });
            
            this.socket.on('internet_status', (data) => {
                this.updateInternetStatus(data.status);
            });
            
            this.socket.on('ping_data', (data) => {
                this.updatePingData(data);
            });
        }
    }

    // Start periodic updates
    startPeriodicUpdates() {
        this.fetchStats();
        this.fetchLogs();
        
        // More frequent ping updates for smooth river flow
        setInterval(() => this.fetchStats(), 5000);
        setInterval(() => this.fetchLogs(), 2000);
        setInterval(() => this.fetchPingData(), 1000); // Update every second for smooth flow
        
        // Start real-time ping monitoring
        this.startRealTimePing();
    }
    
    // Start real-time ping monitoring for river effect
    startRealTimePing() {
        if (this.pingChart && this.socket) {
            // Listen for real-time ping updates
            this.socket.on('real_time_ping', (data) => {
                this.updatePingChart(data);
            });
        }
    }

    // Start the tunnel
    async startTunnel() {
        try {
            this.elements.startButton.disabled = true;
            this.elements.startButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting...';
            
            const response = await fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateStatus('Running');
                this.elements.startButton.disabled = true;
                this.elements.stopButton.disabled = false;
            } else {
                this.showAlert(data.message || 'Failed to start tunnel', 'error');
                this.elements.startButton.disabled = false;
            }
        } catch (error) {
            console.error('Error starting tunnel:', error);
            this.showAlert('Failed to start tunnel', 'error');
            this.elements.startButton.disabled = false;
        } finally {
            this.elements.startButton.innerHTML = '<i class="fas fa-play"></i> Start Tunnel';
        }
    }

    // Stop the tunnel
    async stopTunnel() {
        try {
            this.elements.stopButton.disabled = true;
            this.elements.stopButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Stopping...';
            
            const response = await fetch('/api/stop', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateStatus('Stopped');
                this.elements.startButton.disabled = false;
                this.elements.stopButton.disabled = true;
            } else {
                this.showAlert(data.message || 'Failed to stop tunnel', 'error');
                this.elements.stopButton.disabled = false;
            }
        } catch (error) {
            console.error('Error stopping tunnel:', error);
            this.showAlert('Failed to stop tunnel', 'error');
            this.elements.stopButton.disabled = false;
        } finally {
            this.elements.stopButton.innerHTML = '<i class="fas fa-stop"></i> Stop Tunnel';
        }
    }

    // Copy tunnel URL to clipboard
    async copyTunnelUrl() {
        try {
            const url = this.elements.tunnelUrl.value;
            if (url && url !== 'Not available') {
                await navigator.clipboard.writeText(url);
                this.showAlert('URL copied to clipboard', 'success');
                this.elements.copyUrlButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.elements.copyUrlButton.innerHTML = '<i class="fas fa-copy"></i> Copy URL';
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to copy URL:', error);
            this.showAlert('Failed to copy URL', 'error');
        }
    }

    // Update tunnel status
    updateStatus(status) {
        if (!this.elements.tunnelStatusText) return;
        
        this.elements.tunnelStatusText.textContent = status;
        
        if (status === 'Running') {
            this.elements.tunnelStatusIndicator.className = 'status-indicator running';
            this.elements.startButton.disabled = true;
            this.elements.stopButton.disabled = false;
        } else if (status === 'Stopped') {
            this.elements.tunnelStatusIndicator.className = 'status-indicator stopped';
            this.elements.startButton.disabled = false;
            this.elements.stopButton.disabled = true;
            // Clear tunnel URL
            this.elements.tunnelUrl.value = 'Not available';
            // Clear QR code
            if (this.elements.qrcodeContainer) {
                this.elements.qrcodeContainer.innerHTML = '<div class="qrcode-placeholder">QR Code will appear when tunnel is active</div>';
            }
        } else {
            this.elements.tunnelStatusIndicator.className = 'status-indicator warning';
        }
    }

    // Update internet status
    updateInternetStatus(status) {
        if (!this.elements.internetStatusText) return;
        
        this.elements.internetStatusText.textContent = status ? 'Connected' : 'Disconnected';
        this.elements.internetStatusIndicator.className = status ? 'status-indicator running' : 'status-indicator stopped';
    }

    // Update tunnel URL and generate QR code
    updateTunnelUrl(url) {
        if (!url || !this.elements.tunnelUrl) return;
        
        this.elements.tunnelUrl.value = url;
        
        // Generate QR code
        if (this.elements.qrcodeContainer && typeof QRCode !== 'undefined') {
            this.elements.qrcodeContainer.innerHTML = '';
            this.qrcode = new QRCode(this.elements.qrcodeContainer, {
                text: url,
                width: 150,
                height: 150,
                colorDark: '#2c3e50',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.H
            });
        }
    }

    // Fetch statistics from the server
    async fetchStats() {
        try {
            const response = await fetch('/api/stats');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const stats = await response.json();
            
            // Update statistics
            if (this.elements.tunnelStarts) {
                this.elements.tunnelStarts.textContent = stats.tunnel_starts;
            }
            if (this.elements.internetDisconnects) {
                this.elements.internetDisconnects.textContent = stats.internet_disconnects;
            }
            
            // Update uptime
            if (stats.total_uptime && this.elements.uptime) {
                this.elements.uptime.textContent = this.formatUptime(stats.total_uptime);
            }
            
            // Update status
            this.updateStatus(stats.current_status);
            
            // Update tunnel URL if available
            if (stats.last_tunnel_url) {
                this.updateTunnelUrl(stats.last_tunnel_url);
            }
            
            // Update last check time
            if (this.elements.lastCheck) {
                this.elements.lastCheck.textContent = new Date().toLocaleTimeString();
            }
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    // Fetch logs from the server
    async fetchLogs() {
        try {
            const response = await fetch('/api/logs');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const logs = await response.json();
            
            if (logs.length > 0 && this.elements.recentLogsContainer) {
                // Clear placeholder if present
                const placeholder = this.elements.recentLogsContainer.querySelector('.placeholder');
                if (placeholder) {
                    this.elements.recentLogsContainer.innerHTML = '';
                }
                
                // Add new logs
                logs.forEach(log => {
                    const logEntry = document.createElement('div');
                    logEntry.className = `log-entry ${log.level}`;
                    logEntry.innerHTML = `<span class="log-timestamp">[${log.timestamp}]</span> ${log.message}`;
                    this.elements.recentLogsContainer.appendChild(logEntry);
                });
                
                // Limit to 10 most recent logs
                const entries = this.elements.recentLogsContainer.querySelectorAll('.log-entry');
                if (entries.length > 10) {
                    for (let i = 0; i < entries.length - 10; i++) {
                        this.elements.recentLogsContainer.removeChild(entries[i]);
                    }
                }
                
                // Scroll to bottom
                this.elements.recentLogsContainer.scrollTop = this.elements.recentLogsContainer.scrollHeight;
            }
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    }

    // Format uptime in HH:MM:SS
    formatUptime(seconds) {
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
    showAlert(message, type = 'info') {
        if (typeof window.showAlert === 'function') {
            window.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // Fetch ping data from the server
    async fetchPingData() {
        try {
            const response = await fetch('/api/ping');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            if (data && data.last_ping_time !== null) {
                this.updatePingData(data);
            }
        } catch (error) {
            console.error('Error fetching ping data:', error);
        }
    }

    // Update ping data display
    updatePingData(data) {
        // Update the ping value display
        if (this.elements.pingValue) {
            if (data.last_ping_time !== null) {
                this.elements.pingValue.textContent = data.last_ping_time + ' ms';
                
                // Add color class based on ping value
                this.elements.pingValue.className = 'ping-value';
                if (data.last_ping_time < 50) {
                    this.elements.pingValue.classList.add('excellent');
                } else if (data.last_ping_time < 100) {
                    this.elements.pingValue.classList.add('good');
                } else if (data.last_ping_time < 200) {
                    this.elements.pingValue.classList.add('fair');
                } else {
                    this.elements.pingValue.classList.add('poor');
                }
            } else {
                this.elements.pingValue.textContent = 'Unavailable';
                this.elements.pingValue.className = 'ping-value unavailable';
            }
        }
        
        // Update ping statistics if available
        if (data.stats) {
            this.pingStats = data.stats;
            this.updatePingStats();
        }
        
        // Update the ping chart if we have history data
        if (this.pingChart && data.ping_history && data.ping_history.length > 0) {
            this.updatePingChart(data);
        }
    }

    // Update ping statistics display
    updatePingStats() {
        if (!this.elements.pingStatsContainer) return;
        
        const statItems = this.elements.pingStatsContainer.querySelectorAll('.stat-item');
        if (statItems.length === 4) {
            // Update existing stat items
            statItems[0].querySelector('.stat-value').textContent = `${this.pingStats.avg.toFixed(1)} ms`;
            statItems[1].querySelector('.stat-value').textContent = `${this.pingStats.min} ms`;
            statItems[2].querySelector('.stat-value').textContent = `${this.pingStats.max} ms`;
            statItems[3].querySelector('.stat-value').textContent = `${this.pingStats.count}`;
        } else {
            // Create new stat items if they don't exist
            this.elements.pingStatsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Avg:</span>
                    <span class="stat-value">${this.pingStats.avg.toFixed(1)} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Min:</span>
                    <span class="stat-value">${this.pingStats.min} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Max:</span>
                    <span class="stat-value">${this.pingStats.max} ms</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Count:</span>
                    <span class="stat-value">${this.pingStats.count}</span>
                </div>
            `;
        }
    }

    // Update ping chart with flowing river effect
    updatePingChart(data) {
        if (!this.pingChart) return;
        
        const maxDataPoints = 60; // 60 seconds of data
        const now = Date.now();
        
        // Get current data
        const chartData = this.pingChart.data;
        
        if (data.ping_history && data.ping_history.length > 0) {
            // Use server data if available
            chartData.labels = [];
            chartData.datasets[0].data = [];
            chartData.datasets[1].data = [];
            
            // Filter to last 60 seconds and sort by timestamp
            const cutoffTime = now / 1000 - 60; // 60 seconds ago
            const recentData = data.ping_history
                .filter(item => item.timestamp > cutoffTime)
                .sort((a, b) => a.timestamp - b.timestamp);
            
            recentData.forEach(item => {
                const timeLabel = new Date(item.timestamp * 1000).toLocaleTimeString('en-US', {
                    hour12: false,
                    minute: '2-digit',
                    second: '2-digit'
                });
                chartData.labels.push(timeLabel);
                chartData.datasets[0].data.push(item.ping_time || 0);
                
                // Add average line if we have stats
                if (data.stats && data.stats.avg) {
                    chartData.datasets[1].data.push(data.stats.avg);
                } else {
                    chartData.datasets[1].data.push(null);
                }
            });
        } else {
            // Add single new data point for flowing effect
            const timeLabel = new Date().toLocaleTimeString('en-US', {
                hour12: false,
                minute: '2-digit',
                second: '2-digit'
            });
            
            // Add new data point
            chartData.labels.push(timeLabel);
            chartData.datasets[0].data.push(data.last_ping_time || 0);
            
            if (data.stats && data.stats.avg) {
                chartData.datasets[1].data.push(data.stats.avg);
            } else {
                chartData.datasets[1].data.push(null);
            }
            
            // Remove old data points to maintain 60-second window
            if (chartData.labels.length > maxDataPoints) {
                const pointsToRemove = chartData.labels.length - maxDataPoints;
                chartData.labels.splice(0, pointsToRemove);
                chartData.datasets[0].data.splice(0, pointsToRemove);
                chartData.datasets[1].data.splice(0, pointsToRemove);
            }
        }
        
        // Create smooth flowing animation
        this.pingChart.update('none'); // Update without animation first
        
        // Then animate the new data point
        requestAnimationFrame(() => {
            this.pingChart.update('active');
        });
        
        // Add sparkle effect for new data points
        this.addSparkleEffect();
    }
    
    // Add sparkle effect for visual appeal
    addSparkleEffect() {
        const canvas = this.elements.pingChartCanvas;
        if (!canvas) return;
        
        // Create temporary sparkle elements
        const sparkle = document.createElement('div');
        sparkle.className = 'chart-sparkle';
        sparkle.style.cssText = `
            position: absolute;
            width: 6px;
            height: 6px;
            background: radial-gradient(circle, rgba(52, 152, 219, 1) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            top: ${Math.random() * canvas.offsetHeight}px;
            left: ${canvas.offsetWidth - 20}px;
            opacity: 1;
            z-index: 10;
            animation: sparkleFloat 2s ease-out forwards;
        `;
        
        canvas.parentElement.style.position = 'relative';
        canvas.parentElement.appendChild(sparkle);
        
        // Remove sparkle after animation
        setTimeout(() => {
            if (sparkle.parentNode) {
                sparkle.parentNode.removeChild(sparkle);
            }
        }, 2000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new Dashboard();
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
});