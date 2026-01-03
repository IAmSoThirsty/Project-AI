#!/bin/bash

################################################################################
# The_Triumvirate Integration Script
# 
# This script integrates The_Triumvirate repository as the new web frontend
# for Project-AI. It handles submodule addition, dependency installation,
# configuration, and verification.
#
# Usage:
#   ./scripts/integrate_triumvirate.sh [OPTIONS]
#
# Options:
#   --repo-url URL    Specify The_Triumvirate repository URL
#   --branch BRANCH   Specify branch to use (default: main)
#   --method METHOD   Integration method: submodule|direct|monorepo (default: submodule)
#   --skip-deps       Skip dependency installation
#   --dry-run         Show what would be done without making changes
#   --help            Show this help message
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
REPO_URL="https://github.com/IAmSoThirsty/The_Triumvirate.git"
BRANCH="main"
METHOD="submodule"
SKIP_DEPS=false
DRY_RUN=false

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TRIUMVIRATE_PATH="$PROJECT_ROOT/web/triumvirate"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

run_command() {
    local cmd="$1"
    local description="$2"
    
    if [ "$DRY_RUN" = true ]; then
        print_info "[DRY RUN] Would execute: $cmd"
        return 0
    fi
    
    print_info "Running: $description"
    if eval "$cmd"; then
        print_success "$description completed"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "git is not installed"
        exit 1
    fi
    print_success "git is installed"
    
    # Check if npm is installed (for dependency installation)
    if ! command -v npm &> /dev/null; then
        print_warning "npm is not installed (required for dependency installation)"
        if [ "$SKIP_DEPS" = false ]; then
            print_error "Cannot proceed without npm. Install npm or use --skip-deps"
            exit 1
        fi
    else
        print_success "npm is installed"
    fi
    
    # Check if we're in a git repository
    if [ ! -d "$PROJECT_ROOT/.git" ]; then
        print_error "Not in a git repository"
        exit 1
    fi
    print_success "In git repository"
    
    # Check if web directory exists
    if [ ! -d "$PROJECT_ROOT/web" ]; then
        print_error "web directory not found"
        exit 1
    fi
    print_success "web directory exists"
}

backup_current_frontend() {
    print_header "Backing Up Current Frontend"
    
    local backup_dir="$PROJECT_ROOT/web/frontend.backup.$(date +%Y%m%d_%H%M%S)"
    
    if [ -d "$PROJECT_ROOT/web/frontend" ]; then
        run_command "cp -r $PROJECT_ROOT/web/frontend $backup_dir" \
                    "Backing up current frontend to $backup_dir"
    else
        print_info "No existing frontend to backup"
    fi
}

integrate_as_submodule() {
    print_header "Integrating as Git Submodule"
    
    # Check if submodule already exists
    if [ -d "$TRIUMVIRATE_PATH/.git" ]; then
        print_warning "Triumvirate submodule already exists"
        run_command "cd $TRIUMVIRATE_PATH && git pull origin $BRANCH" \
                    "Updating existing submodule"
        return 0
    fi
    
    # Remove directory if it exists but is not a submodule
    if [ -d "$TRIUMVIRATE_PATH" ]; then
        print_warning "Removing existing triumvirate directory"
        run_command "rm -rf $TRIUMVIRATE_PATH" \
                    "Removing existing directory"
    fi
    
    # Add submodule
    run_command "cd $PROJECT_ROOT && git submodule add -b $BRANCH $REPO_URL web/triumvirate" \
                "Adding The_Triumvirate as submodule"
    
    # Initialize and update submodules
    run_command "cd $PROJECT_ROOT && git submodule update --init --recursive" \
                "Initializing submodules"
}

integrate_directly() {
    print_header "Integrating Directly"
    
    local temp_dir="/tmp/triumvirate_temp_$$"
    
    # Clone to temporary directory
    run_command "git clone -b $BRANCH $REPO_URL $temp_dir" \
                "Cloning The_Triumvirate repository"
    
    # Remove .git directory from cloned repo
    run_command "rm -rf $temp_dir/.git" \
                "Removing .git directory"
    
    # Create triumvirate directory
    run_command "mkdir -p $TRIUMVIRATE_PATH" \
                "Creating triumvirate directory"
    
    # Copy contents
    run_command "cp -r $temp_dir/* $TRIUMVIRATE_PATH/" \
                "Copying Triumvirate contents"
    
    # Cleanup
    run_command "rm -rf $temp_dir" \
                "Cleaning up temporary directory"
}

install_dependencies() {
    if [ "$SKIP_DEPS" = true ]; then
        print_info "Skipping dependency installation (--skip-deps)"
        return 0
    fi
    
    print_header "Installing Dependencies"
    
    if [ ! -f "$TRIUMVIRATE_PATH/package.json" ]; then
        print_warning "No package.json found in Triumvirate"
        return 0
    fi
    
    run_command "cd $TRIUMVIRATE_PATH && npm install" \
                "Installing npm dependencies"
}

update_gitmodules() {
    print_header "Updating .gitmodules"
    
    local gitmodules="$PROJECT_ROOT/.gitmodules"
    
    if grep -q "web/triumvirate" "$gitmodules" 2>/dev/null; then
        print_info ".gitmodules already contains Triumvirate entry"
        return 0
    fi
    
    # Append to .gitmodules if using submodule method
    if [ "$METHOD" = "submodule" ]; then
        cat >> "$gitmodules" << EOF

[submodule "web/triumvirate"]
	path = web/triumvirate
	url = $REPO_URL
	branch = $BRANCH
EOF
        print_success "Updated .gitmodules"
    fi
}

update_package_json() {
    print_header "Updating package.json"
    
    local package_json="$PROJECT_ROOT/package.json"
    
    if [ ! -f "$package_json" ]; then
        print_warning "No package.json found in project root"
        return 0
    fi
    
    print_info "Adding Triumvirate scripts to package.json"
    
    # Note: This is a simple append. In production, use a proper JSON parser like jq
    # For now, provide manual instructions
    print_warning "Manual step required: Add these scripts to package.json:"
    cat << EOF

  "triumvirate:install": "cd web/triumvirate && npm install",
  "triumvirate:dev": "cd web/triumvirate && npm run dev",
  "triumvirate:build": "cd web/triumvirate && npm run build",
  "triumvirate:preview": "cd web/triumvirate && npm run preview",
  "web:full": "npm run triumvirate:build && python -m web.backend.app"
EOF
}

update_env_file() {
    print_header "Updating Environment Configuration"
    
    local env_example="$PROJECT_ROOT/.env.example"
    
    if [ ! -f "$env_example" ]; then
        print_warning "No .env.example found"
        return 0
    fi
    
    # Check if Triumvirate config already exists
    if grep -q "TRIUMVIRATE" "$env_example"; then
        print_info "Triumvirate configuration already in .env.example"
        return 0
    fi
    
    # Append Triumvirate configuration
    cat >> "$env_example" << EOF

# The_Triumvirate Web Frontend Configuration
VITE_API_URL=http://localhost:5000
VITE_WS_URL=ws://localhost:5000
TRIUMVIRATE_PORT=3000
ENABLE_TRIUMVIRATE=true
LEGACY_FRONTEND=false
EOF
    
    print_success "Updated .env.example with Triumvirate configuration"
}

update_documentation() {
    print_header "Updating Documentation"
    
    print_info "Documentation updates needed:"
    echo "  - README.md: Add Triumvirate section"
    echo "  - DEPLOYMENT.md: Update deployment instructions"
    echo "  - PROGRAM_SUMMARY.md: Add Triumvirate architecture"
    
    print_warning "These updates should be done manually or by a follow-up script"
}

verify_integration() {
    print_header "Verifying Integration"
    
    # Check if Triumvirate directory exists and has content
    if [ ! -d "$TRIUMVIRATE_PATH" ]; then
        print_error "Triumvirate directory not found"
        return 1
    fi
    print_success "Triumvirate directory exists"
    
    # Check for essential files
    local essential_files=("package.json" "src" "public")
    for file in "${essential_files[@]}"; do
        if [ -e "$TRIUMVIRATE_PATH/$file" ]; then
            print_success "Found $file"
        else
            print_warning "Missing $file (might be okay depending on structure)"
        fi
    done
    
    # Check if node_modules exists (if deps were installed)
    if [ "$SKIP_DEPS" = false ] && [ -d "$TRIUMVIRATE_PATH/node_modules" ]; then
        print_success "Dependencies installed successfully"
    fi
    
    print_success "Integration verification complete"
}

print_next_steps() {
    print_header "Next Steps"
    
    cat << EOF
${GREEN}Integration complete!${NC}

To start using The_Triumvirate:

1. Configure environment variables:
   ${BLUE}cp .env.example .env${NC}
   ${BLUE}# Edit .env with your settings${NC}

2. Start the development server:
   ${BLUE}cd web/triumvirate${NC}
   ${BLUE}npm run dev${NC}

3. Start the Flask backend:
   ${BLUE}python -m web.backend.app${NC}

4. Access the application:
   ${BLUE}Frontend: http://localhost:3000${NC}
   ${BLUE}Backend:  http://localhost:5000${NC}

For more information, see:
  - TRIUMVIRATE_INTEGRATION.md
  - README.md

EOF
}

show_help() {
    cat << EOF
The_Triumvirate Integration Script

Usage:
  ./scripts/integrate_triumvirate.sh [OPTIONS]

Options:
  --repo-url URL    Specify The_Triumvirate repository URL
                    Default: https://github.com/IAmSoThirsty/The_Triumvirate.git
  
  --branch BRANCH   Specify branch to use
                    Default: main
  
  --method METHOD   Integration method: submodule|direct|monorepo
                    Default: submodule
  
  --skip-deps       Skip dependency installation
  
  --dry-run         Show what would be done without making changes
  
  --help            Show this help message

Examples:
  # Standard integration using defaults
  ./scripts/integrate_triumvirate.sh

  # Use a specific branch
  ./scripts/integrate_triumvirate.sh --branch develop

  # Direct integration (no submodule)
  ./scripts/integrate_triumvirate.sh --method direct

  # Dry run to see what would happen
  ./scripts/integrate_triumvirate.sh --dry-run

EOF
}

################################################################################
# Main Script
################################################################################

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --repo-url)
                REPO_URL="$2"
                shift 2
                ;;
            --branch)
                BRANCH="$2"
                shift 2
                ;;
            --method)
                METHOD="$2"
                shift 2
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Print configuration
    print_header "Integration Configuration"
    echo "Repository URL: $REPO_URL"
    echo "Branch: $BRANCH"
    echo "Method: $METHOD"
    echo "Skip Dependencies: $SKIP_DEPS"
    echo "Dry Run: $DRY_RUN"
    echo ""
    
    # Run integration steps
    check_prerequisites
    backup_current_frontend
    
    case $METHOD in
        submodule)
            integrate_as_submodule
            ;;
        direct)
            integrate_directly
            ;;
        monorepo)
            print_error "Monorepo method not yet implemented"
            exit 1
            ;;
        *)
            print_error "Unknown integration method: $METHOD"
            exit 1
            ;;
    esac
    
    install_dependencies
    update_gitmodules
    update_package_json
    update_env_file
    update_documentation
    verify_integration
    print_next_steps
    
    print_header "Integration Complete"
    print_success "The_Triumvirate has been successfully integrated!"
}

# Run main function
main "$@"
