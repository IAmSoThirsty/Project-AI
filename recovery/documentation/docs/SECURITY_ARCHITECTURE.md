# Security Architecture

## Overview

The `src/security` module implements Thirsty's Asymmetric Security Framework - a comprehensive security substrate providing multi-layered defense, constitutional policy enforcement, and adversarial resistance. It implements Layer 2 and Layer 3 security controls with UTC-aware temporal integrity.

**Purpose**: Provide enterprise-grade security enforcement, cryptographic operations, audit hardening, and asymmetric defense mechanisms across the platform.

**Scope**: Security gateway, policy enforcement, key management, audit systems, economic defense models, and control plane hardening.

## Components

### Core Security Components

- **asymmetric_security.py**: Core asymmetric security framework
  - Layer 3 Security Enforcement Gateway
  - Layer 2 Reuse Friction Index (RFI) Calculator
  - `SecurityContext`: Enterprise security context with UTC-aware temporal markers
  - `OperationalState`: System state machine validation
  - `SecurityViolationError`: Exception for security breaches
  - Constitutional and RFI checks
  - Bounded memory consumption for adversarial defense

- **key_management.py**: Cryptographic key management
  - Key generation and rotation
  - Secure key storage
  - Key derivation
  - Cryptographic operations

- **audit_hardening.py**: Audit trail hardening
  - Tamper-proof logging
  - Audit event validation
  - Compliance reporting
  - Forensic capabilities

- **control_plane_hardening.py**: Control plane security
  - Administrative action validation
  - Control plane isolation
  - Privilege escalation prevention
  - Administrative audit trail

- **abyss_simulation.py**: Adversarial simulation and testing
  - Attack scenario simulation
  - Security testing automation
  - Vulnerability assessment
  - Resilience validation

- **economic_roi_model.py**: Economic defense modeling
  - Attack cost calculation
  - Defense investment ROI
  - Risk quantification
  - Security economics

### Module Structure

```
security/
├── __init__.py                    # Module initialization
├── asymmetric_security.py         # Core security framework
├── key_management.py              # Key management
├── audit_hardening.py             # Audit hardening
├── control_plane_hardening.py     # Control plane security
├── abyss_simulation.py            # Adversarial testing
├── economic_roi_model.py          # Economic modeling
└── __pycache__/                   # Python cache
```

## Dependencies

### Internal Dependencies

- `src.governance`: Policy definitions and enforcement
- `src.app.core`: Core system integration
- `src.data`: Secure data storage
- `src.cognition`: AI-enhanced threat detection

### External Dependencies

- **cryptography**: Cryptographic primitives
- **datetime**: UTC-aware temporal tracking
- **logging**: Security event logging
- **dataclasses**: Configuration management
- **enum**: State machine definitions
- **OrderedDict**: Bounded memory structures

## Data Flow

### Security Enforcement Flow

```
Operation Request
  ↓
Security Context Creation
  ↓
Layer 3 Enforcement Gateway
  ├─ Constitutional checks
  ├─ Operational state validation
  ├─ Jurisdictional boundary check
  └─ Temporal integrity validation
  ↓
Layer 2 RFI Calculator
  ├─ Reuse friction analysis
  ├─ Adversarial resistance check
  └─ Memory bound validation
  ↓
Operation Execution (if approved)
  ↓
Audit Event Recording
  ↓
Response
```

### Key Management Flow

```
Key Request
  ↓
Authentication
  ↓
Authorization
  ↓
Key Retrieval/Generation
  ↓
Cryptographic Operation
  ↓
Audit Log
  ↓
Secure Key Erasure
```

### Audit Trail Flow

```
Security Event
  ↓
Event Validation
  ↓
Tamper-Proof Logging
  ↓
Secure Storage
  ↓
Compliance Reporting
```

## Integration Points

### APIs

- `SecurityGateway.enforce()`: Main enforcement entry point
- `RFICalculator.calculate()`: Reuse friction calculation
- `KeyManager.get_key()`: Key management API
- `AuditLogger.log_event()`: Audit logging API
- `ControlPlane.validate()`: Control plane validation

### Events

- Security violation events
- Audit events
- Key rotation events
- State transition events
- Attack detection events

### Hooks

- Pre-operation security checks
- Post-operation audit hooks
- Key lifecycle hooks
- State transition hooks
- Alert trigger hooks

## Deployment

### Security Configuration

```python
security_config = {
    "enforcement_level": "strict",
    "rfi_threshold": 0.8,
    "operational_state": "normal",
    "audit_level": "comprehensive",
    "key_rotation_interval": 86400,  # 24 hours
    "temporal_tolerance": 300  # 5 minutes
}
```

### Initialization

```python
from src.security.asymmetric_security import SecurityContext, SecurityGateway

context = SecurityContext(
    user_id="user123",
    action="data_access",
    tenant_id="tenant1",
    auth_proof="...",
    audit_span_id="span123"
)

gateway = SecurityGateway(config)
gateway.enforce(context)
```

### Production Deployment

- Security service as separate process
- Hardware security module (HSM) integration
- Vault integration for key storage
- SIEM integration for audit logs
- Distributed security enforcement

## Architecture Patterns

### Defense in Depth

1. **Layer 1**: Network and infrastructure security
2. **Layer 2**: Reuse Friction Index (RFI) - adversarial resistance
3. **Layer 3**: Security Enforcement Gateway - policy enforcement
4. **Layer 4**: Application-level security controls

### Asymmetric Defense

- High cost for attackers
- Low cost for legitimate users
- Reuse friction calculations
- Economic deterrence

### State Machine Security

- Operational state tracking (Normal/Degraded/Locked/Halted)
- State transition validation
- Invalid state detection
- Automatic recovery mechanisms

### UTC-Aware Temporal Integrity

- All timestamps in UTC
- Temporal validation
- Replay attack prevention
- Time-based security policies

## Security Considerations

### Threat Model

- Adversarial AI attacks
- Privilege escalation attempts
- Data exfiltration
- Replay attacks
- Side-channel attacks
- Social engineering
- Supply chain attacks

### Cryptographic Security

- Modern cryptographic algorithms (AES-256, RSA-4096, Ed25519)
- Regular key rotation
- Forward secrecy
- Quantum-resistant preparation
- Secure random number generation

### Audit Security

- Tamper-proof logging
- Write-only audit logs
- Cryptographic hashing
- Distributed audit storage
- Compliance with regulations (SOC 2, ISO 27001, GDPR)

### Memory Security

- Bounded memory structures
- Secure memory wiping
- No sensitive data in swap
- Stack canaries
- ASLR enabled

## Performance Characteristics

- Minimal latency for security checks (<5ms p99)
- Efficient RFI calculations
- Cached policy decisions
- Async audit logging
- Optimized cryptographic operations

## Monitoring and Observability

- Security event metrics
- Violation rate tracking
- RFI distribution monitoring
- Key usage metrics
- Audit volume tracking
- Performance impact analysis
- Threat detection alerts

## Error Handling

- `SecurityViolationError` for breaches
- Detailed error context
- Automatic lockdown on critical violations
- Recovery procedures
- Incident response automation

## Testing Strategy

- Unit tests for each component
- Integration tests for enforcement flow
- Penetration testing
- Fuzzing for input validation
- Adversarial simulation via `abyss_simulation.py`
- Compliance validation tests

## Status

- **Status**: SOLID
- **Last Verified**: 2026-04-09
- **Dependencies**: Verified in smoke tests

## Future Extensions

- Quantum-resistant cryptography
- Hardware security module (HSM) integration
- Advanced threat intelligence integration
- ML-based anomaly detection
- Zero-trust architecture enhancements
- Distributed security enforcement
- Enhanced forensic capabilities
- Automated incident response
- Security policy as code
- Continuous security validation

## Compliance and Standards

- SOC 2 Type II compliance ready
- ISO 27001 aligned
- GDPR compliant
- NIST Cybersecurity Framework aligned
- CIS Controls implementation
- Zero Trust principles
