param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [string]$TargetDatabase = "project_ai_restore",
    [string]$ComposeProject = "project-ai",
    [switch]$ConfirmRestore,
    [switch]$AllowPrimaryDatabase
)

$ErrorActionPreference = "Stop"
if (-not $ConfirmRestore) {
    throw "Restore not confirmed. Re-run with -ConfirmRestore after reviewing the target database."
}
if ($TargetDatabase -notmatch '^[a-zA-Z][a-zA-Z0-9_]{0,62}$') {
    throw "TargetDatabase must be a PostgreSQL-safe identifier."
}
if ($TargetDatabase -eq "project_ai" -and -not $AllowPrimaryDatabase) {
    throw "Primary-database restore refused. Use a separate target or explicitly add -AllowPrimaryDatabase."
}

$resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
docker compose -p $ComposeProject cp $resolvedBackup postgres:/tmp/project-ai-human-restore.dump
if ($LASTEXITCODE -ne 0) { throw "Could not copy backup into PostgreSQL container" }

try {
    docker compose -p $ComposeProject exec -T postgres dropdb -U project_ai --if-exists $TargetDatabase
    if ($LASTEXITCODE -ne 0) { throw "Could not remove the requested restore target" }
    docker compose -p $ComposeProject exec -T postgres createdb -U project_ai $TargetDatabase
    if ($LASTEXITCODE -ne 0) { throw "Could not create the restore target" }
    docker compose -p $ComposeProject exec -T postgres pg_restore -U project_ai -d $TargetDatabase --exit-on-error /tmp/project-ai-human-restore.dump
    if ($LASTEXITCODE -ne 0) { throw "PostgreSQL restore failed" }
    docker compose -p $ComposeProject exec -T postgres psql -U project_ai -d $TargetDatabase -Atc "SELECT component || '=' || version FROM project_ai_schema_versions ORDER BY component"
    if ($LASTEXITCODE -ne 0) { throw "Restored schema verification failed" }
}
finally {
    docker compose -p $ComposeProject exec -T postgres rm -f /tmp/project-ai-human-restore.dump | Out-Null
}
