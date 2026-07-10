# Print (or with -Apply, register) Windows Task Scheduler entries for the
# TAAR first swarm. Default is PRINT ONLY — nothing is registered without
# the explicit -Apply switch. TAAR itself never installs its own schedules.
param(
    [switch]$Apply,
    [string]$Repo = (Get-Location).Path,
    [string]$Python = ""
)
$ErrorActionPreference = "Stop"

# Task Scheduler runs with a minimal environment, so resolve the full
# interpreter path now instead of trusting PATH at trigger time. Pass
# -Python to pick an interpreter other than the first `python` on PATH
# (it must be 3.12+ with taar installed).
if ($Python -ne "") {
    $python = (Get-Command $Python -ErrorAction Stop).Source
} else {
    $python = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $python) {
    throw "python not found on PATH. Install Python 3.12+ and re-run, or pass -Python <path>."
}
if ($python -like "*\WindowsApps\*") {
    throw "python resolves to the Microsoft Store stub ($python), which fails under Task Scheduler. Install Python from python.org or pass -Python <path>."
}

$schedule = @(
    @{ Agent = "heartbeat-reader";           Minutes = 5 },
    @{ Agent = "heartbeat-report-writer";    Minutes = 5 },
    @{ Agent = "lock-reader";                Minutes = 5 },
    @{ Agent = "lock-report-writer";         Minutes = 5 },
    @{ Agent = "runaway-reader";             Minutes = 5 },
    @{ Agent = "runaway-report-writer";      Minutes = 5 },
    @{ Agent = "phantom-reader";             Minutes = 5 },
    @{ Agent = "phantom-report-writer";      Minutes = 5 },
    @{ Agent = "git-status-reader";          Minutes = 60 },
    @{ Agent = "git-status-writer";          Minutes = 60 },
    @{ Agent = "path-drift-reader";          Minutes = 60 },
    @{ Agent = "path-drift-report-writer";   Minutes = 60 },
    @{ Agent = "workflow-reader";            Minutes = 60 },
    @{ Agent = "workflow-report-writer";     Minutes = 60 },
    @{ Agent = "governance-reader";          Minutes = 360 },
    @{ Agent = "governance-digest-writer";   Minutes = 360 }
)

foreach ($entry in $schedule) {
    $name = "TAAR-" + $entry.Agent
    $cmd = "`"$python`" -m taar.cli run $($entry.Agent) --repo `"$Repo`""
    if ($Apply) {
        $action = New-ScheduledTaskAction -Execute $python -Argument "-m taar.cli run $($entry.Agent) --repo `"$Repo`"" -WorkingDirectory $Repo
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes $entry.Minutes) -RepetitionDuration ([TimeSpan]::MaxValue)
        Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Description "TAAR governed agent $($entry.Agent)" -Force | Out-Null
        Write-Host "REGISTERED  $name  (every $($entry.Minutes) min)"
    } else {
        Write-Host "WOULD REGISTER  $name  every $($entry.Minutes) min ->  $cmd"
    }
}
if (-not $Apply) {
    Write-Host ""
    Write-Host "Print-only run complete. Re-run with -Apply to register these tasks."
}
