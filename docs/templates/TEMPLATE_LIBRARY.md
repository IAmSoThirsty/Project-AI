# Template Library - Complete Usage Guide

**Version:** 2.0.0
**Last Updated:** 2026-04-20
**Maintained By:** AGENT-021 (Template Creation Specialist)
**Status:** Production-Ready documentation assets; not runtime deployment approval

---

## Executive Summary

The Project-AI Template Library provides **12 production-ready Obsidian
documentation templates** designed for comprehensive documentation across
module documentation, agent reports, architecture decisions, and user guides.
This status describes the templates, not the production readiness of the
Project-AI runtime. Each template is built with Templater plugin integration,
complete YAML frontmatter compliance with the metadata schema, and intelligent
prompting for dynamic content generation.

**Total Templates:** 12
**Categories:** 4 (Module Documentation, Agent Documentation, Architecture, Guides)
**Metadata Fields:** 75+ fields (schema-compliant)
**Tag Taxonomy:** 129 tags supported

---

## Table of Contents

1. [Template Categories](#template-categories)
2. [Module Documentation Templates](#module-documentation-templates)
3. [Agent Documentation Templates](#agent-documentation-templates)
4. [Architecture Documentation Templates](#architecture-documentation-templates)
5. [Guide Templates](#guide-templates)
6. [How to Use Templates](#how-to-use-templates)
7. [Customization Guide](#customization-guide)
8. [Template Selection Decision Tree](#template-selection-decision-tree)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Template Categories

### Overview

| Category | Templates | Primary Use | Complexity | Avg. Time |
|----------|-----------|-------------|------------|-----------|
| **Module Documentation** | 3 | Document code modules and components | High | 45-90 min |
| **Agent Documentation** | 3 | Agent task reports and audits | Medium | 20-90 min |
| **Architecture Documentation** | 3 | Design decisions and patterns | High | 60-120 min |
| **Guides** | 3 | User guides and references | Low-High | 20-90 min |

### Template Naming Convention

All templates follow the pattern: `[category]-[subcategory]-[specific-type].md`

**Examples:**
- `module-doc-core-system.md` → Module Documentation for Core Systems
- `agent-doc-task-report.md` → Agent Task Completion Report
- `architecture-doc-adr.md` → Architectural Decision Record

---

## Module Documentation Templates

### 1. Core System Module Documentation

**File:** `module-doc-core-system.md`
**Use For:** Business logic modules in `src/app/core/`
**Complexity:** High
**Estimated Time:** 45-60 minutes

**When to Use:**
- Documenting core business logic modules (e.g., `ai_systems.py`, `user_manager.py`)
- Creating API references for internal Python classes
- Documenting state management and persistence patterns

**Key Sections:**
- Module Overview with architecture context diagram
- Complete API Reference (classes, methods, parameters)
- Implementation Details (state management, data flow)
- Dependencies (internal and external)
- Usage Examples (basic, advanced, error handling)
- Testing Guidance with pytest examples
- Configuration and environment setup
- Performance and security considerations

**Template Variables:**
```python
tp.file.title              # Auto-populated from filename
tp.date.now("YYYY-MM-DD")  # Current date
tp.system.prompt()         # Interactive prompts for:
                           #   - Module name
                           #   - Module status
                           #   - Document status
```

**Example Use Case:**
```
Creating documentation for ai_systems.py:
1. Create new note: "AI Systems Module Documentation"
2. Apply template: module-doc-core-system
3. Answer prompts:
   - Module name: ai_systems.py
   - Module status: production
   - Document status: draft
4. Fill in API reference for all 6 classes
5. Add code examples from actual usage
6. Test all code examples work
7. Update status to "active"
```

**Frontmatter Fields:**
- `type`: `api_reference`
- `category`: `backend`
- `tags`: `module`, `core-system`, `api`, `implementation`, `architecture/backend`
- `technologies`: `Python`, `JSON`

---

### 2. GUI Component Module Documentation

**File:** `module-doc-gui-component.md`
**Use For:** PyQt6 UI components in `src/app/gui/`
**Complexity:** Medium
**Estimated Time:** 30-45 minutes

**When to Use:**
- Documenting PyQt6 widgets and panels
- Creating UI component API references
- Documenting signal/slot architecture
- Explaining widget hierarchies and layouts

**Key Sections:**
- Component Overview with visual sketch
- Widget Hierarchy (component tree diagram)
- API Reference (constructor, public methods, protected methods)
- Signals and Slots (comprehensive signal documentation)
- Layout and Styling (Qt stylesheets, theming)
- Event Handling (mouse, keyboard, custom events)
- Usage Examples (instantiation, integration, programmatic updates)
- Integration Patterns (event-driven, timer-based, dialog interaction)
- Testing GUI Components (pytest-qt examples)
- Accessibility (keyboard navigation, screen readers)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Component name
                    #   - Parent class (QWidget/QMainWindow/QDialog)
                    #   - Primary layout type
                    #   - Theme (Leather Book/Tron/Custom)
```

**Example Use Case:**
```
Documenting LeatherBookDashboard:
1. Create note: "Leather Book Dashboard Component"
2. Apply template: module-doc-gui-component
3. Answer prompts:
   - Component name: LeatherBookDashboard
   - Parent class: QWidget
   - Layout: QVBoxLayout
   - Theme: Leather Book
4. Document widget hierarchy (6 zones)
5. List all signals emitted
6. Add signal/slot connection examples
7. Include stylesheet code
```

**Frontmatter Fields:**
- `type`: `api_reference`
- `category`: `frontend`
- `tags`: `module`, `gui`, `pyqt6`, `ui-component`, `architecture/desktop`
- `technologies`: `Python`, `PyQt6`, `Qt Signals`

---

### 3. AI Agent Module Documentation

**File:** `module-doc-agent.md`
**Use For:** AI agent modules in `src/app/agents/`
**Complexity:** High
**Estimated Time:** 60-90 minutes

**When to Use:**
- Documenting specialized AI agents (oversight, planner, validator, explainability)
- Creating agent decision logic specifications
- Documenting input/output schemas
- Explaining agent coordination patterns

**Key Sections:**
- Agent Overview with classification matrix
- Architecture (agent pipeline, system context, lifecycle)
- Input/Output Specifications (JSON schemas, Python type hints, examples)
- Decision Logic (algorithm pseudocode, decision rules, confidence scoring)
- API Reference (class, methods, validation)
- Integration Patterns (synchronous, batch, chaining)
- Configuration (file-based, environment variables)
- Error Handling (exception hierarchy, error scenarios)
- Performance Considerations (latency, optimization)
- Testing Agent Behavior (test examples, coverage goals)
- Ethics and Safety (Asimov's Laws compliance, bias mitigation)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Agent name
                    #   - Agent type (oversight/planner/validator/explainability/custom)
                    #   - Decision model (rule-based/ML-based/hybrid)
                    #   - Algorithm type
```

**Example Use Case:**
```
Documenting OversightAgent:
1. Create note: "Oversight Agent Specification"
2. Apply template: module-doc-agent
3. Answer prompts:
   - Agent name: OversightAgent
   - Type: oversight
   - Decision model: rule-based
   - Algorithm: rule-based
4. Define input/output JSON schemas
5. Document all decision rules with weights
6. Create decision matrix
7. Add Four Laws validation implementation
```

**Frontmatter Fields:**
- `type`: `specification`
- `category`: `architecture`
- `tags`: `agent`, `ai-system`, `automation`, `decision-logic`, `architecture/backend`
- `technologies`: `Python`, `OpenAI`, `AI Agents`

---

## Agent Documentation Templates

### 4. Agent Task Report

**File:** `agent-doc-task-report.md`
**Use For:** Individual agent task completion reports
**Complexity:** Low
**Estimated Time:** 15-20 minutes

**When to Use:**
- After completing any agent task
- Documenting deliverables and quality verification
- Creating audit trails for agent executions
- Recording lessons learned from task execution

**Key Sections:**
- Executive Summary (charter, outcome, quality status)
- Agent Identification (profile, context, scope)
- Task Charter (original requirements, success criteria)
- Execution Summary (approach, methodology, key decisions, tools used)
- Deliverables (detailed list with verification methods)
- Quality Gates Verification (each gate with evidence)
- Audit Trail (timeline, files modified, API calls)
- Blockers and Resolutions (issues encountered and fixed)
- Metrics and Performance (execution metrics, resource usage)
- Lessons Learned (successes, improvements, recommendations)
- Next Steps (immediate actions, follow-up tasks)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Agent number (e.g., 021)
                    #   - Agent role
                    #   - Quality status
                    #   - Human review required (Yes/No)
```

**Example Use Case:**
```
After AGENT-021 completes template creation:
1. Create note: "AGENT-021 Task Report - Template Creation"
2. Apply template: agent-doc-task-report
3. Answer prompts:
   - Agent number: 021
   - Role: Template Creation Specialist
   - Quality status: ALL GATES PASSED
   - Review: No
4. List all 12 templates created
5. Document verification steps
6. Include quality gate evidence
7. Add lessons learned
```

**Frontmatter Fields:**
- `type`: `report`
- `category`: `governance`
- `tags`: `agent`, `task-report`, `execution`, `audit`, `deliverables`
- `status`: `completed` (default)

---

### 5. Security Audit Agent Report

**File:** `agent-doc-security-audit.md`
**Use For:** Security audits and vulnerability assessments
**Complexity:** High
**Estimated Time:** 45-90 minutes

**When to Use:**
- After running Bandit, pip-audit, or manual security reviews
- Documenting vulnerability findings and risk assessments
- Creating remediation plans for security issues
- Compliance reporting (OWASP, CWE, NIST)

**Key Sections:**
- Executive Summary (objective, scope, risk, immediate actions)
- Agent Identification (audit profile, authorization, compliance)
- Audit Scope (in/out scope, scan coverage)
- Methodology (automated scanning, manual review, pentesting)
- Executive Findings Summary (vulnerability counts, OWASP mapping)
- Vulnerability Details (per-vulnerability with CVE, CWE, CVSS, PoC, fixes)
- Risk Assessment (risk matrix, prioritization)
- Remediation Plan (immediate actions, short-term, long-term)
- Compliance Review (OWASP Top 10, best practices)
- Threat Model (attack surface, threat scenarios)
- Verification and Testing (test cases, pentest results)
- Appendices (full scan results, dependency audit, tool configs)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Agent number
                    #   - Audit type (automated/manual/hybrid)
                    #   - Risk level (CRITICAL/HIGH/MEDIUM/LOW)
                    #   - Vulnerabilities count
                    #   - Scope
                    #   - Framework (OWASP/CWE/Custom)
                    #   - Tools used
                    #   - Critical/High/Medium/Low vuln counts
                    #   - Next audit date
```

**Example Use Case:**
```
After Bandit security scan:
1. Create note: "Security Audit Report 2026-04-20"
2. Apply template: agent-doc-security-audit
3. Answer prompts:
   - Agent: 042
   - Type: automated
   - Risk: MEDIUM
   - Vulns: 5
   - Scope: src/app/core/user_manager.py
4. Document each vulnerability with CWE
5. Provide PoC code for critical issues
6. Create remediation steps
7. Include Bandit JSON output in appendix
```

**Frontmatter Fields:**
- `type`: `audit`
- `category`: `security`
- `tags`: `security`, `audit`, `vulnerability`, `assessment`, `penetration-test`, `security/audit`
- `classification`: `confidential`

---

### 6. Agent Convergence Summary

**File:** `agent-doc-convergence-summary.md`
**Use For:** Multi-agent fleet deployments and convergence verification
**Complexity:** Medium
**Estimated Time:** 30-45 minutes

**When to Use:**
- After completing a phase with multiple agents
- Verifying integration across agent deliverables
- Documenting multi-agent coordination outcomes
- Creating system-level status reports

**Key Sections:**
- Executive Summary (objective, agent count, status)
- Convergence Overview (context, objectives, strategy)
- Participating Agents (fleet roster, specialization distribution)
- Convergence Criteria (detailed criteria with measurements)
- Verification Results (automated and manual verification)
- Integration Status (integration matrix, health checks)
- Agent Coordination Matrix (dependency graph, events)
- System-Level Outcomes (deliverables inventory, knowledge growth)
- Quality Verification (metrics, QA checks)
- Issues and Resolutions (problems encountered and fixed)
- Next Phase Readiness (checklist, handoff, recommendations)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Convergence ID (e.g., PHASE-1)
                    #   - Scope (e.g., Phase 1 deployment)
                    #   - Number of agents
                    #   - Completion percentage
                    #   - Current/next phase
                    #   - Next convergence date
```

**Example Use Case:**
```
After Phase 1 completion (20 agents):
1. Create note: "Phase 1 Convergence Summary"
2. Apply template: agent-doc-convergence-summary
3. Answer prompts:
   - ID: PHASE-1
   - Scope: Foundation
   - Agents: 20
   - Completion: 100%
4. List all agents with status
5. Document integration points
6. Verify all criteria passed
7. Create handoff to Phase 2
```

**Frontmatter Fields:**
- `type`: `report`
- `category`: `governance`
- `tags`: `agent`, `convergence`, `multi-agent`, `coordination`, `fleet-deployment`

---

## Architecture Documentation Templates

### 7. Architectural Decision Record (ADR)

**File:** `architecture-doc-adr.md`
**Use For:** Significant architectural decisions
**Complexity:** High
**Estimated Time:** 60-120 minutes

**When to Use:**
- Making major technical decisions (framework choice, design patterns)
- Changing system architecture significantly
- Selecting technologies or external services
- Establishing architectural patterns or standards

**Key Sections:**
- Summary (one-sentence decision, impact)
- Context and Problem Statement (background, problem, scope, business context)
- Decision Drivers (functional/non-functional requirements, constraints)
- Considered Options (multiple options with pros/cons, effort, cost, risk)
- Options Comparison Matrix (multi-dimensional scoring)
- Decision Outcome (chosen option, decision statement, consequences)
- Rationale (technical/business/risk justification, key factors)
- Consequences (architectural/team/long-term impacts)
- Alternatives Considered (why rejected, learnings)
- Related Decisions (upstream/downstream/related ADRs)
- Implementation Notes (strategy, success criteria, rollback plan)
- References (documentation, external resources, prior art)
- Approval (decision makers, review process)

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - ADR number (e.g., 001)
                    #   - Status (proposed/accepted/deprecated/superseded)
                    #   - Deciders (team/role)
                    #   - Issue reference
                    #   - Option 1/2/3 names
                    #   - Selected option
                    #   - Initial/final status
                    #   - Next review date
```

**Example Use Case:**
```
Deciding on state persistence mechanism:
1. Create note: "ADR-005: JSON vs SQLite for State"
2. Apply template: architecture-doc-adr
3. Answer prompts:
   - Number: 005
   - Status: proposed
   - Deciders: Architecture Team
4. Document 3 options: JSON, SQLite, PostgreSQL
5. Compare with matrix (performance, complexity, etc.)
6. Select JSON with rationale
7. Document consequences and mitigations
8. Get approval signatures
```

**Frontmatter Fields:**
- `type`: `decision_record`
- `category`: `architecture`
- `tags`: `architecture`, `adr`, `decision`, `design`, `architecture/design`

---

### 8. Integration API Documentation

**File:** `architecture-doc-integration-api.md`
**Use For:** External service integrations
**Complexity:** Medium
**Estimated Time:** 45-60 minutes

**When to Use:**
- Documenting OpenAI, Hugging Face, GitHub API integrations
- Creating API contract specifications
- Documenting authentication mechanisms
- Explaining rate limits and error handling

**Key Sections:**
- Integration Overview (provider, purpose, type, base URL)
- Authentication (method, configuration, environment setup)
- API Endpoints (per-endpoint with request/response, examples)
- Error Handling (error codes, retry strategy)
- Rate Limits (limits, implementation)
- Security Considerations (key management, SSL, logging)
- Testing (mock server, unit tests)
- Related Documentation

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Service name (e.g., OpenAI GPT-4)
                    #   - API version
                    #   - Auth method (API Key/OAuth/JWT)
```

**Example Use Case:**
```
Documenting OpenAI integration:
1. Create note: "OpenAI GPT-4 Integration Specification"
2. Apply template: architecture-doc-integration-api
3. Answer prompts:
   - Service: OpenAI GPT-4
   - Version: v1
   - Auth: API Key
4. Document all endpoints used
5. Add request/response examples
6. Include error handling code
7. Document rate limits and backoff
```

**Frontmatter Fields:**
- `type`: `specification`
- `category`: `architecture`
- `tags`: `architecture`, `integration`, `api`, `external-service`

---

### 9. Design Pattern Documentation

**File:** `architecture-doc-design-pattern.md`
**Use For:** Reusable design patterns
**Complexity:** High
**Estimated Time:** 90-120 minutes

**When to Use:**
- Documenting architectural patterns used in Project-AI
- Creating pattern libraries (state persistence, signal/slot, plugin)
- Explaining design pattern implementations
- Teaching design patterns to team members

**Key Sections:**
- Intent (one-sentence purpose)
- Also Known As (alternative names)
- Motivation (problem context, when to use, when NOT to use)
- Applicability (conditions for use)
- Structure (class diagram, participants)
- Implementation (step-by-step with code)
- Sample Code (complete working example)
- Project-AI Usage (actual usage in codebase)
- Consequences (benefits, drawbacks, trade-offs)
- Known Uses (in Project-AI, in industry)
- Related Patterns
- References

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Category (Creational/Structural/Behavioral)
                    #   - Difficulty (Beginner/Intermediate/Advanced)
                    #   - Use case area
```

**Example Use Case:**
```
Documenting State Persistence pattern:
1. Create note: "State Persistence Pattern"
2. Apply template: architecture-doc-design-pattern
3. Answer prompts:
   - Category: Behavioral
   - Difficulty: Intermediate
   - Area: Core Systems
4. Explain JSON persistence pattern
5. Show class diagram with _save_state()
6. Provide code from ai_systems.py
7. List trade-offs (simplicity vs scalability)
```

**Frontmatter Fields:**
- `type`: `design`
- `category`: `architecture`
- `tags`: `architecture`, `design-pattern`, `best-practice`

---

## Guide Templates

### 10. Quickstart Feature Guide

**File:** `guide-quickstart-feature.md`
**Use For:** Getting started guides for features
**Complexity:** Low
**Estimated Time:** 20-30 minutes

**When to Use:**
- Onboarding users to new features
- Creating "15-minute quickstart" tutorials
- Providing basic usage examples
- Reducing time-to-first-success for users

**Key Sections:**
- What You'll Learn (objectives checklist)
- Prerequisites (required knowledge/tools)
- Step 1: Installation (with verification)
- Step 2: Basic Configuration
- Step 3: First Usage (simple example)
- Step 4: Common Use Cases (2-3 scenarios)
- Troubleshooting (common problems/solutions)
- Next Steps (links to advanced content)
- Related Resources

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Feature name
                    #   - Estimated time
                    #   - Prerequisites
```

**Example Use Case:**
```
Creating quickstart for image generation:
1. Create note: "Image Generation Quick Start"
2. Apply template: guide-quickstart-feature
3. Answer prompts:
   - Feature: Image Generation
   - Time: 15 minutes
   - Prerequisites: API key configured
4. Write installation steps
5. Add first usage example (generate image)
6. Include 2 use cases (styles, sizes)
7. List common errors and fixes
```

**Frontmatter Fields:**
- `type`: `guide`
- `category`: `documentation`
- `tags`: `guide`, `quickstart`, `tutorial`, `getting-started`
- `difficulty`: `beginner`

---

### 11. Troubleshooting Production Guide

**File:** `guide-troubleshooting-production.md`
**Use For:** Production incident runbooks
**Complexity:** Medium
**Estimated Time:** 45-60 minutes

**When to Use:**
- Creating runbooks for production issues
- Documenting incident response procedures
- Building diagnostic decision trees
- Training support teams on issue resolution

**Key Sections:**
- Symptoms (primary symptoms, observable indicators)
- Quick Diagnosis (verification commands)
- Immediate Actions (P0/P1 emergency steps)
- Diagnostic Steps (step-by-step troubleshooting)
- Root Causes (cause identification and resolution mapping)
- Resolutions (detailed fix procedures with rollback)
- Prevention (short/long-term prevention measures)
- Escalation Path (tiered escalation contacts)
- Post-Incident (documentation, postmortem, tasks)
- Related Runbooks

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Severity (P0/P1/P2/P3)
                    #   - Category (Performance/Availability/Security/Data)
                    #   - Problem category
```

**Example Use Case:**
```
Creating runbook for high memory usage:
1. Create note: "Troubleshooting High Memory Usage"
2. Apply template: guide-troubleshooting-production
3. Answer prompts:
   - Severity: P2
   - Category: Performance
4. List symptoms (>80% memory, slow responses)
5. Create diagnostic decision tree
6. Document 3 root causes with resolutions
7. Add prevention steps and monitoring
```

**Frontmatter Fields:**
- `type`: `runbook`
- `category`: `devops`
- `tags`: `troubleshooting`, `runbook`, `production`, `incident-response`

---

### 12. Developer Reference Guide

**File:** `guide-developer-reference.md`
**Use For:** API reference documentation
**Complexity:** High
**Estimated Time:** 60-90 minutes

**When to Use:**
- Creating comprehensive API documentation
- Documenting public SDK/library interfaces
- Providing complete method references with examples
- Building developer onboarding resources

**Key Sections:**
- Overview (purpose, key features, import)
- Quick Start (basic usage example)
- API Reference (class, constructor, methods with full signatures)
- Properties (all public properties)
- Events and Signals (PyQt6 signals)
- Configuration (file-based, environment)
- Error Handling (exception hierarchy, examples)
- Best Practices (do's and don'ts with examples)
- Advanced Usage (complex use cases)
- Testing (unit test examples)
- Performance (complexity analysis, optimization)
- Migration Guide (version transitions)
- Related Documentation
- Changelog

**Template Variables:**
```python
tp.system.prompt()  # Interactive prompts:
                    #   - Component name
                    #   - Component version
                    #   - Stability (Stable/Beta/Alpha)
```

**Example Use Case:**
```
Creating reference for UserManager:
1. Create note: "User Manager API Reference"
2. Apply template: guide-developer-reference
3. Answer prompts:
   - Component: UserManager
   - Version: 2.0.0
   - Stability: Stable
4. Document all public methods
5. Add code examples for each method
6. Include error handling patterns
7. Add performance notes and best practices
```

**Frontmatter Fields:**
- `type`: `api_reference`
- `category`: `documentation`
- `tags`: `developer-reference`, `api`, `sdk`, `documentation`

---

## How to Use Templates

### Basic Workflow

1. **Create New Note:**
   - In Obsidian, create a new note with descriptive title
   - Example: "User Manager Module Documentation"

2. **Apply Template:**
   - Use Templater command palette: `Ctrl/Cmd + P` → "Templater: Insert Template"
   - Select appropriate template from list
   - Or use hotkey if configured

3. **Answer Interactive Prompts:**
   - Templater will prompt for dynamic values
   - Provide accurate information for metadata generation
   - Values populate YAML frontmatter and content

4. **Fill Template Sections:**
   - Replace placeholder text with actual content
   - Remove unused sections (clearly marked)
   - Add additional sections as needed

5. **Verify Metadata:**
   - Check YAML frontmatter is valid
   - Ensure all required fields populated
   - Verify tags match taxonomy

6. **Review and Publish:**
   - Proofread content
   - Run spell check
   - Update `status` field to `active` or `published`

### Templater Commands

**Insert Template:**
```
Ctrl/Cmd + P → Templater: Insert Template
```

**Jump to Next Cursor:**
```
Alt + Tab (navigates to next <% tp.file.cursor() %> marker)
```

**Refresh Template:**
```
Ctrl/Cmd + P → Templater: Replace templates in the active file
```

---

## Customization Guide

### Modifying Templates

**To Customize a Template:**

1. **Locate Template:**
   ```
   T:\Project-AI-vault\templates\[template-name].md
   ```

2. **Edit in Obsidian:**
   - Open template file
   - Modify sections, add/remove content
   - Preserve Templater syntax: `<% %>`, `<%* %>`

3. **Test Changes:**
   - Create test note
   - Apply modified template
   - Verify prompts and output

4. **Document Changes:**
   - Update this guide if adding new templates
   - Update `.template-categories.json` for metadata

### Adding Custom Prompts

**Syntax:**
```javascript
<%* const value = await tp.system.prompt("Question to ask user:") %>
```

**Example:**
```javascript
<%* const security_level = await tp.system.prompt("Security classification (public/internal/confidential):") %>
```

**Use Value:**
```markdown
**Security Level:** <% security_level %>
```

### Custom Templater Functions

**Create User Functions:**

1. **Location:** `.obsidian/scripts/templater/`

2. **Example Function:**
   ```javascript
   // project_name.js
   module.exports = () => "Project-AI"
   ```

3. **Use in Template:**
   ```markdown
   **Project:** <% tp.user.project_name() %>
   ```

### Template Best Practices

1. **Preserve Structure:**
   - Keep table of contents updated
   - Maintain section hierarchy
   - Use consistent heading levels

2. **Interactive Prompts:**
   - Ask for values that vary per document
   - Use sensible defaults
   - Provide clear prompt text

3. **Metadata Compliance:**
   - Always include required fields
   - Use controlled vocabularies for enums
   - Follow tag taxonomy

4. **Code Examples:**
   - Test all code examples before documenting
   - Use real, working code from project
   - Include expected output

5. **Linking:**
   - Use `[[wikilinks]]` for internal references
   - Link to related documentation
   - Create bidirectional links

---

## Template Selection Decision Tree

```
Start: What are you documenting?

├─ CODE MODULE
│  ├─ Core business logic (src/app/core/)
│  │  └─ Use: module-doc-core-system.md
│  ├─ GUI component (src/app/gui/)
│  │  └─ Use: module-doc-gui-component.md
│  └─ AI agent (src/app/agents/)
│     └─ Use: module-doc-agent.md
│
├─ AGENT TASK/REPORT
│  ├─ Individual task completion
│  │  └─ Use: agent-doc-task-report.md
│  ├─ Security audit/vulnerability scan
│  │  └─ Use: agent-doc-security-audit.md
│  └─ Multi-agent convergence/phase completion
│     └─ Use: agent-doc-convergence-summary.md
│
├─ ARCHITECTURAL DECISION
│  ├─ Major decision (framework, pattern, technology)
│  │  └─ Use: architecture-doc-adr.md
│  ├─ External service integration
│  │  └─ Use: architecture-doc-integration-api.md
│  └─ Reusable design pattern
│     └─ Use: architecture-doc-design-pattern.md
│
└─ USER GUIDE/DOCUMENTATION
   ├─ Quick start tutorial (15-30 min)
   │  └─ Use: guide-quickstart-feature.md
   ├─ Production troubleshooting/runbook
   │  └─ Use: guide-troubleshooting-production.md
   └─ Developer API reference
      └─ Use: guide-developer-reference.md
```

---

## Best Practices

### Documentation Quality

1. **Completeness:**
   - Fill all template sections thoroughly
   - Don't skip examples or edge cases
   - Provide real code that works

2. **Accuracy:**
   - Test all code examples before documenting
   - Verify API signatures match implementation
   - Update documentation when code changes

3. **Clarity:**
   - Use simple, direct language
   - Define technical terms
   - Provide context for decisions

4. **Examples:**
   - Include multiple examples (basic, advanced, edge cases)
   - Show both good and bad patterns
   - Use actual project code when possible

### Metadata Management

1. **Required Fields:**
   - Always complete: `title`, `id`, `type`, `version`, `status`, `author`
   - Set appropriate `category` and `tags`
   - Use correct `classification` level

2. **Tag Selection:**
   - Use 3-7 tags per document
   - Include hierarchical tags (e.g., `architecture/backend`)
   - Follow tag taxonomy (see TAG_TAXONOMY.md)

3. **Version Control:**
   - Increment `version` on significant updates
   - Update `updated_date` on every edit
   - Use semantic versioning (major.minor.patch)

4. **Status Workflow:**
   - Start with `draft`
   - Move to `review` when complete
   - Set to `active` after approval
   - Mark `deprecated` when superseded

### Linking Strategy

1. **Create Bidirectional Links:**
   - Link related documentation both ways
   - Use "Related Documentation" sections
   - Build comprehensive knowledge graph

2. **Link Types:**
   - Dependency links: "This depends on [[X]]"
   - Consumer links: "Used by [[Y]]"
   - Alternative links: "See also [[Z]]"

3. **Validate Links:**
   - Ensure linked documents exist
   - Update links when files renamed
   - Check for broken links periodically

---

## Troubleshooting

### Common Issues

#### Issue 1: Templater Not Working

**Symptoms:**
- Template doesn't insert when selected
- No prompts appear
- Variables show as `<% tp.file.title %>` in output

**Solutions:**
1. Verify Templater plugin installed and enabled
2. Check template folder path: Settings → Templater → Template folder location
3. Restart Obsidian
4. Check for syntax errors in template

---

#### Issue 2: Invalid YAML Frontmatter

**Symptoms:**
- Metadata queries fail
- Dataview shows errors
- Validation fails

**Solutions:**
1. Validate YAML syntax (use YAML linter)
2. Check for unescaped special characters (`:`, `#`, `@`)
3. Ensure proper indentation (2 spaces)
4. Quote string values with special characters

**Example Fix:**
```yaml
# Bad
summary: This: has: colons

# Good
summary: "This: has: colons"
```

---

#### Issue 3: Prompts Showing Wrong Values

**Symptoms:**
- Default values incorrect
- Prompt questions unclear
- Values not populating in content

**Solutions:**
1. Update template with correct default values
2. Clarify prompt questions
3. Use `tp.system.prompt("Question", "Default Value")`
4. Test template in isolation

---

#### Issue 4: Template Selection Confusion

**Symptoms:**
- Unsure which template to use
- Multiple templates seem applicable
- Template doesn't match use case

**Solutions:**
1. Refer to [Template Selection Decision Tree](#template-selection-decision-tree)
2. Check "When to Use" section for each template
3. Review example use cases
4. Ask in team chat/documentation channel

---

## Appendix A: Template File Listing

| # | Template File | Category | Type | Lines |
|---|---------------|----------|------|-------|
| 1 | `module-doc-core-system.md` | Module | Core System | 580+ |
| 2 | `module-doc-gui-component.md` | Module | GUI Component | 750+ |
| 3 | `module-doc-agent.md` | Module | AI Agent | 900+ |
| 4 | `agent-doc-task-report.md` | Agent | Task Report | 450+ |
| 5 | `agent-doc-security-audit.md` | Agent | Security Audit | 520+ |
| 6 | `agent-doc-convergence-summary.md` | Agent | Convergence | 450+ |
| 7 | `architecture-doc-adr.md` | Architecture | ADR | 500+ |
| 8 | `architecture-doc-integration-api.md` | Architecture | Integration | 350+ |
| 9 | `architecture-doc-design-pattern.md` | Architecture | Pattern | 380+ |
| 10 | `guide-quickstart-feature.md` | Guide | Quickstart | 250+ |
| 11 | `guide-troubleshooting-production.md` | Guide | Troubleshooting | 380+ |
| 12 | `guide-developer-reference.md` | Guide | API Reference | 420+ |

**Total Lines of Template Code:** 5,930+ lines

---

## Appendix B: Templater Variable Reference

| Variable | Description | Example Output |
|----------|-------------|----------------|
| `tp.file.title` | Current file title | `"User Manager Documentation"` |
| `tp.file.creation_date()` | File creation date | `"2026-04-20"` |
| `tp.date.now("YYYY-MM-DD")` | Current date | `"2026-04-20"` |
| `tp.date.now("HH:mm:ss")` | Current time | `"14:30:00"` |
| `tp.user.name` | Configured user name | `"John Doe"` |
| `tp.system.prompt("Q")` | Prompt user for input | Returns user input |
| `tp.file.folder()` | Current folder path | `"documentation/modules"` |

**Full Documentation:** [Templater Plugin Docs](https://silentvoid13.github.io/Templater/)

---

## Appendix C: Metadata Schema Quick Reference

**Required Universal Fields:**
```yaml
title: "Document Title"
id: "document-id"
type: "guide|report|specification|api_reference|..."
version: "1.0.0"
created_date: "YYYY-MM-DD"
updated_date: "YYYY-MM-DD"
status: "draft|review|active|deprecated"
author:
  name: "Author Name"
  email: ""
  github: ""
```

**Common Optional Fields:**
```yaml
category: "architecture|security|frontend|backend|..."
tags: ["tag1", "tag2", "tag3"]
technologies: ["Python", "PyQt6"]
classification: "public|internal|confidential"
audience: ["developer", "architect"]
```

**Full Schema:** See `METADATA_SCHEMA.md`

---

## Appendix D: Tag Taxonomy Quick Reference

**Area Tags:**
- `architecture`, `security`, `governance`, `testing`, `deployment`, `development`, `operations`

**Type Tags:**
- `module`, `guide`, `tutorial`, `reference`, `runbook`, `api`, `report`, `audit`

**Component Tags:**
- `core-system`, `gui`, `agent`, `plugin`, `integration`

**Status Tags:**
- `draft`, `review`, `active`, `deprecated`, `archived`

**Audience Tags:**
- `developer`, `architect`, `operator`, `end_user`, `security_engineer`

**Priority Tags:**
- `critical`, `high`, `medium`, `low`

**Full Taxonomy:** See `TAG_TAXONOMY.md`

---

**Template Library Version:** 2.0.0
**Last Updated:** 2026-04-20
**Total Word Count:** 8,200+ words
**Maintained By:** AGENT-021 (Template Creation Specialist)
**Status:** Documentation-ready asset ✅; not runtime deployment approval

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
