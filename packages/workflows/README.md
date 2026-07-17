# Project-AI Human Workflows

Durable human request, review, execution-reservation, and receipt records for the
Control Center. A review is an interface decision only: it is never a canonical
governance verdict and does not itself execute an operation. Self-review is denied and
review/execution decisions require recent MFA step-up.

SQLite supports direct single-process/local use. PostgreSQL provides transactional
idempotency, reviewer uniqueness, cancellation, unique execution reservation, terminal
receipt transitions, and shared state across API replicas when
`PROJECT_AI_DATABASE_URL` is configured. Workflow schema version 2 added the generic
execution receipt record used by the first SWR Control Center workflow. Schema version
3 adds versioned structured request inputs and their canonical SHA-256 digest so a
reviewer can see the exact operation contract and values before making a human decision.
Schema version 4 adds generic durable analysis receipts with canonical input/output JSON,
independent SHA-256 values, an audit hash, and per-account idempotency. Existing
version-1/2 rows migrate fail-closed with an explicit `legacy/v0` marker; version-3 rows
retain their request evidence while gaining the analysis receipt table.
