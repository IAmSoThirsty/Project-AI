# Desktop Application Distribution and Installation

## Overview

Project-AI desktop application uses PyQt6 for the GUI and provides multiple distribution methods: bare-metal Python execution, virtual environment isolation, Windows installer packages, and portable USB deployment. This document covers all desktop deployment patterns from development to end-user installation.

## Desktop Architecture

### Technology Stack

- **UI Framework**: PyQt6 6.x (Qt 6 bindings for Python)
- **Python Version**: 3.11+ (required for modern type hints and performance)
- **Entry Point**: `src/app/main.py` [[src/app/main.py]] → `LeatherBookInterface` class
- **Build System**: PowerShell scripts + batch files
- **Packaging**: Native OS installers (planned: Electron, NSIS, WiX)

### Application Structure

```
Project-AI/
├── src/app/
│   ├── main.py                     # Entry point: LeatherBookInterface
│   ├── core/                       # Business logic (11 modules)
│   │   ├── ai_systems.py          # 6 AI systems (FourLaws, Persona, Memory, etc.)
│   │   ├── user_manager.py        # Authentication
│   │   ├── command_override.py    # Master password system
│   │   ├── learning_paths.py      # OpenAI learning path generator
│   │   ├── data_analysis.py       # CSV/XLSX/JSON analysis
│   │   ├── security_resources.py  # GitHub API integration
│   │   ├── location_tracker.py    # GPS/IP geolocation
│   │   ├── emergency_alert.py     # Emergency contact system
│   │   ├── intelligence_engine.py # OpenAI chat integration
│   │   ├── intent_detection.py    # ML intent classifier
│   │   └── image_generator.py     # HF Stable Diffusion + DALL-E 3
│   ├── agents/                    # AI agent modules (NOT plugins)
│   │   ├── oversight.py           # Action safety validation
│   │   ├── planner.py             # Task decomposition
│   │   ├── validator.py           # Input/output validation
│   │   └── explainability.py      # Decision explanations
│   └── gui/                       # PyQt6 UI modules (6 files)
│       ├── leather_book_interface.py    # Main window (659 lines)
│       ├── leather_book_dashboard.py    # 6-zone dashboard (608 lines)
│       ├── persona_panel.py             # 4-tab AI configuration
│       ├── dashboard_handlers.py        # Event handlers
│       ├── dashboard_utils.py           # Error handling, logging
│       └── image_generation.py          # Image gen UI (450 lines)
├── data/                          # Runtime data (persistent)
│   ├── users.json                 # User profiles (bcrypt hashes)
│   ├── ai_persona/
│   │   └── state.json             # Personality, mood, interaction counts
│   ├── memory/
│   │   └── knowledge.json         # Categorized knowledge base
│   └── learning_requests/
│       └── requests.json          # Learning requests + Black Vault
├── scripts/
│   ├── launch-desktop.bat         # Quick launch (batch)
│   ├── launch-desktop.ps1         # Quick launch (PowerShell)
│   ├── install_desktop.ps1        # Windows installer
│   ├── build_production.ps1       # Multi-platform build script
│   └── create_universal_usb.ps1   # USB installer creation
└── requirements.txt               # Python dependencies
```

## Launch Methods

### Method 1: Direct Python Execution

**Quickest for development**

```bash
# Windows (Command Prompt)
cd T:\Project-AI-main
set PYTHONPATH=%CD%\src
python src\app\main.py

# Windows (PowerShell)
cd T:\Project-AI-main
$env:PYTHONPATH = "$PWD\src"
python src\app\main.py

# Linux/macOS
cd /path/to/Project-AI-main
export PYTHONPATH="$(pwd)/src"
python src/app/main.py
```

**Critical**: MUST use `-m` flag or set `PYTHONPATH` to include `src/` directory

```bash
# Correct (module import)
python -m src.app.main

# Incorrect (breaks imports)
python src/app/main.py  # Fails: "ModuleNotFoundError: No module named 'app.core'"
```

**Why**: Python import system requires `src/` in module search path for `from app.core import ...` statements

### Method 2: Batch File Launcher

**Location**: `scripts/launch-desktop.bat`

**Features**:
- Automatic Python detection
- Virtual environment auto-creation
- Dependency installation
- Error handling with user prompts

```batch
@echo off
setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PYTHONPATH=%SCRIPT_DIR%src"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Create virtual environment if missing
if not exist "%SCRIPT_DIR%.venv" (
    echo Creating Python virtual environment...
    python -m venv "%SCRIPT_DIR%.venv"
)

REM Activate virtual environment
call "%SCRIPT_DIR%.venv\Scripts\activate.bat"

REM Install dependencies
pip install -q -r "%SCRIPT_DIR%requirements.txt" 2>nul

REM Launch application
echo Launching Project-AI Dashboard...
python "%SCRIPT_DIR%src\app\main.py"

if errorlevel 1 (
    echo ERROR: Application failed to start
    pause
)

endlocal
```

**Usage**:
```bash
# Double-click in Windows Explorer
# OR
cd T:\Project-AI-main\scripts
launch-desktop.bat
```

**Advantages**:
- No manual Python setup
- Isolated dependencies (venv)
- One-click launch
- Windows-native

### Method 3: PowerShell Launcher

**Location**: `scripts/launch-desktop.ps1`

**Features**:
- Enhanced error reporting (color-coded)
- Progress indicators
- Automatic venv management
- Cross-platform (PowerShell Core)

```powershell
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = "$scriptDir\src"
$venvDir = "$scriptDir\.venv"
$requirementsFile = "$scriptDir\requirements.txt"

function Show-Error {
    param([string]$message)
    Write-Host "`n[ERROR] $message" -ForegroundColor Red
    [System.Console]::ReadKey() | Out-Null
    exit 1
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-Error "Python not found. Download from https://www.python.org/downloads/"
    }
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Show-Error "Python not found."
}

# Create venv
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv $venvDir
}

# Activate venv
& "$venvDir\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
pip install -q -r $requirementsFile 2>$null

# Launch
Write-Host "Launching Project-AI Dashboard..." -ForegroundColor Green
$env:PYTHONPATH = $pythonPath
python "$scriptDir\src\app\main.py"
```

**Usage**:
```powershell
# PowerShell
cd T:\Project-AI-main\scripts
.\launch-desktop.ps1

# Right-click → Run with PowerShell (if execution policy allows)
```

**Advantages**:
- Better error messages
- Color-coded output
- Cross-platform (PowerShell Core on Linux/macOS)
- Scriptable

## Installation Methods

### Method 4: Installed Application (Windows)

**Location**: `scripts/install_desktop.ps1`

**Installation Flow**:

1. **Check Prerequisites**
   - Node.js (for Electron builds, if available)
   - Python 3.11+

2. **Install Dependencies**
   ```powershell
   cd desktop
   npm install
   ```

3. **Build Installer**
   ```powershell
   npm run build:win  # Creates .exe installer
   ```

4. **Run Installer**
   - Installer: `desktop/release/Project AI Setup.exe`
   - Default install path: `C:\Program Files\ProjectAI`
   - Creates Start Menu shortcut
   - Creates Desktop shortcut

**Build Script** (`install_desktop.ps1`):

```powershell
param(
    [string]$InstallPath = "C:\Program Files\ProjectAI"
)

Write-Host "========================================"
Write-Host "Project-AI Desktop Installation"
Write-Host "========================================"

# Step 1: Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found" -ForegroundColor Red
    exit 1
}

# Step 2: Install dependencies
Push-Location desktop
if (-not (Test-Path "node_modules")) {
    npm install
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}

# Step 3: Build desktop app
npm run build:win
Write-Host "✓ Build complete" -ForegroundColor Green

# Step 4: Create installer
$installer = Get-ChildItem "release\*.exe" | Select-Object -First 1
if ($installer) {
    Write-Host "✓ Installer created: $($installer.Name)" -ForegroundColor Green
    Start-Process -FilePath $installer.FullName -Wait
    Write-Host "✓ Installation complete" -ForegroundColor Green
}

Pop-Location
```

**Usage**:
```powershell
# Administrator PowerShell
cd T:\Project-AI-main
.\scripts\install_desktop.ps1
```

### Method 5: Portable USB Installation

**Location**: `scripts/create_universal_usb.ps1`

**Creates**: Self-contained USB drive with auto-run installation wizard

**USB Structure**:
```
USB Drive (E:\)/
├── autorun.inf                  # Windows auto-run config
├── autorun_wizard.html          # Legion Mini installation wizard (GUI)
├── autorun_launcher.bat         # Windows auto-launcher
├── autorun_launcher.sh          # Linux/macOS auto-launcher
├── START_LEGION.bat             # Quick start (Windows portable mode)
├── START_LEGION.sh              # Quick start (Linux/macOS portable mode)
├── INSTALL_ANDROID.bat          # Android APK installer helper
├── README.md                    # Usage instructions
└── LegionMini/
    ├── backend/                 # Python AI backend
    │   ├── project_ai/
    │   ├── api/
    │   ├── integrations/
    │   ├── requirements.txt
    │   └── start_api.py
    ├── android/
    │   ├── legion_mini-debug.apk
    │   └── legion_mini-release.apk
    ├── desktop/
    │   └── Project AI Setup.exe
    ├── macos/
    │   └── Project AI.dmg
    ├── linux/
    │   └── Project AI.AppImage
    ├── python/
    │   └── python.exe           # Portable Python 3.11 (25MB)
    ├── data/                    # Your data (persists on USB)
    └── config/                  # Configuration files
```

**Creation Script** (`create_universal_usb.ps1`):

```powershell
param([string]$USBDrive)

# Get USB drive letter
if (-not $USBDrive) {
    $USBDrive = Read-Host "Enter USB drive letter (e.g., E:)"
}

$usbRoot = "$USBDrive\"

# Step 1: Create directory structure
$dirs = @(
    "LegionMini", "LegionMini\backend", "LegionMini\android",
    "LegionMini\desktop", "LegionMini\macos", "LegionMini\linux",
    "LegionMini\data", "LegionMini\config", "LegionMini\python"
)
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path "$usbRoot$dir" -Force | Out-Null
}

# Step 2: Copy auto-run files
Copy-Item -Path "usb_installer\autorun_wizard.html" -Destination "$usbRoot\"
Copy-Item -Path "usb_installer\autorun.inf" -Destination "$usbRoot\"
Copy-Item -Path "usb_installer\autorun_launcher.bat" -Destination "$usbRoot\"

# Step 3: Download portable Python
$pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip"
$pythonZip = "$env:TEMP\python-3.11-portable.zip"
Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonZip
Expand-Archive -Path $pythonZip -DestinationPath "$usbRoot\LegionMini\python"

# Step 4: Copy backend files
Copy-Item -Path ".\project_ai" -Destination "$usbRoot\LegionMini\backend\" -Recurse
Copy-Item -Path ".\api" -Destination "$usbRoot\LegionMini\backend\" -Recurse
Copy-Item -Path ".\requirements.txt" -Destination "$usbRoot\LegionMini\backend\"

# Step 5: Copy installers (if built)
if (Test-Path "desktop\release\Project AI Setup.exe") {
    Copy-Item -Path "desktop\release\Project AI Setup.exe" -Destination "$usbRoot\LegionMini\desktop\"
}

# Step 6: Create portable launcher
$winLauncher = @"
@echo off
cd /d "%~dp0LegionMini\backend"
..\python\python.exe start_api.py
pause
"@
Set-Content -Path "$usbRoot\START_LEGION.bat" -Value $winLauncher

Write-Host "✅ Universal USB Drive Created!" -ForegroundColor Green
```

**Features**:
- **Auto-Run**: Wizard launches automatically when USB plugged in (Windows)
- **Portable Python**: No Python installation required on target PC
- **Multi-Platform**: Works on Windows, macOS, Linux, Android (via USB OTG)
- **Data Persistence**: All user data stays on USB drive
- **Offline Operation**: Fully functional without internet (when using local models)

**Usage**:
```powershell
# Create USB installer
cd T:\Project-AI-main
.\scripts\create_universal_usb.ps1
# Enter USB drive letter when prompted

# On target machine:
1. Plug in USB drive
2. Auto-run wizard launches (or open autorun_wizard.html)
3. Select installation type:
   - Portable (runs from USB)
   - Install to Computer (copies to C:\Program Files)
4. Follow Legion Mini's guidance
```

## Build Process

### Production Build Script

**Location**: `scripts/build_production.ps1`

**Capabilities**:
- Multi-platform builds (Desktop, Android, Portable)
- Automated testing
- Deployment package creation

```powershell
param(
    [switch]$Desktop,
    [switch]$Android,
    [switch]$Portable,
    [switch]$All
)

if ($All) {
    $Desktop = $true
    $Android = $true
    $Portable = $true
}

# Set Java environment (for Android builds)
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Build Android APK
if ($Android) {
    & .\gradlew.bat :legion_mini:assembleDebug
    & .\gradlew.bat :legion_mini:assembleRelease
    # Output: android\legion_mini\build\outputs\apk\
}

# Build Desktop App
if ($Desktop) {
    Push-Location desktop
    npm install
    npm run build:win
    # Output: desktop\release\Project AI Setup.exe
    Pop-Location
}

# Run tests
pytest tests/ -v --tb=short

Write-Host "Build Summary"
Write-Host "✓ Android APK: Ready"
Write-Host "✓ Desktop App: Ready"
```

**Usage**:
```powershell
# Build everything
.\scripts\build_production.ps1 -All

# Build specific platform
.\scripts\build_production.ps1 -Desktop
.\scripts\build_production.ps1 -Android
```

## Dependency Management

### Python Dependencies

**File**: `requirements.txt`

**Key Dependencies**:
- PyQt6 >= 6.4.0 (GUI framework)
- scikit-learn >= 1.3.0 (intent classification)
- openai >= 1.0.0 (GPT integration)
- requests >= 2.31.0 (API calls)
- cryptography >= 41.0.0 (encryption)
- bcrypt >= 4.0.0 (password hashing)
- Pillow >= 10.0.0 (image processing)

**Installation**:
```bash
# Development (all dependencies)
pip install -r requirements.txt

# Production (minimal)
pip install -r requirements.txt --no-dev
```

### Desktop Dependencies (Electron/Node)

**File**: `desktop/package.json` (if Electron packaging exists)

**Key Dependencies**:
- electron >= 27.0.0
- electron-builder >= 24.0.0 (installer creation)

**Installation**:
```bash
cd desktop
npm install
```

## Platform-Specific Considerations

### Windows

**Requirements**:
- Windows 10/11 (64-bit)
- Visual C++ Redistributable 2015-2022 (for PyQt6)
- 4GB RAM minimum

**Installation Paths**:
- Installed: `C:\Program Files\ProjectAI`
- User data: `%APPDATA%\ProjectAI` or `data/` in install directory

**Shortcuts**:
- Start Menu: `Start → All Programs → Project AI`
- Desktop: `Project AI.lnk`

### macOS

**Requirements**:
- macOS 10.14+ (Mojave or later)
- Xcode Command Line Tools
- 4GB RAM minimum

**Distribution**:
- `.dmg` installer (drag-and-drop)
- App bundle: `Project AI.app`
- Installed location: `/Applications/Project AI.app`

**User Data**:
- `~/Library/Application Support/ProjectAI/`

### Linux

**Requirements**:
- Most modern distributions (Ubuntu 20.04+, Fedora 35+, etc.)
- Python 3.11+ from system repos or pyenv
- 4GB RAM minimum

**Distribution**:
- AppImage (portable, self-contained)
- `.deb` package (Debian/Ubuntu)
- `.rpm` package (Fedora/RHEL)

**Installation**:
```bash
# AppImage
chmod +x Project-AI.AppImage
./Project-AI.AppImage

# .deb
sudo dpkg -i project-ai_1.0.0_amd64.deb

# .rpm
sudo rpm -ivh project-ai-1.0.0.x86_64.rpm
```

**User Data**:
- `~/.local/share/projectai/`

## Environment Configuration

### Environment Variables

**File**: `.env` [[.env]] (root directory, NOT committed to Git)

```bash
# OpenAI Integration
OPENAI_API_KEY=sk-...

# HuggingFace Integration
HUGGINGFACE_API_KEY=hf_...

# Encryption
FERNET_KEY=<generated_key>

# Email Alerts (optional)
SMTP_USERNAME=<email>
SMTP_PASSWORD=<password>
```

**Generation**:
```python
# Generate Fernet key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**Loading** (in `main.py`):
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### Configuration Files

**User Configuration**:
- `data/users.json` - User profiles with bcrypt hashes
- `data/ai_persona/state.json` - AI personality state
- `data/memory/knowledge.json` - Knowledge base
- `data/learning_requests/requests.json` - Learning requests + Black Vault

**System Configuration**:
- `data/command_override_config.json` - Override system state

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'app.core'**
```bash
# Solution: Set PYTHONPATH
set PYTHONPATH=%CD%\src   # Windows CMD
$env:PYTHONPATH = "$PWD\src"  # PowerShell
export PYTHONPATH="$(pwd)/src"  # Linux/macOS

# OR use module import
python -m src.app.main
```

**2. PyQt6 import errors**
```bash
# Windows: Install Visual C++ Redistributable
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Linux: Install system dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0  # Debian/Ubuntu
sudo dnf install xcb-util-cursor  # Fedora
```

**3. OpenAI API errors**
```bash
# Check .env file exists
ls .env

# Verify API key is loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
```

**4. Permission errors on Linux**
```bash
# Fix script permissions
chmod +x scripts/launch-desktop.sh

# Fix data directory permissions
chmod -R 755 data/
```

**5. Virtual environment activation fails**
```powershell
# Windows: Enable script execution
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Verify venv exists
if (Test-Path .venv) { "venv exists" } else { "venv missing - run python -m venv .venv" }
```

## Performance Optimization

### Startup Time Optimization

1. **Lazy Loading**: Import heavy modules only when needed
   ```python
   # Bad: Import at module level
   import openai
   
   # Good: Import in function
   def generate_learning_path():
       import openai  # Only load when function called
   ```

2. **Compiled Bytecode**: Pre-compile Python files
   ```bash
   python -m compileall src/
   ```

3. **Splash Screen**: Show loading UI while initializing
   ```python
   splash = QSplashScreen(QPixmap("assets/splash.png"))
   splash.show()
   # Initialize heavy components
   splash.close()
   ```

### Memory Optimization

1. **PyQt6 Object Lifecycle**: Delete unused widgets
   ```python
   old_widget.deleteLater()  # Schedule for deletion
   ```

2. **Cache Management**: Limit in-memory caches
   ```python
   from functools import lru_cache
   @lru_cache(maxsize=100)
   def expensive_function(param):
       ...
   ```

## Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] All dependencies in requirements.txt
- [ ] `.env` [[.env]] file created with API keys
- [ ] Virtual environment created
- [ ] PyQt6 tested (launch GUI once)
- [ ] Data directory writable
- [ ] Logs directory created
- [ ] Network access configured (for OpenAI/HuggingFace)
- [ ] Firewall rules (if needed)
- [ ] Antivirus exclusions (if needed)

## Related Documentation

- `01_docker_architecture.md` - Containerized deployment
- `03_portable_usb_deployment.md` - USB installer details
- `06_cross_platform_builds.md` - macOS/Linux builds
- `09_update_distribution.md` - Auto-update mechanism

## References

- **PyQt6 Documentation**: https://doc.qt.io/qtforpython-6/
- **Python Packaging**: https://packaging.python.org/
- **Electron Builder**: https://www.electron.build/
- **AppImage**: https://appimage.org/
