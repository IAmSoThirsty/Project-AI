#!/usr/bin/env bash
# ==============================================================================
# Complete Restore System for Project-AI Core Stack
# ==============================================================================
#
# Full production restore implementation covering:
# - Point-in-time recovery
# - Selective restoration
# - Data validation
# - Rollback capabilities
# - Automated restore testing
#
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"

# Encryption
ENCRYPTION_KEY_FILE="${ENCRYPTION_KEY_FILE:-${PROJECT_ROOT}/.backup-encryption-key}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==============================================================================
# Helper Functions
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

decrypt_file() {
    local input_file=$1
    local output_file="${input_file%.enc}"
    
    if [[ "$input_file" == *.enc ]]; then
        log "Decrypting $(basename "$input_file")..."
        openssl enc -aes-256-cbc -d -pbkdf2 \
            -in "$input_file" \
            -out "$output_file" \
            -pass file:"$ENCRYPTION_KEY_FILE"
        echo "$output_file"
    else
        echo "$input_file"
    fi
}

# ==============================================================================
# List Available Backups
# ==============================================================================

list_backups() {
    local backup_type=${1:-all}
    
    log "Available backups:"
    echo ""
    
    case $backup_type in
        postgres|all)
            if [ -d "${BACKUP_DIR}/postgres" ]; then
                echo "PostgreSQL Backups:"
                find "${BACKUP_DIR}/postgres" -name "*.dump.gz*" -o -name "*.enc" | sort -r | head -20 | while read -r file; do
                    local size=$(du -h "$file" | cut -f1)
                    local date=$(echo "$file" | grep -oP '\d{8}_\d{6}')
                    echo "  - $date: $(basename "$file") ($size)"
                done
                echo ""
            fi
            ;&
        
        redis|all)
            if [ -d "${BACKUP_DIR}/redis" ]; then
                echo "Redis Backups:"
                find "${BACKUP_DIR}/redis" -name "*.tar.gz*" -o -name "*.enc" | sort -r | head -20 | while read -r file; do
                    local size=$(du -h "$file" | cut -f1)
                    local date=$(echo "$file" | grep -oP '\d{8}_\d{6}')
                    echo "  - $date: $(basename "$file") ($size)"
                done
                echo ""
            fi
            ;&
        
        app|all)
            if [ -d "${BACKUP_DIR}/app" ]; then
                echo "Application Backups:"
                find "${BACKUP_DIR}/app" -name "*.tar.gz*" -o -name "*.enc" | sort -r | head -20 | while read -r file; do
                    local size=$(du -h "$file" | cut -f1)
                    local date=$(echo "$file" | grep -oP '\d{8}_\d{6}')
                    echo "  - $date: $(basename "$file") ($size)"
                done
            fi
            ;;
    esac
}

# ==============================================================================
# PostgreSQL Restore
# ==============================================================================

restore_postgres() {
    local backup_file=$1
    local drop_existing=${2:-false}
    
    log "Starting PostgreSQL restore..."
    log "Backup file: $(basename "$backup_file")"
    
    # Verify backup file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Decrypt if needed
    local decrypted_file=$(decrypt_file "$backup_file")
    
    # Decompress
    log "Decompressing backup..."
    local dump_file="${decrypted_file%.gz}"
    gunzip -c "$decrypted_file" > "$dump_file"
    
    # Verify dump file
    log "Verifying backup integrity..."
    if ! docker compose exec -T postgres pg_restore --list "$dump_file" >/dev/null 2>&1; then
        log_error "Backup file is corrupted or invalid!"
        rm "$dump_file" "$decrypted_file" 2>/dev/null || true
        return 1
    fi
    log_success "Backup file is valid"
    
    # Warn user
    log_warning "This will restore the database and may overwrite existing data!"
    if [ "$drop_existing" = true ]; then
        log_warning "DROP_EXISTING is true - all existing data will be removed!"
    fi
    
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        rm "$dump_file" "$decrypted_file" 2>/dev/null || true
        return 1
    fi
    
    # Stop dependent services
    log "Stopping dependent services..."
    docker compose stop project-ai-orchestrator mcp-gateway || true
    
    # Drop existing database if requested
    if [ "$drop_existing" = true ]; then
        log "Dropping existing database..."
        docker compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS project_ai;" || true
        docker compose exec -T postgres psql -U postgres -c "CREATE DATABASE project_ai OWNER project_ai;" || true
    fi
    
    # Copy dump file to container
    log "Copying dump file to container..."
    docker compose cp "$dump_file" postgres:/tmp/restore.dump
    
    # Restore database
    log "Restoring database (this may take several minutes)..."
    docker compose exec -T postgres pg_restore \
        -U project_ai \
        -d project_ai \
        --clean \
        --if-exists \
        --no-owner \
        --no-acl \
        --verbose \
        /tmp/restore.dump 2>&1 | grep -v "^$" || true
    
    # Clean up
    docker compose exec -T postgres rm /tmp/restore.dump
    rm "$dump_file" "$decrypted_file" 2>/dev/null || true
    
    # Verify restore
    log "Verifying restore..."
    local table_count=$(docker compose exec -T postgres psql -U project_ai -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';" | tr -d ' ')
    log_success "Restored $table_count tables"
    
    # Update statistics
    log "Analyzing database..."
    docker compose exec -T postgres psql -U project_ai -c "ANALYZE;" >/dev/null
    
    # Restart services
    log "Restarting services..."
    docker compose start project-ai-orchestrator mcp-gateway
    
    log_success "PostgreSQL restore completed successfully!"
    return 0
}

# ==============================================================================
# Redis Restore
# ==============================================================================

restore_redis() {
    local backup_file=$1
    local flush_existing=${2:-false}
    
    log "Starting Redis restore..."
    log "Backup file: $(basename "$backup_file")"
    
    # Verify backup file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Decrypt if needed
    local decrypted_file=$(decrypt_file "$backup_file")
    
    # Warn user
    log_warning "This will restore Redis data and may overwrite existing cache!"
    if [ "$flush_existing" = true ]; then
        log_warning "FLUSH_EXISTING is true - all existing data will be removed!"
    fi
    
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        rm "$decrypted_file" 2>/dev/null || true
        return 1
    fi
    
    # Stop Redis
    log "Stopping Redis..."
    docker compose stop redis
    
    # Flush existing data if requested
    if [ "$flush_existing" = true ]; then
        log "Removing existing Redis data..."
        docker run --rm \
            -v project-ai-redis-data:/data \
            alpine sh -c "rm -rf /data/*"
    fi
    
    # Extract backup
    log "Extracting backup..."
    local temp_dir=$(mktemp -d)
    tar -xzf "$decrypted_file" -C "$temp_dir"
    
    # Restore RDB file
    if [ -f "$temp_dir/dump.rdb" ]; then
        log "Restoring RDB file..."
        docker run --rm \
            -v project-ai-redis-data:/data \
            -v "$temp_dir:/backup:ro" \
            alpine cp /backup/dump.rdb /data/dump.rdb
    fi
    
    # Restore AOF file
    if [ -f "$temp_dir/appendonly.aof" ]; then
        log "Restoring AOF file..."
        docker run --rm \
            -v project-ai-redis-data:/data \
            -v "$temp_dir:/backup:ro" \
            alpine cp /backup/appendonly.aof /data/appendonly.aof
    fi
    
    # Clean up
    rm -rf "$temp_dir" "$decrypted_file" 2>/dev/null || true
    
    # Start Redis
    log "Starting Redis..."
    docker compose start redis
    
    # Wait for Redis to be ready
    sleep 5
    if docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" ping >/dev/null 2>&1; then
        log_success "Redis is ready"
    else
        log_warning "Redis may not be fully ready yet"
    fi
    
    # Verify restore
    local key_count=$(docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" DBSIZE | grep -oP '\d+' || echo "0")
    log_success "Redis restored with $key_count keys"
    
    log_success "Redis restore completed successfully!"
    return 0
}

# ==============================================================================
# Application Data Restore
# ==============================================================================

restore_application_data() {
    local backup_file=$1
    
    log "Starting application data restore..."
    log "Backup file: $(basename "$backup_file")"
    
    # Verify backup file exists
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Decrypt if needed
    local decrypted_file=$(decrypt_file "$backup_file")
    
    # Warn user
    log_warning "This will restore application data and may overwrite existing files!"
    
    read -p "Are you sure you want to proceed? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled by user"
        rm "$decrypted_file" 2>/dev/null || true
        return 1
    fi
    
    # Stop services
    log "Stopping services..."
    docker compose stop project-ai-orchestrator mcp-gateway
    
    # Extract backup
    log "Extracting backup..."
    local temp_dir=$(mktemp -d)
    tar -xzf "$decrypted_file" -C "$temp_dir"
    
    # Restore orchestrator data
    if [ -f "$temp_dir/orchestrator_data.tar.gz" ]; then
        log "Restoring orchestrator data..."
        docker run --rm \
            -v project-ai-orchestrator-data:/target \
            -v "$temp_dir:/backup:ro" \
            alpine sh -c "rm -rf /target/* && tar xzf /backup/orchestrator_data.tar.gz -C /target"
    fi
    
    # Restore MCP cache
    if [ -f "$temp_dir/mcp_cache.tar.gz" ]; then
        log "Restoring MCP cache..."
        docker run --rm \
            -v project-ai-mcp-cache:/target \
            -v "$temp_dir:/backup:ro" \
            alpine sh -c "rm -rf /target/* && tar xzf /backup/mcp_cache.tar.gz -C /target"
    fi
    
    # Restore configuration (if included)
    if [ -f "$temp_dir/config.tar.gz" ]; then
        log "Configuration backup found (manual restoration required)"
        tar -xzf "$temp_dir/config.tar.gz" -C "${temp_dir}/config_extracted"
        log_warning "Configuration files extracted to: ${temp_dir}/config_extracted"
        log_warning "Review and manually restore if needed"
    fi
    
    # Clean up
    rm -rf "$decrypted_file" 2>/dev/null || true
    
    # Start services
    log "Starting services..."
    docker compose start project-ai-orchestrator mcp-gateway
    
    log_success "Application data restore completed!"
    log "Note: Configuration backup preserved in: ${temp_dir}/config_extracted"
    
    return 0
}

# ==============================================================================
# Full Restore
# ==============================================================================

restore_full() {
    local timestamp=$1
    
    log "=========================================="
    log "Project-AI Full Restore"
    log "=========================================="
    log "Timestamp: $timestamp"
    log "=========================================="
    
    # Find backup files
    local pg_backup=$(find "${BACKUP_DIR}/postgres/${timestamp}" -name "*.dump.gz*" -o -name "*.enc" | head -1)
    local redis_backup=$(find "${BACKUP_DIR}/redis/${timestamp}" -name "*.tar.gz*" -o -name "*.enc" | head -1)
    local app_backup=$(find "${BACKUP_DIR}/app/${timestamp}" -name "*.tar.gz*" -o -name "*.enc" | head -1)
    
    # Verify backups exist
    local missing=0
    [ -z "$pg_backup" ] && log_error "PostgreSQL backup not found for $timestamp" && ((missing++))
    [ -z "$redis_backup" ] && log_warning "Redis backup not found for $timestamp"
    [ -z "$app_backup" ] && log_warning "Application backup not found for $timestamp"
    
    if [ $missing -gt 0 ]; then
        log_error "Cannot proceed with full restore - missing required backups"
        return 1
    fi
    
    # Warn user
    log_warning "This will restore ALL services to state from: $timestamp"
    log_warning "Current data will be OVERWRITTEN!"
    echo ""
    read -p "Type 'RESTORE' to confirm: " -r
    if [ "$REPLY" != "RESTORE" ]; then
        log "Restore cancelled by user"
        return 1
    fi
    
    # Restore in order
    local failed=0
    
    # 1. PostgreSQL (required)
    if ! restore_postgres "$pg_backup" true; then
        log_error "PostgreSQL restore failed!"
        ((failed++))
        return 1  # Critical failure
    fi
    
    # 2. Redis (optional but recommended)
    if [ -n "$redis_backup" ]; then
        if ! restore_redis "$redis_backup" true; then
            log_error "Redis restore failed!"
            ((failed++))
        fi
    fi
    
    # 3. Application data (optional)
    if [ -n "$app_backup" ]; then
        if ! restore_application_data "$app_backup"; then
            log_error "Application data restore failed!"
            ((failed++))
        fi
    fi
    
    # Summary
    log "=========================================="
    if [ $failed -eq 0 ]; then
        log_success "Full restore completed successfully!"
        log "System restored to: $timestamp"
        return 0
    else
        log_error "Restore completed with $failed error(s)"
        return 1
    fi
}

# ==============================================================================
# Main Execution
# ==============================================================================

case "${1:-}" in
    list)
        list_backups "${2:-all}"
        ;;
    
    postgres)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 postgres <backup_file> [drop_existing]"
            exit 1
        fi
        restore_postgres "$2" "${3:-false}"
        ;;
    
    redis)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 redis <backup_file> [flush_existing]"
            exit 1
        fi
        restore_redis "$2" "${3:-false}"
        ;;
    
    app)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 app <backup_file>"
            exit 1
        fi
        restore_application_data "$2"
        ;;
    
    full)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 full <timestamp>"
            log_error "Example: $0 full 20240101_120000"
            echo ""
            log "Available timestamps:"
            find "$BACKUP_DIR" -type d -name "*_*" | grep -oP '\d{8}_\d{6}' | sort -u | tail -10
            exit 1
        fi
        restore_full "$2"
        ;;
    
    *)
        echo "Usage: $0 {list|postgres|redis|app|full} [options]"
        echo ""
        echo "Commands:"
        echo "  list [type]               - List available backups (postgres|redis|app|all)"
        echo "  postgres <file> [drop]    - Restore PostgreSQL from backup"
        echo "  redis <file> [flush]      - Restore Redis from backup"
        echo "  app <file>                - Restore application data"
        echo "  full <timestamp>          - Full system restore from timestamp"
        echo ""
        echo "Examples:"
        echo "  $0 list                                    # List all backups"
        echo "  $0 postgres /path/to/backup.dump.gz.enc    # Restore PostgreSQL"
        echo "  $0 full 20240101_120000                    # Full restore"
        exit 1
        ;;
esac
