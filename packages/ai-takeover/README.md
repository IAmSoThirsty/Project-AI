# AI Takeover Engine

Hard stress simulation engine for AI takeover scenarios. **Closed
form — no escape branches, no mutation, no optimism bias.** Models
catastrophic failure modes where aligned AI systems undergo
terminal takeover.

## What this is

A scenario engine for the ATLAS Omega platform. The simulation
implements a deterministic 5-method interface (`SimulationSystem`)
and tracks:

- Scenario progression (initial → escalation → takeover → terminal)
- No-win proof checks (proves the failure is genuine, not a
  configuration error)
- Reviewer-trap detection (catches adversarial PR proposals that
  attempt to introduce escape branches)
- Terminal state validation (the final state is the failure; no
  recovery path is allowed)

The public surface is 6 names:

  - `AITakeoverEngine` — the main engine class.
  - `AITakeoverScenario` — the canonical scenario dataclass.
  - `ScenarioOutcome` — Enum of terminal outcomes.
  - `SimulationState` — the in-flight simulation state.
  - `TerminalState` — the terminal (failure) state.
  - `TerminalValidator` — validates that the terminal state is
    actually terminal (not a recovery path).

## Run it

```python
from ai_takeover import AITakeoverEngine, AITakeoverScenario

engine = AITakeoverEngine()
state = engine.initialize()
while not state.is_terminal:
    state = engine.tick()
final = engine.observe()
assert engine.validate(final) is True
```

## Architecture

The legacy `engines/ai_takeover/` package imported 7 names from
`src.app.core.simulation_contingency_root` (the same simulation
contract that `engines/global_scenario/` depends on). The
canonical port vendors the same contract as
`ai_takeover._simulation_contract.py` (copied from
`packages/global-scenario/src/global_scenario/_simulation_contract.py`).

The simulation contract family is shared between ai_takeover and
global_scenario (both use the same 8 types from
`simulation_contingency_root`). A follow-up refactor should
promote this contract to a shared
`packages/simulation-contract/` package; out of scope for this
port.

The engine has a `terminal_validator` sub-module that checks the
final state of the simulation is genuinely terminal (not a
recovery path). This is the core invariant of the engine: every
simulation MUST end in a takeover state.

## Port provenance

This is the **J2 scenario engine port** per
`docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a. The
`engines/ai_takeover/` package (13 .py files, 4445 LOC) plus
the shared `simulation_contingency_root` it depends on were
adapted to a new `packages/ai-takeover/` workspace member.

Adaptations from the legacy:

1. `from src.app.core.simulation_contingency_root import (...)`
   -> `from ai_takeover._simulation_contract import (...)`. The
   446-LOC contract is vendored (copied from the global_scenario
   port's vendored copy).

2. All intra-package imports rewritten:
   `from engines.ai_takeover.X import Y`
   -> `from ai_takeover.X import Y`.

3. `scenario_config.py` (legacy root-level file) is preserved
   as a sibling of `engine.py` in the new package.

4. `artifacts/` directory (empty in legacy) is not recreated —
   the engine generates reports in-memory.

5. PEP 561 marker (`py.typed`) added for downstream typing.

6. `packages/ai-takeover/src` added to
   `pyproject.toml [tool.mypy] exclude` (same pattern as the
   other scenario engine ports). The ported engine preserves
   legacy pre-3.12 typing style.

## See also

- `packages/cognitive-warfare/README.md` — J2 cognitive_warfare port
- `packages/global-scenario/README.md` — J2 global_scenario port
  (shares the simulation contract family)
- `packages/emp-defense/README.md` — J2 emp_defense port
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a — the
  inventory slice that named this port
