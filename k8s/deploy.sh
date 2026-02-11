#!/bin/bash
set -euo pipefail

# Kubernetes Deployment Script for Project-AI
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh production deploy

ENVIRONMENT="${1:-dev}"
ACTION="${2:-deploy}"
NAMESPACE="project-ai-${ENVIRONMENT}"

echo "🚀 Project-AI Kubernetes Deployment"
echo "Environment: ${ENVIRONMENT}"
echo "Action: ${ACTION}"
echo "Namespace: ${NAMESPACE}"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl not found. Please install kubectl.${NC}"
        exit 1
    fi
    
    if ! command -v kustomize &> /dev/null; then
        echo -e "${YELLOW}⚠️  kustomize not found. Installing...${NC}"
        curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
        sudo mv kustomize /usr/local/bin/
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Deploy using Kustomize
deploy_kustomize() {
    echo "🔧 Deploying with Kustomize..."
    
    if [ ! -d "k8s/overlays/${ENVIRONMENT}" ]; then
        echo -e "${RED}❌ Environment ${ENVIRONMENT} not found${NC}"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply kustomization
    kustomize build "k8s/overlays/${ENVIRONMENT}" | kubectl apply -f -
    
    echo -e "${GREEN}✅ Deployment completed${NC}"
}

# Deploy using Helm
deploy_helm() {
    echo "🔧 Deploying with Helm..."
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        echo -e "${RED}❌ helm not found. Please install helm.${NC}"
        exit 1
    fi
    
    # Values file for the environment
    VALUES_FILE="helm/project-ai/values-${ENVIRONMENT}.yaml"
    if [ ! -f "${VALUES_FILE}" ]; then
        VALUES_FILE="helm/project-ai/values.yaml"
    fi
    
    # Create namespace
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
    
    # Install or upgrade
    helm upgrade --install "project-ai-${ENVIRONMENT}" \
        ./helm/project-ai \
        --namespace "${NAMESPACE}" \
        --values "${VALUES_FILE}" \
        --timeout 10m \
        --wait
    
    echo -e "${GREEN}✅ Helm deployment completed${NC}"
}

# Rollback deployment
rollback() {
    echo "🔄 Rolling back deployment..."
    
    kubectl rollout undo deployment/project-ai-app -n "${NAMESPACE}"
    kubectl rollout status deployment/project-ai-app -n "${NAMESPACE}"
    
    echo -e "${GREEN}✅ Rollback completed${NC}"
}

# Check deployment status
status() {
    echo "📊 Checking deployment status..."
    
    kubectl get all -n "${NAMESPACE}"
    echo ""
    
    echo "🔍 Pod status:"
    kubectl get pods -n "${NAMESPACE}" -o wide
    echo ""
    
    echo "🔍 Service status:"
    kubectl get svc -n "${NAMESPACE}"
    echo ""
    
    echo "🔍 Ingress status:"
    kubectl get ingress -n "${NAMESPACE}"
}

# Run smoke tests
smoke_test() {
    echo "🧪 Running smoke tests..."
    
    # Get service endpoint
    SERVICE_URL=$(kubectl get ingress -n "${NAMESPACE}" -o jsonpath='{.items[0].spec.rules[0].host}')
    
    if [ -z "${SERVICE_URL}" ]; then
        echo -e "${YELLOW}⚠️  Ingress not configured, using port-forward${NC}"
        kubectl port-forward -n "${NAMESPACE}" svc/project-ai 8080:80 &
        PF_PID=$!
        sleep 5
        SERVICE_URL="localhost:8080"
    fi
    
    echo "Testing endpoint: ${SERVICE_URL}"
    
    # Health check
    if curl -f "http://${SERVICE_URL}/health/live" &> /dev/null; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
        [ ! -z "${PF_PID:-}" ] && kill "${PF_PID}"
        exit 1
    fi
    
    # Kill port-forward if used
    [ ! -z "${PF_PID:-}" ] && kill "${PF_PID}"
    
    echo -e "${GREEN}✅ Smoke tests passed${NC}"
}

# Cleanup resources
cleanup() {
    echo "🧹 Cleaning up resources..."
    
    read -p "Are you sure you want to delete all resources in ${NAMESPACE}? (yes/no): " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        echo "Cleanup cancelled"
        exit 0
    fi
    
    kubectl delete namespace "${NAMESPACE}" --wait=true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main execution
main() {
    check_prerequisites
    
    case "${ACTION}" in
        deploy)
            deploy_kustomize
            status
            ;;
        helm)
            deploy_helm
            status
            ;;
        rollback)
            rollback
            ;;
        status)
            status
            ;;
        test)
            smoke_test
            ;;
        cleanup)
            cleanup
            ;;
        *)
            echo "Usage: $0 [environment] [action]"
            echo "Environments: dev, staging, production"
            echo "Actions: deploy, helm, rollback, status, test, cleanup"
            exit 1
            ;;
    esac
}

main
