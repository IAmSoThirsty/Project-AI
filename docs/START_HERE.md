# Start Here

Welcome to Project-AI's verified proof-of-concept branch.

This branch is intentionally narrower than the full repository. It exists to
make the current working surface understandable, reproducible, and professional.

## First Five Minutes

1. Read the root `README.md`.
2. Run the verification commands.
3. Open the verified manifest.
4. Inspect the Caregiver Scribe docs.
5. Ignore broad historical claims unless they are backed by the manifest.

## What To Run First

From the repository root:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest tests\test_personal_agent.py -q
py -3.12 .\scripts\verify_poc_surface.py
```

Then check the scribe status:

```powershell
py -3.12 .\scripts\personal_agent.py scribe status
```

## What To Read First

- `docs/VERIFIED_POC_MANIFEST.md`
- `docs/PERSONAL_AGENT.md`
- `docs/REVIEWER_GUIDE.md`
- `docs/POC_BRANCH_POLICY.md`

## How To Think About The Repo

Project-AI is a large research codebase. Some areas are working, some are
partial, and some are historical or aspirational. This branch does not ask a
newcomer to sort that out alone.

The rule is simple:

If a capability is not in the verified manifest, treat it as experimental.

## Current Center Of Gravity

The current verified center is the Caregiver Scribe:

- It reads the Obsidian vault structure.
- It indexes Project-AI files as navigable metadata.
- It writes maps and manifests back into the vault.
- It stays bounded to scribe/navigation work.

This is the foundation for later local-agent work.
