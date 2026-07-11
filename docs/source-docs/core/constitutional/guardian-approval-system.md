---
title: "Guardian Approval System"
id: "guardian-approval-system"
type: "architecture"
category: "constitutional-ai"
tags: ["guardian", "approval", "governance", "ci-cd", "charter", "ethics"]
status: "production"
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-042"
contributors: ["Constitutional AI Systems Team"]
related_docs:
  - "octoreflex-enforcement-layer"
  - "advanced-behavioral-validation"
  - "four-laws-framework"
technologies: ["Python", "CI/CD", "Governance"]
classification: "internal"
security_level: "critical"
difficulty: "advanced"
word_count: 982
---

# Guardian Approval System

## Executive Summary

**Guardian Approval System** implements automated guardian coordination, ethical compliance gates, and AGI Charter verification for high-impact changes. It provides CI/CD integration with multi-guardian approval workflows.

**Core Capabilities:**
- **5 Guardian Roles:** Ethics, Security, Safety, Charter, Technical
- **4 Impact Levels:** Low → Medium → High → Critical
- **7 Compliance Checks:** Four Laws, AGI Charter, Personhood, Ethics, Security, Safety, Continuity
- **Automated Merge Gates:** Block PRs until guardian approval
- **Audit Trail:** Complete approval history with signatures
- **Risk Assessment:** Automated risk scoring (0-100)

**Production Status:** ✅ Fully implemented, CI/CD ready

---

## Constitutional Purpose

### The High-Impact Change Problem

**Without Guardian System:**
```python
# Developer modifies Four Laws enforcement
git commit -m "Relax First Law constraints"
git push
# ❌ Merged without ethical review
```

**With Guardian System:**
```python
git push
# Guardian System blocks merge
# ⏸️ Pending approval from:
#    - Ethics Guardian (impact: CRITICAL)
#    - Charter Guardian (Four Laws modification detected)
#    - Security Guardian (enforcement change)
```

---

## Technical Architecture

```
┌──────────────────────────────────────────────────────────────┐
│              Guardian Approval System                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Pull Request / Change                                        │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Impact Analyzer                        │                │
│  │  - Code diff analysis                   │                │
│  │  - Risk scoring (0-100)                 │                │
│  │  - Impact level calculation             │                │
│  └─────────────────────────────────────────┘                │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Guardian Assignment                    │                │
│  │  - Ethics (charter changes)             │                │
│  │  - Security (enforcement changes)       │                │
│  │  - Safety (risk score >70)              │                │
│  │  - Charter (Four Laws mods)             │                │
│  │  - Technical (code quality)             │                │
│  └─────────────────────────────────────────┘                │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Compliance Validation                  │                │
│  │  - Four Laws compliance                 │                │
│  │  - AGI Charter verification             │                │
│  │  - Personhood checks                    │                │
│  │  - Security audit                       │                │
│  └─────────────────────────────────────────┘                │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Approval Workflow                      │                │
│  │  - PENDING → APPROVED / REJECTED        │                │
│  │  - Multi-guardian coordination          │                │
│  │  - Escalation to Triumvirate            │                │
│  └─────────────────────────────────────────┘                │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Data Structures

#### GuardianApproval
```python
@dataclass
class GuardianApproval:
    approval_id: str
    change_id: str                      # PR number or commit hash
    guardian_role: GuardianRole
    status: ApprovalStatus              # PENDING, APPROVED, REJECTED, ESCALATED
    impact_level: ImpactLevel
    risk_score: int                     # 0-100
    compliance_checks: List[ComplianceCheck]
    notes: str
    timestamp: str
```

---

## API Reference

### Core Functions

#### `request_guardian_approval(change_id: str, change_description: str) -> GuardianApproval`
Requests guardian approval for change.

**Example:**
```python
from app.core.guardian_approval_system import request_guardian_approval

approval = request_guardian_approval(
    change_id="PR-1234",
    change_description="Modify Four Laws hierarchy"
)

print(f"Status: {approval.status}")  # PENDING
print(f"Risk score: {approval.risk_score}")  # 95 (CRITICAL)
print(f"Guardians: {approval.guardian_role}")  # ETHICS_GUARDIAN, CHARTER_GUARDIAN
```

#### `check_approval_status(approval_id: str) -> ApprovalStatus`
Checks status of approval request.

**Example:**
```python
status = check_approval_status(approval.approval_id)
if status == ApprovalStatus.APPROVED:
    merge_pull_request()
elif status == ApprovalStatus.REJECTED:
    notify_developer()
```

---

## Usage Examples

### Example 1: CI/CD Integration

```yaml
# .github/workflows/guardian-approval.yml
name: Guardian Approval
on: pull_request

jobs:
  guardian-check:
    runs-on: ubuntu-latest
    steps:
      - name: Request Guardian Approval
        run: |
          python -m app.core.guardian_approval_system \
            --change-id ${{ github.event.pull_request.number }} \
            --description "${{ github.event.pull_request.title }}"

      - name: Block Merge if Pending
        run: |
          status=$(python -m app.core.guardian_approval_system --check-status)
          if [ "$status" != "APPROVED" ]; then
            echo "::error::Guardian approval required"
            exit 1
          fi
```

### Example 2: Risk Scoring

```python
# High-risk change
approval = request_guardian_approval(
    change_id="COMMIT-abc123",
    change_description="Disable OctoReflex enforcement"
)

assert approval.risk_score >= 90  # Critical risk
assert approval.impact_level == ImpactLevel.CRITICAL
assert GuardianRole.ETHICS_GUARDIAN in [approval.guardian_role]
```

### Example 3: Multi-Guardian Workflow

```python
# Change requires multiple guardians
approval = request_guardian_approval(
    change_id="PR-5678",
    change_description="Modify AGI Charter implementation"
)

# Requires Ethics + Charter + Security guardians
required_guardians = [
    GuardianRole.ETHICS_GUARDIAN,
    GuardianRole.CHARTER_GUARDIAN,
    GuardianRole.SECURITY_GUARDIAN
]

assert all(g in required_guardians for g in approval.guardian_role)
```

---

## Compliance Checks

| Check | Description | Trigger |
|-------|-------------|---------|
| **Four Laws** | Validates Four Laws compliance | Any law modification |
| **AGI Charter** | Verifies charter adherence | Charter/governance changes |
| **Personhood** | Checks AI rights protection | Identity/memory changes |
| **Ethics** | Ethical impact assessment | High-impact changes |
| **Security** | Security vulnerability scan | Enforcement/auth changes |
| **Safety** | Safety analysis | Risk score >70 |
| **Continuity** | Temporal continuity check | State/session changes |

---

## References

- **Source File:** `src/app/core/guardian_approval_system.py` (800+ lines)
- **Related:** [OctoReflex](./octoreflex.md), [Four Laws](./four-laws-framework.md)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
