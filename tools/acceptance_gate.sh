#!/usr/bin/env bash
# Stage 18 acceptance gate - POSIX-compatible shell.
set -uo pipefail

failures=()

step() {
    local label="$1"
    shift
    printf '\n=== %s ===\n' "$label"
    if "$@"; then
        printf 'PASS: %s\n' "$label"
    else
        printf 'FAIL: %s\n' "$label"
        failures+=("$label")
    fi
}

assert_clean_checkout() {
    local status
    status="$(git status --porcelain --untracked-files=all)" || return 1
    if [[ -n "$status" ]]; then
        printf 'checkout is not clean:\n%s\n' "$status" >&2
        return 1
    fi
}

run_mypy() {
    uv run mypy --ignore-missing-imports \
        packages/kernel/src packages/security/src packages/governance/src \
        packages/capability/src packages/execution/src packages/companion/src \
        packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src \
        packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
}

run_coverage() {
    QT_QPA_PLATFORM=offscreen uv run pytest -q --tb=short \
        --cov=kernel --cov=security --cov=governance --cov=capability \
        --cov=execution --cov=companion --cov=swr --cov=atlas \
        --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli \
        --cov=project_ai_desktop --cov=project_ai_services \
        --cov-branch --cov-report=term-missing --cov-fail-under=80
}

run_android() {
    (cd apps/android && ./gradlew --no-daemon testDebugUnitTest assembleDebug)
}

run_desktop_smoke() {
    QT_QPA_PLATFORM=offscreen PROJECT_AI_DESKTOP_SMOKE=1 \
        uv run --package project-ai-desktop python -m project_ai_desktop
}

build_and_smoke_desktop() {
    local root="build/acceptance/desktop"
    local executable
    mkdir -p "$root/spec"
    uv run --package project-ai-desktop pyinstaller \
        --noconfirm --clean --onedir \
        --name Project-AI-Desktop \
        --distpath "$root/dist" \
        --workpath "$root/work" \
        --specpath "$root/spec" \
        apps/desktop/src/project_ai_desktop/__main__.py || return 1
    executable="$root/dist/Project-AI-Desktop/Project-AI-Desktop"
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) executable="${executable}.exe" ;;
    esac
    QT_QPA_PLATFORM=offscreen PROJECT_AI_DESKTOP_SMOKE=1 "$executable"
}

# No POSIX equivalent of Windows installer build/smoke: WiX, MSI, and signtool are
# Windows-only tools. tools/acceptance_gate.ps1 has a Build-And-Smoke-Installer step that
# this script deliberately does not mirror.

generate_sbom() {
    local python
    mkdir -p build/acceptance/sbom
    python="$(uv run python -c 'import sys; print(sys.executable)')" || return 1
    uvx --from cyclonedx-bom==7.3.0 cyclonedx-py environment \
        "$python" \
        --pyproject pyproject.toml \
        --output-reproducible \
        --validate \
        --output-format JSON \
        --output-file build/acceptance/sbom/project-ai-python.cdx.json || return 1
    uv run python -c "import json; data=json.load(open('build/acceptance/sbom/project-ai-python.cdx.json', encoding='utf-8')); assert data['bomFormat']=='CycloneDX'; assert data['components']"
}

run_kubernetes_manifest_verification() {
    helm template project-ai-dev helm/project-ai | uv run python tools/verify_helm_template.py
}

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        export TMPDIR=/c/tmp/project-ai-acceptance-temp
        export TEMP="$TMPDIR"
        export TMP="$TMPDIR"
        mkdir -p "$TMPDIR"
        if [[ -z "${ANDROID_HOME:-}" && -n "${LOCALAPPDATA:-}" ]]; then
            ANDROID_HOME="$(cygpath -w "$(cygpath -u "$LOCALAPPDATA")/Android/Sdk")"
            export ANDROID_HOME
        fi
        if [[ -n "${ANDROID_HOME:-}" ]]; then
            export ANDROID_SDK_ROOT="$ANDROID_HOME"
        fi
        ;;
    *) export RUSTUP_TOOLCHAIN=stable ;;
esac

step "Checkout: clean baseline" assert_clean_checkout
step "Python: exact 3.12.10 runtime" \
    uv run python -c 'import sys; assert sys.version_info[:3] == (3, 12, 10), sys.version'
step "Legacy source: baseline snapshot" uv run python tools/verify_legacy_state.py
step "Python: install locked workspace" uv sync --frozen --all-extras --all-packages
step "Repository: pre-commit and gitleaks" uv run pre-commit run --all-files
step "Python: Ruff lint" uv run ruff check .
step "Python: Ruff format" uv run ruff format --check .
step "Python: strict MyPy" run_mypy
step "Python: tests and 80 percent branch coverage" run_coverage
step "Security: 312 asymmetric cases" \
    uv run pytest 'packages/governance/tests/test_asymmetric_security.py::test_all_published_attack_vectors_are_blocked' -q --tb=short
step "Arbiter: 12-test baseline" \
    uv run pytest packages/arbiter/tests/test_arbiter_gov.py -q --tb=short
step "Canonical replay: 5 of 5 invariants" uv run python tools/canonical_replay.py
step "Provenance: frozen 2264-commit chain" uv run python tools/verify_frozen_history.py
step "Android: unit tests and debug assembly" run_android
step "Rust: format" cargo fmt --check
step "Rust: Clippy" cargo clippy --workspace --all-targets --locked -- -D warnings
step "Rust: tests" cargo test --workspace --locked
step "Node: install" pnpm install --frozen-lockfile
step "Node: lint" pnpm web:lint
step "Node: tests" pnpm web:test
step "Node: builds" pnpm web:build
step "Desktop: offscreen source smoke" run_desktop_smoke
step "Desktop: unsigned onedir build and smoke" build_and_smoke_desktop
step "Supply chain: reproducible CycloneDX SBOM" generate_sbom
step "Compose: config" docker compose config --quiet
step "Compose: build and start seven services" \
    docker compose up -d --build --wait --wait-timeout 240
step "Compose: health and container security" uv run python tools/verify_compose_health.py
step "Kubernetes: Helm lint" helm lint helm/project-ai
step "Kubernetes: offline manifest verification" run_kubernetes_manifest_verification
step "Legacy source: final unchanged snapshot" uv run python tools/verify_legacy_state.py
step "Checkout: no tracked or untracked writes" assert_clean_checkout

echo ""
if [[ ${#failures[@]} -eq 0 ]]; then
    printf 'ALL CHECKS PASSED (%s)\n' "$(date -u)"
    exit 0
fi

printf 'FAILED CHECKS (%d):\n' "${#failures[@]}"
printf '  - %s\n' "${failures[@]}"
exit 1
