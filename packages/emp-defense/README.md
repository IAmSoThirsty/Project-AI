# EMP Defense Engine

Electromagnetic pulse (EMP) defense engine for modeling EMP events
and their cascading effects on global civilization infrastructure.

## What this is

A simulation engine for the ATLAS Omega platform. It models:

- Sectorized world state (power, water, food, healthcare, etc.)
- EMP event cascade timelines (long-term infrastructure decay)
- Domain coupling (cross-sector failure propagation)
- Death accounting and population impact
- Time-guarded simulation (sane bounds on tick rates)

The public surface is 4 names:

  - `EMPDefenseEngine` — the main engine class with a 5-method
    interface (`init`, `tick`, `observe`, `step`, `validate`).
  - `EMPScenario` — Enum of canonical scenario presets.
  - `SimulationConfig` — the simulation configuration dataclass.
  - `load_scenario_preset` — load a canonical scenario config.

## Run it

```python
from emp_defense import EMPDefenseEngine, load_scenario_preset

config = load_scenario_preset("carrington")
engine = EMPDefenseEngine(config=config)
engine.init()
while engine.observe().simulation_day < 365:
    engine.tick()
final_state = engine.observe()
```

## Architecture

The legacy `engines/emp_defense/` package imported only from itself
(intra-package imports). The canonical port rewrites
`engines.emp_defense.*` → `emp_defense.*` and registers the new
package in the uv workspace. No vendored contract needed — the
emp_defense package is fully self-contained.

The 11 sub-modules in `emp_defense.modules.*` are pure Python
implementations of the simulation primitives (world state, sector
decay, coupling, death accounting, time guards, etc.). They have
no non-canonical external dependencies.

## Port provenance

This is the **J2 scenario engine port** per
`docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a. The
`engines/emp_defense/` package (15 .py files, 3204 LOC) was
adapted to a new `packages/emp-defense/` workspace member.

Adaptations from the legacy:

1. All intra-package imports rewritten:
   `from engines.emp_defense.X import Y`
   → `from emp_defense.X import Y`.

2. PEP 561 marker (`py.typed`) added for downstream typing.

3. `packages/emp-defense/src` added to
   `pyproject.toml [tool.mypy] exclude` (same pattern as
   `packages/_staging`, `packages/security/reference`,
   `packages/rlp/governance_framework`, and
   `packages/global-scenario/src`). The ported engine preserves
   legacy pre-3.12 typing style.

4. Tests directory dropped its `__init__.py` to avoid the
   mypy "Duplicate module named 'tests'" error that the
   `test_thirsty_lang_smoke.py` and `test_swr_*_integration.py`
   tests already cause.

## See also

- `packages/cognitive-warfare/README.md` — J2 cognitive_warfare port
- `packages/global-scenario/README.md` — J2 global_scenario port
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a — the
  inventory slice that named this port
