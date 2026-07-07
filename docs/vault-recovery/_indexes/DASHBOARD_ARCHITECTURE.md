---
title: Architecture Dashboard
id: dashboard-architecture
type: index
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
status: active
author: AGENT-038
category: architecture
tags:
  - dashboard
  - architecture
  - monitoring
  - live-data
classification: internal
---

# Architecture Dashboard

**Purpose:** Live view of architecture documentation status, component relationships, and design health

**Last Updated:** 2026-04-20

---

## 🏗️ Architecture Document Status

```dataviewjs
// Architecture documents by status
const archDocs = dv.pages()
    .where(p => 
        (p.category === "architecture" || p.type === "architecture") ||
        (p.tags && p.tags.some(t => t.includes("architecture")))
    );

const byStatus = {};
for (const doc of archDocs) {
    const status = doc.status || "unknown";
    if (!byStatus[status]) byStatus[status] = [];
    byStatus[status].push(doc);
}

const statusOrder = ["active", "review", "draft", "deprecated", "archived"];
const results = [];

for (const status of statusOrder) {
    const docs = byStatus[status] || [];
    results.push([
        status.toUpperCase(),
        docs.length,
        docs.length > 0 ? docs.map(d => d.file.link).slice(0, 5).join(", ") : "None"
    ]);
}

dv.table(
    ["Status", "Count", "Recent Documents"],
    results
);

const activeCount = (byStatus["active"] || []).length;
const totalCount = archDocs.length;
const activePercent = totalCount > 0 ? Math.round((activeCount / totalCount) * 100) : 0;

dv.header(4, `📊 ${activeCount}/${totalCount} architecture docs active (${activePercent}%)`);
```

---

## 🔗 Component Relationship Map

```dataviewjs
// Map components and their relationships
const components = [
    "authentication",
    "authorization",
    "api-gateway",
    "data-layer",
    "frontend",
    "backend",
    "monitoring",
    "deployment"
];

const componentDocs = {};
for (const comp of components) {
    componentDocs[comp] = dv.pages()
        .where(p => p.tags && p.tags.some(t => t.includes(comp)))
        .where(p => p.status === "active" || p.status === "review");
}

dv.table(
    ["Component", "Active Docs", "In Review", "Key Documents"],
    components.map(comp => {
        const docs = componentDocs[comp];
        const activeDocs = docs.where(d => d.status === "active");
        const reviewDocs = docs.where(d => d.status === "review");
        const keyDocs = activeDocs.limit(3).map(d => d.file.link).join(", ");
        
        return [
            comp,
            activeDocs.length,
            reviewDocs.length,
            keyDocs || "No active docs"
        ];
    })
);
```

---

## 📐 Design Document Coverage

```dataviewjs
// Design document coverage by component
const designDocs = dv.pages()
    .where(p => p.type === "design" || p.type === "specification")
    .where(p => p.status !== "archived" && p.status !== "deprecated");

const coverage = {
    "UI/UX Design": 0,
    "API Design": 0,
    "Data Model Design": 0,
    "Security Design": 0,
    "Integration Design": 0,
    "System Architecture": 0
};

for (const doc of designDocs) {
    const tags = doc.tags || [];
    if (tags.some(t => t.includes("ui") || t.includes("ux") || t.includes("frontend"))) {
        coverage["UI/UX Design"]++;
    }
    if (tags.some(t => t.includes("api") || t.includes("rest") || t.includes("graphql"))) {
        coverage["API Design"]++;
    }
    if (tags.some(t => t.includes("data") || t.includes("database") || t.includes("schema"))) {
        coverage["Data Model Design"]++;
    }
    if (tags.some(t => t.includes("security") || t.includes("auth"))) {
        coverage["Security Design"]++;
    }
    if (tags.some(t => t.includes("integration") || t.includes("microservice"))) {
        coverage["Integration Design"]++;
    }
    if (tags.some(t => t.includes("architecture") || t.includes("system"))) {
        coverage["System Architecture"]++;
    }
}

dv.table(
    ["Design Area", "Document Count", "Status"],
    Object.entries(coverage).map(([area, count]) => {
        const status = count >= 3 ? "✅ Good" :
                      count >= 1 ? "🟡 Partial" :
                      "⚠️ Missing";
        return [area, count, status];
    })
);
```

---

## 🔄 Recently Updated Architecture Docs

```dataviewjs
// Recent architecture changes
const recentDays = 30;
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - recentDays);

const recentArchDocs = dv.pages()
    .where(p => 
        (p.category === "architecture" || p.type === "architecture" || p.type === "design") &&
        p.updated_date &&
        new Date(p.updated_date) >= cutoffDate
    )
    .sort(p => p.updated_date, 'desc')
    .limit(15);

dv.table(
    ["Document", "Type", "Updated", "Author", "Tags"],
    recentArchDocs.map(p => [
        p.file.link,
        p.type || "Unknown",
        p.updated_date,
        p.author?.name || p.author || "Unknown",
        (p.tags || []).slice(0, 3).join(", ")
    ])
);

dv.header(4, `${recentArchDocs.length} architecture documents updated in last ${recentDays} days`);
```

---

## 🎯 Architecture Decision Records (ADRs)

```dataviewjs
// ADR tracking
const adrs = dv.pages()
    .where(p => 
        p.type === "decision_record" ||
        (p.tags && p.tags.some(t => t.includes("adr") || t.includes("decision")))
    )
    .sort(p => p.created_date, 'desc');

const adrsByStatus = {
    proposed: [],
    accepted: [],
    rejected: [],
    superseded: []
};

for (const adr of adrs) {
    const decision = adr.decision_status || adr.status || "proposed";
    const category = decision.toLowerCase();
    
    if (adrsByStatus[category]) {
        adrsByStatus[category].push(adr);
    } else {
        adrsByStatus["proposed"].push(adr);
    }
}

dv.header(3, `Architecture Decisions (${adrs.length} total)`);

for (const [status, docs] of Object.entries(adrsByStatus)) {
    if (docs.length === 0) continue;
    
    const icon = status === "accepted" ? "✅" :
                status === "proposed" ? "🔵" :
                status === "rejected" ? "❌" :
                "🔄";
    
    dv.header(4, `${icon} ${status.toUpperCase()} (${docs.length})`);
    dv.list(docs.slice(0, 10).map(d => 
        `${d.file.link} - ${d.title || d.file.name}`
    ));
}
```

---

## 📊 Architecture Health Metrics

```dataviewjs
// Calculate architecture documentation health
const allArchDocs = dv.pages()
    .where(p => 
        p.category === "architecture" || 
        p.type === "architecture" ||
        p.type === "design" ||
        (p.tags && p.tags.some(t => t.includes("architecture")))
    );

const metrics = {
    total: allArchDocs.length,
    active: 0,
    hasReview: 0,
    hasVersion: 0,
    hasLinks: 0,
    recentUpdate: 0,
    hasOwner: 0
};

const staleDays = 180;
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - staleDays);

for (const doc of allArchDocs) {
    if (doc.status === "active") metrics.active++;
    if (doc.review_status) metrics.hasReview++;
    if (doc.version) metrics.hasVersion++;
    if (doc.file.outlinks && doc.file.outlinks.length > 0) metrics.hasLinks++;
    if (doc.updated_date && new Date(doc.updated_date) >= cutoffDate) metrics.recentUpdate++;
    if (doc.author || doc.owner) metrics.hasOwner++;
}

const healthScore = Math.round((
    (metrics.active / metrics.total) * 25 +
    (metrics.hasReview / metrics.total) * 15 +
    (metrics.hasVersion / metrics.total) * 15 +
    (metrics.hasLinks / metrics.total) * 15 +
    (metrics.recentUpdate / metrics.total) * 15 +
    (metrics.hasOwner / metrics.total) * 15
));

const progressBar = "█".repeat(Math.floor(healthScore / 5)) + 
                   "░".repeat(20 - Math.floor(healthScore / 5));

dv.header(3, `Health Score: ${healthScore}%`);
dv.paragraph(`${progressBar}`);

dv.table(
    ["Metric", "Value", "Percentage"],
    [
        ["Active Status", metrics.active, `${Math.round((metrics.active/metrics.total)*100)}%`],
        ["Has Review Status", metrics.hasReview, `${Math.round((metrics.hasReview/metrics.total)*100)}%`],
        ["Has Version", metrics.hasVersion, `${Math.round((metrics.hasVersion/metrics.total)*100)}%`],
        ["Has Links", metrics.hasLinks, `${Math.round((metrics.hasLinks/metrics.total)*100)}%`],
        ["Updated (6mo)", metrics.recentUpdate, `${Math.round((metrics.recentUpdate/metrics.total)*100)}%`],
        ["Has Owner", metrics.hasOwner, `${Math.round((metrics.hasOwner/metrics.total)*100)}%`]
    ]
);
```

---

## 🔍 Missing Architecture Documentation

```dataviewjs
// Identify documentation gaps
const requiredComponents = [
    "authentication",
    "authorization",
    "data-persistence",
    "api-design",
    "frontend-architecture",
    "backend-architecture",
    "deployment-architecture",
    "monitoring-architecture",
    "security-architecture",
    "integration-patterns"
];

const gaps = [];

for (const component of requiredComponents) {
    const docs = dv.pages()
        .where(p => 
            (p.tags && p.tags.some(t => t.includes(component))) &&
            (p.type === "architecture" || p.type === "design") &&
            (p.status === "active" || p.status === "review")
        );
    
    if (docs.length === 0) {
        gaps.push([component, "⚠️ Missing", "Create architecture document"]);
    } else if (docs.length === 1) {
        gaps.push([component, "🟡 Minimal", `Only ${docs.length} doc found`]);
    }
}

if (gaps.length > 0) {
    dv.header(3, `⚠️ Documentation Gaps (${gaps.length})`);
    dv.table(
        ["Component", "Status", "Action Needed"],
        gaps
    );
} else {
    dv.header(3, `✅ All required components documented`);
}
```

---

## Quick Actions

- [[Create New Architecture Document]]
- [[Create New Design Document]]
- [[Create New ADR]]
- [[Review Pending Architecture Changes]]
- [[Archive Deprecated Architecture Docs]]

---

**Dashboard Statistics:**
- Total Architecture Documents: *Dynamic count from queries above*
- Active Documents: *Dynamic count from queries above*
- Health Score: *Dynamic score from queries above*
- Last Dashboard Update: 2026-04-20

**Navigation:**
- [[00_INDEX|← Main Index]]
- [[DASHBOARD_SECURITY|Security Dashboard →]]
- [[01_ARCHITECTURE|Architecture Index]]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

