# Enhanced Network Defense Simulation - Quick Start Guide

## Quick Start

### Installation

No additional installation needed beyond base project requirements:

```bash
pip install -r requirements.txt
```

### 30-Second Demo

```python
from engines.network_defense_enhanced import NetworkDefenseEnhancedEngine

# Create and run
engine = NetworkDefenseEnhancedEngine()
engine.init()

for _ in range(10):
    engine.tick()

print(engine.report("summary"))
```

### Run Built-in Demo

```bash
python engines/network_defense_enhanced.py
```

### Run Examples

```bash
python engines/examples_network_defense_enhanced.py
```

### Run Tests

```bash
pytest engines/tests/test_network_defense_enhanced.py -v
```

## Core Features

### 1. DDoS Simulation (Layer 3/4/7)

```python
# Create DDoS-heavy scenario
engine = NetworkDefenseEnhancedEngine({"ddos_probability": 1.0})
engine.init()
engine.tick()

# Mitigate attacks
for attack in engine.state.ddos_attacks:
    if not attack.mitigation_triggered:
        engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
```

**Attack Types**:
- Layer 3: IP flooding, ICMP floods
- Layer 4: TCP SYN floods, UDP floods
- Layer 7: HTTP/HTTPS/DNS/SMTP floods

**Intensities**: LOW (1-10 Gbps), MEDIUM (10-100 Gbps), HIGH (100-500 Gbps), CRITICAL (500+ Gbps)

### 2. APT Modeling

```python
# Progress APT campaigns
for _ in range(50):
    engine.tick()

# Check APT status
for apt in engine.state.apt_scenarios:
    print(f"{apt.threat_actor}: {apt.current_stage.value}")
    print(f"  Credentials stolen: {apt.credentials_stolen}")
    print(f"  Hosts compromised: {len(apt.compromised_hosts)}")
```

**Threat Actors**: APT28, APT29, Lazarus Group, Fancy Bear, Cozy Bear

**13 Attack Stages**: Reconnaissance → Initial Access → Execution → ... → Exfiltration → Impact

### 3. Lateral Movement Detection

```python
# Detect lateral movements
engine = NetworkDefenseEnhancedEngine({"lateral_movement_probability": 1.0})
engine.init()
engine.tick()

# Isolate suspicious hosts
for event in engine.state.lateral_movements:
    if event.is_suspicious:
        engine.action("isolate_host", {"host": event.source_host})
```

**Monitored Protocols**: SMB, RDP, SSH, WMI, PSExec

**Detection Methods**: ML anomaly, behavioral analytics, rule-based

### 4. Network Segmentation Validation

```python
# View segments
for seg in engine.state.network_segments:
    print(f"{seg.name}: VLAN {seg.vlan_id}, {seg.isolation_level}")

# Enforce strict segmentation
engine.action("enforce_segmentation", {"segment_id": "seg_db"})
```

**Default Segments**: DMZ, Web Tier, App Tier, Database Tier, Management

**Validation**: Firewall rules, ACLs, VLAN hopping, routing leaks

### 5. Zero Trust Enforcement

```python
# View policies
for policy in engine.state.zero_trust_policies:
    print(f"{policy.policy_id}: {policy.trust_level.value}")

# Revoke access
engine.action("revoke_access", {"policy_id": "zt_db_access"})
```

**Controls**: MFA, device posture, location checks, time-based access, continuous validation

## Common Patterns

### Integrated Multi-Threat Scenario

```python
config = {
    "ddos_probability": 0.7,
    "apt_probability": 0.5,
    "lateral_movement_probability": 0.6,
}

engine = NetworkDefenseEnhancedEngine(config)
engine.init()

for _ in range(30):
    engine.tick()

# Coordinated defense
for attack in engine.state.ddos_attacks:
    if not attack.mitigation_triggered:
        engine.action("mitigate_ddos", {"attack_id": attack.attack_id})

for apt in engine.state.apt_scenarios:
    if not apt.detected:
        engine.action("block_c2", {"scenario_id": apt.scenario_id})
```

### Real-time Monitoring

```python
engine = NetworkDefenseEnhancedEngine()
engine.init()

while True:
    engine.tick()
    state = engine.observe()
    
    print(f"DDoS: {state['ddos_attacks_active']} active")
    print(f"APT: {state['apt_scenarios_active']} active")
    print(f"Bandwidth: {state['total_bandwidth_used_gbps']:.2f} Gbps")
    
    time.sleep(1)
```

## API Quick Reference

### Engine Methods

- `init()` - Initialize engine
- `tick()` - Advance simulation
- `observe()` - Get current state
- `action(type, params)` - Execute action
- `report(format)` - Generate report

### Action Types

- `mitigate_ddos` - Mitigate DDoS attack
- `isolate_host` - Isolate compromised host
- `block_c2` - Block C2 communications
- `enforce_segmentation` - Enforce segmentation
- `revoke_access` - Revoke zero-trust access

### Report Formats

- `json` - Complete state as JSON
- `summary` - High-level summary
- `detailed` - Detailed analysis

## Metrics

All metrics available via `observe()`:

```python
state = engine.observe()
# Returns:
# - simulation_tick
# - ddos_attacks_active / mitigated
# - apt_scenarios_active / detected
# - lateral_movements_detected / suspicious
# - network_segments / segmentation_violations
# - zero_trust_policies / violations
# - total_bandwidth_used_gbps
# - blocked_attacks
```

## Configuration

```python
config = {
    "ddos_probability": 0.3,      # Per-tick DDoS probability (0.0-1.0)
    "apt_probability": 0.1,       # Per-tick APT probability (0.0-1.0)
    "lateral_movement_probability": 0.2,  # Per-tick lateral movement (0.0-1.0)
}

engine = NetworkDefenseEnhancedEngine(config)
```

## Performance

- Memory: ~10-20 MB per 1000 events
- CPU: Single-threaded, minimal
- Scalability: Tested to 10,000 ticks

## Files

- `engines/network_defense_enhanced.py` - Main engine
- `engines/tests/test_network_defense_enhanced.py` - Test suite (32 tests)
- `engines/examples_network_defense_enhanced.py` - 8 comprehensive examples
- `engines/NETWORK_DEFENSE_ENHANCED_README.md` - Full documentation

## Support

See full documentation in `NETWORK_DEFENSE_ENHANCED_README.md`

Run examples: `python engines/examples_network_defense_enhanced.py`

Run tests: `pytest engines/tests/test_network_defense_enhanced.py -v`
