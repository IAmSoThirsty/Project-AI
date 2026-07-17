param(
    [string]$OutputPath = ".local/backups/project-ai-human-$(Get-Date -Format 'yyyyMMdd-HHmmss').dump",
    [string]$ComposeProject = "project-ai"
)

$ErrorActionPreference = "Stop"
$resolvedOutput = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
$parent = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Force -Path $parent | Out-Null

docker compose -p $ComposeProject exec -T postgres sh -c 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/project-ai-human.dump'
if ($LASTEXITCODE -ne 0) { throw "PostgreSQL backup failed" }

try {
    docker compose -p $ComposeProject cp postgres:/tmp/project-ai-human.dump $resolvedOutput
    if ($LASTEXITCODE -ne 0) { throw "Could not copy PostgreSQL backup to host" }
}
finally {
    docker compose -p $ComposeProject exec -T postgres rm -f /tmp/project-ai-human.dump | Out-Null
}

Write-Output $resolvedOutput
