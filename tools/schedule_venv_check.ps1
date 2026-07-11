#!/usr/bin/env pwsh
# schedule_venv_check.ps1 — Register weekly venv trampoline verification task.
#
# Runs tools/verify_venv_trampolines.py every Monday at 9 AM.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot/.."
$TaskName = "ProjectAI-VenvTrampolineCheck"

# Task Scheduler does not search PATH for Execute; use the venv's absolute
# python.exe (the guard is stdlib-only, so the venv interpreter suffices).
$Action = New-ScheduledTaskAction `
    -Execute "$($RepoRoot.Path)\.venv\Scripts\python.exe" `
    -Argument "$RepoRoot\tools\verify_venv_trampolines.py" `
    -WorkingDirectory $RepoRoot.Path

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd

Write-Host "Registering task: $TaskName (weekly Monday 9 AM)"
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Force | Out-Null

Write-Host "`nRegistered venv trampoline check task."
Write-Host "Remove: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
