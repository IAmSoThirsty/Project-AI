# API Reference

> Canonical operator reference for the Project-AI development FastAPI gateway.
> Source of truth: `packages/api/src/project_ai_api/app.py`. This document
> is maintained against the route definitions and checked by the frozen
> OpenAPI snapshot. If it disagrees with runtime, runtime wins and this file
> must be corrected.

**Status:** live reference for the v0.0.3 successor gateway.
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
- Machine actuation uses a durable per-program bearer credential. A human session
  never satisfies Chimera or Atlas actuation authentication. Development may use
  `PROJECT_AI_API_TOKEN` as an explicit fallback; production sets
  `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true` and provisions one scoped
  credential per program through the owner/MFA administration API.

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
When `THIRSTYS_V3Q_REQUIRED=true`, the SWR execution request may carry externally signed
`v3q_authority_proof` and `v3q_approval_proof` documents. The API transports these
public authorization artifacts to the execution gate; it never creates, stores, or
mounts the corresponding private signing key. Missing or invalid proofs fail closed.
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
| `GET/POST /api/v1/admin/machine-credentials` | Owner/MFA-protected per-program credential inventory and one-time token issuance |
| `POST /api/v1/admin/machine-credentials/{id}/revoke` | Revoke one machine credential without rotating other programs |
| `GET /api/v1/admin/security-events` | Authentication security-event evidence |
| `GET /api/v1/work/operations` | Server allowlist with versioned structured-input contracts for non-actuating requests |
| `GET/POST /api/v1/work/requests...` | Schema-validated non-actuating request, creator cancellation, and MFA-guarded review records |
| `GET /api/v1/work/requests/{request_id}` | Permission-checked request detail, exact structured inputs, input digest, and immutable human-review receipt digests |
| `GET /api/v1/modules/swr/scenarios` | Canonical deterministic SWR scenario catalog and configuration status |
| `GET /api/v1/modules/waterfall/status` | Machine-authenticated copied/standalone Waterfall status and shared-authority configuration |
| `POST /api/v1/modules/waterfall/operations` | Machine-authenticated allow-listed Waterfall operation through V3Q and ExecutionGate |
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
- **Protected** routes require an audit path and a bearer credential with the
  route's scope: `evidence.read`, `evidence.write`, or `analysis.generate`.
  When durable credentials are configured/enforced, the token is resolved from
  the accounts store; only its salted hash is stored and revocation is per
  credential. Machine writes include the credential id and label in the audit
  record. Development fallback uses `PROJECT_AI_API_TOKEN`.

**Fail-closed behavior:**

| Server state | Protected-route behavior |
|---|---|
| No audit path, or no credential backend/token in the selected mode | `503 Service Unavailable` (no auth check runs) |
| `PROJECT_AI_AUDIT_PATH` empty or unset | `503 Service Unavailable` |
| Configured mode, missing `Authorization` header | `401 Unauthorized` with `WWW-Authenticate: Bearer` |
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
  "version": "0.0.3"
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
  "version": "0.0.3",
  "maturity": "development",
  "authority_boundary": "The Control Center presents evidence and requests. It does not grant authority; ...",
  "surfaces": [
    {
      "id": "gateway",
      "label": "Gateway",
      "status": "healthy",
      "metric": "0.0.3",
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
  "version": "0.0.3",
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

All actuation routes require `Authorization: Bearer <scoped-machine-credential>`.
`GET /audit` accepts either that machine credential or a valid human session.
`POST /audit/search` is the preferred human-console read path: it accepts only a valid
same-origin human session and keeps filter identifiers out of request URLs/access logs.
It returns normalized summaries rather than arbitrary relay fields. `POST /audit/detail`
resolves one verified record hash and applies server-side field visibility.
`POST /audit/export` accepts only a valid human session with `audit.export` and
same-origin CSRF proof; machine evidence credentials cannot request exports.

### `GET /audit`

Verifies the append-only Chimera audit log (stored at `PROJECT_AI_AUDIT_PATH`),
then returns a bounded, newest-first page. Filtering never bypasses full-chain
verification. Human clients should use the returned hash cursor for stable paging;
`offset` remains available for existing machine/proof clients. A cursor anchors the
next page after the last record previously returned, so newly appended records do not
duplicate or skip older results.

**Query parameters:**

| Name | Type | Default | Range | Description |
|---|---|---|---|---|
| `limit` | int | 100 | 1..500 | Maximum records to return (most-recent first) |
| `offset` | int | 0 | 0 or greater | Number of matching newest-first records to skip |
| `cursor` | SHA-256 hex | empty | 64 lowercase hex characters | Continue after a previously returned page anchor; cannot be combined with nonzero `offset` |
| `query` | string | empty | 200 characters | Case-insensitive search across the serialized record |
| `event` | string | empty | 120 characters | Exact, case-insensitive event-type filter |
| `actor` | string | empty | 200 characters | Exact actor/agent identifier |
| `account` | string | empty | 200 characters | Exact initiating/creating/reviewing account identifier |
| `operation` | string | empty | 200 characters | Exact operation identifier |
| `resource` | string | empty | 300 characters | Exact resource identifier |
| `verdict` | enum | empty | `ALLOW`, `DENY`, `ESCALATE` | Exact canonical verdict/outcome |
| `severity` | string | empty | 40 characters | Exact severity |
| `from_time` | date-time | empty | timezone required | Include records at or after this instant |
| `to_time` | date-time | empty | timezone required | Include records at or before this instant; cannot precede `from_time` |

**Response 200:**
```json
{
  "chain_valid": true,
  "count": 1,
  "filtered_count": 1,
  "offset": 0,
  "limit": 100,
  "cursor": null,
  "next_cursor": "<sha256-hex-or-null>",
  "has_more": true,
  "records": [
    {
      "event": "<event-type>",
      "hash": "<sha256-hex>",
      "previous_hash": "<sha256-hex>",
      "timestamp": "<iso8601>",
      "<event-specific-fields>": "..."
    }
  ]
}
```

**Response 401:** missing or invalid machine credential and no valid human session.
**Response 422:** malformed/unknown cursor, cursor combined with nonzero offset,
timezone-free time boundary, reversed time range, or invalid query value.
**Response 503:** the selected machine-credential mode or
`PROJECT_AI_AUDIT_PATH` is not configured.

**Curl:**
```bash
curl -s -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     "http://127.0.0.1:8000/audit?limit=50" | python -m json.tool
```

---

### `POST /audit/search`

Returns a verified, normalized `HumanAuditResponse` and accepts the stable cursor and
all filters in a JSON request body. The records contain only event, timestamp, chain
hashes, canonical verdict, severity, and verified status; arbitrary relay fields and
raw identifiers are never included in a human search response. This read-only endpoint
requires a valid human session, `evidence.view`, and a same-origin request. Machine bearer
credentials are not accepted. No CSRF token is required because the operation does not
mutate server state.

The operator console uses this endpoint so actor, account, resource, and free-text
filters do not enter browser request URLs or default reverse-proxy access logs.
Owner, administrator, and auditor roles may filter exact actor, account, operation,
and resource values because they hold `audit.raw_view`. Reviewer, operator, and viewer
roles may filter only the visible summary fields; their `query` search is evaluated
against that same summary projection. Supplying a raw-identifier filter without
`audit.raw_view` returns 403, preventing result counts from becoming a hidden-value
oracle.

```json
{
  "limit": 25,
  "cursor": "<sha256-hex-or-null>",
  "query": "action-safe",
  "event": "chimera.verdict",
  "actor": "ACTOR-REVIEWER",
  "account": "account-reviewer",
  "operation": "evidence.inspect",
  "resource": "bundle:approved-42",
  "verdict": "DENY",
  "severity": "high",
  "from_time": "2026-07-21T12:00:00Z",
  "to_time": "2026-07-21T13:00:00Z"
}
```

**Response 200 (record shape):**

```json
{
  "chain_valid": true,
  "count": 42,
  "filtered_count": 1,
  "offset": 0,
  "limit": 25,
  "cursor": null,
  "next_cursor": null,
  "has_more": false,
  "records": [
    {
      "event": "chimera.verdict",
      "timestamp": "2026-07-21T12:30:00Z",
      "source_hash": "<sha256-hex>",
      "previous_hash": "<sha256-hex>",
      "verdict": "DENY",
      "severity": "high",
      "chain_status": "verified"
    }
  ]
}
```

**Response 401:** no valid human session; machine bearer credentials are not accepted.
**Response 403:** cross-origin request, missing `evidence.view`, or a raw-identifier
filter without `audit.raw_view`.
**Response 422:** malformed/unknown cursor, invalid filter value, timezone-free time
boundary, or reversed time range.

---

### `POST /audit/detail`

Verifies the complete append-only chain, resolves one exact record hash, and returns
normalized integrity metadata plus permission-filtered fields. Owner, administrator,
and auditor roles hold `audit.raw_view` and receive a sanitized raw record. Keys that
indicate passwords, tokens, secrets, cookies, authorization, CSRF, TOTP, recovery codes,
or private keys are replaced with `[REDACTED]` even for those roles. Reviewer, operator,
and viewer roles receive the export allowlist projection: identifiers become SHA-256
digests, arbitrary fields are withheld, and `raw_record` is `null`.

The endpoint is same-origin, human-session-only, and requires `evidence.view`. It is a
read-only operation and therefore does not require a CSRF token. Machine bearer
credentials are not accepted.

**Request body:**

```json
{
  "source_hash": "<sha256-hex>"
}
```

**Response 200 (privileged example):**

```json
{
  "chain_valid": true,
  "chain_status": "verified",
  "chain_position": 41,
  "chain_records": 42,
  "visibility": "privileged",
  "event": "chimera.verdict",
  "timestamp": "2026-07-21T12:30:00Z",
  "source_hash": "<sha256-hex>",
  "previous_hash": "<sha256-hex>",
  "fields": {
    "action_id": "action-42",
    "api_token": "[REDACTED]",
    "verdict": "DENY"
  },
  "redacted_fields": ["api_token"],
  "raw_record": {
    "event": "chimera.verdict",
    "hash": "<sha256-hex>",
    "previous_hash": "<sha256-hex>",
    "timestamp": "2026-07-21T12:30:00Z",
    "action_id": "action-42",
    "api_token": "[REDACTED]",
    "verdict": "DENY"
  }
}
```

**Response 401:** no valid human session; machine bearer credentials are not accepted.
**Response 403:** cross-origin request or missing `evidence.view` permission.
**Response 404:** the hash does not identify a record in the verified snapshot.
**Response 422:** malformed source hash.
**Response 503:** audit storage is unavailable or the complete chain is invalid.

---

### `POST /audit/export`

Creates a bounded, redacted JSON export after verifying the complete source chain.
The server requires the separate `audit.export` human-interface permission, validates
same-origin CSRF proof, limits each export to 500 matching records, and applies a strict
field allowlist. Unknown and free-form event fields are omitted and named in each
record's `redacted_fields`. The canonical `records_sha256` covers exactly the returned
redacted records. A hash-linked `control_center.audit_export` receipt records only the
requesting account, counts, bounds, filter digest, and records digest.

Export filtering follows the same visibility boundary as interactive search. Exact
actor, account, operation, and resource filters require `audit.raw_view`; without that
permission, `query` searches only the visible summary projection. This applies even to
roles that hold `audit.export` so matched-record counts cannot disclose hidden values.

**Request body:**

```json
{
  "limit": 500,
  "offset": 0,
  "query": "action-safe",
  "event": "chimera.verdict",
  "actor": "ACTOR-REVIEWER",
  "account": "account-reviewer",
  "operation": "evidence.inspect",
  "resource": "bundle:approved-42",
  "verdict": "DENY",
  "severity": "high",
  "from_time": "2026-07-21T12:00:00Z",
  "to_time": "2026-07-21T13:00:00Z"
}
```

**Response 200 (abridged):**

```json
{
  "schema_version": "project-ai.audit-export/v1",
  "generated_at": "<iso8601>",
  "source_chain_valid": true,
  "source_chain_records": 42,
  "matched_records": 3,
  "exported_records": 3,
  "offset": 0,
  "limit": 500,
  "filters": {
    "query": "action-safe",
    "event": "chimera.verdict",
    "actor": "ACTOR-REVIEWER",
    "account": "account-reviewer",
    "operation": "evidence.inspect",
    "resource": "bundle:approved-42",
    "verdict": "DENY",
    "severity": "high",
    "from_time": "2026-07-21T12:00:00Z",
    "to_time": "2026-07-21T13:00:00Z"
  },
  "redaction_applied": true,
  "redaction_policy": "allowlist-v1",
  "records_sha256": "<sha256-hex>",
  "export_audit_hash": "<sha256-hex>",
  "records": [
    {
      "event": "chimera.verdict",
      "timestamp": "<iso8601>",
      "source_hash": "<sha256-hex>",
      "previous_hash": "<sha256-hex>",
      "fields": {"action_id_sha256": "<sha256-hex>", "verdict": "DENY"},
      "redacted_fields": ["action_id", "source"]
    }
  ]
}
```

**Response 401:** no valid human session; machine bearer credentials are not accepted.
**Response 403:** missing/invalid CSRF proof, missing `audit.export`, or a raw-identifier
filter without `audit.raw_view`.
**Response 429:** the durable account/source export quota was exceeded; includes
`Retry-After: 900`.
**Response 422:** invalid filter value, timezone-free time boundary, or reversed time
range. The export manifest intentionally records the exact normalized filters; record
redaction applies to `records`, while the appended audit receipt stores only a digest
of the filter manifest.

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

### `GET /api/v1/modules/atlas/sludge`

Lists verified Sludge generation **metadata** from the append-only audit
chain, newest first. Auth: evidence boundary — a signed-in session with
`EVIDENCE_VIEW` **or** the machine bearer token (the same audience `GET /audit`
serves). The chain is verified before any read; a tampered chain returns 503.

Narrative bodies are never persisted: generation returns the fiction once and
the durable record is metadata plus hashes only, so this surface cannot and
does not claim narrative retrieval (`narrative_bodies_persisted` is always
`false`).

**Query:** `limit` (1–100, default 50), `offset` (≥ 0, default 0).

**Response 200:**
```json
{
  "chain_valid": true,
  "authority": "analysis_only",
  "narrative_bodies_persisted": false,
  "total_count": 1,
  "offset": 0,
  "limit": 50,
  "records": [
    {
      "event": "atlas.sludge_narrative",
      "narrative_id": "SLUDGE-....",
      "source_snapshot_sha256": "<sha256>",
      "archetypes": ["hidden_elites"],
      "stack": "SS",
      "audit_hash": "<sha256 of the audit record>",
      "timestamp": "<ISO-8601>"
    }
  ]
}
```

### `GET /api/v1/modules/atlas/sludge/{narrative_id}`

Single-record variant of the listing above; returns `{"record": {...}}` with
the same shape, or 404 when no verified event matches the id.

### Declared OpenAPI security schemes

The frozen baseline (`docs/api/openapi-baseline.json`) declares two
`components.securitySchemes` and marks every protected operation with them:
`machineBearer` (the shared machine token above) and `sessionCookie` (the
opaque human session cookie). Operations without a `security` entry are
public read-only surfaces. Generated clients therefore see auth requirements
directly from the contract.

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

Human login, recovery, MFA, and audit-export paths use durable source/account rate-limit
records; PostgreSQL updates them under row locks so replicas share one limit. Other
expensive read routes still need deployment-level quotas before internet exposure.

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
