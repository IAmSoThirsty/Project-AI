# Project-AI v0.0.3 — P1 Offline-First Local

**Release date:** 2026-07-27
**Production profile:** P1 Offline-First Local
**Audience:** One Windows user
**Required runtime:** Windows 11 and Docker Desktop Linux containers

## Distribution

The release is distributed as five GitHub Release assets:

- `project-ai-p1-v0.0.3-windows-amd64.zip`
- `project-ai-p1-v0.0.3-windows-amd64.zip.sha256`
- `project-ai-p1-v0.0.3-windows-amd64.zip.sig`
- `project-ai-p1-v0.0.3-windows-amd64.zip.pub`
- `project-ai-p1-v0.0.3-manual-acceptance.json`

The ZIP contains the exact seven-image offline set, nine-service Compose
runtime, owner launchers, protected local-secret overlay, backup/restore tools,
license, notices, release metadata, and internal SHA-256 manifest. It requires
no registry pull or cloud login.

Verify the four files before extraction:

```powershell
pwsh -File .\scripts\owner\Test-OfflineRelease.ps1 `
  -ArchivePath .\project-ai-p1-v0.0.3-windows-amd64.zip
```

Release signing-key fingerprint:
`SHA256:rKRWH+iipbORKpYSUuK3zU2w8e9vcLr/2RbI/QUToE8`.

## Production capability

- First-run local Owner account and recovery codes.
- Loopback-only Control Center at `http://127.0.0.1:4175`.
- Governed Atlas and Sovereign War Room workflows with durable receipts.
- Local PostgreSQL, audit, and SWR persistence.
- DPAPI or passphrase-protected local credential store.
- Encrypted full-state backup, fail-closed restore, and recovery denial checks.
- Offline install, restart, upgrade, rollback, status, stop, and explicit
  removal controls.
- Read-only containers, dropped Linux capabilities, and
  `no-new-privileges` across the stack.

## Repairs included in the shipping archive

- Offline image builds run sequentially to avoid Docker Desktop BuildKit
  host-network deadlocks.
- PostgreSQL is started and awaited before local credential rotation.
- Containers with stale secret mounts from another extraction path are
  force-recreated while named data volumes are preserved.
- Python service health checks use the measured 120-second cold-import grace.
- Destructive restores repair `docker cp` ownership with a one-shot,
  `CAP_CHOWN`-only maintenance container before the hardened non-root API
  restarts.
- The exporter recreates ephemeral Compose secret files from the encrypted
  owner store before its post-build 9-service readiness check.
- Windows runtime-secret projections use an SID-scoped common-data path with
  explicit owner, Docker Desktop, SYSTEM, and administrator ACLs. This keeps
  the encrypted credential store private while allowing a fresh Windows user
  to start the shared Docker Desktop engine.
- A rebuild replaces only the selected versioned ZIP and its three derived
  sidecars after image/runtime readiness has passed.
- Startup continues to enforce `--pull never` for offline installation.

## Security and visual gate refresh

- `pypdf` is locked at 6.14.2, resolving CVE-2026-59935,
  CVE-2026-59936, CVE-2026-59937, and CVE-2026-59938.
- PostCSS is forced to 8.5.23 and brace-expansion to 5.0.8.
- ESLint 10.8.0 removes the older minimatch dependency that could not consume
  the patched brace-expansion API.
- React Router remains at 7.18.1. GHSA-qwww-vcr4-c8h2 affects only unstable
  React Server Components paths that this Vite browser client does
  not import or execute. The exception is exact-version, exact-path,
  source-scanned, fail-closed, and expires on 2026-08-31. See
  `docs/security/NODE_DEPENDENCY_AUDIT_EXCEPTIONS.md`.
- Reviewed Windows and Linux operator-console screenshots are committed as the
  v0.0.3 visual-regression baselines.

## Scope boundary

This is a released production deployment only for P1 Offline-First Local.
Kubernetes, hosted ingress, cloud services, registry image publication,
remote monitoring, remote backup, and organizational CAB controls are future
optional P2 work. P1 does not authorize, imply, or depend on P2.
