# Verified POC Manifest

This manifest is the source of truth for the GitHub-facing branch surface.

Each accepted proof of concept must include local evidence. Claims without
commands and results do not belong in the branch README.

## Verification Date

- Date: 2026-04-16
- Machine: local Windows workstation with Python 3.12
- Repository path: repository root
- Branch prepared as: `github/verified-poc-face`

## Accepted POCs

### POC-001: Caregiver Scribe

Status: Verified

Purpose:

The personal agent's first active role is Caregiver Scribe. It learns the
terrain by indexing the Obsidian vault first, then Project-AI files, and writes
navigable maps back into the vault.

Verified commands:

```powershell
py -3.12 .\scripts\personal_agent.py scribe status
py -3.12 .\scripts\personal_agent.py scribe absorb-vault
py -3.12 .\scripts\personal_agent.py scribe learn-repo
```

Recorded result:

```text
Vault absorbed
records: 130

Project-AI files indexed
records: 6175
```

Generated outputs:

- `wiki/_Scribe/Project-AI/00 Scribe Home.md`
- `wiki/_Scribe/Project-AI/Vault Navigation Map.md`
- `wiki/_Scribe/Project-AI/vault_manifest.jsonl`
- `wiki/_Scribe/Project-AI/Project-AI File Index.md`
- `wiki/_Scribe/Project-AI/repo_file_manifest.jsonl`

Scope boundary:

The scribe records file metadata, paths, headings, links, tags, symbols, hashes
when practical, and text signals. It does not claim semantic mastery of all file
contents and does not execute arbitrary repo tasks.

### POC-002: Personal-Agent CLI Access

Status: Verified

Purpose:

Project-AI exposes the caregiver-scribe through both a direct script and the
Project-AI Typer CLI package path.

Verified commands:

```powershell
py -3.12 .\scripts\personal_agent.py scribe status
$env:PYTHONPATH = "src"
py -3.12 -m app.cli personal scribe-status
```

Recorded result:

```text
vault_path: T:\Project-AI-main\wiki
vault_exists: True
is_obsidian_vault: True
scribe_root_exists: True
```

Scope boundary:

This verifies command access and scribe status reporting. It does not verify a
local LLM backend, voice interface, browser, shell execution, or autonomous task
loop.

### POC-003: Scribe Regression Tests

Status: Verified

Purpose:

Focused tests validate memory storage, forgetting, training export, prompt
context, vault absorption, and repo indexing behavior.

Verified command:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest tests\test_personal_agent.py -q
```

Recorded result:

```text
tests/test_personal_agent.py .... 4 passed
```

Scope boundary:

These are focused tests for the caregiver-scribe integration. They do not certify
the full monorepo.

### POC-004: Branch-Face Verification

Status: Verified

Purpose:

The GitHub-facing README should stay aligned with verified evidence instead of
drifting back into broad or aspirational claims.

Verified command:

```powershell
py -3.12 .\scripts\verify_poc_surface.py
```

Recorded result:

```text
Verified POC branch surface checks passed.
```

Scope boundary:

This verifies that required branch-face documents and phrases are present. It
does not prove every historical document in the repository is current.

## Excluded From The Branch Face

The following are not accepted POCs on this branch unless later verified with
local evidence:

- Production readiness of the entire Project-AI monorepo.
- AGI or autonomous-general-agent claims.
- CUDA/AirLLM 70B execution on this machine.
- Full web backend security.
- Full desktop GUI execution.
- Full test-suite health.
- Any feature documented only in aspirational architecture notes.

## Promotion Criteria

To promote a new capability into the branch face:

1. Add a manifest entry with purpose, command, result, and scope boundary.
2. Add or update a focused test where practical.
3. Run the verification locally.
4. Update `README.md` only after the manifest evidence exists.
