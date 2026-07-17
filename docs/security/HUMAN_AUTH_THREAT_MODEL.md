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
