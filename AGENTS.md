# AGENTS.md — Vault-Only Write Governance

This repository allows **broad read access** for coding agents/IDE copilots, while restricting where they may write by default.

## Intent

Enable multiple copilots/agents to understand the full monorepo context, but prevent accidental edits outside the Obsidian knowledge surface.

## Access Policy

### Read Access (Allowed)

Agents may read any repository path needed for context:

- `src/**`
- `tests/**`
- `docs/**`
- `.github/**`
- config/build files and root reports

### Write Access (Default: Restricted)

Agents may write only to vault paths:

- `.obsidian/**`
- `wiki/**`

All non-vault paths are **read-only by default**.

## Override Rule

If a task explicitly requires non-vault edits, the user must explicitly authorize that scope in the prompt.

Without explicit authorization, agents should:

1. Read needed files for understanding.
2. Propose changes.
3. Apply edits only inside `.obsidian/**` and `wiki/**`.

## Collaboration Model

Using four copilots/agents is treated as a team workflow.

Vault write conventions for team safety:

- Keep personal workspace/cache files out of commits.
- Prefer shared-safe config in `.obsidian/` (plugin manifests, graph presets, templates/snippets).
- Keep architecture/context notes in `wiki/` so all agents consume the same source-of-truth.

## Fast Context Entry Points

Agents should prioritize these files for monorepo understanding:

- `README.md`
- `.github/COPILOT_MANDATORY_GUIDE.md`
- `.github/copilot_workspace_profile.md`
- `.github/instructions/mandatory-structured-generation-default.instructions.md`
- `wiki/00_AGENT_MONOREPO_DATABASE.md`

## Mandatory Coding Default (All Agents and IDE Copilots)

For any coding task (code generation, code edits, or code review recommendations), agents MUST follow:

- `.github/instructions/mandatory-structured-generation-default.instructions.md`

Required order:

1. Requirements contract (no silent assumptions)
2. Design
3. Pseudocode
4. Implementation
5. Adversarial self-review
6. Refinement
7. Verification gate

Skipping this protocol is non-compliant.

## Operating Principle

> Read everywhere. Write in vault only.
