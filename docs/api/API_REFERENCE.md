# API Reference

> Canonical operator reference for the Project-AI development FastAPI gateway.
> Source of truth: `packages/api/src/project_ai_api/app.py`. This document
> is maintained against the route definitions and checked by the frozen
> OpenAPI snapshot. If it disagrees with runtime, runtime wins and this file
> must be corrected.

**Status:** live reference for the development gateway (version `0.0.0.dev0`).
**Base URL (local dev):** `http://127.0.0.1:8000`
**Base URL (Compose):** `http://api:8000` from within the Compose network
**OpenAPI schema (live):** `http://127.0.0.1:8000/openapi.json`
**OpenAPI schema (frozen):** `docs/api/openapi-baseline.json`
**Interactive docs (live):** `http://127.0.0.1:8000/docs` (FastAPI Swagger UI)

---

## 0. Authentication

The gateway has two intentionally separate authentication lanes:

- Human Control Center access uses an opaque server-side session in the
  `project_ai_session` HttpOnly cookie. State changes also require the per-session
  `X-CSRF-Token`; browser auth mutations are same-origin only.
- Machine actuation uses `Authorization: Bearer $PROJECT_AI_API_TOKEN`. A human
  session never satisfies Chimera or Atlas actuation authentication.

`GET /api/v1/instance` is a public presentation-identity route used before login.
It reports the configured `PROJECT_AI_INSTANCE_NAME`, identifies the deployment as a
local sovereign instance, and explicitly reports that neither machine identity nor an
execution capability exists in the browser. The display name is not a credential,
machine attestation, or authority grant.

Human auth storage uses `PROJECT_AI_DATABASE_URL` for shared PostgreSQL deployments.
When that variable is absent, direct single-process/local development may use
`PROJECT_AI_ACCOUNT_DB` and `PROJECT_AI_WORKFLOW_DB` SQLite paths. PostgreSQL takes
precedence when both modes are configured. The exactly-once, loopback-only Owner
bootstrap additionally requires `PROJECT_AI_SETUP_SECRET`; TOTP requires
`PROJECT_AI_MFA_KEY`. Set `PROJECT_AI_SESSION_COOKIE_SECURE=true` behind HTTPS.
The server-only `PROJECT_AI_EXECUTION_SECRET` enables one-use capability issuance for
the bounded SWR workflow. It is never sent to the browser. SWR execution additionally
requires a valid `PROJECT_AI_AUDIT_PATH`. `PROJECT_AI_SWR_BUNDLE_DIR` may select a
writable result-export directory; when omitted, configured deployments place it beside
the audit file. Compose and Helm set it to `/data/swr-bundles`.
Local Compose sets `PROJECT_AI_BOOTSTRAP_TRUST_PRIVATE_PROXY=true` so the loopback-only
bootstrap can traverse its private same-origin Nginx proxy. Do not set that flag for an
untrusted or internet-facing proxy path.

Human routes:

| Method and path | Purpose |
|---|---|
| `GET /api/v1/instance` | Identify the connected local sovereign instance and browser trust boundary |
| `GET /api/v1/auth/bootstrap-status` | Report unconfigured, setup-required, or closed state |
| `POST /api/v1/auth/bootstrap` | Create the one local Owner and show recovery codes once |
| `POST /api/v1/auth/login` | Establish a human session |
| `GET /api/v1/auth/session` | Read the current session |
| `POST /api/v1/auth/session/refresh` | Rotate the current session and CSRF token |
| `POST /api/v1/auth/logout` | Revoke the current session |
| `GET /api/v1/auth/sessions` | List the user's sessions |
| `DELETE /api/v1/auth/sessions/{session_id}` | Revoke one of the user's sessions |
| `POST /api/v1/auth/password/change` | Change password and revoke all sessions |
| `POST /api/v1/auth/recovery/start` | Return a non-enumerating recovery instruction |
| `POST /api/v1/auth/recovery/complete` | Consume a one-time recovery code and reset password |
| `GET /api/v1/me` | Return the signed-in account |
| `GET/POST/DELETE /api/v1/auth/mfa...` | Enroll, confirm, step up, inspect, or remove TOTP |
| `GET/POST /api/v1/admin/accounts...` | Permission-enforced account, role, and status administration |
| `GET /api/v1/admin/security-events` | Authentication security-event evidence |
| `GET /api/v1/work/operations` | Server allowlist with versioned structured-input contracts for non-actuating requests |
| `GET/POST /api/v1/work/requests...` | Schema-validated non-actuating request, creator cancellation, and MFA-guarded review records |
| `GET /api/v1/work/requests/{request_id}` | Permission-checked request detail, exact structured inputs, input digest, and immutable human-review receipt digests |
| `GET /api/v1/modules/swr/scenarios` | Canonical deterministic SWR scenario catalog and configuration status |
| `POST /api/v1/work/requests/{request_id}/execute/swr` | MFA-guarded, reviewed, exact-scope SWR execution-gate submission |
| `POST /api/v1/modules/atlas/replay` | Session/CSRF/permission-checked deterministic Atlas evidence reconstruction |
| `GET/POST /api/v1/modules/atlas/projections` | Permission-checked durable Atlas projection history and deterministic analysis creation |
| `GET /api/v1/modules/atlas/projections/{receipt_id}` | Durable Atlas projection input, output, and audit evidence detail |

Passwords, recovery codes, raw session tokens, raw CSRF tokens, and raw TOTP seeds are
not stored. Human review never creates a canonical governance verdict or starts execution.
Request creation accepts only operation identifiers and exact field sets returned by
`GET /api/v1/work/operations`; free-form operations, missing/extra input fields, unsafe
identifier formats, or resource/input conflicts return `409`. The server derives the
canonical resource, persists the schema version and canonical JSON values, and returns a
SHA-256 input receipt so the reviewed values remain independently identifiable.
Request detail exposes each durable human review with a stable SHA-256 receipt over its
immutable fields. A reviewed `scenario.prepare` request whose resource exactly names a
canonical SWR scenario may be submitted by a permitted, recently MFA-verified operator.
The server issues and consumes the scoped capability internally, runs governance and the
execution gate, appends a durable audit record, and stores the result, governance-evidence
digest, execution-event hash, and audit hash in one receipt. Repeating the endpoint returns
the existing receipt without rerunning the scenario. This first bounded workflow accepts
only the scenario's canonical deterministic decision; arbitrary responses are rejected
until request payloads themselves become reviewable durable records.

The machine lane exposes **public** and **protected** routes:

- **Public** routes: no auth required, no token needed.
- **Protected** routes require all three:
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

Returns the current injected canonical-replay checkpoint.

**Response 200:**
```json
{
  "status": "not_run | pass | fail",
  "invariants_passed": 0,
  "invariants_total": 5,
  "updated_at": ""
}
```

The default state is deliberately `not_run`; the API never upgrades it to a
passing claim without injected replay evidence.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/replay/status
```

---

### `GET /api/v1/dashboard`

Read-only aggregator for the operator console foundation. It exposes only
current gateway, replay, audit-chain configuration/integrity, and DOI registry
state. The `work_items` array remains empty until a real authorized work API
exists.

**Response 200 (abridged):**
```json
{
  "status": "ready",
  "version": "0.0.0.dev0",
  "maturity": "development",
  "authority_boundary": "The Control Center presents evidence and requests. It does not grant authority; ...",
  "surfaces": [
    {
      "id": "gateway",
      "label": "Gateway",
      "status": "healthy",
      "metric": "0.0.0.dev0",
      "detail": "Development gateway is live."
    }
  ],
  "doi_records": 21,
  "work_items": []
}
```

**Curl:**
```bash
curl -s http://127.0.0.1:8000/api/v1/dashboard | python -m json.tool
```

---

### `GET /atlas/status`

Returns the Atlas subordination notice. Atlas is an **analysis-only service**;
this endpoint proves the notice is in effect. Human replay verification remains
non-actuating, while machine-authenticated generation retains its separate boundary.

**Response 200:**
```json
{
  "status": "available",
  "version": "0.0.0.dev0",
  "stack": "Atlas",
  "authority": "analysis_only",
  "protected_operations": ["sludge_narrative"],
  "subordination_notice": "...not a decision, authority grant, or actuation..."
}
```

**Use:** governance proof that atlas refuses to grant authority. See
`packages/atlas/src/atlas/__init__.py` for the notice text source.

**Curl:**
```bash
curl -s http://127.0.0.1:8000/atlas/status
```

---

### `POST /api/v1/modules/atlas/replay`

Accepts a portable Atlas replay bundle from a signed-in account with
`modules.analysis.run`, verifies its canonical hash binding, reconstructs the evidence
summary deterministically, and appends a bounded audit receipt. The request, including
its JSON envelope, must not exceed 256 KB.

This endpoint performs analysis only. It creates no governance verdict, issues no
capability, calls no execution gate, and accepts no browser machine token. Raw bundle
content is not copied into the audit relay; only the account identifier, bundle ID,
bundle hash, and reconstructed-state hash are recorded.

**Response 200:** returns `status: verified`, the bundle and reconstructed-state
SHA-256 values, five item counts, the Atlas subordination notice, and a durable audit
receipt SHA-256. Invalid or tampered bundles return `422`; oversized requests return
`413`; an unavailable or invalid audit chain fails closed with `503`.

---

### `GET/POST /api/v1/modules/atlas/projections`

Creates and lists deterministic Atlas projections for signed-in accounts with
`modules.analysis.run`. Creation requires same-origin and CSRF checks, a unique
idempotency key, one to twelve bounded drivers, up to twelve evidence items, and a
request no larger than 256 KB. The server canonicalizes evidence and drivers before
hashing and calls the real Atlas `analyze` contract.

Each result persists the canonical input JSON, output JSON, their SHA-256 values, the
Atlas projection SHA-256, initiating account, and append-only audit hash in workflow
schema version 4. Repeating the same idempotency key and input returns the original
receipt; changed input with that key returns `409`. Audit records contain identifiers
and hashes, not raw claim statements or evidence sources.

These endpoints perform analysis only. Responses explicitly state
`recommendation_created=false`, `governance_verdict_created=false`, and
`execution_started=false`. They issue no capability and do not call the execution gate.

`GET /api/v1/modules/atlas/projections/{receipt_id}` returns the complete durable receipt
only when it is an Atlas projection record; other analysis receipt types are not exposed
through this route.

---

## 2. Protected routes

All actuation routes require `Authorization: Bearer $PROJECT_AI_API_TOKEN`.
`GET /audit` accepts either that machine credential or a valid human session.

### `GET /audit`

Verifies the append-only Chimera audit log (stored at `PROJECT_AI_AUDIT_PATH`),
then returns a bounded, newest-first page. Filtering never bypasses full-chain
verification.

**Query parameters:**

| Name | Type | Default | Range | Description |
|---|---|---|---|---|
| `limit` | int | 100 | 1..500 | Maximum records to return (most-recent first) |
| `offset` | int | 0 | 0 or greater | Number of matching newest-first records to skip |
| `query` | string | empty | 200 characters | Case-insensitive search across the serialized record |
| `event` | string | empty | 120 characters | Exact, case-insensitive event-type filter |

**Response 200:**
```json
{
  "chain_valid": true,
  "count": 1,
  "filtered_count": 1,
  "offset": 0,
  "limit": 100,
  "records": [
    {
      "event": "<event-type>",
      "hash": "<sha256-hex>",
      "prev_hash": "<sha256-hex or null>",
      "timestamp": "<iso8601>",
      "<event-specific-fields>": "..."
    }
  ]
}
```

**Response 401:** missing or invalid machine credential and no valid human session.
**Response 503:** server-side `PROJECT_AI_API_TOKEN` or `PROJECT_AI_AUDIT_PATH` not configured.

The Control Center can export the currently displayed verified page as JSON. The
export includes chain-verification state and active filters; it does not grant
machine authority or alter the audit log.

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

Human login, recovery, and MFA paths use durable source/account rate-limit records;
PostgreSQL updates them under row locks so replicas share one limit. Audit export and
other expensive read routes still need deployment-level quotas before internet exposure.

---

## 5. CORS

The gateway does not enable CORS. Browser callers must use a same-origin proxy. Vite
development servers, the Compose Nginx operator-console service, and the Helm ingress
provide that path. Deployment TLS and trusted-proxy configuration remain operator
responsibilities.

---

## 6. Source of truth

`packages/api/src/project_ai_api/app.py` is runtime truth. The checked-in
`docs/api/openapi-baseline.json` is regenerated with:

```bash
uv run python tools/export_openapi.py
```

`packages/api/tests/test_api.py::test_openapi_baseline_matches_runtime`
fails when runtime and the frozen contract drift. If a route changes shape,
auth model, or response format, update the schema and this human reference in
the same commit.

The auto-generated OpenAPI schema is always available at runtime:
- `http://127.0.0.1:8000/openapi.json` — machine-readable
- `http://127.0.0.1:8000/docs` — Swagger UI

ReDoc is disabled (`redoc_url=None`).
