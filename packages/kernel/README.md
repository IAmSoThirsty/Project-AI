# Project-AI Kernel

The kernel is the bottom Python dependency layer. It defines canonical
outcomes, immutable action requests and decisions, fail-closed invariant
evaluation, hash-bound evidence, an append-only event spine, revisioned
state, deterministic replay verification, and rollback-detecting trusted
time. It has no dependency on governance, capability, execution,
companion, or application packages.

## When to use this package

Use kernel types and primitives when you need:

- A canonical decision/verdict type (`Decision`, `Outcome.ALLOW|DENY|ESCALATE`)
- An immutable `ActionRequest` or `ActionDecision` value
- `InvariantEngine` to attach fail-closed preconditions to any operation
- `EvidenceBundle` to hash-bind a set of evidence with a record ID
- `EventSpine` for an append-only event log with deterministic replay
- `StateRegister` for revisioned state with conflict detection
- `verify_event_chain` to verify the hash-chain integrity of an event log
- `TarlGate` to plug a Tarl policy decision into the kernel verdict flow
- `AttackPatternLibrary` / `BehaviorAnalyzer` for the security envelope

## Public API (top of `__init__.py`)

| Symbol | Purpose |
|---|---|
| `Decision`, `Outcome`, `ActionRequest`, `ActionDecision` | Canonical verdict types |
| `Invariant`, `InvariantEngine`, `InvariantViolation`, `InvariantSeverity` | Fail-closed invariant evaluation |
| `EvidenceBundle`, `build_evidence_bundle` | Hash-bound evidence container |
| `Event`, `EventSpine` | Append-only event log |
| `RevisionConflictError`, `StateRegister`, `StateSnapshot` | Revisioned state |
| `ReplayResult`, `replay`, `verify_event_chain` | Deterministic replay + chain verification |
| `EscalationHandler`, `TarlEnforcementError`, `TarlGate`, `TarlVerdictValue`, `TarlVerdictView` | Tarl bridge |
| `AttackPatternLibrary`, `BehaviorAnalyzer`, `BehaviorPattern`, `HeuristicPredictor` | Threat detection primitives |

## Dependency contract

**Downward-only.** Kernel has zero dependencies on any other Project-AI
package. It is the root of the package graph; every other package may
import kernel, kernel imports nothing else from this monorepo.

Imports: stdlib only (`hashlib`, `hmac`, `json`, `datetime`, `typing`,
`collections`, `dataclasses`, `enum`, `secrets`).

## Architectural invariants

- All evidence is hash-verifiable: `EvidenceBundle` carries a SHA-256
  over its canonicalized content; tampering invalidates the hash.
- Replay is deterministic: `replay(event_log)` produces the same
  state-register state for the same input bytes, every time.
- The event spine is append-only: there is no public `delete` or
  `modify` API; the only way to "change" history is to add a
  compensating event.

## Source of truth

- `packages/kernel/src/kernel/__init__.py` — full export list
- `docs/architecture.md` §"Python Packages" — kernel's position in the
  dep graph (root of the downward-only contract)
- `docs/security.md` — kernel's role in the fail-closed execution gate
