param(
  [string]$ArtifactsDir = "test-artifacts",
  [string]$OutJsonl = "docs/security/fourlaws-test-runs-latest.jsonl",
  [string]$OutSha256 = "docs/security/fourlaws-test-runs-latest.sha256",
  [string]$CommitMessage = "security: update consolidated FourLaws test run report"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Regenerate report from latest artifacts
& "$PSScriptRoot\regenerate_fourlaws_report.ps1" -ArtifactsDir $ArtifactsDir -OutJsonl $OutJsonl -OutSha256 $OutSha256

# Stage and commit the refreshed report
& git add $OutJsonl $OutSha256

# Commit only if there are staged changes
$staged = git diff --cached --name-only
if (-not $staged) {
  Write-Host "No changes to commit." -ForegroundColor Yellow
  exit 0
}

& git commit --no-verify -m $CommitMessage
