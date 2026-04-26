---
title: "Feature: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: feature
doc_type: feature-request
template_type: issues
feature_category: <% tp.system.suggester(["Enhancement", "New Feature", "Improvement", "Optimization"], ["enhancement", "new-feature", "improvement", "optimization"]) %>
priority: <% tp.system.suggester(["🔴 High", "🟡 Medium", "🟢 Low"], ["high", "medium", "low"]) %>
status: <% tp.system.suggester(["💡 Proposed", "🔍 Under Review", "✅ Approved", "🚧 In Development", "✅ Completed", "❌ Rejected"], ["proposed", "review", "approved", "development", "completed", "rejected"]) %>
tags: [template, feature-request, enhancement, templater, <% tp.frontmatter.feature_category %>]
last_updated: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [product, developers, users]
complexity_level: basic
estimated_completion: 15
requires: [templater-plugin]
review_cycle: as-needed
---

# ✨ Feature Request: <% tp.file.title %>

## 📋 Feature Summary

**Category:** <% tp.frontmatter.feature_category %>  
**Priority:** <% tp.frontmatter.priority %>  
**Status:** <% tp.frontmatter.status %>  
**Requested:** <% tp.date.now("YYYY-MM-DD") %>  
**Requester:** <% tp.system.prompt("Your name") %>

### One-Line Description
<% tp.system.prompt("Brief feature description (one sentence)") %>

---

## 🎯 Problem Statement

### What problem does this solve?
<% tp.system.prompt("Describe the problem or pain point (2-3 sentences)") %>

### Who experiences this problem?
<% tp.system.suggester(["All users", "Admin users", "Power users", "New users", "Specific persona"], ["all", "admin", "power", "new", "specific"]) %>

### How often?
<% tp.system.suggester(["Daily", "Weekly", "Monthly", "Occasionally", "Rarely"], ["daily", "weekly", "monthly", "occasionally", "rarely"]) %>

---

## 💡 Proposed Solution

### Feature Description
<% tp.system.prompt("Detailed description of proposed feature") %>

### User Stories
As a <% tp.system.prompt("user type") %>,  
I want to <% tp.system.prompt("action") %>,  
So that <% tp.system.prompt("benefit") %>.

### Acceptance Criteria
- [ ] <% tp.system.prompt("Criterion 1") %>
- [ ] <% tp.system.prompt("Criterion 2") %>
- [ ] <% tp.system.prompt("Criterion 3") %>

---

## 🔄 Alternatives Considered

### Alternative 1: <% tp.system.prompt("Alternative approach") %>
**Pros:** <% tp.system.prompt("Advantages") %>  
**Cons:** <% tp.system.prompt("Disadvantages") %>

### Alternative 2: Do Nothing
**Impact:** <% tp.system.prompt("What happens if we don't build this?") %>

---

## 📊 Impact & Value

**User Value:**
- <% tp.system.prompt("User benefit 1") %>
- User benefit 2

**Business Value:**
- <% tp.system.prompt("Business benefit (e.g., Increase retention by X%)") %>

**Effort Estimate:** <% tp.system.suggester(["Small (1-3 days)", "Medium (1-2 weeks)", "Large (2-4 weeks)", "Extra Large (1+ months)"], ["small", "medium", "large", "xl"]) %>

---

## 🛠️ Implementation Notes

### Technical Approach
<% tp.system.prompt("High-level technical approach", "TBD") %>

### Dependencies
- <% tp.system.prompt("Dependency 1 (e.g., Requires API v2)", "None") %>

### Risks
- <% tp.system.prompt("Risk 1 (e.g., Breaking change for existing users)", "None identified") %>

---

## 📸 Mockups/Examples

**Visual Reference:**
<% tp.system.prompt("Link to mockups/designs", "N/A") %>

**Example from other products:**
<% tp.system.prompt("Reference implementations", "N/A") %>

---

## 📅 Timeline

**Target Quarter:** Q<% tp.system.prompt("Quarter") %> <% tp.date.now("YYYY") %>  
**Milestone:** <% tp.system.prompt("Associated milestone", "TBD") %>

---

## 📚 Related

- [[Related Feature 1]]
- [[Related Issue]]

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/issues-decisions/feature-request.md`*
