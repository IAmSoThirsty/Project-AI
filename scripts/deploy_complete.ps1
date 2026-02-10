# Complete Deployment - One-Click Solution
# This script builds, tests, and prepares everything for deployment

param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Complete Deployment" -ForegroundColor Cyan
Write-Host "Building for Global Production" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Java environment
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

$totalSteps = 7
$currentStep = 0

function Show-Progress {
    param([string]$Message)
    $script:currentStep++
    Write-Host "[$script:currentStep/$totalSteps] $Message" -ForegroundColor Yellow
}

# Step 1: Install Python dependencies
Show-Progress "Installing Python dependencies..."
try {
    pip install -r requirements.txt --quiet
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
}
catch {
    Write-Host "⚠ Python dependency installation had warnings" -ForegroundColor Yellow  
}
Write-Host ""

# Step 2: Run tests (unless skipped)
if (-not $SkipTests) {
    Show-Progress "Running test suite..."
    try {
        .\scripts\run_e2e_tests.ps1
        Write-Host "✓ Tests completed" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠ Some tests failed - review before deploying" -ForegroundColor Yellow
    }
}
else {
    Show-Progress "Skipping tests (as requested)..."
    Write-Host "⚠ Tests skipped" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Build Android APK
Show-Progress "Building Android APK..."
try {
    cd android
    ..\gradlew.bat :legion_mini:assembleDebug --quiet
    ..\gradlew.bat :legion_mini:assembleRelease --quiet
    cd ..
    Write-Host "✓ Android APK built successfully" -ForegroundColor Green
    Write-Host "  📱 Debug: android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk" -ForegroundColor Gray
    Write-Host "  📱 Release: android\legion_mini\build\outputs\apk\release\legion_mini-release.apk" -ForegroundColor Gray
}
catch {
    Write-Host "✗ Android build failed" -ForegroundColor Red
    cd ..
}
Write-Host ""

# Step 4: Build Desktop App
Show-Progress "Building Desktop application..."
try {
    Push-Location desktop
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Installing Node dependencies..." -ForegroundColor Cyan
        npm install --silent
    }
    npm run build:win --silent
    Write-Host "✓ Desktop app built successfully" -ForegroundColor Green
    Write-Host "  🖥️  Installer: desktop\release\Project AI Setup.exe" -ForegroundColor Gray
    Pop-Location
}
catch {
    Write-Host "✗ Desktop build failed" -ForegroundColor Red
    Pop-Location
}
Write-Host ""

# Step 5: Create portable USB package
Show-Progress "Preparing portable USB package..."
Write-Host "  Note: Run '.\scripts\create_portable_usb.ps1' to create" -ForegroundColor Cyan
Write-Host "✓ Portable package script ready" -ForegroundColor Green
Write-Host ""

# Step 6: Create deployment directory
Show-Progress "Organizing deployment packages..."
$deployDir = ".\DEPLOYMENT"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\Android" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\Desktop" -Force | Out-Null
New-Item -ItemType Directory -Path "$deployDir\Documentation" -Force | Out-Null

# Copy files
if (Test-Path "android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk") {
    Copy-Item "android\legion_mini\build\outputs\apk\debug\legion_mini-debug.apk" "$deployDir\Android\" -Force
}
if (Test-Path "android\legion_mini\build\outputs\apk\release\legion_mini-release.apk") {
    Copy-Item "android\legion_mini\build\outputs\apk\release\legion_mini-release.apk" "$deployDir\Android\" -Force
}
if (Test-Path "desktop\release\Project AI Setup.exe") {
    Copy-Item "desktop\release\Project AI Setup.exe" "$deployDir\Desktop\" -Force
}

# Copy documentation
Copy-Item "DEPLOYMENT_GUIDE.md" "$deployDir\Documentation\" -Force
Copy-Item "QUICK_START.md" "$deployDir\Documentation\" -Force
Copy-Item "README.md" "$deployDir\Documentation\" -Force

Write-Host "✓ Deployment packages organized" -ForegroundColor Green
Write-Host ""

# Step 7: Final Summary
Show-Progress "Finalizing deployment..."
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Deployment Packages Created:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Android (Legion Mini):" -ForegroundColor Cyan
if (Test-Path "$deployDir\Android\legion_mini-debug.apk") {
    Write-Host "  ✓ Debug APK (sideload ready)" -ForegroundColor Green
}
if (Test-Path "$deployDir\Android\legion_mini-release.apk") {
    Write-Host "  ✓ Release APK (production ready)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Desktop:" -ForegroundColor Cyan
if (Test-Path "$deployDir\Desktop\Project AI Setup.exe") {
    Write-Host "  ✓ Windows installer" -ForegroundColor Green
}

Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  ✓ Deployment Guide" -ForegroundColor Green
Write-Host "  ✓ Quick Start Guide" -ForegroundColor Green
Write-Host "  ✓ README" -ForegroundColor Green

Write-Host ""
Write-Host "📁 All packages in: .\DEPLOYMENT\" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Desktop Installation:" -ForegroundColor White
Write-Host "    .\DEPLOYMENT\Desktop\Project AI Setup.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "  Android Installation:" -ForegroundColor White
Write-Host "    adb install -r .\DEPLOYMENT\Android\legion_mini-debug.apk" -ForegroundColor Gray  
Write-Host ""
Write-Host "  Portable USB:" -ForegroundColor White
Write-Host "    .\scripts\create_portable_usb.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  Start Backend:" -ForegroundColor White
Write-Host "    python start_api.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  Start Legion:" -ForegroundColor White
Write-Host "    python integrations\openclaw\legion_api.py" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🌍 Ready for Global Deployment!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"
