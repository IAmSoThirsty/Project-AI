---
title: "CLI: <% tp.file.title %>"
created: <% tp.date.now("YYYY-MM-DD") %>
type: documentation
doc_type: cli-reference
template_type: api-documentation
command_name: <% tp.system.prompt("Command name (e.g., deploy, test, build)") %>
cli_tool: <% tp.system.prompt("CLI tool name (e.g., project-ai-cli, npm, docker)") %>
status: <% tp.system.suggester(["✅ Stable", "🚧 Beta", "⚠️ Deprecated"], ["stable", "beta", "deprecated"]) %>
tags: [template, cli-reference, command-line, templater]
last_verified: <% tp.date.now("YYYY-MM-DD") %>
template_status: current
stakeholders: [developers, operations]
complexity_level: basic
estimated_completion: 15
requires: [templater-plugin]
review_cycle: quarterly
---

# 🖥️ CLI Command: <% tp.file.title %>

## Overview
**Command:** `<% tp.system.prompt("command_name") %>`  
**CLI Tool:** <% tp.frontmatter.cli_tool %>  
**Status:** <% tp.frontmatter.status %>  
**Category:** <% tp.system.suggester(["Deployment", "Testing", "Build", "Configuration", "Utility", "Management"], ["deployment", "testing", "build", "config", "utility", "management"]) %>

### Description
<% tp.system.prompt("What does this command do? (1-2 sentences)") %>

### Quick Example
```bash
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> <% tp.system.prompt("basic args (e.g., --env production)") %>
```

---

## Syntax

### Basic Syntax
```bash
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> [OPTIONS] [ARGUMENTS]
```

### Full Syntax
```bash
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> \
  --<% tp.system.prompt("option1") %>=<value> \
  --option2=<value> \
  [--flag] \
  <required_arg> \
  [optional_arg]
```

---

## Arguments

### Required Arguments
| Argument | Type | Description | Example |
|----------|------|-------------|---------|
| `<% tp.system.prompt("arg1") %>` | <% tp.system.suggester(["string", "path", "number", "boolean"], ["string", "path", "number", "boolean"]) %> | <% tp.system.prompt("Description") %> | `<% tp.system.prompt("example") %>` |

### Optional Arguments
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `[arg2]` | type | <% tp.system.prompt("default") %> | Description |

---

## Options

### Required Options
| Option | Short | Type | Description | Example |
|--------|-------|------|-------------|---------|
| `--<% tp.system.prompt("option1") %>` | `-<% tp.system.prompt("o") %>` | <% tp.system.prompt("type") %> | <% tp.system.prompt("Description") %> | `--option1=value` |

### Optional Options
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--<% tp.system.prompt("option2") %>` | `-<% tp.system.prompt("o2") %>` | type | <% tp.system.prompt("default") %> | Description |
| `--verbose` | `-v` | flag | false | Enable verbose output |
| `--dry-run` | | flag | false | Simulate without executing |
| `--help` | `-h` | flag | false | Show help message |

---

## Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--force` / `-f` | Force operation without confirmation | false |
| `--quiet` / `-q` | Suppress output | false |
| `--debug` | Enable debug mode | false |

---

## Environment Variables

**Used by this command:**
| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `<% tp.system.prompt("ENV_VAR_1") %>` | <% tp.system.suggester(["Yes", "No"], ["yes", "no"]) %> | <% tp.system.prompt("Description") %> | `export ENV_VAR_1=value` |
| `ENV_VAR_2` | No | Description | `export ENV_VAR_2=value` |

---

## Examples

### Example 1: Basic Usage
```bash
# <% tp.system.prompt("Example description") %>
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> <% tp.system.prompt("args") %>
```

**Output:**
```
<% tp.system.prompt("Expected output") %>
```

### Example 2: With Options
```bash
# <% tp.system.prompt("Example with options description") %>
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> \
  --<% tp.system.prompt("option1") %>=<% tp.system.prompt("value1") %> \
  --option2=value2 \
  <% tp.system.prompt("argument") %>
```

### Example 3: Advanced Usage
```bash
# <% tp.system.prompt("Advanced example description") %>
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> \
  --verbose \
  --config=custom-config.yml \
  --output=results/ \
  input-file.txt
```

### Example 4: Dry Run
```bash
# Preview changes without executing
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> --dry-run <% tp.system.prompt("args") %>
```

---

## Output

### Success Output
```
<% tp.system.prompt("Success output format") %>
✓ Operation completed successfully
Summary: <details>
Exit code: 0
```

### Error Output
```
<% tp.system.prompt("Error output format") %>
✗ Error: <error message>
Exit code: 1
```

### Exit Codes
| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1 | General error | Check error message |
| 2 | Invalid arguments | Fix command syntax |
| 126 | Permission denied | Check permissions |
| 127 | Command not found | Install tool |

---

## Common Use Cases

### Use Case 1: <% tp.system.prompt("Use case name") %>
**Scenario:** <% tp.system.prompt("When to use this") %>

**Command:**
```bash
<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> <% tp.system.prompt("specific args") %>
```

**Expected Result:** <% tp.system.prompt("What happens") %>

---

### Use Case 2: [Name]
[Repeat structure]

---

## Configuration File

**Config File:** `<% tp.system.prompt("Config file path (e.g., .project-ai-config.yml)", "N/A") %>`

**Format:**
```yaml
<% tp.frontmatter.command_name %>:
  <% tp.system.prompt("option1") %>: <% tp.system.prompt("value") %>
  option2: value
  flags:
    verbose: true
    dry_run: false
```

---

## Troubleshooting

### Common Errors

#### Error 1: "<% tp.system.prompt("Error message") %>"
**Cause:** <% tp.system.prompt("Why this happens") %>

**Solution:**
```bash
# <% tp.system.prompt("Fix command") %>
```

#### Error 2: "Permission denied"
**Cause:** Insufficient permissions

**Solution:**
```bash
sudo <% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> <args>
# OR
chmod +x <file>
```

---

## Related Commands
- [[<% tp.system.prompt("Related command 1") %>]] - Description
- [[Related command 2]] - Description

---

## Aliases & Shortcuts

```bash
# Add to ~/.bashrc or ~/.zshrc
alias <% tp.system.prompt("alias_name") %>='<% tp.frontmatter.cli_tool %> <% tp.frontmatter.command_name %> <% tp.system.prompt("common_args") %>'
```

---

**Last Updated:** <% tp.date.now("YYYY-MM-DD HH:mm") %>  
*Template: `templates/api-reference/cli-command.md`*
