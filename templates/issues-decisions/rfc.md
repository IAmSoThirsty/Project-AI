---
title: "RFC: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: proposal
doc_type: request-for-comments
template_type: issues
rfc_number: <% tp.system.prompt("RFC number (e.g., 001)") %>
status: <% tp.system.suggester(["📝 Draft", "🔍 Under Review", "✅ Accepted", "❌ Rejected", "⏸️ Deferred"], ["draft", "review", "accepted", "rejected", "deferred"]) %>
authors: <% tp.system.prompt("Author names (comma-separated)") %>
tags: [template, rfc, proposal, design-doc, templater]
last_updated: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [architects, developers, product]
complexity_level: advanced
estimated_completion: 35
requires: [templater-plugin]
review_cycle: as-needed
---

# RFC-<% tp.frontmatter.rfc_number %>: <% tp.file.title %>

## 📋 Metadata

**RFC Number:** <% tp.frontmatter.rfc_number %>  
**Status:** <% tp.frontmatter.status %>  
**Authors:** <% tp.frontmatter.authors %>  
**Created:** <% tp.date.now("YYYY-MM-DD") %>  
**Review Deadline:** <% tp.date.now("YYYY-MM-DD", 14) %>

---

## 📝 Abstract

<% tp.system.prompt("One-paragraph summary of the proposal") %>

---

## 🎯 Motivation

### Problem Statement
<% tp.system.prompt("What problem does this solve? (2-3 paragraphs)") %>

### Use Cases
1. **<% tp.system.prompt("Use case 1") %>**
   - Current state: <% tp.system.prompt("Current approach") %>
   - Desired state: <% tp.system.prompt("Desired approach") %>

2. **Use case 2**
   - Current state: 
   - Desired state: 

### Why Now?
<% tp.system.prompt("Why is this important to address now?") %>

---

## 📐 Detailed Design

### High-Level Overview
<% tp.system.prompt("High-level description of the solution (3-4 paragraphs)") %>

### Architecture
<% tp.system.prompt("Architectural changes and components") %>

### API Design (if applicable)
```<% tp.system.prompt("language") %>
# Proposed API
<% tp.system.prompt("API example code") %>
```

### Data Model
```<% tp.system.prompt("format (yaml/json/sql)") %>
<% tp.system.prompt("Data model definition") %>
```

### Implementation Details
<% tp.system.prompt("Key implementation details") %>

---

## 🔄 Rationale and Alternatives

### Why This Approach?
<% tp.system.prompt("Explanation of chosen approach") %>

### Alternative 1: <% tp.system.prompt("Alternative approach 1") %>
**Why not chosen:** <% tp.system.prompt("Reason") %>

### Alternative 2: <% tp.system.prompt("Alternative approach 2") %>
**Why not chosen:** <% tp.system.prompt("Reason") %>

### Alternative 3: Do Nothing
**Impact:** <% tp.system.prompt("Consequences of not implementing") %>

---

## 📚 Prior Art

**Similar Solutions:**
1. <% tp.system.prompt("Example from other projects/companies") %>
   - How it works: 
   - What we're adopting: 
   - What we're changing: 

2. Example 2

**References:**
- <% tp.system.prompt("Reference 1 (article/repo/RFC)") %>
- Reference 2

---

## ❓ Unresolved Questions

### Open Questions
1. <% tp.system.prompt("Question 1 needing resolution") %>
   - **Impact:** <% tp.system.prompt("Why this matters") %>
   - **Options:** <% tp.system.prompt("Possible answers") %>

2. Question 2

### Future Work
- <% tp.system.prompt("Future enhancement 1") %>
- Future enhancement 2

---

## 📊 Impact Analysis

### Technical Impact
**Changes Required:**
- <% tp.system.prompt("Technical change 1") %>
- Technical change 2

**Breaking Changes:**
<% tp.system.prompt("Any breaking changes?", "None") %>

### Operational Impact
**Deployment:** <% tp.system.prompt("Deployment changes needed") %>  
**Monitoring:** <% tp.system.prompt("New monitoring required") %>  
**Documentation:** <% tp.system.prompt("Docs to update") %>

### Team Impact
**Training Needed:** <% tp.system.suggester(["Yes", "No"], ["yes", "no"]) %>  
**New Skills Required:** <% tp.system.prompt("Skills needed", "None") %>

---

## 📅 Implementation Timeline

### Phases
**Phase 1: <% tp.system.prompt("Phase 1 name (e.g., Design & Prototype)") %>**
- Duration: <% tp.system.prompt("Duration") %>
- Deliverables: <% tp.system.prompt("Deliverables") %>

**Phase 2: <% tp.system.prompt("Phase 2 name") %>**
- Duration: 
- Deliverables: 

**Phase 3: <% tp.system.prompt("Phase 3 name") %>**
- Duration: 
- Deliverables: 

### Milestones
| Milestone | Target Date | Owner |
|-----------|-------------|-------|
| <% tp.system.prompt("Milestone 1") %> | <% tp.date.now("YYYY-MM-DD", 30) %> | <% tp.system.prompt("Owner") %> |
| Milestone 2 | | |

---

## 🎯 Success Metrics

**How we'll measure success:**
- <% tp.system.prompt("Metric 1 (e.g., Reduce latency by 30%)") %>
- <% tp.system.prompt("Metric 2") %>
- <% tp.system.prompt("Metric 3") %>

**Validation Plan:**
<% tp.system.prompt("How will we validate success?") %>

---

## 🔐 Security & Privacy

**Security Considerations:**
- <% tp.system.prompt("Security consideration 1") %>
- Security consideration 2

**Privacy Considerations:**
- <% tp.system.prompt("Privacy consideration 1") %>
- Privacy consideration 2

**Compliance:**
<% tp.system.prompt("Compliance requirements (GDPR, HIPAA, etc.)", "N/A") %>

---

## 💰 Cost Analysis

**Development Cost:** <% tp.system.prompt("Development effort estimate") %>  
**Infrastructure Cost:** <% tp.system.prompt("Infrastructure cost change") %>  
**Maintenance Cost:** <% tp.system.prompt("Ongoing cost estimate") %>

**ROI:** <% tp.system.prompt("Expected return on investment") %>

---

## 👥 Stakeholder Review

### Required Approvals
- [ ] <% tp.system.prompt("Stakeholder 1 (e.g., Engineering Lead)") %>
- [ ] <% tp.system.prompt("Stakeholder 2 (e.g., Product Manager)") %>
- [ ] <% tp.system.prompt("Stakeholder 3 (e.g., Security Team)") %>

### Feedback Log
**<% tp.date.now("YYYY-MM-DD") %>** - <% tp.system.prompt("Reviewer") %>: <% tp.system.prompt("Feedback") %>

---

## 📖 References

1. <% tp.system.prompt("Reference 1") %>
2. Reference 2
3. Reference 3

---

## 🔄 Change Log

**<% tp.date.now("YYYY-MM-DD") %>** - Initial draft  
**[Date]** - Updated based on feedback

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/issues-decisions/rfc.md`*
