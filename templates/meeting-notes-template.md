---
title: "Meeting Notes - <% tp.file.title %>"
date: <% tp.date.now("YYYY-MM-DD") %>
time: <% tp.date.now("HH:mm") %>
type: meeting
attendees: []
tags: [meeting, notes]
---

# 🗓️ Meeting: <% tp.file.title %>

**Date:** <% tp.date.now("dddd, MMMM DD, YYYY") %>  
**Time:** <% tp.date.now("HH:mm") %> - <%* tR += tp.date.now("HH:mm", 60) %>  
**Location:** <% tp.system.prompt("Meeting location (virtual/physical)") %>

## 👥 Attendees

<% tp.system.prompt("List attendees (comma-separated)").split(",").map(name => `- ${name.trim()}`).join("\n") %>

## 📌 Agenda

1. <% tp.system.prompt("Agenda item 1") %>
2. <% tp.system.prompt("Agenda item 2") %>
3. <% tp.system.prompt("Agenda item 3") %>

## 📝 Notes

### Discussion Points

#### <% tp.system.prompt("First topic") %>

- Key point 1
- Key point 2
- Key point 3

#### Topic 2

- 

#### Topic 3

- 

## ✅ Action Items

| Task | Assignee | Due Date | Status |
|------|----------|----------|--------|
| <% tp.system.prompt("Action item 1") %> | <% tp.system.prompt("Assignee") %> | <% tp.system.prompt("Due date (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD", 7)) %> | ⏳ Pending |
|      |          |          | ⏳ Pending |

## 🔜 Next Steps

1. 
2. 
3. 

## 📎 Attachments & Links

- 
- 

---

**Next Meeting:** <% tp.system.prompt("Next meeting date (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD", 7)) %>  
**Location:** 

<%* 
// Auto-create follow-up note
const followUp = await tp.system.suggester(
  ["Yes", "No"],
  [true, false],
  false,
  "Create follow-up meeting note?"
);
if (followUp) {
  tR += "\n\n> 📅 Follow-up scheduled";
}
%>
