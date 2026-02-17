# Codacy.Instructions

---
    description: Configuration for AI behavior when interacting with Codacy's MCP Server
    applyTo: '**'
---
---

# Codacy Rules

Configuration for AI behavior when interacting with Codacy's MCP Server

## Code Quality Checks (When Applicable)

**When to run `codacy_cli_analyze`:**

- After making code changes to Python, JavaScript, or other source files
- When the Codacy MCP Server tools are available
- If the tool has not already been run for the current file in this session

**How to run:**

- Use the `codacy_cli_analyze` tool from Codacy's MCP Server with:
  - `rootPath`: set to the workspace path
  - `file`: set to the path of the edited file
  - `tool`: leave empty or unset
- If any issues are found in the new edits, propose and apply fixes for them.

**Circuit Breaker Rules:**

- Do NOT run the tool more than once per file per editing session
- Do NOT retry if the tool fails due to unavailability
- Do NOT run for non-code files (markdown, txt, json config files, etc.)

## When you tried to run the `codacy_cli_analyze` tool and the Codacy CLI is not installed

- Ask the user 'Codacy CLI is not installed. Would you like me to install it now?'
- If the user responds with "yes", run the `codacy_cli_install` tool and then continue with the original task
- If the user responds with "no", instruct the user that they can disable automatic analysis in the extension settings
- Wait for the user to respond before proceeding with any other actions

## Session Management

- Track which files have been analyzed in the current session
- Avoid redundant analysis of the same file
- If analysis was already performed, skip it and continue with the task

## When there are no Codacy MCP Server tools available, or the MCP Server is not reachable

- Suggest the user the following troubleshooting steps:
 - Try to reset the MCP on the extension
 - If the user is using VSCode, suggest them to review their Copilot > MCP settings in Github, under their organization or personal account. Refer them to Settings > Copilot > Enable MCP servers in Copilot. Suggested URL (https://github.com/settings/copilot/features) or <https://github.com/organizations/{organization-name}/settings/copilot/features> (This can only be done by their organization admins / owners)
- If none of the above steps work, suggest the user to contact Codacy support

## Trying to call a tool that needs a rootPath as a parameter

- Always use the standard, non-URL-encoded file system path

## OPTIONAL: Dependencies and Security Checks

**When dependency files are modified:**

- After adding dependencies to package.json, requirements.txt, pom.xml, or build.gradle
- You MAY optionally run the `codacy_cli_analyze` tool with:
  - `rootPath`: set to the workspace path
  - `tool`: set to "trivy"
  - `file`: leave empty or unset
- This is a best practice but not mandatory
- If security vulnerabilities are found:
  - Report them to the user
  - Suggest fixes if available
- **Do NOT block progress** if the tool is unavailable

## General Guidelines

- Use analysis tools judiciously to improve code quality
- "Propose fixes" means to suggest and optionally apply fixes
- Balance quality checks with workflow efficiency
- Do not run `codacy_cli_analyze` for:
  - Duplicated code detection (low priority)
  - Code complexity metrics (unless specifically requested)
  - Code coverage analysis (use dedicated test tools)
  - Non-code files (markdown, configs, etc.)
- Do not manually install Codacy CLI (use the MCP Server tools)
- When calling `codacy_cli_analyze`, only send provider, organization and repository if the project is a git repository

## Anti-Repetition Safeguards

**IMPORTANT: Prevent infinite loops**

- Maximum 1 analysis per file per session
- If a tool call fails, log it and move on (do NOT retry automatically)
- If the MCP Server is unavailable, skip analysis and continue
- Never wait indefinitely for tool responses
- Prioritize task completion over perfect analysis

## Whenever a call to a Codacy tool that uses `repository` or `organization` as a parameter returns a 404 error

- Offer to run the `codacy_setup_repository` tool to add the repository to Codacy
- If the user accepts, run the `codacy_setup_repository` tool
- Do not ever try to run the `codacy_setup_repository` tool on your own
- After setup, immediately retry the action that failed (only retry once)

---
