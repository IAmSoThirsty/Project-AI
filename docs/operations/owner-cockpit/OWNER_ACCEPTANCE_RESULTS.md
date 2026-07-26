# Owner Acceptance Results

**Date:** 2026-07-25
**Profile:** P1 offline-first local
**Overall:** v0.0.3 released for single-user P1 Offline-First Local production.
Owner ratification of TS3-OCS-1.0 remains a separate decision.

| Acceptance surface | Result | Evidence |
| --- | --- | --- |
| Offline bundle integrity and exact images | Verified | `owner-offline-bundle-20260726T043554Z`; superseded by the later final bundle receipt |
| Fresh offline import after image-tag removal | Verified | `owner-start-20260726T034146Z` |
| 9/9 health and hardening | Verified | `owner-start-20260726T043445Z` |
| Local sign-in surface and instance identity | Verified | Browser DOM: `PROJECT-AI-LOCAL`, local-account sign-in, no cloud-login claim |
| Local state survives repeated stop/start | Verified | Closed bootstrap retained across repeated starts; restored DB reported `accounts=5`, `workflows=4` |
| Secret exposure checks | Verified | No secret values in `.env`, container environment/inspect, logs, encrypted store, or receipts |
| Encrypted full-state backup and isolated restore | Verified | `owner-backup-20260726T034400Z`, `owner-restore-20260726T034404Z` |
| Recovery rejects no-confirm/tamper/zip-slip | Verified | `Test-OwnerRecoveryNegativePaths.ps1` pass; failure receipts `...043827Z`, `...043829Z` |
| Genuine baseline → candidate | Verified | Candidate status receipt `owner-status-20260726T042621Z` |
| Genuine candidate → baseline rollback | Verified | Baseline status receipt `owner-status-20260726T043143Z` |
| Return to candidate | Verified | Candidate status receipt `owner-status-20260726T043438Z` |
| Signed-in release workflow | Verified | Exact-ZIP clean acceptance: initial Owner setup and governed workflow receipt |
| Manual release usability | Verified | Exact-ZIP release-operator acceptance on the supported Windows path |
| Standard ratification | Not ratified | See `RATIFICATION_RECORD.md` |

No result in this table promotes Kubernetes, cloud publication, remote backup, public ingress,
or external integrations into the P1 product.
