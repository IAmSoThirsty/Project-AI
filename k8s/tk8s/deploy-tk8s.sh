#!/bin/bash
set -euo pipefail

# TK8S Main Deployment Script
# Deploys all TK8S components to Kubernetes cluster

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              TK8S Deployment Script                                  ║${NC}"
echo -e "${BLUE}║    Thirsty's Kubernetes - Civilization Grade Deployment              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
DRY_RUN="${DRY_RUN:-false}"
SKIP_VALIDATION="${SKIP_VALIDATION:-false}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run           Perform a dry-run (no actual changes)"
            echo "  --skip-validation   Skip post-deployment validation"
            echo "  -h, --help          Show this help message"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 Running in DRY-RUN mode (no changes will be made)${NC}"
    echo ""
    KUBECTL_ARGS="--dry-run=client"
else
    KUBECTL_ARGS=""
fi

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}📋 Checking prerequisites...${NC}"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found${NC}"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    # Check ArgoCD
    if ! kubectl get namespace argocd &> /dev/null; then
        echo -e "${YELLOW}⚠️  ArgoCD not installed. Run ./install-prerequisites.sh first${NC}"
        exit 1
    fi
    
    # Check Kyverno
    if ! kubectl get namespace kyverno &> /dev/null; then
        echo -e "${YELLOW}⚠️  Kyverno not installed. Run ./install-prerequisites.sh first${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
    echo ""
}

# Deploy namespaces
deploy_namespaces() {
    echo -e "${BLUE}🚀 Deploying TK8S namespaces...${NC}"
    
    kubectl apply ${KUBECTL_ARGS} -f namespaces/tk8s-namespaces.yaml
    
    if [ "$DRY_RUN" = false ]; then
        # Wait for namespaces to be ready
        for ns in project-ai-core project-ai-security project-ai-memory project-ai-eca project-ai-monitoring project-ai-system; do
            kubectl wait --for=jsonpath='{.status.phase}'=Active namespace/${ns} --timeout=30s 2>/dev/null || true
        done
    fi
    
    echo -e "${GREEN}✅ Namespaces deployed${NC}"
    echo ""
}

# Deploy RBAC
deploy_rbac() {
    echo -e "${BLUE}🚀 Deploying RBAC policies...${NC}"
    
    kubectl apply ${KUBECTL_ARGS} -f rbac/tk8s-rbac.yaml
    
    echo -e "${GREEN}✅ RBAC policies deployed${NC}"
    echo ""
}

# Deploy Network Policies
deploy_network_policies() {
    echo -e "${BLUE}🚀 Deploying Network Policies...${NC}"
    
    kubectl apply ${KUBECTL_ARGS} -f network-policies/tk8s-network-policies.yaml
    
    echo -e "${GREEN}✅ Network Policies deployed${NC}"
    echo ""
}

# Deploy Kyverno Policies
deploy_kyverno_policies() {
    echo -e "${BLUE}🚀 Deploying Kyverno admission policies...${NC}"
    
    # Check if public key is configured
    if grep -q "# TODO: Replace with actual Cosign public key" security/kyverno-policies.yaml; then
        echo -e "${YELLOW}⚠️  Cosign public key not configured in Kyverno policy${NC}"
        echo "   Run ./generate-cosign-keys.sh to generate and configure keys"
        echo "   Skipping Kyverno policies deployment for now..."
        echo ""
        return 0
    fi
    
    kubectl apply ${KUBECTL_ARGS} -f security/kyverno-policies.yaml
    
    echo -e "${GREEN}✅ Kyverno policies deployed${NC}"
    echo ""
}

# Deploy using Kustomize
deploy_with_kustomize() {
    echo -e "${BLUE}🚀 Deploying TK8S with Kustomize...${NC}"
    
    if command -v kustomize &> /dev/null; then
        kubectl apply ${KUBECTL_ARGS} -k .
        echo -e "${GREEN}✅ Kustomize deployment complete${NC}"
    else
        echo -e "${YELLOW}⚠️  Kustomize not found, using kubectl apply -k${NC}"
        kubectl apply ${KUBECTL_ARGS} -k .
        echo -e "${GREEN}✅ Deployment complete${NC}"
    fi
    
    echo ""
}

# Deploy ArgoCD Applications
deploy_argocd_apps() {
    echo -e "${BLUE}🚀 Deploying ArgoCD applications...${NC}"
    
    kubectl apply ${KUBECTL_ARGS} -f argocd/applications.yaml
    
    if [ "$DRY_RUN" = false ]; then
        echo "  Waiting for ArgoCD applications to sync..."
        sleep 5
        
        # Check ArgoCD application status
        echo ""
        echo "  ArgoCD Application Status:"
        kubectl get applications -n argocd 2>/dev/null || echo "    (Applications not yet created)"
    fi
    
    echo -e "${GREEN}✅ ArgoCD applications deployed${NC}"
    echo ""
}

# Deploy monitoring (optional)
deploy_monitoring() {
    echo -e "${BLUE}🚀 Deploying monitoring configuration...${NC}"
    
    read -p "Deploy monitoring stack (Prometheus, Grafana)? (yes/no): " -r
    if [[ $REPLY =~ ^yes$ ]]; then
        kubectl apply ${KUBECTL_ARGS} -f monitoring/prometheus-config.yaml
        echo -e "${GREEN}✅ Monitoring configuration deployed${NC}"
        echo "   Note: You may need to install Prometheus/Grafana separately via Helm"
    else
        echo "  Skipping monitoring deployment"
    fi
    
    echo ""
}

# Check deployment status
check_status() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${BLUE}Skipping status check in dry-run mode${NC}"
        return 0
    fi
    
    echo -e "${BLUE}📊 Checking deployment status...${NC}"
    echo ""
    
    echo "Namespaces:"
    kubectl get namespaces | grep project-ai || echo "  No TK8S namespaces found"
    echo ""
    
    echo "ServiceAccounts:"
    kubectl get serviceaccounts -n project-ai-core -n project-ai-eca 2>/dev/null || echo "  Not available yet"
    echo ""
    
    echo "NetworkPolicies:"
    kubectl get networkpolicies -A | grep project-ai || echo "  No network policies found"
    echo ""
    
    echo "Kyverno ClusterPolicies:"
    kubectl get clusterpolicies 2>/dev/null || echo "  No cluster policies found"
    echo ""
    
    echo "ArgoCD Applications:"
    kubectl get applications -n argocd 2>/dev/null || echo "  No applications found"
    echo ""
}

# Run validation
run_validation() {
    if [ "$SKIP_VALIDATION" = true ] || [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}Skipping validation${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🔍 Running deployment validation...${NC}"
    echo ""
    
    if [ -f "validate_tk8s.py" ]; then
        python3 validate_tk8s.py || {
            echo -e "${YELLOW}⚠️  Validation script found issues. Review the output above.${NC}"
        }
    else
        echo -e "${YELLOW}⚠️  Validation script not found. Skipping validation.${NC}"
    fi
    
    echo ""
}

# Main deployment flow
main() {
    echo "Starting TK8S deployment..."
    echo ""
    
    # Pre-deployment checks
    check_prerequisites
    
    # Deploy components in order
    deploy_namespaces
    deploy_rbac
    deploy_network_policies
    deploy_kyverno_policies
    
    # Alternative: use Kustomize for all-in-one deployment
    # deploy_with_kustomize
    
    deploy_argocd_apps
    deploy_monitoring
    
    # Post-deployment checks
    check_status
    run_validation
    
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Deployment Complete!                               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ "$DRY_RUN" = false ]; then
        echo -e "${GREEN}✅ TK8S deployed successfully${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Check ArgoCD applications: kubectl get applications -n argocd"
        echo "  2. Monitor pod status: kubectl get pods -A | grep project-ai"
        echo "  3. Access ArgoCD UI: kubectl port-forward svc/argocd-server -n argocd 8080:443"
        echo "  4. Validate deployment: python validate_tk8s.py"
        echo ""
        echo "Documentation:"
        echo "  - Setup Guide: SETUP_GUIDE.md"
        echo "  - Doctrine: ../../docs/TK8S_DOCTRINE.md"
        echo "  - Timeline: ../../docs/CIVILIZATION_TIMELINE.md"
    else
        echo -e "${BLUE}Dry-run complete. Review the output above.${NC}"
        echo "Run without --dry-run to apply changes."
    fi
    
    echo ""
}

# Run main function
main "$@"
