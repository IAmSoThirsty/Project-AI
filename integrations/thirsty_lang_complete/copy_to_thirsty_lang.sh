#!/bin/bash

#############################################################################
# copy_to_thirsty_lang.sh
# 
# Automated deployment script for Thirsty-Lang + TARL integration
# 
# Usage:
#   ./copy_to_thirsty_lang.sh [target_directory]
#   
# Example:
#   ./copy_to_thirsty_lang.sh /path/to/thirsty-lang-repo
#   ./copy_to_thirsty_lang.sh ~/projects/thirsty-lang
#
# Version: 1.0.0
# License: MIT
#############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}"

# Default target directory
DEFAULT_TARGET="../../../thirsty-lang"
TARGET_DIR="${1:-$DEFAULT_TARGET}"

# Log file
LOG_FILE="${SCRIPT_DIR}/deployment.log"

#############################################################################
# Helper Functions
#############################################################################

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$*"
    echo "=========================================="
    echo ""
}

check_dependency() {
    local cmd=$1
    if ! command -v "$cmd" &> /dev/null; then
        log_error "$cmd not found. Please install it first."
        return 1
    fi
    return 0
}

confirm() {
    local prompt="$1"
    local response
    read -r -p "$prompt [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) 
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

#############################################################################
# Pre-flight Checks
#############################################################################

preflight_checks() {
    print_header "Pre-flight Checks"
    
    log_info "Checking dependencies..."
    
    # Check required commands
    local deps=("python3" "node" "npm" "rsync")
    for dep in "${deps[@]}"; do
        if check_dependency "$dep"; then
            log_success "$dep found"
        else
            log_error "Missing dependency: $dep"
            exit 1
        fi
    done
    
    # Check Python version
    local python_version
    python_version=$(python3 --version | awk '{print $2}')
    log_info "Python version: $python_version"
    
    # Check Node.js version
    local node_version
    node_version=$(node --version)
    log_info "Node.js version: $node_version"
    
    # Check source directory
    if [ ! -d "$SOURCE_DIR/bridge" ]; then
        log_error "Source directory not found: $SOURCE_DIR/bridge"
        exit 1
    fi
    log_success "Source directory found: $SOURCE_DIR"
    
    # Check/create target directory
    if [ ! -d "$TARGET_DIR" ]; then
        log_warning "Target directory not found: $TARGET_DIR"
        if confirm "Create target directory?"; then
            mkdir -p "$TARGET_DIR"
            log_success "Created target directory"
        else
            log_error "Target directory required"
            exit 1
        fi
    fi
    log_success "Target directory found: $TARGET_DIR"
    
    # Check write permissions
    if [ ! -w "$TARGET_DIR" ]; then
        log_error "No write permission for target directory"
        exit 1
    fi
    log_success "Write permission confirmed"
}

#############################################################################
# Backup Existing Files
#############################################################################

backup_existing() {
    print_header "Backup Existing Files"
    
    local backup_dir="${TARGET_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
    
    # Check if security directory exists
    if [ -d "${TARGET_DIR}/src/security/bridge" ]; then
        log_info "Existing bridge directory found, creating backup..."
        mkdir -p "$backup_dir"
        cp -r "${TARGET_DIR}/src/security/bridge" "$backup_dir/"
        log_success "Backup created: $backup_dir"
    else
        log_info "No existing files to backup"
    fi
}

#############################################################################
# Create Directory Structure
#############################################################################

create_structure() {
    print_header "Create Directory Structure"
    
    log_info "Creating directory structure..."
    
    local dirs=(
        "src/security/bridge"
        "policies"
        "config"
        "logs"
        "tests/integration"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "${TARGET_DIR}/${dir}"
        log_success "Created: ${dir}"
    done
}

#############################################################################
# Copy Bridge Files
#############################################################################

copy_bridge_files() {
    print_header "Copy Bridge Files"
    
    log_info "Copying bridge files..."
    
    # Copy JavaScript bridge
    if [ -f "${SOURCE_DIR}/bridge/tarl-bridge.js" ]; then
        cp "${SOURCE_DIR}/bridge/tarl-bridge.js" "${TARGET_DIR}/src/security/bridge/"
        log_success "Copied: tarl-bridge.js"
    else
        log_error "Source file not found: tarl-bridge.js"
        exit 1
    fi
    
    # Copy Python unified security
    if [ -f "${SOURCE_DIR}/bridge/unified-security.py" ]; then
        cp "${SOURCE_DIR}/bridge/unified-security.py" "${TARGET_DIR}/src/security/bridge/"
        log_success "Copied: unified-security.py"
    else
        log_error "Source file not found: unified-security.py"
        exit 1
    fi
    
    # Copy bridge README
    if [ -f "${SOURCE_DIR}/bridge/README.md" ]; then
        cp "${SOURCE_DIR}/bridge/README.md" "${TARGET_DIR}/src/security/bridge/"
        log_success "Copied: bridge/README.md"
    fi
}

#############################################################################
# Copy Documentation
#############################################################################

copy_documentation() {
    print_header "Copy Documentation"
    
    log_info "Copying documentation files..."
    
    local docs=(
        "INTEGRATION_COMPLETE.md"
        "MIGRATION_CHECKLIST.md"
        "FEATURES.md"
    )
    
    for doc in "${docs[@]}"; do
        if [ -f "${SOURCE_DIR}/${doc}" ]; then
            cp "${SOURCE_DIR}/${doc}" "${TARGET_DIR}/docs/"
            log_success "Copied: ${doc}"
        else
            log_warning "Documentation not found: ${doc}"
        fi
    done
}

#############################################################################
# Create Configuration Files
#############################################################################

create_config_files() {
    print_header "Create Configuration Files"
    
    # Create .env file if it doesn't exist
    if [ ! -f "${TARGET_DIR}/.env" ]; then
        log_info "Creating .env file..."
        cat > "${TARGET_DIR}/.env" << 'EOF'
# TARL Configuration
TARL_POLICY_DIR=./policies
TARL_AUDIT_LOG=./logs/audit.log
TARL_LOG_LEVEL=INFO
TARL_CACHE_SIZE=1000
TARL_CACHE_TTL=60

# Bridge Configuration
TARL_BRIDGE_PYTHON_PATH=python3
TARL_BRIDGE_TIMEOUT=5000
TARL_BRIDGE_RETRY_ATTEMPTS=3

# Security Configuration
SECURITY_STRICT_MODE=true
SECURITY_AUDIT_ENABLED=true
EOF
        log_success "Created: .env"
    else
        log_info ".env already exists, skipping"
    fi
    
    # Create security.yaml if it doesn't exist
    if [ ! -f "${TARGET_DIR}/config/security.yaml" ]; then
        log_info "Creating config/security.yaml..."
        cat > "${TARGET_DIR}/config/security.yaml" << 'EOF'
security:
  strict_mode: true
  default_action: "deny"
  
  audit:
    enabled: true
    log_file: "./logs/audit.log"
    log_rotation:
      max_size_mb: 100
      max_files: 10
    flush_interval_sec: 30
  
  cache:
    enabled: true
    max_size: 1000
    ttl_sec: 60
    eviction_policy: "lru"
  
  rate_limiting:
    enabled: true
    requests_per_minute: 100
    burst_size: 10

bridge:
  python:
    path: "python3"
    module: "tarl.runtime"
    startup_timeout_sec: 10
  
  communication:
    protocol: "json-rpc"
    buffer_size: 8192
    max_message_size_mb: 10
  
  resilience:
    retry_attempts: 3
    retry_backoff_ms: [100, 500, 1000]
    circuit_breaker:
      failure_threshold: 5
      timeout_sec: 30
      half_open_after_sec: 60
EOF
        log_success "Created: config/security.yaml"
    else
        log_info "config/security.yaml already exists, skipping"
    fi
    
    # Create default policy if it doesn't exist
    if [ ! -f "${TARGET_DIR}/policies/default.yaml" ]; then
        log_info "Creating policies/default.yaml..."
        cat > "${TARGET_DIR}/policies/default.yaml" << 'EOF'
version: "1.0"
name: "Default Security Policy"

rules:
  - id: "file_read_home"
    operation: "file_read"
    resource: "/home/*"
    action: "allow"
    audit: true
  
  - id: "file_write_tmp"
    operation: "file_write"
    resource: "/tmp/*"
    action: "allow"
    audit: true
  
  - id: "system_files_deny"
    operation: "file_*"
    resource: "/etc/*"
    action: "deny"
    reason: "System files are protected"
  
  - id: "network_https"
    operation: "network_request"
    resource: "https://*"
    action: "allow"
    audit: true

resource_limits:
  max_memory_mb: 512
  max_cpu_percent: 80
  max_file_handles: 100
  max_network_connections: 10

temporal_constraints:
  policy_refresh_interval: 300
  decision_cache_ttl: 60
  audit_flush_interval: 30
EOF
        log_success "Created: policies/default.yaml"
    else
        log_info "policies/default.yaml already exists, skipping"
    fi
}

#############################################################################
# Install Dependencies
#############################################################################

install_dependencies() {
    print_header "Install Dependencies"
    
    if confirm "Install Python dependencies?"; then
        log_info "Installing Python dependencies..."
        pip3 install --quiet pyyaml jsonschema cryptography psutil
        log_success "Python dependencies installed"
    fi
    
    if confirm "Install Node.js dependencies?"; then
        log_info "Installing Node.js dependencies..."
        cd "$TARGET_DIR"
        npm install --quiet
        log_success "Node.js dependencies installed"
    fi
}

#############################################################################
# Verification
#############################################################################

verify_installation() {
    print_header "Verify Installation"
    
    log_info "Verifying installation..."
    
    # Check bridge files exist
    local files=(
        "src/security/bridge/tarl-bridge.js"
        "src/security/bridge/unified-security.py"
        "src/security/bridge/README.md"
        "config/security.yaml"
        "policies/default.yaml"
    )
    
    local all_good=true
    for file in "${files[@]}"; do
        if [ -f "${TARGET_DIR}/${file}" ]; then
            log_success "Found: ${file}"
        else
            log_error "Missing: ${file}"
            all_good=false
        fi
    done
    
    # Test TARL import
    log_info "Testing TARL import..."
    if python3 -c "import tarl" 2>/dev/null; then
        log_success "TARL import successful"
    else
        log_warning "TARL not installed (install with: pip install tarl)"
    fi
    
    # Test bridge import
    log_info "Testing bridge module..."
    if node -e "require('${TARGET_DIR}/src/security/bridge/tarl-bridge.js')" 2>/dev/null; then
        log_success "Bridge module loads successfully"
    else
        log_error "Bridge module failed to load"
        all_good=false
    fi
    
    if [ "$all_good" = true ]; then
        log_success "All verification checks passed"
        return 0
    else
        log_error "Some verification checks failed"
        return 1
    fi
}

#############################################################################
# Generate Summary
#############################################################################

generate_summary() {
    print_header "Deployment Summary"
    
    log_info "Deployment completed successfully!"
    echo ""
    log_info "Files installed to: $TARGET_DIR"
    log_info "Log file: $LOG_FILE"
    echo ""
    log_info "Next steps:"
    echo "  1. Review configuration files:"
    echo "     - ${TARGET_DIR}/.env"
    echo "     - ${TARGET_DIR}/config/security.yaml"
    echo "     - ${TARGET_DIR}/policies/default.yaml"
    echo ""
    echo "  2. Install dependencies (if not done):"
    echo "     cd ${TARGET_DIR}"
    echo "     pip3 install pyyaml jsonschema cryptography psutil"
    echo "     npm install"
    echo ""
    echo "  3. Test the integration:"
    echo "     node -e \"const {TARLBridge} = require('./src/security/bridge/tarl-bridge'); console.log('OK')\""
    echo ""
    echo "  4. Read the documentation:"
    echo "     - ${TARGET_DIR}/docs/INTEGRATION_COMPLETE.md"
    echo "     - ${TARGET_DIR}/docs/MIGRATION_CHECKLIST.md"
    echo ""
}

#############################################################################
# Main Execution
#############################################################################

main() {
    # Initialize log file
    echo "========================================" > "$LOG_FILE"
    echo "Deployment started: $(date)" >> "$LOG_FILE"
    echo "========================================" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Print banner
    echo ""
    echo "╔════════════════════════════════════════════════════╗"
    echo "║  Thirsty-Lang + TARL Integration Deployment       ║"
    echo "║  Version 1.0.0                                     ║"
    echo "╚════════════════════════════════════════════════════╝"
    echo ""
    
    # Run deployment steps
    preflight_checks
    backup_existing
    create_structure
    copy_bridge_files
    copy_documentation
    create_config_files
    install_dependencies
    
    # Verify installation
    if verify_installation; then
        generate_summary
        exit 0
    else
        log_error "Installation verification failed"
        log_error "Check log file for details: $LOG_FILE"
        exit 1
    fi
}

# Run main function
main "$@"
