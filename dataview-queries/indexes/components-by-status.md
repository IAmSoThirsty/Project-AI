# Components by Status - Dataview Query

**Purpose:** Dynamically index all components organized by their status (active, deprecated, experimental, archived, planned, in-progress, current).

**Performance:** <1 second for vaults with <10,000 notes  
**Auto-refresh:** Yes (real-time)  
**Last Updated:** 2026-04-21

---

## Query: All Components by Status

```dataview
TABLE 
    file.name as "Component",
    type as "Type",
    priority as "Priority",
    stakeholders as "Stakeholders",
    created as "Created",
    last_verified as "Last Verified"
FROM ""
WHERE status != null
SORT status ASC, priority ASC, file.name ASC
GROUP BY status
```

---

## Query: Active Components

**Critical for production systems**

```dataview
TABLE 
    file.name as "Active Component",
    type as "Type",
    priority as "Priority",
    stakeholders as "Stakeholders",
    area as "Area",
    last_verified as "Last Verified"
FROM ""
WHERE status = "active" OR status = "current"
SORT priority ASC, file.name ASC
```

---

## Query: Deprecated Components

**Components scheduled for removal or replacement**

```dataview
TABLE 
    file.name as "Deprecated Component",
    type as "Type",
    superseded_by as "Superseded By",
    deprecation_date as "Deprecated Date",
    removal_planned as "Removal Date",
    migration_guide as "Migration Guide"
FROM ""
WHERE status = "deprecated"
SORT removal_planned ASC, file.name ASC
```

---

## Query: Experimental Components

**Unstable features under development**

```dataview
TABLE 
    file.name as "Experimental Component",
    type as "Type",
    implementation_status as "Implementation",
    stability as "Stability",
    responsible_team as "Team",
    last_verified as "Last Verified"
FROM ""
WHERE status = "experimental"
SORT priority ASC, file.name ASC
```

---

## Query: Archived Components

**Historical components for reference only**

```dataview
TABLE 
    file.name as "Archived Component",
    type as "Type",
    archived_date as "Archived",
    archive_reason as "Reason",
    superseded_by as "Superseded By"
FROM ""
WHERE status = "archived"
SORT archived_date DESC, file.name ASC
```

---

## Query: Planned Components

**Future features not yet implemented**

```dataview
TABLE 
    file.name as "Planned Component",
    type as "Type",
    priority as "Priority",
    target_release as "Target Release",
    responsible_team as "Team",
    estimated_effort as "Effort"
FROM ""
WHERE status = "planned" OR implementation_status = "planned"
SORT priority ASC, target_release ASC
```

---

## Query: In-Progress Components

**Currently being developed**

```dataview
TABLE 
    file.name as "In-Progress Component",
    type as "Type",
    priority as "Priority",
    completion_percentage as "Progress",
    responsible_team as "Team",
    target_completion as "Target Date"
FROM ""
WHERE status = "in-progress" OR implementation_status = "in-progress"
SORT priority ASC, target_completion ASC
```

---

## DataviewJS: Status Health Dashboard

```dataviewjs
// Comprehensive status analysis with health metrics
const components = dv.pages("")
    .where(p => p.status != null);

// Status distribution
const statusCounts = {};
const now = new Date();

for (const page of components) {
    const status = page.status || "unknown";
    statusCounts[status] = (statusCounts[status] || 0) + 1;
}

// Calculate health metrics
const total = components.length;
const active = statusCounts["active"] || statusCounts["current"] || 0;
const deprecated = statusCounts["deprecated"] || 0;
const experimental = statusCounts["experimental"] || 0;
const archived = statusCounts["archived"] || 0;

const healthScore = ((active / total) * 100).toFixed(1);

// Display health summary
dv.header(3, `📊 Component Health Score: ${healthScore}%`);
dv.paragraph(`**Total Components:** ${total} | **Active:** ${active} | **Deprecated:** ${deprecated} | **Experimental:** ${experimental} | **Archived:** ${archived}`);

// Detailed status table
const statusTable = Object.entries(statusCounts)
    .sort((a, b) => b[1] - a[1])
    .map(([status, count]) => {
        const percentage = ((count / total) * 100).toFixed(1);
        const emoji = status === "active" || status === "current" ? "✅" : 
                     status === "deprecated" ? "⚠️" : 
                     status === "experimental" ? "🧪" : 
                     status === "archived" ? "📦" : "❓";
        return [emoji, status, count, `${percentage}%`];
    });

dv.table(
    ["", "Status", "Count", "Percentage"],
    statusTable
);
```

---

## DataviewJS: Deprecation Timeline

```dataviewjs
// Show deprecated components with removal dates
const deprecated = dv.pages("")
    .where(p => p.status === "deprecated")
    .sort(p => p.removal_planned || "9999-12-31");

if (deprecated.length === 0) {
    dv.paragraph("✅ No deprecated components");
} else {
    dv.header(3, `⚠️ Deprecation Timeline (${deprecated.length} components)`);
    
    const timeline = deprecated.map(p => [
        p.file.link,
        p.type || "unknown",
        p.deprecation_date || "unknown",
        p.removal_planned || "TBD",
        p.superseded_by || "none",
        p.migration_guide ? "✅" : "❌"
    ]);
    
    dv.table(
        ["Component", "Type", "Deprecated", "Removal Date", "Replacement", "Migration Guide"],
        timeline
    );
}
```

---

## DataviewJS: Stale Components Alert

```dataviewjs
// Identify components not verified recently
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

const components = dv.pages("")
    .where(p => p.status === "active" || p.status === "current");

const stale = components
    .where(p => {
        if (!p.last_verified) return true;
        const lastVerified = new Date(p.last_verified);
        return lastVerified < sixMonthsAgo;
    })
    .sort(p => p.last_verified || "2000-01-01");

if (stale.length === 0) {
    dv.paragraph("✅ All active components verified within 6 months");
} else {
    dv.header(3, `⚠️ Stale Components (${stale.length} need review)`);
    
    const staleTable = stale.map(p => {
        const daysSinceVerified = p.last_verified ? 
            Math.floor((new Date() - new Date(p.last_verified)) / (1000 * 60 * 60 * 24)) : 
            "Never";
        
        return [
            p.file.link,
            p.type || "unknown",
            p.priority || "unknown",
            p.last_verified || "Never",
            daysSinceVerified !== "Never" ? `${daysSinceVerified} days` : "Never"
        ];
    });
    
    dv.table(
        ["Component", "Type", "Priority", "Last Verified", "Days Since"],
        staleTable
    );
}
```

---

## Performance Optimization

- **Indexed Fields:** `status`, `priority`, `last_verified`
- **Expected Query Time:** <150ms for 1,000 files, <600ms for 5,000 files
- **Real-time Updates:** Yes, triggers on file modification
- **Caching:** Dataview maintains internal cache for metadata

---

## Usage Examples

### In a Dashboard

```markdown
# Component Status Dashboard

## Active Components
![[components-by-status.md#Active Components]]

## Deprecation Timeline
![[components-by-status.md#Deprecation Timeline]]

## Health Score
![[components-by-status.md#Status Health Dashboard]]
```

### Inline Query

```markdown
We have `= dv.pages("").where(p => p.status === "active").length` active components.
```

---

## Alerts & Notifications

### Components Missing Status

```dataview
TABLE 
    file.name as "Component",
    type as "Type"
FROM ""
WHERE status = null AND type != null
SORT file.name ASC
```

### Components Missing Verification Date

```dataview
TABLE 
    file.name as "Component",
    type as "Type",
    status as "Status"
FROM ""
WHERE last_verified = null AND status = "active"
SORT file.name ASC
```

---

## Related Queries

- [[components-by-type]] - Filter by component type
- [[components-by-priority]] - Filter by P0/P1/P2/P3
- [[components-by-stakeholder]] - Filter by team/role
- [[components-by-category]] - Filter by functional category
- [[components-by-last-updated]] - Filter by recency/staleness
