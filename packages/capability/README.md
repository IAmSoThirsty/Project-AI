# Project-AI Capability

This package issues HMAC-SHA256 capability tokens bound to one subject,
operation, resource, and bounded lifetime. Verification fails on malformed
signatures, expiry, scope mismatch, revocation, or one-time token replay.
Capability authority does not make governance decisions and cannot execute
actions.

## When to use this package

Use capability tokens when you need:

- A scoped, expiring authorization that a specific subject can present
  to a specific resource for a specific operation
- A token that is unforgeable without the issuer's HMAC secret
- A token that is consumed exactly once (one-time replay protection)
- A way to verify a token's signature, scope, and expiry without
  consulting the original issuer

You do **not** use this package to:
- Make governance decisions (that's `packages/governance/`)
- Execute an action (that's `packages/execution/`)
- Audit an event (that's `packages/security/`)

## Public API

| Symbol | Purpose |
|---|---|
| `CapabilityAuthority` | The issuer: mints, verifies, and revokes tokens |
| `CapabilityToken` (frozen dataclass) | A signed, scoped, time-bounded authorization |
| `CapabilityError` | Raised on signature failure, scope mismatch, expiry, replay, or revocation |
| `mint_capability(...)` | Convenience constructor (most common case) |
| `verify_capability(token, ...)` | Stand-alone verifier (no authority state required) |
| `get_capability_authority(...)` | Singleton factory for the default authority |

## Token shape (conceptual)

A capability token is bound to:

- **Subject** — the entity authorized (e.g., `companion_id`, `agent_id`)
- **Operation** — the action being authorized (e.g., `atlas.record`,
  `swr.scenario.record`)
- **Resource** — the target the action operates on (e.g.,
  `atlas:<projection-id>`, `swr:<scenario-id>`)
- **Expiry** — an absolute timestamp after which the token is invalid
- **Signature** — HMAC-SHA256 over the canonicalized subject+op+resource+expiry
  using the issuer's secret

The token is single-use. After `consume(token)`, the same token bytes
will not verify again.

## Dependency contract

Imports: `kernel` (for canonical types) + stdlib (`hmac`, `hashlib`,
`secrets`, `datetime`, `dataclasses`).

Capability cannot import governance, execution, companion, or
application packages. It is a pure cryptographic authority primitive.

## Architectural invariants

- Tokens are **unforgeable** without the issuer's secret
  (HMAC-SHA256, 32-byte minimum secret, constant-time compare on verify)
- Tokens are **scope-limited** — a token for `atlas.record` cannot
  authorize `swr.scenario.record`
- Tokens are **time-bounded** — expiry is mandatory
- Tokens are **single-use** — replay is detected and rejected
- The authority does **not** decide anything; it only proves
  authorization was granted

## Configuration

- `CAPABILITY_AUTHORITY_SECRET` (or equivalent) — the HMAC secret. Must
  be at least 32 bytes. Never committed. See `docs/security.md` for
  secret-handling rules.

## Source of truth

- `packages/capability/src/capability/__init__.py` — full export list
- `docs/architecture.md` §"Python Packages" — capability's tier
- `docs/security.md` §"Capability tokens" — token semantics
