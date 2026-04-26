---
query_name: Untagged and Undertagged Documents Report
query_type: quality-assurance
purpose: Identify documents with missing, insufficient, or inconsistent tags for maintenance
created: 2024-04-20
performance_target: <1s
tags:
  - dataview-query
  - quality-control
  - tag-validation
  - maintenance
related_queries:
  - 01-documents-by-tag-category
  - 04-tag-cooccurrence-matrix
status: production-ready
---

# Untagged and Undertagged Documents Report

**Purpose:** Quality assurance queries to identify documentation gaps, tag coverage issues, and maintenance opportunities. Ensures consistent tag application across the vault for optimal discoverability.

---

## Query 1: Completely Untagged Documents

**Description:** Find all documents with zero tags.

**Simple Query:**
```dataview
TABLE
  file.name as "Document",
  file.ctime as "Created",
  file.mtime as "Last Modified",
  file.size as "Size (bytes)",
  type as "Type"
FROM ""
WHERE !file.tags OR length(file.tags) = 0
SORT file.mtime DESC
```

**Enhanced Query with Context:**
```dataview
TABLE
  file.name as "Document",
  file.folder as "Folder",
  choice(file.mtime >= date(today) - dur(7 days), "🆕 New", 
         file.mtime >= date(today) - dur(30 days), "📅 Recent", 
         "⏰ Old") as "Age",
  file.mtime as "Modified",
  round(file.size / 1024, 1) + " KB" as "Size"
FROM ""
WHERE !file.tags OR length(file.tags) = 0
SORT file.mtime DESC
LIMIT 100
```

**Expected Output:**
```
X results (ideally 0)

| Document | Folder | Age | Modified | Size |
|----------|--------|-----|----------|------|
| temp-notes | /scratch | 🆕 New | 2024-04-19 | 2.3 KB |
| draft-spec | /drafts | 📅 Recent | 2024-04-05 | 15.7 KB |
```

**Aggregate Summary:**
```dataviewjs
const allPages = dv.pages('""');
const untaggedPages = allPages.filter(p => !p.file.tags || p.file.tags.length === 0);
const totalPages = allPages.length;

dv.header(3, "🚨 Untagged Documents Summary");
dv.paragraph(`**Total Documents:** ${totalPages}`);
dv.paragraph(`**Untagged Documents:** ${untaggedPages.length}`);
dv.paragraph(`**Tag Coverage:** ${(((totalPages - untaggedPages.length) / totalPages) * 100).toFixed(1)}%`);
dv.paragraph(`**Quality Goal:** 100% tag coverage`);

if (untaggedPages.length > 0) {
  dv.header(4, "⚠️ Folders with Untagged Documents");
  
  const folderCounts = new Map();
  untaggedPages.forEach(p => {
    const folder = p.file.folder || "(root)";
    folderCounts.set(folder, (folderCounts.get(folder) || 0) + 1);
  });
  
  const sortedFolders = [...folderCounts.entries()]
    .sort((a, b) => b[1] - a[1]);
  
  dv.table(
    ["Folder", "Untagged Count"],
    sortedFolders.map(([folder, count]) => [folder, count])
  );
} else {
  dv.paragraph("✅ **All documents are tagged!**");
}
```

---

## Query 2: Undertagged Documents (< 4 Tags)

**Description:** Documents with fewer than the recommended minimum of 4 tags.

**Quality Threshold Query:**
```dataview
TABLE
  file.name as "Document",
  length(file.tags) as "Tag Count",
  file.tags as "Current Tags",
  choice(
    contains(string(file.tags), "#p0-") OR contains(string(file.tags), "#p1-"), "⚠️ Priority Doc",
    "📝 Standard Doc"
  ) as "Importance",
  file.mtime as "Modified"
FROM ""
WHERE file.tags AND length(file.tags) < 4
SORT length(file.tags) ASC, file.mtime DESC
LIMIT 100
```

**Severity-Based Classification:**
```dataview
TABLE
  file.name as "Document",
  length(file.tags) as "Tags",
  choice(
    length(file.tags) = 1, "🔴 Critical (1 tag)",
    length(file.tags) = 2, "🟠 High (2 tags)",
    length(file.tags) = 3, "🟡 Medium (3 tags)",
    "✅ OK"
  ) as "Severity",
  file.tags as "Current Tags",
  type as "Type"
FROM ""
WHERE file.tags AND length(file.tags) < 4
SORT length(file.tags) ASC
LIMIT 50
```

**Aggregate Analysis:**
```dataviewjs
const pages = dv.pages('""').where(p => p.file.tags && p.file.tags.length > 0);

const tagCountDistribution = {
  "1 tag": pages.filter(p => p.file.tags.length === 1).length,
  "2 tags": pages.filter(p => p.file.tags.length === 2).length,
  "3 tags": pages.filter(p => p.file.tags.length === 3).length,
  "4-5 tags": pages.filter(p => p.file.tags.length >= 4 && p.file.tags.length <= 5).length,
  "6-10 tags": pages.filter(p => p.file.tags.length >= 6 && p.file.tags.length <= 10).length,
  "10+ tags": pages.filter(p => p.file.tags.length > 10).length
};

const undertagged = pages.filter(p => p.file.tags.length < 4).length;

dv.header(3, "📊 Tag Count Distribution");
dv.table(
  ["Tag Range", "Document Count", "% of Vault"],
  Object.entries(tagCountDistribution).map(([range, count]) => [
    range,
    count,
    ((count / pages.length) * 100).toFixed(1) + "%"
  ])
);

dv.paragraph(`**Undertagged Documents (<4 tags):** ${undertagged} (${((undertagged / pages.length) * 100).toFixed(1)}%)`);
dv.paragraph(`**Quality Goal:** <5% undertagged`);
```

---

## Query 3: Missing Priority Tags (P0-P3)

**Description:** Documents lacking priority classification tags.

**Priority Tag Audit:**
```dataview
TABLE
  file.name as "Document",
  file.tags as "Current Tags",
  audience as "Audience",
  type as "Type",
  file.mtime as "Modified"
FROM ""
WHERE 
  file.tags AND
  !contains(string(file.tags), "#p0-") AND
  !contains(string(file.tags), "#p1-") AND
  !contains(string(file.tags), "#p2-") AND
  !contains(string(file.tags), "#p3-")
SORT file.mtime DESC
LIMIT 100
```

**Priority Gap Analysis with Recommendations:**
```dataviewjs
const pages = dv.pages('""').where(p => p.file.tags && p.file.tags.length > 0);

const noPriority = pages.filter(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  return !tagStr.includes("p0-") && !tagStr.includes("p1-") && 
         !tagStr.includes("p2-") && !tagStr.includes("p3-");
});

dv.header(3, "🎯 Priority Tag Gap Analysis");
dv.paragraph(`**Documents without priority tags:** ${noPriority.length} (${((noPriority.length / pages.length) * 100).toFixed(1)}%)`);

// Suggest priorities based on content
const suggestions = noPriority.array().slice(0, 20).map(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  let suggested = "p2-internal"; // Default
  
  if (tagStr.includes("governance") || tagStr.includes("security") || tagStr.includes("core")) {
    suggested = "p0-governance or p0-security";
  } else if (tagStr.includes("guide") || tagStr.includes("tutorial") || tagStr.includes("reference")) {
    suggested = "p1-developer";
  } else if (tagStr.includes("report") || tagStr.includes("status")) {
    suggested = "p2-root";
  } else if (tagStr.includes("archive") || tagStr.includes("deprecated")) {
    suggested = "p3-archive";
  }
  
  return {
    file: p.file.link,
    currentTags: p.file.tags.slice(0, 3).join(", "),
    suggested: suggested,
    confidence: tagStr.includes("governance") || tagStr.includes("security") ? "High" : "Medium"
  };
});

dv.table(
  ["Document", "Current Tags", "Suggested Priority", "Confidence"],
  suggestions.map(s => [s.file, s.currentTags, s.suggested, s.confidence])
);
```

---

## Query 4: Missing Functional Domain Tags

**Description:** Documents without functional categorization (guide, deployment, security, etc.).

**Domain Gap Query:**
```dataview
TABLE
  file.name as "Document",
  filter(file.tags, (t) => startswith(t, "#p0-") OR startswith(t, "#p1-") OR startswith(t, "#p2-") OR startswith(t, "#p3-")) as "Priority",
  file.tags as "All Tags",
  type as "Type"
FROM ""
WHERE 
  file.tags AND
  !contains(string(file.tags), "guide") AND
  !contains(string(file.tags), "tutorial") AND
  !contains(string(file.tags), "reference") AND
  !contains(string(file.tags), "deployment") AND
  !contains(string(file.tags), "security") AND
  !contains(string(file.tags), "testing") AND
  !contains(string(file.tags), "governance") AND
  !contains(string(file.tags), "architecture") AND
  !contains(string(file.tags), "api")
SORT file.mtime DESC
LIMIT 50
```

**Domain Coverage Report:**
```dataviewjs
const pages = dv.pages('""').where(p => p.file.tags && p.file.tags.length > 0);

const functionalDomains = [
  "guide", "tutorial", "reference", "quickstart",
  "deployment", "docker", "kubernetes", "ci-cd",
  "security", "compliance", "audit",
  "testing", "pytest", "e2e",
  "governance", "policy", "ethics",
  "architecture", "diagrams", "design-patterns",
  "api", "sdk"
];

const noDomain = pages.filter(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  return !functionalDomains.some(domain => tagStr.includes(domain));
});

dv.header(3, "📂 Functional Domain Coverage");
dv.paragraph(`**Documents without functional domain tags:** ${noDomain.length} (${((noDomain.length / pages.length) * 100).toFixed(1)}%)`);
dv.paragraph(`**Functional Domains Tracked:** ${functionalDomains.length}`);

// Domain distribution
const domainCounts = functionalDomains.map(domain => {
  const count = pages.filter(p => 
    p.file.tags.join(" ").toLowerCase().includes(domain)
  ).length;
  return { domain, count };
}).filter(d => d.count > 0)
  .sort((a, b) => b.count - a.count);

dv.table(
  ["Domain Tag", "Documents", "% Coverage"],
  domainCounts.slice(0, 15).map(d => [
    d.domain,
    d.count,
    ((d.count / pages.length) * 100).toFixed(1) + "%"
  ])
);
```

---

## Query 5: Inconsistent Tag Patterns

**Description:** Detect documents with unusual or inconsistent tag combinations.

**Pattern Validation:**
```dataviewjs
const pages = dv.pages('""').where(p => p.file.tags && p.file.tags.length > 0);

const issues = [];

pages.forEach(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  const tagArray = p.file.tags.map(t => t.toLowerCase());
  
  // Issue 1: Multiple priority tags (should have exactly one)
  const priorityTags = p.file.tags.filter(t => 
    t.includes("p0-") || t.includes("p1-") || t.includes("p2-") || t.includes("p3-")
  );
  if (priorityTags.length > 1) {
    issues.push({
      file: p.file.link,
      issue: "Multiple priority tags",
      details: priorityTags.join(", "),
      severity: "High"
    });
  }
  
  // Issue 2: Both "guide" and "tutorial" (usually redundant)
  if (tagStr.includes("guide") && tagStr.includes("tutorial")) {
    issues.push({
      file: p.file.link,
      issue: "Redundant: guide + tutorial",
      details: "Consider using one or the other",
      severity: "Low"
    });
  }
  
  // Issue 3: "deprecated" or "archived" but not in P3
  if ((tagStr.includes("deprecated") || tagStr.includes("archived")) && !tagStr.includes("p3-")) {
    issues.push({
      file: p.file.link,
      issue: "Archived but not P3",
      details: "Should have #p3-archive tag",
      severity: "Medium"
    });
  }
  
  // Issue 4: P0 priority but "draft" or "wip"
  if (tagStr.includes("p0-") && (tagStr.includes("draft") || tagStr.includes("wip"))) {
    issues.push({
      file: p.file.link,
      issue: "P0 priority + draft/wip",
      details: "Critical docs shouldn't be drafts",
      severity: "High"
    });
  }
  
  // Issue 5: Technology tag but no guide/reference/tutorial
  const techTags = ["python", "rust", "react", "docker"];
  const hasTech = techTags.some(tech => tagStr.includes(tech));
  const hasDocType = tagStr.includes("guide") || tagStr.includes("tutorial") || 
                      tagStr.includes("reference") || tagStr.includes("api");
  
  if (hasTech && !hasDocType && p.file.tags.length < 5) {
    issues.push({
      file: p.file.link,
      issue: "Technology tag missing doc type",
      details: "Add guide/tutorial/reference",
      severity: "Medium"
    });
  }
});

dv.header(3, "⚠️ Tag Pattern Inconsistencies");
dv.paragraph(`**Total Issues Found:** ${issues.length}`);

if (issues.length > 0) {
  // Group by severity
  const high = issues.filter(i => i.severity === "High");
  const medium = issues.filter(i => i.severity === "Medium");
  const low = issues.filter(i => i.severity === "Low");
  
  dv.paragraph(`🔴 **High Severity:** ${high.length}`);
  dv.paragraph(`🟠 **Medium Severity:** ${medium.length}`);
  dv.paragraph(`🟡 **Low Severity:** ${low.length}`);
  
  dv.table(
    ["Document", "Issue", "Details", "Severity"],
    issues.slice(0, 30).map(i => [i.file, i.issue, i.details, i.severity])
  );
} else {
  dv.paragraph("✅ **No tag pattern inconsistencies detected!**");
}
```

---

## Query 6: Comprehensive Tag Health Report

**Description:** Holistic view of tag quality across the entire vault.

**DataviewJS Health Dashboard:**
```dataviewjs
const allPages = dv.pages('""');
const taggedPages = allPages.filter(p => p.file.tags && p.file.tags.length > 0);

dv.header(2, "🏥 Vault Tag Health Report");

// 1. Coverage Metrics
dv.header(3, "📊 Coverage Metrics");
const coverage = {
  "Total Documents": allPages.length,
  "Tagged Documents": taggedPages.length,
  "Untagged Documents": allPages.length - taggedPages.length,
  "Tag Coverage %": ((taggedPages.length / allPages.length) * 100).toFixed(1) + "%"
};

dv.table(
  ["Metric", "Value"],
  Object.entries(coverage).map(([k, v]) => [k, v])
);

// 2. Quality Metrics
dv.header(3, "✅ Quality Metrics");
const quality = {
  "Properly Tagged (≥4 tags)": taggedPages.filter(p => p.file.tags.length >= 4).length,
  "Undertagged (<4 tags)": taggedPages.filter(p => p.file.tags.length < 4).length,
  "Well-Tagged (≥6 tags)": taggedPages.filter(p => p.file.tags.length >= 6).length,
  "Over-Tagged (>15 tags)": taggedPages.filter(p => p.file.tags.length > 15).length
};

dv.table(
  ["Metric", "Count", "% of Tagged"],
  Object.entries(quality).map(([k, v]) => [
    k, 
    v, 
    ((v / taggedPages.length) * 100).toFixed(1) + "%"
  ])
);

// 3. Taxonomy Compliance
dv.header(3, "🎯 Taxonomy Compliance");
const hasPriority = taggedPages.filter(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  return tagStr.includes("p0-") || tagStr.includes("p1-") || 
         tagStr.includes("p2-") || tagStr.includes("p3-");
}).length;

const hasDomain = taggedPages.filter(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  const domains = ["guide", "tutorial", "deployment", "security", "testing", "governance"];
  return domains.some(d => tagStr.includes(d));
}).length;

const hasTech = taggedPages.filter(p => {
  const tagStr = p.file.tags.join(" ").toLowerCase();
  const techs = ["python", "rust", "react", "docker"];
  return techs.some(t => tagStr.includes(t));
}).length;

dv.table(
  ["Taxonomy Level", "Documents", "% Compliance"],
  [
    ["Has Priority Tag (P0-P3)", hasPriority, ((hasPriority / taggedPages.length) * 100).toFixed(1) + "%"],
    ["Has Domain Tag", hasDomain, ((hasDomain / taggedPages.length) * 100).toFixed(1) + "%"],
    ["Has Technology Tag", hasTech, ((hasTech / taggedPages.length) * 100).toFixed(1) + "%"]
  ]
);

// 4. Health Score
dv.header(3, "🏆 Overall Tag Health Score");

const coverageScore = (taggedPages.length / allPages.length) * 30;
const qualityScore = (quality["Properly Tagged (≥4 tags)"] / taggedPages.length) * 30;
const priorityScore = (hasPriority / taggedPages.length) * 20;
const domainScore = (hasDomain / taggedPages.length) * 20;

const totalScore = coverageScore + qualityScore + priorityScore + domainScore;
const grade = totalScore >= 90 ? "A" : totalScore >= 80 ? "B" : totalScore >= 70 ? "C" : totalScore >= 60 ? "D" : "F";

dv.paragraph(`**Overall Score:** ${totalScore.toFixed(1)}/100`);
dv.paragraph(`**Grade:** ${grade}`);
dv.paragraph("");
dv.paragraph(`**Breakdown:**`);
dv.paragraph(`- Coverage (30%): ${coverageScore.toFixed(1)}/30`);
dv.paragraph(`- Quality (30%): ${qualityScore.toFixed(1)}/30`);
dv.paragraph(`- Priority Compliance (20%): ${priorityScore.toFixed(1)}/20`);
dv.paragraph(`- Domain Compliance (20%): ${domainScore.toFixed(1)}/20`);

// 5. Action Items
dv.header(3, "📝 Recommended Actions");
const actions = [];

if (coverage["Untagged Documents"] > 0) {
  actions.push(`🔴 Tag ${coverage["Untagged Documents"]} untagged documents`);
}
if (quality["Undertagged (<4 tags)"] > taggedPages.length * 0.1) {
  actions.push(`🟠 Improve ${quality["Undertagged (<4 tags)"]} undertagged documents`);
}
if (hasPriority < taggedPages.length * 0.8) {
  actions.push(`🟡 Add priority tags to ${taggedPages.length - hasPriority} documents`);
}
if (hasDomain < taggedPages.length * 0.7) {
  actions.push(`🟡 Add domain tags to ${taggedPages.length - hasDomain} documents`);
}

if (actions.length > 0) {
  actions.forEach(action => dv.paragraph(action));
} else {
  dv.paragraph("✅ **No critical actions needed. Vault tag health is excellent!**");
}
```

---

## Query 7: Recently Modified Untagged Documents (Urgent)

**Description:** New or recently updated documents missing tags (high priority for tagging).

**Urgent Tagging Queue:**
```dataview
TABLE
  file.name as "Document",
  file.mtime as "Modified",
  choice(
    file.mtime >= date(today) - dur(1 days), "🔴 Today",
    file.mtime >= date(today) - dur(7 days), "🟠 This Week",
    file.mtime >= date(today) - dur(30 days), "🟡 This Month",
    "⚪ Older"
  ) as "Urgency",
  round(file.size / 1024, 1) + " KB" as "Size",
  file.folder as "Folder"
FROM ""
WHERE (!file.tags OR length(file.tags) < 3) AND file.mtime >= date(today) - dur(30 days)
SORT file.mtime DESC
LIMIT 50
```

---

## Maintenance Workflows

### Daily Maintenance
```dataview
LIST
FROM ""
WHERE (!file.tags OR length(file.tags) < 4) AND file.mtime >= date(today) - dur(1 days)
SORT file.mtime DESC
```

### Weekly Review
```dataview
TABLE length(file.tags) as "Tags", file.mtime as "Modified"
FROM ""
WHERE file.tags AND length(file.tags) < 4
SORT file.mtime DESC
LIMIT 20
```

### Monthly Audit
Run Query 6 (Comprehensive Tag Health Report) and address action items.

---

## Performance Metrics

| Query Type | Expected Time | Notes |
|------------|---------------|-------|
| Untagged Documents | < 300ms | Simple filter |
| Undertagged Documents | < 400ms | Tag count check |
| Missing Priority | < 500ms | String search |
| Pattern Validation | < 800ms | Complex logic |
| Health Dashboard | < 1s | Comprehensive analysis |

---

## Quality Goals

- **Tag Coverage:** 100% (zero untagged documents)
- **Proper Tagging:** >95% with ≥4 tags
- **Priority Compliance:** >90% have P0-P3 tags
- **Domain Compliance:** >85% have functional domain tags
- **Pattern Consistency:** <5% inconsistency rate

---

## Testing Checklist

- [ ] Verify untagged document detection
- [ ] Test undertagged thresholds (1, 2, 3 tags)
- [ ] Confirm priority tag detection logic
- [ ] Validate domain tag coverage
- [ ] Test pattern inconsistency rules
- [ ] Verify health score calculation
- [ ] Test maintenance workflows
- [ ] Validate folder-based aggregations

---

**Query Version:** 1.0.0  
**Last Updated:** 2024-04-20  
**Tested With:** Dataview 0.5.68  
**Vault Size:** 680+ files  
**Status:** ✅ Production Ready
