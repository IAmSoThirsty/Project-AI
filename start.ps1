# (Sovereign Startup Orchestrator)           [2026-04-09 04:12]
#                                          Status: Active
<#
.SYNOPSIS
    Project-AI Desktop Application Launcher
.DESCRIPTION
    Starts the Python governance API server (port 8001) and Electron desktop app.
    On exit, cleanly shuts down both processes.
.EXAMPLE
    .\start.ps1
    .\start.ps1 -DevMode   # Vite dev server with hot reload
    .\start.ps1 -ServerOnly # Only start the API server
#>

param(
    [switch]$DevMode,
    [switch]$ServerOnly,
    [switch]$Full,
    [int]$Port = 8001,
    [int]$TimeoutSeconds = 30
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$SrcDir = Join-Path $ProjectRoot "src"
$DesktopDir = Join-Path $ProjectRoot "desktop"

# --- Helpers ---

function Write-Status($msg) {
    Write-Host "  [Project-AI] " -ForegroundColor Cyan -NoNewline
    Write-Host $msg
}

function Write-OK($msg) {
    Write-Host "  [  OK  ] " -ForegroundColor Green -NoNewline
    Write-Host $msg
}

function Write-Fail($msg) {
    Write-Host "  [ FAIL ] " -ForegroundColor Red -NoNewline
    Write-Host $msg
}

function Test-ServerReady {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        return ($null -ne $resp.status)
    } catch {
        return $false
    }
}

# --- Banner ---

Write-Host ""
if ($Full) {
    Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║    Project-AI Master UI (Leather Book)       ║" -ForegroundColor Cyan
    Write-Host "  ║    Full Capability / Sovereign Kernel        ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
} else {
    Write-Host "  ╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║    Project-AI Desktop Application            ║" -ForegroundColor Cyan
    Write-Host "  ║    Governance Kernel + PSIA + Triumvirate     ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
}
Write-Host ""

# --- Step 1: Start Governance API Server (Always needed for core services) ---

Write-Status "Starting governance API server on port $Port..."

$env:PYTHONPATH = $SrcDir
$serverProcess = Start-Process -FilePath "python" `
    -ArgumentList "-m", "uvicorn", "psia.server.governance_server:app", "--host", "127.0.0.1", "--port", "$Port", "--log-level", "info" `
    -PassThru -NoNewWindow

if (-not $serverProcess) {
    Write-Fail "Failed to start governance server"
    exit 1
}

Write-Status "Server PID: $($serverProcess.Id) — waiting for readiness..."

# --- Step 2: Wait for /health ---

$elapsed = 0
$ready = $false
while ($elapsed -lt $TimeoutSeconds) {
    Start-Sleep -Seconds 1
    $elapsed++
    if (Test-ServerReady) {
        $ready = $true
        break
    }
    if ($serverProcess.HasExited) {
        Write-Fail "Server process exited prematurely (exit code: $($serverProcess.ExitCode))"
        exit 1
    }
}

if (-not $ready) {
    Write-Fail "Server did not become ready within ${TimeoutSeconds}s"
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-OK "Governance API server online — http://127.0.0.1:$Port/health"

# --- Step 3: Start UI Interface ---

$uiProcess = $null

if (-not $ServerOnly) {
    if ($Full) {
        Write-Status "Starting Master UI (PyQt6)..."
        $uiProcess = Start-Process -FilePath "python" `
            -ArgumentList "src/app/main.py" `
            -WorkingDirectory $ProjectRoot `
            -PassThru -NoNewWindow
        
        if ($uiProcess) {
            Write-OK "Master UI started (PID: $($uiProcess.Id))"
        } else {
            Write-Fail "Failed to start Master UI"
        }
    } else {
        Write-Status "Starting Electron desktop application..."

        if (-not (Test-Path (Join-Path $DesktopDir "node_modules"))) {
            Write-Status "Running npm install in desktop/ ..."
            Push-Location $DesktopDir
            npm install 2>&1 | Out-Null
            Pop-Location
            Write-OK "npm install complete"
        }

        $npmCmd = if ($DevMode) { "dev" } else { "start" }
        $uiProcess = Start-Process -FilePath "npm" `
            -ArgumentList "run", $npmCmd `
            -WorkingDirectory $DesktopDir `
            -PassThru -NoNewWindow

        if ($uiProcess) {
            Write-OK "Desktop app started (PID: $($uiProcess.Id))"
        } else {
            Write-Fail "Failed to start desktop app"
        }
    }
}

# --- Step 4: Wait and cleanup ---

Write-Host ""
Write-Host "  Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

try {
    if ($uiProcess) {
        $uiProcess.WaitForExit()
        Write-Status "UI process exited"
    } else {
        # Server-only mode: wait for server
        $serverProcess.WaitForExit()
    }
} finally {
    Write-Status "Shutting down..."

    if ($uiProcess -and -not $uiProcess.HasExited) {
        Stop-Process -Id $uiProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Status "UI process stopped"
    }

    if (-not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Status "Governance server stopped"
    }

    Write-OK "All services stopped. Goodbye."
}
