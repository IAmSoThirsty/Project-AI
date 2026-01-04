# Secret Purge Runbook (Git history rewrite)

This repository previously committed `.env` containing secrets. Removing the file going forward is not enough; you must **rewrite git history** to purge those blobs.

## Prerequisites

- Rotate leaked credentials **first** (OpenAI key, SMTP password, Fernet key).
- Ensure you have admin rights to force-push to the repo.
- Everyone with clones must re-clone after history rewrite.

## Step-by-step

### 1) Ensure working tree is clean

```bash
git status --porcelain
```

### 2) Install `git-filter-repo` (recommended)

One of:

```bash
pip install git-filter-repo
```

or

```powershell
choco install git-filter-repo
```

### 3) Run the purge script

From repo root:

```powershell
powershell -ExecutionPolicy Bypass -File tools/purge_git_secrets.ps1
```

### 4) Force-push rewritten history

```bash
git push --force --all origin
git push --force --tags origin
```

### 5) Post-purge verification

- Confirm `.env` is not in history:

```bash
git log --all --full-history -- .env
```

- Confirm no blob remains by searching for known tokens (best-effort):

```bash
git rev-list --all | git grep -n "OPENAI_API_KEY" || true
```

## Important notes

- History rewrite is disruptive. Any open PRs may need to be recreated.
- After force-push, all collaborators must:
  - re-clone, or
  - hard reset to the new history and prune old references.
