# Project-AI Containerization Status

## ✓ Running Services

| Service | Container | Image | Port | Status |
|---------|-----------|-------|------|--------|
| API | project-ai-api | project-ai:api | 127.0.0.1:8000 | ✓ Healthy |
| SWR | project-ai-swr | project-ai:service | Internal (8000) | ✓ Healthy |
| Atlas | project-ai-atlas | project-ai:service | Internal (8000) | ✓ Healthy |
| Arbiter-RLP | project-ai-arbiter-rlp | project-ai:service | Internal (8000) | ✓ Healthy |
| Genesis | project-ai-genesis | project-ai:genesis | Internal (8080) | ✓ Healthy |

## ✗ Issues

### Web Portals (Blocked)
- **Services:** docs-portal, proof-portal
- **Status:** Not containerized
- **Issue:** TypeScript workspace resolution failing in Docker
  - `pnpm` workspace packages (`@project-ai/web-shared`) not being resolved during build
  - `lucide-react` dependency also unresolved
  - Likely cause: pnpm workspace symlinks not working correctly in multi-stage Docker builds
  
**Workaround options:**
1. Build web locally (`pnpm --filter "@project-ai/docs-portal" build`), commit dist, copy into Docker
2. Use single-stage build with full workspace (larger image)
3. Pre-build and publish `@project-ai/web-shared` to npm registry
4. Fix pnpm lockfile or workspace configuration

## ✓ Optimizations Applied

- Multi-stage builds (Python, Node, Rust)
- Layer caching: lock files copied before source code
- Security hardening: read-only root, no-new-privileges, CAP_DROP [ALL]
- Health checks: all services
- Explicit networks: all services on `project-ai_services` bridge
- Non-root user: UID 10001
- Internal-only services use `expose:` (no port publish)

## Port Ledger

See `docs/PORT_LEDGER.md` for complete port assignments and reserved ranges.

## Quick Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api
docker compose logs -f swr
docker compose logs -f genesis

# Test API health
curl http://127.0.0.1:8000/health/live

# Stop all
docker compose down

# Clean rebuild
docker compose build --no-cache
docker compose up -d
```

## Environment

See `.env.example` for required variables. Currently `PROJECT_AI_API_TOKEN` is optional (defaults to empty string).
