/**
 * Common JavaScript for Cloudflare Tunnel Monitor
 * Shared functionality across all pages
 */

// Initialize Socket.IO connection
// Using var instead of let to make it globally accessible
var socket;

// Initialize common functionality
function initCommon() {
    // Initialize Socket.IO if not already connected
    if (typeof io !== 'undefined' && !socket) {
        socket = io();
        setupSocketListeners();
    }
    
    // Set up navigation highlighting
    highlightCurrentNavItem();
    
    // Set up mobile menu toggle
    setupMobileMenu();
}

// Set up Socket.IO event listeners
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
    
    // Listen for global notifications
    socket.on('notification', (data) => {
        showAlert(data.message, data.type);
    });
}

// Highlight current navigation item
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('nav a');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath || 
            (href === '/' && currentPath === '/') || 
            (href !== '/' && currentPath.startsWith(href))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
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

// Set up mobile menu toggle functionality
function setupMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mainNav = document.getElementById('main-nav');
    
    if (mobileMenuButton && mainNav) {
        mobileMenuButton.addEventListener('click', () => {
            if (mainNav.classList.contains('mobile-hidden')) {
                mainNav.classList.remove('mobile-hidden');
                mainNav.classList.add('mobile-visible');
                mobileMenuButton.innerHTML = '<i class="fas fa-times"></i>';
            } else {
                mainNav.classList.add('mobile-hidden');
                mainNav.classList.remove('mobile-visible');
                mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
        
        // Close menu when clicking on a link
        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    mainNav.classList.add('mobile-hidden');
                    mainNav.classList.remove('mobile-visible');
                    mobileMenuButton.innerHTML = '<i class="fas fa-bars"></i>';
                }
            });
        });
        
        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                mainNav.classList.remove('mobile-hidden');
                mainNav.classList.remove('mobile-visible');
            } else if (!mainNav.classList.contains('mobile-visible')) {
                mainNav.classList.add('mobile-hidden');
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initCommon);