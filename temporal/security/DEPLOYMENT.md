# Zero-Trust Security - Deployment Guide

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3
- HashiCorp Vault (optional, for secrets management)
- cert-manager (for automated certificate management)
- Calico (optional, for advanced network policies)

## Quick Start

### 1. Install Dependencies

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install sealed-secrets (optional)
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Install Calico (if using advanced network policies)
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

### 2. Deploy Security Infrastructure

```bash
# Navigate to temporal/security directory
cd temporal/security

# Run the integration example to generate configurations
python examples/complete_integration.py

# Deploy network policies
kubectl apply -f k8s/network-policies/

# Deploy mTLS certificates (using cert-manager)
kubectl apply -f k8s/mtls/
```

### 3. Configure Secrets Management

#### Using HashiCorp Vault

```bash
# Enable Vault secrets engines
vault secrets enable -path=secret kv-v2
vault secrets enable -path=transit transit
vault secrets enable database

# Configure database dynamic credentials
vault write database/config/temporal \
    plugin_name=postgresql-database-plugin \
    allowed_roles="temporal-readonly,temporal-readwrite" \
    connection_url="postgresql://{{username}}:{{password}}@temporal-postgresql:5432/temporal?sslmode=verify-full" \
    username="vault" \
    password="vault-password"

# Create database roles
vault write database/roles/temporal-readwrite \
    db_name=temporal \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"
```

#### Using Sealed Secrets

```bash
# Create sealed secrets for Temporal
python -c "
from temporal.security.secrets import SealedSecretsManager, create_temporal_sealed_secrets

manager = SealedSecretsManager()
sealed_secrets = create_temporal_sealed_secrets(manager, namespace='temporal')

# Write to files
for name, yaml_content in sealed_secrets.items():
    with open(f'k8s/sealed-secrets/{name}.yaml', 'w') as f:
        f.write(yaml_content)
"

# Apply sealed secrets
kubectl apply -f k8s/sealed-secrets/
```

## Configuration

### mTLS Configuration

1. **Generate CA Certificate**

```python
from temporal.security.mtls import CertificateManager

cert_manager = CertificateManager()
ca_cert = cert_manager.create_ca()
cert_manager.save_certificate(ca_cert, "certs/ca.crt", "certs/ca.key")
```

2. **Issue Service Certificates**

```python
frontend_cert = cert_manager.issue_certificate(
    common_name="temporal-frontend",
    dns_names=["temporal-frontend", "temporal-frontend.temporal.svc.cluster.local"],
    validity_days=365
)
```

3. **Deploy to Kubernetes**

```bash
# Create secret with CA certificate
kubectl create secret generic temporal-ca \
    --from-file=ca.crt=certs/ca.crt \
    -n temporal

# Create TLS secrets for services
kubectl create secret tls temporal-frontend-tls \
    --cert=certs/temporal-frontend.crt \
    --key=certs/temporal-frontend.key \
    -n temporal
```

### Capability Tokens

1. **Initialize Token Manager**

```python
from temporal.security import CapabilityTokenManager, TokenConstraints

token_manager = CapabilityTokenManager(default_ttl=3600)
```

2. **Issue Tokens**

```python
token = token_manager.issue_token(
    subject="temporal-worker-001",
    scopes=["workflow:execute", "activity:invoke"],
    ttl=3600,
    constraints=TokenConstraints(
        ip_whitelist=["10.0.0.0/24"],
        service_whitelist=["temporal-frontend"],
        rate_limit=1000
    )
)
```

3. **Validate Tokens**

```python
is_valid = token_manager.validate_token(
    token=token,
    required_scopes=["workflow:execute"],
    source_ip="10.0.1.100",
    source_service="temporal-frontend"
)
```

### Network Policies

1. **Create Policies**

```python
from temporal.security import NetworkPolicyManager

policy_manager = NetworkPolicyManager(namespace="temporal")
policy_manager.create_all_temporal_policies()
policy_manager.export_all_policies("./k8s/network-policies")
```

2. **Apply to Kubernetes**

```bash
kubectl apply -f k8s/network-policies/
```

### Audit Logging

1. **Initialize Audit Logger**

```python
from temporal.security import AuditLogger
from temporal.security.audit import AuditStorage

storage = AuditStorage(backend="postgresql", connection_string="...")
audit_logger = AuditLogger(storage_backend=storage)
```

2. **Log Events**

```python
audit_logger.log_event(
    event_type=EventType.AUTHZ_TOKEN_ISSUED,
    actor="system",
    subject="temporal-worker-001",
    action="Issued capability token"
)
```

3. **Query Events**

```python
events = storage.get_events(
    event_type=EventType.AUTHZ_TOKEN_ISSUED,
    start_time=datetime.utcnow() - timedelta(hours=24),
    limit=100
)
```

## Testing

### Test mTLS Connection

```bash
# Test with openssl
openssl s_client -connect temporal-frontend:7233 \
    -cert certs/temporal-client.crt \
    -key certs/temporal-client.key \
    -CAfile certs/ca.crt
```

### Test Network Policies

```bash
# Verify policies are applied
kubectl get networkpolicies -n temporal

# Test connectivity
kubectl run test-pod --image=busybox -it --rm -n temporal -- \
    wget -qO- temporal-frontend:7233
```

### Verify Audit Chain

```python
from temporal.security import AuditLogger
from temporal.security.audit import AuditStorage

storage = AuditStorage(backend="sqlite", connection_string="audit.db")
audit_logger = AuditLogger(storage_backend=storage)

events = storage.get_events(limit=100)
is_valid = audit_logger.verify_chain(events)
print(f"Audit chain valid: {is_valid}")
```

## Monitoring

### Prometheus Metrics

```yaml
# Add to Prometheus scrape config
- job_name: 'temporal-security'
  static_configs:
    - targets: ['temporal-frontend:9090']
  metrics_path: '/metrics'
```

### Key Metrics

- `mtls_cert_expiry_seconds` - Certificate expiration time
- `capability_token_issued_total` - Total tokens issued
- `capability_token_validated_total` - Total token validations
- `network_policy_violations_total` - Network policy violations
- `audit_events_total` - Total audit events

### Grafana Dashboards

```bash
# Import dashboard
kubectl apply -f k8s/monitoring/grafana-dashboard.yaml
```

## Troubleshooting

### Certificate Issues

```bash
# Check certificate validity
openssl x509 -in certs/temporal-frontend.crt -text -noout

# Verify certificate chain
openssl verify -CAfile certs/ca.crt certs/temporal-frontend.crt
```

### Network Policy Issues

```bash
# Check if policies are applied
kubectl describe networkpolicy temporal-frontend -n temporal

# Test connectivity
kubectl exec -it test-pod -n temporal -- nc -zv temporal-frontend 7233
```

### Audit Log Issues

```bash
# Check audit database
sqlite3 temporal_audit.db "SELECT COUNT(*) FROM audit_events;"

# Verify chain integrity
python -m temporal.security.audit.verify_chain
```

## Security Best Practices

1. **Rotate Certificates Regularly**: Set up automated rotation 30 days before expiry
2. **Use Strong Scopes**: Define narrow, specific scopes for capability tokens
3. **Monitor Audit Logs**: Set up alerts for security violations
4. **Regular Security Audits**: Review policies and access patterns monthly
5. **Backup Secrets**: Ensure Vault is backed up and highly available
6. **Network Segmentation**: Use Calico for fine-grained network control
7. **Principle of Least Privilege**: Grant minimum necessary permissions

## Production Checklist

- [ ] mTLS enabled for all inter-service communication
- [ ] Capability tokens with appropriate scopes and constraints
- [ ] Network policies applied and tested
- [ ] Secrets stored in Vault with dynamic generation
- [ ] Audit logging enabled with immutable storage
- [ ] Certificate rotation automated
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery tested
- [ ] Security audit completed
- [ ] Documentation updated

## Support

For issues and questions:
- GitHub Issues: https://github.com/temporal/security
- Documentation: https://docs.temporal.io/security
- Security Contact: security@temporal.io
