# Dataview Performance Guide

**Version:** 1.0.0
**Created:** 2026-04-20
**Author:** AGENT-038 (Dataview Query Library Specialist)
**Purpose:** Comprehensive performance optimization guide for Dataview queries

---

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Query Optimization Principles](#query-optimization-principles)
3. [Common Performance Bottlenecks](#common-performance-bottlenecks)
4. [Optimization Techniques](#optimization-techniques)
5. [Indexing Strategies](#indexing-strategies)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Monitoring & Profiling](#monitoring--profiling)
8. [Best Practices](#best-practices)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Performance Overview

### Target Performance Metrics

| Vault Size | Query Type | Target Time | Max Acceptable | Action Required If |
|------------|-----------|-------------|----------------|-------------------|
| <1,000 files | Simple filter | <30ms | <100ms | >100ms |
| <1,000 files | Complex query | <100ms | <300ms | >300ms |
| 1,000-5,000 files | Simple filter | <50ms | <150ms | >150ms |
| 1,000-5,000 files | Complex query | <200ms | <500ms | >500ms |
| >5,000 files | Simple filter | <100ms | <300ms | >300ms |
| >5,000 files | Complex query | <400ms | <1000ms | >1000ms |

### Query Type Categories

**Simple Filter:**
- Single `where()` clause
- No nested loops
- Direct field access
- Example: `dv.pages().where(p => p.status === "active")`

**Complex Query:**
- Multiple filters
- Array operations
- Link analysis
- Graph algorithms
- Example: Dependency chain analysis, circular reference detection

**Very Complex Query:**
- Full vault scans
- Recursive algorithms
- Cross-reference matrices
- Multi-dimensional aggregations

---

## Query Optimization Principles

### 1. Filter Early, Filter Often

**The Golden Rule:** Reduce the dataset as early as possible in the query chain.

**Bad Example:**
```javascript
// Processes ALL files, then filters, then maps
const pages = dv.pages()
    .map(p => ({
        ...p,
        age: calculateAge(p.created_date),
        score: calculateScore(p)
    }))
    .where(p => p.status === "active" && p.category === "security")
    .sort(p => p.score, 'desc');
```

**Good Example:**
```javascript
// Filters FIRST, processes only matching files
const pages = dv.pages()
    .where(p => p.status === "active" && p.category === "security")
    .map(p => ({
        ...p,
        age: calculateAge(p.created_date),
        score: calculateScore(p)
    }))
    .sort(p => p.score, 'desc');
```

**Performance Impact:** 10x-100x faster for large vaults

---

### 2. Avoid Nested Loops

**Bad Example (O(n²) complexity):**
```javascript
// For each page, searches ALL pages again
for (const page of allPages) {
    const relatedPages = allPages.where(p => p.id === page.related_id);
    // ...
}
```

**Good Example (O(n) complexity):**
```javascript
// Build lookup map once: O(n)
const pageMap = new Map(allPages.map(p => [p.id, p]));

// Lookup: O(1) per item
for (const page of allPages) {
    const relatedPage = pageMap.get(page.related_id);
    // ...
}
```

**Performance Impact:** 100x-1000x faster for >1000 files

---

### 3. Use Lazy Evaluation

**Bad Example:**
```javascript
// Materializes entire array unnecessarily
const activeDocs = dv.pages().where(p => p.status === "active");
const hasActiveDocs = activeDocs.length > 0;
```

**Good Example:**
```javascript
// Stops after finding first match
const hasActiveDocs = dv.pages()
    .where(p => p.status === "active")
    .limit(1).length > 0;
```

**Performance Impact:** 10x faster when checking existence

---

### 4. Cache Expensive Computations

**Bad Example:**
```javascript
// Date parsing happens on EVERY table render
dv.table(
    ["Doc", "Age"],
    pages.map(p => [
        p.file.link,
        Math.floor((Date.now() - new Date(p.date).getTime()) / (1000*60*60*24))
    ])
);
```

**Good Example:**
```javascript
// Parse dates once, reuse value
const pagesWithAge = pages.map(p => ({
    page: p,
    age: Math.floor((Date.now() - new Date(p.date).getTime()) / (1000*60*60*24))
}));

dv.table(
    ["Doc", "Age"],
    pagesWithAge.map(item => [item.page.file.link, item.age])
);
```

**Performance Impact:** 2x-5x faster for date/math-heavy queries

---

### 5. Limit Result Sets

**Always use `.limit()` for potentially large result sets:**

```javascript
// Good: Never render more than 50 rows
const recentDocs = dv.pages()
    .where(p => p.status === "active")
    .sort(p => p.updated_date, 'desc')
    .limit(50);

dv.table(["Doc", "Updated"], recentDocs.map(p => [p.file.link, p.updated_date]));
```

**Performance Impact:** Prevents browser lag when rendering large tables

---

## Common Performance Bottlenecks

### Bottleneck 1: Full Vault Scans

**Problem:**
```javascript
// Scans EVERY file in vault, even templates and archived docs
const docs = dv.pages();
```

**Solution:**
```javascript
// Use source path filtering
const docs = dv.pages('"repo-docs"'); // Only docs in repo-docs folder

// Or exclude paths
const docs = dv.pages()
    .where(p => !p.file.path.includes("_templates") &&
                !p.file.path.includes("archive"));
```

**Performance Gain:** 2x-10x depending on vault structure

---

### Bottleneck 2: Unindexed Field Access

**Problem:**
```javascript
// Accesses nested fields repeatedly
for (const page of pages) {
    const name = page.author?.name || page.author || "Unknown";
    // Used 100 times in loop
}
```

**Solution:**
```javascript
// Extract once
const pagesWithAuthor = pages.map(p => ({
    page: p,
    authorName: p.author?.name || p.author || "Unknown"
}));
```

**Performance Gain:** 3x-5x for deeply nested objects

---

### Bottleneck 3: Inefficient Link Analysis

**Problem:**
```javascript
// Checks every page's outlinks for every page (O(n²))
for (const page1 of allPages) {
    for (const page2 of allPages) {
        if (page2.file.outlinks.some(link => link.path === page1.file.path)) {
            // Found backlink
        }
    }
}
```

**Solution:**
```javascript
// Build backlink index once (O(n))
const backlinkMap = new Map();
for (const page of allPages) {
    for (const link of (page.file.outlinks || [])) {
        if (!backlinkMap.has(link.path)) {
            backlinkMap.set(link.path, []);
        }
        backlinkMap.get(link.path).push(page);
    }
}

// Lookup backlinks (O(1))
const backlinks = backlinkMap.get(targetPage.file.path) || [];
```

**Performance Gain:** 100x-500x for link-heavy vaults

---

### Bottleneck 4: Array Operations in Loops

**Problem:**
```javascript
// Creates new array on every iteration
for (const page of pages) {
    const tags = (page.tags || []).filter(t => t.includes("security"));
    // ...
}
```

**Solution:**
```javascript
// Pre-process arrays
const pagesWithFilteredTags = pages.map(p => ({
    page: p,
    securityTags: (p.tags || []).filter(t => t.includes("security"))
}));

for (const item of pagesWithFilteredTags) {
    // Use item.securityTags directly
}
```

**Performance Gain:** 2x-4x for array-heavy operations

---

## Optimization Techniques

### Technique 1: Progressive Disclosure

Show summary first, details on demand:

```javascript
// Group pages by category
const groups = dv.pages().groupBy(p => p.category);

for (const group of groups) {
    dv.header(3, `${group.key} (${group.rows.length})`);

    if (group.rows.length <= 10) {
        // Show all if small
        dv.table(["Doc"], group.rows.map(p => [p.file.link]));
    } else {
        // Show summary if large
        dv.paragraph(`${group.rows.length} documents. Top 5:`);
        dv.list(group.rows.slice(0, 5).map(p => p.file.link));
    }
}
```

**Benefit:** Faster rendering, better UX for large result sets

---

### Technique 2: Pagination

```javascript
const PAGE_SIZE = 20;
const currentPage = 1; // Could be dynamic

const allResults = dv.pages()
    .where(p => p.status === "active")
    .sort(p => p.updated_date, 'desc');

const totalPages = Math.ceil(allResults.length / PAGE_SIZE);
const pageResults = allResults.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
);

dv.table(["Doc"], pageResults.map(p => [p.file.link]));
dv.paragraph(`Page ${currentPage} of ${totalPages} (${allResults.length} total)`);
```

**Benefit:** Consistent performance regardless of result count

---

### Technique 3: Conditional Computation

Only compute what's needed:

```javascript
const showDetailedStats = false; // Toggle for performance

const pages = dv.pages().where(p => p.status === "active");

if (showDetailedStats) {
    // Expensive computations
    const stats = computeDetailedStatistics(pages);
    dv.table(["Metric", "Value"], Object.entries(stats));
} else {
    // Quick summary only
    dv.paragraph(`${pages.length} active documents`);
}
```

**Benefit:** Users choose between speed and detail

---

### Technique 4: Memoization

Cache results of expensive pure functions:

```javascript
const memoCache = new Map();

function expensiveCalculation(input) {
    if (memoCache.has(input)) {
        return memoCache.get(input);
    }

    const result = /* expensive computation */;
    memoCache.set(input, result);
    return result;
}
```

**Benefit:** Eliminates redundant calculations

---

## Indexing Strategies

### Strategy 1: Frontmatter Field Indexing

**Fast Access Fields (Always in Frontmatter):**
- `status` - Used in most filters
- `category` - Common grouping field
- `created_date` / `updated_date` - Sorting and filtering
- `tags` - Multi-dimensional filtering
- `type` - Document classification

**Slow Access (Avoid):**
- Computed fields (recalculated on every query)
- Deeply nested objects (multiple property accesses)
- Fields requiring string parsing

---

### Strategy 2: Pre-computed Values

Add computed values to frontmatter during document creation:

```yaml
---
title: Security Audit 2026
age_days: 45          # Pre-computed
priority_score: 85    # Pre-computed
is_stale: false       # Pre-computed boolean
---
```

**Query becomes:**
```javascript
// Fast: Direct field access
const staleDocs = dv.pages().where(p => p.is_stale === true);

// Instead of slow: Runtime calculation
const staleDocs = dv.pages().where(p => {
    const age = (Date.now() - new Date(p.updated_date)) / (1000*60*60*24);
    return age > 90;
});
```

**Performance Gain:** 5x-10x for frequently used filters

---

### Strategy 3: Tag Hierarchy

Use hierarchical tags for efficient filtering:

```yaml
tags:
  - security
  - security/audit
  - security/audit/soc2
```

**Query:**
```javascript
// Fast: Single string check
const securityDocs = dv.pages().where(p =>
    p.tags && p.tags.some(t => t.startsWith("security"))
);

// Fast: Specific sub-category
const soc2Audits = dv.pages().where(p =>
    p.tags && p.tags.includes("security/audit/soc2")
);
```

---

## Performance Benchmarks

### Benchmark Suite

Run these queries to measure your vault's performance:

#### Benchmark 1: Simple Filter
```javascript
console.time("Simple Filter");
const result = dv.pages().where(p => p.status === "active").length;
console.timeEnd("Simple Filter");
// Target: <50ms for <5000 files
```

#### Benchmark 2: Multi-Field Filter
```javascript
console.time("Multi-Field Filter");
const result = dv.pages()
    .where(p => p.status === "active" &&
                p.category === "security" &&
                p.tags && p.tags.includes("audit"))
    .length;
console.timeEnd("Multi-Field Filter");
// Target: <100ms for <5000 files
```

#### Benchmark 3: Link Analysis
```javascript
console.time("Link Analysis");
const backlinkMap = new Map();
for (const page of dv.pages()) {
    for (const link of (page.file.outlinks || [])) {
        if (!backlinkMap.has(link.path)) {
            backlinkMap.set(link.path, []);
        }
        backlinkMap.get(link.path).push(page);
    }
}
console.timeEnd("Link Analysis");
// Target: <300ms for <5000 files
```

#### Benchmark 4: Complex Aggregation
```javascript
console.time("Complex Aggregation");
const groups = dv.pages()
    .groupBy(p => p.category)
    .map(g => ({
        category: g.key,
        count: g.rows.length,
        avgAge: g.rows.reduce((sum, p) => {
            const age = p.created_date ?
                (Date.now() - new Date(p.created_date)) / (1000*60*60*24) : 0;
            return sum + age;
        }, 0) / g.rows.length
    }));
console.timeEnd("Complex Aggregation");
// Target: <200ms for <5000 files
```

---

## Monitoring & Profiling

### Browser DevTools Profiling

1. Open Chrome/Edge DevTools (F12)
2. Go to Performance tab
3. Click Record
4. Refresh note with Dataview query
5. Stop recording
6. Analyze flame graph for bottlenecks

**Look for:**
- Long-running function calls (>100ms)
- Repeated function calls (loops)
- Memory spikes (large array operations)

---

### Console Timing

Wrap query sections with timing:

```javascript
console.time("Query Total");

console.time("Data Fetch");
const pages = dv.pages().where(p => p.status === "active");
console.timeEnd("Data Fetch");

console.time("Processing");
const processed = pages.map(p => ({
    page: p,
    age: calculateAge(p.created_date)
}));
console.timeEnd("Processing");

console.time("Rendering");
dv.table(["Doc", "Age"], processed.map(p => [p.page.file.link, p.age]));
console.timeEnd("Rendering");

console.timeEnd("Query Total");
```

**Output:**
```
Data Fetch: 45ms
Processing: 120ms
Rendering: 80ms
Query Total: 245ms
```

---

### Memory Profiling

Check memory usage for large queries:

```javascript
const before = performance.memory.usedJSHeapSize;

// Your query here
const result = heavyQuery();

const after = performance.memory.usedJSHeapSize;
const memoryUsed = (after - before) / (1024 * 1024); // MB

console.log(`Memory used: ${memoryUsed.toFixed(2)} MB`);
```

**Warning Signs:**
- >50 MB for simple queries
- >200 MB for complex queries
- Memory not released after query (check with GC)

---

## Best Practices

### 1. Query Design Checklist

Before writing a query, ask:

- [ ] Can I filter the source (`dv.pages('"folder"')`) instead of all pages?
- [ ] Are my filters ordered from most to least restrictive?
- [ ] Am I using `.limit()` to cap result size?
- [ ] Are there any O(n²) nested loops I can optimize?
- [ ] Can I cache computed values instead of recalculating?
- [ ] Am I using Maps/Sets for O(1) lookups instead of arrays?
- [ ] Have I tested with a large dataset (1000+ files)?

---

### 2. Code Organization

**Bad:**
```javascript
// Everything in one giant query
const result = dv.pages().where(p => /* 50 lines of logic */);
```

**Good:**
```javascript
// Break into logical functions
function isActiveSecurityDoc(page) {
    return page.status === "active" &&
           page.category === "security";
}

function hasRecentUpdate(page, days = 90) {
    if (!page.updated_date) return false;
    const age = (Date.now() - new Date(page.updated_date)) / (1000*60*60*24);
    return age <= days;
}

const result = dv.pages()
    .where(isActiveSecurityDoc)
    .where(p => hasRecentUpdate(p, 30));
```

**Benefits:**
- Reusable logic
- Easier testing
- Better readability
- Simpler profiling

---

### 3. Error Handling

Always handle missing/malformed data:

```javascript
const safePages = dv.pages().map(p => ({
    link: p.file?.link || "Unknown",
    status: p.status || "no-status",
    date: p.updated_date || p.created_date || "no-date",
    tags: Array.isArray(p.tags) ? p.tags : [],
    author: p.author?.name || p.author || "Unknown"
}));

// Now safe to use without null checks
dv.table(["Doc", "Status"], safePages.map(p => [p.link, p.status]));
```

---

### 4. Documentation

Add comments for complex queries:

```javascript
// Find documents that are:
// 1. Active status
// 2. Not updated in 90 days
// 3. Tagged as high priority
// 4. Have no assigned owner
const staleCriticalDocs = dv.pages()
    .where(p => p.status === "active")                          // Active only
    .where(p => {                                               // Stale (90+ days)
        if (!p.updated_date) return true;
        const age = (Date.now() - new Date(p.updated_date)) / (1000*60*60*24);
        return age > 90;
    })
    .where(p => p.priority === "high" || p.priority === "critical") // High priority
    .where(p => !p.owner && !p.author);                         // No owner

// Result: Documents needing urgent assignment
```

---

## Troubleshooting Guide

### Problem: Query Takes >1 Second

**Diagnosis Steps:**

1. **Add timing to isolate bottleneck:**
   ```javascript
   console.time("Data Fetch");
   const pages = dv.pages();
   console.timeEnd("Data Fetch");

   console.time("Filter");
   const filtered = pages.where(/* conditions */);
   console.timeEnd("Filter");

   console.time("Processing");
   const processed = filtered.map(/* transform */);
   console.timeEnd("Processing");
   ```

2. **Check dataset size:**
   ```javascript
   console.log(`Processing ${dv.pages().length} files`);
   ```

3. **Look for nested loops:**
   ```javascript
   // Bad: O(n²)
   for (const page1 of pages) {
       for (const page2 of pages) { /* ... */ }
   }
   ```

4. **Check for repeated calculations:**
   ```javascript
   // Bad: Date parsing in every iteration
   pages.map(p => new Date(p.date))
   ```

**Solutions:**
- Add early filters
- Use Maps for lookups
- Cache calculations
- Limit result set

---

### Problem: Query Returns Empty Results

**Diagnosis Steps:**

1. **Check field names (case-sensitive):**
   ```javascript
   console.log(dv.pages().first()); // Inspect actual field names
   ```

2. **Verify data types:**
   ```javascript
   const page = dv.pages().first();
   console.log(typeof page.status); // string, undefined, object?
   ```

3. **Test filters individually:**
   ```javascript
   console.log("All pages:", dv.pages().length);
   console.log("Status=active:", dv.pages().where(p => p.status === "active").length);
   console.log("Category=security:", dv.pages().where(p => p.category === "security").length);
   ```

4. **Check for null/undefined:**
   ```javascript
   // Add null checks
   .where(p => p.field !== undefined && p.field !== null)
   ```

---

### Problem: Browser Freezes During Query

**Diagnosis:**
- Query is too complex or dataset too large
- Infinite loop in recursive algorithm
- Memory exhaustion

**Solutions:**

1. **Add pagination:**
   ```javascript
   .limit(50) // Cap results
   ```

2. **Use setTimeout for chunking:**
   ```javascript
   async function processInChunks(pages, chunkSize = 100) {
       for (let i = 0; i < pages.length; i += chunkSize) {
           const chunk = pages.slice(i, i + chunkSize);
           await processChunk(chunk);
           await new Promise(resolve => setTimeout(resolve, 10)); // Yield to browser
       }
   }
   ```

3. **Add depth limits to recursion:**
   ```javascript
   function traverse(node, depth = 0, maxDepth = 10) {
       if (depth >= maxDepth) return; // Prevent infinite recursion
       // ...
   }
   ```

---

### Problem: Stale Results (Not Updating)

**Cause:** Dataview caches results

**Solutions:**

1. **Force refresh:** Close and reopen note
2. **Use dynamic date:** `Date.now()` in queries forces recalculation
3. **Check auto-refresh settings:** Dataview plugin settings

---

## Performance Optimization Workflow

1. **Measure Baseline:**
   - Run query with `console.time()`
   - Record time for current vault size

2. **Identify Bottleneck:**
   - Use browser DevTools profiler
   - Add timing to query sections
   - Check for O(n²) algorithms

3. **Apply Optimization:**
   - Start with highest-impact fix (usually filtering)
   - Apply one optimization at a time
   - Re-measure after each change

4. **Validate Results:**
   - Ensure query returns same data
   - Test with edge cases (empty arrays, missing fields)
   - Test with larger dataset

5. **Document:**
   - Add comments explaining optimizations
   - Record performance metrics
   - Note any trade-offs

---

## Conclusion

**Key Takeaways:**

1. **Filter early and often** - Reduce dataset before expensive operations
2. **Avoid nested loops** - Use Maps/Sets for O(1) lookups
3. **Cache computations** - Don't recalculate same values
4. **Limit results** - Use `.limit()` to cap output
5. **Profile regularly** - Measure before and after optimizations
6. **Handle errors** - Always check for missing/null fields

**Target Performance:**
- Simple queries: <100ms
- Complex queries: <500ms
- Never freeze browser (use chunking/pagination)

**When to Optimize:**
- Query takes >500ms consistently
- Browser becomes unresponsive
- Users report slow page loads
- Vault size increases significantly

**When NOT to Optimize:**
- Query runs <200ms
- Used infrequently (once per day)
- Dataset is small (<500 files)
- Optimization adds significant complexity

---

**Version History:**

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-20 | Initial release |

---

**Related Documentation:**
- [[DATAVIEW_QUERY_LIBRARY|Query Library]]
- [[DATAVIEW_SETUP_GUIDE|Setup Guide]]
- [[METADATA_SCHEMA|Metadata Schema]]

---

**End of Performance Guide**

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
