# Templater Quick Reference Card

**One-page cheat sheet for daily use**

---

## 🚀 Quick Start

### Insert Template
1. `Ctrl+P` → "Templater: Insert template"
2. Or click 📋 icon in ribbon

### Create from Template
1. Right-click folder → "Create new note from template"
2. Select template → Enter filename

---

## 📝 Basic Syntax

```markdown
<% code %>          Execute and output
<%* code %>         Execute without output
<%* tR += text %>   Add text to output
```

---

## 🔥 Most Used Commands

```markdown
<!-- Current date -->
<% tp.date.now("YYYY-MM-DD") %>

<!-- File title -->
<% tp.file.title %>

<!-- Ask user -->
<%* await tp.system.prompt("Question?") %>

<!-- Multiple choice -->
<%* await tp.system.suggester(
  ["Option 1", "Option 2"],
  ["value1", "value2"]
) %>

<!-- Frontmatter value -->
<% tp.frontmatter.property %>

<!-- Cursor position -->
<% tp.file.cursor() %>
```

---

## 📅 Date Formats

```markdown
YYYY-MM-DD          → 2024-12-20
dddd, MMMM DD       → Friday, December 20
HH:mm:ss            → 14:30:45
YYYY-[W]WW          → 2024-W51
MMM DD, YYYY        → Dec 20, 2024
```

---

## 🛠️ User Functions

```markdown
<!-- Unique ID -->
<% tp.user.generate_id() %>

<!-- Relative date -->
<% tp.user.relative_date("2024-01-01") %>

<!-- Git branch -->
<%* tR += await tp.user.git_branch() %>

<!-- Word count -->
<% tp.user.word_count(tp.file.content) %>

<!-- Progress bar -->
<% tp.user.progress_bar(75) %>

<!-- Currency -->
<% tp.user.format_currency(1234.56, "USD") %>

<!-- Days between -->
<% tp.user.days_between("2024-01-01", "2024-12-31") %>

<!-- Season -->
<% tp.user.get_season() %>
```

---

## 🎯 Common Patterns

### Navigation Links
```markdown
[[<% tp.date.now("YYYY-MM-DD", -1) %>|← Yesterday]]
[[<% tp.date.now("YYYY-MM-DD", 1) %>|Tomorrow →]]
```

### Conditional Sections
```markdown
<%* if (tp.frontmatter.status === "active") { %>
## Active Project Content
<%* } else { %>
## Inactive Project Content
<%* } %>
```

### Task List from Input
```markdown
<%*
const tasks = await tp.system.prompt("Tasks (comma-separated)");
tasks.split(",").forEach(task => {
  tR += `- [ ] ${task.trim()}\n`;
});
%>
```

### Create New File
```markdown
<%*
await tp.file.create_new(
  tp.file.find_tfile("template.md"),
  "new-filename"
);
%>
```

---

## 📚 Available Templates

| Template | Use For |
|----------|---------|
| `basic-note-template.md` | General notes |
| `meeting-notes-template.md` | Meetings |
| `daily-note-template.md` | Daily journaling |
| `project-template.md` | Project management |
| `code-documentation-template.md` | Code docs |

---

## 🔧 Settings

**Location:** Settings → Templater

- **Template folder:** `templates`
- **User scripts folder:** `templates/scripts`
- **Command timeout:** 5 seconds (increase if needed)
- **Trigger on file creation:** ON
- **Auto jump to cursor:** ON

---

## 🐛 Troubleshooting

### Template not executing?
1. Check plugin enabled (Settings → Community Plugins)
2. Verify template folder path
3. Use `Ctrl+Shift+I` to check errors

### Prompts not appearing?
1. Add `await` before `tp.system.prompt()`
2. Check run mode (works in interactive only)

### User scripts not working?
1. Verify user scripts folder path
2. Check `module.exports` in script
3. Restart Obsidian

### Date formatting wrong?
Use Moment.js tokens: `YYYY-MM-DD`, not `%Y-%m-%d`

---

## 📖 Documentation

- **Setup Guide:** `TEMPLATER_SETUP_GUIDE.md` (48 pages)
- **Command Reference:** `TEMPLATER_COMMAND_REFERENCE.md` (28 pages)
- **Troubleshooting:** `TEMPLATER_TROUBLESHOOTING_GUIDE.md` (25 pages)
- **Installation Summary:** `TEMPLATER_INSTALLATION_COMPLETE.md`

---

## 🆘 Help

**Quick Diagnostics:**
1. Open Developer Console: `Ctrl+Shift+I`
2. Look for red errors in Console tab
3. Check TEMPLATER_TROUBLESHOOTING_GUIDE.md

**Common Issues:**
- Plugin not enabled → Settings → Community Plugins
- Templates not found → Check templates/ folder exists
- Functions undefined → Check user scripts folder setting

**External Help:**
- Official Docs: https://silentvoid13.github.io/Templater/
- Forum: https://forum.obsidian.md/c/plugins/templater/
- GitHub: https://github.com/SilentVoid13/Templater/issues

---

**Print this page for quick reference!**
