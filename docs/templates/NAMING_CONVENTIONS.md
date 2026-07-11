# Template Naming Conventions

## Purpose

This document defines the naming conventions for all templates in the Project-AI Obsidian vault template system. Consistent naming ensures templates are easily discoverable, categorized correctly, and integrate seamlessly with automated workflows.

---

## Core Naming Pattern

All template filenames follow this strict pattern:

```
{category}-{type}-{variant}.md
```

### Component Definitions

1. **Category** (Required)
   - One of four primary categories
   - Always lowercase
   - Must be first component
   - Valid values:
     - `module-doc` - Module and code documentation
     - `agent-doc` - Agent task and execution reports
     - `architecture-doc` - Architecture and design documentation
     - `guide` - User guides and references

2. **Type** (Required)
   - Specific document type within category
   - Lowercase with hyphens between words
   - Should be 1-3 words
   - Describes primary purpose
   - Examples: `core-system`, `task-report`, `adr`, `quickstart`

3. **Variant** (Optional)
   - Specialized version of a type
   - Lowercase with hyphens
   - Used when multiple variants of same type exist
   - Examples: `api`, `feature`, `production`

### Separator Rules

- **Use hyphens (`-`)**: Always use hyphens to separate words
- **No underscores**: Never use `_` in template names
- **No spaces**: Spaces are strictly prohibited
- **No camelCase**: All lowercase only
- **No special characters**: Only alphanumeric and hyphens

### Extension

- **Always `.md`**: All templates must have `.md` extension
- Obsidian recognizes only Markdown templates

---

## Category-Specific Naming Standards

### Module Documentation (`module-doc-*`)

Templates for documenting Python code, modules, classes, and components.

**Pattern**: `module-doc-{component-type}-{specificity}.md`

**Examples**:
```
module-doc-core-system.md       # Core business logic modules
module-doc-gui-component.md     # PyQt6 UI components
module-doc-agent.md             # AI agent modules
module-doc-utility.md           # Utility and helper modules
module-doc-integration.md       # Integration modules
```

**Component Type Values**:
- `core-system` - Business logic in `src/app/core/`
- `gui-component` - UI components in `src/app/gui/`
- `agent` - AI agents in `src/app/agents/`
- `utility` - Helper modules
- `integration` - External service integrations

### Agent Documentation (`agent-doc-*`)

Templates for AI agent task reports and execution documentation.

**Pattern**: `agent-doc-{task-type}-{specialization}.md`

**Examples**:
```
agent-doc-task-report.md           # Standard task completion report
agent-doc-security-audit.md        # Security assessment findings
agent-doc-convergence-summary.md   # Multi-agent coordination
agent-doc-code-review.md           # Code review results
agent-doc-testing-summary.md       # Test execution reports
```

**Task Type Values**:
- `task-report` - General task completion
- `security-audit` - Security assessments
- `convergence-summary` - Multi-agent workflows
- `code-review` - Code analysis results
- `testing-summary` - Test execution outcomes

### Architecture Documentation (`architecture-doc-*`)

Templates for system design, decisions, and architectural documentation.

**Pattern**: `architecture-doc-{doc-type}-{scope}.md`

**Examples**:
```
architecture-doc-adr.md                  # Architectural Decision Record
architecture-doc-integration-api.md      # API integration specs
architecture-doc-design-pattern.md       # Reusable design patterns
architecture-doc-system-overview.md      # High-level system design
architecture-doc-data-flow.md            # Data flow documentation
```

**Doc Type Values**:
- `adr` - Architectural Decision Records
- `integration` - External service integration
- `design-pattern` - Reusable patterns
- `system-overview` - High-level architecture
- `data-flow` - Data movement and transformation

**Scope Values**:
- `api` - API-focused documentation
- `database` - Database architecture
- `security` - Security architecture
- `deployment` - Deployment architecture

### Guides and References (`guide-*`)

Templates for user guides, developer references, and operational documentation.

**Pattern**: `guide-{guide-type}-{audience}.md`

**Examples**:
```
guide-quickstart-feature.md           # Feature quickstart guides
guide-troubleshooting-production.md   # Production troubleshooting
guide-developer-reference.md          # API and component references
guide-deployment-ops.md               # Deployment runbooks
guide-user-manual.md                  # End-user documentation
```

**Guide Type Values**:
- `quickstart` - Getting started guides
- `troubleshooting` - Problem resolution
- `developer-reference` - API documentation
- `deployment` - Deployment procedures
- `user-manual` - End-user instructions

**Audience Values**:
- `feature` - Feature-specific
- `production` - Production environment
- `ops` - Operations team
- `developer` - Development team
- `user` - End users

---

## Document Naming Conventions

When creating documents FROM templates, follow these conventions:

### Module Documentation Files

**Pattern**: `{module-name}.md`

**Rules**:
- Use actual module name from `src/app/`
- Lowercase with hyphens
- Match Python module filename (without `.py`)

**Examples**:
```
notification-service.md     # For src/app/core/notification_service.py
leather-book-interface.md   # For src/app/gui/leather_book_interface.py
oversight-agent.md          # For src/app/agents/oversight.py
```

### Agent Task Reports

**Pattern**: `agent-{id}-{task-slug}-{date}.md`

**Rules**:
- Agent ID: 3-digit number (e.g., `001`, `022`, `155`)
- Task slug: 2-4 word description, hyphenated
- Date: `YYYY-MM` or `YYYY-MM-DD`

**Examples**:
```
agent-003-template-subdirectory-2025-04.md
agent-022-password-policy-2025-04-20.md
agent-099-security-audit-2025-04.md
```

### Architecture Documents

**Pattern**: `{doc-type}-{number}-{title-slug}.md` OR `{topic-slug}.md`

**Rules**:
- ADRs: Always numbered sequentially
- Other docs: Descriptive slug

**Examples**:
```
adr-001-use-pyqt6-for-gui.md
adr-003-sqlite-state-persistence.md
openai-integration-spec.md
plugin-system-architecture.md
```

### Guides

**Pattern**: `{topic}-{guide-type}.md`

**Rules**:
- Topic: Main subject (1-3 words)
- Guide type: quickstart, troubleshooting, reference, manual

**Examples**:
```
deployment-quickstart.md
api-timeout-troubleshooting.md
developer-reference.md
image-generation-user-manual.md
```

---

## Forbidden Patterns

### Do NOT Use

❌ `Template_CoreSystem.md` - Underscores and camelCase
❌ `module doc core system.md` - Spaces
❌ `ModuleDoc-CoreSystem.md` - Mixed case
❌ `module-doc.md` - Missing type
❌ `core-system.md` - Missing category (when used as template)
❌ `module-doc-core-system.txt` - Wrong extension
❌ `module_doc_core_system.md` - Underscores

### Correct Alternatives

✅ `module-doc-core-system.md`
✅ `agent-doc-task-report.md`
✅ `architecture-doc-adr.md`
✅ `guide-quickstart-feature.md`

---

## Special Cases

### Template Metadata Files

Configuration and metadata files use leading dot:

```
.template-categories.json    # Category definitions
```

### Template Documentation Files

Documentation files in `templates/` directory:

```
README.md                    # Template system overview
TEMPLATE_USAGE_GUIDE.md     # Usage instructions
NAMING_CONVENTIONS.md       # This file
```

**Rules**:
- All caps for documentation files
- Hyphens separate words
- Clear descriptive names

---

## Validation Checklist

Before creating a new template, verify:

- [ ] Filename follows `{category}-{type}-{variant}.md` pattern
- [ ] All lowercase
- [ ] Hyphens only (no underscores or spaces)
- [ ] Category is one of: `module-doc`, `agent-doc`, `architecture-doc`, `guide`
- [ ] Type clearly describes template purpose
- [ ] Variant (if used) adds meaningful specialization
- [ ] Extension is `.md`
- [ ] Name is unique within templates directory
- [ ] Name matches entry in `.template-categories.json`

---

## Naming Changes and Deprecation

### Renaming Templates

When renaming templates:

1. **Update template file**: Rename with new convention
2. **Update `.template-categories.json`**: Change filename references
3. **Update README.md**: Update template references
4. **Update TEMPLATE_USAGE_GUIDE.md**: Update examples
5. **Create migration note**: Document old → new mapping
6. **Deprecation period**: Keep old template with deprecation notice for 30 days
7. **Archive old template**: Move to `templates/archived/` after deprecation period

### Deprecation Notice Template

Add to deprecated template:

```markdown
---
DEPRECATED: This template has been renamed
New template: {new-template-name}.md
Deprecation date: YYYY-MM-DD
Removal date: YYYY-MM-DD
---

# DEPRECATED TEMPLATE

This template has been deprecated and will be removed on {removal-date}.

**Please use**: `{new-template-name}.md` instead.

**Migration**: This template is identical to the new template. Simply use the new filename.
```

---

## Integration with Obsidian

### Templater Plugin Recognition

Templater recognizes templates by:
- Location in configured template folder (`templates/`)
- `.md` file extension
- Valid Markdown syntax

### Template Display Names

Templater displays templates with:
- Filename without extension
- Sorted alphabetically
- Grouped by prefix (category)

**Example Templater List**:
```
agent-doc-convergence-summary
agent-doc-security-audit
agent-doc-task-report
architecture-doc-adr
architecture-doc-design-pattern
architecture-doc-integration-api
guide-developer-reference
guide-quickstart-feature
guide-troubleshooting-production
module-doc-agent
module-doc-core-system
module-doc-gui-component
```

### Search Optimization

Consistent naming enables powerful search:

```
# Find all agent templates
agent-doc-*

# Find all architecture templates
architecture-doc-*

# Find all quickstart guides
guide-quickstart-*
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-04-20 | Initial naming conventions established |

---

## Governance

**Authority**: Principal Architect & Documentation Team
**Change Policy**: Naming convention changes require pull request review and team approval
**Review Schedule**: Annual review for relevance and clarity
**Feedback**: GitHub issues with `template-system` label

---

**Version**: 1.0.0
**Last Updated**: 2025-04-20
**Maintained By**: Principal Architect & Documentation Team

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
