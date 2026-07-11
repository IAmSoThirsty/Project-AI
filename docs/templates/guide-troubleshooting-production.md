---
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "runbook"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "published"
author:
  name: "<%tp.user.name || 'Operations Team'%>"
category: "devops"
tags: ["troubleshooting", "runbook", "production", "incident-response"]
classification: "internal"
audience: ["devops", "developer", "support"]
problem_category: ""
summary: "Production troubleshooting runbook for <%`${await tp.system.prompt('Problem category:') || '[Problem]'}`%> with diagnostic steps and resolution procedures."
---

# Troubleshooting: <%tp.file.title%>

> **Severity:** <%`${await tp.system.prompt('Severity (P0/P1/P2/P3):') || 'P2'}`%>
> **Category:** <%`${await tp.system.prompt('Category (Performance/Availability/Security/Data):') || 'Performance'}`%>
> **Last Updated:** <%tp.date.now("YYYY-MM-DD")%>

## Symptoms

**Primary Symptoms:**
- [Symptom 1]: [Description]
- [Symptom 2]: [Description]
- [Symptom 3]: [Description]

**Observable Indicators:**
| Indicator | Normal | Problem | Critical |
|-----------|--------|---------|----------|
| [Metric 1] | [Value] | [Value] | [Value] |
| [Metric 2] | [Value] | [Value] | [Value] |

## Quick Diagnosis

**Is this the right runbook?**
```bash
# Run diagnostic check
[Command to verify problem type]
```

**Expected output if this is the issue:**
```
[Error message or pattern that confirms this is the right runbook]
```

## Immediate Actions (P0/P1 Only)

**Before diagnosing:**
1. [ ] [Emergency action 1]
2. [ ] [Emergency action 2]
3. [ ] [Emergency action 3]

## Diagnostic Steps

### Step 1: Check [Component]

**Command:**
```bash
# Diagnostic command
[Command]
```

**What to look for:**
- [Pattern 1]: Indicates [problem type]
- [Pattern 2]: Indicates [problem type]

**If found:** Go to [Resolution Section]
**If not found:** Proceed to Step 2

---

### Step 2: Check [Component]

**Command:**
```bash
[Diagnostic command]
```

**What to look for:**
```
[Expected output patterns]
```

**If found:** Go to [Resolution Section]
**If not found:** Proceed to Step 3

---

### Step 3: Check [Component]

**Command:**
```bash
[Diagnostic command]
```

**Decision Tree:**
```
Is [condition]?
├─ Yes → Resolution A
└─ No → Is [other condition]?
    ├─ Yes → Resolution B
    └─ No → Escalate
```

## Root Causes

### Cause 1: [Description]

**How to Identify:**
```bash
[Diagnostic command]
```

**Why This Happens:**
[Explanation]

**Resolution:** See [Resolution 1](#resolution-1)

---

### Cause 2: [Description]

**How to Identify:**
```bash
[Diagnostic command]
```

**Why This Happens:**
[Explanation]

**Resolution:** See [Resolution 2](#resolution-2)

## Resolutions

### Resolution 1: [Name]

**Applies to:** [Cause 1, Symptom X]

**Steps:**
1. **Backup current state:**
   ```bash
   [Backup command]
   ```

2. **Apply fix:**
   ```bash
   [Fix command]
   ```

3. **Verify resolution:**
   ```bash
   [Verification command]
   ```

**Expected result:**
```
[Success output]
```

**Rollback if needed:**
```bash
[Rollback command]
```

**Time to fix:** [Duration]

---

### Resolution 2: [Name]

**Applies to:** [Cause 2]

**Steps:**
1. [Step 1]
   ```bash
   [Command]
   ```

2. [Step 2]
   ```bash
   [Command]
   ```

**Verification:**
```bash
[Verification]
```

## Prevention

**Short-term:**
- [Action 1]: [Description]
- [Action 2]: [Description]

**Long-term:**
- [Action 1]: [Description]
- [Action 2]: [Description]

**Monitoring:**
```bash
# Set up alerting
[Alert configuration]
```

## Escalation Path

**If not resolved in [X] minutes:**

1. **Level 1:** [Contact/Team]
   - Contact: [Email/Slack]
   - Provide: [Information needed]

2. **Level 2:** [Contact/Team]
   - Contact: [Email/Slack/Phone]
   - SLA: [Response time]

3. **Level 3:** [Executive/Critical]
   - Contact: [On-call rotation]

## Post-Incident

**After resolution:**
- [ ] Document incident in [tracking system]
- [ ] Update this runbook with learnings
- [ ] Schedule postmortem if P0/P1
- [ ] Create prevention tasks

**Postmortem Template:** [[postmortem-template]]

## Related Runbooks

- [[troubleshooting-xxx]]: Related issue
- [[runbook-yyy]]: Related procedure

---

**Runbook Version:** 1.0
**Last Tested:** <%tp.date.now("YYYY-MM-DD")%>
**Next Review:** [Date]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
