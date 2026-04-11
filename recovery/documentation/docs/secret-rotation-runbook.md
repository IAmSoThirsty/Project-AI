# Secret Rotation Runbook

**Team Charlie - SRE Documentation Lead**

## Overview

Procedures for rotating secrets, API keys, certificates, and JWT signing keys in the Sovereign Governance Substrate.

## Rotation Schedule

| Secret Type | Rotation Frequency | Owner | Automated |
|-------------|-------------------|-------|-----------|
| JWT Signing Key | 90 days | Security Team | ✅ Yes |
| Database Passwords | 90 days | DBA Team | ⚠️ Semi-auto |
| API Keys | 180 days | Platform Team | ❌ Manual |
| TLS Certificates | Auto-renewal | cert-manager | ✅ Yes |
| Vault Root Token | 365 days | Security Team | ❌ Manual |

## JWT Signing Key Rotation

### Automated Rotation (Recommended)

```bash

# Trigger rotation job

kubectl create job jwt-rotation-$(date +%s) \
  --from=cronjob/jwt-key-rotation -n default

# Monitor rotation

kubectl logs -n default job/jwt-rotation-$(date +%s) -f

# Verify new key is active

kubectl get secret jwt-signing-key -n default -o jsonpath='{.data.key}' | base64 -d | head -c 20
```

### Manual Rotation (Emergency)

```bash

# 1. Generate new key

openssl genrsa -out jwt-new.key 4096

# 2. Create Kubernetes secret

kubectl create secret generic jwt-signing-key-new \
  --from-file=key=jwt-new.key \
  -n default --dry-run=client -o yaml | kubectl apply -f -

# 3. Update services to use new key (rolling update)

kubectl set env deployment/auth-service \
  JWT_KEY_SECRET=jwt-signing-key-new -n default

# 4. Wait for rollout

kubectl rollout status deployment/auth-service -n default

# 5. Verify auth still works

curl -X POST https://auth.sovereign.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# 6. Delete old key (after 24h grace period)

kubectl delete secret jwt-signing-key -n default

# 7. Rename new key

kubectl get secret jwt-signing-key-new -n default -o yaml | \
  sed 's/jwt-signing-key-new/jwt-signing-key/' | \
  kubectl apply -f -
```

## Database Password Rotation

### PostgreSQL Password Rotation

```bash

# 1. Connect to primary database

kubectl exec -it postgresql-0 -n default -- psql -U postgres

# 2. Generate new password

NEW_PASS=$(openssl rand -base64 32)

# 3. Update password in PostgreSQL

ALTER USER sovereign WITH PASSWORD '$NEW_PASS';

# 4. Update Kubernetes secret

kubectl create secret generic postgresql-credentials \
  --from-literal=username=sovereign \
  --from-literal=password="[REDACTED]" \
  -n default --dry-run=client -o yaml | kubectl apply -f -

# 5. Rolling restart of all services (to pick up new password)

for deploy in vault trust-graph firewall compliance incident-reflex negotiation verifiable-reality; do
  kubectl rollout restart deployment/$deploy -n default
  kubectl rollout status deployment/$deploy -n default --timeout=5m
done

# 6. Verify connectivity

kubectl exec -n default deploy/sovereign-vault -- \
  psql -h postgresql -U sovereign -d sovereign_db -c "SELECT 1;"
```

## API Key Rotation

### External API Keys (e.g., AWS, Third-party services)

```bash

# 1. Create new API key in external service console

# 2. Update Kubernetes secret

kubectl create secret generic external-api-keys \
  --from-literal=aws-key-id="AKIAIOSFODNN7EXAMPLE" \
  --from-literal=aws-secret-key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  -n default --dry-run=client -o yaml | kubectl apply -f -

# 3. Restart affected services

kubectl rollout restart deployment/service-using-api -n default

# 4. Revoke old key in external service console (after verification)

```

### Internal API Keys (Microservice-to-Microservice)

```bash

# Generate new API key

NEW_API_KEY=$(uuidgen)

# Update in Vault service

kubectl exec -n default deploy/sovereign-vault -- \
  python3 -c "
from app.auth import create_api_key
key = create_api_key(service='trust-graph', permissions=['read', 'write'])
print(f'New API Key: {key}')
"

# Distribute to services via secrets

kubectl create secret generic trust-graph-api-key \
  --from-literal=key="$NEW_API_KEY" \
  -n default --dry-run=client -o yaml | kubectl apply -f -
```

## TLS Certificate Rotation

### Automated (cert-manager)

```bash

# Check certificate status

kubectl get certificate -n default

# Force renewal (if needed)

kubectl delete secret sovereign-tls-cert -n default

# cert-manager will automatically recreate

# Verify renewal

kubectl get certificate sovereign-tls -n default -o yaml | grep "Not After"
```

### Manual Certificate Rotation

```bash

# 1. Generate new certificate

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout sovereign-new.key -out sovereign-new.crt \
  -subj "/CN=*.sovereign.ai/O=Sovereign"

# 2. Create new TLS secret

kubectl create secret tls sovereign-tls-cert-new \
  --cert=sovereign-new.crt \
  --key=sovereign-new.key \
  -n default

# 3. Update Ingress

kubectl patch ingress sovereign-ingress -n default --type=json \
  -p='[{"op": "replace", "path": "/spec/tls/0/secretName", "value": "sovereign-tls-cert-new"}]'

# 4. Verify new certificate is served

echo | openssl s_client -connect sovereign.ai:443 2>/dev/null | openssl x509 -noout -dates

# 5. Delete old certificate (after 24h)

kubectl delete secret sovereign-tls-cert -n default
```

## Vault Root Token Rotation

⚠️ **CRITICAL**: This requires significant downtime planning.

```bash

# 1. Generate new root token

vault operator generate-root -init

# Follow interactive prompts

# 2. Update stored root token

kubectl create secret generic vault-root-token \
  --from-literal=token="$NEW_ROOT_TOKEN" \
  -n observability --dry-run=client -o yaml | kubectl apply -f -

# 3. Update all services using Vault

# (Service-specific procedure)

# 4. Verify Vault access

vault login $NEW_ROOT_TOKEN
vault status
```

## Redis Password Rotation

```bash

# 1. Connect to Redis

kubectl exec -it redis-0 -n default -- redis-cli

# 2. Set new password

CONFIG SET requirepass "new-secure-password"
CONFIG REWRITE

# 3. Update Kubernetes secret

kubectl create secret generic redis-credentials \
  --from-literal=password="[REDACTED]" \
  -n default --dry-run=client -o yaml | kubectl apply -f -

# 4. Restart services using Redis

kubectl rollout restart deployment/auth-service -n default
```

## Rollback Procedures

### If rotation causes service disruption:

```bash

# 1. Revert to old secret

kubectl apply -f secret-backup.yaml

# 2. Restart affected services

kubectl rollout restart deployment/<service> -n default

# 3. Investigate root cause

kubectl logs -n default deploy/<service> --tail=100
```

## Verification Checklist

After any secret rotation:

- [ ] All services healthy (`kubectl get pods -n default`)
- [ ] All readiness probes passing
- [ ] E2E tests pass (`pytest tests/e2e/test_smoke.py`)
- [ ] No authentication errors in logs
- [ ] Monitoring shows normal traffic patterns
- [ ] Old secrets documented and deleted (after grace period)

## Communication Template

```
🔐 Secret Rotation - [SECRET_TYPE]

Scheduled Time: [DATE TIME UTC]
Expected Duration: [X minutes]
Impact: [None / Brief disruption / Service restart required]

Services affected:

- Service 1
- Service 2

Actions:

- [timestamp] Rotation initiated
- [timestamp] New secret deployed
- [timestamp] Services restarted
- [timestamp] Validation complete

Status: ✅ Complete / ⚠️ In Progress / ❌ Failed
```

## Automation Scripts

### Automated JWT Rotation Cron

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: jwt-key-rotation
  namespace: default
spec:
  schedule: "0 2 1 */3 *"  # Every 3 months at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:

          - name: rotate-jwt
            image: sovereign/key-rotator:latest
            command: ["/rotate-jwt.sh"]
            env:
            - name: NOTIFY_SLACK
              value: "true"
          restartPolicy: OnFailure

```

## Emergency Contacts

- **Security Team**: security@sovereign.ai
- **DBA Team**: dba@sovereign.ai
- **On-Call**: +1-XXX-XXX-XXXX

## Related Runbooks

- [Incident Response](../playbooks/INCIDENT_RESPONSE.md)
- [Database Failover](./database-failover-runbook.md)

---
**Last Updated**: 2025-01-15  
**Owner**: Team Charlie - SRE  
**Review Cycle**: Quarterly
