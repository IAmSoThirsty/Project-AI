#!/usr/bin/env bash
# ==============================================================================
# Project-AI Single-Node Core Stack - Validation Script
# ==============================================================================
#
# This script validates the deployment configuration before launching the stack.
# It checks for required files, environment variables, and dependencies.
#
# Usage: ./validate.sh
#
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0

# ==============================================================================
# Helper Functions
# ==============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((WARNINGS++))
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    ((ERRORS++))
}

# ==============================================================================
# Validation Functions
# ==============================================================================

validate_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        return 1
    fi
    
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_success "Docker version: $DOCKER_VERSION"
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose v2 is not available. Please upgrade Docker."
        return 1
    fi
    
    COMPOSE_VERSION=$(docker compose version --short)
    log_success "Docker Compose version: $COMPOSE_VERSION"
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        return 1
    fi
    
    log_success "Docker is properly configured"
}

validate_files() {
    log_info "Checking required files..."
    
    local required_files=(
        "docker-compose.yml"
        "env/project-ai-core.env"
        "mcp/secrets.env"
        "mcp/config.yaml"
        "mcp/registry.yaml"
        "mcp/catalogs/project-ai.yaml"
        "postgres/init/01_extensions.sql"
        "redis/redis.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
        else
            log_success "Found: $file"
        fi
    done
}

validate_env_file() {
    log_info "Validating environment configuration..."
    
    # Check if .env exists (local overrides)
    if [ -f "env/.env" ]; then
        ENV_FILE="env/.env"
        log_info "Using local environment file: env/.env"
    else
        ENV_FILE="env/project-ai-core.env"
        log_warning "No env/.env found, using template: env/project-ai-core.env"
        log_warning "Copy env/project-ai-core.env to env/.env and configure it"
    fi
    
    # Check for required environment variables
    local required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "SECRET_KEY"
        "FERNET_KEY"
    )
    
    local optional_vars=(
        "OPENAI_API_KEY"
        "HUGGINGFACE_API_KEY"
        "MCP_API_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=$" "$ENV_FILE" || ! grep -q "^${var}=" "$ENV_FILE"; then
            log_error "Required variable not set: $var"
        else
            log_success "Variable configured: $var"
        fi
    done
    
    for var in "${optional_vars[@]}"; do
        if grep -q "^${var}=$" "$ENV_FILE" || ! grep -q "^${var}=" "$ENV_FILE"; then
            log_warning "Optional variable not set: $var"
        else
            log_success "Variable configured: $var"
        fi
    done
}

validate_mcp_secrets() {
    log_info "Validating MCP secrets..."
    
    if [ -f "mcp/.secrets.env" ]; then
        log_success "MCP secrets file exists: mcp/.secrets.env"
        
        # Check for key MCP variables
        if grep -q "^MCP_API_KEY=$" "mcp/.secrets.env" || ! grep -q "^MCP_API_KEY=" "mcp/.secrets.env"; then
            log_warning "MCP_API_KEY not set in mcp/.secrets.env"
        else
            log_success "MCP_API_KEY configured"
        fi
    else
        log_warning "MCP secrets file not found: mcp/.secrets.env"
        log_warning "Copy mcp/secrets.env to mcp/.secrets.env and configure it"
    fi
}

validate_ports() {
    log_info "Checking port availability..."
    
    local required_ports=(5000 5432 6379 8000 8001 8765 9000 9001)
    
    for port in "${required_ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_warning "Port $port is already in use"
        else
            log_success "Port $port is available"
        fi
    done
}

validate_disk_space() {
    log_info "Checking disk space..."
    
    local available=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    local required=20
    
    if [ "$available" -lt "$required" ]; then
        log_error "Insufficient disk space. Required: ${required}GB, Available: ${available}GB"
    else
        log_success "Sufficient disk space available: ${available}GB"
    fi
}

validate_memory() {
    log_info "Checking available memory..."
    
    if [ -f "/proc/meminfo" ]; then
        local total_mem=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024/1024)}')
        local required_mem=8
        
        if [ "$total_mem" -lt "$required_mem" ]; then
            log_warning "Low memory. Required: ${required_mem}GB, Available: ${total_mem}GB"
        else
            log_success "Sufficient memory available: ${total_mem}GB"
        fi
    else
        log_info "Cannot determine memory (non-Linux system)"
    fi
}

validate_docker_compose() {
    log_info "Validating docker-compose.yml syntax..."
    
    if docker compose config > /dev/null 2>&1; then
        log_success "docker-compose.yml syntax is valid"
    else
        log_error "docker-compose.yml has syntax errors"
        docker compose config 2>&1 | head -20
    fi
}

generate_secrets() {
    log_info "Secret generation helpers:"
    echo ""
    echo "To generate required secrets, run these commands:"
    echo ""
    echo "# Python method (recommended):"
    echo "python3 << 'EOF'"
    echo "import secrets"
    echo "from cryptography.fernet import Fernet"
    echo ""
    echo "print(\"SECRET_KEY=\" + secrets.token_urlsafe(32))"
    echo "print(\"FERNET_KEY=\" + Fernet.generate_key().decode())"
    echo "print(\"POSTGRES_PASSWORD=\" + secrets.token_urlsafe(24))"
    echo "print(\"REDIS_PASSWORD=\" + secrets.token_urlsafe(24))"
    echo "print(\"MCP_API_KEY=\" + secrets.token_hex(32))"
    echo "EOF"
    echo ""
    echo "# OpenSSL method:"
    echo "SECRET_KEY=\$(openssl rand -base64 32)"
    echo "POSTGRES_PASSWORD=\$(openssl rand -base64 24)"
    echo "REDIS_PASSWORD=\$(openssl rand -base64 24)"
    echo "MCP_API_KEY=\$(openssl rand -hex 32)"
    echo ""
}

# ==============================================================================
# Main Validation
# ==============================================================================

main() {
    echo "=============================================================================="
    echo "Project-AI Single-Node Core Stack - Deployment Validation"
    echo "=============================================================================="
    echo ""
    
    # Run all validations
    validate_docker
    echo ""
    
    validate_files
    echo ""
    
    validate_env_file
    echo ""
    
    validate_mcp_secrets
    echo ""
    
    validate_ports
    echo ""
    
    validate_disk_space
    echo ""
    
    validate_memory
    echo ""
    
    validate_docker_compose
    echo ""
    
    # Summary
    echo "=============================================================================="
    echo "Validation Summary"
    echo "=============================================================================="
    
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        log_success "All validations passed! Ready to deploy."
        echo ""
        echo "To start the stack, run:"
        echo "  docker compose up -d"
        echo ""
        echo "Or use the quickstart script:"
        echo "  ./quickstart.sh"
        return 0
    elif [ $ERRORS -eq 0 ]; then
        log_warning "Validation passed with $WARNINGS warning(s)"
        echo ""
        echo "You can proceed, but review the warnings above."
        echo ""
        generate_secrets
        return 0
    else
        log_error "Validation failed with $ERRORS error(s) and $WARNINGS warning(s)"
        echo ""
        echo "Please fix the errors above before deploying."
        echo ""
        generate_secrets
        return 1
    fi
}

# Run main function
main
