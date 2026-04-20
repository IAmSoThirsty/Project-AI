# Obsidian Vault Git Configuration Decision Matrix

**Version:** 1.0  
**Purpose:** Quick-reference decision guide for selecting appropriate Obsidian git strategy  
**Related:** VAULT_GIT_STRATEGY.md (comprehensive documentation)

---

## Quick Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│ Is Obsidian the PRIMARY documentation platform for ALL team?   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
         NO                      YES
          │                       │
          ▼                       ▼
    PERSONAL VAULT          ┌──────────────────────────────┐
    (.gitignore current)    │ Do team members need SAME    │
                            │ plugin ecosystem/templates?  │
                            └──────────┬───────────────────┘
                                       │
                           ┌───────────┴───────────┐
                           │                       │
                          NO                      YES
                           │                       │
                           ▼                       ▼
                     PERSONAL VAULT          TEAM VAULT
                                         (.gitignore.team-vault)
```

---

## Configuration Matrix

| **Criterion**                          | **Personal Vault** | **Team Vault** | **Current: Project-AI** |
|----------------------------------------|:------------------:|:--------------:|:-----------------------:|
| **Primary Use Case**                   |                    |                |                         |
| Single developer notes                 | ✅ Ideal           | ❌ Overkill    | ✅ Yes                  |
| Team knowledge base                    | ❌ Limited         | ✅ Ideal       | ❌ No                   |
| Mixed tooling (Obsidian + VSCode)      | ✅ Flexible        | ⚠️ Forces lock-in | ✅ Yes               |
|                                        |                    |                |                         |
| **Collaboration Needs**                |                    |                |                         |
| Shared plugin ecosystem                | ❌ Manual          | ✅ Automatic   | ❌ Not needed           |
| Template standardization               | ❌ Manual sharing  | ✅ Tracked     | ⚠️ Ad-hoc               |
| Consistent documentation tooling       | ❌ No              | ✅ Yes         | ❌ No                   |
|                                        |                    |                |                         |
| **Technical Complexity**               |                    |                |                         |
| Merge conflicts (workspace state)      | ✅ Zero            | ⚠️ Low-Medium  | ✅ Zero (current)       |
| Onboarding complexity                  | ✅ Low             | ⚠️ Medium      | ✅ Low (current)        |
| .gitignore maintenance                 | ✅ Simple          | ⚠️ Complex     | ✅ Simple (current)     |
|                                        |                    |                |                         |
| **Operational Benefits**               |                    |                |                         |
| Zero configuration conflicts           | ✅ Yes             | ❌ No          | ✅ Yes (current)        |
| Personal workflow freedom              | ✅ Total           | ⚠️ Constrained | ✅ Total (current)      |
| Team plugin sync                       | ❌ No              | ✅ Yes         | ❌ No                   |
|                                        |                    |                |                         |
| **Git Repository Impact**              |                    |                |                         |
| Commit noise (config churn)            | ✅ None            | ⚠️ Some        | ✅ None (current)       |
| Binary file tracking (themes/plugins)  | ✅ None            | ⚠️ Some        | ✅ None (current)       |
| Repository size                        | ✅ Minimal         | ⚠️ Larger      | ✅ Minimal (current)    |

**Legend:**  
✅ Ideal / Best choice  
⚠️ Works with caveats / Requires discipline  
❌ Not recommended / Doesn't support

---

## Scenario-Based Recommendations

### Scenario 1: Solo Developer Documentation
**Context:** Single developer using Obsidian for project notes and architecture docs

**Recommendation:** **Personal Vault** ✅  
**Rationale:**
- No collaboration overhead
- Complete workflow freedom
- Focus on content, not tooling configuration

**Implementation:**
```gitignore
.obsidian/
```

---

### Scenario 2: Small Team (2-5 developers), Mixed Tooling
**Context:** Some use Obsidian, others use VSCode/Notion/etc.

**Recommendation:** **Personal Vault** ✅  
**Rationale:**
- Avoid forcing Obsidian on entire team
- Content is markdown (readable in any editor)
- Shared templates can be `.md` files in `docs/templates/`

**Implementation:**
```gitignore
.obsidian/
```

**Alternative:** Share templates outside `.obsidian/`:
```
docs/
└── templates/
    ├── ADR-template.md
    ├── bug-report-template.md
    └── feature-spec-template.md
```

---

### Scenario 3: Documentation-First Team, Obsidian Standardized
**Context:** Entire team uses Obsidian as primary docs tool, standardization required

**Recommendation:** **Team Vault** ✅  
**Rationale:**
- Benefit from shared plugin ecosystem (Dataview, Templater, etc.)
- Consistent documentation experience
- Templates and snippets synchronized

**Implementation:**
```bash
# Use .gitignore.team-vault as base
cp .gitignore.team-vault .gitignore

# Clean personal state
Remove-Item .obsidian/workspace*.json -Force
Remove-Item .obsidian/cache -Recurse -Force

# Stage shared configs
git add .obsidian/plugins.json
git add .obsidian/templates/
```

---

### Scenario 4: Enterprise Knowledge Base (10+ contributors)
**Context:** Large team, Obsidian Publish/Sync for documentation portal

**Recommendation:** **Team Vault** ✅ with strict governance  
**Rationale:**
- Scale requires standardization
- Plugin ecosystem critical for advanced features
- Templates/snippets enforce documentation standards

**Additional Requirements:**
- **CODEOWNERS for `.obsidian/`**: Restrict config changes to documentation leads
- **PR Review Required**: All plugin additions reviewed for security/compatibility
- **Version Pinning**: Lock community plugin versions to prevent breaking updates
- **Monthly Audits**: Review `.obsidian/` for cruft and outdated configs

**Implementation:**
```gitignore
# Enhanced team vault with strict controls
.obsidian/workspace*.json
.obsidian/cache/
.obsidian/plugins/*/data.json

# Track with CODEOWNERS
!.obsidian/plugins.json           # @docs-team
!.obsidian/templates/             # @docs-team
!.obsidian/snippets/              # @docs-team
```

**CODEOWNERS:**
```
/.obsidian/ @docs-team
```

---

## Migration Decision Matrix

### When to Migrate: Personal → Team Vault

| **Trigger**                                    | **Migrate?** | **Priority** |
|------------------------------------------------|:------------:|:------------:|
| 3+ team members request same plugin            | ✅ Yes       | Medium       |
| Onboarding takes >1 hour due to vault setup    | ✅ Yes       | High         |
| Template inconsistency causing doc drift       | ✅ Yes       | High         |
| CSS snippets duplicated across personal vaults | ✅ Yes       | Low          |
| Team using Obsidian Publish for public docs    | ✅ Yes       | Critical     |
| Merge conflicts from workspace state           | ❌ No (bug)  | N/A          |
| Individual prefers different theme             | ❌ No        | N/A          |

**Migration Cost Estimate:**
- **Planning:** 4-8 hours (audit, clean, document)
- **Implementation:** 2-4 hours (configure, test, deploy)
- **Validation:** 1 week (team testing, feedback)
- **Total:** ~2 weeks from decision to full adoption

---

## Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Tracking workspace.json
**Symptom:** Constant merge conflicts on `workspace.json`  
**Cause:** Personal workspace state being shared  
**Fix:**
```gitignore
# ALWAYS exclude
.obsidian/workspace*.json
```

### ❌ Anti-Pattern 2: Tracking Plugin Data
**Symptom:** User's plugin settings overwritten after pull  
**Cause:** `plugins/*/data.json` tracked  
**Fix:**
```gitignore
# Track manifest, not data
!.obsidian/plugins.json           # Which plugins (OK)
.obsidian/plugins/*/data.json     # Plugin settings (EXCLUDE)
```

### ❌ Anti-Pattern 3: Inconsistent Strategy Across Branches
**Symptom:** `.obsidian/` tracked in `main`, excluded in `develop`  
**Cause:** Branch-specific `.gitignore` divergence  
**Fix:**
- Standardize `.gitignore` across all branches
- Document strategy in `VAULT_GIT_STRATEGY.md`
- Use branch protection to prevent config drift

### ❌ Anti-Pattern 4: Forcing Obsidian on Team
**Symptom:** PRs rejected due to "not using Obsidian templates"  
**Cause:** Tool-specific workflow requirements  
**Fix:**
- Keep markdown content tool-agnostic
- Provide VSCode/CLI alternatives for templates
- Document non-Obsidian workflows in CONTRIBUTING.md

---

## Project-AI Current Configuration Analysis

### Context
- **Repository Type:** Python desktop application + web version
- **Documentation Scope:** Architecture docs, developer guides, API references
- **Team Size:** Variable (open source contributors)
- **Primary Tools:** VSCode, PyCharm, Obsidian (optional)
- **Documentation Format:** Markdown (tool-agnostic)

### Selected Strategy: **Personal Vault** ✅

**Rationale:**
1. **Mixed Tooling**: Contributors use diverse editors (VSCode, PyCharm, Vim, etc.)
2. **Documentation Focus**: Content > tooling configuration
3. **Low Collaboration Friction**: No forced Obsidian adoption
4. **Zero Conflicts**: Workspace state never committed
5. **Onboarding Simplicity**: Clone and start reading `.md` files

### Configuration Verification

**Current `.gitignore` Entry:**
```gitignore
# Obsidian vault personal settings
# For personal vault usage - excludes workspace-specific configuration
# See VAULT_GIT_STRATEGY.md for team vault configuration
.obsidian/
```

**Tracked Files:**
- ✅ All markdown documentation (`.md`)
- ✅ Images, diagrams, attachments
- ✅ Documentation structure (directories)

**Excluded Files:**
- ❌ Workspace state (`workspace.json`)
- ❌ Personal preferences (`hotkeys.json`, `appearance.json`)
- ❌ Plugin configurations (`.obsidian/plugins/`)
- ❌ Cache files (`.obsidian/cache/`)

**Alternative Sharing Mechanisms:**
- Templates: Share as `.md` files in `docs/templates/` (outside `.obsidian/`)
- Plugin Recommendations: Document in `README.md` or `CONTRIBUTING.md`
- Snippets: Share as standalone CSS files in `docs/styles/`

---

## Quick Reference Commands

### Verify Current Strategy
```powershell
# Check .obsidian/ is excluded
git status | Select-String ".obsidian"
# Should return NOTHING (fully excluded)

# Verify content is tracked
git ls-files "*.md" | Measure-Object -Line
# Should show all markdown files
```

### Switch to Team Vault
```powershell
# 1. Copy team configuration
Copy-Item .gitignore.team-vault .gitignore

# 2. Clean personal state
Remove-Item .obsidian/workspace*.json -Force
Remove-Item .obsidian/cache -Recurse -Force -ErrorAction SilentlyContinue

# 3. Stage shared configs
git add .obsidian/plugins.json
git add .obsidian/templates/
git add .obsidian/snippets/

# 4. Commit
git commit -m "feat: migrate to team vault configuration

See VAULT_GIT_STRATEGY.md for details.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Audit .obsidian/ Contents
```powershell
# List all files with sizes
Get-ChildItem .obsidian -Recurse | 
    Select-Object FullName, Length, LastWriteTime |
    Sort-Object Length -Descending |
    Format-Table -AutoSize

# Find large files (>100KB)
Get-ChildItem .obsidian -Recurse -File |
    Where-Object { $_.Length -gt 100KB } |
    Format-Table Name, Length, FullName
```

---

## Summary Table: When to Use Each Strategy

| **Use Case**                               | **Strategy**     | **Config File**           |
|--------------------------------------------|------------------|---------------------------|
| Solo developer notes                       | Personal Vault   | `.gitignore` (current)    |
| Mixed tooling team (Obsidian optional)     | Personal Vault   | `.gitignore` (current)    |
| Small team, ad-hoc collaboration           | Personal Vault   | `.gitignore` (current)    |
| Documentation-first team (all use Obsidian)| Team Vault       | `.gitignore.team-vault`   |
| Enterprise knowledge base (10+ users)      | Team Vault       | `.gitignore.team-vault`   |
| Obsidian Publish deployment                | Team Vault       | `.gitignore.team-vault`   |

---

## Next Steps

### For Current Configuration (Personal Vault)
1. ✅ `.obsidian/` is excluded (implemented)
2. ✅ Documentation complete (`VAULT_GIT_STRATEGY.md`)
3. ⏭️ Optional: Document recommended plugins in `CONTRIBUTING.md`
4. ⏭️ Optional: Share templates as standalone `.md` files in `docs/templates/`

### For Team Vault Migration (Future)
1. ⏭️ Review `.gitignore.team-vault` example
2. ⏭️ Audit current `.obsidian/` contents
3. ⏭️ Gather team consensus on standardization
4. ⏭️ Follow migration checklist in `VAULT_GIT_STRATEGY.md`

---

**END OF DECISION MATRIX**
