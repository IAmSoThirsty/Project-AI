[CmdletBinding()]
param(
    [string]$OutputPath = "",
    [switch]$SkipBuild,
    [string]$SigningKey = "",
    [string]$SigningPublicKey = "",
    [switch]$RequireSignature,
    [switch]$AllowDirtySource
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "_owner-common.ps1")

function Remove-BundleWorkDirectory {
    param([string]$Path)

    $workRoot = [IO.Path]::GetFullPath((Join-Path (Get-OwnerStateRoot) "bundle-work"))
    $resolved = [IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($workRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove a path outside the owner bundle work directory."
    }
    if (Test-Path -LiteralPath $resolved) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}

function Get-ProjectAIVersion {
    $projectFile = Join-Path $script:OwnerRepositoryRoot "pyproject.toml"
    $projectText = Get-Content -LiteralPath $projectFile -Raw
    $match = [regex]::Match(
        $projectText,
        '(?ms)^\[project\]\s*.*?^version\s*=\s*"(?<version>[^"]+)"'
    )
    if (-not $match.Success) {
        throw "Could not read the Project-AI version from pyproject.toml."
    }
    return $match.Groups["version"].Value
}

function Write-Sha256Sidecar {
    param(
        [Parameter(Mandatory)]
        [string]$ArchivePath
    )

    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ArchivePath).Hash.ToLowerInvariant()
    $sidecar = "$ArchivePath.sha256"
    "$hash *$([IO.Path]::GetFileName($ArchivePath))" |
        Set-Content -LiteralPath $sidecar -Encoding ascii
    return [ordered]@{
        hash = $hash
        path = $sidecar
    }
}

function Write-SshSignatureSidecar {
    param(
        [Parameter(Mandatory)]
        [string]$ArchivePath,
        [Parameter(Mandatory)]
        [string]$PrivateKeyPath,
        [string]$PublicKeyPath
    )

    $sshKeygen = Get-Command ssh-keygen -ErrorAction SilentlyContinue
    if (-not $sshKeygen) {
        throw "ssh-keygen is required to create a detached release signature."
    }
    $resolvedPrivateKey = [IO.Path]::GetFullPath($PrivateKeyPath)
    if (-not (Test-Path -LiteralPath $resolvedPrivateKey -PathType Leaf)) {
        throw "Release signing key is missing: $resolvedPrivateKey"
    }
    if (-not $PublicKeyPath) {
        $PublicKeyPath = "$resolvedPrivateKey.pub"
    }
    $resolvedPublicKey = [IO.Path]::GetFullPath($PublicKeyPath)
    if (-not (Test-Path -LiteralPath $resolvedPublicKey -PathType Leaf)) {
        throw "Release signing public key is missing: $resolvedPublicKey"
    }

    & $sshKeygen.Source -Y sign -f $resolvedPrivateKey `
        -n "project-ai-offline-release" $ArchivePath | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "ssh-keygen could not create the detached release signature."
    }
    $signaturePath = "$ArchivePath.sig"
    if (-not (Test-Path -LiteralPath $signaturePath -PathType Leaf)) {
        throw "ssh-keygen reported success but did not create $signaturePath."
    }
    $publishedPublicKey = "$ArchivePath.pub"
    Copy-Item -LiteralPath $resolvedPublicKey -Destination $publishedPublicKey -Force
    $fingerprint = (& $sshKeygen.Source -lf $resolvedPublicKey -E sha256).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Could not identify the release signing-key fingerprint."
    }
    return [ordered]@{
        algorithm = "ssh-ed25519"
        namespace = "project-ai-offline-release"
        signature = $signaturePath
        public_key = $publishedPublicKey
        fingerprint = $fingerprint
    }
}

Push-Location $script:OwnerRepositoryRoot
$workDirectory = $null
try {
    Assert-OwnerDocker
    # Docker Desktop's BuildKit host-network helper can collide when Compose
    # builds several images concurrently. Sequential builds are deterministic
    # and avoid that local port race.
    $env:COMPOSE_PARALLEL_LIMIT = "1"
    $commit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Could not identify the source commit for the offline bundle."
    }
    $sourceStatus = @(& git status --porcelain=v1 --untracked-files=all)
    if ($LASTEXITCODE -ne 0) {
        throw "Could not identify the source-tree status for the offline bundle."
    }
    $sourceTreeClean = $sourceStatus.Count -eq 0
    if (-not $sourceTreeClean -and -not $AllowDirtySource) {
        throw (
            "The release exporter requires a clean source tree. Commit the release " +
            "revision first, or use -AllowDirtySource only for a non-release test bundle."
        )
    }
    # The exporter verifies the built image set by starting the hardened stack.
    # Stop/removal intentionally deletes the ephemeral runtime-secret files, so
    # recreate them from the protected credential store before Compose starts.
    Ensure-OwnerLocalEnvironment
    Assert-OwnerCredentialContinuity
    Initialize-OwnerSecretStore | Out-Null
    Write-OwnerRuntimeSecrets | Out-Null
    $version = Get-ProjectAIVersion
    if (-not $OutputPath) {
        $OutputPath = (
            ".local/offline-bundles/" +
            "project-ai-p1-v$version-windows-amd64.zip"
        )
    }
    $resolvedOutput = [IO.Path]::GetFullPath((Join-Path $script:OwnerRepositoryRoot $OutputPath))
    New-Item -ItemType Directory -Path (Split-Path -Parent $resolvedOutput) -Force | Out-Null

    if (-not $SkipBuild) {
        Write-Host "Building the exact local P1 image set..." -ForegroundColor Cyan
        # Do not use Compose's aggregate Bake path here. Docker Desktop can deadlock
        # its host-network helper during an aggregate multi-image build. These six
        # explicit builds cover every unique image; swr/atlas/arbiter-rlp share the
        # project-ai:service image.
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
                throw "Project-AI offline image failed to build for service: $service"
            }
        }
    }
    if ((Invoke-OwnerCompose up -d --wait --wait-timeout 300) -ne 0) {
        throw "The built image set did not become ready."
    }
    $hardening = Test-OwnerContainerHardening
    if (-not $hardening.verified) {
        throw "Built image hardening failed: $($hardening.failures -join '; ')"
    }

    $images = @(
        "postgres:16-alpine",
        "project-ai:api",
        "project-ai:docs-portal",
        "project-ai:proof-portal",
        "project-ai:operator-console",
        "project-ai:service",
        "project-ai:genesis"
    )
    $imageRecords = foreach ($image in $images) {
        $id = (& docker image inspect --format "{{.Id}}" $image).Trim()
        if ($LASTEXITCODE -ne 0) {
            throw "Required offline image is missing: $image"
        }
        [ordered]@{ name = $image; id = $id }
    }

    $workRoot = Join-Path (Get-OwnerStateRoot) "bundle-work"
    New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    $workDirectory = Join-Path $workRoot ([Guid]::NewGuid().ToString("N"))
    $bundleRoot = Join-Path $workDirectory "Project-AI-Offline"
    New-Item -ItemType Directory -Path $bundleRoot -Force | Out-Null
    foreach ($directory in @("scripts\owner", "docs\deployment")) {
        New-Item -ItemType Directory -Path (Join-Path $bundleRoot $directory) -Force | Out-Null
    }
    foreach ($file in @(
        "compose.yaml",
        "compose.secrets.yaml",
        ".env.example",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_NOTICES.md",
        "OWNER_QUICKSTART.md",
        "Start Project-AI.cmd",
        "Stop Project-AI.cmd",
        "Project-AI Status.cmd",
        "Install Project-AI Offline.cmd"
    )) {
        Copy-Item -LiteralPath $file -Destination (Join-Path $bundleRoot $file) -Force
    }
    Copy-Item -Path "scripts\owner\*.ps1" -Destination (Join-Path $bundleRoot "scripts\owner") -Force
    Copy-Item -LiteralPath "docs\deployment\DEPLOYMENT_MODEL.md" `
        -Destination (Join-Path $bundleRoot "docs\deployment\DEPLOYMENT_MODEL.md") -Force
    Copy-Item -LiteralPath "docs\deployment\OFFLINE_FIRST_READINESS.md" `
        -Destination (Join-Path $bundleRoot "docs\deployment\OFFLINE_FIRST_READINESS.md") -Force
    $releaseNotes = "docs\deployment\RELEASE_NOTES_v$version.md"
    Copy-Item -LiteralPath $releaseNotes `
        -Destination (Join-Path $bundleRoot $releaseNotes) -Force

    $releaseInformation = [ordered]@{
        schema_version = 1
        product = "Project-AI"
        version = $version
        release = "v$version"
        profile = "P1-offline-first-local"
        audience = "single-user"
        platform = "windows-amd64-docker-linux"
        source_commit = $commit
        source_tree_clean = $sourceTreeClean
        license = "MIT"
        startup = "Install Project-AI Offline.cmd"
        control_center = "http://127.0.0.1:4175"
        p2_status = "future-optional-not-included"
    }
    $releaseInformation | ConvertTo-Json -Depth 10 | Set-Content `
        -LiteralPath (Join-Path $bundleRoot "RELEASE.json") -Encoding utf8NoBOM

    $imageArchive = Join-Path $bundleRoot "project-ai-offline-images.tar"
    & docker save --output $imageArchive @images
    if ($LASTEXITCODE -ne 0) {
        throw "Docker could not export the offline image set."
    }
    $files = Get-ChildItem -LiteralPath $bundleRoot -Recurse -File | Sort-Object FullName
    $fileRecords = foreach ($file in $files) {
        [ordered]@{
            path = [IO.Path]::GetRelativePath($bundleRoot, $file.FullName).Replace("\", "/")
            bytes = $file.Length
            sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
        }
    }
    $manifest = [ordered]@{
        schema_version = 1
        product_version = $version
        release = "v$version"
        profile = "P1-offline-first-local"
        source_base_commit = $commit
        source_tree_clean = $sourceTreeClean
        source_status = @($sourceStatus)
        created_utc = [DateTimeOffset]::UtcNow.ToString("O")
        platform = "windows-amd64-docker-linux"
        startup = "Install Project-AI Offline.cmd"
        registry_pull_required = $false
        images = @($imageRecords)
        files = @($fileRecords)
    }
    $manifest | ConvertTo-Json -Depth 10 | Set-Content `
        -LiteralPath (Join-Path $bundleRoot "offline-bundle-manifest.json") -Encoding utf8NoBOM
    # A deterministic rebuild replaces only the selected release archive and
    # its three derived sidecars. Remove them after image/runtime verification
    # so a failed preflight cannot destroy the prior diagnostic artifact.
    foreach ($publishedPath in @(
        $resolvedOutput,
        "$resolvedOutput.sha256",
        "$resolvedOutput.sig",
        "$resolvedOutput.pub"
    )) {
        if (Test-Path -LiteralPath $publishedPath) {
            Remove-Item -LiteralPath $publishedPath -Force
        }
    }
    Compress-Archive `
        -Path (Join-Path $bundleRoot "*") `
        -DestinationPath $resolvedOutput `
        -Force
    $checksum = Write-Sha256Sidecar -ArchivePath $resolvedOutput
    $signature = $null
    if ($SigningKey) {
        $signature = Write-SshSignatureSidecar `
            -ArchivePath $resolvedOutput `
            -PrivateKeyPath $SigningKey `
            -PublicKeyPath $SigningPublicKey
    }
    elseif ($RequireSignature) {
        throw "A signing key is required when -RequireSignature is selected."
    }
    $receipt = Write-OwnerEvidenceReceipt -Operation "offline-bundle" -Status "verified" -Evidence @{
        archive = $resolvedOutput
        sha256 = $checksum.hash
        checksum_sidecar = $checksum.path
        signature = $signature
        bytes = (Get-Item -LiteralPath $resolvedOutput).Length
        version = $version
        source_base_commit = $commit
        source_tree_clean = $sourceTreeClean
        images = @($imageRecords)
        hardening = $hardening
    }
    Write-Host "P1 offline bundle created and verified." -ForegroundColor Green
    Write-Host "Archive: $resolvedOutput"
    Write-Host "SHA-256: $($checksum.hash)"
    Write-Host "Checksum: $($checksum.path)"
    if ($signature) {
        Write-Host "Signature: $($signature.signature)"
        Write-Host "Public key: $($signature.public_key)"
        Write-Host "Signing key: $($signature.fingerprint)"
    }
    Write-Host "Evidence receipt: $receipt"
    Write-Output $resolvedOutput
}
finally {
    if ($workDirectory) {
        Remove-BundleWorkDirectory -Path $workDirectory
    }
    Pop-Location
}
