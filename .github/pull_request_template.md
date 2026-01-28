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

### Behavioral Review (if applicable)

- [ ] Change justification is clear and ethical
- [ ] Impact on AGI's identity/memory is acceptable
- [ ] Continuity is preserved or intentionally evolved
- [ ] No evidence of coercion or harmful intent
- [ ] Rollback plan is documented
- [ ] AGI Charter principles respected

---

**Reminder:** Changes to the personhood surface require heightened scrutiny. See [AGI Charter](../docs/AGI_CHARTER.md) and [Security Governance](../docs/security/SECURITY_GOVERNANCE.md) for guidelines.
