# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-14 | TIME: 08:35               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

<!-- # Date: 2026-03-14 | Time: 08:35 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/Date-2026--03--14-blue?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Tier-Master-gold?style=for-the-badge" alt="Tier" />
</div>

---
name: Principal Architect Agent Construction
description: Guidelines and template for building a sovereign static-analysis architect agent that audits the entire Project-AI repository state.
---

# Skill: Principal Architect Agent Construction

## Overview
This skill defines the protocol for creating and maintaining "Architect Agents" within the Project-AI sovereign ecosystem. These agents are pure static-analysis engines that map the reality of the codebase against the sovereign intent, specifically tailored for the "Architect Council."

## Core Directives
1. **Total Visibility**: Agents must use `git ls-files` to ensure they audit every tracked file. No exceptions for sub-directories or obscure paths.
2. **Deterministic Categorization**: Every file must fall into a specific bucket:
    - **EXECUTABLE**: Real runnable code with logic beyond stubs.
    - **STUB**: Code file containing only `pass`, logs, or placeholders.
    - **MOCK**: Code that simulates behavior instead of implementing it.
    - **ARCHIVED**: Files in `archive/` or flagged as legacy.
    - **CONFIG**: YAML, TOML, JSON, ENV, etc.
    - **INFRA**: Docker, K8s, Terraform, CI workflows.
    - **SPEC**: Linguistic specs, governance docs, constitutions.
    - **DOC**: Documentation files (cataloged but deprioritized).
    - **UNKNOWN**: Catch-all for unidentifiable files.

3. **Maturity Evaluation**: Completion is measured for all non-DOC files (0%-100%) based on:
    - Presence of real logic (non-comment, non-stub lines).
    - Presence of unit tests (proximity or naming convention).
    - Import resolution and valid syntax.

4. **Council Alignment**: Evaluations must be routed to the nine Peer Architects:
    - **Strategic**: Platform integrity and total system state.
    - **Governance**: Triumvirate balance and Immutable Laws.
    - **Alignment**: Bonding Protocol and AGI Charter.
    - **Linguistic**: Compiler purity and Bijective Grammar.
    - **Verification**: Shadow vs. Canonical plane safety.
    - **Risk**: Simulation coverage and takeover preventatives.
    - **Hardening**: Hydra containment and PSIA pipelines.
    - **Cryptographic**: Ed25519 signing and MD immutability.
    - **Behavioral**: Staffing Manifest and agentic entropy.

## Implementation Template
- **No CLI Interaction**: Must run autonomously.
- **No AI API Calls**: Must rely on pure static analysis.
- **Deterministic Output**: Always produces `ARCHITECT_MANIFEST.json` and `.md`.

## Workflow Integration
Create `.github/workflows/architect.yml` to trigger on `push` and `workflow_dispatch`.
