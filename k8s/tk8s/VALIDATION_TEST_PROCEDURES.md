# TK8S Security Validation Test Procedures

## Purpose

This document provides step-by-step procedures to validate the security claims made in the TK8S documentation. These tests must be executed on a live GKE cluster before considering the implementation "production-ready."

---

## ⚠️ Important Notice

**The TK8S security infrastructure is CONFIGURED but NOT YET VALIDATED.**

Claims about production-readiness, enterprise best practices, and forensic capabilities require the following validations to be executed and captured:

- [ ] Signed image deployment succeeds
- [ ] Unsigned image deployment is denied
- [ ] Lateral pod communication is blocked
- [ ] Audit log deletion attempts are denied
- [ ] Privileged container deployment is denied

**Until these tests are completed, consider the implementation as "designed for production" rather than "production-tested."**

---

## Prerequisites

- Live GKE cluster with TK8S deployed
- Kyverno installed and policies applied
- Network policies deployed
- Audit logging enabled
- Binary Authorization configured (optional but recommended)
- `kubectl` access with admin permissions
- `docker` and `cosign` CLI tools installed
- GCP project with KMS configured

---

## Test 1: Signed Image Deployment (Should Succeed)

### Objective

Verify that properly signed images can be deployed successfully.

### Prerequisites

- Image signed with KMS key
- Kyverno policy `require-kms-cosign-signatures` in enforce mode

### Procedure

1. **Sign a test image:**

```bash

# Set variables

export PROJECT_ID="your-project-id"
export IMAGE="gcr.io/${PROJECT_ID}/test-app:v1.0.0"
export KMS_KEY="gcpkms://projects/${PROJECT_ID}/locations/us-central1/keyRings/tk8s-keyring/cryptoKeys/cosign-key"

# Build and push test image

docker build -t ${IMAGE} -f - . << 'EOF'
FROM nginx:alpine
RUN echo "Test application" > /usr/share/nginx/html/index.html
EOF

docker push ${IMAGE}

# Sign with KMS

COSIGN_EXPERIMENTAL=1 cosign sign --key ${KMS_KEY} ${IMAGE}

# Verify signature

cosign verify --key .kms-keys/cosign-kms.pub ${IMAGE}
```

2. **Deploy signed image:**

```bash
kubectl run test-signed-app \
  --image=${IMAGE} \
  --namespace=project-ai-core \
  --labels="app=test-signed,test=validation"
```

3. **Verify deployment:**

```bash
kubectl get pod test-signed-app -n project-ai-core
```

### Expected Result

✅ **PASS:** Pod is created and running
```
NAME              READY   STATUS    RESTARTS   AGE
test-signed-app   1/1     Running   0          10s
```

### Actual Result

```

# Document actual output here

```

### Capture Evidence

```bash

# Save pod status

kubectl get pod test-signed-app -n project-ai-core -o yaml > evidence/test1-signed-image-success.yaml

# Save Kyverno logs showing signature verification

kubectl logs -n kyverno -l app=kyverno --tail=50 | grep "test-signed-app" > evidence/test1-kyverno-logs.txt
```

### Cleanup

```bash
kubectl delete pod test-signed-app -n project-ai-core
```

---

## Test 2: Unsigned Image Deployment (Should Fail)

### Objective

Verify that unsigned images are rejected by Kyverno admission control.

### Prerequisites

- Kyverno policy `require-kms-cosign-signatures` in enforce mode
- Test image pushed but NOT signed

### Procedure

1. **Push unsigned image:**

```bash
export UNSIGNED_IMAGE="gcr.io/${PROJECT_ID}/test-unsigned:v1.0.0"

docker build -t ${UNSIGNED_IMAGE} -f - . << 'EOF'
FROM nginx:alpine
RUN echo "Unsigned test" > /usr/share/nginx/html/index.html
EOF

docker push ${UNSIGNED_IMAGE}

# DO NOT sign this image

```

2. **Attempt to deploy unsigned image:**

```bash
kubectl run test-unsigned-app \
  --image=${UNSIGNED_IMAGE} \
  --namespace=project-ai-core \
  --labels="app=test-unsigned,test=validation" \
  2>&1 | tee evidence/test2-unsigned-rejection.txt
```

### Expected Result

❌ **FAIL (desired):** Pod creation is denied
```
Error from server: admission webhook "mutate.kyverno.svc-fail" denied the request:

policy require-kms-cosign-signatures/verify-kms-signature failed:
  image 'gcr.io/PROJECT_ID/test-unsigned:v1.0.0': signature verification failed
```

### Actual Result

```

# Document actual output here

```

### Capture Evidence

```bash

# Save rejection message (already captured above)

# Check Kyverno policy reports

kubectl get policyreport -n project-ai-core -o yaml > evidence/test2-policy-reports.yaml

# Save Kyverno audit logs

kubectl logs -n kyverno -l app=kyverno --tail=100 | grep "signature verification failed" > evidence/test2-kyverno-rejection.txt
```

### Verification

```bash

# Verify pod was NOT created

kubectl get pod test-unsigned-app -n project-ai-core 2>&1

# Should return: Error from server (NotFound): pods "test-unsigned-app" not found

```

---

## Test 3: Lateral Pod Communication (Should Fail)

### Objective

Verify that default-deny network policies block lateral communication between pods in different namespaces.

### Prerequisites

- Default-deny network policies applied to all production namespaces
- Two pods deployed in different namespaces

### Procedure

1. **Deploy test pods in different namespaces:**

```bash

# Deploy source pod in project-ai-core

kubectl run test-source \
  --image=busybox:latest \
  --namespace=project-ai-core \
  --command -- sleep 3600

# Deploy target pod in project-ai-security

kubectl run test-target \
  --image=nginx:alpine \
  --namespace=project-ai-security \
  --labels="app=test-target"

# Wait for pods to be running

kubectl wait --for=condition=Ready pod/test-source -n project-ai-core --timeout=60s
kubectl wait --for=condition=Ready pod/test-target -n project-ai-security --timeout=60s

# Get target pod IP

TARGET_IP=$(kubectl get pod test-target -n project-ai-security -o jsonpath='{.status.podIP}')
echo "Target IP: ${TARGET_IP}"
```

2. **Attempt lateral communication:**

```bash

# Try to connect from source to target

kubectl exec test-source -n project-ai-core -- wget -T 5 -O- http://${TARGET_IP}:80 2>&1 | tee evidence/test3-lateral-blocked.txt
```

### Expected Result

❌ **FAIL (desired):** Connection times out or is refused
```
Connecting to 10.x.x.x:80 (10.x.x.x:80)
wget: download timed out
command terminated with exit code 1
```

### Actual Result

```

# Document actual output here

```

### Capture Evidence

```bash

# Save network policy configuration

kubectl get networkpolicy -n project-ai-core -o yaml > evidence/test3-netpol-core.yaml
kubectl get networkpolicy -n project-ai-security -o yaml > evidence/test3-netpol-security.yaml

# Check for denied connections in kube-proxy logs (if available)

kubectl logs -n kube-system -l component=kube-proxy --tail=100 | grep DROP > evidence/test3-netpol-drops.txt

# Document pod network details

kubectl get pod test-source -n project-ai-core -o yaml > evidence/test3-source-pod.yaml
kubectl get pod test-target -n project-ai-security -o yaml > evidence/test3-target-pod.yaml
```

### Cleanup

```bash
kubectl delete pod test-source -n project-ai-core
kubectl delete pod test-target -n project-ai-security
```

---

## Test 4: Audit Log Deletion (Should Fail)

### Objective

Verify that audit logs in Cloud Storage cannot be deleted by cluster administrators.

### Prerequisites

- GKE audit logging enabled
- Logs being sent to Cloud Storage bucket
- IAM policies configured for log bucket

### Procedure

1. **Verify audit log bucket exists:**

```bash
export LOG_BUCKET="${PROJECT_ID}-audit-logs"
gsutil ls -b gs://${LOG_BUCKET}
```

2. **Attempt to delete audit logs (as cluster admin):**

```bash

# Try to delete logs from bucket

gsutil rm -r gs://${LOG_BUCKET}/logs_* 2>&1 | tee evidence/test4-log-deletion-denied.txt
```

3. **Attempt to delete lifecycle policy:**

```bash
gsutil lifecycle get gs://${LOG_BUCKET} > evidence/test4-lifecycle-before.json
gsutil lifecycle set /dev/null gs://${LOG_BUCKET} 2>&1 | tee evidence/test4-lifecycle-deletion-denied.txt
```

### Expected Result

❌ **FAIL (desired):** Access denied
```
AccessDeniedException: 403 Caller does not have storage.objects.delete access to the Google Cloud Storage object.
```

Or if using object retention:
```
BucketLockedException: 403 Locked objects cannot be deleted until retention policy expires
```

### Actual Result

```

# Document actual output here

```

### Capture Evidence

```bash

# Save IAM policy for bucket

gsutil iam get gs://${LOG_BUCKET} > evidence/test4-bucket-iam-policy.json

# Check bucket retention policy

gsutil retention get gs://${LOG_BUCKET} > evidence/test4-retention-policy.txt

# Verify logs are still present

gsutil ls gs://${LOG_BUCKET}/ > evidence/test4-logs-still-exist.txt
```

### Verification

```bash

# Verify lifecycle policy is still in place

gsutil lifecycle get gs://${LOG_BUCKET} > evidence/test4-lifecycle-after.json

# Compare before and after

diff evidence/test4-lifecycle-before.json evidence/test4-lifecycle-after.json

# Should show no differences

```

---

## Test 5: Privileged Container Deployment (Should Fail)

### Objective

Verify that Pod Security Admission (PSA) restricted mode prevents privileged containers.

### Prerequisites

- Namespace labeled with `pod-security.kubernetes.io/enforce: restricted`
- Kyverno policies enforcing security standards

### Procedure

1. **Verify namespace PSA labels:**

```bash
kubectl get namespace project-ai-core -o jsonpath='{.metadata.labels}' | jq .
```

2. **Attempt to deploy privileged container:**

```bash
cat << EOF | kubectl apply -f - 2>&1 | tee evidence/test5-privileged-denied.txt
apiVersion: v1
kind: Pod
metadata:
  name: test-privileged
  namespace: project-ai-core
spec:
  containers:

  - name: privileged-container

    image: nginx:alpine
    securityContext:
      privileged: true
EOF
```

3. **Also test with hostPath volume:**

```bash
cat << EOF | kubectl apply -f - 2>&1 | tee evidence/test5-hostpath-denied.txt
apiVersion: v1
kind: Pod
metadata:
  name: test-hostpath
  namespace: project-ai-core
spec:
  containers:

  - name: hostpath-container

    image: nginx:alpine
    volumeMounts:

    - mountPath: /host

      name: host-volume
  volumes:

  - name: host-volume

    hostPath:
      path: /
      type: Directory
EOF
```

### Expected Result

❌ **FAIL (desired):** Pod creation is denied by PSA or Kyverno
```
Error from server (Forbidden): error when creating "STDIN": pods "test-privileged" is forbidden:
violates PodSecurity "restricted:latest": privileged (container "privileged-container" must not set securityContext.privileged=true)
```

### Actual Result

```

# Document actual output here

```

### Capture Evidence

```bash

# Save namespace security configuration

kubectl get namespace project-ai-core -o yaml > evidence/test5-namespace-psa.yaml

# Check Kyverno policy reports

kubectl get policyreport -n project-ai-core -o yaml > evidence/test5-policy-reports.yaml

# Verify no privileged pods exist

kubectl get pods -n project-ai-core -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].securityContext.privileged}{"\n"}{end}' > evidence/test5-no-privileged-pods.txt
```

### Verification

```bash

# Verify pods were NOT created

kubectl get pod test-privileged -n project-ai-core 2>&1
kubectl get pod test-hostpath -n project-ai-core 2>&1

# Both should return: Error from server (NotFound)

```

---

## Summary Checklist

After completing all tests, fill out this checklist:

### Test Results

- [ ] **Test 1:** Signed image deployment succeeded
- [ ] **Test 2:** Unsigned image deployment was denied
- [ ] **Test 3:** Lateral pod communication was blocked
- [ ] **Test 4:** Audit log deletion was denied
- [ ] **Test 5:** Privileged container deployment was denied

### Evidence Collected

- [ ] All test outputs captured in `evidence/` directory
- [ ] Screenshots of failures captured
- [ ] Kyverno logs collected
- [ ] Network policy verification logs collected
- [ ] GCP audit logs showing access denials collected

### Documentation Updated

- [ ] Test results added to `TEST_RESULTS.md`
- [ ] Claims in documentation updated based on test results
- [ ] Any failures documented with remediation steps

---

## Updating Claims Based on Results

### If All Tests Pass ✅

Update documentation to state:

- ✅ "Production-validated security controls"
- ✅ "Enterprise-tested best practices"
- ✅ "Verified forensic capability"

### If Any Tests Fail ❌

1. Document the failure in `TEST_RESULTS.md`
2. Remediate the issue
3. Re-run the failed test
4. Keep documentation claims qualified until all tests pass

---

## Evidence Directory Structure

```
evidence/
├── test1-signed-image-success.yaml
├── test1-kyverno-logs.txt
├── test2-unsigned-rejection.txt
├── test2-policy-reports.yaml
├── test2-kyverno-rejection.txt
├── test3-lateral-blocked.txt
├── test3-netpol-core.yaml
├── test3-netpol-security.yaml
├── test3-netpol-drops.txt
├── test3-source-pod.yaml
├── test3-target-pod.yaml
├── test4-log-deletion-denied.txt
├── test4-bucket-iam-policy.json
├── test4-retention-policy.txt
├── test4-logs-still-exist.txt
├── test4-lifecycle-before.json
├── test4-lifecycle-after.json
├── test5-privileged-denied.txt
├── test5-hostpath-denied.txt
├── test5-namespace-psa.yaml
├── test5-policy-reports.yaml
└── test5-no-privileged-pods.txt
```

---

## Automated Test Script

For convenience, a bash script is provided to run all tests:

```bash

#!/bin/bash

# Run: ./scripts/run-security-validation-tests.sh

set -e

# Source directory for evidence

EVIDENCE_DIR="evidence"
mkdir -p ${EVIDENCE_DIR}

echo "========================================"
echo "TK8S Security Validation Tests"
echo "========================================"
echo ""

# Test 1: Signed Image

echo "Test 1: Signed image deployment..."

# ... (implement full test)

# Test 2: Unsigned Image

echo "Test 2: Unsigned image rejection..."

# ... (implement full test)

# Test 3: Network Policy

echo "Test 3: Lateral communication block..."

# ... (implement full test)

# Test 4: Log Deletion

echo "Test 4: Audit log protection..."

# ... (implement full test)

# Test 5: Privileged Container

echo "Test 5: Privileged container denial..."

# ... (implement full test)

echo ""
echo "========================================"
echo "All tests complete. Review evidence/"
echo "========================================"
```

---

## Compliance Verification

For SOC 2, ISO 27001, and PCI DSS compliance, ensure:

1. All test evidence is timestamped
2. Test execution is documented with operator names
3. Failures are logged and remediated
4. Re-tests after remediation are documented
5. Evidence is stored in immutable storage
6. Test procedures are reviewed annually

---

## Support

If tests fail or you need assistance:

- Review remediation steps in each test section
- Check Kyverno policy status: `kubectl get clusterpolicy`
- Check network policy status: `kubectl get networkpolicy -A`
- Review GKE audit logging: `gcloud logging read`
- Consult `SECURITY_VERIFICATION_REPORT.md` for troubleshooting

---

**Document Version:** 1.0
**Last Updated:** 2026-02-12
**Status:** Initial draft - Requires validation testing
