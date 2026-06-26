# Stage 19.5I0 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase I
**Discovery:** `docs/internal/PHASE_I_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** Phase I0 envelope — discovery artifact + package skeleton only.

---

## 0. Phase I0 scope (recap)

The phased plan marks Phase I as "REPLAN AT START OF PHASE." Per memory
rule "Discovery-first on rebuild directives," I0 establishes:
1. Discovery artifact documenting legacy temporal (8 py / 2459 LOC).
2. Critical finding: legacy depends on **`temporalio` SDK** (external).
3. Decision: **Option C** — port workflow/activity SHAPE without SDK
   (capture Protocols + dataclasses; defer real runtime).
4. Package skeleton (pyproject, README, __init__.py, workflows/__init__.py,
   py.typed).
5. Workspace registration.
6. Sub-phase plan: I1 (typed dataclasses + activities), I2 (workflows),
   I3 (security).

No source code in I0. Source modules deferred to I1/I2/I3.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/temporal/pyproject.toml` | config | 25 |
| `packages/temporal/README.md` | docs | 35 |
| `packages/temporal/src/temporal/__init__.py` | envelope | 10 |
| `packages/temporal/src/temporal/py.typed` | PEP 561 | 0 |
| `packages/temporal/src/temporal/workflows/__init__.py` | envelope | 7 |
| `docs/internal/PHASE_I_DISCOVERY.md` | discovery | 250 |
| `docs/internal/STAGE_19_5I0_ACCEPTANCE.md` | this file | — |
| **Total** | **7 new files** | **~330 LOC** (mostly docs) |

## 2. Files modified

| Path | Change |
|---|---|
| `pyproject.toml` | Added `project-ai-temporal` to deps, `[tool.uv.workspace]` members, `[tool.uv.sources]` |

## 3. Verification gates (all green — no source, no regression)

```
=== PYTEST ===
888 passed in 2.95s
(no test changes; baseline preserved)

=== MYPY --strict ===
Success: no issues found in 112 source files
(was 110; +2 for temporal __init__.py files)

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
112 files already formatted
```

## 4. Architectural decisions made in I0

**Option C chosen** for the temporalio SDK dependency:
- Workflow definitions = typed Protocols (no decorators)
- Activity definitions = typed Python functions
- Decorators (`@activity.defn`, `@workflow.defn`) deferred
- Real durable execution deferred to a later wave

**Justification:** Minimum viable port. Captures the shape of legacy
without adding a heavy external runtime. Future-proofs against
orchestrator changes.

## 5. Sub-phase plan (Phase I = I0 + I1 + I2 + I3)

| Sub-phase | New source | Purpose | Status |
|---|---|---|---|
| I0 | 0 | Discovery + skeleton | ✓ THIS |
| I1 | 2 | Dataclasses + activities | awaiting go |
| I2 | 2 | Triumvirate workflow + atomic security | awaiting go |
| I3 | 2 | Enhanced security + security agent | awaiting go |

Total: ~6 source files, ~20 file changes. Each sub-phase wave-bounded.

## 6. Risks identified

1. **temporalio SDK**: Resolved — Option C defers.
2. **Async semantics**: May need async/sync duality in I1.
3. **Workflow vs activity boundary**: Two-layer pattern preserved.
4. **RetryPolicy**: Captured as typed dataclass; enforcement deferred.
5. **Correlation IDs**: Will use `kernel.uuid4()` in I1.

## 7. Self-report (v3 §35)

```
Mode: governance system (planning — Phase I0 envelope)
Created:
- T:\Project-AI-Beginnings\docs\internal\PHASE_I_DISCOVERY.md
- T:\Project-AI-Beginnings\docs\internal\STAGE_19_5I0_ACCEPTANCE.md (this file)
- T:\Project-AI-Beginnings\packages\temporal\pyproject.toml
- T:\Project-AI-Beginnings\packages\temporal\README.md
- T:\Project-AI-Beginnings\packages\temporal\src\temporal\__init__.py
- T:\Project-AI-Beginnings\packages\temporal\src\temporal\py.typed
- T:\Project-AI-Beginnings\packages\temporal\src\temporal\workflows\__init__.py
Modified:
- T:\Project-AI-Beginnings\pyproject.toml (added project-ai-temporal)
Verified:
- 888/888 pytest pass (no regression)
- mypy --strict clean on 112 source files
- ruff check + format clean
- temporal legacy inventoried (8 py, 2459 LOC, 2 subdirs)
- Legacy depends on temporalio SDK; Option C chosen (no SDK)
Failed: None.
Not verified:
- async semantics design (deferred to I1)
- workflow/activity runtime (deferred — Option C)
Risks:
- Phase I is substantial; multi-sub-phase required
- Real SDK integration deferred indefinitely
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- User authorization to commit + push I0
- User authorization to start I1 (2 source files: dataclasses + activities)
- Phase J authorization (Atlas envelope — separate)
Commands run:
- uv sync --extra dev --all-packages
- uv run pytest
- uv run mypy packages/ --strict
- uv run ruff check --fix packages/
- uv run ruff format packages/
Safe to continue: yes (for commit + I1); NOT for code edits without explicit "go"
```

## 8. Recommended next actions

1. **Commit Phase I0 + push** (this turn)
2. **Phase I1 authorization required** — 2 source files (dataclasses + activities)
3. **Phase J authorization** — separate envelope for Atlas package
   (months of work)