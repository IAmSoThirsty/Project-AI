# Project-AI Owner Quickstart

**Released product:** Project-AI v0.0.3, P1 Offline-First Local, single Windows user.

Project-AI's production deployment is local and offline-first. The Control Center, governance
runtime, database, audit history, SWR/Atlas/TAAR surfaces, backup, and recovery path run on this
machine. Kubernetes and cloud services are optional additions and are not required.

## What you need

- Windows 11.
- Docker Desktop configured for Linux containers.
- At least 10 GB free disk space.
- For a disconnected installation: the prepared `Project-AI-Offline` bundle. It already contains
  every required container image; no registry login or internet connection is required.

## First offline installation

1. Download the four v0.0.3 release files: the ZIP and its `.sha256`, `.sig`, and `.pub`
   sidecars.
2. Verify them before extraction:

   ```powershell
   pwsh -File .\scripts\owner\Test-OfflineRelease.ps1 `
     -ArchivePath .\project-ai-p1-v0.0.3-windows-amd64.zip
   ```

3. Extract the verified offline bundle to a local folder.
4. Double-click **`Install Project-AI Offline.cmd`**.
5. Wait for the preflight, image import, and nine service readiness checks.
6. Open the exact URL printed by the launcher:

   `http://127.0.0.1:4175`

7. If Owner setup is required, enter the one-time setup key printed by the launcher. Save the
   recovery codes shown by the Control Center.

The launcher creates account-bound, DPAPI-encrypted credentials under `.owner-state/credentials`.
It projects them as ACL-restricted runtime files only while the stack is running. Secret values
are not written to `.env` or container environment variables.

## Offline upgrade on the same machine

Keep the existing installation folder and its `.owner-state` directory. After extracting the
candidate bundle to a separate folder, run:

```powershell
pwsh -File .\scripts\owner\Install-ProjectAIOffline.ps1 `
  -ExistingOwnerState "C:\path\to\current\Project-AI\.owner-state"
```

The installer verifies that it is retaining the same encrypted credential store before starting
the candidate against the retained Docker volumes. If the candidate folder already contains a
different credential store, installation fails closed.

## Daily use

- Start: double-click **`Start Project-AI.cmd`**.
- Status: double-click **`Project-AI Status.cmd`**.
- Stop and keep all data: double-click **`Stop Project-AI.cmd`**.
- Control Center: `http://127.0.0.1:4175`.

The normal owner journey is:

1. Sign in to the Control Center.
2. Read the Command Center condition and evidence freshness.
3. Use Atlas Replay or Atlas Projections for bounded analysis.
4. Create, review, approve, and execute an SWR request only through the governed workflow.
5. Inspect the resulting execution and audit receipts.

The interface does not invent work, evidence, health, or approval. Missing data is shown as
unknown, stale, unavailable, or blocked.

## Backup

With Project-AI running:

```powershell
pwsh -File scripts/owner/Backup-ProjectAI.ps1
```

The result is an encrypted `.paibak` archive containing PostgreSQL human/workflow state,
audit data, SWR bundles, a non-secret local configuration snapshot, a manifest, and SHA-256
digests. By default it is protected to the current Windows account with DPAPI. Use
`-PortablePassphrase (Read-Host -AsSecureString)` when the archive must be restorable after a
Windows reinstall or on another approved machine.

To include credentials, add `-IncludeCredentialStore`. They exist only inside the encrypted
archive. With `-PortablePassphrase`, restore re-protects them for the destination account, so the
archive can recover a Windows reinstall or another approved machine. Store that archive and its
passphrase separately in owner-controlled offline custody.

## Restore

Verify a backup without replacing current state:

```powershell
pwsh -File scripts/owner/Restore-ProjectAI.ps1 `
  -BackupPath .local/backups/<archive>.paibak `
  -ConfirmRestore
```

Restore a backup over a fresh or explicitly disposable local state:

```powershell
pwsh -File scripts/owner/Restore-ProjectAI.ps1 `
  -BackupPath .local/backups/<archive>.paibak `
  -ConfirmRestore `
  -ReplaceCurrentState
```

The default path verifies the restore in an isolated database, then removes that verification
database. Use `-KeepIsolatedDatabase` only when it must remain available for operator inspection.
`-ReplaceCurrentState` is destructive and prompts for confirmation. Every restore verifies archive
paths and every manifest digest before writing state.

## Stop versus erase

The normal stop path keeps PostgreSQL and audit volumes:

```powershell
pwsh -File scripts/owner/Stop-ProjectAI.ps1
```

To remove local runtime data after a verified backup:

```powershell
pwsh -File scripts/owner/Stop-ProjectAI.ps1 -RemoveData
```

The data-removal path is explicit and prompts before deleting Docker volumes. The encrypted
credential store is retained unless the owner separately removes it.

## Failure help

- **Docker engine not running:** start Docker Desktop and wait for its Linux engine to report
  ready.
- **Port 8000, 4173, 4174, or 4175 already in use:** stop the conflicting program and retry.
- **A service is unhealthy:** run `Project-AI Status.cmd`, then
  `docker compose -f compose.yaml -f compose.secrets.yaml logs --tail 100 <service>`.
- **Browser shows an old snapshot:** treat it as stale evidence. Use the Status path and wait for
  a new live gateway response.
- **Credentials cannot decrypt:** use the same Windows account, or supply the portable passphrase
  used when the store/backup was created.
- **Existing data but missing credentials:** startup fails before changing containers. Restore the
  prior `.owner-state/credentials` directory on the same Windows account, or restore an approved
  backup that includes the credential export. Do not generate replacement credentials for an
  existing database volume.

## What is not part of the product

The local product does not require a Kubernetes cluster, public ingress, registry publication,
cloud secret manager, monitoring CRDs, remote backup provider, or CAB. Those belong only to the
optional P2 hosted profile in
[`docs/deployment/DEPLOYMENT_MODEL.md`](docs/deployment/DEPLOYMENT_MODEL.md).

## Release record

The evidence-backed v0.0.3 P1 production result is maintained in
[`docs/deployment/OFFLINE_FIRST_READINESS.md`](docs/deployment/OFFLINE_FIRST_READINESS.md).
The exact release ZIP and sidecars remain the distribution source of truth.
