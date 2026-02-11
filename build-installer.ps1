# Cross-platform build script for Project-AI (PowerShell)
# Supports Windows, macOS (via PowerShell Core), and Linux (via PowerShell Core)

param(
    [string]$Platform = "windows",
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$BuildDir = Join-Path $ProjectRoot "dist"
$Version = (Select-String -Path (Join-Path $ProjectRoot "pyproject.toml") -Pattern 'version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project-AI Build Script v$Version" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Platform: $Platform" -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found. Please install Python 3.11 or later." -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host ""
    Write-Host "[2/6] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "[2/6] Using existing virtual environment..." -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/6] Activating virtual environment..." -ForegroundColor Yellow
if ($IsWindows -or $env:OS -eq "Windows_NT") {
    & .\.venv\Scripts\Activate.ps1
}
else {
    # For macOS/Linux with PowerShell Core
    . ./.venv/bin/Activate.ps1
}
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install/upgrade dependencies
Write-Host ""
Write-Host "[4/6] Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel | Out-Null
python -m pip install -e . | Out-Null
python -m pip install pyinstaller | Out-Null
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Clean previous builds if requested
if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host ""
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $BuildDir
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Write-Host "✓ Cleaned" -ForegroundColor Green
}

# Build with PyInstaller
Write-Host ""
Write-Host "[5/6] Building executable..." -ForegroundColor Yellow
if (Test-Path "project-ai.spec") {
    pyinstaller project-ai.spec --clean --noconfirm
}
else {
    Write-Host "⚠️  project-ai.spec not found, creating basic executable..." -ForegroundColor Yellow
    pyinstaller src/app/main.py `
        --name ProjectAI `
        --onedir `
        --windowed `
        --add-data "data;data" `
        --hidden-import PyQt6 `
        --clean `
        --noconfirm
}
Write-Host "✓ Executable built" -ForegroundColor Green

# Create distributable archive
Write-Host ""
Write-Host "[6/6] Creating distribution archive..." -ForegroundColor Yellow
Push-Location $BuildDir

switch ($Platform) {
    "windows" {
        $archiveName = "ProjectAI-$Version-windows-x86_64.zip"
        if (Test-Path $archiveName) {
            Remove-Item $archiveName
        }
        Compress-Archive -Path "ProjectAI" -DestinationPath $archiveName
        Write-Host "✓ Created $archiveName" -ForegroundColor Green
    }
    "macos" {
        $archiveName = "ProjectAI-$Version-macos.tar.gz"
        tar -czf $archiveName ProjectAI/
        Write-Host "✓ Created $archiveName" -ForegroundColor Green
    }
    "linux" {
        $archiveName = "ProjectAI-$Version-linux-x86_64.tar.gz"
        tar -czf $archiveName ProjectAI/
        Write-Host "✓ Created $archiveName" -ForegroundColor Green
    }
}

Pop-Location

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ Build completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Distribution package location:"
Write-Host "  $BuildDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the application:"
Write-Host "  $BuildDir\ProjectAI\ProjectAI.exe" -ForegroundColor Cyan
Write-Host ""
