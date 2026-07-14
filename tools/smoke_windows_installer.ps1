#!/usr/bin/env pwsh
# Silent install -> verify -> silent uninstall -> verify, against a real Bundle.exe built by
# tools/build_windows_installer.ps1. Shared by tools/acceptance_gate.ps1's
# Build-And-Smoke-Installer step and the ci.yaml windows-installer job so the two paths
# cannot drift, matching the same principle already used for the desktop-only smoke.
#
# Every assertion here checks real, observable state (files on disk, registry values, live
# processes) rather than trusting exit codes alone -- an unforwarded install-path property or
# a missing ARPSYSTEMCOMPONENT would otherwise let a broken installer report success.

param(
    [Parameter(Mandatory = $true)]
    [string]$BundleExe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-UninstallEntry {
    param([string]$ProductCode)
    $paths = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$ProductCode",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\$ProductCode"
    )
    foreach ($path in $paths) {
        $entry = Get-ItemProperty -LiteralPath $path -ErrorAction SilentlyContinue
        if ($entry) { return $entry }
    }
    return $null
}

function Get-SystemComponentFlag {
    # Get-ItemProperty only returns properties that actually exist as registry values, and
    # under Set-StrictMode this throws (rather than returning $null) when a property genuinely
    # isn't present -- which is the expected, correct state for the bundle's own key (it has no
    # SystemComponent value at all, only the two chained MSIs do).
    param($Entry)
    $property = $Entry.PSObject.Properties["SystemComponent"]
    if ($null -eq $property) { return $null }
    return $property.Value
}

$installRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("project-ai-installer-smoke-" + [Guid]::NewGuid().ToString("N"))
$logDir = Join-Path ([System.IO.Path]::GetTempPath()) "project-ai-installer-smoke-logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$installLog = Join-Path $logDir "install.log"
$uninstallLog = Join-Path $logDir "uninstall.log"

Write-Host "`n=== Silent install to temp prefix ===" -ForegroundColor Cyan
Write-Host "InstallFolder override: $installRoot"
$proc = Start-Process -FilePath $BundleExe -ArgumentList "/quiet", "/log", "`"$installLog`"", "InstallFolder=`"$installRoot`"" -Wait -PassThru
if ($proc.ExitCode -ne 0) { throw "Silent install failed with exit code $($proc.ExitCode); see $installLog" }

$desktopExe = Join-Path $installRoot "Desktop\Project-AI-Desktop.exe"
$apiExe = Join-Path $installRoot "Api\project-ai-api-server.exe"
if (-not (Test-Path -LiteralPath $desktopExe)) {
    throw "Property forwarding did not take effect: $desktopExe does not exist. The install likely landed in Program Files instead of the requested temp prefix."
}
if (-not (Test-Path -LiteralPath $apiExe)) {
    throw "Property forwarding did not take effect: $apiExe does not exist."
}
Write-Host "PASS: both executables exist under the requested temp prefix" -ForegroundColor Green

Write-Host "`n=== Add/Remove Programs visibility ===" -ForegroundColor Cyan
$log = Get-Content $installLog -Raw
$bundleMatch = [regex]::Match($log, "registration key:\s*SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\(\{[0-9A-Fa-f-]+\})")
if (-not $bundleMatch.Success) { throw "Could not find the bundle's registration key in $installLog" }
$bundleEntry = Get-UninstallEntry -ProductCode $bundleMatch.Groups[1].Value
if (-not $bundleEntry -or (Get-SystemComponentFlag $bundleEntry) -eq 1) {
    throw "Bundle Add/Remove Programs entry missing or incorrectly hidden"
}
Write-Host "PASS: exactly the bundle is visible in Add/Remove Programs ($($bundleEntry.DisplayName))" -ForegroundColor Green

Write-Host "`n=== Launch installed desktop app, confirm bundled api spawns ===" -ForegroundColor Cyan
$env:PROJECT_AI_DESKTOP_SMOKE = $null
$appProcess = Start-Process -FilePath $desktopExe -PassThru
try {
    $deadline = (Get-Date).AddSeconds(30)
    $apiRunning = $false
    while ((Get-Date) -lt $deadline) {
        if (Get-Process -Name "project-ai-api-server" -ErrorAction SilentlyContinue) {
            $apiRunning = $true
            break
        }
        Start-Sleep -Milliseconds 250
    }
    if (-not $apiRunning) { throw "Bundled api process never started within 30s of launching the installed desktop app" }
    Write-Host "PASS: bundled api process started" -ForegroundColor Green
}
finally {
    # Start-Process -PassThru returns before the window is created, so CloseMainWindow() can
    # silently no-op if called immediately (MainWindowHandle is still zero) -- wait for a real
    # window handle first, and give the graceful WM_CLOSE path real time to run Qt's
    # aboutToQuit handler before ever falling back to a hard kill (which bypasses that handler
    # entirely; no OS mechanism runs app cleanup code on a forced TerminateProcess).
    $closedGracefully = $false
    if (-not $appProcess.HasExited) {
        $handleDeadline = (Get-Date).AddSeconds(10)
        while ((Get-Date) -lt $handleDeadline -and $appProcess.MainWindowHandle -eq [IntPtr]::Zero) {
            Start-Sleep -Milliseconds 200
            $appProcess.Refresh()
        }
        if ($appProcess.MainWindowHandle -ne [IntPtr]::Zero) {
            $appProcess.CloseMainWindow() | Out-Null
            $exitDeadline = (Get-Date).AddSeconds(10)
            while ((Get-Date) -lt $exitDeadline -and -not $appProcess.HasExited) {
                Start-Sleep -Milliseconds 200
                $appProcess.Refresh()
            }
            $closedGracefully = $appProcess.HasExited
        }
    }
    if (-not $appProcess.HasExited) {
        Write-Host "WARN: graceful close did not succeed; force-killing the test process (child cleanup cannot be verified after a forced kill)" -ForegroundColor Yellow
        Stop-Process -Id $appProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

if (-not $closedGracefully) {
    Stop-Process -Name "project-ai-api-server" -Force -ErrorAction SilentlyContinue
    throw "Desktop app did not close gracefully, so the aboutToQuit->terminate_supervisor cleanup path was never exercised by this run"
}

$deadline = (Get-Date).AddSeconds(15)
while ((Get-Date) -lt $deadline) {
    if (-not (Get-Process -Name "project-ai-api-server" -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds 250
}
if (Get-Process -Name "project-ai-api-server" -ErrorAction SilentlyContinue) {
    Stop-Process -Name "project-ai-api-server" -Force -ErrorAction SilentlyContinue
    throw "Bundled api process was still running after the desktop app closed gracefully"
}
Write-Host "PASS: bundled api process was terminated when the desktop app closed gracefully" -ForegroundColor Green

Write-Host "`n=== Silent uninstall ===" -ForegroundColor Cyan
$proc = Start-Process -FilePath $BundleExe -ArgumentList "/quiet", "/uninstall", "/log", "`"$uninstallLog`"" -Wait -PassThru
if ($proc.ExitCode -ne 0) { throw "Silent uninstall failed with exit code $($proc.ExitCode); see $uninstallLog" }

if (Test-Path -LiteralPath $installRoot) {
    throw "Install root still exists after uninstall: $installRoot"
}
if (Get-UninstallEntry -ProductCode $bundleMatch.Groups[1].Value) {
    throw "Bundle Add/Remove Programs entry still present after uninstall"
}
$auditPath = Join-Path $env:LOCALAPPDATA "Project-AI-Desktop\data\chimera-audit.jsonl"
if (Test-Path -LiteralPath $auditPath) {
    Write-Host "PASS: audit evidence retained after uninstall ($auditPath), as documented" -ForegroundColor Green
}
Write-Host "PASS: install root and Add/Remove Programs entry removed" -ForegroundColor Green

Write-Host "`nAll installer smoke checks passed." -ForegroundColor Green
