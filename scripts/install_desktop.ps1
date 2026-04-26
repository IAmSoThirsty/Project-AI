# Project-AI Desktop Installation Script
# Builds and installs the desktop application

param(
    [string]$InstallPath = "C:\Program Files\ProjectAI"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Desktop Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "[1/5] Checking prerequisites..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
}
catch {
    Write-Host "✗ Node.js not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/5] Installing dependencies..." -ForegroundColor Yellow
Push-Location desktop
if (-not (Test-Path "node_modules")) {
    npm install
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/5] Building desktop application..." -ForegroundColor Yellow
npm run build:win
Write-Host "✓ Build complete" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Creating installation..." -ForegroundColor Yellow
$installer = Get-ChildItem "release\*.exe" | Select-Object -First 1
if ($installer) {
    Write-Host "✓ Installer created: $($installer.Name)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "[5/5] Installing application..." -ForegroundColor Yellow
    Start-Process -FilePath $installer.FullName -Wait
    Write-Host "✓ Installation complete" -ForegroundColor Green
}
else {
    Write-Host "✗ Installer not found" -ForegroundColor Red
}

Pop-Location

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Desktop Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project-AI Desktop is now installed!" -ForegroundColor Green
Write-Host "Launch from Start Menu or Desktop shortcut" -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to exit"
