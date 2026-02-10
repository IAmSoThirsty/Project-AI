param(
  [string]$ArtifactsDir = "test-artifacts",
  [string]$OutJsonl = "docs/security/fourlaws-test-runs-latest.jsonl",
  [string]$OutSha256 = "docs/security/fourlaws-test-runs-latest.sha256"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path $ArtifactsDir)) {
  throw "Artifacts directory not found: $ArtifactsDir"
}

# If outputs exist, temporarily clear read-only so we can rewrite.
if (Test-Path $OutJsonl) { attrib -R $OutJsonl }
if (Test-Path $OutSha256) { attrib -R $OutSha256 }

$suites = @(
  'deterministic-1000',
  'property-1000',
  'disallowed-highlevel-1000',
  'hypothesis-threats-1000',
  'redacted-procedural-1000'
)

$inputs = @()
foreach ($s in $suites) {
  $f = Get-ChildItem $ArtifactsDir -Filter "fourlaws-$s-*.jsonl" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if ($null -eq $f) {
    throw "Missing artifact for suite '$s' in '$ArtifactsDir'"
  }

  $inputs += $f.FullName
}

python tools/merge_fourlaws_artifacts.py $OutJsonl $OutSha256 @inputs

# Restore read-only attribute (best-effort)
if (Test-Path $OutJsonl) { attrib +R $OutJsonl }
if (Test-Path $OutSha256) { attrib +R $OutSha256 }
