<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

Edition V1 CTS-5 (Multi-Tenant Surface) Overview

- CTS-5 adds multi-tenant federation, tenant isolation, and API-key based public surface gating for CTS-5 readiness.
- Public API surface remains CTS-4 compatible; CTS-5 introduces per-tenant permissions, surface segmentation, and enhanced governance isolation.
- Authentication: public endpoints rely on API keys configured in ENV; tenants have dedicated keys and tenant context header.
- Operational posture: cross-tenant governance hooks, tenant-scoped audit trails, and scalable rate limits.

Key Prerequisites

- Environment variables AMBASSADOR_API_KEYS (comma-separated keys) and AMBASSADOR_TENANT_MAP (JSON mapping tenant_id -> api_key).
- New headers: X-Tenant-Id must be provided for tenant-scoped requests.
- Public onboarding for tenants; privacy policy and consent flow in place.

Next Steps

- Wire into EditionV1 CI for CTS-5 surface while keeping CTS-4 green in main branch.
- Implement per-tenant dashboards and audit bundles; implement tenant-specific policy bindings.
- CTS-5 adds multi-tenant federation, tenant isolation, and API-key based public surface gating for CTS-5 readiness.
- Public API surface remains CTS-4 compatible; CTS-5 introduces per-tenant permissions, surface segmentation, and enhanced governance isolation.
- Authentication: public endpoints rely on API keys configured in ENV; tenants have dedicated keys and tenant context header.
- Operational posture: cross-tenant governance hooks, tenant-scoped audit trails, and scalable rate limits.
-
- Prerequisites
- Environment variables AMBASSADOR_API_KEYS (comma-separated keys) and AMBASSADOR_TENANT_MAP (JSON mapping tenant_id -> api_key).
- New headers: X-Tenant-Id must be provided for tenant-scoped requests.
- Public onboarding for tenants; privacy policy and consent flow in place.
-
- Next Steps
- Wire into EditionV1 CI for CTS-5 surface while keeping CTS-4 green in main branch.
- Implement per-tenant dashboards and audit bundles; implement tenant-specific policy bindings.
