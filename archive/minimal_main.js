const { app, BrowserWindow } = require('electron');

app.on('ready', () => {
  const win = new BrowserWindow({ width: 400, height: 300 });
  win.loadURL('data:text/html,<h1>Sovereign Check</h1>');
});
