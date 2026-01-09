# 🚨 URGENT: Credential Rotation Required

**Date Issued**: January 9, 2026  
**Priority**: CRITICAL  
**Action Required**: IMMEDIATE

---

## ⚠️ Security Incident Summary

Real secrets were accidentally committed to the repository in the `.env` file and exposed in git history.

### Exposed Credentials

The following credentials were found in commit history and **MUST BE ROTATED IMMEDIATELY**:

1. **OpenAI API Key**: `sk-proj-cFQpst...` (full key was exposed)
2. **SMTP Email Account**: `ProjectAiDevs@gmail.com`
3. **SMTP Password**: `R9609936!`
4. **Fernet Encryption Key**: `Qqyl2vCYY7W4AKuE-DmQLmL7IgXguMis_lFalqlliEc=`

### Immediate Actions Taken

- ✅ `.env` file removed from git tracking
- ✅ `.env` file contents replaced with template (no real secrets)
- ✅ `.gitignore` updated to prevent future commits
- ✅ Documentation updated to use proper placeholders
- ✅ Security scan report reviewed and addressed

---

## 🔄 Required Credential Rotation Steps

### 1. OpenAI API Key (CRITICAL)

**⚠️ This key MUST be rotated immediately to prevent unauthorized API usage.**

```bash
# Step 1: Go to OpenAI API Keys page
https://platform.openai.com/api-keys

# Step 2: Find the exposed key (starts with sk-proj-cFQpst...)
# Step 3: Click "Revoke" to invalidate it immediately

# Step 4: Create a NEW API key with appropriate permissions
# Step 5: Update your local .env file with the NEW key
OPENAI_API_KEY=<your-new-key-here>

# Step 6: Test the application to ensure it works
python -m src.app.main
```

### 2. SMTP Email Account (CRITICAL)

**⚠️ The Gmail account password was exposed. Change it immediately.**

```bash
# Step 1: Go to Gmail security settings
https://myaccount.google.com/security

# Step 2: Change the account password for ProjectAiDevs@gmail.com

# Step 3: Revoke all existing app passwords
https://myaccount.google.com/apppasswords

# Step 4: Generate a NEW app-specific password for Project-AI

# Step 5: Update your local .env file
SMTP_USERNAME=ProjectAiDevs@gmail.com
SMTP_PASSWORD=<new-app-password-here>

# Step 6: Check for unauthorized access
https://myaccount.google.com/notifications
```

### 3. Fernet Encryption Key (HIGH PRIORITY)

**⚠️ The encryption key was exposed. Data encrypted with this key is compromised.**

```bash
# Step 1: Generate a new Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Step 2: Decrypt existing encrypted data with OLD key (if any exists)
# The following files may be encrypted:
# - data/location/history.json.enc
# - Any other *.enc files

# Step 3: Update FERNET_KEY in .env with NEW key
FERNET_KEY=<your-new-base64-key-here>

# Step 4: Re-encrypt all data with the NEW key

# Step 5: Securely delete any backup files encrypted with old key
```

---

## 🔒 Git History Cleanup (REQUIRED)

**⚠️ IMPORTANT**: Even though we've removed the `.env` file from tracking, the secrets still exist in git history. Anyone who clones the repository can see them in old commits.

### Option 1: Using BFG Repo-Cleaner (Recommended)

```bash
# 1. Install BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Clone a fresh copy of the repository
git clone --mirror https://github.com/IAmSoThirsty/Project-AI.git

# 3. Run BFG to remove .env from all history
java -jar bfg.jar --delete-files .env Project-AI.git

# 4. Clean up
cd Project-AI.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (requires admin permissions)
git push --force
```

### Option 2: Using git-filter-repo

```bash
# 1. Install git-filter-repo
pip install git-filter-repo

# 2. Clone a fresh copy
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 3. Remove .env from all history
git filter-repo --path .env --invert-paths --force

# 4. Force push (requires admin permissions)
git push --force --all origin
git push --force --tags origin
```

### After History Cleanup

**All team members MUST:**
1. Delete their local repository clones
2. Re-clone the repository from GitHub
3. Set up new credentials in their local `.env` file

---

## 📋 Verification Checklist

After completing the rotation:

- [ ] OpenAI API key rotated and tested
- [ ] SMTP account password changed
- [ ] SMTP app password regenerated
- [ ] Fernet encryption key regenerated
- [ ] All encrypted data re-encrypted with new key
- [ ] Git history cleaned (using BFG or git-filter-repo)
- [ ] Force push completed successfully
- [ ] Team notified to re-clone repository
- [ ] Application tested with new credentials
- [ ] No unauthorized API usage detected
- [ ] No unauthorized email access detected

---

## 🔍 Monitor for Unauthorized Usage

### OpenAI API

Check for suspicious activity:
```bash
# Go to OpenAI usage dashboard
https://platform.openai.com/usage

# Look for:
# - Unexpected API calls
# - Usage from unknown IP addresses
# - Unusual spending patterns
```

### Gmail Account

Check for unauthorized access:
```bash
# Review recent security activity
https://myaccount.google.com/notifications

# Check for:
# - Login from unknown locations
# - Suspicious sent emails
# - Modified account settings
```

---

## 📞 Incident Response

If you detect unauthorized usage:

1. **Immediately revoke** the compromised credentials
2. **Document** the unauthorized activity (screenshots, logs)
3. **Report** to the security team
4. **Review** audit logs for data access
5. **Assess** potential data breach impact
6. **Notify** affected users if necessary

---

## 🎓 Prevention for Future

### For All Contributors

1. **NEVER** commit `.env` files
2. **ALWAYS** use `.env.example` for templates
3. **VERIFY** `.gitignore` includes `.env`
4. **USE** pre-commit hooks for secret scanning
5. **ROTATE** credentials every 90 days

### Pre-commit Hook Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## 📚 Additional Resources

- [Secret Management Guide](docs/security/SECRET_MANAGEMENT.md)
- [Secret Purge Runbook](docs/security/SECRET_PURGE_RUNBOOK.md)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

---

**Remember**: Treat all exposed credentials as compromised. It's better to rotate unnecessarily than to leave a security vulnerability.

---

*Last Updated: January 9, 2026*
