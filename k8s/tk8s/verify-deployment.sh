#!/bin/bash
set -euo pipefail

# TK8S Deployment Verification Script
# Runs comprehensive checks and validation

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           TK8S Deployment Verification                               ║${NC}"
echo -e "${BLUE}║    Comprehensive validation and health checks                        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((ERRORS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check cluster connectivity
check_cluster() {
    echo -e "${BLUE}📋 Checking cluster connectivity...${NC}"
    
    if kubectl cluster-info &> /dev/null; then
        print_success "Connected to cluster"
        kubectl cluster-info | head -2
    else
        print_error "Cannot connect to cluster"
        return 1
    fi
    echo ""
}

# Check namespaces
check_namespaces() {
    echo -e "${BLUE}📋 Checking TK8S namespaces...${NC}"
    
    REQUIRED_NAMESPACES=(
        "project-ai-core"
        "project-ai-security"
        "project-ai-memory"
        "project-ai-eca"
        "project-ai-monitoring"
        "project-ai-system"
    )
    
    for ns in "${REQUIRED_NAMESPACES[@]}"; do
        if kubectl get namespace "$ns" &> /dev/null; then
            STATUS=$(kubectl get namespace "$ns" -o jsonpath='{.status.phase}')
            if [ "$STATUS" = "Active" ]; then
                print_success "Namespace $ns exists and is Active"
            else
                print_warning "Namespace $ns exists but status is: $STATUS"
            fi
        else
            print_error "Namespace $ns not found"
        fi
    done
    echo ""
}

# Check RBAC
check_rbac() {
    echo -e "${BLUE}📋 Checking RBAC configuration...${NC}"
    
    SERVICE_ACCOUNTS=(
        "project-ai-core:project-ai-core"
        "project-ai-eca:project-ai-eca"
        "project-ai-security:project-ai-security"
        "project-ai-monitoring:project-ai-monitoring"
    )
    
    for sa in "${SERVICE_ACCOUNTS[@]}"; do
        IFS=':' read -r ns name <<< "$sa"
        if kubectl get serviceaccount "$name" -n "$ns" &> /dev/null; then
            print_success "ServiceAccount $name in $ns"
        else
            print_error "ServiceAccount $name not found in $ns"
        fi
    done
    echo ""
}

# Check network policies
check_network_policies() {
    echo -e "${BLUE}📋 Checking Network Policies...${NC}"
    
    POLICIES=(
        "project-ai-eca:deny-all-default"
        "project-ai-eca:eca-egress-only"
        "project-ai-core:project-ai-core-policy"
        "project-ai-security:project-ai-security-policy"
        "project-ai-monitoring:project-ai-monitoring-policy"
    )
    
    for policy in "${POLICIES[@]}"; do
        IFS=':' read -r ns name <<< "$policy"
        if kubectl get networkpolicy "$name" -n "$ns" &> /dev/null; then
            print_success "NetworkPolicy $name in $ns"
        else
            print_error "NetworkPolicy $name not found in $ns"
        fi
    done
    echo ""
}

# Check Kyverno policies
check_kyverno_policies() {
    echo -e "${BLUE}📋 Checking Kyverno ClusterPolicies...${NC}"
    
    POLICIES=(
        "tk8s-verify-image-signatures"
        "tk8s-require-sbom-annotation"
        "tk8s-no-mutable-containers"
        "tk8s-no-shell-access"
        "tk8s-require-readonly-root-filesystem"
        "tk8s-eca-isolation-enforcement"
        "tk8s-require-resource-limits"
    )
    
    for policy in "${POLICIES[@]}"; do
        if kubectl get clusterpolicy "$policy" &> /dev/null; then
            print_success "ClusterPolicy $policy"
        else
            print_warning "ClusterPolicy $policy not found (may not be deployed yet)"
        fi
    done
    echo ""
}

# Check ArgoCD
check_argocd() {
    echo -e "${BLUE}📋 Checking ArgoCD...${NC}"
    
    if kubectl get namespace argocd &> /dev/null; then
        print_success "ArgoCD namespace exists"
        
        # Check ArgoCD server deployment
        if kubectl get deployment argocd-server -n argocd &> /dev/null; then
            READY=$(kubectl get deployment argocd-server -n argocd -o jsonpath='{.status.readyReplicas}')
            DESIRED=$(kubectl get deployment argocd-server -n argocd -o jsonpath='{.spec.replicas}')
            
            if [ "$READY" = "$DESIRED" ]; then
                print_success "ArgoCD server is ready ($READY/$DESIRED replicas)"
            else
                print_warning "ArgoCD server not fully ready ($READY/$DESIRED replicas)"
            fi
        else
            print_error "ArgoCD server deployment not found"
        fi
        
        # Check ArgoCD applications
        echo ""
        echo "  ArgoCD Applications:"
        if kubectl get applications -n argocd &> /dev/null; then
            kubectl get applications -n argocd --no-headers | while read -r line; do
                NAME=$(echo "$line" | awk '{print $1}')
                SYNC=$(echo "$line" | awk '{print $2}')
                HEALTH=$(echo "$line" | awk '{print $3}')
                
                if [ "$SYNC" = "Synced" ] && [ "$HEALTH" = "Healthy" ]; then
                    print_success "Application $NAME: $SYNC, $HEALTH"
                else
                    print_warning "Application $NAME: $SYNC, $HEALTH"
                fi
            done
        else
            print_warning "No ArgoCD applications found"
        fi
    else
        print_error "ArgoCD not installed"
    fi
    echo ""
}

# Check Kyverno
check_kyverno() {
    echo -e "${BLUE}📋 Checking Kyverno...${NC}"
    
    if kubectl get namespace kyverno &> /dev/null; then
        print_success "Kyverno namespace exists"
        
        # Check Kyverno deployment
        if kubectl get deployment kyverno -n kyverno &> /dev/null; then
            READY=$(kubectl get deployment kyverno -n kyverno -o jsonpath='{.status.readyReplicas}')
            DESIRED=$(kubectl get deployment kyverno -n kyverno -o jsonpath='{.spec.replicas}')
            
            if [ "$READY" = "$DESIRED" ]; then
                print_success "Kyverno is ready ($READY/$DESIRED replicas)"
            else
                print_warning "Kyverno not fully ready ($READY/$DESIRED replicas)"
            fi
        else
            print_error "Kyverno deployment not found"
        fi
    else
        print_error "Kyverno not installed"
    fi
    echo ""
}

# Run Python validation script
run_python_validation() {
    echo -e "${BLUE}📋 Running Python validation script...${NC}"
    
    if [ -f "validate_tk8s.py" ]; then
        if command -v python3 &> /dev/null; then
            echo ""
            python3 validate_tk8s.py || {
                print_warning "Python validation script reported issues"
            }
        else
            print_warning "Python3 not found, skipping Python validation"
        fi
    else
        print_warning "validate_tk8s.py not found in current directory"
    fi
    echo ""
}

# Generate summary
generate_summary() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Verification Summary                               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🏛️  CIVILIZATION GRADE ACHIEVED${NC}"
        echo -e "${GREEN}All checks passed successfully!${NC}"
        return 0
    elif [ $ERRORS -eq 0 ]; then
        echo -e "${YELLOW}⚠️  APPROACHING CIVILIZATION GRADE${NC}"
        echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
        echo "Review warnings and address issues if needed."
        return 0
    else
        echo -e "${RED}❌ BELOW CIVILIZATION GRADE${NC}"
        echo -e "${RED}Errors: $ERRORS${NC}"
        echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
        echo ""
        echo "Please address the errors above before proceeding."
        return 1
    fi
}

# Main execution
main() {
    echo "Running TK8S deployment verification..."
    echo ""
    
    # Run all checks
    check_cluster || exit 1
    check_namespaces
    check_rbac
    check_network_policies
    check_kyverno_policies
    check_argocd
    check_kyverno
    run_python_validation
    
    # Generate summary
    generate_summary
    RESULT=$?
    
    echo ""
    echo "Documentation:"
    echo "  - Setup Guide: SETUP_GUIDE.md"
    echo "  - Troubleshooting: README.md"
    echo "  - Doctrine: ../../docs/TK8S_DOCTRINE.md"
    echo ""
    
    exit $RESULT
}

# Run main function
main "$@"
