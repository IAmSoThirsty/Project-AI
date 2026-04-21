# Dataview Query Library

Production-ready Dataview query collection for Obsidian vault management.

---

## Table of Contents
- [[#query-1-active-projects-dashboard|Query 1: Active Projects Dashboard]]
- [[#query-2-priority-task-matrix|Query 2: Priority Task Matrix]]
- [[#query-3-budget-analysis-report|Query 3: Budget Analysis Report]]
- [[#advanced-queries|Advanced Queries]]
- [[#performance-optimization|Performance Optimization]]

---

## Query 1: Active Projects Dashboard

**Purpose:** Display all active projects sorted by priority with key metrics.

**Query:**
\`\`\`dataview
TABLE
  status as "Status",
  priority as "Priority",
  completion + "%" as "Progress",
  owner as "Owner",
  due as "Due Date"
FROM "docs/dataview-examples"
WHERE type = "project" AND status = "active"
SORT priority DESC, due ASC
\`\`\`

**Expected Output:**
| File | Status | Priority | Progress | Owner | Due Date |
|------|--------|----------|----------|-------|----------|
| project-alpha | active | high | 45% | Engineering Team | 2024-06-30 |
| api-docs-portal | active | low | 60% | DevRel Team | 2024-04-30 |

**Performance:** < 50ms (2 files scanned)

**Use Cases:**
- Daily standup dashboard
- Sprint planning
- Executive status reporting
- Resource allocation

---

## Query 2: Priority Task Matrix

**Purpose:** Categorize projects by status and priority for strategic planning.

**Query:**
\`\`\`dataview
TABLE
  length(rows) as "Count",
  sum(rows.budget) as "Total Budget ($)",
  round(average(rows.completion), 1) + "%" as "Avg Completion"
FROM "docs/dataview-examples"
WHERE type = "project"
GROUP BY status, priority
SORT status ASC, priority DESC
\`\`\`

**Expected Output:**
| status, priority | Count | Total Budget ($) | Avg Completion |
|------------------|-------|------------------|----------------|
| active, high | 1 | 150000 | 45.0% |
| active, low | 1 | 45000 | 60.0% |
| completed, critical | 1 | 85000 | 100.0% |
| on-hold, high | 1 | 95000 | 30.0% |
| planning, medium | 1 | 120000 | 15.0% |

**Performance:** < 100ms (5 files scanned, aggregation applied)

**Use Cases:**
- Portfolio management
- Budget allocation
- Risk assessment
- Capacity planning

---

## Query 3: Budget Analysis Report

**Purpose:** Financial overview of all projects with budget utilization.

**Query:**
\`\`\`dataview
TABLE
  budget as "Total Budget ($)",
  round(budget * (completion / 100), 0) as "Spent ($)",
  round(budget * (1 - completion / 100), 0) as "Remaining ($)",
  completion + "%" as "% Complete",
  choice(completion >= 50, "✅ On Track", "⚠️ At Risk") as "Health"
FROM "docs/dataview-examples"
WHERE type = "project" AND budget
SORT budget DESC
\`\`\`

**Expected Output:**
| File | Total Budget ($) | Spent ($) | Remaining ($) | % Complete | Health |
|------|------------------|-----------|---------------|------------|--------|
| project-alpha | 150000 | 67500 | 82500 | 45% | ⚠️ At Risk |
| mobile-redesign | 120000 | 18000 | 102000 | 15% | ⚠️ At Risk |
| database-migration | 95000 | 28500 | 66500 | 30% | ⚠️ At Risk |
| security-audit | 85000 | 85000 | 0 | 100% | ✅ On Track |
| api-docs-portal | 45000 | 27000 | 18000 | 60% | ✅ On Track |

**Performance:** < 80ms (5 files scanned, calculations applied)

**Use Cases:**
- Financial reporting
- Budget forecasting
- Burn rate analysis
- Project health monitoring

---

## Advanced Queries

### 4. Overdue Projects Alert
\`\`\`dataview
TABLE
  due as "Due Date",
  date(today) - due as "Days Overdue",
  priority as "Priority",
  owner as "Owner"
FROM "docs/dataview-examples"
WHERE type = "project" AND due < date(today) AND status != "completed"
SORT due ASC
\`\`\`

### 5. Tag-Based Project Discovery
\`\`\`dataview
TABLE
  status as "Status",
  priority as "Priority",
  completion + "%" as "Progress"
FROM "docs/dataview-examples"
WHERE contains(tags, "ai") OR contains(tags, "security")
SORT priority DESC
\`\`\`

### 6. Completion Timeline
\`\`\`dataview
TABLE
  created as "Started",
  due as "Due",
  completed as "Finished",
  choice(completed, completed - created, "") as "Duration"
FROM "docs/dataview-examples"
WHERE type = "project" AND status = "completed"
SORT completed DESC
\`\`\`

### 7. Team Workload Distribution
\`\`\`dataview
TABLE
  length(rows) as "Projects",
  sum(rows.budget) as "Total Budget ($)",
  round(average(rows.completion), 1) + "%" as "Avg Progress"
FROM "docs/dataview-examples"
WHERE type = "project" AND status != "completed"
GROUP BY owner
SORT length(rows) DESC
\`\`\`

### 8. Critical Path Analysis
\`\`\`dataview
TABLE
  priority as "Priority",
  due as "Deadline",
  completion + "%" as "Progress",
  choice(completion < 50 AND priority = "critical", "🚨 URGENT", 
         choice(completion < 30 AND priority = "high", "⚠️ WARNING", "✅ OK")) as "Alert"
FROM "docs/dataview-examples"
WHERE type = "project" AND status != "completed"
SORT priority DESC, completion ASC
\`\`\`

### 9. Recent Activity Feed
\`\`\`dataview
TABLE
  created as "Created",
  status as "Status",
  owner as "Owner"
FROM "docs/dataview-examples"
WHERE type = "project"
SORT file.mtime DESC
LIMIT 10
\`\`\`

### 10. DataviewJS - Custom Calculations
\`\`\`dataviewjs
const projects = dv.pages('"docs/dataview-examples"')
  .where(p => p.type === "project");

const totalBudget = projects.array()
  .reduce((sum, p) => sum + (p.budget || 0), 0);

const avgCompletion = projects.array()
  .reduce((sum, p) => sum + (p.completion || 0), 0) / projects.length;

dv.header(2, "Portfolio Summary");
dv.paragraph(\`**Total Projects:** \${projects.length}\`);
dv.paragraph(\`**Total Budget:** $\${totalBudget.toLocaleString()}\`);
dv.paragraph(\`**Average Completion:** \${avgCompletion.toFixed(1)}%\`);
dv.paragraph(\`**Active Projects:** \${projects.where(p => p.status === "active").length}\`);
\`\`\`

---

## Performance Optimization

### Best Practices

1. **Use Specific Paths**
   - ❌ `FROM ""` (scans entire vault)
   - ✅ `FROM "docs/dataview-examples"` (scans specific folder)

2. **Filter Early**
   - ❌ `FROM "" WHERE type = "project" AND status = "active"`
   - ✅ `FROM "projects" WHERE status = "active"` (smaller dataset)

3. **Limit Results**
   - ❌ Unbounded queries on large vaults
   - ✅ `LIMIT 50` for large result sets

4. **Avoid Expensive Operations**
   - Minimize nested queries
   - Use built-in aggregations (sum, average, length)
   - Cache complex calculations in frontmatter

5. **Index Metadata Properly**
   - Use consistent field names
   - Use simple data types (string, number, date)
   - Avoid deeply nested structures

### Performance Benchmarks

| Query Type | Files Scanned | Expected Performance |
|------------|---------------|---------------------|
| Simple TABLE | < 100 | < 50ms |
| Filtered TABLE | < 100 | < 80ms |
| GROUP BY aggregation | < 100 | < 150ms |
| Complex calculations | < 50 | < 200ms |
| DataviewJS | < 50 | < 300ms |

**Note:** Times measured on standard desktop (i5, 8GB RAM). Actual performance varies by vault size and system specs.

---

## Query Patterns Reference

### Basic Syntax
\`\`\`
TABLE field1, field2, field3
FROM "path/to/notes"
WHERE condition
SORT field ASC/DESC
LIMIT number
\`\`\`

### Aggregation Functions
- `length(rows)` - Count items
- `sum(rows.field)` - Sum values
- `average(rows.field)` - Calculate average
- `min(rows.field)` - Minimum value
- `max(rows.field)` - Maximum value

### Conditional Logic
- `choice(condition, true_value, false_value)` - If/else
- `contains(list, value)` - Check list membership
- `default(field, fallback)` - Provide default value

### Date Functions
- `date(today)` - Current date
- `date("2024-06-30")` - Parse date
- `dur(1 month)` - Duration

### Operators
- `=`, `!=` - Equality
- `<`, `>`, `<=`, `>=` - Comparison
- `AND`, `OR`, `!` - Logical
- `+`, `-`, `*`, `/` - Arithmetic

---

## Troubleshooting

### Common Issues

1. **Query returns no results**
   - Verify path exists: `FROM "docs/dataview-examples"`
   - Check field names match frontmatter exactly
   - Ensure WHERE conditions are not too restrictive

2. **Performance degradation**
   - Narrow search path
   - Add LIMIT clause
   - Reduce calculation complexity
   - Check vault size (> 1000 notes may need optimization)

3. **Syntax errors**
   - Use backticks for code blocks: \`\`\`dataview
   - Check for typos in field names
   - Verify operator precedence with parentheses
   - Ensure proper quoting of strings

4. **Incorrect calculations**
   - Verify field data types
   - Handle null values with `default()`
   - Round floating-point numbers
   - Use `choice()` for conditional logic

---

## Integration Examples

### Dashboard Integration
Create a "Dashboard.md" file with multiple queries:

\`\`\`markdown
# Project Dashboard

## Active Projects
\`\`\`dataview
[Query 1 here]
\`\`\`

## Budget Summary
\`\`\`dataview
[Query 3 here]
\`\`\`

## Team Workload
\`\`\`dataview
[Query 7 here]
\`\`\`
\`\`\`

### Automation with Templates
Use Templater plugin to generate project files:

\`\`\`markdown
---
title: <% tp.file.title %>
status: planning
priority: medium
type: project
created: <% tp.date.now("YYYY-MM-DD") %>
due: <% tp.date.now("YYYY-MM-DD", 90) %>
tags: []
owner: 
budget: 
completion: 0
---
\`\`\`

---

## Version History

- **v1.0.0** (2024-04-20): Initial query library
  - 10 production queries
  - Performance benchmarks
  - Troubleshooting guide

---

## Support

For issues or enhancements:
1. Check Dataview documentation: https://blacksmithgu.github.io/obsidian-dataview/
2. Review query library examples above
3. Test queries in isolation before combining
4. Monitor performance with Obsidian Developer Tools (Ctrl+Shift+I)

**Query testing workflow:**
1. Create test note with sample metadata
2. Write query targeting specific path
3. Verify results match expectations
4. Measure performance (< 500ms target)
5. Document query in library
