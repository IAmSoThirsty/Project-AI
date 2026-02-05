# Project-AI Installation USB Creator (Compact - 16GB)
# Creates installation package without portable runtime
# User installs Python separately on target machine

param(
    [string]$USBDrive,
    [switch]$SkipAndroid
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Installation USB Creator" -ForegroundColor Cyan
Write-Host "Compact Edition (16GB Compatible)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get USB drive
if (-not $USBDrive) {
    $USBDrive = Read-Host "Enter USB drive letter (e.g., E:)"
    if (-not $USBDrive.EndsWith(":")) {
        $USBDrive = $USBDrive + ":"
    }
}

$usbRoot = "$USBDrive\"

# Validate
Write-Host "[1/8] Validating USB drive..." -ForegroundColor Yellow
if (-not (Test-Path $usbRoot)) {
    Write-Host "✗ USB drive not found: $USBDrive" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check available space
$drive = Get-PSDrive -Name $USBDrive.Replace(":", "")
$freeSpace = [math]::Round($drive.Free / 1GB, 2)
Write-Host "  Available space: $freeSpace GB" -ForegroundColor Cyan

if ($freeSpace -lt 2) {
    Write-Host "✗ Insufficient space! Need at least 2GB free" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ USB drive validated ($freeSpace GB available)" -ForegroundColor Green
Write-Host ""

# Create structure
Write-Host "[2/8] Creating directory structure..." -ForegroundColor Yellow
$dirs = @(
    "ProjectAI_Installer",
    "ProjectAI_Installer\backend",
    "ProjectAI_Installer\android",
    "ProjectAI_Installer\docs",
    "ProjectAI_Installer\scripts"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$usbRoot$dir" -Force | Out-Null
}
Write-Host "✓ Structure created" -ForegroundColor Green
Write-Host ""

# Copy auto-run wizard
Write-Host "[3/8] Copying auto-run installer..." -ForegroundColor Yellow
Copy-Item -Path "usb_installer\autorun_wizard.html" -Destination "$usbRoot\autorun_wizard.html" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "usb_installer\autorun.inf" -Destination "$usbRoot\autorun.inf" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "usb_installer\autorun_launcher.bat" -Destination "$usbRoot\autorun_launcher.bat" -Force -ErrorAction SilentlyContinue
Write-Host "✓ Auto-run files copied" -ForegroundColor Green
Write-Host ""

# Copy backend
Write-Host "[4/8] Copying backend source..." -ForegroundColor Yellow
$backendItems = @("project_ai", "api", "integrations", "requirements.txt", "start_api.py", "pyproject.toml", "setup.py")
foreach ($item in $backendItems) {
    if (Test-Path $item) {
        Copy-Item -Path $item -Destination "$usbRoot\ProjectAI_Installer\backend\" -Recurse -Force
    }
}
Write-Host "✓ Backend copied" -ForegroundColor Green
Write-Host ""

# Copy Android APK
Write-Host "[5/8] Copying Android APK..." -ForegroundColor Yellow
if (-not $SkipAndroid) {
    $apkFound = $false
    $apkPaths = @(
        "android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk",
        "android\legion_mini\build\outputs\apk\release\legion_mini-release.apk"
    )
    foreach ($apkPath in $apkPaths) {
        if (Test-Path $apkPath) {
            Copy-Item -Path $apkPath -Destination "$usbRoot\ProjectAI_Installer\android\" -Force
            $apkFound = $true
        }
    }
    if ($apkFound) {
        Write-Host "✓ Android APK copied" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ APK not found - build it first or use -SkipAndroid" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠ Android APK skipped" -ForegroundColor Yellow
}
Write-Host ""

# Copy documentation
Write-Host "[6/8] Copying documentation..." -ForegroundColor Yellow
$docs = @("README.md", "CHANGELOG.md", "HOW_TO_RUN.md", "QUICK_START.md", "docs\deployment\DEPLOYMENT_GUIDE.md")
foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Copy-Item -Path $doc -Destination "$usbRoot\ProjectAI_Installer\docs\" -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "✓ Documentation copied" -ForegroundColor Green
Write-Host ""

# Create installation scripts
Write-Host "[7/8] Creating installation scripts..." -ForegroundColor Yellow

# Windows installer
$winInstaller = @"
@echo off
title Project-AI Installation
cls

echo ========================================
echo    Project-AI Installation Wizard
echo ========================================
echo.
echo This will install Project-AI on your system.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found!
    echo.
    echo Please install Python 3.11+ from python.org
    echo.
    pause
    exit /b 1
)

echo [1/4] Python detected
python --version

echo.
echo [2/4] Creating installation directory...
set INSTALL_DIR=%USERPROFILE%\ProjectAI
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo [3/4] Copying files...
xcopy /E /I /Y "%~dp0ProjectAI_Installer\backend" "%INSTALL_DIR%"

echo [4/4] Installing Python dependencies...
cd /d "%INSTALL_DIR%"
python -m pip install -r requirements.txt

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Location: %INSTALL_DIR%
echo.
echo To start Project-AI:
echo   cd %INSTALL_DIR%
echo   python start_api.py
echo.
echo Create desktop shortcut? (Y/N)
set /p CREATE_SHORTCUT=
if /i "%CREATE_SHORTCUT%"=="Y" (
    echo Creating shortcut...
    powershell -Command "^$ws = New-Object -ComObject WScript.Shell; ^$s = ^$ws.CreateShortcut('%USERPROFILE%\Desktop\Project-AI.lnk'); ^$s.TargetPath = 'python'; ^$s.Arguments = 'start_api.py'; ^$s.WorkingDirectory = '%INSTALL_DIR%'; ^$s.Save()"
    echo Desktop shortcut created!
)

echo.
pause
"@
Set-Content -Path "$usbRoot\INSTALL_WINDOWS.bat" -Value $winInstaller

# Linux/Mac installer
$unixInstaller = @"
#!/bin/bash
echo "========================================"
echo "   Project-AI Installation Wizard"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 not found!"
    echo ""
    echo "Please install Python 3.11+ first"
    exit 1
fi

echo "[1/4] Python detected"
python3 --version

echo ""
echo "[2/4] Creating installation directory..."
INSTALL_DIR="`$HOME/ProjectAI"
mkdir -p "`$INSTALL_DIR"

echo "[3/4] Copying files..."
cp -r "`$(dirname "`$0")/ProjectAI_Installer/backend/"* "`$INSTALL_DIR/"

echo "[4/4] Installing Python dependencies..."
cd "`$INSTALL_DIR"
python3 -m pip install -r requirements.txt

echo ""
echo "========================================"
echo "   Installation Complete!"
echo "========================================"
echo ""
echo "Location: `$INSTALL_DIR"
echo ""
echo "To start Project-AI:"
echo "  cd `$INSTALL_DIR"
echo "  python3 start_api.py"
echo ""
"@
Set-Content -Path "$usbRoot\INSTALL_LINUX_MAC.sh" -Value $unixInstaller

# Android helper
$androidHelper = @"
@echo off
title Project-AI - Android Installation
echo ========================================
echo    Install Project-AI on Android
echo ========================================
echo.
echo Prerequisites:
echo  1. USB Debugging enabled on device
echo  2. Device connected via USB
echo  3. ADB installed (Android Debug Bridge)
echo.
pause

cd /d "%~dp0ProjectAI_Installer\android"
adb install -r *.apk
if errorlevel 1 (
    echo.
    echo Installation failed!
    echo Make sure ADB is installed and device is connected.
) else (
    echo.
    echo Installation successful!
)
pause
"@
Set-Content -Path "$usbRoot\INSTALL_ANDROID.bat" -Value $androidHelper

Write-Host "✓ Installation scripts created" -ForegroundColor Green
Write-Host ""

# Create README
Write-Host "[8/8] Creating README..." -ForegroundColor Yellow
$readme = @"
# 🚀 Project-AI Installation USB

**Welcome to Project-AI!**

This USB drive contains everything you need to install Project-AI on your computer.

---

## 🎯 Quick Install

### Windows
1. **Double-click**: `INSTALL_WINDOWS.bat`
2. Follow the prompts
3. Done!

### macOS / Linux
1. Open Terminal
2. Run: `bash INSTALL_LINUX_MAC.sh`
3. Done!

### Android
1. Connect device via USB
2. Enable USB Debugging
3. Run: `INSTALL_ANDROID.bat`

---

## 📋 Requirements

**All Platforms:**
- Python 3.11 or higher
- 2GB free disk space
- Internet connection (for dependencies)

**Download Python:**
- Windows: https://python.org/downloads
- macOS: `brew install python` or python.org
- Linux: `sudo apt install python3` or similar

---

## 📦 What Gets Installed

✅ **Project-AI Backend** - Full API server
✅ **Save Points System** - Auto-saves every 15 minutes  
✅ **Legion Integration** - AI chat interface
✅ **Triumvirate Governance** - TARL enforcement
✅ **Complete Documentation**

**Installation Location:**
- Windows: `C:\Users\YourName\ProjectAI`
- macOS/Linux: `~/ProjectAI`

---

## 🚀 After Installation

**Start the server:**
```bash
cd ~/ProjectAI  # or C:\Users\YourName\ProjectAI
python start_api.py
```

**Access the interface:**
- API Docs: http://localhost:8001/docs
- Legion Chat: http://localhost:8002

**See full documentation:**
`docs/HOW_TO_RUN.md`

---

## 🔧 Troubleshooting

**"Python not found"**
- Install Python from python.org
- Make sure to check "Add to PATH" during installation

**"Permission denied"**
- Run installer as Administrator (Windows)
- Use `sudo` on Linux/Mac

**"Dependencies failed"**
- Ensure internet connection
- Try: `python -m pip install --upgrade pip`

---

## 📱 Android App

The Android APK is in `ProjectAI_Installer/android/`

**Manual Installation:**
1. Copy APK to device
2. Enable "Unknown Sources" in Settings
3. Tap APK to install

---

## 💡 What is Project-AI?

Project-AI is a complete AI system with:
- **Triumvirate Governance** (Galahad, Cerberus, CodexDeus)
- **TARL Enforcement** (Triumvirate Autonomous Reasoning Layer)
- **Auto-Save System** (15-minute rotation)
- **Legion AI Integration** (Chat interface)
- **Multi-Platform Support** (Windows/Mac/Linux/Android)

---

## 🆘 Support

- Documentation: `ProjectAI_Installer/docs/`
- GitHub: https://github.com/IAmSoThirsty/Project-AI
- Quick Start: `docs/QUICK_START.md`

---

**Installation Size:** ~500MB (backend) + dependencies
**USB Space Required:** <2GB total

**Ready to install!** 🎉
"@

Set-Content -Path "$usbRoot\README.txt" -Value $readme

Write-Host "✓ README created" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Installation USB Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Location: $USBDrive" -ForegroundColor Cyan
Write-Host "📦 Size: ~1-2GB (fits easily in 16GB)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Contents:" -ForegroundColor Yellow
Write-Host "  • INSTALL_WINDOWS.bat - Windows installer" -ForegroundColor White
Write-Host "  • INSTALL_LINUX_MAC.sh - Unix installer" -ForegroundColor White
Write-Host "  • INSTALL_ANDROID.bat - Android helper" -ForegroundColor White
Write-Host "  • ProjectAI_Installer/ - Source files" -ForegroundColor White
Write-Host "  • README.txt - Instructions" -ForegroundColor White
Write-Host "  • autorun_wizard.html - Auto-launch GUI" -ForegroundColor White
Write-Host ""
Write-Host "✨ Features:" -ForegroundColor Yellow
Write-Host "  • Auto-run wizard on Windows" -ForegroundColor White
Write-Host "  • One-click installation" -ForegroundColor White
Write-Host "  • Cross-platform support" -ForegroundColor White
Write-Host "  • Complete documentation" -ForegroundColor White
Write-Host "  • Android APK included" -ForegroundColor White
Write-Host ""
Write-Host "🎯 To use:" -ForegroundColor Yellow
Write-Host "  1. Safely eject USB" -ForegroundColor White
Write-Host "  2. Plug into target computer" -ForegroundColor White
Write-Host "  3. Run INSTALL_WINDOWS.bat (or equivalent)" -ForegroundColor White
Write-Host "  4. Follow prompts" -ForegroundColor White
Write-Host ""
Write-Host "Installation USB ready! 🚀" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
