# Project-AI Security

This development package carries the selectively imported Chimera v2.2
perimeter and a typed, append-only bridge for governance verdicts,
denials, and canary events. The bridge stores hashes instead of raw
canary values and does not expose Chimera runtime state.

The repository license is MIT. `reference/chimera_v2_2.py` preserves
the imported implementation with only the owner-authorized license-header
normalization. The runtime module is an owned copy that is formatted,
typed, and tested separately. The import report records both source
hashes.

## When to use this package

You use the security package when you need:

- The Chimera v2.2 classification + audit relay surface (selective import)
- A typed, append-only relay for `verdict`, `canary`, and `denial` events
  (the bridge)
- Hash-fingerprint storage for canary values (raw values never persisted)

You do **not** use this package to:
- Make governance decisions (use `packages/governance/`)
- Execute actions (use `packages/execution/`)
- Define canonical types (use `packages/kernel/`)

## Public API

| Symbol | Purpose |
|---|---|
| `AppendOnlyAuditRelay` | The append-only audit log writer |
| `VerdictRecord`, `CanaryRecord`, `DenialRecord` (frozen dataclasses) | Typed event records |
| `receive_verdict(relay, action_id, verdict, source)` | Record a governance verdict |
| `receive_canary_hit(relay, canary_value, context)` | Record a tripped canary (stores only the SHA-256 fingerprint of the value) |
| `active_relay()` | Singleton accessor for the default relay (configured by `PROJECT_AI_AUDIT_PATH`) |
| `SecurityError` | Raised on classification / relay / write failures |

## Audit relay semantics

The relay is **append-only**. There is no `delete` or `modify` API. The
relay is hash-chained: every record carries the SHA-256 of the previous
record, so tampering is detectable. Verification is performed by
`tools/verify_frozen_history.py` for the frozen-history chain, and by
`GET /audit` for the live Chimera audit log.

**Fail-closed behavior:** if the audit path is not configured (no
`PROJECT_AI_AUDIT_PATH`), the protected API routes return `503
Service Unavailable` rather than silently dropping audit events.

## Dependency contract

Imports: `kernel` (canonical types, hash primitives) + stdlib.

The Chimera v2.2 module is selectively imported and lives at
`reference/chimera_v2_2.py`; it is **not** in the runtime import path
of the canonical `project-ai-security` package — only the bridge and
the relay are.

## Architectural invariants

- The audit log is **append-only** and **hash-chained**
- Canary values are **never stored** in raw form; only their
  SHA-256 fingerprints
- The Chimera v2.2 module is **not** exposed to other packages
- The security package is the **only** path through which audit
  events flow into the relay

## Source of truth

- `packages/security/src/security/__init__.py` — full export list
- `packages/security/reference/chimera_v2_2.py` — preserved import
- `docs/security.md` — the full security model (fail-closed gate,
  container hardening, secret scanning)
- `docs/runbooks/INCIDENT_RESPONSE.md` §"Audit chain is broken" — the
  recovery procedure
