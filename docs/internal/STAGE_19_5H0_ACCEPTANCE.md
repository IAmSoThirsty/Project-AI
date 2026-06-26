# Stage 19.5H0 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase H (REPLAN AT START)
**Discovery:** `docs/internal/PHASE_H_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** Phase H0 envelope — discovery artifact + package skeleton only.
**No source code written.** Source modules deferred to H1/H2/H3.

---

## 0. Phase H0 scope (recap)

The phased plan marks Phase H as "REPLAN AT START OF PHASE." Per memory
rule "Discovery-first on rebuild directives," H0 establishes:
1. A discovery artifact documenting legacy TARL's structure (21 py / 3403 LOC / 14 subdirs).
2. A package skeleton (`pyproject.toml`, `README.md`, `__init__.py`, `py.typed`).
3. Workspace registration (deps + sources + members).
4. Verified dependency analysis: TARL legacy is **self-contained** (only stdlib + own submodules).

No actual TARL source code in H0. Source modules are deferred to H1 (types),
H2 (compiler/runtime), H3 (system/stdlib/ffi).

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/tarl/pyproject.toml` | config | 20 |
| `packages/tarl/README.md` | docs | 30 |
| `packages/tarl/src/tarl/__init__.py` | envelope | 10 |
| `packages/tarl/src/tarl/py.typed` | PEP 561 marker | 0 |
| `docs/internal/PHASE_H_DISCOVERY.md` | discovery | 250 |
| `docs/internal/STAGE_19_5H0_ACCEPTANCE.md` | this file | — |
| **Total** | **6 new files** | **~310 LOC** (mostly docs) |

## 2. Files modified

| Path | Change |
|---|---|
| `pyproject.toml` | Added `project-ai-tarl` to root `dependencies`, `[tool.uv.workspace]` members, and `[tool.uv.sources]` (with `workspace = true`) |

## 3. Verification gates (all green — no source, no regression)

```
=== PYTEST ===
718 passed in 2.17s
(no test changes; baseline preserved)

=== MYPY --strict ===
Success: no issues found in 93 source files
(was 92; +1 for tarl __init__.py)

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
93 files already formatted
```

## 4. Architectural invariants (verified at H0)

- **TARL legacy is self-contained.** Static analysis of `tarl/*.py` + `tarl/*/__init__.py`
  shows imports only from stdlib + tarl's own submodules. No upward imports into
  companion / governance / execution / capability. The new `packages/tarl/` can
  depend only on `kernel`. (Verified via `grep -rn "^import \|^from "` on legacy.)
- **Downward-only deps:** New package pyproject declares only `project-ai-kernel`.
- **Canonical types:** Will be used in H1 (`kernel.JsonScalar`, `kernel.JsonValue`).
- **Strict typing:** mypy --strict clean on 93 source files.

## 5. Sub-phase plan (Phase H = H0 + H1 + H2 + H3)

Per the phased plan directive, Phase H is split into 4 sub-phases.
Each is wave-bounded.

| Sub-phase | New source | Purpose | Status |
|---|---|---|---|
| H0 | 0 | Discovery + skeleton | ✓ THIS |
| H1 | 4 (spec, policy, core, diagnostics) | Foundational types | awaiting go |
| H2 | 5 (parser, validate, compiler, runtime, config) | Compile + execute | awaiting go |
| H3 | 5 (system, modules, stdlib, ffi, policies/default) | System layer | awaiting go |

Total: ~14 source files, ~28 file changes. Each sub-phase ends with all
gates green + acceptance record + commit.

## 6. Risks identified + mitigations

1. **TARL dependency surface:** *Mitigated* — confirmed self-contained in H0.
2. **State surface:** Will check in H1; if TARL needs persistent state, must use
   `kernel.StateRegister` (not custom).
3. **FFI bridge:** Likely aspirational in legacy. Will verify in H3; if empty,
   mark as placeholder rather than port.
4. **Fuzz harness:** `tarl/fuzz/fuzz_tarl.py` deferred entirely (no rebuild value).
5. **Tooling:** `tarl/tooling/` deferred — can be CLI in a separate phase.

## 7. Self-report (v3 §35)

```
Mode: governance system (planning — Phase H0 envelope)
Created:
- T:\Project-AI-Beginnings\docs\internal\PHASE_H_DISCOVERY.md
- T:\Project-AI-Beginnings\docs\internal\STAGE_19_5H0_ACCEPTANCE.md (this file)
- T:\Project-AI-Beginnings\packages\tarl\pyproject.toml
- T:\Project-AI-Beginnings\packages\tarl\README.md
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\__init__.py
- T:\Project-AI-Beginnings\packages\tarl\src\tarl\py.typed
Modified:
- T:\Project-AI-Beginnings\pyproject.toml (added project-ai-tarl to deps + workspace + sources)
Deleted: None.
Verified:
- 718/718 pytest pass (no regression)
- mypy --strict clean on 93 source files (was 92; +1 tarl source)
- ruff check clean
- ruff format --check clean (93 files)
- TARL legacy self-containment verified (grep on tarl/*.py + tarl/*/__init__.py)
Failed: None.
Not verified:
- Actual TARL source modules (deferred to H1/H2/H3)
- State surface (will check in H1)
Risks:
- Phase H is substantial; multi-sub-phase required
- New package skeleton only — no source code yet
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- User authorization to commit H0 envelope
- User authorization to start H1 (4 source files: spec, policy, core, diagnostics)
- User authorization for H2, H3 thereafter
- Phase I (Temporal) and Phase J (Atlas) authorizations
- Push decision (already pushed at 527ac12 — origin/main now in sync)
Commands run:
- uv sync --extra dev --all-packages
- uv run pytest
- uv run mypy packages/ --strict
- uv run ruff check --fix packages/
- uv run ruff format packages/
- uv run ruff check packages/
- uv run ruff format --check packages/
Safe to continue: yes (for commit + Phase H1); NOT for code edits without explicit "go"
```

## 8. Recommended next actions

1. **Commit Phase H0 envelope** (this PR) — `git commit -m "feat(stage-19.5H0): packages/tarl skeleton + discovery"`
2. **Phase H1 authorization required** — 4 source files (spec, policy, core, diagnostics) + tests
3. **Then Phase H2** — 5 source files (compiler, runtime, parser, validate, config) + tests
4. **Then Phase H3** — 5 source files (system, modules, stdlib, ffi, policies/default) + tests
5. **Then Phase I** — Temporal package (separate envelope, separate go)
6. **Then Phase J** — Atlas package (months of work, separate envelope)