---
title: "Secret Purge Runbook (Git History Rewrite)"
id: "secret-purge-runbook"
type: "runbook"
version: "1.0.0"
created_date: "2026-01-15"
updated_date: "2026-02-08"
status: "active"
author:
  name: "Security Operations Team"
  email: "secops@project-ai.org"
category: "security"
tags:
  - "area:security"
  - "area:incident-response"
  - "type:runbook"
  - "component:git-filter-repo"
  - "component:history-rewrite"
  - "audience:security-engineer"
  - "audience:devops-engineer"
  - "priority:p0-critical"
  - "special:destructive-operation"
technologies:
  - "git-filter-repo"
  - "Git History Rewrite"
  - "PowerShell"
  - "Secret Rotation"
difficulty: "expert"
estimated_time: "PT60M"
prerequisites:
  - "Admin rights to repository"
  - "git-filter-repo installed"
  - "All secrets already rotated"
  - "Coordination with team for re-cloning"
summary: "Comprehensive runbook for purging secrets from git history using git-filter-repo including rotation, history rewrite, force-push, and verification steps."
scope: "Complete git history purge workflow: prerequisites verification, git-filter-repo execution, force-push rewritten history, team coordination, and post-purge verification"
classification: "confidential"
threat_level: "critical"
triggers:
  - "Accidental .env commit"
  - "API key in git history"
  - "Credential leak detected"
  - "Secret scanner alert"
mitigations:
  - "[[SECRET_ROTATION]]"
  - "[[GIT_HISTORY_REWRITE]]"
  - "[[FORCE_PUSH]]"
  - "[[VERIFICATION_STEPS]]"
defends_against:
  - "Leaked credentials in git history"
  - "Historical secret exposure"
  - "Committed .env files"
  - "API keys in old commits"
compliance:
  - "Incident Response Best Practices"
  - "Secret Leak Remediation"
  - "GDPR Right to Erasure (if PII)"
stakeholders:
  - security-team   - security-operations   - compliance-team
last_verified: 2026-04-20
cvss_score: "N/A - Incident Response Runbook"
cwe_ids:
  - "CWE-798: Use of Hard-coded Credentials"
  - "CWE-312: Cleartext Storage of Sensitive Information"
  - "CWE-522: Insufficiently Protected Credentials"
related_docs:
  - "secret-management"
  - "incident-playbook"
  - "security-framework"
review_status:
  reviewed: true
  reviewers: ["security-team", "devops-team"]
  review_date: "2026-02-08"
  approved: true
audience:
  - "security-engineers"
  - "devops-engineers"
  - "repository-admins"
escalation_path: "Security Lead → CTO"
last_tested: "2026-01-15"
---

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

