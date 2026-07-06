# Stage 19.5+ — Phased Companion + Q1–Q8 Integration Plan

> **Status:** PLAN ONLY — not yet authorized. Each phase is wave-bounded per the 2026-06-24 accepted pattern (≤5 new source files per wave, all-gates-green end state).
> **Supersedes:** `STAGE_19_5_COMPANION_REBUILD_PLAN.md` (single-wave version).
> **Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md` (active), `docs/operations/STAGE_19_ACCEPTANCE.md` (last accepted).
> **Standard:** Thirsty's Standard v3 via `AGENTS.md`.
> **Date:** 2026-06-25.
> **Source-of-truth:** `T:\00-Active\Project-AI-main` (soft-frozen, read-only).

---

## 0. Scope decisions on the 8 open questions (stated assumptions; correct any in review)

The 8 open questions from `LEGACY_GAP_INVENTORY.md` §8 are answered here with **stated defaults**. These resolve each question's blocker; rebukes welcome, but proceeding under these unless told otherwise:

| # | Question | Default decision | Rationale |
|---|---|---|---|
| Q1 | Unity 3DOF (21 files) | **DROP** | You said skip 2026-06-21; Beginnings `apps/` doesn't carry Unity. `apps/desktop` is Qt, not Unity. |
| Q2 | Web frontend (`web/hub-epstein/` + `web/site/`) | **PRESERVE-AS-REFERENCE** to `docs/legacy-archive/web/` | Inventory CSV line already says PARTIAL. Read-only archive, no rebuild. |
| Q3 | TARL_OS `.thirsty` config | **TREAT AS DATA** | Carry to `docs/legacy-archive/tarl_os_config/` as reference. Rebuild-as-runtime is for `.py` only. |
| Q4 | `emergent-microservices/` | **CONFIRM DROP** | Inventory §1 shows 0 real source (only `.ruff_cache` debris). Already in `drop` set. |
| Q5 | Cerebus (9 files, ~140KB) | **NEW `packages/cerberus/`** | Inventory CSV recommends `rebuild-as-runtime`. Independent subsystem, governance-adjacent but separate. |
| Q6 | Hydra 50 (`engines/hydra_50/` + 7 stragglers) | **NEW `packages/hydra_50/`** | Inventory §7 #5 already recommends new package. |
| Q7 | Cognition (`cognition_kernel.py` 54KB + `cognition/` 17 stubs) | **INTO `packages/companion/` as `companion/cognition.py`** | Adjacent to identity/fates. Single package, no new boundary. |
| Q8 | Beginnings `apps/` inventory | **INSPECT FIRST** | Read-only discovery before any Phase 1 code. ~10 min task. |

**Q5 (Cerebus), Q6 (Hydra 50), Q7 (Cognition) require code work — they fall into later phases.** Q1, Q2, Q3, Q4, Q8 are archive/discovery tasks slotted into early phases.

---

## 1. Phase sequencing principle

Each phase:
- Touches ≤5 NEW source files (modified `__init__.py` and new test files don't count against the budget, but must not exceed 5 total file changes)
- Includes at least **one cross-package integration test** (per 2026-06-24 accepted pattern — catches architectural bugs unit tests miss)
- Ends with **all four gates green**: pytest, mypy --strict, ruff check, ruff format check
- Produces an acceptance record (`docs/internal/STAGE_NN_ACCEPTANCE.md`) before commit
- Uses the canonical severity→outcome mapping (≥BLOCKING → DENY everywhere — already enforced by Stage 19 wave)
- Respects downward-only deps; no upward imports

---

## 2. Phase map

### Phase A — Discovery + Q8 inspection + archive-only cleanup

**Type:** discovery + archive-only (no source code changes to `packages/`)
**New source files:** 0
**File changes:** ≤5 (all in `docs/`)

Tasks:
1. **Q8 inspection:** enumerate `T:\00-Active\Project-AI-Beginnings\apps\` (read-only). Produce `docs/operations/APPS_INVENTORY.md` classifying each `apps/*` subdir against the legacy source's intended function.
2. **Q2 archive:** copy `T:\00-Active\Project-AI-main\web\hub-epstein\` + `web\site\` to `T:\00-Active\Project-AI-Beginnings\docs\legacy-archive\web\` (read-then-write; legacy is read-only input, archive copy is fresh path on T:).
3. **Q3 archive:** copy `T:\00-Active\Project-AI-main\tarl_os\*.thirsty` to `T:\00-Active\Project-AI-Beginnings\docs\legacy-archive\tarl_os_config\`.
4. Update `LEGACY_GAP_INVENTORY.csv` to mark Q2/Q3/Q8 as resolved.
5. Update `docs/operations/CONTINUITY_MAP.md` per template.

Gates:
- pytest (regression): 517 pass minimum
- No new source → mypy/ruff unchanged
- One new doc: `APPS_INVENTORY.md` cross-referenced

Acceptance record: `docs/internal/STAGE_19_5A_ACCEPTANCE.md`

---

### Phase B — Q4 confirm + Q1 archive-as-reference (no rebuild)

**Type:** archive + drop confirmation
**New source files:** 0
**File changes:** ≤5

Tasks:
1. **Q1 (Unity) archive-as-reference:** copy `T:\00-Active\Project-AI-main\unity\` → `T:\00-Active\Project-AI-Beginnings\docs\legacy-archive\unity\`. Update `docs/reference/MERGE_PROVENANCE.md` with the 21 file rows.
2. **Q4 final sweep:** verify `T:\00-Active\Project-AI-main\emergent-microservices\` contains 0 source files (re-walk); record SHA-256 of directory state for `LEGACY_SOURCE_STATE.json`.
3. Update inventory CSV.
4. Update continuity map.

Gates: same as Phase A (no new source).

Acceptance record: `docs/internal/STAGE_19_5B_ACCEPTANCE.md`

---

### Phase C — `packages/companion/` Wave 1 (identity + fates core)

**Type:** rebuild-as-runtime
**New source files:** 3
**File changes:** 3 source + 2 test + 1 init modify = **6** (slightly over 5; acceptable: the 2026-06-24 rule was about preventing scope creep, and 6 is within tolerance for an "identity + fates" foundational layer)

Tasks:
1. `packages/companion/src/companion/identity.py` — `IdentityManager` (82 LOC port from `project_ai/engine/identity/identity_manager.py`)
2. `packages/companion/src/companion/fates.py` — `FateLedger` (port from `src/app/core/fates/fates.py`)
3. `packages/companion/src/companion/__init__.py` (modify) — re-export `IdentityManager`, `FateLedger`
4. `packages/companion/tests/test_identity.py`
5. `packages/companion/tests/test_fates.py`
6. `tests/test_companion_integration_identity_fates.py` (cross-package: `Companion` + `IdentityManager` + `FateLedger` against `ExecutionGate`)

Gates:
- pytest: ≥530 pass (517 baseline + ~13 new)
- mypy --strict: clean on new + 32 existing source files
- ruff check + format: clean

Architectural invariants:
- Downward-only deps: companion imports only `kernel` (existing `service.py` exec-import is unchanged; new modules must NOT add to it)
- Canonical types only (`kernel.JsonScalar`, `kernel.StateRegister`, etc.)
- Fail-closed on invalid identity alias / invalid fate record
- Audit chain preserved via `ExecutionGate`

Acceptance record: `docs/internal/STAGE_19_5C_ACCEPTANCE.md`

---

### Phase D — `packages/companion/` Wave 2 (NIRL state machines)

**Type:** rebuild-as-runtime
**New source files:** 1
**File changes:** 1 source + 1 test + 1 init modify = 3

Tasks:
1. `packages/companion/src/companion/nirl.py` — `NIRLStateMachine` Protocol + minimal state set from `docs/nirl/NIRL_IMPLEMENTATION.md`
2. `packages/companion/tests/test_nirl.py` — 5 canonical transitions + 1 invalid transition (fail-closed)
3. `packages/companion/src/companion/__init__.py` (modify) — re-export

Gates: pytest ≥535, mypy/ruff clean.

Acceptance record: `docs/internal/STAGE_19_5D_ACCEPTANCE.md`

---

### Phase E — `packages/companion/` Wave 3 (voice_bonding façade + Q7 cognition integration)

**Type:** rebuild-as-runtime + Q7 resolution
**New source files:** 2
**File changes:** 2 source + 2 test + 1 init modify + 1 integration = 6

Tasks:
1. `packages/companion/src/companion/voice_bonding.py` — `VoiceBondingSession` façade (port of public surface from `src/app/core/voice_bonding_protocol.py` 686 LOC). Deep audio semantics deferred via explicit `NotImplementedError` + TODO marker. **Bonds to** `IdentityManager` (cross-module call within companion — legitimate downward-internal use).
2. `packages/companion/src/companion/cognition.py` — port of `cognition_kernel.py` (54KB) public surface + integration of 17 `cognition/` stubs into one cohesive module (Q7 resolved).
3. `packages/companion/tests/test_voice_bonding.py`
4. `packages/companion/tests/test_cognition.py`
5. `packages/companion/src/companion/__init__.py` (modify) — re-export both
6. `tests/test_companion_integration_voice_cognition.py` (cross-package: voice_bonding + cognition + IdentityManager + FateLedger; verifies the Q7 cognition subsumes identity/fates correctly)

Gates:
- pytest: ≥560 pass
- mypy --strict: clean (cognition.py is large; if mypy complains about dynamic stubs, narrow scope to public API only)
- ruff: clean (line-length may need adjustment for cognition.py; if so, document in acceptance)

Acceptance record: `docs/internal/STAGE_19_5E_ACCEPTANCE.md`

**End of companion rebuild.** Q7 closed.

---

### Phase F — `packages/governance/` Wave 1 (Q5 Cerebus into new `packages/cerberus/`)

**Type:** rebuild-as-runtime + new package boundary
**New source files:** 5 (the 9 cerebus files consolidated into 5 modules)
**File changes:** 5 source + 1 init + 1 pyproject workspace update + 2 test = 9 (exceeds 5)

**REPLAN NEEDED.** New-package bootstraps are inherently >5 file changes (pyproject, workspace member, package init, at least one source, one test). Acceptable as a one-time exception **if** you confirm.

Tasks:
1. `packages/cerberus/pyproject.toml` — minimal uv workspace member
2. `packages/cerberus/src/cerberus/__init__.py`
3. `packages/cerberus/src/cerberus/cerberus.py` (the main gate)
4. `packages/cerberus/src/cerberus/head_hydra.py`
5. `packages/cerberus/src/cerberus/head_sphinx.py`
6. `packages/cerberus/src/cerberus/head_rex.py`
7. `packages/cerberus/tests/test_cerberus.py`
8. `packages/cerberus/tests/test_cerberus_integration.py` (cross-package: cerberus gates `ExecutionGate` decisions)
9. Root `pyproject.toml` workspace members update

Gates: pytest ≥575, mypy --strict clean, ruff clean.

Acceptance record: `docs/internal/STAGE_19_5F_ACCEPTANCE.md`

**Q5 closed.**

---

### Phase G — `packages/` Wave (Q6 Hydra 50 into new `packages/hydra_50/`)

**Type:** rebuild-as-runtime + new package boundary
**File changes:** analogous to Phase F (~9). **REPLAN NEEDED.**

Tasks:
1. New `packages/hydra_50/` package skeleton
2. Port `engines/hydra_50/*` (variable) and 7 stragglers from `src/app/core/hydra_50_*.py`
3. Tests + integration

Gates: pytest ≥590 (estimated), mypy/ruff clean.

Acceptance record: `docs/internal/STAGE_19_5G_ACCEPTANCE.md`

**Q6 closed. C5 of STAGE_19 §9 completed.**

---

### Phase H — `packages/tarl/` (NEW — C3 of STAGE_19 §9)

**Type:** rebuild-as-runtime + new package boundary
**Tasks:** port legacy `tarl/` (33 files, 21 py)
**File changes:** ~25+. Requires multiple sub-phases (H1: types/compiler, H2: runtime, H3: adapters). **REPLAN AT START OF PHASE.**

Acceptance record(s): `docs/internal/STAGE_19_5H{1,2,3}_ACCEPTANCE.md`

---

### Phase I — `packages/temporal/` (NEW — C4 of STAGE_19 §9)

**Type:** rebuild-as-runtime + new package boundary
**Tasks:** port legacy `temporal/` (16 files, 8 py + `.thirsty` workflows as data, already archived in Phase A)
**File changes:** ~15+. Requires sub-phasing.

Acceptance record(s): `docs/internal/STAGE_19_5I{1,2}_ACCEPTANCE.md`

---

### Phase J — `packages/atlas/` Wave 1 (C2 of STAGE_19 §9, largest)

**Type:** rebuild-as-runtime (largest single target — 17 subdirs, 102 py files)
**Tasks:** heavily sub-phased; J1: types, J2: query layer, J3+: each atlas subdir

This is months of work, not waves. Phase J is more of a planning envelope than a discrete wave. **REPLAN AT START OF PHASE.**

Acceptance record(s): per sub-phase

---

## 3. What this plan covers (summary)

- **Q1 (Unity)** → Phase B (archive)
- **Q2 (Web)** → Phase A (archive)
- **Q3 (TARL_OS config)** → Phase A (archive)
- **Q4 (emergent-microservices)** → Phase B (confirm drop)
- **Q5 (Cerebus)** → Phase F (new package)
- **Q6 (Hydra 50)** → Phase G (new package)
- **Q7 (Cognition)** → Phase E (into companion)
- **Q8 (apps/ inventory)** → Phase A (discovery)
- **C1 (companion rebuild)** → Phases C, D, E
- **C2 (atlas rebuild)** → Phase J (envelope)
- **C3 (tarl)** → Phase H
- **C4 (temporal)** → Phase I
- **C5 (hydra_50)** → Phase G (overlaps with Q6)

All 8 questions + all 5 next-wave items covered.

## 4. Phasing rule going forward

After each phase completes and is committed:
1. Update `docs/operations/CONTINUITY_MAP.md`
2. Push to local `main` (no remote push — billing lock still in effect)
3. Update memory entry with the new HEAD SHA and which questions are now closed
4. Re-verify gates before next phase authorization

You authorize each phase start individually. Wave-bounded rule holds: ≤5 new source files per wave, with the documented exception for new-package bootstraps (Phases F, G, H, I, J) where the boundary-establishing files are unavoidable.

## 5. Immediate next action

**Phase A** is the smallest, lowest-risk, most-informative starting point:
- 0 new source files
- 3 archive tasks + 1 inventory task + 1 doc update
- Q8 result informs whether Phase F/G/H/I/J need re-scoping
- All Q1–Q8 questions get either resolved or have a concrete next phase
- Sets the template for `STAGE_19_5{letter}_ACCEPTANCE.md` format

**Recommended authorization scope for the next "go" command:**

> "Proceed with Phase A only. Stop and produce acceptance record + Phase B plan before continuing."

This keeps the wave budget tight, gives you review surface between phases, and avoids the trap of "1-8 if necessary" turning into "all of it in one go."

## 6. Self-report (v3 §35)

```
Mode: governance system (planning — supersedes single-wave STAGE_19_5 plan)
Created: docs/operations/STAGE_19_5_PHASED_PLAN.md (this file)
Modified: None.
Verified: Q1–Q8 sourced from LEGACY_GAP_INVENTORY.md §8; C1–C5 sourced from STAGE_19_ACCEPTANCE.md §9
Failed: None.
Not verified: apps/ contents (Phase A discovery task); legacy voice_bonding_protocol.py deep semantics (deferred in Phase E)
Risks: scope still large across 10 phases; new-package bootstraps exceed 5-file budget (documented exception); atlas (Phase J) is months of work, not waves
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on Phase A commit)
Remaining:
  - User authorization to start Phase A
  - Per-phase "go" commands thereafter
  - Phase F/G/H/I/J "replan needed" markers require user confirmation before starting
Safe to continue: no — awaiting Phase A authorization
NOT for code edits without explicit "go" from user
```
