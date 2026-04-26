# Status-Based Search Queries

Search documents by workflow status (draft, review, published, deprecated).

## Query 1: All Draft Documents

```dataview
TABLE 
  file.ctime as "Created",
  metadata_priority as "Priority",
  metadata_owner as "Owner",
  file.folder as "Location"
FROM ""
WHERE contains(metadata_status, "draft")
SORT file.ctime DESC
```

**Status Values:**
- `draft`: Work in progress, not ready for review
- Use `contains()` for case-insensitive matching

---

## Query 2: Documents In Review

```dataview
TABLE 
  metadata_status as "Status",
  metadata_owner as "Owner",
  metadata_last_reviewed as "Last Reviewed",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_status, "review")
SORT file.mtime DESC
```

**Use Cases:**
- Track review queue
- Identify bottlenecks
- Monitor review SLAs

---

## Query 3: Published Documents

```dataview
TABLE 
  metadata_version as "Version",
  metadata_release as "Release",
  file.ctime as "Published",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "published")
SORT metadata_version DESC
```

**Published Criteria:**
- Approved for production use
- Versioned and released
- Stable and authoritative

---

## Query 4: Deprecated Documents

```dataview
TABLE 
  metadata_deprecated_date as "Deprecated On",
  metadata_replacement as "Replaced By",
  metadata_version as "Last Version",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "deprecated")
SORT metadata_deprecated_date DESC
```

**Deprecated Handling:**
- Mark with deprecation date
- Link to replacement document
- Preserve for historical reference

---

## Query 5: Status Distribution (Group By)

```dataview
TABLE 
  length(rows) as "Count",
  rows.file.name as "Documents"
FROM ""
WHERE metadata_status
GROUP BY metadata_status
SORT length(rows) DESC
```

**Aggregation:**
- Count documents per status
- Identify workflow bottlenecks
- Track distribution trends

---

## Query 6: Status Transition Timeline

```dataview
TABLE 
  metadata_status as "Current Status",
  metadata_status_history as "History",
  file.mtime as "Last Change",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_status_history
SORT file.mtime DESC
LIMIT 20
```

**Status History Tracking:**
- Requires `metadata_status_history` field
- Track status changes over time
- Audit workflow progression

---

## Query 7: Documents by Multiple Statuses (OR Logic)

```dataview
TABLE 
  metadata_status as "Status",
  metadata_priority as "Priority",
  file.mtime as "Modified",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "draft") OR contains(metadata_status, "review")
SORT file.mtime DESC
```

**Multiple Statuses:**
- Use `OR` for union queries
- Combine workflow states
- Filter active documents

---

## Query 8: Status with Priority Filter

```dataview
TABLE 
  metadata_status as "Status",
  metadata_priority as "Priority",
  metadata_owner as "Owner",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_status, "draft") AND contains(metadata_priority, "urgent")
SORT file.mtime DESC
```

**Combined Filters:**
- Status + Priority
- Identify critical drafts
- Prioritize review queue

---

## Query 9: Documents Missing Status

```dataview
TABLE 
  file.name as "Document",
  file.folder as "Location",
  file.ctime as "Created",
  file.mtime as "Modified"
FROM ""
WHERE !metadata_status OR metadata_status = ""
SORT file.mtime DESC
```

**Data Quality:**
- Find incomplete metadata
- Identify unclassified documents
- Enforce metadata standards

---

## Query 10: Status with Owner Accountability

```dataview
TABLE 
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.mtime as "Last Updated",
  metadata_next_review as "Next Review"
FROM ""
WHERE metadata_status AND metadata_owner
GROUP BY metadata_owner
SORT metadata_owner ASC
```

**Owner Accountability:**
- Group by owner
- Track individual workloads
- Monitor team contributions

---

## Query 11: Recently Published Documents (Last 30 Days)

```dataview
TABLE 
  metadata_status as "Status",
  metadata_version as "Version",
  file.mtime as "Published Date",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "published") AND file.mtime >= date(today) - dur(30 days)
SORT file.mtime DESC
```

**Recent Activity:**
- Track publication velocity
- Monitor release cadence
- Identify active areas

---

## Query 12: Draft Duration Analysis

```dataview
TABLE 
  file.name as "Document",
  file.ctime as "Created",
  dur(date(today) - file.ctime) as "Age",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "draft")
SORT dur(date(today) - file.ctime) DESC
```

**Duration Tracking:**
- Identify stale drafts
- Monitor work-in-progress age
- Highlight abandoned documents

---

## Query 13: Status Workflow Kanban View

```dataview
TASK
FROM ""
WHERE metadata_status
GROUP BY metadata_status
```

**Kanban-Style View:**
- Visual workflow representation
- Task-based organization
- Quick status overview

---

## Query 14: Status with Tag Filter

```dataview
TABLE 
  metadata_status as "Status",
  metadata_tags as "Tags",
  metadata_priority as "Priority",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "published") AND contains(metadata_tags, "security")
SORT file.mtime DESC
```

**Tag Filtering:**
- Combine status + tags
- Topic-specific status tracking
- Cross-reference metadata dimensions

---

## Query 15: Custom Status Values

```dataview
TABLE 
  metadata_status as "Status",
  metadata_substatus as "Substatus",
  metadata_owner as "Owner",
  file.mtime as "Modified"
FROM ""
WHERE metadata_substatus AND !contains(metadata_status, "deprecated")
SORT file.mtime DESC
```

**Custom Statuses:**
- `metadata_substatus`: Extended status field
- Examples: "in-progress", "blocked", "waiting-approval"
- Supports complex workflows

---

## Standard Status Values

| Status | Description | Next Steps |
|--------|-------------|------------|
| `draft` | Initial creation, work in progress | Complete content, request review |
| `review` | Under review by stakeholders | Address feedback, approve |
| `published` | Approved and released | Monitor usage, schedule updates |
| `deprecated` | Obsolete, replaced | Archive, redirect to replacement |
| `archived` | Historical reference only | None (read-only) |
| `blocked` | Waiting on dependencies | Resolve blockers |
| `in-progress` | Actively being updated | Continue work |

## Expected Metadata Fields

```yaml
---
metadata_status: draft|review|published|deprecated|archived|blocked|in-progress
metadata_substatus: additional-detail (optional)
metadata_status_history: ["2024-01-01:draft", "2024-02-15:review", "2024-03-01:published"]
metadata_deprecated_date: YYYY-MM-DD (if deprecated)
metadata_replacement: "[[Replacement Document]]" (if deprecated)
metadata_owner: team-name or person-name
metadata_priority: urgent|high|medium|low
metadata_version: semantic version (e.g., "1.2.0")
metadata_release: release identifier (e.g., "v2024.1")
---
```

## Status Workflow Best Practices

1. **Enforce Standards**: Use consistent status values across all documents
2. **Track History**: Log status changes with timestamps
3. **Link Replacements**: Always link deprecated docs to replacements
4. **Automate Transitions**: Use templates to enforce workflow rules
5. **Monitor Age**: Track how long documents stay in each status

## Performance Optimization

1. **Index Status Field**: Dataview automatically indexes metadata fields
2. **Limit Results**: Use `LIMIT` for large repositories
3. **Folder Scoping**: Narrow searches with `FROM "folder/path"`
4. **Cache Queries**: Obsidian caches Dataview results automatically

## Testing Checklist

- [ ] Query returns results in <1 second
- [ ] Case-insensitive matching works (use `contains()`)
- [ ] Missing metadata handled gracefully
- [ ] Status grouping is accurate
- [ ] Sort order is logical
- [ ] All standard status values are recognized

## Troubleshooting

**No Results:**
- Check status value spelling (use `contains()` for flexibility)
- Verify metadata field name: `metadata_status`
- Ensure YAML frontmatter is valid

**Incorrect Grouping:**
- Verify `GROUP BY` clause syntax
- Check for null values in status field
- Use `WHERE metadata_status` to filter nulls

**Performance Issues:**
- Add `LIMIT` clause
- Narrow folder scope with `FROM "path"`
- Reduce complexity of filters
