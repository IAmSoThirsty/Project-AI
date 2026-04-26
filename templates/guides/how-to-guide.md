---
title: "How-To: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: how-to
template_type: guides
task_name: <% tp.system.prompt("Task (e.g., Deploy to Production)") %>
time_required: <% tp.system.prompt("Time needed (e.g., 15 minutes)", "15 minutes") %>
difficulty: <% tp.system.suggester(["Easy", "Moderate", "Complex"], ["easy", "moderate", "complex"]) %>
status: <% tp.system.suggester(["✅ Verified", "🔄 Needs Testing"], ["verified", "needs-testing"]) %>
tags: [template, how-to, procedure, task-guide, templater]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [operators, developers]
complexity_level: basic
estimated_completion: 20
requires: [templater-plugin]
review_cycle: quarterly
---

# 🔧 How-To: <% tp.file.title %>

## 📋 Task Overview

**Task:** <% tp.frontmatter.task_name %>  
**Time Required:** <% tp.frontmatter.time_required %>  
**Difficulty:** <% tp.frontmatter.difficulty %>

### Goal
<% tp.system.prompt("What will be accomplished? (1 sentence)") %>

---

## ✅ Prerequisites

Before starting, ensure:
- [ ] <% tp.system.prompt("Prerequisite 1") %>
- [ ] <% tp.system.prompt("Prerequisite 2") %>
- [ ] Access to: <% tp.system.prompt("Required access/permissions") %>

---

## 📝 Procedure

### Step 1: <% tp.system.prompt("Step 1 title") %>

<% tp.system.prompt("Step 1 description") %>

```bash
<% tp.system.prompt("Step 1 command(s)") %>
```

**Expected result:** <% tp.system.prompt("What happens") %>

---

### Step 2: <% tp.system.prompt("Step 2 title") %>

<% tp.system.prompt("Step 2 description") %>

```bash
<% tp.system.prompt("Step 2 command(s)") %>
```

---

### Step 3: <% tp.system.prompt("Step 3 title") %>

[Continue pattern]

---

### Step 4: Verification

Verify the task completed successfully:

```bash
<% tp.system.prompt("Verification command") %>
```

**Expected output:**
```
<% tp.system.prompt("Success output") %>
```

---

## ✅ Success Criteria

You're done when:
- [ ] <% tp.system.prompt("Success criterion 1") %>
- [ ] <% tp.system.prompt("Success criterion 2") %>
- [ ] All verification checks passed

---

## 🐛 Troubleshooting

### Problem: <% tp.system.prompt("Common problem") %>
**Solution:** <% tp.system.prompt("How to fix") %>

### Problem: Task fails at step X
**Solution:**
1. <% tp.system.prompt("Troubleshooting step 1") %>
2. Check logs: `<% tp.system.prompt("log location") %>`

---

## 📚 Related Guides

- [[<% tp.system.prompt("Related how-to 1") %>]]
- [[Related how-to 2]]

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/guides/how-to-guide.md`*
