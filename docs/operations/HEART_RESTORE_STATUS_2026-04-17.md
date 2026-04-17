# Heart Restore Status

Date: 2026-04-17

Status: local control-plane restore support is wired.

## Verified Structure

- `docs/operations/HEART_RESTORE_MAP_2026-04-02.md` is present as the historical map.
- `wiki/.obsidian` and `wiki/05_Operations/` are present for the local vault parent.
- Bucket 1 required control-plane files are present in the live checkout.
- `src/app/core/master_harness.py` and `src/app/core/nld_harness.py` are not restored because they are conditional and are not present in the checked manifest baseline.
- `Project-AI.code-workspace` remains the broad workspace.
- `IDE_Work_Spaces/project-ai-control-plane.code-workspace` provides the compact control-plane workspace.
- `FIX_WORKSTATION.ps1` runs the local heart-restore verifier.
- `.git` metadata is checked for required local files and folders: `HEAD`, `config`, `index`, `objects`, and `refs`.
- The verifier counts tracked, modified, untracked, and ignored paths from live git state.
- The verifier reads the Repo Library mirror under `wiki/09_Repo-Library/` and compares its recorded HEAD and ignored-file manifest against live git.
- The verifier surveys local and remote branch trees with `git ls-tree` without checking branches out.

## Current Warnings

- Some broad `Project-AI.code-workspace` sibling folders are external to this checkout and may not resolve on every workstation.
- `services/` and `archive/aspirational_architecture/` remain absent Bucket 2 surfaces. Restore them only from verified candidates if a live-root gap appears.
- The Repo Library mirror can lag behind current HEAD until its refresh runs.
- Older local or remote branches can miss current Bucket 1 surfaces. Treat those branch warnings as lineage data unless one of those refs is being promoted back to live control-plane status.

## Verification

Run:

```powershell
.\FIX_WORKSTATION.ps1
```

or:

```powershell
python scripts\verify_heart_restore_map.py --root .
```
