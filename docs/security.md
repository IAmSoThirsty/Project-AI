# Security

## Governance Security Model

### Fail-closed execution gate

The execution gate (`packages/execution`) is the only path through which any
AI-side actuation reaches the world. It requires both:
- A valid governance verdict (`ALLOW` or `ESCALATE`)
- A valid scoped capability token signed by the issuing authority

Any exception, missing token, or unknown state → automatic `DENY`. The gate
cannot be bypassed by any package below it in the dependency graph.

### Constitutional verdicts

Three outcomes: `ALLOW`, `DENY`, `ESCALATE`. Seven-outcome proposals are
reference material only and are not implemented in the development baseline.

### Capability tokens

Tokens are signed with an asymmetric key, scoped to a specific action set, and
have a configurable expiry. A token cannot grant authority beyond its declared
scope. Arbiter and RLP can issue tokens only through the standard token API and
cannot grant themselves AI-side authority.

### Veto

Governance holds a unilateral veto. A `DENY` verdict from governance cannot be
overridden by a capability token. Execution requires both to pass independently.

## Container Security

All seven development containers are hardened identically:

| Property | Value |
|---|---|
| Root filesystem | Read-only (`read_only: true` / `readOnlyRootFilesystem: true`) |
| Linux capabilities | All dropped (`cap_drop: [ALL]` / `capabilities.drop: [ALL]`) |
| Privilege escalation | Disallowed (`no-new-privileges: true` / `allowPrivilegeEscalation: false`) |
| User | Non-root (UID 10001 for Python/Rust services; nginx-unprivileged for portals) |
| Writable surface | `/tmp` emptyDir only (64 MB limit); API adds `/data` for audit output |
| Seccomp (Kubernetes) | `RuntimeDefault` |

Containers do not share network namespaces. Internal adapters (SWR, Atlas,
Arbiter/RLP, Genesis) have no host-bound ports and are not reachable from
outside the Compose network.

## API Security

The API gateway (`packages/api`) requires a bearer token for all Chimera relay
routes. The token is supplied via `PROJECT_AI_API_TOKEN` environment variable.
Health endpoints (`/health/live`) are unauthenticated.

In the development baseline, `PROJECT_AI_API_TOKEN` defaults to empty (no auth).
Set it to a non-empty value to require authentication.

## Source Integrity

### Frozen history chain (Stage -1.5)

A SHA-256 chain-linked snapshot of `T:\Project-AI-main` at the rebuild start is
stored in `docs/internal/frozen-history/`. Each record links to the previous
hash, forming a tamper-evident chain.

Verify:
```bash
python tools/verify_frozen_history.py
# Expected: 2,264/2,264 chain links verified
```

### Sovereign keypair

Governance artifacts in `governance/sovereign_data/` are signed with the
sovereign keypair at `governance/sovereign_data/sovereign_keypair.json`.
The verifier is `governance/sovereign_verifier.py`.

## Secret Scanning

Pre-commit and CI both run gitleaks (`gitleaks v8.21.2`) on every commit.
`detect-private-key` (pre-commit-hooks) provides an additional layer.

The sovereign keypair is stored as a governance artifact, not as a secret. It is
the signing authority for compliance bundles and is intentionally tracked.

## Audit Trail

The API gateway writes a newline-delimited JSON audit log to
`PROJECT_AI_AUDIT_PATH` (default: `/data/chimera-audit.jsonl`). Every Chimera
relay request is logged with timestamp, route, verdict, and authority token hash.
