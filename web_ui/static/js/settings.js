/**
 * Settings JavaScript for Cloudflare Tunnel Monitor
 */

// DOM Elements
const settingsForm = document.getElementById('settings-form');
const saveButton = document.getElementById('save-settings-button');
const resetButton = document.getElementById('reset-settings-button');
const debugCheckbox = document.getElementById('debug_mode');

// Initialize settings page
function initSettings() {
    // Set up button event listeners
    saveButton.addEventListener('click', saveSettings);
    resetButton.addEventListener('click', resetSettings);
    
    // Load current settings
    loadSettings();
}

// Load settings from the server
function loadSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            // Populate form fields with current settings
            document.getElementById('tunnel_url').value = settings.tunnel_url || '';
            document.getElementById('check_interval').value = settings.check_interval || 60;
            document.getElementById('max_retries').value = settings.max_retries || 3;
            document.getElementById('retry_delay').value = settings.retry_delay || 5;
            // Ping test URL removed - using 1.1.1.1 as permanent default
            
            // Set checkboxes
            debugCheckbox.checked = settings.debug_mode || false;
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showAlert('Failed to load settings', 'error');
        });
}

// Save settings to the server
function saveSettings() {
    saveButton.disabled = true;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    
    // Collect form data
    const settings = {
        tunnel_url: document.getElementById('tunnel_url').value,
        check_interval: parseInt(document.getElementById('check_interval').value),
        max_retries: parseInt(document.getElementById('max_retries').value),
        retry_delay: parseInt(document.getElementById('retry_delay').value),
        debug_mode: debugCheckbox.checked
        // Ping test URL removed - using 1.1.1.1 as permanent default
    };
    
    // Validate settings
    if (!settings.tunnel_url) {
        showAlert('Tunnel URL is required', 'error');
        saveButton.disabled = false;
        saveButton.innerHTML = '<i class="fas fa-save"></i> Save Settings';
        return;
    }
    
    // Send settings to server
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showAlert('Settings saved successfully', 'success');
        } else {
            showAlert(data.message || 'Failed to save settings', 'error');
        }
        saveButton.disabled = false;
        saveButton.innerHTML = '<i class="fas fa-save"></i> Save Settings';
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showAlert('Failed to save settings', 'error');
        saveButton.disabled = false;
        saveButton.innerHTML = '<i class="fas fa-save"></i> Save Settings';
    });
}

// Reset settings to defaults
function resetSettings() {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
        fetch('/api/settings/reset', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('Settings reset to defaults', 'success');
                loadSettings(); // Reload settings from server
            } else {
                showAlert(data.message || 'Failed to reset settings', 'error');
            }
        })
        .catch(error => {
            console.error('Error resetting settings:', error);
            showAlert('Failed to reset settings', 'error');
        });
    }
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
document.addEventListener('DOMContentLoaded', initSettings);