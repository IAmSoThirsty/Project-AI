# 🔄 SECRET ROTATION GUIDE

**Sovereign Governance Substrate - Production Procedures**

Version: 1.0  
Last Updated: 2026-04-11  
Classification: **CONFIDENTIAL**

---

## 📋 OVERVIEW

This guide provides detailed procedures for rotating all types of secrets in the Sovereign Governance Substrate. Follow these procedures for both scheduled rotations and emergency responses to security incidents.

---

## 🚨 EMERGENCY ROTATION

**Trigger:** Secret compromise detected or suspected

### Quick Response (< 5 minutes)

```bash
#!/bin/bash

# Emergency rotation script

# 1. IMMEDIATE: Rotate the exposed secret

python rotate_sovereign_keypair.py --emergency

# 2. IMMEDIATE: Revoke old secret from all systems

vault kv metadata delete secret/project-ai/signing/sovereign-keypair

# 3. IMMEDIATE: Restart affected services

kubectl rollout restart deployment/governance-service -n project-ai

# 4. VERIFY: Services operational

kubectl get pods -n project-ai -w

# 5. AUDIT: Check for unauthorized access

vault audit read -format=json | \
  jq '.[] | select(.request.path == "secret/project-ai/signing/sovereign-keypair")'

# 6. NOTIFY: Security team

send_security_alert.sh --level CRITICAL --secret sovereign-keypair
```

### Emergency Checklist

- [ ] **T+0min:** Identify compromised secret
- [ ] **T+5min:** Rotate secret using appropriate script
- [ ] **T+10min:** Verify all services restarted successfully
- [ ] **T+15min:** Confirm no authentication errors in logs
- [ ] **T+30min:** Complete forensic analysis of exposure
- [ ] **T+1hour:** Document incident and lessons learned
- [ ] **T+24hour:** Review and update security procedures

---

## 🔑 SOVEREIGN KEYPAIR ROTATION

**Keypair:** Ed25519 signing key for governance operations  
**Schedule:** Every 180 days or on compromise  
**Downtime:** Zero (dual-key period)

### Prerequisites

- [ ] Vault access (admin role)
- [ ] Governance service access
- [ ] Backup of current keypair
- [ ] Notification system configured

### Procedure

#### Step 1: Generate New Keypair

```bash

# Run the rotation script

python rotate_sovereign_keypair.py

# OR manually:

python3 << 'EOF'
from cryptography.hazmat.primitives.asymmetric import ed25519
from datetime import datetime
import json

# Generate new keypair

private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# Export keys

private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

keypair = {
    "private_key": private_bytes.hex(),
    "public_key": public_bytes.hex(),
    "algorithm": "Ed25519",
    "created_at": datetime.now().isoformat(),
    "version": "v2"
}

print(json.dumps(keypair, indent=2))
EOF
```

#### Step 2: Store New Keypair in Vault

```bash

# Store in Vault (NOT in repository!)

vault kv put secret/project-ai/signing/sovereign-keypair \
  private_key="<hex_private_key>" \
  public_key="<hex_public_key>" \
  algorithm="Ed25519" \
  created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  version="v2"

# Verify storage

vault kv get secret/project-ai/signing/sovereign-keypair
```

#### Step 3: Dual-Key Period (24 hours)

**Purpose:** Allow services to migrate without downtime

```bash

# Keep old keypair as version N-1

vault kv put secret/project-ai/signing/sovereign-keypair-old \
  private_key="<old_hex_private_key>" \
  public_key="<old_hex_public_key>" \
  algorithm="Ed25519" \
  valid_until="$(date -u -d '+24 hours' +%Y-%m-%dT%H:%M:%SZ)"

# Services should accept BOTH public keys during this period

```

#### Step 4: Update Services

```bash

# Governance service configuration

kubectl set env deployment/governance-service \
  SOVEREIGN_KEYPAIR_VERSION=v2 \
  -n project-ai

# Rollout new configuration

kubectl rollout restart deployment/governance-service -n project-ai

# Wait for rollout

kubectl rollout status deployment/governance-service -n project-ai

# Verify service health

kubectl exec -it deployment/governance-service -n project-ai -- \
  python -c "from governance.core import verify_keypair; verify_keypair()"
```

#### Step 5: Revoke Old Public Key

**After 24-hour dual-key period:**

```bash

# Remove old keypair from Vault

vault kv delete secret/project-ai/signing/sovereign-keypair-old

# Update trust stores to reject old public key

update_trust_stores.sh --remove-key <old_public_key>

# Verify old key rejected

test_signature_with_old_key.sh  # Should fail
```

#### Step 6: Audit & Document

```bash

# Log rotation event

vault audit read -format=json | \
  jq '.[] | select(.request.path == "secret/project-ai/signing/sovereign-keypair")'

# Update governance documentation

update_governance_docs.sh --keypair-version v2

# Notify stakeholders

send_notification.sh --type keypair-rotated --recipients governance-team
```

### Verification Checklist

- [ ] New keypair generated successfully
- [ ] New keypair stored in Vault (NOT in repo)
- [ ] Services restarted with new keypair
- [ ] All signature operations succeed
- [ ] Old public key rejected
- [ ] No errors in logs
- [ ] Audit trail complete
- [ ] Documentation updated

---

## 🔐 API KEY ROTATION

**Keys:** OpenAI, DeepSeek, HuggingFace, etc.  
**Schedule:** Every 90 days  
**Downtime:** Zero (dual-key period)

### Procedure

#### Step 1: Generate New API Key

**For external services (e.g., OpenAI):**

1. Login to provider dashboard
2. Generate new API key
3. Note key value (copy once!)
4. Keep old key active for 24 hours

#### Step 2: Store in Vault

```bash

# Store new key

vault kv put secret/project-ai/api-keys/openai \
  api_key="[REDACTED]" \
  created_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  expires_at="$(date -u -d '+90 days' +%Y-%m-%dT%H:%M:%SZ)" \
  version="v2"

# Keep old key temporarily

vault kv put secret/project-ai/api-keys/openai-old \
  api_key="[REDACTED]" \
  valid_until="$(date -u -d '+24 hours' +%Y-%m-%dT%H:%M:%SZ)"
```

#### Step 3: Update Services

```bash

# If using ExternalSecrets, it auto-syncs within refreshInterval

# Force immediate sync:

kubectl annotate externalsecret project-ai-secrets \
  force-sync="$(date +%s)" \
  -n project-ai

# Verify secret updated

kubectl get secret project-ai-secrets -o jsonpath='{.data.OPENAI_API_KEY}' | base64 -d

# Restart services to pick up new key

kubectl rollout restart deployment/ai-service -n project-ai
```

#### Step 4: Revoke Old Key

**After 24 hours:**

```bash

# Revoke old key from provider

# (OpenAI: https://platform.openai.com/api-keys)

# Remove from Vault

vault kv delete secret/project-ai/api-keys/openai-old

# Verify old key no longer works

test_api_key.sh sk-old-key-value  # Should return 401 Unauthorized
```

### Automated Rotation

**Using SecretsManager:**

```python
from src.app.core.secrets_manager import get_secrets_manager
from datetime import datetime, timedelta

secrets = get_secrets_manager()

# Check if rotation needed

secrets_needing_rotation = secrets.get_secrets_needing_rotation()

for secret_key in secrets_needing_rotation:
    if secret_key.startswith("openai_api_key"):

        # Notify admin to generate new key

        notify_admin(f"Please generate new OpenAI API key for rotation")
        
        # Mark for rotation

        secrets.mark_for_rotation(secret_key)
```

---

## 🔒 ENCRYPTION KEY ROTATION

**Keys:** FERNET_KEY, JWT_SECRET_KEY  
**Schedule:** Every 90 days  
**Downtime:** Zero (dual-key period)

### FERNET_KEY Rotation

#### Step 1: Generate New Key

```python
from cryptography.fernet import Fernet

# Generate new Fernet key

new_key = Fernet.generate_key()
print(f"New FERNET_KEY: {new_key.decode()}")
```

#### Step 2: Multi-Key Configuration

**Fernet supports multiple keys for rotation:**

```python
from cryptography.fernet import Fernet, MultiFernet

# Old key (can still decrypt)

old_key = Fernet(b'old-key-here')

# New key (encrypts new data)

new_key = Fernet(b'new-key-here')

# Create MultiFernet with new key first

fernet = MultiFernet([new_key, old_key])

# New encryptions use new_key

# Old ciphertexts still decryptable with old_key

encrypted = fernet.encrypt(b"data")
decrypted = fernet.decrypt(encrypted)
```

#### Step 3: Re-encrypt Existing Data (Optional)

**For critical data, re-encrypt with new key:**

```python
from src.app.core.secrets_manager import EncryptedFileSecretStore
from pathlib import Path

# Initialize with old key

old_store = EncryptedFileSecretStore(
    Path("var/secrets.enc"),
    encryption_key=OLD_FERNET_KEY
)

# Read all secrets

secrets = old_store.list_secrets()

# Initialize new store with new key

new_store = EncryptedFileSecretStore(
    Path("var/secrets_new.enc"),
    encryption_key=NEW_FERNET_KEY
)

# Migrate secrets

for secret_key in secrets:
    secret = old_store.get_secret(secret_key)
    new_store.set_secret(secret_key, secret)

# Atomic swap

Path("var/secrets.enc").rename("var/secrets.enc.old")
Path("var/secrets_new.enc").rename("var/secrets.enc")
```

### JWT_SECRET_KEY Rotation

**⚠️ WARNING:** Rotating JWT secret invalidates all existing tokens!

#### Step 1: Dual-Key Period

```python

# config.py

import os

# Support both old and new keys during transition

JWT_SECRET_KEYS = [
    os.getenv("JWT_SECRET_KEY"),      # New key (signs new tokens)
    os.getenv("JWT_SECRET_KEY_OLD"),  # Old key (validates existing tokens)
]

# jwt_utils.py

import jwt

def verify_token(token):

    # Try each key

    for secret_key in JWT_SECRET_KEYS:
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.InvalidSignatureError:
            continue
    raise jwt.InvalidTokenError("Invalid token")
```

#### Step 2: Notify Users

```bash

# Send email to users

send_notification.sh \
  --type jwt-rotation \
  --message "JWT tokens will expire in 24 hours. Please re-login." \
  --recipients all-users
```

#### Step 3: Grace Period

- **Day 0:** Deploy dual-key configuration
- **Day 1-7:** Both old and new tokens valid
- **Day 7:** Remove old key, invalidate old tokens

#### Step 4: Revoke Old Key

```bash

# Remove old JWT secret

vault kv delete secret/project-ai/encryption/jwt-secret-old

# Update environment (remove JWT_SECRET_KEY_OLD)

kubectl set env deployment/api-service \
  JWT_SECRET_KEY_OLD- \
  -n project-ai
```

---

## 💾 DATABASE CREDENTIAL ROTATION

**Credentials:** PostgreSQL, Redis, MongoDB  
**Schedule:** Every 30 days (or dynamic)  
**Downtime:** Zero (connection pool rotation)

### PostgreSQL Dynamic Credentials

**Using Vault Database Secrets Engine:**

#### Step 1: Configure Vault Database Engine

```bash

# Enable database secrets engine

vault secrets enable database

# Configure PostgreSQL connection

vault write database/config/projectai \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:[REDACTED]@postgres:5432/projectai?sslmode=require" \
  username="vault-admin" \
  password="[REDACTED]"

# Create role for read-only access

vault write database/roles/readonly \
  db_name=projectai \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT ON projectai.* TO '{{name}}'@'%';" \
  default_ttl="24h" \
  max_ttl="72h"

# Create role for read-write access

vault write database/roles/readwrite \
  db_name=projectai \
  creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; GRANT SELECT, INSERT, UPDATE, DELETE ON projectai.* TO '{{name}}'@'%';" \
  default_ttl="24h" \
  max_ttl="72h"
```

#### Step 2: Service Uses Dynamic Credentials

```python
import hvac
import psycopg2

# Get Vault client

client = hvac.Client(url='http://vault:8200', token=VAULT_TOKEN)

# Request database credentials (created on-demand)

db_creds = client.read('database/creds/readwrite')

username = db_creds['data']['username']  # e.g., v-token-readwrite-AbCdEfG
password = db_creds['data']['password']  # e.g., A1b2C3d4E5f6G7h8

# Connect with dynamic credentials

conn = psycopg2.connect(
    host="postgres",
    database="projectai",
    user=username,
    password=password
)

# Credentials auto-expire after TTL (24h)

# Next request gets new credentials

```

### Static Credential Rotation (Legacy)

**For databases not using Vault dynamic secrets:**

#### Step 1: Create New User with New Password

```sql
-- Connect as admin
psql -U postgres -d projectai

-- Create new user
CREATE USER projectai_v2 WITH PASSWORD 'new-secure-password';

-- Grant same permissions as old user
GRANT ALL PRIVILEGES ON DATABASE projectai TO projectai_v2;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO projectai_v2;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO projectai_v2;
```

#### Step 2: Update Vault with New Credentials

```bash
vault kv put secret/project-ai/database \
  username="projectai_v2" \
  password="[REDACTED]" \
  host="postgres.project-ai.svc.cluster.local" \
  port="5432" \
  database="projectai"
```

#### Step 3: Restart Services (Zero-Downtime)

```bash

# Rolling restart (one pod at a time)

kubectl rollout restart deployment/api-service -n project-ai

# Monitor rollout

kubectl rollout status deployment/api-service -n project-ai

# Verify connections using new credentials

kubectl logs -f deployment/api-service -n project-ai | grep "Database connected"
```

#### Step 4: Revoke Old User

**After 24 hours (ensure all pods restarted):**

```sql
-- Verify no active connections from old user
SELECT * FROM pg_stat_activity WHERE usename = 'projectai_v1';

-- Revoke old user
REVOKE ALL PRIVILEGES ON DATABASE projectai FROM projectai_v1;
DROP USER projectai_v1;
```

---

## 🔏 HSM-BACKED SIGNING KEY ROTATION

**Keys:** Sovereign keypair, Triumvirate keys  
**Location:** Hardware Security Module or Vault Transit Engine  
**Schedule:** Every 180 days

### Using Vault Transit Engine

#### Step 1: Create New Key in Transit Engine

```bash

# Create new signing key

vault write transit/keys/sovereign-signing-v2 type=ed25519

# Get public key

vault read transit/keys/sovereign-signing-v2

# Output:

# {

#   "type": "ed25519",

#   "public_key": "...",

#   "creation_time": "2026-04-11T10:00:00Z"

# }

```

#### Step 2: Update Services to Use New Key

```python
import hvac
import base64

# Get Vault client

client = hvac.Client(url='http://vault:8200', token=VAULT_TOKEN)

# Sign with new key

message = b"Governance action: approve proposal"
message_b64 = base64.b64encode(message).decode()

response = client.write(
    'transit/sign/sovereign-signing-v2',
    input=message_b64,
    hash_algorithm='sha2-256'
)

signature = response['data']['signature']

# signature format: vault:v1:<base64_signature>

```

#### Step 3: Dual-Key Period

```python

# Accept signatures from both keys during transition

VALID_SIGNING_KEYS = [
    "sovereign-signing-v2",  # New key
    "sovereign-signing-v1",  # Old key (grace period)
]

def verify_signature(message, signature):
    for key_name in VALID_SIGNING_KEYS:
        try:
            result = client.write(
                f'transit/verify/{key_name}',
                input=base64.b64encode(message).decode(),
                signature=signature
            )
            if result['data']['valid']:
                return True
        except:
            continue
    return False
```

#### Step 4: Revoke Old Key

```bash

# After grace period, disable old key

vault write transit/keys/sovereign-signing-v1/config \
  deletion_allowed=true

# Delete old key

vault delete transit/keys/sovereign-signing-v1
```

---

## 📅 SCHEDULED ROTATION CALENDAR

### Rotation Matrix

| Secret Type | Frequency | Next Rotation | Owner |
|-------------|-----------|---------------|-------|
| **Sovereign Keypair** | 180 days | 2026-10-11 | Governance Team |
| **API Keys** | 90 days | 2026-07-11 | Platform Team |
| **Encryption Keys** | 90 days | 2026-07-11 | Security Team |
| **Database Creds** | 30 days | 2026-05-11 | Database Team |
| **JWT Secrets** | 90 days | 2026-07-11 | API Team |
| **Redis Passwords** | 90 days | 2026-07-11 | Platform Team |
| **Service Certs** | 30 days | 2026-05-11 | Security Team |

### Automated Rotation Schedule

**Cron job configuration:**

```yaml

# k8s/cronjobs/secret-rotation.yaml

apiVersion: batch/v1
kind: CronJob
metadata:
  name: secret-rotation-check
  namespace: project-ai
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: secret-rotator
          containers:

          - name: rotator
            image: project-ai/secret-rotator:latest
            command:
            - python
            - /app/scripts/check_and_rotate_secrets.py
            env:
            - name: VAULT_ADDR
              value: "http://vault:8200"
            - name: VAULT_TOKEN
              valueFrom:
                secretKeyRef:
                  name: vault-token
                  key: token
          restartPolicy: OnFailure

```

**Rotation script:**

```python
#!/usr/bin/env python3

# scripts/check_and_rotate_secrets.py

from src.app.core.secrets_manager import get_secrets_manager
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    secrets = get_secrets_manager()
    
    # Check secrets needing rotation

    secrets_to_rotate = secrets.get_secrets_needing_rotation()
    
    if not secrets_to_rotate:
        logger.info("No secrets need rotation")
        return
    
    logger.info(f"Found {len(secrets_to_rotate)} secrets needing rotation")
    
    for secret_key in secrets_to_rotate:
        logger.info(f"Rotating {secret_key}...")
        
        # Generate new value based on secret type

        new_value = generate_secret_value(secret_key)
        
        # Rotate

        secrets.rotate_secret(secret_key, new_value)
        
        # Notify stakeholders

        notify_rotation(secret_key)
        
        logger.info(f"Successfully rotated {secret_key}")

if __name__ == "__main__":
    main()
```

---

## 🔔 NOTIFICATIONS & ALERTS

### Rotation Notifications

**Before rotation (7 days):**
```bash
send_notification.sh \
  --type upcoming-rotation \
  --secret openai_api_key \
  --date "2026-04-18" \
  --recipients platform-team
```

**During rotation:**
```bash
send_notification.sh \
  --type rotation-in-progress \
  --secret openai_api_key \
  --status "dual-key-period" \
  --recipients platform-team,security-team
```

**After rotation:**
```bash
send_notification.sh \
  --type rotation-complete \
  --secret openai_api_key \
  --old-key-revoked true \
  --recipients platform-team,security-team
```

### Alert Rules

**Prometheus alerts:**

```yaml

# alerts/secret-rotation.yaml

groups:

- name: secret_rotation
  rules:
  
  # Alert when secret is >80% of max age

  - alert: SecretNearingExpiration
    expr: |
      (time() - vault_secret_creation_time) / 
      vault_secret_max_ttl > 0.8
    for: 1h
    annotations:
      summary: "Secret {{ $labels.secret_path }} needs rotation soon"
      description: "Secret is {{ $value | humanizePercentage }} of max age"
  
  # Alert when rotation fails

  - alert: SecretRotationFailed
    expr: |
      vault_secret_rotation_failures_total > 0
    for: 5m
    annotations:
      summary: "Secret rotation failed for {{ $labels.secret_path }}"
      description: "Check logs for rotation errors"
  
  # Alert when old secret still in use after grace period

  - alert: OldSecretStillInUse
    expr: |
      vault_secret_old_key_access_total > 0 and
      (time() - vault_secret_rotation_time) > 172800  # 48 hours
    annotations:
      summary: "Old secret {{ $labels.secret_path }} still being accessed"
      description: "Service may not have picked up new secret"

```

---

## 📝 ROTATION CHECKLIST TEMPLATES

### General Secret Rotation

```markdown

## [SECRET_NAME] Rotation - [DATE]

**Type:** [API Key / Encryption Key / Database Cred / Signing Key]
**Scheduled:** [Yes/No]
**Emergency:** [Yes/No]
**Reason:** [Scheduled rotation / Compromise / Other]

### Pre-Rotation

- [ ] Backup current secret value
- [ ] Identify all services using this secret
- [ ] Notify stakeholders (if scheduled)
- [ ] Verify rollback procedure

### Rotation

- [ ] Generate new secret
- [ ] Store new secret in Vault
- [ ] Begin dual-key period (if applicable)
- [ ] Update service configurations
- [ ] Restart affected services
- [ ] Verify services operational

### Post-Rotation

- [ ] Monitor logs for errors (24 hours)
- [ ] Revoke old secret
- [ ] Update documentation
- [ ] Audit trail review
- [ ] Mark rotation complete

### Verification

- [ ] All services using new secret
- [ ] No authentication errors
- [ ] Old secret no longer accessible
- [ ] Metrics/monitoring still working
- [ ] Audit log entries created

**Rotated by:** [NAME]
**Completion time:** [TIMESTAMP]
**Issues encountered:** [NONE / DESCRIPTION]
```

---

## 🛠️ TROUBLESHOOTING

### Service Won't Start After Rotation

**Symptoms:**

- Service crashlooping
- Authentication errors in logs
- 401/403 responses

**Solution:**
```bash

# 1. Check if service has new secret

kubectl exec -it pod/service-xxx -- env | grep SECRET_KEY

# 2. Force secret sync (if using ExternalSecrets)

kubectl annotate externalsecret project-ai-secrets force-sync="$(date +%s)"

# 3. Verify Vault contains new secret

vault kv get secret/project-ai/api-keys/openai

# 4. Check service account has Vault permissions

kubectl auth can-i get secret project-ai-secrets --as=system:serviceaccount:project-ai:service-name

# 5. Rollback if necessary

vault kv rollback -version=N-1 secret/project-ai/api-keys/openai
kubectl rollout undo deployment/service-name
```

### Old Secret Still Being Used

**Symptoms:**

- Metrics show old key access after grace period
- Multiple authentication methods working

**Solution:**
```bash

# 1. Identify services still using old secret

vault audit read | jq '.[] | select(.request.path contains "old")'

# 2. Check pod restart times

kubectl get pods -o wide

# 3. Force restart pods that haven't rotated

kubectl delete pod <old-pod-name>

# 4. Verify new secret in use

kubectl logs <pod-name> | grep "Using secret version"
```

### Rotation Script Fails

**Symptoms:**

- Rotation script exits with error
- Partial rotation completed

**Solution:**
```bash

# 1. Check Vault connectivity

vault status

# 2. Verify permissions

vault token lookup

# 3. Check rotation state

vault kv get secret/project-ai/rotation-state

# 4. Manual completion

python rotate_sovereign_keypair.py --resume --state-file /tmp/rotation-state.json
```

---

## 📚 REFERENCES

- **Vault Documentation:** https://www.vaultproject.io/docs
- **External Secrets Operator:** https://external-secrets.io
- **Cryptography Library:** https://cryptography.io
- **Kubernetes Secrets:** https://kubernetes.io/docs/concepts/configuration/secret/

---

**Document Status:** ACTIVE  
**Owner:** Security Team  
**Review Schedule:** Quarterly  
**Next Review:** 2026-07-11

**Version History:**

- v1.0 (2026-04-11): Initial release
