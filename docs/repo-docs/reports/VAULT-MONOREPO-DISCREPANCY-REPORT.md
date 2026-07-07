# Vault-MonoRepo Synchronization Discrepancy Report

**Generated**: 2026-04-21
**Session**: 9d59d274-14d2-4f4e-ba6a-39675b58dd2d

## Executive Summary

### Total File Counts

- **Vault (docs/ + indexes/ + relationships/ + .obsidian/)**: 719 files
  - docs/: 490 files
  - indexes/: 11 files  
  - relationships/: 195 files
  - .obsidian/: 23 files

- **MonoRepo Root**: 369 files directly in root
- **MonoRepo Key Directories**:
  - src/: 653 files
  - tests/: 256 files
  - scripts/: 94 files
  - engines/: 115 files
  - api/: 8 files
  - web/: 31 files
  - tarl/: 33 files

### Critical Findings

#### MAJOR DISCREPANCY #1: Root Organization Chaos

**Issue**: 121 AGENT-*files and 87* REPORT.md files scattered in mono-repo root

**Vault State**: docs/reports/ contains only 2 files:

- AGENT-080-COMPLETION-REPORT.md
- HEALTH_REPORT.md

**MonoRepo State**: 121 AGENT-*files in root, 87* REPORT.md files in root

**Problem**:

- Vault expects reports to be organized under docs/reports/
- MonoRepo has 200+ report/agent files scattered in root
- This creates massive navigation confusion
- 99% of AGENT-* files are in root, only 1% in vault structure

#### MAJOR DISCREPANCY #2: Duplicate Files

**Issue**: 6 files exist in BOTH root AND docs/ simultaneously

Files with duplicates:

1. CODE_OF_CONDUCT.md (root + docs/)
2. CONTRIBUTING.md (root + docs/)
3. DEVELOPER_QUICK_REFERENCE.md (root + docs/)
4. HEALTH_REPORT.md (root + docs/reports/)
5. README.md (root + docs/)
6. SECURITY.md (root + docs/)

**Problem**: Which is canonical? Which should be kept?

---

## Vault Structure (Source of Truth for Documentation)

### docs/ Structure (14 subdirectories, 490 files)

- architecture/
- archive/
- assets/
- dataview-examples/
- developer/
- executive/
- governance/
- gradle/
- internal/
- legal/
- operations/
- project_ai_god_tier_diagrams/
- **reports/** ← THIS IS WHERE REPORTS SHOULD BE
- security_compliance/

### indexes/ Structure (11 files, no subdirs)

- README.md
- agent_capabilities_index.md
- api_endpoints_index.md
- code_modules_index.md
- configuration_options_index.md
- deployment_targets_index.md
- documentation_index.md
- governance_policies_index.md
- integration_points_index.md
- security_controls_index.md
- system_components_index.md

### relationships/ Structure (19 subdirectories, 195 files)

- agents/
- cli-automation/
- configuration/
- constitutional/
- core-ai/
- data/
- deployment/
- error-handling/
- governance/
- gui/
- integrations/
- monitoring/
- performance/
- plugins/
- security/
- temporal/
- testing/
- utilities/
- web/

---

## MonoRepo Structure

### Root Directory Issues

**Total root files**: 369

**Breakdown**:

- AGENT-* files: 121 (should be in docs/reports/)
- *REPORT.md files: 87 (should be in docs/reports/)
- Legitimate root files: ~150 (configs, scripts, READMEs)
- Duplicate files: 6 (need resolution)

**Sample AGENT files in root (should be moved)**:

- AGENT_008_P0_METADATA_ENRICHMENT_REPORT.md
- AGENT_009_CLASSIFICATION_REPORT.md
- AGENT_009_MISSION_COMPLETE_CHECKLIST.md
- AGENT_009_P0_GOVERNANCE_SECURITY_METADATA_REPORT.md
- AGENT_010_FINAL_MISSION_REPORT.md
- AGENT_011_AUDIENCE_CLASSIFICATION_REPORT.md
- AGENT_011_DATAVIEW_MISSION_COMPLETE.md
- AGENT_011_METADATA_ENRICHMENT_REPORT.md
- ... (113 more)

**Sample REPORT files in root (should be moved)**:

- ACCOUNT_LOCKOUT_IMPLEMENTATION_REPORT.md
- AGENT_008_P0_METADATA_ENRICHMENT_REPORT.md
- AGENT_009_CLASSIFICATION_REPORT.md
- AGENT_009_P0_GOVERNANCE_SECURITY_METADATA_REPORT.md
- AGENT_010_FINAL_MISSION_REPORT.md
- AGENT_011_AUDIENCE_CLASSIFICATION_REPORT.md
- AGENT_011_METADATA_ENRICHMENT_REPORT.md
- AGENT_011_TIME_ESTIMATION_REPORT.md
- ... (79 more)

### Top-Level Directory Structure

69 top-level directories (excluding .git, venv, node_modules, cache dirs)

Key directories that ARE correctly organized:

- docs/ ✓ (exists and matches vault)
- indexes/ ✓ (exists and matches vault)
- relationships/ ✓ (exists and matches vault)
- src/ ✓ (code directory, correctly separate)
- tests/ ✓ (test directory, correctly separate)
- api/ ✓ (api code, correctly separate)
- web/ ✓ (web app, correctly separate)

---

## Discrepancy Categories

### Category 1: MonoRepo → Vault Mismatches (Files NOT in Vault)

**1.1 Root AGENT Files Not in Vault** (121 files):

- All 121 AGENT-* files in root exist in mono-repo
- Only 8 AGENT-* files exist anywhere in docs/ (vault)
- Only 1 AGENT-* file exists in docs/reports/ specifically
- **Gap**: 113 AGENT files undocumented/misplaced in vault

**1.2 Root REPORT Files Not in Vault** (87 files):

- All 87 *REPORT.md files in root exist in mono-repo
- Only 21 *REPORT.md files exist anywhere in docs/ (vault)
- Only 2 *REPORT.md files exist in docs/reports/ specifically
- **Gap**: 66 REPORT files undocumented/misplaced in vault

**1.3 Properly-Placed Code Directories** (No Action Required):

- src/, tests/, api/, web/, scripts/, engines/, tarl/
- These are CODE, not DOCUMENTATION
- Should remain in mono-repo root, NOT moved to vault
- Vault should INDEX them (in indexes/), RELATE them (in relationships/), but NOT contain them

### Category 2: Vault → MonoRepo Mismatches (Dead References)

**STATUS**: Requires deep link analysis

To determine this, I need to:

1. Scan all markdown files in docs/ for wiki links
2. Scan all markdown files in indexes/ for references
3. Scan all markdown files in relationships/ for references
4. Verify each link target exists in mono-repo

**Estimated issue count**: Unknown (requires Phase 3B analysis)

### Category 3: Duplicate Files Requiring Resolution

| File | Root Location | Vault Location | Action Required |
|------|-------------- |  ---------------- | -----------------|
| CODE_OF_CONDUCT.md | ✓ Exists | ✓ Exists in docs/ | STOP: Ask user which is canonical |
| CONTRIBUTING.md | ✓ Exists | ✓ Exists in docs/ | STOP: Ask user which is canonical |
| DEVELOPER_QUICK_REFERENCE.md | ✓ Exists | ✓ Exists in docs/ | STOP: Ask user which is canonical |
| HEALTH_REPORT.md | ✓ Exists | ✓ Exists in docs/reports/ | STOP: Ask user which is canonical |
| README.md | ✓ Exists | ✓ Exists in docs/ | STOP: Ask user which is canonical |
| SECURITY.md | ✓ Exists | ✓ Exists in docs/ | STOP: Ask user which is canonical |

---

## Proposed Action Plan (REQUIRES USER APPROVAL)

### STOP POINT: Conflict Resolution Required

**Before proceeding, user MUST resolve**:

1. Which duplicate files are canonical? (6 files)
2. Should root AGENT/REPORT files be MOVED or COPIED to docs/reports/?
3. Are there intentional reasons for root placement?

### Proposed Phase 6 Actions (IF APPROVED)

**Assumption**: User wants docs/reports/ to be the canonical location for AGENT/REPORT files

**Action 6.1**: Move AGENT-* files from root → docs/reports/

- Files to move: 121 AGENT-* files
- Source: T:\Project-AI-main\AGENT-*.md
- Destination: T:\Project-AI-main\docs\reports\
- Method: `Move-Item` (not copy, to avoid duplicates)

**Action 6.2**: Move *REPORT.md files from root → docs/reports/

- Files to move: 87 *REPORT.md files
- Source: T:\Project-AI-main\*REPORT.md
- Destination: T:\Project-AI-main\docs\reports\
- Method: `Move-Item`
- NOTE: Some overlap with AGENT files (AGENT_*_REPORT.md already covered in 6.1)

**Action 6.3**: Resolve duplicate files

- Option A: Keep root, delete docs/ copy (for project meta files)
- Option B: Keep docs/, delete root copy (for vault-integrated files)
- Option C: Keep both with clear purpose distinction
- **REQUIRES USER DECISION**

**Action 6.4**: Verify vault indexes and relationships

- Update indexes/ if references changed
- Update relationships/ if file moves broke links
- Scan for broken wiki links after moves

---

## Risk Assessment

### High Risk

1. **Broken Links**: Moving 200+ files WILL break wiki links if not updated
2. **Git History**: File moves may complicate git blame/history
3. **External Dependencies**: Scripts/tools may hardcode paths to root files

### Medium Risk

1. **Duplicate Conflicts**: Without resolution, duplicates remain ambiguous
2. **Missing Updates**: Indexes/relationships may reference old paths

### Low Risk

1. **Code Directory Confusion**: Clear that src/tests/api/web stay in place
2. **Vault Configuration**: .obsidian/ is config, not documentation

---

## Verification Checklist (Post-Synchronization)

After approved actions executed:

- [ ] Verify docs/reports/ contains all expected AGENT-* files
- [ ] Verify docs/reports/ contains all expected *REPORT.md files
- [ ] Verify root no longer has scattered AGENT/REPORT files (only essential ones)
- [ ] Verify no duplicate files remain (unless intentionally kept)
- [ ] Scan docs/ for broken wiki links
- [ ] Scan indexes/ for broken references
- [ ] Scan relationships/ for broken references
- [ ] Update .obsidian/ graph filters if needed
- [ ] Test Obsidian vault opens correctly
- [ ] Verify git status shows expected moves (not deletes/adds)

---

## Questions for User (MUST ANSWER BEFORE PHASE 6)

### Critical Questions

1. **Duplicate File Resolution**: For the 6 duplicate files (CODE_OF_CONDUCT.md, CONTRIBUTING.md, DEVELOPER_QUICK_REFERENCE.md, HEALTH_REPORT.md, README.md, SECURITY.md):
   - Should root or docs/ version be canonical?
   - Should one be deleted or should both remain?

2. **File Movement Method**: For 121 AGENT files and 87 REPORT files:
   - Should files be MOVED (disappear from root) or COPIED (remain in both)?
   - Recommendation: MOVE to avoid duplicates and confusion

3. **Legitimate Root Files**: Are there any AGENT/REPORT files that should STAY in root?
   - Example: README.md typically stays in root for GitHub display
   - Example: SECURITY.md typically stays in root for GitHub security tab

4. **Link Update Scope**: After moving files:
   - Should I scan ALL vault files for broken links and auto-fix?
   - Should I generate a report of broken links for manual review?

5. **Vault Indexes**: After file moves:
   - Should indexes/ be regenerated to reflect new paths?
   - Should I verify all index references are valid?

---

## Recommendation

**My Recommendation as Principal Architect**:

1. **Resolve duplicates**: Keep root versions of CODE_OF_CONDUCT.md, CONTRIBUTING.md, README.md, SECURITY.md (GitHub convention). Move/keep docs/ versions as vault copies.

2. **Move AGENT/REPORT files**: Move all 121 AGENT-*and 87* REPORT.md files from root → docs/reports/. This creates clean root and organized vault.

3. **Update vault links**: After moves, scan all vault markdown files and update wiki link paths to reflect new locations.

4. **Verify indexes**: Update indexes/ to reference new docs/reports/ paths.

5. **Test vault**: Open Obsidian vault and verify navigation, graph view, and links all work.

**This will achieve**: Mono-repo root becomes clean (configs/code only), vault becomes comprehensive guide (all docs organized), perfect mirroring achieved.

---

## End of Report

**Status**: Awaiting user approval for Phase 6 execution

**Next Steps**: User reviews this report, answers critical questions, then gives explicit "proceed" for synchronization execution.
