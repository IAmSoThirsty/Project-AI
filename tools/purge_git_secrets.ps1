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
Write-Host ""
Write-Host "⚠️  CRITICAL: Rotate ALL exposed credentials IMMEDIATELY:" -ForegroundColor Red
Write-Host ""
Write-Host "3) ROTATE OPENAI_API_KEY:" -ForegroundColor Yellow
Write-Host "   - Go to: https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "   - REVOKE the old key (search for exposed key prefix)" -ForegroundColor White
Write-Host "   - Create NEW API key with appropriate permissions" -ForegroundColor White
Write-Host "   - Update .env file with new key" -ForegroundColor White
Write-Host "   - Test application works with new key" -ForegroundColor White
Write-Host ""
Write-Host "4) ROTATE SMTP/Email Credentials:" -ForegroundColor Yellow
Write-Host "   - For Gmail: https://myaccount.google.com/apppasswords" -ForegroundColor White
Write-Host "   - REVOKE old app password" -ForegroundColor White
Write-Host "   - Generate NEW app password" -ForegroundColor White
Write-Host "   - Update SMTP_PASSWORD in .env" -ForegroundColor White
Write-Host "   - Consider changing SMTP_USERNAME if exposed" -ForegroundColor White
Write-Host ""
Write-Host "5) ROTATE FERNET_KEY:" -ForegroundColor Yellow
Write-Host "   - Generate new key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"" -ForegroundColor White
Write-Host "   - ⚠️  WARNING: Rotating Fernet key makes old encrypted data unreadable!" -ForegroundColor Red
Write-Host "   - BEFORE rotating: Decrypt all existing data with old key" -ForegroundColor White
Write-Host "   - Update FERNET_KEY in .env with new key" -ForegroundColor White
Write-Host "   - Re-encrypt all data with new key" -ForegroundColor White
Write-Host ""
Write-Host "6) ROTATE HUGGINGFACE_API_KEY (if exposed):" -ForegroundColor Yellow
Write-Host "   - Go to: https://huggingface.co/settings/tokens" -ForegroundColor White
Write-Host "   - DELETE the old token" -ForegroundColor White
Write-Host "   - Create NEW token with appropriate permissions" -ForegroundColor White
Write-Host "   - Update HUGGINGFACE_API_KEY in .env" -ForegroundColor White
Write-Host ""
Write-Host "7) ROTATE Command Override Password (if set):" -ForegroundColor Yellow
Write-Host "   - Use command override UI to set NEW master password" -ForegroundColor White
Write-Host "   - Update COMMAND_OVERRIDE_PASSWORD in .env (if stored there)" -ForegroundColor White
Write-Host "   - Review command_override_audit.log for suspicious activity" -ForegroundColor White
Write-Host ""
Write-Host "8) Verify rotation complete:" -ForegroundColor Yellow
Write-Host "   - Test application with all new credentials" -ForegroundColor White
Write-Host "   - Check no old credentials remain in code/config" -ForegroundColor White
Write-Host "   - Run: python tools/secret_scan.py (if available)" -ForegroundColor White
Write-Host "   - Document rotation date and next rotation due date" -ForegroundColor White
Write-Host ""
Write-Host "9) Additional security measures:" -ForegroundColor Yellow
Write-Host "   - Enable 2FA on all external accounts (OpenAI, Hugging Face, etc.)" -ForegroundColor White
Write-Host "   - Review access logs for unauthorized usage" -ForegroundColor White
Write-Host "   - Monitor API usage for anomalies" -ForegroundColor White
Write-Host "   - Set up billing alerts (prevent surprise charges)" -ForegroundColor White
Write-Host "   - Add pre-commit hooks to prevent future secret commits" -ForegroundColor White
Write-Host ""
Write-Host "📋 Rotation Checklist:" -ForegroundColor Cyan
Write-Host "  [ ] Git history purged and force-pushed" -ForegroundColor White
Write-Host "  [ ] OpenAI API key revoked and rotated" -ForegroundColor White
Write-Host "  [ ] SMTP credentials rotated" -ForegroundColor White
Write-Host "  [ ] Fernet key rotated (with data migration)" -ForegroundColor White
Write-Host "  [ ] Hugging Face token rotated (if applicable)" -ForegroundColor White
Write-Host "  [ ] Command override password changed" -ForegroundColor White
Write-Host "  [ ] Application tested with new credentials" -ForegroundColor White
Write-Host "  [ ] Secret scanning run (no findings)" -ForegroundColor White
Write-Host "  [ ] Team notified of credential rotation" -ForegroundColor White
Write-Host "  [ ] Documented rotation date and reason" -ForegroundColor White
Write-Host ""
Write-Host "⏰ Set calendar reminder: Rotate credentials again in 90 days" -ForegroundColor Cyan
