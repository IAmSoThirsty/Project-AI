# Cross-Platform Build System and Multi-Target Deployment

## Overview

Project-AI supports deployment across multiple platforms and architectures: Windows (x64, ARM64), macOS (Intel, Apple Silicon), Linux (x86_64, ARM64), Android (ARMv7, ARM64, x86, x86_64). This document covers the unified build system, platform-specific considerations, and multi-target release workflows.

## Build System Architecture

### Multi-Platform Build Matrix

```
Project-AI Build Targets/
├── Desktop
│   ├── Windows
│   │   ├── x64 (Intel/AMD)
│   │   └── ARM64 (Snapdragon)
│   ├── macOS
│   │   ├── x86_64 (Intel Mac)
│   │   └── arm64 (Apple Silicon M1/M2/M3)
│   └── Linux
│       ├── x86_64 (Desktop)
│       ├── ARM64 (Raspberry Pi 4, Pinebook Pro)
│       └── ARMv7 (Raspberry Pi 3)
├── Mobile
│   └── Android
│       ├── arm64-v8a (64-bit ARM)
│       ├── armeabi-v7a (32-bit ARM)
│       ├── x86_64 (emulator)
│       └── x86 (emulator)
└── Containerized
    ├── Docker (linux/amd64, linux/arm64)
    └── Kubernetes (multi-arch manifests)
```

### Build Tools by Platform

| Platform | Build Tool | Package Format | Installer |
|----------|-----------|----------------|-----------|
| Windows | Electron Builder / PyInstaller | .exe, .msi, .zip | NSIS, WiX |
| macOS | Electron Builder / py2app | .dmg, .pkg, .zip | native |
| Linux | Electron Builder / AppImage | .AppImage, .deb, .rpm, .tar.gz | native |
| Android | Gradle | .apk, .aab | Google Play |

## Cross-Platform Build Script

### Unified Production Build

**Location**: `scripts/build_production.ps1`

**Full Multi-Platform Build**:

```powershell
param(
    [switch]$Desktop,
    [switch]$Android,
    [switch]$Portable,
    [switch]$All,
    [switch]$Windows,
    [switch]$macOS,
    [switch]$Linux
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Multi-Platform Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Set Java environment for Android
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Build flags
if ($All) {
    $Desktop = $true
    $Android = $true
    $Windows = $true
    $macOS = $true
    $Linux = $true
}

# ===== ANDROID BUILD =====
if ($Android) {
    Write-Host "`n[1/6] Building Android APKs..." -ForegroundColor Yellow
    
    try {
        Write-Host "  Architecture targets: arm64-v8a, armeabi-v7a, x86, x86_64" -ForegroundColor Cyan
        
        # Debug APK (all ABIs)
        & .\gradlew.bat :legion_mini:assembleDebug
        
        # Release APK (all ABIs)
        & .\gradlew.bat :legion_mini:assembleRelease
        
        # Android App Bundle (for Play Store)
        & .\gradlew.bat :legion_mini:bundleRelease
        
        Write-Host "  ✓ Android build complete" -ForegroundColor Green
        Write-Host "    Debug APK: android\legion_mini\build\outputs\apk\debug\" -ForegroundColor Gray
        Write-Host "    Release APK: android\legion_mini\build\outputs\apk\release\" -ForegroundColor Gray
        Write-Host "    App Bundle: android\legion_mini\build\outputs\bundle\release\" -ForegroundColor Gray
    }
    catch {
        Write-Host "  ✗ Android build failed: $_" -ForegroundColor Red
    }
}

# ===== WINDOWS BUILD =====
if ($Windows) {
    Write-Host "`n[2/6] Building Windows Desktop..." -ForegroundColor Yellow
    
    try {
        Push-Location desktop
        
        if (-not (Test-Path "node_modules")) {
            Write-Host "  Installing dependencies..." -ForegroundColor Cyan
            npm install --silent
        }
        
        # Build for Windows (x64 and ARM64)
        npm run build:win
        
        Write-Host "  ✓ Windows build complete" -ForegroundColor Green
        Write-Host "    Installer: desktop\release\Project AI Setup.exe" -ForegroundColor Gray
        Write-Host "    Portable: desktop\release\Project AI-portable.exe" -ForegroundColor Gray
        
        Pop-Location
    }
    catch {
        Write-Host "  ✗ Windows build failed: $_" -ForegroundColor Red
        Pop-Location
    }
}

# ===== MACOS BUILD =====
if ($macOS) {
    Write-Host "`n[3/6] Building macOS Desktop..." -ForegroundColor Yellow
    
    if ($env:OS -ne "Darwin") {
        Write-Host "  ⚠ macOS builds require macOS host (cross-compilation not supported)" -ForegroundColor Yellow
    }
    else {
        try {
            Push-Location desktop
            
            # Build universal binary (Intel + Apple Silicon)
            npm run build:mac
            
            Write-Host "  ✓ macOS build complete" -ForegroundColor Green
            Write-Host "    DMG: desktop\release\Project AI.dmg" -ForegroundColor Gray
            Write-Host "    App: desktop\release\Project AI.app" -ForegroundColor Gray
            
            Pop-Location
        }
        catch {
            Write-Host "  ✗ macOS build failed: $_" -ForegroundColor Red
            Pop-Location
        }
    }
}

# ===== LINUX BUILD =====
if ($Linux) {
    Write-Host "`n[4/6] Building Linux Desktop..." -ForegroundColor Yellow
    
    if ($env:OS -eq "Windows_NT") {
        Write-Host "  ⚠ Linux builds require Linux host or WSL2" -ForegroundColor Yellow
        Write-Host "  Attempting WSL2 build..." -ForegroundColor Cyan
        
        try {
            wsl bash -c "cd /mnt/t/Project-AI-main/desktop && npm run build:linux"
            Write-Host "  ✓ Linux build complete (via WSL2)" -ForegroundColor Green
        }
        catch {
            Write-Host "  ✗ Linux build failed: $_" -ForegroundColor Red
        }
    }
    else {
        try {
            Push-Location desktop
            
            # Build AppImage, .deb, .rpm
            npm run build:linux
            
            Write-Host "  ✓ Linux build complete" -ForegroundColor Green
            Write-Host "    AppImage: desktop\release\Project AI.AppImage" -ForegroundColor Gray
            Write-Host "    DEB: desktop\release\project-ai_1.0.0_amd64.deb" -ForegroundColor Gray
            Write-Host "    RPM: desktop\release\project-ai-1.0.0.x86_64.rpm" -ForegroundColor Gray
            
            Pop-Location
        }
        catch {
            Write-Host "  ✗ Linux build failed: $_" -ForegroundColor Red
            Pop-Location
        }
    }
}

# ===== PORTABLE USB =====
if ($Portable) {
    Write-Host "`n[5/6] Creating Portable USB Package..." -ForegroundColor Yellow
    Write-Host "  Run scripts\create_universal_usb.ps1 to create USB installer" -ForegroundColor Cyan
}

# ===== TESTS =====
Write-Host "`n[6/6] Running Tests..." -ForegroundColor Yellow

# Python backend tests
Write-Host "  Python unit tests..." -ForegroundColor Cyan
try {
    pytest tests/ -v --tb=short
    Write-Host "  ✓ Python tests passed" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ Some Python tests failed" -ForegroundColor Yellow
}

# Android instrumented tests (if device connected)
if ($Android) {
    try {
        $adbDevices = & adb devices | Select-String -Pattern "device$"
        if ($adbDevices) {
            Write-Host "  Android instrumented tests..." -ForegroundColor Cyan
            & .\gradlew.bat :legion_mini:connectedDebugAndroidTest
            Write-Host "  ✓ Android tests passed" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ⚠ Android tests skipped (no device)" -ForegroundColor Yellow
    }
}

# ===== BUILD SUMMARY =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Android) { Write-Host "✓ Android APK/AAB: Ready" -ForegroundColor Green }
if ($Windows) { Write-Host "✓ Windows Desktop: Ready" -ForegroundColor Green }
if ($macOS) { Write-Host "→ macOS Desktop: Requires macOS host" -ForegroundColor Yellow }
if ($Linux) { Write-Host "✓ Linux Desktop: Ready" -ForegroundColor Green }

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  • Sign releases: See scripts\sign_releases.ps1" -ForegroundColor White
Write-Host "  • Create USB installer: .\scripts\create_universal_usb.ps1" -ForegroundColor White
Write-Host "  • Publish to stores: See docs\PUBLISHING.md" -ForegroundColor White
```

**Usage**:
```powershell
# Build everything (local platform only)
.\scripts\build_production.ps1 -All

# Build specific targets
.\scripts\build_production.ps1 -Android -Windows
.\scripts\build_production.ps1 -Desktop -Portable

# Build only Android
.\scripts\build_production.ps1 -Android
```

## Platform-Specific Build Configuration

### Windows Desktop

**Electron Builder Configuration** (`desktop/package.json`):

```json
{
  "name": "project-ai",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "build:win": "electron-builder --win --x64 --arm64",
    "build:win:x64": "electron-builder --win --x64",
    "build:win:arm64": "electron-builder --win --arm64"
  },
  "build": {
    "appId": "com.projectai.desktop",
    "productName": "Project AI",
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "portable",
          "arch": ["x64"]
        },
        {
          "target": "zip",
          "arch": ["x64", "arm64"]
        }
      ],
      "icon": "assets/icon.ico",
      "publisherName": "Thirsty Projects",
      "verifyUpdateCodeSignature": false
    },
    "nsis": {
      "oneClick": false,
      "perMachine": true,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "Project AI"
    }
  }
}
```

**Build Outputs**:
- `Project AI Setup.exe` - NSIS installer (x64)
- `Project AI Setup ARM64.exe` - NSIS installer (ARM64)
- `Project AI-portable.exe` - Portable executable
- `Project AI-1.0.0-win.zip` - Compressed archive

**Code Signing** (optional):
```json
"win": {
  "certificateFile": "path/to/cert.pfx",
  "certificatePassword": "password",
  "signingHashAlgorithms": ["sha256"]
}
```

### macOS Desktop

**Electron Builder Configuration** (`desktop/package.json`):

```json
{
  "scripts": {
    "build:mac": "electron-builder --mac --universal",
    "build:mac:intel": "electron-builder --mac --x64",
    "build:mac:arm": "electron-builder --mac --arm64"
  },
  "build": {
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["universal"]
        },
        {
          "target": "pkg",
          "arch": ["universal"]
        },
        {
          "target": "zip",
          "arch": ["universal"]
        }
      ],
      "icon": "assets/icon.icns",
      "category": "public.app-category.productivity",
      "hardenedRuntime": true,
      "gatekeeperAssess": false,
      "entitlements": "build/entitlements.mac.plist",
      "entitlementsInherit": "build/entitlements.mac.plist"
    },
    "dmg": {
      "title": "Project AI",
      "background": "assets/dmg-background.png",
      "iconSize": 100,
      "contents": [
        {
          "x": 130,
          "y": 220
        },
        {
          "x": 410,
          "y": 220,
          "type": "link",
          "path": "/Applications"
        }
      ]
    }
  }
}
```

**Entitlements** (`build/entitlements.mac.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
  </dict>
</plist>
```

**Code Signing** (required for macOS 10.14.5+):
```bash
# Sign with Apple Developer ID
export APPLE_ID="your@email.com"
export APPLE_ID_PASSWORD="app-specific-password"

npm run build:mac
```

**Notarization** (required for macOS 10.15+):
```json
"afterSign": "scripts/notarize.js"
```

### Linux Desktop

**Electron Builder Configuration** (`desktop/package.json`):

```json
{
  "scripts": {
    "build:linux": "electron-builder --linux --x64 --arm64",
    "build:linux:x64": "electron-builder --linux --x64",
    "build:linux:arm64": "electron-builder --linux --arm64",
    "build:linux:armv7": "electron-builder --linux --armv7l"
  },
  "build": {
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64", "arm64", "armv7l"]
        },
        {
          "target": "deb",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "rpm",
          "arch": ["x64", "arm64"]
        },
        {
          "target": "tar.gz",
          "arch": ["x64", "arm64", "armv7l"]
        }
      ],
      "icon": "assets/icon.png",
      "category": "Utility",
      "maintainer": "Thirsty Projects <contact@thirstyprojects.com>",
      "vendor": "Thirsty Projects",
      "synopsis": "Personal AI Assistant"
    },
    "deb": {
      "depends": [
        "libgtk-3-0",
        "libnotify4",
        "libnss3",
        "libxss1",
        "libxtst6",
        "xdg-utils"
      ]
    },
    "rpm": {
      "depends": [
        "gtk3",
        "libnotify",
        "nss",
        "libXScrnSaver",
        "libXtst",
        "xdg-utils"
      ]
    }
  }
}
```

**Build Outputs**:
- `Project AI-1.0.0.AppImage` - Universal portable executable
- `project-ai_1.0.0_amd64.deb` - Debian/Ubuntu package
- `project-ai-1.0.0.x86_64.rpm` - Fedora/RHEL package
- `project-ai-1.0.0.tar.gz` - Compressed archive

**AppImage Permissions**:
```bash
chmod +x Project-AI-1.0.0.AppImage
./Project-AI-1.0.0.AppImage
```

### Android Multi-Architecture

**Gradle Configuration** (`android/legion_mini/build.gradle`):

```gradle
android {
    // Enable ABI splitting
    splits {
        abi {
            enable true
            reset()
            include 'arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'
            universalApk true  // Generate universal APK with all ABIs
        }
    }

    // Version code per ABI
    applicationVariants.all { variant ->
        variant.outputs.each { output ->
            def abiCode = project.ext.abiCodes.get(output.getFilter(com.android.build.OutputFile.ABI))
            if (abiCode != null) {
                output.versionCodeOverride = abiCode * 1000 + defaultConfig.versionCode
            }
        }
    }
}

// ABI version codes
project.ext.abiCodes = [
    'arm64-v8a': 3,
    'armeabi-v7a': 2,
    'x86_64': 1,
    'x86': 0
]
```

**Build Commands**:
```bash
# Universal APK (all ABIs, large file)
./gradlew :legion_mini:assembleDebug

# Split APKs (one per ABI, smaller files)
./gradlew :legion_mini:assembleRelease
# Output: legion_mini-arm64-v8a-release.apk, legion_mini-armeabi-v7a-release.apk, etc.

# Android App Bundle (Google Play)
./gradlew :legion_mini:bundleRelease
# Google Play auto-generates per-device APKs
```

## Docker Multi-Architecture Builds

### BuildKit Multi-Platform

**Enable BuildKit**:
```bash
export DOCKER_BUILDKIT=1
```

**Multi-Platform Build**:
```bash
# Build for AMD64 and ARM64
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t projectai/desktop:latest \
  --push \
  .
```

**Docker Compose Multi-Arch**:
```yaml
version: '3.8'

services:
  cerberus:
    image: projectai/cerberus:omega
    platform: linux/amd64  # Force specific architecture
```

**Dockerfile Multi-Stage for ARM**:
```dockerfile
# Use QEMU for cross-compilation
FROM --platform=$BUILDPLATFORM python:3.11-slim as builder

ARG BUILDPLATFORM
ARG TARGETPLATFORM

RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM"

# Build steps...
```

## CI/CD Multi-Platform Workflows

### GitHub Actions Matrix Build

**Location**: `.github/workflows/multi-platform-build.yml`

```yaml
name: Multi-Platform Build

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  build-desktop:
    name: Build Desktop (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            artifact: linux
            script: npm run build:linux
          - os: windows-latest
            artifact: windows
            script: npm run build:win
          - os: macos-latest
            artifact: macos
            script: npm run build:mac
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd desktop
          npm install
      
      - name: Build desktop app
        run: |
          cd desktop
          ${{ matrix.script }}
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: desktop-${{ matrix.artifact }}
          path: desktop/release/*

  build-android:
    name: Build Android (${{ matrix.abi }})
    runs-on: ubuntu-latest
    strategy:
      matrix:
        abi: [arm64-v8a, armeabi-v7a, x86, x86_64]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Build APK
        run: ./gradlew :legion_mini:assemble${{ matrix.abi }}Release
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: android-${{ matrix.abi }}
          path: android/legion_mini/build/outputs/apk/${{ matrix.abi }}/release/*.apk

  build-docker:
    name: Build Docker (Multi-Arch)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: projectai/desktop:latest
```

## Cross-Compilation Challenges

### Python Native Extensions

**Problem**: C extensions (numpy, cryptography) require platform-specific compilation

**Solutions**:

1. **Use Pre-built Wheels**:
```bash
pip install --only-binary :all: numpy
```

2. **Cross-Compile with Buildroot**:
```bash
# For ARM Linux
docker run --rm -v $(pwd):/workspace buildroot/base
```

3. **Use PyInstaller Bootloaders**:
```bash
# Build for ARM64 on x64 host
pyinstaller --target-arch arm64 main.py
```

### Qt/PyQt6 Cross-Compilation

**Problem**: PyQt6 binaries are platform-specific

**Solution**: Build on native platform or use Docker emulation

```yaml
# GitHub Actions: Build on native ARM runner
build-linux-arm64:
  runs-on: [self-hosted, linux, arm64]
```

## Testing Multi-Platform Builds

### Platform Test Matrix

```yaml
test-matrix:
  strategy:
    matrix:
      os: [ubuntu-latest, windows-latest, macos-latest]
      python: ['3.11', '3.12']
  runs-on: ${{ matrix.os }}
  steps:
    - name: Test on ${{ matrix.os }}
      run: pytest tests/
```

### Emulation Testing

**Android Emulator**:
```bash
# Create ARM64 emulator
avdmanager create avd -n test_device -k "system-images;android-33;google_apis;arm64-v8a"

# Run tests
./gradlew :legion_mini:connectedDebugAndroidTest
```

**QEMU for ARM Linux**:
```bash
# Install QEMU
sudo apt install qemu-user-static

# Run ARM binary on x64
qemu-aarch64-static ./Project-AI-arm64.AppImage
```

## Distribution and Packaging

### Release Artifacts Structure

```
releases/
├── v1.0.0/
│   ├── windows/
│   │   ├── Project-AI-Setup-1.0.0-x64.exe
│   │   ├── Project-AI-Setup-1.0.0-arm64.exe
│   │   ├── Project-AI-1.0.0-portable-x64.exe
│   │   └── checksums.txt
│   ├── macos/
│   │   ├── Project-AI-1.0.0-universal.dmg
│   │   ├── Project-AI-1.0.0.pkg
│   │   └── checksums.txt
│   ├── linux/
│   │   ├── Project-AI-1.0.0-x86_64.AppImage
│   │   ├── Project-AI-1.0.0-arm64.AppImage
│   │   ├── project-ai_1.0.0_amd64.deb
│   │   ├── project-ai_1.0.0_arm64.deb
│   │   ├── project-ai-1.0.0.x86_64.rpm
│   │   └── checksums.txt
│   ├── android/
│   │   ├── legion-mini-1.0.0-universal.apk
│   │   ├── legion-mini-1.0.0-arm64-v8a.apk
│   │   ├── legion-mini-1.0.0-armeabi-v7a.apk
│   │   ├── legion-mini-1.0.0.aab (Google Play)
│   │   └── checksums.txt
│   └── docker/
│       └── projectai-desktop-1.0.0-multiarch.tar.gz
```

### Checksum Generation

```powershell
# Generate SHA256 checksums
Get-ChildItem -Recurse -Include *.exe,*.dmg,*.AppImage,*.apk | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    "$hash  $($_.Name)" | Out-File -Append checksums.txt
}
```

## Related Documentation

- `02_desktop_distribution.md` - Desktop deployment details
- `04_android_deployment.md` - Android build specifics
- `07_container_security.md` - Container multi-arch
- `10_cicd_docker_pipeline.md` - Automated multi-platform builds

## References

- **Electron Builder Multi-Platform**: https://www.electron.build/multi-platform-build
- **Docker Buildx**: https://docs.docker.com/buildx/working-with-buildx/
- **GitHub Actions Matrix**: https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs
- **Android ABI Splits**: https://developer.android.com/studio/build/configure-apk-splits
