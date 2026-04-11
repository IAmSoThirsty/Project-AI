# Enhanced Temporal Attack Simulation Engine

## Overview

The Enhanced Temporal Attack Simulation Engine is a comprehensive security testing framework designed to identify, simulate, and detect temporal vulnerabilities in distributed systems. It integrates with Chronos (temporal weight engine) and Atropos (anti-rollback protection) to provide multi-layered temporal security analysis.

## Features

### 1. Time-Based Attack Vectors

#### Race Condition Attacks (5 scenarios)
- **Check-Then-Use Race**: Exploit race between permission check and resource use
- **Double-Spend Race**: Spend same resource twice via concurrent transactions
- **Concurrent Login Race**: Bypass rate limiting via concurrent login attempts
- **Symlink File System Race**: Replace file with symlink between check and use
- **Database Update Race**: Concurrent updates leading to lost writes

#### TOCTOU Attacks (5 scenarios)
- **Permission Check TOCTOU**: Change file permissions between check and use
- **File Content TOCTOU**: Modify file content between validation and execution
- **Resource Quota TOCTOU**: Exceed quota by changing it between check and allocation
- **Authentication State TOCTOU**: Revoke auth between check and privileged operation
- **Cryptographic Key TOCTOU**: Replace crypto key between validation and use

#### Time Manipulation Attacks (3 scenarios)
- **System Clock Rollback**: Roll back system clock to bypass time-based restrictions
- **NTP Time Injection**: Spoof NTP responses to manipulate synchronized time
- **Malicious Timestamp Injection**: Inject forged timestamps in messages/transactions

### 2. Replay Attack Scenarios (6 scenarios)

- **Session Cookie Replay**: Replay captured session cookie to hijack session
- **JWT Token Replay**: Replay stolen JWT token before expiration
- **Signed Message Replay**: Replay legitimately signed message multiple times
- **API Request Replay**: Replay API request to duplicate side effects
- **Challenge-Response Replay**: Replay captured challenge-response to authenticate
- **Cross-Chain Replay**: Replay transaction on different blockchain fork

### 3. Temporal Anomaly Detection

The `TemporalAnomalyDetector` monitors for:

- **Clock Drift**: Detects clock skew between distributed agents
- **Future Timestamps**: Identifies events with timestamps in the future
- **Past Timestamps**: Detects suspiciously old timestamps (potential replay)
- **Sequence Violations**: Identifies out-of-order sequence numbers
- **Duplicate Events**: Detects event replay via content hashing
- **Causal Inconsistencies**: Identifies violations of happens-before relationships

#### Configuration

```python
detector = TemporalAnomalyDetector(
    max_clock_drift_ms=5000,        # Maximum allowed clock drift
    max_future_timestamp_ms=1000,   # Max future timestamp tolerance
    event_window_size=1000           # Size of event history buffer
)
```

#### Usage

```python
# Check single event
anomalies = detector.check_event(event_dict)

# Detect clock drift across agents
drift_anomalies = detector.detect_clock_drift(agent_timestamps)

# Get all detected anomalies
all_anomalies = detector.get_all_anomalies()
```

### 4. Causality Violation Tests

The `CausalityValidator` verifies happens-before relationships using vector clocks:

```python
validator = CausalityValidator()

# Add events with vector clocks
validator.add_event("e1", {"agent1": 1, "agent2": 0})
validator.add_event("e2", {"agent1": 2, "agent2": 1}, depends_on=["e1"])

# Verify happens-before relationship
is_valid, reason = validator.verify_happens_before("e1", "e2")

# Detect violations
violations = validator.detect_violations()

# Check for cycles (temporal paradoxes)
cycle = validator.check_cycle()
```

### 5. Integration with Temporal Agents

#### Chronos Integration

Chronos provides vector clock-based causality tracking:

```python
from src.cognition.temporal.chronos import Chronos

# Initialize and integrate
chronos = Chronos()
engine = TemporalAttackEngine()
engine.integrate_chronos(chronos)

# Chronos detects causality violations
result = engine.simulate_attack("TEMP_CAUSE_001")
```

#### Atropos Integration

Atropos provides anti-rollback protection via hash chaining and monotonic counters:

```python
from src.cognition.temporal.atropos import Atropos

# Initialize and integrate
atropos = Atropos()
engine = TemporalAttackEngine()
engine.integrate_atropos(atropos)

# Atropos detects replay attacks
result = engine.simulate_attack("TEMP_REPLAY_001")
```

## Attack Taxonomy

### Attack Categories

```python
class AttackCategory(Enum):
    RACE_CONDITION = "race_condition"
    TOCTOU = "toctou"
    TIME_MANIPULATION = "time_manipulation"
    SESSION_REPLAY = "session_replay"
    TOKEN_REPLAY = "token_replay"
    MESSAGE_REPLAY = "message_replay"
    CLOCK_SKEW = "clock_skew"
    TIMESTAMP_MANIPULATION = "timestamp_manipulation"
    CAUSALITY_VIOLATION = "causality_violation"
    TIMING_ATTACK = "timing_attack"
    TEMPORAL_SIDE_CHANNEL = "temporal_side_channel"
```

### Severity Levels

```python
class AttackSeverity(Enum):
    CRITICAL = "critical"  # CVSS >= 9.0
    HIGH = "high"          # CVSS >= 7.0
    MEDIUM = "medium"      # CVSS >= 4.0
    LOW = "low"            # CVSS >= 1.0
    INFO = "info"          # CVSS < 1.0
```

## Usage Examples

### Basic Usage

```python
from engines.temporal_attack_enhanced import TemporalAttackEngine

# Initialize engine
engine = TemporalAttackEngine()

# Generate all attack vectors
attacks = engine.generate_all_attack_vectors()
print(f"Generated {len(attacks)} attack scenarios")

# Simulate specific attack
result = engine.simulate_attack("TEMP_RACE_002")
print(f"Attack success: {result['success']}")
print(f"Detection: {result['detection_results']}")

# Generate comprehensive report
report = engine.generate_report()
print(f"Total attacks: {report['attack_vectors']['total']}")
print(f"Total anomalies: {report['anomalies']['total']}")
```

### Anomaly Detection

```python
from engines.temporal_attack_enhanced import TemporalAnomalyDetector
from datetime import datetime, timezone

detector = TemporalAnomalyDetector()

# Check event for anomalies
event = {
    "event_id": "evt_001",
    "event_type": "transaction",
    "timestamp": datetime.now(timezone.utc),
    "source_id": "agent1",
    "sequence": 1,
    "payload": {"amount": 100}
}

anomalies = detector.check_event(event)

for anomaly in anomalies:
    print(f"Anomaly: {anomaly.anomaly_type.value}")
    print(f"Severity: {anomaly.severity.value}")
    print(f"Confidence: {anomaly.confidence:.0%}")
    print(f"Action: {anomaly.recommended_action}")
```

### Causality Validation

```python
from engines.temporal_attack_enhanced import CausalityValidator

validator = CausalityValidator()

# Build causal chain
validator.add_event("create_account", {"agent1": 1})
validator.add_event("deposit", {"agent1": 2}, depends_on=["create_account"])
validator.add_event("withdraw", {"agent1": 3}, depends_on=["deposit"])

# Verify ordering
is_valid, reason = validator.verify_happens_before("create_account", "withdraw")

# Detect violations
violations = validator.detect_violations()
for v in violations:
    print(f"Violation: {v.description}")
    print(f"Expected: {v.expected_order}")
    print(f"Actual: {v.actual_order}")
```

### Export Results

```python
# Export attack vectors
attack_file = engine.export_attack_vectors()
# Exports to: data/temporal_attacks/temporal_attacks_TIMESTAMP.json

# Export anomalies
anomaly_file = engine.export_anomalies()
# Exports to: data/temporal_attacks/temporal_anomalies_TIMESTAMP.json
```

## Attack Scenario Details

### Example: Double-Spend Race Condition

```python
{
    "attack_id": "TEMP_RACE_002",
    "category": "race_condition",
    "severity": "critical",
    "name": "Double-Spend Race Condition",
    "cvss_score": 9.1,
    "description": "Spend same resource twice via concurrent transactions",
    "attack_payload": {
        "attack_type": "double_spend",
        "resource": "tokens/credits",
        "concurrent_transactions": 2,
        "timing_offset_ms": 10,
        "exploit_method": "Parallel transaction submission before balance update"
    },
    "prerequisites": [
        "Non-atomic balance updates",
        "Concurrent transaction processing"
    ],
    "mitigation_strategies": [
        "Implement optimistic locking with version numbers",
        "Use database transaction isolation (SERIALIZABLE)",
        "Apply distributed consensus (Paxos/Raft)",
        "Chronos causality tracking"
    ],
    "temporal_window_ms": 20
}
```

### Example: Session Replay Attack

```python
{
    "attack_id": "TEMP_REPLAY_001",
    "category": "session_replay",
    "severity": "critical",
    "name": "Session Cookie Replay",
    "cvss_score": 8.8,
    "description": "Replay captured session cookie to hijack session",
    "attack_payload": {
        "attack_type": "session_replay",
        "captured_cookie": "session_id=abc123...",
        "replay_window": "Until expiration",
        "method": "Capture via network sniffing or XSS"
    },
    "mitigation_strategies": [
        "Bind sessions to IP address",
        "Implement device fingerprinting",
        "Use short-lived sessions",
        "Atropos replay detection with nonces"
    ],
    "temporal_window_ms": 3600000
}
```

## Data Models

### TemporalAttackVector

```python
@dataclass
class TemporalAttackVector:
    attack_id: str
    category: AttackCategory
    severity: AttackSeverity
    name: str
    description: str
    attack_payload: Dict[str, Any]
    prerequisites: List[str]
    expected_detection: List[str]
    cvss_score: float
    mitigation_strategies: List[str]
    exploitation_complexity: str
    target_components: List[str]
    temporal_window_ms: int
    success_indicators: List[str]
```

### TemporalAnomaly

```python
@dataclass
class TemporalAnomaly:
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AttackSeverity
    description: str
    detected_at: datetime
    event_ids: List[str]
    evidence: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    recommended_action: str
```

### CausalityViolation

```python
@dataclass
class CausalityViolation:
    violation_id: str
    violation_type: str
    description: str
    event_a_id: str
    event_b_id: str
    expected_order: str
    actual_order: str
    evidence: Dict[str, Any]
    severity: AttackSeverity
    detected_at: datetime
```

## Testing

Run the comprehensive test suite:

```bash
python engines/tests/test_temporal_attack_enhanced.py
```

### Test Coverage

- ✓ Attack vector generation (20+ scenarios)
- ✓ Anomaly detection (future timestamps, duplicates, sequence violations, clock drift)
- ✓ Causality validation (happens-before, violations, cycles)
- ✓ Attack simulation
- ✓ Chronos integration
- ✓ Atropos integration
- ✓ Export functionality

## Demonstration

Run the interactive demonstration:

```bash
python examples/temporal_attack_demo.py
```

The demo showcases:
1. Attack vector generation and categorization
2. Temporal anomaly detection scenarios
3. Causality validation and violation detection
4. Chronos integration for causality tracking
5. Atropos integration for replay detection
6. Comprehensive reporting

## Security Considerations

### Detection Strategies

1. **Race Conditions**: Use atomic operations, proper locking, transaction isolation
2. **TOCTOU**: Operate on file descriptors, use capabilities, validate at use time
3. **Time Manipulation**: Use monotonic clocks, NTP authentication, hardware time sources
4. **Replay Attacks**: Implement nonces, sequence numbers, short-lived tokens
5. **Clock Skew**: NTP synchronization, vector clocks, consensus time
6. **Causality Violations**: Vector clocks, dependency validation, DAG enforcement

### Integration Benefits

- **Chronos**: Provides distributed causality tracking via vector clocks
- **Atropos**: Offers anti-rollback via monotonic counters and hash chaining
- **Combined**: Multi-layered temporal security with causality + immutability

## Performance Considerations

- Anomaly detector maintains sliding window (default 1000 events)
- Event hash set grows with unique events (consider periodic cleanup)
- Causality graph uses adjacency lists for O(V+E) operations
- Vector clock comparisons are O(n) where n = number of agents

## Future Enhancements

- [ ] Machine learning-based anomaly detection
- [ ] Adaptive threshold tuning
- [ ] Real-time attack correlation
- [ ] Distributed consensus integration
- [ ] Hardware security module (HSM) support for Atropos
- [ ] Quantum-resistant temporal signatures

## References

- Lamport, L. (1978). "Time, clocks, and the ordering of events in a distributed system"
- Mattern, F. (1988). "Virtual Time and Global States of Distributed Systems"
- EIP-155: "Simple replay attack protection"
- MITRE ATT&CK: Temporal attack techniques

## License

See LICENSE file in repository root.

## Authors

Enhanced Temporal Attack Simulation Engine
Sovereign Governance Substrate Project
