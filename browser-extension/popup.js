// Medical Fact Verifier Extension - Popup Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Popup loaded');
    
    // Check backend status
    checkBackendStatus();
    
    // Load statistics
    loadStatistics();
    
    // Add event listeners
    setupEventListeners();
});

function checkBackendStatus() {
    const statusElement = document.getElementById('backend-status');
    if (!statusElement) return;
    
    statusElement.textContent = 'Checking...';
    statusElement.className = 'checking';
    
    fetch('http://localhost:5000/status')
        .then(response => response.json())
        .then(data => {
            statusElement.textContent = 'Connected';
            statusElement.className = '';
        })
        .catch(error => {
            console.error('Backend connection error:', error);
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'error';
        });
}

function loadStatistics() {
    // Get stored statistics
    chrome.storage.local.get(['verificationStats'], function(result) {
        const stats = result.verificationStats || {
            total: 0,
            safe: 0,
            caution: 0,
            harmful: 0
        };
        
        updateStatsDisplay(stats);
    });
}

function updateStatsDisplay(stats) {
    // Update stat numbers
    const safeElement = document.querySelector('.stat-item.safe .stat-number');
    const cautionElement = document.querySelector('.stat-item.caution .stat-number');
    const harmfulElement = document.querySelector('.stat-item.harmful .stat-number');
    
    if (safeElement) safeElement.textContent = stats.safe || 0;
    if (cautionElement) cautionElement.textContent = stats.caution || 0;
    if (harmfulElement) harmfulElement.textContent = stats.harmful || 0;
}

function setupEventListeners() {
    // Clear statistics button
    const clearBtn = document.getElementById('clear-stats');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            chrome.storage.local.set({
                verificationStats: {
                    total: 0,
                    safe: 0,
                    caution: 0,
                    harmful: 0
                }
            }, function() {
                loadStatistics();
                showNotification('Statistics cleared');
            });
        });
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-stats');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadStatistics();
            checkBackendStatus();
            showNotification('Dashboard refreshed');
        });
    }
}

function showNotification(message) {
    // Simple notification display
    console.log('Notification:', message);
    
    // Create a temporary notification element
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #2e7d32;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 1000;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 2 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 2000);
}
