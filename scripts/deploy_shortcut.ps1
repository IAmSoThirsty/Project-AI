# Project-AI Shortcut Deployment Script
# [2026-03-04 10:40]
# Productivity: Active

$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Project-AI Master Control.lnk"
$ProjectRoot = "c:\Users\Quencher\.gemini\antigravity\scratch\sovereign-repos\Project-AI"
$ExePath = Join-Path $ProjectRoot "dist\ProjectAI\ProjectAI.exe"
$ScriptPath = Join-Path $ProjectRoot "start.ps1"
$IconPath = Join-Path $ProjectRoot "desktop\build\icon.ico"

Write-Host "--- Deploying Sovereign Shortcut ---"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

if (Test-Path $ExePath) {
    Write-Host "✓ Physical App found: $ExePath" -ForegroundColor Green
    $Shortcut.TargetPath = $ExePath
    $Shortcut.Arguments = ""
    $Shortcut.WorkingDirectory = Split-Path $ExePath
} else {
    Write-Host "! Physical App not found. Falling back to start.ps1" -ForegroundColor Yellow
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptPath`" -Full"
    $Shortcut.WorkingDirectory = $ProjectRoot
}

$Shortcut.Description = "Project-AI Sovereign Master UI"

if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
}

$Shortcut.Save()
Write-Host "✓ Shortcut anchored to Desktop: $ShortcutPath" -ForegroundColor Green
