# Getting Started with Project-AI Vault

**Welcome to Your Knowledge Hub!** 🎉

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 15 minutes
**Audience:** New users, developers, documentation contributors
**Prerequisites:** None - start here!

---

## Table of Contents

1. [What is the Project-AI Vault?](#what-is-the-project-ai-vault)
2. [Why Use This Vault?](#why-use-this-vault)
3. [First-Time Setup](#first-time-setup)
4. [Quick Start: Your First 5 Minutes](#quick-start-your-first-5-minutes)
5. [Understanding the Interface](#understanding-the-interface)
6. [Common Workflows](#common-workflows)
7. [Quick Wins: Immediate Value](#quick-wins-immediate-value)
8. [Learning Path](#learning-path)
9. [Getting Help](#getting-help)

---

## What is the Project-AI Vault?

The **Project-AI Vault** is your comprehensive documentation system for the Project-AI ecosystem - a sophisticated Python desktop application with AI capabilities, ethical decision-making frameworks, and advanced user interfaces.

Think of it as:

- 📚 **Your Documentation Library** - All project knowledge in one place
- 🗺️ **Your Navigation System** - Find anything in seconds using powerful search
- 🏗️ **Your Architecture Reference** - Understand how everything fits together
- 🎓 **Your Learning Platform** - Progressive guides from beginner to expert
- 🔍 **Your Discovery Engine** - Explore connections between concepts
- 📊 **Your Knowledge Graph** - Visualize relationships between components

### What Makes This Special?

Unlike traditional documentation folders, this vault uses **Obsidian** - a powerful knowledge management tool that treats documentation as an interconnected knowledge graph. This means:

✅ **Instant Search** - Find any document, tag, or concept in milliseconds
✅ **Visual Connections** - See how components relate in an interactive graph
✅ **Smart Queries** - Ask complex questions like "Show me all security-related agent documentation updated in the last month"
✅ **Tag-Based Navigation** - Browse by topic, component, priority, or any dimension
✅ **Template System** - Create consistent documentation automatically
✅ **Future-Proof** - All documents are plain markdown files

---

## Why Use This Vault?

### For New Users

**"I just want to understand what Project-AI does"**

→ Start with `README.md` and the Quick Start workflows below. You'll be productive in 5 minutes.

### For Developers

**"I need to understand the codebase architecture"**

→ Use tag searches (`#architecture`, `#core-system`) and the dependency graph. Find any component in seconds.

### For Documentation Contributors

**"I need to add documentation for a new feature"**

→ Use templates and the metadata guide. Create consistent, discoverable docs automatically.

### For Project Maintainers

**"I need to track documentation quality and coverage"**

→ Use Dataview queries and the health dashboard. Monitor metrics in real-time.

---

## First-Time Setup

### Step 1: Install Obsidian

**Download Obsidian** (Free, no account required)

1. Visit: https://obsidian.md/download
2. Download for your OS (Windows, macOS, Linux)
3. Install and launch Obsidian

**Why Obsidian?**
- ✅ Free forever for personal use
- ✅ Works offline - no cloud required
- ✅ Plain markdown files - you own your data
- ✅ Powerful plugins and customization
- ✅ Active community and development

### Step 2: Open the Vault

**Two Methods:**

**Method A: From Obsidian**

1. Launch Obsidian
2. Click **"Open folder as vault"**
3. Navigate to `T:\Project-AI-vault\`
4. Click **"Select Folder"**

**Method B: From Windows Explorer**

1. Navigate to `T:\Project-AI-vault\`
2. Right-click in the folder
3. Select **"Open with Obsidian"** (if configured)

**What You Should See:**

```
┌─────────────────────────────────────────────────────────┐
│ Obsidian - Project-AI Vault                             │
├─────────────┬───────────────────────────┬───────────────┤
│             │                           │               │
│  File       │   Document Content        │   Graph View  │
│  Explorer   │                           │               │
│             │   # Getting Started       │     •••       │
│  📁 repo-   │                           │    •   •      │
│    docs     │   Welcome to your...      │   • • • •     │
│  📁 source- │                           │    •   •      │
│    docs     │                           │     •••       │
│  📁 templates│                          │               │
│  📄 README  │                           │               │
│             │                           │               │
└─────────────┴───────────────────────────┴───────────────┘
```

### Step 3: Trust and Configure

**On First Open:**

Obsidian will ask you to trust this vault (for plugin execution).

1. Click **"Trust author and enable plugins"**
2. Wait for plugins to load (5-10 seconds)
3. You're ready to go!

**Why Trust?**
- Enables Dataview queries for smart searches
- Enables Templater for document creation
- All plugins are open-source and audited

**If Plugins Don't Load:**

See the [Troubleshooting Guide](TROUBLESHOOTING.md#plugins-not-loading) for solutions.

---

## Quick Start: Your First 5 Minutes

Let's get you productive immediately! Follow these 5 quick wins:

### Win #1: View the Dashboard (30 seconds)

1. Press `Ctrl+O` (Windows) or `Cmd+O` (Mac)
2. Type: `dashboard`
3. Press Enter

**What You See:** A command center showing recent updates, document counts, quality metrics, and quick actions.

### Win #2: Find a Document (30 seconds)

1. Press `Ctrl+Shift+F` (Quick Search)
2. Type: `four laws`
3. Click the result

**What You Learn:** You can find anything instantly by typing any part of its name or content.

### Win #3: Explore the Graph (1 minute)

1. Press `Ctrl+G` (Open Graph View)
2. Click on any node to open that document
3. Drag nodes to explore connections
4. Use the filters on the right to show only specific tags

**What You Learn:** Everything is connected! The graph shows how components relate.

### Win #4: Use Tags to Browse (1 minute)

1. Click the **Tags** panel (right sidebar)
2. Click on `#architecture`
3. See all architecture-related documents

**Or Search by Tag:**

1. Press `Ctrl+Shift+F`
2. Type: `tag:#security`
3. See all security documents

### Win #5: Run Your First Query (2 minutes)

1. Press `Ctrl+O`
2. Type: `query library`
3. Open `DATAVIEW_QUERY_LIBRARY.md`
4. Copy any query from the examples
5. Create a new note (`Ctrl+N`)
6. Paste the query in a code block
7. Switch to Preview mode (`Ctrl+E`)

**What You Learn:** You can ask complex questions and get live results!

---

## Understanding the Interface

Let me break down what you're seeing:

### The Left Sidebar: File Explorer

```
📁 Project-AI-vault/
├─ 📄 README.md ........................... Start here!
├─ 📄 GETTING_STARTED.md ................. This document
├─ 📁 repo-docs/ ......................... Repository documentation
│  ├─ 📁 architecture/ ................... System design docs
│  ├─ 📁 developer/ ...................... Developer guides
│  ├─ 📁 security/ ....................... Security documentation
│  └─ 📁 user/ ........................... User guides
├─ 📁 source-docs/ ....................... Original source documents
│  ├─ 📁 core/ ........................... Core systems
│  ├─ 📁 gui/ ............................ UI components
│  └─ 📁 agents/ ......................... AI agents
├─ 📁 templates/ ......................... Document templates
├─ 📁 _indexes/ .......................... Navigation indexes (MOCs)
├─ 📁 schemas/ ........................... Metadata validation schemas
└─ 📁 scripts/ ........................... Automation scripts
```

**Pro Tip:** Collapse folders you don't need. Right-click → Collapse all.

### The Center Pane: Document View

This is where you read and edit documents. Two modes:

**Edit Mode** (`Ctrl+E` to toggle)
- See raw markdown syntax
- Edit text directly
- Add links with `[[Document Name]]`

**Preview Mode** (`Ctrl+E` to toggle)
- Beautiful formatted view
- Clickable links
- Live Dataview queries
- Embedded images and diagrams

### The Right Sidebar: Context & Tools

**Tabs You'll Use:**

1. **Outline** - Table of contents for current document
2. **Backlinks** - What other documents link here?
3. **Tags** - All tags in the vault (clickable)
4. **Graph View** - Visual network of connections

**How to Toggle:** Click icons or press `Ctrl+Alt+Left/Right`

### The Command Palette: Your Swiss Army Knife

Press `Ctrl+P` to open the **Command Palette** - your most powerful tool!

Type any command:
- `"graph"` → Open graph view
- `"template"` → Insert a template
- `"search"` → Advanced search
- `"export"` → Export to PDF
- `"theme"` → Change appearance

**Pro Tip:** You can run ANY Obsidian action from here. Don't memorize shortcuts - just type what you want!

---

## Common Workflows

### Workflow 1: "I Need to Find Documentation About X"

**The Best Approach:** Use multi-method search

```
Step 1: Quick Search (Ctrl+Shift+F)
├─ Type keywords: "user authentication"
├─ See instant results across all files
└─ Click to open

Step 2: Tag Search (if Step 1 doesn't work)
├─ Search: tag:#security tag:#authentication
├─ Shows all docs with both tags
└─ More precise results

Step 3: Graph Navigation (for exploration)
├─ Open any related document
├─ View graph (Ctrl+G)
├─ Click connected nodes
└─ Discover related concepts
```

**Example:** "Find documentation about the AI Persona system"

1. Press `Ctrl+Shift+F`
2. Type: `ai persona`
3. Results appear:
   - `AI_PERSONA_IMPLEMENTATION.md` (direct match!)
   - `source-docs/core/ai_systems.md` (contains AIPersona class)
   - `repo-docs/architecture/CORE_SYSTEMS.md` (architecture overview)

### Workflow 2: "I Need to Create New Documentation"

**The Template Way:** Fast and consistent

```
Step 1: Decide What You're Documenting
├─ Core system? → Use "module-doc-core-system"
├─ GUI component? → Use "module-doc-gui-component"
├─ Security feature? → Use "agent-doc-security-audit"
└─ Quickstart guide? → Use "guide-quickstart-feature"

Step 2: Create from Template
├─ Create new note (Ctrl+N)
├─ Open command palette (Ctrl+P)
├─ Type: "Templater: Insert template"
├─ Select your template
└─ Fill in the blanks

Step 3: Add Metadata
├─ Templates auto-generate YAML frontmatter
├─ Review and update tags
├─ Set status, priority, audience
└─ Save (Ctrl+S)

Step 4: Link It In
├─ Add to relevant index (MOC)
├─ Link from related documents
└─ Update dependency graph if needed
```

**Example:** Create documentation for a new API endpoint

1. `Ctrl+N` → New note
2. Name it: `API_ENDPOINT_USER_LOGIN.md`
3. `Ctrl+P` → "Templater: Insert template"
4. Choose: `architecture-doc-integration-api.md`
5. Template creates structure automatically:
   ```yaml
   ---
   type: architecture
   area: integration
   component: api
   status: active
   tags: [api, integration, authentication]
   ---
   ```
6. Fill in endpoint details
7. Link from `API_REFERENCE.md`

### Workflow 3: "I Need to Understand How Components Relate"

**The Visual Approach:** Use the graph!

```
Step 1: Open the Target Document
└─ Navigate to component documentation

Step 2: Open Local Graph
├─ Click graph icon (right sidebar)
├─ OR press Ctrl+G
└─ Shows only connections to current doc

Step 3: Filter the Graph
├─ Use filters panel (right side of graph)
├─ Show only specific tags: #architecture #security
├─ Adjust depth: 1 = direct connections, 2 = extended
└─ Remove clutter: Filter out common tags

Step 4: Explore Interactively
├─ Click nodes to navigate
├─ Hover to see preview
├─ Drag to reorganize
└─ Right-click for options
```

**Example:** Understand the Four Laws system

1. Open `FOUR_LAWS_FRAMEWORK.md`
2. Press `Ctrl+G`
3. Graph shows connections:
   - `ai_systems.py` (implementation)
   - `ETHICS_DOCUMENTATION.md` (design rationale)
   - `SECURITY_MODEL.md` (safety validation)
   - `command_override.py` (override system)
4. Click `command_override.py` to see override logic

### Workflow 4: "I Need to Track Changes or Updates"

**The Query Approach:** Live monitoring

```
Step 1: Open Query Library
└─ File: DATAVIEW_QUERY_LIBRARY.md

Step 2: Choose a Query
├─ Recent updates: Query #3
├─ Documents by status: Query #5
├─ High-priority items: Query #8
└─ Copy the code block

Step 3: Create a Dashboard Note
├─ Create: "MY_DASHBOARD.md"
├─ Paste queries you care about
└─ Switch to Preview mode

Step 4: Bookmark It
├─ Right-click in file explorer
├─ "Star" the file
└─ Appears in Starred section for quick access
```

**Example:** Monitor weekly documentation updates

Create `WEEKLY_UPDATES.md`:

````markdown
# My Weekly Updates Dashboard

## New Documents This Week
```dataviewjs
const oneWeekAgo = new Date();
oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

dv.table(
    ["Document", "Created", "Tags"],
    dv.pages()
        .where(p => p.created_date >= oneWeekAgo)
        .sort(p => p.created_date, 'desc')
        .map(p => [p.file.link, p.created_date, p.tags])
);
```

## Updated Documents This Week
```dataviewjs
// Similar query for updated_date
```
````

### Workflow 5: "I Need to Validate Documentation Quality"

**The Checklist Approach:** Use validation tools

```
Step 1: Run Metadata Validation
├─ Open: schemas/metadata-schema.json
├─ Install: Metadata Validator plugin
├─ Run: "Validate all frontmatter"
└─ Fix errors highlighted

Step 2: Check for Broken Links
├─ Command Palette (Ctrl+P)
├─ "Check for broken links"
└─ Fix or remove dead links

Step 3: Review Tag Consistency
├─ Open: TAG_TAXONOMY.md
├─ Compare your tags against official list
├─ Replace non-standard tags
└─ Follow cardinality rules (1 area tag required, etc.)

Step 4: Run Quality Queries
├─ Open: VAULT_HEALTH_DASHBOARD.md
├─ Review metrics:
│  ├─ Documents missing metadata
│  ├─ Documents with TODO markers
│  ├─ Orphan documents (no backlinks)
│  └─ Documents not updated in 90+ days
└─ Take corrective action
```

---

## Quick Wins: Immediate Value

Here are 10 things you can do RIGHT NOW to get value:

### 1. **Find the Main README** (10 seconds)
- Press `Ctrl+O`
- Type `readme`
- Read the overview

### 2. **See All Architecture Docs** (15 seconds)
- Press `Ctrl+Shift+F`
- Type `tag:#architecture`
- Explore the system design

### 3. **Visualize Component Relationships** (30 seconds)
- Press `Ctrl+G`
- Zoom out (mouse wheel)
- Click clusters to explore

### 4. **Browse by Topic** (30 seconds)
- Right sidebar → Tags panel
- Click any tag
- See all related documents

### 5. **Find Recent Updates** (1 minute)
- Open `DATAVIEW_QUERY_LIBRARY.md`
- Copy "Recent Updates" query
- Paste in new note
- Preview mode shows results

### 6. **Search Within Documents** (30 seconds)
- Open any document
- Press `Ctrl+F`
- Search within that file only

### 7. **Create Your First Document** (2 minutes)
- `Ctrl+N` → New note
- `Ctrl+P` → "Insert template"
- Choose a template
- Fill it out

### 8. **Bookmark Important Files** (15 seconds)
- Right-click on a file
- Select "Star"
- Quick access forever

### 9. **Export to PDF** (1 minute)
- Open any document
- `Ctrl+P` → "Export to PDF"
- Choose location
- Share externally

### 10. **Customize Your Workspace** (2 minutes)
- Settings (bottom left gear icon)
- Appearance → Choose a theme
- Editor → Adjust font size
- Hotkeys → Customize shortcuts

---

## Learning Path

Master the vault in stages:

### Stage 1: Foundation (Day 1) ⭐

**Goal:** Navigate confidently and find documents

**Read:**
- ✅ This guide (GETTING_STARTED.md)
- ✅ README.md
- ✅ SEARCH_GUIDE.md

**Practice:**
- ✅ Open 10 different documents using Quick Search
- ✅ Explore the graph view for 5 minutes
- ✅ Browse documents by tag

**You've Mastered Stage 1 When:**
- You can find any document in under 30 seconds
- You understand the folder structure
- You know how to use tags

### Stage 2: Creation (Week 1) ⭐⭐

**Goal:** Create and organize new documentation

**Read:**
- ✅ TEMPLATE_GUIDE.md
- ✅ METADATA_GUIDE.md
- ✅ templates/TEMPLATE_USAGE_GUIDE.md

**Practice:**
- ✅ Create 3 documents using different templates
- ✅ Add proper metadata to each
- ✅ Link new documents to existing ones

**You've Mastered Stage 2 When:**
- You can create documentation without looking up syntax
- Your metadata passes validation
- You understand linking strategies

### Stage 3: Querying (Week 2) ⭐⭐⭐

**Goal:** Ask complex questions and build dashboards

**Read:**
- ✅ QUERY_REFERENCE.md
- ✅ DATAVIEW_QUERY_LIBRARY.md
- ✅ DATAVIEW_PERFORMANCE_GUIDE.md

**Practice:**
- ✅ Run 10 different Dataview queries
- ✅ Modify a query to filter differently
- ✅ Create your own dashboard

**You've Mastered Stage 3 When:**
- You can write custom Dataview queries
- You understand query performance implications
- You've built a personal dashboard

### Stage 4: Maintenance (Ongoing) ⭐⭐⭐⭐

**Goal:** Keep the vault healthy and high-quality

**Read:**
- ✅ MAINTENANCE_GUIDE.md
- ✅ TAG_REFERENCE.md
- ✅ VAULT_HEALTH_DASHBOARD.md

**Practice:**
- ✅ Run weekly quality checks
- ✅ Fix broken links
- ✅ Update outdated documents
- ✅ Validate metadata consistency

**You've Mastered Stage 4 When:**
- You perform routine maintenance automatically
- You catch quality issues before they spread
- You contribute to improving the taxonomy

---

## Getting Help

### Built-In Resources

**In This Vault:**

1. **FAQ.md** - 30+ frequently asked questions
2. **TROUBLESHOOTING.md** - Solutions to common problems
3. **Tutorial Files** - Step-by-step guides in `/tutorials/`
4. **Query Library** - Copy-paste examples in DATAVIEW_QUERY_LIBRARY.md

### Obsidian Resources

**Official Documentation:**
- https://help.obsidian.md/ - Comprehensive Obsidian docs
- https://obsidian.md/plugins - Plugin directory
- https://forum.obsidian.md/ - Community forum

**Video Tutorials:**
- "Obsidian for Beginners" - YouTube playlist (linked in VIDEO_SCRIPT_OUTLINES.md)
- Plugin-specific tutorials in plugin documentation

### Project-AI Resources

**Repository Documentation:**
- `T:\Project-AI-main\.github\instructions\` - Development guidelines
- `T:\Project-AI-main\DEVELOPER_QUICK_REFERENCE.md` - Code reference
- `T:\Project-AI-main\PROGRAM_SUMMARY.md` - Full architecture

### Getting Live Help

**For Vault Issues:**
1. Check FAQ.md first
2. Search for error messages in TROUBLESHOOTING.md
3. Review VAULT_HEALTH_DASHBOARD.md for validation issues

**For Project-AI Questions:**
1. Review relevant architecture documentation
2. Check component-specific docs in source-docs/
3. Review implementation guides

**For Obsidian Problems:**
1. Settings → Community Plugins → Check for updates
2. Restart Obsidian
3. Check Obsidian forum for known issues

---

## What's Next?

You've completed the getting started guide! Here's your recommended next steps:

### Immediate Next Steps (Today)

1. ✅ Read the [SEARCH_GUIDE.md](SEARCH_GUIDE.md) to master finding documents
2. ✅ Browse through `repo-docs/` to see the documentation structure
3. ✅ Open [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md) and try 3 queries
4. ✅ Star your favorite documents for quick access

### This Week

1. ✅ Complete [TUTORIAL_BASIC_NAVIGATION.md](TUTORIAL_BASIC_NAVIGATION.md)
2. ✅ Read [METADATA_GUIDE.md](METADATA_GUIDE.md)
3. ✅ Create your first document using a template
4. ✅ Explore the graph view for 10 minutes

### This Month

1. ✅ Master Dataview queries with [TUTORIAL_ADVANCED_QUERIES.md](TUTORIAL_ADVANCED_QUERIES.md)
2. ✅ Build your own dashboard
3. ✅ Contribute documentation for a feature you understand
4. ✅ Help improve this documentation!

---

## Feedback Welcome!

This documentation is continuously improving. Found something confusing? Have a suggestion?

**How to Contribute:**

1. Create an issue in the Project-AI repository
2. Add comments directly in this document (Edit mode)
3. Submit a pull request with improvements
4. Share your feedback with the team

**Most Wanted Feedback:**

- 🤔 What was confusing?
- 💡 What examples would help?
- 🚀 What workflows should we document?
- 🐛 What errors did you encounter?

---

## Summary: Your First 5 Minutes Checklist

- [ ] Install Obsidian
- [ ] Open `T:\Project-AI-vault\` as vault
- [ ] Trust and enable plugins
- [ ] Try Quick Search (`Ctrl+Shift+F`)
- [ ] View the graph (`Ctrl+G`)
- [ ] Browse by tags (right sidebar)
- [ ] Run a Dataview query
- [ ] Star this document for reference
- [ ] Read SEARCH_GUIDE.md next
- [ ] Start exploring!

**Welcome to the Project-AI Vault!** 🎉

You're now ready to explore thousands of documents, discover hidden connections, and master the knowledge graph. Happy exploring!

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [user, developer, contributor]
priority: critical
tags: [getting-started, onboarding, tutorial, vault, obsidian]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 4200
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
