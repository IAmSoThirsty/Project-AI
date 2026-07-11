param([string]$Receipt = "project-ai-receipts-2026-07-10")

# Read-only audit collector. Captures raw git data and runs analysis tools,
# logging every command (start/end/exit/output destination) to commands.log.
# Writes ONLY inside the receipt directory.

$ErrorActionPreference = 'Continue'
$ROOT = (Get-Location).Path
$R    = Join-Path $ROOT $Receipt
$RAW  = Join-Path $R 'raw'
$LOG  = Join-Path $R 'commands.log'
$HEAD = (& git rev-parse HEAD).Trim()
New-Item -ItemType Directory -Force $RAW | Out-Null
if (-not (Test-Path $LOG)) { "# commands.log - every command as executed (start/end/exit/output)" | Out-File $LOG -Encoding utf8 }

function Step {
  param([string]$Id, [string]$Desc, [string]$Tool, [scriptblock]$Block)
  $start = (Get-Date).ToString('o')
  $out   = Join-Path $RAW "$Id.txt"
  $cmd   = ($Block.ToString().Trim() -replace '\s+', ' ')
  Add-Content $LOG "=== [$Id] $Desc ==="
  Add-Content $LOG "start=$start  cwd=$ROOT  head=$HEAD  tool=$Tool"
  Add-Content $LOG "command: $cmd"
  Add-Content $LOG "output: raw/$Id.txt"
  $global:LASTEXITCODE = 0
  try { $res = & $Block 2>&1 } catch { $res = "HARNESS-ERROR: $($_.Exception.Message)" }
  $code = $LASTEXITCODE; if ($null -eq $code) { $code = 0 }
  $res | Out-File -FilePath $out -Encoding utf8
  $end = (Get-Date).ToString('o')
  Add-Content $LOG "end=$end  exit=$code"
  Add-Content $LOG ""
  Write-Host ("[{0}] {1} (exit {2})" -f $Id, $Desc, $code)
}

# ---------- Git: files, objects, integrity ----------
Step '01a_git_ls_files' 'Git-tracked file list' 'git' { git ls-files }
Step '01b_git_ls_files_count' 'Git-tracked file count' 'git' { (git ls-files | Measure-Object).Count }
Step '07_git_count_objects' 'Git object database size' 'git' { git count-objects -vH }
Step '08_first_commit' 'First reachable commit (root)' 'git' {
  $root = (git rev-list --max-parents=0 HEAD)
  git show -s --format='sha=%H%nauthor=%an <%ae>%ndate=%ad%nsubject=%s' --date=iso-strict $root
}
Step '09_head_commit' 'HEAD commit details' 'git' {
  git show -s --format='sha=%H%nauthor=%an <%ae>%nauthor_date=%ad%ncommitter_date=%cd%nsubject=%s' --date=iso-strict HEAD
}
Step '11_commit_count_head' 'Commit count on current branch' 'git' { git rev-list --count HEAD }
Step '12_commit_count_all' 'Commit count all reachable refs' 'git' { git rev-list --count --all }
Step '41a_branches_local' 'Local branches' 'git' { git branch }
Step '41b_branches_remote' 'Remote branches' 'git' { git branch -r }
Step '41c_tags' 'Tags' 'git' { git tag }
Step '41d_submodules' 'Submodules' 'git' { git submodule status }
Step '41e_worktrees' 'Worktrees' 'git' { git worktree list }
Step '42a_git_status' 'git status --short' 'git' { git status --short }
Step '42b_git_fsck' 'git fsck --full' 'git' { git fsck --full }

# Raw logs for aggregate.py (no unix pipes; git --format straight to file)
Step '_git_log_head' 'HEAD log (H|an|ae|ad|cd)' 'git' {
  git --no-pager log '--format=%H|%an|%ae|%ad|%cd' --date=iso-strict HEAD
}
Step '_git_log_all' 'All-refs log (H|an|ae|ad)' 'git' {
  git --no-pager log --all '--format=%H|%an|%ae|%ad' --date=iso-strict
}
Step '_git_numstat_head' 'HEAD numstat by commit' 'git' {
  git --no-pager log --numstat '--format=@@@|%H|%an|%ae' HEAD
}

# ---------- Line counts ----------
$excl = '.git,.venv,venv,node_modules,__pycache__,.pytest_cache,.mypy_cache,.ruff_cache,dist,build,target,out,coverage,htmlcov,' + $Receipt
Step '18a_scc' 'Line counts (scc)' 'scc' { scc --exclude-dir $excl . }
Step '18a_scc_json' 'Line counts (scc json)' 'scc' { scc --exclude-dir $excl --format json . }
Step '18b_cloc_tracked' 'Line counts (cloc, git-tracked)' 'cloc' { cloc --vcs=git --quiet }

# ---------- Static analysis (nonzero exit = findings, recorded as data) ----------
Step '26a_ruff_check' 'Ruff lint' 'ruff' { uv run ruff check . --output-format=concise }
Step '26b_ruff_format' 'Ruff format check' 'ruff' { uv run ruff format --check . }
Step '26c_mypy' 'mypy (configured strict set)' 'mypy' {
  uv run python -m mypy packages apps/desktop apps/services tools
}
Step '26d_black' 'Black check (optional, not repo-configured)' 'black' { uv run black --check . }
Step '26e_bandit' 'Bandit security scan (optional)' 'bandit' {
  uv run bandit -r packages apps -q -f txt
}
Step '26f_pyright' 'Pyright (optional, scoped sample; not repo-configured)' 'pyright' {
  pyright packages/kernel/src/kernel
}
Step '26g_eslint_web' 'ESLint via repo pnpm web:lint (configured)' 'pnpm' { pnpm web:lint }

# ---------- Inventories + aggregation (python helpers) ----------
Step '13_17_aggregate' 'Authorship/activity aggregation' 'python' {
  uv run python (Join-Path $R 'aggregate.py') $R
}
Step '27_40_inventory' 'Structural inventories + tree' 'python' {
  uv run python (Join-Path $R 'inventory.py') $ROOT $R
}

# ---------- Archive (item 43) ----------
$arch = Join-Path $R 'archive/project-ai-HEAD.tar.gz'
Step '43_git_archive' 'Deterministic archive of HEAD' 'git' {
  git archive --format=tar.gz -o $arch HEAD; "archive: $arch"; "head: $HEAD"
}

Write-Host "collect.ps1 complete."
