# Developer Guide: Using Wiki Links in Project-AI Documentation

## Quick Reference for Obsidian Navigation

### 🔗 What Are Wiki Links?

Wiki links are Obsidian's format for creating connections between files:
```markdown
[[path/to/file.md]]              # Basic link
[[path/to/file.md|Display Name]] # Link with custom text
[[path/to/file.md#section]]      # Link to specific section
```

---

## 🚀 Quick Start

### Opening Documentation in Obsidian

1. **Install Obsidian**: Download from https://obsidian.md
2. **Open Vault**: File → Open folder → Navigate to `T:\Project-AI-main`
3. **Enable Graph View**: Click graph icon in left sidebar
4. **Start Exploring**: Click any `[[link]]` to navigate

---

## 📚 Navigation Patterns

### Pattern 1: Feature Exploration
**Start**: relationships/gui/00_MASTER_INDEX.md
1. Browse component list
2. Click component link (e.g., `[[src/app/gui/leather_book_dashboard.py]]`)
3. View source code in Obsidian
4. Check backlinks panel (right sidebar) to see all docs that reference it

### Pattern 2: Code-to-Context
**Start**: src/app/gui/persona_panel.py
1. Read docstring backlinks (top of file)
2. Click link to relationship map
3. Explore architecture and design decisions
4. Navigate to related components via cross-references

### Pattern 3: Workflow Discovery
**Start**: relationships/temporal/README.md
1. Browse workflow index
2. Click workflow detail link
3. Click component link to see implementation
4. Use backlinks to find related documentation

---

## 🎯 Key Features

### 1. Graph View
- **Access**: Click graph icon or press `Ctrl+G`
- **Features**:
  - See all file connections visually
  - Identify clusters (GUI, Temporal, etc.)
  - Find orphaned files (no connections)
  - Zoom and pan to explore

### 2. Backlinks Panel
- **Access**: Right sidebar → Backlinks tab
- **Shows**:
  - Files that link to current file
  - Unlinked mentions (component names without links)
  - Context for each link

### 3. Quick Switcher
- **Access**: Press `Ctrl+O`
- **Usage**:
  - Type filename to jump directly
  - Type `[[` in editor for autocomplete
  - Fuzzy search (e.g., "dash hand" finds "dashboard_handlers")

### 4. Local Graph
- **Access**: Right sidebar → Outgoing links tab
- **Shows**:
  - Immediate connections from current file
  - Files this file links to
  - Files that link to this file

---

## 📁 Link Categories in Project-AI

### 1. Source Code References
**Location**: Bottom of documentation files  
**Format**: 
```markdown
## 🔗 Source Code References

- [[src/app/gui/dashboard_handlers.py]] - Implementation file
```
**Use**: Jump from docs to implementation

### 2. Backlinks in Code
**Location**: Top of Python files (comments)  
**Format**:
```python
# 📚 Documentation Links:
# - [[relationships/gui/03_HANDLER_RELATIONSHIPS.md]]
# - [[source-docs/gui/dashboard_handlers.md]]
#
```
**Use**: Find docs from source code

### 3. Inline Component Links
**Location**: Throughout documentation  
**Format**:
```markdown
**LeatherBookDashboard** [[src/app/gui/leather_book_dashboard.py]]
```
**Use**: Quick reference from mentions

### 4. Cross-Document Links
**Location**: "Related Documentation" sections  
**Format**:
```markdown
### Cross-References

- [[relationships/gui/01_DASHBOARD_RELATIONSHIPS.md|Dashboard Relationships]]
```
**Use**: Navigate between related docs

---

## 🛠️ Working with Links

### Creating New Links
```markdown
# Method 1: Type manually
[[src/app/gui/new_panel.py]]

# Method 2: Use autocomplete
[[                          # Press Ctrl+Space for suggestions

# Method 3: With display name
[[src/app/gui/new_panel.py|New Panel Component]]
```

### Updating Broken Links
Obsidian auto-updates links when files are moved, but if manual updates needed:
1. Search for old path: `Ctrl+Shift+F`
2. Replace with new path
3. Verify in graph view

### Adding Links to New Documentation
1. **Source Code References**: Add `## 🔗 Source Code References` section
2. **Backlinks**: Add comment block to source file
3. **Component Links**: Link first mention of each component
4. **Cross-Refs**: Add `## 📚 Related Documentation` section

---

## 🎨 Link Statistics by System

### GUI Documentation
- **Relationship Maps**: 7 files, 76 links
- **Source Docs**: 6 files, 62 links  
- **Source Code**: 9 files, 18 backlinks
- **Total**: 156 links

### Temporal Documentation
- **Relationship Maps**: 5 files, 62 links
- **Source Docs**: 3 files, 23 links
- **Source Code**: 7 files, 13 backlinks
- **Total**: 98 links

### Component Coverage
- **GUI Components**: 35 linked
- **Temporal Components**: 48 linked
- **Total**: 83 unique components

---

## 🔍 Finding Information

### "Where is this component implemented?"
1. Open any documentation file
2. Search for component name (Ctrl+F)
3. Click inline link next to component name
4. Source file opens with implementation

### "What documentation exists for this code?"
1. Open source file
2. Check docstring backlinks (top of file)
3. Click link to documentation
4. Explore relationship maps and source docs

### "What components interact with this one?"
1. Open documentation for component
2. View graph view (Ctrl+G)
3. See connected files
4. Navigate to related components

### "What are all the workflows in the system?"
1. Open `relationships/temporal/README.md`
2. Browse workflow index
3. Click links to detailed workflow docs
4. Use cross-references to explore

---

## 📊 Obsidian Tips

### Keyboard Shortcuts
- `Ctrl+O` - Quick switcher (open file)
- `Ctrl+G` - Toggle graph view
- `Ctrl+F` - Search current file
- `Ctrl+Shift+F` - Search all files
- `Ctrl+E` - Toggle edit/preview mode
- `Alt+Left` - Navigate back
- `Alt+Right` - Navigate forward

### Graph View Controls
- **Zoom**: Mouse wheel or +/- keys
- **Pan**: Click and drag
- **Filter**: Click filter icon to show/hide file types
- **Color Groups**: Use Obsidian settings to color by folder

### Search Tips
- Search by tag: `tag:#documentation`
- Search by path: `path:relationships/gui`
- Search by content: Any text query
- Combine: `tag:#gui path:relationships`

---

## 🚀 Advanced Usage

### Creating Custom Views
Use Obsidian's graph view filters to create custom perspectives:

**GUI Components Only**:
```
path:src/app/gui OR path:relationships/gui OR path:source-docs/gui
```

**Temporal System Only**:
```
path:temporal OR path:relationships/temporal OR path:source-docs/temporal
```

**Documentation Only** (no code):
```
path:relationships OR path:source-docs
```

### Building Navigation Maps
Create custom index files with curated links:
```markdown
# My Custom Navigation

## GUI Development
- [[relationships/gui/00_MASTER_INDEX.md|GUI Overview]]
- [[source-docs/gui/leather_book_dashboard.md|Dashboard Docs]]

## Temporal Workflows
- [[relationships/temporal/README.md|Temporal Overview]]
- [[source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md|All Workflows]]
```

---

## 📝 Maintenance Guidelines

### When Adding New Files
1. Add source code references section
2. Add backlinks to source file
3. Link to relationship maps
4. Update master index

### When Moving Files
1. Obsidian auto-updates wiki links
2. Verify in graph view
3. Check backlinks panel
4. Update any manual cross-references

### When Renaming Components
1. Update inline component links
2. Update component reference map
3. Run link validation
4. Update relationship maps

---

## 🎯 Common Tasks

### Task: "I want to understand the GUI dashboard"
**Path**:
1. Open `relationships/gui/01_DASHBOARD_RELATIONSHIPS.md`
2. Read architecture overview
3. Click `[[src/app/gui/leather_book_dashboard.py]]`
4. Review implementation
5. Check backlinks for related docs

### Task: "I want to see all Temporal workflows"
**Path**:
1. Open `relationships/temporal/01_WORKFLOW_CHAINS.md`
2. Browse workflow list
3. Click specific workflow links
4. View source code via inline links
5. Explore activities via cross-references

### Task: "I want to trace a signal chain"
**Path**:
1. Open `relationships/gui/02_PANEL_RELATIONSHIPS.md`
2. Find signal diagram
3. Click component links to see implementation
4. Use backlinks to find usage examples
5. Follow cross-refs to related handlers

---

## 📞 Support

### Issues with Links
- **Broken links**: Most are expected (future documentation)
- **See**: AGENT-074-FINAL-MISSION-REPORT.md for broken link analysis
- **Report**: Create GitHub issue with label `documentation`

### Questions
- **Documentation**: See AGENT-074-MISSION-COMPLETE.md
- **Obsidian Help**: https://help.obsidian.md
- **Wiki Links**: https://help.obsidian.md/Linking+notes+and+files/Internal+links

---

**Created by**: AGENT-074  
**Date**: 2026-04-20  
**Version**: 1.0

**Enjoy exploring the newly linked documentation!** 🚀
