---
title: "Project: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: project
status: <% tp.system.suggester(["🟢 Active", "🟡 Planning", "🔴 On Hold", "✅ Completed", "❌ Cancelled"], ["active", "planning", "on-hold", "completed", "cancelled"]) %>
priority: <% tp.system.suggester(["🔴 High", "🟡 Medium", "🟢 Low"], ["high", "medium", "low"]) %>
start_date: <% tp.system.prompt("Start date (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD")) %>
due_date: <% tp.system.prompt("Due date (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD", 30)) %>
tags: [project]
---

# 🚀 <% tp.file.title %>

## 📋 Project Overview

**Description:** <% tp.system.prompt("Project description (1-2 sentences)") %>

**Status:** <% tp.frontmatter.status %>  
**Priority:** <% tp.frontmatter.priority %>  
**Start Date:** <% tp.frontmatter.start_date %>  
**Due Date:** <% tp.frontmatter.due_date %>  
**Progress:** <%* tR += "0%" %>

---

## 🎯 Objectives & Goals

### Primary Objective
<% tp.system.prompt("What is the main goal?") %>

### Success Criteria
- [ ] <% tp.system.prompt("Success criterion 1") %>
- [ ] <% tp.system.prompt("Success criterion 2") %>
- [ ] <% tp.system.prompt("Success criterion 3") %>

### Key Results (OKRs)
1. **<% tp.system.prompt("Key Result 1") %>**
   - Measure: 
   - Target: 
   
2. **Key Result 2**
   - Measure: 
   - Target: 

3. **Key Result 3**
   - Measure: 
   - Target: 

---

## 👥 Team & Stakeholders

### Project Team
| Role | Name | Responsibility |
|------|------|----------------|
| Project Lead | <% tp.system.prompt("Project lead name") %> | Overall coordination |
| Developer | | |
| Designer | | |
| QA | | |

### Stakeholders
- **Sponsor:** 
- **Key Stakeholders:** 
- **End Users:** 

---

## 📅 Timeline & Milestones

| Milestone | Due Date | Status | Notes |
|-----------|----------|--------|-------|
| <% tp.system.prompt("Milestone 1") %> | <% tp.date.now("YYYY-MM-DD", 7) %> | ⏳ | |
| Milestone 2 | | ⏳ | |
| Milestone 3 | | ⏳ | |
| Final Delivery | <% tp.frontmatter.due_date %> | ⏳ | |

**Legend:** ⏳ Pending | 🏃 In Progress | ✅ Complete | ⚠️ At Risk | ❌ Blocked

---

## 📋 Task Breakdown

### Phase 1: Planning
- [ ] Define requirements
- [ ] Create technical specifications
- [ ] Resource allocation
- [ ] Risk assessment

### Phase 2: Development
- [ ] 
- [ ] 
- [ ] 

### Phase 3: Testing
- [ ] 
- [ ] 
- [ ] 

### Phase 4: Deployment
- [ ] 
- [ ] 
- [ ] 

### Phase 5: Post-Launch
- [ ] 
- [ ] 
- [ ] 

---

## 🛠️ Resources & Dependencies

### Required Resources
- **Budget:** <% tp.system.prompt("Budget (if applicable)", "N/A") %>
- **Tools:** 
- **Infrastructure:** 

### Dependencies
- **Blocked By:** 
- **Blocks:** 
- **Related Projects:** 

---

## ⚠️ Risks & Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| <% tp.system.prompt("Risk 1") %> | <% tp.system.suggester(["High", "Medium", "Low"], ["High", "Medium", "Low"]) %> | <% tp.system.suggester(["High", "Medium", "Low"], ["High", "Medium", "Low"]) %> | |
|      |             |        | |

---

## 📝 Notes & Updates

### <% tp.date.now("YYYY-MM-DD") %>
<% tp.system.prompt("Initial project notes") %>

---

## 📊 Metrics & KPIs

```dataview
TABLE status, priority, start_date, due_date
FROM "projects"
WHERE file.name = this.file.name
```

**Progress Tracking:**
- Tasks Completed: 0 / 0 (0%)
- Days Remaining: <%* 
  const due = new Date(tp.frontmatter.due_date);
  const now = new Date();
  const diff = Math.ceil((due - now) / (1000 * 60 * 60 * 24));
  tR += diff;
%> days

---

## 🔗 Related Documents

- [[Project Charter]]
- [[Technical Specifications]]
- [[Meeting Notes]]
- [[Sprint Planning]]

---

## 📎 Attachments & References

- 
- 

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>

<%* 
// Create project folder structure
const projectName = tp.file.title.replace(/[^a-z0-9]/gi, '-').toLowerCase();
const shouldCreateFolder = await tp.system.suggester(
  ["Yes - Create project folder", "No - Skip folder creation"],
  [true, false],
  false,
  "Create dedicated folder for this project?"
);

if (shouldCreateFolder) {
  tR += `\n\n> 📁 Project folder: projects/${projectName}`;
}
%>
