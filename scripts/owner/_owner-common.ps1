Set-StrictMode -Version Latest

. (Join-Path $PSScriptRoot "Secret-Store.ps1")

$script:OwnerRepositoryRoot = Get-OwnerRepositoryRoot
$env:PROJECT_AI_RUNTIME_SECRET_ROOT = Get-OwnerRuntimeRoot
$script:OwnerComposeFiles = @(
    "-f", (Join-Path $script:OwnerRepositoryRoot "compose.yaml"),
    "-f", (Join-Path $script:OwnerRepositoryRoot "compose.secrets.yaml"),
    "--project-name", "project-ai"
)

function Invoke-OwnerCompose {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & docker compose @script:OwnerComposeFiles @Arguments | Out-Host
    $exitCode = $LASTEXITCODE
    return $exitCode
}

function Assert-OwnerDocker {
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if ($null -eq $docker) {
        throw "Docker Desktop is not installed or docker.exe is not on PATH."
    }
    & docker version --format "{{.Server.Version}}" *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Desktop is installed, but its Linux container engine is not running."
    }
    & docker compose version --short *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose is unavailable. Update or repair Docker Desktop."
    }
}

function Assert-OwnerPorts {
    $required = @(8000, 4173, 4174, 4175)
    $runningNames = @(
        "project-ai-api",
        "project-ai-docs-portal",
        "project-ai-proof-portal",
        "project-ai-operator-console"
    )
    $owned = @()
    & docker ps --format "{{.Names}}" 2>$null | ForEach-Object {
        if ($_ -in $runningNames) {
            $owned += $_
        }
    }
    foreach ($port in $required) {
        $listener = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
        if ($listener -and $owned.Count -eq 0) {
            throw "Port $port is already in use. Stop the conflicting program, then run Start Project-AI again."
        }
    }
}

function Assert-OwnerDisk {
    $drive = Get-Item -LiteralPath $script:OwnerRepositoryRoot
    $qualifier = Split-Path -Qualifier $drive.FullName
    $disk = Get-PSDrive -Name $qualifier.TrimEnd(":\") -ErrorAction Stop
    if ($disk.Free -lt 10GB) {
        throw "Project-AI needs at least 10 GB free for local images, state, and recovery evidence."
    }
}

function Update-OwnerPostgresCredential {
    param([SecureString]$PortablePassphrase)

    & docker inspect project-ai-postgres *> $null
    if ($LASTEXITCODE -ne 0) {
        return "new-database"
    }
    $newPassword = Get-OwnerSecret -Name "postgres-password" `
        -PortablePassphrase $PortablePassphrase
    $escaped = $newPassword.Replace("'", "''")
    $statement = "ALTER ROLE project_ai PASSWORD '$escaped';"
    $statement | & docker exec -i project-ai-postgres `
        psql -U project_ai -d postgres -v ON_ERROR_STOP=1 *> $null
    $newPassword = $null
    $statement = $null
    if ($LASTEXITCODE -ne 0) {
        throw "Could not rotate the existing local PostgreSQL role to the protected owner credential."
    }
    return "rotated-existing-database"
}

function Assert-OwnerCredentialContinuity {
    param(
        [string]$StateRoot = (Get-OwnerStateRoot),
        [string]$DatabaseVolume = "project-ai_postgres-data"
    )

    $credentialRoot = Join-Path $StateRoot "credentials"
    $required = @(
        "setup-secret",
        "mfa-key",
        "execution-secret",
        "postgres-password"
    )
    $present = @($required | Where-Object {
        Test-Path -LiteralPath (Join-Path $credentialRoot "$_.json")
    })
    if ($present.Count -gt 0 -and $present.Count -ne $required.Count) {
        throw "The encrypted owner credential store is incomplete. Restore it from an approved backup before starting Project-AI."
    }

    & docker volume inspect $DatabaseVolume *> $null
    $existingDatabaseVolume = $LASTEXITCODE -eq 0
    if ($existingDatabaseVolume -and $present.Count -eq 0) {
        throw "Existing Project-AI database state has no matching encrypted owner credentials. Restore .owner-state from the prior installation or an approved backup; new credentials were not generated."
    }
}

function Ensure-OwnerLocalEnvironment {
    param([SecureString]$PortablePassphrase)

    $envPath = Join-Path $script:OwnerRepositoryRoot ".env"
    $secretNames = @(
        "PROJECT_AI_SETUP_SECRET",
        "PROJECT_AI_MFA_KEY",
        "PROJECT_AI_EXECUTION_SECRET",
        "PROJECT_AI_POSTGRES_PASSWORD",
        "PROJECT_AI_DATABASE_URL"
    )
    $retained = [System.Collections.Generic.List[string]]::new()
    if (Test-Path -LiteralPath $envPath) {
        foreach ($line in [IO.File]::ReadAllLines($envPath)) {
            $matched = $false
            foreach ($name in $secretNames) {
                if ($line -match "^\s*$name=(.*)$") {
                    $matched = $true
                    $value = $Matches[1]
                    if ($value -and $name -ne "PROJECT_AI_DATABASE_URL") {
                        $storeName = @{
                            PROJECT_AI_SETUP_SECRET = "setup-secret"
                            PROJECT_AI_MFA_KEY = "mfa-key"
                            PROJECT_AI_EXECUTION_SECRET = "execution-secret"
                            PROJECT_AI_POSTGRES_PASSWORD = "postgres-password"
                        }[$name]
                        Set-OwnerSecret -Name $storeName -Value $value -PortablePassphrase $PortablePassphrase
                    }
                    break
                }
            }
            if (-not $matched) {
                $retained.Add($line)
            }
        }
    }
    else {
        $retained.Add("# Project-AI offline-first local owner profile (non-secret settings only)")
        $retained.Add("PROJECT_AI_INSTANCE_NAME=PROJECT-AI-LOCAL")
        $retained.Add("PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=false")
        $retained.Add("PROJECT_AI_BOOTSTRAP_TRUST_PRIVATE_PROXY=true")
        $retained.Add("PROJECT_AI_WATERFALL_ENABLED=false")
    }
    [IO.File]::WriteAllLines($envPath, $retained, [Text.UTF8Encoding]::new($false))
}

function Test-OwnerHealth {
    $checks = [ordered]@{}
    foreach ($entry in @(
        @{ Name = "API"; Url = "http://127.0.0.1:8000/health/live" },
        @{ Name = "Docs portal"; Url = "http://127.0.0.1:4173/healthz" },
        @{ Name = "Proof portal"; Url = "http://127.0.0.1:4174/healthz" },
        @{ Name = "Control Center"; Url = "http://127.0.0.1:4175/healthz" }
    )) {
        try {
            $response = Invoke-WebRequest -Uri $entry.Url -UseBasicParsing -TimeoutSec 8
            $checks[$entry.Name] = $response.StatusCode -eq 200
        }
        catch {
            $checks[$entry.Name] = $false
        }
    }
    try {
        $bootstrap = Invoke-RestMethod `
            -Uri "http://127.0.0.1:8000/api/v1/auth/bootstrap-status" `
            -TimeoutSec 8
        $checks["Owner bootstrap"] = $bootstrap.status
    }
    catch {
        $checks["Owner bootstrap"] = "unavailable"
    }
    return [pscustomobject]$checks
}

function Test-OwnerContainerHardening {
    $expected = @(
        "project-ai-postgres",
        "project-ai-api",
        "project-ai-docs-portal",
        "project-ai-proof-portal",
        "project-ai-operator-console",
        "project-ai-swr",
        "project-ai-atlas",
        "project-ai-arbiter-rlp",
        "project-ai-genesis"
    )
    $failures = [System.Collections.Generic.List[string]]::new()
    foreach ($name in $expected) {
        $raw = & docker inspect $name 2>$null
        if ($LASTEXITCODE -ne 0) {
            $failures.Add("$name is missing")
            continue
        }
        $container = ($raw | ConvertFrom-Json)[0]
        if (-not $container.State.Running -or $container.State.Health.Status -ne "healthy") {
            $failures.Add("$name is not running and healthy")
        }
        if (-not $container.HostConfig.ReadonlyRootfs) {
            $failures.Add("$name does not use a read-only root filesystem")
        }
        if (@($container.HostConfig.CapDrop) -notcontains "ALL") {
            $failures.Add("$name does not drop all capabilities")
        }
        if (@($container.HostConfig.SecurityOpt) -notcontains "no-new-privileges:true") {
            $failures.Add("$name does not enforce no-new-privileges")
        }
    }
    return [pscustomobject]@{
        verified = $failures.Count -eq 0
        containers = $expected.Count
        failures = $failures.ToArray()
    }
}

function Write-OwnerEvidenceReceipt {
    param(
        [Parameter(Mandatory = $true)][string]$Operation,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][object]$Evidence
    )

    $evidenceRoot = Join-Path $script:OwnerRepositoryRoot ".owner-evidence"
    New-Item -ItemType Directory -Path $evidenceRoot -Force | Out-Null
    $timestamp = [DateTimeOffset]::UtcNow
    $record = [ordered]@{
        schema_version = 1
        evidence_id = "owner-$Operation-$($timestamp.ToString('yyyyMMddTHHmmssfffZ'))"
        operation = $Operation
        status = $Status
        timestamp_utc = $timestamp.ToString("O")
        repository = $script:OwnerRepositoryRoot
        profile = "P1-offline-first-local"
        evidence = $Evidence
    }
    $path = Join-Path $evidenceRoot "$($record.evidence_id).json"
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding utf8NoBOM
    return $path
}

function Write-OwnerDestination {
    param([string]$BootstrapStatus, [string]$SetupSecret)

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " Project-AI Control Center" -ForegroundColor Cyan
    Write-Host " http://127.0.0.1:4175" -ForegroundColor White
    if ($BootstrapStatus -eq "required") {
        Write-Host " First-run setup key: $SetupSecret" -ForegroundColor Yellow
        Write-Host " Save the recovery codes shown after setup." -ForegroundColor Yellow
    }
    else {
        Write-Host " Owner setup: $BootstrapStatus" -ForegroundColor Green
    }
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}
