# ADR-002: Per-program machine credentials

- **Status:** Proposed — NOT implemented. Nothing in this record describes current
  runtime behavior; the current runtime uses exactly one shared machine bearer
  token (`PROJECT_AI_API_TOKEN`).
- **Date:** 2026-07-17
- **Scope:** Machine-facing gateway authentication (`packages/api`), machine
  clients (`packages/cli`, `packages/mcp_server`), deployment surfaces.

## Context

Every machine write surface on the gateway — `POST /chimera/verdict`,
`POST /chimera/canary`, `POST /atlas/sludge` — and every machine read of
protected evidence is authenticated by one shared static bearer token compared
constant-time against `PROJECT_AI_API_TOKEN`. Consequences today:

1. **No per-program accountability.** The audit chain records what happened but
   cannot attribute a machine write to a specific program (CLI, MCP bridge, TAAR
   scheduler, CI job) because they all present the same credential.
2. **All-or-nothing revocation.** Rotating the token revokes every machine client
   at once; there is no way to cut off one compromised program.
3. **Uniform scope.** Any holder of the token can call every machine surface;
   a read-only evidence consumer carries write authority it never needs.
4. The role/permission matrix (`docs/product/ROLE_PERMISSION_MATRIX.md`) and the
   human-auth threat model (`docs/security/HUMAN_AUTH_THREAT_MODEL.md`) both
   assert a hard separation between human sessions and machine credentials, but
   the machine side of that separation has no management story of its own.

This is acceptable for a loopback-only pre-alpha development gateway and wrong
for anything beyond it.

## Decision (proposed)

1. **Credential record.** Add a `machine_credentials` table to the accounts
   store (SQLite + PostgreSQL, same dual-backend pattern as `packages/accounts`):
   `id`, `label`, salted credential hash (Cerberus `PasswordHasher`, same as
   human secrets — raw tokens are never stored), `scopes` (set), `created_at`,
   `created_by` (owner account id), `last_used_at`, `revoked_at`.
2. **Scopes.** Start with exactly three: `evidence.read` (GET /audit, sludge
   inspection), `evidence.write` (chimera verdict/canary relay), and
   `analysis.generate` (POST /atlas/sludge). Scope names are contract, stored
   per credential, and enforced by the gateway guard per route.
3. **Gateway resolution.** `require_machine_auth` resolves the presented bearer
   against active credential records (constant-time hash comparison), rejects
   revoked/unknown credentials, enforces the route's required scope, and stamps
   the credential `id` + `label` into the audit event so every machine write is
   attributable.
4. **Bootstrap demotion.** `PROJECT_AI_API_TOKEN` becomes a bootstrap-only
   credential: valid solely for minting the first owner-created machine
   credential when no credential records exist, then refused. Deployments that
   never configure credential records keep current behavior only in explicit
   development mode.
5. **Management surface.** Owner/administrator session routes (CSRF + recent
   MFA, mirroring account administration):
   `GET/POST /api/v1/admin/machine-credentials`,
   `POST /api/v1/admin/machine-credentials/{id}/revoke`. The raw token is shown
   exactly once at creation (the human-recovery-code handoff pattern).
6. **Clients.** CLI and MCP server continue to read a single env token — now a
   per-program credential. `.env.example`, Compose, and Helm document one
   credential per deployed program (TAAR readers, MCP bridge, CI verifier).

## What this deliberately does NOT change

- Capabilities, governance verdicts, and the execution gate are untouched. A
  machine credential authenticates transport identity; it never becomes
  actuation authority (that remains: governance ALLOW + scoped one-use
  capability + gated executor, per `packages/execution`).
- Human sessions are untouched; the human/machine separation asserted in
  ADR-001 §3 is preserved and finally gets its machine half.

## Consequences

- Attribution: every machine audit event gains a stable credential identity.
- Containment: one compromised program is revoked without touching the rest.
- Least privilege: read-only consumers hold read-only scopes.
- Cost: a schema migration (accounts store version bump, both backends), guard
  changes on every machine route, new admin routes + UI, test matrix growth
  (denial per missing scope, revocation, bootstrap demotion, no-bypass), and
  OpenAPI baseline churn. This is why implementation is deferred rather than
  rushed into the current slice while adjacent lanes are active.

## Test plan (for the implementing session)

- Unknown/revoked/wrong-scope credentials → 401/403, no route body executed.
- Bootstrap token refused once any credential record exists.
- Creation returns raw token exactly once; storage holds only the salted hash.
- Audit events carry credential id/label for every machine write.
- Live PostgreSQL migration proof against a disposable container.
- OpenAPI baseline regenerated; freeze test green.

## Evidence for the current state (what makes this ADR necessary)

- Shared-token guard: `packages/api/src/project_ai_api/app.py`
  (`require_machine_auth`, `_check_machine_credential`).
- Ungoverned egress recorded as related debt: `packages/global-scenario`
  calls World Bank/ACLED via direct `requests` with no gateway identity at all
  (`global_scenario_engine.py`); any egress-governance design should assume
  per-program credentials exist first.
- Machine clients: `packages/cli/src/project_ai_cli/client.py`,
  `packages/mcp_server/src/mcp_server/client.py`.
