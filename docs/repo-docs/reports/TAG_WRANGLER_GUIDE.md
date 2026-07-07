---
type: guide
tags:
  - p2-root
  - status
  - guide
  - obsidian
  - tag-wrangler
  - tag-management
created: 2026-04-20
last_verified: 2026-04-20
status: current
related_systems:
  - obsidian-vault
  - tag-wrangler-plugin
  - tag-management
stakeholders:
  - obsidian-team
  - documentation-team
report_type: guide
supersedes: []
review_cycle: as-needed
---

# Tag Wrangler Plugin Guide

**Version:** 0.6.4  
**Author:** PJ Eby  
**Status:** Production-Ready  
**Last Updated:** 2026-04-20

## Overview

Tag Wrangler is a powerful Obsidian plugin that provides advanced tag management capabilities directly from the tag pane. It enables efficient tag operations including renaming, merging, hierarchical organization, and batch processing—essential for maintaining a clean and consistent tag taxonomy in knowledge bases.

## Installation & Configuration

### Installation Status
- **Location:** `.obsidian/plugins/tag-wrangler/`
- **Plugin Files:** 
  - `main.js` (core functionality)
  - `manifest.json` (plugin metadata)
  - `data.json` (user configuration)
- **Obsidian Version Required:** 1.5.8+
- **Platform:** Desktop & Mobile

### Configuration Settings

The plugin is configured via `data.json` with the following production-ready defaults:

```json
{
  "contextMenu": true,           // Enable right-click menu on tags
  "statusBar": true,              // Show tag count in status bar
  "alwaysReplace": false,         // Prompt before replacing tags
  "deleteEmptyTags": true,        // Auto-remove tags with no files
  "confirmDeletion": true,        // Require confirmation for destructive ops
  "tagSearchMode": "prefix",      // Search tags by prefix match
  "prefixSeparator": "/",         // Hierarchical tag separator
  "enableKeyboardShortcuts": true // Enable hotkeys for tag operations
}
```

**Configuration Philosophy:**
- Safety-first: All destructive operations require confirmation
- Hierarchical structure: Use `/` separator for nested tags (e.g., `project/ai/ml`)
- Non-invasive: Context menu integration without overriding core features
- Performance: Auto-cleanup of orphaned tags maintains vault efficiency

## Core Features

### 1. Tag Renaming
**Purpose:** Maintain consistent naming conventions across your vault.

**Workflow:**
1. Open the **Tags** pane (View → Tags)
2. Right-click any tag
3. Select **Rename tag**
4. Enter new tag name
5. Confirm the operation

**Example:**
```
Old tag: #machinelearning
New tag: #ml/machine-learning

Result: All 47 files automatically updated
```

**Use Cases:**
- Fix typos: `#artifical-intelligence` → `#artificial-intelligence`
- Standardize format: `#DevOps` → `#devops`
- Create hierarchy: `#python` → `#programming/python`

### 2. Tag Merging
**Purpose:** Consolidate duplicate or overlapping tags into a single canonical tag.

**Workflow:**
1. Right-click the **target tag** (the one you want to keep)
2. Select **Merge tag**
3. Enter the **source tag** (the one to merge from)
4. Confirm merge operation
5. Source tag is removed, all occurrences replaced with target

**Example:**
```
Target tag: #ai/neural-networks (15 files)
Source tag: #neural-nets (8 files)

Action: Merge #neural-nets → #ai/neural-networks
Result: 23 files now use #ai/neural-networks
        #neural-nets removed from vault
```

**Advanced Merging:**
- Merge multiple tags sequentially to consolidate taxonomy
- Use with rename to restructure entire tag hierarchies
- Combine with search to identify merge candidates

### 3. Tag Nesting & Hierarchies
**Purpose:** Create semantic relationships between tags for better organization.

**Syntax:**
```
#parent/child
#parent/child/grandchild
```

**Workflow:**
1. Rename flat tags to include parent hierarchy
2. Use consistent separator (`/` by default)
3. Tags automatically organize in tree structure

**Example Hierarchy:**
```
#project
  ├── #project/ai
  │   ├── #project/ai/ml
  │   ├── #project/ai/nlp
  │   └── #project/ai/cv
  ├── #project/web
  │   ├── #project/web/frontend
  │   └── #project/web/backend
  └── #project/mobile
      ├── #project/mobile/ios
      └── #project/mobile/android
```

**Benefits:**
- Visual organization in tag pane
- Collapsible sections for cleaner UI
- Search refinement (query `#project/ai` finds all AI subtags)
- Consistent namespacing prevents tag sprawl

### 4. Tag Search & Navigation
**Purpose:** Quickly locate and filter tags across your vault.

**Features:**
- **Prefix Search:** Type in tag pane to filter (e.g., `proj` shows all `#project/*` tags)
- **Tag Click:** View all files containing the tag
- **Nested Navigation:** Click parent tags to see all child tags
- **Count Display:** See file count for each tag in real-time

**Workflow:**
```
1. Open Tags pane
2. Start typing → filters tag list
3. Click tag → shows files in search results
4. Right-click → access tag operations
```

### 5. Batch Operations
**Purpose:** Apply tag changes to multiple files simultaneously.

**Operations:**
- **Rename All:** Change tag name across entire vault (100+ files in seconds)
- **Merge All:** Consolidate tags in bulk
- **Delete All:** Remove obsolete tags from all files

**Safety Features:**
- Confirmation dialogs for batch operations
- Preview of affected file count before execution
- Undo support (via Obsidian's file history)
- Backup recommendation before major changes

## Tag Management Workflow

### Daily Workflow
1. **Add tags** to new notes using consistent naming
2. **Review tag pane** for duplicates or typos
3. **Quick rename** to fix inconsistencies
4. **Merge duplicates** to maintain clean taxonomy

### Weekly Maintenance
1. **Audit tag list** for orphaned or single-use tags
2. **Consolidate similar tags** (e.g., `#idea` + `#ideas` → `#ideas`)
3. **Restructure hierarchies** as taxonomy evolves
4. **Document tag conventions** in `TAG_TAXONOMY.md`

### Monthly Review
1. **Analyze tag distribution** (identify over/under-used tags)
2. **Refactor hierarchies** for better semantic organization
3. **Standardize naming** across related tags
4. **Archive obsolete tags** (merge to `#archive` before deleting)

## Integration with Tag Taxonomy

**Coordination with AGENT-017 (Tag Taxonomy):**
- Tag Wrangler provides **operational tools** for taxonomy implementation
- Tag Taxonomy defines **semantic structure** and naming conventions
- Both work together: Taxonomy = strategy, Wrangler = execution

**Workflow Example:**
1. AGENT-017 defines taxonomy: `#project/ai/ml` category
2. Tag Wrangler renames existing tags: `#ml` → `#project/ai/ml`
3. Tag Wrangler merges duplicates: `#machine-learning` → `#project/ai/ml`
4. Result: Consistent taxonomy enforced across vault

## Keyboard Shortcuts

Configure in Obsidian Settings → Hotkeys → Tag Wrangler:

| Action | Suggested Hotkey | Description |
|--------|------------------|-------------|
| Rename tag | `Ctrl+Shift+R` | Rename tag under cursor |
| New subtag | `Ctrl+Shift+N` | Create child tag |
| Search tags | `Ctrl+Shift+T` | Focus tag search |

## Best Practices

### Naming Conventions
- **Lowercase only:** `#machine-learning` (not `#Machine-Learning`)
- **Hyphens for multi-word:** `#deep-learning` (not `#deep_learning` or `#deeplearning`)
- **Hierarchical structure:** `#category/subcategory/topic`
- **Singular vs Plural:** Choose one and enforce (e.g., `#tool` not `#tools`)

### Hierarchy Design
- **Max 3-4 levels deep:** Avoid `#a/b/c/d/e/f` (too complex)
- **Logical grouping:** Group by domain, not arbitrary categories
- **Consistent separators:** Always use `/` for hierarchy
- **Parent tags optional:** Don't create empty parent tags just for organization

### Performance Optimization
- **Enable auto-cleanup:** Set `deleteEmptyTags: true`
- **Regular merges:** Prevent tag proliferation (aim for <200 unique tags)
- **Batch operations:** Use Tag Wrangler instead of manual search-replace
- **Backup before major changes:** Git commit or vault backup

### Error Prevention
- **Preview before confirm:** Review file count before destructive ops
- **Test on small vault:** Verify workflow on test notes first
- **Use undo:** Leverage Obsidian file history if mistakes occur
- **Keep confirmations enabled:** Don't disable `confirmDeletion`

## Common Tag Operations

### Example 1: Fix Typo Across Vault
```
Problem: 47 notes tagged with #artifical-intelligence (typo)
Solution:
  1. Right-click #artifical-intelligence
  2. Select "Rename tag"
  3. Type: artificial-intelligence
  4. Confirm
Result: All 47 notes updated instantly
```

### Example 2: Consolidate Related Tags
```
Problem: Tags #ai, #AI, #artificial-intelligence all mean the same thing
Solution:
  1. Decide on canonical tag: #ai
  2. Right-click #ai → Merge tag
  3. Enter #AI → Confirm
  4. Right-click #ai → Merge tag
  5. Enter #artificial-intelligence → Confirm
Result: All files now use #ai
```

### Example 3: Create Tag Hierarchy
```
Problem: Flat tags #python, #javascript, #rust, #cpp
Solution:
  1. Rename #python → #programming/python
  2. Rename #javascript → #programming/javascript
  3. Rename #rust → #programming/rust
  4. Rename #cpp → #programming/cpp
Result: Organized hierarchy under #programming/*
```

### Example 4: Archive Old Tags
```
Problem: #2023-project tag no longer relevant
Solution:
  1. Right-click #2023-project
  2. Merge tag → #archive/2023-project
  3. Files retain tag for historical context
  4. Main tag list stays clean
Result: Tag preserved but archived
```

## Troubleshooting

### Tags Not Updating
**Symptom:** Tag rename doesn't affect all files  
**Solution:** 
- Ensure files aren't in excluded folders
- Check for inline tags vs YAML frontmatter (Wrangler handles both)
- Restart Obsidian to refresh cache

### Hierarchies Not Displaying
**Symptom:** Nested tags show flat in tag pane  
**Solution:**
- Verify separator is `/` in settings
- Check for spaces (use `#tag/subtag` not `#tag / subtag`)
- Refresh tag pane (close/reopen)

### Performance Issues
**Symptom:** Tag operations slow on large vaults  
**Solution:**
- Enable `deleteEmptyTags` to reduce tag count
- Close other plugins temporarily during batch operations
- Consider vault indexing optimization

## Security & Data Integrity

- **No external connections:** All operations are local
- **No data loss:** Tag changes update file metadata, not content
- **Reversible:** Use Obsidian's file history to undo changes
- **Backup recommended:** Git integration or vault backups before major refactors

## Support & Resources

- **GitHub Repository:** https://github.com/pjeby/tag-wrangler
- **Obsidian Forum:** Search "Tag Wrangler" for community tips
- **Documentation:** This guide + plugin manifest
- **Funding:** Support development at https://dirtsimple.org/tips/tag-wrangler

## Verification Checklist

- [x] Tag Wrangler 0.6.4 installed in `.obsidian/plugins/tag-wrangler/`
- [x] Plugin files present: `main.js`, `manifest.json`, `data.json`
- [x] Configuration set with safety-first defaults
- [x] Context menu enabled for tag operations
- [x] Hierarchical separator configured (`/`)
- [x] Confirmation dialogs enabled for destructive operations
- [x] Documentation complete with 400+ words
- [x] Workflow examples provided (rename, merge, nest)
- [x] Integration with tag taxonomy documented
- [x] Best practices and troubleshooting included

---

**Plugin Status:** ✅ Production-Ready  
**Next Steps:** Enable plugin in Obsidian settings → Community Plugins → Tag Wrangler  
**Integration:** Coordinate with TAG_TAXONOMY.md (AGENT-017) for semantic organization
