# Secret Exposure Incident — 2026-05-18

## Status: OPEN — Rotation Required

## Summary

The `.env` file at repository root contained plaintext secret values for:

| Variable | Risk | Rotation Owner |
|----------|------|----------------|
| `JWT_SECRET_KEY` | Auth bypass if leaked | Repository owner |
| `OPENAI_API_KEY` | Billing abuse, data exfiltration | Repository owner |
| `HUGGINGFACE_API_KEY` | Model abuse, billing | Repository owner |

The file was confirmed **not tracked by git** (`git ls-files --error-unmatch .env` returned exit code 1). However, the absence of a `.gitignore` denylist prior to this date means the file *could* have been committed in earlier history.

## Remediation Applied (2026-05-18)

1. **`.gitignore` denylist** — Added comprehensive secret-file patterns (`.env`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.crt`, `id_rsa`, `id_ed25519`, `secrets/`, `private/`, `credentials*`, `token*`, `*.sqlite`, `*.db`).
2. **`.dockerignore` denylist** — Mirrored the same patterns to prevent secrets from entering Docker build context.
3. **`.env` values replaced** — Placeholder values set; secrets must be regenerated.

## Required Manual Steps

> **These cannot be automated and must be completed by the repository owner.**

### 1. Rotate All Secrets

```bash
# JWT — generate a cryptographically strong key (≥32 chars)
python -c "import secrets; print(secrets.token_urlsafe(48))"

# OpenAI — regenerate at https://platform.openai.com/api-keys
# Hugging Face — regenerate at https://huggingface.co/settings/tokens
```

Update `.env` with the new values. **Do not reuse the old values.**

### 2. Audit Git History (Optional but Recommended)

If there is any chance `.env` was committed previously:

```bash
git log --all --diff-filter=A -- .env
```

If results appear, a history rewrite (`git filter-repo`) is required. **Do not execute without explicit approval** — this is a destructive, force-push operation.

### 3. Revoke Old Keys

Even if the keys were placeholders, treat them as compromised:
- Revoke old OpenAI API key in the dashboard.
- Revoke old Hugging Face token in settings.
- Any service that accepted the old `JWT_SECRET_KEY` must invalidate existing JWTs.

## Verification Checklist

- [ ] `JWT_SECRET_KEY` rotated and ≥32 characters
- [ ] `OPENAI_API_KEY` rotated in provider dashboard
- [ ] `HUGGINGFACE_API_KEY` rotated in provider dashboard
- [ ] Old keys revoked at source
- [ ] `git log --all --diff-filter=A -- .env` returns no results (or history rewrite approved)
- [ ] Application starts successfully with new keys
- [ ] This file updated to status **CLOSED** after all items complete
