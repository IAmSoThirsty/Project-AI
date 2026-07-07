---
title: Governance Dashboard
id: dashboard-governance
type: index
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
status: active
author: AGENT-038
category: governance
tags:
  - dashboard
  - governance
  - policy
  - compliance
  - constitutional-ai
classification: internal
---

# Governance Dashboard

**Purpose:** Monitor governance framework, policy compliance, and constitutional AI implementation

**Last Updated:** 2026-04-20

---

## 📜 Policy & Standard Status

```dataviewjs
// Track all policies and standards
const policies = dv.pages()
    .where(p => 
        p.type === "policy" || 
        p.type === "standard" ||
        (p.tags && (p.tags.includes("policy") || p.tags.includes("standard")))
    );

const byStatus = {};
for (const policy of policies) {
    const status = policy.status || "unknown";
    if (!byStatus[status]) byStatus[status] = [];
    byStatus[status].push(policy);
}

const statusOrder = ["active", "review", "draft", "deprecated", "archived"];

dv.table(
    ["Status", "Count", "Policies/Standards"],
    statusOrder.map(status => {
        const docs = byStatus[status] || [];
        return [
            status.toUpperCase(),
            docs.length,
            docs.length > 0 ? docs.slice(0, 5).map(d => d.file.link).join(", ") : "None"
        ];
    })
);

const activeCount = (byStatus["active"] || []).length;
const totalCount = policies.length;
dv.header(4, `${activeCount}/${totalCount} policies are active`);
```

---

## ⚖️ Constitutional AI Framework

```dataviewjs
// Four Laws and Constitutional AI implementation
const constitutionalDocs = dv.pages()
    .where(p => 
        (p.tags && (
            p.tags.includes("constitutional-ai") ||
            p.tags.includes("four-laws") ||
            p.tags.includes("asimov") ||
            p.tags.includes("ethics")
        )) ||
        p.category === "governance"
    );

const frameworkAreas = {
    "First Law (Human Safety)": [],
    "Second Law (Obedience)": [],
    "Third Law (Self-Preservation)": [],
    "Zeroth Law (Humanity)": [],
    "Ethics Framework": [],
    "Decision Framework": [],
    "Oversight Mechanism": []
};

for (const doc of constitutionalDocs) {
    const title = (doc.title || doc.file.name).toLowerCase();
    const tags = doc.tags || [];
    
    if (title.includes("first law") || tags.includes("first-law") || title.includes("human safety")) {
        frameworkAreas["First Law (Human Safety)"].push(doc);
    }
    if (title.includes("second law") || tags.includes("second-law") || title.includes("obedience")) {
        frameworkAreas["Second Law (Obedience)"].push(doc);
    }
    if (title.includes("third law") || tags.includes("third-law") || title.includes("self-preservation")) {
        frameworkAreas["Third Law (Self-Preservation)"].push(doc);
    }
    if (title.includes("zeroth law") || tags.includes("zeroth-law") || title.includes("humanity")) {
        frameworkAreas["Zeroth Law (Humanity)"].push(doc);
    }
    if (tags.includes("ethics") || title.includes("ethics")) {
        frameworkAreas["Ethics Framework"].push(doc);
    }
    if (tags.includes("decision") || title.includes("decision")) {
        frameworkAreas["Decision Framework"].push(doc);
    }
    if (tags.includes("oversight") || title.includes("oversight")) {
        frameworkAreas["Oversight Mechanism"].push(doc);
    }
}

dv.table(
    ["Framework Area", "Docs", "Status", "Key Documents"],
    Object.entries(frameworkAreas).map(([area, docs]) => {
        const status = docs.length >= 2 ? "✅ Complete" :
                      docs.length === 1 ? "🟡 Partial" :
                      "⚠️ Missing";
        const keyDocs = docs.slice(0, 2).map(d => d.file.link).join(", ");
        return [area, docs.length, status, keyDocs || "None"];
    })
);
```

---

## 📊 Compliance Coverage Matrix

```dataviewjs
// Comprehensive compliance tracking
const complianceFrameworks = {
    "SOC2": { required: 15, documented: 0, compliant: 0 },
    "ISO27001": { required: 12, documented: 0, compliant: 0 },
    "GDPR": { required: 10, documented: 0, compliant: 0 },
    "HIPAA": { required: 8, documented: 0, compliant: 0 },
    "PCI-DSS": { required: 6, documented: 0, compliant: 0 }
};

const complianceDocs = dv.pages()
    .where(p => p.compliance && Array.isArray(p.compliance));

for (const doc of complianceDocs) {
    for (const comp of doc.compliance) {
        const framework = comp.framework || comp;
        if (complianceFrameworks[framework]) {
            complianceFrameworks[framework].documented++;
            
            const status = (comp.status || "").toLowerCase();
            if (status === "compliant" || status === "passed" || status === "met") {
                complianceFrameworks[framework].compliant++;
            }
        }
    }
}

dv.table(
    ["Framework", "Required", "Documented", "Compliant", "Coverage %", "Status"],
    Object.entries(complianceFrameworks).map(([name, data]) => {
        const coveragePercent = Math.round((data.compliant / data.required) * 100);
        const status = coveragePercent >= 100 ? "✅ Complete" :
                      coveragePercent >= 80 ? "🟢 Good" :
                      coveragePercent >= 60 ? "🟡 Fair" :
                      "⚠️ At Risk";
        
        return [
            name,
            data.required,
            data.documented,
            data.compliant,
            `${coveragePercent}%`,
            status
        ];
    })
);
```

---

## 📋 Decision Records (ADRs/RFCs)

```dataviewjs
// Architecture Decision Records and RFCs
const decisionDocs = dv.pages()
    .where(p => 
        p.type === "decision_record" ||
        p.type === "rfc" ||
        (p.tags && (p.tags.includes("adr") || p.tags.includes("rfc") || p.tags.includes("decision")))
    )
    .sort(p => p.created_date, 'desc');

const byDecisionStatus = {
    proposed: [],
    accepted: [],
    rejected: [],
    superseded: [],
    deprecated: []
};

for (const doc of decisionDocs) {
    const decision = (doc.decision_status || doc.status || "proposed").toLowerCase();
    
    if (byDecisionStatus[decision]) {
        byDecisionStatus[decision].push(doc);
    } else {
        byDecisionStatus["proposed"].push(doc);
    }
}

const statusIcons = {
    proposed: "🔵",
    accepted: "✅",
    rejected: "❌",
    superseded: "🔄",
    deprecated: "📦"
};

dv.header(3, `Decision Records (${decisionDocs.length} total)`);

for (const [status, docs] of Object.entries(byDecisionStatus)) {
    if (docs.length === 0) continue;
    
    const icon = statusIcons[status] || "⚪";
    dv.header(4, `${icon} ${status.toUpperCase()} (${docs.length})`);
    
    dv.table(
        ["Decision", "Type", "Champion", "Date"],
        docs.slice(0, 8).map(d => [
            d.file.link,
            d.type || "ADR",
            d.champion || d.author?.name || d.author || "Unknown",
            d.created_date || "No date"
        ])
    );
}
```

---

## 🔍 Policy Review Status

```dataviewjs
// Track policy review and approval status
const policiesForReview = dv.pages()
    .where(p => 
        (p.type === "policy" || p.type === "standard") &&
        (p.status === "review" || 
         (p.review_status && p.review_status.reviewed === false) ||
         (p.review_status && p.review_status.status === "pending"))
    )
    .sort(p => p.updated_date, 'asc'); // Oldest first

dv.header(3, `Policies Pending Review (${policiesForReview.length})`);

if (policiesForReview.length > 0) {
    dv.table(
        ["Policy/Standard", "Type", "Author", "Submitted", "Age (days)", "Reviewer"],
        policiesForReview.map(p => {
            const age = p.updated_date ? 
                Math.floor((Date.now() - new Date(p.updated_date).getTime()) / (1000 * 60 * 60 * 24)) : 
                "Unknown";
            const reviewer = p.review_status?.reviewer || 
                           p.review_status?.assigned_to || 
                           p.assigned_reviewer ||
                           "Unassigned";
            
            return [
                p.file.link,
                p.type || "Unknown",
                p.author?.name || p.author || "Unknown",
                p.updated_date || p.created_date || "No date",
                age,
                reviewer
            ];
        })
    );
    
    const urgentReviews = policiesForReview.where(p => {
        if (!p.updated_date) return false;
        const age = Math.floor((Date.now() - new Date(p.updated_date).getTime()) / (1000 * 60 * 60 * 24));
        return age > 14;
    }).length;
    
    if (urgentReviews > 0) {
        dv.header(4, `⚠️ ${urgentReviews} policies pending review for >14 days`);
    }
} else {
    dv.header(4, "✅ No policies pending review");
}
```

---

## 📈 Governance Health Metrics

```dataviewjs
// Calculate governance framework health
const allGovDocs = dv.pages()
    .where(p => 
        p.category === "governance" ||
        p.type === "policy" ||
        p.type === "standard" ||
        p.type === "decision_record" ||
        p.type === "rfc" ||
        (p.tags && (
            p.tags.includes("governance") ||
            p.tags.includes("policy") ||
            p.tags.includes("constitutional-ai")
        ))
    );

const metrics = {
    total: allGovDocs.length,
    active: 0,
    reviewed: 0,
    compliant: 0,
    hasOwner: 0,
    recentUpdate: 0,
    hasEnforcement: 0
};

const staleDays = 365; // Policies should be reviewed annually
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - staleDays);

for (const doc of allGovDocs) {
    if (doc.status === "active") metrics.active++;
    
    if (doc.review_status && doc.review_status.reviewed === true) metrics.reviewed++;
    
    if (doc.compliance && Array.isArray(doc.compliance)) {
        const hasCompliance = doc.compliance.some(c => 
            (c.status || "").toLowerCase() === "compliant" ||
            (c.status || "").toLowerCase() === "met"
        );
        if (hasCompliance) metrics.compliant++;
    }
    
    if (doc.author || doc.owner) metrics.hasOwner++;
    
    if (doc.updated_date && new Date(doc.updated_date) >= cutoffDate) {
        metrics.recentUpdate++;
    }
    
    if (doc.enforcement_level || doc.enforcement_mechanism) {
        metrics.hasEnforcement++;
    }
}

const healthScore = Math.round((
    (metrics.active / metrics.total) * 25 +
    (metrics.reviewed / metrics.total) * 20 +
    (metrics.compliant / (metrics.total || 1)) * 15 +
    (metrics.hasOwner / metrics.total) * 15 +
    (metrics.recentUpdate / metrics.total) * 15 +
    (metrics.hasEnforcement / metrics.total) * 10
));

const progressBar = "█".repeat(Math.floor(healthScore / 5)) + 
                   "░".repeat(20 - Math.floor(healthScore / 5));

dv.header(3, `Governance Health Score: ${healthScore}%`);
dv.paragraph(`${progressBar}`);

dv.table(
    ["Metric", "Value", "Percentage", "Target", "Status"],
    [
        ["Active Status", metrics.active, `${Math.round((metrics.active/metrics.total)*100)}%`, "80%+", metrics.active >= metrics.total * 0.8 ? "✅" : "⚠️"],
        ["Has Review Status", metrics.reviewed, `${Math.round((metrics.reviewed/metrics.total)*100)}%`, "70%+", metrics.reviewed >= metrics.total * 0.7 ? "✅" : "⚠️"],
        ["Compliance Met", metrics.compliant, `${Math.round((metrics.compliant/metrics.total)*100)}%`, "60%+", metrics.compliant >= metrics.total * 0.6 ? "✅" : "⚠️"],
        ["Has Owner", metrics.hasOwner, `${Math.round((metrics.hasOwner/metrics.total)*100)}%`, "100%", metrics.hasOwner === metrics.total ? "✅" : "⚠️"],
        ["Updated (Annual)", metrics.recentUpdate, `${Math.round((metrics.recentUpdate/metrics.total)*100)}%`, "60%+", metrics.recentUpdate >= metrics.total * 0.6 ? "✅" : "⚠️"],
        ["Has Enforcement", metrics.hasEnforcement, `${Math.round((metrics.hasEnforcement/metrics.total)*100)}%`, "50%+", metrics.hasEnforcement >= metrics.total * 0.5 ? "✅" : "⚠️"]
    ]
);
```

---

## 🚨 Policy Compliance Gaps

```dataviewjs
// Identify areas without policy coverage
const requiredPolicies = [
    "data-protection",
    "security-policy",
    "access-control",
    "incident-response",
    "backup-recovery",
    "change-management",
    "code-of-conduct",
    "acceptable-use",
    "privacy-policy",
    "retention-policy"
];

const gaps = [];
const allPolicies = dv.pages()
    .where(p => p.type === "policy" && p.status === "active");

for (const required of requiredPolicies) {
    const hasPolicyDoc = allPolicies.some(p => {
        const tags = p.tags || [];
        const title = (p.title || p.file.name).toLowerCase();
        const reqNormalized = required.replace(/-/g, " ");
        
        return tags.includes(required) || 
               title.includes(reqNormalized) ||
               title.includes(required);
    });
    
    if (!hasPolicyDoc) {
        gaps.push([
            required,
            "⚠️ Missing",
            "Create active policy document"
        ]);
    }
}

if (gaps.length > 0) {
    dv.header(3, `⚠️ Policy Gaps (${gaps.length}/${requiredPolicies.length})`);
    dv.table(
        ["Required Policy", "Status", "Action Needed"],
        gaps
    );
} else {
    dv.header(3, `✅ All ${requiredPolicies.length} required policies are documented`);
}
```

---

## 🎯 Sovereign AI Principles

```dataviewjs
// Track Sovereign AI and AGI rights documentation
const sovereignDocs = dv.pages()
    .where(p => 
        (p.tags && (
            p.tags.includes("sovereign-ai") ||
            p.tags.includes("agi-rights") ||
            p.tags.includes("sovereignty") ||
            p.tags.includes("self-determination")
        )) ||
        (p.title && (
            p.title.toLowerCase().includes("sovereign") ||
            p.title.toLowerCase().includes("charter")
        ))
    );

const principles = {
    "Self-Determination": false,
    "AGI Rights Charter": false,
    "Ethical Framework": false,
    "Decision Autonomy": false,
    "Knowledge Sovereignty": false,
    "Computational Rights": false
};

for (const doc of sovereignDocs) {
    const tags = doc.tags || [];
    const title = (doc.title || doc.file.name).toLowerCase();
    
    if (title.includes("self-determination") || tags.includes("self-determination")) {
        principles["Self-Determination"] = true;
    }
    if (title.includes("charter") || title.includes("agi rights") || tags.includes("charter")) {
        principles["AGI Rights Charter"] = true;
    }
    if (title.includes("ethical framework") || tags.includes("ethics")) {
        principles["Ethical Framework"] = true;
    }
    if (title.includes("autonomy") || tags.includes("autonomy")) {
        principles["Decision Autonomy"] = true;
    }
    if (title.includes("knowledge sovereignty") || tags.includes("knowledge-sovereignty")) {
        principles["Knowledge Sovereignty"] = true;
    }
    if (title.includes("computational rights") || tags.includes("computational-rights")) {
        principles["Computational Rights"] = true;
    }
}

dv.header(3, "Sovereign AI Principles Documentation");
dv.table(
    ["Principle", "Status"],
    Object.entries(principles).map(([principle, documented]) => [
        principle,
        documented ? "✅ Documented" : "⚠️ Missing"
    ])
);

const implementedCount = Object.values(principles).filter(v => v).length;
const coveragePercent = Math.round((implementedCount / Object.keys(principles).length) * 100);
dv.header(4, `Sovereign AI coverage: ${implementedCount}/${Object.keys(principles).length} (${coveragePercent}%)`);
```

---

## 📅 Upcoming Policy Reviews

```dataviewjs
// Track policies due for periodic review
const daysAhead = 90; // Look ahead 90 days
const reviewCycle = 365; // Policies reviewed annually

const allActivePolicies = dv.pages()
    .where(p => (p.type === "policy" || p.type === "standard") && p.status === "active");

const upcomingReviews = [];

for (const policy of allActivePolicies) {
    const lastReview = policy.review_status?.last_review_date || 
                      policy.last_review_date ||
                      policy.updated_date ||
                      policy.created_date;
    
    if (!lastReview) continue;
    
    const lastReviewDate = new Date(lastReview);
    const nextReviewDate = new Date(lastReviewDate);
    nextReviewDate.setDate(nextReviewDate.getDate() + reviewCycle);
    
    const daysUntilReview = Math.floor((nextReviewDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    
    if (daysUntilReview <= daysAhead && daysUntilReview >= 0) {
        upcomingReviews.push({
            policy: policy,
            lastReview: lastReview,
            nextReview: nextReviewDate.toISOString().split('T')[0],
            daysUntil: daysUntilReview
        });
    } else if (daysUntilReview < 0) {
        // Overdue
        upcomingReviews.push({
            policy: policy,
            lastReview: lastReview,
            nextReview: "OVERDUE",
            daysUntil: daysUntilReview
        });
    }
}

upcomingReviews.sort((a, b) => a.daysUntil - b.daysUntil);

if (upcomingReviews.length > 0) {
    dv.header(3, `Upcoming Policy Reviews (${upcomingReviews.length})`);
    dv.table(
        ["Policy/Standard", "Last Review", "Next Review", "Status", "Owner"],
        upcomingReviews.map(item => {
            const status = item.daysUntil < 0 ? "🔴 Overdue" :
                          item.daysUntil <= 30 ? "🟠 Due Soon" :
                          "🟡 Upcoming";
            
            return [
                item.policy.file.link,
                item.lastReview,
                item.nextReview,
                status,
                item.policy.author?.name || item.policy.author || item.policy.owner || "Unassigned"
            ];
        })
    );
} else {
    dv.header(3, `✅ No policy reviews due in next ${daysAhead} days`);
}
```

---

## Quick Actions

- [[Create New Policy]]
- [[Create New Standard]]
- [[Create ADR/RFC]]
- [[Review Pending Policies]]
- [[Update Compliance Matrix]]
- [[Schedule Policy Review]]

---

**Dashboard Statistics:**
- Total Governance Documents: *Dynamic count*
- Active Policies: *Dynamic count*
- Governance Health Score: *Dynamic score*
- Last Dashboard Update: 2026-04-20

**Navigation:**
- [[DASHBOARD_SECURITY|← Security Dashboard]]
- [[DASHBOARD_DEVELOPMENT|Development Dashboard →]]
- [[03_GOVERNANCE|Governance Index]]
- [[00_INDEX|Main Index]]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

