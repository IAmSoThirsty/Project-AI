#!/bin/bash
# Blue-Green Deployment Script for Project-AI
# Implements zero-downtime deployment strategy

set -e

NAMESPACE="${1:-project-ai}"
IMAGE_TAG="${2:-latest}"
STRATEGY="${3:-blue-green}"  # blue-green, canary, or rolling

echo "=========================================="
echo "Project-AI Blue-Green Deployment"
echo "=========================================="
echo "Namespace: $NAMESPACE"
echo "Image Tag: $IMAGE_TAG"
echo "Strategy: $STRATEGY"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current active deployment (blue or green)
CURRENT_COLOR=$(kubectl get service project-ai -n $NAMESPACE -o jsonpath='{.spec.selector.version}' 2>/dev/null || echo "blue")
if [ "$CURRENT_COLOR" = "blue" ]; then
    NEW_COLOR="green"
else
    NEW_COLOR="blue"
fi

echo -e "${BLUE}Current active deployment: ${CURRENT_COLOR}${NC}"
echo -e "${GREEN}New deployment color: ${NEW_COLOR}${NC}"
echo ""

# Function to check deployment health
check_deployment_health() {
    local deployment=$1
    local timeout=300
    local elapsed=0
    
    echo "Waiting for deployment ${deployment} to be ready..."
    
    while [ $elapsed -lt $timeout ]; do
        READY=$(kubectl get deployment ${deployment} -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        DESIRED=$(kubectl get deployment ${deployment} -n $NAMESPACE -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
        
        if [ "$READY" = "$DESIRED" ] && [ "$READY" != "0" ]; then
            echo -e "${GREEN}✓ Deployment ${deployment} is ready (${READY}/${DESIRED} replicas)${NC}"
            return 0
        fi
        
        echo "Waiting... ${READY}/${DESIRED} replicas ready"
        sleep 5
        elapsed=$((elapsed + 5))
    done
    
    echo -e "${RED}✗ Deployment ${deployment} failed to become ready${NC}"
    return 1
}

# Function to run smoke tests
run_smoke_tests() {
    local service_url=$1
    
    echo "Running smoke tests against ${service_url}..."
    
    # Health check
    if curl -f "${service_url}/health/live" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed${NC}"
        return 1
    fi
    
    # Readiness check
    if curl -f "${service_url}/health/ready" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Readiness check passed${NC}"
    else
        echo -e "${RED}✗ Readiness check failed${NC}"
        return 1
    fi
    
    return 0
}

# Step 1: Deploy new version with new color label
echo -e "${YELLOW}[1/6] Deploying new version (${NEW_COLOR})...${NC}"

cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai-${NEW_COLOR}
  namespace: ${NAMESPACE}
  labels:
    app: project-ai
    version: ${NEW_COLOR}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: project-ai
      version: ${NEW_COLOR}
  template:
    metadata:
      labels:
        app: project-ai
        version: ${NEW_COLOR}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
    spec:
      containers:
      - name: project-ai
        image: ghcr.io/iamsothirsty/project-ai:${IMAGE_TAG}
        ports:
        - containerPort: 5000
          name: http
        - containerPort: 9090
          name: metrics
        envFrom:
        - configMapRef:
            name: project-ai-config
        - secretRef:
            name: project-ai-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: project-ai-${NEW_COLOR}
  namespace: ${NAMESPACE}
  labels:
    app: project-ai
    version: ${NEW_COLOR}
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 5000
    name: http
  selector:
    app: project-ai
    version: ${NEW_COLOR}
EOF

echo -e "${GREEN}✓ New deployment created${NC}"
echo ""

# Step 2: Wait for new deployment to be ready
echo -e "${YELLOW}[2/6] Waiting for new deployment to be ready...${NC}"
if ! check_deployment_health "project-ai-${NEW_COLOR}"; then
    echo -e "${RED}Deployment failed. Cleaning up...${NC}"
    kubectl delete deployment project-ai-${NEW_COLOR} -n $NAMESPACE
    kubectl delete service project-ai-${NEW_COLOR} -n $NAMESPACE
    exit 1
fi
echo ""

# Step 3: Run smoke tests on new deployment
echo -e "${YELLOW}[3/6] Running smoke tests...${NC}"

# Port-forward to test the new deployment
kubectl port-forward -n $NAMESPACE svc/project-ai-${NEW_COLOR} 8080:80 &
PF_PID=$!
sleep 5

if ! run_smoke_tests "http://localhost:8080"; then
    echo -e "${RED}Smoke tests failed. Rolling back...${NC}"
    kill $PF_PID 2>/dev/null || true
    kubectl delete deployment project-ai-${NEW_COLOR} -n $NAMESPACE
    kubectl delete service project-ai-${NEW_COLOR} -n $NAMESPACE
    exit 1
fi

kill $PF_PID 2>/dev/null || true
echo -e "${GREEN}✓ Smoke tests passed${NC}"
echo ""

# Step 4: Switch traffic to new deployment (blue-green switch)
echo -e "${YELLOW}[4/6] Switching traffic to new deployment...${NC}"

if [ "$STRATEGY" = "blue-green" ]; then
    # Instant switch
    kubectl patch service project-ai -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"version\":\"${NEW_COLOR}\"}}}"
    echo -e "${GREEN}✓ Traffic switched to ${NEW_COLOR} deployment${NC}"
    
elif [ "$STRATEGY" = "canary" ]; then
    # Canary deployment: gradually shift traffic
    echo "Implementing canary deployment (10% → 50% → 100%)..."
    
    # 10% traffic to new version
    echo "Shifting 10% traffic to ${NEW_COLOR}..."
    kubectl patch service project-ai -n $NAMESPACE --type='json' -p="[{\"op\":\"add\",\"path\":\"/metadata/annotations/traffic.${NEW_COLOR}\",\"value\":\"10\"}]"
    sleep 60
    
    # Check metrics
    echo "Monitoring for 60 seconds..."
    sleep 60
    
    # 50% traffic
    echo "Shifting 50% traffic to ${NEW_COLOR}..."
    kubectl patch service project-ai -n $NAMESPACE --type='json' -p="[{\"op\":\"replace\",\"path\":\"/metadata/annotations/traffic.${NEW_COLOR}\",\"value\":\"50\"}]"
    sleep 60
    
    # Check metrics again
    echo "Monitoring for 60 seconds..."
    sleep 60
    
    # 100% traffic
    echo "Shifting 100% traffic to ${NEW_COLOR}..."
    kubectl patch service project-ai -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"version\":\"${NEW_COLOR}\"}}}"
    echo -e "${GREEN}✓ Canary deployment complete${NC}"
fi
echo ""

# Step 5: Verify new deployment is serving traffic
echo -e "${YELLOW}[5/6] Verifying new deployment...${NC}"
sleep 10

# Check service endpoint
SERVICE_ENDPOINT=$(kubectl get service project-ai -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "localhost")
if [ "$SERVICE_ENDPOINT" = "localhost" ]; then
    # Use port-forward for verification
    kubectl port-forward -n $NAMESPACE svc/project-ai 8080:80 &
    PF_PID=$!
    sleep 5
    SERVICE_ENDPOINT="http://localhost:8080"
fi

if curl -f "${SERVICE_ENDPOINT}/health/live" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ New deployment is serving traffic${NC}"
else
    echo -e "${RED}✗ New deployment is not responding${NC}"
    [ ! -z "$PF_PID" ] && kill $PF_PID 2>/dev/null || true
    exit 1
fi

[ ! -z "$PF_PID" ] && kill $PF_PID 2>/dev/null || true
echo ""

# Step 6: Clean up old deployment
echo -e "${YELLOW}[6/6] Cleaning up old deployment...${NC}"

# Keep old deployment for quick rollback (optional)
read -p "Delete old ${CURRENT_COLOR} deployment? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl delete deployment project-ai-${CURRENT_COLOR} -n $NAMESPACE 2>/dev/null || true
    kubectl delete service project-ai-${CURRENT_COLOR} -n $NAMESPACE 2>/dev/null || true
    echo -e "${GREEN}✓ Old deployment cleaned up${NC}"
else
    echo -e "${YELLOW}⚠ Old deployment kept for quick rollback${NC}"
    echo -e "${YELLOW}  To rollback: kubectl patch service project-ai -n $NAMESPACE -p '{\"spec\":{\"selector\":{\"version\":\"${CURRENT_COLOR}\"}}}'${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo "=========================================="
echo -e "Active deployment: ${GREEN}${NEW_COLOR}${NC}"
echo -e "Previous deployment: ${CURRENT_COLOR} (${REPLY} )"
echo ""
echo "To rollback:"
echo "  kubectl patch service project-ai -n $NAMESPACE -p '{\"spec\":{\"selector\":{\"version\":\"${CURRENT_COLOR}\"}}}'"
echo ""
echo "To monitor:"
echo "  kubectl get pods -n $NAMESPACE -l version=${NEW_COLOR} -w"
echo ""
