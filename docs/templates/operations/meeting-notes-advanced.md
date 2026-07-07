---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.file.last_modified_date("YYYY-MM-DD") %>
type: meeting-notes
category: operations
status: draft
meeting_date: <% tp.system.prompt("Meeting date (YYYY-MM-DD)", tp.file.creation_date("YYYY-MM-DD")) %>
meeting_time: <% tp.system.prompt("Meeting time (HH:MM)", "") %>
duration: <% tp.system.prompt("Duration (minutes)", "60") %>
location: <% tp.system.prompt("Location/Platform", "Virtual") %>
organizer: <% tp.system.prompt("Organizer", "") %>
attendees: []
tags: [meeting, notes]
aliases: []
---

# <%* const meetingTitle = tp.system.prompt("Meeting title", "Team Meeting"); tR += meetingTitle %>

## Meeting Information

| Field | Value |
|-------|-------|
| **Date** | <% tp.frontmatter.meeting_date %> |
| **Time** | <% tp.frontmatter.meeting_time %> |
| **Duration** | <% tp.frontmatter.duration %> minutes |
| **Location** | <% tp.frontmatter.location %> |
| **Organizer** | <% tp.frontmatter.organizer %> |

### Attendees

<%* const numAttendees = parseInt(tp.system.prompt("Number of attendees", "3")); %>
<%* for (let i = 1; i <= numAttendees; i++) { %>
<%* const attendeeName = tp.system.prompt(`Attendee ${i} name`, ""); %>
<%* const attendeeRole = tp.system.prompt(`${attendeeName} role`, ""); %>
- **<% attendeeName %>** - <% attendeeRole %>
<%* } %>

### Absent

- 

### Meeting Type

- [ ] Regular Status Meeting
- [ ] Planning Session
- [ ] Retrospective
- [ ] Decision Meeting
- [ ] Brainstorming
- [ ] Project Review
- [ ] Other: _______________

---

## Agenda

<%* const hasAgenda = tp.system.prompt("Include detailed agenda? (yes/no)", "yes").toLowerCase() === "yes"; %>
<%* if (hasAgenda) { %>
<%* const numAgendaItems = parseInt(tp.system.prompt("Number of agenda items", "4")); %>
<%* for (let i = 1; i <= numAgendaItems; i++) { %>

### <%* tR += i %>. <% tp.system.prompt(`Agenda item ${i} title`, "") %>

**Time Allocated:** <% tp.system.prompt(`Agenda item ${i} duration (minutes)`, "15") %> minutes
**Owner:** <% tp.system.prompt(`Agenda item ${i} owner`, "") %>
**Objective:** <% tp.system.prompt(`Agenda item ${i} objective`, "") %>

**Discussion Points:**
- 
- 
- 

<%* } %>
<%* } else { %>
1. 
2. 
3. 
4. 
<%* } %>

---

## Discussion Notes

### Key Discussion Topics

#### Topic 1: 

**Context:**


**Points Raised:**
- 
- 
- 

**Outcome:**


---

#### Topic 2: 

**Context:**


**Points Raised:**
- 
- 
- 

**Outcome:**


---

### Open Questions

| # | Question | Asked By | Status | Notes |
|---|----------|----------|--------|-------|
| 1 |  |  | Open |  |
| 2 |  |  | Open |  |
| 3 |  |  | Open |  |

---

## Decisions Made

<%* const numDecisions = parseInt(tp.system.prompt("Number of decisions made", "2")); %>
<%* for (let i = 1; i <= numDecisions; i++) { %>

### Decision <%* tR += i %>: <% tp.system.prompt(`Decision ${i} title`, "") %>

**Decision:** 

**Rationale:**


**Impact:**


**Stakeholders Affected:**
- 

**Implementation Timeline:** 

**Owner:** <% tp.system.prompt(`Decision ${i} owner`, "") %>

**Status:** 
- [ ] Approved
- [ ] Requires Follow-up
- [ ] Needs Confirmation
- [ ] On Hold

---

<%* } %>

## Action Items

| # | Action | Owner | Priority | Due Date | Status | Notes |
|---|--------|-------|----------|----------|--------|-------|
| 1 | | | High | | Not Started | |
| 2 | | | Medium | | Not Started | |
| 3 | | | Medium | | Not Started | |
| 4 | | | Low | | Not Started | |

### Action Item Details

#### AI-1: [Action Item Title]

**Description:**


**Owner:** 
**Priority:** High | Medium | Low
**Due Date:** 
**Dependencies:** 
**Success Criteria:**


**Status Updates:**
- [ ] Not Started
- [ ] In Progress
- [ ] Blocked
- [ ] Completed

---

## Next Steps

### Immediate (This Week)
1. 
2. 
3. 

### Short-term (This Month)
1. 
2. 

### Long-term (This Quarter)
1. 

---

## Meeting Effectiveness

### What Went Well
- 
- 
- 

### What Could Be Improved
- 
- 

### Action Items for Future Meetings
- 
- 

---

## Related Resources

### Related Documents
- 

### Previous Meetings
- 

### Follow-up Meetings
- **Next Meeting:** 
- **Frequency:** 

---

## Appendix

### Supporting Materials
- 

### Additional Notes


---

## Meeting Summary

<%* 
// Generate AI-powered summary if available
const projectAIUtils = tp.user["project-ai-utils"];
if (projectAIUtils) {
    tR += "> **Auto-generated Summary:** Use AI integration to generate meeting summary from notes.";
} else {
    tR += "**Key Takeaways:**\n\n1. \n2. \n3. \n\n**Critical Decisions:**\n\n- \n\n**Priority Actions:**\n\n- ";
}
%>

---

**Minutes Prepared By:** <% tp.system.prompt("Prepared by", "") %>
**Date Prepared:** <% tp.file.creation_date("YYYY-MM-DD") %>
**Distribution List:** All attendees + stakeholders

**Next Review:** <% tp.system.prompt("Next review date", "") %>

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

