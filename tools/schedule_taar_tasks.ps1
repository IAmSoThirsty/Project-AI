#!/usr/bin/env pwsh
# schedule_taar_tasks.ps1 — Register Windows Task Scheduler entries for TAAR agents.
#
# Registers scheduled tasks for each TAAR agent defined in the registry.
# Tasks run `uv run --package project-ai-taar taar run <agent_id>` from the repo root.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path "$PSScriptRoot/.."
$TaskPrefix = "TAAR"

# Task Scheduler does not search PATH for Execute; resolve uv's absolute path
# at registration time.
$UvPath = (Get-Command uv -ErrorAction Stop).Source

# Agent definitions: (id, schedule-trigger)
# -Once triggers require -At (mandatory); repetition runs from that start time.
$RepeatStart = (Get-Date).AddMinutes(1)
$Agents = @(
    @{ Id = "heartbeat-reader"; Trigger = New-ScheduledTaskTrigger -Once -At $RepeatStart -RepetitionInterval (New-TimeSpan -Minutes 5) }
    @{ Id = "lock-reader"; Trigger = New-ScheduledTaskTrigger -Once -At $RepeatStart -RepetitionInterval (New-TimeSpan -Minutes 5) }
    @{ Id = "runaway-reader"; Trigger = New-ScheduledTaskTrigger -Once -At $RepeatStart -RepetitionInterval (New-TimeSpan -Minutes 5) }
    @{ Id = "phantom-reader"; Trigger = New-ScheduledTaskTrigger -Once -At $RepeatStart -RepetitionInterval (New-TimeSpan -Minutes 5) }
    @{ Id = "path-drift-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At 1am }
    @{ Id = "secret-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date "00:00") }
    @{ Id = "overnight-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At 6am }
    @{ Id = "overnight-digest"; Trigger = New-ScheduledTaskTrigger -Daily -At 6am }
    @{ Id = "governance-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At 1am }
    @{ Id = "ruff-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date "03:00") }
    @{ Id = "mypy-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At (Get-Date "04:00") }
    @{ Id = "workflow-reader"; Trigger = New-ScheduledTaskTrigger -Daily -At 1am }
)

foreach ($Agent in $Agents) {
    $TaskName = "$TaskPrefix-$($Agent.Id)"
    $Action = New-ScheduledTaskAction `
        -Execute $UvPath `
        -Argument "run --package project-ai-taar taar run $($Agent.Id)" `
        -WorkingDirectory $RepoRoot.Path

    $Settings = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -DontStopOnIdleEnd `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries

    Write-Host "Registering task: $TaskName"
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Agent.Trigger `
        -Settings $Settings `
        -Force | Out-Null
}

Write-Host "`nRegistered $($Agents.Count) TAAR scheduled tasks."
Write-Host "List: Get-ScheduledTask -TaskName 'TAAR-*'"
Write-Host "Remove: Unregister-ScheduledTask -TaskName 'TAAR-*' -Confirm:`$false"
