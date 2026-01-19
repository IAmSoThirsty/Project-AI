# Security Workflow Failure Runbooks

**Purpose:** Quick reference guide for responding to security workflow failures  
**Audience:** On-call engineers, contributors, security team  
**Last Updated:** 2026-01-19

---

## 🚨 Quick Triage

| Workflow | Failure Impact | Response Time | Escalation |
|----------|----------------|---------------|------------|
| **Release Signing** | ⚠️ **HIGH** - Releases cannot be verified | 1 hour | Security team |
| **SBOM Generation** | 🟡 **MEDIUM** - Supply chain visibility lost | 4 hours | Release manager |
| **AI/ML Security** | 🔴 **CRITICAL** - Potential malicious model | 30 minutes | Security + Dev lead |

---

## 1️⃣ Release Artifact Signing Failures

### Workflow: `.github/workflows/sign-release-artifacts.yml`

### Common Failure Scenarios

#### ❌ Failure: Cosign Installation Failed

**Symptoms:**
```
Error: Failed to install Cosign
Unable to locate Cosign binary
```

**Root Cause:** Network issues or upstream release changes

**Resolution:**
```bash
# Check Cosign release availability
curl -I https://github.com/sigstore/cosign/releases/latest

# Workflow uses pinned version - check if it exists
# If not, update action version in workflow file
```

**Fix:**
1. Check if Cosign action version is outdated in workflow (line 26)
2. Update to latest: `sigstore/cosign-installer@v3.x.x`
3. Re-run workflow

**Prevention:** Pin to stable Cosign action version, not `@latest`

---

#### ❌ Failure: No Artifacts to Sign

**Symptoms:**
```
Error: No files found matching dist/*.whl
Signing failed: No artifacts in dist/
```

**Root Cause:** Python build failed before signing step

**Resolution:**
```bash
# Check build step logs
gh run view <run-id> --log

# Verify build dependencies installed
# Check pyproject.toml and setup.py are valid
```

**Fix:**
1. Review "Build Python packages" step logs
2. Fix any build errors (missing dependencies, syntax errors)
3. Verify `python -m build` succeeds locally
4. Push fix and re-run

**Prevention:** Add build verification in CI before signing step

---

#### ❌ Failure: Signature Verification Failed

**Symptoms:**
```
Error: Signature verification failed
Certificate identity does not match expected pattern
```

**Root Cause:** OIDC token identity mismatch or expired certificate

**Resolution:**
```bash
# Check workflow run details
gh run view <run-id>

# Verify repository name matches certificate pattern
# Pattern: https://github.com/IAmSoThirsty/Project-AI/*
```

**Fix:**
1. **DO NOT BYPASS VERIFICATION** - This is a security control
2. Check if workflow ran from a fork (should use fork's identity)
3. Verify `permissions: id-token: write` is set in workflow
4. Check Rekor transparency log: https://rekor.sigstore.dev/
5. If legitimate failure, re-run workflow to get fresh OIDC token

**Prevention:** Test signing in non-prod branch first

---

#### ❌ Failure: Upload to Release Failed

**Symptoms:**
```
Error: Failed to upload assets to release
403 Forbidden or 404 Not Found
```

**Root Cause:** Missing permissions or release doesn't exist

**Resolution:**
```bash
# Check if release exists
gh release view <tag>

# Verify workflow permissions
# Must have: contents: write
```

**Fix:**
1. Verify release was published before workflow ran
2. Check workflow has `contents: write` permission
3. For `workflow_dispatch`: ensure tag exists
4. Re-run workflow after confirming release exists

**Prevention:** Use `release: published` trigger, not `release: created`

---

### Emergency Procedures

#### 🚨 Critical: Release Published Without Signatures

**Impact:** Users cannot verify artifact authenticity

**Immediate Actions:**
1. **DO NOT DELETE RELEASE** - This breaks existing installations
2. Run manual signing workflow:
   ```bash
   gh workflow run sign-release-artifacts.yml \
     --ref main \
     -f tag=v1.0.0
   ```
3. Monitor workflow completion
4. Verify signatures uploaded to release
5. Post comment on release with verification instructions

**Post-Incident:**
1. Document why automatic signing failed
2. Add monitoring for signing workflow failures
3. Consider adding signing as branch protection rule
4. Update release checklist to verify signatures

---

#### 🔧 Manual Signing Procedure (Last Resort)

**Use only if CI/CD signing completely unavailable:**

```bash
# REQUIRES: Cosign installed locally, GitHub CLI authenticated

# 1. Download release artifacts
gh release download v1.0.0

# 2. Sign locally (will use GitHub login for identity)
for artifact in *.whl *.tar.gz; do
  cosign sign-blob --yes "$artifact" \
    --output-signature="${artifact}.sig" \
    --output-certificate="${artifact}.pem"
done

# 3. Generate checksums
sha256sum *.whl *.tar.gz > SHA256SUMS
cosign sign-blob --yes SHA256SUMS \
  --output-signature="SHA256SUMS.sig" \
  --output-certificate="SHA256SUMS.pem"

# 4. Upload to release
gh release upload v1.0.0 *.sig *.pem SHA256SUMS*

# 5. Add note to release
gh release edit v1.0.0 --notes-file - << 'EOF'
⚠️ **Manual Signing Note**
Artifacts were manually signed due to CI/CD issue.
Signatures are still valid and verifiable via Cosign.
EOF
```

**⚠️ IMPORTANT:** Manual signing should be documented in incident report

---

## 2️⃣ SBOM Generation Failures

### Workflow: `.github/workflows/sbom.yml`

### Common Failure Scenarios

#### ❌ Failure: Syft Installation Failed

**Symptoms:**
```
Error: Failed to download Syft
curl: Failed to connect
```

**Root Cause:** Network issues or Anchore CDN problems

**Resolution:**
```bash
# Check Syft availability
curl -I https://raw.githubusercontent.com/anchore/syft/main/install.sh

# Test installation locally
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /tmp/syft
```

**Fix:**
1. Retry workflow (transient network issue)
2. If persistent, check Anchore status page
3. Alternative: Install via GitHub release directly
4. Update workflow to use pre-built binaries

**Prevention:** Consider caching Syft binary in Actions cache

---

#### ❌ Failure: SBOM Generation Incomplete

**Symptoms:**
```
Error: No packages found in scan
SBOM file is empty or has 0 components
```

**Root Cause:** Syft didn't detect package files or wrong scan path

**Resolution:**
```bash
# Check if package files exist
ls -la requirements.txt pyproject.toml package.json

# Test Syft scan locally
syft scan dir:. --scope all-layers
```

**Fix:**
1. Verify `requirements.txt`, `pyproject.toml`, and `package.json` exist
2. Check Syft is scanning from repo root (`dir:.`)
3. Ensure `--scope all-layers` is used
4. Check for Syft version compatibility issues

**Prevention:** Add SBOM validation step to check component count > 0

---

#### ❌ Failure: SBOM Signing Failed

**Symptoms:**
```
Error: Failed to sign SBOM with Cosign
Signature generation failed
```

**Root Cause:** Same as artifact signing issues (OIDC, permissions)

**Resolution:** See "Release Artifact Signing Failures" section above

**Fix:**
1. Verify `id-token: write` permission
2. Check OIDC token validity
3. Re-run workflow for fresh token
4. Verify SBOM files exist before signing step

**Prevention:** Add pre-signing validation

---

#### ❌ Failure: Vulnerability Scan Timeout

**Symptoms:**
```
Error: Grype scan timed out
Resource exhausted
```

**Root Cause:** Large dependency tree or slow vulnerability database

**Resolution:**
```bash
# Check number of dependencies
jq '.components | length' sbom-comprehensive.cyclonedx.json

# Test Grype locally (with timeout)
timeout 300 grype sbom:sbom-comprehensive.cyclonedx.json
```

**Fix:**
1. Increase workflow timeout (default: 30 minutes)
2. Use `continue-on-error: true` for vulnerability scan step (already set)
3. Consider splitting scans (Python vs Node.js)
4. Update Grype to latest version

**Prevention:** This is marked as `continue-on-error`, should not fail workflow

---

### Emergency Procedures

#### 🚨 Critical: Release Published Without SBOM

**Impact:** Supply chain visibility lost, compliance issue

**Immediate Actions:**

1. Run manual SBOM generation:
   ```bash
   # Install Syft
   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
   
   # Clone repository at release tag
   git clone --depth 1 --branch v1.0.0 https://github.com/IAmSoThirsty/Project-AI
   cd Project-AI
   
   # Generate SBOM
   syft scan dir:. --scope all-layers \
     --output cyclonedx-json \
     --file sbom-comprehensive.cyclonedx.json
   
   # Sign SBOM
   cosign sign-blob --yes sbom-comprehensive.cyclonedx.json \
     --output-signature=sbom-comprehensive.cyclonedx.json.sig \
     --output-certificate=sbom-comprehensive.cyclonedx.json.pem
   
   # Upload to release
   gh release upload v1.0.0 sbom-comprehensive.cyclonedx.json*
   ```

2. Document in release notes that SBOM was generated manually
3. Verify SBOM signature works
4. Notify security team

**Post-Incident:**
1. Root cause analysis of SBOM workflow failure
2. Add monitoring for SBOM generation
3. Update release checklist to verify SBOM presence

---

## 3️⃣ AI/ML Model Security Failures

### Workflow: `.github/workflows/ai-model-security.yml`

### Common Failure Scenarios

#### ❌ Failure: ModelScan Installation Failed

**Symptoms:**
```
Error: Could not install modelscan
pip install modelscan failed
```

**Root Cause:** PyPI connectivity or dependency conflicts

**Resolution:**
```bash
# Check PyPI availability
curl -I https://pypi.org/simple/modelscan/

# Test installation locally
pip install modelscan
```

**Fix:**
1. Retry workflow (transient issue)
2. Check for dependency conflicts in workflow logs
3. Pin ModelScan version if unstable
4. Use alternative installation method

**Prevention:** Pin ModelScan version in workflow

---

#### ❌ Failure: Critical Security Issues Detected

**Symptoms:**
```
❌ Security scan FAILED: Critical or high severity issues found
🔴 Critical: Dangerous pattern '__reduce__' found in model.pkl
```

**Root Cause:** Malicious or unsafe model file detected

**Resolution:**
```bash
# THIS IS NOT A FALSE POSITIVE - INVESTIGATE IMMEDIATELY

# 1. Download scan report
gh run download <run-id> --name ai-ml-security-report-<sha>

# 2. Review findings
cat ai_ml_security_report.json | jq '.findings[] | select(.severity == "critical")'

# 3. Identify who added the model
git log --all --full-history -- <model-file>
```

**Fix - DO NOT SKIP THIS:**
1. **BLOCK PR IMMEDIATELY** - Do not merge
2. Review model file provenance (where did it come from?)
3. Check if model uses `__reduce__` legitimately (rare but possible)
4. Scan model file locally:
   ```bash
   modelscan scan -p data/ai_persona/model.pkl
   ```
5. If legitimate:
   - Document why `__reduce__` is needed
   - Add exception with security review approval
   - Implement additional controls (integrity checks, runtime monitoring)
6. If malicious:
   - Remove model file immediately
   - Check for other suspicious files in PR
   - Report to security team
   - Review author's other contributions

**Prevention:** 
- Require model files to have checksums
- Document model sources and training provenance
- Use safer serialization formats (ONNX, TensorFlow SavedModel)

---

#### ❌ Failure: Unsafe Deserialization Detected

**Symptoms:**
```
🟠 High: Unsafe deserialization in src/app/core/model_loader.py: pickle.loads()
```

**Root Cause:** Code uses unsafe deserialization without validation

**Resolution:**
```bash
# Review the specific code location
grep -n "pickle.loads" src/app/core/model_loader.py

# Check if there's input validation
git show <commit>:src/app/core/model_loader.py
```

**Fix:**
1. **If possible, replace pickle with safer alternative:**
   ```python
   # Instead of pickle, use:
   import joblib
   model = joblib.load(path)  # Still uses pickle but with safety checks
   
   # Or for PyTorch:
   import torch
   model = torch.load(path, weights_only=True)  # Safer
   ```

2. **If pickle is required, add validation:**
   ```python
   import pickle
   import hashlib
   
   # Verify model checksum before loading
   expected_hash = "abc123..."
   actual_hash = hashlib.sha256(open(model_path, 'rb').read()).hexdigest()
   if actual_hash != expected_hash:
       raise ValueError("Model integrity check failed")
   
   with open(model_path, 'rb') as f:
       model = pickle.load(f)
   ```

3. **If it's a false positive (loading from trusted source):**
   - Document why pickle is safe in this context
   - Add comment explaining trust model
   - Consider adding to allowlist (with security approval)

**Prevention:**
- Prefer ONNX, TensorFlow SavedModel, or HuggingFace formats
- Always verify model checksums
- Load models from trusted sources only

---

#### ❌ Failure: Scan Script Errors

**Symptoms:**
```
Error: Python script ai_ml_security_scan.py failed
ModuleNotFoundError or syntax error
```

**Root Cause:** Script dependencies missing or Python version mismatch

**Resolution:**
```bash
# Check Python version
python --version  # Should be 3.11

# Test script locally
cd .github/workflows
python ai_ml_security_scan.py
```

**Fix:**
1. Check Python version in workflow (should be 3.11)
2. Verify script dependencies are installed
3. Check for syntax errors in embedded script
4. Test script locally before pushing

**Prevention:** Add script validation tests

---

### Emergency Procedures

#### 🚨 CRITICAL: Malicious Model Detected in Main Branch

**Impact:** Production system may be compromised

**Immediate Actions (within 30 minutes):**

1. **STOP ALL DEPLOYMENTS** - Halt production rollouts immediately

2. **Quarantine the model:**
   ```bash
   # Create incident branch
   git checkout -b incident/malicious-model-$(date +%Y%m%d)
   
   # Remove malicious model
   git rm data/ai_persona/suspicious_model.pkl
   git commit -m "SECURITY: Remove malicious model file"
   
   # Force push to main (requires admin)
   git push origin incident/malicious-model-$(date +%Y%m%d)
   ```

3. **Create security advisory:**
   ```bash
   gh api repos/IAmSoThirsty/Project-AI/security-advisories \
     --method POST \
     --field summary="Malicious AI model detected" \
     --field severity="critical"
   ```

4. **Notify stakeholders:**
   - Security team (immediate)
   - Engineering leadership (within 1 hour)
   - Affected users (after mitigation)

5. **Forensic analysis:**
   ```bash
   # Who added the model?
   git log --all --full-history -- data/ai_persona/suspicious_model.pkl
   
   # What other files did they touch?
   git log --author="<author>" --name-only
   
   # Check for other suspicious patterns
   grep -r "__reduce__\|__setstate__\|exec\|eval" data/
   ```

6. **Containment:**
   - Revoke commit author's access if necessary
   - Review all PRs from same author
   - Scan all model files in repository
   - Check production systems for indicators of compromise

**Post-Incident (within 24 hours):**
1. Full security audit of model pipeline
2. Implement model signing and verification
3. Add model provenance tracking
4. Review access controls for model uploads
5. Incident report and lessons learned

**Communication Template:**
```
Subject: SECURITY INCIDENT - Malicious AI Model Detected

Timeline:
- [TIME] Model security scan detected critical issue
- [TIME] Malicious model quarantined
- [TIME] Code removed from repository
- [TIME] Security advisory published

Impact: [Describe if production was affected]

Mitigation: Malicious model removed, systems verified clean

Next Steps:
- Enhanced model security controls
- Full audit of model pipeline
- Review of access controls

Contact: projectaidevs@gmail.com for questions
```

---

## 📞 Escalation Matrix

| Issue Type | Severity | Initial Response | Escalation Contact | Escalation Time |
|------------|----------|------------------|-------------------|-----------------|
| **Signing failure** | High | On-call engineer | Security team | 1 hour |
| **SBOM missing** | Medium | Release manager | Security team | 4 hours |
| **Malicious model** | Critical | On-call engineer + Security | CTO/Security lead | 30 minutes |
| **False positive** | Low | Contributor | Dev team lead | Next business day |

---

## 🔧 Useful Commands

### Check Workflow Status
```bash
# List recent workflow runs
gh run list --workflow=sign-release-artifacts.yml --limit 5

# View specific run details
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### Manual Workflow Triggers
```bash
# Trigger signing workflow
gh workflow run sign-release-artifacts.yml -f tag=v1.0.0

# Trigger SBOM generation
gh workflow run sbom.yml

# Trigger AI/ML security scan
gh workflow run ai-model-security.yml
```

### Verification Commands
```bash
# Verify artifact signature
cosign verify-blob artifact.whl \
  --signature=artifact.whl.sig \
  --certificate=artifact.whl.pem \
  --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Verify SBOM signature
cosign verify-blob sbom-comprehensive.cyclonedx.json \
  --signature=sbom-comprehensive.cyclonedx.json.sig \
  --certificate=sbom-comprehensive.cyclonedx.json.pem \
  --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Scan SBOM for vulnerabilities
grype sbom:sbom-comprehensive.cyclonedx.json
```

---

## 📚 Additional Resources

- **Security Framework:** [docs/SECURITY_FRAMEWORK.md](../docs/SECURITY_FRAMEWORK.md)
- **SBOM Policy:** [docs/security/SBOM_POLICY.md](../docs/security/SBOM_POLICY.md)
- **Threat Model:** [docs/security/THREAT_MODEL_SECURITY_WORKFLOWS.md](../docs/security/THREAT_MODEL_SECURITY_WORKFLOWS.md)
- **Incident Response:** Contact projectaidevs@gmail.com

---

## 🔄 Continuous Improvement

**After each incident:**
1. Update this runbook with new scenarios
2. Add automation to prevent recurrence
3. Review and improve workflow error messages
4. Update monitoring and alerting

**Feedback:** Open issue with label `runbook-improvement`

---

**Last Updated:** 2026-01-19  
**Maintainer:** Security Team  
**Review Frequency:** Quarterly or after each incident
