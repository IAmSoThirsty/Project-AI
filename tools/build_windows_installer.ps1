#!/usr/bin/env pwsh
# Builds the Windows installer: PyInstaller onedir bundles for the desktop app and the api
# server, a WiX v7 Burn bootstrapper chaining both as MSIs, and (no-op today) signing of
# every produced artifact. Callable both locally and from CI, matching how
# tools/acceptance_gate.ps1's Build-And-Smoke-Desktop already works in both contexts.
#
# WiX Open Source Maintenance Fee: this repo is pre-alpha (0.0.3, no revenue), so the
# free-use terms of the OSMF apply -- see docs/deployment/WINDOWS_INSTALLER.md for the
# revenue threshold and what to do if that ever changes. `-acceptEula wix7` below accepts
# the EULA text (free, no payment) required by WiX v7's CLI; see
# https://docs.firegiant.com/wix/osmf/ for the exact terms.

param(
    [string]$OutputRoot = "build/windows-installer"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path "$PSScriptRoot/..").Path
Push-Location $RepoRoot
try {
    # wix build's -bindpath resolves relative paths against the .wxs source file's own
    # directory, not the invocation cwd -- verified by a real WIX8601/WIX8600 "zero files
    # harvested" failure when these were left relative. Absolute paths throughout avoid the
    # ambiguity entirely.
    $absoluteOutputRoot = Join-Path $RepoRoot $OutputRoot
    $distRoot = Join-Path $absoluteOutputRoot "dist"
    $workRoot = Join-Path $absoluteOutputRoot "work"
    $specRoot = Join-Path $absoluteOutputRoot "spec"
    $installerRoot = Join-Path $absoluteOutputRoot "installer"
    New-Item -ItemType Directory -Force $distRoot | Out-Null
    New-Item -ItemType Directory -Force $installerRoot | Out-Null

    Write-Host "`n=== Build: desktop onedir ===" -ForegroundColor Cyan
    $desktopDist = Join-Path $distRoot "desktop"
    uv run --package project-ai-desktop pyinstaller `
        --noconfirm --clean --onedir `
        --name Project-AI-Desktop `
        --distpath $desktopDist `
        --workpath (Join-Path $workRoot "desktop") `
        --specpath (Join-Path $specRoot "desktop") `
        apps/desktop/src/project_ai_desktop/__main__.py
    if ($LASTEXITCODE -ne 0) { throw "Desktop PyInstaller build failed with exit code $LASTEXITCODE" }

    Write-Host "`n=== Build: api onedir ===" -ForegroundColor Cyan
    $apiDist = Join-Path $distRoot "api"
    # uvloop is POSIX-only and is not resolved into this workspace's Windows lockfile, so it
    # must not be force-included as a hidden import here -- doing so would either be a no-op
    # (module absent) or, on a machine where some other install happened to provide it, a
    # false claim that this build path actually exercises it. httptools IS a Windows-capable
    # wheel and uvicorn[standard] pulls it in, so it is included below.
    uv run --package project-ai-api pyinstaller `
        --noconfirm --clean --onedir `
        --name project-ai-api-server `
        --distpath $apiDist `
        --workpath (Join-Path $workRoot "api") `
        --specpath (Join-Path $specRoot "api") `
        --hidden-import uvicorn.protocols.http.h11_impl `
        --hidden-import uvicorn.protocols.http.httptools_impl `
        --hidden-import uvicorn.protocols.websockets.websockets_impl `
        --hidden-import uvicorn.lifespan.on `
        --hidden-import uvicorn.loops.asyncio `
        packages/api/src/project_ai_api/server.py
    if ($LASTEXITCODE -ne 0) { throw "Api PyInstaller build failed with exit code $LASTEXITCODE" }

    Write-Host "`n=== Sign: onedir executables ===" -ForegroundColor Cyan
    & "$PSScriptRoot/sign_windows_artifact.ps1" -Path (Join-Path $desktopDist "Project-AI-Desktop\Project-AI-Desktop.exe")
    & "$PSScriptRoot/sign_windows_artifact.ps1" -Path (Join-Path $apiDist "project-ai-api-server\project-ai-api-server.exe")

    Write-Host "`n=== Build: WiX MSIs and Burn bundle ===" -ForegroundColor Cyan
    $wixSrc = "installer/windows"
    $desktopMsi = Join-Path $installerRoot "Desktop.msi"
    $apiMsi = Join-Path $installerRoot "Api.msi"
    $bundleExe = Join-Path $installerRoot "Project-AI-Desktop-Setup.exe"

    wix build -acceptEula wix7 `
        "$wixSrc/Desktop.wxs" `
        -bindpath "DesktopSourceDir=$desktopDist\Project-AI-Desktop" `
        -o $desktopMsi
    if ($LASTEXITCODE -ne 0) { throw "wix build (Desktop.msi) failed with exit code $LASTEXITCODE" }

    wix build -acceptEula wix7 `
        "$wixSrc/Api.wxs" `
        -bindpath "ApiSourceDir=$apiDist\project-ai-api-server" `
        -o $apiMsi
    if ($LASTEXITCODE -ne 0) { throw "wix build (Api.msi) failed with exit code $LASTEXITCODE" }

    & "$PSScriptRoot/sign_windows_artifact.ps1" -Path $desktopMsi
    & "$PSScriptRoot/sign_windows_artifact.ps1" -Path $apiMsi

    wix build -acceptEula wix7 `
        "$wixSrc/Bundle.wxs" `
        -ext WixToolset.BootstrapperApplications.wixext `
        -d "DesktopMsiPath=$desktopMsi" `
        -d "ApiMsiPath=$apiMsi" `
        -o $bundleExe
    if ($LASTEXITCODE -ne 0) { throw "wix build (Bundle.exe) failed with exit code $LASTEXITCODE" }

    & "$PSScriptRoot/sign_windows_artifact.ps1" -Path $bundleExe

    Write-Host "`nBuilt: $bundleExe" -ForegroundColor Green
    Write-Output $bundleExe
}
finally {
    Pop-Location
}
