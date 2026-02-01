# Legion Mini Portable - USB Drive Edition
# Complete portable installation script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Legion Mini Portable - USB Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get USB drive letter
$usbDrive = Read-Host "Enter USB drive letter (e.g., E:)"
if (-not $usbDrive.EndsWith(":")) {
    $usbDrive = $usbDrive + ":"
}

$portableRoot = "$usbDrive\LegionMini"

Write-Host "[1/6] Creating portable directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$portableRoot\backend" -Force | Out-Null
New-Item -ItemType Directory -Path "$portableRoot\android" -Force | Out-Null
New-Item -ItemType Directory -Path "$portableRoot\data" -Force | Out-Null
New-Item -ItemType Directory -Path "$portableRoot\config" -Force | Out-Null
New-Item -ItemType Directory -Path "$portableRoot\python" -Force | Out-Null
Write-Host "✓ Directory structure created" -ForegroundColor Green

Write-Host ""
Write-Host "[2/6] Copying Python portable distribution..." -ForegroundColor Yellow
# Download portable Python if not exists
$pythonZip = "$env:TEMP\python-3.11-portable.zip"
if (-not (Test-Path "$portableRoot\python\python.exe")) {
    Write-Host "  Downloading Python 3.11 portable..." -ForegroundColor Cyan
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip"
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip -UseBasicParsing
    Expand-Archive -Path $pythonZip -DestinationPath "$portableRoot\python" -Force
    Remove-Item $pythonZip
    Write-Host "✓ Python portable installed" -ForegroundColor Green
}
else {
    Write-Host "✓ Python already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/6] Copying Project-AI backend..." -ForegroundColor Yellow
# Copy essential backend files
$backendFiles = @(
    "project_ai",
    "api",
    "integrations",
    "requirements.txt",
    "start_api.py"
)

foreach ($item in $backendFiles) {
    $source = ".\$item"
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination "$portableRoot\backend\" -Recurse -Force
    }
}
Write-Host "✓ Backend files copied" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] Copying Android APK..." -ForegroundColor Yellow
$apkPath = "android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk"
if (Test-Path $apkPath) {
    Copy-Item -Path $apkPath -Destination "$portableRoot\android\legion-mini.apk" -Force
    Write-Host "✓ APK copied" -ForegroundColor Green
}
else {
    Write-Host "⚠ APK not found - build it first with: ./gradlew :legion_mini:assembleDebug" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/6] Creating launcher scripts..." -ForegroundColor Yellow

# Create start script
$startScript = @"
@echo off
title Legion Mini - Portable
echo ========================================
echo Legion Mini Portable Edition
echo ========================================
echo.
echo [*] Starting Legion Backend...
cd /d "%~dp0backend"
..\python\python.exe start_api.py
pause
"@

Set-Content -Path "$portableRoot\START_LEGION.bat" -Value $startScript

# Create install APK script  
$installApk = @"
@echo off
title Install Legion Mini APK
echo ========================================
echo Legion Mini - Install Android APK
echo ========================================
echo.
echo Make sure USB Debugging is enabled on your Android device
echo and it's connected via USB.
echo.
pause
adb install -r android\legion-mini.apk
pause
"@

Set-Content -Path "$portableRoot\INSTALL_ANDROID.bat" -Value $installApk

# Create README
$readme = @"
# Legion Mini Portable Edition

## What's Included

- **Backend**: Complete Project-AI backend with Legion integration
- **Android APK**: Legion Mini mobile app
- **Python**: Portable Python 3.11 runtime
- **Data**: Local storage for conversations and saves

## Quick Start

### Desktop Usage
1. Double-click `START_LEGION.bat`
2. Wait for "Uvicorn running on http://0.0.0.0:8001"
3. Open browser to http://localhost:8001/docs

### Android Installation
1. Enable USB Debugging on your Android device
2. Connect device via USB
3. Double-click `INSTALL_ANDROID.bat`
4. Launch Legion Mini app on your device

### Portable Usage
- Plug USB drive into any Windows PC
- Run START_LEGION.bat
- No installation required!
- All data stays on USB drive

## System Requirements

- Windows 10/11 (64-bit)
- 2GB free space on USB drive
- Android 8.0+ for mobile app

## Features

- ✓ Fully portable - no installation
- ✓ Self-contained Python environment
- ✓ Local data storage
- ✓ Auto-save system (15-min intervals)
- ✓ Works offline (when models are local)

## File Structure

```
LegionMini/
├── START_LEGION.bat       # Start backend server
├── INSTALL_ANDROID.bat    # Install Android APK
├── backend/               # Project-AI backend
├── android/               # Android APK
├── python/                # Portable Python
├── data/                  # User data & saves
└── config/                # Configuration files
```

## API Endpoints

Once started, available at http://localhost:8001:

- `/docs` - API documentation
- `/api/savepoints/create` - Create save point
- `/api/savepoints/list` - List saves
- `/chat` - Chat with AI

## Notes

- First run may take a minute to initialize
- Data persists on USB drive between sessions
- Can run on any Windows PC - just plug in and go!
- Legion API runs on port 8002
- Project-AI API runs on port 8001

## Troubleshooting

**"Python not found"**
- Re-run setup script to download Python

**"Port already in use"**
- Close other instances of Legion
- Change port in start_api.py

**APK won't install**
- Enable "Install from Unknown Sources"
- Check USB Debugging is enabled
- Try: `adb devices` to verify connection

---

For support: https://github.com/IAmSoThirsty/Project-AI
"@

Set-Content -Path "$portableRoot\README.md" -Value $readme

Write-Host "✓ Launcher scripts created" -ForegroundColor Green

Write-Host ""
Write-Host "[6/6] Creating portable configuration..." -ForegroundColor Yellow

$config = @"
{
    "portable": true,
    "data_dir": "./data",
    "api_host": "0.0.0.0",
    "api_port": 8001,
    "legion_port": 8002,
    "auto_save_interval": 15
}
"@

Set-Content -Path "$portableRoot\config\portable-config.json" -Value $config
Write-Host "✓ Configuration created" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Portable Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Location: $portableRoot" -ForegroundColor Cyan
Write-Host ""
Write-Host "To use:" -ForegroundColor Yellow
Write-Host "  1. Safely eject USB drive" -ForegroundColor White
Write-Host "  2. Plug into any Windows PC" -ForegroundColor White
Write-Host "  3. Run START_LEGION.bat" -ForegroundColor White
Write-Host ""
Write-Host "Your portable AI assistant is ready!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
