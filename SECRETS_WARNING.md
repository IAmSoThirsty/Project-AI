# 🚨 CRITICAL: Secret Management Warning

## ⚠️ NEVER COMMIT SECRETS TO GIT

This repository uses environment variables for secret management. **NEVER** commit actual secrets to version control.

### What are secrets?
- API keys (OpenAI, Hugging Face, AWS, etc.)
- Passwords and authentication tokens
- Encryption keys (Fernet, JWT, etc.)
- Database credentials
- SMTP passwords
- Any credential that grants access to resources

### Proper Usage

1. **Copy `.env.example` to `.env`**
   ```bash
   cp .env.example .env
   ```

2. **Fill in YOUR OWN credentials in `.env`**
   - Generate your own API keys
   - Never use example values from documentation
   - Never share your `.env` file

3. **Verify `.env` is NOT tracked by git**
   ```bash
   git status .env
   # Should show: "nothing to commit" or file not listed
   ```

### ✅ Safe Practices

- ✅ Use `.env` files for local development (NOT committed)
- ✅ Use environment variables in production
- ✅ Use GitHub Secrets for CI/CD
- ✅ Rotate credentials every 90 days
- ✅ Use secrets managers in production (AWS Secrets Manager, Azure Key Vault, etc.)

### ❌ Dangerous Practices

- ❌ Committing `.env` files
- ❌ Hardcoding API keys in source code
- ❌ Sharing credentials via email/chat
- ❌ Using example credentials from documentation
- ❌ Storing secrets in comments

### 🔥 If Secrets Are Exposed

**IMMEDIATE ACTIONS** (within 1 hour):

1. **REVOKE** exposed credentials immediately
   - OpenAI: https://platform.openai.com/api-keys
   - Hugging Face: https://huggingface.co/settings/tokens
   - Gmail App Passwords: https://myaccount.google.com/apppasswords

2. **GENERATE** new credentials

3. **UPDATE** your local `.env` file with new credentials

4. **NOTIFY** the repository maintainers

5. **FOLLOW** the git history cleanup procedure (see `docs/security/SECRET_PURGE_RUNBOOK.md`)

### 📚 Full Documentation

For complete guidance, see:
- **Secret Management Guide**: `docs/security/SECRET_MANAGEMENT.md`
- **Secret Purge Runbook**: `docs/security/SECRET_PURGE_RUNBOOK.md`
- **Security Policy**: `SECURITY.md`

### 🔍 Pre-commit Checks

Install pre-commit hooks to catch secrets before they're committed:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

**Remember**: When in doubt, treat it as a secret. Better safe than compromised.

**Last Updated**: January 2026
