# Stage 19.5D Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase D
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Commit:** `a1dc9e8`
**Phase scope:** Phase D — companion NIRL state machine.

---

## 0. Phase D scope

Brings the NIRL (Near-term Inference / Relational Language — agent
state machine) layer to `packages/companion/`. One source module
plus extensive tests.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/companion/src/companion/nirl.py` | source | 199 |
| `packages/companion/tests/test_nirl.py` | tests | ~200 (22 tests) |
| `packages/companion/src/companion/__init__.py` | modified — 23 re-exports | — |

## 2. Public exports added

- `NIRLState` (Literal type)
- `NIRLTransition` Protocol
- `DefaultNIRLTransition`
- `NIRLController`

## 3. Architectural invariants (verified)

- **Downward-only deps**: companion imports only its own submodules +
  kernel.
- **Canonical types**: kernel types preserved.
- **Fail-closed**: invalid state transitions raise.
- **Pluggable seams**: NIRLTransition Protocol allows custom transitions.
- **Strict typing**: mypy --strict clean.

## 4. Bugs caught + fixed during self-review

- Protocol argument typing fixes (multiple instances)
- Protocol `__call__` typing required `# type: ignore[assignment]`
  on default args and `# type: ignore[operator]` on call sites

## 5. Gate results (at commit `a1dc9e8`)

| Gate | Result |
|---|---|
| pytest | 572 passed (550 + 22) |
| mypy --strict | clean on 74 source files |
| ruff check | clean |
| ruff format | clean |

## 6. Self-report (v3 §35)

```
Mode: governance system (Phase D execution)
Created:
- packages/companion/src/companion/nirl.py
- packages/companion/tests/test_nirl.py
Verified:
- 572/572 pytest pass (550 + 22)
- mypy --strict clean on 74 source files
- ruff check + format clean
Failed: Multiple (Protocol typing) — all fixed in-session.
Not verified: None.
Risks: None.
Continuity map: docs/operations/CONTINUITY_MAP.md (updated)
Remaining: Per-phase go for Phase E.
Commands run:
- uv run pytest
- uv run mypy packages/ --strict
- uv run ruff check packages/
- uv run ruff format packages/
Safe to continue: yes
```
