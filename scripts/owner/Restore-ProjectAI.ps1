[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [string]$BackupPath,
    [SecureString]$PortablePassphrase,
    [switch]$ConfirmRestore,
    [switch]$ReplaceCurrentState,
    [switch]$RestoreCredentials,
    [switch]$KeepIsolatedDatabase,
    [string]$IsolatedDatabase = "project_ai_restore"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

function Remove-RestoreWorkDirectory {
    param([string]$Path)

    $workRoot = [IO.Path]::GetFullPath((Join-Path (Get-OwnerStateRoot) "restore-work"))
    $resolved = [IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($workRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the owner restore work directory."
    }
    if (Test-Path -LiteralPath $resolved) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}

if (-not $ConfirmRestore) {
    throw "Restore not confirmed. Re-run with -ConfirmRestore after reviewing the backup target."
}
if ($IsolatedDatabase -notmatch "^[a-zA-Z][a-zA-Z0-9_]{0,62}$") {
    throw "IsolatedDatabase must be a PostgreSQL-safe identifier."
}

Push-Location $script:OwnerRepositoryRoot
$workDirectory = $null
try {
    Assert-OwnerDocker
    $resolvedBackup = (Resolve-Path -LiteralPath $BackupPath).Path
    $workRoot = Join-Path (Get-OwnerStateRoot) "restore-work"
    New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    $workDirectory = Join-Path $workRoot ([Guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $workDirectory -Force | Out-Null
    $zipPath = Join-Path $workDirectory "owner-backup.zip"
    Unprotect-OwnerArchive -InputPath $resolvedBackup -OutputPath $zipPath `
        -PortablePassphrase $PortablePassphrase

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $archive = [IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        foreach ($entry in $archive.Entries) {
            $candidate = [IO.Path]::GetFullPath((Join-Path $workDirectory $entry.FullName))
            if (-not $candidate.StartsWith(
                [IO.Path]::GetFullPath($workDirectory),
                [StringComparison]::OrdinalIgnoreCase
            )) {
                throw "Backup contains an unsafe archive path: $($entry.FullName)"
            }
        }
    }
    finally {
        $archive.Dispose()
    }
    $payloadDirectory = Join-Path $workDirectory "payload"
    Expand-Archive -LiteralPath $zipPath -DestinationPath $payloadDirectory
    $manifestPath = Join-Path $payloadDirectory "manifest.json"
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Backup manifest is missing."
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($manifest.schema_version -notin @(1, 2) -or $manifest.profile -ne "P1-offline-first-local") {
        throw "Backup manifest is not a supported Project-AI offline-first backup."
    }
    foreach ($record in $manifest.files) {
        $candidate = [IO.Path]::GetFullPath((Join-Path $payloadDirectory $record.path))
        if (-not $candidate.StartsWith(
            [IO.Path]::GetFullPath($payloadDirectory),
            [StringComparison]::OrdinalIgnoreCase
        )) {
            throw "Backup manifest contains an unsafe path: $($record.path)"
        }
        if (-not (Test-Path -LiteralPath $candidate)) {
            throw "Backup payload is missing $($record.path)."
        }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash.ToLowerInvariant()
        if ($actual -ne $record.sha256) {
            throw "Backup payload hash mismatch for $($record.path)."
        }
    }

    Ensure-OwnerLocalEnvironment -PortablePassphrase $PortablePassphrase
    Initialize-OwnerSecretStore -PortablePassphrase $PortablePassphrase | Out-Null
    Write-OwnerRuntimeSecrets -PortablePassphrase $PortablePassphrase | Out-Null
    if ((Invoke-OwnerCompose up -d --wait --wait-timeout 120 postgres) -ne 0) {
        throw "The local PostgreSQL service did not become ready."
    }

    $targetDatabase = if ($ReplaceCurrentState) { "project_ai" } else { $IsolatedDatabase }
    if ($ReplaceCurrentState) {
        if (-not $PSCmdlet.ShouldProcess(
            "Project-AI local database and audit volume",
            "Replace current owner state from encrypted backup"
        )) {
            return
        }
        Invoke-OwnerCompose stop api docs-portal proof-portal operator-console swr atlas `
            arbiter-rlp genesis | Out-Null
    }

    $dumpPath = Join-Path $payloadDirectory "postgres.dump"
    $restorePath = "/var/lib/postgresql/data/.project-ai-owner-restore.dump"
    & docker cp $dumpPath "project-ai-postgres:$restorePath"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the PostgreSQL dump into the database container."
    }
    try {
        & docker exec project-ai-postgres psql -U project_ai -d postgres -v ON_ERROR_STOP=1 `
            -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$targetDatabase' AND pid <> pg_backend_pid();" | Out-Null
        & docker exec project-ai-postgres dropdb -U project_ai --if-exists $targetDatabase
        if ($LASTEXITCODE -ne 0) {
            throw "Could not remove the requested restore database."
        }
        & docker exec project-ai-postgres createdb -U project_ai $targetDatabase
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create the requested restore database."
        }
        & docker exec project-ai-postgres pg_restore -U project_ai -d $targetDatabase `
            --exit-on-error $restorePath
        if ($LASTEXITCODE -ne 0) {
            throw "PostgreSQL restore failed."
        }
        & docker exec project-ai-postgres psql -U project_ai -d $targetDatabase -Atc `
            "SELECT component || '=' || version FROM project_ai_schema_versions ORDER BY component"
        if ($LASTEXITCODE -ne 0) {
            throw "Restored schema verification failed."
        }
    }
    finally {
        & docker exec project-ai-postgres rm -f $restorePath | Out-Null
    }

    $journey = "schema-verified"
    if (-not $ReplaceCurrentState -and -not $KeepIsolatedDatabase) {
        & docker exec project-ai-postgres dropdb -U project_ai $targetDatabase
        if ($LASTEXITCODE -ne 0) {
            throw "The verified isolated restore database could not be removed."
        }
        $journey = "schema-verified-and-isolated-database-removed"
    }
    if ($ReplaceCurrentState) {
        Invoke-OwnerCompose create api | Out-Null
        $auditSource = Join-Path $payloadDirectory "audit-data"
        $clearCommand = "find /data -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +"
        if ((Invoke-OwnerCompose run --rm --no-deps --entrypoint sh api -c $clearCommand) -ne 0) {
            throw "Could not clear the current audit volume before restore."
        }
        & docker cp "$auditSource/." "project-ai-api:/data"
        if ($LASTEXITCODE -ne 0) {
            throw "Could not restore the audit and SWR state volume."
        }
        # `docker cp` writes restored files as root even though the hardened API
        # runs as 10001:10001. Use a short-lived, non-networked maintenance
        # container with only CAP_CHOWN restored so the production API can read
        # and append its audit/state files after a destructive restore.
        $repairOwnershipCommand = "chown -R 10001:10001 /data"
        if ((
            Invoke-OwnerCompose run --rm --no-deps --user 0 --cap-add CHOWN `
                --entrypoint sh api -c $repairOwnershipCommand
        ) -ne 0) {
            throw "Could not repair restored audit and SWR state ownership."
        }
        if ($RestoreCredentials) {
            $credentialExportPath = Join-Path $payloadDirectory "credential-export.json"
            $legacyCredentialSource = Join-Path $payloadDirectory "encrypted-credentials"
            if (Test-Path -LiteralPath $credentialExportPath) {
                $credentialExport = Get-Content -LiteralPath $credentialExportPath -Raw |
                    ConvertFrom-Json
                foreach ($name in @(
                    "setup-secret",
                    "mfa-key",
                    "execution-secret",
                    "postgres-password"
                )) {
                    $value = $credentialExport.$name
                    if (-not $value) {
                        throw "Credential export is missing '$name'."
                    }
                    Set-OwnerSecret -Name $name -Value $value `
                        -PortablePassphrase $PortablePassphrase
                    $value = $null
                }
                $credentialExport = $null
            }
            elseif (Test-Path -LiteralPath $legacyCredentialSource) {
                $credentialTarget = Join-Path (Get-OwnerStateRoot) "credentials"
                if (Test-Path -LiteralPath $credentialTarget) {
                    Remove-Item -LiteralPath $credentialTarget -Recurse -Force
                }
                Copy-Item -LiteralPath $legacyCredentialSource `
                    -Destination $credentialTarget -Recurse
            }
            else {
                throw "This backup does not include restorable owner credentials."
            }
            Write-OwnerRuntimeSecrets -PortablePassphrase $PortablePassphrase | Out-Null
        }
        if ((Invoke-OwnerCompose up -d --wait --wait-timeout 300) -ne 0) {
            throw "The restored Project-AI stack did not become ready."
        }
        $health = Test-OwnerHealth
        if ($health.API -ne $true -or $health."Control Center" -ne $true) {
            throw "The restored API or Control Center failed its owner health check."
        }
        $journey = "control-center-and-bootstrap-status-reachable"
    }

    $receipt = Write-OwnerEvidenceReceipt -Operation "restore" -Status "verified" -Evidence @{
        backup_id = $manifest.backup_id
        archive_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedBackup).Hash.ToLowerInvariant()
        target_database = $targetDatabase
        current_state_replaced = [bool]$ReplaceCurrentState
        credentials_restored = [bool]$RestoreCredentials
        isolated_database_retained = [bool](
            -not $ReplaceCurrentState -and $KeepIsolatedDatabase
        )
        owner_journey = $journey
    }
    Write-Host "Backup integrity and restore verification passed." -ForegroundColor Green
    Write-Host "Target database: $targetDatabase"
    Write-Host "Evidence receipt: $receipt"
}
catch {
    $receipt = Write-OwnerEvidenceReceipt -Operation "restore" -Status "failed" -Evidence @{
        error = $_.Exception.Message
    }
    Write-Host "Failure receipt: $receipt"
    throw
}
finally {
    if ($workDirectory) {
        Remove-RestoreWorkDirectory -Path $workDirectory
    }
    Pop-Location
}
