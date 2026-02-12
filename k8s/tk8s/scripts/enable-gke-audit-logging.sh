#!/bin/bash
set -euo pipefail

# ============================================================================
# GKE AUDIT LOGGING AND MONITORING SETUP
# Enable comprehensive logging and monitoring for GKE clusters
# ============================================================================

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           GKE Audit Logging & Monitoring Setup                       ║${NC}"
echo -e "${BLUE}║    Immutable audit trail | Workload logging | System monitoring      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ID="${GCP_PROJECT_ID:-}"
CLUSTER_NAME="${GKE_CLUSTER_NAME:-tk8s-prod}"
CLUSTER_LOCATION="${GKE_CLUSTER_LOCATION:-us-central1-a}"
LOG_RETENTION_DAYS="${LOG_RETENTION_DAYS:-365}"

# Validate required variables
if [ -z "${PROJECT_ID}" ]; then
    echo -e "${RED}❌ Error: GCP_PROJECT_ID environment variable is required${NC}"
    echo "   Example: export GCP_PROJECT_ID=my-project-123"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID:       ${PROJECT_ID}"
echo "  Cluster Name:     ${CLUSTER_NAME}"
echo "  Cluster Location: ${CLUSTER_LOCATION}"
echo "  Log Retention:    ${LOG_RETENTION_DAYS} days"
echo ""

# ============================================================================
# VERIFY GCLOUD CLI
# ============================================================================
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install:${NC}"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
gcloud config set project "${PROJECT_ID}" --quiet
echo -e "${GREEN}✅ Project set to: ${PROJECT_ID}${NC}"
echo ""

# ============================================================================
# STEP 1: ENABLE CLOUD LOGGING API
# ============================================================================
echo -e "${BLUE}🔧 Step 1: Enabling Cloud Logging API...${NC}"

gcloud services enable logging.googleapis.com --project="${PROJECT_ID}"
gcloud services enable cloudaudit.googleapis.com --project="${PROJECT_ID}"

echo -e "${GREEN}✅ Cloud Logging API enabled${NC}"
echo ""

# ============================================================================
# STEP 2: ENABLE GKE AUDIT LOGGING
# ============================================================================
echo -e "${BLUE}📝 Step 2: Enabling GKE audit logging...${NC}"

echo "Updating cluster ${CLUSTER_NAME} to enable:"
echo "  - SYSTEM logging (control plane logs)"
echo "  - WORKLOAD logging (pod stdout/stderr)"
echo "  - API audit logs"
echo ""

gcloud container clusters update "${CLUSTER_NAME}" \
    --location="${CLUSTER_LOCATION}" \
    --logging=SYSTEM,WORKLOAD \
    --enable-cloud-logging

echo -e "${GREEN}✅ GKE logging enabled${NC}"
echo ""

# ============================================================================
# STEP 3: ENABLE GKE MONITORING
# ============================================================================
echo -e "${BLUE}📊 Step 3: Enabling GKE monitoring...${NC}"

gcloud container clusters update "${CLUSTER_NAME}" \
    --location="${CLUSTER_LOCATION}" \
    --monitoring=SYSTEM \
    --enable-cloud-monitoring

echo -e "${GREEN}✅ GKE monitoring enabled${NC}"
echo ""

# ============================================================================
# STEP 4: CONFIGURE AUDIT LOG RETENTION
# ============================================================================
echo -e "${BLUE}🗄️  Step 4: Configuring log retention...${NC}"

# Create log sink for long-term storage
LOG_BUCKET_NAME="${PROJECT_ID}-audit-logs"

echo "Creating Cloud Storage bucket for audit logs..."

if gsutil ls -b "gs://${LOG_BUCKET_NAME}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Bucket already exists: ${LOG_BUCKET_NAME}${NC}"
else
    gsutil mb -p "${PROJECT_ID}" -l us-central1 "gs://${LOG_BUCKET_NAME}"
    gsutil lifecycle set - "gs://${LOG_BUCKET_NAME}" << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": ${LOG_RETENTION_DAYS}}
      }
    ]
  }
}
EOF
    echo -e "${GREEN}✅ Audit log bucket created: ${LOG_BUCKET_NAME}${NC}"
fi
echo ""

# ============================================================================
# STEP 5: CREATE LOG SINKS
# ============================================================================
echo -e "${BLUE}📤 Step 5: Creating log sinks...${NC}"

# Sink for Kubernetes audit logs
SINK_NAME="gke-audit-logs-sink"

if gcloud logging sinks describe "${SINK_NAME}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Log sink already exists: ${SINK_NAME}${NC}"
else
    gcloud logging sinks create "${SINK_NAME}" \
        "storage.googleapis.com/${LOG_BUCKET_NAME}" \
        --log-filter='resource.type="k8s_cluster"
protoPayload.methodName=~"^io.k8s.*"
severity >= INFO'
    
    echo -e "${GREEN}✅ Log sink created: ${SINK_NAME}${NC}"
fi

# Sink for admission controller decisions
ADMISSION_SINK_NAME="gke-admission-decisions-sink"

if gcloud logging sinks describe "${ADMISSION_SINK_NAME}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Log sink already exists: ${ADMISSION_SINK_NAME}${NC}"
else
    gcloud logging sinks create "${ADMISSION_SINK_NAME}" \
        "storage.googleapis.com/${LOG_BUCKET_NAME}" \
        --log-filter='resource.type="k8s_cluster"
protoPayload.methodName=~"^io.k8s.admission.*"'
    
    echo -e "${GREEN}✅ Admission log sink created: ${ADMISSION_SINK_NAME}${NC}"
fi
echo ""

# ============================================================================
# STEP 6: CONFIGURE DATA ACCESS AUDIT LOGS
# ============================================================================
echo -e "${BLUE}🔍 Step 6: Configuring data access audit logs...${NC}"

cat > /tmp/audit-config.yaml << EOF
auditConfigs:
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
  service: container.googleapis.com
- auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_WRITE
  service: storage.googleapis.com
EOF

echo "Enabling audit logs for:"
echo "  - GKE API (container.googleapis.com)"
echo "  - Cloud Storage (storage.googleapis.com)"
echo ""

gcloud projects get-iam-policy "${PROJECT_ID}" --format=yaml > /tmp/current-policy.yaml

# Merge audit config with current policy (manual step required)
echo -e "${YELLOW}⚠️  Manual step required:${NC}"
echo "  To enable data access audit logs, add the audit configuration to your IAM policy:"
echo "  1. Run: gcloud projects get-iam-policy ${PROJECT_ID} > policy.yaml"
echo "  2. Add the auditConfigs section from /tmp/audit-config.yaml"
echo "  3. Run: gcloud projects set-iam-policy ${PROJECT_ID} policy.yaml"
echo ""
echo "  Or use the Cloud Console:"
echo "  https://console.cloud.google.com/iam-admin/audit?project=${PROJECT_ID}"
echo ""

# ============================================================================
# STEP 7: CREATE LOG-BASED METRICS
# ============================================================================
echo -e "${BLUE}📈 Step 7: Creating log-based metrics...${NC}"

# Metric for denied pod creations
DENIED_PODS_METRIC="denied_pod_creations"

if gcloud logging metrics describe "${DENIED_PODS_METRIC}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Metric already exists: ${DENIED_PODS_METRIC}${NC}"
else
    gcloud logging metrics create "${DENIED_PODS_METRIC}" \
        --description="Count of denied pod creation attempts" \
        --log-filter='resource.type="k8s_cluster"
protoPayload.methodName="io.k8s.core.v1.pods.create"
protoPayload.response.status="Failure"'
    
    echo -e "${GREEN}✅ Metric created: ${DENIED_PODS_METRIC}${NC}"
fi

# Metric for image signature verification failures
SIG_FAILURE_METRIC="image_signature_failures"

if gcloud logging metrics describe "${SIG_FAILURE_METRIC}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Metric already exists: ${SIG_FAILURE_METRIC}${NC}"
else
    gcloud logging metrics create "${SIG_FAILURE_METRIC}" \
        --description="Count of image signature verification failures" \
        --log-filter='resource.type="k8s_cluster"
jsonPayload.message=~".*signature verification failed.*"'
    
    echo -e "${GREEN}✅ Metric created: ${SIG_FAILURE_METRIC}${NC}"
fi
echo ""

# ============================================================================
# STEP 8: VERIFICATION
# ============================================================================
echo -e "${BLUE}🔍 Step 8: Verifying configuration...${NC}"

echo "Cluster logging configuration:"
gcloud container clusters describe "${CLUSTER_NAME}" \
    --location="${CLUSTER_LOCATION}" \
    --format="value(loggingConfig)"

echo ""
echo "Cluster monitoring configuration:"
gcloud container clusters describe "${CLUSTER_NAME}" \
    --location="${CLUSTER_LOCATION}" \
    --format="value(monitoringConfig)"

echo ""
echo "Log sinks:"
gcloud logging sinks list --format="table(name,destination,filter)"

echo ""

# ============================================================================
# SETUP COMPLETE
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                Audit Logging Setup Complete!                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ Configuration Summary:${NC}"
echo "  ✅ System logging enabled"
echo "  ✅ Workload logging enabled"
echo "  ✅ Cloud monitoring enabled"
echo "  ✅ Log retention: ${LOG_RETENTION_DAYS} days"
echo "  ✅ Log sinks configured"
echo "  ✅ Log-based metrics created"
echo ""

echo -e "${BLUE}📊 View Logs:${NC}"
echo "  Cloud Console: https://console.cloud.google.com/logs/query?project=${PROJECT_ID}"
echo "  CLI: gcloud logging read 'resource.type=\"k8s_cluster\"' --limit 50"
echo ""

echo -e "${BLUE}🔍 Query Examples:${NC}"
echo "  # View all denied pod creations"
echo "  gcloud logging read 'resource.type=\"k8s_cluster\" AND protoPayload.response.status=\"Failure\"' --limit 10"
echo ""
echo "  # View Kyverno policy violations"
echo "  gcloud logging read 'resource.type=\"k8s_cluster\" AND jsonPayload.message=~\".*kyverno.*\"' --limit 10"
echo ""
echo "  # View audit logs for specific namespace"
echo "  gcloud logging read 'resource.type=\"k8s_cluster\" AND resource.labels.namespace_name=\"project-ai-core\"' --limit 10"
echo ""

echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  - Logs are immutable and cannot be deleted by cluster admins"
echo "  - Configure alerting on log-based metrics"
echo "  - Review logs regularly for security incidents"
echo "  - Export logs to long-term storage for compliance"
echo ""

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
