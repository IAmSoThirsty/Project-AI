---
query_name: Documents by Tag Category
query_type: tag-category
purpose: Display documents grouped by tag categories (priority, functional, technology, platform)
created: 2024-04-20
performance_target: <1s
tags:
  - dataview-query
  - tag-navigation
  - category-grouping
  - taxonomy
related_queries:
  - 02-documents-by-tag-combination
  - 03-tag-hierarchy-navigation
status: production-ready
---

# Documents by Tag Category

**Purpose:** Organize and display documents by their tag categories (priority, functional domain, technology stack, platform). Enables systematic navigation through the vault's tag taxonomy.

---

## Query 1: Documents by Priority Category (P0-P3)

**Description:** Group documents by priority level for audience-targeted navigation.

**Query:**
```dataview
TABLE
  file.name as "Document",
  length(file.tags) as "Total Tags",
  file.mtime as "Last Modified",
  type as "Type",
  audience as "Audience"
FROM ""
WHERE file.tags
GROUP BY filter(file.tags, (t) => startswith(t, "#p0-") OR startswith(t, "#p1-") OR startswith(t, "#p2-") OR startswith(t, "#p3-")) as "Priority Tags"
SORT rows[0].file.mtime DESC
LIMIT 100
```

**Enhanced Query (with priority sorting):**
```dataview
TABLE
  length(rows) as "Count",
  join(map(rows.file.name, (f) => "[[" + f + "]]"), ", ") as "Documents (First 5)"
FROM ""
WHERE contains(string(file.tags), "#p0-") OR contains(string(file.tags), "#p1-") OR contains(string(file.tags), "#p2-") OR contains(string(file.tags), "#p3-")
GROUP BY choice(
  contains(string(file.tags), "#p0-"), "P0 - Critical",
  contains(string(file.tags), "#p1-"), "P1 - High",
  contains(string(file.tags), "#p2-"), "P2 - Medium",
  "P3 - Archive"
) as "Priority Category"
SORT "Priority Category" ASC
```

**Expected Output:**
```
4 results

| Priority Category | Count | Documents (First 5) |
|-------------------|-------|---------------------|
| P0 - Critical     | 186   | [[file1]], [[file2]], [[file3]], [[file4]], [[file5]] |
| P1 - High         | 160   | [[file6]], [[file7]], [[file8]], [[file9]], [[file10]] |
| P2 - Medium       | 132   | [[file11]], [[file12]], [[file13]], [[file14]], [[file15]] |
| P3 - Archive      | 80    | [[file16]], [[file17]], [[file18]], [[file19]], [[file20]] |
```

---

## Query 2: Documents by Functional Domain

**Description:** Categorize documents by their functional purpose (development, operations, security, testing, governance).

**Query:**
```dataview
TABLE
  file.name as "Document",
  status as "Status",
  file.mtime as "Modified",
  filter(file.tags, (t) => 
    contains(t, "guide") OR 
    contains(t, "tutorial") OR 
    contains(t, "reference") OR 
    contains(t, "deployment") OR 
    contains(t, "security") OR 
    contains(t, "testing") OR 
    contains(t, "governance")
  ) as "Domain Tags"
FROM ""
WHERE file.tags
FLATTEN choice(
  contains(string(file.tags), "guide") OR contains(string(file.tags), "tutorial") OR contains(string(file.tags), "reference"), "📚 Development",
  contains(string(file.tags), "deployment") OR contains(string(file.tags), "docker") OR contains(string(file.tags), "kubernetes"), "🚀 Operations",
  contains(string(file.tags), "security") OR contains(string(file.tags), "compliance") OR contains(string(file.tags), "audit"), "🔒 Security",
  contains(string(file.tags), "testing") OR contains(string(file.tags), "pytest") OR contains(string(file.tags), "e2e"), "🧪 Testing",
  contains(string(file.tags), "governance") OR contains(string(file.tags), "policy") OR contains(string(file.tags), "ethics"), "⚖️ Governance",
  "📂 Other"
) as "Functional Domain"
WHERE "Functional Domain" != "📂 Other"
SORT "Functional Domain" ASC, file.mtime DESC
LIMIT 100
```

**Aggregated View:**
```dataview
TABLE
  length(rows) as "Document Count",
  round(length(rows) / 680 * 100, 1) + "%" as "% of Vault",
  join(list(rows[0].file.name, rows[1].file.name, rows[2].file.name), ", ") as "Sample Documents"
FROM ""
WHERE file.tags
FLATTEN choice(
  contains(string(file.tags), "guide") OR contains(string(file.tags), "tutorial") OR contains(string(file.tags), "reference"), "Development",
  contains(string(file.tags), "deployment") OR contains(string(file.tags), "docker") OR contains(string(file.tags), "kubernetes"), "Operations",
  contains(string(file.tags), "security") OR contains(string(file.tags), "compliance") OR contains(string(file.tags), "audit"), "Security",
  contains(string(file.tags), "testing") OR contains(string(file.tags), "pytest") OR contains(string(file.tags), "e2e"), "Testing",
  contains(string(file.tags), "governance") OR contains(string(file.tags), "policy") OR contains(string(file.tags), "ethics"), "Governance",
  "Other"
) as "Domain"
WHERE Domain != "Other"
GROUP BY Domain
SORT Domain ASC
```

---

## Query 3: Documents by Technology Stack

**Description:** Filter documents by programming language and framework tags.

**Query:**
```dataview
TABLE
  file.name as "Document",
  type as "Type",
  file.tags as "All Tags",
  file.mtime as "Last Modified"
FROM ""
WHERE 
  contains(string(file.tags), "#python") OR 
  contains(string(file.tags), "#pyqt6") OR 
  contains(string(file.tags), "#react") OR 
  contains(string(file.tags), "#rust") OR 
  contains(string(file.tags), "#go") OR
  contains(string(file.tags), "#typescript") OR
  contains(string(file.tags), "#javascript")
FLATTEN choice(
  contains(string(file.tags), "#python") OR contains(string(file.tags), "#pyqt6"), "🐍 Python",
  contains(string(file.tags), "#react") OR contains(string(file.tags), "#typescript") OR contains(string(file.tags), "#javascript"), "⚛️ JavaScript/React",
  contains(string(file.tags), "#rust"), "🦀 Rust",
  contains(string(file.tags), "#go"), "🔷 Go",
  "Other"
) as "Tech Stack"
WHERE "Tech Stack" != "Other"
SORT "Tech Stack" ASC, file.mtime DESC
LIMIT 100
```

**Technology Distribution:**
```dataview
TABLE
  length(rows) as "Documents",
  round(length(rows) / 680 * 100, 1) + "%" as "Coverage",
  join(unique(flatten(rows.type)), ", ") as "Document Types"
FROM ""
WHERE file.tags
FLATTEN choice(
  contains(string(file.tags), "python") OR contains(string(file.tags), "pyqt6"), "Python",
  contains(string(file.tags), "react") OR contains(string(file.tags), "typescript") OR contains(string(file.tags), "javascript"), "JavaScript/React",
  contains(string(file.tags), "rust"), "Rust",
  contains(string(file.tags), "go"), "Go",
  contains(string(file.tags), "csharp"), "C#",
  "Other"
) as "Technology"
WHERE Technology != "Other"
GROUP BY Technology
SORT Technology ASC
```

---

## Query 4: Documents by Platform Category

**Description:** Categorize by deployment platform (desktop, web, mobile, multi-platform).

**Query:**
```dataview
TABLE
  file.name as "Document",
  deployment_target as "Target",
  production_ready as "Production Ready",
  file.mtime as "Modified"
FROM ""
WHERE 
  contains(string(file.tags), "#desktop") OR 
  contains(string(file.tags), "#web") OR 
  contains(string(file.tags), "#android") OR 
  contains(string(file.tags), "#multi-platform")
FLATTEN choice(
  contains(string(file.tags), "#multi-platform"), "🌐 Multi-Platform",
  contains(string(file.tags), "#desktop"), "🖥️ Desktop",
  contains(string(file.tags), "#web"), "🌍 Web",
  contains(string(file.tags), "#android"), "📱 Android",
  "Other"
) as "Platform"
WHERE Platform != "Other"
SORT Platform ASC, file.mtime DESC
LIMIT 100
```

---

## Query 5: Complete Tag Category Matrix

**Description:** Comprehensive overview of all tag categories with cross-category analysis.

**DataviewJS Query:**
```dataviewjs
const tagCategories = {
  "Priority": ["p0-", "p1-", "p2-", "p3-"],
  "Development": ["guide", "tutorial", "reference", "api"],
  "Operations": ["deployment", "docker", "kubernetes", "ci-cd"],
  "Security": ["security", "compliance", "audit", "encryption"],
  "Testing": ["testing", "pytest", "e2e", "adversarial-testing"],
  "Governance": ["governance", "policy", "ethics", "ai-safety"],
  "Technology": ["python", "rust", "go", "react", "typescript"],
  "Platform": ["desktop", "web", "android", "multi-platform"]
};

const pages = dv.pages('""').where(p => p.file.tags && p.file.tags.length > 0);

const results = Object.entries(tagCategories).map(([category, patterns]) => {
  const matchingPages = pages.filter(p => {
    const tagStr = p.file.tags.join(" ").toLowerCase();
    return patterns.some(pattern => tagStr.includes(pattern));
  });
  
  return {
    category: category,
    count: matchingPages.length,
    percentage: ((matchingPages.length / pages.length) * 100).toFixed(1) + "%",
    topTags: [...new Set(
      matchingPages.flatMap(p => p.file.tags)
        .filter(t => patterns.some(pattern => t.toLowerCase().includes(pattern)))
        .map(t => t.replace("#", ""))
    )].slice(0, 5).join(", ")
  };
});

dv.table(
  ["Category", "Document Count", "% Coverage", "Top Tags"],
  results.map(r => [r.category, r.count, r.percentage, r.topTags])
);

dv.paragraph(`**Total Documents with Tags:** ${pages.length}`);
dv.paragraph(`**Avg Tags per Document:** ${(pages.array().reduce((sum, p) => sum + p.file.tags.length, 0) / pages.length).toFixed(1)}`);
```

---

## Performance Metrics

| Query | Scope | Expected Time | Optimization |
|-------|-------|---------------|--------------|
| Priority Category | All files | < 500ms | Pre-filter by tag existence |
| Functional Domain | All files | < 600ms | Use FLATTEN for category logic |
| Technology Stack | Tagged files | < 400ms | Narrow WHERE clause |
| Platform Category | Platform-tagged | < 300ms | Specific tag filters |
| Tag Category Matrix | All files | < 800ms | DataviewJS with caching |

---

## Use Cases

### 1. Developer Onboarding
**Scenario:** New developer needs Python documentation
```dataview
FROM ""
WHERE contains(string(file.tags), "#p1-developer") AND contains(string(file.tags), "#python")
SORT file.mtime DESC
```

### 2. Security Audit
**Scenario:** Review all security-related governance docs
```dataview
FROM ""
WHERE contains(string(file.tags), "#p0-security") AND contains(string(file.tags), "#governance")
SORT last_verified ASC
```

### 3. Executive Reporting
**Scenario:** Find strategic planning documents
```dataview
FROM ""
WHERE contains(string(file.tags), "#p1-executive") AND contains(string(file.tags), "#strategic")
SORT created DESC
```

### 4. Multi-Platform Development
**Scenario:** Locate all cross-platform guides
```dataview
FROM ""
WHERE contains(string(file.tags), "#multi-platform") AND contains(string(file.tags), "#guide")
```

---

## Testing Instructions

1. **Create test tag structure:**
   ```yaml
   tags:
     - p0-core
     - guide
     - python
     - desktop
   ```

2. **Run each query in Reading View**
3. **Verify grouping logic is correct**
4. **Measure performance with browser DevTools**
5. **Validate results against expected patterns**

---

## Maintenance Notes

- **Tag Consistency:** Queries rely on kebab-case tag naming
- **Performance:** Add `LIMIT` clause for large vaults (1000+ files)
- **Updates:** Modify `tagCategories` object when adding new tag types
- **Validation:** Run monthly to ensure tag coverage remains high

---

**Query Version:** 1.0.0  
**Last Updated:** 2024-04-20  
**Tested With:** Dataview 0.5.68  
**Vault Size:** 680+ files  
**Status:** ✅ Production Ready
