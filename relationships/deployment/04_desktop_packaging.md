# 04: Desktop Packaging Relationships

**Document**: Desktop Application Packaging and Distribution  
**System**: PyQt6 Desktop, Installers, Portable USB, Cross-Platform Builds  
**Related Systems**: CI/CD, Release Automation, Version Management

---


## Navigation

**Location**: `relationships\deployment\04_desktop_packaging.md`

**Parent**: [[relationships\deployment\README.md]]


## Desktop Packaging Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 DESKTOP PACKAGING ECOSYSTEM                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────┐                 │
│  │     Source Code (PyQt6 Application)    │                 │
│  │                                        │                 │
│  │  • src/app/main.py (entry point)      │                 │
│  │  • src/app/gui/ (6 UI modules)        │                 │
│  │  • src/app/core/ (11 business logic)  │                 │
│  │  • requirements.txt (dependencies)     │                 │
│  └──────────────┬─────────────────────────┘                 │
│                 │                                            │
│                 ↓                                            │
│  ┌─────────────────────────────────────────────────┐        │
│  │         Platform-Specific Build Tools           │        │
│  │                                                 │        │
│  │  Windows:                                       │        │
│  │  ├─ PyInstaller (bundle Python + app)         │        │
│  │  ├─ NSIS (installer creation)                 │        │
│  │  └─ Inno Setup (alternative)                  │        │
│  │                                                 │        │
│  │  macOS:                                         │        │
│  │  ├─ PyInstaller (app bundle)                  │        │
│  │  ├─ create-dmg (DMG creation)                 │        │
│  │  └─ codesign (app signing)                    │        │
│  │                                                 │        │
│  │  Linux:                                         │        │
│  │  ├─ PyInstaller (binary)                      │        │
│  │  ├─ AppImageTool (AppImage)                   │        │
│  │  └─ fpm (deb/rpm packages)                    │        │
│  └─────────────┬───────────────────────────────────┘        │
│                │                                             │
│                ↓                                             │
│  ┌──────────────────────────────────────────────┐           │
│  │         Distribution Artifacts               │           │
│  │                                              │           │
│  │  • Project AI Setup.exe (Windows)           │           │
│  │  • ProjectAI.dmg (macOS)                    │           │
│  │  • project-ai.AppImage (Linux)              │           │
│  │  • project-ai-portable.zip (USB)            │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Build Script Relationships

### Windows Build Flow
```powershell
# scripts/build_production.ps1 -Desktop
Set Environment
    ↓ sets
    JAVA_HOME, PATH
    ↓ validates
    Python 3.11+, Node.js
    ↓ executes
    Push-Location desktop
    ↓ checks
    node_modules exists?
        ├─→ Yes: skip npm install
        └─→ No: npm install
            ↓ installs
            Electron, Electron Builder
    ↓ builds
    npm run build:win
        ↓ invokes
        Electron Builder
        ↓ bundles
        Python app + PyQt6 + Electron shell
        ↓ creates
        NSIS Installer
        ↓ outputs
        desktop/release/Project AI Setup.exe
```

### Cross-Platform Build Matrix
```
Build Production Script
    ├─→ Windows Build
    │   ├─ gradlew :legion_mini:assembleRelease (Android)
    │   ├─ npm run build:win (Desktop)
    │   └─ create_portable_usb.ps1 (USB Installer)
    │
    ├─→ macOS Build (if platform = darwin)
    │   ├─ npm run build:mac
    │   ├─ create-dmg
    │   └─ codesign --sign "Developer ID"
    │
    └─→ Linux Build (if platform = linux)
        ├─ npm run build:linux
        ├─ AppImageTool
        └─ fpm -s dir -t deb
```

## Virtual Environment Management

### Development Launch Flow
```
User runs: launch-desktop.bat
    ↓ checks
    .venv directory exists?
        ├─→ No: Create virtual environment
        │   ↓ python -m venv .venv
        │   ↓ .venv\Scripts\activate
        │   ↓ pip install -r requirements.txt
        │
        └─→ Yes: Activate existing
            ↓ .venv\Scripts\activate
            ↓ verifies
            Dependencies up to date?
                ├─→ No: pip install -r requirements.txt
                └─→ Yes: Skip
                    ↓ sets
                    PYTHONPATH=%CD%\src
                    ↓ launches
                    python -m app.main
                    ↓ starts
                    PyQt6 Leather Book Interface
```

### Dependency Isolation
```
Global Python Environment
    ⊗ not used
Local Virtual Environment (.venv)
    ↓ contains
    Python 3.11 Interpreter (symlink)
    ↓ isolated
    Site-Packages:
        ├─ PyQt6 5.15.9
        ├─ PyQt6-Qt6 6.5.0
        ├─ bcrypt 4.0.1
        ├─ cryptography 41.0.3
        ├─ openai 0.27.8
        └─ ... (60+ packages)
            ↓ prevents
            Version Conflicts
            System Python Pollution
```

## Portable USB Deployment

### USB Structure
```
USB Drive (E:\)
├── Project-AI-Portable/
│   ├── autorun.inf (Windows auto-launch)
│   ├── launch_wizard.bat (entry point)
│   ├── legion_mini_wizard.exe (AI installer)
│   ├── python-portable/ (Python 3.11 runtime)
│   │   ├── python.exe
│   │   ├── Lib/ (standard library)
│   │   └── Scripts/
│   ├── app/ (Project-AI application)
│   │   ├── src/
│   │   ├── data/
│   │   └── requirements.txt
│   ├── android/ (APK for USB OTG install)
│   │   └── legion_mini-release.apk
│   └── launchers/
│       ├── launch_windows.bat
│       ├── launch_macos.sh
│       └── launch_linux.sh
```

### USB Installation Flow
```
USB Inserted
    ↓ triggers
    autorun.inf (Windows)
    ↓ executes
    launch_wizard.bat
    ↓ displays
    Legion Mini Wizard (GUI)
    ↓ user selects
    Installation Type:
        ├─→ Desktop Install
        │   ↓ copies
        │   App to %APPDATA%\Project-AI
        │   ↓ creates
        │   Start Menu Shortcut
        │   ↓ registers
        │   Uninstaller
        │
        ├─→ Portable Mode
        │   ↓ runs
        │   Directly from USB
        │   ↓ stores data
        │   USB:\data\
        │
        └─→ Android Install (if connected)
            ↓ detects
            adb devices
            ↓ installs
            adb install legion_mini-release.apk
```

## PyInstaller Bundling

### Dependency Collection
```
PyInstaller Analysis
    ↓ scans
    src/app/main.py (entry point)
    ↓ discovers
    Import Dependencies:
        ├─ PyQt6.QtWidgets → include PyQt6 DLLs
        ├─ openai → include openai package
        ├─ cryptography → include cffi, Rust libs
        └─ bcrypt → include bcrypt._bcrypt.pyd
            ↓ collects
            Python Modules + DLLs
            ↓ bundles
            Single Directory (dist/)
            ↓ or
            Single File (.exe with embedded ZIP)
```

### Spec File Configuration
```python
# project-ai.spec
a = Analysis(
    ['src/app/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('data', 'data'),  # Include data directory
        ('src/app/gui/*.ui', 'app/gui'),  # UI files
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'openai',
        'cryptography.fernet',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude unused large deps
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

## Installer Creation (NSIS)

### NSIS Script Relationships
```nsi
; project-ai-installer.nsi
!define APP_NAME "Project AI"
!define APP_VERSION "1.0.0"

; Dependencies
!include "MUI2.nsh"  ; Modern UI

; Installer Sections
Section "Core Application" SEC01
    SetOutPath "$INSTDIR"
    File /r "dist\project-ai\*.*"
    
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" \
                   "$INSTDIR\project-ai.exe"
    
    CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
                   "$INSTDIR\project-ai.exe"
SectionEnd

Section "Python Runtime" SEC02
    ; Only if not bundled
    File /r "python-embed\*.*"
SectionEnd

Section "Uninstaller"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" \
                     "UninstallString" "$INSTDIR\Uninstall.exe"
SectionEnd
```

### Installation Flow
```
User runs: Project AI Setup.exe
    ↓ NSIS extracts
    Installer Resources
    ↓ displays
    Welcome Screen
    ↓ user accepts
    License Agreement
    ↓ selects
    Installation Directory
    ↓ chooses
    Components:
        [X] Core Application (required)
        [ ] Python Runtime (if not bundled)
        [X] Desktop Shortcut
        [X] Start Menu Entry
    ↓ copies
    Files to $INSTDIR
    ↓ creates
    Registry Entries
    ↓ creates
    Shortcuts
    ↓ displays
    Completion Screen
```

## Platform-Specific Considerations

### Windows
```
Required:
    - Python 3.11+
    - Visual C++ Redistributable 2015-2022
    - Windows 10/11 (PyQt6 requirement)

Build Tools:
    - PyInstaller 5.13+
    - NSIS 3.08
    - Inno Setup 6.2 (alternative)

Challenges:
    - Antivirus false positives (sign with certificate)
    - UAC prompts (require admin for system-wide install)
    - DLL hell (bundle all dependencies)
```

### macOS
```
Required:
    - macOS 10.15+ (Catalina)
    - Xcode Command Line Tools
    - Developer ID certificate (signing)

Build Tools:
    - PyInstaller 5.13+
    - create-dmg
    - codesign, notarytool (Apple notarization)

Challenges:
    - Gatekeeper (require code signing)
    - Notarization (macOS 10.15+)
    - App Translocation (move from Downloads breaks app)
    - Retina display support (hi-DPI icons)
```

### Linux
```
Required:
    - glibc 2.31+ (Ubuntu 20.04+)
    - GTK 3.24+ (for PyQt6)
    - X11 or Wayland

Build Tools:
    - PyInstaller 5.13+
    - AppImageTool
    - fpm (for deb/rpm)

Distribution Methods:
    - AppImage (portable, universal)
    - .deb (Debian, Ubuntu)
    - .rpm (Fedora, RHEL)
    - Snap (Ubuntu Software)
    - Flatpak (Flathub)

Challenges:
    - Library dependencies (bundle or document)
    - Desktop integration (.desktop files)
    - Distribution diversity (test on multiple distros)
```

## Launch Methods

### Method 1: Batch Script (Windows)
```batch
@echo off
REM launch-desktop.bat
cd /d %~dp0
if not exist .venv (
    python -m venv .venv
    .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    .venv\Scripts\activate.bat
)
set PYTHONPATH=%CD%\src
python -m app.main
```

### Method 2: PowerShell Script
```powershell
# launch-desktop.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (!(Test-Path .venv)) {
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    .\.venv\Scripts\Activate.ps1
}

$env:PYTHONPATH = "$PWD\src"
python -m app.main
```

### Method 3: Direct Python
```bash
# Linux/macOS
cd /path/to/Project-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$(pwd)/src
python -m app.main
```

## Update Mechanism

### Desktop Auto-Update Flow
```
Application Startup
    ↓ checks
    GitHub Releases API
    ↓ compares
    Current Version: 1.0.0
    Latest Version: 1.0.1
    ↓ if newer
    Display Update Notification
    ↓ user clicks "Update"
    Download Installer:
        https://github.com/.../releases/download/v1.0.1/Project-AI-Setup.exe
    ↓ verifies
    SHA256 Checksum
    ↓ executes
    Installer (silent mode: /S)
    ↓ replaces
    Application Files
    ↓ restarts
    Application with v1.0.1
```

## Data Persistence

### User Data Locations
```
Windows:
    %APPDATA%\Project-AI\
        ├── data\
        │   ├── ai_persona\state.json
        │   ├── memory\knowledge.json
        │   └── users.json
        └── logs\
            └── project-ai.log

macOS:
    ~/Library/Application Support/Project-AI/
        └── (same structure)

Linux:
    ~/.local/share/project-ai/
        └── (same structure)

Portable USB:
    USB:\Project-AI-Portable\data\
        └── (same structure, persists on USB)
```

## Related Systems

- `05_cicd_pipelines.md` - Automated desktop builds
- `06_release_automation.md` - GitHub Release creation
- `02_docker_relationships.md` - Containerized alternative
- `10_deployment_pipeline_maps.md` - Full deployment flow

---

**Status**: ✅ Complete  
**Coverage**: Desktop packaging, installers, portable USB, cross-platform builds  
**Platforms**: Windows, macOS, Linux
