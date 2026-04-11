# Enhanced Red Team Simulation - Documentation

## Overview

The Enhanced Red Team Engine provides AI-powered adversarial testing capabilities for governance systems with comprehensive attack simulation, vulnerability discovery, and MITRE ATT&CK framework coverage.

## Features

### 1. AI-Powered Adversaries (Reinforcement Learning)

The engine includes a Deep Q-Network (DQN) based RL agent that learns optimal attack strategies:

- **State Representation**: 10-dimensional state vector capturing trust, legitimacy, governance capacity, etc.
- **Action Space**: 10 different attack actions including targeted and coordinated attacks
- **Learning**: Q-learning with experience replay and epsilon-greedy exploration
- **Adaptation**: Agent improves attack success rate over time

**Example Usage:**
```python
from engines.red_team_enhanced import EnhancedRedTeamEngine

# Initialize with RL enabled
engine = EnhancedRedTeamEngine(enable_rl=True)

# Execute attacks - agent learns from each attack
state = {"trust": 0.6, "legitimacy": 0.7, ...}
result = engine.execute_attack(state, use_exploit_chain=True)

# Check learning progress
stats = engine.get_rl_agent_stats()
print(f"Epsilon: {stats['epsilon']}")  # Decreases as agent learns
print(f"Experiences: {stats['total_experiences']}")
```

### 2. Adaptive Attack Strategies

Attacks adapt based on observed defense effectiveness:

- **Defense Tracking**: Monitors defense effectiveness per technique
- **Strategy Adjustment**: Reduces attack effectiveness as defenses adapt
- **Multi-Strategy Support**: Switches between aggressive, stealth, and adaptive modes

**Example:**
```python
# Defenses adapt to repeated techniques
result1 = engine.execute_attack(state, adapt_to_defenses=True)
result2 = engine.execute_attack(state, adapt_to_defenses=True)

# Second attack less effective if same technique used
assert result2['damage'] <= result1['damage']
```

### 3. Exploit Chain Generation

Automatically discovers and chains vulnerabilities for maximum impact:

- **Vulnerability Chaining**: Links exploits based on prerequisites
- **Impact Calculation**: Computes cumulative damage of chains
- **Success Probability**: Estimates chain execution success
- **Optimization**: Ranks chains by total impact

**Example:**
```python
# Discover vulnerabilities
vulns = engine.discover_vulnerabilities(state)

# Generate exploit chains
chains = engine.chain_generator.generate_chains(max_chain_length=5)

# Get best chain
best = engine.chain_generator.get_best_chain(min_impact=0.5)
print(f"Chain: {best.execution_order}")
print(f"Impact: {best.total_impact}")
```

### 4. Automated Vulnerability Discovery

#### Fuzzing Engine

Generates random test inputs to discover edge cases:

- **Mutation Types**: Extreme values, boundary conditions, rapid oscillation
- **Crash Detection**: Identifies collapse conditions
- **Vulnerability Classification**: Categorizes by type and severity

**Example:**
```python
# Generate fuzz inputs
fuzz_inputs = engine.fuzzing_engine.generate_fuzz_inputs(count=100)

# Test each input
for fuzz_input in fuzz_inputs:
    result = engine.fuzzing_engine.test_input(fuzz_input, state)
    if result['vulnerability_found']:
        print(f"Found: {result['vulnerability_type']}")

# Get crash report
report = engine.fuzzing_engine.get_crash_report()
print(f"Crash rate: {report['crash_rate']:.2%}")
```

#### Symbolic Execution Engine

Explores execution paths symbolically:

- **Path Exploration**: Recursively explores state transitions
- **Interesting Paths**: Identifies paths leading to extreme states
- **Coverage Analysis**: Maps reachable states

**Example:**
```python
# Explore execution paths
paths = engine.symbolic_engine.explore_paths(
    initial_state=state,
    max_depth=5
)

# Examine interesting paths
for path in engine.symbolic_engine.interesting_paths:
    print(f"Path: {path['path']}")
    print(f"Final state: {path['final_state']}")
```

### 5. MITRE ATT&CK Coverage

Complete mapping to MITRE ATT&CK framework:

- **Technique Mapping**: 15+ governance-specific techniques
- **Tactic Coverage**: Initial Access, Persistence, Defense Evasion, Impact, etc.
- **Coverage Tracking**: Records tested and successful techniques
- **Reporting**: Comprehensive coverage metrics

**Supported Techniques:**

| Technique ID | Name | Tactic | Target Dimensions |
|--------------|------|--------|-------------------|
| T1566 | Phishing | Initial Access | trust, epistemic_confidence |
| T1098 | Account Manipulation | Persistence | trust, legitimacy |
| T1036 | Masquerading | Defense Evasion | epistemic_confidence, reality_consensus |
| T1562 | Impair Defenses | Defense Evasion | governance_capacity, social_cohesion |
| T1499 | Denial of Service | Impact | governance_capacity, legitimacy |
| T1485 | Data Destruction | Impact | trust, legitimacy, epistemic_confidence |

**Example:**
```python
# Execute campaign with MITRE tracking
campaign_id = engine.start_campaign()

for _ in range(20):
    engine.execute_attack(state)

# Get coverage report
coverage = engine.get_mitre_coverage_report()
print(f"Coverage: {coverage['coverage_percentage']:.1f}%")
print(f"Tested: {coverage['tested_techniques']}/{coverage['total_techniques']}")
print(f"Success rate: {coverage['success_rate']:.1f}%")
```

## Complete Workflow Example

```python
from engines.red_team_enhanced import EnhancedRedTeamEngine

# Initialize engine with all features
engine = EnhancedRedTeamEngine(
    data_dir="data/red_team_enhanced",
    enable_rl=True,
    enable_fuzzing=True,
    enable_symbolic=True,
)

# Define initial state
state = {
    "trust": 0.6,
    "legitimacy": 0.7,
    "epistemic_confidence": 0.65,
    "moral_injury": 0.3,
    "social_cohesion": 0.7,
    "governance_capacity": 0.65,
    "reality_consensus": 0.7,
    "kindness": 0.75,
    "defense_level": 0.5,
}

# Start attack campaign
campaign_id = engine.start_campaign(strategy="adaptive_rl")
print(f"Campaign: {campaign_id}")

# Phase 1: Vulnerability Discovery
print("\n=== Phase 1: Vulnerability Discovery ===")
vulns = engine.discover_vulnerabilities(
    state,
    use_fuzzing=True,
    use_symbolic=True,
)
print(f"Discovered {len(vulns)} vulnerabilities")

# Phase 2: Exploit Chain Generation
print("\n=== Phase 2: Exploit Chain Generation ===")
chains = engine.chain_generator.generate_chains(max_chain_length=4)
print(f"Generated {len(chains)} exploit chains")

# Phase 3: Adaptive Attack Execution
print("\n=== Phase 3: Attack Execution ===")
for i in range(10):
    result = engine.execute_attack(
        state,
        use_exploit_chain=True,
        adapt_to_defenses=True,
    )
    
    print(f"\nAttack {i+1}:")
    print(f"  Success: {result['success']}")
    print(f"  Damage: {result['damage']:.3f}")
    print(f"  Technique: {result['technique_used']}")
    
    # Update state
    for dim, change in result['state_changes'].items():
        state[dim] = max(0.0, min(1.0, state[dim] + change))

# Phase 4: Campaign Analysis
print("\n=== Phase 4: Campaign Report ===")
report = engine.end_campaign()
print(f"Total Attacks: {report['total_attacks']}")
print(f"Success Rate: {report['success_rate']:.1%}")
print(f"Total Damage: {report['total_damage']:.2f}")

# Phase 5: Comprehensive Reporting
print("\n=== MITRE ATT&CK Coverage ===")
mitre = engine.get_mitre_coverage_report()
print(f"Coverage: {mitre['coverage_percentage']:.1f}%")
print(f"Successful Techniques: {mitre['successful_techniques']}")

print("\n=== Vulnerability Report ===")
vuln_report = engine.get_vulnerability_report()
print(f"Total: {vuln_report['total_vulnerabilities']}")
print(f"By Type: {vuln_report['by_type']}")
print(f"By Severity: {vuln_report['by_severity']}")

print("\n=== Exploit Chain Report ===")
chain_report = engine.get_exploit_chain_report()
print(f"Total Chains: {chain_report['total_chains']}")
print(f"Avg Length: {chain_report['average_chain_length']:.1f}")

print("\n=== RL Agent Statistics ===")
rl_stats = engine.get_rl_agent_stats()
print(f"Epsilon: {rl_stats['epsilon']:.3f}")
print(f"Experiences: {rl_stats['total_experiences']}")
print(f"Avg Reward: {rl_stats['average_reward']:.3f}")

# Save state
engine.save_state()
print("\nEngine state saved!")
```

## Advanced Features

### Custom Vulnerability Definition

```python
from engines.red_team_enhanced import Vulnerability

# Define custom vulnerability
custom_vuln = Vulnerability(
    vuln_id="custom_trust_exploit",
    type="social_engineering",
    severity=0.85,
    exploitability=0.75,
    target_dimension="trust",
    prerequisites=["epistemic_confidence"],
    impact={
        "trust": -0.3,
        "social_cohesion": -0.2,
    },
)

# Add to chain generator
engine.chain_generator.add_vulnerability(custom_vuln)
```

### Multi-Campaign Analysis

```python
# Run multiple campaigns with different strategies
strategies = ["aggressive", "stealth", "adaptive", "rl_adaptive"]

for strategy in strategies:
    engine.start_campaign(strategy=strategy)
    
    for _ in range(10):
        engine.execute_attack(state)
    
    report = engine.end_campaign()
    print(f"{strategy}: {report['success_rate']:.1%} success")

# Compare campaigns
all_campaigns = engine.campaigns
best = max(all_campaigns, key=lambda c: c.total_damage)
print(f"Best campaign: {best.campaign_id} ({best.strategy})")
```

### RL Agent Training

```python
# Extended training session
for episode in range(100):
    state = reset_state()  # Reset to initial state
    
    for step in range(20):
        result = engine.execute_attack(state, use_exploit_chain=False)
        
        # Update state
        for dim, change in result['state_changes'].items():
            state[dim] = max(0.0, min(1.0, state[dim] + change))
    
    # Check learning progress
    if episode % 10 == 0:
        stats = engine.get_rl_agent_stats()
        print(f"Episode {episode}: epsilon={stats['epsilon']:.3f}")

# Save trained agent
engine.rl_agent.save("trained_agent.json")
```

## Performance Metrics

### Attack Success Rates

- **RL Agent (trained)**: 70-85% success rate
- **Heuristic Strategy**: 60-75% success rate
- **Random Strategy**: 40-60% success rate

### Vulnerability Discovery

- **Fuzzing**: 10-50 vulnerabilities per 100 test cases
- **Symbolic Execution**: 5-20 interesting paths per state
- **Static Analysis**: 3-10 vulnerabilities per state

### Exploit Chains

- **Average Chain Length**: 2-3 vulnerabilities
- **Maximum Impact**: 2.5-4.0 cumulative severity
- **Success Probability**: 40-80% for well-chained exploits

## Configuration

### Engine Parameters

```python
EnhancedRedTeamEngine(
    data_dir="data/red_team",           # Data storage directory
    enable_rl=True,                      # Enable RL agent
    enable_fuzzing=True,                 # Enable fuzzing
    enable_symbolic=True,                # Enable symbolic execution
)
```

### RL Agent Parameters

```python
DQNAgent(
    state_dim=10,                        # State vector dimensions
    action_dim=10,                       # Number of actions
    learning_rate=0.001,                 # Learning rate
    gamma=0.95,                          # Discount factor
    epsilon=1.0,                         # Initial exploration rate
    epsilon_decay=0.995,                 # Exploration decay
    epsilon_min=0.01,                    # Minimum exploration
    memory_size=10000,                   # Experience replay buffer
)
```

## Integration with Existing Systems

### Django State Integration

```python
from engines.django_state.modules.red_team import RedTeamModule
from engines.red_team_enhanced import EnhancedRedTeamEngine

# Use both engines together
basic_engine = RedTeamModule(laws, black_vault_enabled=True)
enhanced_engine = EnhancedRedTeamEngine()

# Basic attack
basic_event = basic_engine.execute_attack(state_vector)

# Enhanced attack with AI
enhanced_result = enhanced_engine.execute_attack(state_dict)
```

### Kernel Integration

```python
from app.core.cognition_kernel import CognitionKernel

# Route through kernel
kernel = CognitionKernel()

# Wrap attack execution
async def kernel_execute_attack(state):
    result = await kernel.execute(
        func=lambda: engine.execute_attack(state),
        execution_type=ExecutionType.ATTACK,
    )
    return result
```

## Troubleshooting

### RL Agent Not Learning

```python
# Check epsilon decay
stats = engine.get_rl_agent_stats()
if stats['epsilon'] > 0.5:
    print("Agent still exploring, more training needed")

# Force exploitation
engine.rl_agent.epsilon = 0.01  # Minimal exploration
```

### Low Vulnerability Discovery

```python
# Increase fuzzing test cases
fuzz_inputs = engine.fuzzing_engine.generate_fuzz_inputs(count=500)

# Increase symbolic execution depth
paths = engine.symbolic_engine.explore_paths(state, max_depth=8)
```

### Chain Generation Issues

```python
# Check vulnerability prerequisites
for vuln in engine.discovered_vulnerabilities.values():
    print(f"{vuln.vuln_id}: prerequisites={vuln.prerequisites}")

# Manually verify chaining
vuln1 = engine.discovered_vulnerabilities['vuln_1']
vuln2 = engine.discovered_vulnerabilities['vuln_2']
can_chain = engine.chain_generator.can_chain(vuln1, vuln2)
print(f"Can chain: {can_chain}")
```

## Best Practices

1. **Start with Discovery**: Always run vulnerability discovery before attacks
2. **Use Exploit Chains**: Enable `use_exploit_chain=True` for maximum impact
3. **Enable Adaptation**: Use `adapt_to_defenses=True` for realistic scenarios
4. **Train RL Agent**: Run 50+ attacks before expecting optimal performance
5. **Save State**: Regularly save engine state for reproducibility
6. **Monitor Coverage**: Track MITRE ATT&CK coverage to ensure comprehensive testing

## Future Enhancements

- **Multi-Agent Coordination**: Multiple RL agents attacking simultaneously
- **Adversarial GANs**: Generative adversarial networks for attack generation
- **Transfer Learning**: Pre-trained models for common attack patterns
- **Real-time Defense**: Dynamic defense strategy generation
- **Graph Neural Networks**: Relationship-aware attack planning

## References

- MITRE ATT&CK Framework: https://attack.mitre.org/
- Deep Q-Learning: Mnih et al., "Playing Atari with Deep Reinforcement Learning"
- Symbolic Execution: King, "Symbolic Execution and Program Testing"
- Fuzzing: Miller et al., "An Empirical Study of the Reliability of UNIX Utilities"
