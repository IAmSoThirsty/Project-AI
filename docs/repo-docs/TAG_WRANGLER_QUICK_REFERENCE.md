# Tag Wrangler Quick Reference

## Essential Operations

### Rename a Tag
1. Open Tags pane (View → Tags)
2. Right-click tag → **Rename tag**
3. Enter new name → Confirm

### Merge Tags
1. Right-click **target tag** (keep this one)
2. Select **Merge tag**
3. Enter **source tag** (remove this one)
4. Confirm merge

### Create Tag Hierarchy
- Rename tag to include parent: `#tag` → `#parent/tag`
- Use `/` as separator
- Tags auto-organize in tree structure

### Delete Tag
1. Right-click tag → **Delete tag**
2. Confirm (removes from all files)

### Search Tags
- Type in Tags pane to filter
- Click tag to see all files
- Prefix search enabled

## Configuration Quick Access

**Location:** `.obsidian/plugins/tag-wrangler/data.json`

**Key Settings:**
- `contextMenu: true` - Right-click operations
- `deleteEmptyTags: true` - Auto-cleanup
- `confirmDeletion: true` - Safety confirmations
- `prefixSeparator: "/"` - Hierarchy separator

## Keyboard Shortcuts (Recommended)

Configure in Settings → Hotkeys:
- `Ctrl+Shift+R` - Rename tag
- `Ctrl+Shift+N` - New subtag
- `Ctrl+Shift+T` - Search tags

## Common Workflows

### Fix Typo
```
#artifical-intelligence → Rename → #artificial-intelligence
```

### Consolidate Duplicates
```
#ai, #AI, #artificial-intelligence
→ Merge all into #ai
```

### Build Hierarchy
```
#python, #javascript, #rust
→ Rename to #programming/python, #programming/javascript, #programming/rust
```

### Archive Old Tags
```
#2023-project → Merge → #archive/2023-project
```

## Best Practices

✅ **DO:**
- Use lowercase for consistency
- Confirm before destructive operations
- Backup before major refactors
- Review tag pane regularly

❌ **DON'T:**
- Disable confirmations
- Create hierarchies >4 levels deep
- Mix separators (always use `/`)
- Forget to test on small vault first

## Integration

**Works with:**
- Dataview (query hierarchical tags)
- Graph View (visualize tag relationships)
- Search (find files by nested tags)
- TAG_TAXONOMY.md (semantic organization)

**Complements:**
- AGENT-017 Tag Taxonomy (defines structure)
- Tag Wrangler (implements structure)

---

**Full Documentation:** TAG_WRANGLER_GUIDE.md  
**Plugin Version:** 0.6.4  
**Status:** Production-Ready
