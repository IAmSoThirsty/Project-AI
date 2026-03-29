<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / SECURITY.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / SECURITY.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Security Best Practices for TTP

## Secrets Management

### ⚠️ Critical: Never Commit Secrets to Git

**The following files are .gitignored and should NEVER be committed:**
- `*.env` files
- `k8s/**/secrets.yaml` (only .example files are committed)
- Files containing actual credentials

### Development Environment

For local development, create a `.env` file:

```bash
# Create .env file (this is .gitignored)
cat > api/.env << 'EOF'
DATABASE_URL=postgresql://ttp:devpassword@localhost:5432/ttp_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
AWS_ACCESS_KEY_ID=your-dev-key
AWS_SECRET_ACCESS_KEY=your-dev-secret
EOF
```

### Production Environment

#### Option 1: Kubernetes Secrets (Basic)

```bash
# Generate secure values
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Create Kubernetes secret
kubectl create secret generic ttp-secrets \
  --from-literal=DATABASE_URL="postgresql://ttp:${DB_PASSWORD}@prod-db:5432/ttp" \
  --from-literal=SECRET_KEY="${SECRET_KEY}" \
  -n ttp-prod
```

#### Option 2: AWS Secrets Manager (Recommended)

```bash
# Store database credentials in AWS Secrets Manager
aws secretsmanager create-secret \
  --name ttp/prod/database \
  --description "TTP Production Database Credentials" \
  --secret-string '{
    "username": "ttp",
    "password": "'"$(openssl rand -base64 32)"'",
    "host": "ttp-prod-db.xxxxx.rds.amazonaws.com",
    "port": 5432,
    "database": "ttp"
  }' \
  --region us-east-1

# Store JWT secret
aws secretsmanager create-secret \
  --name ttp/prod/jwt-secret \
  --secret-string "$(openssl rand -hex 32)" \
  --region us-east-1
```

Then use [External Secrets Operator](https://external-secrets.io/) to sync to Kubernetes:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: ttp-secrets
  namespace: ttp-prod
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: ttp-secrets
    creationPolicy: Owner
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: ttp/prod/database
        property: url
    - secretKey: SECRET_KEY
      remoteRef:
        key: ttp/prod/jwt-secret
```

#### Option 3: HashiCorp Vault

```bash
# Enable KV secrets engine
vault secrets enable -path=ttp kv-v2

# Store secrets
vault kv put ttp/prod/database \
  url="postgresql://ttp:password@host:5432/ttp"

vault kv put ttp/prod/jwt \
  secret_key="$(openssl rand -hex 32)"
```

## Credential Rotation

### Database Password Rotation

```bash
# 1. Update password in database
psql -h your-db-host -U postgres -c "ALTER USER ttp PASSWORD 'new-password';"

# 2. Update Kubernetes secret
kubectl create secret generic ttp-secrets \
  --from-literal=DATABASE_URL="postgresql://ttp:new-password@host:5432/ttp" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Rolling restart of pods
kubectl rollout restart deployment/ttp-api -n ttp-prod
```

### JWT Secret Rotation

```bash
# Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# Update secret
kubectl patch secret ttp-secrets -n ttp-prod \
  -p '{"stringData":{"SECRET_KEY":"'${NEW_SECRET}'"}}'

# Rolling restart
kubectl rollout restart deployment/ttp-api -n ttp-prod
```

## Security Scanning

### Pre-commit Hooks

Install git-secrets to prevent committing credentials:

```bash
# Install git-secrets
brew install git-secrets  # macOS
# or
apt-get install git-secrets  # Ubuntu

# Configure for repository
cd /path/to/TTP
git secrets --install
git secrets --register-aws
git secrets --add 'password\s*=\s*["\']?[^"\']+["\']?'
git secrets --add 'secret[_-]?key\s*=\s*["\']?[^"\']+["\']?'
```

### GitGuardian Integration

This repository is monitored by GitGuardian. If secrets are detected:

1. **Immediately rotate the exposed credential**
2. **Remove from git history:**
   ```bash
   # Use BFG Repo-Cleaner
   git clone --mirror https://github.com/IAmSoThirsty/TTP.git
   bfg --replace-text passwords.txt TTP.git
   cd TTP.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push --force
   ```

3. **Update the secret in all environments**

## IAM Best Practices

### Use IAM Roles for Service Accounts (IRSA)

Instead of storing AWS credentials in Kubernetes secrets:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ttp-api
  namespace: ttp-prod
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/ttp-api-role
```

### Least Privilege Principle

Grant only required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::ttp-texture-assets/*"
    }
  ]
}
```

## Encryption

### Data at Rest
- Database: Enable RDS encryption
- S3: Enable bucket encryption (AES-256 or KMS)
- Kubernetes: Enable encryption of secrets at rest

### Data in Transit
- Use TLS 1.3 for all connections
- Enable SSL for PostgreSQL
- Use HTTPS for all API calls

## Audit Logging

Enable audit logging for secret access:

```yaml
# In API deployment
env:
  - name: AUDIT_LOG_SECRETS
    value: "true"
```

Monitor secret access:
```bash
# View audit logs
kubectl logs -n ttp-prod deployment/ttp-api | grep "secret_accessed"
```

## Security Checklist

- [ ] No secrets in git repository
- [ ] .gitignore includes secret files
- [ ] Pre-commit hooks installed
- [ ] Secrets stored in external secret manager
- [ ] Regular credential rotation scheduled
- [ ] IAM roles used instead of access keys
- [ ] TLS enabled for all connections
- [ ] Audit logging enabled
- [ ] Security scanning in CI/CD
- [ ] Secrets encrypted at rest in Kubernetes

## References

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [External Secrets Operator](https://external-secrets.io/)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [GitGuardian Best Practices](https://www.gitguardian.com/secrets-detection)
- [Kubernetes Secrets Management](https://kubernetes.io/docs/concepts/configuration/secret/)
