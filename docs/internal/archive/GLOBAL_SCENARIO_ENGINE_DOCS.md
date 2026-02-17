# Global Scenario Engine - Technical Documentation

## Overview

The **Global Scenario Engine** is a production-grade, monolithic risk analysis system that loads real-world data from multiple sources, detects anomalies, builds causal models, and generates probabilistic crisis scenarios with actionable alerts.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│           Simulation Contingency Root (Contract)            │
│  - Abstract interface for all simulation systems            │
│  - SimulationRegistry for system management                 │
│  - Common data structures (ThresholdEvent, CausalLink, etc) │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ implements
                            │
┌─────────────────────────────────────────────────────────────┐
│                Global Scenario Engine                        │
├─────────────────────────────────────────────────────────────┤
│  ETL Layer:                                                  │
│    - WorldBankDataSource (GDP, inflation, unemployment)     │
│    - ACLEDDataSource (conflict events)                      │
│    - Intelligent caching (30-day TTL, SHA256 keys)          │
│                                                              │
│  Detection Layer:                                            │
│    - Z-score based threshold detection                      │
│    - Absolute value thresholds per domain                   │
│    - Configurable sensitivity                               │
│                                                              │
│  Analysis Layer:                                             │
│    - Causal relationship modeling                           │
│    - Historical event correlation                           │
│    - Domain expertise validation                            │
│                                                              │
│  Simulation Layer:                                           │
│    - Monte Carlo probabilistic simulation                   │
│    - 10-year forward projection                             │
│    - Compound crisis detection                              │
│                                                              │
│  Alert Layer:                                                │
│    - Risk scoring (0-100 scale)                             │
│    - Evidence gathering                                      │
│    - Explainability generation                              │
│    - Action recommendations                                  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```

1. ETL Pipeline

   ├─ World Bank API → Economic indicators
   ├─ ACLED API → Conflict events
   └─ Cache → Disk storage (30-day TTL)

2. Threshold Detection

   ├─ Load historical data (2016-YTD)
   ├─ Calculate Z-scores per country/domain
   ├─ Apply absolute thresholds
   └─ Record threshold events

3. Causal Model Building

   ├─ Group events by domain/country
   ├─ Apply domain expertise rules
   ├─ Validate with historical correlations
   └─ Generate causal links

4. Scenario Simulation

   ├─ Define scenario templates
   ├─ Run Monte Carlo (1000 iterations/year)
   ├─ Calculate likelihoods
   └─ Generate 10-year projections

5. Alert Generation

   ├─ Filter high-probability scenarios (>threshold)
   ├─ Calculate risk scores
   ├─ Generate explainability
   └─ Issue crisis alerts
```

## Key Features

### 1. Real-World ETL Pipelines

**World Bank Data Source**

- **API**: https://api.worldbank.org/v2
- **Indicators**:
  - GDP growth (annual %)
  - GDP per capita (current US$)
  - Inflation, consumer prices (annual %)
  - Unemployment, total (% of labor force)
  - Trade (% of GDP)
  - CO2 emissions (metric tons per capita)
  - And 4 more...

**ACLED Data Source**

- **API**: https://api.acleddata.com/acled/read
- **Data**: Armed conflict and civil unrest events
- **Fallback**: Synthetic data generation when API unavailable
- **Coverage**: Global conflict events with fatality counts

**Caching Strategy**

- SHA256-based cache keys
- 30-day expiration
- Automatic retry with exponential backoff
- Graceful degradation to cached data

### 2. Statistical Threshold Detection

**Z-Score Analysis**

```python
z_score = (value - mean) / std
threshold = mean + (z_threshold * std)
severity = min(1.0, z_score / 4.0)
```

**Domain-Specific Thresholds**

- **Economic**: Z-score 2.0, GDP drop > -3.0%
- **Inflation**: Z-score 2.5, absolute > 10%
- **Unemployment**: Z-score 2.0, absolute > 15%
- **Civil Unrest**: Events per 100k population > 1.0
- **Climate**: CO2 growth > 5%

### 3. Causal Modeling

**Pre-Defined Relationships** (validated with historical data)

| Source Domain | Target Domain | Strength | Lag (years) | Confidence |
| ------------- | ------------- | -------- | ----------- | ---------- |
| Economic      | Unemployment  | 0.80     | 0.5         | 80-90%     |
| Economic      | Civil Unrest  | 0.70     | 1.0         | 80%        |
| Unemployment  | Civil Unrest  | 0.75     | 0.5         | 80%        |
| Inflation     | Economic      | 0.60     | 0.5         | 80%        |
| Climate       | Migration     | 0.65     | 2.0         | 80%        |
| Civil Unrest  | Migration     | 0.70     | 1.0         | 80%        |
| Trade         | Economic      | 0.60     | 0.25        | 80%        |

### 4. Scenario Templates

**Compound Crisis Patterns**

1. **Global Economic Collapse** (CATASTROPHIC)

   - Domains: Economic, Unemployment, Trade
   - Base Probability: 5%

1. **Regional Conflict Escalation** (CRITICAL)

   - Domains: Civil Unrest, Military, Migration
   - Base Probability: 15%

1. **Climate-Driven Migration Crisis** (HIGH)

   - Domains: Climate, Migration, Food
   - Base Probability: 25%

1. **Pandemic Resurgence** (HIGH)

   - Domains: Pandemic, Economic, Supply Chain
   - Base Probability: 20%

1. **Inflation Spiral with Social Unrest** (HIGH)

   - Domains: Inflation, Unemployment, Civil Unrest
   - Base Probability: 30%

1. **Cybersecurity Catastrophe** (CRITICAL)

   - Domains: Cybersecurity, Financial, Supply Chain
   - Base Probability: 10%

### 5. Monte Carlo Simulation

**Algorithm**

```python
for year in projection_years:
    for scenario in templates:
        for iteration in num_simulations:

            # Calculate probability factors

            trigger_factor = count_triggers / total_events
            causal_factor = sum(link.strength) / total_links
            base_prob = scenario.base_probability

            # Combine factors with noise

            prob = (base_prob * 0.5 +
                   trigger_factor * 0.3 +
                   causal_factor * 0.2 +
                   random(-0.05, 0.05))

            # Apply temporal decay

            prob *= (1.0 - 0.05 * year_offset)

            # Record success

            if random() < prob:
                successes += 1

        likelihood = successes / num_simulations
```

### 6. Alert Generation

**Risk Scoring**

```
risk_score = likelihood * severity_weight

severity_weights = {
    LOW: 20,
    MEDIUM: 40,
    HIGH: 60,
    CRITICAL: 80,
    CATASTROPHIC: 100
}
```

**Explainability Format**

```markdown

# Scenario: [Title]

**Likelihood**: X.X%
**Severity**: LEVEL
**Projection Year**: YYYY

## Triggering Evidence

1. Country - Domain: metric = value (threshold: T, severity: S%)
2. ...

## Causal Chain Analysis

1. Source → Target (strength: X, lag: Y years, confidence: Z%)
2. ...

## Affected Regions

Countries: [list]

## Impact Domains

[list of domains]
```

## API Reference

### Core Classes

#### `SimulationSystem` (Abstract Base)

```python
class SimulationSystem(ABC):
    @abstractmethod
    def initialize() -> bool

    @abstractmethod
    def load_historical_data(
        start_year: int,
        end_year: int,
        domains: Optional[List[RiskDomain]] = None,
        countries: Optional[List[str]] = None
    ) -> bool

    @abstractmethod
    def detect_threshold_events(
        year: int,
        domains: Optional[List[RiskDomain]] = None
    ) -> List[ThresholdEvent]

    @abstractmethod
    def build_causal_model(
        historical_events: List[ThresholdEvent]
    ) -> List[CausalLink]

    @abstractmethod
    def simulate_scenarios(
        projection_years: int = 10,
        num_simulations: int = 1000
    ) -> List[ScenarioProjection]

    @abstractmethod
    def generate_alerts(
        scenarios: List[ScenarioProjection],
        threshold: float = 0.7
    ) -> List[CrisisAlert]

    @abstractmethod
    def get_explainability(
        scenario: ScenarioProjection
    ) -> str

    @abstractmethod
    def persist_state() -> bool

    @abstractmethod
    def validate_data_quality() -> Dict[str, Any]
```

#### `GlobalScenarioEngine`

```python
class GlobalScenarioEngine(SimulationSystem):
    def __init__(self, data_dir: str = "data/global_scenarios"):
        """Initialize engine with data directory."""

    # Implements all SimulationSystem methods

    # Additional attributes:

    # - world_bank: WorldBankDataSource

    # - acled: ACLEDDataSource

    # - historical_data: Dict[RiskDomain, Dict[str, Dict[int, float]]]

    # - threshold_events: List[ThresholdEvent]

    # - causal_links: List[CausalLink]

    # - scenarios: List[ScenarioProjection]

    # - alerts: List[CrisisAlert]

    # - thresholds: Dict[RiskDomain, Dict]

```

#### `SimulationRegistry`

```python
class SimulationRegistry:
    @classmethod
    def register(cls, name: str, system: SimulationSystem) -> None

    @classmethod
    def get(cls, name: str) -> Optional[SimulationSystem]

    @classmethod
    def list_systems(cls) -> List[str]

    @classmethod
    def unregister(cls, name: str) -> bool
```

### Data Structures

#### `RiskDomain` (Enum)

```python
ECONOMIC, INFLATION, UNEMPLOYMENT, CIVIL_UNREST, CLIMATE,
PANDEMIC, BIOSECURITY, MIGRATION, TRADE, MILITARY,
CYBERSECURITY, POLITICAL, TERRORISM, SUPPLY_CHAIN,
FOOD, WATER, ENERGY, NUCLEAR, SPACE, FINANCIAL
```

#### `AlertLevel` (Enum)

```python
LOW, MEDIUM, HIGH, CRITICAL, CATASTROPHIC
```

#### `ThresholdEvent` (Dataclass)

```python
@dataclass
class ThresholdEvent:
    event_id: str
    timestamp: datetime
    country: str
    domain: RiskDomain
    metric_name: str
    value: float
    threshold: float
    severity: float  # 0-1 scale
    context: Dict[str, Any]
```

#### `CausalLink` (Dataclass)

```python
@dataclass
class CausalLink:
    source: str
    target: str
    strength: float  # 0-1
    lag_years: float
    evidence: List[str]
    confidence: float  # 0-1
```

#### `ScenarioProjection` (Dataclass)

```python
@dataclass
class ScenarioProjection:
    scenario_id: str
    year: int
    likelihood: float  # 0-1
    title: str
    description: str
    trigger_events: List[ThresholdEvent]
    causal_chain: List[CausalLink]
    affected_countries: Set[str]
    impact_domains: Set[RiskDomain]
    severity: AlertLevel
    mitigation_strategies: List[str]
```

#### `CrisisAlert` (Dataclass)

```python
@dataclass
class CrisisAlert:
    alert_id: str
    timestamp: datetime
    scenario: ScenarioProjection
    evidence: List[ThresholdEvent]
    causal_activation: List[CausalLink]
    risk_score: float  # 0-100
    explainability: str
    recommended_actions: List[str]
```

## Usage Examples

### Basic Usage

```python
from app.core.global_scenario_engine import GlobalScenarioEngine

# Initialize engine

engine = GlobalScenarioEngine(data_dir="data/scenarios")
engine.initialize()

# Load historical data

engine.load_historical_data(
    start_year=2016,
    end_year=2024,
    countries=["USA", "CHN", "GBR"]
)

# Detect threshold events

events = engine.detect_threshold_events(2023)

# Build causal model

causal_links = engine.build_causal_model(engine.threshold_events)

# Run simulation

scenarios = engine.simulate_scenarios(
    projection_years=10,
    num_simulations=1000
)

# Generate alerts

alerts = engine.generate_alerts(scenarios, threshold=0.7)

# Get explainability

for alert in alerts:
    explanation = engine.get_explainability(alert.scenario)
    print(explanation)

# Persist state

engine.persist_state()
```

### Using the Registry

```python
from app.core.global_scenario_engine import register_global_scenario_engine
from app.core.simulation_contingency_root import SimulationRegistry

# Register engine

engine = register_global_scenario_engine()

# Retrieve from registry

retrieved = SimulationRegistry.get("global_scenario_engine")

# List all systems

systems = SimulationRegistry.list_systems()
```

### Custom Configuration

```python

# Create engine with custom thresholds

engine = GlobalScenarioEngine(data_dir="custom_data")
engine.thresholds[RiskDomain.ECONOMIC] = {
    "z_score": 3.0,  # More stringent
    "gdp_drop": -5.0
}
```

## Configuration

### Environment Variables

Required for full functionality:

```bash

# Optional: ACLED API (falls back to synthetic data if not set)

ACLED_API_KEY=your_key_here
ACLED_API_EMAIL=your_email@example.com
```

### Threshold Configuration

Edit in code:

```python
engine.thresholds = {
    RiskDomain.ECONOMIC: {
        "z_score": 2.0,
        "gdp_drop": -3.0
    },
    RiskDomain.INFLATION: {
        "z_score": 2.5,
        "absolute": 10.0
    },

    # ... add more domains

}
```

## Performance Considerations

### Data Loading

- **Initial Load**: 30-60 seconds (depends on API response times)
- **Cached Load**: \<1 second (uses local cache)
- **Cache Expiration**: 30 days

### Simulation

- **1000 iterations**: ~1-2 seconds
- **60 scenarios (6 templates × 10 years)**: ~3-5 seconds total

### Memory Usage

- **Typical**: 50-100 MB
- **Large datasets** (200+ countries): 200-300 MB

## Testing

### Run Tests

```bash

# All tests

pytest tests/test_global_scenario_engine.py -v

# Specific test class

pytest tests/test_global_scenario_engine.py::TestGlobalScenarioEngine -v

# With coverage

pytest tests/test_global_scenario_engine.py --cov=app.core.global_scenario_engine
```

### Test Coverage

- **21 tests** covering:
  - Contract interface
  - ETL connectors
  - Threshold detection
  - Causal modeling
  - Scenario simulation
  - Alert generation
  - State persistence
  - Data validation
  - Full integration workflow

## Extending the Engine

### Adding New Data Sources

```python
class CustomDataSource(DataSource):
    """Custom ETL connector."""

    def fetch_custom_data(self, params):

        # Implement custom data fetching

        url = "https://api.example.com/data"
        data = self.fetch_with_retry(url, params)
        return self._transform_data(data)

    def _transform_data(self, raw_data):

        # Transform to standard format

        return {
            "country": {year: value}
        }

# In GlobalScenarioEngine.__init__:

self.custom_source = CustomDataSource(str(cache_dir / "custom"))
```

### Adding New Risk Domains

```python

# In simulation_contingency_root.py

class RiskDomain(Enum):

    # ... existing domains

    QUANTUM_COMPUTING = "quantum_computing"
    SPACE_DEBRIS = "space_debris"

# In GlobalScenarioEngine.load_historical_data:

# Add data loading logic for new domains

quantum_data = self.custom_source.fetch_quantum_data(...)
self.historical_data[RiskDomain.QUANTUM_COMPUTING] = quantum_data
```

### Adding New Scenario Templates

```python

# In GlobalScenarioEngine.simulate_scenarios:

scenario_templates.append({
    "title": "Quantum Computing Disruption",
    "domains": [
        RiskDomain.QUANTUM_COMPUTING,
        RiskDomain.CYBERSECURITY,
        RiskDomain.FINANCIAL
    ],
    "severity": AlertLevel.CRITICAL,
    "base_probability": 0.12
})
```

## Troubleshooting

### API Connection Issues

**Symptom**: `Failed to fetch data from [URL]` **Solution**:

1. Check internet connectivity
1. Verify API endpoints are accessible
1. Check for rate limiting
1. Use cached data (automatic fallback)

### ACLED API Credentials

**Symptom**: `ACLED API credentials not found` **Solution**:

1. Set environment variables: `ACLED_API_KEY`, `ACLED_API_EMAIL`
1. Or let engine use synthetic fallback data (no action required)

### Low Data Quality Score

**Symptom**: Quality score < 70 **Solution**:

1. Increase country coverage
1. Load more historical years
1. Add more data sources
1. Validate API credentials

### Memory Issues

**Symptom**: Out of memory errors **Solution**:

1. Reduce `num_simulations` (default 1000 → 500)
1. Reduce `projection_years` (default 10 → 5)
1. Load fewer countries at once
1. Enable incremental processing

## Production Deployment

### Recommended Setup

```bash

# Install dependencies

pip install -r requirements.txt

# Set environment variables

export ACLED_API_KEY=your_key
export ACLED_API_EMAIL=your_email

# Run demo

python demo_global_scenario_engine.py

# Or integrate into your application

python your_app.py
```

### Scheduled Updates

Use cron/scheduler to refresh data:

```python

# refresh_scenarios.py

from app.core.global_scenario_engine import register_global_scenario_engine

engine = register_global_scenario_engine()
engine.initialize()
engine.load_historical_data(2016, 2024)

# ... run full workflow

engine.persist_state()
```

```cron

# Run daily at 2 AM

0 2 * * * cd /path/to/Project-AI && python refresh_scenarios.py
```

### Monitoring

```python

# Check engine health

validation = engine.validate_data_quality()
if validation['quality_score'] < 70:
    logger.warning(f"Low quality: {validation['issues']}")

# Monitor alert frequency

if len(engine.alerts) > 10:
    logger.warning("High alert frequency - potential systemic crisis")
```

## License

MIT License - See LICENSE file for details.

## Contributors

Project-AI Team

## Support

For issues, questions, or contributions:

- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: See README.md and other docs in repository
