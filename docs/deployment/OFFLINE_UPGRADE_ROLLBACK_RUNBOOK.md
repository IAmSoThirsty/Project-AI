# Offline Upgrade, Rollback, and Recovery

This runbook applies to the P1 offline-first local product. It does not use Helm, a registry,
public ingress, or cloud infrastructure.

## Artifact contract

Each release is a `Project-AI-Offline` bundle containing:

- the exact seven-image Docker archive, including PostgreSQL;
- `compose.yaml` plus the protected-secret overlay;
- owner start/status/stop/backup/restore scripts;
- an `offline-bundle-manifest.json` with base commit, truthful source-tree status, image IDs,
  file hashes, and platform;
- a bundle SHA-256 recorded outside the archive.

An upgrade requires two retained artifacts:

- the currently accepted baseline bundle;
- the candidate bundle.

Do not call a same-image rebuild an upgrade rehearsal. Baseline and candidate image identities
must differ for a cross-version result.

## Before upgrade

1. Confirm the current stack is healthy with `Project-AI Status.cmd`.
2. Complete a real owner workflow and retain its receipt ID.
3. Create an encrypted full-state backup:

   ```powershell
   pwsh -File scripts/owner/Backup-ProjectAI.ps1
   ```

4. Copy the backup and its printed SHA-256 to owner-controlled offline custody.
5. Retain the accepted baseline offline bundle and its SHA-256.

## Upgrade

1. Extract the candidate bundle to a separate folder.
2. Verify its out-of-band SHA-256.
3. Run the installer with the current installation's retained encrypted owner state:

   ```powershell
   pwsh -File .\scripts\owner\Install-ProjectAIOffline.ps1 `
     -ExistingOwnerState "C:\path\to\current\Project-AI\.owner-state"
   ```

   The installer checks the internal manifest, refuses a conflicting credential store, imports
   the exact image IDs, starts with `--pull never`, and waits for readiness.
4. Confirm:
   - 9/9 services are healthy and hardened;
   - Owner login succeeds;
   - the pre-upgrade receipt remains visible;
   - a new Atlas/SWR owner workflow succeeds;
   - the audit record remains readable and integrity status is truthful.

If any check fails, stop. Preserve logs and the failure evidence receipt. Do not erase the
pre-upgrade backup.

## Rollback

1. Stop Project-AI while retaining volumes.
2. From the retained baseline bundle, import baseline images:

   ```powershell
   pwsh -File scripts/owner/Install-ProjectAIOffline.ps1 -ImagesOnly
   ```

3. Start the baseline with pulls disabled:

   ```powershell
   pwsh -File scripts/owner/Start-ProjectAI.ps1 -Offline -NoBrowser
   ```

4. If the baseline cannot safely read the upgraded state, stop it and restore the pre-upgrade
   backup with `-ReplaceCurrentState`.
5. Confirm Owner login, the pre-upgrade receipt, a real workflow, and local health.

## Recovery thresholds

- No registry or internet access is permitted during import/start verification.
- Every bundle and backup digest must match before use.
- Restore refuses unsafe archive paths and payload hash mismatches.
- Startup must reach all nine healthy containers within five minutes.
- No secret may appear in `.env`, container environment, logs, or evidence receipts.
- A failed owner journey leaves the candidate unaccepted and triggers baseline rollback.

## Evidence

Record baseline/candidate bundle hashes, image IDs, backup hash, command exits, health results,
owner workflow/receipt IDs, failure logs, rollback result, and recovery result in
`docs/deployment/OFFLINE_FIRST_READINESS.md` and the continuity map.
