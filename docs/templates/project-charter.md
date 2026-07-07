---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.file.last_modified_date("YYYY-MM-DD") %>
type: project-charter
category: project-management
status: draft
project_name: <% tp.system.prompt("Project name", "") %>
project_code: <% tp.system.prompt("Project code/ID", "") %>
project_phase: initiation
start_date: <% tp.system.prompt("Project start date (YYYY-MM-DD)", "") %>
target_end_date: <% tp.system.prompt("Target end date (YYYY-MM-DD)", "") %>
project_sponsor: <% tp.system.prompt("Project sponsor", "") %>
project_manager: <% tp.system.prompt("Project manager", "") %>
budget: <% tp.system.prompt("Total budget", "") %>
priority: <% tp.system.prompt("Priority (Critical/High/Medium/Low)", "Medium") %>
tags: [project, charter, project-management]
aliases: []
---

# <%* tR += tp.frontmatter.project_name %> - Project Charter

## Executive Summary

**Project Code:** <% tp.frontmatter.project_code %>
**Project Phase:** <% tp.frontmatter.project_phase %>
**Charter Version:** 1.0
**Last Updated:** <% tp.file.last_modified_date("YYYY-MM-DD") %>

### Quick Facts

| Attribute | Value |
|-----------|-------|
| **Project Name** | <% tp.frontmatter.project_name %> |
| **Project Sponsor** | <% tp.frontmatter.project_sponsor %> |
| **Project Manager** | <% tp.frontmatter.project_manager %> |
| **Start Date** | <% tp.frontmatter.start_date %> |
| **Target End Date** | <% tp.frontmatter.target_end_date %> |
| **Total Budget** | <% tp.frontmatter.budget %> |
| **Priority** | <% tp.frontmatter.priority %> |

### Elevator Pitch

> **30-Second Summary:**
> 

---

## 1. Project Purpose and Justification

### 1.1 Business Need

**Problem Statement:**


**Current State:**


**Desired Future State:**


### 1.2 Strategic Alignment

**Organizational Goals Supported:**
- 
- 
- 

**Strategic Initiatives:**
- 
- 

### 1.3 Business Case

**Expected Benefits:**
1. **Financial:** 
2. **Operational:** 
3. **Strategic:** 
4. **Customer/User:** 

**Return on Investment (ROI):**
- **Investment Required:** 
- **Expected Return:** 
- **Payback Period:** 
- **ROI Percentage:** 

### 1.4 Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| 1. Status Quo | | | Rejected |
| 2. | | | |
| 3. | | | |

---

## 2. Project Scope

### 2.1 In Scope

**Deliverables:**
1. 
2. 
3. 
4. 
5. 

**Features/Capabilities:**
- [ ] 
- [ ] 
- [ ] 
- [ ] 

**Affected Systems/Components:**
- 
- 

### 2.2 Out of Scope

**Explicitly Excluded:**
- 
- 
- 

**Future Phase Considerations:**
- 
- 

### 2.3 Assumptions

1. 
2. 
3. 
4. 

### 2.4 Constraints

**Technical:**
- 

**Resource:**
- 

**Time:**
- 

**Budget:**
- 

**Regulatory/Compliance:**
- 

---

## 3. Objectives and Success Criteria

### 3.1 Project Objectives

<%* const numObjectives = parseInt(tp.system.prompt("Number of objectives", "4")); %>
<%* for (let i = 1; i <= numObjectives; i++) { %>

#### Objective <%* tR += i %>: <% tp.system.prompt(`Objective ${i} title`, "") %>

**Description:** 

**SMART Criteria:**
- **Specific:** 
- **Measurable:** 
- **Achievable:** 
- **Relevant:** 
- **Time-bound:** 

**Priority:** High | Medium | Low

<%* } %>

### 3.2 Key Performance Indicators (KPIs)

| KPI | Metric | Target | Measurement Method | Frequency |
|-----|--------|--------|--------------------|-----------|
| 1. | | | | |
| 2. | | | | |
| 3. | | | | |
| 4. | | | | |

### 3.3 Success Criteria

**Project Success Definition:**
- 
- 
- 

**Acceptance Criteria:**
- [ ] All deliverables completed and approved
- [ ] All success criteria met or exceeded
- [ ] Budget variance < ±10%
- [ ] Schedule variance < ±10%
- [ ] Stakeholder satisfaction > 80%
- [ ] 

---

## 4. Stakeholder Analysis

### 4.1 Stakeholder Register

| Stakeholder | Role | Interest | Influence | Communication Need | Strategy |
|-------------|------|----------|-----------|-------------------|----------|
| | Sponsor | High | High | Weekly updates | Actively manage |
| | Manager | High | High | Daily standups | Actively manage |
| | | | | | |
| | | | | | |

### 4.2 RACI Matrix (Responsible, Accountable, Consulted, Informed)

| Activity | PM | Sponsor | Team | Stakeholder A | Stakeholder B |
|----------|----|---------| -----|---------------|---------------|
| Charter Approval | R | A | C | I | I |
| Requirements | R | C | R | C | I |
| Design | C | I | R | C | I |
| Development | A | I | R | I | I |
| Testing | R | C | R | C | I |
| Deployment | A | C | R | I | I |

---

## 5. High-Level Requirements

### 5.1 Functional Requirements

<%* const numFunctionalReqs = parseInt(tp.system.prompt("Number of functional requirements", "5")); %>
<%* for (let i = 1; i <= numFunctionalReqs; i++) { %>
**FR-<%* tR += String(i).padStart(3, '0') %>:** <% tp.system.prompt(`Functional requirement ${i}`, "") %>
<%* } %>

### 5.2 Non-Functional Requirements

**Performance:**
- 

**Security:**
- 

**Scalability:**
- 

**Usability:**
- 

**Maintainability:**
- 

**Compliance:**
- 

---

## 6. Project Organization

### 6.1 Organizational Chart

```
[Project Sponsor]
       |
[Project Manager]
       |
    -------
    |     |
[Team A] [Team B]
```

### 6.2 Roles and Responsibilities

#### Project Sponsor
- **Name:** <% tp.frontmatter.project_sponsor %>
- **Responsibilities:**
  - Provide strategic direction
  - Approve major decisions
  - Remove organizational roadblocks
  - Ensure budget availability

#### Project Manager
- **Name:** <% tp.frontmatter.project_manager %>
- **Responsibilities:**
  - Day-to-day project management
  - Team coordination
  - Risk management
  - Stakeholder communication
  - Deliverable quality

#### Core Team Members

| Name | Role | Responsibilities | Allocation |
|------|------|------------------|------------|
| | Lead Developer | Technical leadership | 100% |
| | Senior Developer | Feature implementation | 80% |
| | QA Lead | Testing strategy | 50% |
| | UX Designer | User experience | 40% |
| | | | |

---

## 7. Project Timeline

### 7.1 Major Milestones

| Milestone | Description | Target Date | Dependencies | Status |
|-----------|-------------|-------------|--------------|--------|
| M1 | Project kickoff | | | Not Started |
| M2 | Requirements complete | | M1 | Not Started |
| M3 | Design approved | | M2 | Not Started |
| M4 | Development complete | | M3 | Not Started |
| M5 | Testing complete | | M4 | Not Started |
| M6 | Go-live | | M5 | Not Started |

### 7.2 Phase Breakdown

#### Phase 1: Initiation (<% tp.system.prompt("Phase 1 duration", "2 weeks") %>)
- Charter approval
- Team assembly
- Initial planning

#### Phase 2: Planning (<% tp.system.prompt("Phase 2 duration", "4 weeks") %>)
- Detailed requirements
- Architecture design
- Resource planning

#### Phase 3: Execution (<% tp.system.prompt("Phase 3 duration", "12 weeks") %>)
- Development
- Testing
- Documentation

#### Phase 4: Closure (<% tp.system.prompt("Phase 4 duration", "2 weeks") %>)
- Deployment
- Training
- Handover
- Lessons learned

---

## 8. Budget and Resources

### 8.1 Budget Summary

| Category | Estimated Cost | Actual Cost | Variance | Notes |
|----------|----------------|-------------|----------|-------|
| Labor | | | | |
| Software/Licenses | | | | |
| Hardware | | | | |
| Training | | | | |
| Contingency (15%) | | | | |
| **Total** | **<% tp.frontmatter.budget %>** | | | |

### 8.2 Resource Requirements

**Human Resources:**
- 
- 

**Technical Resources:**
- 
- 

**Infrastructure:**
- 
- 

---

## 9. Risk Management

### 9.1 High-Level Risks

| Risk ID | Risk Description | Probability | Impact | Risk Score | Mitigation Strategy | Owner |
|---------|-----------------|-------------|--------|------------|---------------------|-------|
| R-001 | | Med | High | Med-High | | |
| R-002 | | Low | High | Med | | |
| R-003 | | Med | Med | Med | | |
| R-004 | | High | Low | Med | | |

**Risk Score Legend:**
- Probability: High (>70%), Medium (30-70%), Low (<30%)
- Impact: High (Major), Medium (Moderate), Low (Minor)

### 9.2 Risk Response Plan

**Risk Appetite:** 

**Escalation Criteria:**
- High risks: Immediate escalation to sponsor
- Medium risks: Include in weekly status
- Low risks: Monitor and document

---

## 10. Communication Plan

### 10.1 Communication Matrix

| Audience | Information | Frequency | Method | Owner |
|----------|-------------|-----------|--------|-------|
| Sponsor | Status, issues, decisions | Weekly | Report + meeting | PM |
| Team | Tasks, blockers | Daily | Standup | PM |
| Stakeholders | Progress, milestones | Bi-weekly | Email update | PM |
| Leadership | High-level status | Monthly | Dashboard | Sponsor |

### 10.2 Reporting Schedule

- **Daily:** Team standup
- **Weekly:** Sponsor update, risk review
- **Bi-weekly:** Stakeholder newsletter
- **Monthly:** Steering committee meeting
- **Ad-hoc:** Issue escalation, decision requests

---

## 11. Quality Management

### 11.1 Quality Standards

**Code Quality:**
- 

**Testing Standards:**
- 

**Documentation Standards:**
- 

**Acceptance Criteria:**
- 

### 11.2 Quality Assurance Process

1. **Peer Review:**
2. **Testing:**
3. **Acceptance:**
4. **Sign-off:**

---

## 12. Change Management

### 12.1 Change Control Process

1. **Submit:** Change request submitted
2. **Review:** Impact assessment
3. **Approve:** CAB approval if needed
4. **Implement:** Controlled implementation
5. **Verify:** Post-implementation review

### 12.2 Change Request Threshold

| Impact Level | Approval Authority | Timeline |
|--------------|-------------------|----------|
| Low (<$1K, <1 day effort) | PM | Immediate |
| Medium (<$10K, <1 week) | Sponsor | 48 hours |
| High (>$10K, >1 week) | CAB | 1 week |

---

## 13. Project Closure Criteria

- [ ] All deliverables completed and accepted
- [ ] All success criteria met
- [ ] Budget reconciled
- [ ] Lessons learned documented
- [ ] Resources released
- [ ] Support transition complete
- [ ] Final report approved
- [ ] Celebration completed!

---

## 14. Approvals

| Name | Role | Signature | Date |
|------|------|-----------|------|
| | Project Sponsor | | |
| | Project Manager | | |
| | Department Head | | |
| | Finance | | |

---

## 15. Appendices

### Appendix A: Acronyms and Definitions

| Term | Definition |
|------|------------|
| PM | Project Manager |
| CAB | Change Advisory Board |
| RACI | Responsible, Accountable, Consulted, Informed |
| | |

### Appendix B: References

- 
- 
- 

### Appendix C: Templates and Tools

- 

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | <% tp.file.creation_date("YYYY-MM-DD") %> | <% tp.system.prompt("Charter author", "") %> | Initial charter |
| | | | |

**Next Review Date:** <% tp.system.prompt("Next review date", "") %>

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

