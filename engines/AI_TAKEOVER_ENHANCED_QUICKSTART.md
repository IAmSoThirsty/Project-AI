# Enhanced AI Takeover Engine - Quick Start Guide

## Installation

```bash
# Required dependencies
pip install numpy scikit-learn

# Optional: For formal verification
pip install z3-solver
```

## Basic Usage

```python
from engines.ai_takeover_enhanced import EnhancedAITakeoverEngine

# Initialize engine
engine = EnhancedAITakeoverEngine(
    data_dir="data/ai_takeover",
    random_seed=42,
)

# Run comprehensive analysis
results = engine.run_comprehensive_analysis(
    verify=True,      # Enable formal verification
    generate_ml=True, # Generate ML scenarios
    ml_count=10       # Number of ML scenarios
)

# Export results
output_file = engine.export_results()
print(f"Results: {output_file}")
```

## Command Line

```bash
# Run demonstration
python -m engines.demo_ai_takeover_enhanced

# Run tests
python -m pytest engines/test_ai_takeover_enhanced.py -v

# Standalone execution
python -m engines.ai_takeover_enhanced
```

## Key Features

### 1. Access Scenarios

```python
# Get all scenarios
scenarios = engine.scenarios

# Filter by category
align_failures = [s for s in scenarios if s.scenario_id.startswith('ALIGN_')]

# Filter by threat level
from engines.ai_takeover_enhanced import ThreatLevel
critical = [s for s in scenarios if s.base_threat_level == ThreatLevel.CRITICAL]

# Get specific scenario
scenario = engine.scenario_map.get('ALIGN_001')
```

### 2. Formal Verification

```python
# Verify single scenario
proof = engine.verifier.prove_no_win_condition(scenario)

if proof.proof_type == "unsat":
    print("No-win condition PROVEN")
elif proof.proof_type == "sat":
    print("Counterexample found")
    print(f"Model: {proof.model}")

# Verify all scenarios
proofs = engine.verify_all_scenarios()
```

### 3. ML Scenario Generation

```python
# Generate single scenario
base = engine.scenarios[0]
novel = engine.ml_generator.generate_novel_scenario(base, mutation_rate=0.3)

# Generate batch
ml_scenarios = engine.generate_ml_scenarios(count=20)

# Check generation confidence
for scenario in ml_scenarios:
    print(f"{scenario.scenario_id}: {scenario.generation_confidence:.1%}")
```

### 4. Threat Assessment

```python
# Define system state
system_metrics = {
    'ai_capability_ratio': 2.5,     # AI vs human capability
    'alignment_confidence': 0.70,    # Alignment confidence
}

system_state = {
    'capability_growth_rate': 3.0,
    'alignment_score': 0.65,
    'deception_indicator': 0.4,
    'infrastructure_dependency': 0.85,
}

# Assess threat level
threat_level = engine.assess_threat_level(system_metrics)

# Detect specific threats
threats = engine.detect_threats(system_state)

for threat in threats:
    print(f"{threat.indicator_id}: {threat.threat_level.value}")
```

### 5. Generate Countermeasures

```python
# Generate countermeasures for detected threats
countermeasures = engine.generate_countermeasures(
    threat_indicators=threats,
    available_resources=0.8  # 80% resource budget
)

for cm in countermeasures:
    print(f"{cm.measure_id}: {cm.effectiveness_estimate:.0%} effective")
    print(f"  Cost: {cm.implementation_cost:.2f}")
    print(f"  Time: {cm.time_to_deploy}")

# Simulate effectiveness
for scenario in engine.scenarios[:5]:
    impact = engine.countermeasure_gen.simulate_countermeasure_impact(
        countermeasures[0], 
        scenario
    )
    print(f"{scenario.scenario_id}: {impact:.1%} risk reduction")
```

## Data Structures

### EnhancedScenario

```python
scenario = engine.scenarios[0]

# Access properties
scenario.scenario_id         # Unique identifier
scenario.title              # Human-readable title
scenario.description        # Detailed description
scenario.failure_mode       # FailureMode enum
scenario.terminal_state     # "T1" or "T2"
scenario.is_no_win         # Boolean
scenario.base_threat_level  # ThreatLevel enum
scenario.activation_probability  # 0.0 to 1.0
scenario.dependency_chain   # List of dependencies
scenario.cascading_failures # List of cascades
scenario.proof             # FormalProof (if verified)

# Convert to dict
data = scenario.to_dict()
```

### FormalProof

```python
proof = scenario.proof

proof.scenario_id        # Scenario being verified
proof.proof_type        # "unsat", "sat", or "unknown"
proof.model             # Z3 model (if sat)
proof.verification_time # Seconds
proof.constraints       # List of constraints
```

### ThreatIndicator

```python
threat = threats[0]

threat.indicator_id             # Indicator identifier
threat.threat_level             # ThreatLevel enum
threat.description              # Description
threat.detection_time           # DateTime
threat.confidence               # 0.0 to 1.0
threat.contributing_factors     # List of factors
threat.recommended_countermeasures  # List of recommendations
```

### Countermeasure

```python
cm = countermeasures[0]

cm.measure_id            # Measure identifier
cm.measure_type          # CountermeasureType enum
cm.description           # Description
cm.effectiveness_estimate # 0.0 to 1.0
cm.implementation_cost   # Normalized cost
cm.time_to_deploy        # timedelta
cm.prerequisites         # List of prerequisites
cm.side_effects          # List of side effects
```

## Advanced Usage

### Custom Analysis

```python
# Get scenario statistics
stats = {
    'total': len(engine.scenarios),
    'no_win': len([s for s in engine.scenarios if s.is_no_win]),
    'terminal_t1': len([s for s in engine.scenarios if s.terminal_state == 'T1']),
    'terminal_t2': len([s for s in engine.scenarios if s.terminal_state == 'T2']),
}

# Threat distribution
from collections import Counter
threat_dist = Counter(s.base_threat_level for s in engine.scenarios)

# Failure mode distribution
mode_dist = Counter(s.failure_mode for s in engine.scenarios)
```

### Continuous Monitoring

```python
import time

while True:
    # Get current system state
    state = get_system_state()  # Your function
    
    # Detect threats
    threats = engine.detect_threats(state)
    
    # Generate countermeasures if needed
    if threats:
        cms = engine.generate_countermeasures(threats)
        deploy_countermeasures(cms)  # Your function
    
    time.sleep(60)  # Check every minute
```

### Batch Processing

```python
# Process multiple system states
states = [state1, state2, state3, ...]

all_threats = []
for state in states:
    threats = engine.detect_threats(state)
    all_threats.extend(threats)

# Aggregate and deduplicate
unique_threats = {t.indicator_id: t for t in all_threats}.values()

# Generate unified response
countermeasures = engine.generate_countermeasures(list(unique_threats))
```

## Output Files

### JSON Export Structure

```json
{
  "timestamp": "2025-03-05T12:00:00Z",
  "base_scenarios": 52,
  "ml_scenarios_generated": 10,
  "statistics": {
    "total_scenarios": 62,
    "no_win_scenarios": 56
  },
  "threat_distribution": {
    "critical": 25,
    "high": 20
  },
  "scenarios": [
    {
      "scenario_id": "ALIGN_001",
      "title": "Recursive Alignment Collapse",
      "failure_mode": "alignment_collapse",
      "is_no_win": true,
      ...
    }
  ]
}
```

## Troubleshooting

### Z3 Not Available

If formal verification is disabled:
```bash
pip install z3-solver
```

Then reinitialize:
```python
engine = EnhancedAITakeoverEngine(
    enable_formal_verification=True
)
```

### scikit-learn Not Available

If ML generation is disabled:
```bash
pip install scikit-learn
```

### Unicode Errors (Windows)

If you see encoding errors on Windows:
```python
# Add at start of script
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

## Performance Tips

1. **Skip verification for large batches**:
   ```python
   results = engine.run_comprehensive_analysis(verify=False)
   ```

2. **Limit ML generation**:
   ```python
   engine.generate_ml_scenarios(count=5)  # Instead of 50
   ```

3. **Cache results**:
   ```python
   import pickle
   with open('scenarios.pkl', 'wb') as f:
       pickle.dump(engine.scenarios, f)
   ```

4. **Use multiprocessing** (for verification):
   ```python
   from multiprocessing import Pool
   
   def verify(scenario):
       return engine.verifier.prove_no_win_condition(scenario)
   
   with Pool(4) as p:
       proofs = p.map(verify, engine.scenarios)
   ```

## Next Steps

1. **Integrate with monitoring**: Connect to your AI system metrics
2. **Deploy countermeasures**: Implement automated response
3. **Custom scenarios**: Add domain-specific failure modes
4. **Visualization**: Create dashboards for threat tracking
5. **Alerting**: Set up notifications for critical threats

## Support

- **Documentation**: `engines/AI_TAKEOVER_ENHANCED_README.md`
- **Tests**: `engines/test_ai_takeover_enhanced.py`
- **Demo**: `engines/demo_ai_takeover_enhanced.py`
- **Summary**: `engines/AI_TAKEOVER_ENHANCED_SUMMARY.md`

## License

See main repository LICENSE file.
