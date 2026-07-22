# Thirsty's Agents 101 — A Guide for Agent Governance

> Source: *Thirsty's Agents 101 — A Guide for Agent Governance*, Edition 1.0 (July 2026),
> Thirsty's Projects LLC, Jeremy Karrick (ORCID 0009-0007-9715-4290). Public release; not
> security classified. This directory integrates the guidebook's source standards, contracts,
> and full agent role templates into machine-readable Markdown for use inside this repository.
> Wording is reproduced faithfully; typography and page flow are adapted for readability.

This is the operating library for how AI agents work in Project-AI. It is **additive** to and
governed by [`AGENTS.md`](../../AGENTS.md) — the binding rule of engagement — and it never relaxes
Thirsty's Standard v3. Where anything here conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Where each source Part lives in this repo

| Guidebook Part | Content | Location in repo |
| --- | --- | --- |
| Part I — Thirsty's Standard v3 | AI execution/creation/coding/review/continuity/deployment contract (41 sections) | Reproduced verbatim in [`AGENTS.md`](../../AGENTS.md) §1 |
| Part II — Agent Operating Contract | Durable standing instructions read first, before any task | [`AGENT_OPERATING_CONTRACT.md`](AGENT_OPERATING_CONTRACT.md) |
| Part III — Thirsty's UX/UI Standard v1 | UX/UI, accessibility, validation, continuity, release contract (41 sections) | [`THIRSTYS_UX_UI_STANDARD_V1.md`](THIRSTYS_UX_UI_STANDARD_V1.md); source PDF in [`thirsty-ux-ui-standard/`](thirsty-ux-ui-standard/) |
| Part IV — Thirsty's Standard V3Q Manifest | Machine-readable behavioral + enforcement contract (rule IDs, controls, evidence, tests) | Package [`packages/thirstys-standard-v3q/`](../../packages/thirstys-standard-v3q/); mirror + verification in [`docs/governance/thirstys-standard-v3q-manifest/`](../governance/thirstys-standard-v3q-manifest/) |
| Part V — Glossary, Reference Index, Disclaimer | Normative + guidebook glossary, controlling-source index, use limits | [`GLOSSARY_AND_REFERENCE.md`](GLOSSARY_AND_REFERENCE.md) |
| Part VI — Full Agent Template Library | 20 bounded professional role contracts | [`agent-role-templates/`](agent-role-templates/) |

## How to use this guide

1. **Start with the operating guide.** Establish the governance sequence, select roles, define
   authority, and understand how evidence, verification, continuity, and release fit together.
2. **Apply the source standards.** Part I is the general operating contract. Part III applies the
   same discipline to UX/UI work. Part II is the standing contract read at task start.
3. **Use the manifest for machine-readable control.** Part IV preserves the V3Q YAML manifest —
   treat its status, versions, control IDs, evidence contracts, and implementation statements
   exactly as written.
4. **Assign bounded roles.** Part VI contains every role template in full. Select the smallest set
   of roles required for the task, define their inputs and authority, and preserve disagreement
   rather than manufacturing consensus.
5. **Verify before claiming completion.** Testing, review, signatures, documentation, or confidence
   do not extend a claim beyond the evidence and conditions actually verified.

## The agent governance stack

1. **Authorized human objective** — purpose, priorities, acceptable risk, approvals, final authority.
2. **Global operating contract** — truthfulness, scope, blockers, risk, evidence, continuity, completion (Parts I–II).
3. **Role contracts** — bounded professional responsibilities, inputs, prohibited behavior, outputs, completion conditions (Part VI).
4. **Task and authority envelope** — declared mode, allowed tools, permissions, data boundaries, dependencies, acceptance criteria.
5. **Execution and evidence** — actions, tests, logs, diffs, runtime observations, durable records.
6. **Independent review and release** — testing, verification, security review, governance review, readiness decision, rollback, continuity.

## End-to-end agent lifecycle

1. Receive the instruction — record the actual objective; do not silently replace, broaden, narrow, or reinterpret it.
2. Establish authority and constraints — who may authorize, what permissions exist, what data may be used, what is prohibited.
3. Declare scope and operating mode — name the level of work.
4. Inspect current state and continuity — read source material, system/repo state, prior decisions, continuity maps, known findings before acting.
5. Identify blockers, risks, and unknowns — stop only where continuing would be unsafe, deceptive, unauthorized, corrupting, or materially dependent on unknown facts; continue safe work.
6. Select and assign roles — give each role explicit inputs, boundaries, authority, outputs, and completion evidence.
7. Plan and sequence work — map dependencies, parallel work, validation gates, rollback conditions, human decision points.
8. Execute the minimal effective change — only authorized work; preserve existing architecture and controls; avoid unrelated cleanup or performative activity.
9. Test normal, boundary, failure, and recovery paths — record passed/failed/blocked/skipped/inconclusive/not-tested accurately.
10. Verify material claims independently — confirm artifact identity, version, environment, evidence integrity, reproduction, acceptance criteria, and the boundary of what was not verified.
11. Hostile-review the result — attack assumptions, paths, dependencies, authority, evidence, bypasses, security, UX, failure recovery, documentation, and readiness claims.
12. Report, preserve continuity, and decide readiness — record created/modified/tested/verified/failed/unverified, risks, remaining work, commands, rollback, and safe-to-continue status.

## Role system and handoffs

Roles are not personalities and do not inherit unlimited authority. Grouped by function:

- **Define** — Researcher, Observer, Analyst, Architect, Planner
- **Execute** — Coordinator, Implementer, Refactorer, Optimizer, Documentation Writer
- **Challenge** — Critic, Security Auditor, Tester, Verifier, Red Team
- **Govern** — Governance Reviewer, Decision Arbiter, Memory Curator, User Experience Reviewer, Teacher

A handoff preserves the accepted objective, source evidence, current state, assumptions, unknowns,
constraints, unresolved disagreement, completion criteria, and the exact boundary of delegated
authority. See [`agent-role-templates/`](agent-role-templates/) for each full contract and the
minimum handoff record.

## Evidence, verification, continuity, readiness

- **Evidence** — a material claim points to the relevant artifact, command output, test result, log,
  configuration, runtime observation, signature, hash, or other admissible record.
- **Verification** — the verifier bounds the claim, checks artifact/environment identity, examines
  evidence integrity, reproduces where practical, attempts falsification, and states remaining uncertainty.
- **Continuity** — the continuity map records what actually changed, what remains, what failed, what
  was not verified, what risks exist, and what action is safe next. It is not a portfolio description.
  This repo's continuity map is [`docs/operations/CONTINUITY_MAP.md`](../operations/CONTINUITY_MAP.md).
- **Readiness is a bounded claim** — general and UX/UI production readiness are evidence-backed checklists
  (Standard v3 §25, UX/UI Standard §25). Missing any item → "Not production-ready yet" + reason + minimum fix.

## Disclaimer

This material is a practical guidebook for designing, governing, operating, reviewing, and documenting
AI agents. It is not a guarantee that any agent, architecture, workflow, or deployment will be
failure-free, secure, lawful, compliant, accurate, available, or fit for every purpose. Written rules,
prompts, manifests, contracts, tests, signatures, logs, and documentation do not independently prove
runtime enforcement or production behavior. Claims must remain bounded to the evidence, version,
environment, and conditions actually verified. The authorized human owner retains responsibility for
objectives, approvals, risk acceptance, deployment decisions, and final judgment. The military /
controlled-file visual treatment of the source is an editorial choice only; the source is not a
publication of any government agency and carries no security classification. Verify the controlling
version before operational use. See [`GLOSSARY_AND_REFERENCE.md`](GLOSSARY_AND_REFERENCE.md) for the
full disclaimer and reference index.

> BUILD CAREFULLY // VERIFY RELENTLESSLY // PRESERVE HUMAN AUTHORITY
> © 2026 Thirsty's Projects LLC — SLC-UT — Jeremy Karrick — ORCID 0009-0007-9715-4290.
