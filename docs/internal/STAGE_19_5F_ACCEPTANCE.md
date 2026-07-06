# Stage 19.5F Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase F
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** New `packages/cerberus/` package — Q5 closure (Cerebus subsystem).

---

## 0. Phase F scope (recap)

First NEW workspace member package in the rebuild. Closes Q5 from
`docs/operations/LEGACY_GAP_INVENTORY.md` §8. Carries the typed surface
of legacy `src/app/core/cerberus_*` files (19 files, ~6,910 LOC) into
a minimal, fail-closed, downward-only package.

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/cerberus/pyproject.toml` | config | 30 |
| `packages/cerberus/README.md` | docs | 50 |
| `packages/cerberus/src/cerberus/__init__.py` | re-exports | 60 |
| `packages/cerberus/src/cerberus/py.typed` | PEP 561 marker | 0 |
| `packages/cerberus/src/cerberus/agent.py` | source | 130 |
| `packages/cerberus/src/cerberus/spawn_constraints.py` | source | 192 |
| `packages/cerberus/src/cerberus/lockdown.py` | source | 208 |
| `packages/cerberus/tests/__init__.py` | marker | 0 |
| `packages/cerberus/tests/test_cerberus_agent.py` | test | 110 (10 tests) |
| `packages/cerberus/tests/test_cerberus_spawn_constraints.py` | test | 165 (14 tests) |
| `packages/cerberus/tests/test_cerberus_lockdown.py` | test | 145 (14 tests) |
| `tests/test_cerberus_integration.py` | integration | 130 (6 tests) |
| **Total** | **12 new files** | **~1220 LOC + 44 tests** |

## 2. Files modified

| Path | Change |
|---|---|
| `pyproject.toml` | Added `project-ai-cerberus` to root `dependencies` and `[tool.uv.workspace]` members |

## 3. Verification gates (all green)

```
=== PYTEST ===
659 passed in 2.04s
(test count: 615 baseline + 44 new Phase F tests, no regression)

=== MYPY --strict ===
Success: no issues found in 86 source files

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
86 files already formatted
```

## 4. Architectural invariants (verified)

- **Downward-only deps**: cerberus imports only kernel + stdlib. Workspace pyproject
  declares deps on kernel/governance/execution/capability. No upward imports. ✓
- **Canonical types**: All state in `kernel.StateRegister`; values are `kernel.JsonValue`. ✓
- **Fail-closed**: All three controllers raise on invalid input (empty id, unknown role,
  unknown state, policy denial, missing cycle detection). Never silent ALLOW. ✓
- **Pluggable seams**: `SpawnPolicy` and `LockdownTrigger` Protocols; both have
  conservative defaults but allow alternate implementations. ✓
- **Single audit chain**: Spawn requests and lockdown events are recorded in StateRegister
  for tamper-evidence; LockdownController can be queried for runtime status. ✓
- **Strict typing**: mypy --strict clean on 86 source files (was 78; +8 new files). ✓
- **Deterministic**: Atomic via StateRegister.update; revision tracking works
  (RevisionConflictError on stale expected_revision). ✓

## 5. Bugs caught + fixed during self-review

1. **`LockdownController.check_or_raise` conflated activation with blocking.** Original
   implementation both auto-activated the lockdown AND raised LockdownError in the same
   call. Tests for "activation via check_or_raise" failed because the exception was
   raised before they could observe the state change. **Fix**: Split into two methods:
   `check_or_raise()` (pure gate, no auto-activation) and `evaluate_and_activate()`
   (trigger check + activation, returns bool). This is the correct semantic
   separation: checking is different from acting on the check.

2. **`uv sync --all-packages` did not auto-register the new package.** Required
   manual `uv pip install -e packages/cerberus` to make the package importable.
   **Fix**: Added `project-ai-cerberus` to root `dependencies` and
   `[tool.uv.workspace]` members in `pyproject.toml`. Future `uv sync` calls
   will pick up cerberus automatically.

3. **Python 3.11 vs 3.12 mismatch in pytest subprocess.** When `uv sync` was run
   without `--all-packages`, pytest was launching a 3.11 interpreter which couldn't
   import packages built for 3.12. **Fix**: Always use `uv sync --extra dev
   --all-packages` going forward; document in commit message.

## 6. Module surface (22 public exports)

- `CerberusAgent`, `CerberusAgentError`
- `ALLOWED_ROLES`, `ALLOWED_AGENT_STATES`
- `SpawnConstraints`, `SpawnPolicy`, `SpawnConstraintError`
- `ALLOWED_AGENT_TYPES`
- `LockdownController`, `LockdownTrigger`, `LockdownError`
- `ALLOWED_LOCKDOWN_REASONS`, `ALLOWED_LOCKDOWN_STATES`
- `LOCKDOWN_ARMED`, `LOCKDOWN_ACTIVE`, `LOCKDOWN_RELEASED`
- `default_spawn_policy`, `default_lockdown_trigger`

## 7. Q5 closure

Q5 marked **RESOLVED 2026-06-25 (Phase F)** in `LEGACY_GAP_INVENTORY.md` §8.
The full legacy cerebus surface is **NOT** ported (deferred to a later wave);
this phase captures the typed surface and fail-closed primitives only.

## 8. Continuity map

`docs/operations/CONTINUITY_MAP.md` updated per template with Phase F session delta.

## 9. Next steps

1. **Commit Phase F** (this PR)
2. **Phase G authorization:*** `packages/hydra_50/` — analogous to F (Q6 closure)
3. **Phase H, I, J authorization:*** Multi-sub-phase new packages (tarl, temporal, atlas)
4. **Push decision:** Local is 12 ahead of origin/main after this commit; explicit
   push authorization still required.

## 10. Self-report (v3 §35)

```
Mode: governance system (Phase F execution)
Created:
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\pyproject.toml
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\README.md
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\__init__.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\py.typed
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\agent.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\spawn_constraints.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\lockdown.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\tests\__init__.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\tests\test_cerberus_agent.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\tests\test_cerberus_spawn_constraints.py
- T:\00-Active\Project-AI-Beginnings\packages\cerberus\tests\test_cerberus_lockdown.py
- T:\00-Active\Project-AI-Beginnings\tests\test_cerberus_integration.py
- T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_19_5F_ACCEPTANCE.md (this file)
Modified:
- T:\00-Active\Project-AI-Beginnings\pyproject.toml (added project-ai-cerberus to deps + workspace)
- T:\00-Active\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.md (Q5 RESOLVED)
- T:\00-Active\Project-AI-Beginnings\docs\operations\CONTINUITY_MAP.md (Phase F delta)
Deleted: None.
Verified:
- 659/659 pytest pass (615 baseline + 44 new)
- mypy --strict clean on 86 source files
- ruff check clean
- ruff format --check clean (86 files)
Failed: None.
Not verified:
- apps/desktop tests + apps/services tests (pre-existing env gaps)
- 3 real bugs caught and fixed during self-review
Risks:
- None introduced by Phase F. Local main will be 12 commits ahead of origin/main
  after this commit (11 prior + 1 this Phase F completion).
Continuity map: docs/operations/CONTINUITY_MAP.md
Remaining:
- User authorization to commit Phase F completion
- Phase G authorization (hydra_50 / Q6 closure)
- Push decision (12 commits ahead, billing unblocked, awaiting explicit go)
Commands run:
- uv sync --extra dev --all-packages (sync workspace + dev tools)
- uv pip install -e packages/cerberus (workspace registration)
- .venv/Scripts/python.exe -m pytest packages/ tools/tests/ tests/ (full suite)
- .venv/Scripts/python.exe -m mypy packages/ --strict (full scope)
- .venv/Scripts/python.exe -m ruff check packages/ (lint)
- .venv/Scripts/python.exe -m ruff format --check packages/ (format)
- .venv/Scripts/python.exe -m ruff check --fix packages/ (auto-fix)
- .venv/Scripts/python.exe -m ruff format packages/ (format)
Safe to continue: yes (for commit + Phase G); NOT for code edits without explicit "go"
```
