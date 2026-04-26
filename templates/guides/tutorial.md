---
title: "Tutorial: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: tutorial
template_type: guides
tutorial_topic: <% tp.system.prompt("Topic (e.g., Building a REST API)") %>
duration: <% tp.system.prompt("Duration (e.g., 30 minutes)", "30 minutes") %>
difficulty: <% tp.system.suggester(["Beginner", "Intermediate", "Advanced"], ["beginner", "intermediate", "advanced"]) %>
status: <% tp.system.suggester(["✅ Current", "🔄 Updating"], ["current", "updating"]) %>
tags: [template, tutorial, learning, step-by-step, templater]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [learners, developers]
complexity_level: intermediate
estimated_completion: 25
requires: [templater-plugin]
review_cycle: quarterly
---

# 📚 Tutorial: <% tp.file.title %>

## 📋 Overview

**Topic:** <% tp.frontmatter.tutorial_topic %>  
**Duration:** <% tp.frontmatter.duration %>  
**Difficulty:** <% tp.frontmatter.difficulty %>

### Learning Objectives
By completing this tutorial, you will:
- <% tp.system.prompt("Objective 1") %>
- <% tp.system.prompt("Objective 2") %>
- <% tp.system.prompt("Objective 3") %>

---

## ✅ Prerequisites

**Required Knowledge:**
- <% tp.system.prompt("Knowledge 1 (e.g., Basic Python)") %>
- <% tp.system.prompt("Knowledge 2") %>

**Required Tools:**
- <% tp.system.prompt("Tool 1") %>
- <% tp.system.prompt("Tool 2") %>

---

## 🎯 What We'll Build

<% tp.system.prompt("Description of final result (2-3 sentences)") %>

**Final Result Preview:**
```
<% tp.system.prompt("Output/result preview") %>
```

---

## 📝 Step 1: <% tp.system.prompt("Step 1 title (e.g., Project Setup)") %>

### Objective
<% tp.system.prompt("What this step accomplishes") %>

### Instructions
1. <% tp.system.prompt("Instruction 1") %>
2. Instruction 2
3. Instruction 3

### Code
```<% tp.system.prompt("language") %>
<% tp.system.prompt("Step 1 code") %>
```

### Checkpoint
✅ Verify your work:
```bash
<% tp.system.prompt("Verification command") %>
```

**Expected:** <% tp.system.prompt("What you should see") %>

---

## 📝 Step 2: <% tp.system.prompt("Step 2 title") %>

### Objective
<% tp.system.prompt("What this step accomplishes") %>

### Instructions
1. <% tp.system.prompt("Instruction 1") %>
2. Instruction 2

### Code
```<% tp.system.prompt("language") %>
<% tp.system.prompt("Step 2 code") %>
```

### Checkpoint
✅ Test your progress:
```bash
<% tp.system.prompt("Test command") %>
```

---

## 📝 Step 3: <% tp.system.prompt("Step 3 title") %>

[Repeat structure]

---

## 🎨 Step 4: <% tp.system.prompt("Final step title (e.g., Adding Polish)") %>

### Objective
Complete the project with final touches

### Instructions
1. <% tp.system.prompt("Final instruction 1") %>
2. Final instruction 2

### Code
```<% tp.system.prompt("language") %>
<% tp.system.prompt("Final code") %>
```

---

## ✨ Final Result

Run the completed project:
```bash
<% tp.system.prompt("Run command") %>
```

**You should see:**
```
<% tp.system.prompt("Final output") %>
```

🎉 **Congratulations!** You've successfully <% tp.system.prompt("what they accomplished") %>.

---

## 🚀 Next Steps

Now that you've completed this tutorial, try:
1. **<% tp.system.prompt("Challenge 1") %>** - Extend functionality
2. **Challenge 2** - Add new features
3. **Challenge 3** - Optimize performance

---

## 📚 Further Reading

- [[<% tp.system.prompt("Related topic 1") %>]]
- [[Related topic 2]]
- **Documentation:** <% tp.system.prompt("Docs link") %>

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/guides/tutorial.md`*
