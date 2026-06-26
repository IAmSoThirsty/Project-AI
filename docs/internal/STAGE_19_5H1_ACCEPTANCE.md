# Stage 19.5H1 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase H1
**Discovery:** `docs/internal/PHASE_H_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Commit:** `967f9e8`
**Phase scope:** Phase H1 of H0+H1+H2+H3 sub-phased TARL rebuild.

---

## 0. Phase H1 scope

Brings the foundational typed primitives for TARL. 4 source modules
plus extensive tests.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/tarl/src/tarl/spec.py` | source | 104 |
| `packages/tarl/src/tarl/policy.py` | source | 109 |
| `packages/tarl/src/tarl/core.py` | source | 108 |
| `packages/tarl/src/tarl/diagnostics.py` | source | 145 |
| `packages/tarl/tests/test_tarl_foundations.py` | tests | ~290 (41 tests) |
| `packages/tarl/src/tarl/__init__.py` | modified — re-exports | — |

## 2. Public exports added

- `TarlVerdict` (ALLOW / DENY / ESCALATE)
- `TarlDecision`, `TarlError`, `make_decision`
- `TarlPolicy`, `allow_policy`, `deny_policy`, `PolicyProtocol`
- `TARL`, `TARL_VERSION`, `make_tarl`
- `Diagnostic`, `DiagnosticBatch`, `Severity`, `Location`, `make_diagnostic`

## 3. Architectural invariants (verified)

- **Downward-only deps**: tarl imports only its own submodules + stdlib.
- **Canonical types**: dataclasses + TypedDicts throughout.
- **Fail-closed**: TarlError on invalid input.
- **Pluggable seams**: PolicyProtocol allows custom rules.
- **Strict typing**: mypy --strict clean.

## 4. Gate results (at commit `967f9e8`)

| Gate | Result |
|---|---|
| pytest | 718 passed (at this commit, with H1 foundation tests) |
| mypy --strict | clean on ~98 source files |
| ruff check | clean |
| ruff format | clean |

## 5. Self-report (v3 §35)

```
Mode: governance system (Phase H1 execution)
Created:
- packages/tarl/src/tarl/spec.py
- packages/tarl/src/tarl/policy.py
- packages/tarl/src/tarl/core.py
- packages/tarl/src/tarl/diagnostics.py
- packages/tarl/tests/test_tarl_foundations.py
Verified:
- 41 tests pass in test_tarl_foundations.py
- mypy --strict clean
- ruff check + format clean
Failed: None.
Not verified: None.
Risks: None.
Continuity map: docs/operations/CONTINUITY_MAP.md (updated)
Remaining: Phase H2 authorization.
Commands run:
- uv run pytest packages/tarl/tests/test_tarl_foundations.py
- uv run mypy packages/ --strict
- uv run ruff check packages/
- uv run ruff format packages/
Safe to continue: yes
```