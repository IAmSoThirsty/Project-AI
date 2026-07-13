#!/usr/bin/env pwsh
# schedule_acceptance_gate.ps1 — Register nightly acceptance gate task.
#
# Runs tools/acceptance_gate.ps1 at 10 PM local time daily.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot/.."
$TaskName = "ProjectAI-AcceptanceGate"

$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\tools\acceptance_gate.ps1" `
    -WorkingDirectory $RepoRoot.Path

$Trigger = New-ScheduledTaskTrigger -Daily -At 10pm

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Write-Host "Registering task: $TaskName (daily 10 PM)"
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Force | Out-Null

Write-Host "`nRegistered acceptance gate task."
Write-Host "Remove: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
