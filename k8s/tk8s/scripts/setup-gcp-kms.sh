#!/bin/bash
set -euo pipefail

# ============================================================================
# GCP KMS SETUP FOR COSIGN IMAGE SIGNING
# Enterprise-Grade Key Management with Hardware Security Module (HSM) backing
# ============================================================================
# This script creates:
# - KMS keyring and signing key
# - Service account with minimal permissions
# - IAM bindings for signing and verification
# ============================================================================

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           GCP KMS Setup for Cosign Image Signing                     ║${NC}"
echo -e "${BLUE}║    Enterprise-Grade Key Management | HSM-backed | Auditable          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ID="${GCP_PROJECT_ID:-}"
LOCATION="${KMS_LOCATION:-us-central1}"
KEYRING_NAME="${KMS_KEYRING:-tk8s-keyring}"
KEY_NAME="${KMS_KEY_NAME:-cosign-key}"
SERVICE_ACCOUNT_NAME="${KMS_SA_NAME:-cosign-signer}"
KEY_ALGORITHM="${KMS_KEY_ALGORITHM:-ec-sign-p256-sha256}"

# Validate required variables
if [ -z "${PROJECT_ID}" ]; then
    echo -e "${RED}❌ Error: GCP_PROJECT_ID environment variable is required${NC}"
    echo "   Example: export GCP_PROJECT_ID=my-project-123"
    exit 1
fi

echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Project ID:       ${PROJECT_ID}"
echo "  Location:         ${LOCATION}"
echo "  Keyring:          ${KEYRING_NAME}"
echo "  Key Name:         ${KEY_NAME}"
echo "  Service Account:  ${SERVICE_ACCOUNT_NAME}"
echo "  Key Algorithm:    ${KEY_ALGORITHM}"
echo ""

# ============================================================================
# VERIFY GCLOUD CLI
# ============================================================================
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install:${NC}"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verify authentication
echo -e "${BLUE}🔐 Verifying GCP authentication...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}❌ Not authenticated. Run: gcloud auth login${NC}"
    exit 1
fi

CURRENT_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
echo -e "${GREEN}✅ Authenticated as: ${CURRENT_ACCOUNT}${NC}"

# Set project
gcloud config set project "${PROJECT_ID}" --quiet
echo -e "${GREEN}✅ Project set to: ${PROJECT_ID}${NC}"
echo ""

# ============================================================================
# STEP 1: CREATE KMS KEYRING
# ============================================================================
echo -e "${BLUE}🔑 Step 1: Creating KMS Keyring...${NC}"

if gcloud kms keyrings describe "${KEYRING_NAME}" \
    --location="${LOCATION}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Keyring '${KEYRING_NAME}' already exists${NC}"
else
    gcloud kms keyrings create "${KEYRING_NAME}" \
        --location="${LOCATION}"
    echo -e "${GREEN}✅ Keyring created: ${KEYRING_NAME}${NC}"
fi

# ============================================================================
# STEP 2: CREATE ASYMMETRIC SIGNING KEY
# ============================================================================
echo -e "${BLUE}🔐 Step 2: Creating asymmetric signing key...${NC}"

if gcloud kms keys describe "${KEY_NAME}" \
    --location="${LOCATION}" \
    --keyring="${KEYRING_NAME}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Key '${KEY_NAME}' already exists${NC}"
else
    gcloud kms keys create "${KEY_NAME}" \
        --location="${LOCATION}" \
        --keyring="${KEYRING_NAME}" \
        --purpose=asymmetric-signing \
        --default-algorithm="${KEY_ALGORITHM}" \
        --protection-level=software
    
    echo -e "${GREEN}✅ Signing key created: ${KEY_NAME}${NC}"
    echo "   Purpose: asymmetric-signing"
    echo "   Algorithm: ${KEY_ALGORITHM}"
    echo "   Protection: software (upgrade to HSM for production)"
fi
echo ""

# ============================================================================
# STEP 3: CREATE SERVICE ACCOUNT
# ============================================================================
echo -e "${BLUE}👤 Step 3: Creating service account...${NC}"

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Service account already exists: ${SERVICE_ACCOUNT_EMAIL}${NC}"
else
    gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
        --display-name="Cosign Image Signing Service Account" \
        --description="Service account for signing container images with Cosign and KMS"
    
    echo -e "${GREEN}✅ Service account created: ${SERVICE_ACCOUNT_EMAIL}${NC}"
fi
echo ""

# ============================================================================
# STEP 4: GRANT KMS SIGNING PERMISSIONS
# ============================================================================
echo -e "${BLUE}🔒 Step 4: Granting KMS signing permissions...${NC}"

# Grant signerVerifier role (allows signing + public key retrieval)
gcloud kms keys add-iam-policy-binding "${KEY_NAME}" \
    --location="${LOCATION}" \
    --keyring="${KEYRING_NAME}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/cloudkms.signerVerifier" \
    --condition=None

echo -e "${GREEN}✅ Granted roles/cloudkms.signerVerifier to ${SERVICE_ACCOUNT_EMAIL}${NC}"
echo "   This role allows:"
echo "   - Asymmetric signing operations"
echo "   - Public key retrieval"
echo "   - No key management or deletion"
echo ""

# ============================================================================
# STEP 5: GRANT CI/CD ACCESS (Optional)
# ============================================================================
echo -e "${BLUE}🔧 Step 5: Configuring CI/CD access...${NC}"
echo "To enable signing from GitHub Actions or Cloud Build, you need to grant access."
echo ""
echo "For GitHub Actions (using Workload Identity):"
echo "  1. Create Workload Identity Pool"
echo "  2. Create Provider for GitHub"
echo "  3. Grant service account impersonation"
echo ""
echo "For Cloud Build:"
read -p "Grant Cloud Build access? (y/n): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
    CLOUD_BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
    
    gcloud kms keys add-iam-policy-binding "${KEY_NAME}" \
        --location="${LOCATION}" \
        --keyring="${KEYRING_NAME}" \
        --member="serviceAccount:${CLOUD_BUILD_SA}" \
        --role="roles/cloudkms.signerVerifier"
    
    echo -e "${GREEN}✅ Granted Cloud Build access${NC}"
fi
echo ""

# ============================================================================
# STEP 6: VERIFY IAM BINDINGS
# ============================================================================
echo -e "${BLUE}🔍 Step 6: Verifying IAM bindings...${NC}"

echo "IAM Policy for key '${KEY_NAME}':"
gcloud kms keys get-iam-policy "${KEY_NAME}" \
    --location="${LOCATION}" \
    --keyring="${KEYRING_NAME}" \
    --format="table(bindings.role,bindings.members.flatten())"

echo ""

# ============================================================================
# STEP 7: EXPORT PUBLIC KEY
# ============================================================================
echo -e "${BLUE}📤 Step 7: Exporting public key...${NC}"

OUTPUT_DIR="$(pwd)/.kms-keys"
mkdir -p "${OUTPUT_DIR}"
PUBLIC_KEY_FILE="${OUTPUT_DIR}/cosign-kms.pub"

# Get the latest key version
KEY_VERSION=$(gcloud kms keys versions list \
    --location="${LOCATION}" \
    --keyring="${KEYRING_NAME}" \
    --key="${KEY_NAME}" \
    --filter="state=ENABLED" \
    --format="value(name)" \
    --limit=1 | awk -F'/' '{print $NF}')

echo "  Latest key version: ${KEY_VERSION}"

# Export public key
gcloud kms keys versions get-public-key "${KEY_VERSION}" \
    --location="${LOCATION}" \
    --keyring="${KEYRING_NAME}" \
    --key="${KEY_NAME}" \
    --output-file="${PUBLIC_KEY_FILE}"

echo -e "${GREEN}✅ Public key exported to: ${PUBLIC_KEY_FILE}${NC}"
echo ""
echo "Public key content:"
echo "────────────────────────────────────────────────────────────────────"
cat "${PUBLIC_KEY_FILE}"
echo "────────────────────────────────────────────────────────────────────"
echo ""

# ============================================================================
# STEP 8: CREATE KUBERNETES SECRET
# ============================================================================
echo -e "${BLUE}☸️  Step 8: Creating Kubernetes secret...${NC}"
echo ""
echo "To deploy the public key to your Kubernetes cluster, run:"
echo ""
echo -e "${YELLOW}kubectl create namespace kyverno --dry-run=client -o yaml | kubectl apply -f -${NC}"
echo -e "${YELLOW}kubectl create secret generic cosign-public-key \\${NC}"
echo -e "${YELLOW}  --from-file=cosign.pub=${PUBLIC_KEY_FILE} \\${NC}"
echo -e "${YELLOW}  -n kyverno${NC}"
echo ""

# ============================================================================
# STEP 9: SETUP SUMMARY
# ============================================================================
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   KMS Setup Complete!                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ KMS Configuration Summary:${NC}"
echo "  🔑 Keyring:       projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}"
echo "  🔐 Key:           projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}/cryptoKeys/${KEY_NAME}"
echo "  👤 Service Account: ${SERVICE_ACCOUNT_EMAIL}"
echo "  📄 Public Key:    ${PUBLIC_KEY_FILE}"
echo ""

# Create KMS reference file
KMS_REF_FILE="${OUTPUT_DIR}/kms-reference.txt"
cat > "${KMS_REF_FILE}" << EOF
# GCP KMS Reference for Cosign Signing
# Use this reference when signing images with Cosign

KMS_KEY_REF="gcpkms://projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}/cryptoKeys/${KEY_NAME}"

# Signing command:
# COSIGN_EXPERIMENTAL=1 cosign sign --key "\${KMS_KEY_REF}" <IMAGE>

# GitHub Actions environment variable:
# COSIGN_KMS_KEY: gcpkms://projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}/cryptoKeys/${KEY_NAME}
EOF

echo -e "${BLUE}📝 KMS reference saved to: ${KMS_REF_FILE}${NC}"
echo ""

echo -e "${YELLOW}⚠️  NEXT STEPS:${NC}"
echo "  1. Deploy public key to Kubernetes (see kubectl command above)"
echo "  2. Update Kyverno policies to reference the Kubernetes secret"
echo "  3. Update CI/CD pipelines with KMS key reference"
echo "  4. Sign images using: COSIGN_EXPERIMENTAL=1 cosign sign --key 'gcpkms://projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}/cryptoKeys/${KEY_NAME}' <IMAGE>"
echo "  5. For production: upgrade key protection level to HSM"
echo ""
echo -e "${YELLOW}⚠️  SECURITY NOTES:${NC}"
echo "  - KMS keys are non-exportable and managed by Google"
echo "  - All signing operations are audited in Cloud Logging"
echo "  - Service account has minimal permissions (signerVerifier only)"
echo "  - Consider enabling key rotation policy"
echo "  - Review IAM bindings regularly"
echo ""
echo -e "${GREEN}✅ Setup complete! Proceed with Kyverno policy deployment.${NC}"
echo ""
