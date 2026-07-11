# Query Reference: Dataview Syntax Guide

**Master Dataview Queries for Dynamic Vault Navigation** 🔎

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 12 minutes
**Audience:** All vault users
**Prerequisites:** Dataview plugin installed

---

## Table of Contents

1. [Query Basics](#query-basics)
2. [Query Syntax Guide](#query-syntax-guide)
3. [Common Query Patterns](#common-query-patterns)
4. [Customization Examples](#customization-examples)
5. [Performance Tips](#performance-tips)
6. [Troubleshooting Queries](#troubleshooting-queries)

---

## Query Basics

### What is Dataview?

**Dataview** turns your vault into a queryable database. Think of it as **SQL for Obsidian** - you can:

✅ Search and filter documents
✅ Create dynamic lists and tables
✅ Aggregate and calculate data
✅ Build dashboards that update automatically
✅ Visualize vault metadata

### Two Query Languages

**1. DQL (Dataview Query Language)** - Simple, SQL-like

```dataview
TABLE status, priority
FROM #architecture
WHERE status = "active"
SORT updated_date DESC
LIMIT 10
```

**2. DataviewJS** - Full JavaScript power

```dataviewjs
dv.table(
  ["Document", "Status"],
  dv.pages("#architecture")
    .where(p => p.status === "active")
    .sort(p => p.updated_date, 'desc')
    .limit(10)
    .map(p => [p.file.link, p.status])
);
```

**When to Use Each:**

- **DQL**: Simple queries, quick filters
- **DataviewJS**: Complex logic, custom formatting, calculations

**We recommend:** Start with DQL, use DataviewJS when needed

---

## Query Syntax Guide

### DQL Syntax

**Basic Structure:**

```
[COMMAND] [fields]
FROM [source]
WHERE [conditions]
SORT [field] [direction]
LIMIT [number]
```

#### Commands

**LIST** - Simple bullet list

```dataview
LIST
FROM #security
WHERE status = "active"
```

**Output:**
- [[Security Audit 2026]]
- [[Authentication Guide]]
- [[Encryption Standards]]

**TABLE** - Structured table with columns

```dataview
TABLE status, priority, updated_date
FROM #architecture
WHERE status = "active"
SORT updated_date DESC
```

**Output:**

| File | status | priority | updated_date |
|------|--------|----------|--------------|
| [[System Architecture]] | active | high | 2026-04-20 |
| [[API Design]] | active | medium | 2026-04-18 |

**TASK** - Show tasks from documents

```dataview
TASK
FROM #project-tracking
WHERE !completed
```

**Output:**
- [ ] Complete security audit
- [ ] Update API documentation

**CALENDAR** - Calendar view by date

```dataview
CALENDAR created_date
FROM #agent-report
```

#### FROM - Source Selection

**By Tag:**

```dataview
FROM #architecture       # Documents with tag "architecture"
FROM #security AND #audit # Multiple tags (AND logic)
FROM #security OR #privacy # Either tag (OR logic)
```

**By Folder:**

```dataview
FROM "repo-docs"              # Specific folder
FROM "repo-docs/architecture"  # Subfolder
FROM "source-docs" OR "repo-docs" # Multiple folders
```

**By Link:**

```dataview
FROM [[MOC Architecture]]    # Documents linked FROM this MOC
FROM outgoing([[README]])    # Documents linked FROM README
FROM [[README]]              # Documents linking TO README (backlinks)
```

**Combine:**

```dataview
FROM #security AND "repo-docs/security"
# Security-tagged docs in security folder
```

#### WHERE - Filter Conditions

**Comparison Operators:**

```dataview
WHERE status = "active"           # Equals
WHERE status != "draft"           # Not equals
WHERE priority = "critical"       # Exact match
WHERE created_date >= 2026-04-01  # Date comparison
WHERE word_count > 1000           # Number comparison
```

**Logical Operators:**

```dataview
WHERE status = "active" AND priority = "high"
WHERE status = "active" OR status = "review"
WHERE status = "active" AND (priority = "critical" OR priority = "high")
WHERE NOT status = "deprecated"
```

**Field Checks:**

```dataview
WHERE tags                  # Has tags field
WHERE !tags                 # No tags field
WHERE status               # Has status field
WHERE contains(tags, "security") # Tag array contains "security"
```

**String Operations:**

```dataview
WHERE contains(file.name, "AGENT")     # Filename contains "AGENT"
WHERE startswith(status, "act")        # status starts with "act"
WHERE endswith(file.name, "REPORT")    # Filename ends with "REPORT"
```

**Array Operations:**

```dataview
WHERE contains(tags, "security")              # Has tag "security"
WHERE contains(audience, "developer")         # Audience includes developer
WHERE length(tags) > 5                        # More than 5 tags
```

#### SORT - Ordering Results

**Basic Sorting:**

```dataview
SORT created_date DESC     # Newest first
SORT updated_date ASC      # Oldest first
SORT file.name             # Alphabetical (default ASC)
SORT priority, status      # Multi-column sort
```

**Direction:**
- `ASC` = Ascending (A→Z, 0→9, old→new)
- `DESC` = Descending (Z→A, 9→0, new→old)

#### LIMIT - Result Count

```dataview
LIMIT 10    # Show only first 10 results
LIMIT 50    # Show first 50
```

**Use Case:** Prevent overwhelming displays, improve performance

### DataviewJS Syntax

**Basic Structure:**

```javascript
dv.table|list|taskList(
  parameters
)
```

#### Core Functions

**dv.table()**

```dataviewjs
dv.table(
  ["Column 1", "Column 2", "Column 3"],  // Headers
  rows                                    // Data array
);
```

**Example:**

```dataviewjs
dv.table(
  ["Document", "Status", "Priority"],
  dv.pages("#architecture")
    .map(p => [p.file.link, p.status, p.priority])
);
```

**dv.list()**

```dataviewjs
dv.list(
  dv.pages("#security").file.link
);
```

**dv.taskList()**

```dataviewjs
dv.taskList(
  dv.pages("#project").file.tasks
    .where(t => !t.completed)
);
```

#### Chaining Operations

**pages() → where() → sort() → limit() → map()**

```dataviewjs
dv.pages("#architecture")           // Get all architecture docs
  .where(p => p.status === "active") // Filter to active only
  .sort(p => p.updated_date, 'desc') // Sort by date, newest first
  .limit(10)                         // Take top 10
  .map(p => [p.file.link, p.status]) // Extract fields
```

#### Field Access

```javascript
p.file.name         // Filename without extension
p.file.path         // Full file path
p.file.link         // Clickable link to file
p.file.size         // File size in bytes
p.file.ctime        // Creation time
p.file.mtime        // Modification time
p.file.tags         // All tags (frontmatter + inline)
p.file.outlinks     // Links FROM this file
p.file.inlinks      // Links TO this file (backlinks)

p.status            // Frontmatter: status
p.priority          // Frontmatter: priority
p.tags              // Frontmatter: tags
p.created_date      // Frontmatter: created_date
p.updated_date      // Frontmatter: updated_date
p.author            // Frontmatter: author
```

#### Filtering

```javascript
.where(p => p.status === "active")
.where(p => p.priority === "critical" || p.priority === "high")
.where(p => p.tags && p.tags.includes("security"))
.where(p => p.updated_date >= new Date("2026-04-01"))
.where(p => p.file.name.includes("AGENT"))
```

#### Sorting

```javascript
.sort(p => p.updated_date, 'desc')  // Newest first
.sort(p => p.priority, 'asc')       // Priority ascending
.sort(p => p.file.name)             // Alphabetical
```

#### Grouping

```javascript
dv.pages()
  .groupBy(p => p.status)
  .map(group => [group.key, group.rows.length])
```

**Output:**

| Status | Count |
|--------|-------|
| active | 147 |
| draft | 23 |
| deprecated | 8 |

---

## Common Query Patterns

### Pattern 1: Recent Updates

**Find documents updated in last N days**

**DQL:**

```dataview
TABLE updated_date, author, status
FROM ""
WHERE updated_date >= date(today) - dur(7 days)
SORT updated_date DESC
```

**DataviewJS:**

```dataviewjs
const sevenDays = new Date();
sevenDays.setDate(sevenDays.getDate() - 7);

dv.table(
  ["Document", "Updated", "Author"],
  dv.pages()
    .where(p => p.updated_date >= sevenDays)
    .sort(p => p.updated_date, 'desc')
    .map(p => [p.file.link, p.updated_date, p.author])
);
```

### Pattern 2: Filter by Multiple Tags

**Find docs with ALL specified tags (AND logic)**

**DataviewJS:**

```dataviewjs
const requiredTags = ["security", "authentication", "active"];

dv.table(
  ["Document", "Tags"],
  dv.pages()
    .where(p =>
      p.tags && requiredTags.every(tag => p.tags.includes(tag))
    )
    .map(p => [p.file.link, p.tags.join(", ")])
);
```

**Find docs with ANY specified tags (OR logic)**

```dataviewjs
const anyTags = ["security", "privacy", "compliance"];

dv.pages()
  .where(p =>
    p.tags && anyTags.some(tag => p.tags.includes(tag))
  )
```

### Pattern 3: Documents Missing Metadata

**Find docs missing required fields**

**DataviewJS:**

```dataviewjs
const requiredFields = ['type', 'area', 'status', 'audience', 'tags'];

dv.table(
  ["Document", "Missing Fields"],
  dv.pages()
    .where(p => requiredFields.some(field => !p[field]))
    .map(p => {
      const missing = requiredFields.filter(f => !p[f]);
      return [p.file.link, missing.join(", ")];
    })
);
```

### Pattern 4: Group and Count

**Count documents by status**

**DataviewJS:**

```dataviewjs
const statusGroups = dv.pages()
  .groupBy(p => p.status || "Unknown");

dv.table(
  ["Status", "Count", "Percentage"],
  statusGroups.map(g => {
    const percentage = ((g.rows.length / dv.pages().length) * 100).toFixed(1);
    return [g.key, g.rows.length, `${percentage}%`];
  })
  .sort(g => g[1], 'desc')
);
```

### Pattern 5: Stale Documents

**Find docs not updated in 90+ days**

**DataviewJS:**

```dataviewjs
const ninetyDays = new Date();
ninetyDays.setDate(ninetyDays.getDate() - 90);

dv.table(
  ["Document", "Last Updated", "Days Stale", "Author"],
  dv.pages()
    .where(p => p.updated_date && p.updated_date < ninetyDays && p.status === "active")
    .map(p => {
      const days = Math.floor((Date.now() - new Date(p.updated_date)) / (1000*60*60*24));
      return [p.file.link, p.updated_date, days, p.author || "Unknown"];
    })
    .sort(p => p[2], 'desc')
);
```

### Pattern 6: Orphan Documents

**Find docs with no backlinks**

**DataviewJS:**

```dataviewjs
dv.table(
  ["Orphan Document", "Created", "Status"],
  dv.pages()
    .where(p => {
      const backlinks = dv.app.metadataCache.getBacklinksForFile(p.file);
      return backlinks ? backlinks.count() === 0 : true;
    })
    .sort(p => p.created_date, 'desc')
    .map(p => [p.file.link, p.created_date, p.status])
);
```

### Pattern 7: Priority Matrix

**Show documents by priority and status**

**DataviewJS:**

```dataviewjs
const priorities = ["critical", "high", "medium", "low"];
const statuses = ["active", "draft", "review"];

dv.table(
  ["Priority", ...statuses],
  priorities.map(priority => {
    const row = [priority];
    statuses.forEach(status => {
      const count = dv.pages()
        .where(p => p.priority === priority && p.status === status)
        .length;
      row.push(count);
    });
    return row;
  })
);
```

**Output:**

| Priority | active | draft | review |
|----------|--------|-------|--------|
| critical | 12 | 3 | 5 |
| high | 45 | 8 | 12 |
| medium | 78 | 15 | 6 |
| low | 23 | 2 | 1 |

### Pattern 8: Tag Frequency

**Count tag usage across vault**

**DataviewJS:**

```dataviewjs
const allTags = dv.pages()
  .flatMap(p => p.tags || [])
  .groupBy(tag => tag);

dv.table(
  ["Tag", "Count", "% of Docs"],
  allTags
    .map(t => {
      const percentage = ((t.rows.length / dv.pages().length) * 100).toFixed(1);
      return [t.key, t.rows.length, `${percentage}%`];
    })
    .sort(t => t[1], 'desc')
    .limit(20)
);
```

---

## Customization Examples

### Example 1: Personal Dashboard

**Create:** `MY_DASHBOARD.md`

````markdown
# My Personal Dashboard

## My Recent Contributions
```dataviewjs
const myAuthor = "AGENT-048"; // Change to your ID
const sevenDays = new Date();
sevenDays.setDate(sevenDays.getDate() - 7);

dv.table(
  ["Document", "Status", "Updated"],
  dv.pages()
    .where(p => p.author === myAuthor && p.updated_date >= sevenDays)
    .sort(p => p.updated_date, 'desc')
    .map(p => [p.file.link, p.status, p.updated_date])
);
```

## Documents I Need to Review
```dataviewjs
dv.table(
  ["Document", "Days in Draft"],
  dv.pages()
    .where(p => p.author === myAuthor && p.status === "draft")
    .map(p => {
      const days = Math.floor((Date.now() - new Date(p.created_date)) / (1000*60*60*24));
      return [p.file.link, days];
    })
    .sort(p => p[1], 'desc')
);
```

## High Priority TODOs
```dataviewjs
dv.taskList(
  dv.pages()
    .where(p => p.priority === "critical" || p.priority === "high")
    .file.tasks
    .where(t => !t.completed)
);
```
````

### Example 2: Security Dashboard

````markdown
# Security Dashboard

## Critical Security Docs
```dataviewjs
dv.table(
  ["Document", "Updated", "Status"],
  dv.pages()
    .where(p =>
      p.tags && p.tags.includes("security") &&
      (p.priority === "critical" || p.tags.includes("security-critical"))
    )
    .sort(p => p.updated_date, 'desc')
    .map(p => [p.file.link, p.updated_date, p.status])
);
```

## Security Audits
```dataviewjs
dv.table(
  ["Audit", "Date", "Findings"],
  dv.pages()
    .where(p => p.tags && p.tags.includes("security/audit"))
    .sort(p => p.created_date, 'desc')
    .map(p => [p.file.link, p.created_date, p.findings_count || "N/A"])
);
```
````

### Example 3: Documentation Health

````markdown
# Documentation Health Report

## Metadata Completeness
```dataviewjs
const total = dv.pages().length;
const complete = dv.pages()
  .where(p => p.type && p.area && p.status && p.audience && p.tags)
  .length;

dv.paragraph(`**Completeness:** ${complete} / ${total} (${((complete/total)*100).toFixed(1)}%)`);
```

## Documents Missing Required Fields
```dataviewjs
const required = ['type', 'area', 'status', 'audience'];
dv.list(
  dv.pages()
    .where(p => required.some(f => !p[f]))
    .limit(10)
    .file.link
);
```

## Stale Documents (180+ days)
```dataviewjs
const sixMonths = new Date();
sixMonths.setDate(sixMonths.getDate() - 180);

dv.list(
  dv.pages()
    .where(p => p.updated_date < sixMonths && p.status === "active")
    .limit(10)
    .file.link
);
```
````

---

## Performance Tips

### Optimization Strategies

**1. Limit Query Scope**

**❌ Slow:**

```dataviewjs
dv.pages()  // Scans ALL files
  .where(p => p.tags && p.tags.includes("security"))
```

**✅ Fast:**

```dataviewjs
dv.pages("#security")  // Scans only tagged files
```

**Speed improvement:** 5-10x faster

**2. Add Result Limits**

```dataviewjs
dv.pages("#architecture")
  .sort(p => p.updated_date, 'desc')
  .limit(20)  // Don't load more than needed
```

**3. Cache Heavy Queries**

Instead of embedding complex queries in multiple files:

1. Create one dashboard note
2. Run all queries there
3. Reference results via links

**4. Reduce Complexity**

**❌ Complex:**

```dataviewjs
dv.pages()
  .where(p => {
    const backlinks = dv.app.metadataCache.getBacklinksForFile(p.file);
    const outlinks = p.file.outlinks;
    const ratio = outlinks.length / backlinks.count();
    return ratio > 2 && p.tags && p.tags.length > 5;
  })
```

**✅ Simpler:**

```dataviewjs
dv.pages("#tag")
  .where(p => p.outlink_count > 10)
  .limit(50)
```

**5. Use WHERE Early**

```dataviewjs
dv.pages()
  .where(p => p.status === "active")  // Filter first
  .sort(p => p.updated_date, 'desc')  // Then sort
  .map(p => [p.file.link, p.status])  // Then format
```

**Order matters:** Filter → Sort → Map

### Performance Benchmarks

| Query Type | Expected Time | Action if Slower |
|------------|---------------|------------------|
| Simple tag filter | <50ms | Limit scope with tags |
| Table with 10 rows | <100ms | Add .limit(10) |
| Table with 100 rows | <200ms | Paginate results |
| Grouped aggregation | <300ms | Cache in dashboard |
| Backlink analysis | <500ms | Limit to specific folder |

---

## Troubleshooting Queries

### Problem: "Query returns no results"

**Check:**

1. **Field names match frontmatter**
   ```javascript
   // Frontmatter: created_date
   .where(p => p.created_date)  // ✅ Match

   // Wrong
   .where(p => p.createdDate)   // ❌ Doesn't exist
   ```

2. **Tag syntax correct**
   ```javascript
   dv.pages("#security")        // ✅ With #
   dv.pages("security")         // ❌ Wrong
   ```

3. **Date comparison format**
   ```javascript
   // ✅ Correct
   p.updated_date >= new Date("2026-04-01")

   // ❌ Wrong
   p.updated_date >= "2026-04-01"
   ```

### Problem: "Error in query"

**Common Errors:**

**Syntax Error:**

```javascript
// ❌ Missing comma
dv.table(
  ["Col1" "Col2"]  // Error!
)

// ✅ Correct
dv.table(
  ["Col1", "Col2"]
)
```

**Field Access Error:**

```javascript
// ❌ Accessing undefined
.map(p => [p.file.link, p.nonexistent_field])

// ✅ Safe access
.map(p => [p.file.link, p.nonexistent_field || "N/A"])
```

**Type Error:**

```javascript
// ❌ Calling wrong type
.where(p => p.tags.includes("security"))  // Error if tags is undefined

// ✅ Check first
.where(p => p.tags && p.tags.includes("security"))
```

### Problem: "Query is very slow"

**Debugging:**

1. **Check query scope**
   ```javascript
   // How many files?
   dv.paragraph(dv.pages().length)
   ```

2. **Time the query**
   ```javascript
   const start = Date.now();
   const results = dv.pages("#tag");
   dv.paragraph(`Query took ${Date.now() - start}ms`);
   ```

3. **Simplify incrementally**
   ```javascript
   // Start simple
   dv.pages("#tag")

   // Add filtering
   dv.pages("#tag").where(p => p.status === "active")

   // Add sorting
   // ... etc
   ```

### Problem: "Results not updating"

**Solutions:**

1. **Refresh Dataview**
   ```
   Ctrl+P → "Dataview: Refresh all views"
   ```

2. **Check refresh interval**
   ```
   Settings → Dataview → Refresh interval: 2500ms
   ```

3. **Restart Obsidian**
   ```
   Complete plugin reload
   ```

---

## Summary

### Query Cheat Sheet

```javascript
// Basic structure
dv.pages([source])        // Get pages
  .where(p => [condition]) // Filter
  .sort(p => [field], 'desc/asc') // Sort
  .limit(N)               // Limit results
  .map(p => [fields])     // Format output

// Common filters
p.status === "active"
p.tags && p.tags.includes("security")
p.updated_date >= new Date("2026-04-01")
p.priority === "critical" || p.priority === "high"

// Common outputs
dv.list(array)
dv.table(headers, rows)
dv.taskList(tasks)
```

---

**Next Steps:**

- **Copy** 3 queries from this guide
- **Modify** them for your needs
- **Create** your own dashboard
- **Explore** [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md) for 25+ examples

**Related Documentation:**

- [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md) - 25+ ready-to-use queries
- [SEARCH_GUIDE.md](SEARCH_GUIDE.md) - Search techniques
- [PLUGIN_REFERENCE.md](PLUGIN_REFERENCE.md) - Dataview configuration

---

**Document Metadata:**

```yaml
---
type: reference
area: documentation
component: vault
status: active
audience: [user, developer, contributor]
priority: high
tags: [dataview, queries, reference, syntax, guide]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 3200
dependencies:
  - DATAVIEW_QUERY_LIBRARY.md
  - PLUGIN_REFERENCE.md
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
