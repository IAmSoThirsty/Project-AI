# Dataview Quick Reference Card

**One-page cheat sheet for Obsidian Dataview queries**

---

## Query Structure

```dataview
TABLE|LIST|TASK|CALENDAR field1, field2, ...
FROM "path/to/notes"
WHERE condition
SORT field ASC|DESC
LIMIT number
```

---

## Common Queries

### All Active Projects
```dataview
TABLE status, priority, due
FROM "projects"
WHERE status = "active"
SORT priority DESC
```

### Recent Notes
```dataview
LIST
FROM ""
SORT file.mtime DESC
LIMIT 10
```

### Incomplete Tasks
```dataview
TASK
FROM "projects"
WHERE !completed
```

### Notes by Tag
```dataview
TABLE file.ctime as "Created"
FROM #project
SORT file.ctime DESC
```

---

## Aggregations

```dataview
TABLE
  length(rows) as "Count",
  sum(rows.budget) as "Total",
  average(rows.score) as "Average",
  min(rows.date) as "Earliest",
  max(rows.date) as "Latest"
FROM "data"
GROUP BY category
```

---

## Calculations

```dataview
TABLE
  budget * 1.1 as "With Tax",
  round(score / total * 100, 1) + "%" as "Percentage",
  due - date(today) as "Days Remaining",
  choice(score > 80, "Pass", "Fail") as "Result"
FROM "exams"
```

---

## Conditional Logic

```dataview
TABLE
  choice(priority = "high", "🔴", 
    choice(priority = "medium", "🟡", "🟢")) as "Icon",
  choice(completion >= 100, "✅", "⏳") as "Status",
  default(owner, "Unassigned") as "Owner"
FROM "projects"
```

---

## Date Functions

```dataview
TABLE
  date(today) as "Today",
  due - date(today) as "Days Until Due",
  date("2024-12-31") as "Specific Date",
  dur(1 week) as "Duration"
FROM "projects"
WHERE due < date(today) + dur(1 week)
```

---

## Filters

```dataview
TABLE status, priority
FROM "projects"
WHERE status = "active"
  AND priority = "high"
  AND due < date(today) + dur(1 month)
  AND contains(tags, "urgent")
```

---

## Field References

### File Metadata (Always Available)
- `file.name` - Filename without extension
- `file.path` - Full file path
- `file.ctime` - Creation time
- `file.mtime` - Last modified time
- `file.size` - File size (bytes)
- `file.tags` - All tags in file
- `file.frontmatter` - All frontmatter fields

### Custom Fields (From YAML)
```yaml
---
status: active
priority: high
due: 2024-06-30
tags: [project, ai]
---
```

Access: `status`, `priority`, `due`, `tags`

---

## DataviewJS

```dataviewjs
// Get pages
const pages = dv.pages('"projects"')
  .where(p => p.status === "active");

// Calculate
const total = pages.array()
  .reduce((sum, p) => sum + (p.budget || 0), 0);

// Render
dv.header(2, "Summary");
dv.paragraph(`Total: $${total.toLocaleString()}`);
dv.table(["Project", "Budget"], 
  pages.array().map(p => [p.file.link, p.budget]));
```

---

## Inline Queries

```markdown
Project count: `= length(dv.pages('"projects"'))`

Total budget: `$= dv.pages('"projects"').array().reduce((sum, p) => sum + p.budget, 0)`
```

---

## Operators

### Comparison
- `=` Equal
- `!=` Not equal
- `<`, `>`, `<=`, `>=` Comparison

### Logical
- `AND` Both conditions
- `OR` Either condition
- `!` Not

### Arithmetic
- `+`, `-`, `*`, `/` Math operations

### String
- `contains(field, "text")` Check contains
- `startswith(field, "prefix")` Check prefix
- `endswith(field, "suffix")` Check suffix

---

## Performance Tips

1. **Narrow paths:** `FROM "specific/folder"` not `FROM ""`
2. **Use LIMIT:** `LIMIT 50` for large result sets
3. **Filter early:** Put WHERE before complex calculations
4. **Cache calculations:** Store in frontmatter instead of computing

---

## Common Patterns

### Project Dashboard
```dataview
TABLE
  status as "Status",
  priority as "Priority",
  due as "Due Date",
  choice(completion >= 50, "✅", "⚠️") as "Health"
FROM "projects"
WHERE status != "completed"
SORT priority DESC, due ASC
```

### Tag Overview
```dataview
TABLE length(rows) as "Count"
FROM ""
FLATTEN file.tags as tag
GROUP BY tag
SORT length(rows) DESC
```

### Weekly Activity
```dataview
LIST
FROM ""
WHERE file.mtime >= date(today) - dur(1 week)
SORT file.mtime DESC
```

### Budget Tracking
```dataview
TABLE
  sum(rows.budget) as "Total Budget",
  sum(rows.spent) as "Total Spent",
  sum(rows.budget) - sum(rows.spent) as "Remaining"
FROM "finance"
GROUP BY category
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No results | Check path exists, verify frontmatter fields |
| Syntax error | Add commas between fields, quote paths |
| Slow query | Add LIMIT, narrow FROM path |
| JS not working | Enable DataviewJS in settings |
| Fields show null | Field missing or misspelled (case-sensitive) |

---

## Examples from This Vault

See production queries in:
- `docs/dataview-examples/QUERY_LIBRARY.md` (10 queries)
- Sample data in `docs/dataview-examples/*.md`

Test with:
```dataview
TABLE status, priority, completion
FROM "docs/dataview-examples"
WHERE type = "project"
```

---

**Quick Start:**
1. Create note with YAML frontmatter
2. Write query in \`\`\`dataview code block
3. Switch to Reading View (Ctrl+E)
4. Query auto-executes and displays results

**Full Guide:** `DATAVIEW_SETUP_GUIDE.md` (3,800+ words)  
**Help:** https://blacksmithgu.github.io/obsidian-dataview/
