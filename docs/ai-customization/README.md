# AI Customization Blueprint

This workspace now includes starter examples for all major customization primitives.

## What Is Included

- Always-on project rules: `.github/copilot-instructions.md`
- File-based instructions: `.github/instructions/*.instructions.md`
- Reusable slash commands: `.github/prompts/*.prompt.md`
- Multi-step workflow skill: `.github/skills/quality-gate/`
- Specialized custom agent: `.github/agents/security-reviewer.agent.md`
- Lifecycle hook config: `.github/hooks/quality-hooks.json`

## Activation Map

- Always-on instructions activate automatically in every request.
- File-based instructions activate on matching files via `applyTo` and on-demand via `description`.
- Prompt files activate when called as slash commands in chat.
- Skills activate when invoked as slash commands or when matched by description.
- Custom agents activate when selected in the agent picker or delegated by another agent.
- Hooks activate on configured lifecycle events.

## MCP Setup Pattern

Use MCP when tasks require external systems such as databases, APIs, cloud services, or ticketing tools.

1. Add or update MCP server config in your workspace MCP config file.
2. Validate server startup locally.
3. Add a custom agent or prompt constrained to MCP tools.
4. Keep credentials in environment variables, never committed files.

This repo already has an MCP config at `config/mcp.json`.

## Agent Plugins

Use plugins when you want a pre-packaged bundle of prompts, skills, agents, hooks, and MCP integrations.

1. Install plugin from your approved source.
2. Review included files and tool permissions.
3. Keep team-shared plugin-derived files in `.github/`.
4. Pin plugin versions and document update cadence.

## Recommended Adoption Order

1. Start with always-on and file-based instructions.
2. Add prompt files for repetitive tasks.
3. Add a skill for repeatable multi-step workflows.
4. Add custom agents for specialist roles.
5. Add MCP for external context.
6. Add hooks for deterministic enforcement.
