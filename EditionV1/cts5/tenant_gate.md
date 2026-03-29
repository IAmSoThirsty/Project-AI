<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / tenant_gate.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / tenant_gate.md # -->
<!-- # ============================================================================ #

Tenant Gate Architecture (CTS-5)

- Tenant Isolation: Each tenant has an isolated governance domain with separate policy bindings and audit trail segments.
- API keys: Per-tenant keys map to tenant IDs; requests must include X-Tenant-Id and X-Api-Key headers.
- Audit: Tenant-scoped audit blocks appended to a tenant-specific segment; cross-tenant aggregation only with explicit cross-tenant governance approvals.
- Compliance: Cross-tenant compliance bundling is supported with TSA sign-offs and cross-tenant dependencies.

Usage Example

- curl -X POST -H "X-Tenant-Id: tenantA" -H "X-Api-Key: KEY_FOR_TENANT_A" -H "Content-Type: application/json" -d '{"action":"read_status"}' https://your-host/ambassador/action
