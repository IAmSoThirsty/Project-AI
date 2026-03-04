# [2026-03-03 14:45]
# Connectivity: Active
# Hardened Startup Coverage Test Suite

# Set Error Action
$ErrorActionPreference = "Continue"

# Define Paths
$DateString = Get-Date -Format "yyyyMMdd_HHmmss"
$ResultsBase = Join-Path $PSScriptRoot "..\..\test_results"
$TestResultsDir = Join-Path $ResultsBase "startup_coverage_$DateString"

# Create Directory
if (-not (Test-Path $ResultsBase)) { New-Item -ItemType Directory -Path $ResultsBase -Force }
New-Item -ItemType Directory -Path $TestResultsDir -Force

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Project-AI Startup Coverage Test Suite" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Output: " -NoNewline; Write-Host $TestResultsDir -ForegroundColor Yellow
Write-Host ""

# Load assemblies
Try {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
} Catch {
    Write-Warning "Failed to load GUI assemblies. Screenshot capture may fail in this environment."
}

function Capture-Screen ([string]$Name) {
    Try {
        $Path = Join-Path $TestResultsDir ($Name + ".png")
        $Screen = [System.Windows.Forms.Screen]::PrimaryScreen
        $Bitmap = New-Object System.Drawing.Bitmap($Screen.Bounds.Width, $Screen.Bounds.Height)
        $Graphics = [System.Drawing.Graphics]::FromImage($Bitmap)
        $Graphics.CopyFromScreen($Screen.Bounds.X, $Screen.Bounds.Y, 0, 0, $Bitmap.Size)
        $Bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
        $Graphics.Dispose()
        $Bitmap.Dispose()
        Write-Host "[SNAPSHOT] OK: " -NoNewline; Write-Host $Name -ForegroundColor Green
    } Catch {
        Write-Host "[SNAPSHOT] FAILED: " -NoNewline; Write-Host $Name -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Gray
    }
}

# 1. Start Governance Server
Write-Host "[1/5] Initializing Governance Server..." -ForegroundColor Yellow
$ServerProcess = Start-Process python -ArgumentList "src/psia/server/governance_server.py" -NoNewWindow -PassThru
Start-Sleep -Seconds 6

# 2. Launch Master UI
Write-Host "[2/5] Launching Master UI..." -ForegroundColor Yellow
$UIProcess = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File .\start.ps1 -Full" -NoNewWindow -PassThru
Start-Sleep -Seconds 2

# 3. Capture Sequences
Capture-Screen "01_Startup_Sequence"
Start-Sleep -Seconds 10
Capture-Screen "02_Leather_Book_Interactive"

# 4. Collection
Write-Host "[4/5] Collecting Metrics..." -ForegroundColor Yellow
$PerfLog = Join-Path $TestResultsDir "performance.txt"
"TIMESTAMP: $(Get-Date)" | Out-File $PerfLog
Try {
    "SERVER_WS: $( ($ServerProcess.WorkingSet64 / 1MB).ToString('F2') ) MB" | Out-File $PerfLog -Append
    "GUI_WS: $( ($UIProcess.WorkingSet64 / 1MB).ToString('F2') ) MB" | Out-File $PerfLog -Append
} Catch {
    "PROCESS_METRICS_FAILED" | Out-File $PerfLog -Append
}

# 5. Shutdown
Write-Host "[5/5] Cleanup..." -ForegroundColor Yellow
Stop-Process -Id $UIProcess.Id -Force -ErrorAction SilentlyContinue
Stop-Process -Id $ServerProcess.Id -Force -ErrorAction SilentlyContinue

Write-Host "SUCCESS." -ForegroundColor Green
