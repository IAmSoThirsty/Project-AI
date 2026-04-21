# Owner/Stakeholder Search Queries

Search documents by owner, stakeholder, team, or accountability assignment.

## Query 1: Documents by Specific Owner

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_status as "Status",
  metadata_priority as "Priority",
  file.mtime as "Last Modified"
FROM ""
WHERE contains(metadata_owner, "team-core")
SORT file.mtime DESC
```

**Owner Types:**
- Individual: "john-doe", "jane-smith"
- Team: "team-core", "team-security"
- Department: "engineering", "product"

---

## Query 2: All Documents by Owner (Grouped)

```dataview
TABLE 
  length(rows) as "Document Count",
  rows.file.name as "Documents"
FROM ""
WHERE metadata_owner
GROUP BY metadata_owner
SORT length(rows) DESC
```

**Workload Distribution:**
- Count documents per owner
- Identify overloaded individuals
- Balance team assignments

---

## Query 3: Unassigned Documents (No Owner)

```dataview
TABLE 
  file.name as "Document",
  file.folder as "Location",
  metadata_status as "Status",
  file.mtime as "Modified"
FROM ""
WHERE !metadata_owner OR metadata_owner = ""
SORT file.mtime DESC
```

**Orphaned Documents:**
- Missing accountability
- Requires owner assignment
- Data quality issue

---

## Query 4: Owner with Status Breakdown

```dataview
TABLE 
  metadata_owner as "Owner",
  length(rows) as "Total",
  length(filter(rows, (r) => contains(r.metadata_status, "draft"))) as "Draft",
  length(filter(rows, (r) => contains(r.metadata_status, "review"))) as "Review",
  length(filter(rows, (r) => contains(r.metadata_status, "published"))) as "Published"
FROM ""
WHERE metadata_owner
GROUP BY metadata_owner
SORT metadata_owner ASC
```

**Owner-Status Matrix:**
- Cross-tabulate owner and status
- Track individual workflows
- Monitor progress per owner

---

## Query 5: Owner with Priority Breakdown

```dataview
TABLE 
  metadata_owner as "Owner",
  length(filter(rows, (r) => contains(r.metadata_priority, "urgent"))) as "Urgent",
  length(filter(rows, (r) => contains(r.metadata_priority, "high"))) as "High",
  length(filter(rows, (r) => contains(r.metadata_priority, "medium"))) as "Medium",
  length(filter(rows, (r) => contains(r.metadata_priority, "low"))) as "Low"
FROM ""
WHERE metadata_owner AND metadata_priority
GROUP BY metadata_owner
SORT metadata_owner ASC
```

**Owner-Priority Matrix:**
- Track urgent/high items per owner
- Identify overloaded individuals
- Resource allocation planning

---

## Query 6: Owner with Stakeholder Collaboration

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_stakeholders as "Stakeholders",
  metadata_status as "Status",
  file.mtime as "Modified"
FROM ""
WHERE metadata_stakeholders
SORT file.mtime DESC
```

**Collaboration Tracking:**
- Primary owner + stakeholders
- Multi-team coordination
- Cross-functional visibility

---

## Query 7: Documents Assigned to Multiple Owners

```dataview
TABLE 
  metadata_owner as "Primary Owner",
  metadata_co_owners as "Co-Owners",
  metadata_status as "Status",
  file.name as "Document"
FROM ""
WHERE metadata_co_owners
SORT file.mtime DESC
```

**Shared Ownership:**
- Joint accountability
- Cross-team documents
- Collaboration patterns

---

## Query 8: Owner with Overdue Reviews

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_next_review as "Review Due",
  metadata_status as "Status",
  file.name as "Document"
FROM ""
WHERE metadata_owner 
  AND metadata_next_review < date(today)
  AND metadata_status != "deprecated"
SORT metadata_next_review ASC
```

**Accountability:**
- Overdue items by owner
- Track review obligations
- SLA monitoring

---

## Query 9: Team Workload Analysis

```dataview
TABLE 
  metadata_owner as "Team",
  length(rows) as "Total Docs",
  length(filter(rows, (r) => contains(r.metadata_priority, "urgent") OR contains(r.metadata_priority, "high"))) as "Critical Items"
FROM ""
WHERE contains(metadata_owner, "team-")
GROUP BY metadata_owner
SORT length(filter(rows, (r) => contains(r.metadata_priority, "urgent") OR contains(r.metadata_priority, "high"))) DESC
```

**Team Load:**
- Focus on teams (prefix: "team-")
- Count critical items per team
- Resource planning

---

## Query 10: Owner by Document Type

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_type as "Type",
  length(rows) as "Count"
FROM ""
WHERE metadata_owner AND metadata_type
GROUP BY metadata_owner, metadata_type
SORT metadata_owner ASC, metadata_type ASC
```

**Specialization:**
- Owner expertise areas
- Document type distribution
- Knowledge domain mapping

---

## Query 11: Recently Active Owners

```dataview
TABLE 
  metadata_owner as "Owner",
  length(rows) as "Documents Modified",
  max(rows.file.mtime) as "Last Activity"
FROM ""
WHERE metadata_owner AND file.mtime >= date(today) - dur(7 days)
GROUP BY metadata_owner
SORT max(rows.file.mtime) DESC
```

**Activity Tracking:**
- Owners active in last 7 days
- Contribution monitoring
- Team engagement

---

## Query 12: Owner with Folder Distribution

```dataview
TABLE 
  metadata_owner as "Owner",
  file.folder as "Folder",
  length(rows) as "Document Count"
FROM ""
WHERE metadata_owner
GROUP BY metadata_owner, file.folder
SORT metadata_owner ASC, file.folder ASC
```

**Organizational Structure:**
- Owner distribution across folders
- Area of responsibility mapping
- Knowledge silos identification

---

## Query 13: Stakeholder Mentions (All Documents)

```dataview
TABLE 
  file.name as "Document",
  metadata_stakeholders as "Stakeholders",
  metadata_owner as "Owner",
  metadata_status as "Status"
FROM ""
WHERE contains(metadata_stakeholders, "security-team")
SORT file.mtime DESC
```

**Stakeholder Filter:**
- Find all docs mentioning specific stakeholder
- Cross-team visibility
- Dependency tracking

---

## Query 14: Owner Contact Information

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_owner_email as "Email",
  metadata_owner_team as "Team",
  length(rows) as "Documents"
FROM ""
WHERE metadata_owner_email
GROUP BY metadata_owner
SORT metadata_owner ASC
```

**Contact Directory:**
- Owner contact details
- Team assignments
- Communication routing

---

## Query 15: Owner with Last Contribution Date

```dataview
TABLE 
  metadata_owner as "Owner",
  max(rows.file.mtime) as "Last Contribution",
  length(rows) as "Total Documents",
  dur(date(today) - max(rows.file.mtime)) as "Days Since Activity"
FROM ""
WHERE metadata_owner
GROUP BY metadata_owner
SORT max(rows.file.mtime) DESC
```

**Owner Activity:**
- Track last contribution date
- Identify inactive owners
- Engagement monitoring

---

## Query 16: Multi-Owner Conflict Detection

```dataview
TABLE 
  file.name as "Document",
  metadata_owner as "Primary Owner",
  metadata_co_owners as "Co-Owners",
  file.mtime as "Last Modified"
FROM ""
WHERE metadata_owner AND metadata_co_owners 
  AND contains(metadata_status, "draft")
SORT file.mtime DESC
```

**Coordination:**
- Multi-owner drafts
- Potential conflicts
- Collaboration tracking

---

## Query 17: Owner Succession Planning

```dataview
TABLE 
  metadata_owner as "Owner",
  metadata_backup_owner as "Backup",
  metadata_status as "Status",
  file.name as "Document"
FROM ""
WHERE metadata_backup_owner
SORT metadata_owner ASC
```

**Business Continuity:**
- Backup owner assignments
- Knowledge transfer tracking
- Risk mitigation

---

## Query 18: Owner by Creation vs Modification

```dataview
TABLE 
  metadata_owner as "Current Owner",
  metadata_created_by as "Original Author",
  file.ctime as "Created",
  file.mtime as "Last Modified"
FROM ""
WHERE metadata_owner != metadata_created_by
SORT file.mtime DESC
```

**Ownership Transfer:**
- Track ownership changes
- Original author vs current owner
- Knowledge transfer patterns

---

## Ownership Model

### Individual Ownership

```yaml
metadata_owner: "john-doe"
metadata_owner_email: "john@example.com"
metadata_owner_team: "engineering"
```

### Team Ownership

```yaml
metadata_owner: "team-security"
metadata_owner_email: "security@example.com"
metadata_stakeholders: ["team-core", "team-ops"]
```

### Shared Ownership

```yaml
metadata_owner: "jane-smith"
metadata_co_owners: ["john-doe", "team-qa"]
metadata_backup_owner: "alice-jones"
```

## Expected Metadata Fields

```yaml
---
# Primary Ownership
metadata_owner: team-name or person-name
metadata_owner_email: contact@example.com
metadata_owner_team: team or department name

# Collaboration
metadata_stakeholders: ["team-1", "person-1", "team-2"]
metadata_co_owners: ["person-2", "team-3"]
metadata_backup_owner: person-name

# Attribution
metadata_created_by: original-author
metadata_contributors: ["contributor-1", "contributor-2"]

# Context
metadata_status: draft|review|published|deprecated
metadata_priority: urgent|high|medium|low
metadata_type: documentation|code|configuration|report
metadata_next_review: YYYY-MM-DD
---
```

## Ownership Best Practices

1. **Clear Assignment**: Every document must have an owner
2. **Team Naming**: Use consistent team prefixes ("team-", "dept-")
3. **Contact Info**: Include email or Slack handle
4. **Backup Owners**: Assign backups for critical documents
5. **Stakeholder Visibility**: Tag all relevant stakeholders
6. **Regular Audits**: Review ownership quarterly
7. **Transfer Protocol**: Document ownership changes

## Owner Accountability Matrix

| Role | Responsibilities | Metadata Fields |
|------|------------------|-----------------|
| **Owner** | Primary accountability, approvals | `metadata_owner`, `metadata_owner_email` |
| **Co-Owner** | Shared responsibility | `metadata_co_owners` |
| **Stakeholder** | Review, input, dependency | `metadata_stakeholders` |
| **Contributor** | Content creation, updates | `metadata_contributors` |
| **Backup** | Continuity, knowledge transfer | `metadata_backup_owner` |

## Performance Optimization

1. **Index Owner Field**: Automatically indexed by Dataview
2. **Limit Results**: Use `LIMIT` for large repositories
3. **Folder Scoping**: Narrow with `FROM "folder/path"`
4. **String Matching**: Use `contains()` for flexible matching

## Testing Checklist

- [ ] Query returns results in <1 second
- [ ] Owner filtering works correctly
- [ ] Missing owners identified (unassigned docs)
- [ ] Grouping/aggregation is accurate
- [ ] Multi-owner documents handled properly
- [ ] Contact information displayed correctly

## Troubleshooting

**No Results:**
- Check owner name spelling
- Verify metadata field name: `metadata_owner`
- Ensure YAML frontmatter is valid

**Duplicate Owners:**
- Standardize owner naming (lowercase, hyphens)
- Use team prefixes consistently
- Create owner directory/glossary

**Performance Issues:**
- Add `LIMIT` clause
- Narrow folder scope
- Use indexed fields (metadata_owner is indexed)
- Reduce aggregation complexity
