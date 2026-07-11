# Search Guide: Finding Anything in Seconds

**Master the Art of Discovery** 🔍

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 12 minutes
**Audience:** All vault users
**Prerequisites:** Basic Obsidian familiarity

---

## Table of Contents

1. [Search Philosophy](#search-philosophy)
2. [Quick Search Methods](#quick-search-methods)
3. [Tag-Based Search](#tag-based-search)
4. [Advanced Search Operators](#advanced-search-operators)
5. [Graph Navigation](#graph-navigation)
6. [Dataview Queries](#dataview-queries)
7. [Search Strategies](#search-strategies)
8. [Performance Tips](#performance-tips)
9. [Troubleshooting Search](#troubleshooting-search)

---

## Search Philosophy

In a vault with **1,000+ documents** across multiple domains, effective search is critical. Project-AI Vault uses a **multi-layered search strategy**:

### The Search Hierarchy

```
Level 1: Quick Search (Ctrl+Shift+F)
├─ Use when: You know keywords or phrases
├─ Speed: Instant (<50ms)
└─ Best for: Finding specific documents or content

Level 2: Tag Search
├─ Use when: You know the category or domain
├─ Speed: Very fast (<100ms)
└─ Best for: Browsing by topic or component

Level 3: Graph Navigation
├─ Use when: Exploring related concepts
├─ Speed: Interactive
└─ Best for: Discovery and understanding relationships

Level 4: Dataview Queries
├─ Use when: Complex filtering needed
├─ Speed: Fast for optimized queries (<200ms)
└─ Best for: Analytical questions and dashboards

Level 5: Full-Text Search
├─ Use when: Need to search within documents
├─ Speed: Slower (depends on vault size)
└─ Best for: Finding specific code or text
```

**Rule of Thumb:** Start simple (Level 1), escalate as needed.

---

## Quick Search Methods

### Method 1: Quick Switcher (Ctrl+O)

**What It Does:** Find documents by filename

**How to Use:**

1. Press `Ctrl+O` (Windows) or `Cmd+O` (Mac)
2. Start typing the document name
3. Use arrow keys to select
4. Press Enter to open

**Features:**

- ✅ **Fuzzy matching** - Type partial words: "aiprs" finds "AI_PERSONA_SYSTEM.md"
- ✅ **Recent files** - Shows recently opened files first
- ✅ **Alias support** - Searches document aliases too
- ✅ **Path search** - Include folder names: "core/ai_systems"

**Examples:**

```
Search: "fourl" → Finds: FOUR_LAWS_FRAMEWORK.md
Search: "gui/lea" → Finds: gui/leather_book_interface.md
Search: "agent017" → Finds: AGENT_017_COMPLETION_REPORT.md
```

**Pro Tips:**

- **Be lazy:** Type the shortest unique prefix
- **Use capitals:** "AIPR" → AI_PERSONA_IMPLEMENTATION.md
- **Recent bias:** Frequently accessed files appear higher

### Method 2: Global Search (Ctrl+Shift+F)

**What It Does:** Search ALL content (filenames + file contents)

**How to Use:**

1. Press `Ctrl+Shift+F`
2. Type your search query
3. Results show instantly
4. Click to open and highlight

**Search Capabilities:**

```
Plain Text Search
├─ "user authentication" → Finds exact phrase
├─ user authentication → Finds both words (anywhere)
└─ "user auth*" → Finds user auth, user authentication, etc.

Boolean Operators
├─ user AND authentication → Both words required
├─ user OR login → Either word matches
├─ user NOT guest → Exclude "guest" results
└─ (user OR admin) AND auth → Complex logic

Regular Expressions (Advanced)
├─ /\b[A-Z]{2,}\b/ → Find acronyms (AI, GUI, API)
├─ /def \w+\(/ → Find Python function definitions
└─ /https?:\/\/.+/ → Find URLs
```

**Result Options:**

- **Show matches** - See context around each match
- **Show more context** - Expand context window
- **Collapse all** - Minimize to file list only
- **Copy results** - Export search results

**Examples:**

```
Query: "ethical decision making"
Results:
├─ FOUR_LAWS_FRAMEWORK.md (5 matches)
├─ AI_PERSONA_IMPLEMENTATION.md (3 matches)
└─ ETHICS_DOCUMENTATION.md (12 matches)

Query: tag:#security AND "password"
Results:
├─ source-docs/core/user_manager.md
├─ repo-docs/security/AUTHENTICATION.md
└─ SECURITY_MODEL.md

Query: path:source-docs "class AIPersona"
Results:
└─ source-docs/core/ai_systems.md (exact location)
```

**Pro Tips:**

- **Use quotes** for exact phrases: `"def validate_action"`
- **Combine with tags** for precision: `tag:#architecture "system design"`
- **Search in specific folders** with `path:` operator
- **Exclude folders** with `-path:` operator

### Method 3: In-File Search (Ctrl+F)

**What It Does:** Search within the currently open document

**How to Use:**

1. Open a document
2. Press `Ctrl+F`
3. Type search term
4. Use arrows to navigate matches

**Features:**

- **Match case** toggle
- **Regular expression** mode
- **Whole word** matching
- **Replace** functionality (`Ctrl+H`)

**When to Use:**

- You're reading a long document
- You know the document but need a specific section
- You want to replace text across the document

---

## Tag-Based Search

Tags are your **most powerful navigation tool**. Project-AI uses **85+ structured tags** across 7 categories.

### Understanding Tag Categories

**See:** [TAG_TAXONOMY.md](TAG_TAXONOMY.md) for complete reference

```yaml
Tag Categories:
├─ area (1-3 required)     # Domain: architecture, security, documentation
├─ type (1-2 required)     # Doc type: guide, reference, architecture
├─ component (0-5)         # System part: agent, gui, core-system
├─ status (1 required)     # Lifecycle: active, draft, deprecated
├─ audience (1-4 required) # Readers: developer, user, architect
├─ priority (0-1)          # Urgency: critical, high, medium, low
└─ special (0-10)          # Markers: breaking-change, security-critical
```

### Tag Search Syntax

**Basic Tag Search:**

```
tag:#architecture          → All architecture docs
tag:#security             → All security docs
tag:#agent                → All agent documentation
```

**Multiple Tag Search (AND logic):**

```
tag:#security tag:#authentication
→ Documents with BOTH tags

tag:#architecture tag:#core-system tag:#active
→ Active core system architecture docs
```

**Tag Search with Content:**

```
tag:#security "encryption"
→ Security docs mentioning encryption

tag:#guide "quickstart"
→ Guides with quickstart content
```

**Exclude Tags:**

```
tag:#documentation -tag:#draft
→ Documentation that's NOT draft status

tag:#architecture -tag:#deprecated
→ Current (non-deprecated) architecture docs
```

### Tag Browser (Visual Search)

**Open:** Right sidebar → Tags icon

**How It Works:**

```
Tag Browser Display:
├─ #architecture (47)
│  ├─ Click → See all 47 docs
│  └─ Hover → Preview count
├─ #security (32)
├─ #agent (28)
└─ ... (all tags alphabetically)
```

**Pro Tips:**

- **Nested tags** show parent/child: `#security/cryptography`
- **Click counts** to see which tags are most used
- **Combine with search** for powerful filtering

### Smart Tag Queries

**Recent + Tag:**

```dataview
LIST
FROM #security
WHERE created_date >= date(today) - dur(7 days)
SORT created_date DESC
```
→ Security docs created this week

**High Priority + Area:**

```dataview
TABLE priority, status, updated_date
FROM #architecture
WHERE priority = "critical" OR priority = "high"
SORT priority ASC, updated_date DESC
```
→ Critical architecture docs to review

---

## Advanced Search Operators

### File Property Operators

Search based on file metadata:

```
created:[date]          → Created on specific date
modified:[date]         → Last modified date
file:README            → Filename contains "README"
path:source-docs/      → In specific folder
extension:md           → File extension
size:[bytes]           → File size
```

**Date Formats:**

```
created:2026-04-20     → Exact date
created:2026-04        → Entire month
modified:>2026-04-01   → After date
modified:<2026-03-31   → Before date
```

**Examples:**

```
file:AGENT modified:>2026-04-15
→ Agent files modified after April 15

path:repo-docs/ extension:md size:>10000
→ Large markdown files in repo-docs/

created:2026-04 tag:#architecture
→ Architecture docs created in April 2026
```

### Content Operators

**Case Sensitivity:**

```
match-case:yes "AIPersona"
→ Exact case match only (excludes "aipersona", "AIPERSONA")
```

**Whole Word:**

```
word:"AI"
→ Matches "AI" but not "AIPlatform" or "AISystem"
```

**Line Context:**

```
line:(def validate_action)
→ Finds exact line (useful for code)
```

### Proximity Operators

**Words Near Each Other:**

```
"security" NEAR/5 "authentication"
→ "security" within 5 words of "authentication"

"password" BEFORE "hash"
→ "password" must appear before "hash"
```

### Regular Expression Search

Enable regex mode in search settings:

**Common Patterns:**

```regex
Function Definitions:
  /def \w+\(/
  → Finds: def validate_action(, def hash_password(

Class Definitions:
  /class \w+:/
  → Finds: class AIPersona:, class UserManager:

Imports:
  /^from \w+ import/
  → Finds all import statements

URLs:
  /https?:\/\/[^\s]+/
  → Finds all HTTP/HTTPS URLs

Email Addresses:
  /[\w.-]+@[\w.-]+\.\w+/
  → Finds: user@example.com

TODO Markers:
  /TODO:|FIXME:|HACK:/
  → Finds code comments with action items

Version Numbers:
  /\d+\.\d+\.\d+/
  → Finds: 1.0.0, 2.3.1

Dates (YYYY-MM-DD):
  /\d{4}-\d{2}-\d{2}/
  → Finds: 2026-04-20
```

---

## Graph Navigation

The **graph view** is your visual search tool. Use it to discover connections and navigate relationships.

### Opening the Graph

**Global Graph:** `Ctrl+G`
- Shows ALL documents and connections
- Can be overwhelming in large vaults

**Local Graph:** Right sidebar → Graph icon
- Shows only connections to current document
- Adjustable depth (1 = direct, 2 = extended)

### Graph Controls

**Filters Panel (Right Side):**

```
Search Files
├─ Type document names to highlight
└─ Multiple selections possible

Tags
├─ Show only specific tags
├─ OR logic: Show if ANY tag matches
└─ AND logic: Show if ALL tags match

Orphans
├─ Show/hide orphan documents
└─ (Documents with no connections)

Attachments
├─ Show/hide image/PDF files
└─ Declutter view
```

**Display Panel:**

```
Forces
├─ Center force: Pull nodes to center
├─ Repel: Push nodes apart
├─ Link force: Pull connected nodes together
└─ Adjust for optimal layout

Node Settings
├─ Text fade threshold: When to hide labels
├─ Node size: Based on backlinks
└─ Line thickness: Connection strength
```

### Graph Search Workflow

**Scenario 1: Explore Component Dependencies**

```
Goal: Understand what depends on AIPersona

Step 1: Open source-docs/core/ai_systems.md
Step 2: Open local graph (right sidebar)
Step 3: Set depth to 2
Step 4: See:
  ├─ Direct dependencies (depth 1)
  │  ├─ AI_PERSONA_IMPLEMENTATION.md
  │  ├─ CORE_SYSTEMS.md
  │  └─ leather_book_interface.md
  └─ Extended dependencies (depth 2)
     ├─ USER_EXPERIENCE.md
     ├─ TESTING_GUIDE.md
     └─ DEPLOYMENT.md
```

**Scenario 2: Find Related Security Docs**

```
Goal: See all security-related architecture

Step 1: Press Ctrl+G (global graph)
Step 2: Filters → Tags → Check #security and #architecture
Step 3: Zoom to fit (mouse wheel)
Step 4: Click any node to navigate
Step 5: Local graph from there for deep dive
```

**Scenario 3: Discover Orphaned Documents**

```
Goal: Find documents with no backlinks

Step 1: Global graph
Step 2: Filters → Check "Orphans"
Step 3: Look for isolated nodes
Step 4: Click to open
Step 5: Add missing links or consider deletion
```

### Graph Navigation Shortcuts

```
Zoom: Mouse wheel
Pan: Click + drag empty space
Select: Click node
Multi-select: Ctrl + Click nodes
Focus: Double-click node (opens in local graph)
Reset: Zoom to fit button (top left)
```

---

## Dataview Queries

**Dataview** enables SQL-like queries over your vault. Perfect for analytical search.

### Query Types

**1. LIST - Simple Lists**

```dataviewjs
// All security documents
dv.list(dv.pages("#security").file.link)
```

**2. TABLE - Structured Data**

```dataviewjs
// Documents by status
dv.table(
  ["Document", "Status", "Priority", "Updated"],
  dv.pages("#architecture")
    .map(p => [p.file.link, p.status, p.priority, p.updated_date])
)
```

**3. TASK - Task Lists**

```dataviewjs
// All incomplete tasks
dv.taskList(
  dv.pages().file.tasks.where(t => !t.completed)
)
```

**4. CALENDAR - Date-Based Views**

```dataviewjs
// Documents created by date
dv.pages()
  .where(p => p.created_date)
  .groupBy(p => p.created_date)
```

### Common Search Queries

**Recent Updates:**

```dataviewjs
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

dv.table(
  ["Document", "Updated", "Author"],
  dv.pages()
    .where(p => p.updated_date >= sevenDaysAgo)
    .sort(p => p.updated_date, 'desc')
    .limit(20)
    .map(p => [p.file.link, p.updated_date, p.author])
);
```

**High Priority Items:**

```dataviewjs
dv.table(
  ["Document", "Priority", "Status", "Audience"],
  dv.pages()
    .where(p => p.priority === "critical" || p.priority === "high")
    .sort(p => p.priority === "critical" ? 0 : 1)
    .map(p => [p.file.link, p.priority, p.status, p.audience])
);
```

**Documents Missing Metadata:**

```dataviewjs
dv.table(
  ["Document", "Missing Fields"],
  dv.pages()
    .where(p => !p.status || !p.tags || !p.audience)
    .map(p => {
      const missing = [];
      if (!p.status) missing.push("status");
      if (!p.tags) missing.push("tags");
      if (!p.audience) missing.push("audience");
      return [p.file.link, missing.join(", ")];
    })
);
```

**Dependency Search:**

```dataviewjs
// Documents that depend on "AIPersona"
dv.table(
  ["Document", "Dependencies"],
  dv.pages()
    .where(p => p.dependencies && p.dependencies.includes("AIPersona"))
    .map(p => [p.file.link, p.dependencies])
);
```

**Tag Combination Search:**

```dataviewjs
// Security + Authentication + Active
dv.table(
  ["Document", "Tags", "Updated"],
  dv.pages()
    .where(p =>
      p.tags &&
      p.tags.includes("security") &&
      p.tags.includes("authentication") &&
      p.status === "active"
    )
    .sort(p => p.updated_date, 'desc')
    .map(p => [p.file.link, p.tags, p.updated_date])
);
```

**See Full Library:** [DATAVIEW_QUERY_LIBRARY.md](DATAVIEW_QUERY_LIBRARY.md)

---

## Search Strategies

### Strategy 1: Precision Search (Known Target)

**When:** You know exactly what you're looking for

**Method:** Quick Switcher or Tag Search

```
Example: Find the AIPersona implementation

Approach:
1. Ctrl+O
2. Type: "ai pers"
3. Open AI_PERSONA_IMPLEMENTATION.md
4. Total time: 3 seconds
```

### Strategy 2: Exploratory Search (Unknown Target)

**When:** You're learning about a topic

**Method:** Tag → Graph → Content

```
Example: Learn about security architecture

Approach:
1. Tag search: #security #architecture
2. Open first result
3. View local graph
4. Explore connected docs
5. Follow interesting links
6. Total time: 5-10 minutes
```

### Strategy 3: Analytical Search (Patterns/Trends)

**When:** You need aggregated data

**Method:** Dataview Queries

```
Example: Find all outdated documentation

Approach:
1. Open DATAVIEW_QUERY_LIBRARY.md
2. Copy "Stale Documents" query
3. Modify threshold (90 days)
4. Run in new note
5. Export results
6. Total time: 2 minutes
```

### Strategy 4: Code Search (Implementation Details)

**When:** You need specific code or syntax

**Method:** Regex Search in source-docs/

```
Example: Find all class definitions

Approach:
1. Ctrl+Shift+F
2. Enable regex mode
3. Query: path:source-docs /^class \w+:/
4. Review matches
5. Total time: 1 minute
```

### Strategy 5: Contextual Search (Related Topics)

**When:** You need everything about a concept

**Method:** Multi-tag + Content Search

```
Example: Everything about user authentication

Approach:
1. Tag search: #security #authentication
2. Content search: "bcrypt" OR "password" OR "login"
3. Graph view of results
4. Create reading list
5. Total time: 5 minutes
```

---

## Performance Tips

### Speed Optimization

**Vault Size Impact:**

```
Small (<500 files):   All searches instant (<50ms)
Medium (500-2000):    Most searches fast (<200ms)
Large (2000-5000):    Dataview queries may lag
Very Large (5000+):   Consider vault splitting
```

**Optimization Techniques:**

1. **Index Search Strings**
   - Obsidian maintains search index
   - Rebuilds on startup (Settings → Files & Links → Rebuild search index)

2. **Limit Query Scope**
   ```dataviewjs
   // Slow: Search entire vault
   dv.pages()

   // Fast: Limit to folder
   dv.pages('"repo-docs/architecture"')

   // Fastest: Limit by tag
   dv.pages("#architecture")
   ```

3. **Optimize Regex**
   ```regex
   Slow:  /.*password.*/  (greedy wildcard)
   Fast:  /\bpassword\b/  (word boundary)
   ```

4. **Cache Heavy Queries**
   - Create dashboard notes with results
   - Refresh daily instead of live queries
   - Use `dataviewjs` with caching variables

5. **Exclude Large Files**
   ```
   Search: authentication -path:logs/ -path:scripts/
   → Exclude log files and scripts from search
   ```

### Search Index Management

**Rebuild Search Index:** (if search feels slow)

```
Steps:
1. Settings (gear icon)
2. Files & Links
3. Click "Rebuild search index"
4. Wait 10-30 seconds
5. Close settings
```

**When to Rebuild:**

- After importing many files
- After major vault restructuring
- If search results seem incomplete
- After Obsidian crash/force quit

---

## Troubleshooting Search

### Problem: "Search returns no results but I know the file exists"

**Solutions:**

1. **Check search syntax**
   - Quotes for exact phrases: `"exact phrase"`
   - Case sensitivity disabled by default

2. **Rebuild search index**
   - Settings → Files & Links → Rebuild search index

3. **Check file location**
   - May be in excluded folder
   - Settings → Files & Links → Excluded files

4. **Try filename search instead**
   - `Ctrl+O` for filename only

### Problem: "Tag search not working"

**Solutions:**

1. **Verify tag format**
   - Must start with `#`: `#architecture` not `architecture`
   - No spaces: `#core-system` not `#core system`

2. **Check tag in frontmatter**
   ```yaml
   ---
   tags: [architecture, security]  # ✅ Valid
   tags: architecture security      # ❌ Invalid
   ---
   ```

3. **Rebuild tag cache**
   - Close and reopen Obsidian
   - Tags rebuild automatically

### Problem: "Dataview query shows 'undefined' or errors"

**Solutions:**

1. **Check plugin enabled**
   - Settings → Community Plugins → Dataview (enabled?)

2. **Verify syntax**
   ```dataviewjs
   // ✅ Correct
   dv.list(dv.pages("#security").file.link)

   // ❌ Wrong
   dv.list(dv.pages("#security"))  // Missing .file.link
   ```

3. **Check field names**
   - Must match frontmatter exactly
   - Case-sensitive: `updated_date` not `Updated_Date`

4. **View error console**
   - `Ctrl+Shift+I` → Console tab
   - See detailed error messages

### Problem: "Graph view shows no connections"

**Solutions:**

1. **Check graph filters**
   - Filters panel → Ensure tags not limiting too much
   - Reset filters to default

2. **Verify documents have links**
   - Links format: `[[Document Name]]`
   - Not markdown links: `[Document](path.md)`

3. **Check orphan filter**
   - May be hiding connected nodes
   - Uncheck "Orphans" filter

4. **Increase graph depth**
   - Local graph → Set depth to 2 or 3

### Problem: "Search is very slow"

**Solutions:**

1. **Reduce query scope**
   ```
   Slow: dv.pages()
   Fast: dv.pages("#architecture")
   ```

2. **Limit results**
   ```dataviewjs
   dv.pages("#security")
     .limit(50)  // Only show first 50
   ```

3. **Check vault size**
   - >5000 files may require optimization
   - Consider splitting vault by domain

4. **Disable unnecessary plugins**
   - Settings → Community Plugins
   - Disable unused plugins
   - Restart Obsidian

---

## Summary: Search Quick Reference

| **Task** | **Method** | **Shortcut** |
|----------|-----------|--------------|
| Find document by name | Quick Switcher | `Ctrl+O` |
| Search all content | Global Search | `Ctrl+Shift+F` |
| Search in current file | In-File Search | `Ctrl+F` |
| Browse by tag | Tag Panel | Right sidebar |
| Visual navigation | Graph View | `Ctrl+G` |
| Analytical queries | Dataview | Code block in note |
| Recent documents | Quick Switcher | `Ctrl+O` (shows recent) |
| Advanced operators | Global Search | `tag:`, `path:`, `file:` |

**Search Mastery Path:**

1. **Week 1:** Master Quick Switcher and Global Search
2. **Week 2:** Learn tag-based navigation
3. **Week 3:** Use graph view for exploration
4. **Week 4:** Write custom Dataview queries

**You've mastered search when:**
- ✅ You can find any document in under 10 seconds
- ✅ You use tags to browse categories efficiently
- ✅ You navigate the graph to discover connections
- ✅ You write custom queries for your workflows

---

**Next Steps:**

- **Practice:** Try 10 different searches right now
- **Read:** [QUERY_REFERENCE.md](QUERY_REFERENCE.md) for advanced queries
- **Explore:** [TUTORIAL_BASIC_NAVIGATION.md](TUTORIAL_BASIC_NAVIGATION.md) for step-by-step practice

Happy searching! 🔍

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [user, developer, contributor]
priority: high
tags: [search, navigation, dataview, graph, obsidian, tutorial]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 3800
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
