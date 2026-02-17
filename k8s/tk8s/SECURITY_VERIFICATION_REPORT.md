# TK8S Security Verification Report

## Purpose

This document provides step-by-step verification procedures and expected outputs for validating the enterprise-grade security setup of TK8S, including privilege verification and Workload Identity binding.

---

## 🔎 Part 1: Verify Effective Privileges

### 1️⃣ Check Service Account Roles (Project-Level)

**Command:**
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:cosign-signer@PROJECT_ID.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

**✅ Expected Output (CORRECT):**
```
ROLE
roles/cloudkms.signerVerifier
```

**❌ Incorrect Output (DANGEROUS):**
```
ROLE
roles/owner
roles/editor
roles/cloudkms.admin
```

**Interpretation:**

- ✅ **PASS**: Only `roles/cloudkms.signerVerifier` is listed
- ❌ **FAIL**: If you see `Owner`, `Editor`, `Admin`, or any broader roles

**Remediation (if failed):**
```bash

# Remove over-privileged bindings

gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/DANGEROUS_ROLE"

# Ensure only signerVerifier at KMS key level (not project level)

gcloud kms keys add-iam-policy-binding cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring \
  --member="serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudkms.signerVerifier"
```

---

### 2️⃣ Check KMS Key-Level Policy

**Command:**
```bash
gcloud kms keys get-iam-policy cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring \
  --format="yaml"
```

**✅ Expected Output (CORRECT):**
```yaml
bindings:

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/cloudkms.signerVerifier
etag: BwYRh8xxxxxx
version: 1
```

**Key Points:**

- ✅ **ONLY** `roles/cloudkms.signerVerifier` is bound
- ✅ Member is the `cosign-signer@PROJECT_ID.iam.gserviceaccount.com` service account
- ✅ No additional members or roles

**Permissions Granted by `roles/cloudkms.signerVerifier`:**

- `cloudkms.cryptoKeyVersions.useToSign` - Sign data
- `cloudkms.cryptoKeyVersions.viewPublicKey` - View public key
- `cloudkms.cryptoKeys.get` - Get key metadata

**Permissions NOT Granted (as expected):**

- ❌ `cloudkms.cryptoKeys.create` - Cannot create keys
- ❌ `cloudkms.cryptoKeys.update` - Cannot modify keys
- ❌ `cloudkms.cryptoKeyVersions.destroy` - Cannot delete key versions
- ❌ `cloudkms.cryptoKeyVersions.create` - Cannot create new versions

---

### 3️⃣ Confirm No Over-Privileged Binding

**Command:**
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --format="yaml" | grep cosign-signer -B 3 -A 3
```

**✅ Expected Output (CORRECT - Empty or minimal):**
```yaml

# No output is GOOD - means no project-level bindings

# OR only specific resource-level bindings like:

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/iam.workloadIdentityUser
```

**❌ Incorrect Output (DANGEROUS):**
```yaml

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/owner  # ❌ DANGEROUS

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/editor  # ❌ DANGEROUS

- members:
  - serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com

  role: roles/cloudkms.admin  # ❌ TOO BROAD
```

**Dangerous Roles to Avoid:**

- ❌ `roles/owner` - Full project access
- ❌ `roles/editor` - Can modify all resources
- ❌ `roles/admin` - Administrative access
- ❌ `roles/cloudkms.admin` - Can delete/modify keys
- ❌ `roles/cloudkms.cryptoKeyEncrypterDecrypter` - Encryption access (not needed for signing)

**Remediation:**
```bash

# List all bindings for the service account

gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:cosign-signer@PROJECT_ID.iam.gserviceaccount.com" \
  --format="table(bindings.role)"

# Remove each over-privileged binding

gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cosign-signer@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/ROLE_TO_REMOVE"
```

---

## 🔐 Part 2: Lock to Workload Identity (Production-Correct)

**⚠️ CRITICAL: Do NOT use JSON key files in production.**

### Why Workload Identity?

| Approach | Security | Key Rotation | Audit Trail | Risk |
|----------|----------|--------------|-------------|------|
| JSON Key File | ❌ Low | Manual | Limited | High - key leakage |
| Workload Identity | ✅ High | Automatic | Complete | Low - no static secrets |

---

### Step 1: Enable Workload Identity on Cluster

**Command:**
```bash
export PROJECT_ID="your-project-id"
export CLUSTER_NAME="tk8s-prod"
export CLUSTER_LOCATION="us-central1-a"

gcloud container clusters update ${CLUSTER_NAME} \
  --location=${CLUSTER_LOCATION} \
  --workload-pool=${PROJECT_ID}.svc.id.goog
```

**Expected Output:**
```
Updating tk8s-prod...done.
Updated [https://container.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1-a/clusters/tk8s-prod].
```

**Verification:**
```bash
gcloud container clusters describe ${CLUSTER_NAME} \
  --location=${CLUSTER_LOCATION} \
  --format="value(workloadIdentityConfig.workloadPool)"
```

**✅ Expected Output:**
```
PROJECT_ID.svc.id.goog
```

---

### Step 2: Create Kubernetes Service Account

**Command:**
```bash
kubectl create namespace tk8s-prod --dry-run=client -o yaml | kubectl apply -f -
kubectl create serviceaccount cosign-signer -n tk8s-prod
```

**Expected Output:**
```
namespace/tk8s-prod created
serviceaccount/cosign-signer created
```

**Verification:**
```bash
kubectl get serviceaccount cosign-signer -n tk8s-prod
```

**✅ Expected Output:**
```
NAME            SECRETS   AGE
cosign-signer   0         10s
```

---

### Step 3: Bind Kubernetes SA to GCP SA

**Command:**
```bash
gcloud iam service-accounts add-iam-policy-binding \
  cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[tk8s-prod/cosign-signer]"
```

**Expected Output:**
```
Updated IAM policy for serviceAccount [cosign-signer@PROJECT_ID.iam.gserviceaccount.com].
bindings:

- members:
  - serviceAccount:PROJECT_ID.svc.id.goog[tk8s-prod/cosign-signer]

  role: roles/iam.workloadIdentityUser
etag: BwYRh8xxxxxx
version: 1
```

**Verification:**
```bash
gcloud iam service-accounts get-iam-policy \
  cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com \
  --format="yaml"
```

**✅ Expected Output:**
```yaml
bindings:

- members:
  - serviceAccount:PROJECT_ID.svc.id.goog[tk8s-prod/cosign-signer]

  role: roles/iam.workloadIdentityUser
etag: BwYRh8xxxxxx
version: 1
```

---

### Step 4: Annotate Kubernetes Service Account

**Command:**
```bash
kubectl annotate serviceaccount cosign-signer \
  -n tk8s-prod \
  iam.gke.io/gcp-service-account=cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com
```

**Expected Output:**
```
serviceaccount/cosign-signer annotated
```

**Verification:**
```bash
kubectl get serviceaccount cosign-signer -n tk8s-prod -o yaml
```

**✅ Expected Output:**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: cosign-signer@PROJECT_ID.iam.gserviceaccount.com
  name: cosign-signer
  namespace: tk8s-prod
```

---

### Step 5: Test Workload Identity

**Create Test Pod:**
```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: workload-identity-test
  namespace: tk8s-prod
spec:
  serviceAccountName: cosign-signer
  containers:

  - name: gcloud

    image: google/cloud-sdk:slim
    command: ["sleep", "infinity"]
EOF
```

**Test Authentication:**
```bash
kubectl exec -it workload-identity-test -n tk8s-prod -- gcloud auth list
```

**✅ Expected Output:**
```
                Credentialed Accounts
ACTIVE  ACCOUNT

*       cosign-signer@PROJECT_ID.iam.gserviceaccount.com

```

**Test KMS Access:**
```bash
kubectl exec -it workload-identity-test -n tk8s-prod -- \
  gcloud kms keys list --location=us-central1 --keyring=tk8s-keyring
```

**✅ Expected Output:**
```
NAME                                                                                      PURPOSE          ALGORITHM                    PROTECTION_LEVEL  LABELS  PRIMARY_ID  PRIMARY_STATE
projects/PROJECT_ID/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key  ASYMMETRIC_SIGN  EC_SIGN_P256_SHA256         SOFTWARE                   1           ENABLED
```

**Cleanup Test Pod:**
```bash
kubectl delete pod workload-identity-test -n tk8s-prod
```

---

## 🎯 Part 3: Workload Identity Benefits Summary

### ✅ What You Get

1. **No Static Secrets**
   - No JSON key files to manage
   - No keys in environment variables
   - No keys in ConfigMaps/Secrets

2. **Automatic Key Rotation**
   - GCP manages credential lifecycle
   - Tokens auto-refresh every hour
   - No manual rotation needed

3. **Granular Permissions**
   - Service account only has access when running in specific namespace
   - Cannot be used outside the cluster
   - Namespace isolation enforced

4. **Complete Audit Trail**
   - Every action logged with pod identity
   - Cloud Audit Logs show which pod made which call
   - Impossible to forge identity

5. **No Credential Leakage Risk**
   - Credentials never leave Google's infrastructure
   - Cannot be extracted from pods
   - Short-lived tokens only

---

## ✅ Final Verification Checklist

Run all checks and verify outputs match expected results:

```bash

#!/bin/bash

set -e

PROJECT_ID="your-project-id"
CLUSTER_NAME="tk8s-prod"
CLUSTER_LOCATION="us-central1-a"

echo "🔍 Verification Checklist"
echo "========================="
echo ""

echo "✅ 1. Service Account Project Roles"
gcloud projects get-iam-policy ${PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
echo ""

echo "✅ 2. KMS Key-Level Policy"
gcloud kms keys get-iam-policy cosign-key \
  --location=us-central1 \
  --keyring=tk8s-keyring \
  --format="yaml"
echo ""

echo "✅ 3. Workload Identity Pool"
gcloud container clusters describe ${CLUSTER_NAME} \
  --location=${CLUSTER_LOCATION} \
  --format="value(workloadIdentityConfig.workloadPool)"
echo ""

echo "✅ 4. Kubernetes Service Account"
kubectl get serviceaccount cosign-signer -n tk8s-prod
echo ""

echo "✅ 5. Workload Identity Binding"
gcloud iam service-accounts get-iam-policy \
  cosign-signer@${PROJECT_ID}.iam.gserviceaccount.com \
  --format="yaml"
echo ""

echo "✅ 6. Service Account Annotation"
kubectl get serviceaccount cosign-signer -n tk8s-prod \
  -o jsonpath='{.metadata.annotations.iam\.gke\.io/gcp-service-account}'
echo ""
echo ""

echo "🎉 All checks complete!"
```

---

## 🚦 Decision Matrix

Based on verification results:

| All Checks Pass | Privilege Minimal | Workload Identity | Decision |
|-----------------|-------------------|-------------------|----------|
| ✅ Yes | ✅ Yes | ✅ Yes | **Proceed to Binary Authorization** |
| ✅ Yes | ✅ Yes | ❌ No | **Configure Workload Identity first** |
| ✅ Yes | ❌ No | ✅ Yes | **Reduce privileges first** |
| ❌ No | - | - | **Fix errors before proceeding** |

---

## 📊 Status Determination

After running all verification commands, determine status:

### ✅ PROCEED TO BINARY AUTHORIZATION

**Conditions:**

- Service account has ONLY `roles/cloudkms.signerVerifier` at KMS key level
- No project-level over-privileged bindings
- Workload Identity is enabled and configured
- Kubernetes service account is annotated
- Test pod can authenticate as GCP service account

**Next Step:**
```bash
echo "✅ PROCEED: Binary Authorization"

# Follow Binary Authorization setup in KMS_SETUP_GUIDE.md Part 6

```

### ✅ PROCEED TO WORM (Write-Once-Read-Many)

**Conditions:**

- All Binary Authorization checks pass
- Audit logging is enabled with immutable storage
- Log retention is configured (365 days minimum)
- No one can delete audit logs (including admins)

**Next Step:**
```bash
echo "✅ PROCEED: WORM - Immutable Audit Trail Active"

# Audit logs are now write-once-read-many

# Compliance: SOC 2, ISO 27001, PCI DSS

```

---

## 🔒 Security Posture After Setup

### Before

- 🔴 Private keys in GitHub Secrets
- 🔴 Downloadable credentials
- 🔴 Manual key rotation
- 🔴 Limited audit trail
- 🔴 Broad service account permissions

### After

- 🟢 Keys in GCP KMS (hardware-backed)
- 🟢 No static credentials
- 🟢 Automatic rotation
- 🟢 Immutable audit logs
- 🟢 Minimal privileges (signerVerifier only)
- 🟢 Workload Identity (no key leakage)
- 🟢 Binary Authorization (hard gate)

---

## 📞 Support

If any verification step fails:

1. Review the remediation steps in this document
2. Check Cloud Audit Logs for permission errors
3. Verify cluster has Workload Identity enabled
4. Ensure namespace and service account names match exactly

**Resources:**

- [GCP KMS IAM](https://cloud.google.com/kms/docs/reference/permissions-and-roles)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Binary Authorization](https://cloud.google.com/binary-authorization/docs)

---

## 📝 Audit Trail

Document your verification:

```markdown

# Security Verification - [DATE]

## Environment

- Project ID: [PROJECT_ID]
- Cluster: [CLUSTER_NAME]
- Location: [CLUSTER_LOCATION]

## Verification Results

- [ ] Service account has minimal privileges
- [ ] KMS key policy is correct
- [ ] No over-privileged bindings
- [ ] Workload Identity enabled
- [ ] Kubernetes SA created and annotated
- [ ] Test pod authenticated successfully

## Status

- [✅] PROCEED TO BINARY AUTHORIZATION
- [ ] PROCEED TO WORM
- [ ] REMEDIATION REQUIRED

## Notes

[Add any additional notes or findings]

## Verified By

Name: _______________
Date: _______________
```

---

**End of Verification Report**
