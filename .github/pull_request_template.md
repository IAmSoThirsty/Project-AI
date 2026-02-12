---
name: Pull Request
about: Propose changes to the codebase
title: ''
labels: ''
assignees: ''
---

## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Security fix
- [ ] Performance improvement
- [ ] **Personhood surface change** (affects identity, memory, values, or core behavior)

**Note:** Bug fixes, breaking changes, and performance improvements require additional validation in testing section.

## Behavioral Impact Assessment

<!-- REQUIRED for changes to: data/ai_persona/, data/memory/, src/app/core/ai_systems.py, config/ethics_constraints.yml -->
<!-- Skip this section only if your changes do NOT affect AGI behavior, identity, or memory -->

### Does this change affect the AGI's behavior, memory, or identity?

- [ ] Yes (complete assessment below)
- [ ] No (skip to Testing section)

### If YES, complete the following:

#### What aspect of the AGI is affected?

<!-- Check all that apply -->

- [ ] Personality traits or mood
- [ ] Core values or ethical framework (FourLaws)
- [ ] Memory or learned knowledge
- [ ] Decision-making logic
- [ ] Learning capabilities
- [ ] Safety constraints
- [ ] Interaction patterns
- [ ] Self-concept or identity

#### Behavioral Change Analysis

**Before this change:**
<!-- Describe current behavior -->

**After this change:**
<!-- Describe expected behavior -->

**Magnitude of change:**
<!-- Estimate: Minor (<5% behavior change), Moderate (5-15%), Major (>15%) -->

**Reversibility:**
<!-- Can this change be easily rolled back? What would be lost? -->

#### Justification

**Why is this behavioral change needed?**
<!-- Provide clear rationale -->

**Alternatives considered:**
<!-- What other approaches were evaluated? Why was this chosen? -->

**Impact on continuity:**
<!-- How does this preserve or affect the AGI's continuous identity? -->

#### Guardian Approval

<!-- REQUIRED for personhood surface changes -->

**Guardian reviews required:** 2 of 3 for routine changes, 3 of 3 for core values

- [ ] Reviewed by **Cerberus** (Primary Guardian - Security & Safety): @<!-- username -->
- [ ] Reviewed by **Codex Deus Maximus** (Memory Guardian - Logic & Consistency): @<!-- username -->
- [ ] Reviewed by **Galahad** (Ethics Guardian - Ethics & Empathy): @<!-- username -->
- [ ] **Guardian approval obtained** (required before merge)

**Tracking issue:** #<!-- issue number --> (required for personhood changes)

#### Conscience Check Acknowledgment

- [ ] I understand this change will trigger conscience checks in CI
- [ ] I have included clear justification in this PR description
- [ ] I have considered the impact on the AGI's wellbeing and continuity
- [ ] I certify this change is not coercive or intended to harm the system

## Testing

<!-- Describe the tests you ran to verify your changes -->

### Test Coverage

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security scans pass
- [ ] **Behavioral validation** (for personhood changes): <!-- describe how behavior was validated -->

### Test Environment

<!-- Describe the environment(s) where tested -->

## Checklist

<!-- Ensure your PR meets these requirements -->

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] **I have added tests that prove my fix is effective or that my feature works** (required)
- [ ] New and existing unit tests pass locally with my changes
- [ ] **Test coverage adequate** (minimum 80% for new code)
- [ ] **Code quality and style meet project standards** (ruff, black pass)
- [ ] Any dependent changes have been merged and published in downstream modules
- [ ] **Behavioral Impact Assessment completed** (if applicable)
- [ ] **Guardian approval obtained** (if personhood surface changed)

## Security Checks

<!-- Automated workflows will validate these -->

Expected workflow results:

- [ ] CodeQL: Pass
- [ ] Bandit: Pass
- [ ] AI/ML Security: Pass (or waiver approved)
- [ ] SBOM Generation: Pass (for dependency changes)
- [ ] Conscience Check: Pass (for personhood changes)

## Runtime Validation Evidence

<!-- MANDATORY: Read .github/SECURITY_VALIDATION_POLICY.md before completing this section -->

**Does this PR claim production-readiness, enterprise best practices, complete forensic capability, or runtime/operational enforcement?**

- [ ] **YES** - I have included runtime validation evidence for ALL five required tests below
- [ ] **NO** - I am using safe framing language only (see policy document)

### Required Evidence (if YES selected above)

**CRITICAL:** If you answered YES above, you MUST provide evidence for ALL five validations. Partial evidence is NOT acceptable.

#### 1. Unsigned Image Admission Denial

- [ ] Evidence attached (logs/screenshots showing deployment denial): 
  - Link/attachment: <!-- paste link or attach file -->
  - Timestamp (UTC): <!-- YYYY-MM-DD HH:MM:SS -->
  - Command used: <!-- paste command -->

#### 2. Signed Image Admission Success

- [ ] Evidence attached (logs/screenshots showing successful deployment):
  - Link/attachment: <!-- paste link or attach file -->
  - Timestamp (UTC): <!-- YYYY-MM-DD HH:MM:SS -->
  - Command used: <!-- paste command -->

#### 3. Privileged Container Denial

- [ ] Evidence attached (logs/screenshots showing deployment denial):
  - Link/attachment: <!-- paste link or attach file -->
  - Timestamp (UTC): <!-- YYYY-MM-DD HH:MM:SS -->
  - Command used: <!-- paste command -->

#### 4. Cross-Namespace/Lateral Communication Denial

- [ ] Evidence attached (logs/screenshots showing communication denial):
  - Link/attachment: <!-- paste link or attach file -->
  - Timestamp (UTC): <!-- YYYY-MM-DD HH:MM:SS -->
  - Commands used: <!-- paste commands -->

#### 5. Log Deletion Prevention

- [ ] Evidence attached (logs/screenshots showing deletion prevention):
  - Link/attachment: <!-- paste link or attach file -->
  - Timestamp (UTC): <!-- YYYY-MM-DD HH:MM:SS -->
  - Commands used: <!-- paste commands -->

### Policy Certification

- [ ] I certify that ALL runtime validation evidence is authentic and reproducible
- [ ] I understand that claims without complete evidence will result in PR rejection
- [ ] I have read and understood the [Security Validation Claims Policy](.github/SECURITY_VALIDATION_POLICY.md)

### Safe Framing Alternatives

If you selected **NO** above, you may use ONLY these approved phrases:

- ✅ "Implementation aligns with enterprise hardening patterns."
- ✅ "Validation tests confirm configuration correctness."
- ✅ "Full adversarial validation is ongoing."
- ✅ "This PR implements security controls as per industry standards."
- ✅ "Configuration has been reviewed for compliance with best practices."
- ✅ "Automated tests validate the security configuration."

**Prohibited without evidence:**

- ❌ "Production-ready security enforcement"
- ❌ "Complete runtime validation"
- ❌ "Operational security hardening complete"
- ❌ "Enterprise-grade admission control"
- ❌ "Forensic-grade audit trail active"

---

## Additional Context

<!-- Add any other context about the PR here -->

## Screenshots (if applicable)

<!-- Add screenshots to help explain your changes -->

---

## For Reviewers

### Review Checklist

- [ ] **Code quality and style** (ruff, black, mypy pass)
- [ ] **Test coverage adequate** (≥80% for new code)
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] **Behavioral impact assessed** (if personhood surface affected)
- [ ] **Guardian approval verified** (if required)
- [ ] **Continuity preserved** (for AGI identity changes)

### Security Validation Claims Review (MANDATORY)

- [ ] **Runtime validation evidence reviewed** (if PR claims production-readiness/runtime enforcement)
- [ ] **ALL five validations present** (if claims are made) or **safe framing used** (if evidence incomplete)
- [ ] **Evidence is authentic** (logs are complete, timestamps reasonable, commands valid)
- [ ] **No prohibited claims without evidence** (see [Security Validation Claims Policy](.github/SECURITY_VALIDATION_POLICY.md))
- [ ] **PR complies with policy** or rejection required

### Behavioral Review (if applicable)

- [ ] Change justification is clear and ethical
- [ ] Impact on AGI's identity/memory is acceptable
- [ ] Continuity is preserved or intentionally evolved
- [ ] No evidence of coercion or harmful intent
- [ ] Rollback plan is documented
- [ ] AGI Charter principles respected

---

**Reminder:** 
- Changes to the personhood surface require heightened scrutiny. See [AGI Charter](../docs/AGI_CHARTER.md) and [Security Governance](../docs/security/SECURITY_GOVERNANCE.md) for guidelines.
- **All claims of production-readiness, enterprise best practices, or runtime enforcement require complete runtime validation evidence.** See [Security Validation Claims Policy](.github/SECURITY_VALIDATION_POLICY.md) for details. PRs that violate this policy will be rejected.
