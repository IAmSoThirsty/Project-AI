# 🚨 URGENT: Credential Rotation Required

**Date**: January 9, 2026  
**Severity**: CRITICAL  
**Status**: ACTION REQUIRED

---

## Overview

Real credentials were discovered in multiple files that were previously committed to git history:

1. **`.env` file** - Commit `6ff0c3e5bae216c2f12da69c0f9d8c07a61d1bf9` (2026-01-09)
2. **`.vs/` directory** - Visual Studio/Copilot session files containing secret references

Even though these files are now removed from git tracking, the credentials exist in the repository history and must be considered **COMPROMISED**.

---

## Exposed Credentials

The following credentials were found in git history and **MUST BE ROTATED IMMEDIATELY**:

### 1. OpenAI API Key ⚠️
- **Key Pattern**: `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`
- **Action Required**: 
  1. Go to https://platform.openai.com/api-keys
  2. **REVOKE** this key immediately
  3. Generate a **NEW** API key
  4. Update your local `.env` file with the new key
  5. Monitor OpenAI usage logs for any unauthorized activity

### 2. SMTP Credentials (Gmail) ⚠️
- **Username**: `ProjectAiDevs@gmail.com`
- **Password**: `R9609936!`
- **Action Required**:
  1. Change the Gmail account password immediately at https://myaccount.google.com/security
  2. Revoke all app passwords at https://myaccount.google.com/apppasswords
  3. Generate a **NEW** app password
  4. Update your local `.env` file with new credentials
  5. Enable 2-factor authentication if not already enabled
  6. Review account activity for unauthorized access

### 3. Fernet Encryption Key ⚠️
- **Key**: `Qqyl2vCYY7W4AKuE-DmQLmL7IgXguMis_lFalqlliEc=`
- **Action Required**:
  1. Generate a new Fernet key:
     ```bash
     python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
     ```
  2. **BEFORE** updating `.env`, decrypt any encrypted files with the OLD key
  3. Update `.env` with the NEW Fernet key
  4. Re-encrypt all files with the NEW key
  5. Securely delete old encrypted backups

---

## Immediate Actions (Complete Within 1 Hour)

- [ ] **REVOKE** OpenAI API key (critical - prevents API abuse)
- [ ] **CHANGE** Gmail password and revoke app passwords
- [ ] **GENERATE** new credentials for all three services
- [ ] **UPDATE** local `.env` file with new credentials (DO NOT commit)
- [ ] **TEST** application with new credentials
- [ ] **NOTIFY** all team members of credential compromise

---

## Git History Cleanup (Complete Within 24 Hours)

⚠️ **WARNING**: This rewrites git history and requires coordination with all contributors.

### Option 1: Using git-filter-repo (Recommended)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove .env and .vs/ from entire git history
git filter-repo --path .env --path .vs --invert-paths --force

# Force push to all branches
git push --force --all origin
git push --force --tags origin
```

### Option 2: Using BFG Repo-Cleaner

```bash
# Download BFG from https://rtyley.github.io/bfg-repo-cleaner/
# Remove .env and .vs/ from history
java -jar bfg.jar --delete-files .env
java -jar bfg.jar --delete-folders .vs

# Clean reflog and force push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force --all origin
git push --force --tags origin
```

### Option 3: Using Provided Scripts

**Windows PowerShell:**
```powershell
./tools/purge_git_secrets.ps1
```

**Linux/macOS/WSL:**
```bash
./tools/purge_git_secrets.sh
```

### After History Rewrite

1. **Notify all contributors** that git history has been rewritten
2. **All team members MUST**:
   - Delete their local repository clones
   - Re-clone from GitHub
   - Reconfigure their local `.env` with NEW credentials
3. **Verify** `.env` no longer appears in git history:
   ```bash
   git log --all --full-history -- .env
   # Should return empty
   ```

---

## Verification Steps

After completing credential rotation and git cleanup:

- [ ] Verify OpenAI API key is revoked in platform dashboard
- [ ] Verify Gmail app password is revoked
- [ ] Verify application works with new credentials
- [ ] Verify `.env` is not in git tracking: `git ls-files | grep .env` (should be empty)
- [ ] Verify `.vs/` is not in git tracking: `git ls-files | grep .vs` (should be empty)
- [ ] Verify `.env` is not in git history: `git log --all -- .env` (should be empty)
- [ ] Verify `.vs/` is not in git history: `git log --all -- .vs` (should be empty)
- [ ] Run secret scanner to verify no secrets remain:
  ```bash
  python tools/secret_scan.py
  ```

---

## Prevention Measures (Already Implemented)

The following changes have been made to prevent future credential exposure:

✅ `.env` removed from git tracking  
✅ `.vs/` IDE directory removed from git tracking  
✅ `.gitignore` strengthened with additional patterns (secrets, IDE files, key files)  
✅ `.env` file sanitized (removed real credentials)  
✅ Documentation examples updated to use clearly fake credentials  
✅ Instructions added to `.env.example` warning against committing secrets  
✅ Visual Studio IDE patterns added to .gitignore

---

## Resources

- [SECRET_MANAGEMENT.md](docs/security/SECRET_MANAGEMENT.md) - Comprehensive secret management guide
- [SECRET_PURGE_RUNBOOK.md](docs/security/SECRET_PURGE_RUNBOOK.md) - Git history cleanup procedures
- [SECURITY.md](SECURITY.md) - Security policy and reporting

---

## Timeline

| Action | Deadline | Status |
|--------|----------|--------|
| Revoke OpenAI key | Within 1 hour | ❌ PENDING |
| Change Gmail credentials | Within 1 hour | ❌ PENDING |
| Rotate Fernet key | Within 1 hour | ❌ PENDING |
| Update local `.env` | Within 1 hour | ❌ PENDING |
| Test application | Within 2 hours | ❌ PENDING |
| Notify team | Within 2 hours | ❌ PENDING |
| Clean git history | Within 24 hours | ❌ PENDING |
| Force push cleaned repo | Within 24 hours | ❌ PENDING |
| Team re-clones repo | Within 48 hours | ❌ PENDING |
| Final verification | Within 72 hours | ❌ PENDING |

---

## Questions or Issues?

- **Security concerns**: Review [docs/security/SECRET_MANAGEMENT.md](docs/security/SECRET_MANAGEMENT.md)
- **Git cleanup help**: Review [docs/security/SECRET_PURGE_RUNBOOK.md](docs/security/SECRET_PURGE_RUNBOOK.md)
- **Need assistance**: Create an issue with the `security` label

---

**Last Updated**: 2026-01-09  
**Next Review**: After credential rotation completion
