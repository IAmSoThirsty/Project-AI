---
title: "INCIDENT: Environment Secret Containment"
id: incident-env-containment-2026-05-18
type: incident-note
status: active
created: 2026-05-18
owner: governance-security
severity: high
---

## Incident Summary

A local runtime environment file was present at repository root (`.env`).

Tracking proof command executed (approved):

- `git ls-files --error-unmatch .env`

Result:

- `.env` is **not currently tracked** by git in this branch.

## Secret Names in Scope (names only; no values)

- `JWT_SECRET_KEY`
- `OPENAI_API_KEY`
- `HUGGINGFACE_API_KEY`

## Containment Actions Completed

1. Added denylist patterns to `t:\Project-AI-main\.gitignore`.
2. Added denylist patterns to `t:\Project-AI-main\.dockerignore`.
3. Preserved `!.env.example` to keep safe templates shareable.
4. Opened deployment freeze artifact (see `.github/DEPLOY_FREEZE_PRE_DOCKER_2026-05-18.md`).

## Required Follow-up

- Rotate all secrets in scope as if exposure may have occurred.
- Deletion of a local file alone is **insufficient** for secret response assurance.
- Prevent future commits with denylist + CI secret scanning fail-closed gates.
- Any history rewrite requires explicit written approval and separate execution plan.

## If `.env` Becomes Tracked Later

Prepared command (DO NOT RUN without explicit approval):

- `git rm --cached .env`

## Current Policy State

- Release/deploy/cloud-build/image-push operations are frozen until:
  1. CI fail-closed repair is completed, and
  2. runtime/deployment canonicalization is completed.
