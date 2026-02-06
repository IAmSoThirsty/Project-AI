// Thirst of Gods - Live Dashboard JavaScript

class ThirstyDashboard {
    constructor() {
        this.ws = null;
        this.startTime = Date.now();
        this.metrics = {
            totalCommands: 0,
            threatsDetected: 0,
            activeDeceptions: 0,
            bubblegumTriggers: 0,
            layers: { 0: 0, 1: 0, 2: 0 },
            attackTypes: {},
            performance: {
                avgDetectionTime: 0,
                avgTransitionTime: 0,
                memoryUsage: 0,
                cpuUsage: 0
            },
            learning: {
                patternsLearned: 0,
                activePlaybooks: 0,
                evolutionCycles: 0,
                detectionAccuracy: 95.8
            }
        };

        this.threatHistory = [];
        this.attackTypeChart = null;

        this.init();
    }

    init() {
        this.initializeHeatmap();
        this.initializeChart();
        this.startUptimeCounter();
        this.connectWebSocket();
        this.startSimulation(); // Demo mode
    }

    connectWebSocket() {
        // Try to connect to backend (graceful degradation if not available)
        try {
            this.ws = new WebSocket('ws://localhost:8765');

            this.ws.onopen = () => {
                this.addActivity('info', 'WebSocket connected - Receiving live data');
                document.getElementById('systemStatus').classList.add('active');
            };

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.updateFromWebSocket(data);
            };

            this.ws.onerror = () => {
                this.addActivity('warning', 'WebSocket unavailable - Running in demo mode');
            };

            this.ws.onclose = () => {
                this.addActivity('warning', 'WebSocket disconnected - Attempting reconnect...');
                setTimeout(() => this.connectWebSocket(), 5000);
            };
        } catch (e) {
            console.log('WebSocket not available, running demo mode');
            this.addActivity('info', 'Demo mode - Simulated data');
        }
    }

    updateFromWebSocket(data) {
        if (data.type === 'metrics') {
            this.updateMetrics(data.payload);
        } else if (data.type === 'threat') {
            this.handleThreat(data.payload);
        } else if (data.type === 'activity') {
            this.addActivity(data.level, data.message);
        }
    }

    updateMetrics(data) {
        this.metrics = { ...this.metrics, ...data };
        this.refreshUI();
    }

    handleThreat(threat) {
        this.threatHistory.push({
            timestamp: Date.now(),
            level: threat.level,
            type: threat.type
        });

        // Keep last 60 seconds
        const cutoff = Date.now() - 60000;
        this.threatHistory = this.threatHistory.filter(t => t.timestamp > cutoff);

        this.addActivity(
            threat.level === 'critical' ? 'danger' : 'warning',
            `Threat detected: ${threat.type} (${threat.confidence}% confidence)`
        );

        this.updateHeatmap();
    }

    startUptimeCounter() {
        setInterval(() => {
            const uptime = Date.now() - this.startTime;
            const hours = Math.floor(uptime / 3600000);
            const minutes = Math.floor((uptime % 3600000) / 60000);
            const seconds = Math.floor((uptime % 60000) / 1000);

            document.getElementById('uptime').textContent =
                `Uptime: ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }, 1000);
    }

    refreshUI() {
        // Update metric cards
        document.getElementById('totalCommands').textContent = this.metrics.totalCommands;
        document.getElementById('threatsDetected').textContent = this.metrics.threatsDetected;
        document.getElementById('activeDeceptions').textContent = this.metrics.activeDeceptions;
        document.getElementById('bubblegumTriggers').textContent = this.metrics.bubblegumTriggers;

        // Update layer distribution
        const total = this.metrics.layers[0] + this.metrics.layers[1] + this.metrics.layers[2];
        if (total > 0) {
            this.updateLayerBar('layer0Bar', (this.metrics.layers[0] / total) * 100);
            this.updateLayerBar('layer1Bar', (this.metrics.layers[1] / total) * 100);
            this.updateLayerBar('layer2Bar', (this.metrics.layers[2] / total) * 100);
        }

        // Update performance metrics
        document.getElementById('avgDetectionTime').textContent =
            `${this.metrics.performance.avgDetectionTime.toFixed(1)}ms`;
        document.getElementById('avgTransitionTime').textContent =
            `${this.metrics.performance.avgTransitionTime.toFixed(1)}ms`;
        document.getElementById('memoryUsage').textContent =
            `${this.metrics.performance.memoryUsage.toFixed(0)} MB`;
        document.getElementById('cpuUsage').textContent =
            `${this.metrics.performance.cpuUsage.toFixed(1)}%`;

        // Update learning stats
        document.getElementById('patternsLearned').textContent = this.metrics.learning.patternsLearned;
        document.getElementById('activePlaybooks').textContent = this.metrics.learning.activePlaybooks;
        document.getElementById('evolutionCycles').textContent = this.metrics.learning.evolutionCycles;
        document.getElementById('detectionAccuracy').textContent =
            `${this.metrics.learning.detectionAccuracy.toFixed(1)}%`;

        // Update chart
        this.updateChart();
    }

    updateLayerBar(barId, percentage) {
        const bar = document.getElementById(barId);
        const barElement = bar.querySelector('.bar');
        const percentageElement = bar.querySelector('.bar-percentage');

        barElement.style.width = `${percentage}%`;
        percentageElement.textContent = `${percentage.toFixed(0)}%`;
    }

    initializeHeatmap() {
        const heatmap = document.getElementById('threatHeatmap');
        for (let i = 0; i < 60; i++) {
            const cell = document.createElement('div');
            cell.className = 'heatmap-cell';
            cell.dataset.index = i;
            heatmap.appendChild(cell);
        }
    }

    updateHeatmap() {
        const cells = document.querySelectorAll('.heatmap-cell');

        // Get threats in each second of last 60 seconds
        const now = Date.now();
        const threatMap = new Array(60).fill(0);

        this.threatHistory.forEach(threat => {
            const secondsAgo = Math.floor((now - threat.timestamp) / 1000);
            if (secondsAgo < 60) {
                const level = { safe: 1, suspicious: 2, malicious: 3, critical: 4 }[threat.level] || 0;
                threatMap[59 - secondsAgo] = Math.max(threatMap[59 - secondsAgo], level);
            }
        });

        cells.forEach((cell, index) => {
            cell.className = 'heatmap-cell';
            const level = threatMap[index];
            if (level > 0) {
                const classes = ['', 'safe', 'suspicious', 'malicious', 'critical'];
                cell.classList.add(classes[level]);
            }
        });
    }

    initializeChart() {
        const ctx = document.getElementById('attackTypesChart').getContext('2d');

        this.attackTypeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [
                    'Privilege Escalation',
                    'Data Exfiltration',
                    'Reconnaissance',
                    'Credential Access',
                    'Persistence',
                    'Other'
                ],
                datasets: [{
                    data: [0, 0, 0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.8)',
                        'rgba(245, 158, 11, 0.8)',
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(167, 139, 250, 0.8)',
                        'rgba(34, 211, 153, 0.8)',
                        'rgba(156, 163, 175, 0.8)'
                    ],
                    borderColor: 'rgba(20, 24, 36, 0.8)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e8eaf0',
                            font: { size: 11 }
                        }
                    }
                }
            }
        });
    }

    updateChart() {
        const data = [
            this.metrics.attackTypes.privilege_escalation || 0,
            this.metrics.attackTypes.data_exfiltration || 0,
            this.metrics.attackTypes.reconnaissance || 0,
            this.metrics.attackTypes.credential_access || 0,
            this.metrics.attackTypes.persistence || 0,
            this.metrics.attackTypes.other || 0
        ];

        this.attackTypeChart.data.datasets[0].data = data;
        this.attackTypeChart.update();
    }

    addActivity(level, message) {
        const feed = document.getElementById('activityFeed');
        const item = document.createElement('div');

        const time = new Date().toLocaleTimeString();
        const icons = {
            info: 'ℹ️',
            warning: '⚠️',
            danger: '🚨'
        };

        item.className = `activity-item ${level}`;
        item.innerHTML = `
            <span class="activity-time">${time}</span>
            <span class="activity-icon">${icons[level] || 'ℹ️'}</span>
            <span class="activity-text">${message}</span>
        `;

        feed.insertBefore(item, feed.firstChild);

        // Keep only last 50 items
        while (feed.children.length > 50) {
            feed.removeChild(feed.lastChild);
        }
    }

    // Demo simulation (when WebSocket not available)
    startSimulation() {
        setInterval(() => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                this.simulateActivity();
            }
        }, 3000);

        setInterval(() => {
            this.updateHeatmap();
        }, 1000);
    }

    simulateActivity() {
        // Simulate random activity
        if (Math.random() > 0.5) {
            this.metrics.totalCommands++;
            this.metrics.layers[Math.floor(Math.random() * 3)]++;

            if (Math.random() > 0.7) {
                // Simulate threat
                this.metrics.threatsDetected++;
                const threatTypes = ['privilege_escalation', 'data_exfiltration', 'reconnaissance'];
                const threatType = threatTypes[Math.floor(Math.random() * threatTypes.length)];

                this.metrics.attackTypes[threatType] = (this.metrics.attackTypes[threatType] || 0) + 1;

                this.handleThreat({
                    level: Math.random() > 0.8 ? 'critical' : 'malicious',
                    type: threatType,
                    confidence: Math.floor(Math.random() * 30) + 70
                });

                if (Math.random() > 0.9) {
                    this.metrics.activeDeceptions++;
                }

                if (Math.random() > 0.95) {
                    this.metrics.bubblegumTriggers++;
                    this.addActivity('danger', '💥 BUBBLEGUM PROTOCOL ACTIVATED!');
                }
            }

            // Update performance metrics with some variance
            this.metrics.performance.avgDetectionTime = 2.5 + Math.random() * 2;
            this.metrics.performance.avgTransitionTime = 1.8 + Math.random() * 1.5;
            this.metrics.performance.memoryUsage = 45 + Math.random() * 15;
            this.metrics.performance.cpuUsage = 12 + Math.random() * 8;

            // Update learning metrics
            if (Math.random() > 0.9) {
                this.metrics.learning.patternsLearned++;
            }
            if (Math.random() > 0.85) {
                this.metrics.learning.activePlaybooks++;
            }
            if (Math.random() > 0.95) {
                this.metrics.learning.evolutionCycles++;
            }

            this.refreshUI();
        }
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new ThirstyDashboard();
    console.log('🔥 Thirst of Gods Dashboard - ONLINE');
});
