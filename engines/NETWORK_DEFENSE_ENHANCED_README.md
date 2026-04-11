# Enhanced Network Defense Simulation Engine

## Overview

The Enhanced Network Defense Simulation Engine is a comprehensive cybersecurity simulation framework that models advanced network attacks and defense mechanisms. It provides realistic scenarios for testing network security controls, detection capabilities, and response procedures.

## Features

### 1. DDoS Simulation (Layer 3/4/7)

Simulates Distributed Denial of Service attacks across multiple OSI layers:

- **Layer 3 (Network)**: IP flooding, ICMP floods
- **Layer 4 (Transport)**: TCP SYN floods, UDP floods, TCP ACK floods
- **Layer 7 (Application)**: HTTP floods, HTTPS floods, DNS amplification, SMTP floods

**Intensity Levels**:
- **LOW**: 1-10 Gbps
- **MEDIUM**: 10-100 Gbps
- **HIGH**: 100-500 Gbps (auto-mitigation triggered)
- **CRITICAL**: 500+ Gbps (auto-mitigation triggered)

**Features**:
- Realistic botnet simulation (100-10,000 bots)
- Amplification attacks (DNS, NTP)
- Automatic mitigation for high-intensity attacks
- Bandwidth and packet-per-second calculations
- Multiple source IP simulation

### 2. APT (Advanced Persistent Threat) Modeling

Simulates sophisticated multi-stage attacks based on real-world threat actors:

**Threat Actors**: APT28, APT29, Lazarus Group, Fancy Bear, Cozy Bear

**Attack Stages** (MITRE ATT&CK aligned):
1. **Reconnaissance**: Target identification and intelligence gathering
2. **Initial Access**: Initial compromise
3. **Execution**: Malicious code execution
4. **Persistence**: Maintain foothold (registry keys, scheduled tasks, services)
5. **Privilege Escalation**: Gain higher privileges
6. **Defense Evasion**: Avoid detection
7. **Credential Access**: Steal credentials
8. **Discovery**: Network and system enumeration
9. **Lateral Movement**: Spread to other systems
10. **Collection**: Gather target data
11. **Command & Control**: C2 communications
12. **Exfiltration**: Data theft
13. **Impact**: Final objectives

**Metrics Tracked**:
- Credentials stolen
- Hosts compromised
- Data exfiltrated (MB)
- Dwell time (days)
- Detection probability
- Persistence mechanisms

### 3. Lateral Movement Detection

Monitors east-west traffic for unauthorized lateral movement:

**Detection Methods**:
- Machine learning anomaly detection
- Behavioral analytics
- Rule-based detection

**Protocols Monitored**:
- SMB (port 445)
- RDP (port 3389)
- SSH (port 22)
- WMI (port 135)
- PSExec (port 5985)

**Indicators**:
- Unauthorized zone crossing
- High anomaly scores
- Unusual protocols
- Abnormal data volumes

**Anomaly Scoring**: 0.0 to 1.0 (>0.7 flagged as suspicious)

### 4. Network Segmentation Validation

Tests VLAN and subnet isolation effectiveness:

**Default Segments**:
- **DMZ** (VLAN 10, 10.0.10.0/24): Controlled isolation
- **Web Tier** (VLAN 20, 10.0.20.0/24): Controlled isolation
- **Application Tier** (VLAN 30, 10.0.30.0/24): Strict isolation
- **Database Tier** (VLAN 40, 10.0.40.0/24): Strict isolation
- **Management** (VLAN 50, 10.0.50.0/24): Strict isolation

**Validation Checks**:
- Firewall rule compliance
- ACL enforcement
- VLAN hopping attempts
- Routing leaks
- Cross-segment access violations

**Features**:
- Micro-segmentation support
- Configurable isolation levels (strict, controlled, permissive)
- Allowed inbound/outbound rules per segment

### 5. Zero Trust Architecture Enforcement

Validates zero-trust principles:

**Zero Trust Policies**:
- **Identity Verification**: User and device identity validation
- **Least Privilege**: Minimal access rights
- **Continuous Validation**: Ongoing authentication
- **Assume Breach**: Never trust, always verify

**Policy Components**:
- **MFA Required**: Multi-factor authentication
- **Device Posture Check**: Security health validation
- **Location Check**: Geo-location verification
- **Time-based Access**: Temporal access controls
- **Context-aware**: Situational awareness
- **Continuous Validation**: Real-time verification

**Trust Levels**:
- **UNTRUSTED**: No access
- **CONDITIONAL**: Limited access
- **TRUSTED**: Standard access
- **VERIFIED**: Full access

## Installation

```bash
# No additional dependencies beyond base requirements
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from engines.network_defense_enhanced import NetworkDefenseEnhancedEngine

# Create engine
engine = NetworkDefenseEnhancedEngine()

# Initialize
if engine.init():
    print("✅ Engine initialized")
    
    # Run simulation
    for i in range(10):
        engine.tick()
        state = engine.observe()
        print(f"Tick {i+1}: {state}")
    
    # Generate report
    print(engine.report("summary"))
```

### Custom Configuration

```python
config = {
    "ddos_probability": 0.5,      # 50% chance per tick
    "apt_probability": 0.2,       # 20% chance per tick
    "lateral_movement_probability": 0.3  # 30% chance per tick
}

engine = NetworkDefenseEnhancedEngine(config)
engine.init()
```

### Defensive Actions

```python
# Mitigate DDoS attack
engine.action("mitigate_ddos", {"attack_id": "ddos_001"})

# Isolate compromised host
engine.action("isolate_host", {"host": "10.0.30.105"})

# Block C2 communications
engine.action("block_c2", {"scenario_id": "apt_lazarus_001"})

# Enforce strict segmentation
engine.action("enforce_segmentation", {"segment_id": "seg_db"})

# Revoke access
engine.action("revoke_access", {"policy_id": "zt_db_access"})
```

### Report Formats

```python
# JSON format
json_report = engine.report("json")

# Summary report
summary = engine.report("summary")

# Detailed report
detailed = engine.report("detailed")
```

## API Reference

### Engine Methods

#### `init() -> bool`
Initialize the simulation engine. Must be called before `tick()`.

**Returns**: `True` if successful, `False` otherwise

#### `tick() -> bool`
Advance simulation by one time step.

**Returns**: `True` if successful, `False` otherwise

#### `observe() -> dict`
Get current simulation state.

**Returns**: Dictionary with current metrics:
- `simulation_tick`: Current tick number
- `ddos_attacks_active`: Active DDoS attacks
- `ddos_attacks_mitigated`: Mitigated DDoS attacks
- `apt_scenarios_active`: Active APT scenarios
- `apt_scenarios_detected`: Detected APT scenarios
- `lateral_movements_detected`: Total lateral movement events
- `suspicious_lateral_movements`: Flagged suspicious events
- `network_segments`: Number of network segments
- `segmentation_violations`: Segmentation violations
- `zero_trust_policies`: Number of policies
- `zero_trust_violations`: Policy violations
- `total_bandwidth_used_gbps`: Current bandwidth usage
- `blocked_attacks`: Total blocked attacks

#### `action(action_type: str, params: dict) -> bool`
Execute a defensive action.

**Action Types**:
- `mitigate_ddos`: Mitigate DDoS attack
- `isolate_host`: Isolate compromised host
- `block_c2`: Block C2 communications
- `enforce_segmentation`: Enforce network segmentation
- `revoke_access`: Revoke zero-trust access

**Returns**: `True` if successful, `False` otherwise

#### `report(format_type: str = "json") -> str`
Generate simulation report.

**Formats**:
- `json`: Complete state as JSON
- `summary`: High-level summary
- `detailed`: Detailed analysis

**Returns**: Formatted report string

## Data Models

### DDoSAttack
```python
@dataclass
class DDoSAttack:
    attack_id: str
    layer: AttackLayer  # LAYER_3, LAYER_4, LAYER_7
    intensity: DDoSIntensity  # LOW, MEDIUM, HIGH, CRITICAL
    bandwidth_gbps: float
    packets_per_second: int
    protocol: str
    source_ips: list[str]
    target_ip: str
    target_port: int
    duration_seconds: int
    amplification_factor: float
    botnet_size: int
    mitigation_triggered: bool
    mitigation_effectiveness: float
```

### APTScenario
```python
@dataclass
class APTScenario:
    scenario_id: str
    threat_actor: str
    current_stage: APTStage
    stages_completed: list[APTStage]
    target_assets: list[str]
    compromised_hosts: list[str]
    credentials_stolen: int
    data_exfiltrated_mb: float
    dwell_time_days: int
    detection_probability: float
    detected: bool
    c2_servers: list[str]
    persistence_mechanisms: list[str]
```

### LateralMovementEvent
```python
@dataclass
class LateralMovementEvent:
    event_id: str
    source_host: str
    destination_host: str
    source_zone: str
    destination_zone: str
    protocol: str
    port: int
    traffic_direction: TrafficDirection  # NORTH_SOUTH, EAST_WEST
    anomaly_score: float
    is_suspicious: bool
    indicators: list[str]
    detection_method: str
```

### NetworkSegment
```python
@dataclass
class NetworkSegment:
    segment_id: str
    name: str
    vlan_id: int
    subnet: str
    isolation_level: str  # "strict", "controlled", "permissive"
    allowed_outbound: list[str]
    allowed_inbound: list[str]
    firewall_rules: int
    acl_rules: int
    micro_segmentation: bool
```

### ZeroTrustPolicy
```python
@dataclass
class ZeroTrustPolicy:
    policy_id: str
    resource: str
    user_identity: str
    device_identity: str
    trust_level: TrustLevel  # UNTRUSTED, CONDITIONAL, TRUSTED, VERIFIED
    mfa_required: bool
    device_posture_check: bool
    location_check: bool
    time_based_access: bool
    context_aware: bool
    continuous_validation: bool
    violations: int
```

## Demo

Run the built-in demo:

```bash
python engines/network_defense_enhanced.py
```

This will:
1. Initialize the engine
2. Run 10 simulation ticks
3. Display real-time metrics
4. Demonstrate defensive actions
5. Generate final report

## Testing

Run the test suite:

```bash
# Run all tests
pytest engines/tests/test_network_defense_enhanced.py -v

# Run specific test class
pytest engines/tests/test_network_defense_enhanced.py::TestDDoSSimulation -v

# Run with coverage
pytest engines/tests/test_network_defense_enhanced.py --cov=engines.network_defense_enhanced
```

## Example Scenarios

### Scenario 1: Multi-Layer DDoS Attack

```python
engine = NetworkDefenseEnhancedEngine({"ddos_probability": 1.0})
engine.init()

# Simulate attacks
for _ in range(5):
    engine._simulate_ddos_attack()

# Observe attacks
state = engine.observe()
print(f"Active attacks: {state['ddos_attacks_active']}")
print(f"Total bandwidth: {state['total_bandwidth_used_gbps']} Gbps")

# Mitigate
for attack in engine.state.ddos_attacks:
    if not attack.mitigation_triggered:
        engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
```

### Scenario 2: APT Campaign

```python
engine = NetworkDefenseEnhancedEngine()
engine.init()

# Progress APT
for _ in range(50):
    engine.tick()

# Check APT status
for apt in engine.state.apt_scenarios:
    print(f"APT: {apt.threat_actor}")
    print(f"  Stage: {apt.current_stage.value}")
    print(f"  Credentials stolen: {apt.credentials_stolen}")
    print(f"  Hosts compromised: {len(apt.compromised_hosts)}")
    print(f"  Detected: {apt.detected}")
```

### Scenario 3: Lateral Movement Detection

```python
engine = NetworkDefenseEnhancedEngine({"lateral_movement_probability": 1.0})
engine.init()

# Detect lateral movements
for _ in range(10):
    engine.tick()

# Analyze suspicious movements
suspicious = [
    lm for lm in engine.state.lateral_movements 
    if lm.is_suspicious
]

for event in suspicious:
    print(f"Suspicious movement detected:")
    print(f"  {event.source_zone} → {event.destination_zone}")
    print(f"  Anomaly score: {event.anomaly_score:.2f}")
    print(f"  Indicators: {', '.join(event.indicators)}")
    
    # Isolate source host
    engine.action("isolate_host", {"host": event.source_host})
```

## Performance

- **Memory**: ~10-20 MB per 1000 simulated events
- **CPU**: Minimal (single-threaded)
- **Scalability**: Tested up to 10,000 ticks without degradation

## Security Considerations

This is a **simulation framework** for training and testing purposes. It:

- Does NOT perform actual attacks
- Does NOT connect to real networks
- Simulates attack patterns for defensive training
- Should only be used in authorized environments

## Contributing

When extending the engine:

1. Follow the existing data model patterns
2. Add comprehensive tests
3. Update documentation
4. Ensure all metrics are tracked
5. Maintain the 5-method engine interface

## License

See project LICENSE file.

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [NIST Zero Trust Architecture](https://www.nist.gov/publications/zero-trust-architecture)
- [DDoS Attack Taxonomy](https://www.cloudflare.com/learning/ddos/)
- [Network Segmentation Best Practices](https://www.nist.gov/publications/)

## Authors

Sovereign Governance Substrate Team

## Version

1.0.0 - Initial Release
