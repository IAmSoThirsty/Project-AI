# Index Navigation Plan

## Purpose

This document provides a comprehensive navigation strategy for the Project-AI Obsidian Vault index system. It defines navigation patterns, use cases, workflows, and examples for effectively discovering and accessing vault content through the multi-dimensional index structure.

**Target Audience:** Developers, architects, AI agents, documentation maintainers, and anyone navigating the vault.

**Scope:** Navigation patterns across all five index dimensions (by-area, by-type, by-priority, by-status, cross-reference).

---

## Navigation Patterns

### Pattern 1: Domain-First Navigation (by-area/)

**Use Case:** You're working in a specific functional domain and need to see all related documentation.

**Navigation Flow:**
1. Start at `_indexes/by-area/`
2. Select domain index (e.g., `security-domain-index.md`)
3. Browse sections within domain
4. Follow document links to content
5. Use cross-references to related domains

**Example Workflow: Security Review**

```
1. Open: _indexes/by-area/security-domain-index.md
2. Navigate to: ## Threat Models (P0)
3. Click: [[threat-model-authentication]]
4. Review content
5. Check cross-references: Related to [[architecture-authentication]]
6. Navigate to: _indexes/by-area/architecture-domain-index.md
7. Find: [[architecture-authentication]] for implementation details
```

**Benefits:**
- Complete domain coverage
- Logical grouping by subsystem
- Easy to identify gaps in domain documentation

**Best For:**
- Deep dives into specific areas
- Domain completeness audits
- Onboarding to a functional area

---

### Pattern 2: Document Type Navigation (by-type/)

**Use Case:** You need a specific type of document regardless of domain.

**Navigation Flow:**
1. Start at `_indexes/by-type/`
2. Select document type (e.g., `runbook-type-index.md`)
3. Filter by priority or domain if needed
4. Access relevant documents

**Example Workflow: Incident Response**

```
1. INCIDENT: Production database connection issues
2. Open: _indexes/by-type/runbook-type-index.md
3. Navigate to: ## Database Runbooks (P0)
4. Click: [[runbook-database-failover]]
5. Execute procedures
6. If issue persists, check: ## Troubleshooting Guides
7. Click: [[guide-database-connection-debugging]]
```

**Benefits:**
- Fast access during time-critical situations (incidents)
- Type-specific quality standards
- Cross-domain document discovery

**Best For:**
- Incident response
- Creating new documents (template discovery)
- Documentation audits (ensuring all APIs have specs)

---

### Pattern 3: Priority-Driven Navigation (by-priority/)

**Use Case:** Resource allocation, sprint planning, or focusing on critical work.

**Navigation Flow:**
1. Start at `_indexes/by-priority/`
2. Select priority level (e.g., `p0-critical-priority-index.md`)
3. Review all P0 documents across domains
4. Work down priority levels as capacity allows

**Example Workflow: Sprint Planning**

```
1. Open: _indexes/by-priority/p0-critical-priority-index.md
2. Review: ## Security (P0) - Identify blocking security issues
3. Review: ## Infrastructure (P0) - Identify operational risks
4. Create sprint backlog from P0 items
5. If capacity remains:
   - Open: _indexes/by-priority/p1-high-priority-index.md
   - Add P1 items to backlog
```

**Benefits:**
- Clear prioritization across domains
- Risk identification (P0 gaps)
- Resource allocation optimization

**Best For:**
- Sprint/iteration planning
- Risk assessments
- Critical issue triage
- Emergency situations (focus on P0 only)

---

### Pattern 4: Lifecycle Status Navigation (by-status/)

**Use Case:** Documentation maintenance, finding current vs. deprecated content.

**Navigation Flow:**
1. Start at `_indexes/by-status/`
2. Select status (e.g., `active-status-index.md` or `deprecated-status-index.md`)
3. Review documents in that lifecycle state
4. Take appropriate action (update, archive, replace)

**Example Workflow: Documentation Cleanup**

```
1. Open: _indexes/by-status/deprecated-status-index.md
2. Review: ## Deprecated Architectures
3. For each deprecated doc:
   - Check superseding document exists
   - Verify migration guide available
   - Add deprecation notice to old doc
   - Archive if >1 year old
4. Open: _indexes/by-status/active-status-index.md
5. Audit for stale dates (last_reviewed > 6 months)
6. Add to review queue
```

**Benefits:**
- Prevents use of outdated information
- Identifies maintenance needs
- Tracks document lifecycle

**Best For:**
- Documentation maintenance
- Preventing use of deprecated approaches
- Content lifecycle management
- Archival planning

---

### Pattern 5: Relationship Navigation (cross-reference/)

**Use Case:** Impact analysis, dependency tracking, exploring alternatives.

**Navigation Flow:**
1. Start at `_indexes/cross-reference/`
2. Select relationship index (e.g., `authentication-dependencies-index.md`)
3. Explore dependencies, conflicts, alternatives
4. Follow relationships to related documents

**Example Workflow: Impact Analysis for Architecture Change**

```
1. Planning: Change authentication from session-based to JWT
2. Open: _indexes/cross-reference/authentication-dependencies-index.md
3. Review: ## Dependencies
   - [[user-manager]] depends on current auth
   - [[api-security]] depends on current auth
   - [[session-storage]] depends on current auth
4. Review: ## Dependents
   - 23 documents depend on [[architecture-authentication]]
5. Create impact assessment:
   - Update required: 23 documents
   - Components affected: user-manager, api-security, session-storage
   - Risk level: HIGH (many dependents)
6. Review: ## Alternatives Considered
   - Check if JWT was previously evaluated: [[spike-jwt-stateless]]
   - Read rejection reasons from previous spike
   - Determine if reasons still apply
```

**Benefits:**
- Comprehensive impact analysis
- Avoids repeating rejected approaches
- Documents relationships explicitly

**Best For:**
- Architecture changes
- Refactoring planning
- Understanding system complexity
- Avoiding duplicate work

---

## Multi-Dimensional Navigation Strategies

### Strategy: Progressive Disclosure

Start broad, narrow progressively based on findings.

**Example: New Developer Onboarding**

```
Phase 1: High-Level Overview (Week 1)
1. _indexes/by-priority/p0-critical-priority-index.md
   → Read all P0 documents (30-50 docs)
   → Understand critical systems and constraints

Phase 2: Domain Deep-Dive (Week 2-3)
2. _indexes/by-area/architecture-domain-index.md
   → Understand system design
3. _indexes/by-area/security-domain-index.md
   → Understand security requirements
4. _indexes/by-area/api-domain-index.md
   → Understand API contracts

Phase 3: Practical Knowledge (Week 4)
5. _indexes/by-type/runbook-type-index.md
   → Learn operational procedures
6. _indexes/by-type/guide-type-index.md
   → Learn development workflows

Phase 4: Current State (Ongoing)
7. _indexes/by-status/active-status-index.md
   → Focus only on current, authoritative documents
   → Ignore deprecated content
```

---

### Strategy: Task-Oriented Navigation

Navigate based on specific task requirements.

**Task Categories:**

#### Development Tasks
```
Task: Implement new API endpoint

Navigation Path:
1. _indexes/by-area/api-domain-index.md
   → Find: [[api-design-standards]]
   → Find: [[api-authentication-guide]]
2. _indexes/by-type/specification-type-index.md
   → Find: [[api-specification-template]]
3. _indexes/by-type/guide-type-index.md
   → Find: [[guide-api-development]]
4. _indexes/cross-reference/api-dependencies-index.md
   → Check dependencies on other components
```

#### Troubleshooting Tasks
```
Task: Debug production issue

Navigation Path:
1. _indexes/by-type/runbook-type-index.md
   → Filter: P0 runbooks for relevant subsystem
   → Execute diagnostic procedures
2. If not resolved:
   _indexes/by-type/troubleshooting-guide-type-index.md
   → Deep-dive diagnostics
3. If still not resolved:
   _indexes/cross-reference/{component}-dependencies-index.md
   → Check for dependency issues
```

#### Documentation Tasks
```
Task: Create new architecture decision record

Navigation Path:
1. _indexes/by-type/adr-type-index.md
   → Review existing ADRs for similar decisions
   → Find ADR template
2. _indexes/by-area/architecture-domain-index.md
   → Find related architecture documents
3. _indexes/cross-reference/architecture-alternatives-index.md
   → Check if alternatives were previously evaluated
4. Create new ADR with complete context
```

---

### Strategy: Context Switching

Efficiently switch between different contexts.

**Scenario: Interrupted Work**

```
Context A: Implementing feature X (Security domain)
↓ INTERRUPT ↓
Context B: Production incident (Infrastructure domain)

Fast Context Switch:
1. Bookmark current location in security-domain-index.md
2. Jump to: _indexes/by-priority/p0-critical-priority-index.md
   → Navigate to: ## Infrastructure (P0)
   → Open: [[runbook-production-incident-response]]
3. Handle incident
4. Return to bookmarked location
5. Resume feature work

Alternative (if context will be suspended for >1 day):
1. Open: _indexes/by-status/in-progress-status-index.md
2. Add: [[feature-x-implementation]] (In-Progress)
   → Document: "Paused at step 3: Database schema migration"
3. Handle incident
4. Next day: Check in-progress-status-index.md to resume
```

---

## Navigation by Use Case

### Use Case 1: New Feature Development

**Goal:** Implement new feature with all necessary context.

**Navigation Sequence:**

```
Step 1: Check if similar feature exists
→ _indexes/by-type/specification-type-index.md
→ Search for similar specs

Step 2: Understand architectural constraints
→ _indexes/by-area/architecture-domain-index.md
→ Review relevant ADRs

Step 3: Check security requirements
→ _indexes/by-priority/p0-critical-priority-index.md
→ Review P0 security requirements
→ _indexes/by-area/security-domain-index.md
→ Find threat models and standards

Step 4: Find implementation patterns
→ _indexes/by-type/guide-type-index.md
→ Find development guides

Step 5: Check dependencies
→ _indexes/cross-reference/{domain}-dependencies-index.md
→ Understand component relationships

Step 6: Create design document
→ Use templates from _indexes/templates/
→ Link to all reference documents
```

---

### Use Case 2: Code Review

**Goal:** Comprehensive code review with security, architecture, and standards checks.

**Navigation Sequence:**

```
Step 1: Identify changed domains
→ Example: Changes to authentication module

Step 2: Load domain standards
→ _indexes/by-area/security-domain-index.md
→ Find: [[standard-password-policy]]
→ Find: [[standard-authentication-requirements]]

Step 3: Load security threat model
→ _indexes/by-area/security-domain-index.md
→ Find: [[threat-model-authentication]]
→ Review mitigation requirements

Step 4: Check architectural decisions
→ _indexes/by-type/adr-type-index.md
→ Find: [[adr-005-bcrypt-hashing]]
→ Verify compliance with ADR

Step 5: Review testing requirements
→ _indexes/by-area/testing-domain-index.md
→ Find: [[test-strategy-security]]
→ Verify test coverage

Step 6: Check for deprecated patterns
→ _indexes/by-status/deprecated-status-index.md
→ Ensure code doesn't use deprecated approaches
```

---

### Use Case 3: Security Audit

**Goal:** Comprehensive security review across all domains.

**Navigation Sequence:**

```
Step 1: Start with P0 security requirements
→ _indexes/by-priority/p0-critical-priority-index.md
→ Section: ## Security (P0)
→ Create checklist of all P0 security requirements

Step 2: Deep-dive security domain
→ _indexes/by-area/security-domain-index.md
→ Review all threat models
→ Review all security standards
→ Review previous audit reports

Step 3: Cross-domain security checks
→ _indexes/by-area/api-domain-index.md → Check API security
→ _indexes/by-area/infrastructure-domain-index.md → Check infra security
→ _indexes/by-area/data-domain-index.md → Check data encryption

Step 4: Check compliance status
→ _indexes/by-status/active-status-index.md
→ Verify all security docs are current (not deprecated)

Step 5: Dependency analysis
→ _indexes/cross-reference/security-dependencies-index.md
→ Map security dependencies across system

Step 6: Document findings
→ Create new audit report
→ Link to all reference documents
→ Add to _indexes/by-type/report-type-index.md
```

---

### Use Case 4: Documentation Maintenance

**Goal:** Keep documentation current and remove outdated content.

**Navigation Sequence:**

```
Step 1: Identify stale documents
→ _indexes/by-status/active-status-index.md
→ Filter by last_reviewed > 6 months
→ Create review queue

Step 2: Review deprecated content
→ _indexes/by-status/deprecated-status-index.md
→ For each deprecated doc:
  - Verify superseding doc exists
  - Check if migration guide needed
  - Add deprecation notices

Step 3: Archive old content
→ _indexes/by-status/archived-status-index.md
→ Review documents > 2 years old
→ Archive if no longer relevant

Step 4: Update indexes
→ Update last_updated dates
→ Update statistics blocks
→ Validate links (check for broken references)

Step 5: Run automated validation
→ scripts/validate-index.py --all
→ scripts/check-index-links.py
→ Fix any errors found
```

---

## Advanced Navigation Techniques

### Technique 1: Graph Traversal

Use Obsidian's graph view with index files as hubs.

**Method:**
1. Open Obsidian graph view
2. Filter to show only index files: `path:_indexes/`
3. Indexes appear as high-degree nodes (many outgoing links)
4. Click index node to see connected documents
5. Follow connections to explore relationships

**Use Case:** Understanding system structure visually.

---

### Technique 2: Dataview Queries

Programmatic navigation using Dataview plugin.

**Example Queries:**

```dataview
// Find all P0 security documents
TABLE priority, status, last_reviewed
FROM "_indexes/by-area"
WHERE contains(file.name, "security") AND priority = "P0"
SORT last_reviewed DESC
```

```dataview
// Find recently updated indexes
TABLE last_updated, total_documents, maintainer
FROM "_indexes"
WHERE last_updated >= date(today) - dur(30 days)
SORT last_updated DESC
```

```dataview
// Find indexes with low coverage
TABLE coverage_percentage, index_scope
FROM "_indexes"
WHERE coverage_percentage < 50
SORT coverage_percentage ASC
```

---

### Technique 3: Tag-Based Navigation

Combine index navigation with tag filtering.

**Method:**
1. Use Obsidian tag pane to filter: `#security #P0`
2. Narrow results using index: `_indexes/by-area/security-domain-index.md`
3. Cross-reference with priority index: `_indexes/by-priority/p0-critical-priority-index.md`

**Use Case:** Multi-faceted filtering (e.g., all active P0 security docs).

---

### Technique 4: Search + Index Verification

Use search for quick lookup, verify with index for completeness.

**Method:**
1. Obsidian search: "authentication threat model"
2. Find: `[[threat-model-authentication]]`
3. Verify completeness:
   - Open: `_indexes/by-area/security-domain-index.md`
   - Check: ## Threat Models section
   - Identify related threat models you might have missed
4. Complete context achieved

**Use Case:** Ensuring you haven't missed related documents.

---

## Navigation Efficiency Tips

### Tip 1: Bookmark Frequently Used Indexes

Create Obsidian bookmarks for indexes you use daily:
- `_indexes/by-priority/p0-critical-priority-index.md` (for sprint work)
- Your domain index (e.g., `_indexes/by-area/backend-domain-index.md`)
- `_indexes/by-type/runbook-type-index.md` (for incidents)

### Tip 2: Use Quick Switcher

Obsidian's quick switcher (`Ctrl+O` / `Cmd+O`):
- Type: "security domain" → Jump to security-domain-index.md
- Type: "p0" → Jump to p0-critical-priority-index.md
- Type: "runbook" → Jump to runbook-type-index.md

### Tip 3: Create Custom Index Views

For specialized workflows, create custom indexes:
- `_indexes/custom/my-sprint-index.md` (personal sprint backlog)
- `_indexes/custom/security-audit-2024-q1-index.md` (audit-specific)
- `_indexes/custom/onboarding-index.md` (curated onboarding path)

### Tip 4: Leverage Cross-References

When you find a document, check its cross-reference index:
- Document: `[[architecture-authentication]]`
- Check: `_indexes/cross-reference/authentication-dependencies-index.md`
- Discover: All related documents, dependencies, alternatives

### Tip 5: Priority-First for Time Constraints

When time-limited, always start with priority indexes:
1. `p0-critical-priority-index.md` (must-know)
2. `p1-high-priority-index.md` (should-know)
3. Lower priorities only if time permits

---

## Troubleshooting Navigation Issues

### Issue: Can't Find Relevant Document

**Solutions:**
1. Try multiple index dimensions:
   - Not in security index? Try API index
   - Not in specification index? Try guide index
2. Use Obsidian search as fallback
3. Check deprecated/archived indexes (might be old)
4. Check cross-reference indexes for relationships

### Issue: Too Many Results

**Solutions:**
1. Add priority filter (focus on P0/P1)
2. Add status filter (focus on Active only)
3. Use more specific domain index
4. Check document dates (focus on recent)

### Issue: Conflicting Information

**Solutions:**
1. Check document status:
   - Active > Deprecated
   - Higher priority > Lower priority
   - Newer > Older (if same status)
2. Check cross-reference index for "Conflicts" section
3. Review ADRs for decision rationale
4. Escalate to maintainer if unresolved

### Issue: Missing Expected Document

**Solutions:**
1. Check if document exists but isn't indexed:
   - Use Obsidian search
   - If found, add to appropriate index
2. Check archived/deprecated indexes
3. Check if superseded by newer document
4. Document may not exist yet (gap identified!)

---

## Index Navigation Checklist

Use this checklist for comprehensive navigation:

**Before Starting Task:**
- [ ] Identify primary domain(s) involved
- [ ] Check P0 requirements in priority index
- [ ] Check current standards in domain index
- [ ] Check for deprecated approaches to avoid
- [ ] Review cross-references for dependencies

**During Task:**
- [ ] Consult relevant runbooks/guides
- [ ] Cross-reference specifications
- [ ] Validate against standards
- [ ] Check for related work (avoid duplication)

**After Completing Task:**
- [ ] Update affected indexes if created new documents
- [ ] Add cross-references if new relationships created
- [ ] Mark in-progress items as complete
- [ ] Archive superseded documents

---

**Version:** 1.0
**Last Updated:** 2024-01-15
**Maintainer:** AGENT-002 (Indexes Subdirectory Specialist)
**Related Documents:**
- [[_indexes/README.md]] - Index system overview
- [[_indexes/templates/INDEX_TEMPLATE.md]] - Index file template
- [[_indexes/.index-schema.json]] - Machine-readable schema

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
