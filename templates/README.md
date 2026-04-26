# Project-AI Templater Templates

**Version:** 1.0  
**Last Updated:** 2026-01-23  
**Total Templates:** 15

---

## 📋 Overview

This directory contains 15 production-ready Templater templates for consistent documentation creation across Project-AI. Templates cover system documentation, API references, guides, and issue/decision tracking.

**Categories:**
- **System Documentation** (4): Comprehensive system, module, integration, and infrastructure docs
- **API Reference** (3): REST endpoints, class/module APIs, and CLI commands
- **Guides** (4): Developer guides, quickstarts, tutorials, and how-tos
- **Issues & Decisions** (4): Bug reports, feature requests, ADRs, and RFCs

---

## 🚀 Quick Start

### Prerequisites
1. **Obsidian** installed
2. **Templater plugin** installed and enabled
3. Template folder configured: `Settings → Templater → Template folder location` → `templates/`

### Using a Template

**Method 1: Command Palette**
1. Create new note or open existing
2. `Ctrl/Cmd + P` → "Templater: Insert Template"
3. Navigate to category (e.g., `system-docs/`)
4. Select template
5. Answer interactive prompts
6. Template generates with your inputs

**Method 2: Hotkey** (Recommended)
1. Set hotkey: `Settings → Hotkeys → Templater: Insert Template`
2. Press hotkey in any note
3. Select template and complete

**Method 3: Folder Templates** (Auto-apply)
1. `Settings → Templater → Folder Templates`
2. Map folder to template (e.g., `docs/api/` → `api-reference/rest-api-endpoint.md`)
3. New notes auto-apply template

---

## 📁 Template Catalog

### System Documentation Templates

#### 1. **New System Documentation** (`system-docs/new-system-documentation.md`)
**When to use:** Documenting new systems, major refactors, or canonical system references

**Includes:**
- Executive summary & business context
- Complete architecture (diagrams, components, flows)
- Security & compliance
- Performance & scalability
- Deployment & infrastructure
- Monitoring & alerting
- Disaster recovery
- Cost management
- Operational runbook

**Estimated time:** 45 minutes

---

#### 2. **New Module Documentation** (`system-docs/new-module-documentation.md`)
**When to use:** Documenting code modules, classes, or libraries

**Includes:**
- Module overview & responsibilities
- Complete API reference (classes, functions, properties)
- Data models & schemas
- Testing strategy & examples
- Performance analysis
- Security considerations
- Integration guide

**Estimated time:** 30 minutes

---

#### 3. **New Integration Documentation** (`system-docs/new-integration-documentation.md`)
**When to use:** Documenting API integrations, external service connections

**Includes:**
- Integration overview & use cases
- Connection details & authentication
- Request/response mapping
- Error handling & retry logic
- Circuit breaker patterns
- Monitoring & SLA
- Testing & deployment

**Estimated time:** 35 minutes

---

#### 4. **New Infrastructure Documentation** (`system-docs/new-infrastructure-documentation.md`)
**When to use:** Documenting cloud resources, servers, databases, infrastructure

**Includes:**
- Infrastructure overview & specs
- IaC (Terraform/CloudFormation) code
- Security configuration
- Monitoring & alerting
- Disaster recovery & backups
- Cost analysis & optimization
- Operational procedures

**Estimated time:** 40 minutes

---

### API Reference Templates

#### 5. **REST API Endpoint** (`api-reference/rest-api-endpoint.md`)
**When to use:** Documenting REST API endpoints

**Includes:**
- Endpoint spec (URL, method, version)
- Request/response schemas
- Authentication & authorization
- Error codes & handling
- Rate limiting
- Code examples (cURL, Python, JS, Node)
- Testing examples

**Estimated time:** 25 minutes

---

#### 6. **Class/Module API** (`api-reference/class-module-api.md`)
**When to use:** Documenting code classes, modules, interfaces

**Includes:**
- Class overview & import
- Constructor documentation
- Methods & properties
- Type annotations
- Inheritance hierarchy
- Usage examples
- Testing examples

**Estimated time:** 20 minutes

---

#### 7. **CLI Command** (`api-reference/cli-command.md`)
**When to use:** Documenting command-line tools and commands

**Includes:**
- Command syntax & usage
- Arguments & options
- Flags & environment variables
- Examples & use cases
- Configuration files
- Troubleshooting guide

**Estimated time:** 15 minutes

---

### Guide Templates

#### 8. **Developer Guide** (`guides/developer-guide.md`)
**When to use:** Creating comprehensive development guides

**Includes:**
- Development environment setup
- Architecture overview
- Coding standards & patterns
- Testing requirements
- Contribution workflow
- Debugging & troubleshooting

**Estimated time:** 30 minutes

---

#### 9. **Quickstart Guide** (`guides/quickstart-guide.md`)
**When to use:** Creating quick getting-started guides

**Includes:**
- Prerequisites
- Installation steps
- First-time configuration
- "Hello World" example
- Next steps
- Common issues

**Estimated time:** 20 minutes

---

#### 10. **Tutorial** (`guides/tutorial.md`)
**When to use:** Creating step-by-step learning tutorials

**Includes:**
- Learning objectives
- Prerequisites
- Step-by-step instructions with code
- Checkpoints & validation
- Summary & next steps
- Further reading

**Estimated time:** 25 minutes

---

#### 11. **How-To Guide** (`guides/how-to-guide.md`)
**When to use:** Creating task-focused procedural guides

**Includes:**
- Task overview & goal
- Prerequisites
- Step-by-step procedure
- Expected outcomes
- Troubleshooting
- Related guides

**Estimated time:** 20 minutes

---

### Issue & Decision Templates

#### 12. **Issue/Bug Template** (`issues-decisions/issue-bug.md`)
**When to use:** Reporting bugs or issues

**Includes:**
- Issue description & severity
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots/logs
- Impact assessment
- Proposed solution

**Estimated time:** 15 minutes

---

#### 13. **Feature Request** (`issues-decisions/feature-request.md`)
**When to use:** Proposing new features or enhancements

**Includes:**
- Feature description
- Problem statement & motivation
- Proposed solution
- Alternatives considered
- Success criteria
- Implementation plan
- Resource requirements

**Estimated time:** 15 minutes

---

#### 14. **Architecture Decision Record (ADR)** (`issues-decisions/adr.md`)
**When to use:** Documenting architectural decisions

**Includes:**
- Decision context & status
- Decision drivers
- Considered options (pros/cons)
- Decision outcome
- Consequences
- Implementation notes
- References

**Estimated time:** 30 minutes

---

#### 15. **RFC (Request for Comments)** (`issues-decisions/rfc.md`)
**When to use:** Proposing significant changes for team review

**Includes:**
- RFC metadata (number, status, authors)
- Abstract & motivation
- Detailed design
- Rationale & alternatives
- Prior art
- Unresolved questions
- Implementation timeline

**Estimated time:** 35 minutes

---

## 🎨 Template Features

All templates include:
- ✅ **Interactive prompts** for guided completion
- ✅ **Dropdown suggesters** for consistent values
- ✅ **Rich YAML metadata** (15-20 fields)
- ✅ **Auto-generated dates** and timestamps
- ✅ **Code examples** in multiple languages
- ✅ **Tables** for structured data
- ✅ **Checklists** for tracking
- ✅ **Links** to related documentation

System docs additionally include:
- ✅ **Mermaid diagrams** for architecture
- ✅ **Dataview queries** for aggregation
- ✅ **Performance metrics**
- ✅ **Security checklists**

---

## 📖 Templater Syntax Guide

### Interactive Prompts
```javascript
<% tp.system.prompt("Prompt text", "default_value") %>
```
- Displays input dialog
- Returns user input
- Default shown as placeholder

### Dropdown Suggesters
```javascript
<% tp.system.suggester(
  ["Display 1", "Display 2"],  // What user sees
  ["value1", "value2"]          // What gets inserted
) %>
```
- Arrow keys to select
- Enter to confirm
- Ensures consistency

### Dynamic Dates
```javascript
<% tp.date.now("YYYY-MM-DD") %>           // 2026-01-23
<% tp.date.now("YYYY-MM-DD", 30) %>       // 30 days from now
<% tp.date.now("YYYY-MM-DD HH:mm") %>     // 2026-01-23 10:30
```

### File Context
```javascript
<% tp.file.title %>                       // Current file name
<% tp.frontmatter.field %>                // Access metadata
```

### Conditional Logic
```javascript
<% if condition %>
  Content when true
<% endif %>
```

---

## 🎯 Best Practices

### Responding to Prompts
1. **Be specific:** "User authentication system" not "auth"
2. **Include units:** "30 seconds" not "30"
3. **Use consistent terms:** Match existing documentation
4. **Fill required prompts:** Don't skip unless intentional
5. **Use defaults wisely:** Modify when appropriate

### After Generation
1. **Review all sections:** Ensure prompts filled correctly
2. **Customize:** Add project-specific details
3. **Add examples:** Real code/data better than placeholders
4. **Link documents:** Connect related docs with `[[links]]`
5. **Update metadata:** Set correct status, tags, dates

### Maintenance
1. **Review quarterly:** Follow template's review_cycle
2. **Update when changed:** Keep docs in sync with code
3. **Fix broken links:** Use Obsidian link checker
4. **Update metadata:** Keep last_verified current
5. **Archive deprecated:** Update status field

---

## 🔧 Troubleshooting

### Template not appearing
**Solution:** Check Templater settings → Template folder location = `templates/`

### Prompts not showing
**Solution:**
1. Ensure Templater enabled
2. Check syntax: `<% tp.system.prompt(...) %>`
3. Restart Obsidian

### Suggester not working
**Solution:**
1. Verify arrays same length
2. Check syntax: `<% tp.system.suggester([...], [...]) %>`
3. Use arrow keys, not mouse

### Date not generating
**Solution:**
1. Check format: `YYYY-MM-DD` (uppercase)
2. Verify syntax: `<% tp.date.now("...") %>`

### Metadata not recognized
**Solution:**
1. Ensure YAML between `---` fences
2. Check indentation (2 spaces)
3. Validate with YAML linter

---

## 📊 Template Quality Metrics

| Category | Avg Size | Avg Lines | Prompts | Suggesters |
|----------|----------|-----------|---------|------------|
| System Docs | 26 KB | 920 | 40+ | 15+ |
| API Reference | 14 KB | 480 | 25+ | 10+ |
| Guides | 11 KB | 380 | 20+ | 8+ |
| Issues/Decisions | 8 KB | 280 | 15+ | 5+ |

**Total Interactive Elements:** 150+ prompts, 80+ suggesters

---

## 🚀 Advanced Usage

### Folder Templates (Auto-apply)
Map folders to templates for automatic application:

```
Settings → Templater → Folder Templates
  docs/api/         → api-reference/rest-api-endpoint.md
  docs/systems/     → system-docs/new-system-documentation.md
  docs/guides/      → guides/developer-guide.md
  issues/           → issues-decisions/issue-bug.md
```

### Custom Scripts
Add custom Templater scripts in `.obsidian/scripts/`:

```javascript
// auto-populate-metadata.js
function getGitInfo() {
  // Get current branch, author, etc.
  return { branch: "main", author: "dev-team" };
}

module.exports = getGitInfo;
```

Use in templates:
```javascript
<% const gitInfo = tp.user.getGitInfo() %>
Branch: <%= gitInfo.branch %>
```

### Template Inheritance
Create base templates, extend with specific variants:

```markdown
<!-- base-template.md -->
<% await tp.file.include("[[templates/common-header]]") %>
<!-- Specific content -->
<% await tp.file.include("[[templates/common-footer]]") %>
```

---

## 📚 Additional Resources

### Internal Documentation
- [[TEMPLATER_SETUP_GUIDE]] - Installation & configuration
- [[TEMPLATER_QUICK_REFERENCE]] - Syntax reference
- [[TEMPLATER_TROUBLESHOOTING_GUIDE]] - Common issues
- [[METADATA_QUICK_REFERENCE]] - Metadata standards
- [[AGENT-102-105-TEMPLATES-REPORT]] - Mission report with examples

### External Resources
- [Templater Documentation](https://silentvoid13.github.io/Templater/)
- [Obsidian Community Forum](https://forum.obsidian.md/)
- [Mermaid Diagram Syntax](https://mermaid-js.github.io/)
- [YAML Specification](https://yaml.org/spec/)

---

## 🤝 Contributing

### Adding New Templates
1. Create template in appropriate category folder
2. Follow existing naming convention: `kebab-case.md`
3. Include comprehensive YAML frontmatter
4. Add interactive prompts for all variables
5. Provide examples and use cases
6. Update this README with template description
7. Test template thoroughly

### Template Standards
- **Frontmatter:** Minimum 15 fields
- **Prompts:** All variables interactive
- **Examples:** Real-world usage shown
- **Metadata:** Audience, area, stakeholders defined
- **Review cycle:** Quarterly minimum
- **Documentation:** Clear purpose and use cases

---

## 📝 Changelog

### 2026-01-23 - v1.0 (Initial Release)
- ✅ Created 15 production-ready templates
- ✅ 4 System Documentation templates
- ✅ 3 API Reference templates
- ✅ 4 Guide templates
- ✅ 4 Issue & Decision templates
- ✅ Comprehensive README and usage guide
- ✅ Mission report with examples

---

## 📧 Support

**Questions or Issues:**
- Create issue: [[issues-decisions/issue-bug.md]]
- Feature request: [[issues-decisions/feature-request.md]]
- Email: projectaidevs@gmail.com

---

**Template System Version:** 1.0  
**Last Updated:** 2026-01-23  
**Maintained by:** Project-AI Team

*These templates are part of the Project-AI documentation automation initiative, designed to ensure consistent, high-quality documentation across all project areas.*
