# Project-AI Command Center

This is your fast-launch hub for working on `Project-AI` inside the vault.

## Core Entry Points

- Repo root: `[[Project-AI/README]]`
- Mandatory guide: `[[Project-AI/.github/COPILOT_MANDATORY_GUIDE]]`
- Verified systems inventory: `[[Project-AI/.github/VERIFIED_SYSTEMS_INVENTORY]]`
- Workspace governance profile: `[[Project-AI/.github/copilot_workspace_profile]]`
- Current branch policy notes: `[[Project-AI/.github/THIRST_BRANCH_ACCEPTANCE_CRITERIA]]`

## Run / Test Quickstart

- Desktop app entry: `python -m src.app.main`
- Full tests: `pytest -v`
- Governance API e2e target: `http://localhost:8001`

## High-Value Project Paths

- Core app: `Project-AI/src/app/`
- Governance pipeline: `Project-AI/src/app/core/governance/pipeline.py`
- Constitutional systems:
  - `Project-AI/src/app/core/octoreflex.py`
  - `Project-AI/src/app/core/tscg_codec.py`
  - `Project-AI/src/app/core/state_register.py`
  - `Project-AI/src/app/core/constitutional_model.py`
- Desktop UI: `Project-AI/src/app/gui/`
- Agents: `Project-AI/src/app/agents/`
- Tests: `Project-AI/tests/`

## Local AI Stack (Obsidian)

- LM Studio endpoint: `http://127.0.0.1:1234/v1`
- Default local model key: `obsidian-agent|lm-studio`
- Local embedding key: `text-embedding-nomic-embed-text-v1.5|lm-studio`

## Suggested Daily Workflow

1. Open this note.
2. Jump to the exact subsystem note/file.
3. Use `templates/AI_AGENT_HANDOFF_TEMPLATE.md` for human/AI coordination.
4. Log outcomes in a short summary note with links to changed files.

## Related Vault Docs

- Vault README: `[[VAULT_README]]`
- Obsidian setup: `[[OBSIDIAN_README]]`
- Dataview query library: `[[DATAVIEW_QUERY_LIBRARY]]`
- Search guide: `[[SEARCH_GUIDE]]`

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
