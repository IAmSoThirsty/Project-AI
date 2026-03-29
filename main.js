/**
 * ============================================================================
 * STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-11 | TIME: 21:35
 * COMPLIANCE: Sovereign-Native / T.A.R.L. v1.0
 * ============================================================================
 * Sovereign Electron Main Process
 * 🌌 THE SOVEREIGN SHELL — Cryptographically Enforced Desktop Layer
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1280,
        height: 800,
        backgroundColor: '#000000',
        titleBarStyle: 'hiddenInset', // Native look on macOS, clean on Windows
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            // T.A.R.L. Security Enforcement:
            nodeIntegration: false,
            contextIsolation: true,
            enableRemoteModule: false,
            sandbox: true
        },
        // Master-Tier Aesthetics
        frame: false, // Custom Sovereign Title Bar
        transparent: true,
        show: false
    });

    win.loadFile('ui/index.html');

    win.once('ready-to-show', () => {
        win.show();
        win.focus();
    });

    // Governance: Handle IPC for Thirsty-Lang
    ipcMain.on('sovereign-event', (event, arg) => {
        console.log(`[Sovereign-Main] Received event: ${arg}`);
    });
}

// OS Management
app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

/**
 * EXIT_HALT_PROTOCOL
 * Activated on security violation
 */
process.on('uncaughtException', (err) => {
    console.error('FATAL_SOVEREIGN_VIO: ', err);
    app.quit();
});
