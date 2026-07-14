# Project-AI Port Ledger
# Single source of truth for all service port assignments.
# Format: SERVICE | CONTAINER PORT | HOST BINDING | PROTOCOL | PURPOSE | VISIBILITY

# ── Published (reachable from host) ───────────────────────────────────────

api             | 8000 | 127.0.0.1:8000 | HTTP | FastAPI/Uvicorn main gateway    | loopback-only
docs-portal     | 8080 | 127.0.0.1:4173 | HTTP | Documentation portal (Nginx)    | loopback-only
proof-portal    | 8080 | 127.0.0.1:4174 | HTTP | Proof portal (Nginx)            | loopback-only

# ── Internal only (expose:, reachable within Docker network only) ─────────

swr             | 8000 | —              | HTTP | Stimulus-response service        | internal
atlas           | 8000 | —              | HTTP | Atlas governance service         | internal
arbiter-rlp     | 8000 | —              | HTTP | Arbiter / RLP service            | internal
genesis         | 8080 | —              | HTTP | Genesis emitter (Rust)           | internal

# ── Reserved for future expansion ─────────────────────────────────────────

# 4175–4180   Additional web portals (same internal 8080 pattern)
# 8001–8010   Additional Python services (same internal 8000 pattern)
# 9000–9010   Monitoring stack (Prometheus :9090, Grafana :3000, etc.)
# 5432        PostgreSQL (pgvector — operationalmemorysystem, already in use on host :5433)

# ── Rules ─────────────────────────────────────────────────────────────────

# 1. All host bindings use 127.0.0.1 (loopback). Never 0.0.0.0 in production.
# 2. Services that are only consumed by other services use expose:, not ports:.
# 3. Health checks use the same port as the service (no separate health port).
# 4. New portals: increment host port from 4175 upward; keep container port 8080.
# 5. New services: keep container port 8000; no host binding unless explicitly needed.
# 6. The Docker bridge network is named project-ai_services.
#    Container DNS: http://api:8000, http://genesis:8080, etc.

# ── CI/CD image registry (GHCR) ───────────────────────────────────────────

# ghcr.io/<owner>/project-ai-api
# ghcr.io/<owner>/project-ai-docs-portal
# ghcr.io/<owner>/project-ai-proof-portal
# ghcr.io/<owner>/project-ai-swr
# ghcr.io/<owner>/project-ai-atlas
# ghcr.io/<owner>/project-ai-arbiter-rlp
# ghcr.io/<owner>/project-ai-genesis
