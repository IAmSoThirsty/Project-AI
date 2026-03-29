# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master -->
Edition V1 CTS-5 Production Guide (Monolith)

- Overview: Single-process sovereign monolith including Thirsty-Lang, Shadow Thirst, TARL OS, SOVEREIGN_RUNTIME, OctoReflex, PSIA Waterfall, Liara, Ambassador surface.
- Prerequisites: environment with Python 3.12, Node.js (>= 16), Docker, and a host that can run the monolith and the ambassador surface.
- Setup:
  - Install dependencies via the central repo scripts (build_all.py).
  - Set AMBASSADOR_API_KEYS and AMBASSADOR_TENANT_MAP per CTS-5 requirements.
- Deploy:
  - Start the ambassador surface (python3 -m ambassador.server).
  - Ensure governance surface (SovereignRuntime) is accessible or mocked for staging.
- Validate:
  - GET /health should return ok; GET /status should reflect ambassador readiness and governance presence; POST /action with a valid API key should return allowed and result.
- Rollback:
  - If governance gating fails, revert to a safe, known-good state via rollback runbooks.

- Long-term: For large-scale production, plan multi-region deployment, with a federation strategy for CTS-5 and beyond.
