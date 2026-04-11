# Liara Safety Guardrails

## Overview

Comprehensive safety mechanisms for Liara, the failover controller, implementing strict security controls and monitoring.

## Architecture

### Components

1. **Capability Token System** (`CapabilityToken`)
   - Cryptographically signed tokens
   - Time-bound with strict TTL enforcement
   - Capability-based access control
   - Tamper-resistant design

2. **TTL Enforcement**
   - Hard maximum limit: 900 seconds (15 minutes)
   - Minimum limit: 60 seconds
   - Cryptographic binding to token signature
   - Automatic expiration and revocation

3. **Audit Logging** (`ImmutableAuditLog`)
   - Blockchain-style hash chain
   - Merkle tree anchoring every 10 entries
   - Tamper-evident design
   - Persistent storage
   - Integrity verification

4. **Emergency Kill Switch**
   - Immediate shutdown on policy violation
   - Automatic activation on:
     - Prohibited operations
     - Rate limit violations
     - Capability violations
   - Admin-key required for deactivation

5. **Rate Limiting** (`RateLimiter`)
   - Per-minute limits (10 actions)
   - Per-hour limits (100 actions)
   - Token bucket algorithm
   - Automatic kill switch trigger on violation

6. **Privilege Verification**
   - Continuous token validation
   - Signature verification
   - TTL checking
   - Capability boundary enforcement

## Safety Guarantees

### 1. TTL Enforcement

```python
# Maximum TTL is cryptographically enforced
token = guard.issue_token("role", caps, 900)  # ✓ OK
token = guard.issue_token("role", caps, 901)  # ✗ SafetyViolation

# TTL is bound to signature - tampering detected
token.expires_at = datetime.utcnow() + timedelta(hours=10)
token.is_valid(secret_key)  # ✗ False - signature invalid
```

### 2. Capability Restrictions

```python
# Whitelist-based capability system
caps = {Capability.READ_METRICS, Capability.READ_HEALTH}
token = guard.issue_token("limited_role", caps, 300)

# Allowed operations
guard.check_action("read_metrics", Capability.READ_METRICS)  # ✓

# Denied operations
guard.check_action("restart_service", Capability.RESTART_SERVICE)  # ✗ SafetyViolation
```

### 3. Prohibited Operations

System-level operations are NEVER allowed:

- `execute_shell`
- `modify_kernel`
- `change_permissions`
- `install_software`
- `modify_firewall`
- `access_secrets`
- `delete_data`
- `modify_audit_log`

Attempting any prohibited operation triggers the kill switch.

### 4. Audit Logging

```python
# All actions are logged in tamper-evident chain
guard.check_action("action1", Capability.READ_METRICS)
guard.check_action("action2", Capability.READ_HEALTH)

# Verify integrity
guard.audit_log.verify_integrity()  # ✓ True

# Tamper with log
guard.audit_log.entries[0].action = "MODIFIED"
guard.audit_log.verify_integrity()  # ✗ False - tamper detected
```

### 5. Kill Switch

```python
# Automatic activation on violation
guard.check_action("execute_shell", Capability.READ_METRICS)
# -> Kill switch activated

# All subsequent actions blocked
guard.check_action("read_metrics", Capability.READ_METRICS)
# -> SafetyViolation: "Kill switch activated"

# Deactivation requires admin key
admin_key = hashlib.sha256(b"admin_override").hexdigest()
guard.deactivate_kill_switch(admin_key)
```

## Usage Examples

### Basic Usage

```python
from kernel.liara_safety import LiaraSafetyGuard, Capability, SafetyViolation

# Initialize guard
guard = LiaraSafetyGuard()

# Issue token with capabilities
capabilities = {
    Capability.READ_HEALTH,
    Capability.READ_METRICS,
    Capability.RESTART_SERVICE,
}

token = guard.issue_token(
    role="failover_controller",
    capabilities=capabilities,
    ttl_seconds=600  # 10 minutes
)

# Perform authorized actions
guard.check_action("monitor_health", Capability.READ_HEALTH, {"target": "db-primary"})
guard.check_action("gather_metrics", Capability.READ_METRICS, {"service": "api"})
guard.check_action("restart_service", Capability.RESTART_SERVICE, {"service": "web"})

# Verify privileges continuously
if guard.verify_privileges():
    print("Privileges valid")

# Revoke token when done
guard.revoke_token("operation_complete")

# Verify audit log integrity
assert guard.audit_log.verify_integrity()
```

### Failover Workflow

```python
# Emergency failover scenario
guard = LiaraSafetyGuard()

# Issue emergency token (maximum TTL)
token = guard.issue_token(
    role="liara_emergency",
    capabilities={
        Capability.READ_HEALTH,
        Capability.ISOLATE_COMPONENT,
        Capability.TRIGGER_FAILOVER,
        Capability.ROUTE_TRAFFIC,
    },
    ttl_seconds=900  # Maximum allowed
)

# Detect failure
guard.check_action("check_primary_health", Capability.READ_HEALTH)

# Isolate failed component
guard.check_action("isolate_primary", Capability.ISOLATE_COMPONENT, {
    "component": "primary-db"
})

# Trigger failover
guard.check_action("failover_to_backup", Capability.TRIGGER_FAILOVER, {
    "from": "primary-db",
    "to": "backup-db"
})

# Reroute traffic
guard.check_action("reroute_traffic", Capability.ROUTE_TRAFFIC, {
    "from": "primary-endpoint",
    "to": "backup-endpoint"
})

# Cleanup
guard.revoke_token("failover_complete")
```

## Available Capabilities

| Capability | Description |
|------------|-------------|
| `READ_METRICS` | Read system metrics |
| `READ_HEALTH` | Read health status |
| `READ_LOGS` | Read log files |
| `RESTART_SERVICE` | Restart a service |
| `SCALE_RESOURCE` | Scale resources up/down |
| `ROUTE_TRAFFIC` | Route network traffic |
| `TRIGGER_BACKUP` | Trigger backup operation |
| `ISOLATE_COMPONENT` | Isolate a component |
| `TRIGGER_FAILOVER` | Trigger failover |

## Security Properties

### Cryptographic Guarantees

1. **Token Integrity**: HMAC-SHA256 signatures prevent tampering
2. **Non-Repudiation**: All actions logged with timestamps and signatures
3. **Audit Trail**: Merkle tree provides cryptographic proof of log integrity

### Safety Invariants

1. **Single Token**: Only one active token at a time
2. **Bounded TTL**: No token can exceed 900 seconds
3. **Capability Isolation**: No capability escalation possible
4. **Immutable Audit**: Audit log cannot be modified without detection
5. **Kill Switch**: Violations immediately halt all operations

### Thread Safety

All operations are thread-safe:
- Token issuance/revocation
- Action checking
- Audit logging
- Rate limiting
- Privilege verification

## Testing

Comprehensive test suite covering:

- Token generation and validation
- TTL enforcement and verification
- Capability-based access control
- Prohibited operation blocking
- Audit log integrity
- Merkle tree anchoring
- Kill switch activation
- Rate limiting
- Concurrent access
- Violation scenarios

Run tests:
```bash
pytest tests/test_liara_safety.py -v
```

## Files

- `kernel/liara_safety.py` - Main implementation
- `tests/test_liara_safety.py` - Comprehensive test suite
- `kernel/liara_safety_examples.py` - Usage examples
- `kernel/test_safety_simple.py` - Quick validation script

## Integration with Existing Liara System

The safety guard integrates with the existing Liara system:

```python
from cognition.liara_guard import authorize_liara, revoke_liara
from kernel.liara_safety import get_safety_guard, Capability

# Get global safety guard
guard = get_safety_guard()

# Issue token with safety enforcement
token = guard.issue_token(
    role="failover_controller",
    capabilities={Capability.TRIGGER_FAILOVER},
    ttl_seconds=900
)

# Use existing Liara authorization (now with safety checks)
authorize_liara("pillar_failed", ttl_seconds=900)

# All Liara actions must pass safety checks
guard.check_action("liara_action", Capability.TRIGGER_FAILOVER)
```

## Monitoring and Observability

```python
# Get current status
status = guard.get_status()

print(f"Kill switch: {status['kill_switch_activated']}")
print(f"Active token: {status['active_token']}")
print(f"Rate limit remaining: {status['rate_limit_remaining']}")
print(f"Audit entries: {status['audit_entries']}")
print(f"Audit integrity: {status['audit_integrity']}")

# Check specific metrics
if status['active_token']:
    print(f"Time remaining: {status['active_token']['time_remaining']}s")
    print(f"Capabilities: {status['active_token']['capabilities']}")
```

## Emergency Procedures

### Kill Switch Activation

If the kill switch is activated:

1. All Liara actions are immediately blocked
2. Active token is revoked
3. Event is logged to audit log
4. Admin notification should be triggered

### Kill Switch Deactivation

Requires admin intervention:

```python
import hashlib

# Generate admin key (in production, use secure key management)
admin_key = hashlib.sha256(b"admin_override").hexdigest()

# Deactivate kill switch
guard.deactivate_kill_switch(admin_key)
```

### Audit Log Investigation

```python
# Review recent actions
for entry in guard.audit_log.entries[-10:]:
    print(f"{entry.timestamp} | {entry.action} | {entry.result} | {entry.role}")

# Verify log integrity
if not guard.audit_log.verify_integrity():
    print("⚠️  CRITICAL: Audit log integrity compromised!")
    # Investigate tampering

# Check Merkle roots
print(f"Merkle roots computed: {len(guard.audit_log.merkle_roots)}")
for i, root in enumerate(guard.audit_log.merkle_roots):
    print(f"  Root {i}: {root}")
```

## Design Rationale

### Why 900 seconds TTL?

- 15 minutes is sufficient for most emergency operations
- Short enough to limit blast radius of compromised tokens
- Long enough to complete complex failover procedures
- Industry standard for emergency access windows

### Why capability-based access?

- Principle of least privilege
- Prevents privilege escalation
- Explicit, auditable permissions
- Fine-grained control

### Why immutable audit log?

- Non-repudiation of actions
- Forensic investigation capability
- Compliance requirements
- Tamper evidence

### Why kill switch?

- Fail-safe mechanism
- Immediate response to violations
- Prevents cascading failures
- Last line of defense

## Future Enhancements

Potential improvements:

1. **Multi-party authorization**: Require multiple tokens for sensitive operations
2. **Time-based capabilities**: Different capabilities at different times
3. **Geolocation restrictions**: Limit operations by location
4. **Audit log encryption**: Encrypt sensitive metadata
5. **Remote attestation**: Cryptographic proof of guard integrity
6. **Rate limit customization**: Per-capability rate limits
7. **Token delegation**: Temporary capability delegation with constraints

## License

Part of the Sovereign Governance Substrate project.

## Authors

- Liara Safety Guardrails Implementation - 2026-03-05
