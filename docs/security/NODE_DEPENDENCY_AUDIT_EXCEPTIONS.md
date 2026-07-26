# Node Dependency Audit Exceptions

**Status:** Active, narrow P1 release exception
**Policy:** `tools/node_dependency_audit_policy.json`
**Verifier:** `python tools/verify_node_dependencies.py`

The Node dependency audit remains fail-closed. Unknown advisories, changed
package versions, changed dependency paths, changed severity, expired
exceptions, stale exceptions, and forbidden source usage all fail the job.

## GHSA-qwww-vcr4-c8h2

- Package: `react-router` 7.18.1
- Scope: `apps/web/operator-console`
- Expires: 2026-08-31T00:00:00Z
- Upstream affected feature: unstable React Server Components APIs
- Project-AI usage: Vite client-side browser routing only
- Source boundary: the verifier scans the operator-console source and rejects
  imports or calls associated with the affected RSC surface.
- Upstream fix status when recorded: React Router 8.3.0 was named by the
  advisory but was not published to the npm registry.

This exception is not proof that the package is vulnerability-free. It records
that the affected feature is outside this product's executable surface while
keeping the advisory visible and time-bounded. Remove the exception immediately
when a compatible patched release is available.
