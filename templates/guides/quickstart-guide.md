---
title: "Quickstart: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: quickstart
template_type: guides
product_name: <% tp.system.prompt("Product/feature name") %>
time_to_complete: <% tp.system.prompt("Estimated time (e.g., 10 minutes)", "10 minutes") %>
difficulty: <% tp.system.suggester(["Beginner", "Intermediate", "Advanced"], ["beginner", "intermediate", "advanced"]) %>
status: <% tp.system.suggester(["✅ Current", "🔄 Updating"], ["current", "updating"]) %>
tags: [template, quickstart, getting-started, tutorial, templater]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [new-users, developers]
complexity_level: basic
estimated_completion: 20
requires: [templater-plugin]
review_cycle: quarterly
---

# 🚀 Quickstart: <% tp.file.title %>

## 📋 Overview

**Product:** <% tp.frontmatter.product_name %>  
**Time to Complete:** <% tp.frontmatter.time_to_complete %>  
**Difficulty:** <% tp.frontmatter.difficulty %>

### What You'll Learn
By the end of this quickstart, you'll be able to:
- <% tp.system.prompt("Learning outcome 1") %>
- <% tp.system.prompt("Learning outcome 2") %>
- <% tp.system.prompt("Learning outcome 3") %>

---

## ✅ Prerequisites

Before starting, ensure you have:
- [ ] <% tp.system.prompt("Prerequisite 1") %>
- [ ] <% tp.system.prompt("Prerequisite 2") %>
- [ ] <% tp.system.prompt("Prerequisite 3") %>

---

## 🔧 Step 1: Installation

Install <% tp.frontmatter.product_name %>:

```bash
<% tp.system.prompt("Installation command") %>
```

**Verify installation:**
```bash
<% tp.system.prompt("Verification command") %>
# Expected output: <% tp.system.prompt("Expected output") %>
```

---

## ⚙️ Step 2: Configuration

Create configuration file:

```bash
<% tp.system.prompt("Config creation command") %>
```

**Minimal configuration:**
```<% tp.system.prompt("config format (yaml/json/etc.)") %>
<% tp.system.prompt("key1") %>: <% tp.system.prompt("value1") %>
key2: value2
```

---

## 🎯 Step 3: Hello World

Create your first <% tp.system.prompt("entity (e.g., project, script, app)") %>:

```bash
<% tp.system.prompt("Creation command") %>
```

**Code:**
```<% tp.system.prompt("language") %>
<% tp.system.prompt("Hello World code") %>
```

**Run:**
```bash
<% tp.system.prompt("Run command") %>
```

**Expected Output:**
```
<% tp.system.prompt("Expected output") %>
```

---

## ✨ Step 4: Next Steps

Now that you're up and running, explore:
1. **<% tp.system.prompt("Next step 1") %>** - [[Link to guide]]
2. **Next step 2** - [[Link]]
3. **Next step 3** - [[Link]]

---

## 🐛 Common Issues

### Issue: <% tp.system.prompt("Common issue") %>
**Solution:** <% tp.system.prompt("Quick fix") %>

---

## 📚 Additional Resources

- [[Full Documentation]]
- [[<% tp.system.prompt("Related guide 1") %>]]
- **Community:** <% tp.system.prompt("Community link", "N/A") %>

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/guides/quickstart-guide.md`*
