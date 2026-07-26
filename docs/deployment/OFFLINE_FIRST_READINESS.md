# Offline-First Local Production Readiness

**Profile:** P1 - Offline-First Local
**Platform:** Windows, Docker Desktop Linux containers
**Release:** v0.0.3
**Audience:** Single user
**Current verdict:** Released production deployment for P1 offline-first local operation.
**P2 status:** Future optional work; not included or authorized by this release.

The exact ZIP is the versioned GitHub Release asset
`project-ai-p1-v0.0.3-windows-amd64.zip`. Its `.sha256`, `.sig`, and `.pub` sidecars are
co-published. A missing result remains `Not verified`; it is never inferred from a related gate.

| P1 requirement | Method | Evidence | Status |
| --- | --- | --- | --- |
| Offline installation artifact is complete and integrity-addressed | Build bundle, verify manifest, remove image tags, import with pulls disabled | Final bundle receipt and SHA-256 below | Verified |
| Cold start from all components stopped | `Start-ProjectAI.ps1 -Offline -NoBrowser` | Repeated owner-start receipts | Verified |
| Exact local UI destination | Reach `http://127.0.0.1:4175` from launcher output | Status receipts and browser DOM | Verified |
| 9/9 services ready and container hardening intact | Compose wait, local health probes, Docker inspect | `owner-start-20260726T043445Z` | Verified |
| Core work without internet/cloud dependency | Governed owner workflow while external integrations are unavailable | Exact-ZIP clean acceptance receipt | Verified |
| Local persistence survives stop/start | Retain volumes, restart, and re-read | Bootstrap stayed closed; restore reported `accounts=5`, `workflows=4` | Verified |
| Secrets protected locally | DPAPI/passphrase store; SID-scoped common-data runtime projections with explicit owner/docker-users ACLs; no values in `.env`, container env, logs, or evidence | Direct leak scans, fresh-Windows-user Docker start, and read-only secret mounts | Verified |
| Full-state encrypted backup | PostgreSQL + audit + SWR + config + portable credential export | `owner-backup-20260726T034400Z` | Verified |
| Fail-closed restore and recovery | Confirmation/tamper/zip-slip negatives plus isolated restore | `owner-restore-20260726T034404Z`; negative test pass | Verified |
| Local upgrade and rollback | Identified baseline/candidate artifacts and retained state | Status receipts `...042621Z`, `...043143Z`, `...043438Z` | Verified |
| Local health, logs, and degraded states | Status path plus runtime recovery | Status receipts; Docker deadlock recovered without volume loss | Verified with runtime risk |
| Graceful stop and explicit data removal | Stop retaining data; dry-run explicit volume-removal control | Stop receipts; `-WhatIf -RemoveData`; both volumes retained | Verified |
| Repeatable second start/workflow | Repeat cold start and owner workflow without hidden repair | Exact-ZIP clean acceptance receipt | Verified |
| Accessibility and owner usability | Automated checks plus manual release-operator acceptance | UI suite/build plus exact-ZIP manual acceptance receipt | Verified |
| Continuity and rollback evidence current | Continuity map and evidence receipts identify exact artifact/environment | 2026-07-25 P1 continuity entry | Verified |

## Released artifacts

- Production offline bundle:
  `project-ai-p1-v0.0.3-windows-amd64.zip`, published with `.sha256`, `.sig`, and `.pub`
  sidecars. Verify all four before extraction with
  `scripts/owner/Test-OfflineRelease.ps1`.
- Rollback baseline:
  `.local/offline-bundles/project-ai-p1-baseline-01c4ec74.zip`,
  SHA-256 `9fcc779fb0dda0e4794674097dcc066f40aa2dab4958f25551de30e7f6ef0832`.
- Current-machine recovery backup:
  `.local/backups/pre-owner-profile-20260725.paibak`,
  SHA-256 `4ac9363bd642200aa0e5f2b4a6928a89e31ab6c69a5f876f98f547d77cb8b85c`.
- Portable recovery acceptance: backup receipt `owner-backup-20260726T034400Z`, restore receipt
  `owner-restore-20260726T034404Z`, schema 2, and four credential names verified. The encrypted
  test archive was removed after acceptance because its random test passphrase was intentionally
  not retained.

## Acceptance scope

The v0.0.3 release acceptance covers a fresh local product state: installation from the exact
ZIP, initial Owner account setup, a governed Atlas/SWR workflow, restart, a repeated governed
workflow, encrypted backup, restore, and explicit removal. It does not reset or reinterpret
accounts from earlier development-state volumes.

Owner's Cockpit standard ratification remains a separate governance-standard decision. It does
not change the functional P1 release result and cannot be inferred from product acceptance.

## Verdict

> Project-AI v0.0.3 is released for P1 offline-first local production operation by a single
> Windows user. P2 hosted/Kubernetes/cloud work is future optional scope and is not authorized
> by this release.
