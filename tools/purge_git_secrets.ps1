param(
  [string]$RepoRoot = (Get-Location).Path,
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "RepoRoot: $RepoRoot"
Set-Location $RepoRoot

function Assert-Command($name) {
  $cmd = Get-Command $name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    throw "Required command '$name' not found on PATH. Install it and re-run."
  }
}

# Prefer git-filter-repo (recommended). Fallback to BFG is not included here.
Assert-Command git

$hasFilterRepo = $false
try {
  git filter-repo --help *> $null
  $hasFilterRepo = $true
} catch {
  $hasFilterRepo = $false
}

if (-not $hasFilterRepo) {
  Write-Host "git-filter-repo not found. Install one of:" -ForegroundColor Yellow
  Write-Host "  - pip install git-filter-repo" -ForegroundColor Yellow
  Write-Host "  - or use package manager: choco install git-filter-repo" -ForegroundColor Yellow
  Write-Host "Then re-run this script." -ForegroundColor Yellow
  exit 2
}

# Safety: require clean working tree
$status = git status --porcelain
if ($status) {
  Write-Host "Working tree not clean. Commit/stash changes first:" -ForegroundColor Red
  Write-Host $status
  exit 3
}

Write-Host "Creating backup tag pre-purge..." -ForegroundColor Cyan
git tag -f pre-secret-purge

if ($DryRun) {
  Write-Host "DRY RUN: would run git-filter-repo to remove .env history." -ForegroundColor Cyan
  exit 0
}

Write-Host "Rewriting history to remove .env from all commits..." -ForegroundColor Cyan
# Remove the file from all history
# Note: this rewrites ALL branches/tags in the local clone.
git filter-repo --path .env --invert-paths --force

Write-Host "Repacking repository..." -ForegroundColor Cyan
git reflog expire --expire=now --all
# Aggressive GC after rewrite

git gc --prune=now --aggressive

Write-Host "DONE. Next steps:" -ForegroundColor Green
Write-Host "  1) Force push:  git push --force --all origin" -ForegroundColor Green
Write-Host "  2) Force push tags: git push --force --tags origin" -ForegroundColor Green
Write-Host "  3) Rotate leaked credentials (OpenAI, SMTP, Fernet) immediately." -ForegroundColor Green
