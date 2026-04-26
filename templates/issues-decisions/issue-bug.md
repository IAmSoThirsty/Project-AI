---
title: "Issue: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: issue
doc_type: bug-report
template_type: issues
issue_type: <% tp.system.suggester(["Bug", "Performance", "Security", "Regression"], ["bug", "performance", "security", "regression"]) %>
severity: <% tp.system.suggester(["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"], ["critical", "high", "medium", "low"]) %>
status: <% tp.system.suggester(["🆕 New", "🔍 Investigating", "🔧 In Progress", "✅ Resolved", "❌ Won't Fix"], ["new", "investigating", "in-progress", "resolved", "wont-fix"]) %>
tags: [template, issue, bug-report, templater, <% tp.frontmatter.issue_type %>]
last_updated: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [developers, qa-team, product]
complexity_level: basic
estimated_completion: 15
requires: [templater-plugin]
review_cycle: as-needed
---

# 🐛 Issue: <% tp.file.title %>

## 📋 Issue Summary

**Type:** <% tp.frontmatter.issue_type %>  
**Severity:** <% tp.frontmatter.severity %>  
**Status:** <% tp.frontmatter.status %>  
**Reported:** <% tp.date.now("YYYY-MM-DD") %>  
**Reporter:** <% tp.system.prompt("Your name") %>

### Description
<% tp.system.prompt("One-line description of the issue") %>

---

## 🔍 Steps to Reproduce

1. <% tp.system.prompt("Step 1") %>
2. <% tp.system.prompt("Step 2") %>
3. <% tp.system.prompt("Step 3") %>
4. Observe the error

---

## ❌ Actual Behavior

<% tp.system.prompt("What actually happens?") %>

**Error Message (if any):**
```
<% tp.system.prompt("Error message / stack trace") %>
```

**Screenshot/Video:**
<% tp.system.prompt("Link to screenshot/video", "N/A") %>

---

## ✅ Expected Behavior

<% tp.system.prompt("What should happen instead?") %>

---

## 💻 Environment

**Operating System:** <% tp.system.prompt("OS (e.g., Windows 11, macOS 14)") %>  
**Application Version:** <% tp.system.prompt("Version") %>  
**Browser (if web):** <% tp.system.prompt("Browser + version", "N/A") %>  
**Other Details:** <% tp.system.prompt("Python version, Node version, etc.") %>

---

## 📊 Impact Assessment

**Affected Users:** <% tp.system.suggester(["All users", "Some users", "Admin only", "Single user"], ["all", "some", "admin", "single"]) %>  
**Workaround Available:** <% tp.system.suggester(["Yes", "No"], ["yes", "no"]) %>

**Business Impact:**
- <% tp.system.prompt("Impact statement (e.g., Blocks user login)") %>

---

## 💡 Proposed Solution

<% tp.system.prompt("Suggested fix (if known)", "Investigation needed") %>

---

## 📎 Additional Context

**Logs:**
```
<% tp.system.prompt("Relevant log excerpts") %>
```

**Related Issues:**
- [[<% tp.system.prompt("Related issue 1", "None") %>]]

---

## 🔄 Investigation Log

### <% tp.date.now("YYYY-MM-DD") %>
- Issue reported
- <% tp.system.prompt("Initial findings") %>

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/issues-decisions/issue-bug.md`*
