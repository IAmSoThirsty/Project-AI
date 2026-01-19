# Security Policy

## Reporting Security Vulnerabilities

We take security seriously and appreciate your efforts to responsibly disclose security vulnerabilities.

### Private Vulnerability Reporting (Recommended)

**For sensitive security issues, please use GitHub's Private Vulnerability Reporting:**

1. Navigate to the [Security tab](https://github.com/IAmSoThirsty/Project-AI/security) of this repository
2. Click on **"Advisories"** in the left sidebar
3. Click **"New draft security advisory"** or **"Report a vulnerability"**
4. Fill in the details of the vulnerability
5. Click **"Submit report"**

**Why use private reporting?**
- Your report remains confidential until we publish an advisory
- We can collaborate privately to understand and fix the issue
- Prevents public disclosure before a patch is available
- Automatically creates a CVE when published (if applicable)

### Alternative Reporting Methods

If you prefer not to use GitHub's private reporting:

- **Email:** projectaidevs@gmail.com
- **Public Issue:** Open an issue labeled `security` (only for non-sensitive issues)

### What to Include

When reporting a vulnerability, please provide:
- **Description:** Clear explanation of the vulnerability
- **Impact:** What could an attacker accomplish?
- **Steps to Reproduce:** Detailed reproduction steps
- **Affected Versions:** Which versions are vulnerable?
- **Suggested Fix:** (Optional) How to remediate the issue
- **Proof of Concept:** (Optional) Code or exploit demonstrating the issue

### Response Timeline

- **Acknowledgment:** Within 72 hours
- **Initial Assessment:** Within 1 week
- **Status Updates:** At least every 2 weeks
- **Fix Timeline:** Depends on severity (see below)

### Severity and Response Times

| Severity | Description | Response Time |
|----------|-------------|---------------|
| **Critical** | Unauthenticated RCE, data breach, credential exposure | 48 hours |
| **High** | Authenticated RCE, privilege escalation, SQL injection | 1 week |
| **Medium** | XSS, CSRF, information disclosure | 2 weeks |
| **Low** | Minor issues with minimal impact | 1 month |

## Security Features

### Dependency Scanning

We continuously monitor dependencies for known vulnerabilities:
- **pip-audit** - Python dependency vulnerability scanning
- **GitHub Dependabot** - Automated dependency updates and alerts
- **Bandit** - Python code security analysis
- **CodeQL** - Semantic code analysis for security issues

### Supply Chain Security

- **SBOM Generation:** Software Bill of Materials for every release (see [SBOM Policy](docs/security/SBOM_POLICY.md))
- **Artifact Signing:** All releases signed with Sigstore Cosign (keyless signing)
- **AI/ML Security:** Automated scanning for model-specific threats
- **Transparency Logs:** All signatures recorded in Sigstore Rekor

### Continuous Security

- Daily automated security scans
- Weekly Bandit security analysis
- Automated security fix PRs for dependencies
- CodeQL analysis on every PR

## Security Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure principles:
1. **Report Received:** Acknowledge within 72 hours
2. **Verification:** Confirm vulnerability (1-5 days)
3. **Fix Development:** Develop and test patch
4. **Private Testing:** Share patch with reporter for validation
5. **Public Disclosure:** Publish advisory and release patch
6. **CVE Assignment:** Request CVE if applicable

### Credit and Recognition

- Security researchers who report vulnerabilities will be credited in:
  - GitHub Security Advisory
  - Release notes
  - CHANGELOG.md (if they consent)
- Hall of Fame for significant findings (coming soon)

### Embargo Period

- **Default:** 90 days from initial report to public disclosure
- **Critical Issues:** May be shortened to 30-45 days if actively exploited
- **Extensions:** Available by mutual agreement

## Out of Scope

The following are **not** considered security vulnerabilities:

- Denial of Service (DoS) requiring excessive resources
- Issues in unsupported versions
- Social engineering attacks
- Physical attacks requiring local access
- Issues in third-party dependencies (report to upstream)
- Theoretical attacks without practical exploitation

## Security Best Practices for Users

### For Developers

1. **Never commit secrets** - Use `.env` files (not in git)
2. **Keep dependencies updated** - Review Dependabot PRs
3. **Run security tests** - Use `pytest tests/test_security*.py`
4. **Validate inputs** - Use provided security modules
5. **Review security docs** - See `docs/SECURITY_FRAMEWORK.md`

### For Deployment

1. **Use HTTPS/TLS** - Never deploy without encryption
2. **Rotate credentials** - Change default passwords immediately
3. **Enable 2FA/MFA** - For all service accounts
4. **Monitor logs** - Watch for suspicious activity
5. **Verify signatures** - Check SBOM and release signatures

### For End Users

1. **Download from official sources** - GitHub releases only
2. **Verify signatures** - Use Cosign to verify artifacts
3. **Check SBOM** - Review dependencies for known issues
4. **Keep updated** - Install security patches promptly
5. **Report issues** - Use private reporting for security concerns

## Additional Resources

- **Security Framework:** [docs/SECURITY_FRAMEWORK.md](docs/SECURITY_FRAMEWORK.md)
- **Security Audit:** [docs/security/SECURITY_AUDIT_EXECUTIVE_SUMMARY.md](docs/security/SECURITY_AUDIT_EXECUTIVE_SUMMARY.md)
- **SBOM Policy:** [docs/security/SBOM_POLICY.md](docs/security/SBOM_POLICY.md)
- **Security Workflows:** [.github/workflows/](../.github/workflows/)

## Legal

- We will not pursue legal action against security researchers who:
  - Act in good faith
  - Follow responsible disclosure
  - Do not access or modify user data
  - Do not disrupt service availability
- This policy is not a vulnerability bounty program (no financial rewards at this time)

---

**Last Updated:** 2026-01-19  
**Contact:** projectaidevs@gmail.com
