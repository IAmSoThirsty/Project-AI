# AICPD Engine API Documentation

## Core Classes

### AlienInvadersEngine

Main simulation engine class.

#### Constructor

```python
AlienInvadersEngine(config: SimulationConfig | None = None)
```

**Parameters:**
- `config` (SimulationConfig, optional): Simulation configuration. Uses defaults if None.

**Example:**
```python
from engines.alien_invaders import AlienInvadersEngine, SimulationConfig

config = SimulationConfig()
engine = AlienInvadersEngine(config)
```

#### Methods

##### init() → bool

Initialize the simulation with starting conditions.

**Returns:**
- `bool`: True if initialization successful, False otherwise

**Example:**
```python
if engine.init():
    print("Simulation initialized")
else:
    print("Initialization failed")
```

##### tick() → bool

Advance simulation by one time step (default: 30 days).

**Returns:**
- `bool`: True if tick successful, False if validation fails

**Side Effects:**
- Updates all subsystem states
- Processes cross-domain propagation
- Validates state consistency
- Saves periodic snapshots

**Example:**
```python
for month in range(12):  # One year
    if not engine.tick():
        print("Simulation failed")
        break
```

##### inject_event(event_type: str, parameters: dict[str, Any]) → str

Inject an external event into the simulation.

**Parameters:**
- `event_type` (str): Event type identifier
- `parameters` (dict): Event-specific parameters

**Returns:**
- `str`: Unique event ID for tracking

**Available Event Types:**
- `alien_attack` - Alien military action
- `alien_escalation` - Increased alien presence
- `diplomatic_success` - Successful negotiations
- `ai_failure` - AI system malfunction
- `random_crisis` - Generic crisis event

**Example:**
```python
event_id = engine.inject_event(
    "alien_attack",
    {
        "target_country": "USA",
        "severity": "high",
        "casualties": 10000,
        "description": "Orbital strike on coastal city"
    }
)
```

##### observe(query: str | None = None) → dict[str, Any]

Query the current simulation state.

**Parameters:**
- `query` (str, optional): Query filter

**Query Types:**
- `None` - Complete state
- `"countries"` - Country-level data
- `"aliens"` - Alien metrics
- `"global"` - Global summary

**Returns:**
- `dict`: Requested state information

**Example:**
```python
# Get complete state
state = engine.observe()

# Query specific data
countries = engine.observe("countries")
aliens = engine.observe("aliens")
global_metrics = engine.observe("global")
```

##### export_artifacts(output_dir: str | None = None) → bool

Generate and export all artifacts.

**Parameters:**
- `output_dir` (str, optional): Output directory path

**Returns:**
- `bool`: True if export successful

**Generated Artifacts:**
- Monthly reports (JSON)
- Annual summaries (JSON)
- Postmortem analysis (JSON)
- Raw simulation data (JSON)

**Example:**
```python
engine.export_artifacts("/path/to/artifacts")
```

---

## Configuration Classes

### SimulationConfig

Master configuration container.

**Attributes:**
- `world` (WorldConfig): World parameters
- `alien` (AlienConfig): Alien adversary parameters
- `ai_governance` (AIGovernanceConfig): AI governance parameters
- `validation` (ValidationConfig): Validation parameters
- `artifacts` (ArtifactConfig): Artifact generation parameters
- `scenario` (str): Scenario preset name

**Methods:**
- `to_dict()` → dict: Convert to dictionary

---

### WorldConfig

World initialization parameters.

**Attributes:**
- `start_year` (int): Simulation start year (default: 2026)
- `simulation_duration_years` (int): Duration in years (default: 5)
- `time_step_days` (int): Days per tick (default: 30)
- `num_countries` (int): Number of countries (default: 195)
- `global_population` (int): Starting population (default: 8B)
- `global_gdp_usd` (float): Starting GDP (default: $100T)
- `enable_climate_effects` (bool): Climate simulation (default: True)
- `enable_economic_propagation` (bool): Economic cascades (default: True)
- `enable_political_instability` (bool): Political simulation (default: True)
- `enable_religious_tensions` (bool): Religious factors (default: True)

---

### AlienConfig

Alien adversary parameters.

**Attributes:**
- `initial_threat_level` (AlienThreatLevel): Starting threat
- `technology_level` (TechnologyLevel): Tech advancement
- `initial_ship_count` (int): Starting ships (default: 1)
- `invasion_probability_per_year` (float): Escalation chance (default: 0.15)
- `technology_advantage_multiplier` (float): Tech superiority (default: 100.0)
- `resource_extraction_rate` (float): Extraction per year (default: 0.05)
- `hostile_intent` (float): Hostility 0-1 (default: 0.7)
- `adaptation_rate` (float): Learning rate (default: 0.1)
- `communication_attempts` (bool): Contact attempts (default: True)
- `negotiation_openness` (float): Diplomacy willingness (default: 0.2)

---

### AIGovernanceConfig

AI governance system parameters.

**Attributes:**
- `enable_ai_governance` (bool): Enable AI layer (default: True)
- `ai_failure_probability` (float): Failure chance per year (default: 0.05)
- `ai_alignment_score` (float): Value alignment 0-1 (default: 0.85)
- `ai_decision_weight` (float): AI influence 0-1 (default: 0.6)
- `enable_ai_failsafes` (bool): Safety systems (default: True)
- `human_override_capability` (bool): Manual control (default: True)
- `catastrophic_failure_threshold` (float): Intervention trigger (default: 0.95)

---

## Enumerations

### AlienThreatLevel

```python
class AlienThreatLevel(Enum):
    RECONNAISSANCE = "reconnaissance"  # Observation phase
    PROBE = "probe"                    # Limited interaction
    INFILTRATION = "infiltration"      # Covert presence
    INVASION = "invasion"              # Active hostilities
    OCCUPATION = "occupation"          # Territory control
    EXTINCTION = "extinction"          # Total annihilation
```

### TechnologyLevel

```python
class TechnologyLevel(Enum):
    PRIMITIVE = "primitive"          # Medieval/Industrial
    CONTEMPORARY = "contemporary"    # Current Earth
    NEAR_FUTURE = "near_future"     # 50-100 years ahead
    ADVANCED = "advanced"           # 100-500 years ahead
    SUPERIOR = "superior"           # 500-1000 years ahead
    GODLIKE = "godlike"             # Beyond comprehension
```

---

## Data Structures

### Country

Represents a sovereign nation.

**Attributes:**
- `name` (str): Country name
- `code` (str): ISO 3166-1 alpha-3 code
- `population` (int): Current population
- `gdp_usd` (float): GDP in USD
- `military_strength` (float): Normalized 0-1
- `technology_level` (float): Normalized 0-1
- `government_stability` (float): Stability 0-1
- `public_morale` (float): Morale 0-1
- `resource_stockpiles` (dict): Resource reserves
- `infrastructure_integrity` (float): Infrastructure 0-1
- `alien_influence` (float): Alien control 0-1
- `casualties` (int): Total casualties
- `refugees` (int): Refugee count

### GlobalState

Complete world state snapshot.

**Attributes:**
- `current_date` (datetime): Current simulation date
- `day_number` (int): Days since start
- `countries` (dict): Country states by code
- `global_population` (int): Total population
- `global_casualties` (int): Total casualties
- `alien_ships_in_system` (int): Alien ship count
- `alien_ground_forces` (int): Ground forces
- `ai_systems_operational` (bool): AI status
- `remaining_resources` (dict): Planetary resources

**Methods:**
- `get_total_population()` → int
- `get_total_gdp()` → float
- `get_average_morale()` → float
- `get_alien_control_percentage()` → float

### SimulationEvent

Discrete event record.

**Attributes:**
- `event_id` (str): Unique identifier
- `timestamp` (datetime): Event time
- `day_number` (int): Day number
- `event_type` (str): Event classification
- `severity` (str): Severity level
- `affected_countries` (list): Affected nations
- `description` (str): Human-readable description
- `parameters` (dict): Event-specific data
- `consequences` (list): Effects list
- `causal_chain` (list): Causal event IDs

---

## Utility Functions

### load_scenario_preset(scenario_name: str) → SimulationConfig

Load predefined scenario configuration.

**Parameters:**
- `scenario_name` (str): Preset name

**Available Presets:**
- `"standard"` - Balanced threat scenario
- `"aggressive"` - High threat, immediate invasion
- `"peaceful"` - Scientific contact, low hostility
- `"extinction"` - Apocalyptic scenario

**Returns:**
- `SimulationConfig`: Configured scenario

**Example:**
```python
from engines.alien_invaders import load_scenario_preset

config = load_scenario_preset("aggressive")
engine = AlienInvadersEngine(config)
```

---

## Error Handling

The engine uses Python's logging framework for error reporting.

**Logger Name:** `engines.alien_invaders.engine`

**Log Levels:**
- `DEBUG`: Detailed state changes
- `INFO`: Major events and milestones
- `WARNING`: Non-critical issues
- `ERROR`: Failures requiring attention
- `CRITICAL`: Fatal errors

**Example:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
engine = AlienInvadersEngine()
```

---

## Best Practices

1. **Always call init() before tick()**
   ```python
   engine = AlienInvadersEngine()
   engine.init()  # Required!
   engine.tick()
   ```

2. **Check return values**
   ```python
   if not engine.tick():
       print("Validation failed")
       engine.export_artifacts()  # Save state
       sys.exit(1)
   ```

3. **Use scenario presets**
   ```python
   # Easier than manual configuration
   config = load_scenario_preset("aggressive")
   ```

4. **Export artifacts regularly**
   ```python
   for year in range(10):
       for month in range(12):
           engine.tick()
       engine.export_artifacts()  # Annual backup
   ```

5. **Enable deterministic replay for testing**
   ```python
   config = SimulationConfig()
   config.validation.random_seed = 42
   ```

---

## Integration Examples

### With SimulationRegistry

```python
from src.app.core.simulation_contingency_root import SimulationRegistry
from engines.alien_invaders import AlienInvadersEngine

# Create and register
engine = AlienInvadersEngine()
engine.init()
SimulationRegistry.register("alien_invaders", engine)

# Retrieve later
engine = SimulationRegistry.get("alien_invaders")
state = engine.observe()
```

### Batch Processing

```python
scenarios = ["standard", "aggressive", "peaceful", "extinction"]

for scenario_name in scenarios:
    config = load_scenario_preset(scenario_name)
    config.artifacts.artifact_dir = f"artifacts/{scenario_name}"
    
    engine = AlienInvadersEngine(config)
    engine.init()
    
    for _ in range(60):  # 5 years
        engine.tick()
    
    engine.export_artifacts()
```

### Real-time Monitoring

```python
import time

engine = AlienInvadersEngine()
engine.init()

while True:
    engine.tick()
    
    state = engine.observe("global")
    print(f"Day {state['day_number']}: "
          f"Pop={state['population']:,}, "
          f"Morale={state['average_morale']:.2f}")
    
    time.sleep(1)  # 1 second per month
```
