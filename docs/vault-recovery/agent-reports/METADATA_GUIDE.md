# Metadata Guide: Structuring Knowledge

**Master Document Metadata and Frontmatter** 📋

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 14 minutes
**Audience:** Documentation contributors, developers
**Prerequisites:** Basic markdown knowledge

---

## Table of Contents

1. [What is Metadata?](#what-is-metadata)
2. [Understanding Frontmatter](#understanding-frontmatter)
3. [Tag Taxonomy Reference](#tag-taxonomy-reference)
4. [Required vs Optional Fields](#required-vs-optional-fields)
5. [Adding Metadata to New Documents](#adding-metadata-to-new-documents)
6. [Metadata Validation](#metadata-validation)
7. [Best Practices](#best-practices)
8. [Common Mistakes](#common-mistakes)
9. [Metadata Schemas](#metadata-schemas)
10. [Examples by Document Type](#examples-by-document-type)

---

## What is Metadata?

**Metadata** is "data about data" - structured information that describes, categorizes, and provides context for your documents.

### Why Metadata Matters

In Project-AI Vault, metadata enables:

✅ **Discovery** - Find documents via tags and queries
✅ **Organization** - Group related documents automatically
✅ **Validation** - Ensure documentation quality and completeness
✅ **Automation** - Generate indexes, dashboards, and reports
✅ **Analytics** - Track documentation coverage and health
✅ **Navigation** - Browse multi-dimensional classifications

### Metadata in Action

**Without Metadata:**
```markdown
# User Authentication System

This document describes the authentication system...
```
→ Hard to find, no context, unclear status

**With Metadata:**
```yaml
---
type: architecture
area: security
component: authentication
status: active
audience: [developer, architect]
priority: critical
tags: [security, authentication, bcrypt, jwt]
version: 2.1.0
created_date: 2026-01-15
updated_date: 2026-04-20
author: AGENT-042
dependencies: [UserManager, PasswordHash]
---

# User Authentication System

This document describes the authentication system...
```
→ Discoverable via 6 methods, clear context, tracked updates

---

## Understanding Frontmatter

**Frontmatter** is YAML metadata at the top of markdown files, enclosed in `---` delimiters.

### Basic Structure

```yaml
---
key: value
list: [item1, item2, item3]
nested:
  subkey: value
---
```

### Rules and Syntax

**1. Delimiters (Required):**

```yaml
---        ← Opening delimiter (first line of file)
# metadata here
---        ← Closing delimiter (must match)
```

**2. Key-Value Pairs:**

```yaml
# Simple values
type: guide
status: active
priority: high

# Quoted values (for special characters)
title: "User's Guide: Getting Started"
description: "A guide for: developers, users"

# Numbers
version: 1.0.0
word_count: 2500

# Booleans
published: true
draft: false

# Dates (ISO 8601 format)
created_date: 2026-04-20
updated_date: 2026-04-20T14:30:00Z
```

**3. Lists (Arrays):**

```yaml
# Inline list
tags: [security, authentication, password]

# Block list (alternative syntax)
tags:
  - security
  - authentication
  - password

# Both are equivalent
```

**4. Nested Objects:**

```yaml
author:
  name: AGENT-048
  role: Documentation Specialist
  contact: agent048@project-ai.local

validation:
  schema: metadata-schema-v1.json
  status: passed
  last_check: 2026-04-20
```

**5. Multi-line Values:**

```yaml
# Preserve line breaks (|)
description: |
  This is a long description
  that spans multiple lines
  and preserves formatting.

# Fold into single line (>)
summary: >
  This is a long summary
  that will be folded
  into a single line.
```

### Common Pitfalls

**❌ Wrong:**
```yaml
---
type: guide  # This is a comment (won't be parsed)
tags: security authentication  # Not a valid list
status: "active'  # Mismatched quotes
created_date: 04/20/2026  # Wrong date format
---
```

**✅ Correct:**
```yaml
---
type: guide
tags: [security, authentication]
status: active
created_date: 2026-04-20
---
```

---

## Tag Taxonomy Reference

Project-AI uses **85+ standardized tags** across **7 categories**. Tags are the primary classification mechanism.

### Tag Categories Overview

| Category | Required | Count | Purpose |
|----------|----------|-------|---------|
| **area** | 1-3 tags | Yes | Domain/discipline (architecture, security, documentation) |
| **type** | 1-2 tags | Yes | Document type (guide, reference, architecture) |
| **component** | 0-5 tags | No | System component (agent, gui, core-system) |
| **status** | 1 tag | Yes | Lifecycle state (active, draft, deprecated) |
| **audience** | 1-4 tags | Yes | Target readers (developer, user, architect) |
| **priority** | 0-1 tag | Recommended | Urgency level (critical, high, medium, low) |
| **special** | 0-10 tags | No | Special markers (breaking-change, security-critical) |

### Area Tags (1-3 required)

**Purpose:** Define the primary domain or discipline

**Complete List:**

```yaml
Core Areas:
- architecture      # System design, patterns, technical architecture
- security          # Security, authentication, cryptography, compliance
- documentation     # Documentation, guides, knowledge management
- development       # Development processes, workflows, tooling
- testing           # Testing, QA, validation, verification
- deployment        # Deployment, DevOps, CI/CD, infrastructure
- integration       # Integration, APIs, third-party services

Specialized Areas:
- ai-systems        # AI/ML systems, agents, intelligence
- ethics            # Ethical AI, governance, Asimov's Laws
- data-management   # Data storage, persistence, databases
- ui-ux             # User interface, user experience, design
- performance       # Performance optimization, profiling, benchmarking
- monitoring        # Observability, logging, metrics, alerting

Domain Areas:
- business          # Business logic, domain models
- operations        # Operations, maintenance, support
- compliance        # Regulatory compliance, standards, policies
```

**Usage Rules:**

- ✅ Use 1-3 area tags per document
- ✅ Primary area comes first in frontmatter
- ✅ Use specialized areas when appropriate
- ❌ Don't use more than 3 area tags

**Examples:**

```yaml
# Single area (simple document)
area: documentation

# Multiple areas (cross-cutting concern)
area: [security, architecture, deployment]

# Specialized + Core
area: [ai-systems, ethics, architecture]
```

### Type Tags (1-2 required)

**Purpose:** Define document structure and format

**Complete List:**

```yaml
Documentation Types:
- guide             # Step-by-step guides, tutorials, how-tos
- reference         # Reference documentation, API docs, schemas
- architecture      # Architecture decisions, design docs, ADRs
- specification     # Requirements, specifications, contracts
- report            # Analysis reports, audits, summaries
- index             # MOCs, navigation hubs, curated lists
- template          # Document templates, boilerplates

Technical Types:
- code-documentation  # Code comments, inline docs, docstrings
- api-documentation   # API reference, endpoints, schemas
- troubleshooting     # Problem-solving, debugging guides
- changelog           # Version history, release notes
- roadmap             # Future plans, feature roadmaps
```

**Usage Rules:**

- ✅ Always include at least 1 type tag
- ✅ Use 2 types if document serves dual purpose
- ❌ Don't mix conflicting types (guide + reference usually conflict)

**Examples:**

```yaml
# Single type
type: guide

# Dual type (valid combination)
type: [reference, troubleshooting]

# Architecture decision record
type: [architecture, specification]
```

### Component Tags (0-5 optional)

**Purpose:** Identify specific system components

**Complete List:**

```yaml
Core Components:
- agent             # AI agents (oversight, planner, validator, explainability)
- core-system       # Core business logic (AIPersona, FourLaws, Memory, etc.)
- gui               # GUI components (LeatherBook, Dashboard, Panels)
- cli               # Command-line interface components

Subsystems:
- authentication    # User authentication, password management
- authorization     # Permissions, access control, RBAC
- encryption        # Cryptography, key management
- storage           # Data persistence, file systems
- networking        # Network communication, APIs, HTTP
- templating        # Template engines, document generation

Infrastructure:
- database          # Database systems, queries, migrations
- cache             # Caching layers, Redis, in-memory caches
- messaging         # Message queues, event buses
- logging           # Logging systems, log aggregation
- monitoring        # Monitoring tools, dashboards, alerts
```

**Usage Rules:**

- ✅ Use 0-5 component tags (optional but recommended)
- ✅ Only tag components directly discussed in document
- ❌ Don't tag every component mentioned in passing

**Examples:**

```yaml
# No component tags (general documentation)
component: []

# Single component
component: authentication

# Multiple components (integration documentation)
component: [authentication, authorization, encryption]

# Core systems focus
component: [agent, core-system, gui]
```

### Status Tags (1 required)

**Purpose:** Track document lifecycle state

**Complete List:**

```yaml
- active            # Current, maintained, production-ready
- draft             # Work in progress, not yet reviewed
- review            # Under review, pending approval
- approved          # Reviewed and approved, ready for publication
- deprecated        # Outdated, replaced, scheduled for removal
- archived          # Historical reference, no longer active
- planned           # Future documentation, not yet started
```

**Lifecycle Flow:**

```
planned → draft → review → approved → active
                                        ↓
                                   deprecated → archived
```

**Usage Rules:**

- ✅ Exactly 1 status tag required
- ✅ Update status when document state changes
- ⚠️ Never leave as 'draft' indefinitely

**Examples:**

```yaml
# New document
status: draft

# Production document
status: active

# Being replaced
status: deprecated
```

### Audience Tags (1-4 required)

**Purpose:** Define target readers

**Complete List:**

```yaml
- user              # End users, non-technical readers
- developer         # Software developers, engineers
- architect         # System architects, technical leads
- contributor       # Documentation contributors, open-source contributors
- operator          # DevOps, operations, system administrators
- security-engineer # Security specialists, auditors
- data-scientist    # ML engineers, data scientists
- executive         # Management, executives, decision-makers
```

**Usage Rules:**

- ✅ At least 1 audience tag required
- ✅ Use 1-4 tags for multi-audience documents
- ✅ Primary audience first in list

**Examples:**

```yaml
# Single audience
audience: developer

# Multi-audience (prioritized)
audience: [developer, architect, security-engineer]

# Broad audience
audience: [user, developer, contributor, operator]
```

### Priority Tags (0-1 recommended)

**Purpose:** Indicate urgency or importance

**Complete List:**

```yaml
- critical          # Must read, blocking issues, security-critical
- high              # Important, should read soon
- medium            # Normal priority, read when relevant
- low               # Optional, nice-to-have, reference
```

**Usage Rules:**

- ✅ Use 0-1 priority tag
- ✅ Reserve "critical" for truly critical items
- ❌ Don't mark everything as "high" or "critical"

**Examples:**

```yaml
# Critical security documentation
priority: critical

# Standard documentation
priority: medium

# No priority (defaults to medium)
priority: null
```

### Special Tags (0-10 optional)

**Purpose:** Mark special conditions or characteristics

**Complete List:**

```yaml
Urgency Markers:
- breaking-change   # Breaking API/interface changes
- security-critical # Security-sensitive content
- requires-action   # Action required from readers

Quality Markers:
- incomplete        # Missing sections, needs completion
- needs-review      # Requires expert review
- outdated          # May contain outdated information

Process Markers:
- auto-generated    # Generated by scripts/tools
- external-dependency  # Depends on external systems
- experimental      # Experimental features, unstable APIs

Domain Markers:
- python            # Python-specific content
- javascript        # JavaScript-specific content
- docker            # Docker/containerization related
- windows           # Windows-specific
- linux             # Linux-specific
```

**Usage Rules:**

- ✅ Use 0-10 special tags
- ✅ Only use when truly applicable
- ❌ Don't overuse - devalues the signal

**Examples:**

```yaml
# Security advisory
tags: [security-critical, requires-action]

# Breaking change announcement
tags: [breaking-change, requires-review]

# Generated documentation
tags: [auto-generated, python]
```

---

## Required vs Optional Fields

### Minimal Valid Frontmatter

**Absolute Minimum:**

```yaml
---
type: guide
area: documentation
status: active
audience: developer
tags: [documentation]
---
```

### Recommended Standard

**Production Quality:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [developer, contributor]
priority: high
tags: [documentation, metadata, frontmatter, yaml]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
---
```

### Field Definitions

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `type` | ✅ Yes | String/Array | Document type | `guide` |
| `area` | ✅ Yes | String/Array | Domain/discipline | `security` |
| `status` | ✅ Yes | String | Lifecycle state | `active` |
| `audience` | ✅ Yes | Array | Target readers | `[developer]` |
| `tags` | ✅ Yes | Array | All classification tags | `[security, auth]` |
| `component` | ⚠️ Recommended | String/Array | System component | `authentication` |
| `priority` | ⚠️ Recommended | String | Importance level | `high` |
| `version` | ⚠️ Recommended | String | Document version | `1.0.0` |
| `created_date` | ⚠️ Recommended | Date | Creation date | `2026-04-20` |
| `updated_date` | ⚠️ Recommended | Date | Last update date | `2026-04-20` |
| `author` | ⚠️ Recommended | String | Primary author | `AGENT-048` |
| `title` | ❌ Optional | String | Display title | `"Metadata Guide"` |
| `description` | ❌ Optional | String | Brief summary | `"Guide to metadata"` |
| `dependencies` | ❌ Optional | Array | Related documents | `[schema.json]` |
| `reviewed_by` | ❌ Optional | String | Reviewer | `AGENT-001` |
| `review_date` | ❌ Optional | Date | Review date | `2026-04-15` |
| `word_count` | ❌ Optional | Number | Approximate count | `2500` |

---

## Adding Metadata to New Documents

### Method 1: Use Templates (Recommended)

**Steps:**

1. Create new note (`Ctrl+N`)
2. Name your file
3. Open command palette (`Ctrl+P`)
4. Type: "Templater: Insert template"
5. Choose appropriate template
6. Template inserts complete frontmatter
7. Review and customize fields

**Example:** Creating an architecture document

```
Template: architecture-doc-adr.md
→ Auto-generates:
---
type: architecture
area: architecture
component: []
status: draft
audience: [architect, developer]
priority: high
tags: [architecture, adr, decision-record]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-XXX
decision_id: ADR-XXX
---
```

**See:** [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) for full template usage

### Method 2: Copy from Similar Document

**Steps:**

1. Find similar document
2. Copy its frontmatter
3. Create new document
4. Paste frontmatter
5. Modify fields appropriately

### Method 3: Manual Creation

**Steps:**

1. Create new document
2. Type `---` on first line
3. Press Enter
4. Add field: value pairs
5. Type `---` on closing line
6. Validate syntax

**Starter Template:**

```yaml
---
type:
area:
component:
status: draft
audience: []
priority:
tags: []
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author:
---
```

---

## Metadata Validation

### Automatic Validation

**Dataview Validation Query:**

```dataviewjs
// Find documents with missing required fields
const requiredFields = ['type', 'area', 'status', 'audience', 'tags'];

dv.table(
  ["Document", "Missing Fields"],
  dv.pages()
    .where(p => {
      return requiredFields.some(field => !p[field]);
    })
    .map(p => {
      const missing = requiredFields.filter(f => !p[f]);
      return [p.file.link, missing.join(", ")];
    })
);
```

### Schema Validation

**Using JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "area", "status", "audience", "tags"],
  "properties": {
    "type": {
      "oneOf": [
        {"type": "string"},
        {"type": "array", "items": {"type": "string"}}
      ],
      "enum": ["guide", "reference", "architecture", "..."]
    },
    "status": {
      "type": "string",
      "enum": ["active", "draft", "review", "approved", "deprecated", "archived"]
    },
    "tags": {
      "type": "array",
      "minItems": 1,
      "items": {"type": "string"}
    }
  }
}
```

**See:** `schemas/metadata-schema-v1.json` for complete schema

### Manual Validation Checklist

**Before Publishing:**

- [ ] Frontmatter enclosed in `---` delimiters
- [ ] Required fields present (type, area, status, audience, tags)
- [ ] Status is valid value (active/draft/review/etc.)
- [ ] Tags match official taxonomy
- [ ] Dates in ISO 8601 format (YYYY-MM-DD)
- [ ] Arrays use square brackets: `[item1, item2]`
- [ ] No syntax errors (run preview mode to check)
- [ ] Version number follows semantic versioning

---

## Best Practices

### 1. Be Consistent

**Do:**
```yaml
# All dates in same format
created_date: 2026-04-20
updated_date: 2026-04-20
review_date: 2026-04-15
```

**Don't:**
```yaml
# Inconsistent date formats
created_date: 2026-04-20
updated_date: 04/20/2026
review_date: April 20, 2026
```

### 2. Use Official Tags Only

**Do:**
```yaml
tags: [architecture, security, authentication]
```

**Don't:**
```yaml
tags: [arch, sec, user-auth, custom-tag]
```

**Reference:** [TAG_TAXONOMY.md](TAG_TAXONOMY.md)

### 3. Update Dates on Changes

**Always update `updated_date` when modifying content:**

```yaml
# Before editing
updated_date: 2026-04-15

# After editing (today is 2026-04-20)
updated_date: 2026-04-20
```

### 4. Version Semantically

Follow **Semantic Versioning** (semver):

```
Major.Minor.Patch
  ↓     ↓     ↓
 1  .  2  .  3

Major: Breaking changes, restructuring
Minor: New sections, significant additions
Patch: Typos, minor corrections, clarifications
```

**Examples:**

```yaml
# Initial version
version: 1.0.0

# Added new section (minor)
version: 1.1.0

# Fixed typos (patch)
version: 1.1.1

# Complete rewrite (major)
version: 2.0.0
```

### 5. Tag Hierarchically

**Tag from general to specific:**

```yaml
# Good: General → Specific
tags: [architecture, security, authentication, bcrypt]

# Bad: Random order
tags: [bcrypt, architecture, authentication, security]
```

### 6. Use Arrays Consistently

**Pick one style and stick to it:**

```yaml
# Style 1: Inline (recommended for short lists)
tags: [architecture, security]
audience: [developer, architect]

# Style 2: Block (for long lists)
tags:
  - architecture
  - security
  - authentication
  - authorization
  - encryption
```

### 7. Document Dependencies

**List related documents:**

```yaml
dependencies:
  - METADATA_SCHEMA.md
  - TAG_TAXONOMY.md
  - TEMPLATE_GUIDE.md
```

### 8. Track Authorship

**For multi-author documents:**

```yaml
author: AGENT-048
contributors:
  - AGENT-017
  - AGENT-036
  - AGENT-042
```

---

## Common Mistakes

### Mistake 1: Missing Delimiters

**❌ Wrong:**
```markdown
type: guide
area: documentation
status: active

# Document Title
```

**✅ Correct:**
```yaml
---
type: guide
area: documentation
status: active
---

# Document Title
```

### Mistake 2: Invalid YAML Syntax

**❌ Wrong:**
```yaml
---
tags: [security authentication]  # Missing comma
status: 'active"                  # Mismatched quotes
created_date: 04-20-2026         # Wrong format
---
```

**✅ Correct:**
```yaml
---
tags: [security, authentication]
status: active
created_date: 2026-04-20
---
```

### Mistake 3: Non-Standard Tags

**❌ Wrong:**
```yaml
---
tags: [auth, sec, ui, custom-thing]
---
```

**✅ Correct:**
```yaml
---
tags: [authentication, security, ui-ux]
---
```

**Check:** [TAG_TAXONOMY.md](TAG_TAXONOMY.md) for valid tags

### Mistake 4: Wrong Status Value

**❌ Wrong:**
```yaml
status: published
status: completed
status: done
```

**✅ Correct:**
```yaml
status: active    # or: draft, review, approved, deprecated, archived
```

### Mistake 5: Audience Not an Array

**❌ Wrong:**
```yaml
audience: developer
```

**✅ Correct:**
```yaml
audience: [developer]
# or
audience:
  - developer
```

### Mistake 6: Forgetting to Update

**❌ Wrong:**
```yaml
# Document edited today (2026-04-20)
updated_date: 2026-01-15  # Old date never updated!
```

**✅ Correct:**
```yaml
# Always update when editing
updated_date: 2026-04-20
```

---

## Metadata Schemas

### Schema Location

**Files:**
- `schemas/metadata-schema-v1.json` - JSON Schema validator
- `METADATA_SCHEMA.md` - Human-readable schema documentation

### Using Schemas

**Validation Tools:**

1. **JSON Schema Validator Plugin** (Obsidian)
2. **Dataview Queries** (built-in validation)
3. **CI/CD Pipeline** (automated validation)

**Manual Validation:**

```bash
# Using Python jsonschema
python scripts/validate-metadata.py
```

---

## Examples by Document Type

### Guide Document

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [user, developer]
priority: high
tags: [guide, tutorial, getting-started, obsidian]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 3500
---
```

### Architecture Document

```yaml
---
type: architecture
area: [architecture, security]
component: [authentication, authorization]
status: active
audience: [architect, developer, security-engineer]
priority: critical
tags: [architecture, adr, security, authentication, design-pattern]
version: 2.1.0
created_date: 2026-01-15
updated_date: 2026-04-20
author: AGENT-042
reviewed_by: AGENT-001
review_date: 2026-04-18
decision_id: ADR-023
---
```

### Reference Document

```yaml
---
type: reference
area: development
component: [api, authentication]
status: active
audience: [developer]
priority: high
tags: [reference, api, authentication, rest, endpoints]
version: 3.2.1
created_date: 2025-11-10
updated_date: 2026-04-20
author: AGENT-035
api_version: v2
---
```

### Agent Report

```yaml
---
type: report
area: [documentation, architecture]
component: vault
status: active
audience: [architect, developer, contributor]
priority: high
tags: [agent-report, completion-report, vault, obsidian]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
agent_id: AGENT-048
mission: Vault Documentation Specialist
phase: 3
deliverables_count: 14
word_count: 21800
---
```

### Troubleshooting Guide

```yaml
---
type: [guide, troubleshooting]
area: [operations, documentation]
component: vault
status: active
audience: [user, developer, operator]
priority: medium
tags: [troubleshooting, guide, problems, solutions, obsidian]
version: 1.2.0
created_date: 2026-03-10
updated_date: 2026-04-20
author: AGENT-038
contributors: [AGENT-012, AGENT-017]
issue_count: 25
---
```

---

## Summary Checklist

**Before Publishing Any Document:**

- [ ] Frontmatter present with `---` delimiters
- [ ] All required fields included (type, area, status, audience, tags)
- [ ] Tags match official taxonomy
- [ ] Dates in YAML format (YYYY-MM-DD)
- [ ] Status is valid value
- [ ] Arrays use brackets and commas
- [ ] Version follows semantic versioning
- [ ] No YAML syntax errors (test in preview mode)
- [ ] Updated date reflects today's date
- [ ] Author field populated

**Monthly Maintenance:**

- [ ] Review and update outdated documents
- [ ] Validate all metadata against schema
- [ ] Check for deprecated tags
- [ ] Update status fields as needed
- [ ] Run metadata quality queries

---

**Next Steps:**

- **Practice:** Add metadata to 3 documents using different templates
- **Read:** [TAG_REFERENCE.md](TAG_REFERENCE.md) for complete tag definitions
- **Validate:** Run metadata validation queries from [VAULT_HEALTH_DASHBOARD.md](VAULT_HEALTH_DASHBOARD.md)
- **Reference:** Bookmark `schemas/metadata-schema-v1.json` for validation

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [developer, contributor]
priority: high
tags: [metadata, frontmatter, yaml, tags, taxonomy, validation]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 4200
dependencies:
  - TAG_TAXONOMY.md
  - schemas/metadata-schema-v1.json
  - TEMPLATE_GUIDE.md
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
