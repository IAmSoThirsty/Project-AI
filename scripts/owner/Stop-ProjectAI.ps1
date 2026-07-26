[CmdletBinding(SupportsShouldProcess)]
param(
    [switch]$RemoveData
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

Push-Location $script:OwnerRepositoryRoot
try {
    Assert-OwnerDocker
    $arguments = @("down", "--remove-orphans")
    if ($RemoveData) {
        if (-not $PSCmdlet.ShouldProcess(
            "Project-AI local Docker volumes",
            "Remove all local owner data"
        )) {
            return
        }
        $arguments += "--volumes"
    }
    $exitCode = Invoke-OwnerCompose @arguments
    if ($exitCode -ne 0) {
        throw "Docker Compose could not stop the Project-AI stack."
    }
    Remove-OwnerRuntimeSecrets
    $remaining = @(& docker ps --filter "name=project-ai-" --format "{{.Names}}")
    $status = if ($remaining.Count -eq 0) { "verified" } else { "failed" }
    $receipt = Write-OwnerEvidenceReceipt -Operation "stop" -Status $status -Evidence @{
        data_removed = [bool]$RemoveData
        remaining_containers = $remaining
        encrypted_credentials_retained = $true
    }
    if ($remaining.Count -gt 0) {
        throw "Project-AI stopped with residual running containers: $($remaining -join ', ')"
    }
    Write-Host "Project-AI is stopped. Local data volumes were $(
        if ($RemoveData) { 'removed' } else { 'retained' }
    )." -ForegroundColor Green
    Write-Host "Evidence receipt: $receipt"
}
finally {
    Pop-Location
}
