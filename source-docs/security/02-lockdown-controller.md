# Lockdown Controller - Progressive System Lockdown

## Overview

The Lockdown Controller manages progressive system lockdown in response to security breaches. It implements 25 lockable system sections with deterministic stage mapping, enabling granular containment of security incidents without shutting down the entire system.

**Location:** [[src/app/core/cerberus_lockdown_controller.py]] (`src/app/core/cerberus_lockdown_controller.py`) (384 lines)

**Core Philosophy:** Progressive containment through staged section lockdown, balancing security response with operational continuity.

---

## Architecture

### Key Concepts

1. **25 Lockable Sections:** Each representing a critical system component
2. **Staged Lockdown:** Progressive escalation from stage 0 (no lockdown) to stage 25 (full lockdown)
3. **Deterministic Formula:** Lockdown stage computed from risk score and bypass depth
4. **Idempotent Operations:** Applying same lockdown twice has no adverse effects
5. **Persistent State:** Lockdown state survives system restarts

### Lockdown Stages

```python
# Stage 0: No lockdown (normal operation)
# Stage 1-5: Low severity (authentication, authorization, data access)
# Stage 6-10: Moderate severity (network, API, admin functions)
# Stage 11-15: Elevated severity (encryption keys, model weights, inference)
# Stage 16-20: High severity (process execution, system calls, database)
# Stage 21-25: Critical severity (monitoring, logging, credentials, tokens)
```

---

## 25 Lockable System Sections

```python
LOCKABLE_SECTIONS = [
    # Authentication & Authorization (Stages 1-2)
    "authentication",        # User login, session management
    "authorization",         # Permission checks, RBAC

    # Data Access (Stages 3-5)
    "data_access",          # Database queries, data retrieval
    "file_operations",      # File I/O, uploads, downloads
    "network_egress",       # Outbound network connections

    # API & Admin (Stages 6-8)
    "api_endpoints",        # REST/GraphQL APIs
    "admin_functions",      # Admin panel, privileged operations
    "user_sessions",        # Session tokens, active sessions

    # Security Infrastructure (Stages 9-11)
    "encryption_keys",      # Cryptographic key access
    "audit_logs",           # Log writing and access
    "configuration",        # System configuration changes

    # AI/ML Components (Stages 12-14)
    "model_weights",        # Neural network model access
    "training_data",        # Training dataset access
    "inference_engine",     # Model inference/prediction

    # System Operations (Stages 15-17)
    "memory_management",    # Memory allocation, garbage collection
    "process_execution",    # Process spawning, command execution
    "system_calls",         # Direct OS system calls

    # Data Layer (Stages 18-20)
    "database_access",      # Direct database connections
    "cache_operations",     # Redis/Memcached operations
    "backup_systems",       # Backup creation/restoration

    # Observability (Stages 21-23)
    "monitoring_systems",   # Metrics collection
    "alert_systems",        # Alert generation and dispatch
    "logging_systems",      # Log aggregation and storage

    # Credential Management (Stages 24-25)
    "credential_storage",   # Password/secret storage
    "token_management",     # JWT, OAuth tokens (FULL LOCKDOWN)
]
```

---

## API Reference

### Initialization

```python
from app.core.cerberus_lockdown_controller import LockdownController

lockdown = LockdownController(
    data_dir="data",              # Base data directory
    observation_only=False        # If True, logs but doesn't actually lock
)
```

**Observation Mode:**
```python
# Use for testing/monitoring without impacting production
lockdown = LockdownController(observation_only=True)

# Will log intended lockdowns without applying them
result = lockdown.apply_lockdown(stage=5, reason="test")
# result['action'] == 'observed_only'
# result['would_lock'] == ['authentication', 'authorization', ...]
```

### Compute Lockdown Stage

```python
stage = lockdown.compute_lockdown_stage(
    risk_score=0.85,     # 0.0-1.0 (threat severity)
    bypass_depth=2       # Number of security layers bypassed
)

# Formula: stage = min(25, ceil(risk_score * 10) + bypass_depth)

# Examples:
# risk_score=0.3, depth=0 → stage 3  (low risk, no bypass)
# risk_score=0.5, depth=1 → stage 6  (medium risk, 1 layer)
# risk_score=0.9, depth=3 → stage 12 (high risk, deep bypass)
# risk_score=1.0, depth=10 → stage 25 (capped at max)
```

**Risk Score Guidelines:**
- **0.0-0.3:** Low severity (probing, reconnaissance)
- **0.4-0.6:** Moderate severity (active exploitation attempts)
- **0.7-0.8:** High severity (successful breach, lateral movement)
- **0.9-1.0:** Critical severity (root access, data exfiltration)

### Apply Lockdown

```python
result = lockdown.apply_lockdown(
    stage=10,                          # Target lockdown stage (0-25)
    reason="privilege_escalation"      # Reason for audit log
)

print(f"""
Lockdown Applied:
- Previous stage: {result['previous_stage']}
- New stage: {result['new_stage']}
- Newly locked: {result['newly_locked']}
- Total locked: {result['total_locked']}
- Action: {result['action']}  # 'locked', 'no_change', or 'observed_only'
""")
```

**Idempotent Behavior:**
```python
# First call: Locks sections 0-9
result1 = lockdown.apply_lockdown(stage=10, reason="breach_detected")
# result1['newly_locked'] = 10 sections

# Second call: No change (already at stage 10)
result2 = lockdown.apply_lockdown(stage=10, reason="reconfirm")
# result2['newly_locked'] = []
# result2['action'] = 'no_change'

# Escalation call: Locks additional sections 10-14
result3 = lockdown.apply_lockdown(stage=15, reason="breach_escalation")
# result3['newly_locked'] = 5 sections (10-14)
```

### Check Section Status

```python
# Check if specific section is locked
is_locked = lockdown.is_section_locked("api_endpoints")

# Get all locked sections
locked = lockdown.get_lockdown_status()['locked_sections']

# Get available (unlocked) sections
available = lockdown.get_available_sections()
```

### Query Lockdown Status

```python
status = lockdown.get_lockdown_status()

print(f"""
Lockdown Status:
- Current stage: {status['current_stage']} / 25
- Severity: {status['severity']}  # low, moderate, elevated, high, critical
- Locked sections: {status['locked_count']} / {status['total_sections']}
- Remaining sections: {status['remaining_count']}
- Lockdown percentage: {status['lockdown_percentage']:.1f}%
- Recent events: {len(status['recent_events'])}
""")

# Severity thresholds:
# - low: 0-4
# - moderate: 5-9
# - elevated: 10-14
# - high: 15-19
# - critical: 20-25
```

### Release Lockdown

```python
# Release to specific stage
result = lockdown.release_lockdown(stage=5)

# Release all lockdowns
result = lockdown.release_lockdown(stage=None)

print(f"""
Lockdown Released:
- Previous stage: {result['previous_stage']}
- New stage: {result['new_stage']}
- Released sections: {result['released_sections']}
- Total locked: {result['total_locked']}
""")
```

**Use Cases:**
- **Controlled De-escalation:** After incident resolved, gradually release locks
- **False Positive Recovery:** Quick recovery from over-zealous lockdown
- **Maintenance Windows:** Temporarily release locks for system updates

### Get Lockdown History

```python
# Get last 50 lockdown events
history = lockdown.get_lockdown_history(limit=50)

for event in history:
    print(f"""
    {event['timestamp']}:
      {event['previous_stage']} → {event['new_stage']}
      Reason: {event['reason']}
      Newly locked: {len(event.get('newly_locked', []))} sections
      Total locked: {event['total_locked']}
    """)
```

---

## Integration Patterns

### Cerberus Hydra Integration

```python
from app.core.cerberus_hydra import CerberusHydraDefense

hydra = CerberusHydraDefense(data_dir="data")

# Hydra uses lockdown controller internally
# On bypass detected:
lockdown_stage = hydra.lockdown_controller.compute_lockdown_stage(
    risk_score=0.85,
    bypass_depth=2
)

result = hydra.lockdown_controller.apply_lockdown(
    stage=lockdown_stage,
    reason=f"hydra_bypass_{bypass_event.event_id}"
)

# Each spawned agent gets assigned a locked section
for i, agent_id in enumerate(spawned_agents):
    section_index = (hydra.lockdown_controller.current_stage + i) % 25
    agent.locked_section = LOCKABLE_SECTIONS[section_index]
```

### Application Code Integration

```python
from app.core.cerberus_lockdown_controller import LockdownController

lockdown = LockdownController(data_dir="data")

# In authentication module
def authenticate_user(username, password):
    if lockdown.is_section_locked("authentication"):
        logger.warning("Authentication locked due to security incident")
        raise SecurityLockdownError("Authentication temporarily unavailable")
    
    # Normal authentication logic
    return verify_credentials(username, password)

# In API endpoint
@app.route('/api/data')
def get_data():
    if lockdown.is_section_locked("api_endpoints"):
        return jsonify({"error": "API locked due to security incident"}), 503
    
    # Normal API logic
    return jsonify(fetch_data())

# In file operations
def read_file(path):
    if lockdown.is_section_locked("file_operations"):
        raise SecurityLockdownError("File operations locked")
    
    # Normal file read
    with open(path, 'r') as f:
        return f.read()
```

### Automated Response Integration

```python
from app.security.monitoring import SecurityMonitor

monitor = SecurityMonitor()

# On high severity event, apply lockdown
@monitor.on_security_event
def handle_security_event(event):
    if event.severity in ['high', 'critical']:
        # Map severity to lockdown stage
        stage_map = {
            'medium': 5,
            'high': 10,
            'critical': 20
        }
        stage = stage_map.get(event.severity, 5)
        
        lockdown.apply_lockdown(
            stage=stage,
            reason=f"security_event_{event.event_type}"
        )
```

---

## State Persistence

### State File Structure

**Location:** `data/cerberus/lockdown/lockdown_state.json`

```json
{
  "current_stage": 10,
  "locked_sections": [
    "authentication",
    "authorization",
    "data_access",
    "file_operations",
    "network_egress",
    "api_endpoints",
    "admin_functions",
    "user_sessions",
    "encryption_keys",
    "audit_logs"
  ],
  "lockdown_history": [
    {
      "timestamp": "2024-01-15T10:30:45.123Z",
      "previous_stage": 0,
      "new_stage": 10,
      "reason": "privilege_escalation_detected",
      "newly_locked": ["authentication", "authorization", ...],
      "total_locked": 10
    }
  ],
  "last_updated": "2024-01-15T10:30:45.123Z"
}
```

### Automatic State Management

```python
# State automatically loaded on initialization
lockdown = LockdownController(data_dir="data")
# Restores: current_stage, locked_sections, lockdown_history

# State automatically saved after:
# - apply_lockdown()
# - release_lockdown()

# Manual save (rarely needed):
lockdown._save_state()
```

---

## Security Patterns

### 1. Progressive Escalation

**Pattern:** Start with minimal lockdown, escalate as threat persists

```python
# Initial breach: Lock authentication/authorization
stage = lockdown.compute_lockdown_stage(risk_score=0.5, bypass_depth=1)
lockdown.apply_lockdown(stage, reason="initial_breach")

# Bypass attempt: Escalate
stage = lockdown.compute_lockdown_stage(risk_score=0.7, bypass_depth=2)
lockdown.apply_lockdown(stage, reason="bypass_attempt")

# Confirmed compromise: Maximum escalation
stage = lockdown.compute_lockdown_stage(risk_score=0.95, bypass_depth=4)
lockdown.apply_lockdown(stage, reason="confirmed_compromise")
```

### 2. Observation Before Action

**Pattern:** Test lockdown impact without disrupting production

```python
# Step 1: Deploy in observation mode
lockdown_test = LockdownController(observation_only=True)
lockdown_test.apply_lockdown(stage=15, reason="test")
# Logs what WOULD be locked, no actual impact

# Step 2: Analyze logs, verify no critical services affected

# Step 3: Deploy in production mode
lockdown_prod = LockdownController(observation_only=False)
lockdown_prod.apply_lockdown(stage=15, reason="production_deployment")
```

### 3. Graceful Degradation

**Pattern:** Provide fallback functionality for locked sections

```python
def get_user_data(user_id):
    if lockdown.is_section_locked("database_access"):
        # Fallback to cached data
        logger.info("Database locked, using cache")
        return cache.get(f"user:{user_id}")
    
    # Normal database query
    return db.query(User).filter_by(id=user_id).first()
```

### 4. Circuit Breaker Integration

**Pattern:** Auto-release lockdown after cooldown period

```python
import time

class LockdownCircuitBreaker:
    def __init__(self, lockdown, cooldown_seconds=300):
        self.lockdown = lockdown
        self.cooldown_seconds = cooldown_seconds
        self.breach_time = None
    
    def on_breach(self, risk_score, bypass_depth):
        # Apply lockdown
        stage = self.lockdown.compute_lockdown_stage(risk_score, bypass_depth)
        self.lockdown.apply_lockdown(stage, reason="auto_breach_response")
        self.breach_time = time.time()
    
    def check_auto_release(self):
        if not self.breach_time:
            return
        
        elapsed = time.time() - self.breach_time
        if elapsed >= self.cooldown_seconds:
            # Release partial lockdown
            current = self.lockdown.get_lockdown_status()['current_stage']
            new_stage = max(0, current // 2)  # Release 50%
            
            self.lockdown.release_lockdown(stage=new_stage)
            logger.info(f"Auto-released lockdown to stage {new_stage}")
```

---

## Performance Considerations

### Memory Footprint

- **State File:** ~20 KB (25 sections × 100 history events)
- **In-Memory:** ~50 KB (state + history)
- **Minimal Overhead:** State checks are O(1) hash lookups

### Response Time

- **is_section_locked():** <0.1 ms (hash set lookup)
- **apply_lockdown():** <5 ms (iterate sections + disk write)
- **get_lockdown_status():** <1 ms (return cached state)

### Concurrency

```python
# Thread-safe by design (state updates are atomic writes)
# Safe for multi-threaded/multi-process access

# Example: Multiple threads checking lockdown status
import threading

def worker_thread(section):
    if lockdown.is_section_locked(section):
        logger.info(f"Section {section} locked, skipping task")
        return
    
    # Perform task
    do_work(section)

threads = [threading.Thread(target=worker_thread, args=(s,)) 
           for s in ['api_endpoints', 'database_access', 'file_operations']]

for t in threads:
    t.start()
```

---

## Monitoring and Alerts

### Integration with SecurityMonitor

```python
from app.security.monitoring import SecurityMonitor

monitor = SecurityMonitor()

# Log lockdown events to CloudWatch/SNS
@lockdown.on_lockdown_applied
def log_lockdown(event):
    monitor.log_security_event(
        event_type="system_lockdown",
        severity="high" if event['new_stage'] >= 15 else "medium",
        source="lockdown_controller",
        description=f"System locked to stage {event['new_stage']}",
        metadata={
            "previous_stage": event['previous_stage'],
            "newly_locked": event['newly_locked'],
            "reason": event['reason']
        }
    )
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Gauge

# Lockdown metrics
lockdown_applications = Counter(
    'cerberus_lockdown_applications_total',
    'Total number of lockdown applications',
    ['reason', 'stage']
)

lockdown_current_stage = Gauge(
    'cerberus_lockdown_current_stage',
    'Current lockdown stage (0-25)'
)

lockdown_locked_sections = Gauge(
    'cerberus_lockdown_locked_sections',
    'Number of currently locked sections'
)

# Update on each lockdown
def apply_lockdown_with_metrics(stage, reason):
    result = lockdown.apply_lockdown(stage, reason)
    
    lockdown_applications.labels(reason=reason, stage=stage).inc()
    lockdown_current_stage.set(result['new_stage'])
    lockdown_locked_sections.set(result['total_locked'])
    
    return result
```

---

## Testing

### Unit Tests

```bash
pytest tests/test_cerberus_lockdown_controller.py -v
```

**Coverage:**
- Stage computation (formula validation)
- Idempotent lockdown application
- Release functionality
- State persistence and restoration
- Observation mode behavior

### Integration Tests

```python
def test_progressive_lockdown():
    """Test progressive lockdown escalation"""
    lockdown = LockdownController(data_dir=tmpdir)
    
    # Stage 1: Low severity
    result1 = lockdown.apply_lockdown(stage=5, reason="test")
    assert result1['new_stage'] == 5
    assert len(result1['newly_locked']) == 5
    
    # Stage 2: Escalate
    result2 = lockdown.apply_lockdown(stage=10, reason="test_escalation")
    assert result2['new_stage'] == 10
    assert len(result2['newly_locked']) == 5  # Only new sections
    
    # Stage 3: Release partial
    result3 = lockdown.release_lockdown(stage=3)
    assert result3['new_stage'] == 3
    assert len(result3['released_sections']) == 7
```

---

## Troubleshooting

### Issue: Lockdown Not Persisting After Restart

**Cause:** State file not being written or wrong data_dir

**Solution:**
```python
# Check state file exists
import os
state_file = "data/cerberus/lockdown/lockdown_state.json"
print(f"State file exists: {os.path.exists(state_file)}")

# Manually save state
lockdown._save_state()

# Check file permissions
print(f"State file permissions: {oct(os.stat(state_file).st_mode)}")
```

### Issue: Lockdown Not Actually Blocking Operations

**Cause:** Application code not checking lockdown status

**Solution:**
```python
# Add lockdown checks to critical operations
def critical_operation():
    # Add this check
    if lockdown.is_section_locked("critical_section"):
        raise SecurityLockdownError("Operation locked")
    
    # Existing logic
    perform_operation()
```

### Issue: Cannot Release Lockdown

**Cause:** Attempting to release to higher stage than current

**Solution:**
```python
# Check current stage first
current = lockdown.get_lockdown_status()['current_stage']
print(f"Current stage: {current}")

# Release to lower stage (or None for full release)
result = lockdown.release_lockdown(stage=current // 2)  # Release 50%
```

---

## Best Practices

1. **Check Before Acting:** Always check `is_section_locked()` before critical operations
2. **Log Lockdowns:** Emit structured logs for all lockdown changes for audit trail
3. **Test Observation Mode:** Use observation mode to verify lockdown impact before production
4. **Progressive Release:** Release lockdowns gradually, not all at once
5. **Monitor Metrics:** Track lockdown frequency and duration for anomaly detection
6. **Document Sections:** Clearly document what each lockable section controls
7. **Graceful Degradation:** Provide fallback behavior for locked sections
8. **Auto-Expire:** Consider implementing auto-release after cooldown period

---


---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/cerberus_lockdown_controller.py]]
- [[src/app/core/security/auth.py]]
- [[utils/encryption/god_tier_encryption.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Documentation

- [01-cerberus-hydra-defense.md](01-cerberus-hydra-defense.md) - Exponential agent spawning system
- [04-observability-metrics.md](04-observability-metrics.md) - Lockdown telemetry and SLO tracking
- [05-security-monitoring.md](05-security-monitoring.md) - CloudWatch integration for lockdown events
- [08-contrarian-firewall.md](08-contrarian-firewall.md) - Orchestrator integration

---

## See Also

- [Progressive Lockdown Design Document](../../docs/PROGRESSIVE_LOCKDOWN.md)
- [Security Response Playbooks](../../docs/SECURITY_PLAYBOOKS.md)
- [Incident Response Procedures](../../docs/INCIDENT_RESPONSE.md)
