# 🔐 Secret Management Guide

**Last Updated**: January 2026  
**Status**: Required Reading for All Contributors

---

## 🚨 Critical Security Rules

### NEVER commit secrets to version control

**What counts as a secret?**

- API keys (OpenAI, Hugging Face, AWS, etc.)
- Passwords and authentication tokens
- Encryption keys (Fernet, JWT, etc.)
- Database credentials
- Private keys (.pem, .key files)
- OAuth client secrets
- SMTP passwords
- Any credential that grants access to resources

---

## ✅ Proper Secret Management

### 1. Use Environment Variables

**Always load secrets from environment variables:**

```python
import os
from dotenv import load_dotenv

# Load from .env file (not committed to git)
load_dotenv()

# Get secrets from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FERNET_KEY = os.getenv("FERNET_KEY")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Validate required secrets are set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set in environment")
```

### 2. Use .env Files Correctly

**Project structure:**
```
.env              # Real secrets - IN .gitignore - NEVER commit
.env.example      # Placeholder values - OK to commit
```

**Example .env.example (safe to commit):**
```bash
# OpenAI API key - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Fernet encryption key - Generate with:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY=YOUR_BASE64_KEY_HERE

# SMTP credentials (optional)
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-app-password-here
```

**Example .env (NEVER commit):**
```bash
OPENAI_API_KEY=sk-proj-abc123...real_key_here
FERNET_KEY=real_base64_key_here==
SMTP_USERNAME=real-email@gmail.com
SMTP_PASSWORD=real_password_here
```

### 3. Verify .gitignore

**Ensure .gitignore contains:**
```gitignore
# Secrets and credentials - NEVER commit
.env
.env.local
.env.*.local
*.key
*.pem
*.p12
secrets.json
credentials.json
```

**Verify it's working:**
```bash
# This should show "nothing to commit" for .env file
git status .env
```

---

## 🔄 Credential Rotation

### When to Rotate

**IMMEDIATE rotation required:**

- Credentials accidentally committed to git
- Credentials shared in chat/email/documentation
- Suspected credential compromise
- Employee/contractor with access leaves team

**Regular rotation schedule:**

- Every 90 days (recommended)
- After security audits
- After major version releases

### How to Rotate

#### 1. OpenAI API Key

```bash
# 1. Go to https://platform.openai.com/api-keys
# 2. Find and REVOKE the old key
# 3. Create NEW key with appropriate permissions
# 4. Update .env file
OPENAI_API_KEY=sk-proj-NEW_KEY_HERE
# 5. Test application
python -m src.app.main
```

#### 2. Fernet Encryption Key

```bash
# ⚠️ WARNING: Rotating Fernet key makes old encrypted data unreadable!

# Step 1: Generate new key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Step 2: Decrypt existing data with OLD key (before rotation)
# This varies by application - check which files use Fernet:
# - location_history.json.enc
# - Any other encrypted files

# Step 3: Update FERNET_KEY in .env with NEW key

# Step 4: Re-encrypt all data with NEW key

# Step 5: Securely delete backup files with old encryption
```

#### 3. SMTP/Email Credentials

```bash
# For Gmail:
# 1. Go to https://myaccount.google.com/apppasswords
# 2. REVOKE old app password
# 3. Generate NEW app password
# 4. Update .env file
SMTP_PASSWORD=NEW_PASSWORD_HERE
```

#### 4. Hugging Face Token

```bash
# 1. Go to https://huggingface.co/settings/tokens
# 2. DELETE old token
# 3. Create NEW token with appropriate permissions
# 4. Update .env file
HUGGINGFACE_API_KEY=hf_NEW_TOKEN_HERE
```

---

## 🔍 Secret Scanning Tools

### 1. Bandit (Python Security Linter)

```bash
# Install
pip install bandit

# Scan for hardcoded secrets
bandit -r src/ tests/ -f json -o bandit_report.json

# Check specific patterns
bandit -r . -x .venv,node_modules --severity-level medium
```

### 2. TruffleHog (Git History Scanner)

```bash
# Install
pip install trufflehog

# Scan entire git history
trufflehog git file://. --only-verified

# Scan specific branch
trufflehog git file://. --branch main
```

### 3. git-secrets (Prevent Commits)

```bash
# Install (macOS)
brew install git-secrets

# Install (Linux)
git clone https://github.com/awslabs/git-secrets
cd git-secrets
sudo make install

# Set up for repository
cd /path/to/Project-AI
git secrets --install
git secrets --register-aws
git secrets --add 'sk-[a-zA-Z0-9]{32,}'  # OpenAI keys
git secrets --add 'hf_[a-zA-Z0-9]{32,}'  # Hugging Face tokens
```

### 4. Project-Specific Scanner

```bash
# Use built-in secret scanner
python tools/secret_scan.py

# This checks for:
# - OpenAI API keys (sk-proj-* pattern)
# - Hugging Face tokens (hf_* pattern)
# - AWS access keys (AKIA* pattern)
# - SMTP passwords
# - Generic secrets in config files
```

---

## 🛡️ Pre-commit Hooks

### Install Pre-commit Framework

```bash
# Install pre-commit
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Example .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
  
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.0
    hooks:
      - id: trufflehog
        args: ['filesystem', '--directory', '.', '--fail']
```

---

## 🚨 If Secrets Are Exposed

### Immediate Actions (Within 1 Hour)

1. **Revoke exposed credentials immediately**
   - Don't wait for git history cleanup
   - Assume credentials are compromised

1. **Generate new credentials**
   - Use platform-specific rotation procedures above

1. **Update application configuration**
   - Update .env with new credentials
   - Test application works

1. **Notify team**
   - Alert all developers
   - Document in security log

### Git History Cleanup (Within 24 Hours)

1. **Use BFG Repo-Cleaner or git-filter-repo**

   ```bash
   # Using git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --path .env --invert-paths --force
   
   # Or use provided scripts:
   # Windows PowerShell:
   ./tools/purge_git_secrets.ps1
   
   # Linux/macOS/WSL:
   ./tools/purge_git_secrets.sh
   ```

1. **Force push cleaned history**

   ```bash
   git push --force --all origin
   git push --force --tags origin
   ```

1. **Notify all contributors**
   - Everyone must re-clone repository
   - Old clones have compromised history

### Review and Prevent (Within 1 Week)

1. **Review access logs**
   - OpenAI usage logs
   - Email account activity
   - AWS CloudTrail (if applicable)

1. **Add secret scanning to CI/CD**

1. **Security training for team**
   - Review this document
   - Understand proper secret management

---

## 📋 Security Checklist

### For New Contributors

- [ ] Read this document completely
- [ ] Copy .env.example to .env
- [ ] Generate YOUR OWN credentials (never use examples)
- [ ] Verify .env is in .gitignore
- [ ] Install pre-commit hooks
- [ ] Test that secrets load correctly

### For Code Reviews

- [ ] No hardcoded secrets in code
- [ ] All secrets loaded from environment
- [ ] No secrets in documentation (use placeholders)
- [ ] No secrets in test files
- [ ] No secrets in comments
- [ ] Updated .env.example if new secrets added

### For Releases

- [ ] Run secret scanning tools
- [ ] Verify no secrets in repository
- [ ] All credentials rotated recently (<90 days)
- [ ] Production uses secrets manager (not .env files)
- [ ] Security audit passed

---

## 🏢 Production Deployment

### Use Secrets Managers

**DO NOT use .env files in production!**

**Recommended solutions:**

1. **AWS Secrets Manager**

   ```python
   import boto3
   
   def get_secret(secret_name):
       client = boto3.client('secretsmanager', region_name='us-east-1')
       response = client.get_secret_value(SecretId=secret_name)
       return json.loads(response['SecretString'])
   
   secrets = get_secret('project-ai/production')
   OPENAI_API_KEY = secrets['OPENAI_API_KEY']
   ```

1. **Azure Key Vault**

   ```python
   from azure.keyvault.secrets import SecretClient
   from azure.identity import DefaultAzureCredential
   
   credential = DefaultAzureCredential()
   client = SecretClient(vault_url="https://myvault.vault.azure.net", credential=credential)
   
   OPENAI_API_KEY = client.get_secret("OPENAI-API-KEY").value
   ```

1. **Google Cloud Secret Manager**

   ```python
   from google.cloud import secretmanager
   
   client = secretmanager.SecretManagerServiceClient()
   name = f"projects/my-project/secrets/openai-api-key/versions/latest"
   response = client.access_secret_version(request={"name": name})
   
   OPENAI_API_KEY = response.payload.data.decode('UTF-8')
   ```

---

## 📊 Secret Inventory

### Current Secrets in Project

| Secret | Location | Rotation Frequency | Owner |
|--------|----------|-------------------|-------|
| OPENAI_API_KEY | .env | 90 days | Dev Team |
| HUGGINGFACE_API_KEY | .env | 90 days | Dev Team |
| FERNET_KEY | .env | 180 days* | Security Team |
| SMTP_USERNAME | .env | As needed | Dev Team |
| SMTP_PASSWORD | .env | 90 days | Dev Team |
| COMMAND_OVERRIDE_PASSWORD | Set in app | As needed | Admin |

*Fernet key rotation requires data migration

---

## 🎓 Training Resources

### Recommended Reading

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning Documentation](https://docs.github.com/en/code-security/secret-scanning)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

### Common Mistakes to Avoid

❌ **DON'T:**

- Commit .env files
- Hardcode API keys in code
- Share credentials via email/chat
- Use example credentials from documentation
- Commit secrets in comments
- Store secrets in test files
- Use same credentials across environments

✅ **DO:**

- Use environment variables
- Rotate credentials regularly
- Use secrets managers in production
- Generate unique credentials per environment
- Use strong, random credentials
- Enable 2FA on all accounts
- Monitor for secret exposure

---

## 📞 Questions or Issues?

- **Security concerns**: Contact security team immediately
- **Need credentials**: Request from team lead (never share existing ones)
- **Credential exposure**: Follow "If Secrets Are Exposed" procedure above

---

**Remember**: When in doubt, treat it as a secret. It's better to be overly cautious than to expose credentials.

---

*Last reviewed: January 2026*  
*Next review: April 2026*
