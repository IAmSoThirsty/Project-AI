# Quick Start Guide - Project-AI

## 🚀 60-Second Quick Start

### Step 1: Start the Backend

```bash
python start_api.py
```

Wait for: `Uvicorn running on http://0.0.0.0:8001`

### Step 2: Start Legion API

```bash
python integrations/openclaw/legion_api.py
```

Wait for: `Legion API: http://localhost:8002`

### Step 3: Access Legion Interface

Open browser: <http://localhost:8002> or open `integrations/openclaw/legion_interface.html`

**Done!** Start chatting with Legion.

---

## Installation

### Option 1: Desktop App

```powershell
.\scripts\install_desktop.ps1
```

### Option 2: Android (Legion Mini)

```powershell
# Build APK
.\gradlew.bat :legion_mini:assembleDebug

# Install
adb install -r android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk
```

### Option 3: Portable USB

```powershell
.\scripts\create_portable_usb.ps1
```

---

## System Requirements

- **OS**: Windows 10/11, macOS, Linux
- **Python**: 3.11+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB free space
- **Android**: 8.0+ (for mobile app)

---

## Key Features

### ✓ Save Points System

- Auto-save every 15 minutes
- Rotating 3-slot auto-saves
- Manual user save points
- Full state restoration

### ✓ Legion Integration

- Triumvirate governance (Galahad, Cerberus, CodexDeus)
- Single-gate architecture
- TARL enforcement
- EED memory system

### ✓ Multi-Platform

- Desktop (Electron)
- Android (Legion Mini)
- Portable USB (no installation)
- Web interface

---

## API Endpoints

### Project-AI API (Port 8001)

- `/docs` - Swagger documentation
- `/api/savepoints/create` - Create save point
- `/api/savepoints/list` - List saves
- `/api/savepoints/restore/{id}` - Restore

### Legion API (Port 8002)

- `/chat` - Send message to Legion
- `/status` - Legion system status
- `/health` - Health check

---

## Testing

### Run All Tests

```powershell
.\scripts\run_e2e_tests.ps1
```

### Manual 5-Hour Test

1. Start backend + Legion
1. Engage in conversation
1. Monitor auto-saves (every 15min)
1. Create manual saves
1. Test restore functionality

---

## Troubleshooting

**Backend won't start:**

```bash
pip install -r requirements.txt
python start_api.py
```

**Android build fails:**

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
.\gradlew.bat clean :legion_mini:assembleDebug
```

**Port already in use:**

- Stop other instances
- Or edit ports in config files

---

## Support

- **Docs**: See `DEPLOYMENT_GUIDE.md`
- **GitHub**: <https://github.com/IAmSoThirsty/Project-AI>
- **API Docs**: <http://localhost:8001/docs> (when running)

---

**Ready to use!** 🎉
