# Human-State PostgreSQL Operations

## Storage selection

`PROJECT_AI_DATABASE_URL` selects PostgreSQL for accounts, sessions, recovery codes,
MFA state, rate limits, security events, work requests, reviews, cancellation, and
execution and analysis receipts. Workflow schema version 2 stores one durable execution
receipt per reviewed request, including governance evidence, execution-event, and audit
hashes. Version 3 adds canonical structured request input evidence. Version 4 adds
idempotent analysis receipts with canonical input/output JSON and independent input,
output, Atlas projection, and audit hashes.
It takes precedence over `PROJECT_AI_ACCOUNT_DB` and `PROJECT_AI_WORKFLOW_DB`.

SQLite remains supported for direct, single-process local development. Do not run
multiple API replicas against SQLite files.

## Compose

Set a non-default password before starting the stack:

```powershell
$env:PROJECT_AI_POSTGRES_PASSWORD = '<random-local-secret>'
$env:PROJECT_AI_SETUP_SECRET = '<one-time-owner-setup-secret>'
$env:PROJECT_AI_MFA_KEY = '<Fernet-key>'
$env:PROJECT_AI_EXECUTION_SECRET = '<at-least-32-random-UTF-8-bytes>'
docker compose up -d postgres api operator-console
docker compose ps
```

Compose constructs the internal DSN and does not publish PostgreSQL to the host.

## Helm

Production values set the API to two replicas and disable SQLite paths. Supply
`secrets.api.databaseUrl` as a PostgreSQL DSN, preferably through the deployment's
secret-management process. The database must require TLS and use a least-privilege
application role in production. An empty DSN leaves human routes unconfigured and
fail-closed.
Supply `secrets.api.executionSecret` with at least 32 random UTF-8 bytes to enable the
server-side SWR capability authority. Leaving it empty keeps execution routes fail-closed.
The API also requires a writable SWR bundle directory. Compose and Helm mount shared
application data and set `PROJECT_AI_SWR_BUNDLE_DIR=/data/swr-bundles`.

## One-time SQLite migration

Back up both SQLite files before migration. The target PostgreSQL tables must be
empty. The command refuses an unexpected SQLite schema or a populated target.

```powershell
$env:PROJECT_AI_DATABASE_URL = 'postgresql://user:password@host:5432/project_ai?sslmode=require'
uv run python tools/migrate_human_state.py `
  --account-db .local/project-ai-accounts.db `
  --workflow-db .local/project-ai-workflows.db
```

The migration preserves password/session/recovery hashes as stored; it never exports
raw credentials because the SQLite store does not contain them. After verification,
retain the source files as rollback evidence until the migration is formally accepted.

## Backup and restore

For the local Compose database:

```powershell
$backup = scripts/operations/backup_human_state.ps1
& $backup
& scripts/operations/restore_human_state.ps1 `
  -BackupPath .local/backups/<backup>.dump `
  -TargetDatabase project_ai_restore `
  -ConfirmRestore
```

Restore defaults to a separate database. Restoring over `project_ai` requires the
additional `-AllowPrimaryDatabase` switch and is destructive. Production managed
database backup, point-in-time recovery, TLS, credential rotation, and a live-cluster
restore drill remain deployment-specific acceptance gates.

## Rollback

1. Stop API writes.
2. Preserve a PostgreSQL dump and current audit evidence.
3. Point one API instance at the preserved SQLite files by removing
   `PROJECT_AI_DATABASE_URL` and setting both SQLite path variables.
4. Verify bootstrap status, login, sessions, request visibility, and audit integrity.
5. Do not run multiple API replicas in rollback SQLite mode.

There is no automatic reverse PostgreSQL-to-SQLite migration.
