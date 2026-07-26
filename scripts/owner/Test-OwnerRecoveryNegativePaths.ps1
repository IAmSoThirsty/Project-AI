[CmdletBinding()]
param(
    [string]$KnownGoodBackup = ".local/backups/pre-owner-profile-20260725.paibak"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

$repositoryRoot = Get-OwnerRepositoryRoot
$stateRoot = [IO.Path]::GetFullPath((Get-OwnerStateRoot))
$testRoot = [IO.Path]::GetFullPath((Join-Path $stateRoot "recovery-negative-tests"))
if (-not $testRoot.StartsWith($stateRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to use a recovery test path outside .owner-state."
}
if (Test-Path -LiteralPath $testRoot) {
    throw "Recovery negative-test path already exists: $testRoot"
}

New-Item -ItemType Directory -Path $testRoot | Out-Null
Set-OwnerRestrictedAcl -LiteralPath $testRoot
Push-Location $repositoryRoot
try {
    $restoreScript = Join-Path $PSScriptRoot "Restore-ProjectAI.ps1"
    $resolvedGoodBackup = (Resolve-Path -LiteralPath $KnownGoodBackup).Path
    $evidenceRoot = Join-Path $repositoryRoot ".owner-evidence"
    $restoreEvidenceBefore = @(
        Get-ChildItem -LiteralPath $evidenceRoot -Filter "owner-restore-*.json" `
            -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty Name
    )

    $confirmationRejected = $false
    try {
        & $restoreScript -BackupPath $resolvedGoodBackup
    }
    catch {
        $confirmationRejected = $_.Exception.Message -like "Restore not confirmed*"
    }
    if (-not $confirmationRejected) {
        throw "Restore did not fail closed when confirmation was omitted."
    }

    $missingStateRoot = Join-Path $testRoot "missing-owner-state"
    New-Item -ItemType Directory -Path $missingStateRoot | Out-Null
    $missingCredentialsRejected = $false
    try {
        Assert-OwnerCredentialContinuity -StateRoot $missingStateRoot
    }
    catch {
        $missingCredentialsRejected = $_.Exception.Message -like "Existing Project-AI database state has no matching*"
    }
    if (-not $missingCredentialsRejected) {
        throw "Startup preflight did not reject an existing database volume without credentials."
    }

    $tamperedBackup = Join-Path $testRoot "tampered.paibak"
    Copy-Item -LiteralPath $resolvedGoodBackup -Destination $tamperedBackup
    $tamperedBytes = [IO.File]::ReadAllBytes($tamperedBackup)
    $tamperedBytes[$tamperedBytes.Length - 1] = $tamperedBytes[$tamperedBytes.Length - 1] -bxor 0x01
    [IO.File]::WriteAllBytes($tamperedBackup, $tamperedBytes)
    [Array]::Clear($tamperedBytes, 0, $tamperedBytes.Length)
    $tamperRejected = $false
    try {
        & $restoreScript -BackupPath $tamperedBackup -ConfirmRestore
    }
    catch {
        $tamperRejected = $true
    }
    if (-not $tamperRejected) {
        throw "Restore accepted a tampered encrypted backup."
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $unsafeZip = Join-Path $testRoot "unsafe.zip"
    $archive = [IO.Compression.ZipFile]::Open(
        $unsafeZip,
        [IO.Compression.ZipArchiveMode]::Create
    )
    try {
        $entry = $archive.CreateEntry("../escape.txt")
        $writer = [IO.StreamWriter]::new($entry.Open())
        try {
            $writer.Write("must-not-escape")
        }
        finally {
            $writer.Dispose()
        }
    }
    finally {
        $archive.Dispose()
    }
    $unsafeBackup = Join-Path $testRoot "unsafe.paibak"
    Protect-OwnerArchive -InputPath $unsafeZip -OutputPath $unsafeBackup
    $unsafeRejected = $false
    try {
        & $restoreScript -BackupPath $unsafeBackup -ConfirmRestore
    }
    catch {
        $unsafeRejected = $_.Exception.Message -like "Backup contains an unsafe archive path*"
    }
    if (-not $unsafeRejected) {
        throw "Restore did not reject a zip-slip archive path."
    }
    if (Test-Path -LiteralPath (Join-Path $stateRoot "escape.txt")) {
        throw "Unsafe archive data escaped the restore workspace."
    }
    $restoreEvidenceAfter = @(
        Get-ChildItem -LiteralPath $evidenceRoot -Filter "owner-restore-*.json" |
            Select-Object -ExpandProperty Name
    )
    $newRestoreEvidence = @(
        $restoreEvidenceAfter | Where-Object { $_ -notin $restoreEvidenceBefore }
    )
    if ($newRestoreEvidence.Count -lt 2) {
        throw "Distinct restore failures did not retain distinct evidence receipts."
    }

    Write-Host "OWNER_RECOVERY_NEGATIVE_TESTS=PASS"
    Write-Host "confirmation_required=true"
    Write-Host "missing_credentials_rejected=true"
    Write-Host "tamper_rejected=true"
    Write-Host "zip_slip_rejected=true"
    Write-Host "distinct_failure_receipts=$($newRestoreEvidence.Count)"
}
finally {
    Pop-Location
    if (Test-Path -LiteralPath $testRoot) {
        Remove-Item -LiteralPath $testRoot -Recurse -Force
    }
}
