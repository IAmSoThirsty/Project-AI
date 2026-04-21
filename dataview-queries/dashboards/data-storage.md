# Data & Storage Dashboard

**Purpose:** Monitor JSON persistence, data files, backup status, and data integrity across all systems

**Core Systems:** All AI systems (FourLaws, Persona, Memory, Learning, Override, Plugin)

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## Data Store Overview

```dataview
TABLE WITHOUT ID
  file.link as "Data File",
  file.size as "Size",
  system-owner as "Owner System",
  dateformat(file.mtime, "yyyy-MM-dd HH:mm") as "Last Modified",
  backup-status as "Backup"
FROM "data"
WHERE contains(file.ext, "json")
SORT file.mtime DESC
```

---

## System Data Files

```dataview
TABLE WITHOUT ID
  system-name as "System",
  data-file as "File Path",
  schema-version as "Schema",
  record-count as "Records",
  integrity-status as "Integrity"
FROM "docs/data"
WHERE data-type = "system-persistence"
SORT system-name ASC
```

---

## Data Persistence Patterns

```dataview
TABLE WITHOUT ID
  pattern-name as "Pattern",
  systems-using as "Used By",
  save-trigger as "Save Trigger",
  load-trigger as "Load Trigger",
  error-handling as "Error Handling"
FROM "docs/data/patterns"
WHERE pattern-category = "persistence"
SORT length(systems-using) DESC
```

---

## Recent Data Changes

```dataview
TABLE WITHOUT ID
  file.link as "File",
  dateformat(file.mtime, "yyyy-MM-dd HH:mm:ss") as "Modified",
  file.size as "Size",
  change-frequency as "Frequency"
FROM "data"
WHERE contains(file.ext, "json")
SORT file.mtime DESC
LIMIT 30
```

---

## Data Integrity Checks

```dataview
TABLE WITHOUT ID
  check-name as "Check",
  data-file as "File",
  last-check as "Last Check",
  status as "Status",
  issues-found as "Issues"
FROM "docs/data/integrity"
WHERE check-type = "automated"
SORT last-check DESC, issues-found DESC
```

---

## Backup Status

```dataview
TABLE WITHOUT ID
  data-file as "File",
  backup-location as "Backup Location",
  last-backup as "Last Backup",
  backup-size as "Size",
  retention-days as "Retention"
FROM "docs/data/backups"
WHERE backup-enabled = true
SORT last-backup ASC
```

---

## Data Schema Definitions

```dataview
TABLE WITHOUT ID
  schema-name as "Schema",
  version as "Version",
  data-file as "File",
  required-fields as "Required Fields",
  validation-rules as "Validation"
FROM "docs/data/schemas"
WHERE schema-type = "json"
SORT schema-name ASC
```

---

## Storage Statistics

```dataview
TABLE WITHOUT ID
  category as "Category",
  total-files as "Files",
  total-size as "Size (MB)",
  avg-file-size as "Avg Size",
  growth-rate as "Growth"
FROM "docs/data/statistics"
WHERE stat-type = "storage"
SORT total-size DESC
```

---

## Data Migration History

```dataview
TABLE WITHOUT ID
  migration-id as "ID",
  from-version as "From",
  to-version as "To",
  data-files as "Files",
  migration-date as "Date",
  status as "Status"
FROM "docs/data/migrations"
WHERE migration-type = "schema"
SORT migration-date DESC
LIMIT 15
```

---

## User Data Files

```dataview
TABLE WITHOUT ID
  file.link as "File",
  user-count as "Users",
  encryption as "Encrypted",
  dateformat(file.mtime, "yyyy-MM-dd") as "Modified"
FROM "data"
WHERE contains(file.name, "users") OR contains(file.name, "user")
SORT file.mtime DESC
```

---

## AI Persona State

```dataview
LIST
FROM "data/ai_persona"
WHERE contains(file.ext, "json")
SORT file.name ASC
```

---

## Memory System Data

```dataview
LIST
FROM "data/memory"
WHERE contains(file.ext, "json")
SORT file.name ASC
```

---

## Learning Requests Data

```dataview
LIST
FROM "data/learning_requests"
WHERE contains(file.ext, "json")
SORT file.name ASC
```

---

## Data Validation Results

```dataview
TABLE WITHOUT ID
  file as "File",
  validation-type as "Validation",
  passed as "Passed",
  warnings as "Warnings",
  errors as "Errors",
  last-validated as "Last Check"
FROM "docs/data/validation"
WHERE validation-enabled = true
SORT errors DESC, warnings DESC
```

---

## Orphaned Data Detection

```dataview
TABLE WITHOUT ID
  file-path as "File",
  orphan-reason as "Reason",
  last-accessed as "Last Access",
  recommended-action as "Action",
  cleanup-safe as "Safe to Clean"
FROM "docs/data/orphaned"
WHERE orphan-status = "detected"
SORT last-accessed ASC
```

---

## Data Access Patterns

```dataview
TABLE WITHOUT ID
  data-file as "File",
  read-frequency as "Reads",
  write-frequency as "Writes",
  access-pattern as "Pattern",
  optimization-needed as "Optimize"
FROM "docs/data/access-patterns"
WHERE contains(tags, "data-access")
SORT write-frequency DESC
```

---

## Storage Capacity

```dataview
TABLE WITHOUT ID
  location as "Location",
  used-space as "Used (MB)",
  available-space as "Available (MB)",
  usage-percent as "Usage %",
  alert-threshold as "Alert At %"
FROM "docs/data/capacity"
WHERE location-type = "data-storage"
SORT usage-percent DESC
```

---

## Open Data Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  issue-type as "Type",
  affected-files as "Files",
  severity as "Severity",
  status as "Status"
FROM "docs/issues"
WHERE issue-category = "data" AND status != "closed"
SORT severity DESC, issue-type ASC
```

---

## Data Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "data") OR contains(tags, "storage") OR contains(tags, "persistence") AND !completed
SORT priority DESC, due ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  topic as "Topic",
  data-focus as "Focus",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/data" OR "docs"
WHERE contains(tags, "data") OR contains(tags, "persistence") OR contains(file.name, "DATA")
SORT file.mtime DESC
LIMIT 12
```

---

## Quick Actions

- 💾 [[Data Persistence|View Persistence Layer]]
- 📊 [[Storage Statistics|View Usage Stats]]
- 🔍 [[Data Integrity|View Integrity Checks]]
- 💼 [[Backup System|View Backup Status]]
- 📋 [[Schema Definitions|View Data Schemas]]
- 🔄 [[Data Migration|View Migration History]]

---

**Query Performance:** Target <1s | **Data Sources:** data/, docs/data, src/app/core/ai_systems.py | **Refresh:** Real-time
