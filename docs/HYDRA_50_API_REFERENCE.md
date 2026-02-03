# HYDRA-50 API REFERENCE
**Complete API Documentation**

## Core Engine API

### HYDRA50Engine

Main engine class for scenario management.

```python
from app.core.hydra_50_engine import HYDRA50Engine

engine = HYDRA50Engine(data_dir="data/hydra50")
```

#### Methods

**`list_scenarios() -> List[Dict]`**
Lists all registered scenarios.

Returns:
- List of scenario dictionaries

Example:
```python
scenarios = engine.list_scenarios()
for scenario in scenarios:
    print(f"{scenario['name']}: {scenario['status']}")
```

**`activate_scenario(scenario_id: str) -> Dict`**
Activates a scenario.

Parameters:
- `scenario_id`: Unique scenario identifier

Returns:
- Result dictionary with success status

Example:
```python
result = engine.activate_scenario("scenario_001")
if result['success']:
    print("Scenario activated")
```

**`deactivate_scenario(scenario_id: str) -> Dict`**
Deactivates a scenario.

**`get_scenario_status(scenario_id: str) -> Dict`**
Gets current status of a scenario.

**`get_system_status() -> Dict`**
Gets overall system status.

Returns:
```python
{
    "active_scenarios": 5,
    "critical_scenarios": 2,
    "total_scenarios": 50,
    "system_health": "HEALTHY",
    "uptime_hours": 24.5,
    "cpu_percent": 45.2,
    "memory_percent": 62.1
}
```

## Telemetry API

### HYDRA50TelemetrySystem

Comprehensive telemetry and monitoring.

```python
from app.core.hydra_50_telemetry import HYDRA50TelemetrySystem

telemetry = HYDRA50TelemetrySystem()
```

#### Metrics Collection

**`metrics_collector.record_counter(name, value, tags)`**
Records counter metric.

**`metrics_collector.record_gauge(name, value, tags)`**
Records gauge metric.

**`metrics_collector.record_histogram(name, value, tags)`**
Records histogram metric.

Example:
```python
telemetry.metrics_collector.record_counter(
    "scenarios_activated",
    1.0,
    {"category": "economic"}
)
```

#### Alert Management

**`alert_manager.create_alert(severity, title, message, source)`**
Creates new alert.

Parameters:
- `severity`: AlertSeverity enum
- `title`: Alert title
- `message`: Alert message
- `source`: Source system

Example:
```python
from app.core.hydra_50_telemetry import AlertSeverity

alert = telemetry.alert_manager.create_alert(
    severity=AlertSeverity.CRITICAL,
    title="Scenario Escalation",
    message="Scenario reached critical level",
    source="hydra_engine"
)
```

## Visualization API

### HYDRA50VisualizationEngine

Scenario visualization generation.

```python
from app.core.hydra_50_visualization import HYDRA50VisualizationEngine

viz = HYDRA50VisualizationEngine()
```

#### Visualization Methods

**`render_escalation_ladder(scenario_name, current_level, max_level, ...)`**
Renders escalation ladder visualization.

Returns:
- Tuple of (ascii_output, data_dict)

Example:
```python
ascii, data = viz.render_escalation_ladder(
    scenario_name="Economic Collapse",
    current_level=3,
    max_level=5,
    level_descriptions={
        0: "Baseline",
        1: "Warning",
        2: "Degradation",
        3: "Strain",
        4: "Cascade",
        5: "Collapse"
    },
    level_values={0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
)
print(ascii)
```

**`render_coupling_graph(nodes, edges, title)`**
Renders cross-domain coupling graph.

**`render_temporal_flow(scenario_name, transitions, current_state)`**
Renders temporal state transition flow.

## Analytics API

### HYDRA50AnalyticsEngine

Advanced analytics and machine learning.

```python
from app.core.hydra_50_analytics import HYDRA50AnalyticsEngine

analytics = HYDRA50AnalyticsEngine()
```

#### Statistical Analysis

**`statistical_analyzer.compute_summary(data)`**
Computes statistical summary.

Returns:
```python
StatisticalSummary(
    mean=0.5,
    median=0.48,
    std_dev=0.15,
    variance=0.0225,
    min_value=0.1,
    max_value=0.9,
    q25=0.35,
    q75=0.65,
    skewness=-0.1,
    kurtosis=2.5,
    count=100
)
```

#### Correlation Analysis

**`correlation_analyzer.compute_correlation(data1, data2, method)`**
Computes correlation coefficient.

Methods: "pearson", "spearman", "kendall"

**`correlation_analyzer.find_significant_correlations(data, threshold)`**
Finds significant correlations above threshold.

#### Predictive Modeling

**`predictive_modeler.train_regression_model(name, X, y, features)`**
Trains regression model.

**`predictive_modeler.predict(name, X, confidence_level)`**
Makes prediction with confidence interval.

#### Risk Quantification

**`risk_quantifier.quantify_risk(loss_distribution, confidence_level)`**
Quantifies risk metrics (VaR, CVaR).

Returns:
```python
RiskMetrics(
    value_at_risk=-0.15,
    conditional_var=-0.22,
    expected_loss=0.08,
    max_loss=0.45,
    probability_of_loss=0.35,
    risk_level=RiskLevel.MODERATE,
    confidence_level=0.95
)
```

## Deep Integration API

### HYDRA50DeepIntegration

System-wide integration controller.

```python
from app.core.hydra_50_deep_integration import HYDRA50DeepIntegration

integration = HYDRA50DeepIntegration()
```

#### Integration Methods

**`handle_scenario_trigger(scenario_id, scenario_type, severity, context)`**
Handles scenario trigger with full system integration.

Orchestrates:
1. Planetary Defense validation
2. Cerberus defense (if high severity)
3. SOC incident reporting
4. Command Center threat report
5. Council advisory (if critical)
6. Event Spine broadcasting

Returns:
```python
{
    "scenario_id": "scenario_001",
    "timestamp": "2024-01-15T10:30:45Z",
    "actions": [
        {
            "action": "planetary_defense_validation",
            "status": "passed",
            "message": "Action complies with Four Laws"
        },
        {
            "action": "cerberus_defense",
            "status": "triggered",
            "result": {"agents_spawned": 3}
        }
    ]
}
```

**`get_integration_health() -> Dict[str, str]`**
Gets health status of all integrations.

**`reconnect_all() -> Dict[str, bool]`**
Attempts to reconnect all disconnected integrations.

## Performance API

### HYDRA50PerformanceOptimizer

Performance optimization system.

```python
from app.core.hydra_50_performance import HYDRA50PerformanceOptimizer

optimizer = HYDRA50PerformanceOptimizer()
```

#### Caching

**`lru_cache.get(key) -> Any`**
Gets value from LRU cache.

**`lru_cache.put(key, value)`**
Puts value in LRU cache.

**`ttl_cache.get(key) -> Any`**
Gets value from TTL cache.

**`ttl_cache.put(key, value, ttl_seconds)`**
Puts value in TTL cache with TTL.

#### Memoization Decorator

```python
from app.core.hydra_50_performance import memoize

@memoize(max_size=128)
def expensive_function(x, y):
    # Computation is cached
    return x ** y
```

## Security API

### HYDRA50SecuritySystem

Complete security system.

```python
from app.core.hydra_50_security import HYDRA50SecuritySystem, Role, Permission

security = HYDRA50SecuritySystem()
```

#### User Management

**`access_control.create_user(username, password, role)`**
Creates new user.

**`access_control.authenticate(username, password)`**
Authenticates user.

**`access_control.check_permission(user, permission)`**
Checks if user has permission.

#### Input Validation

**`validator.validate_username(username)`**
Validates username format.

**`validator.validate_password(password)`**
Validates password strength.

**`validator.detect_sql_injection(text)`**
Detects SQL injection attempts.

**`validator.detect_xss(text)`**
Detects XSS attempts.

**`validator.sanitize_string(text)`**
Sanitizes string for safe use.

## CLI Commands

### Scenario Management

```bash
# List scenarios
hydra50 list-scenarios [--category CATEGORY] [--status STATUS] [--json]

# Activate scenario
hydra50 activate SCENARIO_ID [--force]

# Deactivate scenario
hydra50 deactivate SCENARIO_ID

# Get scenario status
hydra50 status SCENARIO_ID [--json]
```

### Simulation

```bash
# Run simulation
hydra50 simulate SCENARIO_ID [--duration-hours HOURS] [--output-file FILE]
```

### Monitoring

```bash
# Real-time monitoring
hydra50 monitor [--interval SECONDS] [--duration SECONDS]
```

### Data Management

```bash
# Export data
hydra50 export OUTPUT_FILE [--format json|csv]

# Import data
hydra50 import-data INPUT_FILE [--format json|csv]
```

## PyQt6 GUI Components

### HYDRA50Panel

Main GUI panel for Leather Book interface.

```python
from app.gui.hydra_50_panel import HYDRA50Panel

panel = HYDRA50Panel()
panel.show()
```

#### Signals

**`scenario_list.scenario_selected`**
Emitted when scenario is selected.

#### Widgets

- `scenario_list`: ScenarioListWidget
- `status_dashboard`: StatusDashboardWidget
- `visualization`: VisualizationWidget
- `alert_management`: AlertManagementWidget
- `control_panel`: ControlPanelWidget
- `historical_replay`: HistoricalReplayWidget

## Event Types

### System Events

Events published to Event Spine:

- `hydra_50_scenario_triggered`
- `hydra_50_scenario_escalated`
- `hydra_50_scenario_deactivated`
- `hydra_50_alert_created`
- `hydra_50_system_health_changed`

## Error Handling

### Exception Types

**`ScenarioNotFoundError`**
Raised when scenario doesn't exist.

**`ScenarioActivationError`**
Raised when scenario activation fails.

**`IntegrationError`**
Raised when system integration fails.

**`ValidationError`**
Raised when input validation fails.

Example:
```python
try:
    engine.activate_scenario("nonexistent")
except ScenarioNotFoundError as e:
    print(f"Scenario not found: {e}")
```

## Type Hints

All APIs include complete type hints for IDE support:

```python
from typing import List, Dict, Optional, Tuple
from app.core.hydra_50_engine import HYDRA50Engine

def process_scenarios(engine: HYDRA50Engine) -> List[Dict[str, Any]]:
    scenarios: List[Dict] = engine.list_scenarios()
    return [s for s in scenarios if s['status'] == 'active']
```
