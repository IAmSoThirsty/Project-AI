# Tag Reference: Complete Tag Taxonomy

**Your Quick Reference for All 85+ Official Tags** 🏷️

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 8 minutes
**Audience:** Documentation contributors, developers
**Prerequisites:** Basic metadata knowledge

---

## Table of Contents

1. [Tag System Overview](#tag-system-overview)
2. [Quick Reference Tables](#quick-reference-tables)
3. [When to Use Each Tag](#when-to-use-each-tag)
4. [Tag Combinations](#tag-combinations)
5. [Tag Validation Rules](#tag-validation-rules)
6. [Common Mistakes](#common-mistakes)

---

## Tag System Overview

Project-AI uses **7 tag categories** with **85+ standardized tags** to classify documentation across multiple dimensions.

### The 7 Tag Categories

```yaml
1. area (1-3 required)     # Domain: architecture, security, governance
2. type (1-2 required)     # Doc type: guide, reference, architecture
3. component (0-5)         # System: agent, gui, core-system
4. status (1 required)     # Lifecycle: active, draft, deprecated
5. audience (1-4 required) # Readers: developer, user, architect
6. priority (0-1)          # Urgency: critical, high, medium, low
7. special (0-10)          # Markers: breaking-change, security-critical
```

### Tag Format Rules

**Valid:**
- ✅ Lowercase with hyphens: `core-system`, `constitutional-ai`
- ✅ Hierarchical: `security/cryptography`, `architecture/backend`
- ✅ Maximum 30 characters
- ✅ Official taxonomy only (see TAG_TAXONOMY.md)

**Invalid:**
- ❌ Spaces: `core system`
- ❌ CamelCase: `CoreSystem`
- ❌ Custom tags: `my-special-tag`
- ❌ Typos: `authetication`

---

## Quick Reference Tables

### Area Tags (15 tags) - 1-3 Required

**Core Domains:**

| Tag | Use When | Child Tags Available |
|-----|----------|---------------------|
| `architecture` | System design, patterns, ADRs | backend, frontend, desktop, web, data, integration |
| `security` | Security, auth, crypto, audits | cryptography, authentication, authorization, network, audit |
| `governance` | Policy, ethics, compliance | constitutional-ai, policy, compliance, ethics, legal |
| `development` | Coding, testing, tools | python, javascript, testing, ci-cd, api, database |
| `operations` | Deploy, monitoring, maintenance | deployment, infrastructure, monitoring, docker |
| `documentation` | Guides, references, knowledge | knowledge-management, templates, standards |
| `ai-systems` | AI/ML, agents, intelligence | machine-learning, nlp, agents, constitutional-ai |

**Specialized Domains:**

| Tag | Use When |
|-----|----------|
| `integration` | APIs, third-party services, external systems |
| `data-management` | Data storage, persistence, databases |
| `testing` | QA, validation, test strategies |
| `ui-ux` | User interfaces, user experience, design |
| `performance` | Optimization, profiling, benchmarking |
| `monitoring` | Observability, logging, metrics |
| `business` | Business logic, domain models |
| `compliance` | Regulatory, standards, policies |

**Example Usage:**

```yaml
# Single area (simple)
area: documentation

# Multiple areas (cross-cutting)
area: [security, architecture, governance]

# With child tags
area: security
tags: [security, security/cryptography, security/authentication]
```

### Type Tags (12 tags) - 1-2 Required

| Tag | Use When | Typical Sections |
|-----|----------|------------------|
| `guide` | Step-by-step instructions | Introduction, Prerequisites, Steps, Examples |
| `reference` | Lookup documentation | Index, API Reference, Configuration Options |
| `architecture` | Design decisions | Context, Decision, Consequences, Alternatives |
| `specification` | Requirements, contracts | Requirements, Constraints, Acceptance Criteria |
| `report` | Analysis, audit results | Summary, Findings, Recommendations |
| `index` | MOC, navigation hub | Categories, Links, Organization |
| `template` | Document boilerplate | Frontmatter structure, Sections, Placeholders |
| `code-documentation` | Code comments, docstrings | Classes, Methods, Examples |
| `api-documentation` | API reference | Endpoints, Parameters, Responses |
| `troubleshooting` | Problem-solving | Problem, Cause, Solution |
| `changelog` | Version history | Version, Date, Changes |
| `roadmap` | Future plans | Timeline, Features, Milestones |

**Common Combinations:**

```yaml
type: [guide, reference]           # Quickstart + API docs
type: [architecture, specification] # ADR with requirements
type: [reference, troubleshooting]  # Reference + FAQ
```

### Component Tags (25+ tags) - 0-5 Optional

**Core Components:**

| Tag | Description |
|-----|-------------|
| `agent` | AI agents (oversight, planner, validator, explainability) |
| `core-system` | Core business logic (AIPersona, FourLaws, Memory, Learning) |
| `gui` | PyQt6 GUI components (LeatherBook, Dashboard, Panels) |
| `cli` | Command-line interface |
| `api` | REST APIs, endpoints |
| `database` | Database systems, queries |
| `authentication` | User auth, password mgmt |
| `authorization` | Permissions, access control |
| `encryption` | Cryptography, key mgmt |
| `storage` | Data persistence |
| `networking` | Network communication |
| `logging` | Log systems |
| `monitoring` | Monitoring tools |
| `templating` | Template engines |
| `plugin` | Plugin systems |

**Example Usage:**

```yaml
# No components (general doc)
component: []

# Single component
component: authentication

# Multiple (integration doc)
component: [authentication, authorization, encryption]

# Full system doc
component: [agent, core-system, gui, api]
```

### Status Tags (7 tags) - 1 Required

| Tag | Meaning | When to Use |
|-----|---------|-------------|
| `active` | Current, maintained, production | Production documentation |
| `draft` | Work in progress | Initial creation |
| `review` | Pending approval | Submitted for review |
| `approved` | Reviewed, ready to publish | After review pass |
| `deprecated` | Outdated, replaced | Being phased out |
| `archived` | Historical reference | No longer active |
| `planned` | Future documentation | Not yet started |

**Lifecycle Flow:**

```
planned → draft → review → approved → active → deprecated → archived
```

### Audience Tags (8 tags) - 1-4 Required

| Tag | Target Reader | Content Style |
|-----|---------------|---------------|
| `user` | End users, non-technical | Simple language, UI-focused |
| `developer` | Software engineers | Technical, code examples |
| `architect` | System architects, leads | High-level design, patterns |
| `contributor` | Documentation contributors | Standards, templates, guidelines |
| `operator` | DevOps, sysadmins | Operations, deployment, monitoring |
| `security-engineer` | Security specialists | Threat models, audits, crypto |
| `data-scientist` | ML engineers | Algorithms, models, data |
| `executive` | Management, decision-makers | Business value, ROI, summaries |

**Example Usage:**

```yaml
# Single audience
audience: developer

# Multi-audience (prioritized - primary first)
audience: [developer, architect, security-engineer]

# Broad audience
audience: [user, developer, contributor]
```

### Priority Tags (4 tags) - 0-1 Recommended

| Tag | Urgency | Use When |
|-----|---------|----------|
| `critical` | Immediate action required | Security advisories, blocking issues |
| `high` | Important, read soon | Major features, architecture changes |
| `medium` | Normal priority | Standard documentation |
| `low` | Optional, nice-to-have | Advanced topics, edge cases |

**Guidelines:**

- Reserve `critical` for truly critical items (security, blockers)
- Most docs should be `medium` (default)
- Use `high` for important but not urgent
- Use `low` for supplementary material

### Special Tags (15+ tags) - 0-10 Optional

**Urgency Markers:**

| Tag | Meaning |
|-----|---------|
| `breaking-change` | Breaking API/interface changes |
| `security-critical` | Security-sensitive content |
| `requires-action` | Action required from readers |

**Quality Markers:**

| Tag | Meaning |
|-----|---------|
| `incomplete` | Missing sections, needs completion |
| `needs-review` | Requires expert review |
| `outdated` | May contain outdated information |

**Process Markers:**

| Tag | Meaning |
|-----|---------|
| `auto-generated` | Generated by scripts/tools |
| `external-dependency` | Depends on external systems |
| `experimental` | Experimental features, unstable |

**Technology Markers:**

| Tag | Meaning |
|-----|---------|
| `python` | Python-specific content |
| `javascript` | JavaScript-specific |
| `docker` | Docker/containerization |
| `windows` | Windows-specific |
| `linux` | Linux-specific |

---

## When to Use Each Tag

### Scenario 1: Core System Documentation

**Document:** `AI_PERSONA_IMPLEMENTATION.md`

```yaml
area: [ai-systems, architecture]
type: code-documentation
component: [core-system, agent]
status: active
audience: [developer, architect]
priority: high
tags: [ai-systems, core-system, agent, architecture, implementation, python]
```

**Why:**
- `ai-systems` (area) - AI system component
- `architecture` (area) - Design decisions included
- `code-documentation` (type) - Documents code
- `core-system` + `agent` (component) - Specific system parts
- `active` (status) - Production documentation
- `developer` + `architect` (audience) - Technical readers
- `high` (priority) - Core system, important
- Additional tags for discoverability

### Scenario 2: Security Audit Report

**Document:** `SECURITY_AUDIT_2026_Q2.md`

```yaml
area: security
type: report
component: []
status: active
audience: [security-engineer, architect, executive]
priority: critical
tags: [security, security/audit, report, bandit, requires-action]
special: [security-critical, requires-action]
```

**Why:**
- `security` (area) - Security domain
- `report` (type) - Analysis results
- No components (vault-wide audit)
- `active` (status) - Current report
- Multiple audiences (security team + leadership)
- `critical` (priority) - Security findings
- Special tags for urgent attention

### Scenario 3: User Guide

**Document:** `GETTING_STARTED.md`

```yaml
area: documentation
type: guide
component: vault
status: active
audience: [user, developer, contributor]
priority: high
tags: [getting-started, onboarding, tutorial, vault, obsidian]
```

**Why:**
- `documentation` (area) - Documentation about documentation
- `guide` (type) - Step-by-step instructions
- `vault` (component) - Obsidian vault specific
- `active` (status) - Current guide
- Broad audience (all users)
- `high` (priority) - Entry point, important
- Descriptive tags for search

### Scenario 4: API Reference

**Document:** `API_REFERENCE_USER_AUTH.md`

```yaml
area: [development, security]
type: [api-documentation, reference]
component: [api, authentication]
status: active
audience: [developer]
priority: medium
tags: [api, authentication, rest, endpoints, reference, python]
```

**Why:**
- Multiple areas (dev + security)
- Dual type (API docs + reference)
- Specific components
- Developer-focused
- Medium priority (reference material)

---

## Tag Combinations

### Effective Tag Strategies

**1. Core System Documentation:**

```yaml
Required Combination:
  area: [architecture, ai-systems]
  type: code-documentation
  component: core-system
  audience: [developer, architect]
  tags: [core-system, implementation, python]
```

**2. Security Documentation:**

```yaml
Required Combination:
  area: security
  type: [guide, reference]
  component: [authentication, authorization, encryption]
  audience: [developer, security-engineer]
  priority: critical
  special: [security-critical]
  tags: [security, security/cryptography, bcrypt, best-practices]
```

**3. User Guides:**

```yaml
Required Combination:
  area: documentation
  type: guide
  component: vault
  audience: [user, contributor]
  priority: high
  tags: [guide, tutorial, getting-started, obsidian]
```

**4. Architecture Decisions:**

```yaml
Required Combination:
  area: architecture
  type: architecture
  component: []
  audience: [architect, developer]
  priority: high
  tags: [architecture, adr, design-pattern, decision-record]
```

### Anti-Patterns

**❌ Too Many Tags:**

```yaml
# Bad: 20+ tags makes search useless
tags: [architecture, security, development, operations, testing,
       monitoring, deployment, ci-cd, docker, kubernetes, python,
       javascript, typescript, react, flask, postgresql, redis,
       nginx, aws, azure, gcp]

# Good: 5-7 most relevant
tags: [architecture, security, deployment, docker, kubernetes]
```

**❌ Wrong Status:**

```yaml
# Bad: Never stays in draft forever
status: draft
created_date: 2025-06-01  # 10 months old!

# Good: Update status
status: active  # or deprecated if abandoned
```

**❌ Missing Required:**

```yaml
# Bad: Missing required fields
type: guide
tags: [guide]
# Missing: area, status, audience

# Good: All required fields
type: guide
area: documentation
status: active
audience: [user]
tags: [guide, tutorial]
```

---

## Tag Validation Rules

### Cardinality Rules

| Category | Min | Max | Required? |
|----------|-----|-----|-----------|
| **area** | 1 | 3 | ✅ Yes |
| **type** | 1 | 2 | ✅ Yes |
| **component** | 0 | 5 | ❌ No |
| **status** | 1 | 1 | ✅ Yes |
| **audience** | 1 | 4 | ✅ Yes |
| **priority** | 0 | 1 | ⚠️ Recommended |
| **special** | 0 | 10 | ❌ No |

### Validation Query

```dataviewjs
// Find documents with invalid tags
const officialTags = ["architecture", "security", "governance", /* ... */];

dv.table(
  ["Document", "Invalid Tags"],
  dv.pages()
    .where(p => p.tags && p.tags.some(t => !officialTags.includes(t)))
    .map(p => {
      const invalid = p.tags.filter(t => !officialTags.includes(t));
      return [p.file.link, invalid.join(", ")];
    })
);
```

**See:** `scripts/validate-tags.ps1` for automated validation

---

## Common Mistakes

### Mistake 1: Using Non-Standard Tags

**❌ Wrong:**

```yaml
tags: [auth, sec, docs, api-ref]
```

**✅ Correct:**

```yaml
tags: [authentication, security, documentation, api-documentation]
```

**Fix:** Always reference [TAG_TAXONOMY.md](TAG_TAXONOMY.md) for official tags

### Mistake 2: Forgetting Required Categories

**❌ Wrong:**

```yaml
tags: [guide, python]
# Missing: area, type, status, audience
```

**✅ Correct:**

```yaml
area: development
type: guide
status: active
audience: [developer]
tags: [guide, development, python]
```

### Mistake 3: Wrong Tag Format

**❌ Wrong:**

```yaml
tags: [Core System, core_system, coreSystem, CORE-SYSTEM]
```

**✅ Correct:**

```yaml
tags: [core-system]
```

**Rule:** Lowercase with hyphens only

### Mistake 4: Tag Overload

**❌ Wrong:**

```yaml
area: [architecture, security, development, operations, testing, monitoring]
# Too many! Max is 3
```

**✅ Correct:**

```yaml
area: [architecture, security]
# Primary domains only
```

### Mistake 5: Wrong Status Values

**❌ Wrong:**

```yaml
status: published    # Not an official value
status: completed    # Not an official value
status: done         # Not an official value
```

**✅ Correct:**

```yaml
status: active       # Official values only:
# active, draft, review, approved, deprecated, archived, planned
```

---

## Summary

### Tag Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ PROJECT-AI TAG REFERENCE                             │
├──────────────────────────────────────────────────────┤
│ REQUIRED (All Documents)                             │
│ ├─ area: [1-3]    Domain/discipline                  │
│ ├─ type: [1-2]    Document type                      │
│ ├─ status: [1]    Lifecycle state                    │
│ ├─ audience: [1-4] Target readers                    │
│ └─ tags: [5-10]   All tags combined                  │
├──────────────────────────────────────────────────────┤
│ RECOMMENDED                                          │
│ ├─ component: [0-5]  System components               │
│ └─ priority: [0-1]   Urgency level                   │
├──────────────────────────────────────────────────────┤
│ OPTIONAL                                             │
│ └─ special: [0-10]   Special markers                 │
├──────────────────────────────────────────────────────┤
│ FORMAT RULES                                         │
│ ├─ Lowercase only: core-system ✅ CoreSystem ❌      │
│ ├─ Hyphens only: core-system ✅ core_system ❌       │
│ ├─ Official tags: architecture ✅ arch ❌            │
│ └─ Array format: [tag1, tag2] ✅ tag1 tag2 ❌        │
└──────────────────────────────────────────────────────┘
```

### Validation Checklist

Before publishing:

- [ ] All required categories present (area, type, status, audience)
- [ ] Tags use official taxonomy (check TAG_TAXONOMY.md)
- [ ] Format is lowercase-with-hyphens
- [ ] Cardinality rules followed (1-3 areas, 1 status, etc.)
- [ ] Status is valid value (active/draft/etc.)
- [ ] Arrays use square brackets: `[tag1, tag2]`

---

**Next Steps:**

- **Reference:** Bookmark [TAG_TAXONOMY.md](TAG_TAXONOMY.md) for complete definitions
- **Validate:** Run `scripts/validate-tags.ps1` weekly
- **Update:** Review and correct non-standard tags
- **Learn:** Study tag combinations in existing documents

**Related Documentation:**

- [TAG_TAXONOMY.md](TAG_TAXONOMY.md) - Complete tag definitions and hierarchies
- [METADATA_GUIDE.md](METADATA_GUIDE.md) - Frontmatter and metadata
- [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) - Tag consistency checks
- `scripts/validate-tags.ps1` - Automated validation

---

**Document Metadata:**

```yaml
---
type: reference
area: documentation
component: vault
status: active
audience: [developer, contributor]
priority: high
tags: [tags, taxonomy, metadata, reference, validation, documentation]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 2400
dependencies:
  - TAG_TAXONOMY.md
  - METADATA_GUIDE.md
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
