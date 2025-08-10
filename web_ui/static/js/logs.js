/**
 * Logs JavaScript for Cloudflare Tunnel Monitor
 */

// DOM Elements
const logsContainer = document.getElementById('logs-container');
const clearLogsButton = document.getElementById('clear-logs-button');
const exportLogsButton = document.getElementById('export-logs-button');
const autoScrollCheckbox = document.getElementById('auto-scroll-checkbox');
const filterButtons = document.querySelectorAll('.filter-button');

// Variables
let logs = [];
let currentFilter = 'all';
let autoScroll = true;

// Initialize logs page
function initLogs() {
    // Set up button event listeners
    clearLogsButton.addEventListener('click', clearLogs);
    exportLogsButton.addEventListener('click', exportLogs);
    autoScrollCheckbox.addEventListener('change', toggleAutoScroll);
    
    // Set up filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');
            setActiveFilter(filter);
            filterLogs(filter);
        });
    });
    
    // Set auto-scroll checkbox
    autoScrollCheckbox.checked = autoScroll;
    
    // Start fetching logs
    fetchLogs();
    setInterval(fetchLogs, 2000); // Update logs every 2 seconds
}

// Fetch logs from the server
function fetchLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(newLogs => {
            if (newLogs.length > 0) {
                // Update logs array with new logs
                logs = [...logs, ...newLogs];
                
                // Limit logs to prevent memory issues (keep last 1000 logs)
                if (logs.length > 1000) {
                    logs = logs.slice(logs.length - 1000);
                }
                
                // Apply current filter and update display
                filterLogs(currentFilter);
            }
        })
        .catch(error => {
            console.error('Error fetching logs:', error);
        });
}

// Filter logs by level
function filterLogs(filter) {
    // Clear logs container
    logsContainer.innerHTML = '';
    
    // Filter logs based on selected filter
    const filteredLogs = filter === 'all' ? logs : logs.filter(log => log.level === filter);
    
    if (filteredLogs.length === 0) {
        // Show placeholder if no logs
        const placeholder = document.createElement('div');
        placeholder.className = 'logs-placeholder';
        placeholder.textContent = 'No logs to display';
        logsContainer.appendChild(placeholder);
    } else {
        // Add filtered logs to container
        filteredLogs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level}`;
            logEntry.innerHTML = `<span class="log-timestamp">[${log.timestamp}]</span> ${log.message}`;
            logsContainer.appendChild(logEntry);
        });
        
        // Scroll to bottom if auto-scroll is enabled
        if (autoScroll) {
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }
    }
}

// Set active filter button
function setActiveFilter(filter) {
    currentFilter = filter;
    
    // Update active button
    filterButtons.forEach(button => {
        if (button.getAttribute('data-filter') === filter) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Toggle auto-scroll
function toggleAutoScroll() {
    autoScroll = autoScrollCheckbox.checked;
    
    // Scroll to bottom if auto-scroll is enabled
    if (autoScroll) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

// Clear logs
function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        fetch('/api/logs/clear', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                logs = [];
                logsContainer.innerHTML = '';
                const placeholder = document.createElement('div');
                placeholder.className = 'logs-placeholder';
                placeholder.textContent = 'No logs to display';
                logsContainer.appendChild(placeholder);
                showAlert('Logs cleared successfully', 'success');
            } else {
                showAlert(data.message || 'Failed to clear logs', 'error');
            }
        })
        .catch(error => {
            console.error('Error clearing logs:', error);
            showAlert('Failed to clear logs', 'error');
        });
    }
}

// Export logs to file
function exportLogs() {
    // Create a blob with logs data
    const logsText = logs.map(log => `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.message}`).join('\n');
    const blob = new Blob([logsText], { type: 'text/plain' });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cloudflare_tunnel_logs_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 0);
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

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initLogs);