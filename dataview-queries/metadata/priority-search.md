# Priority-Based Search Queries

Search documents by priority level (urgent, high, medium, low).

## Query 1: Urgent Priority Documents

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.mtime as "Last Modified"
FROM ""
WHERE contains(metadata_priority, "urgent")
SORT file.mtime DESC
```

**Urgent Criteria:**
- Immediate action required
- Critical dependencies
- Time-sensitive content

---

## Query 2: High Priority Documents

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  metadata_owner as "Owner",
  metadata_next_review as "Next Review"
FROM ""
WHERE contains(metadata_priority, "high")
SORT file.mtime DESC
```

**High Priority:**
- Important but not urgent
- Core functionality documentation
- Frequently referenced content

---

## Query 3: Medium Priority Documents

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.folder as "Location"
FROM ""
WHERE contains(metadata_priority, "medium")
SORT file.name ASC
LIMIT 50
```

**Medium Priority:**
- Standard documentation
- Supporting materials
- Routine updates

---

## Query 4: Low Priority Documents

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  file.ctime as "Created",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_priority, "low")
SORT file.ctime DESC
```

**Low Priority:**
- Reference materials
- Historical documentation
- Optional enhancements

---

## Query 5: Priority Distribution

```dataview
TABLE 
  length(rows) as "Count",
  rows.file.name as "Documents"
FROM ""
WHERE metadata_priority
GROUP BY metadata_priority
SORT metadata_priority ASC
```

**Priority Breakdown:**
- Visualize priority distribution
- Identify workload balance
- Track priority trends

---

## Query 6: Urgent + High Priority Combined

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_priority, "urgent") OR contains(metadata_priority, "high")
SORT metadata_priority ASC, file.mtime DESC
```

**Critical Work:**
- Focus on high-impact items
- Combine urgent and high priorities
- Sorted by priority, then recency

---

## Query 7: Priority with Status Filter

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_priority, "urgent") AND contains(metadata_status, "draft")
SORT file.mtime DESC
```

**Critical Drafts:**
- Urgent documents still in draft
- High-priority work in progress
- Requires immediate attention

---

## Query 8: Priority by Owner

```dataview
TABLE 
  metadata_priority as "Priority",
  length(rows) as "Document Count",
  rows.file.name as "Documents"
FROM ""
WHERE metadata_priority AND metadata_owner
GROUP BY metadata_owner, metadata_priority
SORT metadata_owner ASC, metadata_priority ASC
```

**Owner Workload:**
- Group by owner and priority
- Identify overloaded individuals
- Balance team priorities

---

## Query 9: Priority with Due Dates

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_next_review as "Due Date",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_priority AND metadata_next_review
SORT metadata_priority ASC, metadata_next_review ASC
```

**Time-Sensitive Priorities:**
- Combine priority with deadlines
- Identify critical path items
- Schedule urgent work

---

## Query 10: Missing Priority Metadata

```dataview
TABLE 
  file.name as "Document",
  file.folder as "Location",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE !metadata_priority OR metadata_priority = ""
SORT file.mtime DESC
```

**Data Quality:**
- Find incomplete metadata
- Enforce priority classification
- Improve documentation standards

---

## Query 11: Priority Changes Over Time

```dataview
TABLE 
  metadata_priority as "Current Priority",
  metadata_priority_history as "History",
  file.mtime as "Last Change",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_priority_history
SORT file.mtime DESC
LIMIT 20
```

**Priority Evolution:**
- Track priority changes
- Audit escalations/de-escalations
- Historical analysis

---

## Query 12: Urgent Documents Overdue for Review

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_next_review as "Review Due",
  metadata_last_reviewed as "Last Reviewed",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_priority, "urgent") 
  AND metadata_next_review < date(today)
  AND metadata_status != "deprecated"
SORT metadata_next_review ASC
```

**Critical Overdue:**
- Urgent items past review date
- High-risk situations
- Requires immediate attention

---

## Query 13: Priority by Document Type

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_type as "Type",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_priority AND metadata_type
GROUP BY metadata_type, metadata_priority
SORT metadata_type ASC, metadata_priority ASC
```

**Type-Priority Matrix:**
- Cross-reference type and priority
- Identify patterns
- Resource allocation planning

---

## Query 14: High Priority Published Documents

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_version as "Version",
  file.mtime as "Published",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_priority, "high") 
  AND contains(metadata_status, "published")
SORT file.mtime DESC
```

**Critical Production Docs:**
- High-priority released content
- Core documentation
- Frequently accessed materials

---

## Query 15: Priority with Tag Filter

```dataview
TABLE 
  metadata_priority as "Priority",
  metadata_tags as "Tags",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_priority AND contains(metadata_tags, "security")
SORT metadata_priority ASC, file.mtime DESC
```

**Topic-Specific Priorities:**
- Filter by tags + priority
- Domain-specific urgency
- Specialized content tracking

---

## Query 16: Priority Escalation Candidates

```dataview
TABLE 
  metadata_priority as "Priority",
  file.ctime as "Created",
  dur(date(today) - file.ctime) as "Age",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_priority, "medium") 
  AND dur(date(today) - file.ctime) > dur(30 days)
  AND contains(metadata_status, "draft")
SORT dur(date(today) - file.ctime) DESC
```

**Stale Work:**
- Medium priority drafts > 30 days old
- Candidates for priority escalation
- Potential abandonment detection

---

## Query 17: Priority Heatmap (Count by Priority)

```dataview
TABLE WITHOUT ID
  metadata_priority as "Priority",
  length(rows) as "Total Documents",
  length(filter(rows, (r) => contains(r.metadata_status, "draft"))) as "Draft",
  length(filter(rows, (r) => contains(r.metadata_status, "review"))) as "Review",
  length(filter(rows, (r) => contains(r.metadata_status, "published"))) as "Published"
FROM ""
WHERE metadata_priority
GROUP BY metadata_priority
SORT metadata_priority ASC
```

**Priority-Status Matrix:**
- Cross-tabulate priority and status
- Workflow bottleneck identification
- Resource allocation insights

---

## Query 18: Priority by Folder

```dataview
TABLE 
  file.folder as "Location",
  metadata_priority as "Priority",
  length(rows) as "Count"
FROM ""
WHERE metadata_priority
GROUP BY file.folder, metadata_priority
SORT file.folder ASC, metadata_priority ASC
```

**Folder-Priority Distribution:**
- Identify high-priority areas
- Organizational structure insights
- Resource planning by area

---

## Priority Classification System

| Priority | SLA | Action Required | Examples |
|----------|-----|-----------------|----------|
| `urgent` | 24 hours | Immediate action | Security patches, critical bugs |
| `high` | 3-5 days | Prioritized work | Core features, major releases |
| `medium` | 1-2 weeks | Scheduled work | Standard documentation, updates |
| `low` | 30+ days | Best effort | Nice-to-have, cleanup tasks |

## Expected Metadata Fields

```yaml
---
metadata_priority: urgent|high|medium|low
metadata_priority_history: ["2024-01-01:medium", "2024-02-15:high", "2024-03-01:urgent"]
metadata_priority_reason: "Critical security vulnerability identified"
metadata_escalation_date: YYYY-MM-DD (if escalated)
metadata_status: draft|review|published|deprecated
metadata_owner: team-name or person-name
metadata_next_review: YYYY-MM-DD
metadata_type: documentation|code|configuration|report
metadata_tags: ["tag1", "tag2"]
---
```

## Priority Best Practices

1. **Regular Review**: Re-evaluate priorities weekly/monthly
2. **Clear Criteria**: Define priority levels consistently
3. **Owner Assignment**: All high/urgent items must have owners
4. **Track Changes**: Log priority escalations/de-escalations
5. **Balance Workload**: Avoid priority inflation (too many "urgent" items)
6. **Link to Due Dates**: Combine priority with deadlines

## Priority Escalation Criteria

**Escalate to Urgent:**
- Security vulnerabilities
- Production outages
- Legal/compliance requirements
- Executive requests

**Escalate to High:**
- Core functionality documentation
- Major feature releases
- Frequent customer inquiries
- Dependency blockers

**De-escalate to Medium/Low:**
- Resolved blockers
- Completed dependencies
- Changed business priorities
- Low usage/impact

## Performance Optimization

1. **Index Priority Field**: Automatically indexed by Dataview
2. **Limit Results**: Use `LIMIT` for large datasets
3. **Folder Scoping**: Narrow with `FROM "folder/path"`
4. **Combined Filters**: Stack filters to reduce result set

## Testing Checklist

- [ ] Query returns results in <1 second
- [ ] All priority levels are recognized
- [ ] Case-insensitive matching works (use `contains()`)
- [ ] Missing metadata handled gracefully
- [ ] Sort order is logical (urgent first)
- [ ] Grouping/aggregation is accurate

## Troubleshooting

**No Results:**
- Check priority value spelling (urgent, high, medium, low)
- Verify metadata field name: `metadata_priority`
- Ensure YAML frontmatter is valid

**Incorrect Priority Order:**
- Use explicit sort: `SORT metadata_priority ASC`
- Alphabetical: high, low, medium, urgent (not logical)
- Consider custom sort with CASE logic

**Performance Issues:**
- Add `LIMIT` clause
- Narrow folder scope
- Use indexed fields (metadata_priority is indexed)
