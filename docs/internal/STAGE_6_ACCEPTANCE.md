# Stage 6 Acceptance: Governance

**Status:** ACCEPTED FOR DEVELOPMENT

- [x] Package depends downward on `project-ai-kernel` only.
- [x] PEP 561 typed-package metadata is present for kernel and governance.
- [x] Blocking/critical invariants deny before governor evaluation.
- [x] A single governor `DENY` unilaterally vetoes other votes.
- [x] `ESCALATE` votes and warning invariants remain `ESCALATE`.
- [x] Missing, faulting, or identity-mismatched governors deny fail closed.
- [x] Every result includes kernel SHA-256 evidence bound to the request and decision.
- [x] Ruff and strict MyPy pass.
- [x] Tests: `6 passed`; branch coverage: `98.43%`.
- [x] Wheel and source distribution build successfully at `0.0.0.dev0`.

Legacy provenance hashes are recorded in `STAGE_6_SOURCE_MAP.md`. No legacy
file or repository state was modified.
