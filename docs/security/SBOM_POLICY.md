# Software Bill of Materials (SBOM) Policy

**Document Version:** 1.0  
**Last Updated:** 2026-01-19  
**Owner:** Project-AI Security Team

---

## 1. Overview

This document defines the policy for generating, publishing, and verifying Software Bill of Materials (SBOM) for Project-AI. SBOMs provide transparency into software components and dependencies, enabling security analysis, license compliance, and supply chain risk management.

---

## 2. Purpose and Scope

### 2.1 Purpose

- **Supply Chain Security:** Enable identification of vulnerable components
- **License Compliance:** Track open-source licenses across dependencies
- **Risk Management:** Understand third-party dependency exposure
- **Regulatory Compliance:** Meet NTIA minimum elements and NIST SP 800-218 requirements
- **Transparency:** Provide stakeholders visibility into software composition

### 2.2 Scope

SBOM generation covers:
- Python dependencies (from `requirements.txt`, `pyproject.toml`)
- Node.js dependencies (from `package.json`)
- Binary artifacts in repository
- System-level dependencies (where applicable)
- Model files and data artifacts (metadata only)

---

## 3. SBOM Format and Standards

### 3.1 Format

**Primary Format:** CycloneDX 1.5 JSON

**Rationale:**
- Industry standard maintained by OWASP
- Machine-readable JSON format
- Comprehensive vulnerability database integration
- Supports nested dependencies and component relationships

**Alternative Formats (on request):**
- SPDX 2.3 (Software Package Data Exchange)
- CycloneDX XML

### 3.2 Standards Compliance

| Standard | Status | Details |
|----------|--------|---------|
| **NTIA Minimum Elements** | ✅ Compliant | All 7 baseline fields included |
| **CycloneDX 1.5 Spec** | ✅ Compliant | Full schema compliance |
| **NIST SP 800-218** | ✅ Compliant | SSDF secure software development |
| **OWASP SCVS** | ✅ Compliant | Software Component Verification Standard |
| **EO 14028** | ✅ Compliant | US Executive Order on cybersecurity |

### 3.3 NTIA Minimum Elements

All SBOMs include:
1. **Supplier Name** - Component author/vendor
2. **Component Name** - Package name
3. **Version** - Semantic version or commit hash
4. **Other Unique Identifiers** - Package URLs (purl), CPE
5. **Dependency Relationships** - Component hierarchy
6. **Author of SBOM Data** - GitHub Actions + Syft
7. **Timestamp** - Generation date/time in UTC

---

## 4. SBOM Generation

### 4.1 Generation Tool

**Tool:** [Syft](https://github.com/anchore/syft) by Anchore

**Version Requirements:** Latest stable release

**Configuration:**
```bash
syft scan dir:. \
  --scope all-layers \
  --output cyclonedx-json \
  --file sbom-comprehensive.cyclonedx.json \
  --source-name "project-ai" \
  --source-version "<git-sha>"
```

### 4.2 Generation Triggers

SBOMs are automatically generated on:

| Event | Frequency | Retention |
|-------|-----------|-----------|
| **Push to main branch** | Every commit | 90 days (artifacts) |
| **Release published** | Every release | Permanent (release assets) |
| **Manual workflow dispatch** | On-demand | 90 days (artifacts) |

### 4.3 Generated Artifacts

Each SBOM generation produces:

| File | Description |
|------|-------------|
| `sbom-comprehensive.cyclonedx.json` | Complete SBOM (all dependencies) |
| `sbom-python.cyclonedx.json` | Python dependencies only |
| `sbom-nodejs.cyclonedx.json` | Node.js dependencies only |
| `sbom-report.txt` | Human-readable dependency list |
| `sbom-metadata.json` | Generation metadata (timestamp, commit, etc.) |
| `sbom-checksums.txt` | SHA-256 checksums for all files |
| `*.sig` | Sigstore Cosign signatures |
| `*.pem` | Sigstore certificates for verification |

---

## 5. SBOM Content

### 5.1 Component Information

Each component includes:
- **Name and Version** - Exact package identifier
- **Package URL (purl)** - Standardized identifier
- **License** - SPDX license identifier
- **Supplier** - Vendor or maintainer
- **Hashes** - SHA-256, SHA-512 checksums
- **Source Repository** - GitHub/GitLab URL (if available)
- **Dependencies** - Direct and transitive dependencies

### 5.2 Metadata

SBOM metadata includes:
- **Repository:** `IAmSoThirsty/Project-AI`
- **Commit SHA:** Full git commit hash
- **Branch:** Branch name (main, develop, etc.)
- **Timestamp:** UTC generation time
- **Generator:** Syft version
- **Format:** CycloneDX version

### 5.3 Exclusions

The following are **not** included in SBOM:
- Development-only dependencies (unless explicitly requested)
- Test fixtures and mock data
- Documentation assets
- Internal tools not shipped in releases
- Sensitive configuration files

---

## 6. SBOM Publication

### 6.1 Release Assets

For every GitHub release, the following SBOM files are attached:
- `sbom-comprehensive.cyclonedx.json` (+ signature + certificate)
- `sbom-python.cyclonedx.json`
- `sbom-nodejs.cyclonedx.json`
- `sbom-report.txt`
- `sbom-checksums.txt` (+ signature + certificate)
- `sbom-metadata.json`
- `SBOM_SUMMARY.md`

### 6.2 CI/CD Artifacts

On every main branch push:
- SBOM uploaded as GitHub Actions artifact
- Retention: 90 days
- Naming: `sbom-<commit-sha>`

### 6.3 Public Access

- **Release SBOMs:** Publicly accessible via GitHub Releases
- **CI Artifacts:** Available to authenticated users with repository access
- **API Access:** Available via GitHub REST API

---

## 7. SBOM Verification

### 7.1 Signature Verification

All SBOMs are signed using Sigstore Cosign with keyless signing.

**Verify SBOM Signature:**
```bash
# Install Cosign
curl -O -L "https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64"
sudo mv cosign-linux-amd64 /usr/local/bin/cosign
sudo chmod +x /usr/local/bin/cosign

# Verify signature
cosign verify-blob sbom-comprehensive.cyclonedx.json \
  --signature=sbom-comprehensive.cyclonedx.json.sig \
  --certificate=sbom-comprehensive.cyclonedx.json.pem \
  --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"
```

### 7.2 Checksum Verification

**Verify File Integrity:**
```bash
# Verify checksum signature first
cosign verify-blob sbom-checksums.txt \
  --signature=sbom-checksums.txt.sig \
  --certificate=sbom-checksums.txt.pem \
  --certificate-identity-regexp="https://github.com/IAmSoThirsty/Project-AI/*" \
  --certificate-oidc-issuer="https://token.actions.githubusercontent.com"

# Then verify file checksums
sha256sum -c sbom-checksums.txt
```

### 7.3 Trust Chain

**Trust Model:**
1. **GitHub Actions OIDC** - Authenticates workflow identity
2. **Sigstore Fulcio** - Issues short-lived signing certificates
3. **Sigstore Rekor** - Records signatures in transparency log
4. **Certificate Verification** - Validates GitHub identity claim

**Guarantees:**
- SBOM was generated by official GitHub Actions workflow
- SBOM has not been modified since generation
- Generation is recorded in immutable transparency log
- Can be audited independently via Rekor

---

## 8. SBOM Usage

### 8.1 Vulnerability Scanning

**Use SBOM to scan for known vulnerabilities:**

```bash
# Using Grype (Anchore)
grype sbom:sbom-comprehensive.cyclonedx.json

# Using OSV Scanner
osv-scanner --sbom=sbom-comprehensive.cyclonedx.json

# Using Trivy
trivy sbom sbom-comprehensive.cyclonedx.json
```

### 8.2 License Compliance

**Extract license information:**

```bash
# List all licenses
jq '.components[] | {name: .name, version: .version, licenses: .licenses}' sbom-comprehensive.cyclonedx.json

# Count by license type
jq '.components[].licenses[].license.id' sbom-comprehensive.cyclonedx.json | sort | uniq -c
```

### 8.3 Dependency Analysis

**Analyze dependency tree:**

```bash
# View all components
cat sbom-report.txt

# Extract specific package versions
jq '.components[] | select(.name == "openai") | {name, version}' sbom-comprehensive.cyclonedx.json

# Count total dependencies
jq '.components | length' sbom-comprehensive.cyclonedx.json
```

### 8.4 Risk Assessment

**Identify high-risk components:**
- Components with known CVEs
- Deprecated packages
- Unmaintained dependencies
- Packages with restrictive licenses

---

## 9. Responsibilities

### 9.1 Security Team

- Monitor SBOM generation success/failures
- Review vulnerability scan results
- Update SBOM policy as needed
- Respond to SBOM-related security incidents

### 9.2 Development Team

- Ensure dependencies are documented in `requirements.txt`, `pyproject.toml`, `package.json`
- Review SBOM for new releases
- Address flagged vulnerabilities
- Test SBOM verification process

### 9.3 Release Manager

- Verify SBOM attached to releases
- Validate SBOM signatures before release
- Communicate SBOM availability to users
- Archive SBOMs for compliance records

---

## 10. Compliance and Auditing

### 10.1 Audit Trail

All SBOM generations are logged:
- **GitHub Actions Logs** - Full generation logs (90 days)
- **Sigstore Rekor** - Permanent transparency log entries
- **Release History** - SBOM versions per release

### 10.2 Regulatory Compliance

| Regulation | Requirement | Compliance |
|------------|-------------|------------|
| **EO 14028** | SBOM for federal software | ✅ NTIA-compliant |
| **NIST SSDF** | Software supply chain security | ✅ SBOM + signatures |
| **GDPR** | Data processing transparency | ✅ No PII in SBOM |
| **SOC 2** | Change management | ✅ Audit trail |

### 10.3 Retention Policy

| Artifact Type | Retention Period |
|---------------|------------------|
| **Release SBOMs** | Permanent (indefinite) |
| **CI Artifact SBOMs** | 90 days |
| **Rekor Log Entries** | Permanent (immutable) |
| **GitHub Actions Logs** | 90 days |

---

## 11. Incident Response

### 11.1 SBOM Compromise

If SBOM integrity is compromised:
1. **Immediate:** Revoke affected release if possible
2. **Investigate:** Review Rekor log for unauthorized entries
3. **Regenerate:** Create new SBOM with updated signatures
4. **Notify:** Inform users via security advisory
5. **Review:** Audit GitHub Actions workflow permissions

### 11.2 Vulnerability Discovery

When vulnerability is found via SBOM:
1. **Assess:** Determine impact and exploitability
2. **Prioritize:** Assign severity (Critical/High/Medium/Low)
3. **Patch:** Update vulnerable dependency
4. **Regenerate:** Create new SBOM with patched dependency
5. **Release:** Publish security update with new SBOM
6. **Communicate:** Issue security advisory

---

## 12. Continuous Improvement

### 12.1 Review Schedule

- **Quarterly:** Review SBOM policy and processes
- **Annually:** Audit SBOM accuracy and completeness
- **As Needed:** Update for new standards or regulations

### 12.2 Metrics

Track the following metrics:
- SBOM generation success rate
- Time to generate SBOM
- Vulnerabilities discovered via SBOM
- SBOM verification success rate
- User adoption of SBOM verification

### 12.3 Future Enhancements

Planned improvements:
- Support for SPDX format (in addition to CycloneDX)
- Integration with dependency review tools
- Automated vulnerability remediation
- SBOM diff between releases
- Machine learning model component tracking

---

## 13. References

### 13.1 Standards and Specifications

- [NTIA Minimum Elements for SBOM](https://www.ntia.gov/sbom)
- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [SPDX Specification](https://spdx.dev/specifications/)
- [NIST SP 800-218 SSDF](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [OWASP SCVS](https://owasp.org/www-project-software-component-verification-standard/)

### 13.2 Tools

- [Syft](https://github.com/anchore/syft) - SBOM generation
- [Grype](https://github.com/anchore/grype) - Vulnerability scanning
- [Cosign](https://github.com/sigstore/cosign) - Artifact signing
- [Sigstore](https://www.sigstore.dev/) - Signature transparency

### 13.3 Related Documentation

- `SECURITY.md` - Security policy and vulnerability reporting
- `docs/SECURITY_FRAMEWORK.md` - Comprehensive security framework
- `docs/security/SECURITY_AUDIT_EXECUTIVE_SUMMARY.md` - Security audit summary
- `.github/workflows/sbom.yml` - SBOM generation workflow
- `.github/workflows/sign-release-artifacts.yml` - Artifact signing workflow

---

## 14. Contact

For questions or concerns about SBOM:
- **Security Issues:** Use GitHub Security Advisories
- **General Questions:** Open GitHub Issue with `sbom` label
- **Email:** Security@thirstysprojects.com

---

## 15. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-19 | Initial SBOM policy document |

---

**Classification:** PUBLIC  
**Distribution:** Unlimited

---

*"Transparency builds trust in software supply chains."*
