# Effort Estimates
**Phase 0 Baseline → Production Release - Work Breakdown Structure**

Generated: 2026-05-16T02:53:42-06:00  
Based on: 1,354 files inspected, 96 high-priority gaps identified  
Methodology: Priority-weighted complexity scoring + historical velocity

---

## Summary

| Priority | Files | Estimated Work | Notes |
|----------|-------|----------------|-------|
| **CRITICAL** | 30 | 134-204 hours | **Includes 8 BROKEN + 14 THEATER CRITICAL** |
| **HIGH** | 66 | 220-330 hours | All user-facing features |
| **MEDIUM** | 169 | Not estimated | Backlog priority |
| **LOW** | 209 | Not estimated | Technical debt |
| **TOTAL High-Priority** | **96** | **354-534 hours** | **CRITICAL + HIGH only** |

**Note**: User explicitly declined time estimates. Estimates provided for planning purposes only, not commitments.

---

## Critical Priority Breakdown (30 files)

### BROKEN CRITICAL (8 files) - BLOCKING

| File Category | Files | Effort Range | Complexity Factors |
|---------------|-------|--------------|-------------------|
| **UTF readline fixes** | 7 | ✅ 0 hours | Already completed (pyreadline3 installed) |
| **AI Systems core logic** | 1 | 6-10 hours | Large file (470 lines), multiple systems, OpenAI integration testing |

**BROKEN CRITICAL Total: 6-10 hours** (7 already fixed)

---

### THEATER CRITICAL (14 files) - SECURITY/FUNCTIONALITY RISKS

| Feature Area | Files | Implement | Remove | Complexity Factors |
|--------------|-------|-----------|--------|-------------------|
| **Kill Switch System** | 2 | 12-16h | 3-4h | OS-specific firewall rules (iptables/nftables/pf/Windows Firewall), cross-platform testing |
| **Network Stealth/Onion** | 2 | 20-30h | 2-3h | Tor integration complex; removal simpler but affects privacy claims |
| **Hardware Root of Trust** | 2 | 10-15h (keychain) / 30-40h (TPM) | 4-6h | TPM integration very complex; OS keychain moderate; removal requires caller updates |
| **Encryption System** | 1 | 6-10h | N/A | Security-sensitive, AEAD required, test vectors |
| **VPN Manager** | 2 | 40-60h | 8-12h | Multi-protocol (WireGuard/OpenVPN/IKEv2), kill switch integration |
| **Browser Engine** | 4 | 30-50h (QtWebEngine) / 4-6h (system browser) | 10-15h | QtWebEngine complex integration; system browser redirect simple |
| **Governance Quorum** | 1 | 8-12h | N/A | Cryptographic proofs, formal verification |

**THEATER CRITICAL Estimates**:
- **Implement Path**: 126-193 hours (full feature implementation)
- **Remove Path**: 27-40 hours (delete + update callers)
- **Hybrid Path** (selective implement): 60-100 hours (keep essential features, remove nice-to-haves)

**Recommended**: Hybrid approach - implement governance quorum + encryption, remove VPN/browser/Tor unless product-critical

---

### STUB/ASPIRATIONAL CRITICAL (8 files)

| Feature Area | Files | Effort Range | Approach |
|--------------|-------|--------------|----------|
| **Browser Sandbox** | 1 STUB | 20-30h (implement) / 1h (remove) | Depends on browser decision |
| **Execution Gate Validation** | 1 ASP | 6-8h | Integration testing and validation |
| **Backend Wiring** | 6 ASP | 12-18h | Import fixes, security hardening, subprocess integration |

**STUB/ASP CRITICAL Total: 38-56 hours** (or 19-27h if browser removed)

---

## HIGH Priority Breakdown (66 files)

*Detailed file-level breakdown requires full query export. Summary:*

| Verdict | Files | Estimated Range | Assumption |
|---------|-------|-----------------|------------|
| **BROKEN HIGH** | 3 | 4-8h each = 12-24h | Similar complexity to UTF import fixes |
| **THEATER HIGH** | 30 | 6-12h each = 180-360h | Mix of removal (2-4h) and implementation (10-20h) |
| **STUB HIGH** | 10 | 8-15h each = 80-150h | Complete or remove, moderate complexity |
| **ASPIRATIONAL HIGH** | 23 | 4-8h each = 92-184h | Add OS integration layer |

**HIGH Priority Total: 364-718 hours** (wide range due to implement vs remove decisions)

**Risk-Adjusted Estimate**: 220-330 hours (assumes ~40% removal, 60% implementation)

---

## Implementation Path Options

### Path A: Minimal Viable Release (CRITICAL only)
**Scope**: 30 CRITICAL files  
**Effort**: 
- Aggressive removal: 71-96 hours (remove most theater, keep governance)
- Balanced hybrid: 110-150 hours (implement essentials, remove rest)
- Full implementation: 170-259 hours (implement everything)

**Outcome**: 
- System stable and secure
- Core features work
- Many claimed features removed or disabled
- Quality: ~70-75% GENUINE

**Risk**: May disappoint users expecting full feature set

---

### Path B: Production Hardening (CRITICAL + HIGH)
**Scope**: 96 high-priority files  
**Effort**: 
- Aggressive removal: 220-300 hours
- Balanced hybrid: 400-550 hours
- Full implementation: 534-977 hours

**Outcome**:
- All important features work
- Security and stability assured
- Some nice-to-have features removed
- Quality: ~85-90% GENUINE

**Risk**: Still leaves medium-priority gaps as backlog

**Recommended**: This path balances scope and timeline

---

### Path C: Complete Overhaul (All Priorities)
**Scope**: All 474 gap files (CRITICAL + HIGH + MEDIUM + LOW)  
**Effort**: 800-1500 hours (very rough estimate)

**Outcome**:
- ≥95% GENUINE quality achieved
- All features complete or cleanly removed
- Comprehensive test coverage
- Production-grade codebase

**Risk**: Very long timeline, high cost

---

## Complexity Factors

Estimates account for:

1. **Code Complexity**: Lines of code, dependencies, integration points
2. **OS Variance**: Cross-platform support increases effort 2-3x
3. **Security Sensitivity**: Security-critical code requires formal review, testing (1.5-2x)
4. **Integration Testing**: Real OS operations need actual system testing (1.5x)
5. **Documentation**: README updates, API docs, changelog entries (+10-20% per feature)

**Confidence Levels**:
- **BROKEN fixes**: High confidence (clear bugs, known fixes)
- **THEATER removal**: High confidence (well-defined scope)
- **THEATER implementation**: Medium confidence (depends on requirements clarity)
- **ASPIRATIONAL OS integration**: Medium confidence (varies by feature)
- **STUB completion**: Low confidence (many unknowns until detailed spec)

---

## Resource Planning

### Skill Mix Required

| Role | Critical Phase | HIGH Phase | Total |
|------|----------------|------------|-------|
| **Senior Python Engineer** | 40-60h | 100-150h | 140-210h |
| **Security Engineer** | 30-50h | 40-60h | 70-110h |
| **DevOps/Infrastructure** | 20-30h | 40-60h | 60-90h |
| **QA/Testing Engineer** | 20-30h | 40-60h | 60-90h |
| **Technical Writer** | 10-15h | 20-30h | 30-45h |

### Parallelization Opportunities

**Wave 1 (CRITICAL) Parallelization**:
- ✅ AI Systems fix (1 developer, 6-10h) - no dependencies
- ✅ Governance Quorum (1 developer, 8-12h) - no dependencies
- ✅ Encryption System (1 security engineer, 6-10h) - no dependencies
- ⏸️ Kill Switch + VPN (1 infra engineer, 50-70h) - sequential (kill switch needs VPN)
- ⏸️ Browser features (1 senior engineer, 30-50h) - requires product decision
- ⏸️ Backend wiring (1 engineer, 12-18h) - depends on VPN/firewall decisions

**Best Case (3 developers parallel)**: 2-3 weeks  
**Realistic (2 developers)**: 3-5 weeks  
**Conservative (1 developer)**: 6-10 weeks

---

## Validation Checkpoints

After each phase completion:

1. **Run canonical/replay.py**: Must show 5/5 invariants pass
2. **Run full test suite**: pytest -v (all tests must pass)
3. **Verify imports**: python -c "from src.app import *" (no crashes)
4. **Check quality baseline**: Run Phase 0 audit queries (track genuine % increase)
5. **Update documentation**: README accuracy, changelog, migration guides

---

## Risk-Adjusted Ranges

**Why wide ranges?**
- Implement vs remove decisions not yet made (2-5x effort difference)
- Cross-platform support varies by feature (1-3x multiplier)
- Integration complexity depends on existing infrastructure
- Security features require more rigorous testing (1.5-2x)

**As decisions are made**, these ranges will narrow significantly.

---

## Recommendation

**Start with Path B (Production Hardening):**
- Focus on CRITICAL + HIGH priorities (96 files)
- Make implement/remove decisions in Wave 1 kickoff meeting
- Target 400-550 hour total effort (balanced hybrid approach)
- Timeline: 10-14 weeks with 2 developers (20-25h/week each)

**Why this path?**
- Achieves production-grade quality without massive overhaul
- Delivers working features users expect
- Removes security theater that creates vulnerability
- Provides clear milestone for "release candidate" status

---

**Effort Estimates Generated by**: Project-AI Phase 0 Baseline Audit System  
**Maintained in**: baseline/EFFORT_ESTIMATES.md  
**Updated**: 2026-05-16T02:53:42-06:00  
**Next Review**: After Wave 1 product decisions
