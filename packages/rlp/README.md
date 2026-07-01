# Project-AI RLP

Experimental Reciprocal Legitimacy Protocol policy engine. It governs
operator/AI legitimacy boundaries, scoped autonomy, reversible
graduation, irreversibility gates, and evidence-bound discretion.

This package is a draft policy layer. Runtime enforcement remains the
responsibility of Project-AI governance and execution packages.

## When to use this package

You use RLP when you need:

- A policy engine for the operator/AI legitimacy boundary
- Scoped-autonomy rules (what an operator can do without an AI
  verdict, what requires one, what requires both)
- Reversible graduation (capabilities that can be granted and later
  revoked without rebuilding policy)
- Irreversibility gates (mutations that, once executed, cannot be
  undone — require a higher approval bar)
- Evidence-bound discretion (the policy can grant the operator
  latitude only when specific evidence is present)

You do **not** use RLP to:
- Make AI-side governance decisions (use `packages/governance/`)
- Execute actions (use `packages/execution/`)
- Replace the AI-side governance pipeline (RLP is operator-side)

## Public API (top of `__init__.py`)

| Symbol | Purpose |
|---|---|
| `RLPEngine` | The policy engine; holds the autonomy + irreversibility + evidence rules |
| `LegitimacyScope` (frozen dataclass) | The current scope of an operator's legitimate action |
| `AutonomyGrant` (frozen dataclass) | A scoped autonomy grant (reversible) |
| `IrreversibilityGate` (frozen dataclass) | The gate for irreversible mutations |
| `evaluate(engine, proposed_action, evidence)` | Pure function: returns the legitimacy scope |
| `grant_autonomy(engine, scope, evidence)` | Issue a reversible autonomy grant |
| `revoke_autonomy(engine, grant_id)` | Revoke a previously granted autonomy |
| `RLPError` | Raised on policy violations, evidence missing, irreversibility threshold not met |

## The legitimacy boundary

The RLP policy answers: "Given the operator's identity, current
autonomy grants, the proposed action, and the available evidence,
what is the legitimacy scope of this action?" The answer is one of:

- **Operator-scope** — operator can proceed (no AI verdict needed)
- **AI-verdict** — operator must obtain an ALLOW from
  `packages/governance/`
- **Dual-legitimacy** — both operator scope AND AI verdict required
- **Irreversibility-gate** — if the action is irreversible, the bar
  is raised (more evidence, dual-signature, time delay)

The RLP engine does **not** issue the AI verdict itself. It only
classifies what is required.

## Why this is "experimental"

RLP is explicitly operator-side, alongside Arbiter. It is a draft
policy engine — its rules are loaded from `packages/rlp/governance_framework/`
(where the policy templates live) and can be evolved without
rebuilding the AI-side governance.

## Dependency contract

Imports: `kernel` + stdlib. RLP is intentionally NOT coupled to
`governance`, `capability`, or `execution`. Its output is a
classification that the operator's calling code interprets; the
operator's code then routes through the AI-side governance +
execution gate as required.

## Architectural invariants

- RLP rules are **versioned** (policy version is part of every
  classification)
- Autonomy grants are **reversible** (revocable by the same
  authority that granted them)
- Irreversibility gates are **always evaluated** (never optional)
- The RLP engine is **pure** (no side effects, no I/O) — the
  caller is responsible for recording the classification

## Policy templates

The policy templates and prompts that drive RLP live in
`packages/rlp/governance_framework/`:
- `templates/` — user-authored governance templates
- `policies/` — active policy documents
- `prompts/` — the prompts that classify actions
- `examples/` — worked examples
- `tests/` — policy-engine test harness
- `scripts/` — operator-side utilities

## Source of truth

- `packages/rlp/src/rlp/__init__.py` — full export list
- `packages/rlp/governance_framework/` — policy templates + prompts
- `docs/architecture.md` §"Python Packages" — RLP's tier
  (operator-side experimental)
