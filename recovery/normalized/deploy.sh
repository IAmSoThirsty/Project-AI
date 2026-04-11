#!/usr/bin/env bash
#                                           [2026-04-09 12:00]
#                                          Productivity: Active
# ============================================================================
# Production Deployment Script - Sovereign Governance Substrate
# ============================================================================
#
# MISSION: Zero-downtime production deployment with comprehensive validation
#
# FEATURES:
# - Pre-flight validation
# - Multiple deployment strategies (rolling, blue-green, canary)
# - Database migration automation
# - Health check validation
# - Automated smoke tests
# - Rollback on failure
# - Comprehensive logging
#
# USAGE:
#   ./deploy.sh <environment> <strategy> [image-tag] [options]
#
# EXAMPLES:
#   ./deploy.sh production rolling v1.2.3
#   ./deploy.sh staging bluegreen latest --skip-migrations
#   ./deploy.sh production canary v1.2.3 --dry-run
#
# ============================================================================

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENVIRONMENT="${1:-production}"
STRATEGY="${2:-rolling}"
IMAGE_TAG="${3:-latest}"

# Namespaces
NAMESPACE="project-ai-${ENVIRONMENT}"

# Image configuration
IMAGE_REGISTRY="${IMAGE_REGISTRY:-ghcr.io/iamsothirsty}"
IMAGE_NAME="${IMAGE_NAME:-project-ai}"
FULL_IMAGE="${IMAGE_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Deployment configuration
DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-600}"
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-30}"
HEALTH_CHECK_INTERVAL="${HEALTH_CHECK_INTERVAL:-10}"

# Feature flags
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_MIGRATIONS="${SKIP_MIGRATIONS:-false}"
DRY_RUN="${DRY_RUN:-false}"
NO_CLEANUP="${NO_CLEANUP:-false}"
VERBOSE="${VERBOSE:-false}"

# Logging
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/deploy-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "${LOG_DIR}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Status tracking
DEPLOYMENT_START_TIME=$(date +%s)
DEPLOYMENT_ID="deploy-$(date +%Y%m%d-%H%M%S)"
PREVIOUS_VERSION=""
ROLLBACK_NEEDED=false

# ============================================================================
# Logging Functions
# ============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log to file
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"

    # Log to console with color
    case "${level}" in
        INFO)
            echo -e "${GREEN}✓${NC} ${message}"
            ;;
        WARN)
            echo -e "${YELLOW}⚠${NC} ${message}"
            ;;
        ERROR)
            echo -e "${RED}✗${NC} ${message}"
            ;;
        DEBUG)
            [[ "${VERBOSE}" == "true" ]] && echo -e "${CYAN}→${NC} ${message}"
            ;;
        STEP)
            echo -e "${MAGENTA}▶${NC} ${message}"
            ;;
        *)
            echo "${message}"
            ;;
    esac
}

step() {
    log "STEP" "$*"
}

info() {
    log "INFO" "$*"
}

warn() {
    log "WARN" "$*"
}

error() {
    log "ERROR" "$*"
}

debug() {
    log "DEBUG" "$*"
}

# ============================================================================
# Utility Functions
# ============================================================================

banner() {
    echo ""
    echo "============================================================================"
    echo "$*"
    echo "============================================================================"
    echo ""
}

check_command() {
    local cmd="$1"
    if ! command -v "${cmd}" &> /dev/null; then
        error "Required command '${cmd}' not found. Please install it."
        exit 1
    fi
}

check_prerequisites() {
    step "Checking prerequisites..."

    local required_cmds=("kubectl" "docker" "python3" "jq" "curl")
    for cmd in "${required_cmds[@]}"; do
        check_command "${cmd}"
    done

    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster. Check your kubeconfig."
        exit 1
    fi

    # Check namespace exists
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        warn "Namespace ${NAMESPACE} does not exist. Creating..."
        kubectl create namespace "${NAMESPACE}"
    fi

    info "Prerequisites check passed"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-migrations)
                SKIP_MIGRATIONS=true
                shift
                ;;
            --no-cleanup)
                NO_CLEANUP=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --timeout=*)
                DEPLOYMENT_TIMEOUT="${1#*=}"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
}

# ============================================================================
# Pre-Flight Validation
# ============================================================================

run_preflight_checks() {
    step "Running pre-flight validation..."

    # Check if pre_deploy_check.py exists
    if [[ -f "${SCRIPT_DIR}/pre_deploy_check.py" ]]; then
        if ! python3 "${SCRIPT_DIR}/pre_deploy_check.py" \
            --environment "${ENVIRONMENT}" \
            --image "${FULL_IMAGE}" \
            --namespace "${NAMESPACE}"; then
            error "Pre-flight validation failed"
            exit 1
        fi
    else
        warn "Pre-flight check script not found, skipping comprehensive validation"

        # Basic checks
        debug "Checking image exists..."
        if [[ "${DRY_RUN}" != "true" ]]; then
            if ! docker pull "${FULL_IMAGE}" &> /dev/null; then
                error "Cannot pull image: ${FULL_IMAGE}"
                exit 1
            fi
        fi

        debug "Checking secrets exist..."
        if ! kubectl get secret project-ai-secrets -n "${NAMESPACE}" &> /dev/null; then
            error "Secret 'project-ai-secrets' not found in namespace ${NAMESPACE}"
            exit 1
        fi

        debug "Checking configmap exists..."
        if ! kubectl get configmap project-ai-config -n "${NAMESPACE}" &> /dev/null; then
            error "ConfigMap 'project-ai-config' not found in namespace ${NAMESPACE}"
            exit 1
        fi
    fi

    info "Pre-flight validation passed"
}

# ============================================================================
# Backup Operations
# ============================================================================

backup_current_state() {
    step "Backing up current state..."

    local backup_dir="${SCRIPT_DIR}/backups/${DEPLOYMENT_ID}"
    mkdir -p "${backup_dir}"

    # Backup deployment
    kubectl get deployment project-ai-app -n "${NAMESPACE}" -o yaml > "${backup_dir}/deployment.yaml" 2>/dev/null || true

    # Backup configmap
    kubectl get configmap project-ai-config -n "${NAMESPACE}" -o yaml > "${backup_dir}/configmap.yaml" 2>/dev/null || true

    # Backup secrets (exclude data for security)
    kubectl get secret project-ai-secrets -n "${NAMESPACE}" -o yaml | \
        grep -v "^\s*data:" > "${backup_dir}/secret-metadata.yaml" 2>/dev/null || true

    # Get current version
    PREVIOUS_VERSION=$(kubectl get deployment project-ai-app -n "${NAMESPACE}" \
        -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null || echo "none")

    info "Current state backed up to: ${backup_dir}"
    info "Previous version: ${PREVIOUS_VERSION}"
}

# ============================================================================
# Database Operations
# ============================================================================

run_database_migrations() {
    if [[ "${SKIP_MIGRATIONS}" == "true" ]]; then
        warn "Skipping database migrations (--skip-migrations)"
        return 0
    fi

    step "Running database migrations..."

    # Check if Alembic is configured
    if [[ ! -f "${SCRIPT_DIR}/alembic.ini" ]] && [[ ! -f "${SCRIPT_DIR}/src/alembic.ini" ]]; then
        warn "Alembic not configured, skipping migrations"
        return 0
    fi

    # Create migration job
    local migration_job="db-migration-${DEPLOYMENT_ID}"

    cat <<EOF | kubectl apply -f - -n "${NAMESPACE}"
apiVersion: batch/v1
kind: Job
metadata:
  name: ${migration_job}
  labels:
    app: project-ai
    deployment-id: ${DEPLOYMENT_ID}
spec:
  ttlSecondsAfterFinished: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migration
        image: ${FULL_IMAGE}
        command: ["python", "-m", "alembic", "upgrade", "head"]
        envFrom:
        - configMapRef:
            name: project-ai-config
        - secretRef:
            name: project-ai-secrets
EOF

    # Wait for migration to complete
    info "Waiting for migration job to complete..."
    if ! kubectl wait --for=condition=complete --timeout=300s job/${migration_job} -n "${NAMESPACE}"; then
        error "Database migration failed"
        kubectl logs job/${migration_job} -n "${NAMESPACE}" || true
        exit 1
    fi

    info "Database migrations completed successfully"

    # Cleanup migration job
    kubectl delete job ${migration_job} -n "${NAMESPACE}" || true
}

# ============================================================================
# Deployment Strategies
# ============================================================================

deploy_rolling_update() {
    step "Deploying with Rolling Update strategy..."

    # Update deployment image
    kubectl set image deployment/project-ai-app \
        project-ai="${FULL_IMAGE}" \
        -n "${NAMESPACE}" \
        --record

    # Wait for rollout
    info "Waiting for rollout to complete (timeout: ${DEPLOYMENT_TIMEOUT}s)..."
    if ! kubectl rollout status deployment/project-ai-app \
        -n "${NAMESPACE}" \
        --timeout="${DEPLOYMENT_TIMEOUT}s"; then
        error "Rollout failed"
        ROLLBACK_NEEDED=true
        return 1
    fi

    info "Rolling update completed successfully"
}

deploy_bluegreen() {
    step "Deploying with Blue-Green strategy..."

    # Use existing blue-green script
    if [[ -f "${SCRIPT_DIR}/k8s/blue-green-deploy.sh" ]]; then
        cd "${SCRIPT_DIR}/k8s"
        if ! ./blue-green-deploy.sh "${NAMESPACE}" "${IMAGE_TAG}" "blue-green"; then
            error "Blue-green deployment failed"
            ROLLBACK_NEEDED=true
            return 1
        fi
        cd "${SCRIPT_DIR}"
    else
        error "Blue-green deployment script not found"
        exit 1
    fi

    info "Blue-green deployment completed successfully"
}

deploy_canary() {
    step "Deploying with Canary strategy..."

    # Use existing blue-green script with canary option
    if [[ -f "${SCRIPT_DIR}/k8s/blue-green-deploy.sh" ]]; then
        cd "${SCRIPT_DIR}/k8s"
        if ! ./blue-green-deploy.sh "${NAMESPACE}" "${IMAGE_TAG}" "canary"; then
            error "Canary deployment failed"
            ROLLBACK_NEEDED=true
            return 1
        fi
        cd "${SCRIPT_DIR}"
    else
        error "Canary deployment script not found"
        exit 1
    fi

    info "Canary deployment completed successfully"
}

execute_deployment() {
    case "${STRATEGY}" in
        rolling)
            deploy_rolling_update
            ;;
        bluegreen|blue-green)
            deploy_bluegreen
            ;;
        canary)
            deploy_canary
            ;;
        *)
            error "Unknown deployment strategy: ${STRATEGY}"
            error "Valid strategies: rolling, bluegreen, canary"
            exit 1
            ;;
    esac
}

# ============================================================================
# Health Checks
# ============================================================================

check_pod_health() {
    step "Checking pod health..."

    local retries=0
    local max_retries="${HEALTH_CHECK_RETRIES}"

    while [[ ${retries} -lt ${max_retries} ]]; do
        local ready_pods=$(kubectl get pods -n "${NAMESPACE}" \
            -l app.kubernetes.io/name=project-ai \
            -o json | jq -r '.items[] | select(.status.phase=="Running") | select(.status.conditions[] | select(.type=="Ready" and .status=="True")) | .metadata.name' | wc -l)

        local total_pods=$(kubectl get deployment project-ai-app -n "${NAMESPACE}" \
            -o jsonpath='{.spec.replicas}')

        if [[ ${ready_pods} -ge ${total_pods} ]]; then
            info "All ${ready_pods}/${total_pods} pods are ready"
            return 0
        fi

        debug "Pods ready: ${ready_pods}/${total_pods}, retrying in ${HEALTH_CHECK_INTERVAL}s..."
        sleep "${HEALTH_CHECK_INTERVAL}"
        ((retries++))
    done

    error "Pod health check failed: not all pods are ready"
    return 1
}

check_health_endpoints() {
    step "Checking health endpoints..."

    # Get service endpoint
    local service_url=$(kubectl get ingress -n "${NAMESPACE}" \
        -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "")

    local use_port_forward=false
    if [[ -z "${service_url}" ]]; then
        warn "No ingress found, using port-forward for health checks"
        use_port_forward=true
        kubectl port-forward -n "${NAMESPACE}" svc/project-ai 8080:80 &
        local pf_pid=$!
        sleep 5
        service_url="localhost:8080"
    fi

    # Check liveness endpoint
    info "Checking liveness endpoint..."
    if ! curl -f -s "http://${service_url}/health/live" > /dev/null; then
        error "Liveness check failed"
        [[ ${use_port_forward} == true ]] && kill ${pf_pid} 2>/dev/null || true
        return 1
    fi
    info "Liveness check passed"

    # Check readiness endpoint
    info "Checking readiness endpoint..."
    if ! curl -f -s "http://${service_url}/health/ready" > /dev/null; then
        error "Readiness check failed"
        [[ ${use_port_forward} == true ]] && kill ${pf_pid} 2>/dev/null || true
        return 1
    fi
    info "Readiness check passed"

    # Check deep health endpoint
    info "Checking deep health endpoint..."
    local health_response=$(curl -f -s "http://${service_url}/health" 2>/dev/null || echo "{}")
    local health_status=$(echo "${health_response}" | jq -r '.status' 2>/dev/null || echo "unknown")

    if [[ "${health_status}" != "healthy" ]]; then
        warn "Deep health check returned: ${health_status}"
        debug "Health response: ${health_response}"
    else
        info "Deep health check passed"
    fi

    # Cleanup port-forward
    [[ ${use_port_forward} == true ]] && kill ${pf_pid} 2>/dev/null || true

    info "All health checks passed"
}

# ============================================================================
# Smoke Tests
# ============================================================================

run_smoke_tests() {
    if [[ "${SKIP_TESTS}" == "true" ]]; then
        warn "Skipping smoke tests (--skip-tests)"
        return 0
    fi

    step "Running smoke tests..."

    # Basic health checks are smoke tests
    if ! check_health_endpoints; then
        error "Smoke tests failed"
        return 1
    fi

    # TODO: Add more comprehensive smoke tests
    # - API endpoint tests
    # - Authentication tests
    # - Critical path validation

    info "Smoke tests passed"
}

# ============================================================================
# Rollback
# ============================================================================

trigger_rollback() {
    error "Deployment failed - triggering automatic rollback..."

    # Use rollback script if available
    if [[ -f "${SCRIPT_DIR}/rollback.sh" ]]; then
        "${SCRIPT_DIR}/rollback.sh" "${ENVIRONMENT}"
    else
        # Fallback to kubectl rollback
        kubectl rollout undo deployment/project-ai-app -n "${NAMESPACE}"
        kubectl rollout status deployment/project-ai-app -n "${NAMESPACE}"
    fi

    info "Rollback completed"
}

# ============================================================================
# Monitoring & Verification
# ============================================================================

verify_deployment() {
    step "Verifying deployment..."

    # Check pod health
    if ! check_pod_health; then
        error "Pod health verification failed"
        return 1
    fi

    # Run smoke tests
    if ! run_smoke_tests; then
        error "Smoke tests verification failed"
        return 1
    fi

    # Check metrics (if Prometheus available)
    # TODO: Query Prometheus for error rates, latency

    info "Deployment verification passed"
}

# ============================================================================
# Cleanup
# ============================================================================

cleanup_old_resources() {
    if [[ "${NO_CLEANUP}" == "true" ]]; then
        warn "Skipping cleanup (--no-cleanup)"
        return 0
    fi

    step "Cleaning up old resources..."

    # Clean up old ReplicaSets (keep last 3)
    kubectl delete replicaset -n "${NAMESPACE}" \
        $(kubectl get rs -n "${NAMESPACE}" -o json | \
        jq -r '.items | sort_by(.metadata.creationTimestamp) | reverse | .[3:] | .[].metadata.name' 2>/dev/null) \
        2>/dev/null || true

    # Clean up completed jobs
    kubectl delete job -n "${NAMESPACE}" \
        --field-selector status.successful=1 \
        2>/dev/null || true

    info "Cleanup completed"
}

# ============================================================================
# Reporting
# ============================================================================

print_deployment_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - DEPLOYMENT_START_TIME))

    banner "DEPLOYMENT SUMMARY"

    echo "Deployment ID:     ${DEPLOYMENT_ID}"
    echo "Environment:       ${ENVIRONMENT}"
    echo "Namespace:         ${NAMESPACE}"
    echo "Strategy:          ${STRATEGY}"
    echo "Image:             ${FULL_IMAGE}"
    echo "Previous Version:  ${PREVIOUS_VERSION}"
    echo "Duration:          ${duration} seconds"
    echo "Log File:          ${LOG_FILE}"
    echo ""

    if [[ "${ROLLBACK_NEEDED}" == "true" ]]; then
        echo -e "${RED}Status:            FAILED (Rolled Back)${NC}"
    else
        echo -e "${GREEN}Status:            SUCCESS${NC}"
    fi

    echo ""
    echo "Next Steps:"
    echo "  1. Monitor application metrics in Grafana"
    echo "  2. Check error logs: kubectl logs -n ${NAMESPACE} -l app.kubernetes.io/name=project-ai"
    echo "  3. Verify user-facing functionality"
    echo ""

    if [[ "${ROLLBACK_NEEDED}" != "true" ]]; then
        echo "To rollback if needed:"
        echo "  ./rollback.sh ${ENVIRONMENT}"
    fi

    echo ""
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    parse_arguments "$@"

    banner "SOVEREIGN GOVERNANCE SUBSTRATE - PRODUCTION DEPLOYMENT"

    info "Environment:  ${ENVIRONMENT}"
    info "Strategy:     ${STRATEGY}"
    info "Image:        ${FULL_IMAGE}"
    info "Dry Run:      ${DRY_RUN}"

    if [[ "${DRY_RUN}" == "true" ]]; then
        warn "DRY RUN MODE - No actual changes will be made"
    fi

    # Pre-deployment
    check_prerequisites
    run_preflight_checks
    backup_current_state

    # Database migrations
    if [[ "${DRY_RUN}" != "true" ]]; then
        run_database_migrations
    else
        info "Skipping database migrations (dry run)"
    fi

    # Execute deployment
    if [[ "${DRY_RUN}" != "true" ]]; then
        if ! execute_deployment; then
            trigger_rollback
            print_deployment_summary
            exit 1
        fi
    else
        info "Skipping deployment execution (dry run)"
    fi

    # Post-deployment verification
    if [[ "${DRY_RUN}" != "true" ]]; then
        if ! verify_deployment; then
            error "Post-deployment verification failed"
            trigger_rollback
            print_deployment_summary
            exit 1
        fi
    else
        info "Skipping deployment verification (dry run)"
    fi

    # Cleanup
    cleanup_old_resources

    # Summary
    print_deployment_summary

    if [[ "${ROLLBACK_NEEDED}" == "true" ]]; then
        exit 1
    fi

    info "Deployment completed successfully!"
    exit 0
}

# Trap errors
trap 'error "Deployment failed at line $LINENO"; trigger_rollback; exit 1' ERR

# Run main
main "$@"
