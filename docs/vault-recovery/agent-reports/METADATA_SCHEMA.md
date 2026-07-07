# Project-AI Documentation Vault Metadata Schema

**Version:** 2.0.0  
**Status:** Production  
**Last Updated:** 2026-04-20  
**Schema Maintainer:** Architecture Team  
**Validation:** JSON Schema v2020-12 + YAML Schema

---

## Table of Contents

1. [Purpose and Scope](#purpose-and-scope)
2. [Schema Architecture](#schema-architecture)
3. [Core Field Reference](#core-field-reference)
4. [Document Type Taxonomy](#document-type-taxonomy)
5. [Data Type Specifications](#data-type-specifications)
6. [Validation Rules](#validation-rules)
7. [Relationship Specifications](#relationship-specifications)
8. [Complete Examples](#complete-examples)
9. [Schema Versioning Policy](#schema-versioning-policy)
10. [Migration Guide](#migration-guide)
11. [Best Practices](#best-practices)
12. [Frequently Asked Questions](#frequently-asked-questions)

---

## Purpose and Scope

### Mission Statement

The Project-AI Metadata Schema provides a **comprehensive, extensible, and machine-readable** frontmatter specification for all documentation artifacts in the Project-AI ecosystem. This schema enables:

- **Automated Discovery**: Programmatic querying and filtering of documentation
- **Relationship Mapping**: Explicit linking between related documents
- **Lifecycle Management**: Tracking document status, versions, and deprecation
- **Multi-Dimensional Classification**: Tagging by type, domain, audience, security level
- **Quality Assurance**: Validation of completeness, freshness, and accuracy
- **Integration**: Seamless consumption by IDEs, documentation generators, and AI systems

### Design Principles

1. **Completeness Over Minimalism**: Capture rich context to eliminate ambiguity
2. **Extensibility**: Support custom fields while maintaining core compatibility
3. **Backward Compatibility**: Schema evolution must not break existing documents
4. **Human Readability**: YAML frontmatter remains accessible to humans
5. **Machine Validation**: 100% of schema is enforceable via JSON Schema
6. **Progressive Disclosure**: Required fields are minimal; optional fields add depth

### Scope

**In Scope:**
- All Markdown documentation (`.md` files)
- Technical specifications, design documents, RFCs, reports
- Runbooks, playbooks, tutorials, guides
- Architecture diagrams (with metadata in companion `.md` files)
- Meeting notes, decision records, postmortems

**Out of Scope:**
- Source code documentation (use JSDoc, docstrings, etc.)
- Configuration files (YAML/JSON configs have their own schemas)
- Binary artifacts (images, PDFs—metadata in sidecar files)

---

## Schema Architecture

### Three-Layer Model

```
Layer 1: Universal Fields (Required for ALL documents)
  ├─ Identification: title, id, type, version
  ├─ Lifecycle: created_date, updated_date, status
  └─ Attribution: author, contributors

Layer 2: Domain-Specific Fields (Required for specific document types)
  ├─ Technical Docs: category, tags, technologies
  ├─ Reports: scope, findings, recommendations
  ├─ Guides: difficulty, prerequisites, estimated_time
  └─ Security: classification, sensitivity, compliance

Layer 3: Extended Metadata (Optional enrichment)
  ├─ Relationships: related_docs, supersedes, dependencies
  ├─ Quality: review_status, test_coverage, accuracy_rating
  ├─ Discovery: keywords, search_terms, aliases
  └─ Custom: project-specific fields with `x-` prefix
```

### Document Type Hierarchy

```yaml
documentation:
  technical:
    - architecture
    - design
    - api_reference
    - specification
  procedural:
    - guide
    - tutorial
    - runbook
    - playbook
  governance:
    - policy
    - standard
    - decision_record
    - rfc
  analytical:
    - report
    - audit
    - assessment
    - postmortem
  reference:
    - glossary
    - faq
    - index
    - changelog
```

---

## Core Field Reference

### Universal Fields (Required)

#### `title`
- **Type:** String
- **Required:** Yes
- **Max Length:** 200 characters
- **Description:** Human-readable document title
- **Validation:** Non-empty, no leading/trailing whitespace
- **Example:** `"Project-AI Authentication Security Audit Report"`

#### `id`
- **Type:** String (kebab-case)
- **Required:** Yes
- **Pattern:** `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Description:** Unique identifier for cross-referencing
- **Validation:** Globally unique within vault, immutable after creation
- **Example:** `"auth-security-audit-2026-02"`

#### `type`
- **Type:** Enum
- **Required:** Yes
- **Allowed Values:** 
  - `architecture`
  - `design`
  - `api_reference`
  - `specification`
  - `guide`
  - `tutorial`
  - `runbook`
  - `playbook`
  - `policy`
  - `standard`
  - `decision_record`
  - `rfc`
  - `report`
  - `audit`
  - `assessment`
  - `postmortem`
  - `glossary`
  - `faq`
  - `index`
  - `changelog`
  - `meeting_notes`
  - `whitepaper`
- **Description:** Primary document classification
- **Example:** `audit`

#### `version`
- **Type:** String (SemVer 2.0.0)
- **Required:** Yes
- **Pattern:** `^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$`
- **Description:** Document version following Semantic Versioning
- **Validation:** Major.Minor.Patch format
- **Example:** `"1.2.0"`, `"2.0.0-beta.1"`, `"1.0.0+20260420"`

#### `created_date`
- **Type:** ISO 8601 Date
- **Required:** Yes
- **Format:** `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`
- **Description:** Original creation timestamp
- **Validation:** Valid date, not in future
- **Example:** `"2026-04-20"`, `"2026-04-20T14:30:00Z"`

#### `updated_date`
- **Type:** ISO 8601 Date
- **Required:** Yes
- **Format:** `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`
- **Description:** Last modification timestamp
- **Validation:** Must be >= created_date
- **Example:** `"2026-04-20T16:45:00Z"`

#### `status`
- **Type:** Enum
- **Required:** Yes
- **Allowed Values:**
  - `draft` - Work in progress, not reviewed
  - `review` - Under peer review
  - `active` - Published and current
  - `deprecated` - Superseded by newer document
  - `archived` - Historical record, no longer applicable
- **Description:** Current lifecycle status
- **Example:** `active`

#### `author`
- **Type:** String or Object
- **Required:** Yes
- **Format:** `"Name <email>"` or `{name: "...", email: "...", github: "..."}`
- **Description:** Primary document author
- **Example:** 
  ```yaml
  author:
    name: "Jane Doe"
    email: "jane@project-ai.org"
    github: "janedoe"
  ```

### Domain-Specific Fields

#### `category`
- **Type:** String
- **Required:** For technical/report/guide documents
- **Allowed Values:**
  - `security`
  - `architecture`
  - `infrastructure`
  - `frontend`
  - `backend`
  - `database`
  - `devops`
  - `testing`
  - `documentation`
  - `governance`
- **Description:** Primary domain classification
- **Example:** `security`

#### `tags`
- **Type:** Array of Strings
- **Required:** No (recommended)
- **Min Items:** 1
- **Max Items:** 20
- **Item Pattern:** `^[a-z0-9-]+$`
- **Description:** Multi-dimensional classification labels
- **Example:** `["authentication", "password-hashing", "bcrypt", "audit"]`

#### `technologies`
- **Type:** Array of Strings
- **Required:** For technical documents
- **Description:** Technologies/frameworks covered
- **Example:** `["Python", "PyQt6", "bcrypt", "OpenAI-API"]`

#### `scope`
- **Type:** String
- **Required:** For reports/audits
- **Max Length:** 500 characters
- **Description:** Scope of analysis or coverage
- **Example:** `"Core authentication/authorization modules in src/app/core/"`

#### `classification`
- **Type:** Enum
- **Required:** For security-sensitive documents
- **Allowed Values:**
  - `public` - No restrictions
  - `internal` - Organization-only
  - `confidential` - Restricted access
  - `secret` - Highly restricted
- **Description:** Security classification level
- **Default:** `internal`
- **Example:** `internal`

#### `difficulty`
- **Type:** Enum
- **Required:** For guides/tutorials
- **Allowed Values:** `beginner`, `intermediate`, `advanced`, `expert`
- **Description:** Target audience skill level
- **Example:** `intermediate`

#### `estimated_time`
- **Type:** String (ISO 8601 Duration) or Integer (minutes)
- **Required:** For tutorials/guides
- **Description:** Expected completion time
- **Example:** `"PT45M"` (45 minutes), `60` (60 minutes)

#### `prerequisites`
- **Type:** Array of Strings
- **Required:** For tutorials/guides with dependencies
- **Description:** Required knowledge or completed documents
- **Example:** `["Python basics", "Understanding of OAuth 2.0"]`

### Relationship Fields

#### `related_docs`
- **Type:** Array of Strings (document IDs)
- **Required:** No
- **Description:** Related documents (see-also references)
- **Validation:** Each ID must exist in vault
- **Example:** `["auth-implementation", "password-policy-2026"]`

#### `supersedes`
- **Type:** String or Array of Strings (document IDs)
- **Required:** When status is `active` and replaces older docs
- **Description:** Documents made obsolete by this document
- **Example:** `"auth-audit-2025-12"`

#### `superseded_by`
- **Type:** String (document ID)
- **Required:** When status is `deprecated`
- **Description:** Newer document that replaces this one
- **Example:** `"auth-audit-2026-04"`

#### `dependencies`
- **Type:** Array of Objects
- **Required:** No
- **Description:** External dependencies
- **Schema:**
  ```yaml
  dependencies:
    - type: document | library | service | api
      name: "Dependency name"
      version: "1.0.0"
      id: "doc-id-if-internal"
  ```

### Quality Metadata

#### `review_status`
- **Type:** Object
- **Required:** No (recommended for critical docs)
- **Schema:**
  ```yaml
  review_status:
    reviewed: true
    reviewers: ["alice", "bob"]
    review_date: "2026-04-20"
    approved: true
  ```

#### `test_coverage`
- **Type:** Object
- **Required:** For technical specifications
- **Schema:**
  ```yaml
  test_coverage:
    has_tests: true
    coverage_percent: 85
    test_files: ["tests/test_auth.py"]
  ```

#### `accuracy_rating`
- **Type:** Integer
- **Required:** No
- **Range:** 1-10
- **Description:** Self-assessed accuracy (10 = verified accurate)
- **Example:** `9`

### Discovery & SEO Fields

#### `keywords`
- **Type:** Array of Strings
- **Required:** No (recommended)
- **Description:** Search optimization terms
- **Example:** `["password security", "threat model", "OWASP"]`

#### `summary`
- **Type:** String
- **Required:** No (recommended)
- **Max Length:** 500 characters
- **Description:** One-paragraph abstract
- **Example:** `"Comprehensive security audit of authentication systems..."`

#### `audience`
- **Type:** Array of Enums
- **Required:** No
- **Allowed Values:**
  - `developer`
  - `architect`
  - `devops`
  - `security_engineer`
  - `product_manager`
  - `executive`
  - `contributor`
  - `end_user`
- **Description:** Target reader personas
- **Example:** `["developer", "security_engineer"]`

### Extended Metadata

#### `contributors`
- **Type:** Array of Strings or Objects
- **Required:** No
- **Description:** Additional contributors beyond primary author
- **Example:**
  ```yaml
  contributors:
    - name: "Bob Smith"
      role: "Technical Reviewer"
    - name: "Alice Johnson"
      role: "Editor"
  ```

#### `changelog`
- **Type:** Array of Objects
- **Required:** No (recommended for versioned docs)
- **Schema:**
  ```yaml
  changelog:
    - version: "1.1.0"
      date: "2026-04-15"
      changes: "Added OAuth 2.0 section"
      author: "jane"
    - version: "1.0.0"
      date: "2026-04-01"
      changes: "Initial release"
      author: "jane"
  ```

#### `compliance`
- **Type:** Array of Strings
- **Required:** For security/regulatory docs
- **Description:** Compliance frameworks addressed
- **Example:** `["GDPR", "SOC2", "OWASP-Top-10"]`

#### `metrics`
- **Type:** Object
- **Required:** No
- **Description:** Document-specific metrics
- **Example:**
  ```yaml
  metrics:
    word_count: 3500
    code_blocks: 12
    diagrams: 3
    external_links: 8
  ```

#### `custom_fields`
- **Type:** Object
- **Required:** No
- **Description:** Project-specific metadata (prefix with `x-`)
- **Example:**
  ```yaml
  custom_fields:
    x-project-id: "PROJECT-AI-2026"
    x-sprint: "Sprint-42"
    x-epic: "Authentication Overhaul"
  ```

---

## Document Type Taxonomy

### Architecture Documents

**Type:** `architecture`  
**Required Fields:** `title`, `id`, `type`, `version`, `created_date`, `updated_date`, `status`, `author`, `category`, `technologies`  
**Recommended Fields:** `tags`, `related_docs`, `review_status`, `summary`, `audience`

**Purpose:** Describe system structure, design decisions, patterns

**Example Use Cases:**
- System architecture diagrams
- Component interaction models
- Technology stack decisions
- Design pattern documentation

### Design Documents

**Type:** `design`  
**Required Fields:** Universal + `category`, `scope`  
**Recommended Fields:** `technologies`, `dependencies`, `review_status`

**Purpose:** Detailed technical designs for features/components

### API Reference

**Type:** `api_reference`  
**Required Fields:** Universal + `technologies`, `version`  
**Recommended Fields:** `endpoints`, `authentication`, `rate_limits`

**Purpose:** API endpoint documentation

### Specifications

**Type:** `specification`  
**Required Fields:** Universal + `category`, `compliance`  
**Recommended Fields:** `review_status`, `test_coverage`

**Purpose:** Formal technical specifications

### Guides

**Type:** `guide`  
**Required Fields:** Universal + `difficulty`, `estimated_time`, `category`  
**Recommended Fields:** `prerequisites`, `technologies`, `audience`

**Purpose:** How-to documentation for specific tasks

### Tutorials

**Type:** `tutorial`  
**Required Fields:** Universal + `difficulty`, `estimated_time`, `prerequisites`  
**Recommended Fields:** `technologies`, `learning_objectives`

**Purpose:** Step-by-step learning paths

### Runbooks

**Type:** `runbook`  
**Required Fields:** Universal + `category`, `scope`, `triggers`  
**Recommended Fields:** `escalation_path`, `dependencies`, `last_tested`

**Purpose:** Operational procedures for incident response

### Playbooks

**Type:** `playbook`  
**Required Fields:** Universal + `category`, `scope`  
**Recommended Fields:** `success_criteria`, `rollback_procedure`

**Purpose:** Standardized operational workflows

### Policies

**Type:** `policy`  
**Required Fields:** Universal + `category`, `compliance`, `enforcement_level`  
**Recommended Fields:** `review_cycle`, `approval_authority`

**Purpose:** Organizational governance rules

### Standards

**Type:** `standard`  
**Required Fields:** Universal + `category`, `scope`  
**Recommended Fields:** `compliance`, `exceptions`

**Purpose:** Technical or procedural standards

### Decision Records

**Type:** `decision_record`  
**Required Fields:** Universal + `decision_date`, `decision_maker`, `options_considered`  
**Recommended Fields:** `consequences`, `context`, `review_date`

**Purpose:** Architectural Decision Records (ADRs)

### RFCs

**Type:** `rfc`  
**Required Fields:** Universal + `proposal_date`, `champion`, `status`  
**Recommended Fields:** `discussion_link`, `votes`, `decision_date`

**Purpose:** Request for Comments / Proposals

### Reports

**Type:** `report`  
**Required Fields:** Universal + `scope`, `findings`, `recommendations`  
**Recommended Fields:** `executive_summary`, `methodology`, `metrics`

**Purpose:** Analysis reports, summaries

### Audits

**Type:** `audit`  
**Required Fields:** Universal + `scope`, `auditor`, `audit_date`, `findings`, `risk_level`  
**Recommended Fields:** `methodology`, `compliance`, `remediation_plan`

**Purpose:** Security, compliance, quality audits

### Assessments

**Type:** `assessment`  
**Required Fields:** Universal + `scope`, `criteria`, `results`  
**Recommended Fields:** `methodology`, `recommendations`

**Purpose:** Evaluations and assessments

### Postmortems

**Type:** `postmortem`  
**Required Fields:** Universal + `incident_date`, `severity`, `root_cause`, `timeline`, `action_items`  
**Recommended Fields:** `impact`, `detection_method`, `lessons_learned`

**Purpose:** Incident analysis and learning

### Glossaries

**Type:** `glossary`  
**Required Fields:** Universal + `scope`, `terms_count`  
**Recommended Fields:** `related_docs`, `audience`

**Purpose:** Term definitions and vocabulary

### FAQs

**Type:** `faq`  
**Required Fields:** Universal + `category`, `questions_count`  
**Recommended Fields:** `audience`, `related_docs`

**Purpose:** Frequently asked questions

### Indexes

**Type:** `index`  
**Required Fields:** Universal + `scope`, `indexed_docs`  
**Recommended Fields:** `auto_generated`, `last_indexed_date`

**Purpose:** Document collections and catalogs

### Changelogs

**Type:** `changelog`  
**Required Fields:** Universal + `scope`, `version_range`  
**Recommended Fields:** `format` (e.g., "Keep a Changelog")

**Purpose:** Version history

### Meeting Notes

**Type:** `meeting_notes`  
**Required Fields:** Universal + `meeting_date`, `attendees`, `agenda`  
**Recommended Fields:** `action_items`, `decisions`, `next_meeting`

**Purpose:** Meeting documentation

### Whitepapers

**Type:** `whitepaper`  
**Required Fields:** Universal + `summary`, `keywords`, `audience`  
**Recommended Fields:** `citation`, `doi`, `peer_reviewed`

**Purpose:** Research and thought leadership

---

## Data Type Specifications

### String Types

#### Basic String
- **Max Length:** 1000 characters (unless specified otherwise)
- **Encoding:** UTF-8
- **Validation:** No control characters (except newline in multi-line)

#### Kebab-Case String
- **Pattern:** `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Use Case:** IDs, tags
- **Example:** `"auth-security-audit"`

#### Email
- **Pattern:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **Example:** `"user@project-ai.org"`

#### URL
- **Pattern:** Must be valid HTTP(S) URL
- **Example:** `"https://docs.project-ai.org/auth"`

#### Semantic Version
- **Pattern:** `^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$`
- **Example:** `"1.2.3"`, `"2.0.0-beta.1"`

### Date/Time Types

#### ISO 8601 Date
- **Format:** `YYYY-MM-DD`
- **Example:** `"2026-04-20"`

#### ISO 8601 DateTime
- **Format:** `YYYY-MM-DDTHH:MM:SSZ` (UTC)
- **Example:** `"2026-04-20T14:30:00Z"`

#### ISO 8601 Duration
- **Format:** `P[n]Y[n]M[n]DT[n]H[n]M[n]S`
- **Example:** `"PT1H30M"` (1 hour 30 minutes)

### Numeric Types

#### Integer
- **Range:** -2,147,483,648 to 2,147,483,647
- **Example:** `42`

#### Percentage
- **Range:** 0-100
- **Type:** Integer or Float
- **Example:** `85`, `92.5`

### Enumeration Types

All enumerations are case-sensitive and lowercase (except where noted).

#### Status
`draft`, `review`, `active`, `deprecated`, `archived`

#### Classification
`public`, `internal`, `confidential`, `secret`

#### Difficulty
`beginner`, `intermediate`, `advanced`, `expert`

#### Risk Level
`low`, `medium`, `high`, `critical`

#### Severity
`minor`, `moderate`, `major`, `critical`

### Structured Types

#### Author Object
```yaml
name: String (required)
email: Email (optional)
github: String (optional)
role: String (optional)
```

#### Dependency Object
```yaml
type: Enum [document, library, service, api]
name: String (required)
version: SemVer (optional)
id: String (optional, required if type=document)
url: URL (optional)
```

#### Review Object
```yaml
reviewed: Boolean (required)
reviewers: Array<String> (required)
review_date: ISO8601Date (required)
approved: Boolean (required)
comments: String (optional)
```

---

## Validation Rules

### Field-Level Validation

1. **Required Field Presence**
   - All universal required fields must be present
   - Type-specific required fields must be present for that type

2. **Type Checking**
   - Strings must be valid UTF-8
   - Dates must be valid ISO 8601
   - Enums must match allowed values (case-sensitive)
   - Arrays must contain elements of specified type

3. **Format Validation**
   - Emails must match email pattern
   - URLs must be valid HTTP(S)
   - SemVer must match semantic versioning spec
   - IDs must be kebab-case

4. **Range Validation**
   - Integers within specified ranges
   - String lengths within limits
   - Array sizes within min/max bounds

### Cross-Field Validation

1. **Date Consistency**
   - `updated_date >= created_date`
   - Future dates not allowed (except for `expiry_date`)

2. **Status Dependencies**
   - If `status = deprecated`, `superseded_by` is required
   - If `status = active` and document replaces older version, `supersedes` recommended

3. **Relationship Integrity**
   - Document IDs in `related_docs` must exist
   - `supersedes` and `superseded_by` must be bidirectional
   - Circular dependencies are warnings (not errors)

4. **Type-Specific Rules**
   - `audit` type requires `risk_level`
   - `tutorial` type requires `difficulty` and `estimated_time`
   - `postmortem` type requires `incident_date` and `severity`

### Document-Level Validation

1. **Uniqueness**
   - `id` must be globally unique
   - `title` should be unique (warning if duplicate)

2. **Completeness**
   - Minimum 100 words in document body (warning)
   - At least 3 tags recommended
   - Summary recommended for documents >1000 words

3. **Quality Checks**
   - No broken internal links
   - No dead external URLs (warning)
   - Code blocks have language specified

---

## Relationship Specifications

### Relationship Types

#### 1. Hierarchical Relationships

**Parent-Child:**
- Used for: Nested documents, document series
- Field: `parent_id` (child points to parent)
- Example: Tutorial series, multi-part reports

**Collection-Member:**
- Used for: Document collections, indexes
- Field: `collection_id`
- Example: "Security Audits 2026" collection

#### 2. Sequential Relationships

**Supersession:**
- Field: `supersedes` (new doc) ↔ `superseded_by` (old doc)
- Bidirectional: Must be maintained on both documents
- Use Case: Version updates, document replacements

**Prerequisite:**
- Field: `prerequisites` (array of IDs)
- Directional: Current doc depends on prerequisites
- Use Case: Learning paths, implementation order

#### 3. Associative Relationships

**Related Documents:**
- Field: `related_docs` (array of IDs)
- Non-directional: See-also references
- Use Case: Cross-references, complementary content

**Dependencies:**
- Field: `dependencies` (array of objects)
- Directional: Current doc depends on external resources
- Use Case: API dependencies, library requirements

### Relationship Graph Example

```yaml
# Document A (Old Authentication Audit)
id: "auth-audit-2025-12"
status: deprecated
superseded_by: "auth-audit-2026-04"

# Document B (New Authentication Audit)
id: "auth-audit-2026-04"
status: active
supersedes: "auth-audit-2025-12"
related_docs:
  - "password-policy-2026"
  - "session-management-guide"

# Document C (Password Policy)
id: "password-policy-2026"
status: active
related_docs:
  - "auth-audit-2026-04"
dependencies:
  - type: document
    id: "crypto-standards"
    version: "1.0.0"
```

### Relationship Validation

**Automated Checks:**
1. Bidirectional supersession links are consistent
2. All referenced document IDs exist
3. No circular supersession chains
4. Prerequisite chains are acyclic (warning if cyclic)

**Warnings:**
- Orphaned documents (no incoming relationships)
- Dead-end documents (no outgoing relationships)
- Deprecated docs still being referenced

---

## Complete Examples

### Example 1: Security Audit Report

```yaml
---
# Universal Fields
title: "Project-AI Authentication & Authorization Security Audit"
id: "auth-security-audit-2026-04"
type: audit
version: "1.0.0"
created_date: "2026-04-15"
updated_date: "2026-04-20"
status: active
author:
  name: "Security Team"
  email: "security@project-ai.org"
  github: "project-ai-security"

# Domain-Specific Fields
category: security
tags:
  - authentication
  - authorization
  - security-audit
  - password-hashing
  - session-management
technologies:
  - Python
  - bcrypt
  - PyQt6
  - passlib
scope: "Core authentication and authorization modules in src/app/core/"
classification: internal
auditor: "Jane Doe"
audit_date: "2026-04-15"
findings:
  critical: 2
  high: 5
  medium: 8
  low: 3
risk_level: high

# Relationship Fields
related_docs:
  - "password-policy-2026"
  - "session-management-guide"
  - "auth-implementation-spec"
supersedes: "auth-audit-2025-12"
dependencies:
  - type: library
    name: "bcrypt"
    version: "4.0.0"
  - type: library
    name: "passlib"
    version: "1.7.4"

# Quality Metadata
review_status:
  reviewed: true
  reviewers:
    - "alice-security"
    - "bob-architect"
  review_date: "2026-04-18"
  approved: true
accuracy_rating: 9

# Discovery Fields
keywords:
  - password security
  - threat model
  - OWASP
  - authentication best practices
summary: "Comprehensive security audit of Project-AI authentication and authorization systems, identifying 18 security issues across multiple risk levels with detailed remediation recommendations."
audience:
  - developer
  - security_engineer
  - architect

# Extended Metadata
contributors:
  - name: "Alice Smith"
    role: "Security Reviewer"
  - name: "Bob Johnson"
    role: "Technical Reviewer"
compliance:
  - "OWASP-Top-10"
  - "CWE-Top-25"
metrics:
  word_count: 4500
  code_blocks: 18
  findings_count: 18
remediation_plan:
  - issue_id: "AUTH-001"
    priority: critical
    estimated_effort: "3 days"
  - issue_id: "AUTH-002"
    priority: high
    estimated_effort: "2 days"
---
```

### Example 2: Tutorial Document

```yaml
---
title: "Getting Started with Project-AI Authentication"
id: "auth-tutorial-getting-started"
type: tutorial
version: "1.1.0"
created_date: "2026-03-01"
updated_date: "2026-04-10"
status: active
author:
  name: "Developer Relations Team"
  email: "devrel@project-ai.org"

category: security
tags:
  - tutorial
  - authentication
  - getting-started
  - beginner
technologies:
  - Python
  - bcrypt
difficulty: beginner
estimated_time: "PT45M"
prerequisites:
  - "Python basics"
  - "Understanding of password hashing"
learning_objectives:
  - "Understand Project-AI authentication flow"
  - "Implement user registration and login"
  - "Hash passwords securely using bcrypt"

related_docs:
  - "auth-api-reference"
  - "password-policy-2026"
  - "user-manager-design"

review_status:
  reviewed: true
  reviewers: ["tech-writer-team"]
  review_date: "2026-04-05"
  approved: true

keywords:
  - authentication tutorial
  - user login
  - password hashing
  - bcrypt tutorial
summary: "Step-by-step guide to implementing authentication in Project-AI applications, covering user registration, login, and password security best practices."
audience:
  - developer
  - contributor

changelog:
  - version: "1.1.0"
    date: "2026-04-10"
    changes: "Added section on password policy validation"
    author: "devrel-team"
  - version: "1.0.0"
    date: "2026-03-01"
    changes: "Initial release"
    author: "devrel-team"
---
```

### Example 3: Architecture Document

```yaml
---
title: "Three-Tier Platform Architecture"
id: "three-tier-architecture-design"
type: architecture
version: "2.0.0"
created_date: "2025-11-15"
updated_date: "2026-04-18"
status: active
author:
  name: "Principal Architect"
  email: "architect@project-ai.org"
  github: "project-ai-architect"

category: architecture
tags:
  - architecture
  - design-patterns
  - platform-design
  - governance
technologies:
  - Python
  - PyQt6
  - Docker
  - Kubernetes
scope: "Complete platform architecture covering Tier 1 (Governance), Tier 2 (AI Systems), Tier 3 (User Interface)"
classification: internal

related_docs:
  - "governance-framework-spec"
  - "ai-systems-architecture"
  - "ui-architecture-guide"
dependencies:
  - type: document
    id: "design-principles"
    version: "1.0.0"
  - type: document
    id: "technology-stack-decision"
    version: "2.1.0"

review_status:
  reviewed: true
  reviewers:
    - "tech-lead"
    - "principal-engineer"
    - "security-lead"
  review_date: "2026-04-15"
  approved: true

keywords:
  - platform architecture
  - three-tier design
  - governance layer
  - separation of concerns
summary: "Comprehensive architecture specification for Project-AI's three-tier platform design, establishing clear separation between governance, AI systems, and user interface layers."
audience:
  - architect
  - developer
  - technical_lead

metrics:
  word_count: 6200
  diagrams: 8
  code_blocks: 15
  external_links: 12

custom_fields:
  x-architecture-decision-records:
    - "ADR-001-three-tier-separation"
    - "ADR-002-governance-layer"
  x-review-cycle: "quarterly"
---
```

### Example 4: API Reference

```yaml
---
title: "Authentication API Reference"
id: "auth-api-reference-v2"
type: api_reference
version: "2.1.0"
created_date: "2026-01-10"
updated_date: "2026-04-20"
status: active
author:
  name: "API Team"
  email: "api@project-ai.org"

category: backend
tags:
  - api
  - authentication
  - rest-api
  - reference
technologies:
  - Flask
  - JWT
  - OAuth2
  - bcrypt
classification: internal

endpoints:
  - path: "/api/v2/auth/register"
    method: POST
    authenticated: false
  - path: "/api/v2/auth/login"
    method: POST
    authenticated: false
  - path: "/api/v2/auth/logout"
    method: POST
    authenticated: true
  - path: "/api/v2/auth/refresh"
    method: POST
    authenticated: true

authentication:
  type: "JWT"
  token_expiry: "1h"
  refresh_token_expiry: "30d"

rate_limits:
  login: "10 requests per minute"
  register: "3 requests per hour"
  refresh: "100 requests per hour"

related_docs:
  - "auth-tutorial-getting-started"
  - "auth-security-audit-2026-04"
  - "jwt-implementation-guide"

dependencies:
  - type: library
    name: "Flask-JWT-Extended"
    version: "4.5.0"
  - type: library
    name: "bcrypt"
    version: "4.0.0"

review_status:
  reviewed: true
  reviewers: ["backend-team"]
  review_date: "2026-04-18"
  approved: true

keywords:
  - authentication API
  - REST endpoints
  - JWT tokens
  - user registration
summary: "Complete API reference for Project-AI authentication endpoints, including registration, login, logout, and token refresh functionality."
audience:
  - developer
  - frontend_developer
  - mobile_developer
---
```

### Example 5: Decision Record (ADR)

```yaml
---
title: "ADR-015: Use bcrypt for Password Hashing"
id: "adr-015-bcrypt-password-hashing"
type: decision_record
version: "1.0.0"
created_date: "2025-10-22"
updated_date: "2025-10-22"
status: active
author:
  name: "Security Architect"
  email: "security@project-ai.org"

category: security
tags:
  - adr
  - decision-record
  - password-hashing
  - cryptography
decision_date: "2025-10-22"
decision_maker: "Security Architecture Team"
options_considered:
  - name: "bcrypt"
    pros:
      - "Industry standard for password hashing"
      - "Built-in salt generation"
      - "Adaptive cost factor"
    cons:
      - "Slower than SHA-256 (by design)"
  - name: "scrypt"
    pros:
      - "Memory-hard algorithm"
      - "Resistant to hardware attacks"
    cons:
      - "More complex to implement"
      - "Less widely adopted"
  - name: "Argon2"
    pros:
      - "Winner of Password Hashing Competition"
      - "Configurable memory and time costs"
    cons:
      - "Newer, less battle-tested"
      - "Limited Python library support"

decision: "Use bcrypt with cost factor 12 for all password hashing"
rationale: "bcrypt provides the best balance of security, performance, and ecosystem support for Project-AI's needs"
consequences:
  positive:
    - "Strong protection against rainbow table attacks"
    - "Automatic salt generation"
    - "Proven track record in production systems"
  negative:
    - "Slower login performance compared to weaker algorithms"
    - "Maximum password length of 72 bytes"
  neutral:
    - "Must monitor bcrypt cost factor as hardware improves"

context: "Project-AI requires secure password storage for user authentication system supporting 10,000+ users"
review_date: "2027-10-22"

related_docs:
  - "password-policy-2026"
  - "auth-security-audit-2026-04"
  - "crypto-standards"

compliance:
  - "OWASP Password Storage Cheat Sheet"
  - "NIST SP 800-63B"
---
```

### Example 6: Runbook

```yaml
---
title: "Authentication Service Failure Recovery Runbook"
id: "runbook-auth-service-failure"
type: runbook
version: "1.2.0"
created_date: "2026-02-10"
updated_date: "2026-04-12"
status: active
author:
  name: "DevOps Team"
  email: "devops@project-ai.org"

category: devops
tags:
  - runbook
  - incident-response
  - authentication
  - disaster-recovery
scope: "Procedures for diagnosing and recovering from authentication service failures"
classification: internal

triggers:
  - "HTTP 500 errors from /api/v2/auth/* endpoints"
  - "Auth service pod crashloop in Kubernetes"
  - "Database connection failures in auth service logs"

escalation_path:
  - level: 1
    role: "On-call Engineer"
    response_time: "5 minutes"
  - level: 2
    role: "Senior DevOps Engineer"
    response_time: "15 minutes"
  - level: 3
    role: "Platform Architect"
    response_time: "30 minutes"

last_tested: "2026-04-01"
test_frequency: "quarterly"

dependencies:
  - type: service
    name: "PostgreSQL"
    version: "14.x"
  - type: service
    name: "Kubernetes"
    version: "1.28.x"
  - type: document
    id: "auth-architecture-design"

related_docs:
  - "monitoring-alerts-guide"
  - "database-recovery-runbook"
  - "incident-response-playbook"

success_criteria:
  - "Auth endpoints returning HTTP 200"
  - "Login success rate >99%"
  - "Average response time <200ms"

rollback_procedure:
  enabled: true
  steps:
    - "Revert to previous container image version"
    - "Restore database from most recent backup"
    - "Verify health checks passing"

keywords:
  - incident response
  - authentication failure
  - service recovery
  - disaster recovery
summary: "Step-by-step procedures for diagnosing and recovering from authentication service failures, including escalation paths, rollback procedures, and verification steps."
audience:
  - devops
  - sre
  - on_call_engineer
---
```

### Example 7: Postmortem

```yaml
---
title: "Postmortem: Authentication Service Outage - April 10, 2026"
id: "postmortem-auth-outage-2026-04-10"
type: postmortem
version: "1.0.0"
created_date: "2026-04-12"
updated_date: "2026-04-15"
status: active
author:
  name: "Incident Commander"
  email: "incidents@project-ai.org"

category: devops
tags:
  - postmortem
  - incident
  - authentication
  - outage
incident_date: "2026-04-10T14:23:00Z"
severity: critical
duration: "PT2H15M"
impact:
  users_affected: 8500
  services_affected:
    - "Web Authentication"
    - "Mobile App Login"
    - "API Token Refresh"
  revenue_impact: "$12,000 estimated"

root_cause: "Database connection pool exhaustion due to unoptimized query in user login flow"
detection_method: "Automated monitoring alert - PagerDuty"
time_to_detect: "PT3M"
time_to_resolve: "PT2H12M"

timeline:
  - time: "2026-04-10T14:23:00Z"
    event: "First PagerDuty alert: Auth service 500 errors"
    actor: "Monitoring System"
  - time: "2026-04-10T14:26:00Z"
    event: "On-call engineer acknowledged alert"
    actor: "Jane Doe"
  - time: "2026-04-10T14:35:00Z"
    event: "Identified database connection pool exhaustion"
    actor: "Jane Doe"
  - time: "2026-04-10T15:00:00Z"
    event: "Escalated to Senior DevOps"
    actor: "Jane Doe"
  - time: "2026-04-10T15:45:00Z"
    event: "Identified problematic query in user_login function"
    actor: "Bob Smith"
  - time: "2026-04-10T16:15:00Z"
    event: "Deployed hotfix with optimized query"
    actor: "Bob Smith"
  - time: "2026-04-10T16:35:00Z"
    event: "Service fully restored, monitoring confirmed"
    actor: "Bob Smith"

lessons_learned:
  what_went_well:
    - "Monitoring detected issue within 3 minutes"
    - "Escalation path worked as designed"
    - "Database backups were current and accessible"
  what_went_wrong:
    - "Unoptimized query not caught in code review"
    - "Load testing didn't simulate realistic user patterns"
    - "Connection pool size not monitored"
  where_we_got_lucky:
    - "Incident occurred during low-traffic period"
    - "Senior engineer was available for escalation"

action_items:
  - id: "AI-001"
    title: "Add database connection pool monitoring"
    owner: "devops-team"
    priority: critical
    due_date: "2026-04-20"
    status: "in_progress"
  - id: "AI-002"
    title: "Implement query performance testing in CI/CD"
    owner: "backend-team"
    priority: high
    due_date: "2026-04-30"
    status: "not_started"
  - id: "AI-003"
    title: "Update load testing scenarios"
    owner: "qa-team"
    priority: high
    due_date: "2026-05-15"
    status: "not_started"
  - id: "AI-004"
    title: "Review and optimize all auth service queries"
    owner: "backend-team"
    priority: medium
    due_date: "2026-05-30"
    status: "not_started"

related_docs:
  - "runbook-auth-service-failure"
  - "database-query-optimization-guide"
  - "incident-response-playbook"

review_status:
  reviewed: true
  reviewers:
    - "incident-commander"
    - "cto"
    - "devops-lead"
  review_date: "2026-04-14"
  approved: true

keywords:
  - incident postmortem
  - database performance
  - connection pool
  - service outage
summary: "Postmortem analysis of authentication service outage on April 10, 2026, caused by database connection pool exhaustion. Includes root cause analysis, timeline, and action items."
audience:
  - devops
  - engineering_leadership
  - backend_developer
---
```

### Example 8: Policy Document

```yaml
---
title: "Password Security Policy"
id: "password-policy-2026"
type: policy
version: "3.0.0"
created_date: "2024-06-01"
updated_date: "2026-04-01"
status: active
author:
  name: "Security Governance Team"
  email: "governance@project-ai.org"

category: security
tags:
  - policy
  - password-security
  - compliance
  - governance
classification: internal
enforcement_level: mandatory
scope: "All Project-AI systems requiring user authentication"

compliance:
  - "NIST SP 800-63B"
  - "OWASP Password Guidelines"
  - "ISO 27001"

review_cycle: "annual"
next_review_date: "2027-04-01"
approval_authority: "Chief Information Security Officer"
approval_date: "2026-03-25"

policy_statements:
  - id: "PS-001"
    statement: "Minimum password length of 12 characters"
    rationale: "Balances security and usability per NIST guidelines"
    exceptions: "None"
  - id: "PS-002"
    statement: "Passwords must use bcrypt with cost factor >= 12"
    rationale: "Industry standard for secure password hashing"
    exceptions: "Legacy systems in migration (expires 2027-01-01)"
  - id: "PS-003"
    statement: "No password expiration requirements"
    rationale: "NIST 800-63B recommends against forced rotation"
    exceptions: "Compromised accounts must change password immediately"

exceptions:
  - system: "Legacy Admin Panel"
    reason: "Migration to new auth system in progress"
    expiry_date: "2026-12-31"
    approved_by: "CISO"

related_docs:
  - "auth-security-audit-2026-04"
  - "adr-015-bcrypt-password-hashing"
  - "password-reset-procedure"

changelog:
  - version: "3.0.0"
    date: "2026-04-01"
    changes: "Removed password expiration requirement per NIST 800-63B"
    author: "security-team"
  - version: "2.0.0"
    date: "2025-06-01"
    changes: "Increased minimum length from 8 to 12 characters"
    author: "security-team"
  - version: "1.0.0"
    date: "2024-06-01"
    changes: "Initial policy"
    author: "security-team"

keywords:
  - password policy
  - security compliance
  - authentication standards
summary: "Comprehensive password security policy for Project-AI, defining requirements for password length, complexity, hashing, and lifecycle management."
audience:
  - developer
  - security_engineer
  - compliance_officer
---
```

### Example 9: Specification

```yaml
---
title: "OAuth 2.0 Implementation Specification"
id: "oauth2-implementation-spec"
type: specification
version: "1.0.0"
created_date: "2026-03-15"
updated_date: "2026-04-18"
status: active
author:
  name: "Security Architecture Team"
  email: "security-arch@project-ai.org"

category: security
tags:
  - specification
  - oauth2
  - authentication
  - authorization
technologies:
  - OAuth2
  - JWT
  - PKCE
  - Flask
classification: internal

scope: "Complete OAuth 2.0 implementation for Project-AI web and mobile applications"

compliance:
  - "RFC 6749 - OAuth 2.0 Framework"
  - "RFC 7636 - PKCE"
  - "RFC 7519 - JSON Web Token"

requirements:
  functional:
    - id: "REQ-001"
      description: "Support authorization code flow with PKCE"
      priority: "must"
    - id: "REQ-002"
      description: "Issue JWT access tokens with 1-hour expiry"
      priority: "must"
    - id: "REQ-003"
      description: "Support refresh tokens with 30-day expiry"
      priority: "must"
    - id: "REQ-004"
      description: "Implement token revocation endpoint"
      priority: "should"
  non_functional:
    - id: "NFR-001"
      description: "Token generation latency < 100ms"
      priority: "should"
    - id: "NFR-002"
      description: "Support 10,000 concurrent token validations"
      priority: "must"

test_coverage:
  has_tests: true
  coverage_percent: 92
  test_files:
    - "tests/test_oauth2_flow.py"
    - "tests/test_token_management.py"
    - "tests/test_pkce.py"

dependencies:
  - type: library
    name: "Authlib"
    version: "1.3.0"
  - type: library
    name: "PyJWT"
    version: "2.8.0"
  - type: document
    id: "jwt-implementation-guide"

related_docs:
  - "auth-api-reference-v2"
  - "security-architecture-design"
  - "token-management-guide"

review_status:
  reviewed: true
  reviewers:
    - "security-architect"
    - "principal-engineer"
  review_date: "2026-04-15"
  approved: true

keywords:
  - OAuth 2.0
  - authorization code flow
  - PKCE
  - JWT tokens
summary: "Comprehensive specification for OAuth 2.0 implementation in Project-AI, covering authorization flows, token management, and security requirements."
audience:
  - developer
  - security_engineer
  - architect
---
```

### Example 10: FAQ Document

```yaml
---
title: "Authentication System FAQ"
id: "auth-faq"
type: faq
version: "1.3.0"
created_date: "2026-01-15"
updated_date: "2026-04-19"
status: active
author:
  name: "Documentation Team"
  email: "docs@project-ai.org"

category: security
tags:
  - faq
  - authentication
  - troubleshooting
  - support
questions_count: 25

audience:
  - developer
  - end_user
  - support_engineer

related_docs:
  - "auth-tutorial-getting-started"
  - "auth-api-reference-v2"
  - "password-policy-2026"
  - "troubleshooting-guide"

keywords:
  - authentication FAQ
  - login issues
  - password reset
  - common questions
summary: "Frequently asked questions about Project-AI authentication system, covering login issues, password management, security best practices, and troubleshooting."

sections:
  - title: "General Questions"
    question_count: 8
  - title: "Password Management"
    question_count: 7
  - title: "Troubleshooting"
    question_count: 6
  - title: "Security Best Practices"
    question_count: 4

changelog:
  - version: "1.3.0"
    date: "2026-04-19"
    changes: "Added OAuth 2.0 questions"
    author: "docs-team"
  - version: "1.2.0"
    date: "2026-03-10"
    changes: "Updated password policy questions"
    author: "docs-team"
  - version: "1.0.0"
    date: "2026-01-15"
    changes: "Initial release"
    author: "docs-team"
---
```

### Additional Examples (11-20)

#### Example 11: Glossary

```yaml
---
title: "Security Terminology Glossary"
id: "security-glossary"
type: glossary
version: "2.1.0"
created_date: "2025-08-01"
updated_date: "2026-04-10"
status: active
author:
  name: "Security Team"
  email: "security@project-ai.org"

category: security
tags:
  - glossary
  - terminology
  - reference
scope: "Security and cryptography terms used in Project-AI documentation"
terms_count: 150

audience:
  - developer
  - security_engineer
  - contributor

related_docs:
  - "security-best-practices"
  - "crypto-standards"
  - "auth-security-audit-2026-04"

keywords:
  - security terminology
  - cryptography definitions
  - glossary
summary: "Comprehensive glossary of security and cryptography terms used throughout Project-AI documentation."
---
```

#### Example 12: Meeting Notes

```yaml
---
title: "Security Architecture Review - Sprint 42"
id: "meeting-security-arch-review-2026-04-15"
type: meeting_notes
version: "1.0.0"
created_date: "2026-04-15"
updated_date: "2026-04-15"
status: active
author:
  name: "Meeting Scribe"
  email: "scribe@project-ai.org"

category: security
tags:
  - meeting-notes
  - architecture-review
  - sprint-42
meeting_date: "2026-04-15T10:00:00Z"
meeting_duration: "PT1H30M"
attendees:
  - "Jane Doe (Security Architect)"
  - "Bob Smith (Principal Engineer)"
  - "Alice Johnson (Product Manager)"
  - "Charlie Brown (Tech Lead)"

agenda:
  - "Review authentication audit findings"
  - "Discuss OAuth 2.0 implementation timeline"
  - "Password policy update approval"
  - "Q2 security roadmap"

decisions:
  - decision: "Approve OAuth 2.0 implementation for Q2"
    decision_maker: "Jane Doe"
    rationale: "Addresses mobile app authentication requirements"
  - decision: "Update password policy to remove expiration"
    decision_maker: "Security Team"
    rationale: "Align with NIST 800-63B recommendations"

action_items:
  - id: "ACT-001"
    title: "Complete OAuth 2.0 specification"
    owner: "security-arch-team"
    due_date: "2026-04-30"
  - id: "ACT-002"
    title: "Update password policy documentation"
    owner: "docs-team"
    due_date: "2026-04-22"

next_meeting: "2026-04-29T10:00:00Z"

related_docs:
  - "auth-security-audit-2026-04"
  - "oauth2-implementation-spec"
  - "password-policy-2026"
---
```

#### Example 13: Whitepaper

```yaml
---
title: "Constitutional AI: Governance-First Architecture for AGI Safety"
id: "whitepaper-constitutional-ai-2026"
type: whitepaper
version: "1.0.0"
created_date: "2026-02-01"
updated_date: "2026-04-12"
status: active
author:
  name: "Research Team"
  email: "research@project-ai.org"

category: governance
tags:
  - whitepaper
  - constitutional-ai
  - agi-safety
  - research
classification: public

summary: "Whitepaper introducing Constitutional AI framework for AGI safety through governance-first architecture and immutable ethical constraints."
keywords:
  - constitutional AI
  - AGI safety
  - ethical AI
  - governance architecture
audience:
  - researcher
  - policy_maker
  - ai_ethicist
  - academic

peer_reviewed: false
citation: "Project-AI Research Team. (2026). Constitutional AI: Governance-First Architecture for AGI Safety. Project-AI Technical Reports."

related_docs:
  - "constitutional-ai-implementation"
  - "governance-framework-spec"
  - "four-laws-specification"

metrics:
  word_count: 12000
  references: 45
  figures: 8
---
```

#### Example 14: Changelog

```yaml
---
title: "Authentication System Changelog"
id: "changelog-auth-system"
type: changelog
version: "1.0.0"
created_date: "2024-01-01"
updated_date: "2026-04-20"
status: active
author:
  name: "Release Management"
  email: "releases@project-ai.org"

category: security
tags:
  - changelog
  - authentication
  - release-notes
scope: "Authentication and authorization modules"
version_range: "1.0.0 to 3.2.0"
format: "Keep a Changelog"

related_docs:
  - "auth-api-reference-v2"
  - "auth-tutorial-getting-started"

audience:
  - developer
  - devops
  - product_manager
---
```

#### Example 15: Index

```yaml
---
title: "Security Documentation Index"
id: "index-security-docs"
type: index
version: "1.5.0"
created_date: "2025-06-01"
updated_date: "2026-04-20"
status: active
author:
  name: "Documentation Team"
  email: "docs@project-ai.org"

category: security
tags:
  - index
  - security
  - documentation
scope: "All security-related documentation"
indexed_docs:
  - "auth-security-audit-2026-04"
  - "password-policy-2026"
  - "oauth2-implementation-spec"
  - "security-glossary"
  - "crypto-standards"
auto_generated: true
last_indexed_date: "2026-04-20"

audience:
  - developer
  - security_engineer
  - contributor
---
```

#### Example 16: Guide (Advanced)

```yaml
---
title: "Advanced OAuth 2.0 Integration Guide"
id: "guide-oauth2-advanced"
type: guide
version: "1.0.0"
created_date: "2026-04-01"
updated_date: "2026-04-18"
status: active
author:
  name: "Backend Team"
  email: "backend@project-ai.org"

category: security
tags:
  - guide
  - oauth2
  - advanced
  - integration
technologies:
  - OAuth2
  - PKCE
  - JWT
  - Flask
difficulty: advanced
estimated_time: "PT3H"
prerequisites:
  - "Understanding of OAuth 2.0 fundamentals"
  - "Experience with REST APIs"
  - "Knowledge of JWT tokens"

learning_objectives:
  - "Implement PKCE flow for mobile apps"
  - "Handle token refresh edge cases"
  - "Secure token storage best practices"

related_docs:
  - "oauth2-implementation-spec"
  - "auth-api-reference-v2"
  - "jwt-implementation-guide"

review_status:
  reviewed: true
  reviewers: ["security-team", "mobile-team"]
  review_date: "2026-04-15"
  approved: true

keywords:
  - OAuth 2.0 integration
  - PKCE implementation
  - mobile authentication
summary: "Advanced guide for integrating OAuth 2.0 with PKCE in mobile and web applications, covering edge cases and security best practices."
audience:
  - developer
  - mobile_developer
---
```

#### Example 17: Assessment

```yaml
---
title: "Third-Party OAuth Provider Security Assessment"
id: "assessment-oauth-providers-2026"
type: assessment
version: "1.0.0"
created_date: "2026-03-20"
updated_date: "2026-04-05"
status: active
author:
  name: "Security Assessment Team"
  email: "security@project-ai.org"

category: security
tags:
  - assessment
  - oauth
  - third-party
  - vendor-review
scope: "Evaluation of Google, GitHub, and Microsoft OAuth providers"
classification: confidential

criteria:
  - name: "Security Posture"
    weight: 40
    score: 9
  - name: "Compliance"
    weight: 30
    score: 10
  - name: "Reliability"
    weight: 20
    score: 8
  - name: "Cost"
    weight: 10
    score: 7

results:
  overall_score: 8.7
  recommendation: "Approve Google and GitHub; defer Microsoft pending security review"

methodology: "Scoring based on NIST Cybersecurity Framework and OWASP guidelines"

related_docs:
  - "oauth2-implementation-spec"
  - "vendor-selection-policy"
  - "third-party-risk-assessment-guide"

recommendations:
  - "Implement Google OAuth as primary provider"
  - "Add GitHub OAuth for developer convenience"
  - "Revisit Microsoft OAuth in Q3 2026"
---
```

#### Example 18: RFC (Request for Comments)

```yaml
---
title: "RFC-023: Passwordless Authentication with WebAuthn"
id: "rfc-023-webauthn"
type: rfc
version: "1.0.0"
created_date: "2026-04-10"
updated_date: "2026-04-20"
status: review
author:
  name: "Jane Doe"
  email: "jane@project-ai.org"

category: security
tags:
  - rfc
  - webauthn
  - passwordless
  - authentication
proposal_date: "2026-04-10"
champion: "Jane Doe"
discussion_link: "https://github.com/project-ai/discussions/123"

abstract: "Proposal to implement WebAuthn for passwordless authentication, reducing password-related security risks and improving user experience."

motivation: "Passwords are the weakest link in authentication security. WebAuthn provides phishing-resistant, passwordless authentication."

proposed_solution:
  - "Implement WebAuthn registration and authentication flows"
  - "Support platform and cross-platform authenticators"
  - "Maintain password authentication as fallback"

alternatives_considered:
  - name: "Magic links"
    rejected_reason: "Email dependency creates single point of failure"
  - name: "SMS OTP"
    rejected_reason: "Vulnerable to SIM swapping attacks"

votes:
  for: 8
  against: 2
  abstain: 1

decision_date: null
decision: "pending"

related_docs:
  - "auth-security-audit-2026-04"
  - "password-policy-2026"
  - "webauthn-research-report"

audience:
  - developer
  - security_engineer
  - architect
  - product_manager
---
```

#### Example 19: Standard

```yaml
---
title: "API Security Standard"
id: "standard-api-security"
type: standard
version: "2.0.0"
created_date: "2025-03-01"
updated_date: "2026-04-01"
status: active
author:
  name: "Security Standards Board"
  email: "standards@project-ai.org"

category: security
tags:
  - standard
  - api-security
  - rest-api
  - best-practices
scope: "All REST and GraphQL APIs in Project-AI"
classification: internal

compliance:
  - "OWASP API Security Top 10"
  - "NIST SP 800-204"

standards:
  - id: "STD-001"
    requirement: "All API endpoints must use HTTPS"
    enforcement: "mandatory"
    exceptions: "Local development only"
  - id: "STD-002"
    requirement: "Implement rate limiting on all public endpoints"
    enforcement: "mandatory"
    exceptions: "None"
  - id: "STD-003"
    requirement: "Use OAuth 2.0 for authentication"
    enforcement: "mandatory"
    exceptions: "Internal service-to-service calls may use mTLS"

exceptions:
  - standard_id: "STD-003"
    system: "Legacy Admin API"
    reason: "Migration in progress"
    expiry_date: "2026-12-31"

review_cycle: "annual"
next_review_date: "2027-04-01"

related_docs:
  - "auth-api-reference-v2"
  - "rate-limiting-implementation"
  - "oauth2-implementation-spec"

keywords:
  - API security
  - REST API standards
  - security requirements
summary: "Comprehensive security standards for all Project-AI APIs, covering authentication, rate limiting, input validation, and secure communication."
audience:
  - developer
  - api_designer
  - security_engineer
---
```

#### Example 20: Design Document

```yaml
---
title: "Multi-Factor Authentication Design"
id: "design-mfa-system"
type: design
version: "1.0.0"
created_date: "2026-04-05"
updated_date: "2026-04-18"
status: review
author:
  name: "Security Engineering Team"
  email: "security-eng@project-ai.org"

category: security
tags:
  - design
  - mfa
  - totp
  - security
technologies:
  - TOTP
  - WebAuthn
  - SMS
  - Python
  - PyOTP
scope: "Multi-factor authentication system design for Project-AI"
classification: internal

design_goals:
  - "Support TOTP, SMS, and WebAuthn as second factors"
  - "Maintain backward compatibility with password-only auth"
  - "Provide recovery codes for account recovery"
  - "Achieve <200ms MFA verification latency"

architecture:
  components:
    - name: "MFA Enrollment Service"
      responsibility: "Handle second factor registration"
    - name: "MFA Verification Service"
      responsibility: "Validate second factor credentials"
    - name: "Recovery Code Manager"
      responsibility: "Generate and validate recovery codes"
  data_model:
    - entity: "UserMFAConfig"
      fields:
        - "user_id (FK)"
        - "mfa_enabled (boolean)"
        - "totp_secret (encrypted)"
        - "webauthn_credentials (encrypted JSON)"
        - "recovery_codes (encrypted array)"

security_considerations:
  - "Encrypt TOTP secrets with Fernet"
  - "Rate limit MFA verification attempts"
  - "Implement backup codes for account recovery"
  - "Audit log all MFA events"

dependencies:
  - type: library
    name: "PyOTP"
    version: "2.9.0"
  - type: library
    name: "webauthn"
    version: "2.0.0"
  - type: document
    id: "auth-security-audit-2026-04"

related_docs:
  - "auth-api-reference-v2"
  - "security-architecture-design"
  - "crypto-standards"

review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false

open_questions:
  - "Should SMS be supported given security concerns?"
  - "What is the recovery code expiration policy?"
  - "How to handle MFA for API-only users?"

keywords:
  - multi-factor authentication
  - TOTP
  - WebAuthn
  - security design
summary: "Detailed design for implementing multi-factor authentication in Project-AI, supporting TOTP, WebAuthn, and recovery codes."
audience:
  - developer
  - security_engineer
  - architect
---
```

---

## Schema Versioning Policy

### Version Numbering

Schema versions follow **Semantic Versioning 2.0.0**:

- **Major (X.0.0)**: Breaking changes (remove required fields, change field types)
- **Minor (1.X.0)**: Backward-compatible additions (new optional fields, new enum values)
- **Patch (1.0.X)**: Documentation fixes, clarifications (no schema changes)

**Current Version:** 2.0.0

### Version History

| Version | Date       | Changes                                      | Breaking? |
|---------|------------|----------------------------------------------|-----------|
| 2.0.0   | 2026-04-20 | Added 15 new optional fields, restructured type taxonomy | No        |
| 1.1.0   | 2026-02-15 | Added `review_status`, `test_coverage` fields | No        |
| 1.0.0   | 2025-12-01 | Initial production release                   | N/A       |

### Deprecation Policy

1. **Announcement**: Deprecated fields announced 6 months before removal
2. **Warning Period**: Tools emit warnings for deprecated field usage
3. **Migration Support**: Migration scripts provided for breaking changes
4. **Removal**: Deprecated fields removed in next major version

**Currently Deprecated:**
- None

### Forward Compatibility

- **Unknown Fields**: Parsers must ignore unknown fields (forward-compatible)
- **New Enum Values**: Add `x-custom-*` values for experimentation
- **Extensions**: Custom fields must use `x-` prefix to avoid collisions

---

## Migration Guide

### Migrating from v1.x to v2.0

**Breaking Changes:** None (fully backward compatible)

**New Fields:**
- `compliance` (array) - Add to policy, audit, spec documents
- `dependencies` (array) - Recommended for technical docs
- `review_status` (object) - Recommended for all production docs
- `test_coverage` (object) - Required for specifications
- `metrics` (object) - Optional for analytics

**Migration Steps:**

1. **Backup existing documents**
   ```powershell
   Copy-Item T:\Project-AI-vault\*.md T:\Project-AI-vault\backup\
   ```

2. **Run migration script**
   ```powershell
   .\migrate-metadata-v1-to-v2.ps1 -SourceDir "T:\Project-AI-vault" -DryRun
   ```

3. **Review changes**
   - Check diff output
   - Validate against JSON Schema
   - Spot-check 5-10 documents

4. **Apply migration**
   ```powershell
   .\migrate-metadata-v1-to-v2.ps1 -SourceDir "T:\Project-AI-vault"
   ```

5. **Validate all documents**
   ```powershell
   .\validate-metadata.ps1 -Recursive
   ```

### Adding Custom Fields

**Best Practice:** Use `custom_fields` with `x-` prefix

```yaml
custom_fields:
  x-project-id: "PROJECT-AI-2026"
  x-epic: "Authentication Overhaul"
  x-sprint: 42
```

**Benefits:**
- Avoids namespace collisions
- Forward-compatible
- Ignored by validation (no schema update needed)

### Handling Validation Errors

**Common Errors:**

1. **Missing Required Field**
   ```
   Error: Field 'author' is required but missing
   Fix: Add author field with name and email
   ```

2. **Invalid Enum Value**
   ```
   Error: 'status' must be one of: draft, review, active, deprecated, archived
   Fix: Correct typo in status value
   ```

3. **Date Format Invalid**
   ```
   Error: 'created_date' must be ISO 8601 format
   Fix: Change "04/20/2026" to "2026-04-20"
   ```

4. **Broken Relationship**
   ```
   Error: Document ID 'auth-audit-2025' referenced in 'related_docs' not found
   Fix: Update ID or remove broken reference
   ```

---

## Best Practices

### 1. Frontmatter Organization

**Recommended Order:**
1. Universal fields
2. Domain-specific fields
3. Relationship fields
4. Quality metadata
5. Discovery fields
6. Extended metadata
7. Custom fields

**Formatting:**
```yaml
---
# Universal Fields
title: "..."
id: "..."
type: "..."
# ... more fields ...

# Domain-Specific Fields
category: "..."
tags: [...]

# Relationships
related_docs: [...]

# Quality Metadata
review_status:
  reviewed: true
  # ...

# Custom Fields
custom_fields:
  x-project-id: "..."
---
```

### 2. ID Naming Conventions

**Format:** `{type}-{topic}-{variant}`

**Examples:**
- `auth-security-audit-2026-04`
- `guide-oauth2-getting-started`
- `adr-015-bcrypt-password-hashing`
- `rfc-023-webauthn`

**Rules:**
- Kebab-case only
- Include type prefix for clarity
- Add date suffix for time-series docs (audits, reports)
- Keep length under 60 characters

### 3. Tag Strategy

**Tag Categories:**
- **Domain:** `authentication`, `database`, `frontend`
- **Type:** `tutorial`, `reference`, `troubleshooting`
- **Technology:** `python`, `react`, `kubernetes`
- **Status:** `draft`, `wip`, `legacy`
- **Audience:** `beginner-friendly`, `internal-only`

**Guidelines:**
- Use 3-10 tags per document
- Prefer existing tags (check tag registry)
- Use lowercase with hyphens
- Avoid redundant tags (e.g., don't tag "guide" if type is already "guide")

### 4. Version Management

**When to Bump Version:**
- **Patch (1.0.X):** Typo fixes, formatting, broken links
- **Minor (1.X.0):** New sections, expanded content, updated examples
- **Major (X.0.0):** Complete rewrites, changed scope, deprecated content

**Always update:**
- `version` field
- `updated_date` field
- `changelog` array (recommended)

### 5. Relationship Maintenance

**Bidirectional Links:**
- When adding `related_docs` reference, add reciprocal link
- When deprecating document, update all referencing documents

**Automated Checks:**
```powershell
# Find broken relationships
.\validate-metadata.ps1 -CheckRelationships

# Find orphaned documents
.\analyze-relationships.ps1 -FindOrphans
```

### 6. Review Workflow

**Before Publishing:**
1. Validate schema: `.\validate-metadata.ps1 -File <path>`
2. Spell check content
3. Test all code examples
4. Verify external links
5. Add to review status:
   ```yaml
   review_status:
     reviewed: true
     reviewers: ["alice", "bob"]
     review_date: "2026-04-20"
     approved: true
   ```

### 7. Deprecation Workflow

**Steps:**
1. Update status: `status: deprecated`
2. Add supersession: `superseded_by: "new-doc-id"`
3. Add deprecation notice in content
4. Update new document: `supersedes: "old-doc-id"`
5. Update referencing documents
6. Archive after 6 months: `status: archived`

---

## Frequently Asked Questions

### General

**Q: Are all fields required?**
A: No. Only universal fields (title, id, type, version, dates, status, author) are required for all documents. Additional fields depend on document type.

**Q: Can I add custom fields?**
A: Yes, use the `custom_fields` object with `x-` prefix to avoid namespace collisions.

**Q: What happens if I use an unknown field?**
A: Validation tools will ignore unknown fields (forward compatibility), but may emit warnings.

### Fields

**Q: What's the difference between `tags` and `keywords`?**
A: `tags` are for classification and filtering. `keywords` are for search optimization (SEO). Tags should be concise (1-2 words); keywords can be phrases.

**Q: Do I need both `summary` and the document content?**
A: Yes. `summary` is for listings, previews, and search results. Document content is the full text.

**Q: How do I reference another document?**
A: Use the document's `id` field in `related_docs`, `supersedes`, or `dependencies`.

**Q: What's the difference between `created_date` and `updated_date`?**
A: `created_date` is when the document was first written (immutable). `updated_date` is when it was last modified (changes on every edit).

### Versioning

**Q: When should I increment the version?**
A: Increment patch for typos/fixes, minor for new content, major for rewrites or scope changes.

**Q: Do I need to update `updated_date` for version bumps?**
A: Yes, always update `updated_date` when changing `version`.

**Q: What if I forget to update the version?**
A: Version mismatches are warnings, not errors. Update the version in your next commit.

### Relationships

**Q: How do I mark a document as deprecated?**
A: Set `status: deprecated` and add `superseded_by: "new-doc-id"`. Update the new document with `supersedes: "old-doc-id"`.

**Q: Can I have circular relationships?**
A: Yes for `related_docs` (non-directional). No for `supersedes` (creates ambiguity). Validators warn on circular `prerequisites`.

**Q: What happens if a referenced document doesn't exist?**
A: Validation fails. Remove the broken reference or create the missing document.

### Validation

**Q: How do I validate my metadata?**
A: Run `.\validate-metadata.ps1 -File <path>` or use the JSON Schema validator.

**Q: What if validation fails?**
A: Read the error message, fix the issue, and re-validate. Common issues: missing required fields, invalid enum values, malformed dates.

**Q: Can I disable validation?**
A: Not recommended. Validation ensures consistency and enables automated tools. If you must, use `x-skip-validation: true` in custom_fields.

### Migration

**Q: How do I migrate from v1.x to v2.0?**
A: Run `.\migrate-metadata-v1-to-v2.ps1`. See [Migration Guide](#migration-guide) for details.

**Q: Will old documents break with the new schema?**
A: No. Schema v2.0 is fully backward compatible. Old documents validate against new schema.

**Q: Do I need to update all documents immediately?**
A: No. Update documents as you edit them. Batch migration is optional.

### Best Practices

**Q: How many tags should I use?**
A: 3-10 tags is ideal. Too few reduces discoverability; too many creates noise.

**Q: Should I include code examples in metadata?**
A: No. Metadata describes the document; code examples go in the document body.

**Q: How often should I review metadata?**
A: Review when editing document content. Audit metadata quarterly for stale dates, broken links, or outdated classifications.

### Tooling

**Q: What tools validate this schema?**
A: `validate-metadata.ps1` (PowerShell), AJV (JavaScript), jsonschema (Python). See `schemas/` directory.

**Q: Can I use this with Obsidian?**
A: Yes. Obsidian supports YAML frontmatter. Use the YAML schema for autocomplete.

**Q: How do I generate documentation from metadata?**
A: Use `dataview` plugin for Obsidian or custom scripts querying frontmatter. Example scripts in `scripts/` directory.

---

## Appendix

### A. Field Quick Reference

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `title` | String | Yes | `"Authentication Audit"` |
| `id` | String | Yes | `"auth-audit-2026-04"` |
| `type` | Enum | Yes | `audit` |
| `version` | SemVer | Yes | `"1.0.0"` |
| `created_date` | ISO8601 | Yes | `"2026-04-20"` |
| `updated_date` | ISO8601 | Yes | `"2026-04-20"` |
| `status` | Enum | Yes | `active` |
| `author` | String/Object | Yes | `{name: "Jane Doe"}` |
| `category` | String | Conditional | `security` |
| `tags` | Array | No | `["auth", "audit"]` |
| `technologies` | Array | Conditional | `["Python", "bcrypt"]` |
| `related_docs` | Array | No | `["password-policy"]` |
| `review_status` | Object | No | `{reviewed: true}` |

### B. Document Type Matrix

| Type | Required Fields | Common Use Cases |
|------|----------------|------------------|
| `architecture` | Universal + category, technologies | System designs, component diagrams |
| `audit` | Universal + scope, auditor, findings, risk_level | Security audits, compliance reviews |
| `guide` | Universal + difficulty, estimated_time, category | How-to documentation |
| `tutorial` | Universal + difficulty, estimated_time, prerequisites | Learning paths |
| `policy` | Universal + category, compliance, enforcement_level | Governance rules |
| `decision_record` | Universal + decision_date, decision_maker, options | ADRs, design decisions |
| `postmortem` | Universal + incident_date, severity, root_cause | Incident analysis |

### C. Validation Checklist

- [ ] All required fields present
- [ ] ID is unique and kebab-case
- [ ] Version follows SemVer
- [ ] Dates are ISO 8601 format
- [ ] Status is valid enum value
- [ ] Tags are lowercase kebab-case
- [ ] Related docs exist
- [ ] Supersession is bidirectional
- [ ] Review status complete (if reviewed)
- [ ] Summary <500 characters
- [ ] No broken links in content

### D. Resources

**Tools:**
- `validate-metadata.ps1` - Schema validation
- `migrate-metadata-v1-to-v2.ps1` - Migration script
- `analyze-relationships.ps1` - Relationship analysis
- `generate-index.ps1` - Auto-generate indexes

**Schemas:**
- `schemas/metadata-schema.json` - JSON Schema
- `schemas/metadata-schema.yaml` - YAML Schema

**Examples:**
- `metadata-examples/` - 20+ example documents

**Support:**
- Documentation: `docs.project-ai.org/metadata-schema`
- Issues: `github.com/project-ai/vault/issues`
- Discussions: `github.com/project-ai/vault/discussions`

---

**Document Version:** 2.0.0  
**Schema Version:** 2.0.0  
**Last Updated:** 2026-04-20  
**Maintainer:** Architecture Team  
**License:** MIT

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

