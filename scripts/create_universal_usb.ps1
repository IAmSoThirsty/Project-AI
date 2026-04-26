# Universal USB Installer - Enhanced Edition
# Creates auto-run USB with Legion Mini AI installation wizard
# Works on: Windows, macOS, Linux, Android (via USB OTG)

param(
    [string]$USBDrive
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Legion Mini Universal USB Installer" -ForegroundColor Cyan
Write-Host "Auto-Run AI Installation Wizard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get USB drive if not specified
if (-not $USBDrive) {
    $USBDrive = Read-Host "Enter USB drive letter (e.g., E:)"
    if (-not $USBDrive.EndsWith(":")) {
        $USBDrive = $USBDrive + ":"
    }
}

$usbRoot = "$USBDrive\"

Write-Host "[1/10] Validating USB drive..." -ForegroundColor Yellow
if (-not (Test-Path $usbRoot)) {
    Write-Host "✗ USB drive not found: $USBDrive" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ USB drive validated" -ForegroundColor Green
Write-Host ""

Write-Host "[2/10] Creating directory structure..." -ForegroundColor Yellow
$dirs = @(
    "LegionMini",
    "LegionMini\backend",
    "LegionMini\android",
    "LegionMini\desktop",
    "LegionMini\macos",
    "LegionMini\linux",
    "LegionMini\data",
    "LegionMini\config",
    "LegionMini\python"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$usbRoot$dir" -Force | Out-Null
}
Write-Host "✓ Directory structure created" -ForegroundColor Green
Write-Host ""

Write-Host "[3/10] Copying auto-run wizard..." -ForegroundColor Yellow
Copy-Item -Path "usb_installer\autorun_wizard.html" -Destination "$usbRoot\autorun_wizard.html" -Force
Copy-Item -Path "usb_installer\autorun.inf" -Destination "$usbRoot\autorun.inf" -Force
Copy-Item -Path "usb_installer\autorun_launcher.bat" -Destination "$usbRoot\autorun_launcher.bat" -Force
Copy-Item -Path "usb_installer\autorun_launcher.sh" -Destination "$usbRoot\autorun_launcher.sh" -Force
Write-Host "✓ Auto-run files copied" -ForegroundColor Green
Write-Host ""

Write-Host "[4/10] Downloading portable Python..." -ForegroundColor Yellow
$pythonZip = "$env:TEMP\python-3.11-portable.zip"
if (-not (Test-Path "$usbRoot\LegionMini\python\python.exe")) {
    Write-Host "  Downloading Python 3.11 portable (25MB)..." -ForegroundColor Cyan
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip"
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip -UseBasicParsing
        Expand-Archive -Path $pythonZip -DestinationPath "$usbRoot\LegionMini\python" -Force
        Remove-Item $pythonZip -Force
        Write-Host "✓ Python portable installed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠ Could not download Python. Manual installation may be required." -ForegroundColor Yellow
    }
}
else {
    Write-Host "✓ Python already present" -ForegroundColor Green
}
Write-Host ""

Write-Host "[5/10] Copying backend files..." -ForegroundColor Yellow
$backendItems = @("project_ai", "api", "integrations", "requirements.txt", "start_api.py")
foreach ($item in $backendItems) {
    $source = ".\$item"
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination "$usbRoot\LegionMini\backend\" -Recurse -Force
    }
}
Write-Host "✓ Backend copied" -ForegroundColor Green
Write-Host ""

Write-Host "[6/10] Copying Android APK..." -ForegroundColor Yellow
$apkPaths = @(
    "android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk",
    "android\legion_mini\build\outputs\apk\release\legion_mini-release.apk"
)
$apkCopied = $false
foreach ($apkPath in $apkPaths) {
    if (Test-Path $apkPath) {
        Copy-Item -Path $apkPath -Destination "$usbRoot\LegionMini\android\" -Force
        $apkCopied = $true
    }
}
if ($apkCopied) {
    Write-Host "✓ Android APK copied" -ForegroundColor Green
}
else {
    Write-Host "⚠ APK not found - build it first" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[7/10] Copying desktop installers..." -ForegroundColor Yellow
# Windows
if (Test-Path "desktop\release\Project AI Setup.exe") {
    Copy-Item -Path "desktop\release\Project AI Setup.exe" -Destination "$usbRoot\LegionMini\desktop\" -Force
}
# macOS (if exists)
if (Test-Path "desktop\release\Project AI.dmg") {
    Copy-Item -Path "desktop\release\Project AI.dmg" -Destination "$usbRoot\LegionMini\macos\" -Force
}
# Linux (if exists)
if (Test-Path "desktop\release\Project AI.AppImage") {
    Copy-Item -Path "desktop\release\Project AI.AppImage" -Destination "$usbRoot\LegionMini\linux\" -Force
}
Write-Host "✓ Desktop installers copied" -ForegroundColor Green
Write-Host ""

Write-Host "[8/10] Creating launcher scripts..." -ForegroundColor Yellow

# Windows launcher
$winLauncher = @"
@echo off
title Legion Mini - Portable Edition
cls
echo ========================================
echo    Legion Mini Portable
echo    Personal AI Assistant
echo ========================================
echo.
echo [*] Starting Legion Backend...
echo.
cd /d "%~dp0LegionMini\backend"
..\python\python.exe start_api.py
pause
"@
Set-Content -Path "$usbRoot\START_LEGION.bat" -Value $winLauncher

# Linux/Mac launcher
$unixLauncher = @"
#!/bin/bash
echo "========================================"
echo "   Legion Mini Portable"
echo "   Personal AI Assistant"
echo "========================================"
echo ""
echo "[*] Starting Legion Backend..."
echo ""
cd "`$(dirname "`$0")/LegionMini/backend"
python3 start_api.py
"@
Set-Content -Path "$usbRoot\START_LEGION.sh" -Value $unixLauncher

# Android installer helper
$androidHelper = @"
@echo off
title Legion Mini - Android Installation
echo ========================================
echo    Install Legion Mini on Android
echo ========================================
echo.
echo Make sure:
echo  1. USB Debugging is enabled
echo  2. Device is connected via USB
echo  3. You have ADB installed
echo.
pause
echo.
echo Installing APK...
cd /d "%~dp0LegionMini\android"
adb install -r legion_mini-debug.apk
pause
"@
Set-Content -Path "$usbRoot\INSTALL_ANDROID.bat" -Value $androidHelper

Write-Host "✓ Launcher scripts created" -ForegroundColor Green
Write-Host ""

Write-Host "[9/10] Creating README and documentation..." -ForegroundColor Yellow
$readme = @"
# 🤖 Legion Mini - Universal USB Edition

**Personal AI Assistant on the Go!**

## ✨ What is This?

This USB drive contains **Legion Mini**, a complete portable AI assistant that works on ANY device!

Just plug it in, and the installation wizard will guide you through setup.

---

## 🚀 Quick Start

### Windows
1. Plug in USB drive
2. **Auto-run wizard should launch automatically**
3. If not, open `autorun_wizard.html` manually
4. Or run `START_LEGION.bat` directly

### macOS
1. Plug in USB drive
2. Open `autorun_launcher.sh`
3. Or open `autorun_wizard.html` in browser

### Linux
1. Mount USB drive
2. Run `./autorun_launcher.sh`
3. Or open `autorun_wizard.html` in browser

### Android (via USB OTG)
1. Connect USB drive via OTG adapter
2. Use file manager to navigate to drive
3. Copy `LegionMini/android/legion_mini-debug.apk` to device
4. Install APK (enable "Unknown Sources")
5. Or run `INSTALL_ANDROID.bat` from PC with device connected

---

## 📁 What's Included

```
USB Drive/
├── autorun_wizard.html      # AI Installation Wizard (GUI)
├── autorun.inf              # Windows auto-run config
├── START_LEGION.bat         # Quick start (Windows)
├── START_LEGION.sh          # Quick start (macOS/Linux)
├── INSTALL_ANDROID.bat      # Android helper
└── LegionMini/
    ├── backend/             # Python AI backend
    ├── android/             # Android APK files
    ├── desktop/             # Windows installer
    ├── macos/               # macOS app (if available)
    ├── linux/               # Linux AppImage (if available)
    ├── python/              # Portable Python runtime
    ├── data/                # Your data & save points
    └── config/              # Configuration files
```

---

## 🎯 Features

- ✅ **Fully Portable** - No installation required on Windows
- ✅ **Cross-Platform** - Works on Windows, Mac, Linux, Android
- ✅ **Auto-Launch** - Plug and play installation wizard
- ✅ **AI Personality** - Legion Mini guides you through setup
- ✅ **Save Points** - Auto-saves every 15 minutes
- ✅ **Offline Capable** - Works without internet (when models are local)
- ✅ **Multi-Device** - Use same USB on multiple computers

---

## 🔧 System Requirements

- **Windows**: 10/11 (64-bit)
- **macOS**: 10.14+
- **Linux**: Most modern distributions
- **Android**: 8.0+ with USB OTG support
- **Storage**: 2GB free on USB drive
- **RAM**: 4GB minimum

---

## 📱 Mobile Installation

**Via USB OTG Adapter:**
1. Connect USB drive to Android phone/tablet
2. Open file manager app
3. Navigate to USB drive
4. Find `LegionMini/android/legion_mini-debug.apk`
5. Tap to install
6. Allow installation from unknown sources
7. Launch Legion Mini app

**Via PC:**
1. Connect Android device to PC via USB
2. Enable USB Debugging on device
3. Run `INSTALL_ANDROID.bat` from USB drive
4. App will install automatically

---

## 🌟 First Time Setup

1. **Launch the wizard** (autorun_wizard.html)
2. **Legion Mini says**: "Well, let's see what we're working with..."
3. **System detection** - Automatically detects your platform
4. **Click "Begin Installation"**
5. **Follow on-screen instructions**
6. **Done!** - Legion Mini is ready

---

## 💡 Tips

- **Keep USB Drive Plugged In** for portable operation
- **Or Install Locally** for better performance
- **All data stays on USB** when running portable mode
- ** Safe to unplug** after proper shutdown
- **Use on multiple PCs** - your data travels with you!

---

## 🆘 Troubleshooting

**Auto-run doesn't start:**
- Open `autorun_wizard.html` manually
- Or run `START_LEGION.bat` directly

**Python not found:**
- USB may not have finished copying
- Re-run universal USB installer

**Android won't install:**
- Enable "Unknown Sources" in Settings
- Check USB Debugging is enabled
- Try manual APK transfer

**Port already in use:**
- Close other Legion instances
- Restart your computer

---

## 📞 Support

- **Documentation**: See `DEPLOYMENT_GUIDE.md` in LegionMini/backend/
- **GitHub**: https://github.com/IAmSoThirsty/Project-AI
- **API Docs**: http://localhost:8001/docs (when running)

---

## 🔒 Privacy

- ✅ All data stored locally on USB drive
- ✅ No cloud sync unless you configure it
- ✅ Complete privacy control
- ✅ Portable across devices

---

**Enjoy your Personal AI Assistant!** 🚀

*"For we are many, and we are one"* - Legion
"@

Set-Content -Path "$usbRoot\README.md" -Value $readme
Write-Host "✓ README created" -ForegroundColor Green
Write-Host ""

Write-Host "[10/10] Finalizing USB drive..." -ForegroundColor Yellow
# Copy documentation
if (Test-Path "DEPLOYMENT_GUIDE.md") {
    Copy-Item -Path "DEPLOYMENT_GUIDE.md" -Destination "$usbRoot\LegionMini\" -Force
}
if (Test-Path "QUICK_START.md") {
    Copy-Item -Path "QUICK_START.md" -Destination "$usbRoot\LegionMini\" -Force
}

Write-Host "✓ USB drive ready" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Universal USB Drive Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Location: $USBDrive" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Features:" -ForegroundColor Yellow
Write-Host "  • Auto-launches installation wizard when plugged in" -ForegroundColor White
Write-Host "  • Works on Windows, macOS, Linux, Android" -ForegroundColor White
Write-Host "  • Legion Mini AI guides installation" -ForegroundColor White
Write-Host "  • Fully portable - no installation required" -ForegroundColor White
Write-Host "  • USB OTG support for mobile devices" -ForegroundColor White
Write-Host ""
Write-Host "🎯 To use:" -ForegroundColor Yellow
Write-Host "  1. Safely eject USB drive" -ForegroundColor White
Write-Host "  2. Plug into any device" -ForegroundColor White
Write-Host "  3. Installation wizard auto-launches" -ForegroundColor White
Write-Host "  4. Follow Legion Mini's guidance" -ForegroundColor White
Write-Host ""
Write-Host "📱 Android:" -ForegroundColor Yellow
Write-Host "  • Connect via USB OTG adapter" -ForegroundColor White
Write-Host "  • Open file manager and install APK" -ForegroundColor White
Write-Host "  • Or use PC with INSTALL_ANDROID.bat" -ForegroundColor White
Write-Host ""
Write-Host "Your Universal AI Assistant is ready! 🚀" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
