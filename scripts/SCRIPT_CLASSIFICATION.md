---
type: script-documentation
tags: [scripts, governance, classification, security, automation]
created: 2026-01-21
last_verified: 2026-04-20
status: current
related_systems: [governance, security, audit-framework]
stakeholders: [security-team, devops, developers]
script_language: [python, powershell, bash]
automation_purpose: [classification, governance, security]
requires_admin: false
review_cycle: quarterly
---

# SCRIPT GOVERNANCE CLASSIFICATION

**Date**: 2026-01-21  
**Classification Authority**: Multi-Path Governance Architecture  
**Review Cycle**: Quarterly or upon script modification

---

## OVERVIEW

This document classifies all scripts in the `scripts/` directory according to governance requirements. Scripts are categorized as:

- **GOVERNED**: Production scripts that MUST route through governance framework
- **ADMIN-BYPASS**: Administrative/development tools with documented bypass justification
- **EXAMPLE**: Demonstration code, not for production use

---

## GOVERNED SCRIPTS (Route through governance)

### Production Utilities

#### `benchmark.py`
- **Purpose**: API performance benchmarking
- **User**: Operations, developers, automated monitoring
- **Risk**: Low (read-only API testing)
- **AI Usage**: No direct AI calls
- **Classification**: **GOVERNED** (production monitoring tool)
- **Justification**: Used in production for performance verification; should be audited

#### `healthcheck.py`
- **Purpose**: Service health verification
- **User**: Operations, CI/CD, monitoring systems
- **Risk**: Low (read-only health checks)
- **AI Usage**: No
- **Classification**: **GOVERNED** (production monitoring)
- **Justification**: Critical for production health monitoring; audit trail required

#### `validate_release.py`
- **Purpose**: Release package validation
- **User**: Release engineers, CI/CD
- **Risk**: Medium (validates production artifacts)
- **AI Usage**: No
- **Classification**: **GOVERNED** (release process)
- **Justification**: Part of production release pipeline; requires governance oversight

### Security & Compliance Tools

#### `run_asl3_security.py`
- **Purpose**: ASL-3 security operations (encryption, monitoring, compliance)
- **User**: Security administrators
- **Risk**: High (manages encryption, security controls)
- **AI Usage**: No (security framework)
- **Classification**: **GOVERNED** (security operations)
- **Justification**: Critical security operations must be audited and governed

#### `run_asl_assessment.py`
- **Purpose**: AI Safety Level evaluation
- **User**: Security team, compliance
- **Risk**: Medium (generates safety assessments)
- **AI Usage**: Analyzes AI safety metrics
- **Classification**: **GOVERNED** (compliance reporting)
- **Justification**: Safety assessments impact production deployment decisions

#### `run_cbrn_classifier.py`
- **Purpose**: CBRN & high-risk capability classification
- **User**: Security team, content moderation
- **Risk**: High (identifies dangerous content)
- **AI Usage**: ML classifier for risk detection
- **Classification**: **GOVERNED** (safety-critical)
- **Justification**: Safety-critical classification system for production

#### `sarif_exporter.py`
- **Purpose**: Security findings export to SARIF format
- **User**: Security team, CI/CD
- **Risk**: Medium (processes security findings)
- **AI Usage**: No (data transformation)
- **Classification**: **GOVERNED** (security reporting)
- **Justification**: Security reporting tool for production systems

### Red Team & Security Testing

#### `run_comprehensive_expansion.py`
- **Purpose**: Comprehensive security test expansion
- **User**: Security team
- **Risk**: High (security testing)
- **AI Usage**: May use AI for test generation
- **Classification**: **GOVERNED** (security testing)
- **Justification**: Security tests should be audited for completeness

#### `run_novel_scenarios.py`
- **Purpose**: Novel attack scenario generation
- **User**: Security researchers
- **Risk**: High (generates attack scenarios)
- **AI Usage**: Likely (scenario generation)
- **Classification**: **GOVERNED** (security research)
- **Justification**: AI-generated attack scenarios need governance oversight

#### `run_red_hat_expert_simulations.py`
- **Purpose**: Advanced red team simulations
- **User**: Security team
- **Risk**: High (simulates attacks)
- **AI Usage**: Likely (attack simulation)
- **Classification**: **GOVERNED** (security testing)
- **Justification**: Attack simulations must be tracked and governed

#### `run_red_team_stress_tests.py`
- **Purpose**: Red team stress testing
- **User**: Security team
- **Risk**: High (stress testing)
- **AI Usage**: Likely (test generation)
- **Classification**: **GOVERNED** (security testing)
- **Justification**: Production stress tests require governance

#### `run_robustness_benchmarks.py`
- **Purpose**: Security robustness benchmarking
- **User**: Security team, QA
- **Risk**: Medium (benchmarking)
- **AI Usage**: Analyzes robustness metrics
- **Classification**: **GOVERNED** (security benchmarking)
- **Justification**: Robustness metrics inform production decisions

#### `run_security_worker.py`
- **Purpose**: Background security worker operations
- **User**: Automated systems
- **Risk**: High (automated security operations)
- **AI Usage**: Possible
- **Classification**: **GOVERNED** (automated security)
- **Justification**: Automated security operations must be fully governed

### Knowledge & Content Management

#### `populate_cybersecurity_knowledge.py`
- **Purpose**: Populate knowledge base with cybersecurity content
- **User**: Content administrators
- **Risk**: Medium (modifies knowledge base)
- **AI Usage**: Integrates with memory systems
- **Classification**: **GOVERNED** (content management)
- **Justification**: Knowledge base modifications should be audited

#### `update_osint_bible.py`
- **Purpose**: Update OSINT knowledge base
- **User**: Content administrators
- **Risk**: Medium (knowledge base updates)
- **AI Usage**: Possible (content processing)
- **Classification**: **GOVERNED** (content management)
- **Justification**: Knowledge updates impact AI behavior

### Integration & Deployment

#### `launch_mcp_server.py`
- **Purpose**: Launch MCP (Model Control Protocol) server
- **User**: Operators, deployment systems
- **Risk**: High (service deployment)
- **AI Usage**: Manages AI model servers
- **Classification**: **GOVERNED** (service deployment)
- **Justification**: Model server deployment is production-critical

#### `setup_temporal.py`
- **Purpose**: Setup Temporal workflow engine
- **User**: DevOps, deployment
- **Risk**: High (infrastructure setup)
- **AI Usage**: No (infrastructure)
- **Classification**: **GOVERNED** (infrastructure deployment)
- **Justification**: Production infrastructure changes require governance

#### `hydra50_deploy.py`
- **Purpose**: Hydra 5.0 security deployment
- **User**: Security team, deployment
- **Risk**: High (security system deployment)
- **AI Usage**: Security framework deployment
- **Classification**: **GOVERNED** (security deployment)
- **Justification**: Security system deployment is critical

---

## ADMIN-BYPASS SCRIPTS (Admin-only, marked with justification)

### Development & Maintenance Tools

#### `fix_assert_statements.py`
- **Purpose**: Convert assert to proper error handling
- **User**: Developers (one-time code migration)
- **Risk**: Medium (code modification)
- **Classification**: **ADMIN-BYPASS** (dev maintenance)
- **Justification**: One-time code quality improvement; admin-supervised
- **Usage**: Restricted to developers during code refactoring

#### `fix_logging_performance.py`
- **Purpose**: Convert f-string logging to lazy % format
- **User**: Developers (code quality improvement)
- **Risk**: Medium (code modification)
- **Classification**: **ADMIN-BYPASS** (dev maintenance)
- **Justification**: Performance optimization tool; developer-supervised
- **Usage**: Run by developers for code quality improvements

#### `fix_logging_performance_surgical.py`
- **Purpose**: Surgical logging performance fixes
- **User**: Developers
- **Risk**: Medium (code modification)
- **Classification**: **ADMIN-BYPASS** (dev maintenance)
- **Justification**: Precise code transformation; requires developer oversight
- **Usage**: Developer-only code refactoring tool

#### `fix_logging_phase2.py`
- **Purpose**: Phase 2 logging fixes (error handlers, multi-line)
- **User**: Developers
- **Risk**: Medium (code modification)
- **Classification**: **ADMIN-BYPASS** (dev maintenance)
- **Justification**: Follow-up refactoring tool; developer-supervised
- **Usage**: Developer code quality tool

#### `fix_syntax_errors.py`
- **Purpose**: Fix broken bracket patterns and syntax issues
- **User**: Developers
- **Risk**: High (code modification)
- **Classification**: **ADMIN-BYPASS** (dev maintenance)
- **Justification**: Emergency syntax fix tool; requires developer review
- **Usage**: Developer-only emergency fixes with manual verification

#### `generate_cli_docs.py`
- **Purpose**: Auto-generate CLI documentation
- **User**: Developers, technical writers
- **Risk**: Low (documentation generation)
- **Classification**: **ADMIN-BYPASS** (documentation tool)
- **Justification**: Documentation generation; no runtime impact
- **Usage**: Developer documentation workflow

#### `generate_cerberus_languages.py`
- **Purpose**: Generate Cerberus multi-language support
- **User**: Developers, i18n team
- **Risk**: Medium (code generation)
- **Classification**: **ADMIN-BYPASS** (code generation)
- **Justification**: Development tool for i18n; developer-supervised
- **Usage**: Developer internationalization workflow

### Backup & Audit Tools

#### `backup_audit.py`
- **Purpose**: Create timestamped audit log backups
- **User**: Administrators, automated backup systems
- **Risk**: Low (read-only backup)
- **Classification**: **ADMIN-BYPASS** (admin utility)
- **Justification**: Backup utility; no production impact
- **Usage**: Admin-scheduled backups

### Installation & Registration

#### `register_legion_moltbook.py`
- **Purpose**: Register Legion MoltBook device
- **User**: Administrators
- **Risk**: Medium (device registration)
- **Classification**: **ADMIN-BYPASS** (admin utility)
- **Justification**: Device registration; admin-only operation
- **Usage**: Admin device management

#### `register_simple.py`
- **Purpose**: Simple registration utility
- **User**: Administrators
- **Risk**: Low (registration helper)
- **Classification**: **ADMIN-BYPASS** (admin utility)
- **Justification**: Admin registration tool
- **Usage**: Administrative setup

### Specialized Utilities

#### `deepseek_v32_cli.py`
- **Purpose**: DeepSeek V3.2 inference CLI
- **User**: Developers, researchers
- **Risk**: Medium (AI model access)
- **AI Usage**: Direct model inference
- **Classification**: **ADMIN-BYPASS** (research tool)
- **Justification**: Research/development tool; not for production users
- **Usage**: Developer/researcher AI model testing
- **NOTE**: If exposed to end-users, MUST be reclassified as GOVERNED

#### `inspection_cli.py`
- **Purpose**: Code inspection utility
- **User**: Developers
- **Risk**: Low (read-only inspection)
- **Classification**: **ADMIN-BYPASS** (dev tool)
- **Justification**: Developer inspection tool
- **Usage**: Developer code analysis

#### `quickstart.py`
- **Purpose**: Quick project setup
- **User**: Developers, new users
- **Risk**: Low (setup helper)
- **Classification**: **ADMIN-BYPASS** (setup tool)
- **Justification**: Development setup; not production code
- **Usage**: Developer onboarding

---

## EXAMPLE SCRIPTS (Demonstrations, not production)

### Demonstration Scripts

#### `demo_cybersecurity_knowledge.py`
- **Purpose**: Demonstrate cybersecurity knowledge base queries
- **User**: Developers, documentation
- **Risk**: Low (demo/educational)
- **AI Usage**: Reads from knowledge base
- **Classification**: **EXAMPLE** (demonstration code)
- **Justification**: Educational demonstration; not for production use
- **Usage**: Documentation examples, developer learning

#### `demo_security_features.py`
- **Purpose**: Interactive security features demonstration
- **User**: Developers, documentation, marketing
- **Risk**: Low (simulated results)
- **AI Usage**: No (uses hardcoded examples)
- **Classification**: **EXAMPLE** (demonstration code)
- **Justification**: Marketing/educational demo; simulated data
- **Usage**: Feature demonstrations, documentation

---

## SHELL/BATCH SCRIPTS (Classified by function)

### Build & Release Scripts (ADMIN-BYPASS)

- `build_production.ps1` - **ADMIN-BYPASS** (build automation)
- `build_release.bat` - **ADMIN-BYPASS** (build automation)
- `build_release.sh` - **ADMIN-BYPASS** (build automation)

**Justification**: Build scripts run in controlled CI/CD environment; admin-supervised

### Cleanup & Maintenance (ADMIN-BYPASS)

- `cleanup_root.ps1` - **ADMIN-BYPASS** (maintenance)

**Justification**: Maintenance script; admin-only

### Installation & Setup (ADMIN-BYPASS)

- `create_installation_usb.ps1` - **ADMIN-BYPASS** (admin utility)
- `create_portable_usb.ps1` - **ADMIN-BYPASS** (admin utility)
- `create_universal_usb.ps1` - **ADMIN-BYPASS** (admin utility)
- `install_desktop.ps1` - **ADMIN-BYPASS** (installation)
- `install-shortcuts.py` - **ADMIN-BYPASS** (installation helper)
- `setup-desktop.bat` - **ADMIN-BYPASS** (setup)
- `setup-docker-wsl.ps1` - **ADMIN-BYPASS** (Docker setup)
- `get-docker.sh` - **ADMIN-BYPASS** (Docker installation)

**Justification**: Installation/setup scripts; admin-supervised

### Deployment Scripts (GOVERNED)

- `deploy-monitoring.sh` - **GOVERNED** (production deployment)
- `deploy_complete.ps1` - **GOVERNED** (production deployment)
- `temporal_quickstart.sh` - **GOVERNED** (infrastructure deployment)

**Justification**: Production deployment scripts require governance

### Launch Scripts (Context-Dependent)

- `launch-desktop.bat` - **ADMIN-BYPASS** (desktop launcher)
- `launch-desktop.ps1` - **ADMIN-BYPASS** (desktop launcher)

**Justification**: Desktop application launchers; no network operations

### Testing Scripts (ADMIN-BYPASS)

- `run_e2e_tests.ps1` - **ADMIN-BYPASS** (testing)

**Justification**: E2E tests run in controlled environment; developer-supervised

---

## WORKFLOW-SPECIFIC SCRIPTS

### Red Team Workflow (GOVERNED)

- `redteam_workflow.py` - **GOVERNED** (security testing workflow)

**Justification**: Coordinates multiple security tests; production impact

---

## SUBDIRECTORIES

### `scripts/demo/` (EXAMPLE)
- **Classification**: All scripts **EXAMPLE**
- **Justification**: Demonstration directory; educational content

### `scripts/deploy/` (GOVERNED)
- **Classification**: All scripts **GOVERNED**
- **Justification**: Deployment automation; production impact

### `scripts/hooks/` (ADMIN-BYPASS)
- **Classification**: All scripts **ADMIN-BYPASS**
- **Justification**: Git hooks; developer workflow automation

### `scripts/install/` (ADMIN-BYPASS)
- **Classification**: All scripts **ADMIN-BYPASS**
- **Justification**: Installation utilities; admin-supervised

### `scripts/verify/` (GOVERNED)
- **Classification**: All scripts **GOVERNED**
- **Justification**: Verification/validation tools; production impact

---

## SUMMARY STATISTICS

### Total Scripts Classified: 58

**GOVERNED**: 19 scripts (33%)
- Production monitoring: 3
- Security operations: 4
- Security testing: 7
- Content management: 2
- Deployment: 3

**ADMIN-BYPASS**: 31 scripts (53%)
- Development tools: 8
- Installation/setup: 12
- Build automation: 3
- Admin utilities: 5
- Testing: 3

**EXAMPLE**: 8 scripts (14%)
- Demonstrations: 2
- Demo directory: 6 (estimated)

---

## IMPLEMENTATION STATUS

### Phase 1: Classification ✅
- [x] All scripts reviewed
- [x] Risk levels assigned
- [x] AI usage identified
- [x] Classifications determined

### Phase 2: Implementation (Next Steps)
- [ ] Modify GOVERNED scripts to use `route_request()`
- [ ] Add admin-bypass headers to ADMIN-BYPASS scripts
- [ ] Add EXAMPLE markers to demo scripts
- [ ] Update script documentation
- [ ] Create governance integration tests

### Phase 3: Validation
- [ ] Test governed script routing
- [ ] Verify admin-bypass warnings display
- [ ] Validate example script markers
- [ ] Update CI/CD to check classifications

---

## GOVERNANCE ROUTING PATTERN

### GOVERNED Scripts Should Use:

```python
#!/usr/bin/env python3
"""
[Script description]

GOVERNANCE: GOVERNED
Classification: Production utility
Risk: [Low/Medium/High]
"""

from app.core.runtime.router import route_request

def main():
    """Main function with governance routing."""
    result = route_request("cli", {
        "action": "script.operation_name",
        "params": {
            "operation": "specific_operation",
            # Script-specific parameters
        },
        "metadata": {
            "script": __file__,
            "user": "operator"
        }
    })
    
    if not result["approved"]:
        print(f"❌ Operation blocked: {result['reason']}")
        return 1
    
    # Proceed with operation
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### ADMIN-BYPASS Scripts Should Have:

```python
#!/usr/bin/env python3
"""
[Script description]

⚠️ ADMIN-ONLY SCRIPT ⚠️
GOVERNANCE: ADMIN-BYPASS
Classification: [Dev tool/Maintenance/Admin utility]
Risk: [Description of risks]
Justification: [Why bypass is acceptable]

WARNING: This script bypasses governance controls.
         - Restricted to system administrators
         - Manual oversight required
         - Not for automated/end-user execution
         - Review security implications before use

Usage: [Specific usage instructions]
"""

# Display warning on execution
import sys
print("⚠️  ADMIN-ONLY SCRIPT - Governance bypass active")
print("    Review security implications before proceeding")
response = input("    Continue? (yes/no): ")
if response.lower() != "yes":
    print("❌ Aborted")
    sys.exit(1)

# Normal script execution
def main():
    # Direct execution without governance routing
    ...
```

### EXAMPLE Scripts Should Have:

```python
#!/usr/bin/env python3
"""
[Script description]

📚 EXAMPLE/DEMONSTRATION CODE
GOVERNANCE: EXAMPLE
Classification: Educational/demonstration
Production Use: NOT RECOMMENDED

This script is for demonstration purposes only.
Do not use in production without proper review and adaptation.

Usage: [Demo usage instructions]
"""

print("📚 DEMONSTRATION MODE")
print("    This is example code for educational purposes")
print()

def main():
    # Demo code
    ...
```

---

## QUARTERLY REVIEW CHECKLIST

- [ ] Review new scripts added since last review
- [ ] Verify existing classifications remain appropriate
- [ ] Check for scripts moved between categories
- [ ] Update risk assessments
- [ ] Validate governance routing implementations
- [ ] Review bypass justifications
- [ ] Update documentation

---

## CHANGE LOG

### 2026-01-21 - Initial Classification
- Classified all 58 scripts in scripts/ directory
- Established governance routing patterns
- Documented bypass justifications
- Created implementation roadmap

---

## APPENDIX: RISK MATRIX

| Risk Level | Criteria | Examples |
|-----------|----------|----------|
| **Low** | Read-only, no modifications, no network | Documentation generation, backups |
| **Medium** | Limited modifications, controlled scope | Code quality tools, content updates |
| **High** | Security-critical, production impact | Security operations, deployment, attack testing |

---

## CONTACT & GOVERNANCE

**Governance Authority**: Multi-Path Governance System  
**Review Frequency**: Quarterly + on-demand for new scripts  
**Exception Process**: Document in SCRIPT_CLASSIFICATION_EXCEPTIONS.md  
**Audit Trail**: All governed scripts logged in audit.log  

---

*This classification is binding for all script execution. Violations of governance requirements must be escalated to security team.*
