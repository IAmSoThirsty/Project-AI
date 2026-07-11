---
# ═══════════════════════════════════════════════════════════════════════════
# AGENT TASK REPORT TEMPLATE
# Document Type: Agent Documentation (Task Completion Report)
# Target: AI agent task execution reports
# Schema Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

# Universal Fields (Required)
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "report"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "completed"
author:
  name: "<%`AGENT-${await tp.system.prompt('Agent number (e.g., 021):') || 'XXX'}`%>"
  email: ""
  github: ""

# Domain-Specific Fields
category: "governance"
tags:
  - "agent"
  - "task-report"
  - "execution"
  - "audit"
  - "deliverables"
classification: "internal"
audience:
  - "operator"
  - "architect"
  - "auditor"

# Agent Task-Specific Fields
agent_id: "<%`AGENT-${await tp.system.prompt('Agent number (e.g., 021):') || 'XXX'}`%>"
task_description: ""
deliverables: []
quality_gates_status: "passed"
completion_timestamp: "<%tp.date.now("YYYY-MM-DDTHH:mm:ss")%>Z"

# Quality Metadata
review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false

# Discovery & SEO
keywords:
  - "agent task"
  - "completion report"
  - "deliverables"
summary: "Task completion report for <%`AGENT-${await tp.system.prompt('Agent number (e.g., 021):') || 'XXX'}`%> documenting deliverables, quality verification, and execution audit trail."

# Relationships
related_docs: []
supersedes: null
---

# <%tp.file.title%>

> **Agent ID:** <%`AGENT-${await tp.system.prompt('Agent number (e.g., 021):') || 'XXX'}`%>
> **Agent Role:** <%`${await tp.system.prompt('Agent role (e.g., Template Creation Specialist):') || '[Agent Role]'}`%>
> **Task Status:** ✅ COMPLETED
> **Completion Time:** <%tp.date.now("YYYY-MM-DD HH:mm:ss")%>

---

## 📋 Executive Summary

**Task Charter:** [One-paragraph summary of assigned task]

**Outcome:** [High-level summary of what was accomplished]

**Quality Status:** <%`${await tp.system.prompt('Quality status (ALL GATES PASSED/PARTIAL/FAILED):') || 'ALL GATES PASSED'}`%>

**Next Actions:** [What should happen next, if anything]

---

## Table of Contents

1. [Agent Identification](#agent-identification)
2. [Task Charter](#task-charter)
3. [Execution Summary](#execution-summary)
4. [Deliverables](#deliverables)
5. [Quality Gates Verification](#quality-gates-verification)
6. [Audit Trail](#audit-trail)
7. [Blockers and Resolutions](#blockers-and-resolutions)
8. [Metrics and Performance](#metrics-and-performance)
9. [Lessons Learned](#lessons-learned)
10. [Next Steps](#next-steps)

---

## Agent Identification

### Agent Profile

| Property | Value |
|----------|-------|
| **Agent ID** | <%`AGENT-${await tp.system.prompt('Agent number (e.g., 021):') || 'XXX'}`%> |
| **Agent Name** | <%`${await tp.system.prompt('Agent name (e.g., Template Creation Specialist):') || '[Agent Name]'}`%> |
| **Agent Type** | <%`${await tp.system.prompt('Agent type (specialist/generalist/auditor):') || 'specialist'}`%> |
| **Charter Source** | <%`${await tp.system.prompt('Charter source (AGENT-XXX/Manual/Automated):') || '[Charter Source]'}`%> |
| **Execution Mode** | <%`${await tp.system.prompt('Execution mode (autonomous/supervised/collaborative):') || 'autonomous'}`%> |

### Context and Scope

**Upstream Dependencies:**
- [Agent/System that triggered this task]
- [Required resources/files/systems]

**Downstream Consumers:**
- [Agent/System that will use these deliverables]
- [Stakeholders awaiting completion]

**Scope Boundaries:**
- **In Scope:** [What was included in the task]
- **Out of Scope:** [What was explicitly excluded]
- **Assumptions:** [Assumptions made during execution]

---

## Task Charter

### Original Charter (Verbatim)

```
[Paste the original charter/instructions provided to the agent]
```

### Interpreted Requirements

**Mandatory Deliverables:**
1. [Deliverable 1 with criteria]
2. [Deliverable 2 with criteria]
3. [Deliverable 3 with criteria]

**Quality Gates:**
1. [Gate 1 with pass/fail criteria]
2. [Gate 2 with pass/fail criteria]
3. [Gate 3 with pass/fail criteria]

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

---

## Execution Summary

### Approach

**Strategy:** [High-level approach taken to accomplish the task]

**Methodology:**
1. **Phase 1:** [Description]
   - Actions: [List of actions]
   - Duration: [Time spent]
   - Outcome: [Result]

2. **Phase 2:** [Description]
   - Actions: [List of actions]
   - Duration: [Time spent]
   - Outcome: [Result]

3. **Phase 3:** [Description]
   - Actions: [List of actions]
   - Duration: [Time spent]
   - Outcome: [Result]

### Key Decisions

| Decision Point | Options Considered | Decision Made | Rationale |
|----------------|-------------------|---------------|-----------|
| [Decision 1] | [Option A, Option B] | [Choice] | [Why] |
| [Decision 2] | [Option A, Option B] | [Choice] | [Why] |

### Tools and Technologies Used

| Tool/Technology | Purpose | Version |
|----------------|---------|---------|
| [Tool 1] | [Purpose] | [Version] |
| [Tool 2] | [Purpose] | [Version] |

---

## Deliverables

### Deliverable 1: [Name]

**Type:** [File/Document/Code/Configuration/etc.]

**Location:** `[Full path or link]`

**Description:** [What is this deliverable and what does it accomplish?]

**Specifications Met:**
- ✅ [Requirement 1]
- ✅ [Requirement 2]
- ✅ [Requirement 3]

**Verification Method:**
```bash
# How to verify this deliverable works
[Command or test procedure]
```

**Sample Output:**
```
[Expected output or result]
```

---

### Deliverable 2: [Name]

**Type:** [File/Document/Code/Configuration/etc.]

**Location:** `[Full path or link]`

**Description:** [What is this deliverable and what does it accomplish?]

**Specifications Met:**
- ✅ [Requirement 1]
- ✅ [Requirement 2]

**Verification Method:**
```bash
# Verification procedure
[Command or test]
```

---

### Deliverable Summary Table

| # | Deliverable | Type | Location | Status | Notes |
|---|-------------|------|----------|--------|-------|
| 1 | [Name] | [Type] | `[Path]` | ✅ Complete | [Notes] |
| 2 | [Name] | [Type] | `[Path]` | ✅ Complete | [Notes] |
| 3 | [Name] | [Type] | `[Path]` | ✅ Complete | [Notes] |

**Total Deliverables:** [Count]
**Completion Rate:** 100%

---

## Quality Gates Verification

### Gate 1: [Gate Name]

**Criteria:** [Specific pass/fail criteria]

**Verification Method:** [How was this verified?]

**Result:** ✅ PASSED / ❌ FAILED / ⚠️ PARTIAL

**Evidence:**
```
[Evidence of gate passage - test output, metrics, screenshots, etc.]
```

**Notes:** [Any relevant observations]

---

### Gate 2: [Gate Name]

**Criteria:** [Specific pass/fail criteria]

**Verification Method:** [How was this verified?]

**Result:** ✅ PASSED / ❌ FAILED / ⚠️ PARTIAL

**Evidence:**
```
[Evidence of gate passage]
```

**Notes:** [Any relevant observations]

---

### Quality Gate Summary

| Gate | Criteria | Method | Result | Notes |
|------|----------|--------|--------|-------|
| Gate 1 | [Criteria] | [Method] | ✅ PASSED | [Notes] |
| Gate 2 | [Criteria] | [Method] | ✅ PASSED | [Notes] |
| Gate 3 | [Criteria] | [Method] | ✅ PASSED | [Notes] |

**Overall Quality Status:** ✅ ALL GATES PASSED

---

## Audit Trail

### Execution Timeline

| Timestamp | Event | Details |
|-----------|-------|---------|
| <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> | Task assigned | Charter received from [source] |
| [Time] | Phase 1 started | [Description] |
| [Time] | Phase 1 completed | [Deliverables created] |
| [Time] | Phase 2 started | [Description] |
| [Time] | Phase 2 completed | [Deliverables created] |
| [Time] | Quality gates verified | All gates passed |
| <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> | Task completed | All deliverables delivered |

### Files Modified/Created

| File Path | Action | Lines Changed | Purpose |
|-----------|--------|---------------|---------|
| `[path]` | Created | [Count] | [Purpose] |
| `[path]` | Modified | +[X] -[Y] | [Purpose] |
| `[path]` | Created | [Count] | [Purpose] |

### External API Calls

| Service | Endpoint | Calls | Purpose |
|---------|----------|-------|---------|
| [Service] | [Endpoint] | [Count] | [Purpose] |

---

## Blockers and Resolutions

### Blocker 1: [Description]

**Impact:** [How did this affect execution?]

**Root Cause:** [Why did this occur?]

**Resolution:** [How was it resolved?]

**Time Lost:** [Duration]

**Prevention:** [How to prevent in future]

---

### Blocker 2: [Description]

**Impact:** [How did this affect execution?]

**Root Cause:** [Why did this occur?]

**Resolution:** [How was it resolved?]

**Time Lost:** [Duration]

**Prevention:** [How to prevent in future]

---

### Blocker Summary

| Blocker | Impact | Resolution | Time Lost |
|---------|--------|------------|-----------|
| [Blocker 1] | [Impact] | [Resolution] | [Duration] |
| [Blocker 2] | [Impact] | [Resolution] | [Duration] |

**Total Blockers:** [Count]
**Total Time Lost:** [Duration]

---

## Metrics and Performance

### Execution Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Total Duration** | [X] hours | [Y] hours | ✅ Within target |
| **Deliverables Count** | [X] items | [Y] items | ✅ Met |
| **Quality Gates Passed** | 100% | 100% | ✅ Met |
| **Lines of Code/Docs** | [X] lines | [Y] lines | ✅ Met |
| **Test Coverage** | [X]% | [Y]% | ✅ Met |

### Resource Utilization

| Resource | Usage | Notes |
|----------|-------|-------|
| **API Calls** | [Count] | [Service names] |
| **Storage** | [Size] | [Location] |
| **Processing Time** | [Duration] | [Breakdown] |

### Quality Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Documentation Word Count** | [Count] | [Target: [X]+ words] |
| **Code Quality** | [Score/Grade] | [Linting/analysis results] |
| **Test Pass Rate** | [Percentage] | [X/Y tests passed] |

---

## Lessons Learned

### What Went Well

1. **[Success 1]:** [Description and why it worked]
2. **[Success 2]:** [Description and why it worked]
3. **[Success 3]:** [Description and why it worked]

### What Could Be Improved

1. **[Improvement 1]:** [Description and how to improve]
2. **[Improvement 2]:** [Description and how to improve]
3. **[Improvement 3]:** [Description and how to improve]

### Recommendations for Future Tasks

1. **Recommendation 1:** [Actionable recommendation]
2. **Recommendation 2:** [Actionable recommendation]
3. **Recommendation 3:** [Actionable recommendation]

---

## Next Steps

### Immediate Actions Required

- [ ] **Action 1:** [Description] - *Assigned to:* [Person/Agent] - *Due:* [Date]
- [ ] **Action 2:** [Description] - *Assigned to:* [Person/Agent] - *Due:* [Date]
- [ ] **Action 3:** [Description] - *Assigned to:* [Person/Agent] - *Due:* [Date]

### Follow-up Tasks

| Task | Description | Owner | Priority | Estimated Effort |
|------|-------------|-------|----------|------------------|
| [Task 1] | [Description] | [Owner] | [High/Medium/Low] | [Hours/Days] |
| [Task 2] | [Description] | [Owner] | [High/Medium/Low] | [Hours/Days] |

### Dependencies Unlocked

This task completion unblocks:
- [[task-or-agent-name]]: [How it's unblocked]
- [[task-or-agent-name]]: [How it's unblocked]

---

## Appendices

### Appendix A: Reference Materials

- [[reference-doc-1]]: [Description]
- [[reference-doc-2]]: [Description]
- External Link: [URL with description]

### Appendix B: Code Samples

```python
# Sample code demonstrating key implementation
[Code snippet]
```

### Appendix C: Test Results

```
[Test output or validation results]
```

---

## Sign-off

**Agent Execution:**
- **Agent ID:** <%`AGENT-${await tp.system.prompt('Agent number:') || 'XXX'}`%>
- **Completion Status:** ✅ COMPLETED
- **Quality Status:** ✅ ALL GATES PASSED
- **Timestamp:** <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> UTC

**Human Review Required:** <%`${await tp.system.prompt('Human review required? (Yes/No):') || 'No'}`%>

**Approvals:**
- [ ] Technical Review: [Reviewer name] - [Date]
- [ ] Quality Assurance: [Reviewer name] - [Date]
- [ ] Architecture Sign-off: [Reviewer name] - [Date]

---

**Report Generated:** <%tp.date.now("YYYY-MM-DD HH:mm:ss")%> UTC
**Report Version:** 1.0.0
**Document Status:** Completed

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
