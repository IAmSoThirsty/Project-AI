#!/usr/bin/env bash
# ==============================================================================
# Project-AI Single-Node Core Stack - Quick Start Script
# ==============================================================================
#
# This script provides an interactive quick start for deploying the stack.
# It guides users through configuration and launches all services.
#
# Usage: ./quickstart.sh [options]
#
# Options:
#   --no-validate    Skip validation checks
#   --no-prompt      Skip interactive prompts (use defaults)
#   --generate-only  Only generate secrets, don't start services
#
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Flags
VALIDATE=true
PROMPT=true
GENERATE_ONLY=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-validate)
            VALIDATE=false
            shift
            ;;
        --no-prompt)
            PROMPT=false
            shift
            ;;
        --generate-only)
            GENERATE_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-validate] [--no-prompt] [--generate-only]"
            exit 1
            ;;
    esac
done

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
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo -e "\n${CYAN}==>${NC} ${YELLOW}$1${NC}\n"
}

prompt_continue() {
    if [ "$PROMPT" = true ]; then
        read -p "$(echo -e ${CYAN}Press Enter to continue...${NC})"
    fi
}

# ==============================================================================
# Banner
# ==============================================================================

print_banner() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        Project-AI Single-Node Core Stack - Quick Start              ║
║                                                                      ║
║  This script will help you deploy the complete Project-AI stack:    ║
║  • PostgreSQL with pgvector (vector memory)                         ║
║  • Redis (queue, cache, pub/sub)                                    ║
║  • MCP Gateway (agent communication)                                ║
║  • Project-AI Orchestrator (core AI system)                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
EOF
}

# ==============================================================================
# Generate Secrets
# ==============================================================================

generate_secrets() {
    log_step "Step 1: Generate Secrets"
    
    if [ -f "env/.env" ]; then
        log_info "Environment file already exists: env/.env"
        if [ "$PROMPT" = true ]; then
            read -p "$(echo -e ${YELLOW}Overwrite existing env/.env? [y/N]:${NC} )" -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Keeping existing env/.env"
                return 0
            fi
        else
            log_info "Keeping existing env/.env"
            return 0
        fi
    fi
    
    log_info "Generating secure secrets..."
    
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        python3 << 'EOF' > /tmp/project-ai-secrets.env
import secrets
from cryptography.fernet import Fernet

print("SECRET_KEY=" + secrets.token_urlsafe(32))
print("FERNET_KEY=" + Fernet.generate_key().decode())
print("POSTGRES_PASSWORD=" + secrets.token_urlsafe(24))
print("REDIS_PASSWORD=" + secrets.token_urlsafe(24))
print("MCP_API_KEY=" + secrets.token_hex(32))
print("JWT_SECRET_KEY=" + secrets.token_urlsafe(32))
EOF
        
        # Copy template and append secrets
        cp env/project-ai-core.env env/.env
        
        # Update secrets in .env
        while IFS='=' read -r key value; do
            sed -i "s|^${key}=.*|${key}=${value}|g" env/.env
        done < /tmp/project-ai-secrets.env
        
        rm /tmp/project-ai-secrets.env
        
        log_success "Secrets generated and saved to env/.env"
        
    elif command -v openssl &> /dev/null; then
        log_warning "Python not available, using OpenSSL (Fernet key will need manual generation)"
        
        cp env/project-ai-core.env env/.env
        
        SECRET_KEY=$(openssl rand -base64 32)
        POSTGRES_PASSWORD=$(openssl rand -base64 24)
        REDIS_PASSWORD=$(openssl rand -base64 24)
        MCP_API_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -base64 32)
        
        sed -i "s|^SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|g" env/.env
        sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|g" env/.env
        sed -i "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|g" env/.env
        sed -i "s|^MCP_API_KEY=.*|MCP_API_KEY=${MCP_API_KEY}|g" env/.env
        sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET_KEY}|g" env/.env
        
        log_warning "FERNET_KEY must be set manually in env/.env"
        log_info "Run: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        
        log_success "Secrets generated (except FERNET_KEY)"
    else
        log_error "Neither Python nor OpenSSL available. Cannot generate secrets."
        exit 1
    fi
    
    # Set file permissions
    chmod 600 env/.env
    log_info "Set secure permissions on env/.env (600)"
}

configure_api_keys() {
    log_step "Step 2: Configure API Keys"
    
    if [ "$PROMPT" = true ]; then
        echo "Enter API keys (press Enter to skip):"
        echo ""
        
        read -p "$(echo -e ${CYAN}OpenAI API Key:${NC} )" OPENAI_KEY
        if [ ! -z "$OPENAI_KEY" ]; then
            sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=${OPENAI_KEY}|g" env/.env
            log_success "OpenAI API key configured"
        fi
        
        read -p "$(echo -e ${CYAN}Hugging Face API Key:${NC} )" HF_KEY
        if [ ! -z "$HF_KEY" ]; then
            sed -i "s|^HUGGINGFACE_API_KEY=.*|HUGGINGFACE_API_KEY=${HF_KEY}|g" env/.env
            log_success "Hugging Face API key configured"
        fi
        
        read -p "$(echo -e ${CYAN}Anthropic API Key:${NC} )" ANTHROPIC_KEY
        if [ ! -z "$ANTHROPIC_KEY" ]; then
            sed -i "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=${ANTHROPIC_KEY}|g" env/.env
            log_success "Anthropic API key configured"
        fi
    else
        log_info "Skipping API key configuration (use --no-prompt to skip)"
        log_info "Edit env/.env to add API keys manually"
    fi
}

generate_mcp_secrets() {
    log_step "Step 3: Generate MCP Secrets"
    
    if [ -f "mcp/.secrets.env" ] && [ "$PROMPT" = true ]; then
        read -p "$(echo -e ${YELLOW}MCP secrets file exists. Overwrite? [y/N]:${NC} )" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Keeping existing mcp/.secrets.env"
            return 0
        fi
    fi
    
    cp mcp/secrets.env mcp/.secrets.env
    
    if command -v openssl &> /dev/null; then
        MCP_API_KEY=$(openssl rand -hex 32)
        MCP_ADMIN_KEY=$(openssl rand -hex 32)
        MCP_JWT_SECRET=$(openssl rand -hex 64)
        MCP_SERVICE_TOKEN=$(openssl rand -base64 48)
        
        sed -i "s|^MCP_API_KEY=.*|MCP_API_KEY=${MCP_API_KEY}|g" mcp/.secrets.env
        sed -i "s|^MCP_ADMIN_API_KEY=.*|MCP_ADMIN_API_KEY=${MCP_ADMIN_KEY}|g" mcp/.secrets.env
        sed -i "s|^MCP_JWT_SECRET=.*|MCP_JWT_SECRET=${MCP_JWT_SECRET}|g" mcp/.secrets.env
        sed -i "s|^MCP_SERVICE_TOKEN=.*|MCP_SERVICE_TOKEN=${MCP_SERVICE_TOKEN}|g" mcp/.secrets.env
        
        chmod 600 mcp/.secrets.env
        log_success "MCP secrets generated"
    else
        log_error "OpenSSL not available. Cannot generate MCP secrets."
        exit 1
    fi
}

# ==============================================================================
# Validation
# ==============================================================================

run_validation() {
    log_step "Step 4: Validate Configuration"
    
    if [ "$VALIDATE" = true ] && [ -f "./validate.sh" ]; then
        chmod +x ./validate.sh
        ./validate.sh
    else
        log_warning "Skipping validation (--no-validate flag or validate.sh not found)"
    fi
}

# ==============================================================================
# Docker Operations
# ==============================================================================

pull_images() {
    log_step "Step 5: Pull Docker Images"
    
    log_info "Pulling required Docker images..."
    docker compose pull
    log_success "Images pulled successfully"
}

start_services() {
    log_step "Step 6: Start Services"
    
    log_info "Starting Project-AI core stack..."
    docker compose up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    log_info "Service status:"
    docker compose ps
}

verify_deployment() {
    log_step "Step 7: Verify Deployment"
    
    log_info "Checking service health..."
    
    # Check PostgreSQL
    if docker compose exec -T postgres pg_isready -U project_ai > /dev/null 2>&1; then
        log_success "PostgreSQL is ready"
    else
        log_warning "PostgreSQL is not ready yet"
    fi
    
    # Check Redis
    if docker compose exec -T redis redis-cli -a "${REDIS_PASSWORD}" ping > /dev/null 2>&1; then
        log_success "Redis is ready"
    else
        log_warning "Redis is not ready yet (may need password)"
    fi
    
    # Check orchestrator health endpoint
    sleep 5
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Orchestrator is healthy"
    else
        log_warning "Orchestrator health check failed (may still be starting)"
    fi
}

print_access_info() {
    log_step "Deployment Complete!"
    
    cat << EOF

${GREEN}╔══════════════════════════════════════════════════════════════════════╗
║                     Project-AI is now running!                       ║
╚══════════════════════════════════════════════════════════════════════╝${NC}

${CYAN}Access Points:${NC}
  • Orchestrator API:    http://localhost:5000
  • Health Endpoint:     http://localhost:8000/health
  • Metrics:             http://localhost:8001/metrics
  • MCP Gateway:         http://localhost:9000
  • MCP Admin:           http://localhost:9001

${CYAN}Management Commands:${NC}
  • View logs:           docker compose logs -f
  • Stop services:       docker compose down
  • Restart:             docker compose restart
  • Service status:      docker compose ps

${CYAN}Database Access:${NC}
  • PostgreSQL:          psql postgresql://project_ai@localhost:5432/project_ai
  • Redis:               redis-cli -p 6379 -a <password>

${CYAN}Configuration Files:${NC}
  • Environment:         env/.env
  • MCP Secrets:         mcp/.secrets.env
  • Logs:                logs/

${CYAN}Documentation:${NC}
  • README:              ./README.md
  • Production Guide:    ../../PRODUCTION_DEPLOYMENT.md

${YELLOW}⚠ Important Notes:${NC}
  1. Secrets are stored in env/.env and mcp/.secrets.env
  2. These files are gitignored and should NEVER be committed
  3. Back up your secrets in a secure location
  4. Configure API keys in env/.env for full functionality

${GREEN}Happy Hacking! 🚀${NC}

EOF
}

# ==============================================================================
# Main Function
# ==============================================================================

main() {
    clear
    print_banner
    echo ""
    
    prompt_continue
    
    # Generate secrets
    generate_secrets
    if [ "$GENERATE_ONLY" = true ]; then
        log_info "Secrets generated. Exiting (--generate-only flag)"
        exit 0
    fi
    
    # Configure API keys
    configure_api_keys
    
    # Generate MCP secrets
    generate_mcp_secrets
    
    # Validate configuration
    run_validation
    
    # Pull images
    pull_images
    
    # Start services
    start_services
    
    # Verify deployment
    verify_deployment
    
    # Print access information
    print_access_info
}

# Run main function
main
