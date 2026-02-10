# Project-AI Production Deployment Guide

## 🚀 Complete Deployment Package

This guide covers deploying Project-AI and Legion Mini to all platforms for production use.

## Quick Start

### Option 1: Automated Build (Recommended)

```powershell
# Build everything
.\scripts\build_production.ps1 -All

# Or build specific platforms
.\scripts\build_production.ps1 -Desktop
.\scripts\build_production.ps1 -Android
```

### Option 2: Manual Build

#### Desktop Application

```powershell
cd desktop
npm install
npm run build:win
```

#### Android APK

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
.\gradlew.bat :legion_mini:assembleDebug
.\gradlew.bat :legion_mini:assembleRelease
```

#### Portable USB Package

```powershell
.\scripts\create_portable_usb.ps1
```

---

## Installation

### Desktop (Windows)

**Standard Installation:**

1. Run: `.\scripts\install_desktop.ps1`
1. Or manually: Run `desktop\release\Project AI Setup.exe`
1. Launch from Start Menu

**Features:**

- Auto-updates
- System-wide installation
- Start menu integration

### Android (Legion Mini)

**Direct Install (ADB):**

```bash
adb install -r android/legion_mini/build/outputs/apk/debug/legion_mini-debug.apk
```

**Sideload Install:**

1. Enable "Unknown Sources" on Android device
1. Transfer APK to device
1. Open APK file and install
1. Launch Legion Mini

**Features:**

- Native Android app
- Works offline (when models local)
- Material Design 3 UI
- WebView-based interface

### Portable USB

**Setup:**

1. Run: `.\scripts\create_portable_usb.ps1`
1. Enter USB drive letter (e.g., `E:`)
1. Wait for completion

**Usage:**

1. Plug USB into ANY Windows PC
1. Run: `E:\LegionMini\START_LEGION.bat`
1. Access at: <http://localhost:8001>

**Features:**

- Fully portable - no installation
- Self-contained Python runtime
- Persistent data on USB
- Run on any Windows PC

---

## System Architecture

### Components

```
Project-AI/
├── Backend API (Python/FastAPI)
│   ├── Port 8001
│   ├── Save points system
│   └── Core AI services
│
├── Legion API (Python/FastAPI)
│   ├── Port 8002
│   ├── Triumvirate governance
│   └── Single-gate architecture
│
├── Desktop App (Electron)
│   ├── Windows installer
│   └── Auto-updater
│
├── Android App (Kotlin/Compose)
│   ├── Legion Mini
│   ├── WebView interface
│   └── Native Android UI
│
└── Portable Package
    ├── Python 3.11 embedded
    ├── All dependencies
    └── Data storage
```

### Save Points System

**Auto-Save:**

- Runs every 15 minutes
- Keeps last 3 auto-saves
- Automatic rotation

**User Saves:**

- Manual save points
- Named and timestamped
- Unlimited storage

**API Endpoints:**

- `POST /api/savepoints/create` - Create save
- `GET /api/savepoints/list` - List saves
- `POST /api/savepoints/restore/{id}` - Restore
- `GET /api/savepoints/auto/status` - Auto-save status

---

## Testing

### End-to-End Tests

```powershell
.\scripts\run_e2e_tests.ps1
```

Tests:

- ✓ Python unit tests
- ✓ Save points system
- ✓ Legion API
- ✓ Android configuration
- ✓ Desktop configuration  
- ✓ Gradle build system

### Manual Testing Checklist

**5-Hour Continuous Operation Test:**

1. Start backend: `python start_api.py`
1. Start Legion: `python integrations/openclaw/legion_api.py`
1. Open desktop app or Legion Mini
1. Engage in conversation
1. Monitor for 5+ hours:
   - Check auto-saves created every 15 min
   - Verify responses remain consistent
   - Test manual save/restore
   - Monitor memory usage
   - Check error logs

**Expected Behavior:**

- No crashes or freezes
- Memory stable (< 2GB)
- Auto-saves rotate correctly
- All API endpoints responsive
- Conversation history persists

---

## Production Deployment

### Environment Setup

**Required:**

- Python 3.11+
- Node.js 18+
- Java JDK 17
- Android SDK (for mobile builds)

**Configuration:**

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Set API keys, ports, etc.
```

### Running in Production

**Backend (Linux/Windows Server):**

```bash
# Using systemd (Linux)
sudo systemctl start project-ai
sudo systemctl start legion-api

# Using PM2 (Cross-platform)
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

**Desktop:**

- Users install via provided installer
- Auto-updates handled automatically

**Mobile:**

- Distribute APK directly (sideload)
- Or submit to Google Play Store ($25 one-time fee)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Run `.\scripts\run_e2e_tests.ps1`
- [ ] Verify all tests pass
- [ ] Check save points system functional
- [ ] Test 5-hour continuous operation
- [ ] Review error logs

### Build

- [ ] Build desktop: `.\scripts\build_production.ps1 -Desktop`
- [ ] Build Android: `.\scripts\build_production.ps1 -Android`
- [ ] Create portable: `.\scripts\create_portable_usb.ps1`
- [ ] Verify all builds successful

### Post-Deployment

- [ ] Test desktop installation
- [  ] Test Android sideload
- [ ] Test portable USB on different PC
- [ ] Verify save/restore functionality
- [ ] Monitor for 24 hours

---

## File Locations

### Built Artifacts

**Desktop:**

- `desktop/release/Project AI Setup.exe`

**Android:**

- `android/legion_mini/build/outputs/apk/debug/legion_mini-debug.apk`
- `android/legion_mini/build/outputs/apk/release/legion_mini-release.apk`

**Portable:**

- `E:\LegionMini\` (or your USB drive)

### Logs

- Backend: `logs/api.log`
- Legion: `logs/legion.log`
- Desktop: `%APPDATA%/Project AI/logs/`
- Android: `logcat` (via `adb logcat`)

---

## Troubleshooting

### Backend Won't Start

- Check Python version: `python --version` (need 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check port availability: `netstat -ano | findstr :8001`

### Android APK Won't Build

- Verify Java: `java -version` (need JDK 17)
- Set JAVA_HOME: See installation guide
- Clean build: `.\gradlew.bat clean :legion_mini:assembleDebug`

### Desktop App Won't Install

- Check Node.js: `node --version` (need 18+)
- Rebuild: `cd desktop && npm run build:win`
- Run as Administrator

### Portable USB Not Working

- Verify Python downloaded: Check `LegionMini\python\python.exe`
- Re-run setup: `.\scripts\create_portable_usb.ps1`
- Check USB drive has 2GB+ free space

---

## Support & Documentation

- GitHub: <https://github.com/IAmSoThirsty/Project-AI>
- API Docs: <http://localhost:8001/docs> (when running)
- Legion Docs: <http://localhost:8002/docs> (when running)

---

## Security Notes

- All data stored locally
- No cloud sync unless configured
- Triumvirate governance on all Legion requests
- TARL enforcement active
- No backdoors or bypass mechanisms

---

**Ready for global deployment! 🌍**
