# Operations

This folder holds live operations documents for Project-AI.

## Heart Restore

- `HEART_RESTORE_MAP_2026-04-02.md` is the source map for control-plane restore order.
- `HEART_RESTORE_STATUS_2026-04-17.md` records the current local verification result.
- `scripts/verify_heart_restore_map.py` validates the map against this checkout.
- `FIX_WORKSTATION.ps1` runs the verifier from the repo root.
- `IDE_Work_Spaces/project-ai-control-plane.code-workspace` opens the compact control-plane workspace.
- `wiki/09_Repo-Library/` is read as the local Mirror/Library and compared with live git state.

The restore order remains:

1. Control plane
2. Workspace wiring
3. Verification
4. Structural cleanup
