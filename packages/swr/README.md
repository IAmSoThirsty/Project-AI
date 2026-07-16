# Project-AI Sovereign War Room

SWR defines deterministic scenarios across five rounds and scores
supplied decisions through a governed `WarRoomCore` facade. Recording a
result is an actuation and therefore requires `ExecutionGate` governance
plus an exact scoped capability (`swr.scenario.record`,
`swr:<scenario-id>`). Legacy bundle, crypto, proof, scoreboard, API, CLI,
and demo behavior now route through the canonical package surface.

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
| `Scenario` | A deterministic scenario spec |
| `ScenarioLibrary` | The five-round scenario catalog |
| `SovereignWarRoom.evaluate(...)` | Read-only: score one supplied decision, no side effects |
| `SovereignWarRoom.run_governed(...)` | Write: append the scored result through the execution gate |
| `WarRoomCore` | Legacy orchestration facade for scenarios, results, proofs, scoreboard, export, API, CLI, and demo |
| `swr.cli.get_swr()` | Factory for a fresh default governed `WarRoomCore` |

## Five-round scenario shape

A scenario belongs to one of five deterministic rounds. Each supplied
decision is scored reproducibly against its expected decision and can be
recorded only through the execution gate.

## Why recording requires the gate

Recording a result is **actuation** — it appends to the active SWR result/proof/score
state and returns an execution-event hash. It does not by itself update the separate
canonical-replay checkpoint. Per the system's fail-closed contract, the only way to
record the result is through
`ExecutionGate.submit_action` with a valid capability token.

The required capability is scoped to:
- **Subject** = the calling operator/agent
- **Operation** = `swr.scenario.record`
- **Resource** = `swr:<scenario-id>`

A token with a different operation or resource will be rejected by
the gate as a scope mismatch (returns `DENY`, no record written).

## Legacy Surfaces

The full legacy SWR surface (api, bundle, core, crypto, governance,
proof, scoreboard, web dashboard, verify_quality.tarl) is preserved at
`packages/_staging/swr/` as provenance input. The canonical
`packages/swr/` package now includes the J6.1 core facade plus API, CLI,
demo, bundle, crypto, governance, proof, scoreboard, scenario, and
war-room modules.

## Dependency contract

Imports: canonical `kernel`, `capability`, `governance`, and `execution`
modules plus package dependencies declared in `packages/swr/pyproject.toml`.
SWR is a consumer of the gate, not a peer.

## Architectural invariants

- `SovereignWarRoom.evaluate` is **side-effect-free** (pure function of inputs)
- `run_governed` / `WarRoomCore.execute_scenario` are the only runtime paths
  that persist scenario results
- The score is **deterministic** (same inputs → same score, bit-for-bit)
- The required capability scope is enforced by the gate; SWR does
  not re-validate

## Source of truth

- `packages/swr/src/swr/__init__.py` — full export list
- `packages/_staging/swr/` — legacy provenance
- `docs/architecture.md` §"Python Packages" — SWR's tier
- `docs/legacy-archive/` (and the future SWR port) — provenance
  documentation
