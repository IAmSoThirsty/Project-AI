# J4 Discovery: Atlas Simulation Port

Per user directive 2026-07-01 ("all-in integration, drive wave-
by-wave") and `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md`
section 6 (Atlas staging residue), the simulation slice covers
4 modules from the legacy atlas simulation package.

## Status: in progress (J4.0 envelope committed; J4.1-J4.4 pending)

## TL;DR

Port 4 simulation modules from
`/t/Project-AI-main/engines/atlas/simulation/` to
`packages/atlas/src/atlas/simulation/`. The legacy is ~2000
LOC. Per the inventory, this is "J3 sub-phase per discovery"
(re-labelled J4 here to follow the J3 SWR naming convention
and avoid collision with the SWR J3 work).

## Legacy inventory

Canonical source: `/t/Project-AI-main/engines/atlas/simulation/`
(May 19 timestamps; the duplicate at
`/t/Project-AI-main/atlas/simulation/` is April 26 / May 16,
older). The engines/ copy is canonical per the same
pitfall-1 pattern established in J3 (SWR port).

| Legacy file | LOC | Public surface |
|---|---|---|
| `monte_carlo_engine.py` | 504 | `Domain` enum, `WorldState`, `NoiseVector`, `CouplingCoefficients`, `MonteCarloEngine`, `get_monte_carlo_engine` |
| `agent_simulator.py` | 455 | `AgentType` enum, `ResourceType` enum, `ResourceConstraints`, `UtilityFunction`, `AgentState`, `AgentSimulator`, `get_agent_simulator` |
| `contingency_triggers.py` | 440 | `StackType` enum, `TriggerType` enum, `PlaybookAction` enum, `TriggerCondition`, `Playbook`, `TriggerActivation`, `ContingencyTriggerFramework`, `get_contingency_trigger_framework` |
| `timeline_divergence.py` | 527 | `UncertaintyAxis` enum, `ProjectionPoint`, `TimelineDivergence`, `ProjectionTensor`, `TimelineDivergenceEngine`, `get_timeline_divergence_engine` |
| `__init__.py` | 19 | ATLAS Ω subordination notice (canonical) |

**Total legacy surface: 1945 LOC across 4 source files + 1
init.**

## Canonical source determination

Per pitfall 1 (trust source files over memory): the engines/
copy is canonical because:
- May 19 timestamps (newer than April 26 / May 16)
- 1 extra line in 3 of 4 files (minor — could be formatting)
- Same public surface as the older copy
- The only diffs are the 2-line `[2026-03-05] Productivity: Active`
  header and 1 blank line difference

The atlas/ copy is older and is a superseded fork per the
inventory's disposition for `atlas.bayesian_engine` (which is
SUPERSEDED). Same pattern applies here.

## Port wave plan

Per the established J3 pattern (envelope → port → commit → hermes-verify
→ push → report):

### J4.0 (this commit) — discovery envelope
- `docs/internal/J4_DISCOVERY.md` (this file)
- 0 source ports
- 0 dep changes
- 0 test additions

### J4.1 — MonteCarloEngine
- `packages/atlas/src/atlas/simulation/__init__.py` (19 lines, ATLAS Ω subordination)
- `packages/atlas/src/atlas/simulation/monte_carlo_engine.py` (504 lines)
- `tests/test_atlas_simulation_monte_carlo_integration.py`
- The MonteCarloEngine is the most foundational of the 4
  modules (it provides the noise + coupling primitives that
  the other 3 modules use)

### J4.2 — AgentSimulator
- `packages/atlas/src/atlas/simulation/agent_simulator.py` (455 lines)
- `tests/test_atlas_simulation_agent_integration.py`
- Depends on MonteCarloEngine for noise injection

### J4.3 — ContingencyTriggerFramework
- `packages/atlas/src/atlas/simulation/contingency_triggers.py` (440 lines)
- `tests/test_atlas_simulation_contingency_integration.py`
- Standalone framework (uses AgentState but no direct dep on
  AgentSimulator)

### J4.4 — TimelineDivergenceEngine
- `packages/atlas/src/atlas/simulation/timeline_divergence.py` (527 lines)
- `tests/test_atlas_simulation_timeline_integration.py`
- Depends on MonteCarloEngine + WorldState

### J4.5 — package init + total port completeness
- `packages/atlas/src/atlas/simulation/__init__.py` (final form, public surface)
- `tests/test_atlas_simulation_port_completeness.py`
- 1 final test that validates all 4 modules + the package
  init

**Total J4 work: 6 commits, 5 source files (1945 lines), 5 test files,
~120+ tests.**

## Architectural invariants

- **Port specifically for Beginnings**: every port is a
  standalone module in `packages/atlas/src/atlas/simulation/`.
  No Pydantic BaseModel dependencies (use frozen dataclasses
  per the J3 pattern; matches existing `packages/atlas/src/atlas/`
  style).
- **No new external deps**: all 4 modules are stdlib-only
  (math, random, statistics, enum, dataclass). No scipy, no
  numpy.
- **Tests are first-class**: each module gets a dedicated
  test file covering public surface + edge cases + invariants.
- **T7 convergence preserved**: the J4 work does not touch
  any of the T7 tier specs (T1-T5b).
- **Zero new mypy drift**: J4 ports follow the established
  pattern (no Pydantic, use frozen dataclasses, target
  Beginnings' style).

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| ATLAS Ω subordination notice needs verbatim preservation | Low | Low | The notice is a 14-line block; copy verbatim from legacy |
| Random seed handling differs between MonteCarlo and AgentSim | Low | Medium | Each engine exposes its own `seed` param; no shared RNG |
| `dataclass(frozen=True)` vs legacy `BaseModel` | Low | Low | J3 pattern establishes this; apply same pattern |
| Package init __all__ needs to match the 4 modules' public surface | Low | Low | J4.5 will finalize the init after all 4 modules are ported |
| TimelineDivergence depends on ProjectionTensor which is a large dataclass | Low | Low | Port ProjectionTensor first inside the timeline module |

## Cross-references

- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` section 6
  (Atlas staging residue): source of the inventory
- `docs/internal/J3_DISCOVERY.md`: prior wave pattern (SWR port)
- `packages/atlas/src/atlas/`: existing canonical atlas surface
  (analysis.py, bayesian.py, sensitivity.py, etc.)
