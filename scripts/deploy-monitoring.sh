#!/bin/bash
# Quick deployment script for Project-AI monitoring stack on Kubernetes
# Deploys Prometheus, Grafana, ELK, Netdata, OpenTelemetry, and Cilium in minutes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${NAMESPACE:-monitoring}
RELEASE_NAME=${RELEASE_NAME:-project-ai-monitoring}
TIMEOUT=${TIMEOUT:-15m}

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Project-AI Monitoring Stack${NC}"
echo -e "${GREEN}Kubernetes + Helm Deployment${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}helm not found. Please install Helm 3.${NC}"
    exit 1
fi

# Check Kubernetes connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Cannot connect to Kubernetes cluster. Check your kubeconfig.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Add Helm repositories
echo -e "${YELLOW}Adding Helm repositories...${NC}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo add elastic https://helm.elastic.co || true
helm repo add netdata https://netdata.github.io/helmchart/ || true
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts || true
helm repo add cilium https://helm.cilium.io/ || true
helm repo add zabbix https://zabbix.github.io/helm-charts || true

echo -e "${YELLOW}Updating repositories...${NC}"
helm repo update

echo -e "${GREEN}✓ Helm repositories configured${NC}"
echo ""

# Create namespace
echo -e "${YELLOW}Creating namespace: ${NAMESPACE}${NC}"
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Namespace ready${NC}"
echo ""

# Check for deployment mode
echo -e "${YELLOW}Select deployment mode:${NC}"
echo "1) Full Stack (Prometheus, Grafana, ELK, Netdata, OpenTelemetry, Cilium)"
echo "2) Minimal (Prometheus + Grafana only)"
echo "3) Production (Full stack with HA and tuning)"
read -r -p "Enter choice [1-3] (default: 1): " DEPLOY_MODE
DEPLOY_MODE=${DEPLOY_MODE:-1}

# Set deployment parameters based on mode
case ${DEPLOY_MODE} in
    1)
        echo -e "${GREEN}Deploying full observability stack...${NC}"
        EXTRA_ARGS=""
        ;;
    2)
        echo -e "${GREEN}Deploying minimal stack (Prometheus + Grafana)...${NC}"
        EXTRA_ARGS="--set prometheus.enabled=true \
                    --set elasticsearch.enabled=false \
                    --set logstash.enabled=false \
                    --set kibana.enabled=false \
                    --set netdata.enabled=false \
                    --set opentelemetry.enabled=false \
                    --set cilium.enabled=false"
        ;;
    3)
        echo -e "${GREEN}Deploying production stack with HA...${NC}"
        EXTRA_ARGS="--set kube-prometheus-stack.prometheus.prometheusSpec.replicas=3 \
                    --set kube-prometheus-stack.alertmanager.alertmanagerSpec.replicas=3 \
                    --set elasticsearch.replicas=5 \
                    --set logstash.replicas=3"
        ;;
    *)
        echo -e "${RED}Invalid choice. Defaulting to full stack.${NC}"
        EXTRA_ARGS=""
        ;;
esac

echo ""

# Deploy the stack
echo -e "${YELLOW}Installing ${RELEASE_NAME} in namespace ${NAMESPACE}...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes...${NC}"
echo ""

if helm install "${RELEASE_NAME}" ./helm/project-ai-monitoring \
    --namespace "${NAMESPACE}" \
    --timeout "${TIMEOUT}" \
    --wait \
    ${EXTRA_ARGS}; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}✓ Deployment Successful!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
else
    echo -e "${RED}Deployment failed. Check the logs above.${NC}"
    exit 1
fi

# Wait for pods to be ready
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=Ready pods --all -n "${NAMESPACE}" --timeout=300s || true

# Display access information
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Access Information${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Get service info
echo -e "${YELLOW}Services:${NC}"
kubectl get svc -n "${NAMESPACE}" | grep -E "NAME|prometheus|grafana|elasticsearch|kibana|netdata|hubble|jaeger"

echo ""
echo -e "${YELLOW}To access services locally, run:${NC}"
echo ""

if [ "${DEPLOY_MODE}" != "2" ]; then
    echo "# Prometheus"
    echo "kubectl port-forward -n ${NAMESPACE} svc/prometheus-kube-prometheus-prometheus 9090:9090 &"
    echo ""
fi

echo "# Grafana"
echo "kubectl port-forward -n ${NAMESPACE} svc/prometheus-grafana 3000:80 &"
GRAFANA_PASS=$(kubectl get secret -n "${NAMESPACE}" prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode)
echo "  URL: http://localhost:3000"
echo "  Username: admin"
echo "  Password: ${GRAFANA_PASS}"
echo ""

if [ "${DEPLOY_MODE}" == "1" ] || [ "${DEPLOY_MODE}" == "3" ]; then
    echo "# Kibana (ELK Stack)"
    echo "kubectl port-forward -n ${NAMESPACE} svc/kibana-kibana 5601:5601 &"
    echo "  URL: http://localhost:5601"
    echo ""
    
    echo "# Hubble UI (eBPF Network Observability)"
    echo "kubectl port-forward -n ${NAMESPACE} svc/cilium-hubble-ui 8080:80 &"
    echo "  URL: http://localhost:8080"
    echo ""
    
    echo "# Netdata (Real-time Performance)"
    echo "kubectl port-forward -n ${NAMESPACE} svc/netdata 19999:19999 &"
    echo "  URL: http://localhost:19999"
    echo ""
    
    echo "# Jaeger UI (Distributed Tracing)"
    echo "kubectl port-forward -n ${NAMESPACE} svc/jaeger-query 16686:16686 &"
    echo "  URL: http://localhost:16686"
    echo ""
fi

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Next Steps${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "1. Access Grafana and explore pre-configured dashboards"
echo "2. View real-time metrics in Prometheus"
if [ "${DEPLOY_MODE}" == "1" ] || [ "${DEPLOY_MODE}" == "3" ]; then
    echo "3. Explore network flows in Hubble UI (eBPF observability)"
    echo "4. Search logs in Kibana (ELK stack)"
    echo "5. Monitor system performance in Netdata"
fi
echo ""
echo "For detailed documentation, see:"
echo "  - docs/PROMETHEUS_INTEGRATION.md"
echo "  - docs/KUBERNETES_MONITORING_GUIDE.md"
echo ""
echo -e "${GREEN}Happy Monitoring! 🚀${NC}"
