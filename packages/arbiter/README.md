# Project-AI Arbiter

Experimental operator-side governance substrate. It binds operator
actions through append-only evidence, delay, adversarial review, dual
signatures, sustainability limits, and succession checks.

This package is a draft. It does not replace or bypass AI-side
governance and must invoke runtime actions through the Project-AI
execution gate.

## When to use this package

You use the Arbiter when you need:

- An operator-side governance surface that records decisions with
  append-only evidence
- A delay + adversarial-review pattern before operator-driven
  mutations
- Dual-signature authorization for high-stakes operator actions
- Sustainability limits (rate / volume / time-bounded)
- Succession checks (the operator-in-charge is verified against the
  registered successor chain)

You do **not** use the Arbiter to:
- Make AI-side governance decisions (use `packages/governance/`)
- Bypass the execution gate (the Arbiter's actions still flow through
  the gate)
- Issue capabilities (use `packages/capability/`)

## Public API (top of `__init__.py`)

| Symbol | Purpose |
|---|---|
| `Arbiter` | The main class; holds operator-side evidence + delay + review state |
| `ArbiterDecision` (frozen dataclass) | A recorded operator decision (append-only) |
| `ArbiterEvidence` (frozen dataclass) | The evidence supporting a decision |
| `propose(arbiter, action, evidence)` | Submit an operator action for review (delay starts) |
| `confirm(arbiter, proposal_id, signature)` | Confirm after delay + adversarial review |
| `dual_sign(arbiter, proposal_id, second_signature)` | Add a second signature for high-stakes actions |
| `ArbiterError` | Raised on bypass attempts, signature failures, sustainability limit violations |

## Why this is "experimental"

The Arbiter is explicitly **outside the AI-side governance tier** (it
sits alongside RLP as an operator-side experimental package). Its job
is to add operator-side friction (delay, review, dual-signature,
limits) to operator actions before they reach the execution gate. The
AI-side governance does not see Arbiter's internal state.

Critically, **Arbiter cannot grant AI-side authority**. If the
operator's proposed action needs a verdict from `packages/governance/`,
Arbiter must route that request through the AI-side governance — the
result is bound, but the verdict itself is the AI-side's.

## Dependency contract

Imports: `kernel` + stdlib. The Arbiter is intentionally NOT coupled
to `governance`, `capability`, or `execution` directly — its
proposals, when confirmed, are submitted as external actions by the
operator's code path (which DOES go through the gate).

## Architectural invariants

- Arbiter evidence is **append-only** (no `delete` or `modify`)
- Delay is **mandatory** before confirmation (configurable minimum)
- Dual-signature is **mandatory** for actions above the
  high-stakes threshold (configurable)
- Sustainability limits are **enforced** (rate / volume / time
  windows; violations are rejected)
- The Arbiter **cannot** make AI-side decisions; it only gates
  operator actions

## Source of truth

- `packages/arbiter/src/arbiter/__init__.py` — full export list
- `docs/architecture.md` §"Python Packages" — arbiter's tier
  (operator-side experimental)
- `docs/security.md` — the trust model (Arbiter is NOT a peer of
  AI-side governance)
