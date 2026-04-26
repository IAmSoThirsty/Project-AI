---
type: automation-guide
tags: [scripts, governance, implementation, automation, ci-cd]
created: 2026-01-21
last_verified: 2026-04-20
status: current
related_systems: [governance, router, audit-framework, ci-cd]
stakeholders: [devops, developers, security-team]
script_language: [python, powershell, bash]
automation_purpose: [deployment, validation, governance]
requires_admin: true
review_cycle: quarterly
---

# Script Governance Implementation Guide

**Status**: Phase 2 - Partial Implementation Complete  
**Date**: 2026-01-21  
**Next Review**: 2026-04-21

---

## Quick Reference

- **Classification Document**: `SCRIPT_CLASSIFICATION.md`
- **Implementation Status**: 5 scripts converted, 53 remaining
- **Priority**: High-risk security scripts first

---

## Implementation Progress

### ✅ Completed (5 scripts)

#### GOVERNED Scripts (3)
1. `run_asl3_security.py` - ASL-3 security operations
2. `run_cbrn_classifier.py` - CBRN classification
3. `populate_cybersecurity_knowledge.py` - Knowledge base management

#### ADMIN-BYPASS Scripts (2)
1. `fix_logging_performance.py` - Logging refactoring tool
2. `fix_assert_statements.py` - Assert statement fixes

#### EXAMPLE Scripts (2)
1. `demo_security_features.py` - Security demo
2. `demo_cybersecurity_knowledge.py` - Knowledge base demo

### 🔄 In Progress (0 scripts)

None currently

### ⏳ Pending Implementation (53 scripts)

#### High Priority GOVERNED (14 scripts)
- [ ] `run_asl_assessment.py`
- [ ] `run_security_worker.py`
- [ ] `run_comprehensive_expansion.py`
- [ ] `run_novel_scenarios.py`
- [ ] `run_red_hat_expert_simulations.py`
- [ ] `run_red_team_stress_tests.py`
- [ ] `run_robustness_benchmarks.py`
- [ ] `sarif_exporter.py`
- [ ] `launch_mcp_server.py`
- [ ] `setup_temporal.py`
- [ ] `hydra50_deploy.py`
- [ ] `update_osint_bible.py`
- [ ] `benchmark.py`
- [ ] `healthcheck.py`

#### Medium Priority GOVERNED (2 scripts)
- [ ] `validate_release.py`

#### ADMIN-BYPASS (29 scripts)
- [ ] `fix_logging_performance_surgical.py`
- [ ] `fix_logging_phase2.py`
- [ ] `fix_syntax_errors.py`
- [ ] `generate_cli_docs.py`
- [ ] `generate_cerberus_languages.py`
- [ ] `backup_audit.py` (header added, needs warning prompt)
- [ ] `register_legion_moltbook.py`
- [ ] `register_simple.py`
- [ ] `deepseek_v32_cli.py`
- [ ] `inspection_cli.py`
- [ ] `quickstart.py`
- [ ] Build scripts (3)
- [ ] Installation scripts (11)
- [ ] Testing scripts (1)

#### EXAMPLE Scripts (1 remaining)
- [ ] Scripts in `demo/` subdirectory

---

## Implementation Patterns

### GOVERNED Script Template

```python
#!/usr/bin/env python3
"""
[Script Name]

GOVERNANCE: GOVERNED
Classification: [Production utility/Security operations/etc.]
Risk: [Low/Medium/High] ([description])

[Description]

Usage:
    [Usage examples]
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.runtime.router import route_request
from app.core.[original_module] import [original_function]


def main_governed():
    """Main function with governance routing."""
    # Extract parameters from command line
    operation = sys.argv[1] if len(sys.argv) > 1 else "default"
    
    # Route through governance
    result = route_request("cli", {
        "action": "category.operation_name",
        "params": {
            "operation": operation,
            "args": sys.argv[1:]  # Or parsed args
        },
        "metadata": {
            "script": __file__,
            "user": "operator",
            "risk_level": "high"  # or "medium", "low"
        }
    })
    
    # Check approval
    if not result.get("approved", False):
        print(f"❌ Operation blocked: {result.get('reason', 'Unknown')}")
        return 1
    
    # Proceed with original operation
    return [original_function]()


if __name__ == "__main__":
    sys.exit(main_governed())
```

### ADMIN-BYPASS Script Template

```python
#!/usr/bin/env python3
"""
[Script Name]

⚠️ ADMIN-ONLY SCRIPT ⚠️
GOVERNANCE: ADMIN-BYPASS
Classification: [Dev tool/Maintenance/Admin utility]
Risk: [Level] ([description of risks])
Justification: [Why bypass is acceptable]

WARNING: This script bypasses governance controls.
         - Restricted to system administrators
         - Manual oversight required
         - Not for automated/end-user execution
         - Review security implications before use

[Description]

Usage:
    [Usage examples]
"""

import sys

def display_admin_warning():
    """Display admin warning and get confirmation."""
    print("⚠️  ADMIN-ONLY SCRIPT - Governance bypass active")
    print("    This script modifies [what it modifies]")
    print("    Risk level: [RISK]")
    print("    Review security implications before proceeding")
    
    response = input("    Continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Aborted")
        sys.exit(1)

def main():
    """Main function."""
    display_admin_warning()
    
    # Original script logic
    ...

if __name__ == "__main__":
    main()
```

### EXAMPLE Script Template

```python
#!/usr/bin/env python3
"""
[Script Name]

📚 EXAMPLE/DEMONSTRATION CODE
GOVERNANCE: EXAMPLE
Classification: Educational/demonstration
Production Use: NOT RECOMMENDED

[Description of what it demonstrates]

This script is for demonstration purposes only.
Do not use in production without proper review and adaptation.

Usage:
    [Usage examples]
"""

def main():
    """Main demo function."""
    print("📚 DEMONSTRATION MODE")
    print("    This is example code for educational purposes")
    print()
    
    # Demo code
    ...

if __name__ == "__main__":
    main()
```

---

## Router Integration Points

### Action Categories

Map script operations to governance action categories:

| Script Type | Action Category | Example |
|------------|----------------|---------|
| Security operations | `security.*` | `security.asl3_operation` |
| Content management | `content.*` | `content.populate_knowledge_base` |
| Deployment | `deployment.*` | `deployment.temporal_setup` |
| Monitoring | `monitoring.*` | `monitoring.health_check` |
| Testing | `testing.*` | `testing.red_team_stress` |

### Metadata Fields

Standard metadata for all governed scripts:

```python
"metadata": {
    "script": __file__,           # Script path (required)
    "user": "operator",            # User role (required)
    "risk_level": "high",          # Risk assessment (required)
    "safety_critical": True,       # Safety-critical flag (optional)
    "requires_audit": True,        # Force audit logging (optional)
    "emergency_override": False    # Emergency flag (optional)
}
```

---

## Testing Strategy

### Unit Tests

Create test file: `tests/governance/test_script_governance.py`

```python
import pytest
from app.core.runtime.router import route_request

def test_governed_script_routing():
    """Test that governed scripts route correctly."""
    result = route_request("cli", {
        "action": "security.asl3_operation",
        "params": {"operation": "status"},
        "metadata": {"script": "test", "user": "test"}
    })
    assert "approved" in result

def test_admin_bypass_warning():
    """Test that admin-bypass scripts display warnings."""
    # Mock test for warning display
    pass

def test_example_script_marker():
    """Test that example scripts have proper markers."""
    # Verify markers exist
    pass
```

### Integration Tests

1. **Governance Routing**: Verify all GOVERNED scripts successfully route
2. **Admin Warnings**: Verify ADMIN-BYPASS scripts display warnings
3. **Audit Logging**: Verify governed scripts create audit entries

### Manual Testing Checklist

- [ ] Run each governed script with valid/invalid permissions
- [ ] Verify admin warnings display and block on "no"
- [ ] Check example scripts display educational notice
- [ ] Verify audit logs contain script executions
- [ ] Test emergency override scenarios

---

## Rollout Plan

### Phase 1: High-Risk Security Scripts ✅ (Partial)
**Timeline**: Week 1  
**Scripts**: 3 completed, 14 remaining  
**Status**: In Progress

- [x] `run_asl3_security.py`
- [x] `run_cbrn_classifier.py`
- [ ] `run_asl_assessment.py`
- [ ] `run_security_worker.py`
- [ ] Other security testing scripts

**Validation**: Security team review + manual testing

### Phase 2: Content & Deployment Scripts
**Timeline**: Week 2  
**Scripts**: 1 completed, 4 remaining  
**Status**: Pending

- [x] `populate_cybersecurity_knowledge.py`
- [ ] `update_osint_bible.py`
- [ ] `launch_mcp_server.py`
- [ ] `setup_temporal.py`
- [ ] `hydra50_deploy.py`

**Validation**: Deploy team review + integration tests

### Phase 3: Monitoring & Utilities
**Timeline**: Week 3  
**Scripts**: 3 scripts  
**Status**: Pending

- [ ] `benchmark.py`
- [ ] `healthcheck.py`
- [ ] `validate_release.py`

**Validation**: Ops team review + CI/CD integration

### Phase 4: Admin-Bypass Scripts
**Timeline**: Week 4  
**Scripts**: 2 completed, 27 remaining  
**Status**: Pending

- [x] `fix_logging_performance.py`
- [x] `fix_assert_statements.py`
- [ ] Other maintenance tools

**Validation**: Developer review + warning display tests

### Phase 5: Example Scripts
**Timeline**: Week 5  
**Scripts**: 2 completed, ~6 remaining  
**Status**: Pending

- [x] `demo_security_features.py`
- [x] `demo_cybersecurity_knowledge.py`
- [ ] Scripts in `demo/` directory

**Validation**: Documentation team review

---

## CI/CD Integration

### GitHub Actions Workflow

Add to `.github/workflows/governance-check.yml`:

```yaml
name: Script Governance Check

on: [push, pull_request]

jobs:
  check-scripts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check script classifications
        run: |
          python scripts/verify/verify_script_governance.py
          
      - name: Verify governed scripts route
        run: |
          pytest tests/governance/test_script_governance.py -v
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for new scripts without classification
python scripts/verify/verify_script_governance.py --check-new
```

---

## Monitoring & Compliance

### Audit Log Queries

Monitor governed script execution:

```python
# Query audit log for script executions
SELECT * FROM audit_log 
WHERE action LIKE 'script.%' 
ORDER BY timestamp DESC 
LIMIT 100;

# Count script executions by category
SELECT action, COUNT(*) as count 
FROM audit_log 
WHERE action LIKE 'script.%' 
GROUP BY action 
ORDER BY count DESC;

# Find blocked script attempts
SELECT * FROM audit_log 
WHERE action LIKE 'script.%' 
AND approved = false;
```

### Compliance Reporting

Generate quarterly report:

```bash
python scripts/verify/generate_script_governance_report.py \
  --quarter Q1-2026 \
  --output reports/script_governance_Q1_2026.md
```

---

## Common Issues & Solutions

### Issue 1: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app.core.runtime.router'`

**Solution**: Ensure router exists at `src/app/core/runtime/router.py`

### Issue 2: Circular Imports

**Problem**: Governance routing causes circular import

**Solution**: Import `route_request` inside `main_governed()` function

### Issue 3: Backwards Compatibility

**Problem**: Scripts called from other scripts break

**Solution**: Keep both `main()` and `main_governed()`, or use environment variable to toggle

### Issue 4: Emergency Override

**Problem**: Need to bypass governance in emergency

**Solution**: Set `"emergency_override": True` in metadata + document in audit log

---

## Governance Bypass Approval Process

For adding new ADMIN-BYPASS scripts:

1. **Document Justification**: Why bypass is necessary
2. **Risk Assessment**: Identify potential impacts
3. **Review Required**: Security team + 1 senior developer
4. **Update Classification**: Add to `SCRIPT_CLASSIFICATION.md`
5. **Add Header**: Include bypass warning and usage restrictions
6. **Test Warning Display**: Verify warning prompts correctly

Template for justification:

```markdown
## BYPASS REQUEST: [script_name.py]

**Requestor**: [Name]  
**Date**: [Date]  
**Purpose**: [What script does]

**Justification**:
- [ ] Developer-only tool (not for end users)
- [ ] One-time migration script
- [ ] Admin maintenance utility
- [ ] No production impact
- [ ] Other: [Explain]

**Risk Assessment**:
- Modifies: [What it modifies]
- Risk Level: [Low/Medium/High]
- Mitigations: [How risks are managed]

**Approvals**:
- [ ] Security Team: [Name, Date]
- [ ] Senior Developer: [Name, Date]
```

---

## Next Steps

### Immediate (This Week)
1. Complete high-priority security scripts (14 remaining)
2. Add governance router tests
3. Update CI/CD to check classifications

### Short-term (Next Month)
1. Complete all GOVERNED script conversions
2. Add admin warnings to all ADMIN-BYPASS scripts
3. Mark all EXAMPLE scripts
4. Create quarterly compliance report

### Long-term (Next Quarter)
1. Automate classification verification
2. Add telemetry for script usage
3. Create dashboard for governance compliance
4. Review and update risk assessments

---

## Resources

- **Classification Doc**: `scripts/SCRIPT_CLASSIFICATION.md`
- **Router Implementation**: `src/app/core/runtime/router.py`
- **Testing Guide**: `tests/governance/README.md`
- **Compliance Dashboard**: `http://localhost:8001/governance/scripts`

---

## Contact

**Governance Team**: governance@project-ai.local  
**Security Team**: security@project-ai.local  
**Escalations**: CTO office  

---

*Last Updated: 2026-01-21*  
*Next Review: 2026-04-21*
