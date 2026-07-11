---
# ═══════════════════════════════════════════════════════════════════════════
# ARCHITECTURAL DECISION RECORD (ADR) TEMPLATE
# Document Type: Architecture Documentation (Decision Record)
# Target: Significant architectural decisions with full context
# Schema Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

# Universal Fields (Required)
title: "ADR-<%`${await tp.system.prompt('ADR number (e.g., 001):') || 'XXX'}`%>: <%tp.file.title%>"
id: "adr-<%`${await tp.system.prompt('ADR number:') || 'xxx'}`%>-<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "decision_record"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "<%`${await tp.system.prompt('ADR status (proposed/accepted/deprecated/superseded):') || 'proposed'}`%>"
author:
  name: "<%tp.user.name || 'Architecture Team'%>"
  email: ""
  github: ""

# Domain-Specific Fields
category: "architecture"
tags:
  - "architecture"
  - "adr"
  - "decision"
  - "design"
  - "architecture/design"
classification: "internal"
audience:
  - "architect"
  - "developer"
  - "technical-lead"

# ADR-Specific Fields
decision_number: "<%`ADR-${await tp.system.prompt('ADR number:') || 'XXX'}`%>"
decision_title: "<%tp.file.title%>"
decision_status: "<%`${await tp.system.prompt('Status:') || 'proposed'}`%>"
decision_context: ""
decision_rationale: ""
consequences: []

# Quality Metadata
review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false

# Discovery & SEO
keywords:
  - "architectural decision"
  - "design choice"
  - "technical decision"
summary: "Architectural decision record for <%tp.file.title%> documenting context, decision, rationale, and consequences."

# Relationships
related_docs: []
supersedes: null
superseded_by: null
---

# ADR-<%`${await tp.system.prompt('ADR number:') || 'XXX'}`%>: <%tp.file.title%>

> **Status:** <%`${await tp.system.prompt('Status (PROPOSED/ACCEPTED/DEPRECATED/SUPERSEDED):') || 'PROPOSED'}`%>
> **Date:** <%tp.date.now("YYYY-MM-DD")%>
> **Deciders:** <%`${await tp.system.prompt('Deciders (e.g., Architecture Team):') || 'Architecture Team'}`%>
> **Technical Story:** <%`${await tp.system.prompt('Issue/ticket reference (e.g., #123):') || '[Issue reference]'}`%>

---

## Summary

**In Short:** [One-sentence summary of the decision]

**Decision:** [The specific decision that was made]

**Impact:** [High-level statement of impact and consequences]

---

## Table of Contents

1. [Context and Problem Statement](#context-and-problem-statement)
2. [Decision Drivers](#decision-drivers)
3. [Considered Options](#considered-options)
4. [Decision Outcome](#decision-outcome)
5. [Rationale](#rationale)
6. [Consequences](#consequences)
7. [Alternatives Considered](#alternatives-considered)
8. [Related Decisions](#related-decisions)
9. [Implementation Notes](#implementation-notes)
10. [References](#references)

---

## Context and Problem Statement

### Background

[Describe the context and background leading to this decision. What is the current situation?]

**Current State:**
- [Description of current architecture/situation]
- [What is working well]
- [What is not working or needs to change]

**Problem Statement:**
[Clear, concise statement of the problem this decision addresses]

**Scope:**
- **In Scope:** [What this decision covers]
- **Out of Scope:** [What this decision does not address]

### Business Context

**Business Drivers:**
- [Business reason 1]
- [Business reason 2]
- [Business reason 3]

**Stakeholders:**
| Stakeholder | Interest | Concerns |
|-------------|----------|----------|
| [Role/Person] | [What they care about] | [Their concerns] |
| [Role/Person] | [What they care about] | [Their concerns] |

**Timeline:**
- **Decision Deadline:** [Date]
- **Implementation Start:** [Date]
- **Target Completion:** [Date]

---

## Decision Drivers

### Functional Requirements

- [Requirement 1]: [Description]
- [Requirement 2]: [Description]
- [Requirement 3]: [Description]

### Non-Functional Requirements

**Performance:**
- [Performance requirement]

**Scalability:**
- [Scalability requirement]

**Security:**
- [Security requirement]

**Maintainability:**
- [Maintainability requirement]

**Cost:**
- [Cost constraints]

### Constraints

**Technical Constraints:**
- [Constraint 1]
- [Constraint 2]

**Organizational Constraints:**
- [Constraint 1]
- [Constraint 2]

**Resource Constraints:**
- **Budget:** [Budget information]
- **Timeline:** [Timeline constraints]
- **Team:** [Team size/skill constraints]

---

## Considered Options

### Option 1: <%`${await tp.system.prompt('Option 1 name:') || '[Option name]'}`%>

**Description:** [Detailed description of this option]

**How It Works:**
```
[Architecture diagram or pseudocode showing how this option would work]
```

**Pros:**
- ✅ [Advantage 1]
- ✅ [Advantage 2]
- ✅ [Advantage 3]

**Cons:**
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]
- ❌ [Disadvantage 3]

**Implementation Effort:** [High/Medium/Low]

**Cost:** [$X or effort estimate]

**Risk:** [High/Medium/Low]

**Example:**
```python
# Code example demonstrating this option
[Code snippet]
```

---

### Option 2: <%`${await tp.system.prompt('Option 2 name:') || '[Option name]'}`%>

**Description:** [Detailed description]

**How It Works:**
```
[Architecture diagram or pseudocode]
```

**Pros:**
- ✅ [Advantage 1]
- ✅ [Advantage 2]

**Cons:**
- ❌ [Disadvantage 1]
- ❌ [Disadvantage 2]

**Implementation Effort:** [High/Medium/Low]

**Cost:** [$X or effort estimate]

**Risk:** [High/Medium/Low]

**Example:**
```python
# Code example
[Code snippet]
```

---

### Option 3: <%`${await tp.system.prompt('Option 3 name:') || '[Option name]'}`%>

**Description:** [Detailed description]

**Pros:**
- ✅ [Advantage 1]

**Cons:**
- ❌ [Disadvantage 1]

**Implementation Effort:** [High/Medium/Low]

**Cost:** [$X]

**Risk:** [High/Medium/Low]

---

### Options Comparison Matrix

| Criterion | Option 1 | Option 2 | Option 3 | Weight |
|-----------|----------|----------|----------|--------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | High |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | High |
| **Cost** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Medium |
| **Complexity** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium |
| **Maintainability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | High |
| **Team Familiarity** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Low |
| **Total Score** | **[Score]** | **[Score]** | **[Score]** | |

*(⭐ = 1 point, scale 1-5)*

---

## Decision Outcome

### Chosen Option

**Selected:** <%`${await tp.system.prompt('Selected option name:') || 'Option [X]'}`%>

**Reason:** [Concise explanation of why this option was chosen over the others]

### Decision Statement

```
We will [specific decision] because [primary reason].

This approach [brief description of approach] to solve [problem statement].

We accept [trade-offs] in exchange for [benefits].
```

### Positive Consequences

- ✅ [Positive consequence 1]
- ✅ [Positive consequence 2]
- ✅ [Positive consequence 3]

### Negative Consequences

- ⚠️ [Negative consequence 1] - **Mitigation:** [How we'll address this]
- ⚠️ [Negative consequence 2] - **Mitigation:** [How we'll address this]

---

## Rationale

### Why This Decision Makes Sense

**Technical Rationale:**
[Detailed technical explanation of why this is the right choice]

**Business Rationale:**
[How this decision supports business objectives]

**Risk Mitigation:**
[How this decision reduces risk or manages uncertainty]

### Key Factors in Decision

1. **Factor 1:** [Explanation]
   - **Weight:** High/Medium/Low
   - **How Option Addresses:** [Description]

2. **Factor 2:** [Explanation]
   - **Weight:** High/Medium/Low
   - **How Option Addresses:** [Description]

3. **Factor 3:** [Explanation]
   - **Weight:** High/Medium/Low
   - **How Option Addresses:** [Description]

---

## Consequences

### Architectural Impact

**System Architecture:**
- [How this affects the overall system architecture]

**Component Interactions:**
- [Changes to how components interact]

**Data Flow:**
- [Changes to data flow patterns]

**Integration Points:**
- [Impact on external integrations]

### Team Impact

**Development:**
- [Impact on development team and workflows]

**Operations:**
- [Impact on operations and deployment]

**Skills Required:**
- [New skills or training needed]

### Long-Term Implications

**Flexibility:**
- [How this affects future flexibility]

**Tech Debt:**
- [Any technical debt introduced or eliminated]

**Scalability:**
- [Long-term scalability implications]

**Maintenance:**
- [Ongoing maintenance considerations]

---

## Alternatives Considered

### Alternative 1: [Name]

**Why Not Chosen:** [Specific reasons this was rejected]

**What We Learned:** [Insights from considering this option]

**Future Reconsideration:** [Under what circumstances would we reconsider?]

---

### Alternative 2: [Name]

**Why Not Chosen:** [Reasons]

**What We Learned:** [Insights]

---

## Related Decisions

### Upstream Decisions

**Depends On:**
- [[adr-xxx]]: [How this decision depends on that one]

### Downstream Decisions

**Enables:**
- [[adr-yyy]]: [What future decisions this enables]

### Related ADRs

- [[adr-zzz]]: [Related decision and relationship]

---

## Implementation Notes

### Implementation Strategy

**Phase 1: [Phase Name]**
- **Duration:** [Timeframe]
- **Actions:**
  1. [Action 1]
  2. [Action 2]
- **Deliverables:** [What will be delivered]

**Phase 2: [Phase Name]**
- **Duration:** [Timeframe]
- **Actions:**
  1. [Action 1]
  2. [Action 2]
- **Deliverables:** [What will be delivered]

### Success Criteria

- [ ] **Criterion 1:** [Measurable criterion]
- [ ] **Criterion 2:** [Measurable criterion]
- [ ] **Criterion 3:** [Measurable criterion]

### Rollback Plan

**If Implementation Fails:**
1. [Rollback step 1]
2. [Rollback step 2]

**Rollback Triggers:**
- [Trigger 1]
- [Trigger 2]

---

## References

### Documentation

- [[architecture-doc-pattern-xxx]]: [Related pattern documentation]
- [[guide-implementation-yyy]]: [Implementation guide]

### External Resources

- [Resource 1 Title](URL): [Brief description]
- [Resource 2 Title](URL): [Brief description]

### Prior Art

- [Example 1]: [Description of similar decision in other projects]
- [Example 2]: [Description]

---

## Change Log

### Version 1.0.0 (<%tp.date.now("YYYY-MM-DD")%>)

- Initial ADR creation
- Status: <%`${await tp.system.prompt('Initial status:') || 'Proposed'}`%>
- Decision documented with full context

---

## Approval

**Decision Makers:**
- [ ] **Principal Architect:** [Name] - [Date]
- [ ] **Technical Lead:** [Name] - [Date]
- [ ] **Product Owner:** [Name] - [Date]

**Review Process:**
1. [Review step 1]
2. [Review step 2]
3. [Review step 3]

**Approval Date:** [Date when decision was accepted]

---

**ADR Status:** <%`${await tp.system.prompt('Final status:') || 'PROPOSED'}`%>
**Next Review Date:** <%`${await tp.system.prompt('Next review date:') || '[Schedule review]'}`%>
**Maintainer:** <%tp.user.name || 'Architecture Team'%>

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
