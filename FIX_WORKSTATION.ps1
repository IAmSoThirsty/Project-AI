param(
    [switch]$Json,
    [switch]$StrictWorkspace
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Verifier = Join-Path $RepoRoot "scripts\verify_heart_restore_map.py"

if (-not (Test-Path -LiteralPath $Verifier)) {
    throw "Heart restore verifier is missing: $Verifier"
}

$python = $env:PYTHON
if ([string]::IsNullOrWhiteSpace($python)) {
    $python = "python"
}

$arguments = @($Verifier, "--root", $RepoRoot)
if ($Json) {
    $arguments += "--json"
}
if ($StrictWorkspace) {
    $arguments += "--strict-workspace"
}

Write-Host "Project-AI Heart Restore verification"
Write-Host "Repo root: $RepoRoot"
& $python @arguments
exit $LASTEXITCODE
