# ⚡ Quick Action Checklist

**URGENT**: Follow these steps in order to remediate the secret exposure.

---

## ✅ Phase 1: IMMEDIATE (Next 1 Hour)

### Step 1: Revoke OpenAI API Key
```bash
# 1. Visit: https://platform.openai.com/api-keys
# 2. Find and REVOKE key: sk-proj-cFQpst...
# 3. Click "Create new secret key"
# 4. Copy the new key
```

### Step 2: Change Gmail Credentials
```bash
# 1. Visit: https://myaccount.google.com/security
# 2. Change password for: ProjectAiDevs@gmail.com
# 3. Visit: https://myaccount.google.com/apppasswords
# 4. REVOKE all existing app passwords
# 5. Generate NEW app password
# 6. Copy the new app password
```

### Step 3: Rotate Fernet Key
```bash
# Generate new Fernet key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output
```

### Step 4: Update Local .env
```bash
# Edit .env file with new credentials
nano .env  # or your preferred editor

# Update these lines:
OPENAI_API_KEY=<paste new OpenAI key>
SMTP_USERNAME=ProjectAiDevs@gmail.com
SMTP_PASSWORD=<paste new app password>
FERNET_KEY=<paste new Fernet key>

# DO NOT COMMIT THIS FILE!
```

### Step 5: Test Application
```bash
# Verify app works with new credentials
python -m src.app.main
```

**✅ Phase 1 Complete**: Credentials rotated, immediate threat mitigated

---

## ⚠️ Phase 2: URGENT (Next 24 Hours)

### Step 6: Clean Git History
```bash
# Install git-filter-repo
pip install git-filter-repo

# Remove secrets from git history
git filter-repo --path .env --path .vs --invert-paths --force

# Force push cleaned history
git push --force --all origin
git push --force --tags origin
```

**Alternative**: Use provided scripts
```bash
# Windows
./tools/purge_git_secrets.ps1

# Linux/macOS
./tools/purge_git_secrets.sh
```

### Step 7: Notify Team
Send this message to all contributors:
```
⚠️ URGENT: Git history has been rewritten to remove exposed secrets.

ACTION REQUIRED:
1. Delete your local repository clone
2. Re-clone from GitHub
3. Set up .env with NEW credentials (do not reuse old ones)
4. Run: python tools/verify_secrets_removed.py

The following credentials were rotated:
- OpenAI API key
- SMTP credentials
- Fernet encryption key

Questions? See CREDENTIAL_ROTATION_REQUIRED.md
```

**✅ Phase 2 Complete**: Git history cleaned, team notified

---

## 🔍 Phase 3: VERIFY (Next 72 Hours)

### Step 8: Run Verification
```bash
# Run automated verification
python tools/verify_secrets_removed.py

# Expected output:
# ✅ ALL CHECKS PASSED
```

### Step 9: Manual Checks
```bash
# Verify .env not tracked
git ls-files | grep .env
# Should only show: .env.example

# Verify .env not in history
git log --all --oneline -- .env
# Should be empty (no output)

# Verify .vs not in history
git log --all --oneline -- .vs
# Should be empty (no output)
```

### Step 10: Monitor for Abuse
```bash
# Check OpenAI usage
# Visit: https://platform.openai.com/usage

# Check Gmail activity
# Visit: https://myaccount.google.com/notifications

# Review for:
# - Unusual API calls
# - Unexpected charges
# - Login attempts from unknown locations
```

**✅ Phase 3 Complete**: Cleanup verified, monitoring active

---

## 📊 Progress Tracker

| Task | Status | Deadline |
|------|--------|----------|
| Revoke OpenAI key | ⏳ | 1 hour |
| Change Gmail password | ⏳ | 1 hour |
| Rotate Fernet key | ⏳ | 1 hour |
| Update .env file | ⏳ | 1 hour |
| Test application | ⏳ | 1 hour |
| Clean git history | ⏳ | 24 hours |
| Force push | ⏳ | 24 hours |
| Notify team | ⏳ | 24 hours |
| Run verification | ⏳ | 72 hours |
| Monitor for abuse | ⏳ | 72 hours |

---

## 🆘 Need Help?

**Quick References:**

- Full details: `CREDENTIAL_ROTATION_REQUIRED.md`
- Summary: `SECRET_REMEDIATION_SUMMARY.md`
- Best practices: `docs/security/SECRET_MANAGEMENT.md`

**Verification Failed?**
```bash
# Show what's wrong
python tools/verify_secrets_removed.py

# Check specific issue
git log --all --oneline -- .env  # Shows if .env in history
git ls-files | grep .env         # Shows tracked .env files
```

**Can't Access Accounts?**
- OpenAI: Account recovery at https://platform.openai.com
- Gmail: Account recovery at https://accounts.google.com/recovery

---

## ⚡ One-Line Commands

**Quick Status Check:**
```bash
python tools/verify_secrets_removed.py && echo "✅ All good!" || echo "❌ Issues found"
```

**Complete Cleanup:**
```bash
pip install git-filter-repo && \
git filter-repo --path .env --path .vs --invert-paths --force && \
git push --force --all origin && \
echo "✅ History cleaned"
```

---

**Remember:** 
- ✅ Code changes are COMPLETE (already in PR)
- ⏳ Credential rotation is YOUR responsibility
- ⏳ Git cleanup is YOUR responsibility
- 📞 Ask for help if needed!

---

**Last Updated**: 2026-01-09  
**Questions?** See full documentation in `CREDENTIAL_ROTATION_REQUIRED.md`
