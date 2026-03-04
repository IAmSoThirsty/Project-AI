<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# 🔐 Enterprise KMS Setup Guide for TK8S

## Overview

This guide walks through migrating from embedded Cosign keys to enterprise-grade GCP Cloud KMS for container image signing. This upgrade provides:

- **Hardware-backed key security**: Keys stored in Google's infrastructure
- **Immutable audit trail**: All signing operations logged
- **Zero key exposure**: Private keys never leave KMS
- **Automated key rotation**: Built-in key lifecycle management
- **Compliance-ready**: Meets SOC 2, ISO 27001, PCI DSS requirements

## Prerequisites

- GCP Project with billing enabled
- `gcloud` CLI installed and authenticated
- `kubectl` configured for your GKE cluster
- `cosign` v2.0+ installed
- Cluster admin permissions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GCP Cloud KMS                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Keyring: tk8s-keyring                               │   │
│  │  ├─ Key: cosign-key (ASYMMETRIC_SIGNING)            │   │
│  │  │  ├─ Algorithm: EC_SIGN_P256_SHA256               │   │
│  │  │  ├─ Protection: SOFTWARE (upgrade to HSM)        │   │
│  │  │  └─ Versions: Auto-rotated                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ API Calls
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              CI/CD Pipeline (GitHub Actions)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  1. Build container image                            │   │
│  │  2. Push to registry (GHCR/GCR)                      │   │
│  │  3. Sign with KMS: cosign sign --key gcpkms://...   │   │
│  │  4. Verify signature                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ Signed Images
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 GKE Cluster (TK8S)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Kyverno Policy                                      │   │
│  │  ├─ Verify signature with public key (K8s Secret)   │   │
│  │  ├─ Block unsigned images                           │   │
│  │  └─ Audit all admissions                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Binary Authorization (Optional)                     │   │
│  │  ├─ Hard gate for image deployment                  │   │
│  │  └─ Requires attestations                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Part 1: GCP KMS Setup

### Step 1: Set Environment Variables

```bash
export GCP_PROJECT_ID="your-project-id"
export KMS_LOCATION="us-central1"
export KMS_KEYRING="tk8s-keyring"
export KMS_KEY_NAME="cosign-key"
export KMS_SA_NAME="cosign-signer"
```

### Step 2: Run KMS Setup Script

```bash
cd k8s/tk8s/scripts
./setup-gcp-kms.sh
```

This script will:

1. ✅ Create KMS keyring
2. ✅ Create asymmetric signing key
3. ✅ Create service account with minimal permissions
4. ✅ Grant `roles/cloudkms.signerVerifier` IAM permissions
5. ✅ Export public key to `.kms-keys/cosign-kms.pub`
6. ✅ Generate KMS reference file

**Expected Output:**
```
╔══════════════════════════════════════════════════════════════════════╗
║           GCP KMS Setup for Cosign Image Signing                     ║
║    Enterprise-Grade Key Management | HSM-backed | Auditable          ║
╚══════════════════════════════════════════════════════════════════════╝

✅ KMS Configuration Summary:
  🔑 Keyring:       projects/PROJECT_ID/locations/us-central1/keyRings/tk8s-keyring
  🔐 Key:           projects/PROJECT_ID/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key
  👤 Service Account: cosign-signer@PROJECT_ID.iam.gserviceaccount.com
  📄 Public Key:    .kms-keys/cosign-kms.pub
```

### Step 3: Verify KMS Setup

```bash

# List keyrings

gcloud kms keyrings list --location=us-central1

# List keys

gcloud kms keys list --location=us-central1 --keyring=tk8s-keyring

# Verify IAM bindings

gcloud kms keys get-iam-policy cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring
```

Expected output:
```
bindings:

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/cloudkms.signerVerifier
```

## Part 2: Kubernetes Secret Deployment

### Step 1: Deploy Public Key to Kubernetes

```bash

# Ensure Kyverno namespace exists

kubectl create namespace kyverno --dry-run=client -o yaml | kubectl apply -f -

# Create secret from exported public key

kubectl create secret generic cosign-public-key \
  --from-file=cosign.pub=.kms-keys/cosign-kms.pub \
  -n kyverno
```

### Step 2: Verify Secret

```bash
kubectl get secret cosign-public-key -n kyverno
kubectl describe secret cosign-public-key -n kyverno
```

## Part 3: Deploy Kyverno Policies

### Step 1: Apply KMS-Backed Verification Policy

```bash
cd k8s/tk8s/security
kubectl apply -f kyverno-kms-verification.yaml
```

This deploys:

- ✅ Image signature verification policy (references K8s secret)
- ✅ Kyverno self-protection policy (prevents deletion)
- ✅ Pod Security Admission enforcement
- ✅ Default-deny NetworkPolicy requirement
- ✅ Audit logging requirement

### Step 2: Verify Policies

```bash
kubectl get clusterpolicies
kubectl describe clusterpolicy require-kms-cosign-signatures
kubectl describe clusterpolicy protect-kyverno
```

### Step 3: Test Policy Enforcement

```bash

# This should FAIL (unsigned image)

kubectl run test-unsigned --image=nginx:latest -n project-ai-core

# Expected error:

# Error from server: admission webhook "mutate.kyverno.svc" denied the request:

# policy require-kms-cosign-signatures/verify-kms-signature failed:

# image signature verification failed

```

## Part 4: Network Policies

### Step 1: Apply Default-Deny Policies

```bash
cd k8s/tk8s/network-policies
kubectl apply -f default-deny-network-policies.yaml
```

⚠️ **WARNING**: This will block all traffic by default. Ensure you have explicit allow policies configured first.

### Step 2: Verify Network Policies

```bash
kubectl get networkpolicies -A
kubectl describe networkpolicy default-deny-all -n project-ai-production
```

## Part 5: GKE Audit Logging

### Step 1: Enable Audit Logging

```bash
export GCP_PROJECT_ID="your-project-id"
export GKE_CLUSTER_NAME="tk8s-prod"
export GKE_CLUSTER_LOCATION="us-central1-a"

cd k8s/tk8s/scripts
./enable-gke-audit-logging.sh
```

This enables:

- ✅ System logging (control plane)
- ✅ Workload logging (pod stdout/stderr)
- ✅ Cloud Monitoring
- ✅ Log retention (365 days default)
- ✅ Log sinks to Cloud Storage
- ✅ Log-based metrics

### Step 2: Verify Logging

```bash

# View cluster logging config

gcloud container clusters describe tk8s-prod \
  --location=us-central1-a \
  --format="value(loggingConfig)"

# View recent logs

gcloud logging read 'resource.type="k8s_cluster"' --limit 10
```

## Part 6: Binary Authorization (Optional but Recommended)

### Step 1: Create Attestor

```bash

# Create note for attestations

NOTE_ID="cosign-attestation-note"
PROJECT_ID="your-project-id"

cat > /tmp/note_payload.json << EOF
{
  "name": "projects/${PROJECT_ID}/notes/${NOTE_ID}",
  "attestation": {
    "hint": {
      "human_readable_name": "Cosign image signature attestation"
    }
  }
}
EOF

curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  --data-binary @/tmp/note_payload.json \
  "https://containeranalysis.googleapis.com/v1/projects/${PROJECT_ID}/notes/?noteId=${NOTE_ID}"

# Create attestor

gcloud container binauthz attestors create cosign-attestor \
  --attestation-authority-note=${NOTE_ID} \
  --attestation-authority-note-project=${PROJECT_ID}
```

### Step 2: Associate KMS Key with Attestor

```bash
gcloud container binauthz attestors public-keys add \
  --attestor=cosign-attestor \
  --keyversion-project=${PROJECT_ID} \
  --keyversion-location=us-central1 \
  --keyversion-keyring=tk8s-keyring \
  --keyversion-key=cosign-key \
  --keyversion=1
```

### Step 3: Deploy Binary Authorization Policy

```bash

# Edit policy template with your PROJECT_ID

cd k8s/tk8s/security
sed -i "s/PROJECT_ID/${PROJECT_ID}/g" binary-authorization-policy.yaml

# Import policy

gcloud container binauthz policy import binary-authorization-policy.yaml
```

### Step 4: Enable on Cluster

```bash
gcloud container clusters update tk8s-prod \
  --enable-binauthz \
  --zone=us-central1-a
```

## Part 7: CI/CD Integration

### GitHub Actions Setup

Update `.github/workflows/tk8s-civilization-pipeline.yml`:

```yaml

- name: Sign image with KMS

  env:
    COSIGN_EXPERIMENTAL: 1
    COSIGN_KMS_KEY: gcpkms://projects/${{ secrets.GCP_PROJECT_ID }}/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key
  run: |
    cosign sign --key "${COSIGN_KMS_KEY}" \
      -a "repo=${{ github.repository }}" \
      -a "workflow=${{ github.workflow }}" \
      -a "ref=${{ github.ref }}" \
      "${IMAGE_TAG}@${IMAGE_DIGEST}"
```

### Required GitHub Secrets

Add these secrets to your repository:

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Workload Identity provider path
- `GCP_SERVICE_ACCOUNT`: Service account email for Workload Identity

### Workload Identity Setup

```bash

# Create Workload Identity pool

gcloud iam workload-identity-pools create "github-actions" \
  --location="global" \
  --description="Workload Identity pool for GitHub Actions"

# Create provider

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-actions" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='IAmSoThirsty/Project-AI'"

# Grant service account impersonation

gcloud iam service-accounts add-iam-policy-binding \
  cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-actions/attribute.repository/IAmSoThirsty/Project-AI"
```

## Part 8: Validation & Testing

### Test Image Signing

```bash

# Build test image

docker build -t gcr.io/${PROJECT_ID}/test:v1.0.0 .

# Push to registry

docker push gcr.io/${PROJECT_ID}/test:v1.0.0

# Sign with KMS

COSIGN_EXPERIMENTAL=1 cosign sign \
  --key gcpkms://projects/${PROJECT_ID}/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key \
  gcr.io/${PROJECT_ID}/test:v1.0.0

# Verify signature

cosign verify \
  --key .kms-keys/cosign-kms.pub \
  gcr.io/${PROJECT_ID}/test:v1.0.0
```

### Test Kyverno Policy

```bash

# Deploy signed image (should succeed)

kubectl run test-signed --image=gcr.io/${PROJECT_ID}/test:v1.0.0 -n project-ai-core

# Check Kyverno logs

kubectl logs -n kyverno -l app=kyverno --tail=100
```

### Test Network Policies

```bash

# Should fail due to default-deny egress

kubectl run test-network --image=busybox -n project-ai-core -- wget -O- google.com

# Check for network policy violations in logs

kubectl logs -n kube-system -l component=kube-proxy | grep DROP
```

## Part 9: Production Hardening

### Upgrade to HSM Protection

For production, upgrade key protection to HSM:

```bash

# Create new HSM-protected key

gcloud kms keys create cosign-key-hsm \
  --location=us-central1 \
  --keyring=tk8s-keyring \
  --purpose=asymmetric-signing \
  --default-algorithm=ec-sign-p256-sha256 \
  --protection-level=hsm

# Migrate to new key (requires re-signing all images)

```

### Enable Key Rotation

```bash
gcloud kms keys update cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring \
  --rotation-period=90d \
  --next-rotation-time=$(date -d '+90 days' -u +%Y-%m-%dT%H:%M:%SZ)
```

### Set Up Alerting

```bash

# Create alert for denied pod creations

gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Denied Pod Creations" \
  --condition-display-name="High rate of denied pods" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s \
  --metric-type="logging.googleapis.com/user/denied_pod_creations"
```

## Troubleshooting

### Issue: "Permission denied" when signing

**Solution**: Verify service account has `roles/cloudkms.signerVerifier`:
```bash
gcloud kms keys get-iam-policy cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring
```

### Issue: Kyverno not verifying signatures

**Solution**: Check secret exists and contains correct public key:
```bash
kubectl get secret cosign-public-key -n kyverno -o jsonpath='{.data.cosign\.pub}' | base64 -d
```

### Issue: Images rejected even when signed

**Solution**: Verify image reference matches policy pattern:
```bash
kubectl describe clusterpolicy require-kms-cosign-signatures

# Check imageReferences patterns match your registry

```

## Security Best Practices

1. ✅ **Never embed private keys**: Use KMS exclusively
2. ✅ **Rotate keys regularly**: Set 90-day rotation policy
3. ✅ **Monitor audit logs**: Set up alerts for anomalies
4. ✅ **Use HSM in production**: Upgrade protection level
5. ✅ **Limit service account permissions**: Grant minimal IAM roles
6. ✅ **Review IAM bindings monthly**: Audit who can sign images
7. ✅ **Enable Binary Authorization**: Add hard gate layer
8. ✅ **Test in staging first**: Validate policies before production
9. ✅ **Document key usage**: Maintain audit trail
10. ✅ **Have rollback plan**: Keep unsigned fallback for emergencies

## Rollback Plan

If issues arise, you can temporarily disable policies:

```bash

# Set Kyverno to audit mode (non-blocking)

kubectl patch clusterpolicy require-kms-cosign-signatures \
  --type=merge \
  -p '{"spec":{"validationFailureAction":"audit"}}'

# Remove network policies

kubectl delete networkpolicy default-deny-all -n project-ai-production

# Disable Binary Authorization

gcloud container clusters update tk8s-prod \
  --no-enable-binauthz \
  --zone=us-central1-a
```

## Support

For issues or questions:

- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: k8s/tk8s/README.md
- Security contact: security@project-ai.io

## References

- [Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [GCP KMS Documentation](https://cloud.google.com/kms/docs)
- [Kyverno Policies](https://kyverno.io/policies/)
- [Binary Authorization](https://cloud.google.com/binary-authorization/docs)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
