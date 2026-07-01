# Project-AI Companion

The development companion owns a stable identity and flat revisioned
state. Reads are passive. State updates and restoration are actions
routed through `ExecutionGate`, so the companion cannot grant itself
governance or capability authority. Voice, visual, and autonomous
cognition surfaces remain outside this development checkpoint.

## When to use this package

You use the companion package when you need to:

- Bind a stable identity to a session or operator
- Persist a flat revisioned state (e.g., preferences, relationship data)
- Drive a stateful interaction through the governance + execution gate

You do **not** use this package to:
- Make governance decisions (use `packages/governance/`)
- Execute side effects directly (use `packages/execution/`)
- Issue capabilities (use `packages/capability/`)

## Public API

| Symbol | Purpose |
|---|---|
| `Companion` | The main class; holds identity + revisioned state |
| `CompanionIdentity` (frozen dataclass) | The stable identity record |
| `CompanionState` (frozen dataclass) | The current revisioned state |
| `bond(gate, identity, ...)` | Bond the companion to a session (routed through gate) |
| `unbond(gate, ...)` | Tear down the bond (routed through gate) |
| `record_fate(gate, ...)` | Record a fate entry (routed through gate) |
| `restore_state(gate, snapshot)` | Restore from a verified snapshot (routed through gate) |

## All mutations go through the gate

The companion is intentionally **incapable of self-authorization**. Every
state change — bonding, unbonding, recording a fate, restoring from a
snapshot — is a call into `ExecutionGate.submit_action` with a
companion-scoped capability token. The gate's fail-closed behavior
applies identically to the companion as to any other caller.

## What is NOT in the development checkpoint

- Voice bonding (`voice_bonding.py` exists in source but the autonomous
  surface is not wired in the development baseline)
- Visual bonding (same — source exists, surface deferred)
- Autonomous cognition (NIRL, Heart, Mini-Brain, Antibody, Forge
  subsystems are present in source but not exposed at the
  development-checkpoint API surface)

These surfaces exist as source so the architectural shape is preserved,
but they are not active runtime paths. The companion is read-and-record
only at this checkpoint.

## Dependency contract

Imports: `kernel` + `governance` + `capability` + `execution` + stdlib.
The companion is a consumer of the gate, not a peer.

## Architectural invariants

- The companion has no authority of its own; every mutation must be
  authorized by a capability token + ALLOW governance verdict
- Identity is stable across restarts (the state revision chain
  preserves it)
- State updates are revisioned; conflicts are detected and rejected
  (no silent overwrites)

## Source of truth

- `packages/companion/src/companion/__init__.py` — full export list
- `docs/architecture.md` §"Python Packages" — companion's tier
