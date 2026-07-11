# Template Guide: Creating Consistent Documentation

**Master Document Templates and Automation** 📝

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 12 minutes
**Audience:** Documentation contributors, developers
**Prerequisites:** Basic Obsidian and markdown knowledge

---

## Table of Contents

1. [What are Templates?](#what-are-templates)
2. [Available Templates](#available-templates)
3. [How to Use Templates](#how-to-use-templates)
4. [Customizing Templates](#customizing-templates)
5. [Creating New Templates](#creating-new-templates)
6. [Templater Best Practices](#templater-best-practices)
7. [Template Syntax Reference](#template-syntax-reference)
8. [Common Use Cases](#common-use-cases)
9. [Troubleshooting](#troubleshooting)

---

## What are Templates?

**Templates** are pre-built document structures that ensure consistency, save time, and enforce documentation standards across the Project-AI vault.

### Why Use Templates?

✅ **Consistency** - All documents of the same type have identical structure
✅ **Speed** - Create new docs in seconds instead of minutes
✅ **Completeness** - Never forget required sections or metadata
✅ **Quality** - Enforce best practices automatically
✅ **Metadata** - Auto-generate correct frontmatter every time
✅ **Standards** - Comply with tag taxonomy and schema validation

### Without vs With Templates

**Without Templates (Manual Creation):**

```markdown
# Some Document

I need to document this feature...

Wait, what metadata fields do I need?
What sections should I include?
What tags are valid?
How do I format this?

→ 15 minutes to create basic structure
→ Missing metadata
→ Inconsistent formatting
→ Validation errors
```

**With Templates (Automated):**

```markdown
1. Ctrl+N (new note)
2. Ctrl+P → "Templater: Insert template"
3. Choose "guide-developer-reference"
4. Fill in the blanks

→ 30 seconds to create complete structure
→ All metadata auto-generated
→ Perfect formatting
→ Validation guaranteed
```

---

## Available Templates

Project-AI Vault provides **15 production-ready templates** across 4 categories.

### Template Categories

```
templates/
├─ Module Documentation (3 templates)
│  ├─ module-doc-core-system.md
│  ├─ module-doc-gui-component.md
│  └─ module-doc-agent.md
│
├─ Architecture Documentation (3 templates)
│  ├─ architecture-doc-adr.md
│  ├─ architecture-doc-design-pattern.md
│  └─ architecture-doc-integration-api.md
│
├─ Guide Documentation (3 templates)
│  ├─ guide-quickstart-feature.md
│  ├─ guide-developer-reference.md
│  └─ guide-troubleshooting-production.md
│
├─ Agent Documentation (3 templates)
│  ├─ agent-doc-task-report.md
│  ├─ agent-doc-security-audit.md
│  └─ agent-doc-convergence-summary.md
│
└─ Supporting Files
   ├─ TEMPLATE_LIBRARY.md ........... Template catalog
   ├─ TEMPLATE_USAGE_GUIDE.md ....... Detailed usage instructions
   ├─ NAMING_CONVENTIONS.md ......... File naming rules
   └─ .template-categories.json ..... Metadata for templates
```

### Template Quick Reference

| Template Name | Use When | Output Example |
|---------------|----------|----------------|
| **module-doc-core-system** | Documenting core Python modules | `AI_PERSONA_IMPLEMENTATION.md` |
| **module-doc-gui-component** | Documenting PyQt6 GUI components | `LEATHER_BOOK_DASHBOARD.md` |
| **module-doc-agent** | Documenting AI agent systems | `AGENT_OVERSIGHT_SYSTEM.md` |
| **architecture-doc-adr** | Recording architecture decisions | `ADR_023_AUTHENTICATION.md` |
| **architecture-doc-design-pattern** | Documenting design patterns | `OBSERVER_PATTERN_USAGE.md` |
| **architecture-doc-integration-api** | API integration documentation | `OPENAI_API_INTEGRATION.md` |
| **guide-quickstart-feature** | Quick start guides for features | `QUICKSTART_IMAGE_GENERATION.md` |
| **guide-developer-reference** | Developer API references | `DEVELOPER_API_REFERENCE.md` |
| **guide-troubleshooting-production** | Troubleshooting guides | `TROUBLESHOOTING_LOGIN.md` |
| **agent-doc-task-report** | Agent completion reports | `AGENT_048_COMPLETION_REPORT.md` |
| **agent-doc-security-audit** | Security audit reports | `SECURITY_AUDIT_2026_Q2.md` |
| **agent-doc-convergence-summary** | Phase completion summaries | `PHASE_3_SUMMARY.md` |

---

## How to Use Templates

### Method 1: Templater Plugin (Recommended)

**Prerequisites:**
- Templater plugin installed and enabled
- Template folder configured: `templates/`

**Steps:**

```
1. Create new note
   └─ Ctrl+N or click "New note" button

2. Open command palette
   └─ Ctrl+P (Windows) or Cmd+P (Mac)

3. Search for Templater
   └─ Type: "Templater: Insert template"

4. Select template
   └─ Browse list, press Enter on desired template

5. Template inserts
   └─ Complete structure with placeholders

6. Fill in placeholders
   └─ Replace <% tp.file.cursor() %> markers
   └─ Update metadata fields
   └─ Add your content

7. Save
   └─ Ctrl+S
```

**Example Workflow:**

```
Task: Document the FourLaws system

Step 1: Ctrl+N → New note named "FOUR_LAWS_FRAMEWORK.md"

Step 2: Ctrl+P → "Templater: Insert template"

Step 3: Select "module-doc-core-system"

Step 4: Template inserts:
---
type: code-documentation
area: [architecture, ai-systems]
component: core-system
status: active
audience: [developer, architect]
priority: high
tags: [core-system, ai-systems, ethics, <% tp.file.cursor(1) %>]
version: 1.0.0
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
author: <% tp.file.cursor(2) %>
---

# <% tp.file.title %>

## Overview
<% tp.file.cursor(3) %>

## Architecture
...

Step 5: Fill in cursors:
- Cursor 1: Add "four-laws"
- Cursor 2: Add your agent ID
- Cursor 3: Write overview

Step 6: Ctrl+S to save
```

### Method 2: Manual Copy-Paste

**Steps:**

1. Navigate to `templates/` folder
2. Open desired template
3. Copy entire content (Ctrl+A, Ctrl+C)
4. Create new note
5. Paste content (Ctrl+V)
6. Modify metadata and placeholders
7. Save

**When to Use:**
- Templater plugin unavailable
- Need to preview template before using
- Creating one-off variations

### Method 3: Hotkey Assignment (Advanced)

**Configure:**

1. Settings → Hotkeys
2. Search "Templater"
3. Assign hotkeys to frequently used templates
4. Example: `Ctrl+Alt+G` → Insert "guide-quickstart-feature"

**Benefits:**
- Instant template insertion
- No menu navigation
- Muscle memory automation

---

## Customizing Templates

### Understanding Template Structure

Templates consist of 3 sections:

```markdown
┌─────────────────────────────────────┐
│ 1. FRONTMATTER (YAML Metadata)      │
│ ---                                 │
│ type: guide                         │
│ tags: [<% placeholders %>]          │
│ created_date: <% auto-generated %>  │
│ ---                                 │
├─────────────────────────────────────┤
│ 2. DOCUMENT HEADER                  │
│ # <% tp.file.title %>               │
│                                     │
│ **Purpose:** <% cursor %>           │
├─────────────────────────────────────┤
│ 3. CONTENT SECTIONS                 │
│ ## Section 1                        │
│ <% tp.file.cursor() %>              │
│                                     │
│ ## Section 2                        │
│ ...                                 │
└─────────────────────────────────────┘
```

### Placeholder Types

**1. Auto-Generated Values:**

```javascript
<% tp.date.now("YYYY-MM-DD") %>        // Today's date: 2026-04-20
<% tp.date.now("YYYY-MM-DD HH:mm") %>  // Date + time: 2026-04-20 14:30
<% tp.file.title %>                    // File name without extension
<% tp.file.path(true) %>               // Full file path
```

**2. Interactive Prompts:**

```javascript
<% tp.system.prompt("Author name") %>           // Ask for input
<% tp.system.suggester(["v1", "v2"], ["v1", "v2"], false, "Version") %>  // Choose from list
```

**3. Cursor Positions:**

```javascript
<% tp.file.cursor(1) %>   // Jump to first cursor
<% tp.file.cursor(2) %>   // Jump to second cursor
<% tp.file.cursor(3) %>   // Jump to third cursor
```

### Customization Examples

**Example 1: Change Default Tags**

**Original:**
```yaml
tags: [architecture, design-pattern, <% tp.file.cursor() %>]
```

**Customized:**
```yaml
tags: [security, authentication, encryption, <% tp.file.cursor() %>]
```

**Example 2: Add Custom Fields**

**Original:**
```yaml
---
type: guide
area: documentation
status: active
---
```

**Customized:**
```yaml
---
type: guide
area: documentation
status: active
project: <% tp.system.prompt("Project name") %>
sprint: <% tp.system.prompt("Sprint number") %>
ticket: <% tp.system.prompt("JIRA ticket") %>
---
```

**Example 3: Dynamic Content Sections**

**Original:**
```markdown
## Installation

### Prerequisites
- Requirement 1
- Requirement 2
```

**Customized:**
```markdown
## Installation

### Prerequisites

**For Windows:**
<% tp.file.cursor(1) %>

**For Linux:**
<% tp.file.cursor(2) %>

**For macOS:**
<% tp.file.cursor(3) %>
```

**Example 4: Conditional Sections**

```javascript
## Security Considerations

<% if (tp.frontmatter.tags.includes("security-critical")) { %>
### 🔒 SECURITY CRITICAL

This document contains security-sensitive information. Handle with care.

**Threat Model:**
<% tp.file.cursor(1) %>

**Mitigations:**
<% tp.file.cursor(2) %>
<% } %>
```

---

## Creating New Templates

### When to Create a Template

Create a new template when:

✅ You create 3+ documents with similar structure
✅ A new document type emerges
✅ Existing templates don't fit your use case
✅ You want to enforce specific standards

### Template Creation Process

**Step 1: Design the Structure**

```markdown
1. Define purpose: What type of document is this?
2. Identify sections: What information does it contain?
3. Determine metadata: What frontmatter fields are needed?
4. List placeholders: What varies between instances?
5. Add examples: Include sample content for guidance
```

**Step 2: Create Template File**

```
1. Navigate to templates/ folder
2. Create new note
3. Name with prefix: category-doc-type.md
   Examples:
   - guide-api-reference.md
   - architecture-doc-microservice.md
   - report-performance-analysis.md
```

**Step 3: Write Template Content**

**Minimal Template Structure:**

```yaml
---
type: <% tp.system.suggester(["guide", "reference", "architecture"], ["guide", "reference", "architecture"]) %>
area: <% tp.system.prompt("Area (e.g., security, architecture)") %>
component: []
status: draft
audience: [<% tp.system.prompt("Primary audience") %>]
priority: medium
tags: [<% tp.file.cursor(1) %>]
version: 1.0.0
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
author: <% tp.system.prompt("Author") %>
---

# <% tp.file.title %>

**Purpose:** <% tp.file.cursor(2) %>

---

## Table of Contents

1. [Overview](#overview)
2. [<% tp.file.cursor(3) %>](#)
3. [Conclusion](#conclusion)

---

## Overview

<% tp.file.cursor(4) %>

---

## Conclusion

<% tp.file.cursor(5) %>

---

**Document Metadata:**

```yaml
Template metadata inserted above.
```
```

**Step 4: Test Template**

```
1. Create test note
2. Insert your template
3. Verify:
   ✅ Metadata generates correctly
   ✅ Placeholders work
   ✅ Cursors jump in logical order
   ✅ Dates auto-populate
   ✅ Prompts ask right questions
4. Refine as needed
```

**Step 5: Document Template**

Add entry to `templates/TEMPLATE_LIBRARY.md`:

```markdown
### guide-api-reference

**Purpose:** Document REST API endpoints and schemas

**Use When:**
- Documenting new API endpoints
- Creating API reference pages
- Specifying request/response formats

**Auto-Generated Fields:**
- `created_date` - Today's date
- `updated_date` - Today's date
- File title from filename

**Prompts:**
- Author name
- API version
- Primary audience

**Output Example:** `API_USER_LOGIN.md`

**See Also:** architecture-doc-integration-api
```

### Template Naming Conventions

**Pattern:** `{category}-doc-{type}.md`

**Categories:**
- `module-doc-` - Code/module documentation
- `architecture-doc-` - Architecture decisions
- `guide-` - User/developer guides
- `agent-doc-` - Agent reports
- `report-` - Analysis reports
- `reference-` - Reference materials

**Examples:**
- `guide-quickstart-feature.md`
- `architecture-doc-adr.md`
- `module-doc-core-system.md`
- `report-security-audit.md`

**See:** `templates/NAMING_CONVENTIONS.md` for full rules

---

## Templater Best Practices

### 1. Use Cursor Positions Wisely

**Good:** Logical tab order

```javascript
## Overview
<% tp.file.cursor(1) %>  ← First cursor (most important)

## Configuration
<% tp.file.cursor(2) %>  ← Second cursor

## Advanced
<% tp.file.cursor(3) %>  ← Third cursor
```

**Bad:** Random order

```javascript
## Overview
<% tp.file.cursor(3) %>  ← Jumps around confusingly

## Configuration
<% tp.file.cursor(1) %>

## Advanced
<% tp.file.cursor(2) %>
```

### 2. Provide Helpful Prompts

**Good:** Clear, specific

```javascript
<% tp.system.prompt("Component name (e.g., AIPersona, UserManager)") %>
<% tp.system.prompt("Priority: critical, high, medium, or low") %>
```

**Bad:** Vague

```javascript
<% tp.system.prompt("Name") %>
<% tp.system.prompt("Info") %>
```

### 3. Use Suggesters for Fixed Options

**Good:** Dropdown selection

```javascript
<% tp.system.suggester(
  ["critical", "high", "medium", "low"],
  ["critical", "high", "medium", "low"],
  false,
  "Select priority level"
) %>
```

**Bad:** Free text (invites errors)

```javascript
<% tp.system.prompt("Priority") %>
```

### 4. Auto-Generate Dates

**Always:**

```javascript
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
```

**Never:**

```javascript
created_date: 2026-04-20  ← Hardcoded, becomes incorrect
```

### 5. Include Examples and Guidance

**Good:** Helpful comments

```yaml
tags: [<% tp.file.cursor() %>]
# Example: [architecture, security, authentication, bcrypt]
```

**Bad:** No guidance

```yaml
tags: [<% tp.file.cursor() %>]
```

### 6. Validate Frontmatter Syntax

**Always test:**

```
1. Insert template
2. Switch to Preview mode
3. Check for errors
4. Fix YAML syntax issues
```

### 7. Keep Templates Updated

**Maintenance schedule:**

- Monthly: Review for outdated patterns
- After schema changes: Update metadata fields
- After tag taxonomy updates: Update tag examples
- When errors reported: Fix and document

---

## Template Syntax Reference

### Templater Basics

**Date/Time Functions:**

```javascript
<% tp.date.now("FORMAT") %>           // Current date/time
<% tp.date.tomorrow("YYYY-MM-DD") %>  // Tomorrow
<% tp.date.yesterday("YYYY-MM-DD") %> // Yesterday
<% tp.date.weekday("YYYY-MM-DD", 1) %> // Next Monday (0=Sunday, 1=Monday)

// Format options:
YYYY-MM-DD       → 2026-04-20
YYYY-MM-DD HH:mm → 2026-04-20 14:30
MMM DD, YYYY     → Apr 20, 2026
```

**File Functions:**

```javascript
<% tp.file.title %>           // Filename without .md
<% tp.file.path(true) %>      // Relative path
<% tp.file.folder(true) %>    // Parent folder
<% tp.file.creation_date() %> // File creation timestamp
<% tp.file.cursor(N) %>       // Cursor position N
```

**System Functions:**

```javascript
<% tp.system.prompt("Question") %>  // Text input prompt
<% tp.system.clipboard() %>         // Clipboard content

// Suggester (dropdown)
<% tp.system.suggester(
  ["Display 1", "Display 2"],  // Display options
  ["value1", "value2"],         // Return values
  false,                        // Allow multiple?
  "Prompt text"                 // Prompt
) %>
```

**Frontmatter Access:**

```javascript
<% tp.frontmatter.tags %>      // Access frontmatter.tags
<% tp.frontmatter.status %>    // Access frontmatter.status
```

**JavaScript Execution:**

```javascript
<%*
// Multi-line JavaScript
const author = await tp.system.prompt("Author");
const date = tp.date.now("YYYY-MM-DD");
tR += `author: ${author}\ndate: ${date}`;
%>
```

### Advanced Templater

**Conditional Content:**

```javascript
<%* if (tp.file.title.includes("SECURITY")) { %>
## 🔒 Security Notice
This document contains security-sensitive information.
<%* } %>
```

**Loops:**

```javascript
<%*
const tags = await tp.system.prompt("Tags (comma-separated)");
const tagArray = tags.split(",").map(t => t.trim());

for (let tag of tagArray) {
  tR += `- ${tag}\n`;
}
%>
```

**File Creation:**

```javascript
<%*
await tp.file.create_new(
  tp.file.find_tfile("template-name"),
  "New File Name",
  true,  // Open file?
  tp.file.folder(true)  // In same folder
);
%>
```

---

## Common Use Cases

### Use Case 1: Weekly Report Template

**Scenario:** Create weekly documentation progress reports

**Template:**

```yaml
---
type: report
area: documentation
status: active
audience: [contributor, architect]
priority: medium
tags: [report, weekly-update, documentation, progress]
version: 1.0.0
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
author: <% tp.system.prompt("Your name") %>
week_start: <% tp.date.weekday("YYYY-MM-DD", 1, -7) %>
week_end: <% tp.date.now("YYYY-MM-DD") %>
---

# Weekly Documentation Report: <% tp.date.now("YYYY-[W]WW") %>

**Reporting Period:** <% tp.date.weekday("YYYY-MM-DD", 1, -7) %> to <% tp.date.now("YYYY-MM-DD") %>

---

## Summary

<% tp.file.cursor(1) %>

## Documents Created This Week

- Document 1: <% tp.file.cursor(2) %>
- Document 2:
- Document 3:

## Documents Updated This Week

- Update 1: <% tp.file.cursor(3) %>
- Update 2:

## Challenges

<% tp.file.cursor(4) %>

## Next Week Goals

<% tp.file.cursor(5) %>
```

### Use Case 2: Meeting Notes Template

**Template:**

```yaml
---
type: reference
area: operations
status: active
audience: [contributor, developer]
priority: medium
tags: [meeting-notes, <% tp.system.prompt("Meeting type") %>]
version: 1.0.0
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
author: <% tp.system.prompt("Note taker") %>
meeting_date: <% tp.date.now("YYYY-MM-DD HH:mm") %>
attendees: [<% tp.file.cursor(1) %>]
---

# Meeting Notes: <% tp.file.title %>

**Date:** <% tp.date.now("YYYY-MM-DD HH:mm") %>
**Duration:** <% tp.system.prompt("Duration (e.g., 60 min)") %>
**Location:** <% tp.system.prompt("Location (e.g., Zoom, Room 301)") %>

---

## Attendees

- <% tp.file.cursor(2) %>

## Agenda

1. <% tp.file.cursor(3) %>
2.
3.

## Discussion Notes

### Topic 1: <% tp.file.cursor(4) %>

Notes here...

### Topic 2:

## Action Items

- [ ] <% tp.file.cursor(5) %> (Owner: , Due: )
- [ ]

## Next Meeting

**Date:** <% tp.date.now("YYYY-MM-DD", 7) %>
**Topics:**
```

### Use Case 3: Bug Report Template

**Template:**

```yaml
---
type: troubleshooting
area: [development, operations]
component: <% tp.system.prompt("Component name") %>
status: active
audience: [developer]
priority: <% tp.system.suggester(["critical", "high", "medium", "low"], ["critical", "high", "medium", "low"]) %>
tags: [bug, troubleshooting, <% tp.file.cursor(1) %>]
version: 1.0.0
created_date: <% tp.date.now("YYYY-MM-DD") %>
updated_date: <% tp.date.now("YYYY-MM-DD") %>
author: <% tp.system.prompt("Reporter") %>
bug_id: <% tp.system.prompt("Bug ID (if applicable)") %>
---

# Bug Report: <% tp.file.title %>

**Severity:** <% tp.system.suggester(["Critical", "High", "Medium", "Low"], ["critical", "high", "medium", "low"]) %>
**Reported By:** <% tp.system.prompt("Reporter") %>
**Reported Date:** <% tp.date.now("YYYY-MM-DD") %>

---

## Summary

<% tp.file.cursor(2) %>

## Steps to Reproduce

1. <% tp.file.cursor(3) %>
2.
3.

## Expected Behavior

<% tp.file.cursor(4) %>

## Actual Behavior

<% tp.file.cursor(5) %>

## Environment

- OS: <% tp.system.prompt("OS version") %>
- Python: <% tp.system.prompt("Python version") %>
- Application Version: <% tp.system.prompt("App version") %>

## Error Messages

```
<% tp.file.cursor(6) %>
```

## Workaround

<% tp.file.cursor(7) %>

## Proposed Solution

<% tp.file.cursor(8) %>

## Related Issues

- <% tp.file.cursor(9) %>
```

---

## Troubleshooting

### Problem: "Template not found"

**Solution:**

1. Check template folder setting
   - Settings → Templater → Template folder location
   - Should be: `templates/`

2. Verify template exists
   - Navigate to `templates/` in file explorer
   - Confirm file is there

3. Restart Obsidian
   - Close and reopen
   - Templater rescans folder

### Problem: "Syntax error in template"

**Solution:**

1. Check Templater syntax
   - Must be: `<% %>` not `{{ }}` or `<< >>`

2. Validate YAML frontmatter
   - Use YAML linter: http://www.yamllint.com/
   - Check for missing commas, quotes, colons

3. Test template in isolation
   - Create new note
   - Insert template
   - View in preview mode
   - Check console for errors (`Ctrl+Shift+I`)

### Problem: "Cursor positions not working"

**Solution:**

1. Enable cursor jumps
   - Settings → Templater → Options
   - Enable "Automatic jump to cursor"

2. Check cursor syntax
   - Correct: `<% tp.file.cursor(1) %>`
   - Wrong: `<% tp.file.cursor() %>` (missing number)

3. Remove duplicate cursors
   - Each cursor number used only once

### Problem: "Prompts not appearing"

**Solution:**

1. Check Templater enabled
   - Settings → Community Plugins
   - Templater should be ON

2. Verify prompt syntax
   - Correct: `<% tp.system.prompt("Question") %>`
   - Include quotes around question

3. Try system suggester instead
   - More reliable for predefined options

### Problem: "Dates generating incorrectly"

**Solution:**

1. Check date format string
   - `YYYY-MM-DD` not `YYYY-mm-dd` (mm is minutes)
   - `HH` for 24-hour, `hh` for 12-hour

2. Verify locale settings
   - Settings → Templater → Locale
   - Set to your region

3. Use static format
   - Always use ISO 8601: `YYYY-MM-DD`

---

## Summary Checklist

**Using Templates:**

- [ ] Templater plugin installed and enabled
- [ ] Template folder configured (`templates/`)
- [ ] Understand when to use each template
- [ ] Know how to fill in placeholders
- [ ] Can customize metadata before saving

**Creating Templates:**

- [ ] Design structure before coding
- [ ] Use consistent naming: `{category}-doc-{type}.md`
- [ ] Include complete frontmatter
- [ ] Add cursor positions in logical order
- [ ] Test template before using in production
- [ ] Document template in TEMPLATE_LIBRARY.md

**Best Practices:**

- [ ] Auto-generate dates with Templater
- [ ] Use suggesters for fixed options
- [ ] Provide clear prompt questions
- [ ] Include examples and guidance
- [ ] Validate YAML syntax
- [ ] Keep templates updated

---

**Next Steps:**

- **Practice:** Use 5 different templates this week
- **Customize:** Modify a template for your workflow
- **Create:** Build a custom template for repeated use cases
- **Reference:** Bookmark `templates/TEMPLATE_LIBRARY.md`

**Related Documentation:**

- [METADATA_GUIDE.md](METADATA_GUIDE.md) - Understanding frontmatter
- [TUTORIAL_CREATING_DOCUMENTS.md](TUTORIAL_CREATING_DOCUMENTS.md) - Step-by-step document creation
- `templates/TEMPLATE_USAGE_GUIDE.md` - Detailed template usage
- `templates/NAMING_CONVENTIONS.md` - File naming rules

---

**Document Metadata:**

```yaml
---
type: guide
area: documentation
component: vault
status: active
audience: [developer, contributor]
priority: high
tags: [templates, templater, automation, documentation, guide]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 3600
dependencies:
  - METADATA_GUIDE.md
  - TAG_REFERENCE.md
  - templates/TEMPLATE_LIBRARY.md
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
