---
title: "ADR: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: decision
doc_type: architecture-decision-record
template_type: issues
adr_number: <% tp.system.prompt("ADR number (e.g., 001)") %>
status: <% tp.system.suggester(["💡 Proposed", "✅ Accepted", "⚠️ Deprecated", "❌ Superseded"], ["proposed", "accepted", "deprecated", "superseded"]) %>
decision_date: <% tp.date.now("YYYY-MM-DD") %>
tags: [template, adr, architecture-decision, design-decision, templater]
last_updated: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [architects, tech-leads, developers]
complexity_level: advanced
estimated_completion: 30
requires: [templater-plugin]
review_cycle: annual
---

# ADR-<% tp.frontmatter.adr_number %>: <% tp.file.title %>

## 📋 Metadata

**Status:** <% tp.frontmatter.status %>  
**Date:** <% tp.frontmatter.decision_date %>  
**Deciders:** <% tp.system.prompt("Who made this decision? (names/roles)") %>  
**Technical Story:** <% tp.system.prompt("Link to story/epic", "N/A") %>

---

## 🎯 Context and Problem Statement

<% tp.system.prompt("What is the issue we're addressing? (2-3 sentences)") %>

**Key Questions:**
- <% tp.system.prompt("Question 1 this decision must answer") %>
- <% tp.system.prompt("Question 2") %>
- <% tp.system.prompt("Question 3") %>

---

## 🔍 Decision Drivers

**Technical Drivers:**
- <% tp.system.prompt("Technical factor 1 (e.g., Scalability to 10K users)") %>
- <% tp.system.prompt("Technical factor 2") %>

**Business Drivers:**
- <% tp.system.prompt("Business factor 1") %>
- Business factor 2

**Constraints:**
- <% tp.system.prompt("Constraint 1 (e.g., Must use existing cloud provider)") %>
- Constraint 2

---

## 💡 Considered Options

### Option 1: <% tp.system.prompt("Option 1 name") %>

**Description:** <% tp.system.prompt("Option 1 description") %>

**Pros:**
- ✅ <% tp.system.prompt("Pro 1") %>
- ✅ Pro 2

**Cons:**
- ❌ <% tp.system.prompt("Con 1") %>
- ❌ Con 2

**Cost:** <% tp.system.prompt("Cost estimate", "N/A") %>  
**Effort:** <% tp.system.suggester(["Low", "Medium", "High"], ["low", "medium", "high"]) %>

---

### Option 2: <% tp.system.prompt("Option 2 name") %>

**Description:** <% tp.system.prompt("Option 2 description") %>

**Pros:**
- ✅ <% tp.system.prompt("Pro 1") %>
- ✅ Pro 2

**Cons:**
- ❌ <% tp.system.prompt("Con 1") %>
- ❌ Con 2

**Cost:** <% tp.system.prompt("Cost estimate") %>  
**Effort:** <% tp.system.suggester(["Low", "Medium", "High"], ["low", "medium", "high"]) %>

---

### Option 3: <% tp.system.prompt("Option 3 name (or remove if N/A)") %>

[Repeat structure]

---

## ✅ Decision Outcome

**Chosen Option:** "<% tp.system.prompt("Selected option name") %>"

**Rationale:**
<% tp.system.prompt("Why was this option chosen? (2-3 sentences)") %>

**Key Reasons:**
1. <% tp.system.prompt("Reason 1") %>
2. <% tp.system.prompt("Reason 2") %>
3. <% tp.system.prompt("Reason 3") %>

---

## 📊 Consequences

### Positive Consequences
- ✅ <% tp.system.prompt("Positive consequence 1") %>
- ✅ Positive consequence 2
- ✅ Positive consequence 3

### Negative Consequences
- ❌ <% tp.system.prompt("Negative consequence 1") %>
- ❌ Negative consequence 2

### Neutral Consequences
- ℹ️ <% tp.system.prompt("Neutral consequence 1 (e.g., Team needs training)") %>

---

## 🛠️ Implementation

**Approach:**
<% tp.system.prompt("High-level implementation approach") %>

**Steps:**
1. <% tp.system.prompt("Implementation step 1") %>
2. Step 2
3. Step 3

**Timeline:** <% tp.system.prompt("Implementation timeline", "TBD") %>  
**Owner:** <% tp.system.prompt("Implementation owner") %>

---

## 📏 Validation

**Success Criteria:**
- <% tp.system.prompt("Success criterion 1") %>
- Success criterion 2

**Validation Method:**
<% tp.system.prompt("How will we validate this decision?") %>

**Review Date:** <% tp.date.now("YYYY-MM-DD", 180) %> (6 months)

---

## 🔗 Related Decisions

- [[ADR-<% tp.system.prompt("related ADR number", "N/A") %>]] - <% tp.system.prompt("Relationship") %>
- [[Related decision 2]]

---

## 📚 References

1. <% tp.system.prompt("Reference 1 (article, RFC, documentation)") %>
2. Reference 2
3. Reference 3

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/issues-decisions/adr.md`*
