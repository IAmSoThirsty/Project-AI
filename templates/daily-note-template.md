---
title: "Daily Note - <% tp.date.now("YYYY-MM-DD") %>"
date: <% tp.date.now("YYYY-MM-DD") %>
day: <% tp.date.now("dddd") %>
week: <% tp.date.now("YYYY-[W]WW") %>
type: template
template_type: daily-note
tags: [template, daily-note, journal, productivity, templater]
last_verified: 2026-04-20
template_status: current
related_systems: [templater, obsidian, daily-notes]
stakeholders: [developers, learners, individual-contributors]
complexity_level: beginner
demonstrates: [daily-journaling, task-tracking, reflection, navigation-links, mood-tracking, templater-prompts, auto-file-creation]
runnable: true
estimated_completion: 3
requires: [templater-plugin, daily-notes-plugin]
review_cycle: quarterly
---

# 📅 <% tp.date.now("dddd, MMMM DD, YYYY") %>

[[<% tp.date.now("YYYY-MM-DD", -1, tp.file.title, "YYYY-MM-DD") %>|← Yesterday]] | [[<% tp.date.now("YYYY-MM-DD", 1, tp.file.title, "YYYY-MM-DD") %>|Tomorrow →]]

---

## 🌅 Morning Review

**Weather:** <% tp.system.prompt("Weather today") %>  
**Energy Level:** <% tp.system.suggester(["⚡⚡⚡⚡⚡ Excellent", "⚡⚡⚡⚡ Good", "⚡⚡⚡ Average", "⚡⚡ Low", "⚡ Very Low"], ["⚡⚡⚡⚡⚡", "⚡⚡⚡⚡", "⚡⚡⚡", "⚡⚡", "⚡"]) %>  
**Mood:** <% tp.system.suggester(["😊 Happy", "😐 Neutral", "😔 Down", "😤 Frustrated", "🤔 Contemplative"], ["😊", "😐", "😔", "😤", "🤔"]) %>

## 🎯 Today's Priorities

1. [ ] **<% tp.system.prompt("Priority 1") %>** ⭐⭐⭐
2. [ ] **<% tp.system.prompt("Priority 2") %>** ⭐⭐
3. [ ] **<% tp.system.prompt("Priority 3") %>** ⭐

## 📋 Tasks

### 🔴 High Priority
- [ ] 

### 🟡 Medium Priority
- [ ] 

### 🟢 Low Priority
- [ ] 

## 📝 Notes & Ideas

### Work
- 

### Personal
- 

### Learning
- 

## 🎉 Wins & Achievements

- 

## 🤔 Challenges & Blockers

- 

## 💡 Ideas & Insights

- 

## 🌙 Evening Reflection

**Completed Tasks:** <%* tR += "X/Y" %>  
**Top Win:** _To be filled at end of day_  
**Tomorrow's Focus:** _To be filled at end of day_

---

## 📊 Stats

**Created:** <% tp.file.creation_date("HH:mm") %>  
**Word Count:** <%* tR += tp.file.content.split(/\s+/).length %> words  
**Links:** <%* tR += (tp.file.content.match(/\[\[.*?\]\]/g) || []).length %>

## 🔗 Quick Links

- [[Weekly Review - <% tp.date.now("YYYY-[W]WW") %>|This Week]]
- [[Monthly Review - <% tp.date.now("YYYY-MM") %>|This Month]]
- [[Projects]]
- [[Goals]]

---

<%* 
// Auto-suggest creating tomorrow's note
const currentHour = new Date().getHours();
if (currentHour >= 20) {
  const createTomorrow = await tp.system.suggester(
    ["Yes", "No"],
    [true, false],
    false,
    "Create tomorrow's daily note?"
  );
  if (createTomorrow) {
    const tomorrow = tp.date.now("YYYY-MM-DD", 1);
    await tp.file.create_new(tp.file.find_tfile("daily-note-template.md"), tomorrow, false, tp.file.folder(true));
  }
}
%>
