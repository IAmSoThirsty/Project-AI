# TK8S Enterprise Security Upgrade

## Overview

This directory contains enterprise-grade security configurations for TK8S (Thirsty's Kubernetes), including:

- **GCP KMS Integration**: Hardware-backed key management for image signing
- **Kyverno Policies**: Advanced admission control with self-protection
- **Network Policies**: Default-deny zero-trust network model
- **GKE Security**: Binary Authorization and audit logging
- **CI/CD Integration**: Enhanced signing workflows

## ⚠️ Implementation Status

**Configuration:** ✅ COMPLETE
**Live Validation:** ⏳ REQUIRED BEFORE PRODUCTION

This implementation provides enterprise-grade security infrastructure that is **configured** following best practices, but requires **validation testing** on a live GKE cluster before production deployment.

**Required Validations (See VALIDATION_TEST_PROCEDURES.md):**

1. Verify signed images deploy successfully
2. Confirm unsigned images are rejected
3. Test network policy enforcement
4. Validate audit log immutability
5. Verify privileged container rejection

**Until these tests pass, treat this as "designed for production" rather than "production-tested."**

## Directory Structure

```
k8s/tk8s/
├── scripts/
│   ├── setup-gcp-kms.sh              # GCP KMS setup automation
│   └── enable-gke-audit-logging.sh   # GKE audit logging configuration
├── security/
│   ├── kyverno-kms-verification.yaml  # KMS-backed verification policies
│   ├── kyverno-policies-kms.yaml      # Legacy KMS policies
│   ├── kyverno-policies.yaml          # Legacy policies
│   └── binary-authorization-policy.yaml # GKE Binary Authorization
├── network-policies/
│   ├── default-deny-network-policies.yaml  # Zero-trust network policies
│   └── tk8s-network-policies.yaml          # Existing network policies
├── namespaces/
│   └── tk8s-namespaces.yaml          # Updated with Pod Security Admission
├── workflows/
│   └── enhanced-image-signing.yml    # CI/CD workflow snippet
├── KMS_SETUP_GUIDE.md                # Comprehensive setup guide
└── README.md                         # This file
```

## Quick Start

### Phase 1: GCP KMS Setup

```bash

# Set environment variables

export GCP_PROJECT_ID="your-project-id"
export KMS_LOCATION="us-central1"

# Run setup script

cd k8s/tk8s/scripts
./setup-gcp-kms.sh

# Deploy public key to Kubernetes

kubectl create namespace kyverno --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic cosign-public-key \
  --from-file=cosign.pub=.kms-keys/cosign-kms.pub \
  -n kyverno
```

### Phase 2: Deploy Kyverno Policies

```bash
cd k8s/tk8s/security
kubectl apply -f kyverno-kms-verification.yaml
```

This deploys 5 critical policies:

1. ✅ **KMS Signature Verification** - Verifies images with KMS public key
2. ✅ **Kyverno Self-Protection** - Prevents policy deletion/tampering
3. ✅ **Pod Security Admission** - Enforces restricted standards
4. ✅ **Network Policy Requirement** - Requires default-deny policies
5. ✅ **Audit Logging** - Enforces audit labels on workloads

### Phase 3: Network Policies (Careful!)

```bash
cd k8s/tk8s/network-policies

# ⚠️ WARNING: This blocks all traffic by default

# Ensure explicit allow policies exist first

kubectl apply -f default-deny-network-policies.yaml
```

### Phase 4: GKE Audit Logging

```bash
export GKE_CLUSTER_NAME="tk8s-prod"
export GKE_CLUSTER_LOCATION="us-central1-a"

cd k8s/tk8s/scripts
./enable-gke-audit-logging.sh
```

### Phase 5: Binary Authorization (Optional)

```bash
cd k8s/tk8s/security

# Edit binary-authorization-policy.yaml with your PROJECT_ID

gcloud container binauthz policy import binary-authorization-policy.yaml
```

## Security Features

### 🔐 KMS-Backed Signing

- **Zero key exposure**: Private keys never leave Google's infrastructure
- **Hardware security**: Optional HSM backing
- **Audit trail**: All signing operations logged
- **Compliance**: Meets SOC 2, ISO 27001, PCI DSS

**Key Reference:**
```
gcpkms://projects/PROJECT_ID/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key
```

### 🛡️ Kyverno Protection

- **Self-protection**: Policies cannot be deleted
- **Signature verification**: All images must be signed
- **Namespace protection**: Critical namespaces protected
- **Webhook protection**: Admission webhooks immutable

### 🔒 Network Isolation

- **Default deny**: All traffic blocked by default
- **Zero trust**: Explicit allow required
- **Namespace isolation**: ECA has maximum isolation
- **DNS allowed**: Explicit DNS egress for all namespaces

### 📊 Audit & Compliance

- **System logging**: Control plane audit logs
- **Workload logging**: Application logs
- **Log retention**: 365 days default
- **Log sinks**: Immutable storage in Cloud Storage
- **Metrics**: Denied pods, signature failures

## CI/CD Integration

### GitHub Actions

See `workflows/enhanced-image-signing.yml` for complete implementation.

**Key features:**

- Dual mode: Keyless (OIDC) for staging, KMS for production
- Automatic signature verification
- Binary Authorization attestations
- Configurable via GitHub variables

**Required Secrets:**

- `GCP_PROJECT_ID`
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`

**Required Variables:**

- `USE_KMS_SIGNING`: Enable KMS signing (true/false)
- `USE_BINARY_AUTH`: Enable Binary Authorization (true/false)

## Validation

### Test Image Signing

```bash

# Build and sign test image

docker build -t gcr.io/${PROJECT_ID}/test:v1 .
docker push gcr.io/${PROJECT_ID}/test:v1

COSIGN_EXPERIMENTAL=1 cosign sign \
  --key gcpkms://projects/${PROJECT_ID}/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key \
  gcr.io/${PROJECT_ID}/test:v1

# Verify signature

cosign verify \
  --key .kms-keys/cosign-kms.pub \
  gcr.io/${PROJECT_ID}/test:v1
```

### Test Kyverno Policy

```bash

# This should FAIL (unsigned)

kubectl run test-fail --image=nginx:latest -n project-ai-core

# This should SUCCEED (if signed)

kubectl run test-pass --image=gcr.io/${PROJECT_ID}/test:v1 -n project-ai-core
```

### Test Network Policy

```bash

# Should fail (egress blocked)

kubectl run test-net --image=busybox -n project-ai-core -- wget -O- google.com
```

### View Audit Logs

```bash

# Recent k8s events

gcloud logging read 'resource.type="k8s_cluster"' --limit 10

# Denied pod creations

gcloud logging read 'resource.type="k8s_cluster" AND protoPayload.response.status="Failure"' --limit 10

# Kyverno decisions

gcloud logging read 'jsonPayload.message=~".*kyverno.*"' --limit 10
```

## Security Levels

### Level 1: Basic (Current State)

- ✅ Keyless signing with GitHub OIDC
- ✅ Kyverno image verification
- ✅ Basic network policies

### Level 2: Enhanced (This Upgrade)

- ✅ KMS-backed signing
- ✅ Kyverno self-protection
- ✅ Default-deny network policies
- ✅ Pod Security Admission (restricted)
- ✅ GKE audit logging

### Level 3: Enterprise (Optional)

- ⬜ HSM-backed keys
- ⬜ Binary Authorization hard gate
- ⬜ Multi-region KMS replication
- ⬜ Key rotation automation
- ⬜ SIEM integration

### Level 4: Defense-in-Depth (Future)

- ⬜ Runtime security (Falco)
- ⬜ Service mesh (Istio)
- ⬜ Workload identity federation
- ⬜ OPA policy engine
- ⬜ Continuous compliance scanning

## Rollback

If issues arise:

```bash

# Disable Kyverno enforcement (audit mode)

kubectl patch clusterpolicy require-kms-cosign-signatures \
  --type=merge \
  -p '{"spec":{"validationFailureAction":"audit"}}'

# Remove network policies

kubectl delete networkpolicy default-deny-all -A

# Disable Binary Authorization

gcloud container clusters update tk8s-prod \
  --no-enable-binauthz \
  --zone=us-central1-a
```

## Monitoring

### Key Metrics

- **denied_pod_creations**: Count of blocked pod deployments
- **image_signature_failures**: Signature verification failures
- **network_policy_violations**: Blocked network connections

### Dashboards

- Cloud Console Logs: `https://console.cloud.google.com/logs/query?project=${PROJECT_ID}`
- GKE Monitoring: `https://console.cloud.google.com/monitoring?project=${PROJECT_ID}`
- Binary Auth: `https://console.cloud.google.com/security/binary-authorization?project=${PROJECT_ID}`

## Support

- **Setup Guide**: See `KMS_SETUP_GUIDE.md` for detailed instructions
- **GitHub Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Security Contact**: security@project-ai.io

## References

- [Cosign Documentation](https://docs.sigstore.dev/cosign/overview/)
- [GCP KMS](https://cloud.google.com/kms/docs)
- [Kyverno](https://kyverno.io/)
- [Binary Authorization](https://cloud.google.com/binary-authorization/docs)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

## Contributing

See `CONTRIBUTING.md` in the repository root.

## License

See `LICENSE` in the repository root.
