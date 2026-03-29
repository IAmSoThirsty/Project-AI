/**
 * ============================================================================
 * STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-11 | TIME: 21:35
 * COMPLIANCE: Sovereign-Native / T.A.R.L. v1.0
 * ============================================================================
 * Sovereign Preload Bridge
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('sovereign', {
    sendEvent: (event, data) => {
        // Governance: Whitelist channels
        const validChannels = ['sovereign-event'];
        if (validChannels.includes(event)) {
            ipcRenderer.send(event, data);
        }
    },
    receive: (channel, func) => {
        const validChannels = ['from-main'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    }
});
