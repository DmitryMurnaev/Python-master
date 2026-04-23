// app/static/js/app.js
// Main JavaScript for Python Master

// Cookie helper for auth token
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// API request helper
async function apiRequest(url, options = {}) {
    const token = getCookie('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show XP popup notification
function showXpPopup(xp) {
    const popup = document.createElement('div');
    popup.className = 'xp-popup fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    popup.innerHTML = `+${xp} XP`;
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.remove();
    }, 3000);
}

// Show achievement notification
function showAchievement(title, icon) {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-yellow-600 text-white px-6 py-3 rounded-lg shadow-lg z-50';
    notification.innerHTML = `${icon} ${title}`;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Theme toggle
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    html.classList.remove('dark', 'light');
    html.classList.add(newTheme);

    // Save preference
    localStorage.setItem('theme', newTheme);
}

// Load theme on page load
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.classList.add(savedTheme);
}

// Progress bar animation
function animateProgressBars() {
    const bars = document.querySelectorAll('[data-progress]');
    bars.forEach(bar => {
        const value = bar.dataset.progress;
        bar.style.width = `${value}%`;
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    loadTheme();
    animateProgressBars();
});

// Tab navigation
function initTabs() {
    const tabs = document.querySelectorAll('[data-tab]');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.dataset.tab;
            const target = document.getElementById(targetId);

            if (target) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                // Show target tab
                target.classList.remove('hidden');

                // Update active state
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
            }
        });
    });
}

// Run initialization
initTabs();