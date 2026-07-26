[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

Push-Location $script:OwnerRepositoryRoot
try {
    Assert-OwnerDocker
    Write-Host "Project-AI local service status" -ForegroundColor Cyan
    Invoke-OwnerCompose ps | Out-Null
    $health = Test-OwnerHealth
    Write-Host ""
    $health.PSObject.Properties | ForEach-Object {
        [pscustomobject]@{
            Surface = $_.Name
            State = $_.Value
        }
    } | Format-Table -AutoSize
    $ready = @($health.PSObject.Properties | Where-Object {
        $_.Name -ne "Owner bootstrap"
    } | ForEach-Object { $_.Value }) -notcontains $false
    $receipt = Write-OwnerEvidenceReceipt -Operation "status" -Status $(
        if ($ready) { "verified" } else { "degraded" }
    ) -Evidence @{ health = $health }
    Write-Host "Control Center: http://127.0.0.1:4175"
    Write-Host "Evidence receipt: $receipt"
    if (-not $ready) {
        exit 2
    }
}
finally {
    Pop-Location
}
