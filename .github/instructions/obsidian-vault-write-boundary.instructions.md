---
description: "Vault-only write policy for AI agents: read entire repository, but write only to .obsidian/** and wiki/** unless explicitly authorized by user."
applyTo: "**"
---

# Obsidian Vault Write Boundary

## Policy

AI agents and IDE copilots operating in this repository must follow this boundary:

- **Read access:** all repository files and folders.
- **Write access (default):** `.obsidian/**` and `wiki/**` only.
- **All other paths:** read-only unless the user explicitly authorizes non-vault edits in the prompt.

## Required Behavior

1. Use repository-wide reading for context and analysis.
2. Place generated/updated artifacts in vault paths (`.obsidian/**`, `wiki/**`).
3. When a request implies non-vault edits, ask for explicit scope confirmation before editing outside vault.
4. If no explicit override is given, do not modify non-vault files.

## Rationale

This repository uses the Obsidian vault as the shared, team-readable knowledge surface for multiple copilots/agents. Vault-only writes reduce accidental codebase drift while preserving full-context understanding.
