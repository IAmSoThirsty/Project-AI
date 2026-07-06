# Django State Engine

Human Misunderstanding Extinction Engine. Production-grade
simulation for modeling irreversible state evolution, human
misunderstanding cascades, and system extinction dynamics.

## What this is

A scenario engine for the ATLAS Omega platform. The simulation
models:

- **Irreversibility laws**: trust decay, kindness singularity,
  betrayal probability, and other "once-crossed, never-recovered"
  dynamics.
- **Event sourcing and causal timeline**: every state change is
  recorded with full provenance; the causal timeline can be
  replayed.
- **Black vault SHA-256 fingerprinting**: every emitted event is
  hashed for tamper detection.
- **Entropy delta calculation**: the simulation tracks how much
  disorder is added per tick.
- **Module integration**: 7 simulation modules coordinate through
  the engine.
- **DARPA-grade evaluation**: a 600-LOC evaluation rubric that
  scores the simulation against the canonical DARPA evaluation
  criteria.

The public surface is 26 names:

  - `DjangoStateEngine` — the main engine class.
  - **Kernel** (5): `CausalEvent`, `CollapseScheduler`,
    `IrreversibilityLaws`, `RealityClock`, `StateVector`.
  - **Modules** (7): `HumanForcesModule`,
    `InstitutionalPressureModule`, `MetricsModule`,
    `OutcomesModule`, `PerceptionWarfareModule`, `RedTeamModule`,
    `TimelineModule`.
  - **Schemas** (10): `BetrayalEvent`, `CooperationEvent`,
    `EngineConfig`, `Event`, `EventType`,
    `InstitutionalFailureEvent`, `IrreversibilityConfig`,
    `ManipulationEvent`, `OutcomeThresholds`, `RedTeamEvent`,
    `StateDimension`.
  - **Evaluation** (2): `DARPAEvaluator`, `validators`.

## Run it

```python
from django_state import DjangoStateEngine, EngineConfig

config = EngineConfig()
engine = DjangoStateEngine(config=config)
state = engine.initialize()
while not state.is_terminal:
    state = engine.tick()
final = engine.observe()
print(final.summary())
```

## Architecture

The legacy `engines/django_state/` package used intra-package
relative imports (e.g. `from ..kernel.X import Y`,
`from .modules import ...`). The canonical port rewrites all
intra-package imports to absolute `from django_state.X import Y`
form (the relative `..` syntax doesn't survive the package
rename).

The engine has 5 sub-packages:

  - `kernel/` — irreversibility laws, reality clock, collapse
    scheduler, state vector.
  - `modules/` — 7 simulation modules (human forces, institutional
    pressure, metrics, outcomes, perception warfare, red team,
    timeline).
  - `schemas/` — 3 schema files (config, event, state).
  - `evaluation/` — DARPA-grade evaluation rubric and validators.
  - `tests/` — 3 test files (integration, kernel, modules).

The package has no non-canonical external dependencies. The port
is a pure rename + scaffold.

## Port provenance

This is the **J2 scenario engine port** per
`docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a. The
`engines/django_state/` package (22 source files + 3 test files
= 25 files, 6641 LOC) was adapted to a new
`packages/django-state/` workspace member.

Adaptations from the legacy:

1. All intra-package imports rewritten:
   `from .X import Y` / `from ..X import Y` /
   `from engines.django_state.X import Y`
   -> `from django_state.X import Y`.

2. PEP 561 marker (`py.typed`) added for downstream typing.

3. `packages/django-state/src` AND `packages/django-state/tests`
   added to `pyproject.toml [tool.mypy] exclude` (same pattern
   as the other scenario engine ports). The ported engine
   preserves legacy pre-3.12 typing style.

## See also

- `packages/cognitive-warfare/README.md` — J2 cognitive_warfare port
- `packages/global-scenario/README.md` — J2 global_scenario port
- `packages/emp-defense/README.md` — J2 emp_defense port
- `packages/ai-takeover/README.md` — J2 ai_takeover port
- `packages/alien-invaders/README.md` — J2 alien_invaders port
- `docs/internal/LEGACY_TO_CANONICAL_INVENTORY.md` §2a — the
  inventory slice that named this port
