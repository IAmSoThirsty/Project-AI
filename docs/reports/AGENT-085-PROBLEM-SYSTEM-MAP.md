---
agent_id: AGENT-085
mission: troubleshooting-to-system-links
phase: phase-5-cross-linking
created: 2026-04-20
status: in-progress
deliverable_type: navigation-map
target_links: 300
actual_links: 0
tags:
  - phase-5
  - cross-linking
  - troubleshooting
  - navigation
  - wiki-links
stakeholders:
  - documentation-team
  - support-team
  - developers
related_agents:
  - AGENT-069
  - AGENT-040
---

# AGENT-085: Problem→System Navigation Map

## Mission Overview

**Objective**: Create comprehensive bidirectional wiki links from troubleshooting documentation to relevant system documentation, enabling faster problem resolution.

**Target**: ~300 troubleshooting→system wiki links  
**Current**: 0 links (in progress)  
**Completion**: 0%

---

## Troubleshooting Documentation Inventory

### Core Troubleshooting Guides (6 Documents)

#### 1. **TEMPLATER_TROUBLESHOOTING_GUIDE.md** (30.9 KB)
**Focus**: Obsidian Templater plugin issues
- Installation issues
- Template execution issues  
- User scripts issues
- Syntax errors
- Performance issues
- Integration issues

**System Links Needed**:
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]
- [[TEMPLATER_SETUP_GUIDE]]
- [[TEMPLATER_QUICK_REFERENCE]]
- [[TEMPLATER_COMMAND_REFERENCE]]
- [[docs/developer/config.md]]
- [[docs/architecture/MODULE_CONTRACTS]]

**Priority**: HIGH (Most detailed troubleshooting guide)

#### 2. **vault-troubleshooting-guide.md** (46.2 KB)
**Focus**: Obsidian vault configuration and plugins
- Vault structure issues
- Plugin conflicts
- Dataview issues
- Templater issues
- Graph view issues
- Tag Wrangler issues

**System Links Needed**:
- [[docs/architecture/ROOT_STRUCTURE]]
- [[DATAVIEW_SETUP_GUIDE]]
- [[GRAPH_VIEW_GUIDE]]
- [[TAG_WRANGLER_GUIDE]]
- [[DOCUMENTATION_STRUCTURE_GUIDE]]
- [[docs/developer/DEVELOPMENT]]

**Priority**: HIGH (Most comprehensive vault guide)

#### 3. **docs/dataview-examples/TROUBLESHOOTING.md** (19.1 KB)
**Focus**: Dataview plugin query errors and performance
- Installation issues
- Query errors
- Performance problems
- DataviewJS issues
- Configuration problems
- Platform-specific issues

**System Links Needed**:
- [[DATAVIEW_SETUP_GUIDE]]
- [[docs/dataview-examples/QUICK_REFERENCE]]
- [[docs/developer/config.md]]
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]
- [[docs/architecture/STATE_MODEL]]

**Priority**: HIGH (Dataview-specific troubleshooting)

#### 4. **.github/ISSUE_AUTOMATION.md** (11.1 KB)
**Focus**: Automated issue management system
- Auto-triage issues
- False positive detection
- Security workflow issues
- Auto-resolution problems

**System Links Needed**:
- [[.github/AUTOMATION]]
- [[.github/SECURITY_AUTOMATION]]
- [[.github/workflows/]] (directory reference)
- [[docs/developer/checks.md]]
- [[SECURITY]]

**Priority**: MEDIUM (Workflow troubleshooting)

#### 5. **src/thirsty_lang/docs/FAQ.md** (3.6 KB)
**Focus**: Thirsty-lang programming language FAQs
- Installation questions
- Running programs
- Debugging
- Learning resources

**System Links Needed**:
- [[src/thirsty_lang/docs/QUICK_REFERENCE]]
- [[src/thirsty_lang/docs/SECURITY_GUIDE]]
- [[integrations/thirsty_lang_complete/QUICK_REFERENCE]]
- [[docs/developer/DEVELOPMENT]]

**Priority**: LOW (Smaller scope)

#### 6. **DATAVIEW_SETUP_GUIDE.md** (Needs verification)
**Focus**: Dataview installation and configuration
- Setup process
- Configuration options

**System Links Needed**:
- [[docs/dataview-examples/TROUBLESHOOTING]]
- [[docs/dataview-examples/QUICK_REFERENCE]]
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]

**Priority**: MEDIUM (Setup-focused, less troubleshooting)

---

### Fix Reports & Issue Documentation (13 Documents)

#### Security Fix Reports

1. **PATH_TRAVERSAL_FIX_REPORT.md** (12.7 KB)
   - **Links to**: 
     - [[docs/PATH_SECURITY_GUIDE]]
     - [[docs/security_compliance/THREAT_MODEL_SECURITY_WORKFLOWS]]
     - [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]]
     - [[docs/architecture/ARCHITECTURE_SECURITY_ETHICS_OVERVIEW]]

2. **TIMING_ATTACK_FIX_REPORT.md** (10.6 KB)
   - **Links to**:
     - [[docs/reports/ACCOUNT_LOCKOUT_IMPLEMENTATION_REPORT]]
     - [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]]
     - [[docs/security_compliance/SECURITY_AGENTS_GUIDE]]

3. **GUI_INPUT_VALIDATION_FIX_REPORT.md** (10.0 KB)
   - **Links to**:
     - [[docs/reports/GUI_ARCHITECTURE_EVALUATION_REPORT]]
     - [[docs/developer/DESKTOP_APP_README]]
     - [[docs/architecture/ARCHITECTURE_OVERVIEW]]
     - [[INPUT_VALIDATION_SECURITY_AUDIT]]

4. **BYPASS_FIX_REPORT.md** (7.9 KB)
   - **Links to**:
     - [[docs/reports/CONSTITUTIONAL_AI_IMPLEMENTATION_REPORT]]
     - [[docs/architecture/AGENT_MODEL]]
     - [[docs/developer/AI_SAFETY_OVERVIEW]]
     - [[docs/architecture/ARCHITECTURE_SECURITY_ETHICS_OVERVIEW]]

5. **AGENT_23_SHELL_INJECTION_FIX_REPORT.md** (4.9 KB)
   - **Links to**:
     - [[ISSUE_SHELL_INJECTION_B602]]
     - [[SECURITY]]
     - [[docs/security_compliance/THREAT_MODEL_SECURITY_WORKFLOWS]]

#### Issue Documentation

6. **ISSUE_SHELL_INJECTION_B602.md** (7.2 KB)
   - **Links to**:
     - [[docs/reports/AGENT_23_SHELL_INJECTION_FIX_REPORT]]
     - [[SECURITY]]
     - [[docs/developer/checks.md]]

7. **ISSUE_B324_MD5_WEAK_HASH.md** (6.7 KB)
   - **Links to**:
     - [[docs/reports/SHA256_AUDIT_REPORT]]
     - [[docs/CRYPTO_RANDOM_AUDIT]]
     - [[docs/security_compliance/SECURITY_AGENTS_GUIDE]]

#### Archive Fix Reports

8. **docs/internal/archive/CRITICAL_FIXES_SUMMARY.md** (12.2 KB)
9. **docs/internal/archive/CI_CD_FIX_ANALYSIS.md** (8.7 KB)
10. **docs/internal/archive/session-notes/FIXES_APPLIED.md** (7.1 KB)
11. **docs/internal/archive/session-notes/LINT_FIXES_REPORT.md** (7.6 KB)
12. **docs/internal/archive/session-notes/SYNTAX_HIGHLIGHTING_FIX.md** (5.7 KB)
13. **docs/internal/archive/session-notes/QUICK_REFERENCE_FIXES.md** (3.5 KB)
14. **docs/internal/archive/historical-summaries/SECURITY_FIX_SUMMARY.md** (4.6 KB)

---

## System Documentation Inventory

### Architecture Documentation (30+ Documents)

**Core Architecture**:
- [[docs/architecture/ARCHITECTURE_OVERVIEW]]
- [[docs/architecture/ARCHITECTURE_SECURITY_ETHICS_OVERVIEW]]
- [[docs/architecture/PROJECT_STRUCTURE]]
- [[docs/architecture/ROOT_STRUCTURE]]
- [[docs/architecture/MODULE_CONTRACTS]]
- [[docs/architecture/STATE_MODEL]]

**Specialized Systems**:
- [[docs/architecture/AGENT_MODEL]]
- [[docs/architecture/CAPABILITY_MODEL]]
- [[docs/architecture/ENGINE_SPEC]]
- [[docs/architecture/WORKFLOW_ENGINE]]
- [[docs/architecture/INTEGRATION_LAYER]]
- [[docs/architecture/IDENTITY_ENGINE]]

**Advanced Architectures**:
- [[docs/architecture/GOD_TIER_PLATFORM_IMPLEMENTATION]]
- [[docs/architecture/GOD_TIER_SYSTEMS_DOCUMENTATION]]
- [[docs/architecture/GOD_TIER_DISTRIBUTED_ARCHITECTURE]]
- [[docs/architecture/GOD_TIER_INTELLIGENCE_SYSTEM]]
- [[docs/architecture/HYDRA_50_ARCHITECTURE]]
- [[docs/architecture/CONTRARIAN_FIREWALL_ARCHITECTURE]]
- [[docs/architecture/TARL_ARCHITECTURE]]
- [[docs/architecture/TEMPORAL_INTEGRATION_ARCHITECTURE]]

**Security & Safety**:
- [[docs/architecture/ARCHITECTURE_SECURITY_ETHICS_OVERVIEW]]
- [[docs/architecture/OFFLINE_FIRST_ARCHITECTURE]]
- [[docs/architecture/PLATFORM_COMPATIBILITY]]
- [[docs/architecture/SOVEREIGN_RUNTIME]]
- [[docs/architecture/PLANETARY_DEFENSE_MONOLITH]]

---

### Developer Documentation (50+ Documents)

**Quick Start Guides**:
- [[docs/developer/DESKTOP_APP_QUICKSTART]]
- [[docs/developer/HOW_TO_RUN]]
- [[docs/developer/DEVELOPMENT]]
- [[docs/developer/ANTIGRAVITY_QUICKSTART]]
- [[docs/developer/IMAGE_GENERATION_QUICKSTART]]

**Implementation Guides**:
- [[docs/developer/AI_PERSONA_IMPLEMENTATION]]
- [[docs/developer/CONTINUOUS_LEARNING]]
- [[docs/developer/COMMAND_MEMORY_FEATURES]]
- [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]]
- [[docs/developer/IMPLEMENTATION_COMPLETE]]

**API References**:
- [[docs/developer/DEVELOPER_QUICK_REFERENCE]]
- [[docs/developer/HYDRA_50_API_REFERENCE]]
- [[docs/developer/TEMPORAL_QUICK_REFERENCE]]
- [[docs/developer/LIARA_QUICK_REFERENCE]]
- [[docs/developer/api.md]]
- [[docs/developer/config.md]]

**Deployment Guides**:
- [[docs/developer/DEPLOYMENT_GUIDE]]
- [[docs/developer/E2E_SETUP_GUIDE]]
- [[docs/developer/HYDRA_50_DEPLOYMENT_GUIDE]]
- [[docs/developer/WEB_DEPLOYMENT_GUIDE]]
- [[docs/developer/PRODUCTION_RELEASE_GUIDE]]
- [[docs/developer/INFRASTRUCTURE_PRODUCTION_GUIDE]]
- [[docs/developer/KUBERNETES_MONITORING_GUIDE]]

**Specialized Guides**:
- [[docs/developer/CONTRARIAN_FIREWALL_API_GUIDE]]
- [[docs/developer/DEEPSEEK_V32_GUIDE]]
- [[docs/developer/TARL_ORCHESTRATION_GUIDE]]
- [[docs/developer/DOCKER_WSL_SETUP]]

**Testing & Quality**:
- [[docs/developer/checks.md]]
- [[docs/developer/codacy_setup.md]]
- [[docs/developer/100_PERCENT_COVERAGE]]
- [[docs/developer/COVERAGE_ACHIEVEMENT_SUMMARY]]

---

## Link Categories & Patterns

### Category 1: Installation/Setup Issues → Setup Guides

**Pattern**: Installation errors link to setup documentation

**Examples**:
- Templater installation error → [[TEMPLATER_SETUP_GUIDE]]
- Dataview not appearing → [[DATAVIEW_SETUP_GUIDE]]
- Vault structure wrong → [[docs/architecture/ROOT_STRUCTURE]]
- Plugin conflicts → [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]

**Estimated Links**: 50

---

### Category 2: Configuration Issues → Configuration Docs

**Pattern**: Configuration problems link to config references

**Examples**:
- Templater config not persisting → [[docs/developer/config.md]]
- Dataview settings reverting → [[docs/dataview-examples/QUICK_REFERENCE]]
- Plugin settings issue → [[TEMPLATER_QUICK_REFERENCE]]
- Workflow config error → [[.github/AUTOMATION]]

**Estimated Links**: 40

---

### Category 3: Execution/Runtime Issues → Architecture Docs

**Pattern**: Runtime errors link to system architecture

**Examples**:
- Template execution fails → [[docs/architecture/WORKFLOW_ENGINE]]
- Query performance slow → [[docs/architecture/STATE_MODEL]]
- Script errors → [[docs/architecture/MODULE_CONTRACTS]]
- Integration failures → [[docs/architecture/INTEGRATION_LAYER]]

**Estimated Links**: 60

---

### Category 4: Security Issues → Security Docs

**Pattern**: Security problems link to security architecture

**Examples**:
- Path traversal vulnerability → [[docs/PATH_SECURITY_GUIDE]]
- Timing attacks → [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]]
- Input validation → [[INPUT_VALIDATION_SECURITY_AUDIT]]
- Authentication errors → [[docs/reports/ACCOUNT_LOCKOUT_IMPLEMENTATION_REPORT]]
- Bypass attempts → [[docs/architecture/ARCHITECTURE_SECURITY_ETHICS_OVERVIEW]]

**Estimated Links**: 50

---

### Category 5: Performance Issues → Performance Docs

**Pattern**: Performance problems link to optimization guides

**Examples**:
- Slow queries → [[docs/architecture/STATE_MODEL]]
- Memory leaks → [[docs/developer/DEVELOPMENT]]
- High CPU usage → [[docs/architecture/WORKFLOW_ENGINE]]
- Database slow → [[docs/reports/DATABASE_PERSISTENCE_AUDIT_REPORT]]

**Estimated Links**: 30

---

### Category 6: Developer Issues → Developer Guides

**Pattern**: Developer problems link to developer documentation

**Examples**:
- API errors → [[docs/developer/api.md]]
- Deployment failures → [[docs/developer/DEPLOYMENT_GUIDE]]
- Testing issues → [[docs/developer/checks.md]]
- Coverage problems → [[docs/developer/100_PERCENT_COVERAGE]]
- Docker issues → [[docs/developer/DOCKER_WSL_SETUP]]

**Estimated Links**: 50

---

### Category 7: Platform Issues → Platform Docs

**Pattern**: Platform-specific issues link to compatibility docs

**Examples**:
- Windows path errors → [[docs/architecture/PLATFORM_COMPATIBILITY]]
- Mobile performance → [[docs/architecture/OFFLINE_FIRST_ARCHITECTURE]]
- Cross-platform bugs → [[docs/architecture/GOD_TIER_PLATFORM_IMPLEMENTATION]]

**Estimated Links**: 20

---

## Implementation Strategy

### Phase 1: High-Priority Guides (Weeks 1-2)

**Files**:
1. TEMPLATER_TROUBLESHOOTING_GUIDE.md (+ 50 links)
2. vault-troubleshooting-guide.md (+ 60 links)
3. docs/dataview-examples/TROUBLESHOOTING.md (+ 40 links)

**Target**: 150 links

---

### Phase 2: Security & Fix Reports (Week 3)

**Files**:
4. PATH_TRAVERSAL_FIX_REPORT.md (+ 15 links)
5. TIMING_ATTACK_FIX_REPORT.md (+ 12 links)
6. GUI_INPUT_VALIDATION_FIX_REPORT.md (+ 15 links)
7. BYPASS_FIX_REPORT.md (+ 10 links)
8. ISSUE_SHELL_INJECTION_B602.md (+ 8 links)
9. ISSUE_B324_MD5_WEAK_HASH.md (+ 8 links)

**Target**: 68 links

---

### Phase 3: Supporting Docs & FAQs (Week 4)

**Files**:
10. .github/ISSUE_AUTOMATION.md (+ 20 links)
11. src/thirsty_lang/docs/FAQ.md (+ 15 links)
12. DATAVIEW_SETUP_GUIDE.md (+ 12 links)
13. Archive fix reports (+ 35 links total)

**Target**: 82 links

---

## Link Quality Standards

### ✅ Valid Wiki Link Format
```markdown
See [[TEMPLATER_SETUP_GUIDE]] for installation instructions.
See [[docs/architecture/ARCHITECTURE_OVERVIEW]] for system architecture.
```

### ✅ Descriptive Link Context
```markdown
For performance optimization, see [[docs/architecture/STATE_MODEL#caching-strategies]].
```

### ✅ Bidirectional Links
```markdown
# In troubleshooting guide:
See [[SYSTEM_GUIDE]] for architecture details.

# In system guide:
For troubleshooting, see [[TROUBLESHOOTING_GUIDE]].
```

### ❌ Invalid Patterns
```markdown
❌ See SYSTEM_GUIDE (not a wiki link)
❌ See [SYSTEM_GUIDE](SYSTEM_GUIDE.md) (not wiki format)
❌ [[broken link]] (dangling reference)
```

---

## System Reference Section Template

Add to each troubleshooting guide:

```markdown
---

## System Reference

### Related Architecture
- [[docs/architecture/ARCHITECTURE_OVERVIEW]] - Overall system architecture
- [[docs/architecture/MODULE_CONTRACTS]] - Module interfaces
- [[docs/architecture/STATE_MODEL]] - State management

### Related Guides
- [[SETUP_GUIDE]] - Installation and configuration
- [[QUICK_REFERENCE]] - Command reference
- [[DEVELOPER_GUIDE]] - Developer documentation

### Related Security
- [[SECURITY]] - Security policy
- [[docs/security_compliance/THREAT_MODEL]] - Threat model
- [[docs/PATH_SECURITY_GUIDE]] - Path security

### Related Troubleshooting
- [[OTHER_TROUBLESHOOTING_GUIDE]] - Related issues
- [[FAQ]] - Frequently asked questions

---
```

---

## Common Issues Index

### Installation Issues
| Problem | Troubleshooting Guide | System Reference |
|---------|----------------------|------------------|
| Plugin not appearing | [[TEMPLATER_TROUBLESHOOTING_GUIDE#issue-1]] | [[TEMPLATER_SETUP_GUIDE]] |
| Permission errors | [[vault-troubleshooting-guide#permissions]] | [[docs/PATH_SECURITY_GUIDE]] |
| File conflicts | [[vault-troubleshooting-guide#conflicts]] | [[docs/architecture/ROOT_STRUCTURE]] |

### Configuration Issues
| Problem | Troubleshooting Guide | System Reference |
|---------|----------------------|------------------|
| Settings not persisting | [[TEMPLATER_TROUBLESHOOTING_GUIDE#issue-settings]] | [[docs/developer/config.md]] |
| Query errors | [[docs/dataview-examples/TROUBLESHOOTING#query-errors]] | [[docs/dataview-examples/QUICK_REFERENCE]] |
| Workflow failures | [[.github/ISSUE_AUTOMATION#troubleshooting]] | [[.github/AUTOMATION]] |

### Performance Issues
| Problem | Troubleshooting Guide | System Reference |
|---------|----------------------|------------------|
| Slow queries | [[docs/dataview-examples/TROUBLESHOOTING#performance]] | [[docs/architecture/STATE_MODEL]] |
| High CPU | [[vault-troubleshooting-guide#performance]] | [[docs/architecture/WORKFLOW_ENGINE]] |
| Memory leaks | [[vault-troubleshooting-guide#memory]] | [[docs/developer/DEVELOPMENT]] |

### Security Issues
| Problem | Troubleshooting Guide | System Reference |
|---------|----------------------|------------------|
| Path traversal | [[docs/reports/PATH_TRAVERSAL_FIX_REPORT]] | [[docs/PATH_SECURITY_GUIDE]] |
| Timing attacks | [[docs/reports/TIMING_ATTACK_FIX_REPORT]] | [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]] |
| Input validation | [[docs/reports/GUI_INPUT_VALIDATION_FIX_REPORT]] | [[INPUT_VALIDATION_SECURITY_AUDIT]] |
| Shell injection | [[ISSUE_SHELL_INJECTION_B602]] | [[SECURITY]] |

---

## Progress Tracking

### By Document Type
- [ ] Core troubleshooting guides (6 docs): 0/150 links
- [ ] Security fix reports (5 docs): 0/60 links  
- [ ] Issue documentation (2 docs): 0/16 links
- [ ] Archive fix reports (7 docs): 0/35 links
- [ ] Supporting docs (3 docs): 0/39 links

### By Category
- [ ] Installation/Setup links: 0/50
- [ ] Configuration links: 0/40
- [ ] Execution/Runtime links: 0/60
- [ ] Security links: 0/50
- [ ] Performance links: 0/30
- [ ] Developer links: 0/50
- [ ] Platform links: 0/20

### Overall Progress
- **Target**: 300 links
- **Actual**: 0 links
- **Completion**: 0%

---

## Quality Assurance Checklist

- [ ] All troubleshooting guides have "System Reference" section
- [ ] All wiki links use correct `[[path/to/file]]` format
- [ ] No dangling references (all linked files exist)
- [ ] Bidirectional links created where appropriate
- [ ] Common issues index complete
- [ ] All links tested for validity
- [ ] Section anchors use correct `#heading-name` format
- [ ] Links include descriptive context

---

## Next Actions

1. ✅ Create problem-system mapping database
2. ⏳ Analyze TEMPLATER_TROUBLESHOOTING_GUIDE for link opportunities
3. ⏳ Add wiki links to TEMPLATER_TROUBLESHOOTING_GUIDE
4. ⏳ Add "System Reference" section to TEMPLATER_TROUBLESHOOTING_GUIDE
5. ⏳ Analyze vault-troubleshooting-guide.md
6. ⏳ Add wiki links to vault-troubleshooting-guide.md
7. ⏳ Continue through all troubleshooting documents
8. ⏳ Create bidirectional links in system docs
9. ⏳ Validate all links
10. ⏳ Generate final report

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-04-20  
**Status**: Planning Complete, Implementation Starting
