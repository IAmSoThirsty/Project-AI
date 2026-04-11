# Temporal Cloud Zero-Trust Security Framework

## Overview

This security framework implements comprehensive zero-trust security controls for Temporal Cloud infrastructure, ensuring defense-in-depth protection against attacks.

## Components

### 1. mTLS (Mutual TLS)
- **Location**: `mtls/`
- **Purpose**: Secure inter-service communication with mutual authentication
- **Features**:
  - Certificate generation and rotation
  - Integration with cert-manager and Vault PKI
  - Automatic certificate lifecycle management
  - Support for both internal and external CAs

### 2. Capability Tokens
- **Location**: `capability_tokens/`
- **Purpose**: Fine-grained authorization with cryptographically secure tokens
- **Features**:
  - Scope-based permissions
  - Time-to-Live (TTL) enforcement
  - Constraint validation (IP, service, resource)
  - Token revocation and rotation

### 3. Network Policies
- **Location**: `network_policies/`
- **Purpose**: Network segmentation and traffic control
- **Features**:
  - Kubernetes NetworkPolicy definitions
  - Calico integration for advanced policies
  - Zero-trust network architecture
  - Egress and ingress controls

### 4. Secrets Management
- **Location**: `secrets/`
- **Purpose**: Secure credential storage and distribution
- **Features**:
  - HashiCorp Vault integration
  - Sealed Secrets for Kubernetes
  - Dynamic secret generation
  - Secret rotation policies

### 5. Audit Logging
- **Location**: `audit/`
- **Purpose**: Immutable audit trail of security events
- **Features**:
  - Cryptographic event signing
  - Tamper-proof log storage
  - Real-time security monitoring
  - Compliance reporting

## Quick Start

```python
from temporal.security import (
    CertificateManager,
    CapabilityTokenManager,
    NetworkPolicyManager,
    SecretsManager,
    AuditLogger,
)

# Initialize security components
cert_manager = CertificateManager()
token_manager = CapabilityTokenManager()
policy_manager = NetworkPolicyManager()
secrets_manager = SecretsManager()
audit_logger = AuditLogger()

# Issue a capability token
token = token_manager.issue_token(
    subject="temporal-worker-001",
    scopes=["workflow:execute", "activity:invoke"],
    ttl=3600,
    constraints={"ip": "10.0.0.0/24", "service": "temporal-frontend"}
)

# Apply network policy
policy_manager.apply_policy(
    name="temporal-workers",
    namespace="temporal",
    ingress_rules=[...],
    egress_rules=[...]
)

# Log security event
audit_logger.log_event(
    event_type="TOKEN_ISSUED",
    subject="temporal-worker-001",
    metadata={"token_id": token.id, "scopes": token.scopes}
)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Zero-Trust Security Layer                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │   mTLS   │  │ Capability│  │ Network  │  │ Secrets  │  │
│  │          │  │  Tokens   │  │ Policies │  │   Mgmt   │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │              │         │
│       └──────────────┴──────────────┴──────────────┘         │
│                           │                                   │
│                    ┌──────┴──────┐                           │
│                    │ Audit Logger │                           │
│                    └─────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Security Principles

1. **Least Privilege**: Grant minimum necessary permissions
2. **Defense in Depth**: Multiple layers of security controls
3. **Zero Trust**: Never trust, always verify
4. **Immutable Audit**: Tamper-proof logging of all security events
5. **Automated Rotation**: Regular rotation of credentials and certificates

## Configuration

See individual component READMEs for detailed configuration:
- [mTLS Configuration](mtls/README.md)
- [Capability Tokens](capability_tokens/README.md)
- [Network Policies](network_policies/README.md)
- [Secrets Management](secrets/README.md)
- [Audit Logging](audit/README.md)

## Deployment

### Kubernetes

```bash
# Apply network policies
kubectl apply -f network_policies/k8s/

# Deploy cert-manager
kubectl apply -f mtls/k8s/cert-manager.yaml

# Configure Vault integration
kubectl apply -f secrets/k8s/vault-config.yaml
```

### Docker Compose

```bash
# Start with security features enabled
docker-compose -f docker-compose.security.yml up -d
```

## Compliance

This framework supports compliance with:
- SOC 2 Type II
- ISO 27001
- GDPR
- HIPAA
- PCI DSS

## Testing

```bash
# Run security tests
pytest temporal/security/tests/ -v

# Run penetration tests
pytest temporal/security/tests/penetration/ -v

# Verify mTLS configuration
python -m temporal.security.mtls.verify

# Test capability token validation
python -m temporal.security.capability_tokens.test_validation
```

## Monitoring

Security metrics are exposed via Prometheus:
- `mtls_cert_expiry_seconds` - Time until certificate expiration
- `capability_token_issued_total` - Total tokens issued
- `capability_token_validated_total` - Total token validations
- `network_policy_violations_total` - Network policy violations
- `audit_events_total` - Total audit events logged

## Support

For security issues, please contact: security@temporal.io
For general questions, see: https://docs.temporal.io/security
