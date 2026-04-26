---
type: guide
tags:
  - p2-root
  - status
  - guide
  - obsidian
  - templater
  - troubleshooting
created: 2024-12-20
last_verified: 2026-04-20
status: current
related_systems:
  - obsidian-vault
  - templater-plugin
  - diagnostics
stakeholders:
  - obsidian-team
  - documentation-team
report_type: guide
supersedes: []
review_cycle: as-needed
---

# Templater Troubleshooting Guide

**Version:** 1.0  
**Last Updated:** 2024-12-20  
**Templater Version:** 2.19.1

---

## 📋 Overview

This guide helps you diagnose and fix common issues with Templater in the Project-AI environment. Each problem includes symptoms, causes, and step-by-step solutions.

**Related Documentation**:
- [[TEMPLATER_SETUP_GUIDE]] - Installation and configuration guide
- [[TEMPLATER_QUICK_REFERENCE]] - Quick reference for commands
- [[TEMPLATER_COMMAND_REFERENCE]] - Complete command reference
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration and structure
- [[vault-troubleshooting-guide]] - General vault troubleshooting

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Template Execution Issues](#template-execution-issues)
4. [User Scripts Issues](#user-scripts-issues)
5. [Syntax Errors](#syntax-errors)
6. [Performance Issues](#performance-issues)
7. [Integration Issues](#integration-issues)
8. [Advanced Troubleshooting](#advanced-troubleshooting)
9. [Getting Additional Help](#getting-additional-help)
10. [System Reference](#system-reference)

---

## Quick Diagnostics

### 5-Minute Health Check

Run through this checklist to identify common issues:

#### ✅ Checklist

- [ ] **Plugin Enabled**: Settings → Community Plugins → Templater has checkmark
- [ ] **Template Folder Set**: Settings → Templater → Template folder location = `templates`
- [ ] **Templates Exist**: Verify files exist in `templates/` directory
- [ ] **User Scripts Folder**: Settings → Templater → User scripts folder = `templates/scripts`
- [ ] **Scripts Exported**: Check `utils.js` has `module.exports = {...}`
- [ ] **No Syntax Errors**: Open Developer Console (`Ctrl+Shift+I`), check for errors
- [ ] **Latest Version**: Templater version 2.19.1 or newer
- [ ] **Obsidian Updated**: Obsidian version 1.0.0 or newer

#### 🔍 Quick Test

Create a new note and insert this template code:

```markdown
Test: <% tp.date.now("YYYY-MM-DD") %>
```

**Expected Result**: `Test: 2024-12-20` (current date)

**If it shows raw code**: Template execution is broken → See [Template Execution Issues](#template-execution-issues)

**If it shows nothing**: Plugin not enabled → See [Installation Issues](#installation-issues)

---

## Installation Issues

### Issue 1: Templater Not Showing in Plugins List

**Symptoms**:
- Templater doesn't appear in Settings → Community Plugins
- Can't find Templater in Community Plugins Browser
- Installation appears to fail silently

**Possible Causes**:
1. Plugin files not properly downloaded
2. Incorrect folder structure
3. Obsidian hasn't detected new plugin
4. File permissions issue

**Solutions**:

#### Solution A: Verify Installation

1. **Check Plugin Directory**:
   ```powershell
   # Run in PowerShell
   Get-ChildItem "T:\Project-AI-main\.obsidian\plugins\templater-obsidian"
   ```

   **Expected Files**:
   - `main.js` (319,145 bytes)
   - `manifest.json` (331 bytes)
   - `styles.css` (4,932 bytes)
   - `data.json` (548 bytes)

2. **If Files Missing**: Reinstall
   ```powershell
   # Download latest release
   $version = "2.19.1"
   $path = "T:\Project-AI-main\.obsidian\plugins\templater-obsidian"
   
   Invoke-WebRequest -Uri "https://github.com/SilentVoid13/Templater/releases/download/$version/main.js" -OutFile "$path\main.js"
   Invoke-WebRequest -Uri "https://github.com/SilentVoid13/Templater/releases/download/$version/manifest.json" -OutFile "$path\manifest.json"
   Invoke-WebRequest -Uri "https://github.com/SilentVoid13/Templater/releases/download/$version/styles.css" -OutFile "$path\styles.css"
   ```

#### Solution B: Restart Obsidian

1. Close Obsidian completely
2. Reopen vault
3. Check Settings → Community Plugins

#### Solution C: Enable Community Plugins

1. Settings → Community Plugins
2. Click "Turn on community plugins" if disabled
3. Restart Obsidian

#### Solution D: Check File Permissions

```powershell
# Windows: Ensure files are readable
icacls "T:\Project-AI-main\.obsidian\plugins\templater-obsidian\*" /grant:r Users:R
```

---

### Issue 2: Templater Installed But Not Enabled

**Symptoms**:
- Templater appears in plugin list but has no checkmark
- Toggle doesn't stay enabled
- Error message when enabling

**Solutions**:

#### Solution A: Enable Plugin

1. Settings → Community Plugins
2. Find "Templater" in list
3. Click toggle to enable
4. Look for checkmark

#### Solution B: Check for Errors

1. Press `Ctrl+Shift+I` to open Developer Console
2. Try enabling Templater
3. Watch Console tab for red errors
4. Common errors:
   - **"Cannot find module"**: Reinstall plugin
   - **"Parse error"**: `manifest.json` corrupted
   - **"Permission denied"**: File permissions issue

#### Solution C: Verify manifest.json

```powershell
Get-Content "T:\Project-AI-main\.obsidian\plugins\templater-obsidian\manifest.json"
```

**Should contain**:
```json
{
  "id": "templater-obsidian",
  "name": "Templater",
  "version": "2.19.1",
  ...
}
```

If corrupted, re-download from GitHub.

#### Solution D: Check community-plugins.json

```powershell
Get-Content "T:\Project-AI-main\.obsidian\community-plugins.json"
```

**Should include**:
```json
[
  "dataview",
  "templater-obsidian"
]
```

If missing, add manually:
```powershell
$plugins = @("dataview", "templater-obsidian")
$plugins | ConvertTo-Json | Set-Content "T:\Project-AI-main\.obsidian\community-plugins.json"
```

---

### Issue 3: Template Folder Not Recognized

**Symptoms**:
- Templates don't appear in Templater menu
- "No templates found" error
- Can't select templates

**Related Documentation**: See [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] for vault structure and [[docs/architecture/ROOT_STRUCTURE]] for project organization.

**Solutions**:

#### Solution A: Verify Folder Path

1. Settings → Templater → Template folder location
2. Should show: `templates`
3. If different, change to `templates`

#### Solution B: Check Folder Exists

```powershell
Test-Path "T:\Project-AI-main\templates"
# Should return: True
```

If False:
```powershell
New-Item -ItemType Directory -Path "T:\Project-AI-main\templates"
```

#### Solution C: Verify Template Files

```powershell
Get-ChildItem "T:\Project-AI-main\templates\*.md"
```

**Expected**:
- `basic-note-template.md`
- `meeting-notes-template.md`
- `daily-note-template.md`
- `project-template.md`
- `code-documentation-template.md`

#### Solution D: Use Absolute Path (if relative fails)

Sometimes relative paths don't work. Try absolute:

1. Settings → Templater → Template folder location
2. Enter: `T:\Project-AI-main\templates`
3. Restart Obsidian

---

## Template Execution Issues

**Quick Reference**: For template syntax, see [[TEMPLATER_QUICK_REFERENCE]] and [[TEMPLATER_COMMAND_REFERENCE]]. For execution architecture, see [[docs/architecture/WORKFLOW_ENGINE]].

### Issue 4: Template Code Shows as Raw Text

**Symptoms**:
- Template inserts `<% tp.date.now() %>` instead of executing
- No prompts appear
- Code visible in note

**Possible Causes**:
1. Templater not enabled
2. Wrong syntax (single `%` instead of double `%%`)
3. File not recognized as template
4. Execution mode incorrect

**Solutions**:

#### Solution A: Verify Templater Enabled

1. Settings → Community Plugins
2. Templater should have checkmark
3. If no checkmark, toggle to enable

#### Solution B: Check Syntax

**Wrong**:
```markdown
< % tp.date.now() % >  <!-- Spaces -->
< tp.date.now() >      <!-- Single < > -->
```

**Correct**:
```markdown
<% tp.date.now() %>
```

#### Solution C: Use Templater Command

Don't just paste template code. Use Templater to insert:

1. Place cursor where template should go
2. Press `Ctrl+P`
3. Type "Templater: Insert template"
4. Select template from list

Or:

1. Click Templater ribbon icon (📋)
2. Select template

#### Solution D: Check Run Mode

Some templates only work in specific modes:

```markdown
<%* 
// This only works in CreateNewFromTemplate mode
if (tp.config.run_mode === "CreateNewFromTemplate") {
  tR += "New file!";
}
%>
```

**Test with simple template**:
```markdown
<% tp.date.now("YYYY-MM-DD") %>
```

If this works but complex templates don't, issue is in template logic.

---

### Issue 5: Prompts Not Appearing

**Symptoms**:
- `tp.system.prompt()` doesn't show dialog
- `tp.system.suggester()` skips without asking
- Template executes but values are undefined

**Solutions**:

#### Solution A: Use Await

**Wrong**:
```markdown
<%*
const name = tp.system.prompt("Name");
tR += name; // undefined
%>
```

**Correct**:
```markdown
<%*
const name = await tp.system.prompt("Name");
tR += name; // works
%>
```

#### Solution B: Check Run Mode

Prompts only work in interactive modes:

```markdown
<%*
// Check if prompts will work
const canPrompt = tp.config.run_mode === "CreateNewFromTemplate" || 
                  tp.config.run_mode === "AppendActiveFile";

if (canPrompt) {
  const name = await tp.system.prompt("Name");
  tR += name;
} else {
  tR += "Default name";
}
%>
```

#### Solution C: Verify Not in Batch Mode

If creating multiple files in loop, prompts may be suppressed:

```markdown
<%*
// Prompt ONCE before loop
const baseName = await tp.system.prompt("Base name");

for (let i = 0; i < 5; i++) {
  const filename = `${baseName}-${i}`;
  await tp.file.create_new(template, filename, false);
}
%>
```

#### Solution D: Check for Blocking Code

Long-running code before prompt may cause timeout:

**Problematic**:
```markdown
<%*
// This takes 10 seconds
for (let i = 0; i < 1000000000; i++) {}

// Prompt may timeout
const name = await tp.system.prompt("Name");
%>
```

**Fixed**:
```markdown
<%*
// Prompt first
const name = await tp.system.prompt("Name");

// Then do heavy processing
for (let i = 0; i < 1000000000; i++) {}
%>
```

---

### Issue 6: Template Execution Timeout

**Symptoms**:
- Template partially executes
- "Template execution timeout" error
- Long templates don't complete

**Solutions**:

#### Solution A: Increase Timeout

1. Settings → Templater → Command timeout
2. Increase from default 5 seconds to 30 seconds
3. Restart Obsidian

#### Solution B: Optimize Template

Reduce expensive operations:

**Slow**:
```markdown
<%*
// Reading file in loop (slow)
for (let i = 0; i < 100; i++) {
  const data = tp.user.getAIPersonaMood(); // Reads file 100 times
  tR += data;
}
%>
```

**Fast**:
```markdown
<%*
// Read once, use many times
const mood = tp.user.getAIPersonaMood();
for (let i = 0; i < 100; i++) {
  tR += mood;
}
%>
```

#### Solution C: Split into Smaller Templates

Instead of one giant template:

**Before**:
```markdown
<!-- mega-template.md (1000 lines) -->
```

**After**:
```markdown
<!-- main-template.md -->
<%* tR += await tp.file.include(tp.file.find_tfile("header.md")) %>
<%* tR += await tp.file.include(tp.file.find_tfile("body.md")) %>
<%* tR += await tp.file.include(tp.file.find_tfile("footer.md")) %>
```

---

## User Scripts Issues

### Issue 7: User Scripts Not Found

**Symptoms**:
- `tp.user.function_name is not a function`
- `tp.user` is empty object
- Custom functions unavailable

**Solutions**:

#### Solution A: Verify Scripts Folder

1. Settings → Templater → User script functions folder
2. Should show: `templates/scripts`
3. If different, change to `templates/scripts`

#### Solution B: Check Script File Exists

```powershell
Test-Path "T:\Project-AI-main\templates\scripts\utils.js"
# Should return: True
```

If False:
```powershell
# Recreate from TEMPLATER_SETUP_GUIDE.md
# Or download from repository
```

#### Solution C: Verify Exports

Open `templates/scripts/utils.js` and check last line:

```javascript
module.exports = {
    generate_id,
    relative_date,
    git_branch,
    random_from_array,
    word_count,
    generate_toc,
    format_currency,
    days_between,
    get_season,
    progress_bar
};
```

**Must export all functions** you want to use.

#### Solution D: Restart Obsidian

User scripts are loaded on startup. After changes:

1. Close Obsidian
2. Reopen vault
3. Test function: `<% tp.user.generate_id() %>`

---

### Issue 8: User Script Syntax Errors

**Symptoms**:
- Functions defined but don't work
- JavaScript errors in Developer Console
- Functions return undefined

**Solutions**:

#### Solution A: Check JavaScript Syntax

Common errors:

**Missing semicolon**:
```javascript
// Wrong
function myFunc() {
    return "value"  // Missing ;
}

// Correct
function myFunc() {
    return "value";
}
```

**Unclosed brackets**:
```javascript
// Wrong
function myFunc() {
    if (condition) {
        return "value";
    // Missing }
}

// Correct
function myFunc() {
    if (condition) {
        return "value";
    }
}
```

**Wrong quotes**:
```javascript
// Wrong (smart quotes from Word)
return "value";

// Correct (straight quotes)
return "value";
```

#### Solution B: Test in Developer Console

1. Press `Ctrl+Shift+I`
2. Go to Console tab
3. Paste function code
4. Test: `myFunction()`

If error appears, fix syntax issue.

#### Solution C: Use Try-Catch

Wrap risky code:

```javascript
function myFunction() {
    try {
        // Risky operation
        const result = someOperation();
        return result;
    } catch (error) {
        console.error("Error in myFunction:", error);
        return "Error occurred";
    }
}
```

#### Solution D: Validate with Linter

```powershell
# If you have Node.js installed
npm install -g eslint
eslint templates/scripts/utils.js
```

---

### Issue 9: Node.js Modules Not Working

**Symptoms**:
- `require('fs')` fails
- `require('child_process')` fails
- Module not found errors

**Solutions**:

#### Solution A: Check Obsidian Version

Node.js modules require Obsidian 0.15.0+:

1. Settings → About
2. Check version
3. Update if needed

#### Solution B: Use Correct Module Syntax

```javascript
// Correct for Obsidian
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Wrong (ES6 imports don't work in user scripts)
import fs from 'fs';  // Won't work
```

#### Solution C: Available Modules

Only built-in Node.js modules work:

**Available**:
- `fs` - File system
- `path` - Path operations
- `child_process` - Run commands
- `util` - Utilities
- `os` - Operating system info

**Not Available**:
- External npm packages
- Custom modules from `node_modules`

#### Solution D: Fallback for Unsupported Features

```javascript
function myFunction() {
    try {
        const fs = require('fs');
        // Use fs...
    } catch (error) {
        // Fallback if module unavailable
        return "Feature not available";
    }
}
```

---

## Syntax Errors

### Issue 10: Date Formatting Not Working

**Symptoms**:
- `Invalid date` output
- Wrong date format
- Timezone issues

**Solutions**:

#### Solution A: Use Correct Format Tokens

Templater uses **Moment.js**, not strftime:

**Wrong (strftime)**:
```markdown
<% tp.date.now("%Y-%m-%d") %>  <!-- Won't work -->
```

**Correct (Moment.js)**:
```markdown
<% tp.date.now("YYYY-MM-DD") %>  <!-- Works -->
```

**Common Tokens**:
| Want | Token | Example |
|------|-------|---------|
| Year 4-digit | `YYYY` | 2024 |
| Year 2-digit | `YY` | 24 |
| Month number | `MM` | 12 |
| Month name | `MMMM` | December |
| Day number | `DD` | 20 |
| Day name | `dddd` | Friday |
| Hour 24h | `HH` | 14 |
| Hour 12h | `hh` | 02 |
| Minutes | `mm` | 30 |
| Seconds | `ss` | 45 |
| AM/PM | `A` | PM |

#### Solution B: Check Offset Parameter

Offset is in **days**, not months:

```markdown
<!-- 7 days from now -->
<% tp.date.now("YYYY-MM-DD", 7) %>

<!-- 7 days ago -->
<% tp.date.now("YYYY-MM-DD", -7) %>

<!-- NOT 7 months (use calculation instead) -->
```

For months:
```markdown
<%*
const date = new Date();
date.setMonth(date.getMonth() + 7);
tR += date.toISOString().split('T')[0];
%>
```

#### Solution C: Reference Format

When using reference date, specify format:

```markdown
<% tp.date.now("YYYY-MM-DD", 1, "2024-01-01", "YYYY-MM-DD") %>
```

---

### Issue 11: Frontmatter Not Accessible

**Symptoms**:
- `tp.frontmatter.property` returns undefined
- Can't read YAML values

**Solutions**:

#### Solution A: Verify YAML Syntax

**Wrong**:
```markdown
title: My Note
tags: [tag1]

Content starts here...
```

**Correct**:
```markdown
---
title: My Note
tags: [tag1]
---

Content starts here...
```

Must have `---` delimiters!

#### Solution B: Check Property Names

**Hyphenated properties**:
```markdown
---
my-property: value
---

<!-- Use bracket notation -->
<% tp.frontmatter["my-property"] %>
```

**CamelCase properties**:
```markdown
---
myProperty: value
---

<!-- Use dot notation -->
<% tp.frontmatter.myProperty %>
```

#### Solution C: Wait for Parse

Frontmatter might not be immediately available:

```markdown
<%*
await new Promise(resolve => setTimeout(resolve, 100));
tR += tp.frontmatter.title;
%>
```

Or use file manager:
```markdown
<%*
await tp.app.fileManager.processFrontMatter(
  tp.config.target_file,
  (fm) => {
    tR += fm.title;
  }
);
%>
```

---

### Issue 12: File Operations Failing

**Symptoms**:
- `tp.file.create_new()` doesn't create file
- `tp.file.move()` fails silently
- Path errors

**Solutions**:

#### Solution A: Use Await

**Wrong**:
```markdown
<%*
tp.file.create_new("template.md", "new-file");
tR += "Created!"; // Executes before file created
%>
```

**Correct**:
```markdown
<%*
await tp.file.create_new("template.md", "new-file");
tR += "Created!"; // Executes after file created
%>
```

#### Solution B: Verify Template Exists

```markdown
<%*
const template = tp.file.find_tfile("template.md");
if (!template) {
  tR += "Template not found!";
} else {
  await tp.file.create_new(template, "new-file");
}
%>
```

#### Solution C: Create Folders First

```markdown
<%*
// Create folder if it doesn't exist
try {
  await tp.app.vault.createFolder("projects/2024");
} catch (error) {
  // Folder already exists, ignore error
}

// Now create file in folder
await tp.file.create_new(
  tp.file.find_tfile("template.md"),
  "projects/2024/new-file"
);
%>
```

#### Solution D: Use Relative Paths

```markdown
<%*
// Relative to vault root
await tp.file.create_new(
  tp.file.find_tfile("template.md"),
  "folder/subfolder/new-file"
);
%>
```

---

## Performance Issues

### Issue 13: Slow Template Execution

**Symptoms**:
- Templates take 10+ seconds to execute
- Obsidian freezes during template insertion
- Timeout errors

**Solutions**:

#### Solution A: Profile Your Template

Add timing:

```markdown
<%*
const start = Date.now();

// Your template code here...

const duration = Date.now() - start;
tR += `\n\n<!-- Executed in ${duration}ms -->`;
%>
```

Identify slow sections.

#### Solution B: Cache Expensive Operations

**Slow**:
```markdown
<%*
for (let i = 0; i < 100; i++) {
  const files = tp.app.vault.getMarkdownFiles(); // Called 100 times
  tR += files.length;
}
%>
```

**Fast**:
```markdown
<%*
const files = tp.app.vault.getMarkdownFiles(); // Called once
for (let i = 0; i < 100; i++) {
  tR += files.length;
}
%>
```

#### Solution C: Limit API Calls

**Slow**:
```markdown
<%*
for (let i = 0; i < 10; i++) {
  const response = await tp.obsidian.request({url: "..."});
  tR += response;
}
%>
```

**Fast**:
```markdown
<%*
const response = await tp.obsidian.request({url: "..."});
for (let i = 0; i < 10; i++) {
  tR += response;
}
%>
```

#### Solution D: Use Efficient Loops

**Slow**:
```markdown
<%*
const items = [];
for (let i = 0; i < 1000; i++) {
  tR += "- Item\n"; // Concatenating 1000 times
}
%>
```

**Fast**:
```markdown
<%*
const items = [];
for (let i = 0; i < 1000; i++) {
  items.push("- Item");
}
tR += items.join("\n");
%>
```

---

### Issue 14: High Memory Usage

**Symptoms**:
- Obsidian uses excessive RAM
- System slow when using templates
- Out of memory errors

**Solutions**:

#### Solution A: Avoid Large String Concatenation

**Bad**:
```markdown
<%*
let huge = "";
for (let i = 0; i < 100000; i++) {
  huge += "text\n";
}
tR += huge;
%>
```

**Good**:
```markdown
<%*
const lines = [];
for (let i = 0; i < 100000; i++) {
  lines.push("text");
}
tR += lines.join("\n");
%>
```

#### Solution B: Process in Chunks

```markdown
<%*
const chunkSize = 1000;
const totalItems = 10000;

for (let i = 0; i < totalItems; i += chunkSize) {
  const chunk = [];
  for (let j = i; j < i + chunkSize && j < totalItems; j++) {
    chunk.push(`Item ${j}`);
  }
  tR += chunk.join("\n") + "\n";
}
%>
```

#### Solution C: Clean Up Variables

```markdown
<%*
let largeData = generateLargeData();
tR += processData(largeData);

// Release memory
largeData = null;
%>
```

---

## Integration Issues

### Issue 15: Dataview Integration Problems

**Symptoms**:
- Dataview queries in templates don't work
- `dataview` is undefined
- Queries show as code blocks

**Solutions**:

#### Solution A: Use Dataview Code Blocks

Dataview queries must be in code blocks, not template syntax:

**Correct**:
```markdown
\`\`\`dataview
TABLE status, priority
FROM "projects"
WHERE status = "active"
\`\`\`
```

**Not**:
```markdown
<%* 
// This won't work
tR += "dataview query...";
%>
```

#### Solution B: Generate Dataview Dynamically

```markdown
<%*
const folder = await tp.system.prompt("Folder to query");
tR += `\`\`\`dataview\n`;
tR += `TABLE file.ctime, file.mtime\n`;
tR += `FROM "${folder}"\n`;
tR += `\`\`\``;
%>
```

---

### Issue 16: Project-AI Data Access Issues

**Symptoms**:
- Can't read `data/ai_persona/state.json`
- File not found errors
- Permission denied errors

**Solutions**:

#### Solution A: Use Absolute Paths

```javascript
// In user script (templates/scripts/project-ai-utils.js)
const fs = require('fs');
const path = require('path');

function getAIPersonaMood() {
    // Absolute path from vault root
    const dataPath = path.join(
        "T:\\Project-AI-main",
        "data",
        "ai_persona",
        "state.json"
    );
    
    try {
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        return data.current_mood || 'neutral';
    } catch (error) {
        console.error("Error reading AI persona data:", error);
        return 'unknown';
    }
}
```

#### Solution B: Handle Missing Files Gracefully

```javascript
function getProjectAIData(dataFile) {
    const basePath = "T:\\Project-AI-main\\data";
    const fullPath = path.join(basePath, dataFile);
    
    if (!fs.existsSync(fullPath)) {
        console.warn(`File not found: ${fullPath}`);
        return null;
    }
    
    try {
        return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
    } catch (error) {
        console.error(`Error parsing ${dataFile}:`, error);
        return null;
    }
}
```

#### Solution C: Check File Permissions

```powershell
# Verify files are readable
Get-Acl "T:\Project-AI-main\data\ai_persona\state.json"
```

---

## Advanced Troubleshooting

### Using Developer Console

Press `Ctrl+Shift+I` to open Developer Console.

#### Console Tab

View JavaScript errors:

```javascript
// Red errors indicate problems
Uncaught TypeError: tp.user.myFunction is not a function
  at eval (eval at <anonymous>, <anonymous>:1:1)
```

#### Sources Tab

Debug template execution:

1. Sources → Filesystem
2. Find template file
3. Set breakpoints
4. Step through execution

#### Network Tab

Monitor API calls:

1. Network tab
2. Execute template
3. View HTTP requests
4. Check response codes

---

### Verbose Logging

Enable detailed logging:

1. Settings → Templater → Enable debug mode (if available)
2. Or add to templates:

```markdown
<%*
console.log("Template started");
console.log("Run mode:", tp.config.run_mode);
console.log("Target file:", tp.config.target_file.path);

// Your code...

console.log("Template completed");
%>
```

View logs in Developer Console.

---

### Template Testing Environment

Create test vault for safe experimentation:

1. Create folder: `T:\templater-testing`
2. Open in Obsidian as new vault
3. Install Templater
4. Test templates without affecting Project-AI

---

### Backup and Recovery

Before major changes:

```powershell
# Backup templates
Copy-Item "T:\Project-AI-main\templates" -Destination "T:\templates-backup-$(Get-Date -Format 'yyyy-MM-dd')" -Recurse

# Backup Templater settings
Copy-Item "T:\Project-AI-main\.obsidian\plugins\templater-obsidian\data.json" -Destination "T:\templater-config-backup.json"
```

If something breaks:

```powershell
# Restore templates
Copy-Item "T:\templates-backup-2024-12-20\*" -Destination "T:\Project-AI-main\templates" -Recurse -Force

# Restore settings
Copy-Item "T:\templater-config-backup.json" -Destination "T:\Project-AI-main\.obsidian\plugins\templater-obsidian\data.json" -Force
```

---

## Getting Additional Help

### Documentation Resources

1. **This Guide**: `TEMPLATER_SETUP_GUIDE.md`
2. **Command Reference**: `TEMPLATER_COMMAND_REFERENCE.md`
3. **Official Docs**: https://silentvoid13.github.io/Templater/
4. **Moment.js Formats**: https://momentjs.com/docs/

### Community Support

1. **Obsidian Forum**:
   - https://forum.obsidian.md/c/plugins/templater/
   - Search existing topics
   - Ask new questions

2. **GitHub Issues**:
   - https://github.com/SilentVoid13/Templater/issues
   - Check known issues
   - Report bugs

3. **Reddit**:
   - r/ObsidianMD
   - r/ObsidianPlugins

### Reporting Issues

When asking for help, include:

1. **Obsidian Version**: Settings → About
2. **Templater Version**: Settings → Community Plugins
3. **Operating System**: Windows, Mac, Linux
4. **Error Message**: Exact text from Developer Console
5. **Template Code**: Minimal example that reproduces issue
6. **Steps to Reproduce**: What you did before error occurred

**Template for Bug Reports**:

```markdown
## Environment
- Obsidian: 1.4.16
- Templater: 2.19.1
- OS: Windows 11

## Problem
Template execution fails with "function not defined" error.

## Steps to Reproduce
1. Create new note
2. Insert template: `basic-note-template.md`
3. Error appears in console

## Expected Behavior
Template should execute and populate note.

## Actual Behavior
Error: "tp.user.generate_id is not a function"

## Template Code
\`\`\`markdown
ID: <% tp.user.generate_id() %>
\`\`\`

## Error Message
\`\`\`
Uncaught TypeError: tp.user.generate_id is not a function
  at eval (eval at <anonymous>, <anonymous>:1:1)
\`\`\`

## Additional Context
User scripts folder is set to "templates/scripts" and utils.js exists.
```

---

## Common Error Messages

### "Template execution timeout"

**Cause**: Template took longer than timeout setting  
**Fix**: Increase timeout in Settings → Templater → Command timeout

### "Cannot find module 'X'"

**Cause**: Trying to use unavailable Node.js module  
**Fix**: Use only built-in modules (fs, path, child_process, util, os)

### "tp.user.X is not a function"

**Cause**: User script not loaded or function not exported  
**Fix**: 
1. Verify user scripts folder setting
2. Check `module.exports` in script
3. Restart Obsidian

### "Invalid date"

**Cause**: Wrong date format or invalid date value  
**Fix**: Use Moment.js format tokens (YYYY-MM-DD, not %Y-%m-%d)

### "File already exists"

**Cause**: Trying to create file that already exists  
**Fix**: Check if file exists first or use unique names

### "Permission denied"

**Cause**: File/folder permissions issue  
**Fix**: Check file permissions with `icacls` (Windows) or `chmod` (Unix)

---

## Prevention Tips

### Best Practices to Avoid Issues

1. **Always Use Await**:
   ```markdown
   <%* const result = await asyncFunction() %>
   ```

2. **Validate User Input**:
   ```markdown
   <%*
   const input = await tp.system.prompt("Enter date");
   if (/^\d{4}-\d{2}-\d{2}$/.test(input)) {
     tR += input;
   } else {
     tR += "Invalid format";
   }
   %>
   ```

3. **Handle Errors**:
   ```markdown
   <%*
   try {
     const result = riskyOperation();
     tR += result;
   } catch (error) {
     tR += `Error: ${error.message}`;
   }
   %>
   ```

4. **Test in Isolation**:
   - Test new templates in test vault first
   - Start simple, add complexity gradually
   - Use console.log for debugging

5. **Keep Backups**:
   - Back up templates before major changes
   - Version control with Git
   - Export important templates

6. **Stay Updated**:
   - Update Templater when new versions release
   - Check changelog for breaking changes
   - Test templates after updates

---

## Emergency Recovery

If everything is broken:

### Nuclear Option: Reinstall Templater

```powershell
# 1. Backup current state
Copy-Item "T:\Project-AI-main\.obsidian\plugins\templater-obsidian" -Destination "T:\templater-backup" -Recurse

# 2. Remove plugin
Remove-Item "T:\Project-AI-main\.obsidian\plugins\templater-obsidian" -Recurse -Force

# 3. Remove from enabled list
$plugins = @("dataview")
$plugins | ConvertTo-Json | Set-Content "T:\Project-AI-main\.obsidian\community-plugins.json"

# 4. Restart Obsidian

# 5. Reinstall Templater from Community Plugins browser

# 6. Restore templates (but not plugin files)
Copy-Item "T:\templates-backup\*" -Destination "T:\Project-AI-main\templates" -Recurse -Force

# 7. Reconfigure settings
# Settings → Templater → Template folder location = templates
# Settings → Templater → User scripts folder = templates/scripts
```

---

**Need More Help?**

If this guide didn't solve your problem:

1. Check [[TEMPLATER_SETUP_GUIDE]] for detailed configuration
2. Check [[TEMPLATER_COMMAND_REFERENCE]] for syntax help
3. Search [Templater Discussions](https://github.com/SilentVoid13/Templater/discussions)
4. Ask in [Obsidian Forum](https://forum.obsidian.md/)
5. Report bug on [GitHub Issues](https://github.com/SilentVoid13/Templater/issues)

---

## System Reference

### Related Architecture Documentation

- [[docs/architecture/ARCHITECTURE_OVERVIEW]] - Overall system architecture
- [[docs/architecture/MODULE_CONTRACTS]] - Module interfaces and contracts
- [[docs/architecture/STATE_MODEL]] - State management patterns
- [[docs/architecture/WORKFLOW_ENGINE]] - Workflow execution engine
- [[docs/architecture/INTEGRATION_LAYER]] - Integration patterns
- [[docs/architecture/ROOT_STRUCTURE]] - Project structure and organization

### Related Setup & Configuration

- [[TEMPLATER_SETUP_GUIDE]] - Complete installation and setup guide
- [[TEMPLATER_QUICK_REFERENCE]] - Quick command reference
- [[TEMPLATER_COMMAND_REFERENCE]] - Detailed command documentation
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration dashboard
- [[DATAVIEW_SETUP_GUIDE]] - Dataview plugin setup
- [[docs/developer/config.md]] - Configuration management

### Related Troubleshooting Guides

- [[vault-troubleshooting-guide]] - Comprehensive vault troubleshooting
- [[docs/dataview-examples/TROUBLESHOOTING]] - Dataview query troubleshooting
- [[GRAPH_VIEW_GUIDE]] - Graph view configuration
- [[TAG_WRANGLER_GUIDE]] - Tag management
- [[EXCALIDRAW_GUIDE]] - Excalidraw integration

### Related Developer Documentation

- [[docs/developer/DEVELOPER_QUICK_REFERENCE]] - Developer quick reference
- [[docs/developer/DEVELOPMENT]] - Development environment setup
- [[docs/developer/HOW_TO_RUN]] - Running the application
- [[docs/developer/checks.md]] - Quality checks and testing
- [[docs/developer/CONTRIBUTING]] - Contributing guidelines

### Related Security Documentation

- [[SECURITY]] - Security policy
- [[docs/PATH_SECURITY_GUIDE]] - Path security guidelines
- [[INPUT_VALIDATION_SECURITY_AUDIT]] - Input validation audit
- [[docs/security_compliance/SECURITY_AGENTS_GUIDE]] - Security agents guide
- [[docs/security_compliance/THREAT_MODEL_SECURITY_WORKFLOWS]] - Threat model

### Related Automation

- [[.github/AUTOMATION]] - GitHub automation workflows
- [[.github/SECURITY_AUTOMATION]] - Security automation
- [[.github/ISSUE_AUTOMATION]] - Issue management automation

### Common Problem → Solution Map

| Problem Category | This Guide Section | Related System Documentation |
|------------------|-------------------|------------------------------|
| Installation fails | [[#installation-issues]] | [[TEMPLATER_SETUP_GUIDE]], [[docs/developer/config.md]] |
| Template won't execute | [[#template-execution-issues]] | [[docs/architecture/WORKFLOW_ENGINE]], [[TEMPLATER_QUICK_REFERENCE]] |
| Scripts not working | [[#user-scripts-issues]] | [[TEMPLATER_COMMAND_REFERENCE]], [[docs/architecture/MODULE_CONTRACTS]] |
| Syntax errors | [[#syntax-errors]] | [[TEMPLATER_QUICK_REFERENCE]], [[docs/developer/checks.md]] |
| Performance slow | [[#performance-issues]] | [[docs/architecture/STATE_MODEL]], [[docs/developer/DEVELOPMENT]] |
| Plugin conflicts | [[#integration-issues]] | [[vault-troubleshooting-guide]], [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] |

### Quick Navigation

- **For Installation Help**: Start with [[TEMPLATER_SETUP_GUIDE]] → Return here if issues persist
- **For Command Syntax**: See [[TEMPLATER_QUICK_REFERENCE]] → [[TEMPLATER_COMMAND_REFERENCE]] for details
- **For Performance Issues**: Check [[docs/architecture/STATE_MODEL]] → [[docs/developer/DEVELOPMENT]]
- **For Security Concerns**: Review [[SECURITY]] → [[docs/PATH_SECURITY_GUIDE]]
- **For Vault Issues**: See [[vault-troubleshooting-guide]] → [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]

---

**Document Version**: 1.1.0  
**Last Updated**: 2026-04-20  
**Phase 5 Enhancement**: Added comprehensive system references and wiki links  
**Maintained by:** Project-AI Team
