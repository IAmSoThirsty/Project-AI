// (Substrate Interface Bridge)              [2026-04-09 04:12]
//                                          Status: Active
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
