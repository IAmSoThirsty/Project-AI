# Reviewer Guide

This guide helps reviewers evaluate the verified POC branch without getting
lost in the full Project-AI monorepo.

## Review Order

1. Start with `README.md`.
2. Read `docs/VERIFIED_POC_MANIFEST.md`.
3. Run the focused verification commands.
4. Inspect `src/app/personal_agent.py`.
5. Inspect `tests/test_personal_agent.py`.
6. Inspect `scripts/verify_poc_surface.py`.

## Commands

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest tests\test_personal_agent.py -q
py -3.12 .\scripts\verify_poc_surface.py
py -3.12 .\scripts\personal_agent.py scribe status
```

## What Counts As Verified

A feature is verified for this branch only when it has:

- A manifest entry.
- A local command.
- A recorded result.
- A clear scope boundary.
- A test where practical.

## What Does Not Count As Verified

- Historical completion claims.
- Architecture documents without local commands.
- Generated logs without reproduction steps.
- Production wording without evidence.
- Full-monorepo health claims.

## Current Accepted Surface

- Caregiver Scribe.
- Obsidian-backed scribe maps.
- Personal-agent CLI access.
- Branch-face verification.

## Review Notes

The repo contains many older documents with ambitious language. On this branch,
the root README and verified manifest are authoritative for public claims.

If an older document conflicts with the manifest, use the manifest.
