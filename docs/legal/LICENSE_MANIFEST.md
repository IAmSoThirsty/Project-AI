# Project-AI License Manifest

**Version:** 1.0.0  
**Effective Date:** February 8, 2026  
**Authority:** Canonical index of all Project-AI licenses

---

## PURPOSE

This manifest is the **authoritative mapping** of licenses to components, supremacy order, and enforcement precedence. In case of ambiguity or conflict, courts and arbitrators should consult this manifest.

---

## I. SUPREMACY ORDER

When conflicts arise between licenses, the following order applies:

1. **PAGL (Project-AI Governance License)** - Behavioral constraints supersede all other permissions
2. **Sovereign Use License** - Government-specific restrictions and requirements
3. **Commercial Use License** - Commercial use terms and compensation
4. **Acceptance Ledger License** - Cryptographic proof framework
5. **Apache License 2.0** - Patent-protected novel components
6. **MIT License** - General codebase copyright
7. **Output License** - AI-generated content
8. **Data Ingest License** - User data submission
9. **CLA** - Contributor rights grant
10. **Jurisdictional Annexes** - Region-specific legal requirements

**Final Authority:** In all cases, the Acceptance Ledger is the system of record for what was agreed.

---

## II. COMPONENT → LICENSE MAPPING

### Source Code

| Component | Path Pattern | Primary License | Secondary License(s) |
|-----------|--------------|-----------------|----------------------|
| Core framework | `src/app/core/**` | MIT | PAGL |
| Governance systems | `src/app/governance/**` | Apache 2.0 | PAGL |
| Acceptance ledger | `src/app/governance/acceptance_ledger.py` | Apache 2.0 | PAGL, Ledger License |
| Triumvirate | `api/main.py` (Galahad, Cerberus, CodexDeus) | Apache 2.0 | PAGL |
| AI engines | `src/app/core/intelligence_engine.py` | MIT | PAGL |
| Memory systems | `src/app/core/memory_engine.py` | MIT | PAGL |
| GUI | `src/app/gui/**` | MIT | PAGL |
| CLI | `src/app/cli/**` | MIT | PAGL |
| API | `api/**` | MIT | PAGL |
| Utilities | `utils/**` | MIT | - |
| Tests | `tests/**` | MIT | - |

### Documentation

| Component | Path Pattern | License |
|-----------|--------------|---------|
| Legal documents | `docs/legal/**` | CC-BY-4.0 |
| Technical docs | `docs/**` (excluding legal) | CC-BY-4.0 |
| Code comments | `**/*.py` (docstrings) | Same as containing file |
| README | `README.md` | CC-BY-4.0 |

### Generated Content

| Type | License |
|------|---------|
| AI outputs | Output License |
| User data | Data Ingest License (user owns) |
| Training data | Data Ingest License |
| Logs and telemetry | Data Ingest License |

### Acceptance Records

| Type | License |
|------|---------|
| Ledger entries | Acceptance Ledger License |
| Cryptographic signatures | Acceptance Ledger License |
| Audit logs | Acceptance Ledger License + PAGL |

---

## III. LICENSE FILE LOCATIONS

All license documents are discoverable at these canonical paths:

### Primary Licenses (Root Directory)

- `/LICENSE` - MIT License (general code)
- `/LICENSE-APACHE` - Apache License 2.0 (novel/patent components)

### Governance and Behavioral Licenses

- `/docs/legal/PROJECT_AI_GOVERNANCE_LICENSE.md` - PAGL (constitutional layer)
- `/docs/legal/MASTER_SERVICES_AGREEMENT.md` - User agreement
- `/docs/legal/ACCEPTANCE_LEDGER_LICENSE.md` - Cryptographic proof framework

### Use-Specific Licenses

- `/docs/legal/COMMERCIAL_USE_LICENSE.md` - Commercial use terms
- `/docs/legal/SOVEREIGN_USE_LICENSE.md` - Government use terms
- `/docs/legal/OUTPUT_LICENSE.md` - AI-generated content
- `/docs/legal/DATA_INGEST_LICENSE.md` - User data submission

### Contribution and Compliance

- `/docs/legal/CONTRIBUTOR_LICENSE_AGREEMENT.md` - CLA for contributors
- `/docs/legal/COMPLIANCE_CHECKLIST.md` - Operational compliance
- `/docs/legal/PRICING_FRAMEWORK.md` - Tier structure and pricing

### Jurisdictional Annexes

- `/docs/legal/jurisdictions/EU_GDPR.md` - European Union (GDPR)
- `/docs/legal/jurisdictions/US_CCPA.md` - California (CCPA) [TODO: Create]
- `/docs/legal/jurisdictions/CA_PIPEDA.md` - Canada (PIPEDA) [TODO: Create]
- `/docs/legal/jurisdictions/UK_DPA.md` - United Kingdom (DPA 2018) [TODO: Create]
- `/docs/legal/jurisdictions/AU_PRIVACY.md` - Australia (Privacy Act) [TODO: Create]

### Executive and Business

- `/docs/legal/EXECUTIVE_OVERVIEW.md` - C-suite summary
- `/docs/legal/BOARD_SUMMARY.md` - Board-level summary [TODO: Create]

### This Manifest

- `/docs/legal/LICENSE_MANIFEST.md` - This document

---

## IV. ENFORCEMENT PRECEDENCE

### Runtime Enforcement Order

When Project-AI evaluates an action at runtime:

```python
def enforce_licenses(context):
    # 1. Check acceptance ledger (required for all use)
    if not ledger.has_valid_entry(context.user_id):
        return DENY("No valid acceptance in ledger")
    
    # 2. Check for termination
    if ledger.is_terminated(context.user_id):
        return DENY("User terminated")
    
    # 3. Check PAGL governance constraints
    if pagl.is_prohibited(context.action):
        return DENY("PAGL prohibition")
    
    # 4. Check sovereign restrictions
    if context.is_government and not sovereign_license.authorized(context):
        return DENY("Unauthorized government use")
    
    # 5. Check commercial requirements
    if context.is_commercial and not commercial_license.valid(context):
        return DENY("Commercial license required")
    
    # 6. Check tier entitlements
    if not tier_enforcer.has_access(context.user, context.feature):
        return DENY("Feature not in tier")
    
    # 7. Allow (with audit)
    audit_log.record(context)
    return ALLOW
```

### Conflict Resolution

**If multiple licenses apply to same component:**
1. Most restrictive license governs behavior
2. Most permissive license governs copyright
3. PAGL always applies (non-removable)

**Example:** 
- Code under MIT (permissive) + PAGL (restrictive)
- You can copy/modify (MIT) but cannot remove governance (PAGL)

---

## V. LICENSE COMPATIBILITY MATRIX

### Outbound Compatibility

What licenses can be applied to derivative works:

| Base License | Compatible Downstream Licenses |
|--------------|-------------------------------|
| MIT | MIT, Apache 2.0, GPL, proprietary (any) |
| Apache 2.0 | Apache 2.0, GPLv3+, proprietary (with patent grant) |
| PAGL | PAGL (must be preserved) |
| CC-BY-4.0 | CC-BY-4.0, CC-BY-SA-4.0 |

### Inbound Compatibility

What licenses can be incorporated into Project-AI:

| External License | Compatible? | Notes |
|------------------|-------------|-------|
| MIT | ✅ Yes | Fully compatible |
| Apache 2.0 | ✅ Yes | Preferred for patent protection |
| BSD (2/3-clause) | ✅ Yes | Compatible |
| GPLv2/v3 | ❌ No | Incompatible (copyleft) |
| LGPL | ⚠️ Maybe | Dynamic linking only |
| Proprietary | ❌ No | Violates open source commitment |

---

## VI. SPECIAL CASES

### Forking Project-AI

**If you fork Project-AI, you MUST:**
1. Retain all licenses in original positions
2. Preserve PAGL in full (governance non-removable)
3. Maintain acceptance ledger compatibility
4. Clearly identify as fork (no misrepresentation)
5. Cannot claim "ungoverned" or "unrestricted" version

**You MAY:**
- Relicense MIT-only components under compatible licenses
- Add additional governance (stricter)
- Enhance security and cryptography
- Create derivatives under MIT/Apache terms

**You MAY NOT:**
- Remove or disable PAGL
- Strip out governance systems
- Claim fork is "Project-AI" without distinction

### Commercial Sublicensing

**SaaS providers offering Project-AI:**
- Must have valid Commercial Use License
- Must preserve governance systems
- Must maintain acceptance ledger for their users
- Cannot sublicense governance removal rights
- Must disclose use of Project-AI in their terms

### Government Modifications

**Government-modified versions:**
- Must retain Sovereign Use License requirements
- Cannot classify governance violations
- Audit logs must remain accessible to oversight
- Modifications do not exempt from PAGL
- Enhanced governance acceptable; reduced governance forbidden

### Plugin Ecosystem

**Third-party plugins:**
- Not governed by Project-AI licenses (independent works)
- BUT: Cannot disable or bypass governance when integrated
- Plugin outputs subject to Output License when using Project-AI
- Plugins using Project-AI API must comply with PAGL

---

## VII. INTERPRETATION GUIDELINES

### For Courts

**When interpreting this manifest:**
1. Technical enforcement reflects legal intent
2. Cryptographic ledger is authoritative evidence
3. Governance constraints are contractual terms
4. Open source licenses (MIT/Apache) govern copyright
5. PAGL governs behavior and use

### For Arbitrators

**When resolving disputes:**
1. Consult acceptance ledger for agreed terms
2. Apply supremacy order for conflicts
3. Interpret ambiguities in favor of safety
4. Defer to technical enforcement as expression of intent

### For Users

**When uncertain about licensing:**
1. If unsure which license applies, assume most restrictive
2. If considering prohibited use, assume it's prohibited
3. If governance unclear, consult acceptance ledger
4. If still uncertain, contact: legal@project-ai.dev

---

## VIII. AUDIT AND VERIFICATION

### License Compliance Verification

**Automated checks:**
```bash
# Verify all license headers present
./scripts/verify-license-headers.sh

# Check PAGL compliance
./scripts/check-governance-integrity.sh

# Validate acceptance ledger
python -m src.app.governance.verify_ledger
```

**Manual audits:**
- Quarterly review by legal counsel
- Annual third-party license compliance audit
- Continuous monitoring via CI/CD

### License Violation Response

**If violation detected:**
1. Immediate notification to violator
2. Grace period (7 days for good-faith errors)
3. Termination if not remediated
4. Recording in acceptance ledger
5. Public disclosure (for serious violations)

---

## IX. AMENDMENTS

### How to Amend This Manifest

**Minor changes (corrections, clarifications):**
- 30-day notice
- Published in changelog
- Effective immediately

**Major changes (new licenses, supremacy changes):**
- 90-day notice
- Public comment period (30 days)
- User re-acceptance required for continued use
- Existing agreements honored through term

### Version History

- **v1.0.0** (2026-02-08): Initial release

---

## X. CONTACT

**License Questions:** licensing@project-ai.dev  
**Legal Matters:** legal@project-ai.dev  
**Compliance:** compliance@project-ai.dev  
**Commercial Licensing:** sales@project-ai.dev  
**Government Authorization:** government@project-ai.dev

---

## APPENDIX A: QUICK REFERENCE

### What License Do I Need?

```
┌─ Using Project-AI?
│
├─ Personal use (no revenue) → Solo Tier (FREE)
│   • Licenses: MIT + Apache + PAGL (automatic)
│
├─ Commercial use (<$50K/year) → Solo Commercial ($99 lifetime)
│   • Add: Commercial Use License
│
├─ Company (2-50 employees) → Company Tier ($19/mo or $499 lifetime)
│   • Add: Commercial Use License
│
├─ Organization (50+ employees) → Organization Tier ($49/mo or $2,499 lifetime)
│   • Add: Commercial Use License
│
└─ Government/Military → Government Tier ($99+/mo)
    • Add: Commercial + Sovereign Use License
```

### What Can I Do With Each License?

| Action | MIT | Apache | PAGL | Commercial | Sovereign |
|--------|-----|--------|------|------------|-----------|
| Copy code | ✅ | ✅ | N/A | N/A | N/A |
| Modify code | ✅ | ✅ | ⚠️ Not governance | N/A | N/A |
| Distribute | ✅ | ✅ | ⚠️ With PAGL | N/A | N/A |
| Use commercially | ✅ | ✅ | ⚠️ If licensed | ✅ | N/A |
| Remove governance | ❌ | ❌ | ❌ | ❌ | ❌ |
| Government use | ✅ | ✅ | ⚠️ If authorized | N/A | ✅ |

---

**END OF LICENSE MANIFEST**

*The authoritative index of Project-AI's legal framework.*

**Last Updated:** 2026-02-08  
**Next Review:** 2026-05-08
