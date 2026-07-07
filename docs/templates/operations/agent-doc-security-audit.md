---
# ═══════════════════════════════════════════════════════════════════════════
# SECURITY AUDIT AGENT REPORT TEMPLATE
# Document Type: Agent Documentation (Security Audit Findings)
# Target: Security audit and vulnerability assessment reports
# Schema Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

# Universal Fields (Required)
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "audit"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "completed"
author: 
  name: "<%`AGENT-${await tp.system.prompt('Agent number (e.g., 042):') || 'XXX'}: Security Audit Agent`%>"
  email: ""
  github: ""

# Domain-Specific Fields
category: "security"
tags:
  - "security"
  - "audit"
  - "vulnerability"
  - "assessment"
  - "penetration-test"
  - "security/audit"
classification: "confidential"
audience:
  - "security_engineer"
  - "architect"
  - "devops"

# Audit-Specific Fields
scope: ""
vulnerabilities_found: 0
risk_assessment: "low"
remediation_plan: []

# Quality Metadata
review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false

# Discovery & SEO
keywords:
  - "security audit"
  - "vulnerability assessment"
  - "penetration test"
  - "threat model"
summary: "Security audit report for <%`${await tp.system.prompt('Scope (e.g., authentication modules):') || '[Scope]'}`%> documenting vulnerabilities, risk assessment, and remediation recommendations."

# Relationships
related_docs: []
supersedes: null
---

# <%tp.file.title%>

> **Audit Type:** <%`${await tp.system.prompt('Audit type (automated/manual/hybrid):') || 'automated'}`%>  
> **Scan Date:** <%tp.date.now("YYYY-MM-DD")%>  
> **Overall Risk:** <%`${await tp.system.prompt('Risk level (CRITICAL/HIGH/MEDIUM/LOW):') || 'MEDIUM'}`%>  
> **Vulnerabilities Found:** <%`${await tp.system.prompt('Number of vulnerabilities:') || '0'}`%>

---

## 🔒 Executive Summary

**Audit Objective:** [One-sentence description of audit purpose]

**Scope:** <%`${await tp.system.prompt('Audit scope (e.g., src/app/core/user_manager.py):') || '[Define audit scope]'}`%>

**Risk Assessment:** [High-level risk determination and business impact]

**Immediate Actions Required:** [Critical findings requiring immediate attention]

---

## Table of Contents

1. [Agent Identification](#agent-identification)
2. [Audit Scope](#audit-scope)
3. [Methodology](#methodology)
4. [Executive Findings Summary](#executive-findings-summary)
5. [Vulnerability Details](#vulnerability-details)
6. [Risk Assessment](#risk-assessment)
7. [Remediation Plan](#remediation-plan)
8. [Compliance Review](#compliance-review)
9. [Threat Model](#threat-model)
10. [Verification and Testing](#verification-and-testing)
11. [Appendices](#appendices)

---

## Agent Identification

### Audit Agent Profile

| Property | Value |
|----------|-------|
| **Agent ID** | <%`AGENT-${await tp.system.prompt('Agent number:') || 'XXX'}`%> |
| **Agent Role** | Security Audit Specialist |
| **Audit Type** | <%`${await tp.system.prompt('Type (SAST/DAST/Manual/Hybrid):') || 'Hybrid'}`%> |
| **Audit Framework** | <%`${await tp.system.prompt('Framework (OWASP/CWE/Custom):') || 'OWASP Top 10'}`%> |
| **Tools Used** | <%`${await tp.system.prompt('Tools (Bandit/Ruff/Manual/etc):') || 'Bandit, Manual Review'}`%> |

### Authorization and Compliance

**Audit Authorization:** [Who authorized this audit?]

**Compliance Standards:**
- [ ] OWASP Top 10 2021
- [ ] CWE Top 25
- [ ] NIST Cybersecurity Framework
- [ ] PCI-DSS (if applicable)
- [ ] GDPR (if applicable)

---

## Audit Scope

### Scope Definition

**In Scope:**
- [ ] **Modules:** `[List of modules/files audited]`
- [ ] **Components:** [Specific components or systems]
- [ ] **Dependencies:** [Third-party libraries checked]
- [ ] **Configuration:** [Config files reviewed]

**Out of Scope:**
- [Items explicitly excluded from audit]

### Scan Coverage

| Category | Files Scanned | Lines Analyzed | Functions Reviewed |
|----------|---------------|----------------|--------------------|
| **Core Modules** | [Count] | [Count] | [Count] |
| **GUI Components** | [Count] | [Count] | [Count] |
| **Agents** | [Count] | [Count] | [Count] |
| **Configuration** | [Count] | N/A | N/A |
| **Dependencies** | [Count] | N/A | N/A |
| **Total** | [Count] | [Count] | [Count] |

---

## Methodology

### Audit Approach

**Phase 1: Automated Scanning**
- **Tool:** [Tool name and version]
- **Configuration:** [Scan settings]
- **Duration:** [Time spent]
- **Findings:** [Count of automated findings]

**Phase 2: Manual Code Review**
- **Focus Areas:** [Security-critical code paths]
- **Techniques:** [Code auditing methods]
- **Duration:** [Time spent]
- **Findings:** [Count of manual findings]

**Phase 3: Penetration Testing** (if applicable)
- **Methods:** [Testing methods]
- **Tools:** [Tools used]
- **Findings:** [Count of pentest findings]

### Scanning Tools Configuration

```bash
# Bandit security scan
bandit -r src/app/ -f json -o bandit_report.json

# Ruff security checks
ruff check . --select S  # Security checks

# pip-audit for dependencies
pip-audit --format json
```

---

## Executive Findings Summary

### Vulnerability Count by Severity

| Severity | Count | Percentage | Status |
|----------|-------|------------|--------|
| 🔴 **CRITICAL** | <%`${await tp.system.prompt('Critical vulns:') || '0'}`%> | [%] | [Remediated/Pending] |
| 🟠 **HIGH** | <%`${await tp.system.prompt('High vulns:') || '0'}`%> | [%] | [Remediated/Pending] |
| 🟡 **MEDIUM** | <%`${await tp.system.prompt('Medium vulns:') || '0'}`%> | [%] | [Remediated/Pending] |
| 🟢 **LOW** | <%`${await tp.system.prompt('Low vulns:') || '0'}`%> | [%] | [Remediated/Pending] |
| ℹ️ **INFO** | <%`${await tp.system.prompt('Info findings:') || '0'}`%> | [%] | [Acknowledged] |
| **TOTAL** | [Count] | 100% | |

### Vulnerability Categories (OWASP)

| OWASP Category | Vulnerabilities | Severity |
|----------------|-----------------|----------|
| A01:2021 - Broken Access Control | [Count] | [Severity] |
| A02:2021 - Cryptographic Failures | [Count] | [Severity] |
| A03:2021 - Injection | [Count] | [Severity] |
| A04:2021 - Insecure Design | [Count] | [Severity] |
| A05:2021 - Security Misconfiguration | [Count] | [Severity] |
| A06:2021 - Vulnerable Components | [Count] | [Severity] |
| A07:2021 - Authentication Failures | [Count] | [Severity] |
| A08:2021 - Data Integrity Failures | [Count] | [Severity] |
| A09:2021 - Logging/Monitoring Failures | [Count] | [Severity] |
| A10:2021 - SSRF | [Count] | [Severity] |

---

## Vulnerability Details

### CRITICAL-001: [Vulnerability Title]

**Severity:** 🔴 CRITICAL  
**CWE ID:** CWE-[XXX]  
**CVSS Score:** [Score] ([Vector String])  
**Status:** ❌ OPEN / ✅ FIXED / ⏳ IN PROGRESS

**Description:**
[Detailed description of the vulnerability]

**Location:**
```
File: src/app/[module]/[file].py
Line: [Line number(s)]
Function: [Function name]
```

**Vulnerable Code:**
```python
# Vulnerable implementation
[Code snippet showing the vulnerability]
```

**Attack Vector:**
```python
# Example exploit demonstrating the vulnerability
[Proof of concept code]
```

**Impact:**
- **Confidentiality:** [HIGH/MEDIUM/LOW]
- **Integrity:** [HIGH/MEDIUM/LOW]
- **Availability:** [HIGH/MEDIUM/LOW]
- **Business Impact:** [Description of business consequences]

**Likelihood:** [HIGH/MEDIUM/LOW]

**Risk Score:** [Severity × Likelihood]

**Recommended Fix:**
```python
# Secure implementation
[Code showing the recommended fix]
```

**Remediation Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Verification:**
```bash
# How to verify the fix
[Test command or procedure]
```

**References:**
- OWASP: [URL]
- CWE: https://cwe.mitre.org/data/definitions/[XXX].html
- CVE: [CVE-YYYY-XXXXX] (if applicable)

---

### HIGH-001: [Vulnerability Title]

**Severity:** 🟠 HIGH  
**CWE ID:** CWE-[XXX]  
**CVSS Score:** [Score]  
**Status:** ❌ OPEN / ✅ FIXED

**Description:**
[Detailed description]

**Location:**
```
File: [Path]
Line: [Number]
```

**Vulnerable Code:**
```python
[Code snippet]
```

**Impact:**
[Impact analysis]

**Recommended Fix:**
```python
[Fixed code]
```

**Remediation Steps:**
1. [Step 1]
2. [Step 2]

---

### MEDIUM-001: [Vulnerability Title]

**Severity:** 🟡 MEDIUM  
**CWE ID:** CWE-[XXX]  
**Status:** [Status]

**Description:**
[Description]

**Location:**
```
File: [Path]
Line: [Number]
```

**Recommended Fix:**
[Fix description]

---

## Risk Assessment

### Overall Risk Matrix

|  | **High Likelihood** | **Medium Likelihood** | **Low Likelihood** |
|---|---|---|---|
| **Critical Impact** | 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM |
| **High Impact** | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW |
| **Medium Impact** | 🟡 MEDIUM | 🟢 LOW | 🟢 LOW |
| **Low Impact** | 🟢 LOW | 🟢 LOW | ℹ️ INFO |

### Risk Prioritization

| Vulnerability | Severity | Likelihood | Impact | Priority | Target Fix Date |
|---------------|----------|------------|--------|----------|----------------|
| CRITICAL-001 | Critical | High | High | P0 | [Date] |
| HIGH-001 | High | Medium | High | P1 | [Date] |
| MEDIUM-001 | Medium | Low | Medium | P2 | [Date] |

**Priority Definitions:**
- **P0:** Immediate fix required (within 24 hours)
- **P1:** Urgent fix required (within 1 week)
- **P2:** Fix in next sprint
- **P3:** Fix when convenient

---

## Remediation Plan

### Immediate Actions (P0/P1)

#### Action 1: Fix CRITICAL-001

**Vulnerability:** [Name]

**Remediation:**
```python
# Implementation
[Code fix]
```

**Owner:** [Developer/Team]

**Estimated Effort:** [Hours/Days]

**Dependencies:** [Any dependencies]

**Verification:**
```bash
# Test command
[Verification procedure]
```

**Status:** ❌ TODO / ⏳ IN PROGRESS / ✅ COMPLETE

---

### Short-Term Actions (P2)

| Action | Vulnerability | Owner | Effort | Status |
|--------|---------------|-------|--------|--------|
| [Action 1] | MEDIUM-001 | [Owner] | [Effort] | [Status] |
| [Action 2] | MEDIUM-002 | [Owner] | [Effort] | [Status] |

---

### Long-Term Improvements

1. **Security Hardening:** [Description]
   - **Actions:** [List]
   - **Timeline:** [Duration]

2. **Process Improvements:** [Description]
   - **Actions:** [List]
   - **Timeline:** [Duration]

3. **Training and Awareness:** [Description]
   - **Actions:** [List]
   - **Timeline:** [Duration]

---

## Compliance Review

### OWASP Top 10 Compliance

| OWASP Category | Status | Notes |
|----------------|--------|-------|
| A01: Broken Access Control | ✅ Compliant / ⚠️ Partial / ❌ Non-Compliant | [Notes] |
| A02: Cryptographic Failures | ✅ / ⚠️ / ❌ | [Notes] |
| A03: Injection | ✅ / ⚠️ / ❌ | [Notes] |
| A04: Insecure Design | ✅ / ⚠️ / ❌ | [Notes] |
| A05: Security Misconfiguration | ✅ / ⚠️ / ❌ | [Notes] |

### Security Best Practices

- [ ] **Input Validation:** All inputs validated and sanitized
- [ ] **Output Encoding:** All outputs properly encoded
- [ ] **Authentication:** Strong authentication mechanisms
- [ ] **Authorization:** Proper access controls
- [ ] **Cryptography:** Secure algorithms and key management
- [ ] **Error Handling:** Secure error handling (no info leakage)
- [ ] **Logging:** Comprehensive audit logging
- [ ] **Dependency Management:** All dependencies up-to-date

---

## Threat Model

### Attack Surface

**Entry Points:**
1. [Entry point 1]: [Description and risk]
2. [Entry point 2]: [Description and risk]

**Trust Boundaries:**
1. [Boundary 1]: [Description]
2. [Boundary 2]: [Description]

### Threat Scenarios

#### Threat 1: [Threat Name]

**Attacker Profile:** [Internal/External, Skill Level]

**Attack Vector:** [How the attack is carried out]

**Mitigation:** [Current mitigations in place]

**Residual Risk:** [Remaining risk after mitigations]

---

## Verification and Testing

### Security Test Cases

| Test ID | Test Description | Expected Result | Actual Result | Status |
|---------|------------------|-----------------|---------------|--------|
| SEC-001 | [Test description] | [Expected] | [Actual] | ✅ / ❌ |
| SEC-002 | [Test description] | [Expected] | [Actual] | ✅ / ❌ |

### Penetration Test Results

**Test Date:** [Date]

**Methodology:** [Methodology]

**Findings:**
- [Finding 1]
- [Finding 2]

---

## Appendices

### Appendix A: Full Scan Results

```json
{
  "tool": "Bandit",
  "version": "1.7.5",
  "scan_date": "<%tp.date.now("YYYY-MM-DD")%>",
  "results": [
    // Full JSON output
  ]
}
```

### Appendix B: Dependency Audit

| Package | Version | Vulnerability | Severity | Fix Version |
|---------|---------|---------------|----------|-------------|
| [Package] | [Version] | CVE-YYYY-XXXXX | [Severity] | [Fix Version] |

### Appendix C: Security Tool Configuration

```yaml
# Bandit configuration
[Configuration content]
```

---

## Sign-off

**Audit Execution:**
- **Agent ID:** <%`AGENT-${await tp.system.prompt('Agent number:') || 'XXX'}`%>
- **Audit Status:** ✅ COMPLETED
- **Total Vulnerabilities:** [Count]
- **Critical/High:** [Count]
- **Timestamp:** <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> UTC

**Review and Approval:**
- [ ] **Security Team Review:** [Reviewer] - [Date]
- [ ] **Architecture Review:** [Reviewer] - [Date]
- [ ] **Management Acknowledgment:** [Reviewer] - [Date]

**Next Audit Date:** <%`${await tp.system.prompt('Next audit date (YYYY-MM-DD):') || '[Schedule next audit]'}`%>

---

**Report Generated:** <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> UTC  
**Classification:** CONFIDENTIAL  
**Distribution:** Security Team, Architecture Team, Development Team

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

