<#
PROJECT_AI_CACHE_CLEANUP_COMMANDS_DRAFT.ps1
DRAFT ONLY - DO NOT RUN WITHOUT COMPLETING THE OWNER APPROVAL CHECKLIST IN PROJECT_AI_CACHE_CLEANUP_APPROVAL_PACKET.md

This file was generated as part of a strictly read-only approval packet task.
It contains NO authorization to clean anything.
All steps below are illustrative, safe-staged, and must be reviewed line-by-line.

Assumptions if ever used:
- You have completed the full checklist.
- You have owner explicit approval for the specific candidates.
- You are running from a clean tree.
- Backup target is OUTSIDE T:\Project-AI-main (e.g. the consolidation-logs folder or another drive).
#>

Set-Location "T:\Project-AI-main"

Write-Warning "=== DRAFT CACHE CLEANUP - REVIEW PACKET FIRST ==="
Write-Warning "This script is a DRAFT. It has not been executed by the agent."
Write-Warning "Running it without owner approval and full validation may cause data loss."

# 1. Reconfirm clean git status (required gate)
$dirty = (git status --porcelain | Measure-Object -Line).Lines
if ($dirty -ne 0) {
  Write-Error "Tree is not clean. Aborting draft. (git status --porcelain = $dirty)"
  exit 1
}
Write-Output "Gate 1 passed: git status clean (0 dirty lines)"

$candidates = @('__pycache__','.hypothesis','.mypy_cache','.pytest_cache','.ruff_cache','ci-reports','test-artifacts')

# 2. Create backup copy outside Project-AI-main
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupRoot = "T:\Project-AI-consolidation-logs\cache_backup_$timestamp"
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
Write-Output "Backup root: $backupRoot"

$backupManifest = @()
foreach ($cand in $candidates) {
  if (Test-Path ".\$cand") {
    $dest = Join-Path $backupRoot $cand
    Write-Output "Backing up $cand -> $dest"
    Copy-Item -Path ".\$cand" -Destination $dest -Recurse -Force
    # 3. Hash before/after (we hash the copy)
    $hash = Get-FileHash -Path $dest -Algorithm SHA256 -ErrorAction SilentlyContinue
    $backupManifest += [PSCustomObject]@{ Candidate=$cand; BackupPath=$dest; SHA256=$hash.Hash; Size=(Get-ChildItem $dest -Recurse -File | Measure Length -Sum).Sum }
  }
}
$backupManifest | Export-Csv -NoTypeInformation (Join-Path $backupRoot "backup_manifest.csv")
Write-Output "Backup manifest written. Hashes captured for all copied candidates."

# 4. Remove only the ignored/generated candidate paths (DRAFT - commented for safety)
#    In a real run you would uncomment AFTER owner sign-off and re-validation.
foreach ($cand in $candidates) {
  if (Test-Path ".\$cand") {
    Write-Warning "DRAFT: Would remove $cand (it is currently GitIgnored + no tracked content)"
    # REMOVE THE NEXT LINE'S COMMENT ONLY AFTER FULL APPROVAL + BACKUP VERIFICATION
    # Remove-Item -Path ".\$cand" -Recurse -Force -ErrorAction Stop
    Write-Output "DRAFT: (Remove-Item for $cand is commented out in this draft)"
  }
}

# 5. Re-run validation after hypothetical removal
Write-Output "`n=== Post-removal (hypothetical) validation would run here ==="
Write-Output "python -m pytest --collect-only -q"
Write-Output "ap validate agent_playbook"
# (In real use: capture output again and compare to packet)

# 6. Final git status
Write-Output "`n=== Final git status (after any real removal) ==="
git status --porcelain
git status --short

Write-Output "`nDRAFT COMPLETE. Compare backup_manifest.csv hashes if you ever execute a real cleanup."
Write-Warning "Remember: this packet + draft authorize nothing. Owner decision required for every step."
