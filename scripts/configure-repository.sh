#!/bin/bash
# ==============================================================================
# Repository Configuration Script
# ==============================================================================
# This script helps configure GitHub repository settings for the sovereign
# CI/CD pipeline, implementing the hardening requirements specified in
# docs/REPOSITORY_HARDENING.md
#
# Usage:
#   ./scripts/configure-repository.sh [--check-only]
#
# Requirements:
#   - gh (GitHub CLI) with admin access to repository
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
CHECK_ONLY=false

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
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI (gh) is not installed"
        echo ""
        echo "Install from: https://cli.github.com/"
        exit 1
    fi

    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        log_error "Not authenticated with GitHub CLI"
        echo ""
        echo "Run: gh auth login"
        exit 1
    fi

    log_success "GitHub CLI authenticated"
}

# ==============================================================================
# Configuration Checks
# ==============================================================================

check_branch_protection() {
    local branch=$1

    log_info "Checking branch protection for ${branch}..."

    # Get branch protection settings
    local protection=$(gh api "/repos/${REPO}/branches/${branch}/protection" 2>/dev/null || echo "{}")

    if [ "$protection" = "{}" ]; then
        log_warning "No branch protection configured for ${branch}"
        return 1
    fi

    # Check required reviews
    local required_reviews=$(echo "$protection" | jq -r '.required_pull_request_reviews.required_approving_review_count // 0')
    if [ "$required_reviews" -ge 2 ]; then
        log_success "Required approvals: ${required_reviews}"
    else
        log_warning "Required approvals: ${required_reviews} (should be 2+)"
    fi

    # Check required status checks
    local status_checks=$(echo "$protection" | jq -r '.required_status_checks.checks // [] | length')
    if [ "$status_checks" -gt 0 ]; then
        log_success "Required status checks: ${status_checks}"
    else
        log_warning "No required status checks configured"
    fi

    # Check signed commits
    local signed_commits=$(echo "$protection" | jq -r '.required_signatures.enabled // false')
    if [ "$signed_commits" = "true" ]; then
        log_success "Signed commits required"
    else
        log_warning "Signed commits not required"
    fi

    # Check linear history
    local linear_history=$(echo "$protection" | jq -r '.required_linear_history.enabled // false')
    if [ "$linear_history" = "true" ]; then
        log_success "Linear history required"
    else
        log_warning "Linear history not enforced"
    fi

    return 0
}

check_security_features() {
    log_info "Checking security features..."

    # Get repository settings
    local repo_info=$(gh api "/repos/${REPO}")

    # Check vulnerability alerts
    local vuln_alerts=$(echo "$repo_info" | jq -r '.has_vulnerability_alerts // false')
    if [ "$vuln_alerts" = "true" ]; then
        log_success "Vulnerability alerts enabled"
    else
        log_warning "Vulnerability alerts disabled"
    fi

    # Check if Dependabot is enabled (separate API call)
    if gh api "/repos/${REPO}/vulnerability-alerts" &> /dev/null; then
        log_success "Dependabot alerts enabled"
    else
        log_warning "Dependabot alerts disabled"
    fi

    # Check security scanning
    local code_scanning=$(gh api "/repos/${REPO}/code-scanning/alerts" 2>/dev/null | jq -r 'length // -1')
    if [ "$code_scanning" != "-1" ]; then
        log_success "Code scanning configured (${code_scanning} alerts)"
    else
        log_warning "Code scanning not configured or no access"
    fi

    return 0
}

check_actions_permissions() {
    log_info "Checking Actions permissions..."

    # Get Actions permissions
    local actions_perms=$(gh api "/repos/${REPO}/actions/permissions" 2>/dev/null || echo "{}")

    if [ "$actions_perms" = "{}" ]; then
        log_warning "Could not retrieve Actions permissions"
        return 1
    fi

    # Check if Actions are enabled
    local enabled=$(echo "$actions_perms" | jq -r '.enabled // false')
    if [ "$enabled" = "true" ]; then
        log_success "GitHub Actions enabled"
    else
        log_error "GitHub Actions disabled"
        return 1
    fi

    # Check allowed actions
    local allowed=$(echo "$actions_perms" | jq -r '.allowed_actions // "all"')
    log_info "Allowed actions: ${allowed}"

    if [ "$allowed" = "selected" ]; then
        log_success "Actions restricted to selected (recommended)"
    else
        log_warning "All actions allowed (consider restricting)"
    fi

    return 0
}

check_required_labels() {
    log_info "Checking required labels..."

    local required_labels=("security" "supply-chain" "auto-merge" "breaking-change" "release" "canonical" "triumvirate")
    local found=0

    # Get all labels
    local labels=$(gh api "/repos/${REPO}/labels" --jq '.[].name')

    for label in "${required_labels[@]}"; do
        if echo "$labels" | grep -q "^${label}$"; then
            ((found++))
        else
            log_warning "Label missing: ${label}"
        fi
    done

    if [ $found -eq ${#required_labels[@]} ]; then
        log_success "All ${#required_labels[@]} required labels present"
    else
        log_warning "${found}/${#required_labels[@]} required labels found"
    fi

    return 0
}

check_codeowners() {
    log_info "Checking CODEOWNERS file..."

    if [ -f ".github/CODEOWNERS" ]; then
        log_success "CODEOWNERS file exists"

        # Count entries
        local entries=$(grep -v "^#" .github/CODEOWNERS | grep -v "^$" | wc -l)
        log_info "CODEOWNERS entries: ${entries}"
    else
        log_warning "CODEOWNERS file not found"
        return 1
    fi

    return 0
}

# ==============================================================================
# Configuration Application
# ==============================================================================

apply_branch_protection() {
    local branch=$1

    log_info "Applying branch protection to ${branch}..."

    # Create protection configuration
    local protection_config=$(cat <<EOF
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "🛡️ Sovereign Pipeline - Full Trust Chain"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 2
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
)

    if gh api -X PUT "/repos/${REPO}/branches/${branch}/protection" \
        --input - <<< "$protection_config" &> /dev/null; then
        log_success "Branch protection applied to ${branch}"
        return 0
    else
        log_error "Failed to apply branch protection to ${branch}"
        return 1
    fi
}

enable_security_features() {
    log_info "Enabling security features..."

    # Enable vulnerability alerts
    if gh api -X PUT "/repos/${REPO}/vulnerability-alerts" &> /dev/null; then
        log_success "Vulnerability alerts enabled"
    else
        log_warning "Could not enable vulnerability alerts"
    fi

    # Enable automated security fixes
    if gh api -X PUT "/repos/${REPO}/automated-security-fixes" &> /dev/null; then
        log_success "Automated security fixes enabled"
    else
        log_warning "Could not enable automated security fixes"
    fi

    return 0
}

create_required_labels() {
    log_info "Creating required labels..."

    local labels=(
        "security:b60205:Security-related issues/PRs"
        "supply-chain:d93f0b:Supply chain security"
        "auto-merge:0e8a16:Auto-approve after tests pass"
        "breaking-change:d73a4a:Breaking API changes"
        "release:0075ca:Release preparation"
        "canonical:5319e7:Canonical scenario changes"
        "triumvirate:fbca04:Triumvirate system changes"
    )

    for label_def in "${labels[@]}"; do
        IFS=':' read -r name color description <<< "$label_def"

        if gh api "/repos/${REPO}/labels" --jq '.[].name' | grep -q "^${name}$"; then
            log_info "Label exists: ${name}"
        else
            if gh api -X POST "/repos/${REPO}/labels" \
                -f name="$name" \
                -f color="$color" \
                -f description="$description" &> /dev/null; then
                log_success "Created label: ${name}"
            else
                log_warning "Could not create label: ${name}"
            fi
        fi
    done

    return 0
}

# ==============================================================================
# Main Flow
# ==============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --check-only)
                CHECK_ONLY=true
                shift
                ;;
            --help)
                echo "Usage: $0 [--check-only]"
                echo ""
                echo "Options:"
                echo "  --check-only    Only check configuration without applying changes"
                echo "  --help          Show this help message"
                echo ""
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    print_header "🔒 Repository Configuration for Sovereign CI/CD"

    log_info "Repository: ${REPO}"
    log_info "Mode: $([ "$CHECK_ONLY" = true ] && echo "Check Only" || echo "Apply Configuration")"
    echo ""

    # Check requirements
    check_requirements
    echo ""

    # Verification checks
    local checks_passed=0
    local checks_total=0

    print_header "📋 Configuration Verification"

    # Check branch protection
    log_info "Branch Protection Checks:"
    echo ""
    for branch in main release; do
        if check_branch_protection "$branch"; then
            ((checks_passed++))
        fi
        ((checks_total++))
        echo ""
    done

    # Check security features
    if check_security_features; then
        ((checks_passed++))
    fi
    ((checks_total++))
    echo ""

    # Check Actions permissions
    if check_actions_permissions; then
        ((checks_passed++))
    fi
    ((checks_total++))
    echo ""

    # Check labels
    if check_required_labels; then
        ((checks_passed++))
    fi
    ((checks_total++))
    echo ""

    # Check CODEOWNERS
    if check_codeowners; then
        ((checks_passed++))
    fi
    ((checks_total++))

    # Summary
    print_header "📊 Verification Summary"
    echo "Checks passed: ${checks_passed}/${checks_total}"
    echo ""

    if [ $checks_passed -eq $checks_total ]; then
        log_success "All configuration checks passed!"
        echo ""
        exit 0
    fi

    # If check-only mode, exit here
    if [ "$CHECK_ONLY" = true ]; then
        log_warning "Some configuration checks failed"
        echo ""
        echo "Run without --check-only to apply recommended configuration."
        echo ""
        exit 1
    fi

    # Apply configuration
    print_header "🔧 Applying Configuration"

    log_warning "This will modify repository settings"
    read -p "Continue? (y/N): " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Configuration cancelled"
        exit 0
    fi

    echo ""

    # Apply branch protection
    for branch in main release; do
        apply_branch_protection "$branch"
    done
    echo ""

    # Enable security features
    enable_security_features
    echo ""

    # Create labels
    create_required_labels
    echo ""

    print_header "✅ Configuration Complete"

    log_success "Repository configuration applied"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review branch protection settings in GitHub UI"
    echo "   2. Ensure CODEOWNERS file is present and configured"
    echo "   3. Enable signed commits requirement manually (requires admin)"
    echo "   4. Configure Actions allowed list in repository settings"
    echo ""
    echo "See: docs/REPOSITORY_HARDENING.md for complete checklist"
    echo ""
}

# Run main function
main "$@"
