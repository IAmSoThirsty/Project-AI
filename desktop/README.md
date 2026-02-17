# Project AI - Desktop Application

## Overview

Cross-platform desktop application for **Project AI Governance Kernel** built with Electron, React, TypeScript, and Material-UI.

## Features

✅ **Native Desktop Application**

- Windows, macOS, Linux support
- Custom window controls
- System tray integration
- Persistent settings

✅ **Triumvirate Dashboard**

- Real-time kernel status
- Pillar health monitoring
- Recent decisions

✅ **Intent Submission**

- Interactive form
- Real-time governance evaluation
- Detailed verdict display

✅ **Audit Log Viewer**

- Complete decision history
- Cryptographic tracking

✅ **TARL Rules Explorer**

- Policy visualization
- Risk indicators

## Tech Stack

- **Framework**: Electron 28
- **UI**: React 18 + TypeScript
- **Components**: Material-UI (MUI) 5
- **Build**: Vite + electron-builder
- **API Client**: Axios

## Prerequisites

- Node.js 18+ and npm
- Governance Kernel running at `localhost:8001`

## Installation

```bash
cd desktop
npm install
```

## Development

### Start Dev Server

```bash
npm run dev
```

This starts:

1. Vite dev server (React hot reload)
2. Electron app

### Backend Connection

Ensure the Governance Kernel is running:
```bash
cd ..
python start_api.py
```

## Building

### Build for Current Platform

```bash
npm run build       # Compile TypeScript + React
npm run package     # Create distributable
```

### Build for Specific Platform

```bash
npm run build:win     # Windows installer (.exe)
npm run build:mac     # macOS DMG
npm run build:linux   # Linux AppImage
```

Output in `release/` folder.

## Project Structure

```
desktop/
├── electron/
│   ├── main.ts          # Electron main process
│   └── preload.ts       # IPC bridge
├── src/
│   ├── api/
│   │   └── governance.ts    # API client
│   ├── components/
│   │   ├── TitleBar.tsx     # Custom title bar
│   └── Sidebar.tsx      # Navigation
│   ├── pages/
│   │   ├── Dashboard.tsx    # Dashboard screen
│   │   ├── Intent.tsx       # Intent submission
│   │   ├── Audit.tsx        # Audit log
│   │   └── Tarl.tsx         # TARL rules
│   ├── types/
│   │   └── electron.d.ts    # TypeScript types
│   ├── App.tsx          # Main app component
│   └── main.tsx         # React entry
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript config
└── package.json         # Dependencies
```

## Features in Detail

### Custom Title Bar

- Minimize, maximize, close controls
- Drag to move window
- Platform-native feel

### Sidebar Navigation

- Dashboard
- Submit Intent
- Audit Log
- TARL Rules

### API Integration

All endpoints:

- `GET /health` - Kernel status
- `GET /tarl` - Governance rules
- `GET /audit` - Audit history
- `POST /intent` - Submit for evaluation

### Persistent Settings

Uses `electron-store` for:

- Window size/position
- User preferences

## Security

- Context isolation enabled
- Node integration disabled
- Secure IPC communication
- TARL enforcement on all requests

## Distribution

Built apps include:

- **Windows**: NSIS installer (.exe)
- **macOS**: DMG image
- **Linux**: AppImage

## Troubleshooting

### Cannot connect to backend

- Verify API running at `localhost:8001`
- Check firewall settings

### Build fails

```bash
npm clean
npm install
npm run build
```

## License

MIT - See main project LICENSE

---

**Production-ready cross-platform desktop governance client.**
