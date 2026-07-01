# API Reference

> Canonical operator reference for the Project-AI development FastAPI gateway.
> Source of truth: `packages/api/src/project_ai_api/app.py`. This document
> is generated from the route definitions; if it disagrees with the source,
> the source wins and this file is stale.

**Status:** live reference for the development gateway (version `0.0.0.dev0`).
**Base URL (local dev):** `http://127.0.0.1:8000`
**Base URL (Compose):** `http://api:8000` from within the Compose network
**OpenAPI schema (live):** `http://127.0.0.1:8000/openapi.json`
**Interactive docs (live):** `http://127.0.0.1:8000/docs` (FastAPI Swagger UI)

---

## 0. Authentication

The gateway exposes **public** and **protected** routes.

- **Public** routes: no auth required, no token needed.
- **Protected** routes: require both:
  1. `PROJECT_AI_API_TOKEN` configured on the server (non-empty)
  2. `PROJECT_AI_AUDIT_PATH` configured on the server (writable path)
  3. `Authorization: Bearer <token>` header on the request, where `<token>` is
     the server-side `PROJECT_AI_API_TOKEN` value (constant-time compared via
     `hmac.compare_digest`)

**Fail-closed behavior:**

| Server state | Protected-route behavior |
|---|---|
| `PROJECT_AI_API_TOKEN` empty or unset | `503 Service Unavailable` (no auth check runs) |
| `PROJECT_AI_AUDIT_PATH` empty or unset | `503 Service Unavailable` |
| `PROJECT_AI_API_TOKEN` set, missing `Authorization` header | `401 Unauthorized` with `WWW-Authenticate: Bearer` |
| Wrong scheme (not `Bearer`) or wrong token | `401 Unauthorized` with `WWW-Authenticate: Bearer` |
| Correct `Authorization: Bearer <token>` | route runs |

The 503-vs-401 distinction is intentional: 503 means "this surface is not
configured for this environment" (not an auth failure), 401 means "the
caller failed to authenticate."

---

## 1. Public routes

### `GET /health/live`

Liveness probe. Returns immediately, no auth, no side effects.

**Response 200:**
```json
{
  "status": "live",
  "version": "0.0.0.dev0"
}
```

**Use:** container healthcheck (already wired in `compose.yaml` for the `api`
service), k8s liveness probe, smoke test.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/health/live
```

---

### `GET /dois`

Returns the static DOI catalog (papers ingested from the legacy `Project-AI
Papers` corpus, SHA-256 verified per `docs/reference/INGEST_MANIFEST.md`).

**Response 200:**
```json
{
  "dois": [
    {
      "title": "...",
      "doi": "10.5281/zenodo....",
      "domain": "...",
      "url": "https://doi.org/..."
    }
  ]
}
```

**Use:** reference for citation lookup, oracle registry verification.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/dois | python -m json.tool
```

---

### `GET /replay/status`

Returns the current canonical-replay status from the deterministic replay
system ported in Phase J2.9.

**Response 200:**
```json
{
  "replay": {
    "bundle_count": <int>,
    "last_verified_at": "<iso8601 or null>",
    "chain_intact": <bool>
  }
}
```

**Use:** sanity check that the replay system is initialized; `chain_intact`
must be `true` for production readiness.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/replay/status
```

---

### `GET /atlas/status`

Returns the Atlas subordination notice. Atlas is a **read-only analytical
projection service**; this endpoint proves the notice is in effect.

**Response 200:**
```json
{
  "subordination_notice": "Atlas is an analytical projection service ..."
}
```

**Use:** governance proof that atlas refuses to grant authority. See
`packages/atlas/src/atlas/__init__.py` for the notice text source.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/atlas/status
```

---

## 2. Protected routes

All require `Authorization: Bearer $PROJECT_AI_API_TOKEN`.

### `GET /audit`

Reads the last N entries from the append-only Chimera audit log (stored at
`PROJECT_AI_AUDIT_PATH`).

**Query parameters:**

| Name | Type | Default | Range | Description |
|---|---|---|---|---|
| `limit` | int | 100 | 1..500 | Maximum records to return (most-recent first) |

**Response 200:**
```json
{
  "events": [
    {
      "event": "<event-type>",
      "hash": "<sha256-hex>",
      "prev_hash": "<sha256-hex or null>",
      "ts": "<iso8601>",
      "<event-specific-fields>": "..."
    }
  ]
}
```

**Response 401:** missing or invalid bearer token.
**Response 503:** server-side `PROJECT_AI_API_TOKEN` or `PROJECT_AI_AUDIT_PATH` not configured.

**Curl:**
```bash
curl -s -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     "http://127.0.0.1:8000/audit?limit=50" | python -m json.tool
```

---

### `POST /chimera/verdict`

Relays a Chimera governance verdict to the append-only audit log. The
gateway does **not** make governance decisions — it only records that
a verdict was issued. Governance itself lives in `packages/governance/`.

**Request body:**
```json
{
  "action_id": "<uuid-or-action-identifier>",
  "verdict": "ALLOW",
  "source": "operator-cli"
}
```

`verdict` is one of the three canonical outcomes: `ALLOW`, `DENY`, `ESCALATE`.

**Response 202 (Accepted):**
```json
{
  "event": "chimera.verdict",
  "hash": "<sha256-hex of the new audit record>"
}
```

**Response 401:** see Auth.
**Response 503:** see Auth.
**Response 422:** request body failed Pydantic validation (unknown verdict
value, missing field, wrong type).

**Curl:**
```bash
curl -s -X POST \
     -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"action_id":"act-001","verdict":"ALLOW","source":"manual-test"}' \
     http://127.0.0.1:8000/chimera/verdict
```

---

### `POST /chimera/canary`

Relays a Chimera canary hit (a tripped decoy token indicating a probe or
intrusion attempt). Stores only the SHA-256 fingerprint of the canary
value, never the raw value.

**Request body:**
```json
{
  "canary_value": "<the-tripped-canary-string>",
  "context": "operator-canary-test"
}
```

**Response 202 (Accepted):**
```json
{
  "event": "chimera.canary",
  "hash": "<sha256-hex of the new audit record>"
}
```

**Response 401:** see Auth.
**Response 503:** see Auth.
**Response 422:** request body failed validation.

**Curl (using a file for the canary value, never inline in shell history):**
```bash
echo -n "tripwire-2026-06-30-aaa" > /tmp/canary.txt
curl -s -X POST \
     -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"canary_value\":\"$(cat /tmp/canary.txt)\",\"context\":\"smoke-test\"}" \
     http://127.0.0.1:8000/chimera/canary
rm /tmp/canary.txt
```

---

### `POST /atlas/sludge`

Generates an SS-only (Sludge Stack) fictional narrative from a Reality Stack
snapshot. This is the Phase J2.7 Sludge sandbox port; it produces an
**isolated fictional artifact** and does not grant authority or actuate a
decision. The endpoint records an `atlas.sludge_narrative` audit event.

**Request body:**
```json
{
  "rs_snapshot": { "<reality-stack-key>": "<value>" },
  "archetypes": ["hidden_elites"]
}
```

`archetypes` is optional; when omitted, defaults are used. Valid values are
the `NarrativeArchetype` enum (see `packages/atlas/src/atlas/sludge_sandbox.py`).

**Response 202 (Accepted):**
```json
{
  "hash": "<sha256-hex of the new audit record>",
  "narrative": {
    "narrative_id": "<uuid>",
    "archetypes": ["hidden_elites"],
    "stack": "SS",
    "source_snapshot_sha256": "<sha256 of rs_snapshot>",
    "content": "..."
  }
}
```

**Response 401:** see Auth.
**Response 503:** see Auth.
**Response 422:** snapshot failed validation, or the sludge sandbox raised
`SludgeSandboxError` (e.g., contamination check failed).

**Curl:**
```bash
cat > /tmp/snapshot.json <<'EOF'
{
  "rs_snapshot": {"actor": "operator-test", "domain": "smoke"},
  "archetypes": ["hidden_elites"]
}
EOF
curl -s -X POST \
     -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d @/tmp/snapshot.json \
     http://127.0.0.1:8000/atlas/sludge
rm /tmp/snapshot.json
```

---

## 3. Error response shapes

The gateway uses standard HTTP status codes plus a JSON `detail` field for
human-readable error context:

| Status | Meaning | Shape |
|---|---|---|
| 401 | Invalid or missing bearer token | `{"detail": "Invalid bearer token"}` with `WWW-Authenticate: Bearer` header |
| 422 | Request body or query failed Pydantic validation | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| 503 | Protected surface not configured (token or audit path missing) | `{"detail": "Protected API surfaces are not configured"}` |

---

## 4. Rate limits and quotas

The development gateway does not implement rate limiting. Production
deployments must place a reverse proxy (nginx, Envoy) in front of the
gateway and apply per-token rate limits. The gateway's
`x-python-security` Compose hardening does not include rate limits by
design — see `docs/operations/PERFORMANCE_SLOS.md` (to be authored) for
the recommended targets.

---

## 5. CORS

The development gateway does not enable CORS. Browser-based callers must
proxy through a same-origin web portal. The `docs-portal` and `proof-portal`
Compose services are configured to do this correctly.

---

## 6. Source of truth

This document is generated by reading the FastAPI route decorators in
`packages/api/src/project_ai_api/app.py`. If a route changes shape,
auth model, or response format, **update this file in the same commit**.

The auto-generated OpenAPI schema is always available at runtime:
- `http://127.0.0.1:8000/openapi.json` — machine-readable
- `http://127.0.0.1:8000/docs` — Swagger UI
- `http://127.0.0.1:8000/redoc` — ReDoc UI
