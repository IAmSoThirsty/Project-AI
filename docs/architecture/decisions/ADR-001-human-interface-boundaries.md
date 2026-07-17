# ADR-001: Human interface delivery and authority boundaries

- **Status:** Accepted for current implementation
- **Date:** 2026-07-15
- **Scope:** Project-AI human interface foundation

## Decision

1. `apps/web/operator-console` is the canonical human interface.
2. Desktop delivery will open the canonical console in the system browser unless a
   later decision authorizes a maintained webview shell.
3. Human account/session identity is distinct from actor identity, capability
   authority, governance verdicts, and execution authority.
4. The console may present evidence and submit API requests, but it cannot grant
   itself authority or bypass the execution gate.
5. Local single-owner delivery is the first account target. The data model must
   preserve a later path to multiple human accounts.
6. SQLite is the local development default and PostgreSQL is the deployed database
   target; neither account store is implemented yet.
7. Android remains read-only until a separate mobile threat model authorizes any
   review or approval actions.
8. The existing PyQt desktop client remains a read-only development surface. Its
   distribution licensing and long-term role are unresolved.

## Consequences

- The web console is built once and reused rather than duplicating feature logic in
  native desktop UI.
- API bearer tokens remain machine/development credentials and must not be presented
  as human login.
- Human authentication, secure sessions, recovery, MFA, and administration are a
  distinct implementation phase with their own tests and security acceptance.
- Unimplemented navigation is labeled as planned and remains non-interactive.

## Evidence

- Active plan: `docs/operations/HUMAN_INTERFACE_IMPLEMENTATION_PLAN.md`
- Console: `apps/web/operator-console`
- Dashboard contract: `GET /api/v1/dashboard`
- Frozen API baseline: `docs/api/openapi-baseline.json`
