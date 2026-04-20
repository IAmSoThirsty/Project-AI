# Obsidian Vault Git Strategy

**Version:** 1.0  
**Status:** Production  
**Author:** AGENT-010 (GitIgnore Configuration Specialist)  
**Date:** 2025-01-20

---

## Executive Summary

This document defines the git strategy for Obsidian vault integration within the Project-AI repository, providing clear guidance for both **personal vault** and **team vault** scenarios. The current configuration implements a **personal vault** approach, excluding all `.obsidian/` settings from version control to prevent conflicts from user-specific workspace preferences.

---

## Problem Statement

Obsidian stores workspace configuration in the `.obsidian/` directory, which contains:

- **Personal Preferences**: Theme, hotkeys, editor settings, window layout
- **Machine-Specific Paths**: Absolute file paths, plugin data locations
- **Workspace State**: Last opened files, pane arrangements, graph view settings
- **Plugin Configurations**: Community plugin settings (often user-specific)
- **Cache Files**: Search indices, graph data, file metadata

**The Challenge**: Deciding what to track in version control without causing:
1. Merge conflicts from concurrent workspace state changes
2. Overwriting personal preferences across team members
3. Breaking plugin configurations due to machine-specific paths
4. Repository bloat from cache and ephemeral state files

---

## Decision Matrix: Personal vs Team Vault

### Personal Vault (CURRENT CONFIGURATION)

**Use When:**
- Obsidian vault is used by a single developer for project documentation
- Documentation is primary purpose, not collaborative knowledge management
- Each team member maintains their own vault structure
- Vault serves as personal project notes/scratchpad

**Configuration:**
```gitignore
# .gitignore
.obsidian/
```

**Tracked:**
- Markdown content (`.md` files)
- Attachments (images, PDFs, etc.)
- Project-specific documentation structure

**Excluded:**
- All `.obsidian/` directory contents
- User preferences, themes, hotkeys
- Workspace state, cache files
- Plugin configurations

**Advantages:**
- ✅ Zero merge conflicts from workspace state
- ✅ Complete personalization freedom
- ✅ No machine-specific path issues
- ✅ Clean git history (no config churn)

**Disadvantages:**
- ❌ Plugins not synchronized across team
- ❌ Recommended templates/snippets not shared
- ❌ Each user configures vault from scratch

---

### Team Vault (ALTERNATIVE APPROACH)

**Use When:**
- Obsidian vault is primary knowledge base for entire team
- Shared plugin ecosystem enhances collaboration
- Standardized workspace improves onboarding
- Documentation-as-code with strong governance

**Configuration:**
See `.gitignore.team-vault` for example implementation.

**Tracked (Selective):**
- `plugins.json` - Enabled plugin list
- `community-plugins.json` - Community plugin registry
- `core-plugins.json` - Core plugin toggles
- `templates/` - Shared note templates
- `snippets/` - CSS customizations
- `graph.json` - Graph view defaults (with caution)

**Excluded (Always):**
- `workspace.json` - User-specific layouts
- `workspace-mobile.json` - Mobile layout state
- `hotkeys.json` - Personal keybindings
- `appearance.json` - Theme/font preferences
- `plugins/*/data.json` - Plugin-specific user data
- `cache/` - All cache files

**Advantages:**
- ✅ Plugin ecosystem synchronized
- ✅ Shared templates and snippets
- ✅ Faster onboarding for new team members
- ✅ Consistent documentation tooling

**Disadvantages:**
- ❌ Requires discipline to avoid committing workspace state
- ❌ Merge conflicts on shared configs (e.g., plugin versions)
- ❌ Risk of breaking personal workflows with shared settings
- ❌ More complex `.gitignore` maintenance

---

## Implementation: Personal Vault (Current)

### Current `.gitignore` Entry

```gitignore
# Obsidian vault personal settings
# For personal vault usage - excludes workspace-specific configuration
# See VAULT_GIT_STRATEGY.md for team vault configuration
.obsidian/
```

### What This Achieves

1. **Complete Isolation**: Each developer's Obsidian workspace is entirely personal
2. **Zero Conflicts**: No risk of workspace state merge conflicts
3. **Freedom**: Users choose themes, plugins, layouts independently
4. **Simplicity**: No coordination required for vault configuration

### Verification

After adding `.obsidian/` to `.gitignore`:

```powershell
# Verify exclusion
git status
# Should NOT show .obsidian/ as untracked

# Test with new file in .obsidian/
echo "test" > .obsidian/test.txt
git status
# Should NOT detect the new file
```

### Migration from Tracked .obsidian/

If `.obsidian/` was previously tracked:

```powershell
# Remove from git index (keeps local files)
git rm -r --cached .obsidian/

# Commit removal
git commit -m "chore: exclude .obsidian/ from version control

Personal vault configuration should not be tracked.
See VAULT_GIT_STRATEGY.md for rationale.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

# Verify exclusion
git status  # Should be clean
```

---

## Alternative: Team Vault Configuration

For teams wanting to share vault configuration, see `.gitignore.team-vault` for a selective-tracking approach.

### Key Principles for Team Vaults

1. **Track Plugin Lists, Not Plugin Data**
   - ✅ Track: `plugins.json` (which plugins enabled)
   - ❌ Don't track: `plugins/calendar/data.json` (user's calendar events)

2. **Share Templates, Not Workspace State**
   - ✅ Track: `templates/` (note templates)
   - ❌ Don't track: `workspace.json` (open tabs, pane layout)

3. **Standardize Defaults, Allow Personalization**
   - ✅ Track: `core-plugins.json` (team-recommended core plugins)
   - ❌ Don't track: `appearance.json` (user's theme/font)

4. **Use Environment-Agnostic Paths**
   - Avoid absolute paths in tracked configs
   - Use vault-relative paths where possible
   - Document external dependencies (fonts, system tools)

---

## Decision Rationale

### Why Personal Vault for Project-AI?

**Context Analysis:**
- **Documentation Ownership**: Project docs are code-adjacent (README, architecture docs)
- **Primary Workflow**: Developers use Obsidian as enhanced note-taking, not primary IDE
- **Team Size**: Variable contributor count with different documentation preferences
- **Vault Scope**: Project documentation, not enterprise knowledge base

**Reasoning:**
1. **Low Collaboration Friction**: Developers want documentation workflow freedom
2. **Vault Diversity**: Some use Obsidian, others use VSCode, Notion, etc.
3. **Content > Configuration**: Focus on tracking markdown content, not tooling
4. **Onboarding Simplicity**: New contributors don't need Obsidian-specific setup

**Conclusion:**
Excluding `.obsidian/` entirely aligns with Project-AI's documentation-as-code philosophy while avoiding tooling lock-in.

---

## Team Vault Adoption Checklist

If migrating to team vault configuration:

- [ ] **Audit Current `.obsidian/` Contents**
  - Identify what's actually valuable to share
  - Remove machine-specific paths
  - Clean out cache/workspace state

- [ ] **Update `.gitignore`** (use `.gitignore.team-vault` as base)
  - Selectively track plugin manifests
  - Exclude all personal state
  - Add negative patterns for templates/snippets

- [ ] **Document Team Standards**
  - Required plugins for full documentation experience
  - Template usage guidelines
  - CSS snippet purposes and maintenance

- [ ] **Test Across Environments**
  - Clone repo on clean machine
  - Verify plugins install correctly
  - Confirm no broken paths

- [ ] **Establish Update Protocol**
  - Who can modify shared configs?
  - PR review for plugin additions?
  - Version pinning for critical plugins?

---

## File Inventory: .obsidian/ Contents

### Always Exclude (Personal)
- `workspace.json` - Current open tabs, pane layout, sidebar state
- `workspace-mobile.json` - Mobile app layout
- `hotkeys.json` - User keybindings
- `appearance.json` - Theme, font, accent color
- `cache/` - Search indices, metadata cache
- `plugins/*/data.json` - Plugin-specific user data

### Consider Tracking (Team Vault)
- `plugins.json` - List of enabled community plugins
- `community-plugins.json` - Community plugin registry/versions
- `core-plugins.json` - Core plugin toggles
- `templates/` - Note templates
- `snippets/` - CSS customizations
- `graph.json` - Graph view defaults (with caution)

### Rarely Track (High Conflict Risk)
- `app.json` - App settings (often includes paths)
- `types.json` - Property types (may include user examples)
- `bookmarks.json` - User's bookmarked notes

---

## Best Practices

### For Personal Vaults
1. **Document Dependencies**: If vault uses specific plugins, list them in README
2. **Export Templates**: Share critical templates as standalone `.md` files
3. **No Vault Lock-In**: Ensure documentation is readable without Obsidian

### For Team Vaults
1. **Pin Plugin Versions**: Use `versions` field in manifests to prevent breaking updates
2. **Code Review Configs**: Treat `.obsidian/` changes like infrastructure-as-code
3. **Provide Fallbacks**: Document non-Obsidian workflows (VSCode, GitHub web editor)
4. **Regular Audits**: Quarterly review of tracked configs to prune cruft

---

## Migration Path: Personal → Team Vault

### Phase 1: Audit (Week 1)
```powershell
# Analyze current .obsidian/ contents
Get-ChildItem .obsidian -Recurse | Select-Object FullName, Length

# Identify valuable configs
# - Which plugins enhance documentation?
# - Are templates used across team?
# - Any critical CSS snippets?
```

### Phase 2: Prepare (Week 2)
```powershell
# Clean vault
Remove-Item .obsidian/cache -Recurse -Force
Remove-Item .obsidian/workspace*.json

# Copy .gitignore.team-vault to .gitignore
Copy-Item .gitignore.team-vault .gitignore

# Test selective tracking
git status  # Verify only desired files shown
```

### Phase 3: Deploy (Week 3)
```powershell
# Add tracked configs
git add .obsidian/plugins.json
git add .obsidian/community-plugins.json
git add .obsidian/templates/

# Commit with documentation
git commit -m "feat: migrate to team vault configuration

Track shared plugin configs and templates.
Personal settings remain local.

See VAULT_GIT_STRATEGY.md for details."
```

### Phase 4: Validate (Week 4)
- Test on clean clone
- Verify plugin installation
- Confirm no broken workflows
- Gather team feedback

---

## Troubleshooting

### .obsidian/ Still Showing in Git Status

**Cause:** Files were tracked before `.gitignore` update

**Fix:**
```powershell
git rm -r --cached .obsidian/
git commit -m "chore: untrack .obsidian/"
```

### Plugin Settings Lost After Pull

**Cause:** Plugin data files are excluded (team vault)

**Expected:** Plugin-specific user data should remain local  
**Verify:** Check `.obsidian/plugins/*/data.json` in `.gitignore`

### Merge Conflicts in workspace.json

**Cause:** `workspace.json` is being tracked (configuration error)

**Fix:**
```powershell
# Add to .gitignore
echo ".obsidian/workspace*.json" >> .gitignore

# Remove from tracking
git rm --cached .obsidian/workspace.json
```

---

## Related Documentation

- **Obsidian Sync Docs**: [docs/OBSIDIAN_INTEGRATION.md](./docs/OBSIDIAN_INTEGRATION.md) (if exists)
- **Project Documentation Standards**: [CONTRIBUTING.md](./CONTRIBUTING.md)
- **Git Workflow**: [.github/CONTRIBUTING.md](./.github/CONTRIBUTING.md)

---

## Revision History

| Version | Date       | Changes                          | Author    |
|---------|------------|----------------------------------|-----------|
| 1.0     | 2025-01-20 | Initial personal vault strategy  | AGENT-010 |

---

## Appendix A: Plugin Recommendations

For developers using Obsidian with Project-AI:

### Recommended Plugins
- **Dataview**: Query markdown as database (useful for docs/examples)
- **Templater**: Advanced templating for documentation
- **Linter**: Enforce markdown standards
- **Git**: In-vault git operations (mobile sync)

### Configuration Tips
```json
// .obsidian/plugins.json (not tracked in personal vault)
{
  "dataview": true,
  "templater-obsidian": true,
  "obsidian-linter": true,
  "obsidian-git": true
}
```

Install via Obsidian Settings > Community Plugins.

---

## Appendix B: Vault Structure Best Practices

Recommended structure for Project-AI documentation vault:

```
vault-root/
├── README.md              # Vault index
├── architecture/          # System architecture docs
├── development/           # Developer guides
├── operations/            # Deployment, monitoring
├── templates/             # Note templates (shareable)
│   ├── ADR.md            # Architecture Decision Record
│   ├── Bug-Report.md
│   └── Feature-Spec.md
└── .obsidian/            # Excluded from git (personal vault)
```

---

**END OF DOCUMENT**
