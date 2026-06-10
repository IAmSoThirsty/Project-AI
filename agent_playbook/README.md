---
title: "Agent Playbook & Reusable Skills Library - Project-AI Sovereign AI Governance Laboratory"
version: "2.3"
last_updated: "2026-06-10"
status: "Project-AI handoff readiness candidate / Project-AI Main handoff not applied"
domain: "meta"
tags: [playbook, skills-library, organizational-memory, reflexivity, staging]
invariant_impact: "Operationalizes skill capture, organizational memory, review discipline, and governance self-control for agentic development. Current status is deliberately bounded by claims and handoff readiness gates."
---

# Agent Playbook & Reusable Skills Library

**Version**: 2.4 - Integrated into Project-AI Main per direct owner instruction (2026-06-10). Previous handoff-readiness-candidate language superseded.

**Purpose**: Living, versioned repository of captured workflows, patterns, decision rationales, reusable skills, governance templates, and self-review controls for Project-AI / Grok Build agentic work.

Per direct human owner instruction on 2026-06-10, the Agent Playbook has been integrated into Project-AI Main (at `agent_playbook/`). The prior "handoff readiness candidate / Main handoff not applied" status is superseded. The final handoff evidence packet documented repo-side completion; this integration executes the owner's order.

## Current Readiness Boundary

The following files control readiness and claims:

- [Can't Compare Standard](CANT_COMPARE_STANDARD.md) - Defines the target maturity standard and current blockers.
- [Claims Boundary](CLAIMS_BOUNDARY.md) - Defines what may and may not be claimed.
- [Project-AI Handoff Readiness](PROJECT_AI_HANDOFF_READINESS.md) - Active handoff boundary and final repo-side checklist.
- [Project-AI Promotion Gate](PROJECT_AI_PROMOTION_GATE.md) - Legacy state-transition gate preserved for historical evidence continuity.
- [Change Control](CHANGE_CONTROL.md) - Defines how governance artifacts change.
- [Deprecation Policy](DEPRECATION_POLICY.md) - Defines how stale artifacts are retired.
- [Roadmap Governance](ROADMAP_GOVERNANCE.md) - Defines Now / Next / Later / Reject classification.
- [Roadmap Integration Review](ROADMAP_INTEGRATION_REVIEW.md) - Current reconciliation source for the next execution phases.

## What Exists Now

- Constitution, roadmap, templates, protocols, anti-pattern catalog, failure memory, risk register, metrics seed, adoption docs, and external review framing.
- No-silent-pass validator script at `tools/validate_agent_playbook.py`, with checks run, files inspected, warnings, failures, known blind spots, final status, global Markdown link checks, evidence provenance artifact checks, and trust-root fingerprint checks.
- Thin Python package / CLI seed under `src/agent_playbook/`, including advisory `classify` and diagnostic `doctor` support.
- Local source-checkout module shim under `agent_playbook/` for `python -m agent_playbook.cli`.
- Machine-readable governance core and load profiles under `governance/`.
- Machine-readable promotion gate requirements under `governance/PROMOTION_GATE_REQUIREMENTS.json`.
- Provenance scripts for manifest generation, Merkle tree generation, and Ed25519 signing/verification.
- Hash-backed provenance verification through `ap verify-provenance` and `ap validate --verify-provenance`.
- Signature-capable Ed25519 manifest verification through `ap verify-provenance --public-key <path> --require-signature`.
- Root-of-trust process documentation under `provenance/TRUST_ROOT.md`.
- Signature-backed seed evidence bundle under `evidence/2026-06-08-playbook-seeding/`.
- Signature-backed Project-AI promotion-readiness bundle under `evidence/2026-06-09-project-ai-promotion-readiness/`.
- Signature-backed review-gap hardening evidence bundle under `evidence/2026-06-10-review-gap-hardening/`.
- Signature-backed final handoff readiness evidence bundle under `evidence/2026-06-10-final-handoff-readiness/`.
- Promotion evidence and human signoff templates, with validator-enforced section coverage.
- Active async review, authority continuity, review debt, and second-human review protocols.
- Core Markdown template schemas and heuristic semantic validation for failure records and signoff records.
- Deprecation review register and deprecation record template for pruning discipline.
- Second-human/external-review packet, outreach template, and readiness checklist.
- Portable agent prompting standards and runtime training pack, without claiming mature cross-model validation.

## Integration Status (Owner Directive 2026-06-10)

Per direct human owner instruction, the full contents of this Agent Playbook have been integrated into Project-AI Main under the `agent_playbook/` directory.

The previous "handoff readiness candidate" and "do not claim integration" language has been superseded by the owner's explicit order. Historical evidence bundles remain for audit continuity. 

Future claims in the integrated copy should be evaluated against the current state in Project-AI Main.

## Directory Structure

```text
agent_playbook/
├── README.md
├── INDEX.md
├── CONSTITUTION.md
├── CANT_COMPARE_STANDARD.md
├── CLAIMS_BOUNDARY.md
├── PROJECT_AI_HANDOFF_READINESS.md
├── PROJECT_AI_PROMOTION_GATE.md
├── CHANGE_CONTROL.md
├── DEPRECATION_POLICY.md
├── ROADMAP_GOVERNANCE.md
├── ROADMAP_INTEGRATION_REVIEW.md
├── docs/
│   ├── MASTER_IMPROVEMENT_ROADMAP.md
│   ├── EXPANSION_PLAN_A_B_C.md
│   └── PHASE_A_B_C_EXECUTION_PLAN.md
├── governance/
├── templates/
├── protocols/
├── anti_patterns/
├── failures/
├── evidence/
├── provenance/
├── schemas/
├── tools/
├── src/
├── examples/
├── metrics/
├── risk_register/
├── external_review/
├── adoption/
├── usage/
└── meta/
```

## How to Use With Grok Build

Load only what the task requires. Do not require Grok to load the entire repo every session.

Minimum governance load for ordinary work:

1. `README.md`
2. `INDEX.md`
3. `CLAIMS_BOUNDARY.md`
4. `PROJECT_AI_HANDOFF_READINESS.md` if handoff, integration, or readiness is discussed
5. `PROJECT_AI_PROMOTION_GATE.md` only when historical gate criteria or the older signed evidence bundle are relevant
6. Relevant template, protocol, failure, or anti-pattern files for the task
7. `usage/portable-agent-prompting-standards.md` and `usage/agent-runtime-training-pack.md` when using a non-Grok runtime or transferring prompts across agents

For roadmap or meta-governance work, also load:

1. `ROADMAP_INTEGRATION_REVIEW.md`
2. `ROADMAP_GOVERNANCE.md`
3. `CHANGE_CONTROL.md`
4. `DEPRECATION_POLICY.md`
5. `CANT_COMPARE_STANDARD.md`

To get an advisory load profile:

```powershell
$env:PYTHONPATH='src'
python -m agent_playbook.cli classify "prepare Project-AI handoff review"
```

Classifier output is a recommendation, not approval or validator enforcement.

## Change Rule

Any change that affects claims, handoff readiness, roadmap sequencing, templates, protocols, or constitutional behavior must follow [CHANGE_CONTROL.md](CHANGE_CONTROL.md) and update [INDEX.md](INDEX.md) and [CHANGELOG.md](CHANGELOG.md) when navigation or status changes.

## Validation

Run from the repository root:

```powershell
python tools/validate_agent_playbook.py
python -m compileall .
python -m agent_playbook.cli version
python -m agent_playbook.cli classify "prepare Project-AI handoff review"
python -m agent_playbook.cli validate .
python -m agent_playbook.cli verify-provenance evidence/2026-06-08-playbook-seeding
python -m agent_playbook.cli verify-provenance evidence/2026-06-08-playbook-seeding --public-key provenance/public_key.pem --require-signature
python -m agent_playbook.cli verify-provenance --public-key provenance/public_key.pem --require-signature
python -m agent_playbook.cli validate . --verify-provenance --public-key provenance/public_key.pem --require-signature
python -m agent_playbook.cli doctor .
```

Current validator behavior: validation, handoff readiness checks, legacy promotion evidence structure checks, human signoff semantic heuristics, schema coverage checks, evidence provenance artifact checks, and trust-root signature fingerprint checks are available. Ed25519 signature verification is available through `ap verify-provenance --public-key provenance/public_key.pem --require-signature`. These checks do not perform external timestamp verification, independent review, complete human rationale judgment, signed release verification, or Project-AI Main handoff approval.

## Handoff Rule (Superseded)

The human owner has now explicitly directed and ordered the integration (2026-06-10). The integration has been executed into Project-AI Main. This section is retained for historical reference only.
