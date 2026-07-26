[CmdletBinding()]
param(
    [string]$OutputPath = "",
    [SecureString]$PortablePassphrase,
    [switch]$IncludeCredentialStore
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

function Remove-BackupWorkDirectory {
    param([string]$Path)

    $workRoot = [IO.Path]::GetFullPath((Join-Path (Get-OwnerStateRoot) "backup-work"))
    $resolved = [IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($workRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the owner backup work directory."
    }
    if (Test-Path -LiteralPath $resolved) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}

Push-Location $script:OwnerRepositoryRoot
$workDirectory = $null
try {
    Assert-OwnerDocker
    Ensure-OwnerLocalEnvironment -PortablePassphrase $PortablePassphrase
    $health = Test-OwnerHealth
    if ($health.API -ne $true) {
        throw "The API is not live. Start Project-AI before creating a full-state backup."
    }
    if (-not $OutputPath) {
        $OutputPath = ".local/backups/project-ai-owner-$(
            [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssZ')
        ).paibak"
    }
    $resolvedOutput = [IO.Path]::GetFullPath((Join-Path $script:OwnerRepositoryRoot $OutputPath))
    New-Item -ItemType Directory -Path (Split-Path -Parent $resolvedOutput) -Force | Out-Null

    $workRoot = Join-Path (Get-OwnerStateRoot) "backup-work"
    New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    $workDirectory = Join-Path $workRoot ([Guid]::NewGuid().ToString("N"))
    $payloadDirectory = Join-Path $workDirectory "payload"
    $auditDirectory = Join-Path $payloadDirectory "audit-data"
    New-Item -ItemType Directory -Path $auditDirectory -Force | Out-Null
    Set-OwnerRestrictedAcl -LiteralPath $workDirectory

    # Docker Desktop cannot reliably docker-cp files out of a tmpfs mount. Use
    # the PostgreSQL data volume for the short-lived dump and remove it in the
    # finally block.
    $dumpInContainer = "/var/lib/postgresql/data/.project-ai-owner-backup.dump"
    & docker exec project-ai-postgres pg_dump `
        -U project_ai -d project_ai -Fc -f $dumpInContainer
    if ($LASTEXITCODE -ne 0) {
        throw "PostgreSQL pg_dump failed."
    }
    try {
        & docker cp `
            "project-ai-postgres:$dumpInContainer" `
            (Join-Path $payloadDirectory "postgres.dump")
        if ($LASTEXITCODE -ne 0) {
            throw "Could not copy the PostgreSQL dump to the backup workspace."
        }
    }
    finally {
        & docker exec project-ai-postgres rm -f $dumpInContainer | Out-Null
    }

    & docker cp "project-ai-api:/data/." $auditDirectory
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the owner audit and SWR state volume."
    }
    Copy-Item -LiteralPath ".env" -Destination (Join-Path $payloadDirectory "local.env") -Force
    if ($IncludeCredentialStore) {
        $credentialExport = [ordered]@{}
        foreach ($name in @(
            "setup-secret",
            "mfa-key",
            "execution-secret",
            "postgres-password"
        )) {
            $credentialExport[$name] = Get-OwnerSecret -Name $name `
                -PortablePassphrase $PortablePassphrase
        }
        $credentialExport | ConvertTo-Json -Depth 4 | Set-Content `
            -LiteralPath (Join-Path $payloadDirectory "credential-export.json") `
            -Encoding utf8NoBOM
        $credentialExport = $null
    }

    $files = Get-ChildItem -LiteralPath $payloadDirectory -Recurse -File | Sort-Object FullName
    $manifestFiles = foreach ($file in $files) {
        [ordered]@{
            path = [IO.Path]::GetRelativePath($payloadDirectory, $file.FullName).Replace("\", "/")
            bytes = $file.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
        }
    }
    $imageEvidence = @{}
    foreach ($container in @(
        "project-ai-postgres",
        "project-ai-api",
        "project-ai-docs-portal",
        "project-ai-proof-portal",
        "project-ai-operator-console",
        "project-ai-swr",
        "project-ai-atlas",
        "project-ai-arbiter-rlp",
        "project-ai-genesis"
    )) {
        $imageId = & docker inspect --format "{{.Image}}" $container 2>$null
        if ($LASTEXITCODE -eq 0) {
            $imageEvidence[$container] = $imageId
        }
    }
    $manifest = [ordered]@{
        schema_version = 2
        backup_id = "owner-backup-$([DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssZ'))"
        created_utc = [DateTimeOffset]::UtcNow.ToString("O")
        profile = "P1-offline-first-local"
        scope = @("postgres-human-state", "audit-data", "swr-bundles", "non-secret-local-config")
        encrypted_credentials_included = [bool]$IncludeCredentialStore
        credentials_portable = [bool](
            $IncludeCredentialStore -and $null -ne $PortablePassphrase
        )
        encryption = if ($null -eq $PortablePassphrase) {
            "windows-dpapi-current-user"
        }
        else {
            "aes-256-gcm-pbkdf2-sha256-200000"
        }
        images = $imageEvidence
        files = @($manifestFiles)
    }
    if ($IncludeCredentialStore) {
        $manifest.scope += "credential-export-inside-encrypted-archive"
    }
    $manifestPath = Join-Path $payloadDirectory "manifest.json"
    $manifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $manifestPath -Encoding utf8NoBOM

    $zipPath = Join-Path $workDirectory "owner-backup.zip"
    Compress-Archive -Path (Join-Path $payloadDirectory "*") -DestinationPath $zipPath
    Protect-OwnerArchive -InputPath $zipPath -OutputPath $resolvedOutput `
        -PortablePassphrase $PortablePassphrase
    $archiveHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedOutput).Hash.ToLowerInvariant()
    $receipt = Write-OwnerEvidenceReceipt -Operation "backup" -Status "verified" -Evidence @{
        backup_id = $manifest.backup_id
        archive = $resolvedOutput
        sha256 = $archiveHash
        bytes = (Get-Item -LiteralPath $resolvedOutput).Length
        scope = $manifest.scope
        encryption = $manifest.encryption
    }
    Write-Host "Encrypted full-state backup created." -ForegroundColor Green
    Write-Host "Archive: $resolvedOutput"
    Write-Host "SHA-256: $archiveHash"
    Write-Host "Evidence receipt: $receipt"
    Write-Output $resolvedOutput
}
catch {
    $receipt = Write-OwnerEvidenceReceipt -Operation "backup" -Status "failed" -Evidence @{
        error = $_.Exception.Message
    }
    Write-Host "Failure receipt: $receipt"
    throw
}
finally {
    if ($workDirectory) {
        Remove-BackupWorkDirectory -Path $workDirectory
    }
    Pop-Location
}
