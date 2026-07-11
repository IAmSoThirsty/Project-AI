---
title: Security Dashboard
id: dashboard-security
type: index
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
status: active
author: AGENT-038
category: security
tags:
  - dashboard
  - security
  - monitoring
  - audit
  - compliance
classification: internal
---

# Security Dashboard

**Purpose:** Real-time security posture monitoring, audit tracking, and vulnerability management

**Last Updated:** 2026-04-20

---

## 🔴 Critical Security Findings

```dataviewjs
// Show critical security findings from audit documents
const securityAudits = dv.pages()
    .where(p =>
        (p.type === "audit" || p.type === "assessment") &&
        (p.tags && p.tags.some(t => t.includes("security"))) &&
        (p.status === "active" || p.status === "review")
    );

const criticalFindings = [];
const highFindings = [];

for (const audit of securityAudits) {
    if (audit.findings && Array.isArray(audit.findings)) {
        for (const finding of audit.findings) {
            const severity = (finding.severity || finding.risk_level || "unknown").toLowerCase();
            const status = (finding.status || "open").toLowerCase();

            if (status !== "resolved" && status !== "closed") {
                const item = {
                    title: finding.title || finding.description || "Unnamed",
                    severity: severity,
                    status: status,
                    source: audit.file.link,
                    date: finding.date || audit.created_date
                };

                if (severity === "critical") {
                    criticalFindings.push(item);
                } else if (severity === "high") {
                    highFindings.push(item);
                }
            }
        }
    }
}

if (criticalFindings.length > 0) {
    dv.header(3, `🔴 CRITICAL FINDINGS (${criticalFindings.length}) - IMMEDIATE ACTION REQUIRED`);
    dv.table(
        ["Finding", "Status", "Source Document", "Reported"],
        criticalFindings.map(f => [f.title, f.status, f.source, f.date])
    );
} else {
    dv.header(3, "✅ No critical security findings");
}

if (highFindings.length > 0) {
    dv.header(3, `🟠 HIGH SEVERITY FINDINGS (${highFindings.length})`);
    dv.table(
        ["Finding", "Status", "Source Document", "Reported"],
        highFindings.slice(0, 10).map(f => [f.title, f.status, f.source, f.date])
    );
    if (highFindings.length > 10) {
        dv.paragraph(`*... and ${highFindings.length - 10} more high severity findings*`);
    }
}
```

---

## 🛡️ Security Documentation Status

```dataviewjs
// Track security documentation coverage
const securityDocs = dv.pages()
    .where(p =>
        (p.category === "security" || p.tags && p.tags.some(t => t.includes("security")))
    );

const docTypes = {
    "Security Policy": 0,
    "Audit Report": 0,
    "Threat Model": 0,
    "Security Guide": 0,
    "Incident Response": 0,
    "Penetration Test": 0,
    "Vulnerability Assessment": 0,
    "Security Architecture": 0
};

for (const doc of securityDocs) {
    const type = doc.type || "unknown";
    const tags = doc.tags || [];

    if (type === "policy" || tags.includes("policy")) docTypes["Security Policy"]++;
    if (type === "audit" || tags.includes("audit")) docTypes["Audit Report"]++;
    if (tags.includes("threat-model") || tags.includes("threat")) docTypes["Threat Model"]++;
    if (type === "guide" && tags.includes("security")) docTypes["Security Guide"]++;
    if (tags.includes("incident") || tags.includes("incident-response")) docTypes["Incident Response"]++;
    if (tags.includes("pentest") || tags.includes("penetration-test")) docTypes["Penetration Test"]++;
    if (type === "assessment" || tags.includes("vulnerability")) docTypes["Vulnerability Assessment"]++;
    if (tags.includes("security") && (type === "architecture" || type === "design")) docTypes["Security Architecture"]++;
}

dv.table(
    ["Document Type", "Count", "Status"],
    Object.entries(docTypes).map(([type, count]) => {
        const status = count >= 2 ? "✅ Good" :
                      count === 1 ? "🟡 Minimal" :
                      "⚠️ Missing";
        return [type, count, status];
    })
);

const totalSecDocs = securityDocs.length;
dv.header(4, `Total security documents: ${totalSecDocs}`);
```

---

## 📋 Compliance Framework Coverage

```dataviewjs
// Compliance framework tracking
const frameworks = ["SOC2", "ISO27001", "GDPR", "HIPAA", "PCI-DSS", "NIST-CSF"];

const complianceDocs = dv.pages()
    .where(p => p.compliance && Array.isArray(p.compliance));

const coverage = {};
for (const framework of frameworks) {
    coverage[framework] = {
        total: 0,
        compliant: 0,
        partial: 0,
        nonCompliant: 0
    };
}

for (const doc of complianceDocs) {
    for (const comp of doc.compliance) {
        const framework = comp.framework || comp;
        if (coverage[framework]) {
            coverage[framework].total++;

            const status = (comp.status || "unknown").toLowerCase();
            if (status === "compliant" || status === "passed") {
                coverage[framework].compliant++;
            } else if (status === "partial" || status === "in_progress") {
                coverage[framework].partial++;
            } else if (status === "non-compliant" || status === "failed") {
                coverage[framework].nonCompliant++;
            }
        }
    }
}

dv.table(
    ["Framework", "Total Docs", "✅ Compliant", "🟡 Partial", "❌ Non-Compliant", "Coverage"],
    frameworks.map(fw => {
        const data = coverage[fw];
        const coveragePercent = data.total > 0 ?
            Math.round(((data.compliant + data.partial * 0.5) / data.total) * 100) : 0;

        return [
            fw,
            data.total,
            data.compliant,
            data.partial,
            data.nonCompliant,
            `${coveragePercent}%`
        ];
    })
);
```

---

## 🔐 Authentication & Authorization Coverage

```dataviewjs
// Security control coverage for auth systems
const authDocs = dv.pages()
    .where(p =>
        p.tags && (
            p.tags.includes("authentication") ||
            p.tags.includes("authorization") ||
            p.tags.includes("access-control")
        )
    )
    .where(p => p.status === "active" || p.status === "review");

const authControls = {
    "Password Policy": false,
    "MFA/2FA": false,
    "Session Management": false,
    "OAuth/SSO": false,
    "API Authentication": false,
    "Role-Based Access Control": false,
    "Privilege Management": false,
    "Account Lockout": false
};

for (const doc of authDocs) {
    const tags = doc.tags || [];
    const title = (doc.title || doc.file.name).toLowerCase();

    if (tags.includes("password") || title.includes("password")) authControls["Password Policy"] = true;
    if (tags.includes("mfa") || tags.includes("2fa") || title.includes("multi-factor")) authControls["MFA/2FA"] = true;
    if (tags.includes("session") || title.includes("session")) authControls["Session Management"] = true;
    if (tags.includes("oauth") || tags.includes("sso")) authControls["OAuth/SSO"] = true;
    if (tags.includes("api-auth") || (tags.includes("api") && tags.includes("authentication"))) authControls["API Authentication"] = true;
    if (tags.includes("rbac") || title.includes("role-based")) authControls["Role-Based Access Control"] = true;
    if (tags.includes("privilege") || title.includes("privilege")) authControls["Privilege Management"] = true;
    if (tags.includes("lockout") || title.includes("lockout")) authControls["Account Lockout"] = true;
}

dv.header(3, "Authentication & Authorization Controls");
dv.table(
    ["Control", "Status"],
    Object.entries(authControls).map(([control, implemented]) => [
        control,
        implemented ? "✅ Documented" : "⚠️ Missing"
    ])
);

const implementedCount = Object.values(authControls).filter(v => v).length;
const coveragePercent = Math.round((implementedCount / Object.keys(authControls).length) * 100);
dv.header(4, `Auth control coverage: ${implementedCount}/${Object.keys(authControls).length} (${coveragePercent}%)`);
```

---

## 📊 Security Audit Timeline

```dataviewjs
// Recent security audits and assessments
const auditDocs = dv.pages()
    .where(p =>
        (p.type === "audit" || p.type === "assessment") &&
        (p.tags && p.tags.some(t => t.includes("security")))
    )
    .sort(p => p.created_date, 'desc')
    .limit(15);

dv.table(
    ["Audit/Assessment", "Type", "Date", "Status", "Findings", "Risk Level"],
    auditDocs.map(p => {
        const findingCount = (p.findings && Array.isArray(p.findings)) ? p.findings.length : 0;
        const riskLevel = p.risk_level || p.overall_risk || "Unknown";

        return [
            p.file.link,
            p.type || "Unknown",
            p.created_date || "No date",
            p.status || "Unknown",
            findingCount,
            riskLevel
        ];
    })
);

const recentAudits = auditDocs.where(p => {
    if (!p.created_date) return false;
    const daysSince = (Date.now() - new Date(p.created_date).getTime()) / (1000 * 60 * 60 * 24);
    return daysSince <= 90;
}).length;

dv.header(4, `${recentAudits} security audits conducted in last 90 days`);
```

---

## 🚨 Security Incident Tracking

```dataviewjs
// Track security incidents and response
const incidents = dv.pages()
    .where(p =>
        (p.tags && (
            p.tags.includes("incident") ||
            p.tags.includes("breach") ||
            p.tags.includes("security-event")
        )) ||
        p.type === "incident_report"
    )
    .sort(p => p.created_date, 'desc');

const byStatus = {
    open: [],
    investigating: [],
    resolved: [],
    closed: []
};

for (const incident of incidents) {
    const status = (incident.incident_status || incident.status || "open").toLowerCase();
    if (byStatus[status]) {
        byStatus[status].push(incident);
    } else {
        byStatus["open"].push(incident);
    }
}

dv.header(3, `Security Incidents (${incidents.length} total)`);

const statusIcons = {
    open: "🔴",
    investigating: "🟡",
    resolved: "🟢",
    closed: "✅"
};

for (const [status, docs] of Object.entries(byStatus)) {
    if (docs.length === 0) continue;

    const icon = statusIcons[status] || "⚪";
    dv.header(4, `${icon} ${status.toUpperCase()} (${docs.length})`);

    if (docs.length > 0 && (status === "open" || status === "investigating")) {
        dv.table(
            ["Incident", "Severity", "Date", "Owner"],
            docs.slice(0, 5).map(d => [
                d.file.link,
                d.severity || "Unknown",
                d.created_date || "No date",
                d.owner || d.assigned_to || "Unassigned"
            ])
        );
    } else {
        dv.list(docs.slice(0, 5).map(d => d.file.link));
    }
}

const openIncidents = (byStatus["open"] || []).length + (byStatus["investigating"] || []).length;
if (openIncidents > 0) {
    dv.header(4, `⚠️ ${openIncidents} incidents require attention`);
}
```

---

## 🔒 Cryptography & Encryption Status

```dataviewjs
// Cryptography implementation tracking
const cryptoDocs = dv.pages()
    .where(p =>
        p.tags && (
            p.tags.includes("cryptography") ||
            p.tags.includes("encryption") ||
            p.tags.includes("crypto")
        )
    );

const cryptoAreas = {
    "Data at Rest Encryption": false,
    "Data in Transit (TLS/SSL)": false,
    "Key Management": false,
    "Hashing Algorithms": false,
    "Certificate Management": false,
    "Secrets Management": false
};

for (const doc of cryptoDocs) {
    const tags = doc.tags || [];
    const title = (doc.title || doc.file.name).toLowerCase();

    if (tags.includes("at-rest") || title.includes("at rest") || title.includes("disk encryption")) {
        cryptoAreas["Data at Rest Encryption"] = true;
    }
    if (tags.includes("tls") || tags.includes("ssl") || title.includes("transit")) {
        cryptoAreas["Data in Transit (TLS/SSL)"] = true;
    }
    if (tags.includes("key-management") || title.includes("key management")) {
        cryptoAreas["Key Management"] = true;
    }
    if (tags.includes("hashing") || tags.includes("hash") || title.includes("bcrypt") || title.includes("sha")) {
        cryptoAreas["Hashing Algorithms"] = true;
    }
    if (tags.includes("certificate") || title.includes("certificate")) {
        cryptoAreas["Certificate Management"] = true;
    }
    if (tags.includes("secrets") || title.includes("secrets")) {
        cryptoAreas["Secrets Management"] = true;
    }
}

dv.header(3, "Cryptography Coverage");
dv.table(
    ["Area", "Status", "Action"],
    Object.entries(cryptoAreas).map(([area, implemented]) => [
        area,
        implemented ? "✅ Documented" : "⚠️ Missing",
        implemented ? "Review & Update" : "Create Documentation"
    ])
);
```

---

## 📈 Security Metrics Trend

```dataviewjs
// Calculate security health score
const allSecDocs = dv.pages()
    .where(p =>
        p.category === "security" ||
        (p.tags && p.tags.some(t => t.includes("security")))
    );

const metrics = {
    totalDocs: allSecDocs.length,
    activeDocs: 0,
    auditsConducted: 0,
    findingsResolved: 0,
    findingsOpen: 0,
    policiesActive: 0,
    recentUpdates: 0
};

const staleDays = 180;
const cutoffDate = new Date();
cutoffDate.setDate(cutoffDate.getDate() - staleDays);

for (const doc of allSecDocs) {
    if (doc.status === "active") metrics.activeDocs++;
    if (doc.type === "audit" || doc.type === "assessment") metrics.auditsConducted++;
    if (doc.type === "policy" && doc.status === "active") metrics.policiesActive++;
    if (doc.updated_date && new Date(doc.updated_date) >= cutoffDate) metrics.recentUpdates++;

    if (doc.findings && Array.isArray(doc.findings)) {
        for (const finding of doc.findings) {
            const status = (finding.status || "open").toLowerCase();
            if (status === "resolved" || status === "closed") {
                metrics.findingsResolved++;
            } else {
                metrics.findingsOpen++;
            }
        }
    }
}

const resolutionRate = (metrics.findingsResolved + metrics.findingsOpen) > 0 ?
    Math.round((metrics.findingsResolved / (metrics.findingsResolved + metrics.findingsOpen)) * 100) : 100;

const healthScore = Math.round((
    (metrics.activeDocs / metrics.totalDocs) * 25 +
    Math.min((metrics.auditsConducted / 4), 1) * 20 +
    (resolutionRate / 100) * 25 +
    Math.min((metrics.policiesActive / 5), 1) * 15 +
    (metrics.recentUpdates / metrics.totalDocs) * 15
));

const progressBar = "█".repeat(Math.floor(healthScore / 5)) +
                   "░".repeat(20 - Math.floor(healthScore / 5));

dv.header(3, `Security Health Score: ${healthScore}%`);
dv.paragraph(`${progressBar}`);

dv.table(
    ["Metric", "Value", "Target", "Status"],
    [
        ["Active Docs", metrics.activeDocs, `${Math.round(metrics.totalDocs * 0.8)}+`, metrics.activeDocs >= metrics.totalDocs * 0.8 ? "✅" : "⚠️"],
        ["Audits (Annual)", metrics.auditsConducted, "4+", metrics.auditsConducted >= 4 ? "✅" : "⚠️"],
        ["Finding Resolution", `${resolutionRate}%`, "80%+", resolutionRate >= 80 ? "✅" : "⚠️"],
        ["Active Policies", metrics.policiesActive, "5+", metrics.policiesActive >= 5 ? "✅" : "⚠️"],
        ["Recent Updates", metrics.recentUpdates, `${Math.round(metrics.totalDocs * 0.5)}+`, metrics.recentUpdates >= metrics.totalDocs * 0.5 ? "✅" : "⚠️"]
    ]
);
```

---

## Quick Actions

- [[Create Security Audit]]
- [[Create Security Policy]]
- [[Report Security Incident]]
- [[Review Open Findings]]
- [[Update Compliance Status]]

---

**Dashboard Statistics:**
- Total Security Documents: *Dynamic count*
- Open Critical Findings: *Dynamic count*
- Security Health Score: *Dynamic score*
- Last Dashboard Update: 2026-04-20

**Navigation:**
- [[DASHBOARD_ARCHITECTURE|← Architecture Dashboard]]
- [[DASHBOARD_GOVERNANCE|Governance Dashboard →]]
- [[02_SECURITY|Security Index]]
- [[00_INDEX|Main Index]]

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
