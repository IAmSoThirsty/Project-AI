# Index Organization System

## Overview

The `_indexes/` directory provides a comprehensive navigation and organization system for the Project-AI Obsidian Vault. This system enables multi-dimensional access to vault content through various organizational perspectives, ensuring knowledge is discoverable regardless of your current context or mental model.

**Purpose:** This index system serves as the primary navigation infrastructure for 2,000+ vault documents across 40+ categories. It provides curated pathways through the knowledge graph, reducing cognitive load and enabling rapid context switching between architectural concerns, development priorities, and operational domains.

**Philosophy:** Rather than forcing a single hierarchical organization (which inevitably breaks down for cross-cutting concerns), this system provides multiple orthogonal index dimensions. A single document about "API Authentication" can be discovered via security indexes, API indexes, implementation priority indexes, or architectural pattern indexes.

## Directory Structure

### Primary Index Dimensions

```
_indexes/
├── by-area/           # Domain-based organization (Security, Architecture, Infrastructure, etc.)
├── by-type/           # Document type organization (Guides, References, Decisions, etc.)
├── by-priority/       # Priority-based organization (P0-Critical, P1-High, P2-Medium, P3-Low)
├── by-status/         # Lifecycle status (Active, Archived, Deprecated, Planned)
├── cross-reference/   # Relationship-based indexes (Dependencies, Conflicts, Alternatives)
├── templates/         # Index file templates for consistency
└── README.md          # This document
```

### Organization Principles

1. **Multi-Dimensional Access**: Content accessible from multiple perspectives
2. **Semantic Clarity**: Index names clearly indicate scope and purpose
3. **Mechanical Precision**: Consistent structure enables automation
4. **Human-Optimized**: Designed for rapid scanning and navigation
5. **Machine-Parseable**: Structured for tooling and validation

## Index Types and Usage

### by-area/: Domain-Based Indexes

**Purpose:** Organize content by architectural domain or functional area.

**When to Use:**
- You're working within a specific domain (e.g., security, API design)
- You need to see all documents related to a functional area
- You want to assess domain completeness or identify gaps

**Example Indexes:**
- `security-index.md` - All security-related documents (threat models, audits, standards)
- `architecture-index.md` - Architecture decisions, patterns, design documents
- `api-index.md` - API specifications, endpoints, integration guides
- `infrastructure-index.md` - Deployment, scaling, monitoring, DevOps
- `testing-index.md` - Test strategies, coverage reports, QA documentation
- `governance-index.md` - Policies, compliance, audit trails

**Structure Example:**
```markdown
# Security Domain Index

## Threat Models
- [[threat-model-authentication]] (P0, Active)
- [[threat-model-data-encryption]] (P0, Active)

## Security Audits
- [[security-audit-2024-Q1]] (P1, Completed)
- [[security-audit-api-surface]] (P1, In-Progress)

## Security Standards
- [[standard-password-policy]] (P0, Active)
- [[standard-encryption-requirements]] (P0, Active)
```

### by-type/: Document Type Indexes

**Purpose:** Organize content by document archetype or format.

**When to Use:**
- You need a specific type of document (e.g., all runbooks during incident response)
- You're auditing documentation completeness (ensuring all APIs have specifications)
- You want to apply type-specific quality standards

**Document Types:**
- **Specifications**: Formal technical specifications (API specs, data schemas)
- **Guides**: How-to guides, tutorials, walkthroughs
- **References**: Quick reference sheets, cheat sheets, API documentation
- **Decisions**: Architecture Decision Records (ADRs), design decisions
- **Reports**: Audit reports, security assessments, performance analyses
- **Runbooks**: Operational procedures, incident response playbooks
- **Standards**: Coding standards, security policies, best practices
- **Templates**: Reusable document templates

**Structure Example:**
```markdown
# Architecture Decision Records Index

## Active ADRs
- [[adr-001-python-stack]] - Python as primary backend language
- [[adr-002-pyqt6-gui]] - PyQt6 for desktop UI framework
- [[adr-003-json-persistence]] - JSON for configuration persistence

## Superseded ADRs
- [[adr-legacy-001-flask-only]] - Superseded by ADR-002 (PyQt6 adoption)
```

### by-priority/: Priority-Based Indexes

**Purpose:** Organize content by business/technical priority for execution planning.

**When to Use:**
- Sprint planning or roadmap prioritization
- Incident triage (finding P0 runbooks immediately)
- Resource allocation decisions
- Risk assessment (identifying P0 gaps)

**Priority Levels:**
```
P0 (Critical):  System-critical, blocking, security-critical
P1 (High):      Important but not blocking, significant value
P2 (Medium):    Useful but not urgent, incremental improvements
P3 (Low):       Nice-to-have, future considerations
```

**Structure Example:**
```markdown
# P0 Critical Priority Index

## Security (P0)
- [[threat-model-authentication]] - Auth system threat model
- [[standard-password-policy]] - Password security requirements
- [[runbook-security-incident]] - Security incident response

## Infrastructure (P0)
- [[runbook-database-failover]] - Database failover procedure
- [[monitoring-alert-thresholds]] - Critical alerting configuration

## Compliance (P0)
- [[policy-data-retention]] - Legal data retention requirements
```

### by-status/: Lifecycle Status Indexes

**Purpose:** Track document lifecycle and maintenance state.

**When to Use:**
- Identifying stale or outdated documentation
- Finding deprecated approaches to avoid
- Planning documentation updates
- Archiving superseded content

**Status Values:**
```
Active:      Current, maintained, authoritative
Planned:     Approved but not yet implemented
In-Progress: Being actively developed/written
Review:      Complete but awaiting review/approval
Archived:    Historical reference, no longer current
Deprecated:  Do not use, kept for historical context
Superseded:  Replaced by newer document (link included)
```

**Structure Example:**
```markdown
# Deprecated Documents Index

## Deprecated Architectures
- [[architecture-flask-monolith]]
  - Status: Deprecated (2024-01)
  - Reason: Replaced by PyQt6 desktop + Flask API hybrid
  - Superseded By: [[architecture-current-hybrid]]

## Deprecated APIs
- [[api-v1-specification]]
  - Status: Deprecated (2024-03)
  - Reason: Security vulnerabilities, poor design
  - Superseded By: [[api-v2-specification]]
  - Migration Guide: [[guide-api-v1-to-v2-migration]]
```

### cross-reference/: Relationship Indexes

**Purpose:** Document dependencies, conflicts, and relationships between documents.

**When to Use:**
- Impact analysis (what breaks if we change X?)
- Conflict resolution (which documents contradict?)
- Prerequisite tracking (what must be read first?)
- Alternative exploration (what other approaches exist?)

**Relationship Types:**
- **Dependencies**: Document A requires understanding Document B
- **Conflicts**: Documents that contradict or compete
- **Alternatives**: Different approaches to the same problem
- **Complements**: Documents that work together
- **Prerequisites**: Required reading order

**Structure Example:**
```markdown
# Authentication Architecture Relationships

## Dependencies
[[architecture-authentication]] depends on:
- [[threat-model-authentication]] (security requirements)
- [[standard-password-policy]] (password rules)
- [[adr-005-bcrypt-hashing]] (implementation decision)

## Alternatives Considered
- [[spike-oauth2-only]] (rejected: complexity)
- [[spike-jwt-stateless]] (rejected: session management needed)
- [[spike-magic-link]] (rejected: user experience)

## Related Documents
- [[guide-user-registration]] (implements this architecture)
- [[runbook-password-reset]] (operational procedure)
- [[test-strategy-auth]] (testing approach)
```

## Index File Template

All index files follow a consistent structure defined in `templates/INDEX_TEMPLATE.md`:

```yaml
---
index_type: "by-area" | "by-type" | "by-priority" | "by-status" | "cross-reference"
index_scope: "security" | "architecture" | "api" | etc.
last_updated: YYYY-MM-DD
maintainer: "Agent ID or team name"
total_documents: 42
metadata_schema_version: "1.0"
---

# [Index Name]

## Overview
[2-3 sentence description of index scope and purpose]

## Contents
[Organized sections with document links and metadata]

## Statistics
- Total Documents: 42
- By Priority: P0(5), P1(12), P2(18), P3(7)
- By Status: Active(30), Archived(10), Deprecated(2)
- Last Updated: 2024-01-15
```

## Naming Conventions

### Index File Names

**Pattern:** `{scope}-{type}-index.md`

**Examples:**
- `security-domain-index.md` (by-area)
- `adr-type-index.md` (by-type)
- `p0-critical-priority-index.md` (by-priority)
- `active-status-index.md` (by-status)
- `authentication-dependencies-index.md` (cross-reference)

**Rules:**
1. Lowercase with hyphens (kebab-case)
2. Descriptive and unambiguous
3. Include index type suffix (`-index.md`)
4. Scope comes first, type second
5. Maximum 50 characters (excluding `.md`)

### Section Headers

**Pattern:** `## {Category} ({Status/Priority if applicable})`

**Examples:**
```markdown
## Threat Models (P0)
## Architecture Decisions (Active)
## Deprecated APIs
## Related Documents
```

## Index Maintenance

### Update Frequency

- **by-area indexes**: Update when new documents added to domain (event-driven)
- **by-priority indexes**: Review weekly during sprint planning
- **by-status indexes**: Update immediately when document status changes
- **cross-reference indexes**: Update when relationships change or conflicts identified

### Automated Validation

The `.index-schema.json` schema enables automated validation:

```bash
# Validate index structure
python scripts/validate-index.py _indexes/by-area/security-domain-index.md

# Check for broken links
python scripts/check-index-links.py _indexes/

# Verify metadata completeness
python scripts/audit-index-metadata.py _indexes/
```

### Quality Checklist

- [ ] All linked documents exist
- [ ] Metadata is complete and accurate
- [ ] Priority/status annotations are current
- [ ] No duplicate entries
- [ ] Sections are logically organized
- [ ] Statistics block is accurate
- [ ] Last updated date is current

## Integration with Obsidian

### Graph View

Indexes create high-degree nodes in the Obsidian graph, serving as navigation hubs:
- Index files appear as central nodes
- Content documents cluster around indexes
- Multiple indexes create overlapping clusters (multi-dimensional organization)

### Dataview Queries

Indexes support dynamic queries:

```dataview
TABLE priority, status, maintainer
FROM "_indexes/by-area"
WHERE contains(file.name, "security")
SORT priority ASC
```

### Tag Integration

Indexes complement but don't replace tags:
- **Tags**: Fine-grained content classification (e.g., #security/authentication)
- **Indexes**: Curated navigation and relationships
- **Best Practice**: Use both for maximum discoverability

## Troubleshooting

### Index Not Appearing in Search

**Cause:** File not in vault root or `_indexes/` directory.

**Solution:** Ensure file is in correct subdirectory: `_indexes/by-area/`, `_indexes/by-type/`, etc.

### Broken Links in Index

**Cause:** Referenced document was moved, renamed, or deleted.

**Solution:** Run `scripts/check-index-links.py` to identify and fix broken links.

### Duplicate Entries

**Cause:** Document added to index multiple times or exists in multiple sections.

**Solution:** Valid if document belongs in multiple sections (cross-cutting concern). Otherwise, remove duplicate and add cross-reference.

### Outdated Statistics

**Cause:** Manual statistics block not updated after adding/removing documents.

**Solution:** Run `scripts/audit-index-metadata.py --fix` to auto-update statistics.

### Conflicting Priority/Status

**Cause:** Document has different priority in different indexes.

**Solution:** Priority is context-dependent (a document can be P0 for security but P2 for performance). Ensure annotations include context: `(P0-Security)` vs `(P2-Performance)`.

## Best Practices

### For Index Creators

1. **Start with Template**: Always use `templates/INDEX_TEMPLATE.md`
2. **Be Specific**: Narrow scope is better than broad (create multiple focused indexes)
3. **Add Context**: Include priority, status, and brief description for each entry
4. **Maintain Sections**: Use logical grouping (by subsystem, by priority, chronologically)
5. **Update Proactively**: Update index when adding related documents, not just during audits

### For Index Users

1. **Multi-Index Lookup**: Check multiple index types for comprehensive understanding
2. **Follow Relationships**: Use cross-reference indexes to explore related content
3. **Respect Priority**: P0 indexes should be read completely, P3 can be skimmed
4. **Check Status**: Always verify document status before relying on deprecated content
5. **Contribute Updates**: If you find a gap or error, update the index immediately

### For System Maintainers

1. **Schema Enforcement**: Validate all indexes against `.index-schema.json` weekly
2. **Automated Audits**: Run link checks and metadata audits daily in CI/CD
3. **Prune Obsolete**: Archive indexes for deprecated areas quarterly
4. **Monitor Coverage**: Ensure all vault documents appear in at least one index
5. **Document Decisions**: When creating new index types, document rationale in this README

## Governance

**Index Ownership:** Each index must have a designated maintainer (human or agent).

**Change Control:** Structural changes to index system (new index types, schema changes) require architecture review.

**Quality Gates:** All index updates must pass automated validation before merge.

**Audit Trail:** Index changes are tracked in git history with descriptive commit messages.

## Future Enhancements

Planned but not yet implemented:

1. **Automated Index Generation**: Bot to auto-generate indexes from document metadata
2. **Index Diff Reports**: Show changes between index versions
3. **Smart Recommendations**: Suggest related documents based on current context
4. **Visual Index Maps**: Graph visualization of index relationships
5. **Search Integration**: Deep search within indexed content only

---

**Version:** 1.0
**Last Updated:** 2024-01-15
**Maintainer:** AGENT-002 (Indexes Subdirectory Specialist)
**Total Index Types:** 5
**Estimated Vault Coverage:** 2000+ documents across 40+ categories

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
