/**
 * Common JavaScript for Cloudflare Tunnel Monitor
 * Shared functionality across all pages
 */

// Initialize Socket.IO connection - using let for modern JavaScript
let socket;

// Initialize common functionality
const initCommon = () => {
    try {
        // Initialize Socket.IO if not already connected
        if (typeof io !== 'undefined' && !socket) {
            socket = io({
                transports: ['websocket', 'polling'],
                timeout: 5000,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionAttempts: 5
            });
            setupSocketListeners();
        }
        
        // Set up navigation highlighting
        highlightCurrentNavItem();
        
        // Set up mobile menu toggle
        setupMobileMenu();
        
        // Initialize touch interactions for mobile
        initTouchInteractions();
    } catch (error) {
        console.error('Error initializing common functionality:', error);
    }
};

// Set up Socket.IO event listeners
const setupSocketListeners = () => {
    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        updateConnectionStatus(false);
    });
    
    // Listen for global notifications
    socket.on('notification', (data) => {
        showAlert(data.message, data.type);
    });
};

// Highlight current navigation item
const highlightCurrentNavItem = () => {
    try {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('nav a');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href === currentPath || 
                (href === '/' && currentPath === '/') || 
                (href !== '/' && currentPath.startsWith(href))) {
                item.classList.add('active');
                item.setAttribute('aria-current', 'page');
            } else {
                item.classList.remove('active');
                item.removeAttribute('aria-current');
            }
        });
    } catch (error) {
        console.error('Error highlighting navigation item:', error);
    }
};

// Show alert message with improved accessibility
const showAlert = (message, type = 'info') => {
    try {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type}`;
        alertElement.setAttribute('role', 'alert');
        alertElement.setAttribute('aria-live', 'polite');
        
        const closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'close-btn';
        closeButton.innerHTML = '&times;';
        closeButton.setAttribute('aria-label', 'Close alert');
        closeButton.addEventListener('click', () => {
            alertElement.remove();
        });
        
        alertElement.innerHTML = message;
        alertElement.appendChild(closeButton);
        
        const main = document.querySelector('main');
        if (main) {
            main.insertBefore(alertElement, main.firstChild);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.remove();
            }
        }, 5000);
    } catch (error) {
        console.error('Error showing alert:', error);
    }
};

// Set up mobile menu toggle functionality with improved accessibility
const setupMobileMenu = () => {
    try {
        const mobileMenuButton = document.getElementById('mobile-menu-button');
        const mainNav = document.getElementById('main-nav');
        
        if (mobileMenuButton && mainNav) {
            let isMenuOpen = false;
            
            const toggleMenu = () => {
                isMenuOpen = !isMenuOpen;
                
                if (isMenuOpen) {
                    mainNav.classList.remove('mobile-hidden');
                    mainNav.classList.add('mobile-visible');
                    mobileMenuButton.innerHTML = '<i class="fas fa-times"></i>';
                    mobileMenuButton.setAttribute('aria-label', 'Close menu');
                    mobileMenuButton.setAttribute('aria-expanded', 'true');
                } else {
                    mainNav.classList.add('mobile-hidden');
                    mainNav.classList.remove('mobile-visible');
                    mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
                    mobileMenuButton.setAttribute('aria-label', 'Open menu');
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                }
            };
            
            mobileMenuButton.addEventListener('click', toggleMenu);
            
            // Close menu when clicking on a link
            const navLinks = mainNav.querySelectorAll('a');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    if (window.innerWidth <= 768 && isMenuOpen) {
                        toggleMenu();
                    }
                });
            });
            
            // Handle window resize
            window.addEventListener('resize', () => {
                if (window.innerWidth > 768) {
                    mainNav.classList.remove('mobile-hidden', 'mobile-visible');
                    isMenuOpen = false;
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                } else if (!isMenuOpen) {
                    mainNav.classList.add('mobile-hidden');
                }
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (event) => {
                if (isMenuOpen && !mainNav.contains(event.target) && !mobileMenuButton.contains(event.target)) {
                    toggleMenu();
                }
            });
        }
    } catch (error) {
        console.error('Error setting up mobile menu:', error);
    }
};

// Initialize touch interactions for better mobile experience
const initTouchInteractions = () => {
    // Add touch-friendly classes to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.classList.add('touch-friendly');
    });
};

// Update connection status indicator
const updateConnectionStatus = (isConnected) => {
    const connectionIndicator = document.getElementById('connection-status');
    if (connectionIndicator) {
        connectionIndicator.className = isConnected ? 'status-indicator running' : 'status-indicator stopped';
        connectionIndicator.title = isConnected ? 'Connected to server' : 'Disconnected from server';
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initCommon);

// Export functions for global access
window.showAlert = showAlert;
window.socket = socket;