#!/usr/bin/env pwsh
# Stage 18 acceptance gate - Windows / PowerShell.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$failures = [System.Collections.Generic.List[string]]::new()
$acceptanceTemp = "C:\tmp\project-ai-acceptance-temp"
New-Item -ItemType Directory -Force $acceptanceTemp | Out-Null
$env:TEMP = $acceptanceTemp
$env:TMP = $acceptanceTemp
if (-not $env:ANDROID_HOME) {
    $androidSdk = Join-Path $env:LOCALAPPDATA "Android\Sdk"
    if (Test-Path -LiteralPath $androidSdk) {
        $env:ANDROID_HOME = $androidSdk
    }
}
if ($env:ANDROID_HOME) {
    $env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
}

function Step {
    param([string]$Label, [scriptblock]$Body)
    Write-Host "`n=== $Label ===" -ForegroundColor Cyan
    try {
        $global:LASTEXITCODE = 0
        & $Body
        if ($LASTEXITCODE -ne 0) {
            throw "Exit code $LASTEXITCODE"
        }
        Write-Host "PASS: $Label" -ForegroundColor Green
    }
    catch {
        Write-Host "FAIL: ${Label}: $_" -ForegroundColor Red
        $script:failures.Add($Label)
    }
}

function Assert-CleanCheckout {
    $status = @(git status --porcelain --untracked-files=all)
    if ($LASTEXITCODE -ne 0) {
        throw "git status failed with exit code $LASTEXITCODE"
    }
    if ($status.Count -ne 0) {
        throw "checkout is not clean: $($status -join '; ')"
    }
}

function Run-Android {
    Push-Location apps/android
    try {
        .\gradlew.bat --no-daemon testDebugUnitTest assembleDebug
    }
    finally {
        Pop-Location
    }
}

function Run-DesktopSmoke {
    $previousPlatform = $env:QT_QPA_PLATFORM
    $previousSmoke = $env:PROJECT_AI_DESKTOP_SMOKE
    try {
        $env:QT_QPA_PLATFORM = "offscreen"
        $env:PROJECT_AI_DESKTOP_SMOKE = "1"
        uv run --package project-ai-desktop python -m project_ai_desktop
    }
    finally {
        $env:QT_QPA_PLATFORM = $previousPlatform
        $env:PROJECT_AI_DESKTOP_SMOKE = $previousSmoke
    }
}

function Build-And-Smoke-Desktop {
    $root = "build/acceptance/desktop"
    New-Item -ItemType Directory -Force "$root/spec" | Out-Null
    uv run --package project-ai-desktop pyinstaller `
        --noconfirm --clean --onedir `
        --name Project-AI-Desktop `
        --distpath "$root/dist" `
        --workpath "$root/work" `
        --specpath "$root/spec" `
        apps/desktop/src/project_ai_desktop/__main__.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }
    $env:QT_QPA_PLATFORM = "offscreen"
    $env:PROJECT_AI_DESKTOP_SMOKE = "1"
    & "$root/dist/Project-AI-Desktop/Project-AI-Desktop.exe"
}

function Generate-Sbom {
    New-Item -ItemType Directory -Force build/acceptance/sbom | Out-Null
    $python = uv run python -c "import sys; print(sys.executable)"
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve uv Python"
    }
    uvx --from cyclonedx-bom==7.3.0 cyclonedx-py environment `
        $python `
        --pyproject pyproject.toml `
        --output-reproducible `
        --validate `
        --output-format JSON `
        --output-file build/acceptance/sbom/project-ai-python.cdx.json
    if ($LASTEXITCODE -ne 0) {
        throw "CycloneDX generation failed with exit code $LASTEXITCODE"
    }
    uv run python -c "import json; data=json.load(open('build/acceptance/sbom/project-ai-python.cdx.json', encoding='utf-8')); assert data['bomFormat']=='CycloneDX'; assert data['components']"
}

Step "Checkout: clean baseline" { Assert-CleanCheckout }
Step "Python: exact 3.12.10 runtime" {
    uv run python -c "import sys; assert sys.version_info[:3] == (3, 12, 10), sys.version"
}
Step "Legacy source: baseline snapshot" { uv run python tools/verify_legacy_state.py }
Step "Python: install locked workspace" { uv sync --frozen --all-extras --all-packages }
Step "Repository: pre-commit and gitleaks" { uv run pre-commit run --all-files }
Step "Python: Ruff lint" { uv run ruff check . }
Step "Python: Ruff format" { uv run ruff format --check . }
Step "Python: strict MyPy" {
    uv run mypy --ignore-missing-imports `
        packages/kernel/src packages/security/src packages/governance/src `
        packages/capability/src packages/execution/src packages/companion/src `
        packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src `
        packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
}
Step "Python: tests and 80 percent branch coverage" {
    $env:QT_QPA_PLATFORM = "offscreen"
    uv run pytest -q --tb=short `
        --cov=kernel --cov=security --cov=governance --cov=capability `
        --cov=execution --cov=companion --cov=swr --cov=atlas `
        --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli `
        --cov=project_ai_desktop --cov=project_ai_services `
        --cov-branch --cov-report=term-missing --cov-fail-under=80
}
Step "Security: 312 asymmetric cases" {
    uv run pytest `
        "packages/governance/tests/test_asymmetric_security.py::test_all_published_attack_vectors_are_blocked" `
        -q --tb=short
}
Step "Arbiter: 12-test baseline" {
    uv run pytest packages/arbiter/tests/test_arbiter_gov.py -q --tb=short
}
Step "Canonical replay: 5 of 5 invariants" { uv run python tools/canonical_replay.py }
Step "Provenance: frozen 2264-commit chain" { uv run python tools/verify_frozen_history.py }
Step "Android: unit tests and debug assembly" { Run-Android }
Step "Rust: format" { cargo fmt --check }
Step "Rust: Clippy" { cargo clippy --workspace --all-targets --locked -- -D warnings }
Step "Rust: tests" { cargo test --workspace --locked }
Step "Node: install" { pnpm install --frozen-lockfile }
Step "Node: lint" { pnpm web:lint }
Step "Node: tests" { pnpm web:test }
Step "Node: builds" { pnpm web:build }
Step "Desktop: offscreen source smoke" { Run-DesktopSmoke }
Step "Desktop: unsigned onedir build and smoke" { Build-And-Smoke-Desktop }
Step "Supply chain: reproducible CycloneDX SBOM" { Generate-Sbom }
Step "Compose: config" { docker compose config --quiet }
Step "Compose: build and start seven services" {
    docker compose up -d --build --wait --wait-timeout 240
}
Step "Compose: health and container security" { uv run python tools/verify_compose_health.py }
Step "Kubernetes: Helm lint" { helm lint helm/project-ai }
Step "Kubernetes: client dry run" {
    helm template project-ai-dev helm/project-ai | kubectl apply --dry-run=client -f -
}
Step "Legacy source: final unchanged snapshot" { uv run python tools/verify_legacy_state.py }
Step "Checkout: no tracked or untracked writes" { Assert-CleanCheckout }

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "ALL CHECKS PASSED ($((Get-Date).ToUniversalTime().ToString('u')))" -ForegroundColor Green
    exit 0
}

Write-Host "FAILED CHECKS ($($failures.Count)):" -ForegroundColor Red
$failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
exit 1
