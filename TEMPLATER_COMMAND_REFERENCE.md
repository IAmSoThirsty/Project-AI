# Templater Command Reference Guide

**Version:** 1.0  
**Last Updated:** 2024-12-20  
**Templater Version:** 2.19.1

---

## 📋 Quick Reference

This document provides a comprehensive command reference for all Templater internal functions, user scripts, and syntax patterns.

---

## Table of Contents

1. [Syntax Basics](#syntax-basics)
2. [tp.file Module](#tpfile-module)
3. [tp.date Module](#tpdate-module)
4. [tp.frontmatter Module](#tpfrontmatter-module)
5. [tp.system Module](#tpsystem-module)
6. [tp.config Module](#tpconfig-module)
7. [tp.obsidian Module](#tpobsidian-module)
8. [tp.user Module (Custom Scripts)](#tpuser-module-custom-scripts)
9. [Control Flow](#control-flow)
10. [Common Patterns](#common-patterns)
11. [Cheat Sheet](#cheat-sheet)

---

## Syntax Basics

### Template Delimiters

```markdown
<% code %>          Execute code and output result
<%* code %>         Execute code without output
<%+ code %>         Execute code in next step
```

### Output to Template

```markdown
<!-- Using return value (implicit) -->
<% tp.date.now() %>

<!-- Using tR variable (explicit) -->
<%* tR += "text" %>

<!-- Multiline output -->
<%*
tR += "Line 1\n";
tR += "Line 2\n";
tR += "Line 3";
%>
```

### Comments

```markdown
<%* /* JavaScript comment */ %>
<%* // Single line comment %>

<%*
/* 
 * Multi-line comment
 * Useful for documentation
 */
%>
```

---

## tp.file Module

File operations and metadata access.

### Properties

| Property | Returns | Example |
|----------|---------|---------|
| `tp.file.content` | String | Current file content |
| `tp.file.cursor` | Number | Cursor position |
| `tp.file.cursor_append` | String | Append text at cursor |
| `tp.file.exists(path)` | Boolean | Check if file exists |
| `tp.file.folder(relative)` | String | Parent folder path |
| `tp.file.include(file)` | String | Include another file's content |
| `tp.file.last_modified_date(format)` | String | Last modification date |
| `tp.file.path(relative)` | String | File path |
| `tp.file.rename(new_name)` | Promise | Rename file |
| `tp.file.selection()` | String | Selected text |
| `tp.file.tags` | Array | File tags |
| `tp.file.title` | String | File title (without extension) |

### Methods

#### `tp.file.create_new(template, filename, open_new, folder)`

Create a new file from a template.

**Parameters**:
- `template`: TFile object or string (use `tp.file.find_tfile()`)
- `filename`: String - name of new file
- `open_new`: Boolean - open in new pane (default: true)
- `folder`: String - destination folder path

**Returns**: Promise<TFile>

**Examples**:

```markdown
<%* 
// Create new file from template
await tp.file.create_new(
  tp.file.find_tfile("daily-note-template.md"),
  "2024-12-20",
  false,
  "daily-notes"
);
%>

<%*
// Create file with current date
const today = tp.date.now("YYYY-MM-DD");
await tp.file.create_new(
  tp.file.find_tfile("daily-note-template.md"),
  today
);
%>

<%*
// Create multiple files
const dates = ["2024-12-20", "2024-12-21", "2024-12-22"];
for (const date of dates) {
  await tp.file.create_new(
    tp.file.find_tfile("daily-note-template.md"),
    date,
    false
  );
}
%>
```

#### `tp.file.creation_date(format)`

Get file creation date.

**Parameters**:
- `format`: String - moment.js format string

**Returns**: String

**Examples**:

```markdown
<% tp.file.creation_date("YYYY-MM-DD") %>
<!-- Output: 2024-12-20 -->

<% tp.file.creation_date("dddd, MMMM DD, YYYY") %>
<!-- Output: Friday, December 20, 2024 -->

<% tp.file.creation_date("HH:mm:ss") %>
<!-- Output: 14:30:45 -->
```

#### `tp.file.cursor(order)`

Set cursor position after template execution.

**Parameters**:
- `order`: Number - cursor order (for multiple cursors)

**Returns**: String (cursor marker)

**Examples**:

```markdown
# Meeting Notes

## Attendees
<% tp.file.cursor(1) %>

## Agenda
<% tp.file.cursor(2) %>

## Notes
<% tp.file.cursor(3) %>
```

#### `tp.file.find_tfile(filename)`

Find a file by name.

**Parameters**:
- `filename`: String - file name (with or without extension)

**Returns**: TFile object or null

**Examples**:

```markdown
<%*
const template = tp.file.find_tfile("daily-note-template.md");
if (template) {
  tR += "Template found!";
} else {
  tR += "Template not found!";
}
%>

<%*
// Find and include template
const header = tp.file.find_tfile("header.md");
if (header) {
  tR += await tp.file.include(header);
}
%>
```

#### `tp.file.folder(relative)`

Get parent folder path.

**Parameters**:
- `relative`: Boolean - return relative path (default: false)

**Returns**: String

**Examples**:

```markdown
<% tp.file.folder() %>
<!-- Output: /projects/2024 -->

<% tp.file.folder(true) %>
<!-- Output: projects/2024 -->
```

#### `tp.file.include(file)`

Include content from another file.

**Parameters**:
- `file`: TFile object

**Returns**: Promise<String>

**Examples**:

```markdown
<%* 
// Include header
tR += await tp.file.include(tp.file.find_tfile("header.md"));
%>

<%*
// Conditional include
const useHeader = true;
if (useHeader) {
  const header = tp.file.find_tfile("header.md");
  tR += await tp.file.include(header);
}
%>
```

#### `tp.file.move(new_path)`

Move/rename file to new location.

**Parameters**:
- `new_path`: String - new file path (absolute or relative)

**Returns**: Promise

**Examples**:

```markdown
<%*
// Move to archive
await tp.file.move("archive/old-note.md");
%>

<%*
// Organize by date
const year = tp.date.now("YYYY");
const month = tp.date.now("MM");
await tp.file.move(`daily/${year}/${month}/${tp.file.title}.md`);
%>
```

#### `tp.file.path(relative)`

Get file path.

**Parameters**:
- `relative`: Boolean - return relative path (default: false)

**Returns**: String

**Examples**:

```markdown
<% tp.file.path() %>
<!-- Output: /projects/2024/project-ai.md -->

<% tp.file.path(true) %>
<!-- Output: projects/2024/project-ai.md -->
```

#### `tp.file.rename(new_title)`

Rename current file.

**Parameters**:
- `new_title`: String - new file name (without extension)

**Returns**: Promise

**Examples**:

```markdown
<%*
// Rename with timestamp
const newName = `${tp.file.title}-${tp.date.now("YYYY-MM-DD")}`;
await tp.file.rename(newName);
%>

<%*
// Rename based on frontmatter
await tp.file.rename(tp.frontmatter.title);
%>
```

#### `tp.file.selection()`

Get currently selected text.

**Returns**: String

**Examples**:

```markdown
<%*
const selected = tp.file.selection();
tR += `You selected: ${selected}`;
%>

<%*
// Transform selection
const selected = tp.file.selection();
const uppercase = selected.toUpperCase();
tR += uppercase;
%>
```

---

## tp.date Module

Date and time operations.

### Methods

#### `tp.date.now(format, offset, reference, reference_format)`

Get current date/time or calculate offset.

**Parameters**:
- `format`: String - moment.js format string
- `offset`: Number - days offset (positive = future, negative = past)
- `reference`: String - reference date (optional)
- `reference_format`: String - format of reference date (optional)

**Returns**: String

**Examples**:

```markdown
<!-- Current date -->
<% tp.date.now("YYYY-MM-DD") %>
<!-- Output: 2024-12-20 -->

<!-- Date with offset -->
<% tp.date.now("YYYY-MM-DD", 7) %>
<!-- Output: 2024-12-27 (7 days from now) -->

<% tp.date.now("YYYY-MM-DD", -7) %>
<!-- Output: 2024-12-13 (7 days ago) -->

<!-- From reference date -->
<% tp.date.now("YYYY-MM-DD", 1, "2024-01-01", "YYYY-MM-DD") %>
<!-- Output: 2024-01-02 -->

<!-- Various formats -->
<% tp.date.now("dddd, MMMM DD, YYYY") %>
<!-- Output: Friday, December 20, 2024 -->

<% tp.date.now("YYYY-[W]WW") %>
<!-- Output: 2024-W51 -->

<% tp.date.now("HH:mm:ss") %>
<!-- Output: 14:30:45 -->

<% tp.date.now("MMM DD, YYYY") %>
<!-- Output: Dec 20, 2024 -->
```

**Common Format Tokens**:

| Token | Output | Example |
|-------|--------|---------|
| `YYYY` | 4-digit year | 2024 |
| `YY` | 2-digit year | 24 |
| `MMMM` | Full month name | December |
| `MMM` | Short month name | Dec |
| `MM` | 2-digit month | 12 |
| `M` | Month number | 12 |
| `DD` | 2-digit day | 20 |
| `D` | Day number | 20 |
| `dddd` | Full day name | Friday |
| `ddd` | Short day name | Fri |
| `HH` | 24-hour (2-digit) | 14 |
| `H` | 24-hour | 14 |
| `hh` | 12-hour (2-digit) | 02 |
| `h` | 12-hour | 2 |
| `mm` | Minutes (2-digit) | 30 |
| `m` | Minutes | 30 |
| `ss` | Seconds (2-digit) | 45 |
| `s` | Seconds | 45 |
| `A` | AM/PM | PM |
| `a` | am/pm | pm |
| `WW` | Week of year | 51 |

#### `tp.date.tomorrow(format)`

Get tomorrow's date.

**Parameters**:
- `format`: String - moment.js format string

**Returns**: String

**Examples**:

```markdown
<% tp.date.tomorrow("YYYY-MM-DD") %>
<!-- Output: 2024-12-21 -->

<% tp.date.tomorrow("dddd") %>
<!-- Output: Saturday -->
```

#### `tp.date.yesterday(format)`

Get yesterday's date.

**Parameters**:
- `format`: String - moment.js format string

**Returns**: String

**Examples**:

```markdown
<% tp.date.yesterday("YYYY-MM-DD") %>
<!-- Output: 2024-12-19 -->

<% tp.date.yesterday("MMM DD") %>
<!-- Output: Dec 19 -->
```

#### `tp.date.weekday(format, weekday, reference, reference_format)`

Get specific weekday.

**Parameters**:
- `format`: String - moment.js format string
- `weekday`: Number - day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
- `reference`: String - reference date (default: today)
- `reference_format`: String - format of reference (optional)

**Returns**: String

**Examples**:

```markdown
<!-- Next Monday -->
<% tp.date.weekday("YYYY-MM-DD", 1) %>

<!-- Next Sunday -->
<% tp.date.weekday("YYYY-MM-DD", 0) %>

<!-- Last Friday -->
<% tp.date.weekday("YYYY-MM-DD", 5, tp.date.now("YYYY-MM-DD", -7), "YYYY-MM-DD") %>
```

---

## tp.frontmatter Module

Access YAML frontmatter properties.

### Syntax

```markdown
<% tp.frontmatter.property_name %>
<% tp.frontmatter["property-with-hyphens"] %>
```

### Examples

```markdown
---
title: My Note
status: active
priority: high
tags: [tag1, tag2]
created: 2024-12-20
---

<!-- Access properties -->
Title: <% tp.frontmatter.title %>
Status: <% tp.frontmatter.status %>
Priority: <% tp.frontmatter.priority %>

<!-- Array properties -->
<%*
tp.frontmatter.tags.forEach(tag => {
  tR += `- ${tag}\n`;
});
%>

<!-- Conditional based on frontmatter -->
<%* if (tp.frontmatter.status === "active") { %>
This project is currently active!
<%* } else { %>
This project is not active.
<%* } %>
```

---

## tp.system Module

User interaction and system operations.

### Methods

#### `tp.system.prompt(prompt_text, default_value, throw_on_cancel, multiline)`

Prompt user for text input.

**Parameters**:
- `prompt_text`: String - prompt message
- `default_value`: String - pre-filled value (optional)
- `throw_on_cancel`: Boolean - throw error if cancelled (default: false)
- `multiline`: Boolean - multi-line input (default: false)

**Returns**: Promise<String>

**Examples**:

```markdown
<%* 
const name = await tp.system.prompt("Enter your name");
tR += `Hello, ${name}!`;
%>

<%*
const description = await tp.system.prompt(
  "Enter description",
  "Default description"
);
tR += description;
%>

<%*
const notes = await tp.system.prompt(
  "Enter your notes",
  "",
  false,
  true  // Multi-line
);
tR += notes;
%>
```

#### `tp.system.suggester(text_items, items, throw_on_cancel, placeholder, limit)`

Display selection menu.

**Parameters**:
- `text_items`: Array<String> - display labels
- `items`: Array<Any> - return values (must match text_items length)
- `throw_on_cancel`: Boolean - throw error if cancelled (default: false)
- `placeholder`: String - placeholder text (optional)
- `limit`: Number - max items to display (optional)

**Returns**: Promise<Any> (selected item from `items` array)

**Examples**:

```markdown
<%*
const status = await tp.system.suggester(
  ["🟢 Active", "🟡 Planning", "🔴 On Hold"],
  ["active", "planning", "on-hold"]
);
tR += `Status: ${status}`;
%>

<%*
const priority = await tp.system.suggester(
  ["High", "Medium", "Low"],
  [1, 2, 3]
);
tR += `Priority level: ${priority}`;
%>

<%*
// Boolean choice
const confirm = await tp.system.suggester(
  ["Yes", "No"],
  [true, false],
  false,
  "Proceed with operation?"
);

if (confirm) {
  tR += "Confirmed!";
} else {
  tR += "Cancelled.";
}
%>
```

#### `tp.system.clipboard()`

Get clipboard content.

**Returns**: Promise<String>

**Examples**:

```markdown
<%* 
const clipboardText = await tp.system.clipboard();
tR += clipboardText;
%>

<%*
// Quote clipboard content
const clip = await tp.system.clipboard();
tR += `> ${clip.split('\n').join('\n> ')}`;
%>
```

---

## tp.config Module

Templater configuration and context.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `tp.config.template_file` | TFile | Template file being used |
| `tp.config.target_file` | TFile | Target file for template |
| `tp.config.run_mode` | String | How template was triggered |
| `tp.config.active_file` | TFile | Currently active file |

### Run Modes

- `CreateNewFromTemplate` - New file from template
- `AppendActiveFile` - Appended to existing file
- `OverwriteFile` - Replacing file content
- `OverwriteActiveFile` - Replacing active file
- `DynamicProcessor` - Dynamic template execution
- `StartupTemplate` - Startup template execution

### Examples

```markdown
<%*
// Get run mode
tR += `Run mode: ${tp.config.run_mode}`;
%>

<%*
// Different behavior based on mode
if (tp.config.run_mode === "CreateNewFromTemplate") {
  tR += "This is a new file!";
} else {
  tR += "This is an existing file.";
}
%>

<%*
// Access target file info
const file = tp.config.target_file;
tR += `File: ${file.basename}\n`;
tR += `Path: ${file.path}\n`;
tR += `Size: ${file.stat.size} bytes`;
%>
```

---

## tp.obsidian Module

Access Obsidian API.

### Properties

| Property | Description |
|----------|-------------|
| `tp.obsidian.app` | Obsidian App object |

### Common Uses

#### Request API

```markdown
<%*
// HTTP request
const response = await tp.obsidian.request({
  url: "https://api.quotable.io/random",
  method: "GET"
});

const data = JSON.parse(response);
tR += `> ${data.content}\n> — ${data.author}`;
%>
```

#### Vault Operations

```markdown
<%*
// Create folder
await tp.app.vault.createFolder("new-folder");
%>

<%*
// List files
const files = tp.app.vault.getMarkdownFiles();
tR += `Total files: ${files.length}`;
%>

<%*
// Read file
const fileContent = await tp.app.vault.read(someFile);
tR += fileContent;
%>
```

---

## tp.user Module (Custom Scripts)

Custom functions from user scripts.

### Installed Functions (from utils.js)

#### `tp.user.generate_id()`

Generate unique ID.

**Returns**: String

**Example**:
```markdown
<% tp.user.generate_id() %>
<!-- Output: 1ko234abc-x9y8z -->
```

#### `tp.user.relative_date(dateString)`

Format date as relative string.

**Parameters**:
- `dateString`: String - date in YYYY-MM-DD format

**Returns**: String

**Example**:
```markdown
<% tp.user.relative_date("2024-01-01") %>
<!-- Output: "3 weeks ago" -->

<% tp.user.relative_date("2025-01-01") %>
<!-- Output: "2 weeks from now" -->
```

#### `tp.user.git_branch()`

Get current git branch.

**Returns**: Promise<String>

**Example**:
```markdown
<%* tR += await tp.user.git_branch() %>
<!-- Output: "main" or "feature/templater" -->
```

#### `tp.user.random_from_array(arr)`

Get random item from array.

**Parameters**:
- `arr`: Array - items to choose from

**Returns**: Any

**Example**:
```markdown
<% tp.user.random_from_array(["Red", "Green", "Blue"]) %>
<!-- Output: "Green" (random) -->

<% tp.user.random_from_array([1, 2, 3, 4, 5]) %>
<!-- Output: 3 (random) -->
```

#### `tp.user.word_count(text)`

Count words in text.

**Parameters**:
- `text`: String - text to count

**Returns**: Number

**Example**:
```markdown
<% tp.user.word_count(tp.file.content) %>
<!-- Output: 1234 -->

<% tp.user.word_count("Hello world this is a test") %>
<!-- Output: 6 -->
```

#### `tp.user.generate_toc(content)`

Generate table of contents from headings.

**Parameters**:
- `content`: String - markdown content

**Returns**: String

**Example**:
```markdown
<%* tR += tp.user.generate_toc(tp.file.content) %>
<!-- Output:
## Table of Contents

- [Heading 1](#heading-1)
  - [Subheading 1.1](#subheading-1-1)
- [Heading 2](#heading-2)
-->
```

#### `tp.user.format_currency(amount, currency)`

Format currency value.

**Parameters**:
- `amount`: Number - amount to format
- `currency`: String - currency code (default: "USD")

**Returns**: String

**Example**:
```markdown
<% tp.user.format_currency(1234.56, "USD") %>
<!-- Output: "$1,234.56" -->

<% tp.user.format_currency(1234.56, "EUR") %>
<!-- Output: "€1,234.56" -->
```

#### `tp.user.days_between(date1, date2)`

Calculate days between two dates.

**Parameters**:
- `date1`: String - first date (YYYY-MM-DD)
- `date2`: String - second date (YYYY-MM-DD)

**Returns**: Number

**Example**:
```markdown
<% tp.user.days_between("2024-01-01", "2024-12-31") %>
<!-- Output: 365 -->

Duration: <% tp.user.days_between(tp.frontmatter.start_date, tp.frontmatter.end_date) %> days
```

#### `tp.user.get_season(date)`

Get season for date.

**Parameters**:
- `date`: Date - date object (default: now)

**Returns**: String

**Example**:
```markdown
<% tp.user.get_season() %>
<!-- Output: "Winter" (based on current date) -->

<% tp.user.get_season(new Date("2024-07-15")) %>
<!-- Output: "Summer" -->
```

#### `tp.user.progress_bar(percentage, length)`

Generate progress bar.

**Parameters**:
- `percentage`: Number - completion percentage (0-100)
- `length`: Number - bar length in characters (default: 20)

**Returns**: String

**Example**:
```markdown
<% tp.user.progress_bar(75, 20) %>
<!-- Output: [███████████████░░░░░] 75% -->

<% tp.user.progress_bar(33, 10) %>
<!-- Output: [███░░░░░░░] 33% -->
```

---

## Control Flow

### If/Else

```markdown
<%* if (condition) { %>
Content if true
<%* } else if (otherCondition) { %>
Content if other condition
<%* } else { %>
Content if false
<%* } %>
```

**Examples**:

```markdown
<%* if (tp.frontmatter.status === "active") { %>
## 🟢 Active Project
<%* } else { %>
## 🔴 Inactive Project
<%* } %>

<%*
const hour = new Date().getHours();
if (hour < 12) {
  tR += "Good morning! 🌅";
} else if (hour < 18) {
  tR += "Good afternoon! ☀️";
} else {
  tR += "Good evening! 🌙";
}
%>
```

### Loops

#### For Loop

```markdown
<%*
for (let i = 0; i < 5; i++) {
  tR += `- Item ${i + 1}\n`;
}
%>
```

#### For...of Loop

```markdown
<%*
const items = ["Apple", "Banana", "Cherry"];
for (const item of items) {
  tR += `- ${item}\n`;
}
%>
```

#### While Loop

```markdown
<%*
let count = 0;
while (count < 5) {
  tR += `Count: ${count}\n`;
  count++;
}
%>
```

#### forEach

```markdown
<%*
const tasks = ["Task 1", "Task 2", "Task 3"];
tasks.forEach((task, index) => {
  tR += `${index + 1}. ${task}\n`;
});
%>
```

---

## Common Patterns

### Task List from User Input

```markdown
<%*
const tasks = await tp.system.prompt("Enter tasks (comma-separated)");
tasks.split(",").forEach(task => {
  tR += `- [ ] ${task.trim()}\n`;
});
%>
```

### Date Range

```markdown
From: <% tp.date.now("YYYY-MM-DD") %>  
To: <% tp.date.now("YYYY-MM-DD", 30) %>  
Duration: 30 days
```

### Conditional Sections

```markdown
<%* if (tp.frontmatter.type === "project") { %>
## Project Details
...
<%* } %>

<%* if (tp.frontmatter.type === "meeting") { %>
## Meeting Details
...
<%* } %>
```

### Dynamic File Creation

```markdown
<%*
const count = await tp.system.prompt("How many files?");
for (let i = 0; i < parseInt(count); i++) {
  const name = `file-${i + 1}`;
  await tp.file.create_new(
    tp.file.find_tfile("template.md"),
    name,
    false
  );
}
tR += `Created ${count} files!`;
%>
```

### Table Generation

```markdown
<%*
const data = [
  {name: "Alice", age: 30, role: "Developer"},
  {name: "Bob", age: 25, role: "Designer"},
  {name: "Carol", age: 35, role: "Manager"}
];

tR += "| Name | Age | Role |\n";
tR += "|------|-----|------|\n";

data.forEach(row => {
  tR += `| ${row.name} | ${row.age} | ${row.role} |\n`;
});
%>
```

### API Integration

```markdown
<%*
try {
  const response = await tp.obsidian.request({
    url: "https://api.github.com/repos/obsidianmd/obsidian-releases",
    method: "GET"
  });
  
  const repo = JSON.parse(response);
  tR += `Repository: ${repo.full_name}\n`;
  tR += `Stars: ${repo.stargazers_count}\n`;
  tR += `Forks: ${repo.forks_count}\n`;
} catch (error) {
  tR += `Error: ${error.message}`;
}
%>
```

---

## Cheat Sheet

### Essential Commands

```markdown
<!-- Current date -->
<% tp.date.now("YYYY-MM-DD") %>

<!-- File title -->
<% tp.file.title %>

<!-- User input -->
<%* await tp.system.prompt("Question?") %>

<!-- Selection menu -->
<%* await tp.system.suggester(["Option 1", "Option 2"], ["val1", "val2"]) %>

<!-- Frontmatter -->
<% tp.frontmatter.property %>

<!-- Create file -->
<%* await tp.file.create_new(template, filename) %>

<!-- Include file -->
<%* await tp.file.include(file) %>

<!-- Cursor position -->
<% tp.file.cursor() %>
```

### Date Formats

```markdown
<% tp.date.now("YYYY-MM-DD") %>           <!-- 2024-12-20 -->
<% tp.date.now("dddd, MMMM DD, YYYY") %>  <!-- Friday, December 20, 2024 -->
<% tp.date.now("HH:mm") %>                <!-- 14:30 -->
<% tp.date.now("YYYY-[W]WW") %>           <!-- 2024-W51 -->
```

### Navigation

```markdown
[[<% tp.date.now("YYYY-MM-DD", -1) %>|← Yesterday]]
[[<% tp.date.now("YYYY-MM-DD", 1) %>|Tomorrow →]]
```

### Quick Snippets

```markdown
<!-- ID -->
ID: <% tp.user.generate_id() %>

<!-- Timestamp -->
Generated: <% tp.date.now("YYYY-MM-DD HH:mm:ss") %>

<!-- Progress -->
<% tp.user.progress_bar(50) %>

<!-- Word count -->
Words: <% tp.user.word_count(tp.file.content) %>

<!-- Season -->
Season: <% tp.user.get_season() %>
```

---

## See Also

- [Templater Setup Guide](TEMPLATER_SETUP_GUIDE.md) - Complete setup documentation
- [Templater Troubleshooting Guide](TEMPLATER_TROUBLESHOOTING_GUIDE.md) - Problem solving
- [Official Templater Docs](https://silentvoid13.github.io/Templater/) - Comprehensive reference
- [Moment.js Formats](https://momentjs.com/docs/#/displaying/format/) - Date formatting

---

**Last Updated:** 2024-12-20  
**Maintained by:** Project-AI Team
