---
# METADATA - Required for all index files
index_type: "by-area"
index_scope: "security"
last_updated: "2024-01-15"
maintainer: "AGENT-002"
total_documents: 8
metadata_schema_version: "1.0"
priority_distribution:
  p0: 3
  p1: 3
  p2: 2
  p3: 0
status_distribution:
  active: 6
  planned: 1
  in_progress: 1
  review: 0
  archived: 0
  deprecated: 0
  superseded: 0
tags:
  - index
  - navigation
  - security
  - audit
related_indexes:
  - "[[architecture-domain-index]]"
  - "[[compliance-domain-index]]"
coverage_percentage: 75
---

# Security Domain Index

> **Index Type:** by-area  
> **Scope:** All security-related documentation including threat models, audits, policies, and standards  
> **Maintainer:** AGENT-002  
> **Last Updated:** 2024-01-15

## Overview

This index provides comprehensive navigation to all security documentation in the Project-AI vault. It encompasses threat modeling, security audits, compliance policies, authentication/authorization standards, encryption requirements, and vulnerability assessments. Use this index as your primary entry point for security reviews, incident response, compliance audits, and security architecture decisions.

**Use This Index When:**
- Conducting security reviews or audits
- Responding to security incidents
- Implementing authentication or authorization features
- Ensuring compliance with security policies
- Assessing security posture across domains

**Related Indexes:**
- [[architecture-domain-index]] - For architecture decisions affecting security
- [[compliance-domain-index]] - For regulatory compliance requirements
- [[api-domain-index]] - For API security specifications

---

## Contents

### Threat Models (P0)

> **Section Description:** Security threat analysis and mitigation strategies for critical system components

- [[threat-model-authentication]] - Authentication system threat analysis and mitigations (P0, Active)
  - **Key Topics:** password-attacks, session-hijacking, brute-force-protection
  - **Dependencies:** [[standard-password-policy]], [[adr-005-bcrypt-hashing]]
  - **Last Reviewed:** 2024-01-10
  
- [[threat-model-data-encryption]] - Data encryption at rest and in transit threat model (P0, Active)
  - **Key Topics:** encryption-algorithms, key-management, tls-configuration
  - **Related:** [[standard-encryption-requirements]]
  - **Last Reviewed:** 2024-01-08

- [[threat-model-api-security]] - API security threat model covering injection, CSRF, rate limiting (P0, Active)
  - **Key Topics:** sql-injection, xss-prevention, csrf-protection, rate-limiting
  - **Dependencies:** [[api-security-specification]]
  - **Last Reviewed:** 2024-01-12

### Security Audits (P1)

> **Section Description:** Security assessment reports and audit findings

- [[security-audit-2024-q1]] - Q1 2024 comprehensive security audit (P1, In-Progress)
  - **Key Topics:** vulnerability-scan, penetration-testing, code-review
  - **Related:** [[security-audit-action-plan-2024-q1]]
  - **Last Reviewed:** 2024-01-15

- [[security-audit-authentication-system]] - Focused audit of authentication implementation (P1, Active)
  - **Key Topics:** password-storage, session-management, oauth-implementation
  - **Dependencies:** [[threat-model-authentication]]
  - **Last Reviewed:** 2024-01-05

### Security Standards (P0)

> **Section Description:** Mandatory security policies and implementation standards

- [[standard-password-policy]] - Password complexity, rotation, and storage requirements (P0, Active)
  - **Key Topics:** password-complexity, bcrypt-hashing, password-rotation
  - **Dependencies:** [[adr-005-bcrypt-hashing]]
  - **Last Reviewed:** 2024-01-10

- [[standard-encryption-requirements]] - Encryption standards for data at rest and in transit (P0, Active)
  - **Key Topics:** aes-256, tls-1.3, fernet-encryption, key-rotation
  - **Related:** [[threat-model-data-encryption]]
  - **Last Reviewed:** 2024-01-08

### Security Runbooks (P1)

> **Section Description:** Operational procedures for security incidents and routine security tasks

- [[runbook-security-incident-response]] - Step-by-step incident response procedures (P1, Planned)
  - **Key Topics:** incident-triage, containment, forensics, post-mortem
  - **Dependencies:** [[standard-incident-classification]]
  - **Last Reviewed:** 2024-01-15

---

## Quick Reference

### High-Priority Documents (P0/P1)

Critical documents that should be reviewed first:

1. [[threat-model-authentication]] - Authentication threat model (P0)
2. [[threat-model-data-encryption]] - Encryption threat model (P0)
3. [[standard-password-policy]] - Password requirements (P0)
4. [[standard-encryption-requirements]] - Encryption standards (P0)
5. [[threat-model-api-security]] - API security threats (P0)

### Recently Updated

Documents updated in the last 30 days:

- [[security-audit-2024-q1]] - Updated 2024-01-15
- [[threat-model-api-security]] - Updated 2024-01-12
- [[threat-model-authentication]] - Updated 2024-01-10

### Deprecated/Superseded

No deprecated security documents currently. All security documentation is maintained as active.

---

## Statistics

**Document Counts:**
- Total Documents: 8
- Active: 6
- Archived: 0
- Deprecated: 0
- In Progress: 1
- Planned: 1

**Priority Distribution:**
- P0 (Critical): 3
- P1 (High): 3
- P2 (Medium): 2
- P3 (Low): 0

**Last Major Update:** 2024-01-15  
**Index Version:** 1.0  
**Coverage:** 75% of security domain

---

## Cross-References

### Dependencies

This index contains documents that depend on:
- [[adr-005-bcrypt-hashing]] from [[adr-type-index]] (password hashing decision)
- [[api-security-specification]] from [[api-domain-index]] (API security requirements)

### Dependents

Documents in other indexes that depend on this content:
- [[architecture-authentication]] in [[architecture-domain-index]]
- [[guide-user-registration]] in [[guide-type-index]]
- [[api-v2-specification]] in [[specification-type-index]]

### Related Domains

See also:
- [[compliance-domain-index]] - For GDPR, SOC2, and regulatory compliance
- [[architecture-domain-index]] - For security architecture decisions
- [[api-domain-index]] - For API security specifications

---

## Maintenance Notes

### Update Triggers

This index should be updated when:
- [x] New security documents added (threat models, audits, standards)
- [x] Document status changes (Active → Deprecated, etc.)
- [x] Security vulnerabilities discovered requiring new threat models
- [x] Security audit completed with new findings
- [x] Quarterly security documentation review

### Validation Checklist

Before committing index updates:
- [x] All document links resolve correctly (no broken links)
- [x] Metadata block is complete and accurate
- [x] Priority/status annotations are current
- [x] Statistics block reflects actual counts
- [x] No duplicate entries
- [x] Last updated date is current
- [x] Related indexes are updated if needed

### Quality Standards

- **Link Format:** Use `[[wikilink]]` format, not markdown links
- **Annotations:** Always include (Priority, Status) for documents
- **Descriptions:** Keep to one line, under 100 characters
- **Sectioning:** Group logically by document type (Threat Models, Audits, Standards, Runbooks)
- **Depth:** Maximum 3 levels of nesting maintained

---

## Troubleshooting

### Common Issues

**Issue:** Document appears in multiple sections  
**Resolution:** Valid if document covers multiple security concerns. Cross-listing is intentional.

**Issue:** Priority conflicts with other indexes  
**Resolution:** All security documents are P0 from security perspective, but may be P2 from performance perspective. Context-dependent priority is valid.

**Issue:** Statistics don't match actual counts  
**Resolution:** Run `scripts/audit-index-metadata.py --fix` to auto-update statistics block.

---

**Index Version:** 1.0  
**Schema Version:** 1.0  
**Created By:** AGENT-002 (Indexes Subdirectory Specialist)  
**Last Updated:** 2024-01-15

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

