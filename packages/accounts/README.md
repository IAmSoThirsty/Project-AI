# Project-AI Human Accounts

This package owns durable human account credentials, roles, recovery codes,
server-side sessions, lockout state, account-to-actor bindings, and authentication
security events. It does not grant capabilities, governance verdicts, or execution
authority.

Storage supports SQLite for direct single-process/local development and PostgreSQL
for shared multi-replica deployment. Both stores use deterministic schema versions;
PostgreSQL migrations and Owner bootstrap use transaction-scoped advisory locks.
Only password hashes, recovery-code hashes, session-token hashes, and CSRF-token
hashes are persisted. Raw secrets are returned only at their one-time creation
boundary.

Current scope includes one-time Owner bootstrap, login lockout, opaque sessions,
idle and absolute expiry, session rotation/revocation, password changes, and local
recovery-code reset. TOTP enrollment, encrypted seed storage, replay-resistant login,
recent step-up, removal, and recovery reset are implemented when
`PROJECT_AI_MFA_KEY` is configured. `PROJECT_AI_DATABASE_URL` selects PostgreSQL and
takes precedence over the SQLite path. `tools/migrate_human_state.py` performs a
one-time, empty-target SQLite migration without rehashing stored credentials.
