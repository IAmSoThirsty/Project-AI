# Stage 19.5 — packages/companion/ Rebuild Plan (SUPERSEDED)

> **Status:** SUPERSEDED by `docs/operations/STAGE_19_5_PHASED_PLAN.md`. Kept for historical reference only.
> **Reason:** User authorized integrating Q1–Q8 in 5-file waves. The single-wave companion plan here is now Phase C/D/E of the larger phased plan.
> **Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md` (active), `docs/operations/STAGE_19_ACCEPTANCE.md` (last accepted).
> **Standard:** Thirsty's Standard v3 via `AGENTS.md`.
> **Date:** 2026-06-25.
> **Source-of-truth:** `T:\00-Active\Project-AI-main` (soft-frozen, read-only).

---

## 1. Goal

Bring `packages/companion/` from a 93-LOC thin wrapper up to the minimum viable surface that matches the user-visible legacy subsystems called out by `STAGE_19_ACCEPTANCE.md` §9 priority #1: **identity, NIRL state machines, fates/memory, voice_bonding_protocol**.

This is a **rebuild**, not a `cp -r legacy/* companion/`. New code lives in the existing package, follows downward-only deps, exposes canonical types from `kernel`, reuses the existing `ExecutionGate` boundary.

## 2. Current state

`packages/companion/` (verified at commit `0d3128c`):

- `src/companion/__init__.py` — 7 LOC, exports `Companion`, `UPDATE_OPERATION`, `RESTORE_OPERATION`
- `src/companion/service.py` — 93 LOC, `Companion` class wrapping `ExecutionGate` for state update/restore
- `tests/test_companion.py` — 111 LOC, passes
- No `identity`, `nirl`, `fates`, or `voice_bonding` modules
- No `packages/companion/pyproject.toml` — package is configured via root `pyproject.toml` `[tool.uv.workspace]` members

Verified: 517 pytest pass across all packages; mypy --strict clean; ruff clean (last acceptance run).

## 3. Legacy surface to integrate (read-only audit)

| Legacy path | LOC | Status | Proposed target |
|---|---|---|---|
| `project_ai/engine/identity/identity_manager.py` | 82 | Stable | `companion/identity.py` |
| `docs/nirl/*` (spec + impl + state machines) | spec only | spec-only | `companion/nirl.py` (state-machine primitives) |
| `src/app/core/fates/fates.py` | (var) | Stable | `companion/fates.py` |
| `src/app/core/voice_bonding_protocol.py` | 686 | Large, complex | `companion/voice_bonding.py` (minimal façade, defer deep protocol semantics) |
| `src/app/core/bonding_protocol.py` | 763 | Adjacent to voice | **OUT OF SCOPE** — see §5 |

Total to integrate ≈ 4 modules. Fits within ≤5 new files wave budget.

## 4. Wave plan (one wave, ≤5 new files)

### Wave 1 — companion core expansion

New files (5):

1. `packages/companion/src/companion/identity.py`
   - `IdentityManager` class: stable identity primitives (id derivation, companion_id validation, alias map)
   - Reuses `kernel.StateRegister` for identity record
   - Imports only: `kernel` (canonical types)

2. `packages/companion/src/companion/nirl.py`
   - `NIRLStateMachine` Protocol + minimal `NIRL_IMPLEMENTATION.md` extracted state set
   - Pure-python, no I/O; deterministic transitions only
   - Imports only: stdlib

3. `packages/companion/src/companion/fates.py`
   - `FateLedger` over `kernel.StateRegister`, append-only
   - Operations: `record_fate`, `query_fates`, `prune_fates`
   - Imports only: `kernel`

4. `packages/companion/src/companion/voice_bonding.py`
   - `VoiceBondingSession` façade: minimal binding-state container
   - Deep protocol semantics (audio frames, codec, etc.) deferred — returns `NotImplementedError` with TODO pointer
   - Imports only: `kernel`, stdlib

5. `packages/companion/src/companion/__init__.py` (modify, not new)
   - Re-export new symbols
   - Backward-compatible (existing 3 exports unchanged)

New tests (parallel files, all in same wave):

- `tests/test_identity.py` — covers happy path + 3 invariant-violation cases
- `tests/test_nirl.py` — covers 5 canonical state transitions + 1 invalid transition (fail-closed)
- `tests/test_fates.py` — covers append + query + prune
- `tests/test_voice_bonding.py` — covers façade construction + deferral marker
- **1 cross-package integration test** in `tests/test_companion_integration.py` — `Companion` + `IdentityManager` + `FateLedger` against real `ExecutionGate`. Per 2026-06-24 accepted pattern: cross-package integration tests catch architectural bugs unit tests miss.

### Architectural invariants (per AGENTS.md)

- **Downward-only deps:** companion imports only from `kernel` (and stdlib). No import from `governance`, `execution`, `swr`, `atlas`, `api`, `cli`. The existing `service.py` imports `execution` — this is a known v1 wart; the new modules must NOT add to it. If `voice_bonding.py` truly needs an executor boundary, route through `ExecutionGate` parameter (passed in, not imported).
- **Canonical types:** use `kernel.JsonScalar`, `kernel.JsonValue`, `kernel.StateRegister`, `kernel.StateSnapshot`. No `dict[str, Any]` escape hatches.
- **Fail-closed:** every state-machine transition returns ESCALATE-or-reject on ambiguous input; no silent ALLOW.
- **Single audit chain:** all companion mutations route through existing `ExecutionGate.submit_action` → audit chain preserved.
- **Pluggable seams:** `IdentityManager` exposes a Protocol for the underlying id-derivation function; `NIRLStateMachine` is itself a Protocol.
- **Strict typing:** mypy --strict must remain clean.

### Forbidden in this wave

- Touching `bonding_protocol.py` (763 LOC, semantics TBD)
- Adding new dependencies
- Modifying any other package
- Adding new packages
- Modifying `pyproject.toml` workspace members
- Any deletion
- Any write to `T:\00-Active\Project-AI-main`

## 5. Open questions deferred (do not block this wave)

- Q5 (Cerebus) and Q7 (Cognition) from `LEGACY_GAP_INVENTORY.md` §8 affect companion's future surface but not this wave
- `bonding_protocol.py` integration — separate future wave after voice_bonding façade exists
- `packages/companion/pyproject.toml` separation — only if root pyproject grows unwieldy; not needed now

## 6. Acceptance gate (must all pass before commit)

Per `STAGE_19_ACCEPTANCE.md` §7:

```
=== TESTS ===
EXIT: 0
N passed in T.TTs   (where N ≥ 517 baseline + ~15 new tests)

=== MYPY --strict ===
EXIT: 0
Success: no issues found in packages/companion/ (+ the existing 32 source files)

=== RUFF check ===
EXIT: 0
All checks passed!

=== RUFF format check ===
EXIT: 0
M files already formatted

=== ARCHITECTURAL INVARIANTS ===
- Downward-only deps verified (no new upward imports)
- Canonical types used (no Any/dict escape)
- Fail-closed on all state transitions
- Single audit chain preserved
- Protocols in place for pluggable seams
```

Plus self-report per v3 §35 (`FINAL_REPORT_TEMPLATE.md`).

## 7. Acceptance record

Will be written to `docs/internal/STAGE_19_5_ACCEPTANCE.md` on completion, modeled on `docs/operations/STAGE_19_ACCEPTANCE.md` format, before the wave is committed.

## 8. Risk register

- **voice_bonding.py deferral** — Minimal façade returns `NotImplementedError` for deep ops. Risk: tests can't cover real audio semantics. Mitigation: clearly documented TODO; deferral is explicit, not silent.
- **NIRL state set** — Only the states mentioned in `NIRL_IMPLEMENTATION.md` will be implemented. Legacy may have additional states not yet enumerated. Mitigation: Protocol allows plugging in additional state machines later.
- **identity.py alias map** — Legacy uses simple dict; rebuild will use `kernel.StateRegister` for audit traceability. Risk: behavior change if alias map mutations weren't audited before. Mitigation: keep public method signatures identical to legacy `IdentityManager`; if divergence is found, document in acceptance report.
- **Wave budget** — 5 new files + 5 new test files + 1 integration test + 1 modified `__init__.py` = **12 file changes total**. This exceeds the "≤5 new files" budget stated in your 2026-06-24 acceptance. See §9.

## 9. Note on wave budget

Your 2026-06-24 accepted pattern was "≤5 new files per wave, all-gates-green end state." This plan produces **5 new source files + 5 new test files + 1 integration test + 1 modified `__init__.py`**. The source-file count is exactly 5; test files are separate. If you want strict ≤5 total file changes, the wave can be split into:

- Wave 1a: identity + fates (2 source + 2 test + 1 init modify = 5)
- Wave 1b: nirl + voice_bonding (2 source + 2 test + 1 integration = 5)

This is **a question to answer before authorization**, not a recommendation — both are valid.

## 10. Self-report (v3 §35)

```
Mode: governance system (planning)
Created: docs/operations/STAGE_19_5_COMPANION_REBUILD_PLAN.md (this file)
Modified: None.
Verified: legacy surface enumerated (read-only); current companion state captured (read-only)
Failed: None.
Not verified: full content of legacy voice_bonding_protocol.py (sample read; deep semantics deferred)
Risks: see §8; wave budget question §9
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
  - User authorization to execute this plan
  - Decision on §9 wave-budget split (single wave vs 1a/1b)
Safe to continue: no — awaiting user authorization
NOT for code edits without explicit "go" from user
```
