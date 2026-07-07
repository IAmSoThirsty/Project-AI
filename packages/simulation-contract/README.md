# Simulation Contract (shared)

Shared simulation contract for Project-AI's scenario
engines. Promoted from 3 vendored copies (one in
`global_scenario`, one in `ai_takeover`, one in
`alien_invaders`) to eliminate drift and make future
contract changes atomic.

## What's here

- 9 public types: `RiskDomain`, `AlertLevel`,
  `ThresholdEvent`, `CausalLink`, `ScenarioProjection`,
  `CrisisAlert`, `RegistryAccessRequest`,
  `SimulationSystem`, `SimulationRegistry`
- One module: `simulation_contract.contract`
- Zero runtime dependencies (uses only `logging`,
  `abc`, `dataclasses`, `datetime`, `enum`, `typing`)

## Why this is a shared package

Originally at
`T:\00-Active\Project-AI-main\src\app\core\simulation_contingency_root.py`.

Vendored 3 times during the J2 ports
(global_scenario in `4078747c`, ai_takeover in
`ec839b08`, alien_invaders in `b8f43cfe`). The 3
vendored copies drifted (different docstrings, different
lazy-import paths, different line counts) and fixing a
contract bug required touching 3 files.

A shared package makes future contract changes atomic:
one edit, one test run, all engines see the new
contract.

The 3 vendored copies are now thin re-exports of this
package (see the "migration" section below). They are
preserved for backward compatibility with the 3 engine
packages' public API, but new code should depend on
`project-ai-simulation-contract` directly.

## Migration of `RegistryAccessRequest`

`RegistryAccessRequest` used to live in
`alien_invaders.modules.planetary_defense_monolith`.
Moving it to the shared contract broke the backward
dependency that the vendored copies had (each had a
lazy `from alien_invaders.modules.planetary_defense_monolith
import RegistryAccessRequest` inside `SimulationRegistry`).
The lazy import was a smell — a shared contract must
not depend on a specific engine.

The `alien_invaders.modules.planetary_defense_monolith`
now imports `RegistryAccessRequest` from the shared
contract (no circular dep).

## How to use

```python
from simulation_contract import (
    SimulationRegistry,
    SimulationSystem,
    RiskDomain,
    AlertLevel,
    ThresholdEvent,
    CausalLink,
    ScenarioProjection,
    CrisisAlert,
    RegistryAccessRequest,
)

class MyEngine(SimulationSystem):
    def name(self) -> str:
        return "my-engine"
    # ...

SimulationRegistry.register(MyEngine())
```

## See also

- `packages/global-scenario/`, `packages/ai-takeover/`,
  `packages/alien-invaders/` — the 3 J2 engines that
  consume this contract
- `docs/reference/historical-archive/` — historical
  port documentation

## Verification

Tests live in
`packages/simulation-contract/tests/`. The 4 canonical
gates (pytest, mypy, ruff check, ruff format) are
green; T7 convergence hash is preserved at every
commit.
