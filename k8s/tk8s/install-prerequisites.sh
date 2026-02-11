#!/bin/bash
set -euo pipefail

# TK8S Prerequisites Installation Script
# Installs ArgoCD, Kyverno, and required tools

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         TK8S Prerequisites Installation Script                      ║${NC}"
echo -e "${BLUE}║    Thirsty's Kubernetes - Civilization Grade Infrastructure         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running with proper permissions
if [[ $EUID -eq 0 ]]; then
   echo -e "${YELLOW}⚠️  Warning: Running as root. This script should be run as a regular user with kubectl access.${NC}"
fi

# Check kubectl connection
check_kubectl() {
    echo -e "${BLUE}📋 Checking kubectl connection...${NC}"
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
        echo "   Install: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster. Please configure kubectl.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ kubectl connected to cluster${NC}"
    kubectl cluster-info | head -2
    echo ""
}

# Check helm installation
check_helm() {
    echo -e "${BLUE}📋 Checking Helm installation...${NC}"
    if ! command -v helm &> /dev/null; then
        echo -e "${YELLOW}⚠️  Helm not found. Installing Helm...${NC}"
        curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
        echo -e "${GREEN}✅ Helm installed${NC}"
    else
        echo -e "${GREEN}✅ Helm already installed: $(helm version --short)${NC}"
    fi
    echo ""
}

# Check cosign installation
check_cosign() {
    echo -e "${BLUE}📋 Checking Cosign installation...${NC}"
    if ! command -v cosign &> /dev/null; then
        echo -e "${YELLOW}⚠️  Cosign not found. Installing Cosign...${NC}"
        
        # Detect OS and architecture
        OS=$(uname -s | tr '[:upper:]' '[:lower:]')
        ARCH=$(uname -m)
        if [ "$ARCH" = "x86_64" ]; then
            ARCH="amd64"
        elif [ "$ARCH" = "aarch64" ]; then
            ARCH="arm64"
        fi
        
        # Download and install cosign
        COSIGN_VERSION="v2.2.2"
        curl -Lo cosign "https://github.com/sigstore/cosign/releases/download/${COSIGN_VERSION}/cosign-${OS}-${ARCH}"
        chmod +x cosign
        sudo mv cosign /usr/local/bin/ 2>/dev/null || mv cosign ~/bin/
        
        echo -e "${GREEN}✅ Cosign installed${NC}"
    else
        echo -e "${GREEN}✅ Cosign already installed: $(cosign version 2>&1 | head -1)${NC}"
    fi
    echo ""
}

# Check syft installation
check_syft() {
    echo -e "${BLUE}📋 Checking Syft installation...${NC}"
    if ! command -v syft &> /dev/null; then
        echo -e "${YELLOW}⚠️  Syft not found. Installing Syft...${NC}"
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin 2>/dev/null || \
        curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b ~/bin
        echo -e "${GREEN}✅ Syft installed${NC}"
    else
        echo -e "${GREEN}✅ Syft already installed: $(syft version | head -1)${NC}"
    fi
    echo ""
}

# Install ArgoCD
install_argocd() {
    echo -e "${BLUE}🚀 Installing ArgoCD...${NC}"
    
    # Check if ArgoCD is already installed
    if kubectl get namespace argocd &> /dev/null; then
        echo -e "${YELLOW}⚠️  ArgoCD namespace already exists. Checking deployment...${NC}"
        if kubectl get deployment argocd-server -n argocd &> /dev/null; then
            echo -e "${GREEN}✅ ArgoCD already installed${NC}"
            return 0
        fi
    fi
    
    # Create ArgoCD namespace
    echo "  Creating argocd namespace..."
    kubectl create namespace argocd 2>/dev/null || true
    
    # Install ArgoCD
    echo "  Installing ArgoCD manifests..."
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    # Wait for ArgoCD to be ready
    echo "  Waiting for ArgoCD to be ready (timeout: 5 minutes)..."
    kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd || {
        echo -e "${YELLOW}⚠️  ArgoCD deployment may still be starting. Check status with: kubectl get pods -n argocd${NC}"
    }
    
    echo -e "${GREEN}✅ ArgoCD installed successfully${NC}"
    echo ""
    
    # Get admin password
    echo -e "${BLUE}📝 ArgoCD Admin Credentials:${NC}"
    echo "  Username: admin"
    echo -n "  Password: "
    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" 2>/dev/null | base64 -d || echo "(password not yet available)"
    echo ""
    echo ""
    
    echo -e "${BLUE}📝 To access ArgoCD UI:${NC}"
    echo "  Port-forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
    echo "  Access: https://localhost:8080"
    echo ""
}

# Install Kyverno
install_kyverno() {
    echo -e "${BLUE}🚀 Installing Kyverno...${NC}"
    
    # Check if Kyverno is already installed
    if kubectl get namespace kyverno &> /dev/null; then
        echo -e "${YELLOW}⚠️  Kyverno namespace already exists. Checking deployment...${NC}"
        if kubectl get deployment kyverno -n kyverno &> /dev/null; then
            echo -e "${GREEN}✅ Kyverno already installed${NC}"
            return 0
        fi
    fi
    
    # Add Kyverno Helm repo
    echo "  Adding Kyverno Helm repository..."
    helm repo add kyverno https://kyverno.github.io/kyverno/ 2>/dev/null || true
    helm repo update
    
    # Install Kyverno
    echo "  Installing Kyverno via Helm..."
    helm install kyverno kyverno/kyverno -n kyverno --create-namespace --wait --timeout 300s || {
        echo -e "${YELLOW}⚠️  Kyverno installation may still be in progress. Check status with: kubectl get pods -n kyverno${NC}"
    }
    
    # Wait for Kyverno to be ready
    echo "  Waiting for Kyverno to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/kyverno -n kyverno || {
        echo -e "${YELLOW}⚠️  Kyverno deployment may still be starting.${NC}"
    }
    
    echo -e "${GREEN}✅ Kyverno installed successfully${NC}"
    echo ""
}

# Verify installations
verify_installations() {
    echo -e "${BLUE}🔍 Verifying installations...${NC}"
    echo ""
    
    echo "ArgoCD Pods:"
    kubectl get pods -n argocd --no-headers 2>/dev/null || echo "  Not available"
    echo ""
    
    echo "Kyverno Pods:"
    kubectl get pods -n kyverno --no-headers 2>/dev/null || echo "  Not available"
    echo ""
    
    echo -e "${GREEN}✅ Verification complete${NC}"
    echo ""
}

# Main execution
main() {
    echo "Starting TK8S prerequisites installation..."
    echo ""
    
    # Check prerequisites
    check_kubectl
    check_helm
    check_cosign
    check_syft
    
    # Install components
    install_argocd
    install_kyverno
    
    # Verify
    verify_installations
    
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                   Installation Complete!                            ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✅ All prerequisites installed successfully${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Generate Cosign keys: ./generate-cosign-keys.sh"
    echo "  2. Deploy TK8S: ./deploy-tk8s.sh"
    echo "  3. Validate: python validate_tk8s.py"
    echo ""
}

# Run main function
main "$@"
