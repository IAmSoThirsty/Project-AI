$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $Root

$paths = @(
    "logs",
    "output",
    "tmp",
    "data\genesis_pins",
    "data\tsa_anchors",
    "data\sovereign_audit",
    "Claude",
    "Codex"
)

foreach ($path in $paths) {
    New-Item -ItemType Directory -Force -Path $path | Out-Null
}

Write-Host "Running canonical loader verification..."
python Verify-SovereignLoaders.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running Thirsty interpreter smoke verifier..."
python scripts\verify\verify_thirsty_interpreter.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "SOFT_HEAL_COMPLETE"
