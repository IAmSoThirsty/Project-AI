# Stage 5 Acceptance: Kernel

**Status:** ACCEPTED FOR DEVELOPMENT

- [x] Workspace install and editable import report `0.0.0.dev0`.
- [x] Package uses only the Python standard library.
- [x] Canonical outcomes are exactly `ALLOW`, `DENY`, and `ESCALATE`.
- [x] Invariant evaluator faults become critical violations and fail closed.
- [x] Evidence, event chains, and state snapshots are SHA-256 content-bound.
- [x] Event replay verifies sequence, previous hash, and event hash.
- [x] State updates require the expected revision and restoration verifies integrity.
- [x] Trusted time rejects an observed clock rollback.
- [x] Ruff passes.
- [x] strict MyPy passes for source and tests.
- [x] Tests: `7 passed`; branch coverage: `99.60%`.
- [x] Wheel and source distribution build successfully.

Legacy source paths and hashes are recorded in `STAGE_5_SOURCE_MAP.md`. The
legacy repository was read only and remains unchanged.
