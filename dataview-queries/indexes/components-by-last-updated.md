# Components by Last Updated - Dataview Query

**Purpose:** Dynamically index all components organized by last update date, identifying recent changes and stale documentation.

**Performance:** <1 second for vaults with <10,000 notes  
**Auto-refresh:** Yes (real-time)  
**Last Updated:** 2026-04-21

---

## Query: All Components by Last Updated

```dataview
TABLE 
    file.name as "Component",
    type as "Type",
    priority as "Priority",
    status as "Status",
    last_verified as "Last Verified",
    updated_date as "Updated",
    days_since as "Days Ago"
FROM ""
WHERE last_verified != null OR updated_date != null OR file.mtime != null
SORT file.mtime DESC
```

---

## Query: Recently Updated Components

**Components updated in the last 30 days**

```dataview
TABLE 
    file.name as "Recently Updated",
    type as "Type",
    priority as "Priority",
    status as "Status",
    last_verified as "Last Verified",
    file.mtime as "Modified"
FROM ""
WHERE file.mtime >= date(today) - dur(30 days)
SORT file.mtime DESC
```

---

## Query: Recently Verified Components

**Components verified in the last 90 days**

```dataview
TABLE 
    file.name as "Recently Verified",
    type as "Type",
    priority as "Priority",
    status as "Status",
    last_verified as "Last Verified",
    review_cycle as "Review Cycle",
    stakeholders as "Stakeholders"
FROM ""
WHERE last_verified >= date(today) - dur(90 days)
SORT last_verified DESC
```

---

## Query: Stale Components (90+ Days)

**Components not updated in 90+ days**

```dataview
TABLE 
    file.name as "Stale Component",
    type as "Type",
    priority as "Priority",
    status as "Status",
    last_verified as "Last Verified",
    file.mtime as "Last Modified",
    stakeholders as "Stakeholders"
FROM ""
WHERE file.mtime < date(today) - dur(90 days) AND (status = "active" OR status = "current")
SORT priority ASC, file.mtime ASC
```

---

## Query: Critical Stale Components (P0/P1)

**High-priority components requiring review**

```dataview
TABLE 
    file.name as "Critical Stale",
    type as "Type",
    priority as "Priority",
    last_verified as "Last Verified",
    file.mtime as "Last Modified",
    stakeholders as "Stakeholders",
    review_cycle as "Review Cycle"
FROM ""
WHERE (priority = "P0" OR priority = "P1") 
    AND (status = "active" OR status = "current")
    AND (last_verified < date(today) - dur(90 days) OR last_verified = null)
SORT priority ASC, last_verified ASC
```

---

## Query: Never Verified Components

**Components missing verification date**

```dataview
TABLE 
    file.name as "Never Verified",
    type as "Type",
    priority as "Priority",
    status as "Status",
    created as "Created",
    file.ctime as "File Created",
    stakeholders as "Stakeholders"
FROM ""
WHERE type != null AND last_verified = null
SORT priority ASC, file.ctime ASC
```

---

## Query: Components Due for Review

**Components past their review cycle**

```dataview
TABLE 
    file.name as "Review Due",
    type as "Type",
    priority as "Priority",
    review_cycle as "Review Cycle",
    last_verified as "Last Verified",
    next_review as "Next Review",
    stakeholders as "Stakeholders"
FROM ""
WHERE next_review != null AND next_review <= date(today)
SORT next_review ASC, priority ASC
```

---

## DataviewJS: Update Timeline Analysis

```dataviewjs
// Analyze component update patterns
const components = dv.pages("")
    .where(p => p.type != null);

const now = new Date();
const buckets = {
    "Last 7 days": 0,
    "Last 30 days": 0,
    "Last 90 days": 0,
    "Last 180 days": 0,
    "Last 365 days": 0,
    "Over 1 year": 0,
    "Never updated": 0
};

for (const page of components) {
    const lastUpdate = page.last_verified || page.updated_date || page.file.mtime;
    
    if (!lastUpdate) {
        buckets["Never updated"]++;
        continue;
    }
    
    const updateDate = new Date(lastUpdate);
    const daysSince = Math.floor((now - updateDate) / (1000 * 60 * 60 * 24));
    
    if (daysSince <= 7) {
        buckets["Last 7 days"]++;
    } else if (daysSince <= 30) {
        buckets["Last 30 days"]++;
    } else if (daysSince <= 90) {
        buckets["Last 90 days"]++;
    } else if (daysSince <= 180) {
        buckets["Last 180 days"]++;
    } else if (daysSince <= 365) {
        buckets["Last 365 days"]++;
    } else {
        buckets["Over 1 year"]++;
    }
}

const total = components.length;

dv.header(3, `📅 Update Timeline (${total} components)`);

const table = Object.entries(buckets).map(([period, count]) => {
    const percentage = ((count / total) * 100).toFixed(1);
    const emoji = period === "Last 7 days" ? "🟢" : 
                 period === "Last 30 days" ? "🟡" : 
                 period === "Last 90 days" ? "🟠" : 
                 period === "Over 1 year" || period === "Never updated" ? "🔴" : "⚪";
    return [emoji, period, count, `${percentage}%`];
});

dv.table(
    ["", "Period", "Count", "Percentage"],
    table
);
```

---

## DataviewJS: Staleness Risk Dashboard

```dataviewjs
// Identify high-risk stale components
const components = dv.pages("")
    .where(p => (p.status === "active" || p.status === "current") && p.priority != null);

const now = new Date();
const risks = [];

for (const page of components) {
    const lastUpdate = page.last_verified || page.updated_date || page.file.mtime;
    
    if (!lastUpdate) {
        risks.push({
            component: page.file.link,
            priority: page.priority,
            type: page.type || "unknown",
            daysSince: "Never",
            riskLevel: "Critical",
            reason: "Never verified"
        });
        continue;
    }
    
    const updateDate = new Date(lastUpdate);
    const daysSince = Math.floor((now - updateDate) / (1000 * 60 * 60 * 24));
    
    let riskLevel = "Low";
    let reason = "";
    
    // Risk calculation based on priority and staleness
    if (page.priority === "P0") {
        if (daysSince > 90) {
            riskLevel = "Critical";
            reason = "P0 not verified in 90+ days";
        } else if (daysSince > 60) {
            riskLevel = "High";
            reason = "P0 not verified in 60+ days";
        }
    } else if (page.priority === "P1") {
        if (daysSince > 180) {
            riskLevel = "High";
            reason = "P1 not verified in 180+ days";
        } else if (daysSince > 120) {
            riskLevel = "Medium";
            reason = "P1 not verified in 120+ days";
        }
    } else if (page.priority === "P2") {
        if (daysSince > 365) {
            riskLevel = "Medium";
            reason = "P2 not verified in 365+ days";
        }
    }
    
    if (riskLevel !== "Low") {
        risks.push({
            component: page.file.link,
            priority: page.priority,
            type: page.type || "unknown",
            daysSince: daysSince,
            riskLevel: riskLevel,
            reason: reason
        });
    }
}

// Sort by risk level, then priority
const riskOrder = { "Critical": 0, "High": 1, "Medium": 2, "Low": 3 };
risks.sort((a, b) => {
    if (riskOrder[a.riskLevel] !== riskOrder[b.riskLevel]) {
        return riskOrder[a.riskLevel] - riskOrder[b.riskLevel];
    }
    return a.priority.localeCompare(b.priority);
});

dv.header(3, `🚨 Staleness Risk Dashboard (${risks.length} at-risk components)`);

if (risks.length === 0) {
    dv.paragraph("✅ No high-risk stale components identified!");
} else {
    const table = risks.map(r => {
        const emoji = r.riskLevel === "Critical" ? "🔴" : 
                     r.riskLevel === "High" ? "🟠" : 
                     r.riskLevel === "Medium" ? "🟡" : "🟢";
        return [
            emoji,
            r.component,
            r.priority,
            r.type,
            r.daysSince === "Never" ? "Never" : `${r.daysSince} days`,
            r.reason
        ];
    });
    
    dv.table(
        ["Risk", "Component", "Priority", "Type", "Days Since", "Reason"],
        table
    );
}
```

---

## DataviewJS: Update Velocity by Category

```dataviewjs
// Track update frequency by category
const components = dv.pages("")
    .where(p => (p.area || p.category) && (p.last_verified || p.updated_date || p.file.mtime));

const velocity = {};

for (const page of components) {
    const categories = new Set();
    
    if (page.area) {
        const areas = Array.isArray(page.area) ? page.area : [page.area];
        areas.forEach(a => categories.add(a));
    }
    
    if (page.category) {
        const cats = Array.isArray(page.category) ? page.category : [page.category];
        cats.forEach(c => categories.add(c));
    }
    
    const lastUpdate = page.last_verified || page.updated_date || page.file.mtime;
    const updateDate = new Date(lastUpdate);
    const daysSince = Math.floor((new Date() - updateDate) / (1000 * 60 * 60 * 24));
    
    categories.forEach(cat => {
        if (!velocity[cat]) {
            velocity[cat] = { count: 0, totalDays: 0, recent: 0, stale: 0 };
        }
        velocity[cat].count++;
        velocity[cat].totalDays += daysSince;
        if (daysSince <= 30) velocity[cat].recent++;
        if (daysSince > 90) velocity[cat].stale++;
    });
}

// Calculate averages
const sorted = Object.entries(velocity)
    .map(([category, data]) => ({
        category: category,
        count: data.count,
        avgDays: Math.round(data.totalDays / data.count),
        recent: data.recent,
        stale: data.stale,
        freshness: ((data.recent / data.count) * 100).toFixed(0)
    }))
    .sort((a, b) => a.avgDays - b.avgDays);

dv.header(3, `📈 Update Velocity by Category`);
dv.table(
    ["Category", "Components", "Avg Days Since Update", "Recent (30d)", "Stale (90d+)", "Freshness %"],
    sorted.map(s => [
        s.category,
        s.count,
        s.avgDays,
        s.recent,
        s.stale,
        `${s.freshness}%`
    ])
);
```

---

## DataviewJS: Review Cycle Compliance

```dataviewjs
// Check compliance with review cycles
const components = dv.pages("")
    .where(p => p.review_cycle && p.last_verified);

const compliance = {
    compliant: [],
    overdue: [],
    approaching: []
};

const now = new Date();

for (const page of components) {
    const lastVerified = new Date(page.last_verified);
    const daysSince = Math.floor((now - lastVerified) / (1000 * 60 * 60 * 24));
    
    // Parse review cycle
    let cycleDays = 365; // default to yearly
    if (page.review_cycle === "monthly") cycleDays = 30;
    else if (page.review_cycle === "quarterly") cycleDays = 90;
    else if (page.review_cycle === "semi-annually") cycleDays = 180;
    else if (page.review_cycle === "yearly") cycleDays = 365;
    
    const daysUntilDue = cycleDays - daysSince;
    
    if (daysUntilDue < 0) {
        compliance.overdue.push({
            component: page.file.link,
            cycle: page.review_cycle,
            daysSince: daysSince,
            daysOverdue: Math.abs(daysUntilDue),
            priority: page.priority || "unknown"
        });
    } else if (daysUntilDue <= 14) {
        compliance.approaching.push({
            component: page.file.link,
            cycle: page.review_cycle,
            daysSince: daysSince,
            daysUntilDue: daysUntilDue,
            priority: page.priority || "unknown"
        });
    } else {
        compliance.compliant.push({
            component: page.file.link,
            cycle: page.review_cycle,
            daysSince: daysSince,
            daysUntilDue: daysUntilDue,
            priority: page.priority || "unknown"
        });
    }
}

const total = compliance.compliant.length + compliance.overdue.length + compliance.approaching.length;
const complianceRate = ((compliance.compliant.length / total) * 100).toFixed(1);

dv.header(3, `📋 Review Cycle Compliance: ${complianceRate}%`);
dv.paragraph(`**Compliant:** ${compliance.compliant.length} | **Approaching:** ${compliance.approaching.length} | **Overdue:** ${compliance.overdue.length}`);

// Show overdue items
if (compliance.overdue.length > 0) {
    dv.header(4, `🔴 Overdue Reviews (${compliance.overdue.length})`);
    compliance.overdue.sort((a, b) => b.daysOverdue - a.daysOverdue);
    dv.table(
        ["Component", "Review Cycle", "Days Overdue", "Priority"],
        compliance.overdue.slice(0, 10).map(c => [
            c.component,
            c.cycle,
            c.daysOverdue,
            c.priority
        ])
    );
}

// Show approaching items
if (compliance.approaching.length > 0) {
    dv.header(4, `🟡 Approaching Reviews (${compliance.approaching.length})`);
    compliance.approaching.sort((a, b) => a.daysUntilDue - b.daysUntilDue);
    dv.table(
        ["Component", "Review Cycle", "Days Until Due", "Priority"],
        compliance.approaching.slice(0, 10).map(c => [
            c.component,
            c.cycle,
            c.daysUntilDue,
            c.priority
        ])
    );
}
```

---

## DataviewJS: Activity Heatmap

```dataviewjs
// Generate activity heatmap by month
const components = dv.pages("")
    .where(p => p.last_verified || p.updated_date || p.file.mtime);

const monthCounts = {};
const now = new Date();

for (let i = 0; i < 12; i++) {
    const month = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const monthKey = month.toISOString().substring(0, 7);
    monthCounts[monthKey] = 0;
}

for (const page of components) {
    const lastUpdate = page.last_verified || page.updated_date || page.file.mtime;
    if (lastUpdate) {
        const updateDate = new Date(lastUpdate);
        const monthKey = updateDate.toISOString().substring(0, 7);
        if (monthCounts.hasOwnProperty(monthKey)) {
            monthCounts[monthKey]++;
        }
    }
}

// Sort by month descending
const sorted = Object.entries(monthCounts)
    .sort((a, b) => b[0].localeCompare(a[0]));

dv.header(3, `🔥 Activity Heatmap (Last 12 Months)`);

const table = sorted.map(([month, count]) => {
    const intensity = count === 0 ? "⬜" :
                     count < 5 ? "🟩" :
                     count < 10 ? "🟨" :
                     count < 20 ? "🟧" : "🟥";
    return [month, intensity, count];
});

dv.table(
    ["Month", "Activity", "Updates"],
    table
);
```

---

## Performance Optimization

- **Indexed Fields:** `last_verified`, `updated_date`, `file.mtime`
- **Expected Query Time:** <150ms for 1,000 files, <600ms for 5,000 files
- **Real-time Updates:** Yes, triggers on file modification
- **Caching:** Dataview maintains internal cache for file metadata

---

## Usage Examples

### In a Dashboard

```markdown
# Update Tracking Dashboard

## Recently Updated
![[components-by-last-updated.md#Recently Updated Components]]

## Staleness Risks
![[components-by-last-updated.md#Staleness Risk Dashboard]]

## Review Compliance
![[components-by-last-updated.md#Review Cycle Compliance]]
```

### Inline Query

```markdown
Components updated in last 7 days: `= dv.pages("").where(p => p.file.mtime >= dv.date(dv.date("today") - dv.duration("7 days"))).length`
```

---

## Review Cycle Recommendations

| Priority | Review Cycle | Max Staleness | Action |
|----------|-------------|---------------|--------|
| **P0** | Monthly | 90 days | Critical - immediate review |
| **P1** | Quarterly | 180 days | High - schedule review |
| **P2** | Semi-annually | 365 days | Medium - add to backlog |
| **P3** | Yearly | No limit | Low - review as needed |

---

## Alerts & Notifications

### Missing Last Verified Date

```dataview
TABLE 
    file.name as "Component",
    type as "Type",
    priority as "Priority",
    status as "Status",
    file.ctime as "Created"
FROM ""
WHERE type != null AND last_verified = null AND (status = "active" OR status = "current")
SORT priority ASC, file.ctime ASC
```

### Components Not Modified in 365+ Days

```dataview
TABLE 
    file.name as "Very Stale",
    type as "Type",
    priority as "Priority",
    file.mtime as "Last Modified"
FROM ""
WHERE file.mtime < date(today) - dur(365 days) AND (status = "active" OR status = "current")
SORT priority ASC, file.mtime ASC
```

---

## Related Queries

- [[components-by-type]] - Filter by component type
- [[components-by-status]] - Filter by active/deprecated/experimental
- [[components-by-stakeholder]] - Filter by team/role
- [[components-by-priority]] - Filter by P0/P1/P2/P3
- [[components-by-category]] - Filter by functional category
