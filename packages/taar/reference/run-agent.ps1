# Run one TAAR agent through the governed executor (Windows).
# Usage: .\scripts\run-agent.ps1 -AgentId heartbeat-reader
param(
    [Parameter(Mandatory = $true)][string]$AgentId,
    [string]$Repo = ""
)
$ErrorActionPreference = "Stop"
$argsList = @("-m", "taar.cli", "run", $AgentId)
if ($Repo -ne "") { $argsList += @("--repo", $Repo) }
python @argsList
exit $LASTEXITCODE
