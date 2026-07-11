---
created: <% tp.file.creation_date("YYYY-MM-DD") %>
updated: <% tp.file.last_modified_date("YYYY-MM-DD") %>
type: incident-postmortem
category: operations
status: draft
incident_id: <% tp.system.prompt("Incident ID", "INC-") %>
incident_date: <% tp.system.prompt("Incident date (YYYY-MM-DD)", tp.file.creation_date("YYYY-MM-DD")) %>
incident_time: <% tp.system.prompt("Incident start time (HH:MM UTC)", "") %>
severity: <% tp.system.prompt("Severity (SEV1/SEV2/SEV3/SEV4)", "SEV2") %>
incident_manager: <% tp.system.prompt("Incident manager", "") %>
services_affected: []
tags: [incident, postmortem, operations, sre]
aliases: []
---

# Incident Postmortem: <%* tR += tp.system.prompt("Incident title", "") %>

## Incident Summary

**Incident ID:** <% tp.frontmatter.incident_id %>
**Severity:** <% tp.frontmatter.severity %>
**Status:** Resolved | Mitigated | Ongoing

| Attribute | Value |
|-----------|-------|
| **Detection Time** | <% tp.frontmatter.incident_date %> <% tp.frontmatter.incident_time %> UTC |
| **Resolution Time** | <% tp.system.prompt("Resolution time (YYYY-MM-DD HH:MM UTC)", "") %> |
| **Total Duration** | <% tp.system.prompt("Total duration (HH:MM)", "") %> |
| **Incident Manager** | <% tp.frontmatter.incident_manager %> |
| **Services Affected** | <% tp.system.prompt("Services affected (comma-separated)", "") %> |
| **Customer Impact** | High | Medium | Low | None |

### One-Line Summary

>

### Impact Summary

**Users Affected:** <% tp.system.prompt("Number/percentage of users affected", "") %>
**Geographic Scope:** <% tp.system.prompt("Geographic scope (Global/Regional/etc)", "") %>
**Revenue Impact:** <% tp.system.prompt("Revenue impact estimate", "") %>
**SLA Breach:** Yes | No

---

## Severity Classification

<%* const severity = tp.frontmatter.severity; %>
<%* if (severity === "SEV1") { %>
**SEV1 - Critical**
- Complete system outage
- Data loss risk
- Security breach
- All hands on deck

<%* } else if (severity === "SEV2") { %>
**SEV2 - Major**
- Significant service degradation
- Major feature unavailable
- Affecting large customer segment
- Immediate response required

<%* } else if (severity === "SEV3") { %>
**SEV3 - Minor**
- Minor service degradation
- Limited customer impact
- Workaround available
- Scheduled response acceptable

<%* } else if (severity === "SEV4") { %>
**SEV4 - Informational**
- No customer impact
- Internal tooling affected
- Cosmetic issues
- Low priority fix

<%* } %>

---

## Timeline of Events

### Detection and Escalation

| Time (UTC) | Event | Owner | Notes |
|------------|-------|-------|-------|
| | 🔴 **Incident Start** | | First sign of anomaly |
| | 🔔 **Alert Triggered** | | Monitoring alert fired |
| | 👤 **On-Call Notified** | | PagerDuty/alert sent |
| | 📢 **Incident Declared** | | War room opened |
| | 🚨 **Escalated** | | Escalation to senior eng |

### Investigation and Mitigation

| Time (UTC) | Event | Owner | Notes |
|------------|-------|-------|-------|
| | 🔍 **Investigation Began** | | Initial diagnostics |
| | 💡 **Root Cause Identified** | | Issue found |
| | 🛠️ **Mitigation Started** | | Fix implementation began |
| | ✅ **Service Restored** | | Primary service recovered |
| | 🔄 **Full Recovery** | | All systems normal |

### Communication

| Time (UTC) | Event | Audience | Channel |
|------------|-------|----------|---------|
| | 📣 Internal notification | Team | Slack |
| | 📣 Customer communication | External | Status page |
| | 📣 Status update | Leadership | Email |
| | 📣 Resolution notice | All | All channels |

---

## Detailed Timeline

<%* const numTimelineEvents = parseInt(tp.system.prompt("Number of detailed timeline events", "8")); %>
<%* for (let i = 1; i <= numTimelineEvents; i++) { %>
### <% tp.system.prompt(`Event ${i} time (HH:MM UTC)`, "") %> - <% tp.system.prompt(`Event ${i} title`, "") %>

**Actor:** <% tp.system.prompt(`Event ${i} actor`, "") %>
**Action:**


**Impact:**


**Evidence:**
-

---
<%* } %>

---

## Root Cause Analysis

### What Happened?

**Technical Root Cause:**


**Contributing Factors:**
1.
2.
3.

**Proximate Cause:**


**Ultimate Cause:**


### Why Did It Happen?

**5 Whys Analysis:**

1. **Why did the incident occur?**

2. **Why was that the case?**

3. **Why was that condition present?**

4. **Why wasn't that prevented?**

5. **Why was the system vulnerable?**


### How Was It Detected?

**Detection Method:**
- [ ] Automated monitoring alert
- [ ] User report
- [ ] Internal team discovery
- [ ] Third-party notification
- [ ] Other: _______________

**Alert Details:**
- **Monitoring Tool:**
- **Alert Name:**
- **Threshold:**
- **Time to Alert:**

**Detection Gap Analysis:**


---

## Impact Assessment

### User Impact

**Affected Users:**
- **Total Users Affected:**
- **Percentage of User Base:**
- **User Segments:**
  -
  -

**User Experience Impact:**
- [ ] Complete service unavailability
- [ ] Severe performance degradation (>5s latency)
- [ ] Moderate performance degradation (2-5s latency)
- [ ] Minor performance degradation (<2s latency)
- [ ] Intermittent errors
- [ ] Feature unavailability
- [ ] Data integrity issues

**User-Reported Issues:**
- **Support Tickets:** <% tp.system.prompt("Number of support tickets", "0") %>
- **Social Media Mentions:**
- **Direct Complaints:**

### Business Impact

**Financial Impact:**
- **Revenue Lost:**
- **SLA Credits:**
- **Refunds/Compensation:**
- **Total Financial Impact:**

**Operational Impact:**
- **Engineering Hours:** <% tp.system.prompt("Total engineering hours spent", "") %>
- **Opportunity Cost:**
- **Team Morale:**

**Reputational Impact:**
- **Media Coverage:** Yes | No
- **Social Sentiment:** Positive | Neutral | Negative
- **Customer Trust:** Not Affected | Slightly Affected | Significantly Affected

### Technical Impact

**Systems Affected:**

| System/Service | Impact Level | Duration | Recovery Method |
|----------------|--------------|----------|-----------------|
| | Critical | | |
| | Major | | |
| | Minor | | |

**Data Impact:**
- [ ] No data loss
- [ ] Temporary data inconsistency (resolved)
- [ ] Permanent data loss
- [ ] Data corruption

**If data was affected:**
- **Records Affected:**
- **Data Recovery Method:**
- **Recovery Success Rate:**

---

## Response Evaluation

### What Went Well

1. ✅
2. ✅
3. ✅

### What Went Poorly

1. ❌
2. ❌
3. ❌

### Luck Factor

**What got lucky:**
-
-

**What could have been worse:**
-
-

---

## Mitigation Actions Taken

### Immediate Actions (During Incident)

1. **Action:**
   - **Time:**
   - **Outcome:**
   - **Effectiveness:** High | Medium | Low

2. **Action:**
   - **Time:**
   - **Outcome:**
   - **Effectiveness:** High | Medium | Low

### Short-term Fixes (Temporary)

1. **Action:**
   - **Implemented:** Yes | No
   - **Status:** Active | Removed
   - **Plan to Replace:**

---

## Corrective and Preventive Actions

### Action Items

<%* const numActionItems = parseInt(tp.system.prompt("Number of action items", "5")); %>
<%* for (let i = 1; i <= numActionItems; i++) { %>
#### Action Item <%* tR += i %>: <% tp.system.prompt(`Action ${i} title`, "") %>

**Type:** Prevention | Detection | Mitigation | Documentation | Process
**Priority:** P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)

**Description:**


**Rationale:**


**Assigned To:** <% tp.system.prompt(`Action ${i} owner`, "") %>
**Due Date:** <% tp.system.prompt(`Action ${i} due date`, "") %>
**Estimated Effort:** <% tp.system.prompt(`Action ${i} effort (hours/days)`, "") %>

**Acceptance Criteria:**
- [ ]
- [ ]
- [ ]

**Status:**
- [ ] Not Started
- [ ] In Progress
- [ ] Completed
- [ ] Verified

**Tracking:** <% tp.system.prompt(`Action ${i} ticket/issue number`, "") %>

---
<%* } %>

### Action Item Summary

| Priority | Category | Count | Completion Rate |
|----------|----------|-------|-----------------|
| P0 | Prevention | | 0% |
| P0 | Detection | | 0% |
| P1 | Mitigation | | 0% |
| P2 | Documentation | | 0% |
| P3 | Process | | 0% |

---

## Prevention Measures

### Technical Improvements

**Monitoring & Alerting:**
- [ ] Add new monitoring metrics
- [ ] Improve alert sensitivity
- [ ] Add redundant monitoring
- [ ] Create custom dashboards

**Architecture:**
- [ ] Add redundancy
- [ ] Improve failover
- [ ] Implement circuit breakers
- [ ] Add graceful degradation

**Infrastructure:**
- [ ] Scale resources
- [ ] Add load balancing
- [ ] Improve deployment process
- [ ] Implement chaos engineering

### Process Improvements

**Operational:**
- [ ] Update runbooks
- [ ] Improve incident response procedures
- [ ] Enhance communication protocols
- [ ] Conduct training

**Development:**
- [ ] Add automated tests
- [ ] Improve code review process
- [ ] Enhance deployment safeguards
- [ ] Implement feature flags

---

## Lessons Learned

### For Engineering

**Technical Lessons:**
1.
2.
3.

**Skills Gaps Identified:**
-
-

**Training Needs:**
-
-

### For Operations

**Process Lessons:**
1.
2.
3.

**Tool Improvements:**
-
-

### For Organization

**Communication Lessons:**
-

**Decision-Making Lessons:**
-

**Escalation Lessons:**
-

---

## Supporting Information

### Relevant Logs

**Application Logs:**
```
[Paste relevant log excerpts]
```

**System Metrics:**
- **CPU Usage:**
- **Memory Usage:**
- **Network I/O:**
- **Database Connections:**

### Related Documentation

- [[Runbook: <% tp.frontmatter.services_affected %>]]
- [[Architecture: <component>]]
- [[SOP: Incident Response]]

### External References

- Vendor support ticket:
- Related incidents:
- Industry postmortems:

---

## Communication Record

### Internal Communication

**Stakeholders Notified:**
- [ ] Engineering team
- [ ] Product team
- [ ] Customer support
- [ ] Leadership
- [ ] Sales team

**Communication Channels Used:**
- [ ] Slack #incidents
- [ ] Email
- [ ] War room (Zoom)
- [ ] Status page (internal)

### External Communication

**Customer Communication:**
- [ ] Status page update
- [ ] Email to affected customers
- [ ] In-app notification
- [ ] Social media update

**Communication Templates Used:**
- Initial notification:
- Status updates:
- Resolution notice:
- Postmortem summary:

---

## Metrics

### Response Metrics

| Metric | Target | Actual | Delta |
|--------|--------|--------|-------|
| **Time to Detect** | <5 min | | |
| **Time to Acknowledge** | <2 min | | |
| **Time to Escalate** | <10 min | | |
| **Time to Mitigate** | <30 min | | |
| **Time to Resolve** | <2 hours | | |
| **Time to Communicate** | <15 min | | |

### Performance Metrics

| Metric | Normal | During Incident | Impact |
|--------|--------|-----------------|--------|
| **Requests/sec** | | | |
| **Error Rate** | | | |
| **P50 Latency** | | | |
| **P95 Latency** | | | |
| **P99 Latency** | | | |

---

## Follow-up

### Postmortem Review Meeting

**Date:** <% tp.system.prompt("Postmortem meeting date", "") %>
**Attendees:**
-
-
-

**Discussion Points:**
-

**Decisions Made:**
-

### 30-Day Follow-up

**Date:**
**Action Items Completed:** ___%
**Remaining Work:**

### 90-Day Follow-up

**Date:**
**All Actions Completed:** Yes | No
**Effectiveness Assessment:**

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Incident Manager | <% tp.frontmatter.incident_manager %> | | |
| Engineering Lead | | | |
| SRE Lead | | | |
| VP Engineering | | | |

---

## Appendices

### Appendix A: Full Logs

[Attach or link to full logs]

### Appendix B: Screenshots/Dashboards

[Attach relevant screenshots]

### Appendix C: Communication Transcripts

[Attach Slack logs, emails, etc.]

### Appendix D: Code Changes

[Link to PRs, commits, config changes]

---

**Postmortem Author:** <% tp.system.prompt("Postmortem author", "") %>
**Last Updated:** <% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>
**Next Review:** 30 days from resolution

**Tags:** #incident #postmortem #sev<% tp.frontmatter.severity.toLowerCase() %> #lessons-learned

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
