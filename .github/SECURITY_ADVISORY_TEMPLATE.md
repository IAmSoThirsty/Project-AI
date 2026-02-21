---
name: Security Advisory
about: Template for creating security advisories for vulnerabilities in Project-AI
title: '[SECURITY] '
labels: security, critical
assignees: ''
---

<!--
This template is for creating security advisories that will be published on GitHub.
Do NOT use this for public disclosure of unpatched vulnerabilities.
Use private security advisories first, then publish after a fix is available.
-->

## Security Advisory Summary

**CVE ID** (if assigned): CVE-YYYY-NNNNN
**Advisory ID**: GHSA-XXXX-XXXX-XXXX
**Severity**: [Critical / High / Moderate / Low]
**CWE**: CWE-XXX

### Affected Component

**Package**: `project-ai` or specific module
**Affected Versions**: X.Y.Z - A.B.C
**Fixed in Version**: X.Y.Z

---

## Vulnerability Description

### Summary
<!-- Provide a brief, high-level summary of the vulnerability in 1-2 sentences -->

### Impact
<!-- Describe the security impact if this vulnerability is exploited -->
**CVSS Score**: X.X (Severity)
**Attack Vector**: [Network / Adjacent / Local / Physical]
**Attack Complexity**: [Low / High]
**Privileges Required**: [None / Low / High]
**User Interaction**: [None / Required]
**Scope**: [Unchanged / Changed]

### Affected Functionality
<!-- List the specific functions, classes, or modules affected -->
- Component: `src/path/to/component.py`
- Function: `vulnerable_function()`
- Lines: XX-YY

---

## Technical Details

### Root Cause
<!-- Explain the technical root cause of the vulnerability -->

### Attack Scenario
<!-- Provide a realistic attack scenario (without providing exploit code) -->

### Proof of Concept (Optional)
<!-- If safe to disclose, provide a minimal PoC demonstrating the issue -->
```python
# Example: Demonstrating the vulnerability
# DO NOT include actual exploit code
```

---

## Mitigation and Remediation

### Immediate Workarounds
<!-- Temporary mitigations users can apply while waiting for a patch -->
1.
2.
3.

### Patches Available
<!-- Link to the pull request(s) that fix the vulnerability -->
- PR #XXX: [Brief description]
- Commit: [SHA]

### Upgrade Instructions
```bash
# For users upgrading to the patched version
pip install --upgrade project-ai>=X.Y.Z
```

### Verification
<!-- How users can verify they're no longer vulnerable -->
```bash
# Check installed version
pip show project-ai | grep Version

# Run self-test if available
python -m project_ai.security_check
```

---

## Credits

### Reporter
<!-- Credit the security researcher who reported the issue -->
- **Name**: [Reporter Name]
- **Organization**: [If applicable]
- **Contact**: [Email or GitHub handle]

### Remediation Team
<!-- Credit the team members who fixed the issue -->
- @username1
- @username2

---

## Timeline

| Date | Event |
|------|-------|
| YYYY-MM-DD | Vulnerability reported |
| YYYY-MM-DD | Vulnerability confirmed |
| YYYY-MM-DD | Fix developed and tested |
| YYYY-MM-DD | Security advisory published |
| YYYY-MM-DD | Patch released (vX.Y.Z) |
| YYYY-MM-DD | Public disclosure |

---

## References

### Internal
- Security Policy: [SECURITY.md](../SECURITY.md)
- Related Issue: #XXX
- Related PR: #XXX

### External
- CVE Record: https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-YYYY-NNNNN
- NVD Entry: https://nvd.nist.gov/vuln/detail/CVE-YYYY-NNNNN
- GitHub Advisory: https://github.com/IAmSoThirsty/Project-AI/security/advisories/GHSA-XXXX-XXXX-XXXX

### Related Vulnerabilities
<!-- Link to similar CVEs or advisories in other projects -->
-

---

## Additional Information

### CVSS Vector String
```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
```

### Weaknesses (CWE)
- [CWE-XXX: Description](https://cwe.mitre.org/data/definitions/XXX.html)

### Compliance Considerations
<!-- Note any compliance frameworks affected (SOC2, ISO 27001, etc.) -->
-

---

## Contact Information

For questions about this advisory:
- **Email**: security@thirstysprojects.com
- **GitHub**: Create an issue with the `security` label
- **Private Report**: Use [GitHub Security Advisories](https://github.com/IAmSoThirsty/Project-AI/security/advisories/new)

---

**Responsible Disclosure**: Project-AI follows a 90-day responsible disclosure policy. Security researchers should report vulnerabilities privately via GitHub Security Advisories or email. Public disclosure should not occur until a patch is available or the 90-day window expires.

**Bug Bounty**: Project-AI does not currently operate a bug bounty program, but we greatly appreciate security research contributions and will credit researchers in advisories.
