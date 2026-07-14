#!/usr/bin/env pwsh
# Signs a single Windows artifact (exe/dll/msi) if a certificate is configured; otherwise
# no-ops. Shared by every call site in tools/build_windows_installer.ps1 so the no-op
# behavior cannot drift between artifacts (see docs/deployment/WINDOWS_INSTALLER.md).
#
# Usage: tools/sign_windows_artifact.ps1 -Path <file>
#
# Reads CODESIGN_CERT_PATH / CODESIGN_CERT_PASSWORD from the environment. Currently
# unsigned in this repo: no certificate is configured anywhere, so every call is a no-op
# today. This is deliberate, not a placeholder awaiting deletion -- see the Documentation
# Truth Rule in AGENTS.md.

param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Path)) {
    throw "sign_windows_artifact.ps1: no such file: $Path"
}

if (-not $env:CODESIGN_CERT_PATH -or -not $env:CODESIGN_CERT_PASSWORD) {
    Write-Host "unsigned: no signing certificate configured ($Path)"
    exit 0
}

signtool sign `
    /f "$env:CODESIGN_CERT_PATH" `
    /p "$env:CODESIGN_CERT_PASSWORD" `
    /fd sha256 `
    /tr "http://timestamp.digicert.com" `
    /td sha256 `
    "$Path"

if ($LASTEXITCODE -ne 0) {
    throw "signtool failed with exit code $LASTEXITCODE for $Path"
}

Write-Host "signed: $Path"
