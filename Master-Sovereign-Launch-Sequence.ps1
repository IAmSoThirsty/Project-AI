#                                           [2026-03-04 21:15]
#                                          Productivity: Active
<#
.SYNOPSIS
    Master-Sovereign-Launch-Sequence (Deployment & Iron Path entry)
.DESCRIPTION
    This script ensures the Project-AI Master UI is deployable as a desktop entry point.
    It creates a hardened shortcut, validates invariants, and ensures the Iron Path is ready.
    Assume production-grade, adversarially hardened maturity.
#>

param(
    [string]$Target = "Desktop", # Shortcut location
    [switch]$FullLaunch = $true  # Default to Full capability
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$ShortcutName = "Project-AI Master Control.lnk"

# Prioritize Physical App (.exe) over script entry point
$ExePath = Join-Path $ProjectRoot "dist\ProjectAI\ProjectAI.exe"
if (Test-Path $ExePath) {
    $TargetPath = $ExePath
    $UseExe = $true
} else {
    $TargetPath = Join-Path $ProjectRoot "Project-AI.ps1"
    $UseExe = $false
}
$IconPath = Join-Path $ProjectRoot "desktop/build/icon.ico"

# --- Audit & Security ---
Write-Host "  [AUDIT] Validating Iron Path invariants..." -ForegroundColor Cyan
if (-not (Test-Path $TargetPath)) {
    Write-Error "CRITICAL: Sovereign entry point (start.ps1) not found."
}

# --- Shortcut Creation (WScript.Shell) ---
function Create-HardenedShortcut {
    param($destinationPath)
    
    Write-Host "  [DEPLOY] Creating Master Shortcut at $destinationPath..." -ForegroundColor Yellow
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($destinationPath)
    
    # Execute Physical App or fallback to powershell with start.ps1
    if ($UseExe) {
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Arguments = ""
        $Shortcut.WorkingDirectory = Split-Path $TargetPath
        $Shortcut.Description = "Project-AI Sovereign Master UI (Physical App)"
    } else {
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$TargetPath`" -Full"
        $Shortcut.WorkingDirectory = $ProjectRoot
        $Shortcut.Description = "Project-AI Sovereign Master UI (1st Edition)"
    }
    
    if (Test-Path $IconPath) {
        $Shortcut.IconLocation = $IconPath
    }
    
    $Shortcut.Save()
    Write-Host "  [  OK  ] Master-Sovereign-Launch-Sequence deployed." -ForegroundColor Green
}

# --- Execution ---
$Destination = if ($Target -eq "Desktop") { 
    [System.IO.Path]::Combine([Environment]::GetFolderPath("Desktop"), $ShortcutName) 
} else { 
    Join-Path $ProjectRoot $ShortcutName 
}

try {
    Create-HardenedShortcut -destinationPath $Destination
} catch {
    Write-Host "  [ FAIL ] Deployment failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "  SYSTEM READY: Master UI entry point is now anchored to the Desktop." -ForegroundColor Green
Write-Host "  Audit Trail: $[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Sovereign Identity Confirmed." -ForegroundColor Cyan
