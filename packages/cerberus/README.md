# project-ai-cerberus

Multi-agent runtime surface for Project-AI Beginnings. Closes Q5 from
`docs/operations/LEGACY_GAP_INVENTORY.md` §8.

Minimum viable port of legacy `src/app/core/cerberus_*` files (19 files,
~6,910 LOC in legacy). This module captures the typed surface and
fail-closed primitives only — full behavioral fidelity is deferred.

## Architectural invariants (AGENTS.md)

- **Downward-only deps**: cerberus imports only kernel + governance +
  execution + capability + stdlib. No upward imports.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- **Fail-closed**: spawn constraints reject unknown agent types, missing
  capabilities, and any unsatisfied invariant; never silent ALLOW.
- **Pluggable seams**: SpawnPolicy and LockdownTrigger Protocols.
- **Single audit chain**: all spawn attempts and lockdown events route
  through ExecutionGate (via capability.consume).
- **Strict typing**: mypy --strict clean.

## Modules

- `agent` — `CerberusAgent`: lightweight per-agent state holder (id, role,
  state, revision). State in kernel.StateRegister.
- `spawn_constraints` — `SpawnConstraints` + `SpawnPolicy` Protocol:
  fail-closed gate evaluating (agent_type, requested_capability,
  parent_chain) against a pluggable policy.
- `lockdown` — `LockdownController` + `LockdownTrigger` Protocol:
  emergency halt for the cerberus runtime. Once locked, no further
  spawns allowed until manual unlock.
