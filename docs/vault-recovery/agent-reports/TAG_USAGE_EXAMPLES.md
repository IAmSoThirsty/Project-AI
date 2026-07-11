# Tag Taxonomy Usage Examples

> **Quick Reference for Tag Selection**
> **Version:** 1.0
> **Last Updated:** 2025-01-20
> **See Also:** TAG_TAXONOMY.md (complete reference)

---

## Quick Tag Selection Guide

### Step-by-Step Process

1. **Identify Area(s)** - What domain does this cover? (1-3 tags)
2. **Select Type** - What format is this document? (1-2 tags)
3. **List Components** - What systems/modules are covered? (0-5 tags)
4. **Set Status** - What lifecycle stage? (exactly 1 tag)
5. **Define Audience** - Who should read this? (1-4 tags)
6. **Assign Priority** - How urgent? (0-1 tag, optional)
7. **Add Special Tags** - Any cross-cutting concerns? (0-10 tags)

---

## 25 Real-World Examples

### Example 1: Security Audit Report

**Document:** Annual security audit of authentication systems

```yaml
---
title: "2025 Security Audit - User Authentication"
status: active
priority: P0

tags:
  # Area (2 tags)
  - security
  - security/audit

  # Type (1 tag)
  - report

  # Component (3 tags)
  - user-manager
  - command-override
  - security/authentication

  # Audience (3 tags)
  - security
  - developer
  - executive

  # Special (2 tags)
  - troubleshooting
  - best-practices
---
```

**Rationale:**
- Security + audit area (primary concern)
- Report type (findings document)
- Specific components audited
- Multiple audiences (security team, devs who fix, execs who approve budget)
- P0 because security is critical
- Troubleshooting (helps fix issues) + best-practices (recommendations)

---

### Example 2: PyQt6 Developer Guide

**Document:** Step-by-step guide for GUI development

```yaml
---
title: "PyQt6 GUI Development Guide"
status: active
priority: P2

tags:
  # Area (2 tags)
  - development
  - development/python

  # Type (1 tag)
  - guide

  # Component (2 tags)
  - gui
  - persona-system

  # Audience (2 tags)
  - developer
  - contributor

  # Special (2 tags)
  - quickstart
  - tutorial
---
```

**Rationale:**
- Development/Python area (coding focus)
- Guide type (how-to instructions)
- GUI + persona components (specific systems)
- Developer + contributor audience (open to community)
- P2 standard priority (not urgent, not trivial)
- Quickstart + tutorial (learning-focused)

---

### Example 3: Constitutional AI Whitepaper

**Document:** Research paper on Four Laws implementation

```yaml
---
title: "Constitutional AI: Asimov's Laws in Code"
status: active
priority: P0

tags:
  # Area (2 tags)
  - governance
  - governance/constitutional-ai

  # Type (1 tag)
  - whitepaper

  # Component (3 tags)
  - constitutional-ai
  - governance-engine
  - agents

  # Audience (4 tags - broad reach)
  - executive
  - researcher
  - public
  - legal

  # Special (1 tag)
  - best-practices
---
```

**Rationale:**
- Governance/constitutional-ai (core area)
- Whitepaper (research-backed)
- All related components
- Broad audience (execs for strategy, researchers for citations, public for transparency, legal for compliance)
- P0 (foundational document)
- Best-practices (recommended approach)

---

### Example 4: Docker Deployment Runbook

**Document:** Operations guide for deploying with Docker

```yaml
---
title: "Docker Compose Deployment Runbook"
status: active
priority: P1

tags:
  # Area (2 tags)
  - operations
  - operations/deployment

  # Type (1 tag)
  - runbook

  # Component (2 tags)
  - docker
  - hydra-swarm

  # Audience (2 tags)
  - operator
  - developer

  # Special (3 tags)
  - quickstart
  - troubleshooting
  - automation
---
```

**Rationale:**
- Operations/deployment (ops focus)
- Runbook (step-by-step procedures)
- Docker + Hydra components
- Operator primary, developer secondary
- P1 (deployment is important)
- Quickstart (fast path), troubleshooting (fixes), automation (CI/CD integration)

---

### Example 5: API Reference Documentation

**Document:** Complete API reference for intelligence engine

```yaml
---
title: "Intelligence Engine API Reference"
status: active
priority: P2

tags:
  # Area (2 tags)
  - development
  - development/api

  # Type (1 tag)
  - api-doc

  # Component (3 tags)
  - intelligence-engine
  - user-manager
  - memory-system

  # Audience (3 tags)
  - developer
  - contributor
  - public

  # Special (0 tags)
---
```

**Rationale:**
- Development/API area
- API-doc type (specific format)
- All APIs documented
- Public-facing (open documentation)
- P2 standard priority
- No special tags (straightforward reference)

---

### Example 6: Incident Response Runbook

**Document:** Critical incident response procedures

```yaml
---
title: "Security Incident Response Runbook"
status: active
priority: P0

tags:
  # Area (3 tags - cross-cutting)
  - operations
  - operations/troubleshooting
  - security

  # Type (1 tag)
  - runbook

  # Component (2 tags)
  - cerberus
  - hydra-swarm

  # Audience (2 tags)
  - operator
  - security

  # Special (2 tags)
  - troubleshooting
  - monitoring
---
```

**Rationale:**
- Operations + security (cross-cutting concern)
- Runbook (operational procedures)
- Cerberus + Hydra (multi-process oversight)
- Operator + security (on-call staff)
- P0 (critical incidents)
- Troubleshooting + monitoring (incident handling)

---

### Example 7: TARL Language Specification

**Document:** Formal specification of TARL language

```yaml
---
title: "TARL Language Specification v2.0"
status: active
priority: P0

tags:
  # Area (2 tags)
  - governance
  - architecture

  # Type (1 tag)
  - spec

  # Component (2 tags)
  - thirsty-lang
  - tarl

  # Audience (3 tags)
  - architect
  - developer
  - researcher

  # Special (0 tags)
---
```

**Rationale:**
- Governance + architecture (policy language)
- Spec (formal specification)
- TARL components
- Technical audiences
- P0 (foundational)
- No special tags (formal spec)

---

### Example 8: Plugin Development Tutorial

**Document:** Tutorial for creating plugins

```yaml
---
title: "Plugin Development Tutorial"
status: active
priority: P3

tags:
  # Area (2 tags)
  - development
  - development/python

  # Type (1 tag)
  - guide

  # Component (1 tag)
  - plugin-system

  # Audience (2 tags)
  - developer
  - contributor

  # Special (3 tags)
  - tutorial
  - quickstart
  - template
---
```

**Rationale:**
- Development/Python (coding tutorial)
- Guide type
- Plugin system only
- Developer + contributor
- P3 (nice to have, not critical)
- Tutorial + quickstart + template (learning resources)

---

### Example 9: Bcrypt Implementation Guide

**Document:** Security guide for password hashing

```yaml
---
title: "Bcrypt Password Hashing Implementation"
status: active
priority: P1

tags:
  # Area (2 tags)
  - security
  - security/authentication

  # Type (2 tags)
  - guide
  - source-doc

  # Component (1 tag)
  - user-manager

  # Audience (1 tag)
  - developer

  # Special (2 tags)
  - best-practices
  - tutorial
---
```

**Rationale:**
- Security/authentication area
- Guide + source-doc (code examples)
- User-manager component
- Developer audience
- P1 (security is important)
- Best-practices + tutorial

---

### Example 10: GitHub Actions CI/CD

**Document:** CI/CD pipeline documentation

```yaml
---
title: "GitHub Actions CI/CD Pipeline"
status: active
priority: P2

tags:
  # Area (2 tags)
  - development
  - development/ci-cd

  # Type (1 tag)
  - guide

  # Component (0 tags - no specific component)

  # Audience (2 tags)
  - developer
  - operator

  # Special (2 tags)
  - automation
  - best-practices
---
```

**Rationale:**
- Development/CI-CD area
- Guide type
- No specific component (general CI/CD)
- Developer + operator
- P2 standard
- Automation + best-practices

---

### Example 11: Deprecated MD5 Migration

**Document:** Migration guide from MD5 to SHA-256

```yaml
---
title: "Migrate from MD5 to SHA-256"
status: deprecated
priority: P1
superseded_by: "[[SHA256_IMPLEMENTATION.md]]"

tags:
  # Area (2 tags)
  - security
  - security/cryptography

  # Type (1 tag)
  - guide

  # Component (1 tag)
  - user-manager

  # Audience (1 tag)
  - developer

  # Special (3 tags)
  - migration
  - breaking-change
  - deprecated-feature
---
```

**Rationale:**
- Security/cryptography area
- Guide type (migration steps)
- User-manager component
- Developer audience
- P1 (security fix needed)
- Deprecated status with superseded_by
- Migration + breaking-change + deprecated-feature

---

### Example 12: Temporal Workflow Integration

**Document:** Integration guide for Temporal

```yaml
---
title: "Temporal Workflow Integration Guide"
status: active
priority: P2

tags:
  # Area (3 tags)
  - architecture
  - architecture/integration
  - operations

  # Type (2 tags)
  - guide
  - spec

  # Component (1 tag)
  - temporal

  # Audience (3 tags)
  - architect
  - developer
  - operator

  # Special (2 tags)
  - integration
  - quickstart
---
```

**Rationale:**
- Architecture/integration + operations
- Guide + spec (hybrid)
- Temporal component
- Multiple audiences (design, implement, operate)
- P2 standard
- Integration + quickstart

---

### Example 13: Emergency Alert System

**Document:** Emergency alert system documentation

```yaml
---
title: "Emergency Alert System Documentation"
status: active
priority: P1

tags:
  # Area (2 tags)
  - operations
  - security

  # Type (2 tags)
  - guide
  - spec

  # Component (1 tag)
  - emergency-alert

  # Audience (2 tags)
  - developer
  - operator

  # Special (1 tag)
  - integration
---
```

**Rationale:**
- Operations + security (emergency response)
- Guide + spec (how to use + technical spec)
- Emergency-alert component
- Developer + operator
- P1 (emergency systems are important)
- Integration (email/SMS setup)

---

### Example 14: Prometheus Monitoring Setup

**Document:** Monitoring system setup guide

```yaml
---
title: "Prometheus Monitoring Setup Guide"
status: active
priority: P1

tags:
  # Area (2 tags)
  - operations
  - operations/monitoring

  # Type (1 tag)
  - guide

  # Component (0 tags - external tool)

  # Audience (2 tags)
  - operator
  - developer

  # Special (3 tags)
  - monitoring
  - automation
  - quickstart
---
```

**Rationale:**
- Operations/monitoring area
- Guide type
- No component (Prometheus is external)
- Operator primary, developer secondary
- P1 (monitoring is critical)
- Monitoring + automation + quickstart

---

### Example 15: AGI Charter

**Document:** AGI rights and ethics charter

```yaml
---
title: "AGI Charter: Rights, Dignity, and Governance"
status: active
priority: P0

tags:
  # Area (3 tags)
  - governance
  - governance/ethics
  - legal

  # Type (2 tags)
  - whitepaper
  - spec

  # Component (1 tag)
  - constitutional-ai

  # Audience (4 tags - maximum reach)
  - executive
  - legal
  - public
  - researcher

  # Special (1 tag)
  - best-practices
---
```

**Rationale:**
- Governance/ethics + legal
- Whitepaper + spec (research + formal)
- Constitutional-AI component
- Broad audience (all stakeholders)
- P0 (foundational charter)
- Best-practices

---

### Example 16: Learning System Black Vault

**Document:** Black Vault specification

```yaml
---
title: "Black Vault Specification - Forbidden Knowledge"
status: active
priority: P1

tags:
  # Area (2 tags)
  - governance
  - architecture

  # Type (1 tag)
  - spec

  # Component (2 tags)
  - learning-system
  - constitutional-ai

  # Audience (2 tags)
  - architect
  - developer

  # Special (1 tag)
  - best-practices
---
```

**Rationale:**
- Governance + architecture (policy enforcement)
- Spec type (formal specification)
- Learning + constitutional-ai
- Architect + developer
- P1 (governance system)
- Best-practices

---

### Example 17: Hydra Swarm Architecture

**Document:** Multi-process architecture whitepaper

```yaml
---
title: "Hydra Swarm: Multi-Process Sovereignty"
status: active
priority: P0

tags:
  # Area (2 tags)
  - architecture
  - architecture/distributed

  # Type (2 tags)
  - whitepaper
  - spec

  # Component (2 tags)
  - hydra-swarm
  - cerberus

  # Audience (3 tags)
  - architect
  - executive
  - researcher

  # Special (1 tag)
  - best-practices
---
```

**Rationale:**
- Architecture/distributed
- Whitepaper + spec (research + formal)
- Hydra + Cerberus
- High-level audiences
- P0 (core architecture)
- Best-practices

---

### Example 18: Index Template

**Document:** Template for creating indexes

```yaml
---
title: "Index Template Documentation"
status: active
priority: P2

tags:
  # Area (1 tag)
  - operations

  # Type (2 tags)
  - template
  - index

  # Component (0 tags)

  # Audience (2 tags)
  - developer
  - internal

  # Special (2 tags)
  - template
  - automation
---
```

**Rationale:**
- Operations area (documentation ops)
- Template + index type
- No component (meta-documentation)
- Developer + internal
- P2 standard
- Template + automation

---

### Example 19: Fernet Encryption Guide

**Document:** Encryption implementation guide

```yaml
---
title: "Fernet Encryption Best Practices"
status: active
priority: P1

tags:
  # Area (2 tags)
  - security
  - security/cryptography

  # Type (1 tag)
  - guide

  # Component (1 tag)
  - location-tracker

  # Audience (2 tags)
  - security
  - developer

  # Special (1 tag)
  - best-practices
---
```

**Rationale:**
- Security/cryptography
- Guide type
- Location-tracker (uses Fernet)
- Security + developer
- P1 (encryption is important)
- Best-practices

---

### Example 20: Troubleshooting FAQ

**Document:** Common issues and solutions

```yaml
---
title: "Project-AI Troubleshooting FAQ"
status: active
priority: P2

tags:
  # Area (2 tags)
  - operations
  - operations/troubleshooting

  # Type (1 tag)
  - guide

  # Component (0 tags - general)

  # Audience (3 tags)
  - developer
  - operator
  - contributor

  # Special (2 tags)
  - troubleshooting
  - faq
---
```

**Rationale:**
- Operations/troubleshooting
- Guide type
- No specific component (general FAQ)
- Broad technical audience
- P2 standard
- Troubleshooting + FAQ

---

### Example 21: Gradle Build Configuration

**Document:** Build system configuration guide

```yaml
---
title: "Gradle Build System Configuration"
status: active
priority: P2

tags:
  # Area (2 tags)
  - development
  - development/tooling

  # Type (2 tags)
  - guide
  - reference

  # Component (1 tag)
  - gradle

  # Audience (1 tag)
  - developer

  # Special (2 tags)
  - quickstart
  - best-practices
---
```

**Rationale:**
- Development/tooling
- Guide + reference (hybrid)
- Gradle component
- Developer audience
- P2 standard
- Quickstart + best-practices

---

### Example 22: MIT License Documentation

**Document:** License and legal documentation

```yaml
---
title: "MIT License - Project-AI"
status: active
priority: P0

tags:
  # Area (2 tags)
  - legal
  - legal/licensing

  # Type (1 tag)
  - reference

  # Component (0 tags)

  # Audience (3 tags)
  - legal
  - public
  - executive

  # Special (0 tags)
---
```

**Rationale:**
- Legal/licensing
- Reference type
- No component (project-wide)
- Legal + public + executive
- P0 (legal compliance)
- No special tags

---

### Example 23: React Frontend Architecture (Draft)

**Document:** WIP architecture document

```yaml
---
title: "React Frontend Architecture v2.0"
status: draft
priority: P2
maintainer: "AGENT-042"

tags:
  # Area (3 tags)
  - architecture
  - architecture/frontend
  - architecture/web

  # Type (2 tags)
  - spec
  - adr

  # Component (1 tag)
  - web

  # Audience (2 tags)
  - architect
  - developer

  # Special (0 tags)
---
```

**Rationale:**
- Architecture/frontend/web
- Spec + ADR (decision document)
- Web component
- Architect + developer
- P2 standard
- Draft status (not yet finalized)
- Maintainer specified (required for draft/in-progress)

---

### Example 24: Performance Optimization Runbook

**Document:** Performance tuning procedures

```yaml
---
title: "Performance Optimization Runbook"
status: active
priority: P1

tags:
  # Area (2 tags)
  - operations
  - operations/performance

  # Type (1 tag)
  - runbook

  # Component (0 tags - system-wide)

  # Audience (2 tags)
  - operator
  - developer

  # Special (2 tags)
  - performance
  - troubleshooting
---
```

**Rationale:**
- Operations/performance
- Runbook type
- No specific component (general optimization)
- Operator + developer
- P1 (performance matters)
- Performance + troubleshooting

---

### Example 25: Experimental SNN Integration (Planned)

**Document:** Future feature specification

```yaml
---
title: "Spiking Neural Network Co-Processor Integration"
status: planned
priority: P3
target_date: "2025-Q3"
milestone: "v3.0"

tags:
  # Area (2 tags)
  - architecture
  - architecture/integration

  # Type (1 tag)
  - spec

  # Component (0 tags - future component)

  # Audience (2 tags)
  - architect
  - researcher

  # Special (1 tag)
  - experimental
---
```

**Rationale:**
- Architecture/integration
- Spec type (planning document)
- No component yet (future)
- Architect + researcher
- P3 (future work)
- Planned status with target_date and milestone
- Experimental tag

---

## Tag Combination Patterns

### Common Patterns

**Security Documentation:**
```yaml
tags: [security, security/*, report|guide, component, security, P0, troubleshooting]
```

**Developer Guides:**
```yaml
tags: [development, development/*, guide, component, developer, P2, tutorial|quickstart]
```

**Operational Runbooks:**
```yaml
tags: [operations, operations/*, runbook, component, operator, P1, troubleshooting]
```

**Architecture Specs:**
```yaml
tags: [architecture, architecture/*, spec, component, architect, P1]
```

**Executive Whitepapers:**
```yaml
tags: [executive|governance, executive/*, whitepaper, component, executive, P0]
```

**Legal Documentation:**
```yaml
tags: [legal, legal/*, reference|spec, legal+public, P0]
```

---

## Anti-Patterns (What NOT to Do)

❌ **Over-tagging:**
```yaml
# BAD: Too many tags, redundant, not useful
tags: [security, security/audit, security/authentication, security/cryptography,
       report, guide, spec, user-manager, command-override, memory-system,
       developer, architect, operator, executive, legal, security,
       P0, P1, troubleshooting, best-practices, quickstart, tutorial, faq]
```

✅ **Focused tagging:**
```yaml
# GOOD: Precise, relevant, discoverable
tags: [security, security/audit, report, user-manager,
       security+developer, P0, troubleshooting]
```

---

❌ **Vague tagging:**
```yaml
# BAD: Not specific enough
tags: [development, guide, developer]
```

✅ **Specific tagging:**
```yaml
# GOOD: Clear intent and scope
tags: [development, development/python, guide, gui, developer, tutorial]
```

---

❌ **Missing required tags:**
```yaml
# BAD: Missing status, audience
tags: [security, report, user-manager]
```

✅ **Complete tagging:**
```yaml
# GOOD: All required categories
tags: [security, security/audit, report, user-manager,
       active, security+developer, P0]
```

---

❌ **Invalid hierarchy:**
```yaml
# BAD: Child tag without parent
tags: [security/cryptography, report, active, developer]
```

✅ **Valid hierarchy:**
```yaml
# GOOD: Parent tag included
tags: [security, security/cryptography, report, active, developer]
```

---

## Quick Reference Table

| Category | Required | Min | Max | Example |
|----------|----------|-----|-----|---------|
| **Area** | Yes | 1 | 3 | `security`, `security/audit` |
| **Type** | Yes | 1 | 2 | `guide`, `report` |
| **Component** | No | 0 | 5 | `user-manager`, `gui` |
| **Status** | Yes | 1 | 1 | `active`, `draft` |
| **Audience** | Yes | 1 | 4 | `developer`, `executive` |
| **Priority** | Recommended | 0 | 1 | `P0`, `P1`, `P2` |
| **Special** | No | 0 | 10 | `quickstart`, `tutorial` |

---

## Validation

Always run validation before committing:

```powershell
# Validate single file
.\validate-tags.ps1 -Path "my-document.md" -Verbose

# Validate directory
.\validate-tags.ps1 -Path "T:\Project-AI-vault\repo-docs"

# Generate HTML report
.\validate-tags.ps1 -Path "." -OutputFormat HTML -ReportPath "validation-report.html"
```

---

**Last Updated:** 2025-01-20
**Version:** 1.0
**See Also:** TAG_TAXONOMY.md, tag-hierarchy.json, validate-tags.ps1

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
