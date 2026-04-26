---
type: guide
tags:
  - p2-root
  - status
  - guide
  - obsidian
  - templater
  - setup
created: 2024-12-20
last_verified: 2026-04-20
status: current
related_systems:
  - obsidian-vault
  - templater-plugin
  - template-automation
stakeholders:
  - obsidian-team
  - documentation-team
report_type: guide
supersedes: []
review_cycle: as-needed
---

# Templater Setup Guide for Project-AI

**Version:** 1.0  
**Last Updated:** 2024-12-20  
**Plugin Version:** 2.19.1  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation Summary](#installation-summary)
3. [Configuration Details](#configuration-details)
4. [Template Directory Structure](#template-directory-structure)
5. [Available Templates](#available-templates)
6. [Using Templates](#using-templates)
7. [Templater Syntax Guide](#templater-syntax-guide)
8. [Advanced Features](#advanced-features)
9. [User Scripts](#user-scripts)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Integration with Project-AI](#integration-with-project-ai)

---

## 🎯 Overview

### What is Templater?

Templater is a powerful template language plugin for Obsidian that allows you to create dynamic notes with intelligent automation. It extends the basic Obsidian template functionality with:

- **Dynamic Variables**: Access file metadata, dates, user input, and system information
- **JavaScript Execution**: Run custom JavaScript code within templates
- **User Scripts**: Create reusable custom functions in external JavaScript files
- **Conditional Logic**: Include/exclude content based on conditions
- **Loops**: Generate repetitive content programmatically
- **Async Operations**: Execute asynchronous operations like API calls
- **Auto-completion**: Automatically populate templates when files are created

### Why Use Templater in Project-AI?

Project-AI is a sophisticated AI-powered desktop application with extensive documentation needs. Templater helps maintain consistency across:

- **Code Documentation**: Standardized documentation for Python modules, classes, and functions
- **Project Management**: Uniform project tracking, meeting notes, and task management
- **Daily Operations**: Consistent daily notes, logs, and reports
- **Development Workflows**: Standardized bug reports, feature requests, and technical specifications

### Installation Verification

✅ **Templater Version**: 2.19.1 (Latest)  
✅ **Plugin Status**: Enabled  
✅ **Templates Folder**: `templates/` (configured)  
✅ **User Scripts Folder**: `templates/scripts/` (configured)  
✅ **Sample Templates**: 5 production-ready templates installed  
✅ **Custom Functions**: 10+ utility functions available

---

## 📦 Installation Summary

### What Was Installed

The following components have been successfully installed and configured:

#### 1. Templater Plugin
- **Location**: `.obsidian/plugins/templater-obsidian/`
- **Files Installed**:
  - `main.js` (319,145 bytes) - Core plugin logic
  - `manifest.json` (331 bytes) - Plugin metadata
  - `styles.css` (4,932 bytes) - Plugin styling
  - `data.json` (548 bytes) - Plugin configuration

#### 2. Directory Structure
```
Project-AI-main/
├── .obsidian/
│   ├── plugins/
│   │   └── templater-obsidian/
│   │       ├── main.js
│   │       ├── manifest.json
│   │       ├── styles.css
│   │       └── data.json
│   └── community-plugins.json (updated)
└── templates/
    ├── scripts/
    │   └── utils.js
    ├── basic-note-template.md
    ├── meeting-notes-template.md
    ├── daily-note-template.md
    ├── project-template.md
    └── code-documentation-template.md
```

#### 3. Sample Templates
Five production-ready templates covering common use cases:
1. **Basic Note Template** - General-purpose note structure
2. **Meeting Notes Template** - Structured meeting documentation
3. **Daily Note Template** - Daily journaling and task tracking
4. **Project Template** - Comprehensive project management
5. **Code Documentation Template** - Technical code documentation

#### 4. User Scripts
Custom JavaScript utilities in `templates/scripts/utils.js`:
- ID generation
- Date formatting
- Git integration
- Array utilities
- Text analysis
- Currency formatting
- Progress bars

---

## ⚙️ Configuration Details

### Plugin Settings

The Templater plugin is configured with the following settings in `.obsidian/plugins/templater-obsidian/data.json`:

```json
{
  "command_timeout": 5,
  "templates_folder": "templates",
  "templates_pairs": [["", ""]],
  "trigger_on_file_creation": true,
  "auto_jump_to_cursor": true,
  "enable_system_commands": false,
  "shell_path": "",
  "user_scripts_folder": "templates/scripts",
  "enable_folder_templates": true,
  "folder_templates": [{"folder": "", "template": ""}],
  "syntax_highlighting": true,
  "enabled_templates_hotkeys": [""],
  "startup_templates": [""]
}
```

### Key Configuration Options Explained

| Setting | Value | Purpose |
|---------|-------|---------|
| `templates_folder` | `templates` | Where template files are stored |
| `user_scripts_folder` | `templates/scripts` | Where custom JavaScript functions live |
| `trigger_on_file_creation` | `true` | Auto-apply templates when creating files |
| `auto_jump_to_cursor` | `true` | Jump to cursor position after template execution |
| `enable_system_commands` | `false` | **Security**: Disabled for safety (prevents arbitrary shell commands) |
| `enable_folder_templates` | `true` | Allows different templates for different folders |
| `syntax_highlighting` | `true` | Syntax highlighting for template code |
| `command_timeout` | `5` | Timeout (seconds) for template execution |

### Security Considerations

**🔒 System Commands Disabled**: The `enable_system_commands` setting is intentionally set to `false` to prevent arbitrary shell command execution. This aligns with Project-AI's security-first approach.

If you need system integration, use the **user scripts** feature instead, which provides controlled JavaScript execution in a safer environment.

---

## 📁 Template Directory Structure

### Recommended Organization

```
templates/
├── scripts/                    # Custom JavaScript functions
│   ├── utils.js               # General utilities
│   ├── project-ai-utils.js    # Project-AI specific functions (future)
│   └── api-helpers.js         # API integration helpers (future)
│
├── notes/                      # Note templates
│   ├── basic-note-template.md
│   ├── meeting-notes-template.md
│   └── daily-note-template.md
│
├── projects/                   # Project management templates
│   ├── project-template.md
│   ├── sprint-template.md     # (future)
│   └── roadmap-template.md    # (future)
│
├── code/                       # Code documentation templates
│   ├── code-documentation-template.md
│   ├── api-reference-template.md  # (future)
│   └── class-diagram-template.md  # (future)
│
├── reports/                    # Report templates
│   ├── weekly-report.md       # (future)
│   ├── security-audit.md      # (future)
│   └── performance-report.md  # (future)
│
└── workflows/                  # Workflow templates
    ├── bug-report.md          # (future)
    ├── feature-request.md     # (future)
    └── code-review.md         # (future)
```

### Current Structure (v1.0)

As of this installation, the structure is flat for simplicity:

```
templates/
├── scripts/
│   └── utils.js
├── basic-note-template.md
├── meeting-notes-template.md
├── daily-note-template.md
├── project-template.md
└── code-documentation-template.md
```

**Note**: You can organize templates into subdirectories at any time. Templater will find them as long as they're under the `templates/` root.

---

## 📝 Available Templates

### 1. Basic Note Template

**File**: `templates/basic-note-template.md`  
**Use Case**: General-purpose notes, documentation, brainstorming

**Features**:
- Automatic title, creation date, modification date
- YAML frontmatter with metadata
- Objectives checklist
- Related documents section
- Auto-generated metadata table

**When to Use**:
- Creating general documentation
- Quick notes or ideas
- Reference materials
- Knowledge base articles

**Example Output**:
```markdown
---
title: "My New Note"
created: 2024-12-20 10:30
modified: 2024-12-20 10:30
tags: [sample, templater]
author: Project-AI
status: draft
---

# My New Note

## 📋 Overview
[User provides description]

## 🎯 Objectives
- [ ] Objective 1
...
```

---

### 2. Meeting Notes Template

**File**: `templates/meeting-notes-template.md`  
**Use Case**: Recording meeting discussions, action items, decisions

**Features**:
- Auto-calculated meeting end time
- Attendee list with prompt
- Agenda items with user input
- Action items table with assignees and due dates
- Follow-up meeting creation option
- Automatic next meeting scheduling

**When to Use**:
- Team meetings
- Client calls
- Sprint planning sessions
- Retrospectives
- One-on-ones

**Dynamic Elements**:
- Prompts for location, attendees, agenda items
- Auto-calculates meeting end time (60 minutes after start)
- Suggests creating follow-up meeting note
- Links to previous/next meetings

**Example Output**:
```markdown
---
title: "Meeting Notes - Sprint Planning Q1"
date: 2024-12-20
time: 14:00
type: meeting
attendees: []
tags: [meeting, notes]
---

# 🗓️ Meeting: Sprint Planning Q1

**Date:** Friday, December 20, 2024
**Time:** 14:00 - 15:00
**Location:** Conference Room A

## 👥 Attendees
- Alice Johnson
- Bob Smith
- Carol White
...
```

---

### 3. Daily Note Template

**File**: `templates/daily-note-template.md`  
**Use Case**: Daily journaling, task tracking, reflection

**Features**:
- Navigation links to yesterday/tomorrow
- Morning review (weather, energy, mood)
- Priority tasks with star ratings
- Task categories (high/medium/low priority)
- Evening reflection section
- Auto-suggestion to create tomorrow's note (after 8 PM)
- Weekly/monthly review links
- Auto-calculated stats (word count, links)

**When to Use**:
- Daily planning and review
- Personal journaling
- Time tracking
- Habit tracking
- Productivity monitoring

**Interactive Elements**:
- Energy level selector (5 levels)
- Mood selector (5 options)
- Priority task prompts
- Evening reflection prompts
- Auto-creates tomorrow's note if requested

**Example Output**:
```markdown
---
title: "Daily Note - 2024-12-20"
date: 2024-12-20
day: Friday
week: 2024-W51
tags: [daily-note, journal]
---

# 📅 Friday, December 20, 2024

[[2024-12-19|← Yesterday]] | [[2024-12-21|Tomorrow →]]

## 🌅 Morning Review
**Weather:** Sunny, 72°F
**Energy Level:** ⚡⚡⚡⚡ Good
**Mood:** 😊 Happy

## 🎯 Today's Priorities
1. [ ] **Complete Templater setup** ⭐⭐⭐
2. [ ] **Review code documentation** ⭐⭐
3. [ ] **Team standup** ⭐
...
```

---

### 4. Project Template

**File**: `templates/project-template.md`  
**Use Case**: Comprehensive project management and tracking

**Features**:
- Interactive project status selector
- Priority level selection
- OKR (Objectives and Key Results) framework
- Team and stakeholder tracking
- Timeline and milestones table
- Task breakdown by phase
- Risk assessment matrix
- Progress metrics with Dataview queries
- Auto-calculated days remaining
- Optional project folder creation

**When to Use**:
- New project initialization
- Project planning
- Stakeholder communication
- Progress tracking
- Post-mortem documentation

**Interactive Selectors**:
- Status: Active, Planning, On Hold, Completed, Cancelled
- Priority: High, Medium, Low
- Risk probability and impact levels

**Dataview Integration**:
```dataview
TABLE status, priority, start_date, due_date
FROM "projects"
WHERE file.name = this.file.name
```

**Example Output**:
```markdown
---
title: "Project: Project-AI Dashboard Redesign"
created: 2024-12-20
type: project
status: active
priority: high
start_date: 2024-12-20
due_date: 2025-01-31
tags: [project]
---

# 🚀 Project-AI Dashboard Redesign

## 📋 Project Overview
**Description:** Modernize the PyQt6 dashboard with improved UX
**Status:** 🟢 Active
**Priority:** 🔴 High
...
```

---

### 5. Code Documentation Template

**File**: `templates/code-documentation-template.md`  
**Use Case**: Technical documentation for code modules, classes, functions

**Features**:
- Language selector (Python, JavaScript, TypeScript, Java, C++, Go, Rust, Other)
- Architecture and component documentation
- Parameter and return value tables
- Data flow diagrams (Mermaid)
- Test coverage tracking
- Security considerations
- Performance analysis (Big O notation)
- Usage examples with code blocks
- Change log
- Maintainer information

**When to Use**:
- Documenting new modules
- API documentation
- Class/interface documentation
- Function reference guides
- Architecture documentation

**Technical Sections**:
- Class/module structure
- Dependencies
- Key components with parameter tables
- Data flow diagrams
- Configuration options
- Test cases
- Known issues and limitations
- Security considerations
- Performance metrics
- Complexity analysis

**Example Output**:
```markdown
---
title: "Code Documentation - AIPersona Class"
created: 2024-12-20
type: code-documentation
language: python
project: Project-AI
tags: [code, documentation, python]
---

# 💻 AIPersona Class

## 📁 File Information
**File Path:** `src/app/core/ai_systems.py`
**Language:** python
**Project:** Project-AI
**Last Modified:** 2024-12-20

## 📋 Overview
### Purpose
Manages the AI personality system with 8 trait dimensions...
```

---

## 🚀 Using Templates

### Method 1: Ribbon Icon

1. Click the Templater icon (📋) in the left ribbon
2. Select a template from the dropdown
3. Template will be inserted at cursor position or replace file content

### Method 2: Command Palette

1. Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
2. Type "Templater"
3. Select "Templater: Insert Template"
4. Choose your template

### Method 3: Folder Templates

Configure folder-specific templates in Templater settings:

1. Settings → Templater → Folder Templates
2. Add rule: `projects/` folder → `project-template.md`
3. New files in `projects/` automatically use project template

**Example Configuration**:
```json
{
  "folder_templates": [
    {"folder": "projects", "template": "project-template.md"},
    {"folder": "meetings", "template": "meeting-notes-template.md"},
    {"folder": "daily", "template": "daily-note-template.md"},
    {"folder": "code-docs", "template": "code-documentation-template.md"}
  ]
}
```

### Method 4: Hotkeys

Assign keyboard shortcuts to frequently used templates:

1. Settings → Hotkeys
2. Search "Templater"
3. Assign key combinations to specific templates

**Recommended Hotkeys**:
- `Ctrl+Shift+D` → Daily Note Template
- `Ctrl+Shift+M` → Meeting Notes Template
- `Ctrl+Shift+P` → Project Template

### Method 5: Create from Template

1. Right-click in file explorer
2. Select "Create new note from template"
3. Choose template
4. Enter filename

---

## 📚 Templater Syntax Guide

### Basic Syntax

Templater uses `<% %>` delimiters for code execution:

```markdown
<!-- Simple variable -->
<% tp.date.now("YYYY-MM-DD") %>

<!-- Expression that doesn't output -->
<%* /* JavaScript code */ %>

<!-- Expression that outputs to template -->
<%* tR += "output text" %>
```

### Internal Functions

Templater provides built-in function modules:

#### tp.file - File Operations

```markdown
<!-- File title -->
<% tp.file.title %>

<!-- File creation date -->
<% tp.file.creation_date("YYYY-MM-DD HH:mm") %>

<!-- File modification date -->
<% tp.file.last_modified_date("YYYY-MM-DD HH:mm") %>

<!-- File path -->
<% tp.file.path() %>

<!-- Parent folder -->
<% tp.file.folder() %>

<!-- File content -->
<% tp.file.content %>

<!-- Create new file -->
<%* await tp.file.create_new("template.md", "new-file-name") %>

<!-- Move file -->
<%* await tp.file.move("new/path/file.md") %>

<!-- Rename file -->
<%* await tp.file.rename("new-name.md") %>
```

#### tp.date - Date/Time Operations

```markdown
<!-- Current date -->
<% tp.date.now("YYYY-MM-DD") %>

<!-- Date with offset -->
<% tp.date.now("YYYY-MM-DD", 7) %> <!-- 7 days from now -->
<% tp.date.now("YYYY-MM-DD", -7) %> <!-- 7 days ago -->

<!-- Format options (using moment.js) -->
<% tp.date.now("dddd, MMMM DD, YYYY") %> <!-- Friday, December 20, 2024 -->
<% tp.date.now("HH:mm:ss") %> <!-- 14:30:45 -->
<% tp.date.now("YYYY-[W]WW") %> <!-- 2024-W51 -->

<!-- Tomorrow -->
<% tp.date.tomorrow("YYYY-MM-DD") %>

<!-- Yesterday -->
<% tp.date.yesterday("YYYY-MM-DD") %>

<!-- Weekday -->
<% tp.date.weekday("YYYY-MM-DD", 0) %> <!-- Next Sunday (0=Sunday) -->
<% tp.date.weekday("YYYY-MM-DD", 1) %> <!-- Next Monday (1=Monday) -->
```

#### tp.frontmatter - YAML Frontmatter

```markdown
<!-- Access frontmatter values -->
<% tp.frontmatter.title %>
<% tp.frontmatter.status %>
<% tp.frontmatter.tags %>

<!-- Example: Use frontmatter in template -->
Current status: <% tp.frontmatter.status %>
Priority: <% tp.frontmatter.priority %>
```

#### tp.system - User Interaction

```markdown
<!-- Prompt for user input -->
<% tp.system.prompt("Enter description") %>

<!-- Prompt with default value -->
<% tp.system.prompt("Enter name", "Default Name") %>

<!-- Multiple choice suggester -->
<% tp.system.suggester(
  ["Option 1", "Option 2", "Option 3"],
  ["value1", "value2", "value3"]
) %>

<!-- Example: Priority selector -->
<% tp.system.suggester(
  ["🔴 High", "🟡 Medium", "🟢 Low"],
  ["high", "medium", "low"]
) %>

<!-- Clipboard content -->
<% tp.system.clipboard() %>
```

#### tp.config - Obsidian Configuration

```markdown
<!-- Active file -->
<% tp.config.active_file %>

<!-- Target file (when inserting template into existing file) -->
<% tp.config.target_file %>

<!-- Run mode -->
<% tp.config.run_mode %> <!-- CreateNewFromTemplate, AppendActiveFile, etc. -->
```

#### tp.web - Web Operations

```markdown
<!-- Get daily quote from API -->
<%* 
const response = await tp.obsidian.request({
  url: "https://api.quotable.io/random"
});
const data = JSON.parse(response);
tR += `> ${data.content}\n> — ${data.author}`;
%>

<!-- Fetch data from URL -->
<%* 
const html = await tp.obsidian.request({
  url: "https://example.com"
});
%>
```

---

### Advanced Syntax

#### Conditional Logic

```markdown
<%* if (condition) { %>
Content if true
<%* } else { %>
Content if false
<%* } %>

<!-- Example: Show section based on status -->
<%* if (tp.frontmatter.status === "active") { %>
## 🟢 Active Project
Current tasks...
<%* } else { %>
## 🔴 Inactive Project
This project is on hold.
<%* } %>
```

#### Loops

```markdown
<%* 
const items = ["Item 1", "Item 2", "Item 3"];
for (const item of items) {
  tR += `- ${item}\n`;
}
%>

<!-- Example: Generate task list -->
<%* 
const tasks = await tp.system.prompt("Enter tasks (comma-separated)");
tasks.split(",").forEach(task => {
  tR += `- [ ] ${task.trim()}\n`;
});
%>
```

#### Async/Await Operations

```markdown
<%*
// Async function call
const result = await someAsyncFunction();
tR += result;
%>

<!-- Example: Create multiple files -->
<%*
const fileNames = ["file1", "file2", "file3"];
for (const name of fileNames) {
  await tp.file.create_new(
    tp.file.find_tfile("template.md"),
    name
  );
}
%>
```

#### Complex Calculations

```markdown
<%*
// Calculate project duration
const start = new Date(tp.frontmatter.start_date);
const end = new Date(tp.frontmatter.due_date);
const duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
tR += `Duration: ${duration} days`;
%>

<!-- Example: Progress calculation -->
<%*
const total = 10;
const completed = 7;
const percentage = Math.round((completed / total) * 100);
const bar = "█".repeat(completed) + "░".repeat(total - completed);
tR += `Progress: [${bar}] ${percentage}%`;
%>
```

---

## 🔧 Advanced Features

### 1. User Scripts

User scripts are custom JavaScript functions stored in `templates/scripts/` that can be called from any template.

**Benefits**:
- Reusable code across templates
- Complex logic separated from templates
- Easier maintenance and testing
- Access to Node.js modules

**Installed User Script**: `templates/scripts/utils.js`

**Available Functions**:

```markdown
<!-- Generate unique ID -->
<% tp.user.generate_id() %>
<!-- Output: 1234567890ab-c3d4e -->

<!-- Relative date formatting -->
<% tp.user.relative_date("2024-01-01") %>
<!-- Output: "3 weeks ago" or "2 days from now" -->

<!-- Current git branch -->
<% tp.user.git_branch() %>
<!-- Output: "main" or "feature/templater-setup" -->

<!-- Random item from array -->
<% tp.user.random_from_array(["Red", "Green", "Blue"]) %>
<!-- Output: "Green" (random) -->

<!-- Word count -->
<% tp.user.word_count(tp.file.content) %>
<!-- Output: 1234 -->

<!-- Generate table of contents -->
<%* tR += tp.user.generate_toc(tp.file.content) %>
<!-- Output: Auto-generated TOC from headings -->

<!-- Format currency -->
<% tp.user.format_currency(1234.56, "USD") %>
<!-- Output: "$1,234.56" -->

<!-- Days between dates -->
<% tp.user.days_between("2024-01-01", "2024-12-31") %>
<!-- Output: 365 -->

<!-- Current season -->
<% tp.user.get_season() %>
<!-- Output: "Winter" (based on current date) -->

<!-- Progress bar -->
<% tp.user.progress_bar(75, 20) %>
<!-- Output: [███████████████░░░░░] 75% -->
```

**Creating Your Own User Scripts**:

1. Create a new JavaScript file in `templates/scripts/`
2. Define functions using standard JavaScript
3. Export functions using `module.exports`
4. Call functions using `tp.user.function_name()`

**Example**: `templates/scripts/project-ai-utils.js`

```javascript
// Project-AI specific utilities

function get_ai_persona_mood() {
    // Read from data/ai_persona/state.json
    const fs = require('fs');
    const path = 'data/ai_persona/state.json';
    
    try {
        const data = JSON.parse(fs.readFileSync(path, 'utf8'));
        return data.current_mood || 'neutral';
    } catch (error) {
        return 'unknown';
    }
}

function format_python_class(className, methods) {
    let output = `class ${className}:\n`;
    output += `    """${className} class documentation"""\n\n`;
    
    methods.forEach(method => {
        output += `    def ${method}(self):\n`;
        output += `        """${method} method documentation"""\n`;
        output += `        pass\n\n`;
    });
    
    return output;
}

module.exports = {
    get_ai_persona_mood,
    format_python_class
};
```

**Usage in Template**:

```markdown
Current AI Mood: <% tp.user.get_ai_persona_mood() %>

<%* tR += tp.user.format_python_class("MyClass", ["method1", "method2"]) %>
```

---

### 2. Folder Templates

Automatically apply templates when creating files in specific folders.

**Configuration** (in `.obsidian/plugins/templater-obsidian/data.json`):

```json
{
  "enable_folder_templates": true,
  "folder_templates": [
    {"folder": "projects", "template": "project-template.md"},
    {"folder": "meetings", "template": "meeting-notes-template.md"},
    {"folder": "daily", "template": "daily-note-template.md"},
    {"folder": "code-docs", "template": "code-documentation-template.md"}
  ]
}
```

**How It Works**:
1. Create a new file in `projects/` folder
2. Templater automatically inserts `project-template.md`
3. No manual template selection needed

**Benefits**:
- Consistent structure within folders
- Faster note creation
- Reduced errors (no forgetting to apply template)

---

### 3. Startup Templates

Run templates when Obsidian starts (useful for dashboards, habit trackers).

**Configuration**:

```json
{
  "startup_templates": [
    "templates/startup-dashboard.md"
  ]
}
```

**Use Cases**:
- Daily dashboard with stats
- Habit tracker checklist
- Task overview
- Morning routine

---

### 4. Template Hotkeys

Assign keyboard shortcuts to templates for instant access.

**Setup**:
1. Settings → Hotkeys
2. Search "Templater: Insert"
3. Assign keys to "Templater: Insert <template-name>"

**Recommended Shortcuts**:
- `Ctrl+Shift+D` → Daily Note
- `Ctrl+Shift+M` → Meeting Notes
- `Ctrl+Shift+P` → Project
- `Ctrl+Shift+C` → Code Documentation
- `Ctrl+Shift+N` → Basic Note

---

### 5. Dynamic Template Selection

Use JavaScript to choose templates based on conditions.

**Example**: Different templates based on day of week

```markdown
<%*
const day = tp.date.now("dddd");
let template;

if (day === "Monday") {
  template = "weekly-planning-template.md";
} else if (day === "Friday") {
  template = "weekly-review-template.md";
} else {
  template = "daily-note-template.md";
}

const content = await tp.file.include(tp.file.find_tfile(template));
tR += content;
%>
```

---

### 6. Template Chaining

Include one template inside another for composition.

**Example**: `templates/report-template.md`

```markdown
# Report

## Header
<%* tR += await tp.file.include(tp.file.find_tfile("header-template.md")) %>

## Content
...

## Footer
<%* tR += await tp.file.include(tp.file.find_tfile("footer-template.md")) %>
```

**Benefits**:
- DRY (Don't Repeat Yourself)
- Consistent components across templates
- Easier maintenance

---

## 🏆 Best Practices

### 1. Template Naming Conventions

**Use Descriptive Names**:
- ✅ `meeting-notes-template.md`
- ✅ `daily-note-template.md`
- ❌ `template1.md`
- ❌ `temp.md`

**Suffix with "-template"**:
- Makes templates easy to identify
- Prevents confusion with actual notes

**Use Kebab-Case**:
- Lowercase with hyphens
- Cross-platform compatible
- URL-friendly

---

### 2. YAML Frontmatter Standards

**Always Include**:
- `title`: Note title
- `created`: Creation date
- `type`: Note type (meeting, project, daily-note, etc.)
- `tags`: Relevant tags

**Optional but Recommended**:
- `modified`: Last modification date
- `status`: Status (draft, active, complete)
- `priority`: Priority level
- `author`: Creator name

**Example**:
```yaml
---
title: "My Note"
created: 2024-12-20
modified: 2024-12-20
type: note
status: draft
priority: medium
tags: [tag1, tag2]
author: Project-AI
---
```

---

### 3. User Input Best Practices

**Provide Defaults**:
```markdown
<!-- Good: Default value provided -->
<% tp.system.prompt("Enter name", "Default Name") %>

<!-- Less ideal: No default -->
<% tp.system.prompt("Enter name") %>
```

**Use Suggesters for Constrained Input**:
```markdown
<!-- Good: Limited options -->
<% tp.system.suggester(["High", "Medium", "Low"], ["high", "medium", "low"]) %>

<!-- Bad: Free text for status -->
<% tp.system.prompt("Enter status (active/inactive/complete)") %>
```

**Group Related Prompts**:
```markdown
<!-- Prompt once, parse later -->
<%*
const projectInfo = tp.system.prompt("Enter: name,status,priority (comma-separated)");
const [name, status, priority] = projectInfo.split(",").map(s => s.trim());
%>
```

---

### 4. Error Handling

**Always Handle Async Errors**:
```markdown
<%*
try {
  const result = await riskyOperation();
  tR += result;
} catch (error) {
  tR += `Error: ${error.message}`;
}
%>
```

**Validate User Input**:
```markdown
<%*
const dateInput = tp.system.prompt("Enter date (YYYY-MM-DD)");
const isValid = /^\d{4}-\d{2}-\d{2}$/.test(dateInput);

if (isValid) {
  tR += `Valid date: ${dateInput}`;
} else {
  tR += `Invalid date format. Please use YYYY-MM-DD.`;
}
%>
```

---

### 5. Performance Optimization

**Cache Expensive Operations**:
```markdown
<%*
// Don't do this in a loop:
for (let i = 0; i < 10; i++) {
  const mood = tp.user.get_ai_persona_mood(); // Reads file 10 times
  tR += mood;
}

// Do this instead:
const mood = tp.user.get_ai_persona_mood(); // Read once
for (let i = 0; i < 10; i++) {
  tR += mood;
}
%>
```

**Limit API Calls**:
```markdown
<%*
// Cache API responses
let quote = "";
try {
  const response = await tp.obsidian.request({
    url: "https://api.quotable.io/random"
  });
  quote = JSON.parse(response).content;
} catch (error) {
  quote = "Failed to load quote";
}
tR += quote;
%>
```

---

### 6. Documentation Within Templates

**Add Comments**:
```markdown
<%* 
// This section calculates project duration
const start = new Date(tp.frontmatter.start_date);
const end = new Date(tp.frontmatter.due_date);
const duration = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
tR += `Duration: ${duration} days`;
%>
```

**Explain Complex Logic**:
```markdown
<%*
// Auto-suggest creating tomorrow's note after 8 PM
const currentHour = new Date().getHours();
if (currentHour >= 20) {
  // Ask user if they want to create tomorrow's note
  const createTomorrow = await tp.system.suggester(
    ["Yes", "No"],
    [true, false]
  );
  
  if (createTomorrow) {
    const tomorrow = tp.date.now("YYYY-MM-DD", 1);
    await tp.file.create_new(
      tp.file.find_tfile("daily-note-template.md"),
      tomorrow
    );
  }
}
%>
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Template Not Executing

**Symptoms**:
- Template code appears as raw text: `<% tp.date.now() %>`
- No prompts appear
- Template doesn't expand

**Solutions**:

1. **Check Plugin Status**:
   - Settings → Community Plugins → Ensure Templater is enabled
   - Look for checkmark next to "Templater"

2. **Verify Template Folder**:
   - Settings → Templater → Template folder location
   - Should be: `templates`
   - Check that templates actually exist in this folder

3. **Restart Obsidian**:
   - Close and reopen Obsidian
   - Sometimes needed after installing/updating plugins

4. **Check Template Syntax**:
   ```markdown
   <!-- Wrong: Single % -->
   < % tp.date.now() % >
   
   <!-- Correct: Double %% -->
   <% tp.date.now() %>
   ```

5. **Look for JavaScript Errors**:
   - Press `Ctrl+Shift+I` to open Developer Console
   - Check for red error messages
   - Look in Console tab

---

#### Issue 2: User Scripts Not Working

**Symptoms**:
- `tp.user.function_name is not a function`
- Custom functions return undefined
- No functions available in `tp.user`

**Solutions**:

1. **Verify User Scripts Folder**:
   - Settings → Templater → User script functions folder
   - Should be: `templates/scripts`
   - Ensure `utils.js` exists in this folder

2. **Check Export Syntax**:
   ```javascript
   // Wrong: No export
   function myFunction() {
       return "value";
   }
   
   // Correct: Exported
   function myFunction() {
       return "value";
   }
   
   module.exports = {
       myFunction
   };
   ```

3. **Validate JavaScript Syntax**:
   - Open `templates/scripts/utils.js`
   - Check for syntax errors (missing brackets, quotes, etc.)
   - Test JavaScript in Developer Console

4. **Restart Required**:
   - After adding new user scripts, restart Obsidian
   - Templater caches scripts on startup

5. **Check File Permissions**:
   - Ensure Obsidian can read JavaScript files
   - On Unix/Mac: `chmod 644 templates/scripts/*.js`

---

#### Issue 3: Prompts Not Appearing

**Symptoms**:
- `tp.system.prompt()` doesn't show dialog
- `tp.system.suggester()` returns undefined
- Template executes but skips prompts

**Solutions**:

1. **Check Run Mode**:
   - Prompts only work in interactive mode
   - Don't work in startup templates or batch operations

2. **Await Async Prompts**:
   ```markdown
   <!-- Wrong: Missing await -->
   <%*
   const name = tp.system.prompt("Name");
   tR += name; // undefined
   %>
   
   <!-- Correct: Use await -->
   <%*
   const name = await tp.system.prompt("Name");
   tR += name; // works
   %>
   ```

3. **Verify Suggester Syntax**:
   ```markdown
   <!-- Wrong: Mismatched arrays -->
   <% tp.system.suggester(
     ["Option 1", "Option 2"],
     ["value1"] // Only 1 value for 2 options
   ) %>
   
   <!-- Correct: Matching arrays -->
   <% tp.system.suggester(
     ["Option 1", "Option 2"],
     ["value1", "value2"]
   ) %>
   ```

4. **Check for Blocking Code**:
   - Long-running code before prompt may cause timeout
   - Move prompts to beginning of template

---

#### Issue 4: Dates Formatting Wrong

**Symptoms**:
- Date shows as `Invalid date`
- Format doesn't match expected output
- Timezone issues

**Solutions**:

1. **Use Correct Format Tokens**:
   ```markdown
   <!-- Moment.js format tokens -->
   <% tp.date.now("YYYY-MM-DD") %>     <!-- 2024-12-20 -->
   <% tp.date.now("dddd, MMMM DD") %>  <!-- Friday, December 20 -->
   <% tp.date.now("HH:mm:ss") %>       <!-- 14:30:45 -->
   
   <!-- Wrong: strftime tokens (not supported) -->
   <% tp.date.now("%Y-%m-%d") %>       <!-- Won't work -->
   ```

2. **Check Offset Parameter**:
   ```markdown
   <!-- Offset is in days, not months -->
   <% tp.date.now("YYYY-MM-DD", 7) %>  <!-- 7 days from now -->
   <% tp.date.now("YYYY-MM-DD", -7) %> <!-- 7 days ago -->
   ```

3. **Reference Moment.js Docs**:
   - Templater uses moment.js for date formatting
   - See: https://momentjs.com/docs/#/displaying/format/

---

#### Issue 5: File Operations Failing

**Symptoms**:
- `tp.file.create_new()` doesn't create file
- `tp.file.move()` fails silently
- File path errors

**Solutions**:

1. **Use Await for Async Operations**:
   ```markdown
   <%*
   // Wrong: Missing await
   tp.file.create_new("template.md", "new-file");
   
   // Correct: Await the promise
   await tp.file.create_new("template.md", "new-file");
   %>
   ```

2. **Check File Paths**:
   ```markdown
   <%*
   // Relative to vault root
   await tp.file.create_new(
     tp.file.find_tfile("template.md"), // Template
     "folder/new-file"                   // Destination
   );
   %>
   ```

3. **Verify Template Exists**:
   ```markdown
   <%*
   const templateFile = tp.file.find_tfile("missing-template.md");
   if (!templateFile) {
     tR += "Template not found!";
   } else {
     await tp.file.create_new(templateFile, "new-file");
   }
   %>
   ```

4. **Handle Folder Creation**:
   ```markdown
   <%*
   // Create folder if it doesn't exist
   const folderPath = "projects/2024";
   await tp.app.vault.createFolder(folderPath).catch(() => {});
   await tp.file.create_new(template, `${folderPath}/new-file`);
   %>
   ```

---

#### Issue 6: System Commands Not Working

**Symptoms**:
- Shell commands don't execute
- `tp.system.command()` returns error

**Solution**:

**By Design**: System commands are **disabled** for security in this installation.

```json
{
  "enable_system_commands": false
}
```

**Alternatives**:
1. Use **user scripts** with Node.js `child_process`
2. Use **Obsidian plugins** for system integration
3. Enable carefully (security risk) in Settings → Templater

**Example with User Scripts** (if system commands needed):

```javascript
// templates/scripts/system-utils.js
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

async function runCommand(command) {
    try {
        const { stdout, stderr } = await execPromise(command);
        return stdout || stderr;
    } catch (error) {
        return `Error: ${error.message}`;
    }
}

module.exports = { runCommand };
```

```markdown
<!-- In template -->
<%* tR += await tp.user.runCommand('ls -la') %>
```

---

#### Issue 7: Frontmatter Not Accessible

**Symptoms**:
- `tp.frontmatter.property` returns undefined
- YAML values not reading

**Solutions**:

1. **Ensure YAML Syntax**:
   ```markdown
   <!-- Wrong: No YAML delimiters -->
   title: My Note
   tags: [tag1]
   
   <!-- Correct: Wrapped in --- -->
   ---
   title: My Note
   tags: [tag1]
   ---
   ```

2. **Check Property Names**:
   ```markdown
   ---
   my-property: value  <!-- Hyphenated key -->
   ---
   
   <!-- Access with bracket notation -->
   <% tp.frontmatter["my-property"] %>
   
   <!-- Or rename to camelCase -->
   ---
   myProperty: value
   ---
   <% tp.frontmatter.myProperty %>
   ```

3. **Wait for Frontmatter Parse**:
   ```markdown
   <%*
   // Frontmatter might not be available immediately
   await tp.app.fileManager.processFrontMatter(
     tp.config.target_file,
     (fm) => {
       tR += fm.title;
     }
   );
   %>
   ```

---

### Getting Help

If you encounter issues not covered here:

1. **Check Templater Documentation**:
   - https://silentvoid13.github.io/Templater/

2. **Obsidian Community Forum**:
   - https://forum.obsidian.md/
   - Search for "Templater" issues

3. **GitHub Issues**:
   - https://github.com/SilentVoid13/Templater/issues
   - Check existing issues or create new one

4. **Developer Console**:
   - Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)
   - Look for error messages in Console tab
   - Include in bug reports

5. **Project-AI Support**:
   - Check Project-AI documentation
   - Consult `.github/instructions/` directory
   - Contact maintainers

---

## 🔗 Integration with Project-AI

### Project-AI Context

Project-AI is a sophisticated Python desktop application with:
- **PyQt6 GUI** (Leather Book interface)
- **6 AI Systems** (FourLaws, Persona, Memory, Learning, Override, Plugins)
- **Extensive Documentation** needs
- **Multi-tier Architecture**
- **Security-First** approach

### How Templater Enhances Project-AI

#### 1. Consistent Documentation

**Before Templater**:
- Inconsistent code documentation
- Manual frontmatter creation
- Forgotten metadata
- Different formats across contributors

**After Templater**:
- Standardized code documentation template
- Auto-generated metadata
- Consistent structure
- Enforced best practices

#### 2. Development Workflows

**Use Templates For**:
- **Feature Planning**: `project-template.md`
- **Bug Reports**: Create custom `bug-report-template.md`
- **Code Reviews**: Create custom `code-review-template.md`
- **Security Audits**: Standardized audit reports
- **Testing Plans**: Structured test documentation

#### 3. Knowledge Management

**Templates Support**:
- **Daily Logs**: Track development progress
- **Meeting Notes**: Team communications
- **Learning Paths**: AI self-improvement documentation
- **Architecture Decisions**: ADRs (Architecture Decision Records)

#### 4. Integration with Existing Systems

**Project-AI Data Access**:

Create user script to read Project-AI data:

```javascript
// templates/scripts/project-ai-integration.js
const fs = require('fs');
const path = require('path');

function getAIPersonaMood() {
    try {
        const dataPath = 'data/ai_persona/state.json';
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        return data.current_mood || 'neutral';
    } catch (error) {
        return 'unknown';
    }
}

function getMemoryStats() {
    try {
        const dataPath = 'data/memory/knowledge.json';
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        
        return {
            total_entries: Object.keys(data).length,
            categories: Object.keys(data)
        };
    } catch (error) {
        return { total_entries: 0, categories: [] };
    }
}

function getRecentLearningRequests() {
    try {
        const dataPath = 'data/learning_requests/requests.json';
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        
        return data.slice(0, 5); // Last 5 requests
    } catch (error) {
        return [];
    }
}

module.exports = {
    getAIPersonaMood,
    getMemoryStats,
    getRecentLearningRequests
};
```

**Use in Templates**:

```markdown
---
title: "Development Log - <% tp.date.now('YYYY-MM-DD') %>"
ai_mood: <% tp.user.getAIPersonaMood() %>
---

# Development Log

**AI Persona Mood**: <% tp.user.getAIPersonaMood() %>

## Memory System Stats
<%*
const stats = tp.user.getMemoryStats();
tR += `- Total Entries: ${stats.total_entries}\n`;
tR += `- Categories: ${stats.categories.join(', ')}\n`;
%>

## Recent Learning Requests
<%*
const requests = tp.user.getRecentLearningRequests();
requests.forEach(req => {
  tR += `- ${req.content} (${req.status})\n`;
});
%>
```

#### 5. Automated Reporting

**Weekly Development Report Template**:

```markdown
---
title: "Weekly Report - Week <% tp.date.now('WW, YYYY') %>"
week: <% tp.date.now('YYYY-[W]WW') %>
date_range: <% tp.date.weekday('YYYY-MM-DD', 1, 0) %> to <% tp.date.weekday('YYYY-MM-DD', 0, 0) %>
---

# Weekly Development Report

**Week**: <% tp.date.now('WW, YYYY') %>  
**Period**: <% tp.date.weekday('MMM DD', 1, 0) %> - <% tp.date.weekday('MMM DD', 0, 0) %>

## AI System Status

**Persona Mood**: <% tp.user.getAIPersonaMood() %>  
**Memory Entries**: <%* tR += tp.user.getMemoryStats().total_entries %>  
**Learning Requests**: <%* tR += tp.user.getRecentLearningRequests().length %>

## Accomplishments

- [ ] <% tp.system.prompt("Key accomplishment 1") %>
- [ ] Accomplishment 2
- [ ] Accomplishment 3

## Challenges

- Challenge 1
- Challenge 2

## Next Week Goals

1. Goal 1
2. Goal 2
3. Goal 3

## Metrics

| Metric | Value |
|--------|-------|
| Commits | <%* tR += "X" %> |
| PRs Merged | <%* tR += "Y" %> |
| Issues Closed | <%* tR += "Z" %> |
| Tests Added | <%* tR += "N" %> |

---

**Generated**: <% tp.date.now('YYYY-MM-DD HH:mm') %>
```

---

## 🎓 Learning Path

### Beginner (Week 1)

**Goals**: Understand basic Templater syntax and use existing templates

**Tasks**:
1. Read this guide (Overview, Installation, Using Templates)
2. Create a note using `basic-note-template.md`
3. Create a daily note using `daily-note-template.md`
4. Understand `<% %>` syntax
5. Learn `tp.date.now()` and `tp.file.title`

**Practice**:
- Create 7 daily notes (one per day)
- Use meeting notes template for a mock meeting
- Customize prompts in basic note template

---

### Intermediate (Week 2-3)

**Goals**: Customize templates and use advanced features

**Tasks**:
1. Modify existing templates (add/remove sections)
2. Learn `tp.system.prompt()` and `tp.system.suggester()`
3. Understand YAML frontmatter access (`tp.frontmatter`)
4. Use `tp.file.create_new()` for file creation
5. Explore user scripts (`tp.user` functions)

**Practice**:
- Create custom template for bug reports
- Add custom fields to project template
- Use user scripts in templates (progress bars, ID generation)
- Set up folder templates for auto-application

---

### Advanced (Week 4+)

**Goals**: Write user scripts and complex templates

**Tasks**:
1. Create custom user scripts in JavaScript
2. Use async/await for API calls
3. Implement conditional logic and loops
4. Chain templates together
5. Integrate with Project-AI data sources

**Practice**:
- Write user script to read Project-AI JSON files
- Create template that generates reports from data
- Build automated weekly report generator
- Implement template that creates multiple files
- Contribute templates back to Project-AI repository

---

## 📚 Additional Resources

### Official Documentation
- **Templater Docs**: https://silentvoid13.github.io/Templater/
- **Obsidian Docs**: https://help.obsidian.md/
- **Moment.js Formats**: https://momentjs.com/docs/#/displaying/format/

### Community Resources
- **Obsidian Forum**: https://forum.obsidian.md/c/plugins/templater/
- **Reddit r/ObsidianMD**: https://reddit.com/r/ObsidianMD
- **GitHub Discussions**: https://github.com/SilentVoid13/Templater/discussions

### Video Tutorials
- Search YouTube for "Templater Obsidian tutorial"
- Many community creators have step-by-step guides

### Example Vaults
- **Templater Examples**: https://github.com/SilentVoid13/Templater/tree/master/docs/examples
- Community template collections on GitHub

---

## 🎯 Next Steps

### Immediate Actions

1. **Test Templates**: Create a note with each template to verify functionality
2. **Customize**: Modify templates to match your workflow
3. **Set Hotkeys**: Assign keyboard shortcuts to frequently used templates
4. **Create Folder Rules**: Set up automatic template application

### Short-term (This Week)

1. **Create Custom Templates**: Bug report, code review, architecture decision record
2. **Explore User Scripts**: Try all functions in `utils.js`
3. **Set Up Daily Notes**: Use daily note template every day
4. **Document Project Work**: Use project template for current initiatives

### Medium-term (This Month)

1. **Write User Scripts**: Create Project-AI integration scripts
2. **Build Workflows**: Automate repetitive documentation tasks
3. **Share Templates**: Contribute useful templates to Project-AI repo
4. **Train Team**: Share Templater knowledge with contributors

### Long-term (This Quarter)

1. **Advanced Automation**: API integrations, data-driven reports
2. **Template Library**: Comprehensive collection for all Project-AI needs
3. **Documentation Standards**: Enforce template usage via contributor guidelines
4. **Continuous Improvement**: Gather feedback and iterate on templates

---

## 📊 Success Metrics

### How to Measure Templater Success

**Quantitative Metrics**:
- **Template Usage**: Number of notes created from templates per week
- **Time Savings**: Estimated time saved vs. manual documentation
- **Consistency**: Percentage of notes following standard format
- **Coverage**: Percentage of documentation types with templates

**Qualitative Metrics**:
- **Developer Satisfaction**: Ease of use, perceived value
- **Documentation Quality**: Completeness, consistency, findability
- **Onboarding Speed**: Time for new contributors to get productive
- **Knowledge Sharing**: Improved team communication

**Target Goals**:
- 80%+ of new notes use templates
- 50%+ time savings on documentation
- 100% code modules have documentation (via template)
- <1 hour onboarding for new contributors

---

## 🙏 Acknowledgments

### Credits

- **Templater Plugin**: Created by [SilentVoid13](https://github.com/SilentVoid13)
- **Obsidian**: Developed by [Obsidian.md](https://obsidian.md/)
- **Project-AI**: Open-source AI assistant framework
- **Community**: Obsidian and Templater community contributors

### Contributions Welcome

This setup guide and templates are living documents. Contributions are welcome:

1. **Improve Templates**: Fix issues, add features
2. **Add Templates**: Create new templates for common use cases
3. **Update Documentation**: Clarify instructions, add examples
4. **Share Scripts**: Contribute useful user scripts
5. **Report Issues**: File bugs or suggest improvements

**How to Contribute**:
1. Fork Project-AI repository
2. Make changes in `templates/` or documentation
3. Test thoroughly
4. Submit pull request with clear description

---

## 📄 License

This Templater setup, documentation, and templates are part of the Project-AI ecosystem and follow the project's MIT license.

**MIT License**:
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

---

## 📞 Support

### Getting Help

**For Templater Issues**:
1. Check [Troubleshooting](#troubleshooting) section above
2. Search [Templater Docs](https://silentvoid13.github.io/Templater/)
3. Ask in [Obsidian Forum](https://forum.obsidian.md/)
4. File issue on [Templater GitHub](https://github.com/SilentVoid13/Templater/issues)

**For Project-AI Issues**:
1. Check Project-AI documentation in `docs/`
2. Review `.github/instructions/` directory
3. File issue on Project-AI repository
4. Contact maintainers

**For Template Customization**:
1. Review [Templater Syntax Guide](#templater-syntax-guide)
2. Study existing templates in `templates/`
3. Experiment in test notes (not production)
4. Ask community for guidance

---

**Setup completed successfully!** 🎉

You now have a production-ready Templater installation with:
- ✅ Latest plugin version (2.19.1)
- ✅ 5 comprehensive templates
- ✅ Custom user scripts library
- ✅ Complete documentation
- ✅ Integration guidelines
- ✅ Troubleshooting resources

**Happy templating!** 📝
