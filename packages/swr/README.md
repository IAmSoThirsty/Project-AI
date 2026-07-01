# Project-AI Sovereign War Room

SWR defines deterministic scenarios across five rounds and scores
supplied decisions without side effects. Recording a result is an
actuation and therefore requires `ExecutionGate` governance plus an
exact scoped capability (`swr.scenario.record`, `swr:<scenario-id>`).
The legacy bundle, deployment, and duplicate governance surfaces remain
provenance inputs rather than runtime paths.

## When to use this package

You use SWR when you need:

- A deterministic, multi-round scenario with reproducible outcomes
- A scoring surface for supplied decisions (no side effects on read)
- A replay-able record of a completed scenario (write through the
  execution gate)

You do **not** use SWR to:
- Make governance decisions (use `packages/governance/`)
- Run analyses with side effects (use `packages/atlas/`)
- Mutate state directly (use `packages/execution/`)

## Public API

| Symbol | Purpose |
|---|---|
| `SovereignScenario` (frozen dataclass) | A deterministic scenario spec |
| `SovereignDecision` (frozen dataclass) | A supplied decision for a round |
| `SovereignScore` (frozen dataclass) | The round-by-round score |
| `WarRoom.run(scenario, decisions)` | Read-only: score the decisions, no side effects |
| `WarRoom.record(result, gate, token)` | Write: append the scored result through the execution gate |
| `get_war_room()` | Singleton factory for the default war room |
| `reset_war_room()` | Test/reset helper |

## Five-round scenario shape

A scenario is a 5-round decision tree. The supplied `decisions`
argument is a tuple of 5 `SovereignDecision` values. The score is
deterministic: same input → same output, every time. The output is a
`SovereignScore` with per-round scores and a total.

## Why recording requires the gate

Recording a result is **actuation** — it persists to the audit log
and increments the canonical-replay state. Per the system's
fail-closed contract, the only way to persist anything is through
`ExecutionGate.submit_action` with a valid capability token.

The required capability is scoped to:
- **Subject** = the calling operator/agent
- **Operation** = `swr.scenario.record`
- **Resource** = `swr:<scenario-id>`

A token with a different operation or resource will be rejected by
the gate as a scope mismatch (returns `DENY`, no record written).

## Legacy surfaces (provenance only)

The full legacy SWR surface (api, bundle, core, crypto, governance,
proof, scoreboard, web dashboard, verify_quality.tarl) is preserved at
`packages/_staging/swr/` as a provenance input. These files are the
authoritative source for the next port wave; the canonical
`packages/swr/` package captures only the minimum-viable port (the
`scenario.py` and `war_room.py` modules).

## Dependency contract

Imports: `kernel` (canonical types) + `execution` (for the gate call)
+ stdlib. SWR is a consumer of the gate, not a peer.

## Architectural invariants

- `WarRoom.run` is **side-effect-free** (pure function of inputs)
- `WarRoom.record` is the **only** way to persist a scenario result
- The score is **deterministic** (same inputs → same score, bit-for-bit)
- The required capability scope is enforced by the gate; SWR does
  not re-validate

## Source of truth

- `packages/swr/src/swr/__init__.py` — full export list
- `packages/_staging/swr/` — legacy provenance
- `docs/architecture.md` §"Python Packages" — SWR's tier
- `docs/legacy-archive/` (and the future SWR port) — provenance
  documentation
