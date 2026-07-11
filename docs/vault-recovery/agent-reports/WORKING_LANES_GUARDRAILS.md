# Working Lanes Guardrails (Vault vs Repo)

Use this note to avoid mixing operational note work with production code work.

## Lane A — Obsidian Vault (Operational Layer)

**Location:** `t:\Project-AI-vault`

### ✅ DO in repo

- Write and organize notes, plans, handoffs, and dashboards.
- Maintain templates, prompt files, taxonomy docs, and query libraries.
- Update Obsidian workspace/settings for personal workflow.
- Use this lane for AI coordination, summaries, and navigation artifacts.

### ❌ DON’T treat as source-of-truth code lane

- Don’t run production PR workflows from vault clone.
- Don’t assume vault clone branch state equals active development repo state.

---

## Lane B — Development Repo (Production Layer)

**Location:** `t:\Project-AI-main`

### ✅ DO here

- Implement code changes.
- Run build/lint/test/security checks.
- Commit, branch, push, and open PRs.
- Perform release-impacting edits and validation.

### ❌ DON’T clutter with note-ops

- Don’t store transient operational dashboards/checklists here unless repo policy requires it.

---

## Current Setup Snapshot

- Vault contains a reference clone for navigation: `t:\Project-AI-vault\Project-AI`
- Active development repo remains: `t:\Project-AI-main`

Interpretation:

- **Browse in vault, build in repo.**

---

## Quick Decision Rule

If work item starts with **“code compiles/tests/PR”** → use **Lane B**.

If work item starts with **“organize/track/explain/navigate/coordinate”** → use **Lane A**.

---

## Agent Instruction Snippet (copy/paste)

> Use `t:\Project-AI-main` for all code modifications, tests, and PR-facing changes.
> Use `t:\Project-AI-vault` for notes, planning, dashboards, and coordination artifacts only.

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
