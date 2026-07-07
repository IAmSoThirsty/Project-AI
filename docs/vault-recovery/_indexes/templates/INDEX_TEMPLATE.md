---
# METADATA - Required for all index files
index_type: "by-area"  # Options: by-area | by-type | by-priority | by-status | cross-reference
index_scope: "security"  # The domain/category this index covers
last_updated: "2024-01-15"  # ISO 8601 date format (YYYY-MM-DD)
maintainer: "AGENT-XXX"  # Agent ID, team name, or individual responsible for maintenance
total_documents: 0  # Total number of documents indexed (auto-update with validation script)
metadata_schema_version: "1.0"  # Schema version for validation
priority_distribution:  # Distribution of priorities (optional, for by-priority indexes)
  p0: 0
  p1: 0
  p2: 0
  p3: 0
status_distribution:  # Distribution of statuses (optional)
  active: 0
  planned: 0
  in_progress: 0
  review: 0
  archived: 0
  deprecated: 0
  superseded: 0
tags:  # Obsidian tags for discoverability
  - index
  - navigation
  - YOUR_DOMAIN_TAG
related_indexes:  # Links to related index files
  - "[[another-related-index]]"
coverage_percentage: 0  # Estimated percentage of domain coverage (0-100)
---

# [Index Name] Index

> **Index Type:** {by-area | by-type | by-priority | by-status | cross-reference}  
> **Scope:** {Brief description of what this index covers}  
> **Maintainer:** {Agent ID or team name}  
> **Last Updated:** {YYYY-MM-DD}

## Overview

{2-4 sentence description of this index's purpose, scope, and how it fits into the larger vault organization system. Explain who should use this index and when.}

**Use This Index When:**
- {Primary use case scenario}
- {Secondary use case scenario}
- {Tertiary use case scenario}

**Related Indexes:**
- [[related-index-1]] - {Brief relationship description}
- [[related-index-2]] - {Brief relationship description}

---

## Contents

### {Section Name} ({Optional Priority/Status})

> **Section Description:** {1-2 sentences describing what documents belong in this section}

#### {Subsection Name} (if needed)

- [[document-name-1]] - {Brief description} ({Priority}, {Status})
  - **Key Topics:** {topic1, topic2, topic3}
  - **Dependencies:** [[prerequisite-doc-1]], [[prerequisite-doc-2]]
  - **Last Reviewed:** {YYYY-MM-DD}
  
- [[document-name-2]] - {Brief description} ({Priority}, {Status})
  - **Key Topics:** {topic1, topic2, topic3}
  - **Related:** [[related-doc-1]]
  - **Last Reviewed:** {YYYY-MM-DD}

- [[document-name-3]] - {Brief description} ({Priority}, {Status})
  - **Key Topics:** {topic1, topic2, topic3}
  - **Supersedes:** [[old-doc-1]]
  - **Last Reviewed:** {YYYY-MM-DD}

### {Another Section Name}

- [[document-name-4]] - {Brief description} ({Priority}, {Status})
- [[document-name-5]] - {Brief description} ({Priority}, {Status})
- [[document-name-6]] - {Brief description} ({Priority}, {Status})

---

## Quick Reference

### High-Priority Documents (P0/P1)

Critical documents that should be reviewed first:

1. [[p0-document-1]] - {One-line description}
2. [[p0-document-2]] - {One-line description}
3. [[p1-document-1]] - {One-line description}

### Recently Updated

Documents updated in the last 30 days:

- [[recent-doc-1]] - Updated {YYYY-MM-DD}
- [[recent-doc-2]] - Updated {YYYY-MM-DD}

### Deprecated/Superseded

Documents no longer current but kept for historical reference:

- [[deprecated-doc-1]] - Deprecated {YYYY-MM-DD}, Use [[new-doc-1]] instead
- [[superseded-doc-1]] - Superseded by [[replacement-doc-1]]

---

## Statistics

**Document Counts:**
- Total Documents: {count}
- Active: {count}
- Archived: {count}
- Deprecated: {count}
- In Progress: {count}

**Priority Distribution:**
- P0 (Critical): {count}
- P1 (High): {count}
- P2 (Medium): {count}
- P3 (Low): {count}

**Last Major Update:** {YYYY-MM-DD}  
**Index Version:** 1.0  
**Coverage:** {percentage}% of {domain} domain

---

## Cross-References

### Dependencies

This index contains documents that depend on:
- [[dependency-doc-1]] from [[other-index-1]]
- [[dependency-doc-2]] from [[other-index-2]]

### Dependents

Documents in other indexes that depend on this content:
- [[dependent-doc-1]] in [[other-index-3]]
- [[dependent-doc-2]] in [[other-index-4]]

### Related Domains

See also:
- [[related-domain-index-1]] - For {related concern}
- [[related-domain-index-2]] - For {alternative approach}

---

## Maintenance Notes

### Update Triggers

This index should be updated when:
- [ ] New documents added to {scope} domain
- [ ] Document status changes (Active → Deprecated, etc.)
- [ ] Priority adjustments during sprint planning
- [ ] Major architectural changes affecting {scope}
- [ ] Quarterly index audit cycle

### Validation Checklist

Before committing index updates:
- [ ] All document links resolve correctly (no broken links)
- [ ] Metadata block is complete and accurate
- [ ] Priority/status annotations are current
- [ ] Statistics block reflects actual counts
- [ ] No duplicate entries (unless intentional cross-listing)
- [ ] Last updated date is current
- [ ] Related indexes are updated if needed

### Quality Standards

- **Link Format:** Use `[[wikilink]]` format, not markdown links
- **Annotations:** Always include (Priority, Status) for documents
- **Descriptions:** Keep to one line, under 100 characters
- **Sectioning:** Group logically by subsystem, priority, or chronology
- **Depth:** Maximum 3 levels of nesting (Section → Subsection → Items)

---

## Troubleshooting

### Common Issues

**Issue:** Document appears in multiple sections  
**Resolution:** Valid if document has cross-cutting concerns. Add note explaining why.

**Issue:** Broken link to document  
**Resolution:** Check if document was renamed/moved. Update link or add to deprecated section.

**Issue:** Priority conflicts between indexes  
**Resolution:** Priority can be context-dependent. Add context qualifier: (P0-Security) vs (P2-Performance)

**Issue:** Statistics don't match actual counts  
**Resolution:** Run `scripts/audit-index-metadata.py --fix` to auto-update.

**Issue:** Index becoming too large (>200 documents)  
**Resolution:** Split into multiple focused indexes by subsystem or priority level.

---

## Template Usage Instructions

### Creating a New Index

1. **Copy this template** to appropriate subdirectory:
   - `by-area/` for domain-based indexes
   - `by-type/` for document type indexes
   - `by-priority/` for priority-based indexes
   - `by-status/` for lifecycle status indexes
   - `cross-reference/` for relationship indexes

2. **Fill in metadata block** (YAML frontmatter):
   - Set `index_type` to match subdirectory
   - Set `index_scope` to your specific domain/category
   - Update `last_updated` to current date
   - Set `maintainer` to your agent ID or team name

3. **Replace placeholders**:
   - `{Index Name}` → Actual index name
   - `{Brief description}` → Specific descriptions
   - `{Section Name}` → Logical section names
   - `{count}` → Actual document counts
   - `{percentage}` → Estimated coverage

4. **Add your content**:
   - List documents with links, descriptions, priority, status
   - Organize into logical sections
   - Add cross-references and dependencies
   - Update statistics

5. **Validate before committing**:
   ```bash
   python scripts/validate-index.py path/to/your-new-index.md
   ```

### Updating an Existing Index

1. **Add new documents** to appropriate sections
2. **Update metadata block** (`last_updated`, `total_documents`, distributions)
3. **Update statistics block** to reflect changes
4. **Run validation** to check for errors
5. **Commit with descriptive message**: `"Update security-domain-index: Add 3 new threat models"`

### Best Practices

- **Be Specific:** Narrow scope is better than broad scope
- **Stay Current:** Update when documents are added, not just during audits
- **Add Context:** Brief descriptions help users decide if document is relevant
- **Link Liberally:** Cross-reference related indexes and documents
- **Validate Often:** Run automated checks to catch errors early
- **Document Why:** If structure deviates from template, explain in maintenance notes

---

**Template Version:** 1.0  
**Schema Version:** 1.0  
**Created By:** AGENT-002 (Indexes Subdirectory Specialist)  
**Last Updated:** 2024-01-15

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

