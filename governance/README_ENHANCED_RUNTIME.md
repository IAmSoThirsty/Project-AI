# Enhanced Sovereign Runtime

## Overview

The Enhanced Sovereign Runtime extends the base Sovereign Runtime with advanced policy enforcement capabilities, including capability-based security, time constraints, JIT policy compilation, and cryptographic proofs.

## Features

### 1. Capability-Based Security

Fine-grained capabilities with scope, TTL, and constraints:

- **Scopes**: Global, Service, Resource, Operation
- **Time-To-Live (TTL)**: Automatic expiration
- **Usage Limits**: Maximum use count
- **Constraints**: Time windows, rate limits, conditions, delegation rules
- **Delegation**: Controlled capability delegation with depth limits

#### Example Usage

```python
from governance.sovereign_runtime_enhanced import (
    EnhancedSovereignRuntime,
    CapabilityScope,
    CapabilityConstraint
)

runtime = EnhancedSovereignRuntime()

# Issue a capability token
token = runtime.issue_capability(
    issuer="admin",
    subject="user123",
    action="read:customer_data",
    scope=CapabilityScope.SERVICE,
    scope_value="customer_api",
    ttl_seconds=3600,  # 1 hour
    max_uses=100
)

# Check capability
valid, reason = runtime.check_capability(token.token_id)

# Use capability
success, reason = runtime.use_capability(token.token_id)
```

### 2. Time-Based Constraints

Enforce temporal policies and rate limits:

- **Business Hours**: Define allowed operation windows
- **Time Windows**: Specific date/time ranges
- **Rate Limiting**: Token bucket algorithm
- **Blackout Periods**: Scheduled maintenance windows

#### Example Usage

```python
from governance.sovereign_runtime_enhanced import TimeWindow, RateLimitConfig

# Configure business hours
business_hours = TimeWindow(
    start_hour=9,
    end_hour=17,
    days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
    timezone_name="UTC"
)
runtime.time_engine.set_business_hours(business_hours)

# Configure rate limit
rate_config = RateLimitConfig(
    max_calls=100,
    window_seconds=60
)
runtime.time_engine.register_rate_limit("api_calls", rate_config)

# Check rate limit
allowed, info = runtime.time_engine.check_rate_limit("api_calls", "user1")
```

### 3. Dynamic Policy Compilation (JIT)

Compile policies to bytecode for fast execution:

- **Policy DSL**: JSON-based policy definitions
- **Rule Evaluation**: Conditional logic with safe eval
- **Performance**: JIT compilation for speed
- **Statistics**: Execution metrics and profiling

#### Example Usage

```python
# Define policy
policy_def = {
    "rules": [
        {
            "condition": "context.get('user_role') == 'admin'",
            "allow": True,
            "reason": "Admin access granted"
        },
        {
            "condition": "context.get('emergency', False)",
            "allow": True,
            "reason": "Emergency override"
        }
    ],
    "default": {
        "allowed": False,
        "reason": "Access denied"
    }
}

# Compile policy
runtime.compile_policy("access_control", policy_def)

# Evaluate policy
allowed, reason, metadata = runtime.evaluate_policy(
    "access_control",
    {"user_role": "admin"}
)
```

### 4. Cryptographic Proofs

Ed25519 signatures for all policy decisions:

- **Non-repudiation**: Cryptographically signed decisions
- **Tamper Detection**: Hash chain integrity
- **Audit Trail**: Immutable decision log
- **Verification**: Public key verification

#### Example Usage

```python
# Evaluate with proof generation
allowed, reason, metadata = runtime.evaluate_policy(
    "security_policy",
    context={"user": "alice", "action": "read"},
    generate_proof=True
)

proof_id = metadata["proof_id"]

# Verify proof
proof = runtime.proof_generator.proofs[proof_id]
is_valid = runtime.proof_generator.verify_proof(proof)

# Export proofs
runtime.proof_generator.export_proofs(Path("proofs.json"))
```

### 5. Integration

#### STATE_REGISTER

Tracks policy decisions in a state register:

```python
# Enforce policy (automatically updates STATE_REGISTER)
allowed, reason, metadata = runtime.enforce_policy(
    "data_access_policy",
    context={"user": "bob", "resource": "database"}
)

# Check state register
state = runtime.state_register["data_access_policy"]
print(f"Last decision: {state['last_decision']}")
print(f"Timestamp: {state['timestamp']}")
```

#### Triumvirate Integration

High-stakes decisions require Triumvirate consensus:

```python
def triumvirate_callback(policy_id, context, decision):
    """Triumvirate review for high-stakes operations"""
    if context.get("high_stakes", False):
        # Simulate consensus check
        return {
            "override": True,
            "allowed": False,
            "reason": "Requires additional approval"
        }
    return {"override": False}

runtime.register_triumvirate_callback(triumvirate_callback)

# Enforce with Triumvirate override
allowed, reason, metadata = runtime.enforce_policy(
    "critical_operation",
    context={"high_stakes": True},
    triumvirate_override=True
)
```

## Architecture

```
EnhancedSovereignRuntime
├── CapabilityRegistry
│   ├── Token Management
│   ├── Subject Indexing
│   └── Expiration Cleanup
├── TimeConstraintEngine
│   ├── Business Hours
│   ├── Rate Limiters
│   └── Temporal Policies
├── PolicyCompiler
│   ├── Policy Parser
│   ├── JIT Compilation
│   └── Execution Engine
├── ProofGenerator
│   ├── Ed25519 Signing
│   ├── Hash Computation
│   └── Verification
└── Integration Layer
    ├── STATE_REGISTER
    └── Triumvirate Callback
```

## Convenience Methods

```python
# Business hours capability
token = runtime.create_business_hours_capability(
    issuer="hr_system",
    subject="employee",
    action="access:office_systems",
    ttl_days=90
)

# Rate-limited capability
token = runtime.create_rate_limited_capability(
    issuer="api_gateway",
    subject="api_client",
    action="api:call",
    max_calls=1000,
    window_seconds=3600,
    ttl_days=30
)

# State summary
summary = runtime.get_state_summary()

# Full compliance export
runtime.export_full_compliance_bundle(Path("compliance/"))
```

## Compliance & Audit

### Audit Trail Integrity

```python
# Verify audit trail
is_valid, issues = runtime.base_runtime.verify_audit_trail_integrity()

if not is_valid:
    print(f"Integrity issues: {issues}")
```

### Compliance Bundle Export

```python
# Export complete compliance bundle
runtime.export_full_compliance_bundle(Path("compliance_bundle/"))

# Files generated:
# - base_compliance.json (audit trail + integrity verification)
# - policy_proofs.json (all cryptographic proofs)
# - state_summary.json (runtime state snapshot)
```

## Performance

- **Policy Compilation**: Sub-millisecond compilation time
- **Policy Evaluation**: <1ms average execution time
- **Capability Checks**: <0.1ms per check
- **Proof Generation**: ~1-2ms per proof
- **Rate Limiting**: O(1) token bucket algorithm

## Security

- **Ed25519 Signatures**: 256-bit security
- **SHA-256 Hashing**: Collision-resistant hashing
- **Immutable Audit**: Hash-chained audit trail
- **Safe Evaluation**: Restricted AST evaluation for policies
- **No Code Injection**: Sandboxed policy execution

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_sovereign_runtime_enhanced.py -v
```

Test coverage includes:
- 39 test cases
- Capability management
- Time constraints
- Policy compilation
- Cryptographic proofs
- Integration scenarios
- Performance benchmarks

## Demo

Run the interactive demonstration:

```bash
python governance/demo_enhanced_runtime.py
```

Demonstrates:
1. Capability-based security
2. Time-based constraints
3. JIT policy compilation
4. Cryptographic proofs
5. STATE_REGISTER integration
6. Triumvirate integration
7. Audit trail & compliance

## API Reference

### EnhancedSovereignRuntime

#### Methods

- `issue_capability(...)` - Issue a new capability token
- `check_capability(token_id, context)` - Check capability validity
- `use_capability(token_id, context)` - Use a capability
- `compile_policy(policy_id, policy_def)` - Compile a policy
- `evaluate_policy(policy_id, context, generate_proof)` - Evaluate policy
- `enforce_policy(policy_id, context, triumvirate_override)` - Enforce policy
- `register_triumvirate_callback(callback)` - Register Triumvirate integration
- `get_state_summary()` - Get runtime state summary
- `export_full_compliance_bundle(output_dir)` - Export compliance bundle

### CapabilityToken

#### Properties

- `token_id` - Unique token identifier
- `issuer` - Token issuer
- `subject` - Token subject (who can use it)
- `action` - Permitted action
- `scope` - Capability scope
- `expires_at` - Expiration timestamp
- `max_uses` - Maximum use count
- `uses_count` - Current use count
- `constraints` - List of constraints

#### Methods

- `is_valid(context)` - Check validity
- `use()` - Increment usage counter
- `delegate(new_subject, constraints)` - Delegate to another subject

### PolicyCompiler

#### Methods

- `compile_policy(policy_id, policy_def)` - Compile policy
- `get_compiled_policy(policy_id)` - Get compiled policy
- `get_stats()` - Get compilation statistics

### ProofGenerator

#### Methods

- `generate_proof(decision_type, policy_id, context, decision)` - Generate proof
- `verify_proof(proof)` - Verify proof
- `export_proofs(output_path)` - Export all proofs

## Integration Points

### With Base Sovereign Runtime

```python
# Access base runtime features
runtime.base_runtime.audit_log("CUSTOM_EVENT", data)
runtime.base_runtime.create_config_snapshot(config)
runtime.base_runtime.verify_audit_trail_integrity()
```

### With External Systems

```python
# Custom STATE_REGISTER implementation
runtime.state_register = custom_state_register

# Custom Triumvirate implementation
runtime.register_triumvirate_callback(custom_triumvirate_handler)
```

## License

Part of the Sovereign Governance Substrate project.

## See Also

- `sovereign_runtime.py` - Base runtime system
- `temporal_audit_ledger.py` - Temporal audit logging
- `existential_proof.py` - Existential proof system
