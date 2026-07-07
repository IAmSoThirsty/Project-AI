---
title: Development Dashboard
id: dashboard-development
type: index
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
status: active
author: AGENT-038
category: development
tags:
  - dashboard
  - development
  - engineering
  - code-quality
classification: internal
---

# Development Dashboard

**Purpose:** Track development documentation, code quality, testing status, and technical debt

**Last Updated:** 2026-04-20

---

## 💻 Development Documentation Status

```dataviewjs
// Development docs by type and status
const devDocs = dv.pages()
    .where(p => 
        p.category === "development" ||
        (p.tags && (
            p.tags.includes("development") ||
            p.tags.includes("programming") ||
            p.tags.includes("coding") ||
            p.tags.includes("api")
        ))
    );

const docTypes = {
    "API Documentation": 0,
    "Developer Guide": 0,
    "Code Standard": 0,
    "Library/Framework Doc": 0,
    "Tutorial": 0,
    "Troubleshooting Guide": 0
};

for (const doc of devDocs) {
    const type = doc.type || "unknown";
    const tags = doc.tags || [];
    
    if (type === "api_reference" || tags.includes("api")) docTypes["API Documentation"]++;
    if (type === "guide" && tags.includes("development")) docTypes["Developer Guide"]++;
    if (type === "standard" || tags.includes("coding-standard")) docTypes["Code Standard"]++;
    if (tags.includes("library") || tags.includes("framework")) docTypes["Library/Framework Doc"]++;
    if (type === "tutorial" && tags.includes("development")) docTypes["Tutorial"]++;
    if (tags.includes("troubleshooting") || tags.includes("debugging")) docTypes["Troubleshooting Guide"]++;
}

dv.table(
    ["Document Type", "Count", "Status"],
    Object.entries(docTypes).map(([type, count]) => {
        const status = count >= 3 ? "✅ Good" :
                      count >= 1 ? "🟡 Minimal" :
                      "⚠️ Missing";
        return [type, count, status];
    })
);

dv.header(4, `${devDocs.length} development documents total`);
```

---

## 🧪 Test Coverage Overview

```dataviewjs
// Test coverage by component
const testDocs = dv.pages()
    .where(p => 
        p.test_coverage !== undefined ||
        p.tests !== undefined ||
        (p.tags && p.tags.includes("testing"))
    );

const componentCoverage = {};

for (const doc of testDocs) {
    const tags = doc.tags || [];
    const component = tags.find(t => 
        ["authentication", "authorization", "api", "frontend", "backend", "database", "ui", "data-layer"].includes(t)
    ) || "other";
    
    if (!componentCoverage[component]) {
        componentCoverage[component] = {
            docs: [],
            totalCoverage: 0,
            count: 0
        };
    }
    
    let coverage = 0;
    if (typeof doc.test_coverage === 'number') {
        coverage = doc.test_coverage;
    } else if (doc.test_coverage?.percentage) {
        coverage = doc.test_coverage.percentage;
    } else if (doc.tests && Array.isArray(doc.tests)) {
        const passedTests = doc.tests.filter(t => 
            (t.status || "").toLowerCase() === "passed" || 
            (t.status || "").toLowerCase() === "pass"
        ).length;
        coverage = doc.tests.length > 0 ? Math.round((passedTests / doc.tests.length) * 100) : 0;
    }
    
    componentCoverage[component].docs.push({ doc, coverage });
    componentCoverage[component].totalCoverage += coverage;
    componentCoverage[component].count += 1;
}

const coverageResults = Object.entries(componentCoverage).map(([component, data]) => {
    const avgCoverage = data.count > 0 ? Math.round(data.totalCoverage / data.count) : 0;
    const status = avgCoverage >= 80 ? "✅ Good" :
                  avgCoverage >= 60 ? "🟡 Fair" :
                  avgCoverage >= 40 ? "🟠 Low" :
                  "🔴 Critical";
    
    return [component, data.count, `${avgCoverage}%`, status];
}).sort((a, b) => parseInt(a[2]) - parseInt(b[2])); // Sort by coverage (lowest first)

dv.header(3, "Test Coverage by Component");
dv.table(
    ["Component", "Docs Tested", "Avg Coverage", "Status"],
    coverageResults
);

const lowCoverageComponents = coverageResults.filter(r => parseInt(r[2]) < 60);
if (lowCoverageComponents.length > 0) {
    dv.header(4, `⚠️ ${lowCoverageComponents.length} components with <60% test coverage`);
}
```

---

## 🚀 Feature Development Status

```dataviewjs
// Track feature specifications and implementation
const featureDocs = dv.pages()
    .where(p => 
        p.type === "specification" || 
        p.type === "design" ||
        (p.tags && p.tags.includes("feature"))
    );

const featureStatus = {
    "Not Started": [],
    "In Progress": [],
    "In Review": [],
    "Completed": [],
    "On Hold": []
};

for (const feature of featureDocs) {
    const implStatus = (feature.implementation_status || 
                       feature.development_status || 
                       feature.status || 
                       "not started").toLowerCase();
    
    if (implStatus.includes("completed") || implStatus === "active") {
        featureStatus["Completed"].push(feature);
    } else if (implStatus.includes("progress") || implStatus === "draft") {
        featureStatus["In Progress"].push(feature);
    } else if (implStatus.includes("review")) {
        featureStatus["In Review"].push(feature);
    } else if (implStatus.includes("hold") || implStatus.includes("blocked")) {
        featureStatus["On Hold"].push(feature);
    } else {
        featureStatus["Not Started"].push(feature);
    }
}

dv.header(3, `Feature Development Pipeline (${featureDocs.length} features)`);

for (const [status, features] of Object.entries(featureStatus)) {
    if (features.length === 0) continue;
    
    const icon = status === "Completed" ? "✅" :
                status === "In Review" ? "👁️" :
                status === "In Progress" ? "🔨" :
                status === "On Hold" ? "⏸️" :
                "📋";
    
    dv.header(4, `${icon} ${status} (${features.length})`);
    dv.table(
        ["Feature", "Type", "Owner", "Updated"],
        features.slice(0, 10).map(f => [
            f.file.link,
            f.type || "Unknown",
            f.owner || f.author?.name || f.author || "Unassigned",
            f.updated_date || "No date"
        ])
    );
}

const completionRate = featureDocs.length > 0 ?
    Math.round((featureStatus["Completed"].length / featureDocs.length) * 100) : 0;
dv.header(4, `Overall completion: ${completionRate}% (${featureStatus["Completed"].length}/${featureDocs.length})`);
```

---

## 📚 API Documentation Coverage

```dataviewjs
// Track API endpoint documentation
const apiDocs = dv.pages()
    .where(p => 
        p.type === "api_reference" ||
        (p.tags && (p.tags.includes("api") || p.tags.includes("rest") || p.tags.includes("graphql")))
    );

const apiCategories = {
    "Authentication APIs": 0,
    "User Management APIs": 0,
    "Data APIs": 0,
    "Integration APIs": 0,
    "Admin APIs": 0,
    "Public APIs": 0
};

for (const doc of apiDocs) {
    const tags = doc.tags || [];
    const title = (doc.title || doc.file.name).toLowerCase();
    
    if (tags.includes("authentication") || title.includes("auth")) apiCategories["Authentication APIs"]++;
    if (tags.includes("user") || title.includes("user")) apiCategories["User Management APIs"]++;
    if (tags.includes("data") || title.includes("data")) apiCategories["Data APIs"]++;
    if (tags.includes("integration") || title.includes("integration")) apiCategories["Integration APIs"]++;
    if (tags.includes("admin") || title.includes("admin")) apiCategories["Admin APIs"]++;
    if (tags.includes("public") || title.includes("public")) apiCategories["Public APIs"]++;
}

dv.header(3, `API Documentation (${apiDocs.length} documents)`);
dv.table(
    ["API Category", "Documented Endpoints", "Status"],
    Object.entries(apiCategories).map(([category, count]) => {
        const status = count >= 2 ? "✅ Good" :
                      count === 1 ? "🟡 Minimal" :
                      "⚠️ Missing";
        return [category, count, status];
    })
);
```

---

## 🐛 Technical Debt Tracking

```dataviewjs
// Track technical debt items
const debtDocs = dv.pages()
    .where(p => 
        (p.tags && (
            p.tags.includes("technical-debt") ||
            p.tags.includes("refactor") ||
            p.tags.includes("debt") ||
            p.tags.includes("todo")
        )) ||
        (p.type === "assessment" && p.category === "technical-debt")
    );

const debtBySeverity = {
    critical: [],
    high: [],
    medium: [],
    low: []
};

for (const doc of debtDocs) {
    const severity = (doc.severity || doc.priority || "medium").toLowerCase();
    
    if (debtBySeverity[severity]) {
        debtBySeverity[severity].push(doc);
    } else {
        debtBySeverity["medium"].push(doc);
    }
}

dv.header(3, `Technical Debt (${debtDocs.length} items)`);

const severityOrder = ["critical", "high", "medium", "low"];
for (const severity of severityOrder) {
    const items = debtBySeverity[severity];
    if (items.length === 0) continue;
    
    const icon = severity === "critical" ? "🔴" :
                severity === "high" ? "🟠" :
                severity === "medium" ? "🟡" :
                "🔵";
    
    dv.header(4, `${icon} ${severity.toUpperCase()} (${items.length})`);
    dv.table(
        ["Item", "Area", "Status", "Owner"],
        items.slice(0, 8).map(item => [
            item.file.link,
            (item.tags || []).find(t => 
                ["frontend", "backend", "database", "infrastructure"].includes(t)
            ) || "Unknown",
            item.status || "Open",
            item.owner || item.author?.name || item.author || "Unassigned"
        ])
    );
}

const criticalDebt = debtBySeverity.critical.length;
if (criticalDebt > 0) {
    dv.header(4, `⚠️ ${criticalDebt} critical technical debt items require immediate attention`);
}
```

---

## 🔧 Code Quality Metrics

```dataviewjs
// Code quality and linting status
const qualityDocs = dv.pages()
    .where(p => 
        p.code_quality !== undefined ||
        p.linting_status !== undefined ||
        (p.tags && (p.tags.includes("code-quality") || p.tags.includes("linting")))
    );

const qualityMetrics = {
    totalDocs: qualityDocs.length,
    passingLint: 0,
    highQuality: 0,
    needsWork: 0,
    hasMetrics: 0
};

for (const doc of qualityDocs) {
    if (doc.linting_status === "passed" || doc.linting_status === "clean") {
        qualityMetrics.passingLint++;
    }
    
    if (doc.code_quality) {
        qualityMetrics.hasMetrics++;
        const quality = typeof doc.code_quality === 'string' ? 
            doc.code_quality.toLowerCase() : 
            (doc.code_quality.rating || "").toLowerCase();
        
        if (quality.includes("excellent") || quality.includes("good") || quality === "a") {
            qualityMetrics.highQuality++;
        } else if (quality.includes("poor") || quality.includes("needs") || quality === "d" || quality === "f") {
            qualityMetrics.needsWork++;
        }
    }
}

dv.header(3, "Code Quality Metrics");
dv.table(
    ["Metric", "Value", "Percentage"],
    [
        ["Documents Tracked", qualityMetrics.totalDocs, "100%"],
        ["Passing Linters", qualityMetrics.passingLint, `${Math.round((qualityMetrics.passingLint/qualityMetrics.totalDocs)*100)}%`],
        ["High Quality", qualityMetrics.highQuality, `${Math.round((qualityMetrics.highQuality/qualityMetrics.totalDocs)*100)}%`],
        ["Needs Work", qualityMetrics.needsWork, `${Math.round((qualityMetrics.needsWork/qualityMetrics.totalDocs)*100)}%`],
        ["Has Quality Metrics", qualityMetrics.hasMetrics, `${Math.round((qualityMetrics.hasMetrics/qualityMetrics.totalDocs)*100)}%`]
    ]
);

if (qualityMetrics.needsWork > 0) {
    dv.header(4, `⚠️ ${qualityMetrics.needsWork} code areas need quality improvements`);
}
```

---

## 📦 Dependency Management

```dataviewjs
// Track external dependencies and versions
const docsWithDeps = dv.pages()
    .where(p => 
        p.dependencies !== undefined ||
        p.external_dependencies !== undefined
    );

const depCategories = {
    "Python Packages": new Set(),
    "JavaScript Packages": new Set(),
    "System Libraries": new Set(),
    "External APIs": new Set()
};

const outdatedDeps = [];
const securityIssues = [];

for (const doc of docsWithDeps) {
    const deps = doc.dependencies || doc.external_dependencies || [];
    
    for (const dep of deps) {
        const depName = typeof dep === 'string' ? dep : dep.name;
        const depType = typeof dep === 'object' ? dep.type : "unknown";
        
        if (depType === "python" || depName.includes("pip") || depName.includes(".py")) {
            depCategories["Python Packages"].add(depName);
        } else if (depType === "javascript" || depName.includes("npm") || depName.includes("node")) {
            depCategories["JavaScript Packages"].add(depName);
        } else if (depType === "system" || depType === "library") {
            depCategories["System Libraries"].add(depName);
        } else if (depType === "api" || depType === "external") {
            depCategories["External APIs"].add(depName);
        }
        
        // Check for outdated/security flags
        if (typeof dep === 'object') {
            if (dep.outdated === true || dep.status === "outdated") {
                outdatedDeps.push({ name: depName, source: doc.file.link });
            }
            if (dep.security_issue === true || dep.vulnerability === true) {
                securityIssues.push({ name: depName, source: doc.file.link });
            }
        }
    }
}

dv.header(3, "Dependency Overview");
dv.table(
    ["Category", "Unique Dependencies"],
    Object.entries(depCategories).map(([category, deps]) => [
        category,
        deps.size
    ])
);

if (outdatedDeps.length > 0) {
    dv.header(4, `⚠️ ${outdatedDeps.length} outdated dependencies detected`);
    dv.list(outdatedDeps.slice(0, 5).map(d => `${d.name} (${d.source})`));
}

if (securityIssues.length > 0) {
    dv.header(4, `🔴 ${securityIssues.length} dependencies with security issues`);
    dv.list(securityIssues.slice(0, 5).map(d => `${d.name} (${d.source})`));
}
```

---

## 🎯 Development Sprint View

```dataviewjs
// Current sprint/iteration status
const sprintDocs = dv.pages()
    .where(p => 
        p.sprint !== undefined ||
        p.iteration !== undefined ||
        (p.tags && p.tags.includes("sprint"))
    );

const currentSprint = sprintDocs
    .where(p => {
        const sprint = p.sprint || p.iteration;
        return sprint && (sprint.status === "active" || sprint.status === "current");
    });

const sprintTasks = currentSprint.flatMap(doc => {
    if (doc.tasks && Array.isArray(doc.tasks)) {
        return doc.tasks.map(task => ({
            task: task,
            doc: doc
        }));
    }
    return [];
});

const tasksByStatus = {
    todo: [],
    inProgress: [],
    review: [],
    done: []
};

for (const item of sprintTasks) {
    const status = (item.task.status || "todo").toLowerCase().replace(/[_\s-]/g, '');
    
    if (status.includes("done") || status.includes("complete")) {
        tasksByStatus.done.push(item);
    } else if (status.includes("progress") || status.includes("doing")) {
        tasksByStatus.inProgress.push(item);
    } else if (status.includes("review")) {
        tasksByStatus.review.push(item);
    } else {
        tasksByStatus.todo.push(item);
    }
}

const totalTasks = sprintTasks.length;
const completedTasks = tasksByStatus.done.length;
const sprintProgress = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

dv.header(3, `Current Sprint Progress: ${sprintProgress}%`);
const progressBar = "█".repeat(Math.floor(sprintProgress / 5)) + 
                   "░".repeat(20 - Math.floor(sprintProgress / 5));
dv.paragraph(`${progressBar} ${completedTasks}/${totalTasks} tasks`);

dv.table(
    ["Status", "Count", "Percentage"],
    [
        ["✅ Done", tasksByStatus.done.length, `${Math.round((tasksByStatus.done.length/totalTasks)*100)}%`],
        ["👁️ Review", tasksByStatus.review.length, `${Math.round((tasksByStatus.review.length/totalTasks)*100)}%`],
        ["🔨 In Progress", tasksByStatus.inProgress.length, `${Math.round((tasksByStatus.inProgress.length/totalTasks)*100)}%`],
        ["📋 To Do", tasksByStatus.todo.length, `${Math.round((tasksByStatus.todo.length/totalTasks)*100)}%`]
    ]
);
```

---

## 📊 Development Health Score

```dataviewjs
// Calculate overall development health
const allDevDocs = dv.pages()
    .where(p => 
        p.category === "development" ||
        p.type === "api_reference" ||
        p.type === "specification" ||
        (p.tags && (
            p.tags.includes("development") ||
            p.tags.includes("api") ||
            p.tags.includes("testing")
        ))
    );

const metrics = {
    total: allDevDocs.length,
    active: 0,
    hasTesting: 0,
    highCoverage: 0,
    hasAPI: 0,
    recentUpdate: 0,
    hasOwner: 0
};

const staleDays = 90;
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - staleDays);

for (const doc of allDevDocs) {
    if (doc.status === "active") metrics.active++;
    
    if (doc.test_coverage !== undefined || doc.tests !== undefined) {
        metrics.hasTesting++;
        
        const coverage = typeof doc.test_coverage === 'number' ? doc.test_coverage : 0;
        if (coverage >= 80) metrics.highCoverage++;
    }
    
    if (doc.type === "api_reference" || (doc.tags && doc.tags.includes("api"))) {
        metrics.hasAPI++;
    }
    
    if (doc.updated_date && new Date(doc.updated_date) >= cutoffDate) {
        metrics.recentUpdate++;
    }
    
    if (doc.author || doc.owner) metrics.hasOwner++;
}

const healthScore = Math.round((
    (metrics.active / metrics.total) * 20 +
    (metrics.hasTesting / metrics.total) * 25 +
    (metrics.highCoverage / (metrics.hasTesting || 1)) * 20 +
    (metrics.hasAPI / Math.max(metrics.total * 0.2, 1)) * 15 +
    (metrics.recentUpdate / metrics.total) * 10 +
    (metrics.hasOwner / metrics.total) * 10
));

const progressBar = "█".repeat(Math.floor(healthScore / 5)) + 
                   "░".repeat(20 - Math.floor(healthScore / 5));

dv.header(3, `Development Health Score: ${healthScore}%`);
dv.paragraph(`${progressBar}`);

dv.table(
    ["Metric", "Value", "Percentage", "Status"],
    [
        ["Active Status", metrics.active, `${Math.round((metrics.active/metrics.total)*100)}%`, metrics.active >= metrics.total * 0.7 ? "✅" : "⚠️"],
        ["Has Testing", metrics.hasTesting, `${Math.round((metrics.hasTesting/metrics.total)*100)}%`, metrics.hasTesting >= metrics.total * 0.5 ? "✅" : "⚠️"],
        ["High Coverage (≥80%)", metrics.highCoverage, `${Math.round((metrics.highCoverage/(metrics.hasTesting || 1))*100)}%`, metrics.highCoverage >= (metrics.hasTesting || 1) * 0.7 ? "✅" : "⚠️"],
        ["API Documented", metrics.hasAPI, `${Math.round((metrics.hasAPI/metrics.total)*100)}%`, metrics.hasAPI >= metrics.total * 0.15 ? "✅" : "⚠️"],
        ["Updated (90d)", metrics.recentUpdate, `${Math.round((metrics.recentUpdate/metrics.total)*100)}%`, metrics.recentUpdate >= metrics.total * 0.4 ? "✅" : "⚠️"],
        ["Has Owner", metrics.hasOwner, `${Math.round((metrics.hasOwner/metrics.total)*100)}%`, metrics.hasOwner >= metrics.total * 0.8 ? "✅" : "⚠️"]
    ]
);
```

---

## Quick Actions

- [[Create API Documentation]]
- [[Create Developer Guide]]
- [[Create Code Standard]]
- [[Log Technical Debt]]
- [[Update Test Coverage]]
- [[Review Code Quality]]

---

**Dashboard Statistics:**
- Total Development Documents: *Dynamic count*
- Features In Development: *Dynamic count*
- Development Health Score: *Dynamic score*
- Last Dashboard Update: 2026-04-20

**Navigation:**
- [[DASHBOARD_GOVERNANCE|← Governance Dashboard]]
- [[DASHBOARD_OPERATIONS|Operations Dashboard →]]
- [[04_DEVELOPMENT|Development Index]]
- [[00_INDEX|Main Index]]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

