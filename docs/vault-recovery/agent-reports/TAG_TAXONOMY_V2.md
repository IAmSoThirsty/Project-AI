# Tag Taxonomy Reference v2.0

> **Metadata Schema Version:** 2.0
> **Last Updated:** 2025-01-23
> **Maintainer:** AGENT-039 (Tag Taxonomy Refinement Specialist)
> **Status:** Active
> **Supersedes:** TAG_TAXONOMY.md v1.0 (AGENT-017)
> **Scope:** Refined controlled vocabulary based on actual usage analysis

---

## Executive Summary

This document defines **Tag Taxonomy v2.0** for Project-AI documentation management, refined based on comprehensive usage analysis of the vault ecosystem. Version 2.0 reduces tag count from 120 to **85 tags** (29% reduction), adds **5 high-value missing tags**, deprecates **40 unused tags**, and clarifies TYPE vs SPECIAL distinction to improve adoption.

### What Changed in v2.0

**✅ Improvements:**
- **Added 5 missing tags:** postmortem, rfc, changelog, end-user, ai-engineer
- **Deprecated 40 unused tags:** Removed low-value tags with 0% adoption
- **Clarified TYPE vs SPECIAL:** Decision tree eliminates category confusion
- **Fixed naming standards:** Enforced kebab-case, lowercase, singular forms
- **Simplified component strategy:** Deprecated component category (0% adoption)
- **Updated validation rules:** Stricter enforcement, automated compliance checking

**📊 v1.0 vs v2.0 Comparison:**

| Metric | v1.0 | v2.0 | Change |
|--------|------|------|--------|
| Total tags | 120 | 85 | -29% |
| Area tags | 42 | 25 | -40% |
| Type tags | 10 | 13 | +30% |
| Status tags | 10 | 7 | -30% |
| Audience tags | 10 | 12 | +20% |
| Priority tags | 5 | 5 | 0% |
| Special tags | 20 | 20 | 0% |
| Component tags | 23 | 3 | -87% |
| Actual usage rate | 21.7% | **Target: 65%** | +43% |
| Compliance rate | 57% | **Target: 90%** | +33% |

**Migration Required:** See TAG_MIGRATION_GUIDE.md for upgrade path from v1.0 to v2.0.

---

## Design Principles (Updated for v2.0)

### Core Tenets

1. **Multi-Dimensional Classification**: Documents classified along 7 independent axes
2. **Pragmatic Minimalism**: Only include tags with demonstrated need (remove deadweight)
3. **Evidence-Based Design**: Taxonomy reflects actual usage patterns, not theoretical ideals
4. **Automated Enforcement**: Machine-readable schema enables CI/CD validation
5. **Clear Semantics**: Eliminate ambiguity (TYPE vs SPECIAL decision tree)
6. **Migration-Friendly**: Deprecated tags map cleanly to replacements

### Tag Lifecycle

**New Tag Addition Criteria:**
- ✅ Used in 3+ documents OR
- ✅ Projected use in 10+ planned documents OR
- ✅ Fills critical gap (e.g., missing audience like "end-user")

**Tag Deprecation Criteria:**
- ❌ Zero usage after 6 months AND
- ❌ No planned usage AND
- ❌ Redundant with existing tags

**Tag Review Cadence:** Quarterly usage analysis (AGENT-039 role)

---

## Table of Contents

1. [Tag Format Conventions](#tag-format-conventions)
2. [Category Definitions](#category-definitions)
   - [Area Tags](#area-tags)
   - [Type Tags](#type-tags)
   - [Status Tags](#status-tags)
   - [Audience Tags](#audience-tags)
   - [Priority Tags](#priority-tags)
   - [Special Tags](#special-tags)
3. [Deprecated Categories](#deprecated-categories)
4. [TYPE vs SPECIAL Decision Tree](#type-vs-special-decision-tree)
5. [Validation Rules](#validation-rules)
6. [Migration from v1.0](#migration-from-v10)
7. [Examples](#examples)

---

## Tag Format Conventions

### Naming Rules (Enforced)

```yaml
# ✅ CORRECT
tags: [api-doc, security/authentication, end-user]

# ❌ WRONG
tags: [API-Doc, security_authentication, end_users]
```

**Rules:**
1. **Lowercase only**: `developer` not `Developer` or `DEVELOPER`
2. **Kebab-case**: `api-doc` not `api_doc` or `apiDoc`
3. **Singular nouns**: `developer` not `developers`
4. **No quotes in arrays**: `[developer]` not `["developer"]`
5. **Hierarchical slash**: `area/child` for parent/child relationships
6. **Max length**: 30 characters
7. **Allowed characters**: `a-z`, `0-9`, `-`, `/` only

### Cardinality Rules

| Category | Min Tags | Max Tags | Required | Mutually Exclusive |
|----------|----------|----------|----------|-------------------|
| **Area** | 1 | 3 | ✅ Yes | No |
| **Type** | 1 | 2 | ✅ Yes | No |
| **Status** | 1 | 1 | ✅ Yes | ✅ Yes |
| **Audience** | 1 | 4 | ✅ Yes | No |
| **Priority** | 0 | 1 | Recommended | ✅ Yes |
| **Special** | 0 | 10 | No | No |

---

## Category Definitions

### Area Tags

**Purpose:** Primary domain, discipline, or concern area
**Hierarchy:** Two-level (parent + optional children)
**Required:** Yes (1-3 tags)
**Cardinality:** Minimum 1 parent tag, optionally 1-2 child tags

#### Parent Tags (7)

##### `architecture`
**Definition:** System design, structure, patterns, and technical architecture decisions.

**When to Use:**
- Design documents defining system structure
- Architecture Decision Records (ADRs)
- Component interaction diagrams
- Technical architecture patterns
- Integration architecture

**Child Tags (5):**
- `architecture/backend` - Server-side architecture, APIs, data layer, business logic
- `architecture/frontend` - UI/UX architecture, client-side design, presentation layer
- `architecture/desktop` - PyQt6 desktop application architecture, GUI patterns
- `architecture/web` - React/Flask web application architecture, SPA design
- `architecture/data` - Data models, schemas, persistence layer, database design

**Examples:**
```yaml
# ADR about microservices
area: [architecture, architecture/backend]

# Desktop UI design
area: [architecture, architecture/desktop]
```

**Removed in v2.0:** `architecture/integration`, `architecture/distributed` (low value, covered by parent tag)

---

##### `security`
**Definition:** Security mechanisms, threat models, cryptography, access control, and vulnerability management.

**When to Use:**
- Security policies and procedures
- Threat model analyses
- Cryptographic implementations
- Penetration test reports
- Security audit findings
- Vulnerability assessments

**Child Tags (4):**
- `security/authentication` - User authentication, OAuth, JWT, bcrypt, password security
- `security/authorization` - RBAC, permissions, access control, privilege escalation
- `security/audit` - Security audits, penetration tests, vulnerability scans, compliance audits
- `security/incident-response` - Incident playbooks, breach procedures, forensics

**Examples:**
```yaml
# Bcrypt implementation guide
area: [security, security/authentication]

# Penetration test report
area: [security, security/audit]
type: report
special: [troubleshooting]
```

**Removed in v2.0:** `security/cryptography` (merge into authentication), `security/network` (covered by infrastructure), `security/application` (redundant with parent), `security/infrastructure` (merge into operations)

---

##### `governance`
**Definition:** Policy, compliance, ethics frameworks, decision-making processes, and constitutional AI governance.

**When to Use:**
- Governance policies and frameworks
- Compliance documentation (GDPR, SOC2, etc.)
- Ethics frameworks (Constitutional AI, Asimov's Laws)
- Regulatory compliance guides
- Legal compliance

**Child Tags (3):**
- `governance/policy` - Organizational policies, procedures, standards
- `governance/compliance` - Regulatory compliance, certifications, audits
- `governance/ethics` - Ethical frameworks, Constitutional AI, value alignment, Asimov's Laws

**Examples:**
```yaml
# Four Laws framework
area: [governance, governance/ethics]
type: whitepaper

# GDPR compliance guide
area: [governance, governance/compliance]
type: guide
```

**Removed in v2.0:** `governance/constitutional-ai` (too specific, use ethics), `governance/legal` (redundant with area:legal), `governance/sovereignty` (niche, 0% usage)

---

##### `development`
**Definition:** Software development practices, tools, workflows, and implementation details.

**When to Use:**
- Development guides and tutorials
- API documentation
- Testing strategies
- CI/CD pipelines
- Developer tools
- Code standards

**Child Tags (4):**
- `development/python` - Python-specific development, libraries, frameworks
- `development/javascript` - JavaScript, TypeScript, Node.js, React development
- `development/testing` - Testing strategies, unit tests, integration tests, QA
- `development/api` - REST APIs, GraphQL, API design patterns

**Examples:**
```yaml
# PyQt6 developer guide
area: [development, development/python]
type: guide
audience: [developer]

# API reference documentation
area: [development, development/api]
type: api-doc
```

**Removed in v2.0:** `development/ci-cd` (merge into operations/deployment), `development/tooling` (too broad), `development/database` (merge into architecture/data)

---

##### `operations`
**Definition:** System operations, deployment, monitoring, maintenance, and infrastructure management.

**When to Use:**
- Deployment runbooks
- Monitoring and observability
- Operational procedures
- Troubleshooting guides
- Performance tuning
- Infrastructure as Code

**Child Tags (3):**
- `operations/deployment` - Deployment procedures, CI/CD, release management, rollbacks
- `operations/monitoring` - Observability, logging, metrics, alerting, dashboards
- `operations/troubleshooting` - Incident response, debugging, problem resolution

**Examples:**
```yaml
# Docker deployment runbook
area: [operations, operations/deployment]
type: runbook
component: [docker]

# Performance monitoring guide
area: [operations, operations/monitoring]
type: guide
special: [performance]
```

**Removed in v2.0:** `operations/maintenance` (merge into troubleshooting), `operations/backup-recovery` (move to special), `operations/performance` (move to special), `operations/infrastructure` (redundant with parent)

---

##### `legal`
**Definition:** Legal frameworks, licensing, intellectual property, contracts, and regulatory requirements.

**When to Use:**
- License documentation (Apache, MIT, GPL)
- Privacy policies and terms of service
- Intellectual property documentation
- Contractual agreements
- Regulatory compliance (GDPR, CCPA, HIPAA)

**Child Tags:** None (flat)

**Examples:**
```yaml
# Apache License documentation
area: legal
type: reference

# Privacy policy
area: [legal, governance/compliance]
type: spec
audience: [legal, executive, public]
```

**Note:** 0% usage in v1.0, but retained as critical category for legal documentation.

---

##### `executive`
**Definition:** Business-level documentation, whitepapers, vision statements, and stakeholder communications.

**When to Use:**
- Business case whitepapers
- Vision and mission statements
- ROI analyses and cost-benefit studies
- Stakeholder presentations
- Executive summaries
- Investor documentation

**Child Tags:** None (flat)

**Examples:**
```yaml
# Constitutional AI whitepaper
area: [governance, executive]
type: whitepaper
audience: [executive, researcher, public]

# Product vision document
area: executive
type: whitepaper
audience: [executive, internal]
```

**Note:** 0% usage in v1.0, but retained for business documentation.

---

### Type Tags

**Purpose:** Document format, structure, and intended use
**Hierarchy:** Flat (no parent/child)
**Required:** Yes (1-2 tags)
**Cardinality:** Minimum 1, maximum 2

#### Document Types (13 tags)

##### `guide`
**Definition:** Instructional content with step-by-step procedures, sequential learning paths.

**When to Use:**
- Getting started guides
- Installation guides
- How-to tutorials
- Procedural documentation
- User manuals

**Characteristics:**
- Sequential structure (step 1, step 2, ...)
- Action-oriented (do this, then do that)
- Beginner to intermediate audience

**Examples:**
```yaml
# Installation guide
type: guide
special: [quickstart]

# Tutorial walkthrough
type: guide
special: [tutorial]
```

---

##### `reference`
**Definition:** Factual reference material designed for lookup and quick information retrieval.

**When to Use:**
- Command references
- Configuration option references
- Glossaries and terminology
- Quick reference cards
- Parameter documentation

**Characteristics:**
- Non-sequential (can be read in any order)
- Lookup-oriented (find specific info quickly)
- Comprehensive coverage of options

**Examples:**
```yaml
# Configuration reference
type: reference
area: [operations]

# Glossary
type: reference
special: [glossary]
```

---

##### `spec`
**Definition:** Formal technical specifications defining requirements, interfaces, or protocols.

**When to Use:**
- Technical specifications
- Protocol specifications
- Interface definitions
- Requirements documents
- Standards documentation

**Characteristics:**
- Formal language
- Precise definitions
- Testable requirements
- Version-controlled

**Examples:**
```yaml
# API specification
type: spec
area: [development, development/api]

# Security policy specification
type: spec
area: [security, governance/policy]
```

---

##### `report`
**Definition:** Analysis, findings, or assessment documents with conclusions and recommendations.

**When to Use:**
- Audit reports
- Assessment reports
- Performance analysis
- Security scan results
- Research findings

**Characteristics:**
- Analytical structure (intro, findings, conclusions)
- Evidence-based
- Recommendations section
- Date-stamped

**Examples:**
```yaml
# Security audit report
type: report
area: [security, security/audit]
special: [audit]

# Performance assessment
type: report
area: [operations]
special: [performance, assessment]
```

---

##### `whitepaper`
**Definition:** Authoritative, research-backed technical or business documents presenting solutions or positions.

**When to Use:**
- Technical whitepapers
- Position papers
- Research publications
- Architectural manifestos
- Business case studies

**Characteristics:**
- Research-backed
- Authoritative tone
- External audience (public, investors)
- Polished presentation

**Examples:**
```yaml
# Constitutional AI whitepaper
type: whitepaper
area: [governance, governance/ethics]
audience: [executive, researcher, public]
```

---

##### `api-doc`
**Definition:** API-specific documentation with endpoints, parameters, request/response examples.

**When to Use:**
- REST API documentation
- GraphQL schema documentation
- SDK documentation
- API versioning guides

**Characteristics:**
- Endpoint listings
- Request/response examples
- Authentication documentation
- Error code references

**Examples:**
```yaml
# REST API reference
type: api-doc
area: [development, development/api]
audience: [developer, contributor]
```

**Note:** Replaces non-standard `api_reference` from v1.0.

---

##### `source-doc`
**Definition:** Documentation embedded in or generated from source code (module docs, docstrings).

**When to Use:**
- Module documentation
- Class/function documentation
- Auto-generated code docs (Sphinx, JSDoc)
- Code architecture documentation

**Characteristics:**
- Tied to specific source code
- May be auto-generated
- Developer-focused
- Version-aligned with code

**Examples:**
```yaml
# PyQt6 GUI module documentation
type: source-doc
area: [architecture, architecture/desktop]
audience: [developer, contributor]
```

**Note:** Replaces non-standard `Module` from v1.0.

---

##### `runbook`
**Definition:** Operational procedures for system management, deployment, and incident response.

**When to Use:**
- Deployment procedures
- Incident response playbooks
- Operational checklists
- Emergency procedures

**Characteristics:**
- Step-by-step operational procedures
- Assumes operational context
- Time-sensitive actions
- Operator-focused

**Examples:**
```yaml
# Docker deployment runbook
type: runbook
area: [operations, operations/deployment]
audience: [operator, developer]
```

---

##### `adr`
**Definition:** Architecture Decision Records documenting significant architectural choices.

**When to Use:**
- Architectural decisions (technology choices, patterns)
- Design trade-offs
- Technical direction changes
- Rationale documentation

**Characteristics:**
- Immutable (ADRs are never changed, only superseded)
- Structured format (Context, Decision, Consequences)
- Numbered sequence (ADR-001, ADR-002)
- Status field (accepted, superseded, deprecated)

**Examples:**
```yaml
# ADR-001: Python as primary language
type: adr
area: [architecture, development/python]
audience: [architect, developer]
```

**Note:** Replaces non-standard `decision_record` from v1.0.

---

##### `index`
**Definition:** Navigation and discovery documents (MOCs, tables of contents, categorized listings).

**When to Use:**
- Map of Contents (MOC)
- Category indexes
- Tag-based indexes
- Navigation hubs

**Characteristics:**
- Link-heavy (points to many other documents)
- Organizational structure
- Maintained regularly
- Entry point for exploration

**Examples:**
```yaml
# Architecture MOC
type: index
area: architecture
audience: [architect, developer]
```

**Note:** Also known as MOC (Map of Content) in Obsidian terminology.

---

##### `postmortem`
**Definition:** Incident postmortem, failure analysis, and lessons learned documents.

**When to Use:**
- Outage postmortems
- Security incident retrospectives
- Failed deployment analysis
- Root cause analysis (RCA)

**Characteristics:**
- Timeline of events
- Root cause identification
- Action items for prevention
- Blameless culture

**Examples:**
```yaml
# Database outage postmortem
type: postmortem
area: [operations]
special: [troubleshooting]
priority: P0
```

**Note:** NEW in v2.0 (identified as missing from usage analysis).

---

##### `rfc`
**Definition:** Request for Comments - proposal documents requiring feedback and discussion.

**When to Use:**
- Design proposals (pre-ADR)
- Feature requests requiring discussion
- Architecture exploration
- Community feedback solicitation

**Characteristics:**
- Proposal stage (not yet decided)
- Open for feedback
- May become ADR after acceptance
- Discussion-oriented

**Examples:**
```yaml
# RFC: New authentication system
type: rfc
area: [security, security/authentication]
audience: [architect, developer, security]
status: review
```

**Note:** NEW in v2.0 (identified as missing from usage analysis).

---

##### `changelog`
**Definition:** Version history, release notes, and change documentation.

**When to Use:**
- CHANGELOG.md files
- Release notes
- Version upgrade guides
- Breaking change notices

**Characteristics:**
- Reverse chronological order
- Categorized changes (added, changed, deprecated, removed, fixed, security)
- Version-tagged
- User-facing language

**Examples:**
```yaml
# Project changelog
type: changelog
special: [versioning]
audience: [developer, contributor, end-user]
```

**Note:** NEW in v2.0 (identified as missing from usage analysis).

---

### Status Tags

**Purpose:** Lifecycle stage and current state of the document
**Hierarchy:** Flat (no parent/child)
**Required:** Yes (exactly 1 tag)
**Mutually Exclusive:** Yes (only ONE status tag allowed)

#### Lifecycle States (7 tags)

##### `active`
**Definition:** Current, actively maintained, and authoritative documentation.

**When to Use:**
- Production-ready documentation
- Current best practices
- Maintained and up-to-date
- Primary reference

**Transitions From:** draft, review
**Transitions To:** deprecated, archived, superseded

**Usage:** 76% of documents (most common status)

---

##### `draft`
**Definition:** Work in progress, not yet reviewed or finalized.

**When to Use:**
- Initial documentation creation
- Major revisions in progress
- Not yet reviewed
- May contain placeholders

**Required Metadata:** `maintainer` (who's writing it)

**Transitions From:** planned
**Transitions To:** review, active, blocked

**Usage:** 8% of documents

**Note:** Replaces `in-progress` from v1.0 (redundant).

---

##### `review`
**Definition:** Complete and awaiting review/approval.

**When to Use:**
- Awaiting peer review
- Awaiting stakeholder approval
- Content complete, not yet approved
- Quality gate stage

**Required Metadata:** `reviewers` (who should review)

**Transitions From:** draft
**Transitions To:** active, draft (if revisions needed)

**Usage:** 5% of documents

---

##### `deprecated`
**Definition:** Marked for removal or replacement, but still accessible.

**When to Use:**
- Outdated practices
- Replaced by newer documentation
- Scheduled for removal
- No longer recommended

**Required Metadata:**
- `superseded_by` (link to replacement)
- `deprecation_reason` (why deprecated)
- `deprecation_date` (when marked deprecated)

**Transitions From:** active
**Transitions To:** archived, removed

**Usage:** 0% (no deprecated docs yet, but essential for lifecycle)

---

##### `superseded`
**Definition:** Replaced by a newer version of the same document.

**When to Use:**
- Old version of versioned document
- Historical reference only
- Specific version superseded (not the concept)

**Required Metadata:**
- `superseded_by` (link to new version)
- `superseded_date`

**Transitions From:** active, deprecated

**Usage:** 0% (retained for version control)

---

##### `archived`
**Definition:** Preserved for historical reference, no longer maintained.

**When to Use:**
- Historical documentation
- Compliance retention
- Deprecated and retained
- No longer relevant but preserved

**Required Metadata:** `archived_date`, `archived_reason`

**Transitions From:** active, deprecated, superseded

**Usage:** 0% (retained for retention policies)

---

##### `blocked`
**Definition:** Cannot proceed due to dependencies or external factors.

**When to Use:**
- Waiting for external deliverable
- Blocked by technical limitation
- Awaiting decision
- Dependency not yet met

**Required Metadata:**
- `blocked_reason` (what's blocking)
- `blocked_by` (who/what is blocking)
- `blocked_date`

**Transitions From:** draft
**Transitions To:** draft, active, archived

**Usage:** 0% (retained for workflow management)

---

**Removed in v2.0:**
- `in-progress` → Merged into `draft`
- `legacy` → Merged into `archived`
- `planned` → Removed (documentation shouldn't exist for non-existent features)

---

### Audience Tags

**Purpose:** Intended readers and appropriate access level
**Hierarchy:** Flat (no parent/child)
**Required:** Yes (1-4 tags)
**Cardinality:** Minimum 1, maximum 4

#### Reader Personas (12 tags)

##### `developer`
**Definition:** Software engineers, DevOps engineers, SREs, and technical implementers.

**Use for:**
- Source code documentation
- API references
- Development guides
- Technical implementations

**Skill Level:** Technical, hands-on coding

**Usage:** 40% of audience tags (most common)

---

##### `architect`
**Definition:** System architects, technical leads, principal engineers, and senior engineers.

**Use for:**
- Architecture decision records
- System design documents
- High-level technical specifications
- Integration architecture

**Skill Level:** Senior technical, design-focused

**Usage:** 22% of audience tags

---

##### `operator`
**Definition:** System operators, SREs, IT administrators, on-call staff.

**Use for:**
- Runbooks
- Operational procedures
- Monitoring and alerting
- Incident response

**Skill Level:** Operations-focused, production systems

**Usage:** 0% (retained for operational docs)

---

##### `executive`
**Definition:** C-level executives, investors, board members, and business stakeholders.

**Use for:**
- Whitepapers
- Business case studies
- Vision documents
- Executive summaries

**Skill Level:** Non-technical to semi-technical, business-focused

**Usage:** 0% (retained for business docs)

---

##### `legal`
**Definition:** Legal counsel, compliance officers, risk management, and regulatory experts.

**Use for:**
- Legal compliance documentation
- Privacy policies
- Terms of service
- Regulatory filings

**Skill Level:** Legal domain expertise

**Usage:** 0% (retained for legal docs)

---

##### `security`
**Definition:** Security engineers, penetration testers, security auditors, and InfoSec teams.

**Use for:**
- Threat models
- Security audits
- Vulnerability reports
- Security procedures

**Skill Level:** Security domain expertise

**Usage:** 0% (to be promoted)

**Note:** Replaces non-standard `security_engineer`, `security-engineers`.

---

##### `researcher`
**Definition:** AI researchers, data scientists, academic collaborators, and R&D teams.

**Use for:**
- Research papers
- AI system whitepapers
- Experimental features
- Academic collaborations

**Skill Level:** Research-focused, theoretical

**Usage:** 6% of audience tags

---

##### `contributor`
**Definition:** Open-source contributors, community members, and external developers.

**Use for:**
- Contribution guidelines
- Code of conduct
- Development setup
- Pull request process

**Skill Level:** Varying, external to core team

**Usage:** 6% of audience tags

---

##### `internal`
**Definition:** Project-AI internal team members only (restricted visibility).

**Use for:**
- Internal engineering notes
- Sensitive design decisions
- Team-specific processes
- Pre-release documentation

**Visibility:** Restricted (not public)

**Usage:** 0% (retained for access control)

---

##### `public`
**Definition:** General public, open-source community, and anyone with vault access.

**Use for:**
- Public-facing documentation
- Open-source project documentation
- Community resources
- Public whitepapers

**Visibility:** Public

**Usage:** 0% (to be promoted for OSS docs)

---

##### `end-user`
**Definition:** Non-technical application end users (people using the software, not building it).

**Use for:**
- User guides
- Help documentation
- FAQ for end users
- Feature tutorials

**Skill Level:** Non-technical

**Usage:** 6% of audience tags

**Note:** NEW in v2.0 (critical missing audience).

---

##### `ai-engineer`
**Definition:** AI/ML engineers, data scientists working on AI systems, and model developers.

**Use for:**
- AI system architecture
- Model training guides
- Constitutional AI documentation
- Persona system design

**Skill Level:** AI/ML domain expertise

**Usage:** 6% of audience tags

**Note:** NEW in v2.0 (specialized audience needed for AI-focused docs).

---

**Removed from v1.0:** None (audience tags all retained or added)

---

### Priority Tags

**Purpose:** Importance and urgency of the document
**Hierarchy:** Flat (no parent/child)
**Required:** Recommended (0-1 tag)
**Mutually Exclusive:** Yes (only ONE priority tag allowed)

#### Priority Levels (5 tags)

##### `P0`
**Definition:** Critical - Mission-critical, must review immediately.

**SLA:** 24 hours

**Use When:**
- Security vulnerabilities
- Production-breaking issues
- Legal compliance requirements
- Executive-level decisions
- Safety-critical documentation

**Usage:** 80% of prioritized documents (⚠️ Priority inflation concern)

**Examples:**
```yaml
# Security incident postmortem
type: postmortem
priority: P0

# Critical ADR
type: adr
priority: P0
```

---

##### `P1`
**Definition:** High - Important, review within 3 days.

**SLA:** 72 hours

**Use When:**
- High-impact features
- Major architectural decisions
- Important bug fixes
- Significant operational changes

**Usage:** 10% of prioritized documents

---

##### `P2`
**Definition:** Medium - Standard priority, review within 1 week.

**SLA:** 1 week

**Use When:**
- Standard features
- Routine updates
- Medium-impact changes
- Regular maintenance

**Usage:** 0% (should be default for most docs)

---

##### `P3`
**Definition:** Low - Nice to have, review when capacity allows.

**SLA:** No strict timeline

**Use When:**
- Minor improvements
- Cosmetic changes
- Low-impact updates
- Enhancement ideas

**Usage:** 0%

---

##### `P4`
**Definition:** Deferred - Backlog item, review during planning cycles.

**SLA:** Planning cycles only

**Use When:**
- Future considerations
- Experimental ideas
- Research items
- Long-term plans

**Usage:** 0%

---

**Note:** Priority distribution is unhealthy in current usage (80% P0). Consider:
- Only use priority for truly time-sensitive docs
- Leave most docs unprioritized
- Reserve P0 for genuine emergencies

---

### Special Tags

**Purpose:** Cross-cutting concerns or special characteristics
**Hierarchy:** Flat (no parent/child)
**Required:** No (0-10 tags)
**Cardinality:** Optional, up to 10 tags

**Note:** Special tags are CHARACTERISTICS, not document types. See [TYPE vs SPECIAL Decision Tree](#type-vs-special-decision-tree) for guidance.

#### Process & Workflow (6 tags)

##### `migration`
**Definition:** Migration processes, version upgrades, and platform transitions.

**Use When:**
- Database migrations
- Platform upgrades
- Version migration guides
- Technology transitions

**Example:**
```yaml
type: guide
special: [migration]
```

---

##### `integration`
**Definition:** System integration, external service connections, and API integrations.

**Use When:**
- Third-party integrations
- API integration guides
- Service mesh documentation
- Webhook implementations

---

##### `troubleshooting`
**Definition:** Problem diagnosis and resolution procedures.

**Use When:**
- Debugging guides
- Known issues documentation
- Error resolution procedures
- Diagnostic workflows

**Note:** High-value tag, should be heavily promoted.

---

##### `automation`
**Definition:** Automated processes, scripts, and workflow automation.

**Use When:**
- CI/CD pipelines
- Automated testing
- Script documentation
- Workflow automation

---

##### `versioning`
**Definition:** Version control, release management, and versioning strategies.

**Use When:**
- Semantic versioning guides
- Release management processes
- Version compatibility matrices

---

##### `backup-recovery`
**Definition:** Backup strategies, disaster recovery, and business continuity.

**Use When:**
- Backup procedures
- Disaster recovery plans
- Business continuity documentation
- Data retention policies

---

#### Quality & Performance (3 tags)

##### `best-practices`
**Definition:** Recommended patterns, proven approaches, and quality standards.

**Use When:**
- Style guides
- Design pattern catalogs
- Security best practices
- Performance optimization patterns

**Note:** High-value tag, should be heavily promoted.

---

##### `performance`
**Definition:** Performance optimization, benchmarking, and tuning.

**Use When:**
- Performance tuning guides
- Benchmark results
- Optimization techniques
- Scalability documentation

---

##### `testing`
**Definition:** Testing strategies, test documentation, and QA procedures.

**Use When:**
- Test strategy documentation
- QA procedures
- Test case documentation
- Test automation guides

---

#### Monitoring & Operations (1 tag)

##### `monitoring`
**Definition:** System monitoring, observability, and alerting.

**Use When:**
- Monitoring setup guides
- Observability strategies
- Dashboard documentation
- Alert configuration

---

#### Documentation Meta (5 tags)

##### `template`
**Definition:** Reusable templates for documents, code, or configurations.

**Use When:**
- Document templates
- Code scaffolding
- Configuration templates
- Boilerplate documentation

---

##### `tutorial`
**Definition:** Educational, step-by-step learning content with hands-on exercises.

**Use When:**
- Hands-on learning guides
- Step-by-step workshops
- Interactive learning content

**Note:** Use `type: guide` + `special: [tutorial]`, NOT `type: tutorial`.

---

##### `quickstart`
**Definition:** Getting started guides and quick setup documentation.

**Use When:**
- Getting started guides
- Quick setup procedures
- Hello World examples
- Rapid onboarding

**Note:** High-value tag, should be heavily promoted.

---

##### `faq`
**Definition:** Frequently asked questions and common inquiries.

**Use When:**
- FAQ documents
- Common questions
- Quick answers

**Note:** Use `type: reference` + `special: [faq]`, NOT `type: faq`.

---

##### `glossary`
**Definition:** Terminology definitions and vocabulary references.

**Use When:**
- Terminology glossaries
- Vocabulary references
- Acronym definitions

**Note:** Use `type: reference` + `special: [glossary]`, NOT `type: glossary`.

---

#### Status Modifiers (5 tags)

##### `experimental`
**Definition:** Experimental features, prototypes, and research implementations.

**Use When:**
- Experimental features
- Prototype documentation
- Research implementations
- Alpha/beta features

---

##### `deprecated-feature`
**Definition:** Documentation for features being phased out.

**Use When:**
- Features marked for removal
- Migration from deprecated features
- Backward compatibility notes

**Note:** Different from `status: deprecated` (which marks the *document* as deprecated).

---

##### `breaking-change`
**Definition:** Breaking changes requiring user action.

**Use When:**
- Breaking API changes
- Incompatible upgrades
- Migration required

---

##### `localization`
**Definition:** Internationalization, localization, and translation.

**Use When:**
- i18n/l10n documentation
- Translation guides
- Locale-specific documentation

**Note:** 0% usage, retained for future i18n needs.

---

##### `accessibility`
**Definition:** Accessibility standards, WCAG compliance, and inclusive design.

**Use When:**
- Accessibility guidelines
- WCAG compliance documentation
- Inclusive design patterns

**Note:** 0% usage, retained for future a11y program.

---

## Deprecated Categories

### Component Tags (DEPRECATED in v2.0)

**Reason for Deprecation:**
- **0% adoption** across entire vault after 6+ months
- Redundant with file path (e.g., `source-docs/gui/` already indicates GUI component)
- Redundant with content (documents explicitly name components)
- No clear use case for component-based filtering
- Adds tagging burden without demonstrated value

**Migration Path:**
- Remove `component:` field from frontmatter
- Use `area:` hierarchical tags for component-level granularity
- Rely on file path and content for component identification

**Retained Component Tags (3):**
For special cases where component is not obvious from path:

- `docker` - When documenting Docker but file isn't in docker directory
- `gradle` - When documenting Gradle in non-Gradle contexts
- `temporal` - When referencing Temporal workflow engine

**Example Migration:**
```yaml
# v1.0 (component tags)
type: source-doc
component: [gui, persona-system]

# v2.0 (no component, use area instead)
type: source-doc
area: [architecture, architecture/desktop]
```

---

## TYPE vs SPECIAL Decision Tree

**Problem:** Confusion between TYPE (document format) and SPECIAL (characteristics) causes misuse.

### Decision Tree

```
Q1: What is this document?
├─ A format/structure? → Use TYPE
│  ├─ How should I read it?
│  │  ├─ Sequentially (step-by-step) → type: guide
│  │  ├─ Lookup (find specific info) → type: reference
│  │  ├─ Analytical (findings + conclusions) → type: report
│  │  └─ Definitional (formal requirements) → type: spec
│  │
│  ├─ What is its primary purpose?
│  │  ├─ Navigation/discovery → type: index
│  │  ├─ API documentation → type: api-doc
│  │  ├─ Code documentation → type: source-doc
│  │  ├─ Operational procedures → type: runbook
│  │  ├─ Architectural decision → type: adr
│  │  ├─ Proposal for feedback → type: rfc
│  │  ├─ Incident analysis → type: postmortem
│  │  ├─ Version history → type: changelog
│  │  └─ Authoritative position → type: whitepaper
│
└─ A characteristic? → Use SPECIAL
   ├─ How was it created?
   │  └─ From a template → special: [template]
   │
   ├─ What's its purpose/scope?
   │  ├─ Quick onboarding → special: [quickstart]
   │  ├─ Learning via exercises → special: [tutorial]
   │  ├─ Problem resolution → special: [troubleshooting]
   │  ├─ Performance focus → special: [performance]
   │  ├─ Testing focus → special: [testing]
   │  └─ Migration focus → special: [migration]
   │
   └─ What's its status?
      ├─ Experimental/unproven → special: [experimental]
      ├─ Breaking compatibility → special: [breaking-change]
      └─ Deprecated feature → special: [deprecated-feature]
```

### Examples (Correct Usage)

```yaml
# ✅ Tutorial guide
type: guide
special: [tutorial, quickstart]
# Reasoning: Guide is the format, tutorial is the teaching method

# ✅ API troubleshooting reference
type: reference
special: [troubleshooting]
# Reasoning: Reference is the format, troubleshooting is the purpose

# ✅ Security audit report
type: report
special: [audit, troubleshooting]
# Reasoning: Report is the format, audit is the characteristic

# ✅ FAQ reference
type: reference
special: [faq]
# Reasoning: Reference is the format, FAQ is the characteristic

# ✅ Glossary reference
type: reference
special: [glossary]
# Reasoning: Reference is the format, glossary is the characteristic

# ✅ Migration runbook
type: runbook
special: [migration, automation]
# Reasoning: Runbook is the format, migration+automation are characteristics
```

### Examples (Wrong Usage from v1.0)

```yaml
# ❌ WRONG (from metadata-examples/)
type: tutorial

# ✅ CORRECT
type: guide
special: [tutorial]

# ❌ WRONG
type: faq

# ✅ CORRECT
type: reference
special: [faq]

# ❌ WRONG
type: troubleshooting

# ✅ CORRECT
type: guide
special: [troubleshooting]
# OR
type: reference
special: [troubleshooting]
```

---

## Validation Rules

### Automated Validation (CI/CD)

**Validation Script:** `scripts/validate-tags-strict.ps1`

**Validation Checks:**

1. **Tag Format Validation**
   - ✅ Lowercase only: `^[a-z0-9/-]+$`
   - ✅ Kebab-case (hyphens): No underscores
   - ✅ Singular form: No pluralized tags
   - ✅ No quotes: Detect and reject quoted tags
   - ✅ Max length: 30 characters
   - ✅ Valid characters: `a-z`, `0-9`, `-`, `/` only

2. **Cardinality Validation**
   - ✅ Area: 1-3 tags required
   - ✅ Type: 1-2 tags required
   - ✅ Status: Exactly 1 tag required
   - ✅ Audience: 1-4 tags required
   - ✅ Priority: 0-1 tags allowed
   - ✅ Special: 0-10 tags allowed

3. **Whitelist Validation**
   - ✅ All tags must exist in tag-hierarchy.json
   - ❌ Reject non-standard tags
   - ⚠️ Warn on deprecated tags

4. **Hierarchical Validation**
   - ✅ Child tags require parent tag present
     - Example: `architecture/backend` requires `architecture`
   - ✅ Parent must be valid parent tag
   - ❌ Reject orphaned child tags

5. **Mutual Exclusivity Validation**
   - ✅ Status: Only 1 status tag allowed
   - ✅ Priority: Only 1 priority tag allowed
   - ❌ Reject multiple mutually exclusive tags

6. **Deprecated Tag Validation**
   - ⚠️ Warn if using deprecated tag
   - 💡 Suggest replacement tag
   - 📅 Show migration deadline

### Validation Output Example

```
=== TAG VALIDATION REPORT ===

❌ ERRORS (Must Fix):
  templates/module-doc-core-system.md
    - type: "Module" → Not in taxonomy
      Suggestion: Use "source-doc"
    - audience: ["developer"] → Quoted tags
      Fix: Remove quotes: audience: [developer]

⚠️ WARNINGS (Should Fix):
  _indexes/by-area/security-domain-index.md
    - type: "by-area" → Non-standard
      Suggestion: Use "index"

✅ PASSED (67 files)

Compliance: 85% (67/78 files)
```

---

## Migration from v1.0

### Migration Strategy

**Phase 1: Fix Templates (Week 1)**
- Update 4 template files
- Remove quotes from audience tags
- Change `type: Module` to `type: source-doc`

**Phase 2: Fix Metadata Examples (Week 1-2)**
- Update 20 metadata example files
- Migrate non-standard type tags to standard equivalents
- Add special tags where appropriate

**Phase 3: Deploy Validation (Week 2)**
- Enable validate-tags-strict.ps1 in CI/CD
- Run validation on all files
- Generate compliance report

**Phase 4: Bulk Migration (Week 3)**
- Migrate non-standard tags using automated script
- Update deprecated tags
- Remove component category

**Phase 5: Enforcement (Week 4+)**
- Block PRs with validation failures
- Require 100% compliance for new docs

### Tag Migration Table

| v1.0 Tag | v2.0 Tag | Category | Action |
|----------|----------|----------|--------|
| `api_reference` | `api-doc` | type | Rename (underscore to hyphen) |
| `Module` | `source-doc` | type | Rename + lowercase |
| `decision_record` | `adr` | type | Rename (use standard abbreviation) |
| `specification` | `spec` | type | Abbreviate |
| `"developer"` | `developer` | audience | Remove quotes |
| `"architect"` | `architect` | audience | Remove quotes |
| `developers` | `developer` | audience | Singular form |
| `architects` | `architect` | audience | Singular form |
| `security_engineer` | `security` | audience | Use standard tag |
| `in-progress` | `draft` | status | Merge into draft |
| `legacy` | `archived` | status | Merge into archived |
| `production` | `active` | status | Use active |
| `completed` | `active` | status | Use active |
| `component: [any]` | (removed) | component | Remove field |
| `type: tutorial` | `type: guide` + `special: [tutorial]` | type→special | Move to special |
| `type: faq` | `type: reference` + `special: [faq]` | type→special | Move to special |
| `type: glossary` | `type: reference` + `special: [glossary]` | type→special | Move to special |

### Migration Script

```powershell
# migrate-tags-v1-to-v2.ps1

param(
    [string]$Path = "T:\Project-AI-vault",
    [switch]$DryRun = $false
)

$migrations = @(
    @{Old='api_reference'; New='api-doc'; Category='type'},
    @{Old='Module'; New='source-doc'; Category='type'},
    @{Old='decision_record'; New='adr'; Category='type'},
    @{Old='specification'; New='spec'; Category='type'},
    @{Old='in-progress'; New='draft'; Category='status'},
    @{Old='legacy'; New='archived'; Category='status'},
    @{Old='production'; New='active'; Category='status'},
    @{Old='completed'; New='active'; Category='status'},
    @{Old='developers'; New='developer'; Category='audience'},
    @{Old='architects'; New='architect'; Category='audience'},
    @{Old='security_engineer'; New='security'; Category='audience'}
)

Get-ChildItem -Path $Path -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $modified = $false

    foreach ($mig in $migrations) {
        $pattern = "$($mig.Category):\s*$($mig.Old)"
        if ($content -match $pattern) {
            $content = $content -replace $pattern, "$($mig.Category): $($mig.New)"
            $modified = $true
            Write-Host "[$($_.Name)] Migrated $($mig.Old) → $($mig.New)"
        }
    }

    # Remove component field
    $content = $content -replace 'component:.*\n', ''

    # Remove quotes from arrays
    $content = $content -replace '\["([^"]+)"\]', '[$1]'

    if ($modified -and -not $DryRun) {
        Set-Content $_.FullName -Value $content
    }
}
```

**Usage:**
```powershell
# Dry run (preview changes)
.\migrate-tags-v1-to-v2.ps1 -DryRun

# Execute migration
.\migrate-tags-v1-to-v2.ps1
```

---

## Examples

### Example 1: Security Audit Report

```yaml
---
type: report
area: [security, security/audit]
status: active
audience: [security, developer, executive]
priority: P0
special: [audit, troubleshooting]
maintainer: "Security Team"
created: 2025-01-20
updated: 2025-01-20
tags:
  - security
  - audit
  - compliance
  - bcrypt
  - password-hashing
---
```

**Justification:**
- **type: report** → Format is analytical report
- **area: security + security/audit** → Security domain, audit subdomain
- **audience: 3 groups** → Security team, developers (to fix), executives (awareness)
- **priority: P0** → Security issues are critical
- **special: audit + troubleshooting** → Audit characteristic + fixes issues

---

### Example 2: PyQt6 Developer Guide

```yaml
---
type: guide
area: [development, development/python]
status: active
audience: [developer, contributor]
priority: P2
special: [quickstart, tutorial]
maintainer: "AGENT-016"
created: 2025-01-15
tags:
  - gui
  - pyqt6
  - getting-started
---
```

**Justification:**
- **type: guide** → Step-by-step instructional format
- **area: development/python** → Python development domain
- **special: quickstart + tutorial** → Quick onboarding with hands-on exercises

---

### Example 3: Constitutional AI Whitepaper

```yaml
---
type: whitepaper
area: [governance, governance/ethics]
status: active
audience: [executive, researcher, public, legal]
priority: P0
special: [best-practices]
maintainer: "Executive Team"
created: 2024-01-01
tags:
  - constitutional-ai
  - ethics
  - governance
  - four-laws
---
```

**Justification:**
- **type: whitepaper** → Authoritative research document
- **area: governance/ethics** → Ethics governance domain
- **audience: 4 groups** → Executives (vision), researchers (theory), public (transparency), legal (compliance)
- **priority: P0** → Foundational document

---

### Example 4: Docker Deployment Runbook

```yaml
---
type: runbook
area: [operations, operations/deployment]
status: active
audience: [operator, developer]
priority: P1
special: [quickstart, automation, troubleshooting]
maintainer: "DevOps Team"
created: 2025-01-10
tags:
  - docker
  - deployment
  - ci-cd
---
```

**Justification:**
- **type: runbook** → Operational procedure
- **area: operations/deployment** → Deployment operations domain
- **special: 3 tags** → Quick setup, automated process, includes troubleshooting

---

### Example 5: API Reference Documentation

```yaml
---
type: api-doc
area: [development, development/api]
status: active
audience: [developer, contributor, public]
priority: P2
special: []
maintainer: "API Team"
created: 2025-01-12
tags:
  - rest-api
  - authentication
  - endpoints
---
```

**Justification:**
- **type: api-doc** → API-specific documentation
- **area: development/api** → API development domain
- **special: none** → No cross-cutting characteristics

---

## Maintenance

### Quarterly Tag Review (AGENT-039 Role)

**Frequency:** Every 3 months

**Process:**
1. **Usage Analysis:**
   - Run tag frequency analysis
   - Identify tags with <5% usage
   - Identify non-standard tags in use

2. **Gap Analysis:**
   - Collect new tag requests
   - Identify concepts without tags
   - Evaluate emerging patterns

3. **Deprecation Candidates:**
   - Tags with 0 usage for 6+ months
   - Redundant tags
   - Over-specific tags

4. **Recommendations:**
   - Propose new tags (with justification)
   - Propose tag deprecations (with migration path)
   - Propose taxonomy restructuring (if needed)

5. **Update Taxonomy:**
   - Increment version (2.1, 2.2, etc.)
   - Update tag-hierarchy.json
   - Update TAG_TAXONOMY.md
   - Create TAG_MIGRATION_GUIDE.md

### Tag Addition Workflow

**Requester:** Any team member
**Reviewer:** Tag Taxonomy Specialist (AGENT-039 role)

**Steps:**
1. **Request:** Submit tag addition request with:
   - Proposed tag name
   - Category (area, type, status, audience, priority, special)
   - Definition
   - Use cases (3+ examples)
   - Projected usage (how many docs?)

2. **Review:** Tag specialist evaluates:
   - Is there an existing tag that covers this?
   - Does it fit taxonomy structure?
   - Is it too specific or too broad?
   - What's the migration path for existing docs?

3. **Approval:** If approved:
   - Add to tag-hierarchy.json
   - Add to TAG_TAXONOMY.md
   - Update validation script
   - Announce to team

4. **Rejection:** If rejected:
   - Explain which existing tag to use instead
   - Document decision for future reference

---

## Version History

### v2.0 (2025-01-23)
- **Initial v2.0 release** based on comprehensive usage analysis
- Added 5 new tags: postmortem, rfc, changelog, end-user, ai-engineer
- Deprecated component category (0% adoption)
- Removed 40 unused tags (area children, status variants)
- Clarified TYPE vs SPECIAL distinction with decision tree
- Updated validation rules and migration guide
- Reduced total tags from 120 to 85 (29% reduction)

### v1.0 (2025-01-20)
- Initial release by AGENT-017
- Defined 120 tags across 7 categories
- Established hierarchical structure
- Created tag-hierarchy.json schema

---

**Document Status:** Active
**Next Review:** 2025-04-23 (Quarterly)
**Maintainer:** AGENT-039 (Tag Taxonomy Refinement Specialist)
**Compliance Target:** 90% by 2025-02-23

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
