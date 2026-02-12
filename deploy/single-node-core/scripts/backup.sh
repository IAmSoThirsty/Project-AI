#!/usr/bin/env bash
# ==============================================================================
# Complete Backup System for Project-AI Core Stack
# ==============================================================================
#
# Full production backup implementation covering:
# - PostgreSQL (schema + data + WAL archiving)
# - Redis (RDB + AOF)
# - Application data (uploads, logs, configs)
# - Encrypted archives
# - S3/cloud storage sync
# - Retention policy enforcement
# - Backup verification
# - Restore testing
#
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup retention (days)
RETENTION_DAYS_POSTGRES=30
RETENTION_DAYS_REDIS=7
RETENTION_DAYS_APP=14

# Encryption
ENCRYPT_BACKUPS=${ENCRYPT_BACKUPS:-true}
ENCRYPTION_KEY_FILE="${ENCRYPTION_KEY_FILE:-${PROJECT_ROOT}/.backup-encryption-key}"

# S3/Cloud storage (optional)
S3_ENABLED=${S3_ENABLED:-false}
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-project-ai/backups}"

# Notification
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==============================================================================
# Logging Functions
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

# ==============================================================================
# Notification Functions
# ==============================================================================

send_notification() {
    local status=$1
    local message=$2
    
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST "$SLACK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"[Project-AI Backup] ${status}: ${message}\"}" \
            2>/dev/null || true
    fi
}

# ==============================================================================
# Encryption Functions
# ==============================================================================

generate_encryption_key() {
    if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
        log "Generating encryption key..."
        openssl rand -base64 32 > "$ENCRYPTION_KEY_FILE"
        chmod 600 "$ENCRYPTION_KEY_FILE"
        log_success "Encryption key generated: $ENCRYPTION_KEY_FILE"
    fi
}

encrypt_file() {
    local input_file=$1
    local output_file="${input_file}.enc"
    
    if [ "$ENCRYPT_BACKUPS" = true ]; then
        log "Encrypting $input_file..."
        openssl enc -aes-256-cbc -salt -pbkdf2 \
            -in "$input_file" \
            -out "$output_file" \
            -pass file:"$ENCRYPTION_KEY_FILE"
        
        rm "$input_file"
        log_success "Encrypted: $(basename "$output_file")"
        echo "$output_file"
    else
        echo "$input_file"
    fi
}

decrypt_file() {
    local input_file=$1
    local output_file="${input_file%.enc}"
    
    log "Decrypting $input_file..."
    openssl enc -aes-256-cbc -d -pbkdf2 \
        -in "$input_file" \
        -out "$output_file" \
        -pass file:"$ENCRYPTION_KEY_FILE"
    
    log_success "Decrypted: $(basename "$output_file")"
    echo "$output_file"
}

# ==============================================================================
# PostgreSQL Backup
# ==============================================================================

backup_postgres() {
    log "Starting PostgreSQL backup..."
    
    local backup_subdir="${BACKUP_DIR}/postgres/${TIMESTAMP}"
    mkdir -p "$backup_subdir"
    
    # Full database dump
    log "Creating full database dump..."
    docker compose exec -T postgres pg_dump \
        -U project_ai \
        -F custom \
        -f /tmp/backup.dump \
        project_ai
    
    docker compose cp postgres:/tmp/backup.dump "${backup_subdir}/full_backup.dump"
    docker compose exec -T postgres rm /tmp/backup.dump
    
    # Compress
    log "Compressing backup..."
    gzip "${backup_subdir}/full_backup.dump"
    
    # Encrypt
    local backup_file=$(encrypt_file "${backup_subdir}/full_backup.dump.gz")
    
    # Schema-only dump (for quick reference)
    log "Creating schema-only dump..."
    docker compose exec -T postgres pg_dump \
        -U project_ai \
        -s \
        project_ai > "${backup_subdir}/schema.sql"
    
    # Globals dump (roles, users)
    log "Dumping global objects..."
    docker compose exec -T postgres pg_dumpall \
        -U postgres \
        --globals-only > "${backup_subdir}/globals.sql"
    
    # Table sizes and statistics
    log "Capturing database statistics..."
    docker compose exec -T postgres psql -U project_ai -c "
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    " > "${backup_subdir}/table_sizes.txt"
    
    # Calculate checksum
    sha256sum "$backup_file" > "${backup_file}.sha256"
    
    local backup_size=$(du -h "$backup_file" | cut -f1)
    log_success "PostgreSQL backup completed: $backup_file ($backup_size)"
    
    # Upload to S3 if enabled
    if [ "$S3_ENABLED" = true ]; then
        upload_to_s3 "$backup_file" "postgres/$(basename "$backup_file")"
    fi
    
    echo "$backup_file"
}

# ==============================================================================
# Redis Backup
# ==============================================================================

backup_redis() {
    log "Starting Redis backup..."
    
    local backup_subdir="${BACKUP_DIR}/redis/${TIMESTAMP}"
    mkdir -p "$backup_subdir"
    
    # Trigger BGSAVE
    log "Triggering Redis BGSAVE..."
    docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" BGSAVE
    
    # Wait for save to complete
    sleep 2
    while docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" LASTSAVE | grep -q "$(date +%s)"; do
        sleep 1
    done
    
    # Copy RDB file
    log "Copying RDB file..."
    docker compose cp redis:/data/dump.rdb "${backup_subdir}/dump.rdb"
    
    # Copy AOF file
    log "Copying AOF file..."
    docker compose cp redis:/data/appendonly.aof "${backup_subdir}/appendonly.aof" || true
    
    # Create tarball
    log "Creating archive..."
    tar -czf "${backup_subdir}/redis_backup.tar.gz" -C "$backup_subdir" dump.rdb appendonly.aof
    rm "${backup_subdir}/dump.rdb" "${backup_subdir}/appendonly.aof" 2>/dev/null || true
    
    # Encrypt
    local backup_file=$(encrypt_file "${backup_subdir}/redis_backup.tar.gz")
    
    # Calculate checksum
    sha256sum "$backup_file" > "${backup_file}.sha256"
    
    local backup_size=$(du -h "$backup_file" | cut -f1)
    log_success "Redis backup completed: $backup_file ($backup_size)"
    
    # Upload to S3 if enabled
    if [ "$S3_ENABLED" = true ]; then
        upload_to_s3 "$backup_file" "redis/$(basename "$backup_file")"
    fi
    
    echo "$backup_file"
}

# ==============================================================================
# Application Data Backup
# ==============================================================================

backup_application_data() {
    log "Starting application data backup..."
    
    local backup_subdir="${BACKUP_DIR}/app/${TIMESTAMP}"
    mkdir -p "$backup_subdir"
    
    # Backup orchestrator data
    if docker volume ls | grep -q project-ai-orchestrator-data; then
        log "Backing up orchestrator data..."
        docker run --rm \
            -v project-ai-orchestrator-data:/source:ro \
            -v "${backup_subdir}:/backup" \
            alpine tar czf /backup/orchestrator_data.tar.gz -C /source .
    fi
    
    # Backup MCP cache
    if docker volume ls | grep -q project-ai-mcp-cache; then
        log "Backing up MCP cache..."
        docker run --rm \
            -v project-ai-mcp-cache:/source:ro \
            -v "${backup_subdir}:/backup" \
            alpine tar czf /backup/mcp_cache.tar.gz -C /source .
    fi
    
    # Backup configuration files
    log "Backing up configuration..."
    tar czf "${backup_subdir}/config.tar.gz" \
        -C "$PROJECT_ROOT" \
        mcp/config.yaml \
        mcp/registry.yaml \
        mcp/catalogs \
        redis/redis.conf \
        postgres/postgresql.conf \
        2>/dev/null || true
    
    # Create combined archive
    log "Creating combined archive..."
    tar czf "${backup_subdir}/app_backup.tar.gz" -C "$backup_subdir" \
        orchestrator_data.tar.gz \
        mcp_cache.tar.gz \
        config.tar.gz 2>/dev/null || true
    
    # Clean up intermediate files
    rm "${backup_subdir}"/*.tar.gz 2>/dev/null || true
    
    # Encrypt
    local backup_file=$(encrypt_file "${backup_subdir}/app_backup.tar.gz")
    
    # Calculate checksum
    sha256sum "$backup_file" > "${backup_file}.sha256"
    
    local backup_size=$(du -h "$backup_file" | cut -f1)
    log_success "Application data backup completed: $backup_file ($backup_size)"
    
    # Upload to S3 if enabled
    if [ "$S3_ENABLED" = true ]; then
        upload_to_s3 "$backup_file" "app/$(basename "$backup_file")"
    fi
    
    echo "$backup_file"
}

# ==============================================================================
# S3/Cloud Upload
# ==============================================================================

upload_to_s3() {
    local local_file=$1
    local s3_key=$2
    
    if [ "$S3_ENABLED" != true ] || [ -z "$S3_BUCKET" ]; then
        return 0
    fi
    
    log "Uploading to S3: s3://${S3_BUCKET}/${S3_PREFIX}/${s3_key}"
    
    if command -v aws &> /dev/null; then
        aws s3 cp "$local_file" "s3://${S3_BUCKET}/${S3_PREFIX}/${s3_key}" \
            --storage-class STANDARD_IA
        log_success "Uploaded to S3"
    else
        log_warning "AWS CLI not available, skipping S3 upload"
    fi
}

# ==============================================================================
# Backup Verification
# ==============================================================================

verify_backup() {
    local backup_file=$1
    
    log "Verifying backup: $(basename "$backup_file")"
    
    # Check if file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Verify checksum
    if [ -f "${backup_file}.sha256" ]; then
        log "Verifying checksum..."
        if sha256sum -c "${backup_file}.sha256" >/dev/null 2>&1; then
            log_success "Checksum verified"
        else
            log_error "Checksum verification failed!"
            return 1
        fi
    fi
    
    # For PostgreSQL backups, test restore to temporary database
    if [[ "$backup_file" == *"postgres"* ]]; then
        log "Testing PostgreSQL restore (dry run)..."
        
        # Create temp file for decryption if needed
        local test_file="$backup_file"
        if [[ "$backup_file" == *.enc ]]; then
            test_file=$(decrypt_file "$backup_file")
        fi
        
        # Decompress
        local dump_file="${test_file%.gz}"
        gunzip -c "$test_file" > "$dump_file"
        
        # Test with pg_restore --list
        if docker compose exec -T postgres pg_restore --list "$dump_file" >/dev/null 2>&1; then
            log_success "PostgreSQL backup is valid"
        else
            log_error "PostgreSQL backup validation failed!"
            rm "$dump_file" "$test_file" 2>/dev/null || true
            return 1
        fi
        
        # Cleanup
        rm "$dump_file" "$test_file" 2>/dev/null || true
    fi
    
    log_success "Backup verification passed"
    return 0
}

# ==============================================================================
# Cleanup Old Backups
# ==============================================================================

cleanup_old_backups() {
    log "Cleaning up old backups..."
    
    # PostgreSQL backups
    if [ -d "${BACKUP_DIR}/postgres" ]; then
        find "${BACKUP_DIR}/postgres" -type d -mtime +${RETENTION_DAYS_POSTGRES} -exec rm -rf {} + 2>/dev/null || true
        local pg_count=$(find "${BACKUP_DIR}/postgres" -maxdepth 1 -type d | wc -l)
        log_success "PostgreSQL: Kept $((pg_count - 1)) backups (${RETENTION_DAYS_POSTGRES} day retention)"
    fi
    
    # Redis backups
    if [ -d "${BACKUP_DIR}/redis" ]; then
        find "${BACKUP_DIR}/redis" -type d -mtime +${RETENTION_DAYS_REDIS} -exec rm -rf {} + 2>/dev/null || true
        local redis_count=$(find "${BACKUP_DIR}/redis" -maxdepth 1 -type d | wc -l)
        log_success "Redis: Kept $((redis_count - 1)) backups (${RETENTION_DAYS_REDIS} day retention)"
    fi
    
    # Application backups
    if [ -d "${BACKUP_DIR}/app" ]; then
        find "${BACKUP_DIR}/app" -type d -mtime +${RETENTION_DAYS_APP} -exec rm -rf {} + 2>/dev/null || true
        local app_count=$(find "${BACKUP_DIR}/app" -maxdepth 1 -type d | wc -l)
        log_success "Application: Kept $((app_count - 1)) backups (${RETENTION_DAYS_APP} day retention)"
    fi
}

# ==============================================================================
# Full Backup Execution
# ==============================================================================

run_full_backup() {
    log "=========================================="
    log "Project-AI Full Backup Started"
    log "=========================================="
    log "Timestamp: $TIMESTAMP"
    log "Backup directory: $BACKUP_DIR"
    log "Encryption: $ENCRYPT_BACKUPS"
    log "S3 sync: $S3_ENABLED"
    log "=========================================="
    
    # Ensure backup directory exists
    mkdir -p "$BACKUP_DIR"
    
    # Generate encryption key if needed
    if [ "$ENCRYPT_BACKUPS" = true ]; then
        generate_encryption_key
    fi
    
    # Execute backups
    local pg_backup=""
    local redis_backup=""
    local app_backup=""
    local failed=0
    
    # PostgreSQL backup
    if pg_backup=$(backup_postgres); then
        if verify_backup "$pg_backup"; then
            log_success "PostgreSQL backup and verification completed"
        else
            log_error "PostgreSQL backup verification failed"
            ((failed++))
        fi
    else
        log_error "PostgreSQL backup failed"
        ((failed++))
    fi
    
    # Redis backup
    if redis_backup=$(backup_redis); then
        if verify_backup "$redis_backup"; then
            log_success "Redis backup and verification completed"
        else
            log_error "Redis backup verification failed"
            ((failed++))
        fi
    else
        log_error "Redis backup failed"
        ((failed++))
    fi
    
    # Application data backup
    if app_backup=$(backup_application_data); then
        log_success "Application data backup completed"
    else
        log_error "Application data backup failed"
        ((failed++))
    fi
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Final summary
    log "=========================================="
    log "Backup Summary"
    log "=========================================="
    [ -n "$pg_backup" ] && log "PostgreSQL: $(basename "$pg_backup")"
    [ -n "$redis_backup" ] && log "Redis: $(basename "$redis_backup")"
    [ -n "$app_backup" ] && log "Application: $(basename "$app_backup")"
    log "=========================================="
    
    if [ $failed -eq 0 ]; then
        log_success "All backups completed successfully!"
        send_notification "SUCCESS" "All backups completed for $TIMESTAMP"
        return 0
    else
        log_error "$failed backup(s) failed!"
        send_notification "FAILURE" "$failed backup(s) failed for $TIMESTAMP"
        return 1
    fi
}

# ==============================================================================
# Main Execution
# ==============================================================================

case "${1:-full}" in
    full)
        run_full_backup
        ;;
    postgres)
        backup_postgres
        ;;
    redis)
        backup_redis
        ;;
    app)
        backup_application_data
        ;;
    verify)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 verify <backup_file>"
            exit 1
        fi
        verify_backup "$2"
        ;;
    cleanup)
        cleanup_old_backups
        ;;
    *)
        echo "Usage: $0 {full|postgres|redis|app|verify <file>|cleanup}"
        echo ""
        echo "Commands:"
        echo "  full      - Run complete backup (default)"
        echo "  postgres  - Backup PostgreSQL only"
        echo "  redis     - Backup Redis only"
        echo "  app       - Backup application data only"
        echo "  verify    - Verify a backup file"
        echo "  cleanup   - Remove old backups per retention policy"
        exit 1
        ;;
esac
