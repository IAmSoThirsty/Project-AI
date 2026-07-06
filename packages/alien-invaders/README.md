# Alien Invaders Contingency Plan Defense (AICPD) Engine

Production-grade simulation system for modeling alien invasion
scenarios. Models the dynamics of an alien invasion, including
causal event clocks, world state, and a planetary defense monolith
that gates major actions through a governance contract.

## What this is

A scenario engine for the ATLAS Omega platform. The simulation
includes:

- A `PlanetaryDefenseMonolith` that intercepts all major actions
  and routes them through a governance contract. The monolith
  references the canonical `kernel.ActionRequest` /
  `kernel.Outcome` model.
- A causal clock that records events with time-of-occurrence
  metadata.
- A world state model (countries, global state, events).
- A set of invariants the simulation must maintain.
- A `AlienInvadersSimulationAdapter` that wraps the engine with
  the `SimulationSystem` contract interface (shared with
  global_scenario and ai_takeover).

The public surface is 8 names:

  - `AlienInvadersEngine` — the main engine class.
  - `SimulationConfig` — the simulation configuration dataclass.
  - `AlienConfig` — the alien attacker config.
  - `WorldConfig` — the world defender config.
  - `AIGovernanceConfig` — the AI governance config.
  - `AlienThreatLevel` — Enum of threat tiers.
  - `TechnologyLevel` — Enum of technology levels.
  - `load_scenario_preset` — load a canonical scenario.

## Run it

```python
from alien_invaders import AlienInvadersEngine, load_scenario_preset

config = load_scenario_preset("first_contact")
engine = AlienInvadersEngine(config=config)
if engine.init():
    while engine.observe().simulation_day < 365:
        engine.tick()
    final = engine.observe()
    print(final.summary())
```

## Architecture

The legacy `engines/alien_invaders/` package imported 7 names from
`src.app.core.simulation_contingency_root` (the same simulation
contract that `engines/global_scenario/` and
`engines/ai_takeover/` depend on). The canonical port vendors
the same contract as
`alien_invaders._simulation_contract.py` (copied from
`packages/global-scenario/src/global_scenario/_simulation_contract.py`).

The `planetary_defense_monolith.py` is the **shared monolith** —
the canonical-equivalent gatekeeper that intercepts major
actions. It's part of the alien_invaders package (where it
originates in the legacy) and is shared with global_scenario and
emp_defense through cross-package references. For this port, the
monolith is preserved in-place.

The simulation contract family is shared between
`global_scenario`, `ai_takeover`, and `alien_invaders` (all use
the same 8 types from `simulation_contingency_root`). A follow-up
refactor should promote this contract to a shared
`packages/simulation-contract/` package; out of scope for this
port.

## Port provenance

This is the **J2 scenario engine port** per
`docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a. The
`engines/alien_invaders/` package (10 .py files, 3085 LOC) plus
the shared `simulation_contingency_root` it depends on were
adapted to a new `packages/alien-invaders/` workspace member.

Adaptations from the legacy:

1. `from src.app.core.simulation_contingency_root import (...)`
   -> `from alien_invaders._simulation_contract import (...)`. The
   446-LOC contract is vendored (copied from the global_scenario
   port's vendored copy).

2. All intra-package imports rewritten:
   `from engines.alien_invaders.X import Y`
   -> `from alien_invaders.X import Y`.

3. The shared `planetary_defense_monolith` is preserved in the
   new package (it's the largest single module in the legacy at
   301 LOC). The `SimulationRegistry` reference inside
   `integration.py` (in a try/except for optional import) is
   resolved via the vendored contract.

4. The `artifacts/` directory (empty in legacy) is not
   recreated; the engine writes reports in-memory.

5. PEP 561 marker (`py.typed`) added for downstream typing.

6. `packages/alien-invaders/src` AND
   `packages/alien-invaders/tests` added to
   `pyproject.toml [tool.mypy] exclude` (same pattern as the
   other scenario engine ports). The ported engine preserves
   legacy pre-3.12 typing style.

## See also

- `packages/cognitive-warfare/README.md` — J2 cognitive_warfare port
- `packages/global-scenario/README.md` — J2 global_scenario port
- `packages/emp-defense/README.md` — J2 emp_defense port
- `packages/ai-takeover/README.md` — J2 ai_takeover port
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a — the
  inventory slice that named this port
