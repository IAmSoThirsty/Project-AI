# AICPD Engine Operations Guide

## Installation

### Prerequisites

- Python 3.11+
- Project-AI repository cloned

### No Additional Dependencies

The AICPD engine uses only Python standard library. No external packages required beyond the base Project-AI dependencies.

---

## Quick Start

### 1. Run Standard Simulation

```bash
cd /path/to/Project-AI
python engines/alien_invaders/run_simulation.py
```

This runs a 5-year standard scenario simulation.

### 2. View Results

```bash
# View postmortem
cat engines/alien_invaders/artifacts/postmortem/simulation_postmortem.json

# List monthly reports
ls engines/alien_invaders/artifacts/monthly/

# List annual reports
ls engines/alien_invaders/artifacts/annual/
```

---

## Command-Line Usage

### Basic Syntax

```bash
python engines/alien_invaders/run_simulation.py [OPTIONS]
```

### Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--scenario` | standard, aggressive, peaceful, extinction | standard | Scenario preset |
| `--duration` | Integer | 5 | Simulation years |
| `--output` | Path | engines/alien_invaders/artifacts | Output directory |
| `--log-level` | DEBUG, INFO, WARNING, ERROR | INFO | Logging verbosity |

### Examples

```bash
# Aggressive 10-year scenario
python engines/alien_invaders/run_simulation.py \
    --scenario aggressive \
    --duration 10

# Peaceful scenario with debug logging
python engines/alien_invaders/run_simulation.py \
    --scenario peaceful \
    --log-level DEBUG

# Custom output directory
python engines/alien_invaders/run_simulation.py \
    --output /tmp/alien_sim_results
```

---

## Programmatic Usage

### Basic Script

```python
from engines.alien_invaders import AlienInvadersEngine

# Create and initialize
engine = AlienInvadersEngine()
engine.init()

# Run simulation
for year in range(5):
    for month in range(12):
        engine.tick()

# Export results
engine.export_artifacts()
```

### With Custom Configuration

```python
from engines.alien_invaders import (
    AlienInvadersEngine,
    SimulationConfig,
    AlienThreatLevel,
    TechnologyLevel,
)

# Create configuration
config = SimulationConfig()
config.world.simulation_duration_years = 10
config.alien.initial_threat_level = AlienThreatLevel.INVASION
config.alien.technology_level = TechnologyLevel.GODLIKE
config.alien.hostile_intent = 0.9

# Run simulation
engine = AlienInvadersEngine(config)
engine.init()

for _ in range(120):  # 10 years
    if not engine.tick():
        print("Simulation failed validation")
        break

engine.export_artifacts()
```

### With Event Injection

```python
engine = AlienInvadersEngine()
engine.init()

# Run simulation with events
for month in range(60):
    engine.tick()
    
    # Inject crisis every year
    if month % 12 == 0:
        engine.inject_event(
            "alien_attack",
            {
                "target_country": "USA",
                "severity": "high",
                "casualties": 50000,
            }
        )

engine.export_artifacts()
```

---

## Monitoring and Logging

### Log Files

**Default Location:** `engines/alien_invaders/artifacts/simulation.log`

**Log Format:**
```
YYYY-MM-DD HH:MM:SS,mmm [LEVEL] logger_name: message
```

### Real-Time Monitoring

```python
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler('simulation_debug.log')  # File
    ]
)

engine = AlienInvadersEngine()
engine.init()

# Run with detailed logs
for month in range(12):
    engine.tick()
    state = engine.observe("global")
    print(f"Month {month+1}: Population={state['population']:,}")
```

### Progress Tracking

```python
def run_with_progress(engine, total_ticks):
    """Run simulation with progress bar."""
    for tick in range(total_ticks):
        if not engine.tick():
            print(f"Failed at tick {tick}")
            return False
        
        # Progress update
        if (tick + 1) % 12 == 0:
            year = (tick + 1) // 12
            state = engine.observe("global")
            print(f"Year {year}: {state['population']:,} population, "
                  f"{state['casualties']:,} casualties")
    
    return True

engine = AlienInvadersEngine()
engine.init()
run_with_progress(engine, 60)
engine.export_artifacts()
```

---

## Artifact Management

### Output Structure

```
artifacts/
├── monthly/
│   ├── report_2026_01.json
│   ├── report_2026_02.json
│   └── ...
├── annual/
│   ├── report_2026.json
│   ├── report_2027.json
│   └── ...
├── postmortem/
│   └── simulation_postmortem.json
├── raw_data.json
└── simulation.log
```

### Artifact Contents

**Monthly Reports:**
- Month identifier
- Event count
- Event details (ID, type, severity, description)

**Annual Reports:**
- Year summary
- Total events
- Population and casualties
- Alien control percentage
- Major events (critical/catastrophic only)

**Postmortem:**
- Complete configuration
- Simulation duration metrics
- Final state snapshot
- Alien metrics
- Key events timeline
- Validation summary
- Outcome classification

**Raw Data:**
- Complete event log with parameters
- Validation history with violations
- Timestamped records

### Parsing Artifacts

```python
import json
from pathlib import Path

def analyze_simulation(artifact_dir):
    """Analyze simulation results."""
    # Load postmortem
    postmortem_path = Path(artifact_dir) / "postmortem" / "simulation_postmortem.json"
    with open(postmortem_path) as f:
        postmortem = json.load(f)
    
    # Extract metrics
    outcome = postmortem["outcome_classification"]
    pop_loss = postmortem["final_state"]["population_loss_pct"]
    alien_control = postmortem["final_state"]["alien_control_pct"]
    
    print(f"Outcome: {outcome}")
    print(f"Population Loss: {pop_loss:.1f}%")
    print(f"Alien Control: {alien_control:.1f}%")
    
    # Load annual reports
    annual_dir = Path(artifact_dir) / "annual"
    for report_file in sorted(annual_dir.glob("*.json")):
        with open(report_file) as f:
            report = json.load(f)
        year = report["year"]
        events = report["summary"]["total_events"]
        print(f"Year {year}: {events} events")

# Usage
analyze_simulation("engines/alien_invaders/artifacts")
```

---

## Validation and Quality Assurance

### Pre-Run Validation

```python
def validate_config(config):
    """Validate configuration before running."""
    assert 0.0 <= config.alien.hostile_intent <= 1.0
    assert config.world.simulation_duration_years > 0
    assert config.world.global_population > 0
    assert config.world.time_step_days > 0
    print("Configuration valid")

config = SimulationConfig()
validate_config(config)
```

### Post-Run Validation

```python
def validate_results(engine):
    """Validate simulation results."""
    state = engine.observe("global")
    
    # Check population conservation
    initial_pop = engine.config.world.global_population
    final_pop = state["population"]
    assert final_pop <= initial_pop, "Population increased!"
    
    # Check validation history
    failed_validations = [
        v for v in engine.validation_history if not v.is_valid
    ]
    if failed_validations:
        print(f"WARNING: {len(failed_validations)} validation failures")
    
    print("Results valid")

engine = AlienInvadersEngine()
engine.init()
for _ in range(60):
    engine.tick()
validate_results(engine)
```

---

## Troubleshooting

### Common Issues

**Issue: "Cannot tick: simulation not initialized"**

Solution: Call `init()` before `tick()`
```python
engine = AlienInvadersEngine()
engine.init()  # Required
engine.tick()
```

**Issue: "State validation failed"**

Solution: Check validation violations in log
```python
for validation in engine.validation_history:
    if not validation.is_valid:
        print("Violations:", validation.violations)
```

**Issue: Import errors**

Solution: Ensure Python path includes project root
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

**Issue: Artifacts not generated**

Solution: Check output directory permissions
```bash
mkdir -p engines/alien_invaders/artifacts
chmod 755 engines/alien_invaders/artifacts
```

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

engine = AlienInvadersEngine()
engine.init()

# Tick with detailed output
for i in range(12):
    print(f"\n=== Tick {i} ===")
    if not engine.tick():
        print("FAILED")
        break
    
    state = engine.observe()
    print(f"Day: {state['day_number']}")
    print(f"Events: {state['num_events']}")
```

---

## Performance Optimization

### Reduce Snapshot Frequency

```python
config = SimulationConfig()
config.validation.save_state_frequency = 360  # Once per year instead of monthly
```

### Disable Unnecessary Artifacts

```python
config = SimulationConfig()
config.artifacts.generate_monthly_reports = False  # Skip monthly reports
config.artifacts.include_raw_data = False  # Skip raw data
```

### Batch Multiple Simulations

```python
def run_batch(scenarios, duration=5):
    """Run multiple scenarios efficiently."""
    results = {}
    
    for scenario_name in scenarios:
        config = load_scenario_preset(scenario_name)
        config.world.simulation_duration_years = duration
        config.artifacts.artifact_dir = f"artifacts/{scenario_name}"
        
        engine = AlienInvadersEngine(config)
        engine.init()
        
        for _ in range(duration * 12):
            engine.tick()
        
        engine.export_artifacts()
        results[scenario_name] = engine.observe()
    
    return results

# Run all scenarios
results = run_batch(["standard", "aggressive", "peaceful", "extinction"])
```

---

## Integration with Defense Engine

The AICPD engine is compatible with the existing Defense Engine infrastructure.

### Register with SimulationRegistry

```python
from src.app.core.simulation_contingency_root import SimulationRegistry
from engines.alien_invaders import AlienInvadersEngine

# Initialize engine
engine = AlienInvadersEngine()
engine.init()

# Register
SimulationRegistry.register("alien_invaders", engine)

# Verify registration
systems = SimulationRegistry.list_systems()
print("Registered systems:", systems)
```

### Query from Registry

```python
# Retrieve engine
engine = SimulationRegistry.get("alien_invaders")

if engine:
    state = engine.observe("global")
    print("Current state:", state)
else:
    print("Engine not found")
```

---

## Maintenance

### Artifact Cleanup

```bash
# Remove old artifacts
rm -rf engines/alien_invaders/artifacts/*

# Remove logs
rm engines/alien_invaders/artifacts/*.log
```

### Disk Space Management

```python
import shutil
from pathlib import Path

def cleanup_artifacts(artifact_dir, keep_postmortem=True):
    """Clean up old artifacts."""
    artifact_path = Path(artifact_dir)
    
    # Remove monthly reports
    monthly_dir = artifact_path / "monthly"
    if monthly_dir.exists():
        shutil.rmtree(monthly_dir)
    
    # Keep postmortem if requested
    if not keep_postmortem:
        postmortem_dir = artifact_path / "postmortem"
        if postmortem_dir.exists():
            shutil.rmtree(postmortem_dir)
    
    print("Cleanup complete")

# Usage
cleanup_artifacts("engines/alien_invaders/artifacts", keep_postmortem=True)
```

---

## Production Deployment

### Containerized Execution

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "engines/alien_invaders/run_simulation.py", \
     "--scenario", "standard", \
     "--duration", "5"]
```

### Scheduled Execution

```bash
# Cron job: Run monthly
0 0 1 * * cd /path/to/Project-AI && python engines/alien_invaders/run_simulation.py
```

### CI/CD Integration

```yaml
# .github/workflows/aicpd-simulation.yml
name: AICPD Simulation

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  simulate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: python engines/alien_invaders/run_simulation.py
      - uses: actions/upload-artifact@v2
        with:
          name: simulation-artifacts
          path: engines/alien_invaders/artifacts/
```

---

## Support and Documentation

- **Full Documentation**: `engines/alien_invaders/docs/README.md`
- **API Reference**: `engines/alien_invaders/docs/api/API_REFERENCE.md`
- **Issue Tracking**: GitHub Issues
- **Integration Guide**: Compatible with existing Defense Engine

---

**Ready for deployment. Simulate scenarios. Prepare for contact.** 👽🚀
