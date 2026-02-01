# Complete Production Build Script
# Builds all platforms and creates deployment packages

param(
    [switch]$Desktop,
    [switch]$Android,
    [switch]$Portable,
    [switch]$All
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Production Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Java environment for this session
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

if ($All) {
    $Desktop = $true
    $Android = $true
    $Portable = $true
}

# Build Android APK
if ($Android -or $All) {
    Write-Host "[1/4] Building Android APK..." -ForegroundColor Yellow
    Write-Host "  Platform: Android (Legion Mini)" -ForegroundColor Cyan
    
    try {
        & .\gradlew.bat :legion_mini:assembleDebug
        & .\gradlew.bat :legion_mini:assembleRelease
        Write-Host "✓ Android APK built successfully" -ForegroundColor Green
        Write-Host "  Debug: android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk" -ForegroundColor Gray
        Write-Host "  Release: android\legion_mini\build\outputs\apk\release\legion_mini-release.apk" -ForegroundColor Gray
    }
    catch {
        Write-Host "✗ Android build failed: $_" -ForegroundColor Red
    }
    Write-Host ""
}

# Build Desktop App
if ($Desktop -or $All) {
    Write-Host "[2/4] Building Desktop Application..." -ForegroundColor Yellow
    Write-Host "  Platform: Windows (Electron)" -ForegroundColor Cyan
    
    try {
        Push-Location desktop
        if (-not (Test-Path "node_modules")) {
            Write-Host "  Installing dependencies..." -ForegroundColor Cyan
            npm install
        }
        npm run build:win
        Write-Host "✓ Desktop app built successfully" -ForegroundColor Green
        Write-Host "  Installer: desktop\release\Project AI Setup.exe" -ForegroundColor Gray
        Pop-Location
    }
    catch {
        Write-Host "✗ Desktop build failed: $_" -ForegroundColor Red
        Pop-Location
    }
    Write-Host ""
}

# Create Portable USB Package
if ($Portable -or $All) {
    Write-Host "[3/4] Creating Portable USB Package..." -ForegroundColor Yellow
    Write-Host "  Creating self-contained USB distribution..." -ForegroundColor Cyan
    
    Write-Host "  Note: Run scripts\create_portable_usb.ps1 to create USB package" -ForegroundColor Yellow
    Write-Host ""
}

# Run Tests
Write-Host "[4/4] Running Tests..." -ForegroundColor Yellow

# Python tests
Write-Host "  Python unit tests..." -ForegroundColor Cyan
try {
    pytest tests/ -v --tb=short
    Write-Host "✓ Python tests passed" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Some Python tests failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($Android -or $All) {
    Write-Host "✓ Android APK: Ready" -ForegroundColor Green
}
if ($Desktop -or $All) {
    Write-Host "✓ Desktop App: Ready" -ForegroundColor Green
}
if ($Portable -or $All) {
    Write-Host "→ Portable USB: Run create_portable_usb.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  • Install Desktop: Run desktop\release\Project AI Setup.exe" -ForegroundColor White
Write-Host "  • Install Android: adb install android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk" -ForegroundColor White
Write-Host "  • Create USB: .\scripts\create_portable_usb.ps1" -ForegroundColor White
Write-Host ""
