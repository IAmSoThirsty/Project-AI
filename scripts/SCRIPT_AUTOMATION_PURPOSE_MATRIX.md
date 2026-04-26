---
type: script-documentation
tags: [scripts, automation, classification, matrix, reference]
created: 2026-04-20
last_verified: 2026-04-20
status: current
related_systems: [governance, classification, automation]
stakeholders: [devops, security-team, automation-team]
script_language: [python, powershell, bash]
automation_purpose: [classification, reference]
requires_admin: false
review_cycle: quarterly
---

# Script Automation Purpose Matrix

**Generated:** 2026-04-20  
**Authority:** AGENT-016 (Scripts Documentation Metadata Enrichment Specialist)  
**Source:** SCRIPT_CLASSIFICATION.md

---

## Overview

This matrix provides a cross-reference of scripts by automation purpose, script language, and admin requirements. Use this for quick lookup and operational planning.

---

## Automation Purpose Taxonomy

### 1. Validation (13 scripts)
Scripts that validate, verify, or check compliance.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `benchmark.py` | Python | No | Low | GOVERNED |
| `healthcheck.py` | Python | No | Low | GOVERNED |
| `validate_release.py` | Python | No | Medium | GOVERNED |
| `run_asl_assessment.py` | Python | No | Medium | GOVERNED |
| `run_asl3_security.py` | Python | Yes | High | GOVERNED |
| `run_cbrn_classifier.py` | Python | No | High | GOVERNED |
| `run_robustness_benchmarks.py` | Python | No | Medium | GOVERNED |
| `sarif_exporter.py` | Python | No | Medium | GOVERNED |
| `validate_index_names.py` | Python | No | Low | ADMIN-BYPASS |
| `verify_governance.py` | Python | No | Low | ADMIN-BYPASS |
| `run_e2e_tests.ps1` | PowerShell | No | Low | ADMIN-BYPASS |
| **Automation scripts/** | PowerShell | No | Low | ADMIN-BYPASS |
| - `validate-tags.ps1` | PowerShell | No | Low | ADMIN-BYPASS |

### 2. Deployment (9 scripts)
Scripts that deploy, install, or configure systems.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `launch_mcp_server.py` | Python | Yes | High | GOVERNED |
| `setup_temporal.py` | Python | Yes | High | GOVERNED |
| `hydra50_deploy.py` | Python | Yes | High | GOVERNED |
| `deploy-monitoring.sh` | Bash | Yes | High | GOVERNED |
| `deploy_complete.ps1` | PowerShell | Yes | High | GOVERNED |
| `temporal_quickstart.sh` | Bash | Yes | High | GOVERNED |
| `install_desktop.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| `setup-desktop.bat` | Batch | Yes | Medium | ADMIN-BYPASS |
| `setup-docker-wsl.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |

### 3. Security Testing (7 scripts)
Scripts that perform security testing, red teaming, or attack simulation.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `run_comprehensive_expansion.py` | Python | No | High | GOVERNED |
| `run_novel_scenarios.py` | Python | No | High | GOVERNED |
| `run_red_hat_expert_simulations.py` | Python | No | High | GOVERNED |
| `run_red_team_stress_tests.py` | Python | No | High | GOVERNED |
| `run_security_worker.py` | Python | Yes | High | GOVERNED |
| `redteam_workflow.py` | Python | No | High | GOVERNED |
| `demo_security_features.py` | Python | No | Low | EXAMPLE |

### 4. Analysis (8 scripts)
Scripts that analyze data, generate reports, or extract insights.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `backup_audit.py` | Python | No | Low | ADMIN-BYPASS |
| `inspection_cli.py` | Python | No | Low | ADMIN-BYPASS |
| `deepseek_v32_cli.py` | Python | No | Medium | ADMIN-BYPASS |
| **Automation scripts/** | PowerShell | No | Low | ADMIN-BYPASS |
| - `add-metadata.ps1` | PowerShell | No | Low | ADMIN-BYPASS |
| - `convert-links.ps1` | PowerShell | No | Low | ADMIN-BYPASS |
| - `batch-process.ps1` | PowerShell | No | Low | ADMIN-BYPASS |
| - `test-automation-scripts.ps1` | PowerShell | No | Low | ADMIN-BYPASS |

### 5. Content Management (3 scripts)
Scripts that manage knowledge bases, documentation, or content.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `populate_cybersecurity_knowledge.py` | Python | No | Medium | GOVERNED |
| `update_osint_bible.py` | Python | No | Medium | GOVERNED |
| `demo_cybersecurity_knowledge.py` | Python | No | Low | EXAMPLE |

### 6. Code Maintenance (7 scripts)
Scripts that fix, refactor, or improve code quality.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `fix_assert_statements.py` | Python | No | Medium | ADMIN-BYPASS |
| `fix_logging_performance.py` | Python | No | Medium | ADMIN-BYPASS |
| `fix_logging_performance_surgical.py` | Python | No | Medium | ADMIN-BYPASS |
| `fix_logging_phase2.py` | Python | No | Medium | ADMIN-BYPASS |
| `fix_syntax_errors.py` | Python | No | High | ADMIN-BYPASS |
| `generate_cli_docs.py` | Python | No | Low | ADMIN-BYPASS |
| `generate_cerberus_languages.py` | Python | No | Medium | ADMIN-BYPASS |

### 7. Build Automation (3 scripts)
Scripts that build, compile, or package releases.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `build_production.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| `build_release.bat` | Batch | Yes | Medium | ADMIN-BYPASS |
| `build_release.sh` | Bash | Yes | Medium | ADMIN-BYPASS |

### 8. Installation (8 scripts)
Scripts that install software, create installers, or configure environments.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `create_installation_usb.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| `create_portable_usb.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| `create_universal_usb.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| `install-shortcuts.py` | Python | Yes | Low | ADMIN-BYPASS |
| `get-docker.sh` | Bash | Yes | Medium | ADMIN-BYPASS |
| `register_legion_moltbook.py` | Python | Yes | Medium | ADMIN-BYPASS |
| `register_simple.py` | Python | Yes | Low | ADMIN-BYPASS |
| `quickstart.py` | Python | No | Low | ADMIN-BYPASS |

### 9. System Utilities (4 scripts)
General-purpose system utilities and launchers.

| Script | Language | Admin? | Risk | Classification |
|--------|----------|--------|------|----------------|
| `launch-desktop.bat` | Batch | No | Low | ADMIN-BYPASS |
| `launch-desktop.ps1` | PowerShell | No | Low | ADMIN-BYPASS |
| `cleanup_root.ps1` | PowerShell | Yes | Medium | ADMIN-BYPASS |
| Demo directory scripts | Mixed | No | Low | EXAMPLE |

---

## Script Language Distribution

### Python (38 scripts - 66%)

**GOVERNED (16 scripts)**
- Production monitoring: 3
- Security operations: 4
- Security testing: 7
- Content management: 2

**ADMIN-BYPASS (20 scripts)**
- Code maintenance: 7
- Analysis: 3
- Validation: 2
- Installation: 4
- Utilities: 4

**EXAMPLE (2 scripts)**
- Demonstrations: 2

### PowerShell (14 scripts - 24%)

**GOVERNED (3 scripts)**
- Deployment: 2
- Monitoring: 1

**ADMIN-BYPASS (11 scripts)**
- Build automation: 1
- Installation: 4
- Automation tools: 4
- Testing: 1
- Utilities: 1

### Bash (4 scripts - 7%)

**GOVERNED (1 script)**
- Deployment: 1

**ADMIN-BYPASS (3 scripts)**
- Build automation: 1
- Installation: 1
- Deployment: 1

### Batch (2 scripts - 3%)

**ADMIN-BYPASS (2 scripts)**
- Build automation: 1
- Utilities: 1

---

## Admin Requirements Analysis

### Requires Admin Privileges (21 scripts - 36%)

**Why admin access needed:**
1. **System Installation** (8 scripts)
   - USB creation, shortcuts, Docker setup
   - System-level configuration changes

2. **Production Deployment** (6 scripts)
   - Service deployment, infrastructure setup
   - Security system configuration

3. **Build Operations** (3 scripts)
   - Package signing, system-wide builds

4. **Security Operations** (2 scripts)
   - ASL-3 encryption, security controls

5. **Maintenance** (2 scripts)
   - Root cleanup, system configuration

### No Admin Required (37 scripts - 64%)

Safe for standard user execution:
- Development tools (code fixes, docs generation)
- Analysis and reporting
- Validation and testing
- Content management
- Demonstrations

---

## Risk Level Distribution

### High Risk (15 scripts - 26%)

**Characteristics:**
- Security-critical operations
- Production deployment
- Attack simulation
- System-level changes

**Examples:**
- Security testing suite (7 scripts)
- Deployment automation (6 scripts)
- Emergency fixes (2 scripts)

**Controls:**
- All GOVERNED or with admin warnings
- Audit logging required
- Manual oversight mandatory

### Medium Risk (18 scripts - 31%)

**Characteristics:**
- Code modifications
- Content updates
- Build automation
- Installation

**Examples:**
- Code maintenance tools (7 scripts)
- Content management (3 scripts)
- Build scripts (3 scripts)
- Installation utilities (5 scripts)

**Controls:**
- Most ADMIN-BYPASS with justification
- Testing required before production
- Rollback capability recommended

### Low Risk (25 scripts - 43%)

**Characteristics:**
- Read-only operations
- Analysis and reporting
- Validation without changes
- Demonstrations

**Examples:**
- Monitoring tools (3 scripts)
- Backup utilities (1 script)
- Analysis tools (4 scripts)
- Demo scripts (8+ scripts)

**Controls:**
- Minimal restrictions
- Suitable for automation
- Safe for CI/CD integration

---

## Governance Classification Summary

| Classification | Count | Percentage | Primary Purpose |
|----------------|-------|------------|-----------------|
| **GOVERNED** | 19 | 33% | Production operations requiring audit |
| **ADMIN-BYPASS** | 31 | 53% | Admin tools with documented justification |
| **EXAMPLE** | 8 | 14% | Educational demonstrations |
| **TOTAL** | **58** | **100%** | Complete script inventory |

---

## Operational Patterns

### Pattern 1: Production Monitoring
**Scripts:** `benchmark.py`, `healthcheck.py`, `validate_release.py`  
**Language:** Python  
**Purpose:** Validation  
**Admin:** No  
**Risk:** Low-Medium  
**Classification:** GOVERNED  
**Usage:** CI/CD pipelines, automated monitoring

### Pattern 2: Security Operations
**Scripts:** ASL-3, CBRN, security worker, red team suite  
**Language:** Python  
**Purpose:** Security Testing, Validation  
**Admin:** Mixed (some require admin)  
**Risk:** High  
**Classification:** GOVERNED  
**Usage:** Security team, manual execution, audit required

### Pattern 3: Code Quality Tools
**Scripts:** fix_logging*, fix_assert_statements, fix_syntax_errors  
**Language:** Python  
**Purpose:** Code Maintenance  
**Admin:** No  
**Risk:** Medium-High  
**Classification:** ADMIN-BYPASS  
**Usage:** Developer workstations, pre-commit hooks

### Pattern 4: Documentation Automation
**Scripts:** automation/add-metadata.ps1, convert-links.ps1, validate-tags.ps1  
**Language:** PowerShell  
**Purpose:** Analysis, Validation  
**Admin:** No  
**Risk:** Low  
**Classification:** ADMIN-BYPASS  
**Usage:** Documentation workflows, CI/CD

### Pattern 5: Deployment Automation
**Scripts:** deploy_complete.ps1, setup_temporal.py, hydra50_deploy.py  
**Language:** Mixed (Python, PowerShell, Bash)  
**Purpose:** Deployment  
**Admin:** Yes  
**Risk:** High  
**Classification:** GOVERNED  
**Usage:** DevOps team, production releases

---

## Quick Lookup Tables

### By Governance Classification

#### GOVERNED Scripts (19)
```
benchmark.py
healthcheck.py
validate_release.py
run_asl3_security.py
run_asl_assessment.py
run_cbrn_classifier.py
sarif_exporter.py
run_comprehensive_expansion.py
run_novel_scenarios.py
run_red_hat_expert_simulations.py
run_red_team_stress_tests.py
run_robustness_benchmarks.py
run_security_worker.py
populate_cybersecurity_knowledge.py
update_osint_bible.py
launch_mcp_server.py
setup_temporal.py
hydra50_deploy.py
redteam_workflow.py
```

#### ADMIN-BYPASS Scripts (31)
```
fix_assert_statements.py
fix_logging_performance.py
fix_logging_performance_surgical.py
fix_logging_phase2.py
fix_syntax_errors.py
generate_cli_docs.py
generate_cerberus_languages.py
backup_audit.py
register_legion_moltbook.py
register_simple.py
deepseek_v32_cli.py
inspection_cli.py
quickstart.py
validate_index_names.py
verify_governance.py
install-shortcuts.py
build_production.ps1
build_release.bat
build_release.sh
cleanup_root.ps1
create_installation_usb.ps1
create_portable_usb.ps1
create_universal_usb.ps1
install_desktop.ps1
setup-desktop.bat
setup-docker-wsl.ps1
get-docker.sh
launch-desktop.bat
launch-desktop.ps1
run_e2e_tests.ps1
automation/* (4 scripts)
```

#### EXAMPLE Scripts (8)
```
demo_security_features.py
demo_cybersecurity_knowledge.py
demo/* (6+ scripts)
```

---

## Usage Recommendations

### For DevOps Teams
**Focus on:** GOVERNED deployment scripts + ADMIN-BYPASS automation tools  
**Key Scripts:**
- `deploy_complete.ps1` - Production deployment
- `setup_temporal.py` - Infrastructure setup
- `automation/batch-process.ps1` - Documentation automation
- `validate_release.py` - Release validation

### For Security Teams
**Focus on:** GOVERNED security operations + security testing  
**Key Scripts:**
- `run_asl3_security.py` - ASL-3 operations
- `run_cbrn_classifier.py` - CBRN classification
- Red team suite (7 scripts) - Attack testing
- `sarif_exporter.py` - Security reporting

### For Developers
**Focus on:** ADMIN-BYPASS code quality tools + validation  
**Key Scripts:**
- `fix_logging_performance.py` - Performance optimization
- `generate_cli_docs.py` - Documentation generation
- `automation/validate-tags.ps1` - Tag validation
- `inspection_cli.py` - Code inspection

### For Technical Writers
**Focus on:** ADMIN-BYPASS documentation tools  
**Key Scripts:**
- `automation/add-metadata.ps1` - Metadata generation
- `automation/convert-links.ps1` - Link conversion
- `automation/validate-tags.ps1` - Tag validation
- `automation/batch-process.ps1` - Batch operations

---

## Related Documentation

- **SCRIPT_CLASSIFICATION.md** - Complete classification reference
- **IMPLEMENTATION_GUIDE.md** - Implementation patterns and rollout plan
- **GROUP5_COMPLETION_REPORT.md** - Classification project completion report
- **automation/AUTOMATION_GUIDE.md** - PowerShell automation comprehensive guide
- **automation/README.md** - Quick reference for automation tools

---

## Maintenance

**Review Schedule:** Quarterly or upon script addition/modification  
**Next Review:** 2026-07-20  
**Owner:** DevOps + Security Teams  
**Updates:** Submit PR with classification changes to SCRIPT_CLASSIFICATION.md

---

*Generated by AGENT-016 (Scripts Documentation Metadata Enrichment Specialist)*  
*Authority: Principal Architect Implementation Standard*  
*Last Updated: 2026-04-20*
