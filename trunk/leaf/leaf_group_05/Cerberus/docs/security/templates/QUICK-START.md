<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / QUICK-START.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / QUICK-START.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Quick Start Guide - Security Templates

## 📋 Template Overview

| Template | File | Lines | Size | Use Case |
|----------|------|-------|------|----------|
| **Vulnerability Report** | `vulnerability-report-template.md` | 597 | 15K | Document security vulnerabilities with CVSS scoring |
| **Audit Report** | `audit-report-template.md` | 677 | 18K | Conduct comprehensive security audits |
| **Incident Report** | `incident-report-template.md` | 625 | 19K | Document security incidents and investigations |
| **Security Review** | `security-review-template.md` | 800 | 21K | Review code and design security |
| **README Guide** | `README.md` | 466 | 16K | Complete template documentation |

**Total:** 3,165 lines | 100K | 5 files

---

## 🚀 Quick Start (5 Minutes)

### 1. Identify Your Need

```
Is there a:
├─ Security vulnerability? → Use Vulnerability Report
├─ Security incident/breach? → Use Incident Report
├─ Security audit/compliance check? → Use Audit Report
└─ Code/design security review? → Use Security Review
```

### 2. Copy Template

```bash
# Example: Creating a vulnerability report
cp vulnerability-report-template.md VUL-2024-0001-SQLi.md

# Or: Creating an incident report
cp incident-report-template.md INC-2024-0001-UnauthorizedAccess.md
```

### 3. Fill in Key Sections

Every template has this structure:
```
1. Document Information (Metadata)
   ↓
2. Executive Summary (Key findings)
   ↓
3-N. Detailed Sections (Specific content)
   ↓
Final. Sign-off & Approvals
```

### 4. Complete and Submit

- Mark sections as needed
- Obtain required signatures
- Distribute according to classification

---

## 📝 Template Quick Reference

### Vulnerability Report Template
**When to use:** A security flaw is discovered

**Key sections:**
1. **CVSS Scoring** - Quantify severity (0.0-10.0 scale)
2. **Reproduction Steps** - How to trigger the vulnerability
3. **Proof of Concept** - Working code demonstration
4. **Impact Assessment** - Business and security consequences
5. **Remediation Plan** - Immediate, short-term, long-term fixes
6. **Guardian Analysis** - Which Cerberus Guardians are affected

**Critical fields to fill:**
- [ ] CVSS Vector: `CVSS:3.1/AV:*/AC:*/PR:*/UI:*/S:*/C:*/I:*/A:*`
- [ ] Severity: CRITICAL / HIGH / MEDIUM / LOW / INFO
- [ ] Affected Guardian: [GUARDIAN_NAME]
- [ ] Reproduction steps with actual commands
- [ ] PoC code that demonstrates the vulnerability

**Typical completion time:** 2-4 hours

---

### Audit Report Template
**When to use:** Security audit or compliance assessment

**Key sections:**
1. **Scope & Objectives** - What is being audited
2. **Methodology** - How the audit is conducted
3. **Findings** - Issues organized by severity
4. **Compliance Status** - Standards/regulations compliance
5. **Recommendations** - Prioritized improvement actions
6. **Guardian Coverage** - Audit of Guardian modules

**Critical fields to fill:**
- [ ] Audit scope and exclusions
- [ ] Findings with severity levels
- [ ] Compliance percentage by standard
- [ ] Guardian security scores
- [ ] Corrective action plans with owners and dates

**Typical completion time:** 40-80 hours

---

### Incident Report Template
**When to use:** Security incident investigation

**Key sections:**
1. **Detection & Classification** - How/when incident was found
2. **Timeline** - Detailed chronology of events
3. **Guardian Response** - How Guardian modules responded
4. **Root Cause Analysis** - Why the incident happened
5. **Response Actions** - What was done to contain/recover
6. **Lessons Learned** - Improvements needed
7. **Follow-up Items** - Actions to prevent recurrence

**Critical fields to fill:**
- [ ] Complete timeline from detection to resolution
- [ ] Guardian alert logs and responses
- [ ] Root cause identification
- [ ] Affected systems and data count
- [ ] Follow-up actions with owners and deadlines

**Typical completion time:** 16-40 hours

---

### Security Review Template
**When to use:** Code or design security assessment

**Key sections:**
1. **Architecture Review** - Design security validation
2. **Threat Model Review** - Threat assessment and mitigations
3. **Code Review** - Security code issues found
4. **Cryptography Review** - Cryptographic implementation validation
5. **Security Controls** - Verification of security controls
6. **Integration Testing** - Security test results
7. **Recommendations** - Priority improvement actions

**Critical fields to fill:**
- [ ] Overall security rating (Excellent/Good/Acceptable/Needs Improvement/Critical)
- [ ] Issues found organized by severity
- [ ] CVSS scores or equivalent severity for code issues
- [ ] Guardian integration test results
- [ ] Approval status before deployment

**Typical completion time:** 24-48 hours

---

## 🎯 Common Workflows

### Workflow 1: Report a Vulnerability

```
1. Discovery
   ↓
2. Copy vulnerability-report-template.md
   ↓
3. Fill Executive Summary (2 min)
   ↓
4. Add CVSS Scoring (10 min)
   ↓
5. Document reproduction steps (30 min)
   ↓
6. Create PoC code (30 min)
   ↓
7. Analyze Guardian impact (15 min)
   ↓
8. Recommend fixes (30 min)
   ↓
9. Get security team review (varies)
   ↓
10. Distribute to stakeholders
```

### Workflow 2: Conduct Security Audit

```
1. Planning
   └─ Copy audit-report-template.md
   └─ Define scope
   └─ Schedule audit
   ↓
2. Execution (Weeks 1-2)
   └─ Document review
   └─ System testing
   └─ Interviews
   └─ Fill in findings
   ↓
3. Analysis (Week 3)
   └─ Compile findings
   └─ Calculate compliance scores
   └─ Develop recommendations
   ↓
4. Reporting (Week 4)
   └─ Complete executive summary
   └─ Obtain approvals
   └─ Distribute report
   └─ Schedule follow-up
```

### Workflow 3: Respond to Incident

```
1. Incident Detected (T+0)
   └─ Copy incident-report-template.md
   └─ Begin logging timeline
   ↓
2. Immediate Response (T+0 to T+4 hours)
   └─ Fill: Detection & Classification
   └─ Fill: Timeline (start)
   └─ Fill: Guardian Response
   └─ Fill: Immediate Actions
   ↓
3. Investigation (T+4 to T+72 hours)
   └─ Complete: Timeline
   └─ Complete: Root Cause Analysis
   └─ Complete: Affected Systems
   └─ Complete: Forensic findings
   ↓
4. Recovery (T+72 hours+)
   └─ Complete: Response Actions
   └─ Complete: Lessons Learned
   └─ Complete: Follow-up Items
   ↓
5. Closure
   └─ Get management sign-off
   └─ Distribute final report
   └─ Track remediation actions
```

### Workflow 4: Perform Security Review

```
1. Setup (Day 1)
   └─ Copy security-review-template.md
   └─ Define scope
   └─ Assemble review team
   ↓
2. Architecture Review (Days 2-3)
   └─ Study design documentation
   └─ Fill: Architecture section
   └─ Create threat model
   ↓
3. Code Review (Days 4-6)
   └─ Static analysis
   └─ Manual code inspection
   └─ Fill: Code Review Findings
   └─ Cryptography validation
   ↓
4. Testing (Days 7-8)
   └─ Security testing
   └─ Guardian integration testing
   └─ Fill: Integration Testing results
   ↓
5. Recommendations (Days 9)
   └─ Prioritize findings
   └─ Fill: Recommendations
   └─ Determine approval status
   ↓
6. Sign-off (Days 10+)
   └─ Get team approval
   └─ Management authorization
   └─ Distribute for action
```

---

## ✅ Pre-Submission Checklist

### All Templates

- [ ] Document Information section completed
- [ ] All dates filled in
- [ ] Author and reviewer names added
- [ ] Classification level set appropriately
- [ ] All placeholder text [REMOVED or FILLED]
- [ ] Sign-off sections completed
- [ ] Revision history updated
- [ ] Appendices/evidence attached if applicable

### Vulnerability Report Specific

- [ ] CVSS vector properly formatted
- [ ] CVSS score calculated correctly (0.0-10.0)
- [ ] Guardian affected clearly identified
- [ ] PoC code tested and working
- [ ] Reproduction steps verified
- [ ] Remediation timeline set

### Audit Report Specific

- [ ] Audit scope clearly defined
- [ ] Findings organized by severity
- [ ] Compliance percentages calculated
- [ ] All Guardian modules assessed
- [ ] CAP timeline established
- [ ] Follow-up audit scheduled

### Incident Report Specific

- [ ] Complete timeline from discovery to closure
- [ ] Guardian responses documented
- [ ] Root cause clearly identified
- [ ] All affected systems listed
- [ ] Lessons learned included
- [ ] Follow-up action owners assigned

### Security Review Specific

- [ ] Approval status determined
- [ ] All findings documented
- [ ] Security rating assigned
- [ ] Guardian integration verified
- [ ] Cryptography review completed
- [ ] Management approval obtained

---

## 🔒 Security & Classification

### Mark All Reports With Classification

```markdown
| Classification | Audience | Distribution |
|---|---|---|
| PUBLIC | Anyone | No restrictions |
| INTERNAL | Employees | Internal networks only |
| CONFIDENTIAL | Leadership/Security | Secure channels |
| RESTRICTED | Need-to-know | Encrypted email/secure portal |
```

### Handling Sensitive Reports

1. **Storage:** Use encrypted drives/secure storage only
2. **Transfer:** Use encrypted email or secure file portal
3. **Print:** Shred or securely destroy printed copies
4. **Retention:** Follow organization retention policy
5. **Disposal:** Permanently delete digital copies when no longer needed

---

## 🔍 Finding Specific Sections

### Quick Section Locator

```
VULNERABILITY REPORT:
├─ CVSS Scoring → Section 2.2
├─ Code Analysis → Section 3.2
├─ PoC Code → Section 5.1
└─ Remediation → Section 9

AUDIT REPORT:
├─ Compliance Status → Section 5
├─ Guardian Assessment → Section 5.3
├─ Findings → Section 4
└─ Recommendations → Section 7

INCIDENT REPORT:
├─ Timeline → Section 3
├─ Guardian Response → Section 3.2
├─ Root Cause → Section 5
└─ Follow-up → Section 9

SECURITY REVIEW:
├─ Architecture → Section 3
├─ Threat Model → Section 4
├─ Code Issues → Section 5
└─ Recommendations → Section 11
```

---

## 💡 Pro Tips

1. **Templates are starting points** - Customize as needed for your organization
2. **Use existing templates** - Keep previous reports for reference and consistency
3. **Automate where possible** - Use security tools to populate sections automatically
4. **Document everything** - Include evidence and links to supporting documentation
5. **Timeline is critical** - Accurate dates and times are essential for audits and incidents
6. **Guardian focus** - Always analyze impact on Cerberus Guardian modules
7. **Be specific** - Use actual filenames, IPs, usernames, not placeholders
8. **Keep it professional** - Use clear language and professional formatting
9. **Get approvals early** - Don't wait until the end to get sign-offs
10. **Archive reports** - Keep historical records for trend analysis and compliance

---

## 📞 Support

**For questions about:**
- **Specific templates** → See README.md
- **CVSS scoring** → https://www.first.org/cvss/calculator/3.1
- **Audit standards** → Review ISO 27001, NIST CSF
- **Incident response** → See incident-response guide
- **Guardian architecture** → See guardian-architecture guide

---

## 📅 Version Information

- **Created:** 2024
- **Template Version:** 1.0
- **Cerberus Framework Version:** Compatible with v1.0+
- **Last Updated:** 2024

---

## Next Steps

1. **Review README.md** for detailed template information
2. **Copy your needed template** to a working directory
3. **Fill in metadata** (document information section)
4. **Work through sections** in order
5. **Get required approvals** before distribution
6. **Archive the completed report** for compliance

---

**Ready to get started?** Select a template and begin! 🚀
