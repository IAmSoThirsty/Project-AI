# Core AI Systems Dashboard

**Purpose:** Real-time monitoring of all six core AI systems (FourLaws, AIPersona, Memory, Learning, CommandOverride, PluginManager)

**Location:** `src/app/core/ai_systems.py`

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## System Status Overview

```dataview
TABLE WITHOUT ID
  file.link as "System",
  status as "Status",
  version as "Version",
  last_audit as "Last Audit",
  health_score as "Health"
FROM "docs/systems" OR "src/app/core"
WHERE system-type = "core-ai" OR contains(file.name, "ai_systems")
SORT health_score DESC
```

---

## Active AI Systems

```dataview
TABLE WITHOUT ID
  system-name as "System",
  primary-function as "Primary Function",
  data-persistence as "Data File",
  lines-of-code as "LOC",
  test-coverage as "Coverage"
FROM "docs/systems"
WHERE system-type = "core-ai"
SORT system-name ASC
```

---

## Recent System Updates

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  change-type as "Change Type",
  dateformat(file.mtime, "yyyy-MM-dd") as "Modified",
  summary as "Summary"
FROM "docs/systems" OR "docs/changelog"
WHERE contains(tags, "core-ai") OR contains(tags, "ai-systems")
SORT file.mtime DESC
LIMIT 10
```

---

## System Dependencies

```dataview
TABLE WITHOUT ID
  file.link as "System",
  dependencies as "Depends On",
  dependents as "Used By",
  integration-points as "Integration Points"
FROM "docs/systems"
WHERE system-type = "core-ai"
SORT length(dependents) DESC
```

---

## Key Metrics Summary

```dataview
TABLE WITHOUT ID
  metric-name as "Metric",
  current-value as "Current",
  target-value as "Target",
  trend as "Trend",
  last-measured as "Last Check"
FROM "docs/metrics"
WHERE metric-category = "core-ai"
SORT metric-priority ASC
```

---

## Critical Configuration Files

```dataview
LIST
FROM "data/ai_persona" OR "data/memory" OR "data/learning_requests" OR "data"
WHERE contains(file.ext, "json") AND contains(file.path, "data")
SORT file.name ASC
```

---

## System Health Indicators

```dataview
TABLE WITHOUT ID
  indicator-name as "Indicator",
  status as "Status",
  value as "Value",
  threshold as "Threshold",
  alert-level as "Alert"
FROM "docs/health"
WHERE system = "core-ai"
SORT alert-level DESC, indicator-name ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  doc-type as "Type",
  tags as "Tags",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs"
WHERE contains(tags, "ai-systems") OR contains(tags, "core") OR contains(file.name, "AI_PERSONA") OR contains(file.name, "LEARNING_REQUEST")
SORT file.mtime DESC
LIMIT 15
```

---

## Open Issues & Tasks

```dataview
TASK
FROM "docs/tasks" OR "docs/issues"
WHERE contains(tags, "core-ai") AND !completed
SORT priority DESC, due ASC
```

---

## Performance Benchmarks

```dataview
TABLE WITHOUT ID
  benchmark-name as "Benchmark",
  system as "System",
  execution-time as "Time (ms)",
  memory-usage as "Memory (MB)",
  last-run as "Last Run"
FROM "docs/benchmarks"
WHERE system-type = "core-ai"
SORT execution-time DESC
LIMIT 10
```

---

## Quick Actions

- 📊 [[AI_PERSONA_IMPLEMENTATION|View Persona Implementation]]
- 📚 [[LEARNING_REQUEST_IMPLEMENTATION|View Learning System]]
- 🔒 [[Command Override System|View Override System]]
- 🧠 [[Memory Expansion System|View Memory System]]
- ⚖️ [[Four Laws Implementation|View FourLaws System]]
- 🔌 [[Plugin System|View Plugin Manager]]

---

## System Architecture Map

```dataview
TABLE WITHOUT ID
  file.link as "Component",
  layer as "Layer",
  responsibility as "Responsibility",
  api-surface as "API Methods"
FROM "docs/architecture"
WHERE component-type = "core-ai"
SORT layer ASC, file.name ASC
```

---

**Query Performance:** Target <1s | **Data Sources:** docs/systems, src/app/core, data/ | **Refresh:** Real-time
