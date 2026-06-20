# Stage 8 Acceptance: Execution

**Status:** ACCEPTED FOR DEVELOPMENT

- [x] `ExecutionGate.submit_action()` is the sole packaged actuation path.
- [x] AI-side governance runs before authority consumption or execution.
- [x] Only `ALLOW` proceeds; `DENY` and `ESCALATE` never invoke the executor.
- [x] Capability tokens bind actor, operation, and resource and are consumed once.
- [x] Missing, expired, mismatched, revoked, replayed, and malformed authority denies.
- [x] Governor and executor exceptions fail closed.
- [x] All paths append hash-chained kernel events.
- [x] Denials relay to Chimera without exposing private state.
- [x] Chimera relay failure remains denied and is audit-visible.
- [x] Ruff and strict MyPy pass across the dependency chain.
- [x] Tests: `7 passed`; branch coverage: `100.00%`.
- [x] Wheel and source distribution build successfully at `0.0.0.dev0`.

Legacy execution source hashes are recorded in `STAGE_8_SOURCE_MAP.md`; no
legacy source was modified.
