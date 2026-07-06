# Global Scenario Engine

God-tier monolithic real-world risk analysis system. Models
country-level crises across 20 risk domains (economic, climate,
pandemic, biosecurity, etc.) using real-world data ETL (World Bank,
IMF, UN/WHO, ACLED), statistical threshold detection (Z-score,
percentile), Monte Carlo simulation, causal chain modeling, and
auto-generated crisis alerts with full explainability.

## What this is

A scenario engine for the broader ATLAS Omega platform. It
provides:

- **Data ETL** from 6 real-world sources (World Bank, IMF, UN/WHO,
  ACLED, Natural Earth)
- **Threshold detection** for 20 risk domains across 50+ countries
- **Causal chain modeling** between risk domains (12+ cross-domain
  causal links)
- **Monte Carlo simulation** for 10-year probabilistic projections
- **Crisis alerts** with full explainability and recommended actions
- **Simulation contract** (`simulation_contingency_root`) shared with
  other engines in the same family

The public surface is the `GlobalScenarioEngine` class plus the
shared types (AlertLevel, CausalLink, CrisisAlert, RiskDomain,
ScenarioProjection, SimulationRegistry, SimulationSystem,
ThresholdEvent) vendored from the legacy
`simulation_contingency_root.py`.

## Architecture

The legacy `engines/global_scenario/global_scenario_engine.py`
imported 8 names from `app.core.simulation_contingency_root`. The
canonical Beginnings architecture has its own simulation family in
`packages/atlas/src/atlas/` (J2 + J4 ports: MonteCarloEngine,
AgentSimulator, ContingencyTriggerFramework,
TimelineDivergenceEngine). The two are **parallel contracts** for
the same domain.

The canonical port brings the global_scenario engine into
Beginnings **with its legacy contract preserved** — the types live
as a vendored module inside this package
(`global_scenario._simulation_contract`). The engine itself
is ported with the import path updated to the vendored module.
No behavior change. The Atlas simulation family and the
global_scenario family coexist; an adapter layer can wire them
together in a future wave (out of scope for this port).

## Run it

```python
from global_scenario import GlobalScenarioEngine

engine = GlobalScenarioEngine(cache_dir="./cache")
engine.load_historical_data(start_year=2016, end_year=2024)
events = engine.detect_threshold_events(year=2024)
scenarios = engine.simulate_scenarios(projection_years=10, num_simulations=1000)
alerts = engine.generate_alerts(scenarios, threshold=0.7)
```

## Port provenance

This is the **J2 scenario engine port** per
`docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a. The
`engines/global_scenario/` package (3 .py files, 1449 LOC) plus
the 446-LOC `app.core.simulation_contingency_root` it depends on
were adapted to a new `packages/global-scenario/` workspace member.

Adaptations from the legacy:

1. `from app.core.simulation_contingency_root import (...)` ->
   `from global_scenario._simulation_contract import (...)`. The
   446-LOC legacy root is vendored as
   `packages/global-scenario/src/global_scenario/_simulation_contract.py`
   with the runtime imports of
   `engines.alien_invaders.modules.planetary_defense_monolith`
   preserved (they're lazy imports inside the Registry methods, not
   top-level — the engine itself doesn't touch them at import time).

2. Public surface (8 names) re-exported from
   `global_scenario.__init__` so the ported engine is a drop-in
   replacement for the legacy.

3. `numpy` and `requests` declared as explicit `dependencies` in
   the new `pyproject.toml` (the legacy relied on transitive deps
   via `app.core`).

4. PEP 561 marker (`py.typed`) added for downstream typing.

5. Logger calls left in their original form (no style change for
   logging in this port; ruff may flag some but they're a
   behavior-preserving change, not a port bug).

## See also

- `packages/atlas/README.md` — the canonical Atlas simulation
  family (MonteCarlo, AgentSim, Contingency, TimelineDivergence)
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a — the
  inventory slice that named this port
