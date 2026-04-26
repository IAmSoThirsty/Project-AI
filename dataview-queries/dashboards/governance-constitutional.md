# Governance & Constitutional Dashboard

**Purpose:** Monitor FourLaws ethics framework, learning approvals, Black Vault, and constitutional compliance

**Core Systems:** FourLaws, LearningRequestManager, CommandOverride

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Constitutional Framework Status

```dataview
TABLE WITHOUT ID
  law-name as "Law",
  priority as "Priority",
  enforcement-status as "Status",
  violation-count as "Violations",
  last-validated as "Last Check"
FROM "docs/governance"
WHERE law-type = "asimov" OR contains(tags, "four-laws")
SORT priority ASC
```

---

## Learning Request Pipeline

```dataview
TABLE WITHOUT ID
  request-id as "Request ID",
  status as "Status",
  category as "Category",
  submitted-date as "Submitted",
  approval-status as "Approval"
FROM "docs/learning-requests" OR "data/learning_requests"
WHERE contains(tags, "learning-request")
SORT submitted-date DESC
LIMIT 20
```

---

## Black Vault Contents

```dataview
TABLE WITHOUT ID
  content-hash as "Hash (SHA-256)",
  rejection-reason as "Reason",
  date-added as "Date Added",
  source-category as "Category",
  danger-level as "Danger Level"
FROM "docs/black-vault"
WHERE vault-type = "learning-denied"
SORT date-added DESC
LIMIT 15
```

---

## Command Override Audit Log

```dataview
TABLE WITHOUT ID
  timestamp as "Timestamp",
  command as "Command",
  override-reason as "Reason",
  user as "User",
  approval-chain as "Approval"
FROM "docs/audit-logs"
WHERE log-type = "command-override"
SORT timestamp DESC
LIMIT 25
```

---

## Ethics Validation Results

```dataview
TABLE WITHOUT ID
  action as "Action Requested",
  validation-result as "Result",
  violated-laws as "Violated Laws",
  context as "Context",
  timestamp as "Timestamp"
FROM "docs/ethics-validations"
WHERE contains(tags, "four-laws-validation")
SORT timestamp DESC
LIMIT 15
```

---

## Governance Policy Compliance

```dataview
TABLE WITHOUT ID
  policy-name as "Policy",
  compliance-status as "Status",
  coverage as "Coverage %",
  last-audit as "Last Audit",
  violations as "Violations"
FROM "docs/policies"
WHERE policy-category = "governance" OR policy-category = "ethics"
SORT compliance-status ASC, violations DESC
```

---

## Learning Request Statistics

```dataview
TABLE WITHOUT ID
  category as "Category",
  total-requests as "Total",
  approved as "Approved",
  denied as "Denied",
  pending as "Pending",
  approval-rate as "Approval %"
FROM "docs/statistics"
WHERE stat-type = "learning-requests"
SORT approval-rate ASC
```

---

## Constitutional Violations

```dataview
TABLE WITHOUT ID
  violation-id as "ID",
  law-violated as "Law Violated",
  severity as "Severity",
  action-attempted as "Action",
  prevention-method as "Prevention",
  timestamp as "Timestamp"
FROM "docs/violations"
WHERE violation-type = "constitutional"
SORT timestamp DESC, severity DESC
LIMIT 20
```

---

## Human-in-the-Loop Approvals

```dataview
TABLE WITHOUT ID
  approval-id as "ID",
  request-type as "Type",
  status as "Status",
  requested-by as "Requester",
  approver as "Approver",
  decision-date as "Decision Date"
FROM "docs/approvals"
WHERE approval-category = "learning" OR approval-category = "command-override"
SORT decision-date DESC
LIMIT 20
```

---

## Governance Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  policy-area as "Area",
  enforcement-level as "Enforcement",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/governance" OR "docs/policies"
WHERE contains(tags, "governance") OR contains(tags, "ethics") OR contains(tags, "constitutional")
SORT file.mtime DESC
```

---

## Safety Protocol Status

```dataview
TABLE WITHOUT ID
  protocol-name as "Protocol",
  active as "Active",
  trigger-conditions as "Triggers",
  escalation-path as "Escalation",
  test-status as "Tested"
FROM "docs/safety-protocols"
WHERE protocol-type = "governance" OR protocol-type = "override"
SORT protocol-name ASC
```

---

## Black Vault Analytics

```dataview
TABLE WITHOUT ID
  category as "Category",
  total-items as "Total Items",
  avg-danger-level as "Avg Danger",
  most-common-reason as "Common Reason",
  last-addition as "Last Added"
FROM "docs/vault-analytics"
WHERE vault-name = "black-vault"
SORT total-items DESC
```

---

## Open Governance Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "governance") OR contains(tags, "ethics") OR contains(tags, "constitutional") AND !completed
SORT priority DESC, due ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  doc-type as "Type",
  compliance-area as "Area",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs"
WHERE contains(file.name, "FOUR_LAWS") OR contains(file.name, "LEARNING_REQUEST") OR contains(file.name, "GOVERNANCE") OR contains(tags, "constitutional")
SORT file.mtime DESC
LIMIT 10
```

---

## Quick Actions

- ⚖️ [[Four Laws Implementation|View FourLaws System]]
- 📚 [[Learning Request Manager|View Learning System]]
- 🔒 [[Command Override System|View Override Protocols]]
- 🚫 [[Black Vault|View Black Vault Contents]]
- 📋 [[Governance Policies|View All Policies]]
- 🔍 [[Audit Logs|View Complete Audit Trail]]

---

**Query Performance:** Target <1s | **Data Sources:** docs/governance, docs/audit-logs, data/learning_requests | **Refresh:** Real-time
