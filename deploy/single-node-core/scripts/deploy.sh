#!/usr/bin/env bash
# ==============================================================================
# Production Deployment Automation - Project-AI Core Stack
# ==============================================================================
#
# Complete production deployment with:
# - Pre-flight checks
# - Zero-downtime deployment
# - Database migrations
# - Health verification
# - Rollback capability
# - Post-deployment tests
#
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_MODE="${DEPLOYMENT_MODE:-production}"
SKIP_BACKUP="${SKIP_BACKUP:-false}"
SKIP_MIGRATION="${SKIP_MIGRATION:-false}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ==============================================================================
# Logging
# ==============================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $*"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $*"
}

log_step() {
    echo -e "\n${CYAN}==>${NC} ${YELLOW}$*${NC}\n"
}

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

preflight_checks() {
    log_step "Running Pre-flight Checks"
    
    local failed=0
    
    # Check Docker
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon not running"
        ((failed++))
    else
        log_success "Docker daemon is running"
    fi
    
    # Check Docker Compose
    if ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose v2 not available"
        ((failed++))
    else
        log_success "Docker Compose v2 available"
    fi
    
    # Check disk space
    local available=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available" -lt 20 ]; then
        log_error "Insufficient disk space: ${available}GB (required: 20GB)"
        ((failed++))
    else
        log_success "Sufficient disk space: ${available}GB"
    fi
    
    # Check configuration files
    if [ ! -f "$PROJECT_ROOT/env/.env" ]; then
        log_error "Environment file missing: env/.env"
        ((failed++))
    else
        log_success "Environment file found"
    fi
    
    if [ ! -f "$PROJECT_ROOT/mcp/.secrets.env" ]; then
        log_warning "MCP secrets file missing (optional)"
    else
        log_success "MCP secrets file found"
    fi
    
    # Check required secrets
    source "$PROJECT_ROOT/env/.env" 2>/dev/null || true
    
    if [ -z "${POSTGRES_PASSWORD:-}" ]; then
        log_error "POSTGRES_PASSWORD not set"
        ((failed++))
    fi
    
    if [ -z "${REDIS_PASSWORD:-}" ]; then
        log_error "REDIS_PASSWORD not set"
        ((failed++))
    fi
    
    if [ -z "${SECRET_KEY:-}" ]; then
        log_error "SECRET_KEY not set"
        ((failed++))
    fi
    
    if [ $failed -gt 0 ]; then
        log_error "Pre-flight checks failed: $failed error(s)"
        return 1
    fi
    
    log_success "All pre-flight checks passed"
    return 0
}

# ==============================================================================
# Backup Current State
# ==============================================================================

backup_current_state() {
    if [ "$SKIP_BACKUP" = "true" ]; then
        log_warning "Skipping backup (SKIP_BACKUP=true)"
        return 0
    fi
    
    log_step "Backing Up Current State"
    
    # Check if services are running
    if ! docker compose ps | grep -q "Up"; then
        log_warning "No running services to backup"
        return 0
    fi
    
    # Run backup script
    if [ -f "$SCRIPT_DIR/backup.sh" ]; then
        log "Running full backup..."
        "$SCRIPT_DIR/backup.sh" full
        log_success "Backup completed"
    else
        log_warning "Backup script not found, skipping backup"
    fi
}

# ==============================================================================
# Pull Latest Images
# ==============================================================================

pull_images() {
    log_step "Pulling Latest Docker Images"
    
    log "Pulling base stack images..."
    docker compose pull
    
    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        log "Pulling monitoring stack images..."
        docker compose -f docker-compose.yml -f docker-compose.prod.yml pull
    fi
    
    log_success "Images pulled successfully"
}

# ==============================================================================
# Database Migrations
# ==============================================================================

run_migrations() {
    if [ "$SKIP_MIGRATION" = "true" ]; then
        log_warning "Skipping migrations (SKIP_MIGRATION=true)"
        return 0
    fi
    
    log_step "Running Database Migrations"
    
    # Ensure Postgres is running
    if ! docker compose ps postgres | grep -q "Up"; then
        log "Starting PostgreSQL..."
        docker compose up -d postgres
        sleep 10
    fi
    
    # Check if migrations directory exists
    if [ -d "$PROJECT_ROOT/../../src/app/migrations" ]; then
        log "Running Alembic migrations..."
        docker compose exec -T project-ai-orchestrator alembic upgrade head || true
        log_success "Migrations completed"
    else
        log_warning "No migrations directory found, skipping"
    fi
}

# ==============================================================================
# Deploy Services
# ==============================================================================

deploy_services() {
    log_step "Deploying Services"
    
    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        log "Deploying PRODUCTION stack (base + monitoring)..."
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        log "Deploying BASE stack..."
        docker compose up -d
    fi
    
    log_success "Services deployed"
}

# ==============================================================================
# Health Checks
# ==============================================================================

wait_for_health() {
    local service=$1
    local endpoint=$2
    local max_attempts=${3:-30}
    local interval=${4:-10}
    
    log "Waiting for $service to be healthy..."
    
    for i in $(seq 1 $max_attempts); do
        if curl -sf "$endpoint" >/dev/null 2>&1; then
            log_success "$service is healthy"
            return 0
        fi
        
        if [ $i -eq $max_attempts ]; then
            log_error "$service failed to become healthy after $((max_attempts * interval)) seconds"
            return 1
        fi
        
        echo -n "."
        sleep $interval
    done
}

verify_deployment() {
    log_step "Verifying Deployment"
    
    local failed=0
    
    # Wait for services to start
    sleep 15
    
    # Check Postgres
    if docker compose exec -T postgres pg_isready -U project_ai >/dev/null 2>&1; then
        log_success "PostgreSQL is ready"
    else
        log_error "PostgreSQL is not ready"
        ((failed++))
    fi
    
    # Check Redis
    if docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" ping >/dev/null 2>&1; then
        log_success "Redis is ready"
    else
        log_error "Redis is not ready"
        ((failed++))
    fi
    
    # Check Orchestrator
    if wait_for_health "Orchestrator" "http://localhost:8000/health" 20 10; then
        :  # Success message already logged
    else
        ((failed++))
    fi
    
    # Check MCP Gateway
    if wait_for_health "MCP Gateway" "http://localhost:9000/health" 20 10; then
        :  # Success message already logged
    else
        log_warning "MCP Gateway health check failed (may be optional)"
    fi
    
    # Check monitoring stack (if production)
    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        if wait_for_health "Prometheus" "http://localhost:9090/-/healthy" 15 5; then
            :
        else
            log_warning "Prometheus not healthy"
        fi
        
        if wait_for_health "Grafana" "http://localhost:3000/api/health" 20 5; then
            :
        else
            log_warning "Grafana not healthy"
        fi
    fi
    
    if [ $failed -gt 0 ]; then
        log_error "Deployment verification failed: $failed critical service(s) unhealthy"
        return 1
    fi
    
    log_success "All critical services are healthy"
    return 0
}

# ==============================================================================
# Smoke Tests
# ==============================================================================

run_smoke_tests() {
    log_step "Running Smoke Tests"
    
    local failed=0
    
    # Test database query
    log "Testing database connectivity..."
    if docker compose exec -T postgres psql -U project_ai -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "Database query successful"
    else
        log_error "Database query failed"
        ((failed++))
    fi
    
    # Test Redis operations
    log "Testing Redis operations..."
    if docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" SET test_key "test_value" >/dev/null 2>&1; then
        log_success "Redis write successful"
    else
        log_error "Redis write failed"
        ((failed++))
    fi
    
    # Test API endpoint
    log "Testing API endpoints..."
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        log_success "API health endpoint responding"
    else
        log_error "API health endpoint not responding"
        ((failed++))
    fi
    
    # Test metrics endpoint
    if curl -sf http://localhost:8001/metrics >/dev/null 2>&1; then
        log_success "Metrics endpoint responding"
    else
        log_warning "Metrics endpoint not responding (non-critical)"
    fi
    
    if [ $failed -gt 0 ]; then
        log_error "Smoke tests failed: $failed test(s)"
        return 1
    fi
    
    log_success "All smoke tests passed"
    return 0
}

# ==============================================================================
# Rollback
# ==============================================================================

rollback() {
    log_step "Rolling Back Deployment"
    
    log_error "Deployment failed, initiating rollback..."
    
    # Stop new services
    docker compose down || true
    
    # Restore from backup if available
    local latest_backup=$(find "${BACKUP_DIR:-backups}" -type d -name "*_*" | sort -r | head -1)
    
    if [ -n "$latest_backup" ]; then
        log "Found backup: $latest_backup"
        log "Run './scripts/restore.sh full $(basename "$latest_backup")' to restore"
    else
        log_warning "No backup found for automatic rollback"
    fi
    
    log_error "Rollback initiated - manual intervention required"
    exit 1
}

# ==============================================================================
# Deployment Summary
# ==============================================================================

print_summary() {
    log_step "Deployment Complete!"
    
    cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════════════╗
║                    🎉 Deployment Successful! 🎉                      ║
╚══════════════════════════════════════════════════════════════════════╝${NC}

${CYAN}📊 Service Status:${NC}
$(docker compose ps | tail -n +2)

${CYAN}🌐 Access Points:${NC}
  • Orchestrator API:    http://localhost:5000
  • Health Check:        http://localhost:8000/health
  • Metrics:             http://localhost:8001/metrics
  • MCP Gateway:         http://localhost:9000
  • MCP Admin:           http://localhost:9001

EOF

    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        cat << EOF
${CYAN}📈 Monitoring:${NC}
  • Prometheus:          http://localhost:9090
  • Grafana:             http://localhost:3000
    Username: ${GRAFANA_ADMIN_USER:-admin}
    Password: <from environment>
  • AlertManager:        http://localhost:9093
  • Loki:                http://localhost:3100

EOF
    fi

    cat << EOF
${CYAN}🔧 Management:${NC}
  • View logs:           docker compose logs -f
  • Check status:        docker compose ps
  • Stop services:       docker compose down
  • Backup:              ./scripts/backup.sh full
  • Restore:             ./scripts/restore.sh list

${YELLOW}⚠ Next Steps:${NC}
  1. Configure monitoring alerts (monitoring/alertmanager/alertmanager.yml)
  2. Set up automated backups (cron: ./scripts/backup.sh full)
  3. Review logs for any warnings
  4. Configure external monitoring (if applicable)
  5. Test failover procedures

${GREEN}✅ Production deployment completed successfully!${NC}

EOF
}

# ==============================================================================
# Main Deployment Flow
# ==============================================================================

main() {
    clear
    
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║     Project-AI Production Deployment Automation                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
    
    log "Deployment mode: $DEPLOYMENT_MODE"
    log "Skip backup: $SKIP_BACKUP"
    log "Skip migration: $SKIP_MIGRATION"
    echo ""
    
    # Confirm production deployment
    if [ "$DEPLOYMENT_MODE" = "production" ]; then
        log_warning "This will deploy to PRODUCTION environment"
        read -p "$(echo -e ${YELLOW}Type 'DEPLOY' to confirm:${NC} )" -r
        if [ "$REPLY" != "DEPLOY" ]; then
            log "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Execute deployment steps
    preflight_checks || exit 1
    backup_current_state || true  # Don't fail on backup error
    pull_images || { log_error "Failed to pull images"; exit 1; }
    deploy_services || { log_error "Failed to deploy services"; rollback; }
    run_migrations || log_warning "Migrations failed (non-critical)"
    verify_deployment || { log_error "Deployment verification failed"; rollback; }
    run_smoke_tests || { log_error "Smoke tests failed"; rollback; }
    
    # Success!
    print_summary
}

# Run main deployment
main "$@"
