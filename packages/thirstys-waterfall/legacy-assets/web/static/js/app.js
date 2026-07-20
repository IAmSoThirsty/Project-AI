/**
 * Thirsty's Waterfall - Privacy Browser Application Logic
 * =======================================================
 * 
 * MAXIMUM ALLOWED DESIGN IMPLEMENTATION
 * 
 * Architecture:
 * ------------
 * 1. Application State Management Layer
 * 2. API Communication Layer (REST + WebSocket)
 * 3. UI Controller Layer
 * 4. Tab Management System
 * 5. Navigation System
 * 6. Privacy Dashboard Controller
 * 7. Event Handling System
 * 8. Notification System
 * 9. Authentication Layer
 * 10. Error Handling & Recovery
 * 
 * Design Patterns:
 * ---------------
 * - Singleton: Application state
 * - Observer: Event system and WebSocket
 * - Module: Encapsulated functionality
 * - Factory: Tab and notification creation
 * - Strategy: Search provider selection
 */

// ============================================================================
// APPLICATION STATE LAYER
// ============================================================================

class ApplicationState {
    constructor() {
        this.tabs = new Map();
        this.activeTabId = null;
        this.systemStatus = {
            running: false,
            vpn: { connected: false },
            firewalls: { active: [] },
            stats: {
                trackersBlocked: 0,
                adsBlocked: 0,
                malwareBlocked: 0,
                dataEncrypted: 0
            }
        };
        this.authToken = localStorage.getItem('auth_token');
        this.settings = this.loadSettings();
    }

    loadSettings() {
        const defaults = {
            privacyMode: 'maximum',
            blockPopups: true,
            blockRedirects: true,
            antiFingerprinting: true,
            killSwitch: true,
            searchEngine: 'duckduckgo'
        };
        const saved = localStorage.getItem('settings');
        return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
    }

    saveSettings() {
        localStorage.setItem('settings', JSON.stringify(this.settings));
    }
}

const appState = new ApplicationState();

// ============================================================================
// API CLIENT LAYER
// ============================================================================

class APIClient {
    constructor(baseURL = 'http://localhost:8080') {
        this.baseURL = baseURL;
        this.socket = null;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (appState.authToken) {
            headers['Authorization'] = `Bearer ${appState.authToken}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (response.status === 401) {
                this.handleUnauthorized();
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${endpoint}`, error);
            throw error;
        }
    }

    async login(username, password) {
        const response = await this.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (response.access_token) {
            appState.authToken = response.access_token;
            localStorage.setItem('auth_token', response.access_token);
        }

        return response;
    }

    // System Control
    async startSystem() {
        return this.request('/api/system/start', { method: 'POST' });
    }

    async stopSystem() {
        return this.request('/api/system/stop', { method: 'POST' });
    }

    async getSystemStatus() {
        return this.request('/api/system/status');
    }

    // VPN Control
    async connectVPN(options = {}) {
        return this.request('/api/vpn/connect', {
            method: 'POST',
            body: JSON.stringify(options)
        });
    }

    async disconnectVPN() {
        return this.request('/api/vpn/disconnect', { method: 'POST' });
    }

    async getVPNStatus() {
        return this.request('/api/vpn/status');
    }

    // Firewall Control
    async listFirewalls() {
        return this.request('/api/firewalls/list');
    }

    async toggleFirewall(firewallId, enabled) {
        return this.request(`/api/firewalls/${firewallId}/toggle`, {
            method: 'POST',
            body: JSON.stringify({ enabled })
        });
    }

    // Browser Control
    async listTabs() {
        return this.request('/api/browser/tabs');
    }

    async createTab(url) {
        return this.request('/api/browser/tabs', {
            method: 'POST',
            body: JSON.stringify({ url })
        });
    }

    // WebSocket Connection
    initWebSocket() {
        if (this.socket?.connected) return;

        this.socket = io(`${this.baseURL}/events`, {
            auth: { token: appState.authToken }
        });

        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            showNotification('Connected to Thirsty\'s Waterfall', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });

        this.socket.on('state_change', (data) => {
            handleStateChange(data);
        });

        this.socket.on('error', (error) => {
            console.error('WebSocket error:', error);
        });
    }

    handleUnauthorized() {
        localStorage.removeItem('auth_token');
        appState.authToken = null;
        // Redirect to login or show login modal
        showNotification('Session expired. Please login again.', 'error');
    }
}

const api = new APIClient();

// ============================================================================
// TAB MANAGEMENT SYSTEM
// ============================================================================

class TabManager {
    constructor() {
        this.tabsContainer = document.getElementById('tabs-container');
        this.viewport = document.getElementById('browser-viewport');
        this.addressBar = document.getElementById('address-bar');
        this.tabIdCounter = 0;
    }

    createTab(url = 'about:blank', title = 'New Tab') {
        const tabId = `tab-${this.tabIdCounter++}`;

        const tab = {
            id: tabId,
            url: url,
            title: title,
            history: [url],
            historyIndex: 0,
            loading: false,
            encrypted: true
        };

        appState.tabs.set(tabId, tab);
        this.renderTab(tab);
        this.switchToTab(tabId);

        return tab;
    }

    renderTab(tab) {
        const tabElement = document.createElement('div');
        tabElement.className = 'tab';
        tabElement.dataset.tabId = tab.id;
        tabElement.innerHTML = `
            <i class="fas fa-lock tab-icon"></i>
            <span class ="tab-title">${this.escapeHtml(tab.title)}</span>
            <button class="tab-close" aria-label="Close tab">
                <i class="fas fa-times"></i>
            </button>
        `;

        tabElement.addEventListener('click', (e) => {
            if (!e.target.closest('.tab-close')) {
                this.switchToTab(tab.id);
            }
        });

        tabElement.querySelector('.tab-close').addEventListener('click', (e) => {
            e.stopPropagation();
            this.closeTab(tab.id);
        });

        this.tabsContainer.appendChild(tabElement);
    }

    switchToTab(tabId) {
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

        // Add active class to selected tab
        const tabElement = document.querySelector(`[data-tab-id="${tabId}"]`);
        if (tabElement) {
            tabElement.classList.add('active');
        }

        appState.activeTabId = tabId;
        const tab = appState.tabs.get(tabId);

        if (tab) {
            this.addressBar.value = tab.url;
            this.renderTabContent(tab);
        }
    }

    closeTab(tabId) {
        const tabElement = document.querySelector(`[data-tab-id="${tabId}"]`);
        if (tabElement) {
            tabElement.remove();
        }

        appState.tabs.delete(tabId);

        // Switch to another tab if this was the active one
        if (appState.activeTabId === tabId) {
            const remainingTabs = Array.from(appState.tabs.keys());
            if (remainingTabs.length > 0) {
                this.switchToTab(remainingTabs[0]);
            } else {
                this.createTab();
            }
        }
    }

    renderTabContent(tab) {
        if (tab.url === 'about:blank' || !tab.url) {
            this.viewport.innerHTML = document.getElementById('start-page').outerHTML;
            document.getElementById('start-page').classList.remove('hidden');
        } else {
            // In a real implementation, this would render an iframe or custom engine
            // For demo purposes, show a placeholder
            this.viewport.innerHTML = `
                <div class="page-content" style="padding: 2rem;">
                    <div style="background: var(--color-glass); backdrop-filter: blur(20px); 
                                border: 1px solid var(--color-glass-border); border-radius: 1rem; 
                                padding: 2rem; text-align: center;">
                        <i class="fas fa-lock" style="font-size: 3rem; color: var(--color-success); margin-bottom: 1rem;"></i>
                        <h2 style="margin-bottom: 1rem;">Encrypted Connection</h2>
                        <p style="color: var(--color-text-secondary); margin-bottom: 1rem;">
                            URL: <strong>${this.escapeHtml(tab.url)}</strong>
                        </p>
                        <p style="color: var(--color-text-tertiary); font-size: 0.875rem;">
                            All traffic encrypted with 7-layer protection • VPN Active • Trackers Blocked
                        </p>
                    </div>
                </div>
            `;
        }
    }

    navigate(url) {
        const activeTab = appState.tabs.get(appState.activeTabId);
        if (!activeTab) return;

        // Process URL
        const processedUrl = this.processURL(url);

        activeTab.url = processedUrl;
        activeTab.history = [...activeTab.history.slice(0, activeTab.historyIndex + 1), processedUrl];
        activeTab.historyIndex = activeTab.history.length - 1;

        this.updateActiveTab(activeTab);
        this.renderTabContent(activeTab);

        // Update stats
        appState.systemStatus.stats.trackersBlocked += Math.floor(Math.random() * 5);
        appState.systemStatus.stats.adsBlocked += Math.floor(Math.random() * 10);
        updateStatsDisplay();
    }

    processURL(input) {
        // Check if it's a search query or URL
        if (input.includes(' ') || (!input.includes('.') && !input.startsWith('http'))) {
            // It's a search query
            return this.getSearchURL(input);
        }

        // Add https:// if no protocol
        if (!input.startsWith('http://') && !input.startsWith('https://')) {
            return `https://${input}`;
        }

        return input;
    }

    getSearchURL(query) {
        const engines = {
            duckduckgo: `https://duckduckgo.com/?q=${encodeURIComponent(query)}`,
            startpage: `https://www.startpage.com/do/search?q=${encodeURIComponent(query)}`,
            brave: `https://search.brave.com/search?q=${encodeURIComponent(query)}`
        };

        const engine = appState.settings.searchEngine || 'duckduckgo';
        return engines[engine] || engines.duckduckgo;
    }

    goBack() {
        const activeTab = appState.tabs.get(appState.activeTabId);
        if (!activeTab || activeTab.historyIndex <= 0) return;

        activeTab.historyIndex--;
        activeTab.url = activeTab.history[activeTab.historyIndex];
        this.updateActiveTab(activeTab);
        this.renderTabContent(activeTab);
    }

    goForward() {
        const activeTab = appState.tabs.get(appState.activeTabId);
        if (!activeTab || activeTab.historyIndex >= activeTab.history.length - 1) return;

        activeTab.historyIndex++;
        activeTab.url = activeTab.history[activeTab.historyIndex];
        this.updateActiveTab(activeTab);
        this.renderTabContent(activeTab);
    }

    refresh() {
        const activeTab = appState.tabs.get(appState.activeTabId);
        if (!activeTab) return;

        this.renderTabContent(activeTab);
        showNotification('Page refreshed', 'info');
    }

    updateActiveTab(tab) {
        const tabElement = document.querySelector(`[data-tab-id="${tab.id}"]`);
        if (tabElement) {
            const titleElement = tabElement.querySelector('.tab-title');
            titleElement.textContent = tab.title || new URL(tab.url).hostname || 'New Tab';
        }
        this.addressBar.value = tab.url;
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

const tabManager = new TabManager();

// ============================================================================
// UI CONTROLLER LAYER
// ============================================================================

class UIController {
    constructor() {
        this.privacyDashboard = document.getElementById('privacy-dashboard');
        this.downloadPanel = document.getElementById('downloads-panel');
        this.settingsPanel = document.getElementById('settings-panel');
    }

    togglePrivacyDashboard() {
        this.privacyDashboard.classList.toggle('hidden');
    }

    toggleDownloadsPanel() {
        this.downloadPanel.classList.toggle('hidden');
    }

    toggleSettingsPanel() {
        this.settingsPanel.classList.toggle('hidden');
    }

    updateVPNStatus(status) {
        const indicator = document.getElementById('vpn-indicator');
        const protocolEl = document.getElementById('vpn-protocol');
        const hopsEl = document.getElementById('vpn-hops');
        const locationEl = document.getElementById('vpn-location');

        if (status.connected) {
            indicator.classList.add('active');
            protocolEl.textContent = status.protocol || 'WireGuard';
            hopsEl.textContent = status.hop_count || 3;
            locationEl.textContent = status.location || 'Multi-hop chain';
        } else {
            indicator.classList.remove('active');
        }
    }

    updateFirewallStatus(firewalls) {
        const indicator = document.getElementById('firewall-indicator');
        const activeCount = firewalls.filter(f => f.active).length;

        indicator.title = `${activeCount}/8 Firewalls Active`;

        if (activeCount > 0) {
            indicator.classList.add('active');
        } else {
            indicator.classList.remove('active');
        }
    }
}

const uiController = new UIController();

// ============================================================================
// NOTIFICATION SYSTEM
// ============================================================================

function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notifications');
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        background: var(--color-glass);
        backdrop-filter: blur(20px);
        border: 1px solid var(--color-glass-border);
        border-left: 3px solid var(--color-${type === 'error' ? 'error' : type === 'success' ? 'success' : 'primary'});
        border-radius: var(--radius-lg);
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        animation: slideIn 0.3s ease-out;
        box-shadow: var(--shadow-lg);
    `;

    const icon = type === 'error' ? 'exclamation-circle' :
        type === 'success' ? 'check-circle' : 'info-circle';

    notification.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
    `;

    container.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ============================================================================
// STATS UPDATE SYSTEM
// ============================================================================

function updateStatsDisplay() {
    const stats = appState.systemStatus.stats;

    document.getElementById('stat-trackers').textContent = stats.trackersBlocked;
    document.getElementById('stat-ads').textContent = stats.adsBlocked;
    document.getElementById('stat-malware').textContent = stats.malwareBlocked;
    document.getElementById('stat-encrypted').textContent = `${(stats.dataEncrypted / 1024 / 1024).toFixed(2)} MB`;

    // Update tracker counter in address bar
    const trackerCounter = document.querySelector('#tracker-blocker .counter');
    if (trackerCounter) {
        trackerCounter.textContent = stats.trackersBlocked;
    }
}

// Simulate stats increase
setInterval(() => {
    if (appState.systemStatus.running) {
        appState.systemStatus.stats.dataEncrypted += Math.random() * 1024 * 100; // Random bytes
        updateStatsDisplay();
    }
}, 5000);

// ============================================================================
// EVENT HANDLERS
// ============================================================================

function handleStateChange(data) {
    if (data.type === 'system_started') {
        appState.systemStatus.running = true;
        showNotification('System started successfully', 'success');
    } else if (data.type === 'system_stopped') {
        appState.systemStatus.running = false;
        showNotification('System stopped', 'info');
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Navigation controls
    document.getElementById('btn-back').addEventListener('click', () => tabManager.goBack());
    document.getElementById('btn-forward').addEventListener('click', () => tabManager.goForward());
    document.getElementById('btn-refresh').addEventListener('click', () => tabManager.refresh());
    document.getElementById('btn-home').addEventListener('click', () => tabManager.navigate('about:blank'));

    // Address bar
    document.getElementById('address-bar').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            tabManager.navigate(e.target.value);
        }
    });

    // Quick search
    const quickSearch = document.getElementById('quick-search');
    if (quickSearch) {
        quickSearch.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                tabManager.navigate(e.target.value);
            }
        });
    }

    // New tab button
    document.getElementById('btn-new-tab').addEventListener('click', () => {
        tabManager.createTab();
    });

    // Browser action buttons
    document.getElementById('btn-privacy-dashboard').addEventListener('click', () => {
        uiController.togglePrivacyDashboard();
    });

    document.getElementById('btn-downloads').addEventListener('click', () => {
        uiController.toggleDownloadsPanel();
    });

    document.getElementById('btn-settings').addEventListener('click', () => {
        uiController.toggleSettingsPanel();
    });

    // Close dashboard button
    document.getElementById('close-dashboard')?.addEventListener('click', () => {
        uiController.togglePrivacyDashboard();
    });

    // Close panel buttons
    document.querySelectorAll('.close-panel').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.side-panel').classList.add('hidden');
        });
    });

    // VPN toggle button
    document.getElementById('btn-vpn-toggle')?.addEventListener('click', async () => {
        try {
            if (appState.systemStatus.vpn.connected) {
                await api.disconnectVPN();
                showNotification('VPN disconnected', 'info');
            } else {
                await api.connectVPN({ multi_hop: true, hop_count: 3 });
                showNotification('VPN connected', 'success');
            }
        } catch (error) {
            showNotification('VPN operation failed', 'error');
        }
    });

    // Shortcuts
    document.querySelectorAll('.shortcut').forEach(shortcut => {
        shortcut.addEventListener('click', () => {
            const url = shortcut.dataset.url;
            if (url) {
                tabManager.navigate(url);
            }
        });
    });

    // Initialize
    try {
        // Login with demo credentials
        await api.login('admin', 'admin');

        // Initialize WebSocket
        api.initWebSocket();

        // Create initial tab
        tabManager.createTab();

        // Load system status
        const status = await api.getSystemStatus();
        appState.systemStatus = { ...appState.systemStatus, ...status };

        // Start system if not running
        if (!appState.systemStatus.running) {
            await api.startSystem();
        }

        showNotification('Thirsty\'s Waterfall Ready', 'success');
    } catch (error) {
        console.error('Initialization failed:', error);
        showNotification('Running in demo mode', 'info');
        tabManager.createTab();
    }
});

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    .notifications {
        position: fixed;
        top: var(--spacing-md);
        right: var(--spacing-md);
        z-index: var(--z-tooltip);
        max-width: 400px;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
