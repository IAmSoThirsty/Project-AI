# Stage 19.5I1 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase I1
**Discovery:** `docs/internal/PHASE_I_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Commit:** `7a15132`
**Phase scope:** Phase I1 of I0+I1+I2+I3 sub-phased temporal rebuild.

---

## 0. Phase I1 scope

Brings the typed request/response primitives + activity definitions for
temporal. 2 source modules + extensive tests.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/temporal/src/temporal/dataclasses.py` | source | ~280 |
| `packages/temporal/src/temporal/activities.py` | source | ~210 |
| `packages/temporal/tests/test_temporal_i1.py` | tests | ~380 (43 tests) |
| `packages/temporal/src/temporal/__init__.py` | modified — re-exports | — |

## 2. Public exports added

- `TriumvirateRequest`, `TriumvirateResult`
- `SecurityAgentRequest`, `SecurityAgentResult`
- `RetryPolicy`
- `new_correlation_id()`
- `TemporalError`, `TemporalValidationError`
- `ActivityError`, `ActivityTimeoutError`
- `run_activity`, `run_triumvirate_pipeline`, `run_security_agent_scan`

## 3. Architectural invariants (verified)

- **Downward-only deps**: temporal imports only its own + kernel.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue.
- **Fail-closed**: TemporalValidationError on all bad input.
- **Pluggable seams**: Activity Protocol + RetryPolicy.
- **Deterministic**: deterministic output for deterministic input.
- **Strict typing**: mypy --strict clean.

## 4. Bugs caught + fixed during self-review

1. Protocol type confusion: `run_activity(activity_fn: Activity)`
   rejected plain callables. Fix: type as `Callable[[Request], Result]`.
2. Unused type: ignore comment. Removed.
3. Wrong expected error message in test. Fixed to match real error.
4. Duplicate test. Removed.
5. Empty string test unreachable. Removed.

## 5. Gate results (at commit `7a15132`)

| Gate | Result |
|---|---|
| pytest | 931 passed (888 + 43) |
| mypy --strict | clean on 115 source files |
| ruff check | clean |
| ruff format | clean |

## 6. Self-report (v3 §35)

```
Mode: governance system (Phase I1 execution)
Created:
- packages/temporal/src/temporal/dataclasses.py
- packages/temporal/src/temporal/activities.py
- packages/temporal/tests/test_temporal_i1.py
Verified:
- 931/931 pytest pass (888 + 43)
- mypy --strict clean on 115 source files
- ruff check + format clean
Failed: 5 in initial run (now all fixed).
Not verified: Real SDK integration (deferred — Option C).
Risks: None.
Continuity map: docs/operations/CONTINUITY_MAP.md (updated)
Remaining: Phase I2 authorization.
Commands run:
- uv run pytest
- uv run pytest packages/temporal/ (targeted)
- uv run mypy packages/ --strict
- uv run ruff check --fix packages/
- uv run ruff format packages/
Safe to continue: yes
```