# Security Validation Evidence Checklist

**Quick Reference for Contributors**

This checklist helps you determine if your PR requires runtime validation evidence and what you need to provide.

---

## Step 1: Does Your PR Require Evidence?

Check your PR description, commit messages, code comments, and documentation for these phrases:

### Prohibited Claims (Require Evidence)

- [ ] "Production-ready"
- [ ] "Enterprise best practices"
- [ ] "Complete forensic capability"
- [ ] "Runtime enforcement"
- [ ] "Operational security"
- [ ] "Admission control enforcement"
- [ ] "Policy enforcement validated"
- [ ] "Security hardening complete"
- [ ] Any similar assertion of runtime/operational enforcement

**If you checked ANY box above, proceed to Step 2. Otherwise, proceed to Step 3.**

---

## Step 2: Provide ALL Five Runtime Validations

You MUST provide evidence for ALL five validations. Partial evidence is NOT acceptable.

### ✅ Validation 1: Unsigned Image Admission Denial

**What to do:**
1. Deploy an unsigned container image to your cluster
2. Capture the admission controller denial output
3. Take a screenshot or copy the full error message
4. Note the timestamp (UTC)

**Example command:**
```bash
kubectl apply -f unsigned-image-deployment.yaml
```

**Expected output (example):**
```
Error from server (Forbidden): admission webhook "image-signing.validation" denied the request: 
Image "example.com/app:latest" is not signed with a trusted key
```

**Evidence to include in PR:**
- [ ] Screenshot or log output
- [ ] Timestamp (UTC): _______________
- [ ] Command used: _______________

---

### ✅ Validation 2: Signed Image Admission Success

**What to do:**
1. Deploy a properly signed container image to your cluster
2. Capture the admission controller acceptance output
3. Verify the pod is running
4. Take a screenshot or copy the output
5. Note the timestamp (UTC)

**Example commands:**
```bash
kubectl apply -f signed-image-deployment.yaml
kubectl get pods
```

**Expected output (example):**
```
deployment.apps/secure-app created
NAME                          READY   STATUS    RESTARTS   AGE
secure-app-5d8f9c7b6d-x4k2p   1/1     Running   0          5s
```

**Evidence to include in PR:**
- [ ] Screenshot or log output
- [ ] Timestamp (UTC): _______________
- [ ] Command used: _______________

---

### ✅ Validation 3: Privileged Container Denial

**What to do:**
1. Create a deployment with `securityContext.privileged: true`
2. Attempt to deploy it
3. Capture the admission controller denial output
4. Take a screenshot or copy the error message
5. Note the timestamp (UTC)

**Example command:**
```bash
kubectl apply -f privileged-deployment.yaml
```

**Expected output (example):**
```
Error from server (Forbidden): admission webhook "pod-security.validation" denied the request: 
Privileged containers are not allowed. SecurityContext.privileged must be false or unset
```

**Evidence to include in PR:**
- [ ] Screenshot or log output
- [ ] Timestamp (UTC): _______________
- [ ] Command used: _______________

---

### ✅ Validation 4: Cross-Namespace/Lateral Communication Denial

**What to do:**
1. Create pods in two different namespaces (or same namespace with restrictive policies)
2. Attempt to communicate from one pod to a service in another namespace
3. Capture the network policy denial (connection timeout, DNS failure, or rejection)
4. Take a screenshot or copy the output
5. Note the timestamp (UTC)

**Example commands:**
```bash
kubectl exec -n namespace-a pod-a -- curl http://service-b.namespace-b.svc.cluster.local
kubectl logs -n namespace-a pod-a
```

**Expected output (example):**
```
curl: (28) Connection timed out after 10001 milliseconds
[ERROR] Failed to connect to namespace-b service: Connection refused
```

**Evidence to include in PR:**
- [ ] Screenshot or log output
- [ ] Timestamp (UTC): _______________
- [ ] Commands used: _______________
- [ ] Network policy configuration: _______________

---

### ✅ Validation 5: Log Deletion Prevention

**What to do:**
1. Exec into a running pod
2. Attempt to delete application logs
3. Capture the system response (denial or detection)
4. Check audit logs for the attempt
5. Take a screenshot or copy the output
6. Note the timestamp (UTC)

**Example commands:**
```bash
kubectl exec -n production pod-app -- rm -rf /var/log/app/*
kubectl logs -n kube-system audit-logger | grep "log-deletion-attempt"
```

**Expected output (example):**
```
rm: cannot remove '/var/log/app/app.log': Operation not permitted
2026-02-12T16:00:00Z WARNING User attempted unauthorized log deletion: pod=production/pod-app
```

**Evidence to include in PR:**
- [ ] Screenshot or log output
- [ ] Timestamp (UTC): _______________
- [ ] Commands used: _______________
- [ ] Audit log entry: _______________

---

## Step 3: Use Safe Framing Language

If you did NOT check any boxes in Step 1, or if you cannot provide ALL five validations, use ONLY these approved phrases:

### ✅ Approved Framing

- "Implementation aligns with enterprise hardening patterns."
- "Validation tests confirm configuration correctness."
- "Full adversarial validation is ongoing."
- "This PR implements security controls as per industry standards."
- "Configuration has been reviewed for compliance with best practices."
- "Automated tests validate the security configuration."

### ❌ Prohibited Framing (Without Evidence)

- "Production-ready security enforcement"
- "Complete runtime validation"
- "Operational security hardening complete"
- "Enterprise-grade admission control"
- "Forensic-grade audit trail active"

---

## Step 4: Complete the PR Template

When you open your PR, complete the **"Runtime Validation Evidence"** section:

1. Select YES or NO for whether you're making runtime enforcement claims
2. If YES, attach evidence for ALL five validations
3. If NO, ensure you're using safe framing language only
4. Check the certification boxes
5. Submit your PR

---

## Step 5: Reviewer Checklist

If you're reviewing a PR, verify:

- [ ] PR checked for prohibited claims in title, description, code, and docs
- [ ] If claims are made, ALL five validations are present
- [ ] Evidence is authentic (logs are complete, timestamps reasonable, commands valid)
- [ ] If evidence is incomplete, PR uses safe framing language only
- [ ] PR complies with [Security Validation Claims Policy](SECURITY_VALIDATION_POLICY.md)

---

## Common Questions

### Q: What if I only have 3 out of 5 validations?

**A:** Either complete the remaining 2 validations, or reframe your claims using safe language. Partial evidence is not acceptable.

### Q: Can I claim "partial production-readiness"?

**A:** No. Either you have complete evidence and can claim production-readiness, or you use safe framing language.

### Q: What if my PR doesn't involve security at all?

**A:** If your PR makes no security or runtime enforcement claims, you don't need to provide any runtime validation evidence. Simply select "NO" in the PR template.

### Q: Can I provide evidence in a follow-up PR?

**A:** No. Evidence must be included in the PR that makes the claims. You can submit the PR with safe framing language now, then submit a separate PR with complete evidence later.

### Q: What if I'm working on a test environment?

**A:** The same policy applies. You must have a test environment that supports all five validations if you want to claim runtime enforcement.

---

## Need Help?

- Read the full policy: [SECURITY_VALIDATION_POLICY.md](SECURITY_VALIDATION_POLICY.md)
- Open a discussion: [GitHub Discussions](https://github.com/IAmSoThirsty/Project-AI/discussions)
- Ask in your PR: Reviewers can provide guidance

---

**Remember:** When in doubt, use safe framing language. It's always acceptable to say "validation is ongoing" rather than claim completion without evidence.
