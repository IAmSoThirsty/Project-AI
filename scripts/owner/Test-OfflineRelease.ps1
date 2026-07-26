[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ArchivePath,
    [string]$ChecksumPath = "",
    [string]$SignaturePath = "",
    [string]$PublicKeyPath = ""
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

function Test-SshFileSignature {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        [Parameter(Mandatory)]
        [string]$DetachedSignature,
        [Parameter(Mandatory)]
        [string]$PublicKey,
        [Parameter(Mandatory)]
        [string]$WorkingDirectory
    )

    $sshKeygen = Get-Command ssh-keygen -ErrorAction SilentlyContinue
    if (-not $sshKeygen) {
        throw "ssh-keygen is required to verify the detached release signature."
    }
    $allowedSigners = Join-Path $WorkingDirectory "allowed_signers"
    $publicKeyLine = (Get-Content -LiteralPath $PublicKey -Raw).Trim()
    if ($publicKeyLine -notmatch '^ssh-ed25519\s+[A-Za-z0-9+/=]+(?:\s+.*)?$') {
        throw "The release public key is not a valid SSH Ed25519 public key."
    }
    "project-ai-release $publicKeyLine" |
        Set-Content -LiteralPath $allowedSigners -Encoding ascii

    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $sshKeygen.Source
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    foreach ($argument in @(
        "-Y",
        "verify",
        "-f",
        $allowedSigners,
        "-I",
        "project-ai-release",
        "-n",
        "project-ai-offline-release",
        "-s",
        $DetachedSignature
    )) {
        $startInfo.ArgumentList.Add($argument)
    }

    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "Could not start ssh-keygen for release-signature verification."
    }
    $inputStream = [IO.File]::OpenRead($FilePath)
    try {
        $inputStream.CopyTo($process.StandardInput.BaseStream)
        $process.StandardInput.Close()
        $output = $process.StandardOutput.ReadToEnd()
        $errorOutput = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        $exitCode = $process.ExitCode
    }
    finally {
        $inputStream.Dispose()
        $process.Dispose()
    }
    if ($exitCode -ne 0) {
        throw "Release signature verification failed: $errorOutput"
    }
    return ($output + $errorOutput).Trim()
}

$resolvedArchive = [IO.Path]::GetFullPath($ArchivePath)
if (-not (Test-Path -LiteralPath $resolvedArchive -PathType Leaf)) {
    throw "Release archive is missing: $resolvedArchive"
}
if (-not $ChecksumPath) {
    $ChecksumPath = "$resolvedArchive.sha256"
}
if (-not $SignaturePath) {
    $SignaturePath = "$resolvedArchive.sig"
}
if (-not $PublicKeyPath) {
    $PublicKeyPath = "$resolvedArchive.pub"
}
foreach ($sidecar in @($ChecksumPath, $SignaturePath, $PublicKeyPath)) {
    if (-not (Test-Path -LiteralPath $sidecar -PathType Leaf)) {
        throw "Release sidecar is missing: $sidecar"
    }
}

$checksumText = (Get-Content -LiteralPath $ChecksumPath -Raw).Trim()
$checksumMatch = [regex]::Match(
    $checksumText,
    '^(?<hash>[0-9a-fA-F]{64}) \*(?<name>.+)$'
)
if (-not $checksumMatch.Success) {
    throw "The SHA-256 sidecar is not in '<hash> *<filename>' format."
}
if ($checksumMatch.Groups["name"].Value -ne [IO.Path]::GetFileName($resolvedArchive)) {
    throw "The SHA-256 sidecar names a different archive."
}
$actualHash = (
    Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedArchive
).Hash.ToLowerInvariant()
if ($actualHash -ne $checksumMatch.Groups["hash"].Value.ToLowerInvariant()) {
    throw "The release archive does not match its SHA-256 sidecar."
}

$verificationRoot = Join-Path (Get-OwnerStateRoot) "release-verify"
New-Item -ItemType Directory -Path $verificationRoot -Force | Out-Null
$workingDirectory = Join-Path $verificationRoot ([Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $workingDirectory -Force | Out-Null
try {
    $signatureResult = Test-SshFileSignature `
        -FilePath $resolvedArchive `
        -DetachedSignature $SignaturePath `
        -PublicKey $PublicKeyPath `
        -WorkingDirectory $workingDirectory

    $expanded = Join-Path $workingDirectory "expanded"
    Expand-Archive -LiteralPath $resolvedArchive -DestinationPath $expanded
    $manifestPath = Join-Path $expanded "offline-bundle-manifest.json"
    $releasePath = Join-Path $expanded "RELEASE.json"
    foreach ($required in @(
        $manifestPath,
        $releasePath,
        (Join-Path $expanded "LICENSE"),
        (Join-Path $expanded "NOTICE"),
        (Join-Path $expanded "THIRD_PARTY_NOTICES.md"),
        (Join-Path $expanded "Install Project-AI Offline.cmd"),
        (Join-Path $expanded "project-ai-offline-images.tar")
    )) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
            throw "The release archive is missing required content: $required"
        }
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    $release = Get-Content -LiteralPath $releasePath -Raw | ConvertFrom-Json
    if (
        $manifest.schema_version -ne 1 -or
        $manifest.profile -ne "P1-offline-first-local" -or
        -not $manifest.source_tree_clean
    ) {
        throw "The release manifest is not a clean P1 offline-first release."
    }
    if (
        $release.schema_version -ne 1 -or
        $release.profile -ne "P1-offline-first-local" -or
        $release.audience -ne "single-user" -or
        -not $release.source_tree_clean -or
        $release.version -ne $manifest.product_version -or
        $release.source_commit -ne $manifest.source_base_commit
    ) {
        throw "RELEASE.json is inconsistent with the offline bundle manifest."
    }
    foreach ($record in $manifest.files) {
        $candidate = [IO.Path]::GetFullPath((Join-Path $expanded $record.path))
        if (-not $candidate.StartsWith($expanded, [StringComparison]::OrdinalIgnoreCase)) {
            throw "The release manifest contains an unsafe path: $($record.path)"
        }
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "The release archive is missing $($record.path)."
        }
        $recordHash = (
            Get-FileHash -Algorithm SHA256 -LiteralPath $candidate
        ).Hash.ToLowerInvariant()
        if ($recordHash -ne $record.sha256) {
            throw "The release archive has a hash mismatch for $($record.path)."
        }
    }

    [ordered]@{
        status = "verified"
        release = $release.release
        profile = $release.profile
        audience = $release.audience
        archive = $resolvedArchive
        sha256 = $actualHash
        source_commit = $release.source_commit
        signature = $signatureResult
        file_records = @($manifest.files).Count
        image_records = @($manifest.images).Count
    } | ConvertTo-Json -Depth 10
}
finally {
    $resolvedVerificationRoot = [IO.Path]::GetFullPath($verificationRoot)
    $resolvedWorkingDirectory = [IO.Path]::GetFullPath($workingDirectory)
    if (
        $resolvedWorkingDirectory.StartsWith(
            $resolvedVerificationRoot,
            [StringComparison]::OrdinalIgnoreCase
        ) -and
        (Test-Path -LiteralPath $resolvedWorkingDirectory)
    ) {
        Remove-Item -LiteralPath $resolvedWorkingDirectory -Recurse -Force
    }
}
