# Security and Compliance Badge Recommendations

This document provides recommended badges for README.md to showcase the security and compliance features implemented in Project-AI.

## Recommended Badges

### Supply Chain Security

```markdown
<!-- Artifact Signing -->
[![Signed with Sigstore](https://img.shields.io/badge/Signed%20with-Sigstore-blue?logo=sigstore)](https://github.com/IAmSoThirsty/Project-AI/releases)

<!-- SBOM -->
[![SBOM Available](https://img.shields.io/badge/SBOM-CycloneDX%201.5-brightgreen?logo=owasp)](https://github.com/IAmSoThirsty/Project-AI/releases)

<!-- NTIA Compliance -->
[![NTIA SBOM](https://img.shields.io/badge/NTIA-SBOM%20Compliant-success)](docs/security/SBOM_POLICY.md)
```

### Security Scanning

```markdown
<!-- CodeQL -->
[![CodeQL](https://github.com/IAmSoThirsty/Project-AI/workflows/Security%20-%20Consolidated/badge.svg)](https://github.com/IAmSoThirsty/Project-AI/actions/workflows/security-consolidated.yml)

<!-- AI/ML Security -->
[![AI/ML Security](https://img.shields.io/badge/AI%2FML-Security%20Scanned-blueviolet?logo=python)](https://github.com/IAmSoThirsty/Project-AI/actions/workflows/ai-model-security.yml)
```

### Compliance Standards

```markdown
<!-- NIST SSDF -->
[![NIST SSDF](https://img.shields.io/badge/NIST%20SP%20800--218-SSDF%20Compliant-blue)](docs/SECURITY_FRAMEWORK.md)

<!-- OWASP -->
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%20Compliant-orange?logo=owasp)](docs/SECURITY_FRAMEWORK.md)
```

### Vulnerability Reporting

```markdown
<!-- Security Policy -->
[![Security Policy](https://img.shields.io/badge/Security-Private%20Reporting-red?logo=github)](SECURITY.md)
```

## Complete Badge Section

Here's a complete badge section you can add to README.md:

```markdown
## 🔒 Security & Compliance

[![Signed with Sigstore](https://img.shields.io/badge/Signed%20with-Sigstore-blue?logo=sigstore)](https://github.com/IAmSoThirsty/Project-AI/releases)
[![SBOM Available](https://img.shields.io/badge/SBOM-CycloneDX%201.5-brightgreen?logo=owasp)](https://github.com/IAmSoThirsty/Project-AI/releases)
[![NTIA SBOM](https://img.shields.io/badge/NTIA-SBOM%20Compliant-success)](docs/security/SBOM_POLICY.md)
[![CodeQL](https://github.com/IAmSoThirsty/Project-AI/workflows/Security%20-%20Consolidated/badge.svg)](https://github.com/IAmSoThirsty/Project-AI/actions/workflows/security-consolidated.yml)
[![AI/ML Security](https://img.shields.io/badge/AI%2FML-Security%20Scanned-blueviolet?logo=python)](https://github.com/IAmSoThirsty/Project-AI/actions/workflows/ai-model-security.yml)
[![NIST SSDF](https://img.shields.io/badge/NIST%20SP%20800--218-SSDF%20Compliant-blue)](docs/SECURITY_FRAMEWORK.md)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%20Compliant-orange?logo=owasp)](docs/SECURITY_FRAMEWORK.md)
[![Security Policy](https://img.shields.io/badge/Security-Private%20Reporting-red?logo=github)](SECURITY.md)

**Supply Chain Security:**
- 🔐 All releases signed with [Sigstore Cosign](https://www.sigstore.dev/)
- 📦 SBOM generated for every release (CycloneDX 1.5)
- 🤖 AI/ML model security scanning
- 🔍 Private vulnerability reporting via GitHub Security Advisories

**Compliance:**
- ✅ NTIA SBOM Minimum Elements
- ✅ NIST SP 800-218 SSDF
- ✅ OWASP Top 10 & SCVS
- ✅ US Executive Order 14028
```

## Alternative: Compact Version

For a more compact presentation:

```markdown
## Security

[![Security](https://img.shields.io/badge/security-compliant-success?style=for-the-badge)](docs/SECURITY_FRAMEWORK.md)

All releases are cryptographically signed and include SBOM. See [Security Framework](docs/SECURITY_FRAMEWORK.md) for details.
```

## Badge Placement Recommendations

### Option 1: Top of README (After Title)

Place badges immediately after the project title and description for maximum visibility.

### Option 2: Security Section

Create a dedicated "Security & Compliance" section in the README with badges and detailed information.

### Option 3: Shields.io Badges in Table

Use a table format for organized presentation:

```markdown
| Category | Status |
|----------|--------|
| Artifact Signing | [![Sigstore](https://img.shields.io/badge/Signed-Sigstore-blue)](releases) |
| SBOM | [![CycloneDX](https://img.shields.io/badge/SBOM-CycloneDX-green)](releases) |
| Security Scanning | [![CodeQL](https://img.shields.io/badge/CodeQL-Passing-success)](actions) |
| AI/ML Security | [![ModelScan](https://img.shields.io/badge/ModelScan-Passing-success)](actions) |
```

## Additional Resources

- **Security Policy:** [SECURITY.md](SECURITY.md)
- **Security Framework:** [docs/SECURITY_FRAMEWORK.md](docs/SECURITY_FRAMEWORK.md)
- **SBOM Policy:** [docs/security/SBOM_POLICY.md](docs/security/SBOM_POLICY.md)
- **Security Workflows:** [.github/workflows/](.github/workflows/)

## Notes

1. **Dynamic Badges:** Some badges (like CodeQL status) will update automatically based on workflow status
1. **Static Badges:** Compliance badges are static and should be updated if compliance status changes
1. **Links:** All badges link to relevant documentation or releases
1. **Customization:** Feel free to adjust colors, styles, and wording to match project branding

## Testing Badges

Before adding badges to README.md:

1. Ensure workflows have run successfully at least once
1. Verify release has been published with signed artifacts and SBOM
1. Check that badge URLs resolve correctly
1. Test badge links point to correct documentation

---

**Note:** These badges are recommendations only. The user should manually add them to README.md in the location and style they prefer.
