# Security Governance and Ownership

**Document Version:** 1.0  
**Last Updated:** 2026-01-19  
**Owner:** Security Team  
**Review Frequency:** Quarterly

---

## Table of Contents

1. [Ownership and Responsibilities](#ownership-and-responsibilities)
2. [Security KPIs](#security-kpis)
3. [Waiver Process](#waiver-process)
4. [Override Authority](#override-authority)
5. [Local Development](#local-development)
6. [Downstream Integration](#downstream-integration)

---

## Ownership and Responsibilities

### Workflow Ownership

| Workflow | Primary Owner | Backup Owner | Responsibilities |
|----------|---------------|--------------|------------------|
| **Release Artifact Signing** | Security Team | DevOps Lead | Maintain Cosign integration, monitor signing success rate, rotate keys (if needed) |
| **SBOM Generation** | Security Team | Release Manager | Maintain Syft version, ensure SBOM completeness, handle format updates |
| **AI/ML Model Security** | Security Team + ML Lead | Principal Engineer | Tune scanner sensitivity, review false positives, update threat signatures |
| **Periodic Verification** | Security Team | DevOps Lead | Monitor nightly scans, triage vulnerability reports, maintain KPIs |

### Contact Information

| Role | GitHub Handle | Email | Escalation Path |
|------|---------------|-------|-----------------|
| **Security Lead** | @security-lead | projectaidevs@gmail.com | CTO → CEO |
| **DevOps Lead** | @devops-lead | projectaidevs@gmail.com | Engineering Director |
| **ML Lead** | @ml-lead | projectaidevs@gmail.com | Principal Engineer |
| **Release Manager** | @release-manager | projectaidevs@gmail.com | Engineering Director |

### Responsibilities Matrix

#### Security Team
- ✅ **Approve security waivers** (sole authority)
- ✅ **Review security findings** from all workflows
- ✅ **Maintain threat model** and risk assessments
- ✅ **Respond to security incidents** within SLA
- ✅ **Update security policies** and governance docs
- ✅ **Train developers** on security best practices

#### DevOps Lead
- ✅ **Maintain workflow infrastructure** (Actions, runners)
- ✅ **Monitor workflow success rates** and performance
- ✅ **Update tool versions** (Cosign, Syft, ModelScan)
- ✅ **Troubleshoot CI/CD failures** not related to security findings
- ✅ **Optimize workflow performance** (caching, parallelization)

#### ML Lead
- ✅ **Review AI/ML security findings** with security team
- ✅ **Validate false positives** for model security scans
- ✅ **Recommend model serialization** best practices
- ✅ **Approve model-specific waivers** (with security team)

#### Release Manager
- ✅ **Verify SBOM presence** in all releases
- ✅ **Confirm signatures attached** to release assets
- ✅ **Communicate security status** to stakeholders
- ✅ **Coordinate security fixes** in release cycle

#### All Developers
- ✅ **Fix security findings** in their code/models
- ✅ **Request waivers** through proper process
- ✅ **Follow security policies** and best practices
- ✅ **Report security issues** via private channels

---

## Security KPIs

### Current Targets

| KPI | Target | Measurement | Owner | Review Frequency |
|-----|--------|-------------|-------|------------------|
| **Signed Release Coverage** | 100% | % of releases with .sig files | Security Team | Weekly |
| **SBOM Coverage** | 100% | % of releases with SBOM | Security Team | Weekly |
| **Mean Time to Remediate (MTTR) - Critical** | 48 hours | Time from detection to fix merged | Security Team | Daily |
| **MTTR - High** | 7 days | Time from detection to fix merged | Security Team | Weekly |
| **MTTR - Medium** | 30 days | Time from detection to fix merged | Security Team | Monthly |
| **AI Model Scan Coverage** | 100% | % of model changes scanned before merge | ML Lead | Weekly |
| **False Positive Rate - AI/ML** | <20% | % of findings marked as false positive | ML Lead | Monthly |
| **Workflow Success Rate** | >95% | % of successful workflow runs | DevOps Lead | Daily |
| **Vulnerability Backlog** | <10 open | Number of unresolved critical/high | Security Team | Daily |
| **Waiver Active Count** | <5 active | Number of active security waivers | Security Team | Weekly |

### KPI Dashboard

**Automated reporting:** `.github/workflows/periodic-security-verification.yml`  
**Frequency:** Nightly (3 AM UTC)  
**Location:** Workflow artifacts + GitHub Actions summary

**Manual review:** Monthly security team meeting  
**Escalation:** CTO notified if any KPI red for >7 days

### Historical Tracking

KPI data is retained in workflow artifacts for 365 days:
```bash
# Download historical KPIs
gh run list --workflow=periodic-security-verification.yml --limit 12
gh run download <run-id> --name security-kpis-<number>
```

---

## Waiver Process

### When to Request a Waiver

**Valid reasons:**
- ✅ **Known false positive** with clear technical justification
- ✅ **Legacy system** with documented migration plan
- ✅ **Tool limitation** reported upstream with workaround
- ✅ **Temporary blocker** with time-bound resolution plan

**Invalid reasons:**
- ❌ "We need to ship faster" - security is not negotiable
- ❌ "I don't understand the finding" - request help instead
- ❌ "It's probably fine" - proper analysis required
- ❌ "Everyone else does this" - not a valid security argument

### Waiver Request Process

#### Step 1: Create Tracking Issue

```markdown
Title: [WAIVER REQUEST] Brief description

## Security Finding
- Workflow: (signing/sbom/ai-model)
- File/Scope: (specific file or check)
- Severity: (critical/high/medium)
- Finding: (exact error message or finding)

## Justification
(Clear technical explanation of why waiver is needed)

## Mitigation Plan
- What additional controls are in place?
- What is the timeline to fix properly?
- What is the residual risk?

## Requested Duration
- Start: YYYY-MM-DD
- End: YYYY-MM-DD (max 90 days)

## Approver
@security-lead (tag security team for review)
```

#### Step 2: Security Review

**Security team reviews within 48 hours:**
1. Validate justification is technically sound
2. Assess residual risk
3. Confirm mitigation plan is adequate
4. Verify tracking issue exists
5. Approve or request changes

**Approval criteria:**
- Technical justification is clear and correct
- Residual risk is acceptable
- Mitigation controls are in place
- Duration is reasonable (≤90 days)
- Tracking issue with fix plan exists

#### Step 3: Add Waiver to Configuration

**Security team adds to `.github/security-waivers.yml`:**

```yaml
waivers:
  - id: descriptive-id-2026-01
    type: ai-model
    scope: data/ai_persona/model.pkl
    justification: |
      Clear explanation of why waiver is needed.
      Technical details and risk analysis.
    approver: security-lead
    created: 2026-01-19
    expires: 2026-04-19  # Max 90 days
    issue: https://github.com/IAmSoThirsty/Project-AI/issues/123
```

#### Step 4: CI Enforcement

**Waiver is automatically enforced by CI:**
- Workflow checks `.github/security-waivers.yml`
- Validates waiver is not expired
- Applies waiver to specific finding
- Logs waiver usage in workflow output

#### Step 5: Expiry and Renewal

**On expiry date:**
- CI automatically rejects the finding
- Developer must fix the issue OR request new waiver
- New waiver requires fresh security review

**Renewal process:**
- Must provide update on fix progress
- Security team reviews residual risk
- Max total waiver time: 180 days (two 90-day periods)
- After 180 days, issue must be fixed or permanently accepted with documented exception

### Waiver Labels (Alternative Mechanism)

**For PR-specific waivers:**

Add label to PR: `security-waiver:<type>`

Example labels:
- `security-waiver:ai-model-false-positive`
- `security-waiver:sbom-generation-issue`

**PR description must include:**
```markdown
## Security Waiver Request
- Type: ai-model
- Justification: (clear explanation)
- Approved by: @security-lead
- Tracking issue: #123
```

**Label permissions:**
- Only security team can add waiver labels
- Automated checks verify label was added by authorized user
- PR requires security team approval before merge

---

## Override Authority

### Authorization Levels

| Level | Authority | Use Case | Required Approvals |
|-------|-----------|----------|-------------------|
| **L1: Developer** | Request waiver | False positive, need help | 0 (request only) |
| **L2: Team Lead** | Review findings | Validate technical details | 1 (self) |
| **L3: Security Team** | Approve waivers | Grant temporary exceptions | 1 (security team member) |
| **L4: Security Lead** | Emergency override | Critical production issue | 1 (security lead) + incident report |
| **L5: CTO** | Policy exception | Permanent exception with risk acceptance | 1 (CTO) + risk acknowledgment document |

### Emergency Override Procedure

**Use only for critical production incidents:**

1. **Security Lead approval** (verbal OK initially)
2. **Add override label** to PR: `security-override:emergency`
3. **Merge with documentation** in PR description:
   ```markdown
   ## Emergency Security Override
   - Approved by: @security-lead (verbal approval at HH:MM UTC)
   - Incident: #<incident-number>
   - Justification: (brief reason)
   - Post-incident review: Scheduled for YYYY-MM-DD
   ```
4. **Incident report required** within 24 hours
5. **Post-incident review** within 1 week

**Audit trail:**
- All overrides logged in workflow runs
- Monthly audit of override usage
- Quarterly review with executive team

### Allowed Failure Modes (Permanent Suppressions)

**Encoded in `.github/security-waivers.yml`:**

```yaml
allowed_failures:
  ai_model:
    - pattern: "torch.load.*weights_only=True"
      reason: "PyTorch safe loading is secure"
      severity: medium
```

**Governance:**
- Security team maintains allowed failures list
- Reviewed quarterly
- Each entry requires:
  - Technical justification
  - Security team approval
  - Documentation in threat model

**Warning signs of normalization:**
- ⚠️ Allowed failures list growing rapidly
- ⚠️ Developers copying patterns without understanding
- ⚠️ Vague justifications ("it's fine", "everyone does this")
- ⚠️ No attempt to fix underlying issues

**Prevention:**
- Monthly review of allowed failures usage
- Require specific patterns (not wildcards)
- Sunset old entries when better solutions exist
- Training on secure alternatives

---

## Local Development

### Local SBOM Generation

**Prerequisites:**
```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Verify installation
syft version
```

**Generate SBOM locally:**
```bash
# Full SBOM (same as CI)
syft scan dir:. \
  --scope all-layers \
  --output cyclonedx-json \
  --file sbom-local.cyclonedx.json

# Human-readable format
syft scan dir:. --output table

# Python dependencies only
syft scan file:requirements.txt --output table

# Specific directory
syft scan dir:./src --output table
```

**Scan for vulnerabilities:**
```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan SBOM
grype sbom:sbom-local.cyclonedx.json

# Scan directory directly
grype dir:.

# Filter by severity
grype dir:. --fail-on critical
```

**Common issues:**

| Error | Fix |
|-------|-----|
| "No package manager files found" | Run from repo root, not subdirectory |
| "Failed to catalog" | Check file permissions, ensure dependencies installed |
| Timeout | Use `--scope squashed` instead of `--scope all-layers` |

### Local Release Signing

**Prerequisites:**
```bash
# Install Cosign
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Verify installation
cosign version
```

**Build and sign locally:**
```bash
# Build Python package
python -m build

# Sign artifact (uses GitHub login for identity)
cosign sign-blob --yes dist/project_ai-1.0.0-py3-none-any.whl \
  --output-signature=dist/project_ai-1.0.0-py3-none-any.whl.sig \
  --output-certificate=dist/project_ai-1.0.0-py3-none-any.whl.pem

# Verify signature
cosign verify-blob dist/project_ai-1.0.0-py3-none-any.whl \
  --signature=dist/project_ai-1.0.0-py3-none-any.whl.sig \
  --certificate=dist/project_ai-1.0.0-py3-none-any.whl.pem \
  --certificate-identity-regexp=".*" \
  --certificate-oidc-issuer="https://github.com/login/oauth"
```

**Note:** Local signing uses your GitHub identity, not the repository's CI identity. For production releases, always use CI/CD signing.

### Local AI/ML Security Scanning

**Prerequisites:**
```bash
# Install ModelScan
pip install modelscan

# Verify installation
modelscan --help
```

**Scan models locally:**
```bash
# Scan single model
modelscan scan -p data/ai_persona/model.pkl

# Scan directory
modelscan scan -p data/ai_persona/

# JSON output for parsing
modelscan scan -p data/ai_persona/model.pkl -o results.json

# Scan all pickle files
find data -name "*.pkl" -exec modelscan scan -p {} \;
```

**Run custom security script:**
```bash
# Extract script from workflow (one-time setup)
cat > ai_ml_security_scan_local.py << 'EOF'
# (Copy the embedded script from ai-model-security.yml)
EOF

# Run locally
python ai_ml_security_scan_local.py
```

**Test unsafe deserialization detection:**
```bash
# Use grep to find patterns (quick check)
grep -r "pickle.loads\|eval(\|exec(" src/ tools/

# Use Bandit for comprehensive scan
pip install bandit
bandit -r src/ -f screen
```

### Reproducing CI Failures

**Steps to debug workflow failures locally:**

1. **Get the exact workflow version:**
   ```bash
   gh run view <run-id> --log > workflow-log.txt
   # Check tool versions in log
   ```

2. **Match tool versions:**
   ```bash
   # Install same Syft version as CI
   syft version  # Check CI log for version
   
   # Install specific version if needed
   curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | \
     sh -s -- -b /usr/local/bin v0.XX.Y
   ```

3. **Reproduce scan:**
   ```bash
   # Use exact same command from workflow
   syft scan dir:. --scope all-layers --output cyclonedx-json
   ```

4. **Check differences:**
   ```bash
   # Compare local vs CI results
   diff sbom-local.cyclonedx.json sbom-ci.cyclonedx.json
   ```

### Environment-Specific Testing

**Test different security profiles:**

```bash
# Permissive mode (feature branches)
export SECURITY_PROFILE=permissive
python ai_ml_security_scan_local.py

# Standard mode (PR to main)
export SECURITY_PROFILE=standard
python ai_ml_security_scan_local.py

# Strict mode (main/release)
export SECURITY_PROFILE=strict
python ai_ml_security_scan_local.py
```

---

## Downstream Integration

### Consuming Signed Artifacts

#### Python Package Installation with Verification

**Option 1: Manual verification before install**

```bash
# Download from GitHub release
gh release download v1.0.0

# Verify signature
cosign verify-blob project_ai-1.0.0-py3-none-any.whl \
  --signature=project_ai-1.0.0-py3-none-any.whl.sig \
  --certificate=project_ai-1.0.0-py3-none-any.whl.pem \
  --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Verify checksum
sha256sum -c SHA256SUMS

# Install if verification passes
pip install project_ai-1.0.0-py3-none-any.whl
```

**Option 2: Automated verification script**

```bash
#!/bin/bash
# verify-and-install.sh

RELEASE_TAG="v1.0.0"
REPO="IAmSoThirsty/Project-AI"

# Download release artifacts
gh release download "$RELEASE_TAG" -R "$REPO"

# Find wheel file
WHEEL=$(ls project_ai-*.whl | head -1)

# Verify signature
echo "Verifying signature..."
if ! cosign verify-blob "$WHEEL" \
  --signature="${WHEEL}.sig" \
  --certificate="${WHEEL}.pem" \
  --certificate-identity-regexp="https://github.com/${REPO}/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"; then
  echo "❌ Signature verification failed!"
  exit 1
fi

# Verify checksum
echo "Verifying checksum..."
if ! sha256sum -c SHA256SUMS 2>&1 | grep -q "$WHEEL: OK"; then
  echo "❌ Checksum verification failed!"
  exit 1
fi

echo "✅ Verification successful! Installing..."
pip install "$WHEEL"
```

#### Docker Integration

```dockerfile
# Dockerfile with signature verification
FROM python:3.11-slim

# Install Cosign
RUN curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64" && \
    mv cosign-linux-amd64 /usr/local/bin/cosign && \
    chmod +x /usr/local/bin/cosign

# Download and verify
ARG RELEASE_TAG=v1.0.0
COPY verify-and-install.sh /tmp/
RUN /tmp/verify-and-install.sh

# Application runs with verified package
CMD ["project-ai"]
```

### Consuming SBOMs

#### Vulnerability Scanning in CI/CD

```yaml
# .github/workflows/dependency-check.yml (downstream repo)
name: Check Dependency Vulnerabilities

on: [push, pull_request]

jobs:
  scan-dependencies:
    runs-on: ubuntu-latest
    steps:
      - name: Download Project-AI SBOM
        run: |
          gh release download v1.0.0 \
            -R IAmSoThirsty/Project-AI \
            -p "sbom-comprehensive.cyclonedx.json"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Verify SBOM signature
        run: |
          gh release download v1.0.0 \
            -R IAmSoThirsty/Project-AI \
            -p "sbom-comprehensive.cyclonedx.json.sig" \
            -p "sbom-comprehensive.cyclonedx.json.pem"
          
          cosign verify-blob sbom-comprehensive.cyclonedx.json \
            --signature=sbom-comprehensive.cyclonedx.json.sig \
            --certificate=sbom-comprehensive.cyclonedx.json.pem \
            --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
            --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
      
      - name: Scan for vulnerabilities
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
          grype sbom:sbom-comprehensive.cyclonedx.json --fail-on high
```

#### License Compliance Check

```bash
#!/bin/bash
# check-licenses.sh

# Download SBOM
gh release download v1.0.0 \
  -R IAmSoThirsty/Project-AI \
  -p "sbom-comprehensive.cyclonedx.json"

# Extract licenses
LICENSES=$(jq -r '.components[].licenses[]?.license.id' sbom-comprehensive.cyclonedx.json | sort -u)

# Check against allowed list
ALLOWED=("MIT" "Apache-2.0" "BSD-3-Clause" "ISC")
VIOLATIONS=()

while IFS= read -r license; do
  if [[ ! " ${ALLOWED[@]} " =~ " ${license} " ]]; then
    VIOLATIONS+=("$license")
  fi
done <<< "$LICENSES"

if [ ${#VIOLATIONS[@]} -gt 0 ]; then
  echo "❌ License violations found:"
  printf '%s\n' "${VIOLATIONS[@]}"
  exit 1
else
  echo "✅ All licenses approved"
fi
```

#### Supply Chain Policy Enforcement (OPA)

```rego
# policy.rego
package supply_chain

import future.keywords.if
import future.keywords.in

# Deny if artifact is not signed
deny[msg] {
    not input.signature_verified
    msg := "Artifact must be cryptographically signed"
}

# Deny if SBOM is missing
deny[msg] {
    not input.sbom_present
    msg := "SBOM must be present for all artifacts"
}

# Deny if critical vulnerabilities exist
deny[msg] {
    input.sbom.vulnerabilities.critical > 0
    msg := sprintf("Critical vulnerabilities found: %d", [input.sbom.vulnerabilities.critical])
}

# Warn if high vulnerabilities exist
warn[msg] {
    input.sbom.vulnerabilities.high > 0
    msg := sprintf("High vulnerabilities found: %d", [input.sbom.vulnerabilities.high])
}
```

```bash
# Evaluate policy
opa eval --data policy.rego --input input.json 'data.supply_chain.deny'
```

### Integration Patterns

#### Pattern 1: Continuous Monitoring

```yaml
# Monitor upstream releases
name: Check Upstream Updates

on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly Monday 9 AM

jobs:
  check-updates:
    runs-on: ubuntu-latest
    steps:
      - name: Get latest release
        id: upstream
        run: |
          LATEST=$(gh release list -R IAmSoThirsty/Project-AI --limit 1 | cut -f1)
          echo "version=$LATEST" >> "$GITHUB_OUTPUT"
      
      - name: Download and verify SBOM
        run: |
          gh release download "${{ steps.upstream.outputs.version }}" \
            -R IAmSoThirsty/Project-AI \
            -p "sbom-*"
          
          # Verify signature...
          # Scan for vulnerabilities...
          # Update if safe...
```

#### Pattern 2: Air-gapped Deployment

```bash
#!/bin/bash
# prepare-airgapped-deployment.sh

RELEASE="v1.0.0"

# Download all artifacts
gh release download "$RELEASE" -R IAmSoThirsty/Project-AI

# Verify everything
for artifact in *.whl *.tar.gz; do
  echo "Verifying $artifact..."
  cosign verify-blob "$artifact" \
    --signature="${artifact}.sig" \
    --certificate="${artifact}.pem" \
    --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
    --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
done

# Create deployment bundle
tar czf project-ai-${RELEASE}-verified.tar.gz \
  *.whl *.tar.gz *.sig *.pem \
  sbom-comprehensive.cyclonedx.json \
  SHA256SUMS

echo "✅ Verified deployment bundle created: project-ai-${RELEASE}-verified.tar.gz"
```

---

## References

- [Security Framework](../SECURITY_FRAMEWORK.md)
- [SBOM Policy](SBOM_POLICY.md)
- [Workflow Runbooks](SECURITY_WORKFLOW_RUNBOOKS.md)
- [Threat Model](THREAT_MODEL_SECURITY_WORKFLOWS.md)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-19 | Initial governance document |

---

**Contact:** projectaidevs@gmail.com  
**Classification:** INTERNAL
