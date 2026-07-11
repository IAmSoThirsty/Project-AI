# Plugin Reference Guide

**Obsidian Plugins for Project-AI Vault** 🔌

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 10 minutes
**Audience:** All vault users
**Prerequisites:** Obsidian installed

---

## Table of Contents

1. [Plugin Overview](#plugin-overview)
2. [Core Plugins](#core-plugins)
3. [Community Plugins](#community-plugins)
4. [Plugin Configuration](#plugin-configuration)
5. [Use Cases](#use-cases)
6. [Troubleshooting](#troubleshooting)

---

## Plugin Overview

Project-AI Vault uses **2 core plugins** and **3 essential community plugins** to enable advanced knowledge management.

### Installed Plugins

| Plugin | Type | Purpose | Required |
|--------|------|---------|----------|
| **Dataview** | Community | SQL-like queries, dynamic lists | ✅ Critical |
| **Templater** | Community | Advanced template engine | ✅ Critical |
| **Excalidraw** | Community | Diagramming and visual notes | ⚠️ Recommended |
| **File Explorer** | Core | File browsing and management | ✅ Critical |
| **Search** | Core | Full-text search across vault | ✅ Critical |

### Plugin Dependencies

```
Vault Functionality Depends On:
├─ Dataview → Dynamic queries, dashboards, analytics
├─ Templater → Document templates, metadata generation
├─ File Explorer → Navigation and organization
├─ Search → Content discovery
└─ Excalidraw → Architecture diagrams (optional)
```

---

## Core Plugins

**Built into Obsidian** - Always available, cannot be uninstalled

### 1. File Explorer

**Purpose:** Browse and manage vault files and folders

**Features:**
- ✅ Tree view of all files
- ✅ Drag-and-drop file organization
- ✅ Right-click context menus
- ✅ Star important files
- ✅ Create folders and files
- ✅ Rename and delete

**Configuration:**

```
Settings → File Explorer
├─ Reveal active file: Auto-scroll to current file
├─ Sort order: Name, modified date, created date
├─ Folder collapse: Remember collapse state
└─ New file location: Same folder / Root / Folder path
```

**Shortcuts:**

```
Ctrl+Click file    → Open in new pane
Right-click file   → Context menu (rename, delete, etc.)
Drag file          → Move to new folder
Star file          → Bookmark for quick access
```

**Use Cases:**

```
Daily Workflow:
1. Browse by folder structure
2. Star frequently accessed files
3. Drag-and-drop to reorganize
4. Right-click to rename/delete
```

### 2. Search

**Purpose:** Find content across entire vault

**Features:**
- ✅ Full-text search
- ✅ Boolean operators (AND, OR, NOT)
- ✅ Regular expressions
- ✅ File property filters
- ✅ Context display
- ✅ Match case / whole word

**Configuration:**

```
Settings → Search
├─ Collapse results: Show only file names vs full context
├─ Context length: Lines of context around matches
├─ Ignore case: Case-sensitive search toggle
└─ Show existing only: Hide search if no matches
```

**Search Operators:**

```
Plain Text:
  "exact phrase"       → Exact match
  word1 word2          → Both words (anywhere)
  word1 OR word2       → Either word
  word1 -word2         → word1 but NOT word2

File Properties:
  file:README          → Filename contains "README"
  path:source-docs/    → In specific folder
  tag:#security        → Has specific tag

Advanced:
  /regex/              → Regular expression search
  match-case:yes       → Case sensitive
```

**Use Cases:**

```
Find Code:
  /def \w+\(/          → Python function definitions

Find Security Docs:
  tag:#security path:repo-docs/

Find Recent Updates:
  modified:>2026-04-15
```

---

## Community Plugins

### 1. Dataview ⭐ CRITICAL

**Purpose:** Query vault like a database, create dynamic views

**Why Critical:**
- All dashboard queries depend on it
- Enables advanced search and filtering
- Powers vault health monitoring
- Creates dynamic indexes and MOCs

**Installation:**

```
Settings → Community Plugins
→ Browse
→ Search "Dataview"
→ Install
→ Enable
```

**Configuration:**

```
Settings → Dataview
├─ Enable JavaScript Queries: ON (required)
├─ Enable Inline Queries: ON
├─ Enable Inline JavaScript: ON
└─ Refresh Interval: 2500ms
```

**Syntax Types:**

**1. DQL (Dataview Query Language)**

```dataview
TABLE status, priority, updated_date
FROM #architecture
WHERE status = "active"
SORT updated_date DESC
LIMIT 10
```

**2. JavaScript API**

```dataviewjs
dv.table(
  ["Document", "Status", "Updated"],
  dv.pages("#architecture")
    .where(p => p.status === "active")
    .sort(p => p.updated_date, 'desc')
    .limit(10)
    .map(p => [p.file.link, p.status, p.updated_date])
);
```

**Common Queries:**

```dataviewjs
// Recent updates (last 7 days)
const sevenDays = new Date();
sevenDays.setDate(sevenDays.getDate() - 7);

dv.list(
  dv.pages()
    .where(p => p.updated_date >= sevenDays)
    .sort(p => p.updated_date, 'desc')
    .file.link
);
```

```dataviewjs
// Documents by status
dv.table(
  ["Status", "Count"],
  dv.pages()
    .groupBy(p => p.status || "Unknown")
    .map(g => [g.key, g.rows.length])
    .sort(g => g[1], 'desc')
);
```

```dataviewjs
// Missing required metadata
const required = ['type', 'area', 'status', 'audience'];
dv.list(
  dv.pages()
    .where(p => required.some(f => !p[f]))
    .file.link
);
```

**Performance:**

```
Optimization Tips:
├─ Limit scope: dv.pages("#tag") not dv.pages()
├─ Add .limit(N) to large results
├─ Cache heavy queries in dashboard notes
└─ Use WHERE clauses early in chain
```

**See Also:** [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md) for 25+ examples

### 2. Templater ⭐ CRITICAL

**Purpose:** Advanced template system with dynamic content

**Why Critical:**
- All document templates depend on it
- Enables automatic metadata generation
- Reduces documentation time by 80%
- Ensures consistency across vault

**Installation:**

```
Settings → Community Plugins
→ Browse
→ Search "Templater"
→ Install
→ Enable
```

**Configuration:**

```
Settings → Templater
├─ Template folder location: templates/
├─ Syntax highlighting: ON
├─ Automatic jump to cursor: ON
├─ Trigger on file creation: OFF
└─ Enable folder templates: ON (optional)
```

**Key Features:**

**1. Dynamic Dates**

```javascript
Created: <% tp.date.now("YYYY-MM-DD") %>
Updated: <% tp.date.now("YYYY-MM-DD HH:mm") %>
Tomorrow: <% tp.date.tomorrow("YYYY-MM-DD") %>
```

**2. User Prompts**

```javascript
Author: <% tp.system.prompt("Your name") %>
Priority: <% tp.system.suggester(
  ["critical", "high", "medium", "low"],
  ["critical", "high", "medium", "low"]
) %>
```

**3. File Properties**

```javascript
# <% tp.file.title %>
Path: <% tp.file.path(true) %>
Folder: <% tp.file.folder(true) %>
```

**4. Cursor Positions**

```javascript
## Overview
<% tp.file.cursor(1) %>  ← Jump here first

## Details
<% tp.file.cursor(2) %>  ← Then here
```

**Usage:**

```
1. Create new note (Ctrl+N)
2. Open command palette (Ctrl+P)
3. "Templater: Insert template"
4. Choose template
5. Fill prompts
6. Tab through cursor positions
```

**Custom Hotkey:**

```
Settings → Hotkeys
→ Search "Templater: Insert template"
→ Assign: Alt+E (recommended)
```

**See Also:** [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md) for full guide

### 3. Excalidraw (Optional)

**Purpose:** Create diagrams, sketches, and visual notes

**Why Recommended:**
- Architecture diagrams
- Workflow visualizations
- Concept sketches
- Annotations on images

**Installation:**

```
Settings → Community Plugins
→ Browse
→ Search "Excalidraw"
→ Install
→ Enable
```

**Configuration:**

```
Settings → Excalidraw
├─ Folder: visual-maps/ (or preferred location)
├─ Template: Use default
├─ Export format: PNG + SVG
└─ Auto-save: ON
```

**Features:**

```
Drawing Tools:
├─ Shapes: Rectangle, circle, diamond, arrow
├─ Text: Labels and annotations
├─ Freehand: Pen tool for sketches
├─ Images: Import and annotate
└─ Library: Reusable component templates
```

**Use Cases:**

```
Architecture Documentation:
1. Create new Excalidraw note
2. Draw system architecture
3. Export as PNG
4. Embed in markdown: ![[architecture.excalidraw.png]]

Workflow Diagrams:
1. Create flowchart
2. Add decision points
3. Link to related docs
4. Embed in guide
```

**Shortcuts:**

```
S → Selection tool
R → Rectangle
C → Circle
A → Arrow
T → Text
D → Draw (freehand)
Ctrl+D → Duplicate
Ctrl+Z → Undo
```

**See Also:** Visual maps in `visual-maps/` folder

---

## Plugin Configuration

### Enabling Community Plugins

**First Time Setup:**

```
1. Settings → Community Plugins
2. Click "Turn on community plugins"
3. Confirm security warning (trust vault)
4. Click "Browse"
5. Search for plugin
6. Click "Install"
7. Click "Enable"
```

**Safety:**

- Community plugins are open-source
- Reviewed by Obsidian team
- Can inspect source code
- Disable anytime

### Plugin Settings

**Access:**

```
Settings → [Plugin Name]
or
Settings → Community Plugins → Installed → [Plugin] → Gear Icon
```

**Recommended Settings:**

**Dataview:**
```yaml
Enable JavaScript Queries: ON
Enable Inline Queries: ON
Enable Inline JavaScript: ON
Refresh Interval: 2500ms
```

**Templater:**
```yaml
Template folder: templates/
Automatic jump to cursor: ON
Enable folder templates: ON
```

**Excalidraw:**
```yaml
Folder: visual-maps/
Export: PNG + SVG
Auto-save: ON
```

### Plugin Updates

**Check for Updates:**

```
Settings → Community Plugins
→ Check for updates (button)
→ Update all (or update individually)
```

**Auto-Update:**

```
Settings → Community Plugins
→ Enable: "Auto-update plugins"
```

**Frequency:** Check weekly for security updates

---

## Use Cases

### Use Case 1: Create Documentation Dashboard

**Plugins Used:** Dataview

**Steps:**

```markdown
1. Create: DOCUMENTATION_DASHBOARD.md

2. Add query:
```dataviewjs
// Recent documentation updates
const week = new Date();
week.setDate(week.getDate() - 7);

dv.table(
  ["Document", "Updated", "Author"],
  dv.pages()
    .where(p => p.area === "documentation" && p.updated_date >= week)
    .sort(p => p.updated_date, 'desc')
    .map(p => [p.file.link, p.updated_date, p.author])
);
```

3. Switch to Preview mode
4. Bookmark for daily review
```

### Use Case 2: Generate Document from Template

**Plugins Used:** Templater

**Steps:**

```
1. Ctrl+N → New note: "API_USER_LOGIN.md"
2. Alt+E → Insert template
3. Choose: "architecture-doc-integration-api"
4. Templater prompts:
   - Author: AGENT-048
   - API version: v2
   - Priority: critical
5. Fill in template sections
6. Save (Ctrl+S)
```

**Result:** Fully structured API documentation in 2 minutes

### Use Case 3: Visualize Architecture

**Plugins Used:** Excalidraw

**Steps:**

```
1. Create: SYSTEM_ARCHITECTURE.excalidraw
2. Draw components (rectangles)
3. Add arrows for data flow
4. Label connections
5. Export: SYSTEM_ARCHITECTURE.excalidraw.png
6. Embed in docs: ![[SYSTEM_ARCHITECTURE.excalidraw.png]]
```

### Use Case 4: Find All TODOs

**Plugins Used:** Search + Dataview

**Search Method:**

```
Ctrl+Shift+F
Search: TODO:
Results: All TODO comments across vault
```

**Dataview Method:**

```dataviewjs
// All documents with TODO tags
dv.table(
  ["Document", "TODOs"],
  dv.pages()
    .where(p => p.tags && p.tags.includes("todo"))
    .map(p => [p.file.link, p.tags])
);
```

### Use Case 5: Monitor Vault Health

**Plugins Used:** Dataview

**Dashboard Queries:**

```dataviewjs
// Missing metadata
const required = ['type', 'area', 'status'];
dv.list(
  dv.pages()
    .where(p => required.some(f => !p[f]))
    .file.link
);

// Stale documents (180+ days)
const sixMonths = new Date();
sixMonths.setDate(sixMonths.getDate() - 180);

dv.list(
  dv.pages()
    .where(p => p.updated_date < sixMonths)
    .file.link
);

// Orphaned documents
dv.list(
  dv.pages()
    .where(p => {
      const backlinks = dv.app.metadataCache.getBacklinksForFile(p.file);
      return backlinks.count() === 0;
    })
    .file.link
);
```

---

## Troubleshooting

### Problem: "Dataview queries not rendering"

**Symptoms:** Code blocks show instead of results

**Solutions:**

1. **Check plugin enabled**
   ```
   Settings → Community Plugins → Dataview → Enabled?
   ```

2. **Enable JavaScript**
   ```
   Settings → Dataview → Enable JavaScript Queries → ON
   ```

3. **Switch to Preview mode**
   ```
   Ctrl+E to toggle Edit/Preview
   Queries only render in Preview
   ```

4. **Check syntax**
   ```dataviewjs
   // Correct
   dv.list(dv.pages().file.link)

   // Wrong (missing dv.)
   list(pages().file.link)
   ```

5. **View console errors**
   ```
   Ctrl+Shift+I → Console tab
   See JavaScript errors
   ```

### Problem: "Template not inserting"

**Symptoms:** Nothing happens when inserting template

**Solutions:**

1. **Check Templater enabled**
   ```
   Settings → Community Plugins → Templater → Enabled?
   ```

2. **Verify template folder**
   ```
   Settings → Templater → Template folder: templates/
   Folder must exist and contain .md files
   ```

3. **Check template syntax**
   ```
   Must use: <% %>
   Not: {{ }} or << >>
   ```

4. **Use command palette**
   ```
   Ctrl+P → "Templater: Insert template"
   If this works, hotkey might be wrong
   ```

### Problem: "Plugin not appearing in settings"

**Symptoms:** Can't find plugin after installation

**Solutions:**

1. **Refresh plugin list**
   ```
   Settings → Community Plugins → Reload
   or restart Obsidian
   ```

2. **Enable community plugins**
   ```
   Settings → Community Plugins
   "Turn on community plugins" button
   ```

3. **Check installation**
   ```
   Settings → Community Plugins → Installed plugins
   Should appear in list
   ```

### Problem: "Slow performance with Dataview"

**Symptoms:** Queries take >3 seconds to run

**Solutions:**

1. **Limit query scope**
   ```dataviewjs
   // Slow
   dv.pages()

   // Fast
   dv.pages("#specific-tag")
   ```

2. **Add result limits**
   ```dataviewjs
   dv.pages().limit(50)
   ```

3. **Cache in dashboard**
   ```
   Instead of live queries everywhere,
   create one dashboard with all queries
   ```

4. **Reduce refresh rate**
   ```
   Settings → Dataview → Refresh interval: 5000ms
   ```

---

## Summary

### Critical Plugins

**Must Have:**
- ✅ Dataview - Dynamic queries and dashboards
- ✅ Templater - Document templates
- ✅ File Explorer (core) - Navigation
- ✅ Search (core) - Discovery

**Recommended:**
- ⚠️ Excalidraw - Diagrams and sketches

### Quick Setup Checklist

- [ ] Community plugins enabled
- [ ] Dataview installed and configured
- [ ] Templater installed and configured
- [ ] Template folder set: `templates/`
- [ ] Dataview JavaScript enabled
- [ ] Custom hotkeys configured
- [ ] Test queries working
- [ ] Test templates inserting

### Getting Help

**Plugin Documentation:**

- Dataview: https://blacksmithgu.github.io/obsidian-dataview/
- Templater: https://silentvoid13.github.io/Templater/
- Excalidraw: https://github.com/zsviczian/obsidian-excalidraw-plugin
- Obsidian: https://help.obsidian.md/

**In-Vault Resources:**

- [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md)
- [TEMPLATE_GUIDE.md](TEMPLATE_GUIDE.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Next Steps:**

- **Install** critical plugins today
- **Configure** settings as recommended
- **Try** 3 Dataview queries this week
- **Create** 1 document from template

---

**Document Metadata:**

```yaml
---
type: reference
area: documentation
component: vault
status: active
audience: [user, developer, contributor]
priority: high
tags: [plugins, dataview, templater, obsidian, reference, configuration]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 2700
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
