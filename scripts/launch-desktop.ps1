# Project-AI Desktop Application Launcher (PowerShell)
# This script launches the Project-AI dashboard application
# Usage: Right-click -> Run with PowerShell

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonPath = "$scriptDir\src"
$venvDir = "$scriptDir\.venv"
$requirementsFile = "$scriptDir\requirements.txt"

# Function to show error and wait
function Show-Error {
    param([string]$message)
    Write-Host "`n[ERROR] $message" -ForegroundColor Red
    Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
    [System.Console]::ReadKey() | Out-Null
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Show-Error "Python is not installed or not in PATH. Download from https://www.python.org/downloads/"
    }
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Show-Error "Python is not installed or not in PATH. Download from https://www.python.org/downloads/"
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $venvDir)) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Cyan
    try {
        python -m venv $venvDir
        if ($LASTEXITCODE -ne 0) {
            Show-Error "Failed to create virtual environment"
        }
    } catch {
        Show-Error "Failed to create virtual environment: $_"
    }
}

# Activate virtual environment
$activateScript = "$venvDir\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Show-Error "Virtual environment activation script not found"
}

try {
    & $activateScript
} catch {
    Show-Error "Failed to activate virtual environment: $_"
}

# Install dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
if (Test-Path $requirementsFile) {
    try {
        pip install -q -r $requirementsFile 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Some dependencies may not have installed correctly" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Warning: Failed to install some dependencies: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: requirements.txt not found" -ForegroundColor Yellow
}

# Launch the application
Write-Host "Launching Project-AI Dashboard..." -ForegroundColor Green
$env:PYTHONPATH = $pythonPath
try {
    python "$scriptDir\src\app\main.py"
    if ($LASTEXITCODE -ne 0) {
        Show-Error "Application exited with error code $LASTEXITCODE"
    }
} catch {
    Show-Error "Failed to start application: $_"
}
