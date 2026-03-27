# [2026-03-04 11:55]
# Productivity: Active
# Project-AI Build Script - Hardened Pathing

param(
    [string]$Platform = "windows",
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Item .
$BuildDir = Join-Path $ProjectRoot.FullName "dist"
$VenvDir = Join-Path $ProjectRoot.FullName ".venv"
$PythonExe = if ($IsWindows -or $env:OS -eq "Windows_NT") { Join-Path $VenvDir "Scripts\python.exe" } else { Join-Path $VenvDir "bin/python" }

Write-Host "--- Project-AI Sovereign Build ---"
Write-Host "Project Root: $($ProjectRoot.FullName)"

# 1. Prerequisites (Hardened — repairs venv in-place, never deletes locked files)
if (-not (Test-Path $VenvDir)) {
    Write-Host "[1/6] Creating venv..."
    python -m venv $VenvDir
} else {
    Write-Host "[1/6] Existing venv found. Repairing in-place..."
    python -m venv --upgrade $VenvDir
}

# 2. Dependencies & Pip Bootstrapping
Write-Host "[2/6] Ensuring pip is available and installing dependencies..."
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
if (-not (Test-Path $PipExe)) {
    Write-Host "  [REPAIR] Pip missing. Bootstrapping via ensurepip..."
    & $PythonExe -m ensurepip --default-pip --upgrade
}

& $PythonExe -m pip install --upgrade pip setuptools wheel
& $PythonExe -m pip install -e .
& $PythonExe -m pip install pyinstaller

# 3. Clean Build Output (does NOT touch .venv — avoids file-lock issues)
if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host "[3/6] Cleaning dist directory..."
    Remove-Item -Recurse -Force $BuildDir -ErrorAction SilentlyContinue
}

# 4. Build
Write-Host "[4/6] Running Sovereign Build Orchestrator..."
$PyArgs = if ($Clean) { "--clean" } else { "" }
& $PythonExe build_orchestrator.py $PyArgs

Write-Host "[4.1/6] Packaging executable..."
$PyInstallerExe = if ($IsWindows -or $env:OS -eq "Windows_NT") { Join-Path $VenvDir "Scripts\pyinstaller.exe" } else { Join-Path $VenvDir "bin/pyinstaller" }

if (Test-Path "$ProjectRoot/ProjectAI.spec") {
    & $PyInstallerExe "$ProjectRoot/ProjectAI.spec" --clean --noconfirm
}
else {
    & $PyInstallerExe src/app/main.py --name ProjectAI --onedir --windowed --add-data "data;data" --hidden-import PyQt6 --clean --noconfirm
}

# 5. Archive
Write-Host "[5/6] Archiving..."
if (-not (Test-Path $BuildDir)) { New-Item -ItemType Directory -Path $BuildDir -Force }
Push-Location $BuildDir

# Note: PyInstaller creates a folder named after the --name argument (ProjectAI) inside 'dist'
$TargetFolder = Join-Path $BuildDir "ProjectAI"
if (-not (Test-Path $TargetFolder)) {
    Write-Host "Error: Build folder not found at $TargetFolder"
    exit 1
}

if ($Platform -eq "windows") {
    $archiveName = "ProjectAI-windows.zip"
    if (Test-Path $archiveName) { Remove-Item $archiveName }
    Compress-Archive -Path "ProjectAI" -DestinationPath $archiveName
}
else {
    $archiveName = "ProjectAI-$Platform.tar.gz"
    tar -czf $archiveName ProjectAI/
}

Pop-Location
Write-Host "=========================================="
Write-Host "Sovereign Build Complete: $BuildDir"
Write-Host "=========================================="
