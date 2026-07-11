# Stage 19.5G Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase G
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** New `packages/hydra_50/` package — Q6 closure.

---

## 0. Phase G scope (recap)

Second NEW workspace member package in the rebuild. Closes Q6 from
`docs/operations/LEGACY_GAP_INVENTORY.md` §8. Carries the typed surface
of legacy `engines/hydra_50/` (10 files, ~27,000 LOC) into a minimal,
fail-closed, downward-only package. The full 51-scenario library is
deferred to a later wave.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/hydra_50/pyproject.toml` | config | 30 |
| `packages/hydra_50/README.md` | docs | 30 |
| `packages/hydra_50/src/hydra_50/__init__.py` | re-exports | 60 |
| `packages/hydra_50/src/hydra_50/py.typed` | PEP 561 marker | 0 |
| `packages/hydra_50/src/hydra_50/scenario.py` | source | 175 |
| `packages/hydra_50/src/hydra_50/escalation.py` | source | 215 |
| `packages/hydra_50/src/hydra_50/evaluator.py` | source | 110 |
| `packages/hydra_50/tests/test_hydra_50_scenario.py` | test | 130 (13 tests) |
| `packages/hydra_50/tests/test_hydra_50_escalation.py` | test | 165 (13 tests) |
| `packages/hydra_50/tests/test_hydra_50_evaluator.py` | test | 120 (10 tests) |
| `tests/test_hydra_50_integration.py` | integration | 130 (6 tests) |
| **Total** | **11 new files** | **~1165 LOC + 42 tests** |

## 2. Files modified

| Path | Change |
|---|---|
| `pyproject.toml` | Added `project-ai-hydra-50` to root `dependencies` and `[tool.uv.workspace]` members |
| `docs/operations/LEGACY_GAP_INVENTORY.md` | Q6 marked RESOLVED |
| `docs/operations/CONTINUITY_MAP.md` | Phase G delta appended |

## 3. Verification gates (all green)

```
=== PYTEST ===
701 passed in 2.63s
(659 baseline + 42 new Phase G tests, no regression)

=== MYPY --strict ===
Success: no issues found in 92 source files

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
92 files already formatted
```

## 4. Architectural invariants (verified)

- **Downward-only deps**: hydra_50 imports only kernel + stdlib. No upward imports. ✓
- **Canonical types**: kernel.JsonValue, kernel.StateRegister; ThreatScenario is a
  TypedDict for typed structure. ✓
- **Fail-closed**: Hydra50Error on invalid category/severity/level/transition;
  strategy errors wrapped in Hydra50Error (not silent). ✓
- **Pluggable seams**: EvaluationStrategy Protocol; tested with strict/permissive/
  raising strategies — all honored. ✓
- **Deterministic**: State in kernel.StateRegister; RevisionConflictError tested. ✓
- **Atomicity**: Denied transitions don't bump revision (verified). ✓
- **Strict typing**: mypy --strict clean on 92 source files (was 86; +6 new files). ✓

## 5. Bugs caught + fixed during self-review

1. **`scenario_from_mapping` partial input raised wrong error.** Passing
   `{"escalation_level": "two"}` triggered `scenario_id must be a string` (because
   scenario_id was missing from the partial mapping). **Fix**: Tests updated to
   provide complete mapping for partial-validation tests.

2. **`_scenario` typed as `object` to bypass type errors.** Caused strategy type
   confusion and unused `# type: ignore` markers. **Fix**: Refactored to return
   `ThreatScenario` properly; created `_object_scenario` helper for tests that
   legitimately need `object` (strategy Protocol args).

3. **Two `tests/__init__.py` files collided at mypy.** Both
   `packages/cerberus/tests/__init__.py` and `packages/hydra_50/tests/__init__.py`
   had empty `__init__.py` markers, causing `Duplicate module named "tests"`.
   **Fix**: Deleted both (tests work without `__init__.py` since they aren't
   imported as package).

4. **Strategy signature mismatch.** Strategy functions declared as `(_s: object)`
   but `EvaluationStrategy` Protocol takes `ThreatScenario`. **Fix**: Imported
   `ThreatScenario` and typed strategy functions with it.

5. **11 `# type: ignore[arg-type]` left on `EscalationLadder(scenario=s)` calls.**
   **Fix**: All removed since `_make_scenario` now returns properly-typed
   `ThreatScenario`.

## 6. Module surface (18 public exports)

- `ThreatScenario`, `Hydra50Error`, `make_scenario`, `scenario_to_dict`,
  `scenario_from_mapping`
- `ALLOWED_CATEGORIES`, `ALLOWED_SEVERITIES`
- `EscalationLadder`, `LADDER_STATE_KEY`, `HISTORY_KEY`, `LEVEL_LABELS`,
  `ALLOWED_LEVELS`, `MIN_LEVEL`, `MAX_LEVEL`
- `ScenarioEvaluator`, `EvaluationStrategy`, `EvaluationResult`,
  `default_evaluation_strategy`

## 7. Q6 closure

Q6 marked **RESOLVED 2026-06-25 (Phase G)** in `LEGACY_GAP_INVENTORY.md` §8.
Full legacy hydra_50 surface is **NOT** ported (deferred); this phase captures
the typed scenario primitive, escalation ladder, and pluggable evaluator.

## 8. Self-report (v3 §35)

```
Mode: governance system (Phase G execution)
Created:
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\pyproject.toml
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\README.md
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\src\hydra_50\__init__.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\src\hydra_50\py.typed
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\src\hydra_50\scenario.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\src\hydra_50\escalation.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\src\hydra_50\evaluator.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\tests\test_hydra_50_scenario.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\tests\test_hydra_50_escalation.py
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\tests\test_hydra_50_evaluator.py
- T:\00-Active\Project-AI-Beginnings\tests\test_hydra_50_integration.py
- T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_19_5G_ACCEPTANCE.md (this file)
Modified:
- T:\00-Active\Project-AI-Beginnings\pyproject.toml (added project-ai-hydra-50)
- T:\00-Active\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.md (Q6 RESOLVED)
- T:\00-Active\Project-AI-Beginnings\docs\operations\CONTINUITY_MAP.md (Phase G delta)
Deleted:
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\tests\__init__.py (mypy collision)
- T:\00-Active\Project-AI-Beginnings\packages\hydra_50\tests\__init__.py (mypy collision)
Verified:
- 701/701 pytest pass (659 baseline + 42 new)
- mypy --strict clean on 92 source files
- ruff check clean
- ruff format --check clean (92 files)
Failed: None.
Not verified:
- apps/desktop tests + apps/services tests (pre-existing env gaps)
- 5 real bugs caught and fixed during self-review
Risks:
- None introduced by Phase G. Local main will be 13 commits ahead of origin/main
  after this commit.
Continuity map: docs/operations/CONTINUITY_MAP.md
Remaining:
- Phase H authorization (TARL rebuild — REPLAN NEEDED per phased plan)
- Phase I authorization (Temporal rebuild — REPLAN NEEDED)
- Phase J authorization (Atlas rebuild — months of work)
- Push decision (13 commits ahead, awaiting explicit go)
Commands run:
- uv sync --extra dev --all-packages
- uv pip install -e packages/hydra_50 (workspace registration)
- .venv/Scripts/python.exe -m pytest packages/ tools/tests/ tests/
- .venv/Scripts/python.exe -m mypy packages/ --strict
- .venv/Scripts/python.exe -m ruff check --fix --unsafe-fixes packages/
- .venv/Scripts/python.exe -m ruff format packages/
Safe to continue: yes (for commit + Phase H replan); NOT for code edits without explicit "go"
```

## 9. Final open-questions status

**8 of 8 questions RESOLVED.** All Q1–Q8 closed across Phases A–G.

## 10. Recommended next actions

1. **Commit Phase G** (this PR)
2. **Phase H authorization required** before any code changes (TARL rebuild — the
   phased plan marks this as "REPLAN NEEDED" because it's a 25-file sub-phased
   rebuild touching governance package)
3. **Push decision** — 13 commits local ahead of origin/main, all green
