# Components by Type - Dataview Query

**Purpose:** Dynamically index all components organized by their type (module, agent, system, integration, service, engine, kernel, runtime, architecture, workflow).

**Performance:** <1 second for vaults with <10,000 notes  
**Auto-refresh:** Yes (real-time)  
**Last Updated:** 2026-04-21

---

## Query: All Components by Type

```dataview
TABLE 
    file.name as "Component",
    status as "Status",
    priority as "Priority",
    stakeholders as "Stakeholders",
    created as "Created",
    last_verified as "Last Verified"
FROM ""
WHERE type != null
SORT type ASC, priority ASC, file.name ASC
GROUP BY type
```

---

## Query: Components by Specific Type

### Architecture Documents

```dataview
TABLE 
    file.name as "Architecture",
    architecture_layer as "Layer",
    design_pattern as "Patterns",
    status as "Status",
    priority as "Priority",
    last_verified as "Last Verified"
FROM ""
WHERE type = "architecture"
SORT priority ASC, file.name ASC
```

### Engine Components

```dataview
TABLE 
    file.name as "Engine",
    engine_type as "Engine Type",
    implementation_status as "Implementation",
    language as "Language",
    status as "Status",
    last_verified as "Last Verified"
FROM ""
WHERE type CONTAINS "engine" OR engine_type != null
SORT engine_type ASC, file.name ASC
```

### Guide Documents

```dataview
TABLE 
    file.name as "Guide",
    difficulty as "Difficulty",
    estimated_reading_time as "Reading Time",
    audience as "Audience",
    status as "Status",
    last_verified as "Last Verified"
FROM ""
WHERE type = "guide"
SORT difficulty ASC, file.name ASC
```

### Service Components

```dataview
TABLE 
    file.name as "Service",
    component as "Components",
    status as "Status",
    priority as "Priority",
    stakeholders as "Stakeholders",
    last_verified as "Last Verified"
FROM ""
WHERE type = "service" OR component != null
SORT priority ASC, file.name ASC
```

### Integration Components

```dataview
TABLE 
    file.name as "Integration",
    related_systems as "Related Systems",
    depends_on as "Dependencies",
    status as "Status",
    priority as "Priority",
    last_verified as "Last Verified"
FROM ""
WHERE type = "integration" OR related_systems != null
SORT priority ASC, file.name ASC
```

### Kernel/Runtime Components

```dataview
TABLE 
    file.name as "Kernel/Runtime",
    type as "Type",
    language as "Language",
    implementation_status as "Implementation",
    status as "Status",
    last_verified as "Last Verified"
FROM ""
WHERE type CONTAINS "kernel" OR type CONTAINS "runtime"
SORT type ASC, file.name ASC
```

### Workflow Components

```dataview
TABLE 
    file.name as "Workflow",
    workflow_type as "Workflow Type",
    triggers as "Triggers",
    status as "Status",
    priority as "Priority",
    last_verified as "Last Verified"
FROM ""
WHERE type = "workflow" OR workflow_type != null
SORT priority ASC, file.name ASC
```

---

## DataviewJS: Advanced Type Analysis

For more complex analysis with statistics:

```dataviewjs
// Group components by type with counts and status breakdown
const components = dv.pages("")
    .where(p => p.type != null);

// Group by type
const byType = components.groupBy(p => p.type);

// Create summary table
const summary = byType.map(group => {
    const active = group.rows.where(r => r.status === "active").length;
    const deprecated = group.rows.where(r => r.status === "deprecated").length;
    const experimental = group.rows.where(r => r.status === "experimental").length;
    const total = group.rows.length;
    
    return {
        "Type": group.key,
        "Total": total,
        "Active": active,
        "Deprecated": deprecated,
        "Experimental": experimental,
        "P0": group.rows.where(r => r.priority === "P0").length,
        "P1": group.rows.where(r => r.priority === "P1").length
    };
});

// Sort by total count descending
summary.sort((a, b) => b.Total - a.Total);

dv.table(
    ["Type", "Total", "Active", "Deprecated", "Experimental", "P0", "P1"],
    summary.map(s => [s.Type, s.Total, s.Active, s.Deprecated, s.Experimental, s.P0, s.P1])
);
```

---

## DataviewJS: Type Distribution Chart

```dataviewjs
// Count components by type
const components = dv.pages("")
    .where(p => p.type != null);

const typeCounts = {};
for (const page of components) {
    const type = page.type;
    typeCounts[type] = (typeCounts[type] || 0) + 1;
}

// Sort by count
const sorted = Object.entries(typeCounts)
    .sort((a, b) => b[1] - a[1]);

// Display as table with percentages
const total = components.length;
dv.table(
    ["Type", "Count", "Percentage"],
    sorted.map(([type, count]) => [
        type,
        count,
        `${((count / total) * 100).toFixed(1)}%`
    ])
);
```

---

## Performance Optimization

- **Indexed Fields:** `type`, `status`, `priority`
- **Expected Query Time:** <200ms for 1,000 files, <800ms for 5,000 files
- **Real-time Updates:** Yes, triggers on file modification
- **Caching:** Dataview maintains internal cache for metadata

---

## Usage Examples

### In a Dashboard

```markdown
# Component Type Dashboard

## Overview
![[components-by-type.md#Query All Components by Type]]

## Architecture Components
![[components-by-type.md#Architecture Documents]]

## Engine Components
![[components-by-type.md#Engine Components]]
```

### Inline Query

```markdown
We have `= dv.pages("").where(p => p.type === "architecture").length` architecture documents.
```

---

## Related Queries

- [[components-by-status]] - Filter by active/deprecated/experimental
- [[components-by-priority]] - Filter by P0/P1/P2/P3
- [[components-by-stakeholder]] - Filter by team/role
- [[components-by-category]] - Filter by functional category
- [[components-by-last-updated]] - Filter by recency/staleness
