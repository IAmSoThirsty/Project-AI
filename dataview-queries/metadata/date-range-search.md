# Date Range Search Queries

Search documents by creation date, modification date, or review date ranges.

## Query 1: Documents by Creation Date Range

```dataview
TABLE 
  file.ctime as "Created",
  metadata_status as "Status",
  metadata_priority as "Priority",
  metadata_owner as "Owner"
FROM ""
WHERE file.ctime >= date(2024-01-01) AND file.ctime <= date(2024-12-31)
SORT file.ctime DESC
```

**Variables to Customize:**
- `date(2024-01-01)`: Start date (YYYY-MM-DD format)
- `date(2024-12-31)`: End date (YYYY-MM-DD format)

---

## Query 2: Documents by Modification Date Range

```dataview
TABLE 
  file.mtime as "Last Modified",
  metadata_status as "Status",
  file.ctime as "Created",
  metadata_owner as "Owner"
FROM ""
WHERE file.mtime >= date(2024-06-01) AND file.mtime <= date(2024-12-31)
SORT file.mtime DESC
LIMIT 50
```

**Variables to Customize:**
- `date(2024-06-01)`: Start date for modifications
- `date(2024-12-31)`: End date for modifications
- `LIMIT 50`: Maximum number of results (adjust as needed)

---

## Query 3: Documents by Review Date Range

```dataview
TABLE 
  metadata_last_reviewed as "Last Reviewed",
  metadata_next_review as "Next Review",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_last_reviewed >= date(2024-01-01) AND metadata_last_reviewed <= date(2024-12-31)
SORT metadata_last_reviewed DESC
```

**Requires Metadata:**
- `metadata_last_reviewed`: ISO date when document was last reviewed
- `metadata_next_review`: ISO date when next review is due

---

## Query 4: Documents Reviewed in Last 30 Days

```dataview
TABLE 
  metadata_last_reviewed as "Reviewed",
  file.mtime as "Modified",
  metadata_status as "Status",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_last_reviewed >= date(today) - dur(30 days)
SORT metadata_last_reviewed DESC
```

**Dynamic Date Calculation:**
- `date(today)`: Current date
- `dur(30 days)`: 30-day duration
- Adjust `30` to any number of days

---

## Query 5: Documents Created This Month

```dataview
TABLE 
  file.ctime as "Created",
  metadata_type as "Type",
  metadata_status as "Status",
  metadata_priority as "Priority"
FROM ""
WHERE file.ctime.year = date(today).year AND file.ctime.month = date(today).month
SORT file.ctime DESC
```

**Date Components:**
- `.year`: Extract year from date
- `.month`: Extract month from date
- Automatically adjusts to current month

---

## Query 6: Documents Modified Today

```dataview
LIST
FROM ""
WHERE file.mtime >= date(today)
SORT file.mtime DESC
```

**Use Cases:**
- Daily activity tracking
- Recent work identification
- Collaboration monitoring

---

## Query 7: Documents Needing Review (Overdue)

```dataview
TABLE 
  metadata_next_review as "Review Due",
  metadata_last_reviewed as "Last Reviewed",
  metadata_owner as "Owner",
  metadata_status as "Status"
FROM ""
WHERE metadata_next_review < date(today) AND metadata_status != "deprecated"
SORT metadata_next_review ASC
```

**Logic:**
- `metadata_next_review < date(today)`: Review date has passed
- Excludes deprecated documents
- Shows oldest due dates first

---

## Query 8: Documents Created Between Two Timestamps

```dataview
TABLE 
  file.ctime as "Created",
  file.folder as "Location",
  metadata_type as "Type",
  metadata_tags as "Tags"
FROM ""
WHERE file.ctime >= date(2024-03-15T09:00:00) AND file.ctime <= date(2024-03-15T17:00:00)
SORT file.ctime DESC
```

**Timestamp Format:**
- `YYYY-MM-DDTHH:MM:SS`: ISO 8601 format
- Time is in 24-hour format
- Useful for tracking specific work sessions

---

## Query 9: Documents Modified in Last N Hours

```dataview
TABLE 
  file.mtime as "Modified",
  file.name as "Document",
  metadata_owner as "Owner"
FROM ""
WHERE file.mtime >= date(today) - dur(6 hours)
SORT file.mtime DESC
```

**Time Units:**
- `hours`: For recent activity
- `minutes`: For real-time monitoring
- `days`: For weekly/monthly views

---

## Query 10: Date Range with Status Filter

```dataview
TABLE 
  file.ctime as "Created",
  file.mtime as "Modified",
  metadata_status as "Status",
  metadata_priority as "Priority"
FROM ""
WHERE file.ctime >= date(2024-01-01) 
  AND file.ctime <= date(2024-12-31)
  AND contains(metadata_status, "published")
SORT file.ctime DESC
```

**Combined Filters:**
- Date range + status check
- Use `contains()` for partial matches
- Stack multiple `AND` conditions

---

## Performance Tips

1. **Limit Results**: Use `LIMIT` clause to cap large result sets
2. **Index Dates**: Date comparisons are fast in Dataview
3. **Cache Results**: Obsidian caches Dataview queries automatically
4. **Folder Scope**: Narrow with `FROM "folder/path"`

## Common Date Functions

| Function | Description | Example |
|----------|-------------|---------|
| `date(today)` | Current date | `date(today)` |
| `date(tomorrow)` | Tomorrow's date | `date(tomorrow)` |
| `date(yesterday)` | Yesterday's date | `date(yesterday)` |
| `date(sow)` | Start of week | `date(sow)` |
| `date(eow)` | End of week | `date(eow)` |
| `date(som)` | Start of month | `date(som)` |
| `date(eom)` | End of month | `date(eom)` |
| `date(soy)` | Start of year | `date(soy)` |
| `date(eoy)` | End of year | `date(eoy)` |
| `dur(N days)` | Duration in days | `dur(7 days)` |

## Expected Metadata Fields

Required for full functionality:

```yaml
---
metadata_status: draft|review|published|deprecated
metadata_priority: urgent|high|medium|low
metadata_owner: team-name or person-name
metadata_last_reviewed: YYYY-MM-DD
metadata_next_review: YYYY-MM-DD
metadata_type: documentation|code|configuration|report
metadata_tags: ["tag1", "tag2"]
---
```

## Testing Checklist

- [ ] Query returns results in <1 second
- [ ] Date ranges work correctly
- [ ] Null values handled gracefully
- [ ] Sort order is correct
- [ ] Metadata fields are displayed properly
- [ ] LIMIT clause prevents performance issues
- [ ] Dynamic dates update automatically

## Troubleshooting

**No Results:**
- Check date format: `date(YYYY-MM-DD)`
- Verify metadata fields exist
- Check folder path in `FROM` clause

**Performance Issues:**
- Add `LIMIT` clause
- Narrow folder scope
- Use indexed file properties (file.ctime, file.mtime)

**Incorrect Dates:**
- Ensure ISO 8601 format in metadata
- Check timezone settings in Obsidian
- Verify date arithmetic (today - dur(N days))
