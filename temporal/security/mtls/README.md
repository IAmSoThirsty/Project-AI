# mTLS (Mutual TLS) Implementation

## Overview

This module provides comprehensive mutual TLS support for secure inter-service communication in Temporal Cloud infrastructure.

## Features

- **Certificate Generation**: Create CA and service certificates with strong cryptography
- **Automatic Rotation**: Rotate certificates before expiry
- **Multiple Backends**: Support for Vault PKI and cert-manager
- **Certificate Validation**: Verify certificates against CA
- **Lifecycle Management**: Track certificate validity and expiration

## Quick Start

### Creating a Certificate Authority

```python
from temporal.security.mtls import CertificateManager

cert_manager = CertificateManager()

# Create CA
ca_cert = cert_manager.create_ca(
    common_name="Temporal Cloud Root CA",
    organization="Temporal Technologies",
    validity_days=3650
)

# Save CA certificate and key
cert_manager.save_certificate(
    ca_cert,
    cert_path="./certs/ca.crt",
    key_path="./certs/ca.key"
)
```

### Issuing Service Certificates

```python
# Issue certificate for temporal-frontend
frontend_cert = cert_manager.issue_certificate(
    common_name="temporal-frontend",
    dns_names=["temporal-frontend", "temporal-frontend.temporal.svc.cluster.local"],
    ip_addresses=["10.0.1.100"],
    validity_days=365
)

cert_manager.save_certificate(
    frontend_cert,
    cert_path="./certs/frontend.crt",
    key_path="./certs/frontend.key"
)
```

### Using Vault PKI

```python
from temporal.security.mtls import VaultPKI

vault_pki = VaultPKI(
    vault_addr="https://vault.example.com:8200",
    vault_token="s.abc123...",
    pki_path="pki",
    role_name="temporal-service"
)

# Issue certificate from Vault
cert_data = vault_pki.issue_certificate(
    common_name="temporal-worker",
    ttl="8760h",
    alt_names="temporal-worker.example.com,worker.example.com",
    ip_sans="10.0.1.101"
)

# Save certificate
with open("worker.crt", "w") as f:
    f.write(cert_data["certificate"])
with open("worker.key", "w") as f:
    f.write(cert_data["private_key"])
```

### Certificate Rotation

```python
# Check certificates needing rotation
certs_to_rotate = cert_manager.get_certificates_needing_rotation(
    certificates=[frontend_cert, worker_cert],
    rotation_threshold_days=30
)

# Rotate certificates
for cert in certs_to_rotate:
    new_cert = cert_manager.rotate_certificate(cert, validity_days=365)
    cert_manager.save_certificate(
        new_cert,
        cert_path=f"./certs/{cert.subject}.crt",
        key_path=f"./certs/{cert.subject}.key"
    )
```

## Kubernetes Integration

### Using cert-manager

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: temporal-ca-issuer
spec:
  ca:
    secretName: temporal-ca-secret

---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: temporal-frontend
  namespace: temporal
spec:
  secretName: temporal-frontend-tls
  duration: 8760h
  renewBefore: 720h
  commonName: temporal-frontend
  dnsNames:
    - temporal-frontend
    - temporal-frontend.temporal.svc.cluster.local
  issuerRef:
    name: temporal-ca-issuer
    kind: ClusterIssuer
```

### Vault PKI Setup

```bash
# Enable PKI secrets engine
vault secrets enable pki

# Set max lease TTL
vault secrets tune -max-lease-ttl=87600h pki

# Generate root CA
vault write pki/root/generate/internal \
    common_name="Temporal Cloud Root CA" \
    ttl=87600h

# Create role
vault write pki/roles/temporal-service \
    allowed_domains="temporal.svc.cluster.local,example.com" \
    allow_subdomains=true \
    max_ttl="8760h"
```

## Configuration

### mTLS Config Example

```python
from temporal.security.mtls import MTLSConfig

mtls_config = MTLSConfig(
    ca_cert_path="./certs/ca.crt",
    cert_path="./certs/service.crt",
    key_path="./certs/service.key",
    verify_client=True,
    verify_server=True,
    min_tls_version="1.3",
    cipher_suites=[
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
    ],
    cert_rotation_days=30,
    key_size=4096
)
```

## Security Best Practices

1. **Key Size**: Use at least 2048-bit RSA keys (4096-bit for CA)
2. **Validity Period**: Limit certificate validity to 1 year or less
3. **Rotation**: Rotate certificates 30 days before expiry
4. **Storage**: Protect private keys with 0600 permissions
5. **TLS Version**: Use TLS 1.3 with strong cipher suites
6. **Mutual Auth**: Always verify both client and server certificates

## Certificate Monitoring

Monitor certificate expiry with Prometheus:

```python
from prometheus_client import Gauge

cert_expiry_gauge = Gauge(
    'mtls_cert_expiry_seconds',
    'Time until certificate expiration',
    ['subject']
)

for cert in certificates:
    expiry_seconds = (cert.not_valid_after - datetime.utcnow()).total_seconds()
    cert_expiry_gauge.labels(subject=cert.subject).set(expiry_seconds)
```

## Troubleshooting

### Certificate Verification Failed

```bash
# Verify certificate chain
openssl verify -CAfile ca.crt service.crt

# Check certificate details
openssl x509 -in service.crt -text -noout

# Test mTLS connection
openssl s_client -connect localhost:7233 \
    -cert service.crt -key service.key -CAfile ca.crt
```

### Certificate Expired

```bash
# Check expiry date
openssl x509 -in service.crt -noout -dates

# Rotate certificate
python -m temporal.security.mtls.rotate --cert service.crt
```
