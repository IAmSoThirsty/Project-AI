# Temporal Systems Dashboard

**Purpose:** Monitor time-based operations, scheduling, history tracking, and temporal data integrity

**Core Systems:** Memory (conversation history), Location Tracker (encrypted history), Learning (request timeline)

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Temporal System Status

```dataview
TABLE WITHOUT ID
  system-name as "System",
  temporal-feature as "Feature",
  retention-period as "Retention",
  history-size as "History Size",
  cleanup-status as "Cleanup"
FROM "docs/temporal"
WHERE system-type = "temporal"
SORT system-name ASC
```

---

## Conversation History

```dataview
TABLE WITHOUT ID
  conversation-id as "ID",
  user as "User",
  start-time as "Start",
  end-time as "End",
  message-count as "Messages",
  categories as "Categories"
FROM "docs/memory/conversations"
WHERE contains(tags, "conversation-history")
SORT start-time DESC
LIMIT 25
```

---

## Location History

```dataview
TABLE WITHOUT ID
  location-id as "ID",
  timestamp as "Timestamp",
  location-type as "Type",
  encrypted as "Encrypted",
  retention-days as "Retention"
FROM "docs/location/history"
WHERE contains(tags, "location-tracking")
SORT timestamp DESC
LIMIT 20
```

---

## Learning Request Timeline

```dataview
TABLE WITHOUT ID
  request-id as "Request",
  submitted-date as "Submitted",
  approval-date as "Approved",
  processing-time as "Time to Process",
  status as "Status"
FROM "docs/learning-requests"
WHERE contains(tags, "learning-timeline")
SORT submitted-date DESC
LIMIT 20
```

---

## Event Timeline

```dataview
TABLE WITHOUT ID
  event-id as "ID",
  event-type as "Type",
  timestamp as "Timestamp",
  system as "System",
  severity as "Severity",
  description as "Description"
FROM "docs/events"
WHERE contains(tags, "event-timeline")
SORT timestamp DESC
LIMIT 30
```

---

## Data Retention Policies

```dataview
TABLE WITHOUT ID
  data-type as "Data Type",
  retention-period as "Retention",
  auto-cleanup as "Auto Cleanup",
  last-cleanup as "Last Cleanup",
  records-deleted as "Deleted"
FROM "docs/temporal/retention"
WHERE policy-type = "retention"
SORT retention-period ASC
```

---

## Scheduled Operations

```dataview
TABLE WITHOUT ID
  operation-name as "Operation",
  schedule as "Schedule",
  last-run as "Last Run",
  next-run as "Next Run",
  status as "Status",
  duration as "Duration"
FROM "docs/temporal/scheduled"
WHERE operation-type = "scheduled"
SORT next-run ASC
```

---

## Temporal Integrity Checks

```dataview
TABLE WITHOUT ID
  check-name as "Check",
  data-source as "Data Source",
  last-check as "Last Check",
  anomalies-found as "Anomalies",
  status as "Status"
FROM "docs/temporal/integrity"
WHERE check-type = "temporal"
SORT last-check DESC
```

---

## Historical Data Growth

```dataview
TABLE WITHOUT ID
  data-category as "Category",
  current-size as "Size (MB)",
  growth-rate as "Growth/Day",
  projected-size as "Projected (30d)",
  cleanup-needed as "Cleanup"
FROM "docs/temporal/growth"
WHERE metric-type = "historical-growth"
SORT growth-rate DESC
```

---

## Audit Trail

```dataview
TABLE WITHOUT ID
  audit-id as "ID",
  timestamp as "Timestamp",
  user as "User",
  action as "Action",
  system as "System",
  details as "Details"
FROM "docs/audit-logs"
WHERE log-type = "audit"
SORT timestamp DESC
LIMIT 30
```

---

## Time-Series Data

```dataview
TABLE WITHOUT ID
  metric-name as "Metric",
  system as "System",
  sample-rate as "Sample Rate",
  retention as "Retention",
  compression as "Compressed"
FROM "docs/temporal/timeseries"
WHERE data-type = "timeseries"
SORT system ASC, metric-name ASC
```

---

## Timestamp Synchronization

```dataview
TABLE WITHOUT ID
  system as "System",
  time-source as "Time Source",
  sync-status as "Status",
  last-sync as "Last Sync",
  drift as "Drift (ms)"
FROM "docs/temporal/sync"
WHERE sync-enabled = true
SORT drift DESC
```

---

## Historical Queries Performance

```dataview
TABLE WITHOUT ID
  query-name as "Query",
  time-range as "Time Range",
  avg-duration as "Avg (ms)",
  max-duration as "Max (ms)",
  optimization-needed as "Optimize"
FROM "docs/temporal/query-performance"
WHERE query-type = "historical"
SORT avg-duration DESC
LIMIT 15
```

---

## Archival Status

```dataview
TABLE WITHOUT ID
  archive-name as "Archive",
  data-type as "Data Type",
  archive-date as "Archived",
  size as "Size (MB)",
  location as "Location",
  accessibility as "Access"
FROM "docs/temporal/archives"
WHERE archive-status = "active"
SORT archive-date DESC
LIMIT 20
```

---

## Temporal Anomalies

```dataview
TABLE WITHOUT ID
  anomaly-id as "ID",
  detection-time as "Detected",
  anomaly-type as "Type",
  affected-system as "System",
  severity as "Severity",
  resolution-status as "Status"
FROM "docs/temporal/anomalies"
WHERE anomaly-category = "temporal"
SORT detection-time DESC
LIMIT 15
```

---

## Backup History

```dataview
TABLE WITHOUT ID
  backup-id as "ID",
  backup-time as "Time",
  data-sources as "Sources",
  backup-size as "Size (MB)",
  duration as "Duration",
  status as "Status"
FROM "docs/temporal/backups"
WHERE backup-type = "automated"
SORT backup-time DESC
LIMIT 20
```

---

## Clock Drift Monitoring

```dataview
TABLE WITHOUT ID
  system as "System",
  reference-time as "Reference",
  local-time as "Local",
  drift-ms as "Drift (ms)",
  alert-threshold as "Alert At",
  last-check as "Last Check"
FROM "docs/temporal/clock-drift"
WHERE monitoring-enabled = true
SORT drift-ms DESC
```

---

## Temporal Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "temporal") OR contains(tags, "history") OR contains(tags, "scheduling") AND !completed
SORT priority DESC, due ASC
```

---

## Open Temporal Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  issue-type as "Type",
  system as "System",
  severity as "Severity",
  created as "Created",
  status as "Status"
FROM "docs/issues"
WHERE issue-category = "temporal" AND status != "closed"
SORT severity DESC, created ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  temporal-aspect as "Aspect",
  system-focus as "System",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/temporal" OR "docs"
WHERE contains(tags, "temporal") OR contains(tags, "history") OR contains(tags, "scheduling")
SORT file.mtime DESC
LIMIT 12
```

---

## Quick Actions

- ⏱️ [[Conversation History|View Memory Timeline]]
- 📍 [[Location History|View Location Timeline]]
- 📚 [[Learning Timeline|View Request History]]
- 🔍 [[Audit Trail|View Complete Audit Log]]
- 📦 [[Archival System|View Archives]]
- ⏰ [[Scheduled Operations|View Schedule]]

---

**Query Performance:** Target <1s | **Data Sources:** docs/temporal, data/memory, data/location | **Refresh:** Real-time
