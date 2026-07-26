[CmdletBinding()]
param(
    [string]$BundleRoot = "",
    [string]$ExistingOwnerState = "",
    [SecureString]$PortablePassphrase,
    [switch]$NoBrowser,
    [switch]$ImagesOnly
)

$ErrorActionPreference = "Stop"
if (-not $BundleRoot) {
    $BundleRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
}
else {
    $BundleRoot = [IO.Path]::GetFullPath($BundleRoot)
}
$manifestPath = Join-Path $BundleRoot "offline-bundle-manifest.json"
$imagesPath = Join-Path $BundleRoot "project-ai-offline-images.tar"
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Offline bundle manifest is missing: $manifestPath"
}
if (-not (Test-Path -LiteralPath $imagesPath)) {
    throw "Offline container image archive is missing: $imagesPath"
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ($manifest.schema_version -ne 1 -or $manifest.profile -ne "P1-offline-first-local") {
    throw "This is not a supported Project-AI P1 offline bundle."
}
foreach ($record in $manifest.files) {
    $candidate = [IO.Path]::GetFullPath((Join-Path $BundleRoot $record.path))
    if (-not $candidate.StartsWith($BundleRoot, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Offline bundle manifest contains an unsafe path: $($record.path)"
    }
    if (-not (Test-Path -LiteralPath $candidate)) {
        throw "Offline bundle is missing $($record.path)."
    }
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $candidate).Hash.ToLowerInvariant()
    if ($actual -ne $record.sha256) {
        throw "Offline bundle hash mismatch for $($record.path)."
    }
}
& docker version --format "{{.Server.Version}}" *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is installed, but its Linux container engine is not running."
}
& docker load --input $imagesPath
if ($LASTEXITCODE -ne 0) {
    throw "Docker could not import the Project-AI offline images."
}
foreach ($image in $manifest.images) {
    $actualId = & docker image inspect --format "{{.Id}}" $image.name
    if ($LASTEXITCODE -ne 0 -or $actualId -ne $image.id) {
        throw "Imported image identity mismatch for $($image.name)."
    }
}
Write-Host "Offline images imported and verified." -ForegroundColor Green
if (-not $ImagesOnly) {
    if ($ExistingOwnerState) {
        $existingStateRoot = [IO.Path]::GetFullPath($ExistingOwnerState)
        $existingCredentials = Join-Path $existingStateRoot "credentials"
        $targetCredentials = Join-Path $BundleRoot ".owner-state\credentials"
        if (-not (Test-Path -LiteralPath $existingCredentials -PathType Container)) {
            throw "Existing owner-state credential directory is missing: $existingCredentials"
        }
        if (Test-Path -LiteralPath $targetCredentials) {
            $sourceHashes = @(Get-ChildItem -LiteralPath $existingCredentials -File | ForEach-Object {
                "$($_.Name):$((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash)"
            } | Sort-Object)
            $targetHashes = @(Get-ChildItem -LiteralPath $targetCredentials -File | ForEach-Object {
                "$($_.Name):$((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash)"
            } | Sort-Object)
            if (($sourceHashes -join "`n") -ne ($targetHashes -join "`n")) {
                throw "The target already contains a different owner credential store."
            }
        }
        else {
            New-Item -ItemType Directory -Path (Split-Path -Parent $targetCredentials) -Force | Out-Null
            Copy-Item -LiteralPath $existingCredentials -Destination $targetCredentials -Recurse
        }
        Write-Host "Existing encrypted owner credentials retained for this upgrade." -ForegroundColor Green
    }
    & (Join-Path $BundleRoot "scripts\owner\Start-ProjectAI.ps1") `
        -Offline -NoBrowser:$NoBrowser -PortablePassphrase $PortablePassphrase
    if ($LASTEXITCODE -ne 0) {
        throw "The imported offline Project-AI stack did not start successfully."
    }
}
