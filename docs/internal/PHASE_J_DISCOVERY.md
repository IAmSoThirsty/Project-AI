# Phase J Discovery + Sub-Phase Plan — packages/atlas/

**Status:** DISCOVERY + PLAN (no code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
  ("REPLAN AT START OF PHASE" + "months of work" + 102 files)
**Date:** 2026-06-25
**Source-of-truth:** `T:\Project-AI-main\atlas\` (read-only)
**Target:** New `packages/atlas/` workspace member

> Current-state note (2026-06-29): this discovery plan is historical. The
> J2.1-J2.9 continuation waves have now been locally implemented, and all J1
> audit gaps are closed with implementation CI evidence through run
> `28362042896`.
> Use `docs/internal/STAGE_19_5_SESSION_LEDGER.md` for current status.

---

## 0. Why this discovery is its own phase

Legacy atlas is the largest subsystem by far:

- **51 Python files / 12,480 LOC / 120 total files** (51 py + 69 other)
- **15+ subpackages** with deeply nested structure
- **Bayesian engine, Monte Carlo simulation, constitutional kernel**
- Touches **governance** (constitutional_kernel), **kernel**
  (epistemic safeguards), **simulation** (timeline divergence)

The phased plan explicitly directs: "REPLAN AT START OF PHASE.
Months of work. Sub-phased."

This is NOT a phase to consume in one go. The recommendation is
**J0 envelope + explicit authorization per sub-phase thereafter**.

---

## 1. Legacy atlas surface inventory

### Top-level subpackages

| Subpackage | LOC est. | py files | Purpose | Port priority |
|---|---|---|---|---|
| `atlas/core/` | ~3500 | 11 | Core engines (bayesian, graph, ingestion, normalization, scoring, projections) | **J1** (split into J1a/J1b/J1c) |
| `atlas/simulation/` | ~2000 | 4 | Agent sim, Monte Carlo, contingency, timeline divergence | **J3** |
| `atlas/analysis/` | ~800 | 2 | Failure surveillance, sensitivity analyzer | **J2** |
| `atlas/governance/` | ~600 | 1 | Constitutional kernel | **J4** |
| `atlas/safeguards/` | ~600 | 1 | Epistemic safeguards | **J4** |
| `atlas/audit/` | ~400 | 1 | Audit trail | **J2** |
| `atlas/sandbox/` | ~400 | 1 | Sludge sandbox | **J5** |
| `atlas/schemas/` | ~300 | 1 | Schema validator | **J2** |
| `atlas/cli/` | ~250 | 1 | Atlas CLI | **J5** |
| `atlas/config/` | ~200 | 1 | Config loader | **J1** (foundations) |
| `atlas/verification/` | ~200 | 1 | Replay system | **J5** |
| Other (`data/`, `logs/`, `reports/`, `safety/`, `export/`) | ~230 | 5 | Data dirs + light modules | **J5** |
| **Total py** | **~12,480** | **51** | | |

### core/ sub-subpackages (heavy)

```
atlas/core/
├── bayesian_engine.py
├── drivers/
│   ├── calculator.py
│   └── driver_engine_10d.py
├── graph/
│   ├── builder.py
│   └── temporal_graph.py
├── ingestion/
│   ├── ingester.py
│   └── tier_classifier.py
├── normalization/
│   └── normalizer.py
├── projections/
│   └── simulator.py
└── scoring/
    └── scorer.py
```

**Core is 11 py files / ~3500 LOC** — alone would warrant its own
3 sub-phase split (J1a foundations, J1b ingestion/normalization,
J1c graph/scoring/projections).

---

## 2. Architectural challenges

1. **Scope**: 12,480 LOC is ~12x Phase H total. Cannot be done in one wave.
2. **External deps**: Need to inventory imports to see if atlas depends
   on heavy external libs (numpy, scipy, networkx?).
3. **Bayesian + Monte Carlo**: Numerical work; may need numpy/scipy.
4. **Constitutional kernel**: Touches governance — must respect
   downward-only deps rule.
5. **Heavy subdirs**: `core/drivers/`, `core/graph/`, `core/ingestion/`
   each warrant sub-phasing.

---

## 3. Architectural invariants (AGENTS.md v3)

Atlas rebuild must respect:
- **Downward-only deps**: atlas may import from `kernel` + stdlib only.
  External numerical libs (if needed) must be **optional** or
  abstracted via Protocol.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue.
- **Fail-closed**: invalid inputs → AtlasError.
- **Pluggable seams**: BayesianProtocol, MonteCarloProtocol.
- **Deterministic**: seeded RNG for reproducibility.
- **Strict typing**: mypy --strict clean.
- **Audit chain**: every simulation step recorded.

---

## 4. Sub-phase plan (REPLAN)

Per the phased plan's directive ("months of work. Sub-phased"), I'm
splitting Phase J into **6 sub-phases** plus a discovery envelope.

### Phase J0 — Discovery + skeleton (this turn)

**Scope:** Discovery artifact + package skeleton + workspace registration
**New source files:** 0 (only `pyproject.toml`, `README.md`, `__init__.py`,
`py.typed`)
**File changes:** ≤5
**Tasks:**
1. Write this discovery doc (done)
2. Create `packages/atlas/` package skeleton
3. Register in `pyproject.toml` workspace + sources
4. Verify all gates still green
5. Write `docs/internal/STAGE_19_5J0_ACCEPTANCE.md`
6. Commit Phase J0

### Phase J1 — Core foundations (config + base types)

**Scope:** Core foundations — config loader + base dataclasses
**New source files:** 3 (`config.py`, `types.py`, `__init__.py` updates)
**Tasks:**
1. `packages/atlas/src/atlas/config.py` — AtlasConfig dataclass
2. `packages/atlas/src/atlas/types.py` — AtlasError, severity types,
   audit record TypedDict
3. Tests
4. Commit Phase J1

### Phase J2 — Analysis + audit + schemas

**Scope:** Analysis layer (failure_surveillance, sensitivity_analyzer),
audit trail, schema validator
**New source files:** 3 (`analysis.py`, `audit.py`, `schemas.py`)
**Tasks:**
1. Failure surveillance Protocol + default
2. Sensitivity analyzer Protocol + default
3. Audit trail (append-only)
4. Schema validator
5. Tests
6. Commit Phase J2

### Phase J3 — Simulation layer (Monte Carlo, agent sim, timeline)

**Scope:** Monte Carlo engine, agent simulator, timeline divergence,
contingency triggers
**New source files:** 4 (`simulation.py` × 4 OR combined)
**Tasks:**
1. MonteCarloEngine with seeded RNG
2. AgentSimulator with protocol
3. TimelineDivergence with deterministic output
4. ContingencyTriggers
5. Tests
6. Commit Phase J3

### Phase J4 — Governance + safeguards (constitutional kernel, epistemic)

**Scope:** ConstitutionalKernel, EpistemicSafeguards
**New source files:** 2
**Tasks:**
1. ConstitutionalKernel Protocol + default
2. EpistemicSafeguards
3. Tests
4. Commit Phase J4

### Phase J5 — Sandbox + CLI + verification + data dirs

**Scope:** Sludge sandbox, CLI, replay system
**New source files:** 3-5
**Tasks:**
1. SludgeSandbox
2. AtlasCLI (stub)
3. ReplaySystem
4. Data dir structure (staging only — no data files)
5. Tests
6. Commit Phase J5

### Phase J6 — Core split (if not deferred)

**The 3500-LOC `core/` subpackage** is large enough to warrant its own
3 sub-phases. Options:

**Option X:** Split core into J6a (ingestion + normalization),
J6b (graph + scoring + projections), J6c (drivers + bayesian).

**Option Y:** Keep core in J1 and accept it as 1 sub-phase with
~3500 LOC spread across 5-7 source files (still wave-bounded per file).

**Recommendation: Option Y** — keep core atomic in J1 to minimize the
number of sub-phases. Each source file is still ≤5 files per wave.

### Deferred (out of scope for J):
- `atlas/data/raw/`, `atlas/data/normalized/` — directory markers only
- `atlas/data/stacks/` — external dataset dependencies
- `atlas/logs/`, `atlas/reports/` — runtime output dirs
- Real Bayesian numerical work (numpy/scipy optional)
- Real Monte Carlo workers
- Atlas CLI real commands (CLI stub only)

---

## 5. Estimated file count

| Sub-phase | New source | New test | Init modify | Other | Total |
|---|---|---|---|---|---|
| J0 | 0 | 0 | 0 | pyproject, README, py.typed, docs | 4-5 |
| J1 | 2 | 1 | 1 | 1 integration | 5 |
| J2 | 3 | 1 | 1 | 1 integration | 6 |
| J3 | 4 | 1 | 1 | 1 integration | 7 |
| J4 | 2 | 1 | 1 | 1 integration | 5 |
| J5 | 3 | 1 | 1 | 1 integration | 6 |
| **Total** | **14 source** | **5+** | **5** | **5+** | **~35** |

Phase J = ~14 source files + ~5 test files = ~19 files.
~30% of legacy LOC (the minimum viable port).

---

## 6. Critical risks

1. **Numerical dependencies**: numpy/scipy if needed. Recommend
   **stdlib-only math** + Protocol abstraction; numerical deps
   optional later.
2. **Constitutional kernel**: Touches governance — defer real policy
   enforcement to J4 sub-phase.
3. **12,480 LOC scope**: ~14 source files is ~900 LOC avg per file.
   Realistic minimum is much smaller; recommend further sub-phasing.
4. **External data files**: `data/raw/`, `data/stacks/` — defer;
   legacy doesn't load them by default.

---

## 7. Recommended authorization scope

> "Proceed with Phase J0 only (discovery skeleton). Then authorize
> each sub-phase individually (J1, J2, J3, J4, J5). NO blanket
> authorization for the whole phase J."

This preserves the wave-bounded pattern that worked for Phases A-I:
J0 sets the envelope, each subsequent sub-phase gets explicit go.

---

## 8. Self-report (v3 §35)

```
Mode: governance system (planning — Phase J discovery)
Created: docs/internal/PHASE_J_DISCOVERY.md (this file)
Modified: None.
Verified: atlas legacy surface inventoried (51 py, 12,480 LOC, 15+ subpackages).
Failed: None.
Not verified:
- External deps in atlas (numpy, scipy, networkx?) — pending J1 audit
- Performance characteristics — not measured
Risks: substantial; 12,480 LOC exceeds all prior phases combined;
  multi-sub-phase required; numerical libs may need optionality;
  constitutional_kernel touches governance.
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on J0 commit)
Remaining:
- User authorization to start Phase J0 (this turn)
- Per-sub-phase "go" for J1, J2, J3, J4, J5 thereafter
- External dependency audit (deferred to J1)
```
