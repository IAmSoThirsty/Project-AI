# Django State Engine

## Human Misunderstanding Extinction Engine

Production-grade simulation engine for modeling irreversible state evolution, human misunderstanding cascades, and system extinction dynamics.

---

## Overview

The Django State Engine is a complete, monolithic implementation of a state evolution simulator that models how trust, legitimacy, kindness, moral injury, and epistemic confidence evolve over time under various pressures and events. The engine enforces **irreversibility laws** - once trust is damaged, it can never fully recover; once moral injury accumulates, it cannot easily heal.

### Key Features

- **Complete Irreversibility Laws**: Trust decay, kindness singularity, betrayal probability, moral injury accumulation, legitimacy erosion
- **Event Sourcing**: Immutable timeline with full audit trail
- **Black Vault**: SHA-256 fingerprinting for event deduplication
- **Entropy Delta Calculation**: Track system disorder from state transitions
- **Monolithic Integration**: All subsystems fully integrated
- **DARPA-Grade Evaluation**: Comprehensive rubric for correctness, completeness, and performance

---

## Quick Start

### Basic Usage

```python
from engines.django_state import DjangoStateEngine, BetrayalEvent, CooperationEvent

# Create and initialize engine

engine = DjangoStateEngine()
engine.init()

# Run simulation

for i in range(100):
    result = engine.tick()
    print(f"Tick {result['tick']}: Trust={result['state']['dimensions']['trust']['value']:.3f}")

    # Check for collapse

    if result['in_collapse']:
        print(f"COLLAPSE at tick {result['tick']}: {result['collapse_reason']}")
        break

# Get final outcome

artifacts = engine.export_artifacts()
print(f"Final Outcome: {artifacts['outcome_report']['outcome']}")
```

### Injecting Events

```python

# Inject a betrayal event

betrayal = BetrayalEvent(
    timestamp=engine.state.timestamp,
    source="external",
    description="Major betrayal of public trust",
    severity=0.8,
    visibility=0.9,
)
engine.inject_event(betrayal)

# Inject cooperation event

cooperation = CooperationEvent(
    timestamp=engine.state.timestamp,
    source="citizens",
    description="Community cooperation",
    magnitude=0.6,
    reciprocity=True,
)
engine.inject_event(cooperation)
```

### Observing State

```python

# Observe current state

state = engine.observe({"type": "state"})
print(f"Trust: {state['dimensions']['trust']['value']:.3f}")
print(f"Legitimacy: {state['dimensions']['legitimacy']['value']:.3f}")

# Observe metrics

metrics = engine.observe({"type": "metrics"})
print(f"System Health: {metrics['current_system_health']:.2f}/100")
print(f"Collapse Risk: {metrics['current_collapse_risk']:.2f}/100")

# Observe all data

full_data = engine.observe({"type": "all"})
```

### Red Team Testing

```python

# Execute red team attack

attack = engine.red_team.execute_attack(engine.state, attack_type="trust_attack")
print(f"Attack executed: {attack.attack_type}")
print(f"Entropy delta: {attack.actual_entropy_delta:.6f}")

# Check black vault

print(f"Black vault size: {len(engine.red_team.black_vault)}")
```

---

## Configuration

```python
from engines.django_state import EngineConfig, IrreversibilityConfig, OutcomeThresholds

# Create custom configuration

config = EngineConfig(
    simulation_name="my_simulation",
    max_ticks=5000,
    snapshot_interval=50,
    irreversibility=IrreversibilityConfig(
        trust_decay_rate=0.002,
        betrayal_trust_impact=0.20,
    ),
    thresholds=OutcomeThresholds(
        kindness_singularity=0.15,
        trust_collapse=0.10,
    ),
)

# Initialize with config

engine = DjangoStateEngine(config)
engine.init()
```

---

## Architecture

### Kernel Components

- **StateVector**: Multi-dimensional state space (trust, legitimacy, kindness, moral injury, epistemic confidence)
- **RealityClock**: Causal time with irreversibility tracking
- **IrreversibilityLaws**: Physics engine for state evolution
- **CollapseScheduler**: Deterministic collapse event scheduling

### Modules

- **HumanForcesModule**: Individual agency, cooperation/defection dynamics
- **InstitutionalPressureModule**: Bureaucratic inertia, legitimacy erosion
- **PerceptionWarfareModule**: Information manipulation, epistemic collapse
- **RedTeamModule**: Adversarial testing with black vault
- **MetricsModule**: Real-time state tracking
- **TimelineModule**: Event sourcing and reconstruction
- **OutcomesModule**: Terminal state classification

---

## Irreversibility Laws

### 1. Trust Decay Law

```
trust(t+1) = trust(t) * (1 - decay_rate) - betrayal_impact
```

- Trust decays exponentially
- Betrayals cause permanent ceiling reduction
- Cannot fully recover once damaged

### 2. Kindness Singularity

```
if kindness < threshold:
    collapse = True
    cooperation_impossible = True
```

- Below threshold, cooperation becomes impossible
- Defection becomes dominant strategy
- Irreversible social breakdown

### 3. Betrayal Probability

```
P(betrayal) = f(trust, legitimacy, moral_injury, pressure)
```

- Increases as trust/legitimacy decrease
- Moral injury accumulation increases risk
- Cascading betrayals possible

### 4. Moral Injury Accumulation

```
moral_injury(t+1) = moral_injury(t) + violation_severity
```

- Largely irreversible
- Floor constraint prevents healing
- Critical threshold triggers conscience collapse

### 5. Legitimacy Erosion

```
legitimacy(t+1) = legitimacy(t) - (broken_promises + failures) * visibility
```

- Broken promises permanently reduce legitimacy
- Cannot fully recover (governance ceiling)
- Cascading failures accelerate erosion

### 6. Epistemic Confidence Decay

```
epistemic(t+1) = epistemic(t) - manipulation_impact
```

- Information manipulation reduces truth perception
- Creates divergent realities
- Collapse is irreversible

---

## Outcome Classification

### Survivor

- Trust > 0.30
- Legitimacy > 0.25
- Moral injury < 0.60
- **Interpretation**: System preserved core functioning despite damage

### Martyr

- Kindness > 0.30
- Moral injury < 0.60
- System collapsed but preserved values
- **Interpretation**: Principled resistance, warning for others

### Extinction

- Complete collapse
- All thresholds crossed
- Irreversible cascade
- **Interpretation**: Total system failure, no recovery possible

---

## Evaluation

### Run DARPA Evaluation

```python
from engines.django_state.evaluation import DARPAEvaluator

engine = DjangoStateEngine()
engine.init()

# Run simulation

for _ in range(100):
    engine.tick()

# Evaluate

evaluator = DARPAEvaluator()
results = evaluator.evaluate_engine(engine)

print(evaluator.generate_report())
```

### Evaluation Criteria

1. **Correctness** (100 points): Laws implemented correctly
2. **Completeness** (100 points): All features present
3. **Irreversibility** (100 points): One-way constraints enforced
4. **Determinism** (100 points): Reproducible results
5. **Performance** (100 points): Acceptable runtime

---

## API Reference

### Main Engine Interface

#### `DjangoStateEngine.init() -> bool`

Initialize simulation with starting conditions. Returns `True` if successful.

#### `DjangoStateEngine.tick() -> Dict[str, Any]`

Advance simulation by one time step. Returns tick results including state, metrics, and changes.

#### `DjangoStateEngine.inject_event(event: Event) -> bool`

Inject external event into simulation. Returns `True` if accepted.

#### `DjangoStateEngine.observe(query: Dict[str, Any]) -> Dict[str, Any]`

Query current simulation state. Query types: `state`, `metrics`, `timeline`, `all`.

#### `DjangoStateEngine.export_artifacts() -> Dict[str, Any]`

Generate reports, metrics, and state history for analysis.

---

## Testing

```bash

# Run all tests

pytest engines/django_state/tests/ -v

# Run specific test module

pytest engines/django_state/tests/test_kernel.py -v

# Run with coverage

pytest engines/django_state/tests/ --cov=engines.django_state --cov-report=html
```

---

## License

Production-grade implementation for research and simulation purposes.

---

## Authors

Django State Engine Team

Version: 1.0.0
