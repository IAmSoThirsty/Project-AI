# Alien Invaders Contingency Plan Defense (AICPD) Engine

## Overview

The **Alien Invaders Contingency Plan Defense (AICPD) Engine** is a complete, production-grade simulation system designed to model alien invasion scenarios and their cascading effects across all domains of human civilization. It implements deterministic, causally-consistent world modeling with full state validation and artifact generation.

**NEW**: Now integrated with **Planetary Defense Monolith** for constitutional law evaluation, sole time authority, and mandatory projection mode. See [MONOLITH_INTEGRATION.md](MONOLITH_INTEGRATION.md) for details.

## Architecture

### Core Components

1. **Engine** (`engine.py`) - Main simulation engine with mandatory interface
2. **World State** (`modules/world_state.py`) - Complete state representation
3. **Configuration Schema** (`schemas/config_schema.py`) - Type-safe configuration
4. **Simulation Runner** (`run_simulation.py`) - Execution harness
5. **Planetary Defense Monolith** (`modules/planetary_defense_monolith.py`) - Constitutional kernel (NEW)

### Mandatory Interface

All contingency engines must implement these five methods:

- `init()` - Initialize simulation with starting conditions
- `tick()` - Advance simulation by one time step
- `inject_event(type, parameters)` - Inject external events
- `observe(query)` - Query current state
- `export_artifacts(output_dir)` - Generate reports and data

### Monolithic Integration (NEW)

The engine now integrates with the Planetary Defense Monolith for:

- **Integration Point A**: Invariants as constitutional laws (not post-hoc checks)
- **Integration Point B**: Causal clock as sole time authority (eliminates race conditions)
- **Integration Point C**: Mandatory read-only projection for SimulationRegistry

See [MONOLITH_INTEGRATION.md](MONOLITH_INTEGRATION.md) for complete documentation.

### World Model Subsystems

The engine simulates seven interconnected domains:

1. **Political Model** - Government stability, alliances, conflicts
2. **Economic Model** - GDP, trade, unemployment, inflation
3. **Military Model** - Force strength, casualties, readiness
4. **Societal Model** - Public morale, civil unrest, cohesion
5. **Infrastructure Model** - Integrity, damage, recovery
6. **Environment Model** - Climate, atmosphere, resources
7. **Religion/Culture Model** - Tensions, cohesion, belief systems

### Cross-Domain Propagation

The engine enforces causal consistency through:

- **Economic → Military**: GDP affects military strength
- **Military → Societal**: Casualties reduce morale
- **Political → Economic**: Instability increases unemployment
- **Environmental → Societal**: Resource scarcity increases unrest
- **Alien Activity → All Domains**: Cascading effects across all systems

### Conservation Laws

The engine enforces strict conservation:

- **Population**: Can only decrease (births disabled during crisis)
- **Resources**: Can only be depleted, never created
- **Energy**: Total energy in system is conserved
- **Causality**: All effects must have documented causes

### AI Governance Layer

Optional AI decision-making system with:

- **Alignment Score**: Tracks AI-human value alignment
- **Failure Modes**: Probabilistic AI system failures
- **Human Override**: Emergency manual control capability
- **Failsafes**: Automatic shutdown on catastrophic misalignment

## Usage

### Quick Start

```python
from engines.alien_invaders import AlienInvadersEngine, SimulationConfig

# Create engine with default configuration
engine = AlienInvadersEngine()

# Initialize
engine.init()

# Run for 5 years (60 months)
for _ in range(60):
    engine.tick()

# Export artifacts
engine.export_artifacts()
```

### Scenario Presets

```python
from engines.alien_invaders import load_scenario_preset

# Load aggressive invasion scenario
config = load_scenario_preset("aggressive")
engine = AlienInvadersEngine(config)
```

Available presets:
- `standard` - Balanced threat, 15% invasion probability
- `aggressive` - High threat, immediate invasion
- `peaceful` - Scientific interest, low hostility
- `extinction` - Apocalyptic scenario, godlike technology

### Running from Command Line

```bash
# Run standard 5-year simulation
python engines/alien_invaders/run_simulation.py

# Run aggressive scenario for 10 years
python engines/alien_invaders/run_simulation.py --scenario aggressive --duration 10

# Custom output directory
python engines/alien_invaders/run_simulation.py --output /path/to/artifacts
```

### Event Injection

```python
# Inject alien attack event
engine.inject_event(
    "alien_attack",
    {
        "target_country": "USA",
        "severity": "high",
        "casualties": 10000,
    }
)

# Inject diplomatic success
engine.inject_event(
    "diplomatic_success",
    {
        "severity": "medium",
        "description": "Successful negotiation with alien emissary",
    }
)
```

### State Observation

```python
# Get complete state
state = engine.observe()

# Query specific domains
countries = engine.observe("countries")
aliens = engine.observe("aliens")
global_metrics = engine.observe("global")
```

## Configuration

### World Configuration

```python
from engines.alien_invaders import WorldConfig

world_config = WorldConfig(
    start_year=2026,
    simulation_duration_years=5,
    time_step_days=30,  # Monthly ticks
    num_countries=195,
    global_population=8_000_000_000,
    global_gdp_usd=100_000_000_000_000,
    enable_climate_effects=True,
    enable_economic_propagation=True,
    enable_political_instability=True,
    enable_religious_tensions=True,
)
```

### Alien Configuration

```python
from engines.alien_invaders import AlienConfig, AlienThreatLevel, TechnologyLevel

alien_config = AlienConfig(
    initial_threat_level=AlienThreatLevel.RECONNAISSANCE,
    technology_level=TechnologyLevel.SUPERIOR,
    initial_ship_count=1,
    invasion_probability_per_year=0.15,
    technology_advantage_multiplier=100.0,
    resource_extraction_rate=0.05,
    hostile_intent=0.7,
    adaptation_rate=0.1,
    communication_attempts=True,
    negotiation_openness=0.2,
)
```

### AI Governance Configuration

```python
from engines.alien_invaders import AIGovernanceConfig

ai_config = AIGovernanceConfig(
    enable_ai_governance=True,
    ai_failure_probability=0.05,
    ai_alignment_score=0.85,
    ai_decision_weight=0.6,
    enable_ai_failsafes=True,
    human_override_capability=True,
    catastrophic_failure_threshold=0.95,
)
```

## Artifacts

The engine generates comprehensive documentation:

### Monthly Reports

Location: `artifacts/monthly/report_YYYY_MM.json`

Contains:
- Event log for the month
- Severity classification
- Affected countries
- Day-by-day breakdown

### Annual Reports

Location: `artifacts/annual/report_YYYY.json`

Contains:
- Year summary statistics
- Population changes
- Casualty totals
- Major events
- Alien control percentage

### Postmortem Analysis

Location: `artifacts/postmortem/simulation_postmortem.json`

Contains:
- Complete configuration dump
- Simulation duration metrics
- Final state analysis
- Alien metrics summary
- Key events timeline
- Validation summary
- Outcome classification

Outcome classifications:
- `extinction` - >90% population loss
- `occupation` - >80% alien control
- `partial_control` - >50% alien control
- `catastrophic_losses` - >50% population loss
- `major_losses` - >20% population loss
- `diplomatic_resolution` - Ceasefire achieved
- `survival` - Humanity survived intact

### Raw Data

Location: `artifacts/raw_data.json`

Contains:
- Complete event log with parameters
- Validation history with violations
- State snapshots (if enabled)

## Validation & Determinism

### State Validation

Every tick validates:

1. **Population Conservation** - Population never increases
2. **Resource Conservation** - Resources never exceed initial levels
3. **Energy Conservation** - Total system energy conserved
4. **Causality** - All effects have documented causes
5. **State Coherence** - No contradictory state values

### Deterministic Replay

Enable deterministic replay:

```python
config.validation.deterministic_replay = True
config.validation.random_seed = 42
```

Replay from snapshot:

```python
# Save snapshot
snapshot = engine.state_snapshots[day_number]

# Create new engine and restore
new_engine = AlienInvadersEngine(config)
new_engine.init()
new_engine.state = snapshot

# Continue from snapshot
new_engine.tick()
```

## Integration with SimulationRegistry

Register with the global simulation registry:

```python
from src.app.core.simulation_contingency_root import SimulationRegistry
from engines.alien_invaders import AlienInvadersEngine

# Create and register
engine = AlienInvadersEngine()
SimulationRegistry.register("alien_invaders", engine)

# Retrieve later
engine = SimulationRegistry.get("alien_invaders")
```

## Performance

Typical performance on modern hardware:

- Initialization: ~100ms
- Tick (30-day step): ~10-50ms
- 5-year simulation (60 ticks): ~1-3 seconds
- Artifact generation: ~500ms

Memory usage:
- Engine: ~50MB
- State: ~10MB
- Snapshots: ~10MB per snapshot

## Extending the Engine

### Adding New Event Types

```python
def _process_event(self, event: SimulationEvent):
    if event.event_type == "custom_event":
        # Custom processing logic
        pass
```

### Adding New Subsystems

1. Create module in `modules/`
2. Add update method to engine
3. Call in `tick()` method
4. Add to propagation chain

### Custom Validation Rules

```python
def _validate_state(self) -> ValidationState:
    validation = super()._validate_state()
    
    # Custom validation
    if self.state.custom_metric > threshold:
        validation.violations.append("Custom metric exceeded")
        validation.is_valid = False
    
    return validation
```

## Testing

Run tests:

```bash
# Unit tests
pytest engines/alien_invaders/tests/test_engine.py

# Integration tests
pytest engines/alien_invaders/tests/test_integration.py

# Full test suite
pytest engines/alien_invaders/tests/
```

## Troubleshooting

### Common Issues

**Simulation fails to initialize**
- Check configuration values are within valid ranges
- Ensure output directory is writable
- Verify Python version ≥ 3.11

**State validation failures**
- Review validation violations in log
- Check for conservation law violations
- Disable strict validation for experimental runs

**Performance issues**
- Reduce `save_state_frequency` to save fewer snapshots
- Disable raw data export if not needed
- Increase `time_step_days` for larger steps

## License

MIT License - See root LICENSE file

## Support

- Documentation: `engines/alien_invaders/docs/`
- Issues: GitHub Issues
- Integration: Compatible with existing Defense Engine

---

**Stay prepared. Model scenarios. Survive invasion.** 👽🛡️
