# Human Account and Session Threat Model

**Status:** Active for the implemented local Owner slice; remaining controls are listed
explicitly.

## Boundary

The human account service authenticates a person to the Control Center. It does not
mint machine credentials, capabilities, governance outcomes, or execution authority.
The browser receives an opaque session cookie; only the server stores account and
session state.

## Protected assets

- Password, recovery-code, session-token, and CSRF-token material
- Human identity and account-to-actor binding
- Active-session inventory and security-event history
- Evidence available to authenticated operators
- The separation between human UI access and machine actuation credentials

## Threats and current controls

| Threat | Current control | Verification |
|---|---|---|
| Password/database disclosure | Cerberus PBKDF2 password hashes; raw passwords are never stored | Account tests inspect the database bytes |
| Session database disclosure | Random opaque tokens; only token and CSRF hashes are stored | Account tests inspect the database bytes |
| Session fixation/replay | Token rotation, idle and absolute expiry, revocation, password-change revocation | Deterministic service and API tests |
| Cross-site request forgery | SameSite cookies, per-session CSRF token/header, and same-origin checks on auth state changes | API denial tests |
| Credential guessing | Durable source throttling and account lockout | Persistence/lockout tests |
| Recovery-code theft/reuse | Hashed one-time codes; successful use revokes all sessions | Recovery tests |
| First-run takeover | Loopback-only bootstrap, explicit setup secret, atomic exactly-once account creation | API/service bootstrap tests |
| Machine-token exposure in UI | Ordinary login never accepts or stores a machine token; actuation routes still require bearer auth | Browser and API authority-boundary tests |
| Account enumeration | Generic recovery-start response and generic invalid-login response | API tests |
| Stale or stolen device | User-visible session list and revocation | Browser/API tests |
| TOTP seed disclosure | Fernet-encrypted seed; key supplied separately from database | Service/API tests inspect stored bytes |
| TOTP replay | Monotonic consumed time-step counter | Deterministic service tests |
| Self-approval | Request creator cannot review the same request | Workflow denial tests |
| Browser capability theft | SWR capability is issued and consumed inside the server; no capability field exists in the browser API | OpenAPI/client inspection and integration tests |
| Review/execution scope drift | SWR operation, scenario resource, approval state, and canonical decision are checked before reservation and again by governance | API mismatch and direct no-bypass tests |
| Duplicate execution | Durable unique request reservation returns the existing receipt across concurrent repository instances | SQLite and live PostgreSQL concurrency tests |
| Unauthorized audit export | Export is a cookie-authenticated POST requiring same-origin CSRF proof and the separate `audit.export` permission; machine evidence-read credentials cannot use it | API role, CSRF, origin, and machine-boundary denial tests |
| Secret or free-form audit data in exports | Export uses an explicit field allowlist, omits every other event field, names omitted fields, and never exports a raw audit record | API redaction and negative-secret assertions |
| Audit export resource exhaustion | Server-side export size is bounded to 500 records and each account/source pair uses the durable five-minute action-rate bucket | Validation and rate-limit tests |
| Untraceable or modified export | Full-chain verification precedes filtering; the response carries a canonical records digest and the relay records a hash-linked `control_center.audit_export` receipt without copying filter text or records | Digest recomputation and audit-receipt tests |
| Cursor tampering, filter drift, or append-time page movement | A cursor is the verified anchor record hash and must exist in the current filtered snapshot; nonzero offsets cannot be combined with cursors. The client retains cursor history, so later appends do not duplicate or skip older evidence | API append-between-pages, invalid-cursor, filter-boundary, and UI navigation tests |
| Ambiguous audit time boundaries | `from_time` and `to_time` require explicit timezone offsets and the server rejects reversed ranges before returning records | API naive-time and reversed-range denial tests |
| Human filter identifiers disclosed in access URLs | The operator console sends filters to the same-origin, human-session-only `POST /audit/search` body; the machine/proof GET remains compatible but is not used by the human UI | API origin/machine denial tests, client request-shape test, and live access-log inspection |
| Raw relay records disclosed through human search | `POST /audit/search` projects every match to a fixed summary containing only event/time, chain hashes, canonical verdict/severity, and verified status | API negative-field assertions and typed client contract |
| Hidden audit values inferred through filters or result counts | Exact actor, account, operation, and resource filters require `audit.raw_view`; lower-privilege free-text queries search only the visible summary projection. Export enforces the same boundary | API role-denial, negative-query, hash-query, and export-filter tests |
| Unauthorized raw audit detail | `POST /audit/detail` requires a same-origin human session and `evidence.view`; only Owner, Administrator, and Auditor roles hold the separate `audit.raw_view` permission | Role-matrix, API redacted/privileged response, origin, and machine-denial tests |
| Credentials disclosed in privileged detail | Credential-bearing field-name fragments are replaced with `[REDACTED]` before either normalized fields or sanitized raw JSON leave the server | API negative-secret and explicit-redaction assertions |
| Audit evidence rendered as executable markup | Raw detail is returned as data and React renders JSON through text nodes inside `code`; no unescaped HTML rendering path exists | Browser DOM assertion and automated accessibility test |
| Stale evidence remains visible after integrity failure | A new query clears prior records and details before verification; any chain failure renders a lockdown state with no cached evidence | UI valid-then-503 regression test |

## Audit export data-flow boundary

The browser may request a redacted JSON export of the current audit query. The server
authenticates the human session, validates same-origin CSRF proof, checks the independent
`audit.export` permission, consumes the durable export rate limit, verifies the entire
append-only chain, applies the bounded filter, and projects each record through a strict
allowlist. The returned digest covers exactly the projected records. Only hashes, counts,
offsets, and the requesting account identifier enter the export audit receipt; raw query
text and record values do not. The browser receives no machine credential and performs no
authority-bearing action.

Interactive audit reads follow a separate read-only boundary. The operator console sends
its cursor and filters in the body of `POST /audit/search`; the server requires a valid
same-origin human session and `evidence.view`. This prevents actor, account, resource,
and free-text filters from entering the request URL or default access logs. The endpoint
does not mutate state and does not accept a machine bearer credential. Exact raw-identifier
filters require `audit.raw_view`; lower-privilege free-text queries search only the fixed
summary projection. The export path applies the same constraint so response counts cannot
be used as a blind oracle for withheld audit values.

Human record detail follows the same session/origin boundary. The browser submits only
the selected source hash to `POST /audit/detail`. The server verifies the complete chain
again, locates that exact hash, and applies `audit.raw_view` before constructing the
response. Lower-privilege roles receive allowlisted fields and hashed identifiers with no
raw record. Privileged roles receive a sanitized raw record, but credential-bearing keys
remain redacted. The browser treats all returned values as text.

## Remaining security work

- Invitation/email delivery, Owner transfer, administrator password reset, and MFA
  enforcement policy are not implemented.
- SQLite remains the local single-process store. PostgreSQL provides transaction-locked
  schema migration, bootstrap, rate limiting, and shared multi-replica state. Live
  concurrency and dump/restore tests have passed; managed-service TLS, credential
  rotation, and live-cluster restore drills remain deployment acceptance work.
- TLS termination acceptance, CSP, external
  penetration testing, and accessibility/security acceptance are pending deployment work.
- Recovery codes are displayed once; the operator remains responsible for storing them
  outside the application database.

## Fail-closed rules

- Missing account storage returns an unavailable state, not anonymous access.
- Missing/invalid sessions return 401; missing/invalid CSRF proof returns 403.
- Cross-origin auth mutations return 403.
- Human sessions cannot call Chimera or Atlas machine routes. The bounded SWR endpoint
  can only ask the server to issue an exact-scope one-use capability after separate human
  review, recent MFA, durable reservation, governance, and audit checks.
- New roles or consequential actions must not ship until server denial tests exist.
