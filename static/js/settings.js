/**
 * Settings JavaScript for Cloudflare Tunnel Monitor
 * Modern ES6+ implementation with enhanced error handling
 */

class Settings {
    constructor() {
        this.elements = {};
        this.init();
    }

    // Initialize settings page
    init() {
        try {
            this.cacheElements();
            this.setupEventListeners();
            this.loadSettings();
        } catch (error) {
            console.error('Error initializing settings:', error);
            this.showAlert('Failed to initialize settings page', 'error');
        }
    }

    // Cache DOM elements
    cacheElements() {
        this.elements = {
            settingsForm: document.getElementById('settings-form'),
            saveButton: document.getElementById('save-settings-button'),
            resetButton: document.getElementById('reset-settings-button'),
            debugCheckbox: document.getElementById('debug_mode'),
            tunnelUrl: document.getElementById('tunnel_url'),
            checkInterval: document.getElementById('check_interval'),
            maxRetries: document.getElementById('max_retries'),
            retryDelay: document.getElementById('retry_delay')
        };

        // Validate required elements
        const requiredElements = ['settingsForm', 'saveButton', 'resetButton'];
        for (const elementName of requiredElements) {
            if (!this.elements[elementName]) {
                throw new Error(`Required element '${elementName}' not found`);
            }
        }
    }

    // Setup event listeners
    setupEventListeners() {
        this.elements.saveButton.addEventListener('click', () => this.saveSettings());
        this.elements.resetButton.addEventListener('click', () => this.resetSettings());
        
        // Add form validation
        this.elements.settingsForm.addEventListener('input', () => this.validateForm());
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 's':
                        event.preventDefault();
                        this.saveSettings();
                        break;
                    case 'r':
                        if (event.shiftKey) {
                            event.preventDefault();
                            this.resetSettings();
                        }
                        break;
                }
            }
        });
    }

    // Initialize theme from localStorage or system preference
    initializeTheme() {
        const savedTheme = localStorage.getItem('theme-preference') || 'auto';
        
        // Set the correct radio button
        this.elements.themeRadios.forEach(radio => {
            if (radio.value === savedTheme) {
                radio.checked = true;
            }
        });
        
        this.applyTheme(savedTheme);
    }
    
    // Handle theme change
    handleThemeChange(theme) {
        localStorage.setItem('theme-preference', theme);
        this.applyTheme(theme);
        
        // Add a smooth transition effect
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }
    
    // Apply theme to document
    applyTheme(theme) {
        const root = document.documentElement;
        
        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
        } else if (theme === 'light') {
            root.setAttribute('data-theme', 'light');
        } else {
            // Auto mode - remove attribute to use system preference
            root.removeAttribute('data-theme');
        }
    }
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const settings = await response.json();
            
            // Populate form fields with current settings
            if (this.elements.tunnelUrl) {
                this.elements.tunnelUrl.value = settings.tunnel_url || '';
            }
            if (this.elements.checkInterval) {
                this.elements.checkInterval.value = settings.check_interval || 60;
            }
            if (this.elements.maxRetries) {
                this.elements.maxRetries.value = settings.max_retries || 3;
            }
            if (this.elements.retryDelay) {
                this.elements.retryDelay.value = settings.retry_delay || 5;
            }
            
            // Set checkboxes
            if (this.elements.debugCheckbox) {
                this.elements.debugCheckbox.checked = settings.debug_mode || false;
            }
            
            this.validateForm();
        } catch (error) {
            console.error('Error loading settings:', error);
            this.showAlert('Failed to load settings', 'error');
        }
    }

    // Save settings to the server
    async saveSettings() {
        try {
            // Validate form before saving
            if (!this.validateForm()) {
                return;
            }
            
            this.elements.saveButton.disabled = true;
            this.elements.saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            
            // Collect form data
            const settings = {
                tunnel_url: this.elements.tunnelUrl?.value || '',
                check_interval: parseInt(this.elements.checkInterval?.value || 60),
                max_retries: parseInt(this.elements.maxRetries?.value || 3),
                retry_delay: parseInt(this.elements.retryDelay?.value || 5),
                debug_mode: this.elements.debugCheckbox?.checked || false
            };
            
            // Validate settings
            if (!settings.tunnel_url) {
                this.showAlert('Tunnel URL is required', 'error');
                return;
            }
            
            // Send settings to server
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings),
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showAlert('Settings saved successfully', 'success');
            } else {
                this.showAlert(data.message || 'Failed to save settings', 'error');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showAlert('Failed to save settings', 'error');
        } finally {
            this.elements.saveButton.disabled = false;
            this.elements.saveButton.innerHTML = '<i class="fas fa-save"></i> Save Settings';
        }
    }

    // Reset settings to defaults
    async resetSettings() {
        try {
            const confirmed = await this.showConfirmDialog(
                'Are you sure you want to reset all settings to default values?'
            );
            
            if (!confirmed) return;
            
            const response = await fetch('/api/settings/reset', {
                method: 'POST',
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showAlert('Settings reset to defaults', 'success');
                await this.loadSettings(); // Reload settings from server
            } else {
                this.showAlert(data.message || 'Failed to reset settings', 'error');
            }
        } catch (error) {
            console.error('Error resetting settings:', error);
            this.showAlert('Failed to reset settings', 'error');
        }
    }

    // Validate form
    validateForm() {
        let isValid = true;
        
        // Validate tunnel URL
        if (this.elements.tunnelUrl) {
            const url = this.elements.tunnelUrl.value.trim();
            if (!url) {
                this.setFieldError(this.elements.tunnelUrl, 'Tunnel URL is required');
                isValid = false;
            } else if (!this.isValidUrl(url)) {
                this.setFieldError(this.elements.tunnelUrl, 'Please enter a valid URL');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.tunnelUrl);
            }
        }
        
        // Validate numeric fields
        const numericFields = [
            { element: this.elements.checkInterval, min: 1, max: 3600, name: 'Check Interval' },
            { element: this.elements.maxRetries, min: 1, max: 100, name: 'Max Retries' },
            { element: this.elements.retryDelay, min: 1, max: 3600, name: 'Retry Delay' }
        ];
        
        for (const field of numericFields) {
            if (field.element) {
                const value = parseInt(field.element.value);
                if (isNaN(value) || value < field.min || value > field.max) {
                    this.setFieldError(field.element, `${field.name} must be between ${field.min} and ${field.max}`);
                    isValid = false;
                } else {
                    this.clearFieldError(field.element);
                }
            }
        }
        
        // Update save button state
        if (this.elements.saveButton) {
            this.elements.saveButton.disabled = !isValid;
        }
        
        return isValid;
    }

    // Utility functions
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    setFieldError(element, message) {
        element.classList.add('error');
        let errorElement = element.parentNode.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            element.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
    }

    clearFieldError(element) {
        element.classList.remove('error');
        const errorElement = element.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.remove();
        }
    }

    showConfirmDialog(message) {
        return new Promise((resolve) => {
            resolve(confirm(message));
        });
    }

    // Show alert message
    showAlert(message, type = 'info') {
        if (typeof window.showAlert === 'function') {
            window.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize settings when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new Settings();
    } catch (error) {
        console.error('Failed to initialize settings:', error);
    }
});