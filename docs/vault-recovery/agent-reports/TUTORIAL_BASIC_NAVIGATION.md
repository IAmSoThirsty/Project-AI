# Tutorial: Basic Navigation

**Step-by-Step Guide to Navigating the Project-AI Vault** 🧭

**Version:** 1.0.0  
**Last Updated:** 2026-04-20  
**Estimated Time:** 20 minutes  
**Skill Level:** Beginner  
**Audience:** New vault users

---

## Tutorial Overview

**What You'll Learn:**
- ✅ How to find any document in seconds
- ✅ Navigate using wiki links and backlinks
- ✅ Use the graph view effectively
- ✅ Browse documents by tags
- ✅ Understand Maps of Content (MOCs)

**Prerequisites:**
- Obsidian installed
- Project-AI Vault opened
- 20 minutes of focused time

**By the End:**
You'll confidently navigate 1,000+ documents without getting lost!

---

## Step 1: Orient Yourself (3 minutes)

### Exercise 1.1: View the Vault Structure

**Action:** Open the file explorer (left sidebar)

**What to Do:**

1. Look at the left sidebar
2. If not visible, press `Ctrl+Alt+L` or click the folder icon
3. Observe the folder structure:

```
📁 Project-AI-vault/
├─ 📁 repo-docs/           ← Repository documentation
├─ 📁 source-docs/         ← Original source code docs
├─ 📁 templates/           ← Document templates
├─ 📁 _indexes/            ← Navigation indexes (MOCs)
├─ 📁 schemas/             ← Metadata validation
├─ 📁 scripts/             ← Automation scripts
└─ 📄 README.md           ← START HERE!
```

**Your Task:**

- [ ] Click on `repo-docs` folder → Expand it
- [ ] Click on `source-docs` folder → Expand it
- [ ] Click on `README.md` → Read the first section

**What You Learned:**
- Vault has organized folder structure
- Documentation is grouped by purpose
- README is your starting point

### Exercise 1.2: Open Your First Document

**Action:** Use Quick Switcher to open README

**Steps:**

1. Press `Ctrl+O` (Quick Switcher)
2. Type: `readme`
3. You'll see "README.md" highlighted
4. Press `Enter`

**Result:** README.md opens in the center pane

**Your Task:**

- [ ] Scroll through README
- [ ] Notice the Table of Contents
- [ ] Click on a heading in TOC (it jumps to that section!)

**What You Learned:**
- `Ctrl+O` is your fastest navigation tool
- Fuzzy search works (you don't need exact names)
- TOC links jump to sections

---

## Step 2: Follow Wiki Links (4 minutes)

### Exercise 2.1: Understand Wiki Links

**Concept:** Wiki links are clickable connections between documents

**Format:** `[[Document Name]]`

**Examples in README:**

```markdown
See [[GETTING_STARTED]] for quick start
Learn about [[TAG_TAXONOMY]] for tagging
Review [[DATAVIEW_QUERY_LIBRARY]] for queries
```

**Action:** Follow your first wiki link

**Steps:**

1. In README, find a wiki link (in double brackets)
2. `Ctrl+Click` the link (or just click in Preview mode)
3. New document opens!
4. Press `Ctrl+Alt+←` to go back to README

**Your Task:**

- [ ] Click 3 different wiki links from README
- [ ] Use `Ctrl+Alt+←` to navigate back each time
- [ ] Notice how easy it is to explore

**What You Learned:**
- Wiki links connect related documents
- Click to follow, `Ctrl+Alt+←` to return
- You can't get lost - back button always works

### Exercise 2.2: Use Backlinks

**Concept:** Backlinks show which documents link TO the current document

**Action:** View backlinks panel

**Steps:**

1. Open any document (e.g., `TAG_TAXONOMY.md`)
2. Look at right sidebar
3. Find "Backlinks" section (or click backlinks icon)
4. See all documents that link to this one

**Your Task:**

- [ ] Open `TAG_TAXONOMY.md`
- [ ] View backlinks panel (right sidebar)
- [ ] Click on a backlink to see where it's referenced
- [ ] Navigate back

**What You Learned:**
- Backlinks = reverse navigation
- See who references this document
- Discover related content automatically

---

## Step 3: Navigate with Tags (5 minutes)

### Exercise 3.1: Browse the Tag Panel

**Action:** Open tags panel and explore

**Steps:**

1. Right sidebar → Click "Tags" icon (or search for tag panel)
2. See all tags in vault with counts
3. Tags are sorted alphabetically

**What You See:**

```
Tags Panel:
├─ #architecture (47)
├─ #security (32)
├─ #agent (28)
├─ #guide (25)
└─ ... (85+ tags total)
```

**Your Task:**

- [ ] Open Tags panel
- [ ] Click on `#architecture` tag
- [ ] See all architecture documents
- [ ] Click on `#security` tag
- [ ] Compare the document lists

**What You Learned:**
- Tags group related documents
- Click tag to see all tagged documents
- Easy way to browse by topic

### Exercise 3.2: Search by Tag

**Action:** Use search to filter by tags

**Steps:**

1. Press `Ctrl+Shift+F` (Global Search)
2. Type: `tag:#security`
3. See all security-tagged documents
4. Try: `tag:#security tag:#authentication` (multiple tags!)

**Your Task:**

- [ ] Search for `tag:#architecture`
- [ ] Search for `tag:#guide`
- [ ] Search for `tag:#security tag:#critical`
- [ ] Click on a result to open it

**What You Learned:**
- `tag:#name` searches by tag
- Combine multiple tags for precision
- Faster than browsing folders

---

## Step 4: Use the Graph View (4 minutes)

### Exercise 4.1: Open Global Graph

**Action:** Visualize entire vault as network

**Steps:**

1. Press `Ctrl+G` (Open Graph View)
2. Graph opens showing all documents as nodes
3. Lines connect linked documents
4. Zoom in/out with mouse wheel

**What You See:**

```
Graph View:
  • = Document (node)
  ─ = Link between documents
  
Clusters = Related topics
Dense areas = Highly connected
Isolated nodes = Orphans (need links!)
```

**Your Task:**

- [ ] Press `Ctrl+G` to open graph
- [ ] Zoom out to see full vault
- [ ] Zoom in on a cluster
- [ ] Click a node to open that document
- [ ] Close graph (`Ctrl+W`)

**What You Learned:**
- Graph shows connections visually
- Clusters reveal topic groups
- Click nodes to navigate

### Exercise 4.2: Use Local Graph

**Action:** See connections for ONE document

**Steps:**

1. Open a document (e.g., `AI_PERSONA_IMPLEMENTATION.md`)
2. Right sidebar → Graph icon (or `Ctrl+G` with doc open)
3. See only documents connected to this one
4. Adjust depth (1 = direct, 2 = extended)

**Your Task:**

- [ ] Open `TAG_TAXONOMY.md`
- [ ] View local graph (right sidebar)
- [ ] Set depth to 1 (direct connections only)
- [ ] Set depth to 2 (see extended connections)
- [ ] Click a connected node

**What You Learned:**
- Local graph = focused navigation
- Depth controls how far you look
- Great for exploring related docs

---

## Step 5: Navigate with MOCs (4 minutes)

### Exercise 5.1: Understand Maps of Content

**Concept:** MOCs (Maps of Content) are index documents that organize related links

**Think of MOCs as:**
- 📚 Table of Contents for a topic
- 🗺️ Navigation hub
- 📂 Curated collection

**Location:** `_indexes/` folder

**Action:** Open an MOC

**Steps:**

1. Press `Ctrl+O`
2. Type: `index`
3. Browse available MOCs
4. Open one that interests you

**Your Task:**

- [ ] Open `_indexes/` folder in file explorer
- [ ] Click on any MOC (e.g., `ARCHITECTURE_INDEX.md`)
- [ ] See organized list of links
- [ ] Click a link to jump to that doc

**What You Learned:**
- MOCs organize documents by topic
- Curated links save exploration time
- Start here when learning new area

### Exercise 5.2: Create Your Own Reading List

**Action:** Make a personal navigation document

**Steps:**

1. Create new note: `MY_READING_LIST.md`
2. Add heading: `# My Reading List`
3. Add wiki links to documents you want to read:

```markdown
# My Reading List

## To Read This Week
- [[GETTING_STARTED]]
- [[SEARCH_GUIDE]]
- [[TAG_TAXONOMY]]

## In Progress
- [[DATAVIEW_QUERY_LIBRARY]]

## Completed
- [[README]]
```

4. Save (`Ctrl+S`)
5. Star this document (right-click → Star)

**Your Task:**

- [ ] Create `MY_READING_LIST.md`
- [ ] Add 5 documents you want to read
- [ ] Star the file for quick access
- [ ] Update it as you read

**What You Learned:**
- You can create personal MOCs
- Starred files appear in sidebar
- Organize your learning path

---

## Navigation Challenges

**Test your skills with these challenges:**

### Challenge 1: Speed Navigation

**Goal:** Find and open 5 documents in under 2 minutes

**Documents to Find:**

1. `FOUR_LAWS_FRAMEWORK` (search: "four laws")
2. `LEATHER_BOOK_INTERFACE` (search: "leather")
3. `AGENT_048_COMPLETION_REPORT` (search: "048")
4. `SECURITY_MODEL` (tag: `#security`)
5. `DATAVIEW_QUERY_LIBRARY` (search: "query")

**Use:**
- `Ctrl+O` for quick switcher
- `Ctrl+Shift+F` for global search
- Tag panel for browsing

**Timer:** Start now!

**Your Result:**

- [ ] Found all 5 documents
- [ ] Time taken: _____ minutes

### Challenge 2: Connection Explorer

**Goal:** Find how two documents are connected

**Start:** `README.md`  
**End:** `AI_PERSONA_IMPLEMENTATION.md`

**Method:**

1. Open README
2. Look for links that lead toward AI Persona
3. Follow the chain of links
4. Track your path

**Your Path:**

```
README → [_____] → [_____] → AI_PERSONA_IMPLEMENTATION
```

**Hint:** Look for architecture or core systems links

### Challenge 3: Tag Master

**Goal:** Find all documents with specific tag combinations

**Find:**

1. All documents tagged `#architecture` AND `#security`
2. All documents tagged `#guide` AND `#tutorial`
3. All documents tagged `#agent` in `active` status

**Method:**

```
Search: tag:#architecture tag:#security
Search: tag:#guide tag:#tutorial
Search: tag:#agent status:active
```

**Your Findings:**

- [ ] Architecture + Security: _____ documents found
- [ ] Guide + Tutorial: _____ documents found
- [ ] Agent + Active: _____ documents found

---

## Summary: Navigation Toolkit

**You Now Know:**

✅ **File Explorer** - Browse folder structure  
✅ **Quick Switcher** (`Ctrl+O`) - Find files by name  
✅ **Global Search** (`Ctrl+Shift+F`) - Search all content  
✅ **Wiki Links** - Follow connections between docs  
✅ **Backlinks** - See who references this doc  
✅ **Tags** - Browse by category  
✅ **Graph View** (`Ctrl+G`) - Visualize connections  
✅ **MOCs** - Navigate curated indexes

**Navigation Decision Tree:**

```
I want to...

Find specific doc by name?
  → Use Quick Switcher (Ctrl+O)

Find docs about a topic?
  → Use Tag Panel or search tag:#topic

Explore related docs?
  → Use Graph View (Ctrl+G)

Get overview of area?
  → Check MOCs in _indexes/

Find who references doc?
  → Check Backlinks panel

Search for specific text?
  → Use Global Search (Ctrl+Shift+F)
```

---

## Next Steps

**Now that you've mastered navigation:**

1. ✅ **Next Tutorial:** [TUTORIAL_CREATING_DOCUMENTS.md](TUTORIAL_CREATING_DOCUMENTS.md)
2. 📖 **Deep Dive:** [SEARCH_GUIDE.md](SEARCH_GUIDE.md) - Advanced search techniques
3. 🎯 **Practice:** Navigate the vault daily for 5 minutes
4. 🔖 **Bookmark:** Star your most-used documents

**Keep Practicing:**

- Use `Ctrl+O` instead of file explorer
- Follow wiki links instead of searching
- Check graph view when exploring new topics
- Build your personal reading list

**You've completed Basic Navigation!** 🎉

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [user, contributor]
priority: high
tags: [tutorial, navigation, beginner, getting-started, obsidian]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
estimated_time: 20 minutes
difficulty: beginner
word_count: 1850
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

