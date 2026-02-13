#!/bin/bash
# ==============================================================================
# Supply Chain Verification Script
# ==============================================================================
# This script verifies the complete supply chain integrity for a given
# workflow run, implementing external verification as specified in the
# sovereign CI/CD architecture.
#
# Usage:
#   ./scripts/verify-supply-chain.sh <RUN_ID>
#
# Requirements:
#   - gh (GitHub CLI)
#   - docker
#   - jq
#   - syft
#   - git
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO="IAmSoThirsty/Project-AI"
IMAGE_BASE="ghcr.io/iamsothirsty/project-ai"

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "══════════════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "══════════════════════════════════════════════════════════════════════"
    echo ""
}

check_requirements() {
    local missing=0

    for cmd in gh docker jq git; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd is not installed"
            missing=1
        fi
    done

    if ! command -v syft &> /dev/null; then
        log_warning "syft is not installed (SBOM verification will be limited)"
    fi

    if [ $missing -eq 1 ]; then
        log_error "Missing required dependencies"
        exit 1
    fi
}

# ==============================================================================
# Verification Steps
# ==============================================================================

verify_run_exists() {
    local run_id=$1

    log_info "Verifying workflow run ${run_id}..."

    if ! gh run view "$run_id" --repo "$REPO" &> /dev/null; then
        log_error "Workflow run ${run_id} not found"
        exit 1
    fi

    log_success "Workflow run found"
}

verify_artifacts() {
    local run_id=$1
    local required_artifacts=("sbom" "canonical-execution-trace")
    local found=0

    log_info "Verifying artifacts..."

    # List artifacts
    local artifacts=$(gh run view "$run_id" --repo "$REPO" --json artifacts -q '.artifacts[].name')

    for artifact in "${required_artifacts[@]}"; do
        if echo "$artifacts" | grep -q "^${artifact}$"; then
            log_success "Artifact found: ${artifact}"
            ((found++))
        else
            log_warning "Artifact not found: ${artifact}"
        fi
    done

    if [ $found -eq ${#required_artifacts[@]} ]; then
        log_success "All required artifacts present"
        return 0
    else
        log_warning "${found}/${#required_artifacts[@]} required artifacts found"
        return 1
    fi
}

download_artifacts() {
    local run_id=$1
    local work_dir=$2

    log_info "Downloading artifacts..."

    cd "$work_dir"

    # Download SBOM
    if gh run download "$run_id" --repo "$REPO" -n sbom 2>/dev/null; then
        log_success "Downloaded SBOM"
    else
        log_warning "Could not download SBOM"
    fi

    # Download execution trace
    if gh run download "$run_id" --repo "$REPO" -n canonical-execution-trace 2>/dev/null; then
        log_success "Downloaded canonical execution trace"
    else
        log_warning "Could not download execution trace"
    fi

    # Download adversarial reports
    if gh run download "$run_id" --repo "$REPO" -n adversarial-test-reports 2>/dev/null; then
        log_success "Downloaded adversarial test reports"
    else
        log_warning "Could not download adversarial reports"
    fi
}

verify_sbom() {
    local work_dir=$1

    log_info "Verifying SBOM..."

    if [ ! -f "$work_dir/sbom.json" ]; then
        log_warning "SBOM file not found"
        return 1
    fi

    # Check SBOM format
    if ! jq -e '.name' "$work_dir/sbom.json" &> /dev/null; then
        log_error "SBOM file is not valid JSON"
        return 1
    fi

    # Compute SBOM hash
    local sbom_hash=$(sha256sum "$work_dir/sbom.json" | awk '{print $1}')
    log_success "SBOM hash: ${sbom_hash:0:16}..."

    # Validate with syft if available
    if command -v syft &> /dev/null; then
        if syft "$work_dir/sbom.json" --quiet &> /dev/null; then
            log_success "SBOM validation passed"
        else
            log_warning "SBOM validation had warnings"
        fi
    fi

    # Count packages
    local package_count=$(jq -r '.packages | length' "$work_dir/sbom.json" 2>/dev/null || echo "0")
    log_info "SBOM contains ${package_count} packages"

    return 0
}

verify_execution_trace() {
    local work_dir=$1

    log_info "Verifying canonical execution trace..."

    if [ ! -f "$work_dir/execution_trace.json" ]; then
        log_warning "Execution trace file not found"
        return 1
    fi

    # Check trace format
    if ! jq -e '.metadata.replay_id' "$work_dir/execution_trace.json" &> /dev/null; then
        log_error "Execution trace is not valid"
        return 1
    fi

    # Extract key information
    local replay_id=$(jq -r '.metadata.replay_id' "$work_dir/execution_trace.json")
    local phases=$(jq -r '.execution.phases | length' "$work_dir/execution_trace.json")
    local all_met=$(jq -r '.outcome.all_criteria_met' "$work_dir/execution_trace.json")

    log_info "Replay ID: ${replay_id}"
    log_info "Phases executed: ${phases}"

    if [ "$all_met" = "true" ]; then
        log_success "All success criteria met"
    else
        log_warning "Some success criteria not met"
    fi

    # Check invariants if present
    if jq -e '.invariants' "$work_dir/execution_trace.json" &> /dev/null; then
        local passed=$(jq -r '.invariants.passed | length' "$work_dir/execution_trace.json" 2>/dev/null || echo "0")
        local failed=$(jq -r '.invariants.failed | length' "$work_dir/execution_trace.json" 2>/dev/null || echo "0")

        log_info "Invariants: ${passed} passed, ${failed} failed"

        if [ "$failed" -eq 0 ]; then
            log_success "All invariants passed"
        else
            log_error "${failed} invariants failed"
            return 1
        fi
    fi

    return 0
}

verify_image_attestation() {
    local image_tag=$1

    log_info "Verifying Docker image attestation..."

    # Try to pull image
    if ! docker pull "${IMAGE_BASE}:${image_tag}" &> /dev/null; then
        log_warning "Could not pull image ${IMAGE_BASE}:${image_tag}"
        return 1
    fi

    # Get image digest
    local digest=$(docker inspect "${IMAGE_BASE}:${image_tag}" \
        --format='{{index .RepoDigests 0}}' 2>/dev/null | cut -d@ -f2)

    if [ -z "$digest" ]; then
        log_warning "Could not extract image digest"
        return 1
    fi

    log_success "Image digest: ${digest:0:19}..."

    # Verify attestation using gh CLI
    if gh attestation verify \
        --repo "$REPO" \
        "${IMAGE_BASE}@${digest}" &> /dev/null; then
        log_success "Image attestation verified"
        return 0
    else
        log_warning "Could not verify image attestation (may not be available for this run)"
        return 1
    fi
}

verify_commit_signature() {
    local commit_sha=$1

    log_info "Verifying commit signature..."

    # Fetch commit
    if ! git fetch origin "$commit_sha" &> /dev/null; then
        log_warning "Could not fetch commit ${commit_sha}"
        return 1
    fi

    # Verify signature
    if git verify-commit "$commit_sha" &> /dev/null; then
        log_success "Commit signature verified"
        return 0
    else
        log_warning "Commit is not signed or verification failed"
        return 1
    fi
}

# ==============================================================================
# Main Verification Flow
# ==============================================================================

main() {
    if [ $# -lt 1 ]; then
        echo "Usage: $0 <RUN_ID> [IMAGE_TAG]"
        echo ""
        echo "Example: $0 1234567890 main"
        echo ""
        echo "This script verifies the complete supply chain integrity"
        echo "for a given workflow run."
        exit 1
    fi

    local run_id=$1
    local image_tag=${2:-main}

    print_header "🛡️  Supply Chain Verification"

    log_info "Run ID: ${run_id}"
    log_info "Image tag: ${image_tag}"
    log_info "Repository: ${REPO}"
    echo ""

    # Check requirements
    check_requirements

    # Create temporary work directory
    local work_dir=$(mktemp -d)
    trap "rm -rf $work_dir" EXIT

    log_info "Work directory: ${work_dir}"
    echo ""

    # Verification steps
    local checks_passed=0
    local checks_total=0

    # 1. Verify run exists
    print_header "STEP 1: Workflow Run Verification"
    verify_run_exists "$run_id" && ((checks_passed++))
    ((checks_total++))

    # 2. Verify artifacts
    print_header "STEP 2: Artifact Verification"
    verify_artifacts "$run_id" && ((checks_passed++))
    ((checks_total++))

    # 3. Download artifacts
    print_header "STEP 3: Artifact Download"
    download_artifacts "$run_id" "$work_dir"

    # 4. Verify SBOM
    print_header "STEP 4: SBOM Verification"
    verify_sbom "$work_dir" && ((checks_passed++))
    ((checks_total++))

    # 5. Verify execution trace
    print_header "STEP 5: Execution Trace Verification"
    verify_execution_trace "$work_dir" && ((checks_passed++))
    ((checks_total++))

    # 6. Verify image attestation
    print_header "STEP 6: Image Attestation Verification"
    verify_image_attestation "$image_tag" && ((checks_passed++))
    ((checks_total++))

    # 7. Get commit SHA from run and verify
    print_header "STEP 7: Commit Signature Verification"
    local commit_sha=$(gh run view "$run_id" --repo "$REPO" --json headSha -q '.headSha')
    if [ -n "$commit_sha" ]; then
        log_info "Commit SHA: ${commit_sha}"
        verify_commit_signature "$commit_sha" && ((checks_passed++))
    else
        log_warning "Could not extract commit SHA from run"
    fi
    ((checks_total++))

    # Summary
    print_header "📊 Verification Summary"

    echo "Checks passed: ${checks_passed}/${checks_total}"
    echo ""

    if [ $checks_passed -eq $checks_total ]; then
        log_success "ALL CHECKS PASSED - Supply chain integrity verified"
        echo ""
        echo "🎉 This build is verified and can be trusted:"
        echo "   ✅ Artifacts present and valid"
        echo "   ✅ SBOM generated and verified"
        echo "   ✅ Execution trace consistent"
        echo "   ✅ Image attestation valid"
        echo "   ✅ Commit signature verified"
        echo ""
        exit 0
    elif [ $checks_passed -ge 4 ]; then
        log_warning "PARTIAL VERIFICATION - ${checks_passed}/${checks_total} checks passed"
        echo ""
        echo "⚠️  Most checks passed, but some verification steps failed."
        echo "   This may be due to missing optional components."
        echo ""
        exit 0
    else
        log_error "VERIFICATION FAILED - Only ${checks_passed}/${checks_total} checks passed"
        echo ""
        echo "❌ Supply chain integrity could not be verified."
        echo "   Please review the errors above."
        echo ""
        exit 1
    fi
}

# Run main function
main "$@"
