[CmdletBinding()]
param(
    [SecureString]$PortablePassphrase,
    [switch]$NoBuild,
    [switch]$Offline,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

Push-Location $script:OwnerRepositoryRoot
try {
    Write-Host "Project-AI owner preflight..." -ForegroundColor Cyan
    Assert-OwnerDocker
    Assert-OwnerDisk
    Assert-OwnerPorts
    Ensure-OwnerLocalEnvironment -PortablePassphrase $PortablePassphrase
    Assert-OwnerCredentialContinuity
    $created = Initialize-OwnerSecretStore -PortablePassphrase $PortablePassphrase
    Write-OwnerRuntimeSecrets -PortablePassphrase $PortablePassphrase | Out-Null

    $configExit = Invoke-OwnerCompose config --quiet
    if ($configExit -ne 0) {
        throw "The local owner Compose configuration is invalid."
    }
    if ($Offline) {
        $NoBuild = $true
    }
    if (-not $NoBuild) {
        # Docker Desktop's BuildKit worker is resource-constrained on the
        # supported offline host. Build each unique image deterministically
        # instead of asking Compose/Bake to build the full graph concurrently.
        $env:COMPOSE_PARALLEL_LIMIT = "1"
        foreach ($service in @(
            "api",
            "swr",
            "docs-portal",
            "proof-portal",
            "operator-console",
            "genesis"
        )) {
            & docker compose --progress plain @script:OwnerComposeFiles build $service | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "Project-AI image failed to build for service: $service"
            }
        }
    }

    $recreateContainers = $false
    $existingWorkingDirectory = (
        & docker inspect --format `
            '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}' `
            project-ai-postgres 2>$null
    )
    if ($LASTEXITCODE -eq 0 -and $existingWorkingDirectory) {
        $existingWorkingDirectory = [IO.Path]::GetFullPath(
            $existingWorkingDirectory.Trim()
        ).TrimEnd("\", "/")
        $ownerWorkingDirectory = [IO.Path]::GetFullPath(
            $script:OwnerRepositoryRoot
        ).TrimEnd("\", "/")
        $recreateContainers = -not $existingWorkingDirectory.Equals(
            $ownerWorkingDirectory,
            [StringComparison]::OrdinalIgnoreCase
        )
        if ($recreateContainers) {
            Write-Host (
                "Recreating containers whose secret mounts belong to a different " +
                "Project-AI installation path. Named data volumes are preserved."
            ) -ForegroundColor Yellow
        }
    }

    # Credential rotation needs the existing database to be running. Docker
    # Desktop stops containers during an engine restart, so reconcile and wait
    # for PostgreSQL before attempting docker exec.
    $databaseArguments = @("up", "-d", "--no-build")
    if ($recreateContainers) {
        $databaseArguments += "--force-recreate"
    }
    if ($Offline) {
        $databaseArguments += @("--pull", "never")
    }
    $databaseArguments += @("--wait", "--wait-timeout", "120", "postgres")
    if ((Invoke-OwnerCompose @databaseArguments) -ne 0) {
        throw "The local Project-AI database did not become ready for credential rotation."
    }
    $databaseCredential = Update-OwnerPostgresCredential `
        -PortablePassphrase $PortablePassphrase
    $arguments = @("up", "-d", "--no-build")
    if ($recreateContainers) {
        $arguments += "--force-recreate"
    }
    if ($Offline) {
        $arguments += @("--pull", "never")
    }
    $arguments += @("--wait", "--wait-timeout", "300")
    $startExit = Invoke-OwnerCompose @arguments
    if ($startExit -ne 0) {
        throw "Project-AI did not become ready within five minutes."
    }

    $health = Test-OwnerHealth
    $healthValues = @($health.PSObject.Properties | Where-Object {
        $_.Name -ne "Owner bootstrap"
    } | ForEach-Object { $_.Value })
    if ($healthValues -contains $false) {
        throw "One or more owner-facing health checks failed after Compose reported ready."
    }

    $hardening = Test-OwnerContainerHardening
    if (-not $hardening.verified) {
        throw "Container hardening verification failed: $($hardening.failures -join '; ')"
    }
    $receipt = Write-OwnerEvidenceReceipt -Operation "start" -Status "verified" -Evidence @{
        compose = "ready"
        health = $health
        hardening = $hardening
        offline_pull_disabled = [bool]$Offline
        recreated_stale_compose_project = $recreateContainers
        credentials_created = @($created)
        database_credential = $databaseCredential
        control_center = "http://127.0.0.1:4175"
    }
    $setupSecret = Get-OwnerSecret -Name "setup-secret" -PortablePassphrase $PortablePassphrase
    Write-OwnerDestination -BootstrapStatus $health."Owner bootstrap" -SetupSecret $setupSecret
    Write-Host "Evidence receipt: $receipt"
    if (-not $NoBrowser) {
        Start-Process "http://127.0.0.1:4175"
    }
}
catch {
    Write-Error $_
    Write-Host "Current service state:" -ForegroundColor Yellow
    Invoke-OwnerCompose ps | Out-Null
    Write-Host "Recent service logs:" -ForegroundColor Yellow
    Invoke-OwnerCompose logs --tail 40 | Out-Null
    $receipt = Write-OwnerEvidenceReceipt -Operation "start" -Status "failed" -Evidence @{
        error = $_.Exception.Message
    }
    Write-Host "Failure receipt: $receipt"
    exit 1
}
finally {
    Pop-Location
}
