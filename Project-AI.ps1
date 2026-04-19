# (Sovereign Interface Catalyst)             [2026-04-09 04:26]
#                                          Status: Active
<#
.SYNOPSIS
    Project-AI Sovereign 1st Edition Launcher
.DESCRIPTION
    Hardened entry point for the Project-AI High-Fidelity Interface.
    Orchestrates the Ignition Sequence and boots the Sovereign Kernel.
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$SrcDir = Join-Path $ProjectRoot "src"

Write-Host ""
Write-Host "  🛡️  PROJECT-AI SOVEREIGN IGNITION (v1.0.0-E1)" -ForegroundColor Cyan
Write-Host "  ─────────────────────────────────────────────" -ForegroundColor Cyan

# Environment Setup
$env:PYTHONPATH = $SrcDir
$env:QT_API = "pyqt6"

# Run Ignition Sequence
Write-Host "  [SYSTEM] Engaging Cognitive Kernel..." -ForegroundColor Yellow
python src/app/main.py

Write-Host "  [SYSTEM] Shutdown sequence complete." -ForegroundColor Green
