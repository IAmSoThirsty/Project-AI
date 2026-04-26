# GUI Components Dashboard

**Purpose:** Monitor PyQt6 components, Leather Book UI, dashboard zones, and user interface status

**Core Systems:** LeatherBookInterface, LeatherBookDashboard, PersonaPanel, Image Generation UI

**Last Updated:** `= dateformat(this.file.mtime, "yyyy-MM-dd HH:mm")`

---

## GUI Component Status

```dataview
TABLE WITHOUT ID
  component-name as "Component",
  component-type as "Type",
  lines-of-code as "LOC",
  status as "Status",
  last-modified as "Modified"
FROM "docs/gui" OR "src/app/gui"
WHERE contains(tags, "gui") OR contains(file.path, "gui")
SORT component-type ASC, component-name ASC
```

---

## Main UI Components

```dataview
TABLE WITHOUT ID
  file.link as "Component",
  parent-class as "Parent",
  key-features as "Features",
  signal-count as "Signals",
  complexity as "Complexity"
FROM "docs/gui/components"
WHERE component-category = "main"
SORT complexity DESC
```

---

## Dashboard Zones

```dataview
TABLE WITHOUT ID
  zone-name as "Zone",
  zone-number as "#",
  purpose as "Purpose",
  widgets as "Widgets",
  interactions as "Interactions"
FROM "docs/gui/dashboard"
WHERE dashboard-type = "six-zone"
SORT zone-number ASC
```

---

## PyQt6 Signals & Slots

```dataview
TABLE WITHOUT ID
  component as "Component",
  signal-name as "Signal",
  connected-slots as "Connected To",
  usage-count as "Usage",
  documentation as "Docs"
FROM "docs/gui/signals"
WHERE framework = "pyqt6"
SORT component ASC, signal-name ASC
```

---

## UI Theme Configuration

```dataview
TABLE WITHOUT ID
  theme-element as "Element",
  tron-green as "Tron Green",
  tron-cyan as "Tron Cyan",
  background as "Background",
  usage-context as "Context"
FROM "docs/gui/themes"
WHERE theme-name = "leather-book"
SORT theme-element ASC
```

---

## Component Dependencies

```dataview
TABLE WITHOUT ID
  component as "Component",
  imports as "Imports",
  depends-on as "Dependencies",
  used-by as "Used By",
  coupling-score as "Coupling"
FROM "docs/gui/dependencies"
WHERE component-type = "gui"
SORT coupling-score DESC
```

---

## Recent UI Updates

```dataview
TABLE WITHOUT ID
  file.link as "File",
  change-type as "Change",
  dateformat(file.mtime, "yyyy-MM-dd") as "Date",
  summary as "Summary"
FROM "src/app/gui" OR "docs/gui"
WHERE contains(tags, "gui") OR contains(file.path, "gui")
SORT file.mtime DESC
LIMIT 20
```

---

## Image Generation UI

```dataview
TABLE WITHOUT ID
  component as "Component",
  layout-type as "Layout",
  features as "Features",
  async-handling as "Async",
  integration-points as "Integration"
FROM "docs/gui/image-generation"
WHERE ui-category = "image-gen"
SORT component ASC
```

---

## Widget Hierarchy

```dataview
TABLE WITHOUT ID
  widget-name as "Widget",
  parent-widget as "Parent",
  level as "Level",
  child-count as "Children",
  layout-manager as "Layout"
FROM "docs/gui/widgets"
WHERE contains(tags, "widget-hierarchy")
SORT level ASC, widget-name ASC
```

---

## Event Handlers

```dataview
TABLE WITHOUT ID
  handler-name as "Handler",
  component as "Component",
  event-type as "Event",
  trigger-conditions as "Trigger",
  complexity as "Complexity"
FROM "docs/gui/handlers"
WHERE handler-category = "event"
SORT complexity DESC, component ASC
```

---

## GUI Performance Metrics

```dataview
TABLE WITHOUT ID
  metric-name as "Metric",
  component as "Component",
  current-value as "Current",
  target-value as "Target",
  status as "Status"
FROM "docs/performance/gui"
WHERE metric-type = "gui-performance"
SORT status ASC, current-value DESC
```

---

## Persona Panel Configuration

```dataview
TABLE WITHOUT ID
  tab-name as "Tab",
  tab-number as "#",
  purpose as "Purpose",
  controls as "Controls",
  data-binding as "Data Binding"
FROM "docs/gui/persona-panel"
WHERE panel-type = "four-tab"
SORT tab-number ASC
```

---

## UI State Management

```dataview
TABLE WITHOUT ID
  state-variable as "State",
  component as "Component",
  persistence as "Persistent",
  update-frequency as "Update Freq",
  validation as "Validation"
FROM "docs/gui/state"
WHERE state-category = "ui"
SORT component ASC, state-variable ASC
```

---

## Threading & Async Operations

```dataview
TABLE WITHOUT ID
  operation as "Operation",
  thread-type as "Thread",
  component as "Component",
  duration as "Duration",
  safety-notes as "Safety"
FROM "docs/gui/threading"
WHERE threading-model = "pyqt6"
SORT duration DESC
```

---

## Layout Definitions

```dataview
TABLE WITHOUT ID
  layout-name as "Layout",
  layout-type as "Type",
  components as "Components",
  responsive as "Responsive",
  complexity as "Complexity"
FROM "docs/gui/layouts"
WHERE ui-framework = "pyqt6"
SORT complexity DESC
```

---

## Open GUI Issues

```dataview
TABLE WITHOUT ID
  issue-id as "ID",
  component as "Component",
  severity as "Severity",
  description as "Description",
  assigned-to as "Assigned"
FROM "docs/issues"
WHERE issue-type = "gui" AND status != "closed"
SORT severity DESC, component ASC
```

---

## GUI Test Coverage

```dataview
TABLE WITHOUT ID
  component as "Component",
  test-count as "Tests",
  coverage as "Coverage %",
  last-test-run as "Last Run",
  status as "Status"
FROM "docs/testing/gui"
WHERE test-category = "gui"
SORT coverage ASC
```

---

## User Interface Tasks

```dataview
TASK
FROM "docs/tasks"
WHERE contains(tags, "gui") OR contains(tags, "ui") AND !completed
SORT priority DESC, due ASC
```

---

## Related Documentation

```dataview
TABLE WITHOUT ID
  file.link as "Document",
  doc-type as "Type",
  component-focus as "Focus",
  dateformat(file.mtime, "yyyy-MM-dd") as "Updated"
FROM "docs/gui" OR "docs"
WHERE contains(tags, "gui") OR contains(file.name, "DEVELOPER_QUICK_REFERENCE") OR contains(file.name, "DESKTOP")
SORT file.mtime DESC
LIMIT 12
```

---

## Quick Actions

- 🖥️ [[Leather Book Interface|View Main Interface]]
- 📊 [[Dashboard Zones|View Dashboard Layout]]
- 🎭 [[Persona Panel|View AI Configuration UI]]
- 🎨 [[Image Generation UI|View Image Gen Interface]]
- 🔄 [[Signal/Slot Mapping|View Event System]]
- 📐 [[Layout System|View Layout Managers]]

---

**Query Performance:** Target <1s | **Data Sources:** src/app/gui, docs/gui, DEVELOPER_QUICK_REFERENCE.md | **Refresh:** Real-time
