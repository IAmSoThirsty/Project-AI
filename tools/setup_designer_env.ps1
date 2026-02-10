# PowerShell script to create/activate a venv and launch Qt Designer (Windows)
# Usage: Open PowerShell, allow script execution for the session:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\tools\setup_designer_env.ps1

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..')).Path
$VenvDir = Join-Path $RepoRoot 'venv-designer'
$LogFile = Join-Path $ScriptDir 'setup_designer_env.ps1.log'

Write-Host "Repo root: $RepoRoot"

# Ensure python available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Install Python 3.8+ or add it to PATH and re-run."
    exit 1
}

# Create venv if missing
if (-not (Test-Path (Join-Path $VenvDir 'Scripts\Activate.ps1'))) {
    Write-Host "Creating virtual environment at $VenvDir..."
    python -m venv "$VenvDir" 2>&1 | Tee-Object -FilePath $LogFile
    if ($LASTEXITCODE -ne 0) { Write-Error "Creating venv failed. See $LogFile"; exit 1 }
}

# Activate venv for this script
$activate = Join-Path $VenvDir 'Scripts\Activate.ps1'
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
} else {
    Write-Error "Activation script not found at $activate"; exit 1
}

# Ensure pip up to date
Write-Host "Upgrading pip, setuptools, wheel (logging to $LogFile)..."
& "$VenvDir\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel 2>&1 | Tee-Object -FilePath $LogFile

# Install requirements if present
$designerReq1 = Join-Path $ScriptDir 'requirements-designer.txt'
$designerReq2 = Join-Path $RepoRoot 'requirements-designer.txt'
$backend = 'pyqt'

if (Test-Path $designerReq1) {
    Write-Host "Installing from $designerReq1 (logging to $LogFile)"
    & "$VenvDir\Scripts\python.exe" -m pip install -r "$designerReq1" 2>&1 | Tee-Object -FilePath $LogFile
} elseif (Test-Path $designerReq2) {
    Write-Host "Installing from $designerReq2 (logging to $LogFile)"
    & "$VenvDir\Scripts\python.exe" -m pip install -r "$designerReq2" 2>&1 | Tee-Object -FilePath $LogFile
} else {
    Write-Host "No requirements-designer.txt found. Installing PyQt6 + pyqt6-tools... (logging to $LogFile)"
    & "$VenvDir\Scripts\python.exe" -m pip install pyqt6 pyqt6-tools 2>&1 | Tee-Object -FilePath $LogFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyQt6 install failed; attempting PySide6 fallback..."
        & "$VenvDir\Scripts\python.exe" -m pip install pyside6 2>&1 | Tee-Object -FilePath $LogFile
        if ($LASTEXITCODE -ne 0) {
            Write-Error "PySide6 install failed as well. See $LogFile for details."
        } else { $backend = 'pyside' }
    }
}

# Helper to find designer binaries
function Try-StartDesigner($paths) {
    foreach ($p in $paths) {
        if (Test-Path $p) {
            Write-Host "Launching Designer: $p"
            Start-Process -FilePath $p
            return $true
        }
    }
    return $false
}

# Look in virtualenv locations
if ($backend -eq 'pyqt') {
    $candidates = @()
    $candidates += Join-Path $VenvDir 'Scripts\designer.exe'
    $candidates += Join-Path $VenvDir 'Lib\site-packages\pyqt6_tools\Qt\bin\designer.exe'
    $candidates += Join-Path $VenvDir 'Scripts\pyqt6-tools.exe'
    if (Try-StartDesigner $candidates) { return }
}
if ($backend -eq 'pyside') {
    $candidates = @()
    $candidates += Join-Path $VenvDir 'Scripts\pyside6-designer.exe'
    $candidates += Join-Path $VenvDir 'Lib\site-packages\PySide6\Qt\bin\designer.exe'
    if (Try-StartDesigner $candidates) { return }
}

# Try PATH
$pathCandidates = @('designer','pyside6-designer','pyqt6-tools')
foreach ($exe in $pathCandidates) {
    if (Get-Command $exe -ErrorAction SilentlyContinue) {
        Write-Host "Launching $exe from PATH"
        Start-Process -FilePath $exe
        exit 0
    }
}

Write-Host "Could not find Qt Designer. See $LogFile for install logs."
Write-Host "Activate the venv and run Designer manually if available:"
Write-Host "  & '$VenvDir\\Scripts\\Activate.ps1'"
Write-Host "  '$VenvDir\\Scripts\\designer.exe'"
Write-Host "To launch the developer UI (app) after activation:"
Write-Host "  $VenvDir\\Scripts\\python.exe -m src.app.main"

exit 0
