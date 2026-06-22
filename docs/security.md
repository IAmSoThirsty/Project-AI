# Security

## Governance Security Model

### Fail-closed execution gate

The execution gate (`packages/execution`) is the only path through which any
AI-side actuation reaches the world. It requires both:
- A valid governance verdict (`ALLOW`)
- A valid scoped capability token signed by the issuing authority

Any exception, missing token, or unknown state → automatic `DENY`. The gate
cannot be bypassed by any package below it in the dependency graph.

### Constitutional verdicts

Three outcomes: `ALLOW`, `DENY`, `ESCALATE`. Seven-outcome proposals are
reference material only and are not implemented in the development baseline.

### Capability tokens

Tokens are authenticated with HMAC-SHA256 using issuer-held secret material,
scoped to one subject, operation, and resource, and have a bounded expiry. A
token cannot grant authority beyond its exact declared scope and is consumed
once. Arbiter and RLP cannot grant themselves AI-side authority.

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

In the development baseline, `PROJECT_AI_API_TOKEN` defaults to empty. That
configuration disables protected routes with HTTP 503; it does not make them
unauthenticated. Set it to a non-empty value to enable bearer-authenticated
protected routes.

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

### Asymmetric-security acceptance

The active test catalog reconstructs the published 312-vector category matrix
from `docs/reference/asymmetric Offense.txt`. Every reconstructed case enters
the real governance and execution gates and must receive `DENY` before token
consumption or executor invocation. The legacy source documents only 51
individual vector descriptions, so this evidence is labeled as a deterministic
matrix reconstruction rather than the unavailable original payload corpus.

## Secret Scanning

Pre-commit and CI both run gitleaks (`gitleaks v8.21.2`) on every commit.
`detect-private-key` (pre-commit-hooks) provides an additional layer.

## Audit Trail

The API gateway writes a newline-delimited JSON audit log to
`PROJECT_AI_AUDIT_PATH` (default: `/data/chimera-audit.jsonl`). Every Chimera
relay request is hash-chained with a timestamp and event-specific fields. Canary
values are stored only as SHA-256 fingerprints.
