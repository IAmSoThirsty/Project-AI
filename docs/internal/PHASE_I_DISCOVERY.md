# Phase I Discovery + Sub-Phase Plan — packages/temporal/

**Status:** DISCOVERY + PLAN (no code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase I ("REPLAN AT START OF PHASE")
**Date:** 2026-06-25
**Source-of-truth:** `T:\Project-AI-main\temporal\` (read-only)
**Target:** New `packages/temporal/` workspace member

---

## 0. Why discovery-first here

The phased plan marks Phase I as "REPLAN AT START OF PHASE." Legacy
temporal has architectural differences from prior phases:

- 8 Python files / 2459 LOC / 2 subdirs (`temporal/` + `temporal/workflows/`)
- Depends on **`temporalio`** SDK (external dep, NOT in workspace)
- Uses Temporal workflow/activity annotations (`@activity.defn`, `@workflow.defn`)
- Async-first (`async def` everywhere)
- ~20 distinct workflow/activity functions across 5 modules

Without scoping, Phase I risks scope creep identical to what Phase H
avoided via sub-phasing.

---

## 1. Legacy temporal surface inventory

| File | LOC | Purpose | Port priority |
|---|---|---|---|
| `temporal/__init__.py` | 19 | Package marker + re-exports | **I0** (envelope) |
| `temporal/workflows/__init__.py` | 19 | Workflows package marker | **I0** |
| `temporal/workflows/activities.py` | 224 | Activity definitions (`run_triumvirate_pipeline`) | **I1** |
| `temporal/workflows/triumvirate_workflow.py` | 280 | Triumvirate workflow definition | **I2** |
| `temporal/workflows/atomic_security_activities.py` | 446 | Atomic security activities | **I2** |
| `temporal/workflows/enhanced_security_workflows.py` | 448 | Enhanced security workflows | **I3** |
| `temporal/workflows/security_agent_activities.py` | 517 | Security agent activities | **I3** |
| `temporal/workflows/security_agent_workflows.py` | 506 | Security agent workflows | **I3** |
| **Total** | **2459** | | |

**Dependencies of temporal:**
- `temporalio.workflow`, `temporalio.activity` (workflow/activity decorators)
- `temporalio.common.RetryPolicy` (retry configuration)
- stdlib (`hashlib`, `json`, `logging`, `tarfile`, `uuid`)
- All workflow files use `@activity.defn` and `@workflow.defn` decorators

---

## 2. Architectural challenge: temporalio SDK

**The legacy depends on the external `temporalio` SDK.** Three options:

### Option A: Add temporalio as a real dependency

**Pros:**
- Workflows run for real
- Genuine durable execution

**Cons:**
- Adds heavy external runtime (workers, activities, async event loop)
- The `temporalio` package is large (~10MB) and complex
- Adds an external service dependency for "running" temporal
- The new package `temporal` would NOT be a leaf (depends on external SDK)

### Option B: Build abstraction layer (Protocol-based)

**Pros:**
- Optional SDK; workflows are typed contracts
- Tests can run without SDK
- Future-compatible with temporalio or other orchestrators

**Cons:**
- More code
- The decorators `@activity.defn` need translation

### Option C: Port workflow SHAPE without runtime

**Pros:**
- Smallest scope
- Tests are pure Python; no external deps
- Sets up future runtime integration

**Cons:**
- Workflows don't actually execute (just definitions)
- Need to revisit when real runtime is needed

### Recommended: **Option C** for Phase I (minimum viable port)

Capture the workflow/activity **shape**:
- Typed request/response dataclasses
- Workflow definitions as Protocols (not decorators)
- Activity definitions as typed functions
- Test that composition is well-formed

Defer real runtime (Option A or B) to a later wave.

---

## 3. Architectural invariants (AGENTS.md v3)

temporal rebuild must respect:
- **Downward-only deps**: temporal may import from `kernel` + stdlib only.
  NO external SDK in the minimum viable port (Option C).
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue for any
  JSON-interchangeable state.
- **Fail-closed**: invalid workflow inputs → TemporalError. Never silent.
- **Pluggable seams**: Activity Protocol + Workflow Protocol.
- **Deterministic**: workflows produce same output for same input.
- **Strict typing**: mypy --strict clean.

---

## 4. Sub-phase plan (REPLAN)

Per the phased plan's directive ("I1, I2" — sub-phasing required), I'm
splitting Phase I into 3 sub-phases plus a discovery envelope.

### Phase I0 — Discovery + skeleton (this turn)

**Scope:** Discovery artifact + package skeleton + workspace registration
**New source files:** 0 (only `pyproject.toml`, `README.md`, `__init__.py`,
`py.typed`, `__init__.py` for `workflows/` subdir)
**File changes:** ≤5
**Tasks:**
1. Write this discovery doc (done)
2. Create `packages/temporal/` package skeleton
3. Register in `pyproject.toml` workspace + sources
4. Verify all gates still green (no source changes = no regression)
5. Write `docs/internal/STAGE_19_5I0_ACCEPTANCE.md`
6. Commit Phase I0

### Phase I1 — Activities + dataclasses (typed surface)

**Scope:** Typed request/response dataclasses for the activity layer.
**New source files:** 3 (`dataclasses.py`, `activities.py`, `__init__.py` updates)
**Tasks:**
1. `packages/temporal/src/temporal/dataclasses.py` — `TriumvirateRequest`,
   `SecurityAgentRequest`, etc. (typed primitives from legacy)
2. `packages/temporal/src/temporal/activities.py` — Activity definitions
   as plain Python functions (no SDK decorators), wrapped in Protocol
3. `packages/temporal/tests/test_temporal_activities.py` — unit tests
4. Integration test
5. Commit Phase I1

### Phase I2 — Triumvirate workflow + atomic security

**Scope:** Workflow definitions for triumvirate pipeline + atomic security
**New source files:** 2 (`triumvirate_workflow.py`, `atomic_security.py`)
**Tasks:**
1. Triumvirate workflow Protocol + minimal implementation
2. Atomic security activity wrappers
3. Tests
4. Commit Phase I2

### Phase I3 — Enhanced security + security agent workflows

**Scope:** Remaining workflow surface
**New source files:** 2 (`enhanced_security.py`, `security_agent.py`)
**Tasks:**
1. Enhanced security workflows + activities
2. Security agent workflows + activities
3. Tests
4. Commit Phase I3

### Deferred (out of scope for I):
- Real temporalio SDK integration (Option A/B)
- Durable execution runtime
- Worker process
- `.thirsty` workflow data (already archived in Phase A)

---

## 5. Estimated file count

| Sub-phase | New source | New test | Init modify | Other | Total |
|---|---|---|---|---|---|
| I0 | 0 | 0 | 0 | pyproject, README, py.typed, this doc | 4-5 |
| I1 | 2 | 1 | 1 | 1 integration test | 5 |
| I2 | 2 | 1 | 1 | 1 integration test | 5 |
| I3 | 2 | 1 | 1 | 1 integration test | 5 |
| **Total** | **6** | **3** | **3** | **3** | **~20** |

Each sub-phase is wave-bounded (≤3 source files per sub-wave, well within
the established 5-file limit).

---

## 6. Risks and open questions

1. **temporalio SDK dependency** — *Resolved*: Option C defers real SDK.
2. **Async semantics** — Legacy uses `async def` everywhere. The minimum
   port may need async/sync duality (async for SDK compat, sync for tests).
3. **Workflow vs activity boundary** — In legacy, workflows orchestrate
   activities. The minimum port must preserve this two-layer pattern.
4. **RetryPolicy semantics** — Legacy uses `temporalio.common.RetryPolicy`.
   The minimum port captures the configuration as a typed dataclass; actual
   retry enforcement deferred.
5. **Correlation IDs** — Legacy uses uuid for correlation. The minimum port
   preserves this via `kernel.uuid4()` (or stdlib).

---

## 7. Recommended authorization scope

> "Proceed with Phase I0 only (discovery skeleton). Stop and produce
> I0 acceptance record + Phase I1 plan before continuing."

This preserves the wave-bounded pattern that worked for Phases A–H:
I0 sets the envelope (≤5 files, all gates green), I1 brings typed
primitives, I2 brings workflows, I3 brings the system layer.

---

## 8. Self-report (v3 §35)

```
Mode: governance system (planning — Phase I discovery)
Created: docs/internal/PHASE_I_DISCOVERY.md (this file)
Modified: None.
Verified: temporal legacy surface inventoried (8 py, 2459 LOC, 2 subdirs).
Failed: None.
Not verified: temporalio SDK availability (deferred — using Option C).
Risks: substantial scope; multi-sub-phase required; SDK integration deferred.
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on I0 commit)
Remaining:
  - User authorization to start Phase I0 (this turn)
  - Per-sub-phase "go" for I1, I2, I3 thereafter
  - Phase J authorization (Atlas envelope — separate)
```