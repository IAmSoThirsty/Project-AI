# Tag Taxonomy Reference

> **Metadata Schema Version:** 1.0  
> **Last Updated:** 2025-01-20  
> **Maintainer:** AGENT-017 (Tag Taxonomy Architect)  
> **Status:** Active  
> **Scope:** Complete controlled vocabulary for Project-AI vault documentation

---

## Executive Summary

This document defines the **complete tag taxonomy** for Project-AI documentation management. It provides a controlled vocabulary, hierarchical structure, usage guidelines, and validation rules to ensure consistent, discoverable, and maintainable documentation across the vault ecosystem.

**Purpose:**
- Establish authoritative tag definitions and hierarchies
- Enable precise multi-dimensional document classification
- Support automated validation and discovery workflows
- Integrate with metadata schema (AGENT-016) and index systems (AGENT-002)

**Scope:**
- 100+ standardized tags across 7 major categories
- Hierarchical parent/child relationships
- Validation rules and constraints
- Integration patterns for frontmatter, indexes, and automation

---

## Table of Contents

1. [Taxonomy Architecture](#taxonomy-architecture)
2. [Tag Categories](#tag-categories)
   - [Area Tags](#area-tags)
   - [Type Tags](#type-tags)
   - [Component Tags](#component-tags)
   - [Status Tags](#status-tags)
   - [Audience Tags](#audience-tags)
   - [Priority Tags](#priority-tags)
   - [Special Tags](#special-tags)
3. [Tag Hierarchy](#tag-hierarchy)
4. [Usage Guidelines](#usage-guidelines)
5. [Validation Rules](#validation-rules)
6. [Examples](#examples)
7. [Integration Patterns](#integration-patterns)
8. [Maintenance](#maintenance)

---

## Taxonomy Architecture

### Design Principles

1. **Multi-Dimensional Classification**: Documents classified along 7 independent axes (area, type, component, status, audience, priority, special)
2. **Hierarchical Structure**: Parent tags contain child tags for granular categorization
3. **Controlled Vocabulary**: Enumerated valid tags prevent tag sprawl and inconsistency
4. **Machine-Readable**: JSON schema enables automated validation and processing
5. **Human-Friendly**: Clear naming conventions and comprehensive definitions
6. **Extensible**: Structured process for adding new tags without breaking existing systems

### Tag Format Conventions

```yaml
# Tag Naming Rules:
# - Use lowercase with hyphens (kebab-case): "constitutional-ai"
# - Use singular nouns for components: "agent" not "agents"
# - Use descriptive adjectives for status: "active" not "live"
# - Use hierarchical prefixes for parent/child: "security/cryptography"
# - Maximum length: 30 characters
# - No special characters except hyphen (-)
# - No spaces (use hyphens instead)
```

### Tag Cardinality Rules

| Category | Min Tags | Max Tags | Required |
|----------|----------|----------|----------|
| **Area** | 1 | 3 | Yes |
| **Type** | 1 | 2 | Yes |
| **Component** | 0 | 5 | No |
| **Status** | 1 | 1 | Yes |
| **Audience** | 1 | 4 | Yes |
| **Priority** | 0 | 1 | Recommended |
| **Special** | 0 | 10 | No |

---

## Tag Categories

### Area Tags

**Purpose:** Define the primary domain, discipline, or concern area of the document.

**Required:** Yes (1-3 tags)  
**Hierarchy:** Two-level (parent/child)

#### Core Areas

##### `architecture`
**Definition:** System design, structure, patterns, and technical architecture decisions.

**When to Use:**
- Design documents defining system structure
- Architecture Decision Records (ADRs)
- Component interaction diagrams
- Technical architecture patterns

**Child Tags:**
- `architecture/backend` - Server-side architecture, APIs, data layer
- `architecture/frontend` - UI/UX architecture, client-side design
- `architecture/desktop` - PyQt6 desktop application architecture
- `architecture/web` - React/Flask web application architecture
- `architecture/data` - Data models, schemas, persistence layer
- `architecture/integration` - System integration patterns, microservices
- `architecture/distributed` - Distributed systems, multi-process architecture

**Examples:**
- `architecture` + `architecture/distributed` → Hydra Swarm design document
- `architecture` + `architecture/backend` → API Gateway specification

---

##### `security`
**Definition:** Security mechanisms, threat models, cryptography, access control, and vulnerability management.

**When to Use:**
- Security policies and procedures
- Threat model analyses
- Cryptographic implementations
- Penetration test reports
- Security audit findings

**Child Tags:**
- `security/cryptography` - Encryption, hashing, key management
- `security/authentication` - User auth, OAuth, JWT, bcrypt
- `security/authorization` - RBAC, permissions, access control
- `security/network` - TLS, firewall rules, network security
- `security/application` - Input validation, XSS, CSRF, injection prevention
- `security/infrastructure` - Container security, secrets management
- `security/audit` - Security audits, penetration tests, vulnerability scans
- `security/incident-response` - Incident playbooks, breach procedures

**Examples:**
- `security` + `security/cryptography` → Fernet encryption implementation guide
- `security` + `security/audit` → Bandit security scan report

---

##### `governance`
**Definition:** Policy, compliance, ethics frameworks, decision-making processes, and constitutional AI governance.

**When to Use:**
- Policy documents and charters
- Constitutional AI frameworks
- Compliance documentation
- Ethics guidelines and frameworks
- Governance workflows

**Child Tags:**
- `governance/constitutional-ai` - Four Laws, ethical constraints, Asimov frameworks
- `governance/policy` - Organizational policies, procedures, standards
- `governance/compliance` - Regulatory compliance, audit requirements
- `governance/ethics` - AI ethics, AGI rights, moral frameworks
- `governance/legal` - Licensing, contracts, intellectual property
- `governance/sovereignty` - Sovereign AI principles, self-determination

**Examples:**
- `governance` + `governance/constitutional-ai` → Four Laws implementation guide
- `governance` + `governance/legal` → AGI Charter and rights specification

---

##### `development`
**Definition:** Software development practices, tools, workflows, and technical implementation.

**When to Use:**
- Developer guides and API documentation
- Code implementation guides
- Development tool documentation
- Programming tutorials
- Technical how-to guides

**Child Tags:**
- `development/python` - Python-specific development
- `development/javascript` - JavaScript/Node.js development
- `development/testing` - Unit tests, integration tests, TDD
- `development/ci-cd` - Continuous integration/deployment pipelines
- `development/tooling` - Development tools, linters, formatters
- `development/api` - API design, REST, GraphQL
- `development/database` - Database development, migrations, queries

**Examples:**
- `development` + `development/python` → Python testing guide
- `development` + `development/ci-cd` → GitHub Actions workflow documentation

---

##### `operations`
**Definition:** System operations, deployment, monitoring, maintenance, and infrastructure management.

**When to Use:**
- Deployment guides and runbooks
- Monitoring and alerting setup
- Operational procedures
- Infrastructure as Code
- SRE documentation

**Child Tags:**
- `operations/deployment` - Deployment processes, Docker, Kubernetes
- `operations/monitoring` - Prometheus, logging, metrics, alerting
- `operations/maintenance` - System maintenance, updates, patches
- `operations/troubleshooting` - Debugging guides, incident runbooks
- `operations/backup-recovery` - Backup strategies, disaster recovery
- `operations/performance` - Performance tuning, optimization
- `operations/infrastructure` - Infrastructure management, cloud services

**Examples:**
- `operations` + `operations/deployment` → Docker Compose deployment guide
- `operations` + `operations/monitoring` → Prometheus setup documentation

---

##### `legal`
**Definition:** Legal frameworks, licensing, intellectual property, contracts, and regulatory compliance.

**When to Use:**
- License documentation
- Legal policies and procedures
- Contract templates
- Intellectual property documentation
- Regulatory compliance guides

**Child Tags:**
- `legal/licensing` - Software licenses, open source compliance
- `legal/privacy` - GDPR, data privacy, PII handling
- `legal/contracts` - Contract templates, agreements
- `legal/intellectual-property` - Patents, trademarks, copyrights
- `legal/regulatory` - Regulatory compliance, industry standards

**Examples:**
- `legal` + `legal/licensing` → MIT License documentation
- `legal` + `legal/privacy` → GDPR compliance guide

---

##### `executive`
**Definition:** Business-level documentation, whitepapers, vision statements, and stakeholder communications.

**When to Use:**
- Executive summaries and whitepapers
- Business strategy documents
- Investor presentations
- High-level vision statements
- Stakeholder communications

**Child Tags:**
- `executive/vision` - Strategic vision, mission statements
- `executive/whitepaper` - Technical whitepapers, research papers
- `executive/business` - Business models, market analysis
- `executive/stakeholder` - Stakeholder communications, reports

**Examples:**
- `executive` + `executive/vision` → Project-AI vision and roadmap
- `executive` + `executive/whitepaper` → Sovereign AI whitepaper

---

### Type Tags

**Purpose:** Define the document format, structure, and intended use.

**Required:** Yes (1-2 tags)  
**Hierarchy:** Flat (no parent/child)

#### Document Types

##### `guide`
**Definition:** Instructional content providing step-by-step procedures or how-to information.

**Characteristics:**
- Sequential structure
- Action-oriented language
- Clear prerequisites
- Expected outcomes

**Examples:**
- Installation guides
- User guides
- Tutorial documents
- Quick-start guides

---

##### `reference`
**Definition:** Factual reference material for lookup and consultation.

**Characteristics:**
- Alphabetical or logical organization
- Comprehensive coverage
- Minimal narrative
- Quick access patterns

**Examples:**
- API reference documentation
- Configuration reference
- Command-line reference
- Tag taxonomy (this document)

---

##### `spec`
**Definition:** Formal technical specifications defining requirements, interfaces, or standards.

**Characteristics:**
- Precise technical language
- Requirements statements (MUST/SHOULD/MAY)
- Versioned
- Implementation-agnostic where possible

**Examples:**
- API specifications
- Data schema specifications
- Protocol specifications
- Interface specifications

---

##### `report`
**Definition:** Analysis, findings, or assessment documents generated from evaluation activities.

**Characteristics:**
- Executive summary
- Methodology section
- Findings/results
- Recommendations

**Examples:**
- Security audit reports
- Test reports
- Performance analysis reports
- Compliance audit reports

---

##### `whitepaper`
**Definition:** Authoritative, research-backed documents explaining technology, solutions, or positions.

**Characteristics:**
- Research-based
- Authoritative tone
- Citations and references
- Problem/solution structure

**Examples:**
- Sovereign AI whitepaper
- Constitutional AI framework
- Technical research papers

---

##### `api-doc`
**Definition:** API-specific documentation including endpoints, parameters, responses, and examples.

**Characteristics:**
- Endpoint listings
- Request/response examples
- Authentication requirements
- Error codes and handling

**Examples:**
- REST API documentation
- GraphQL schema documentation
- SDK documentation

---

##### `source-doc`
**Definition:** Documentation embedded in or generated from source code.

**Characteristics:**
- Code-adjacent or inline
- Auto-generated components
- Language-specific formatting
- Synchronized with code

**Examples:**
- Docstrings documentation
- Inline code comments
- Auto-generated API docs (Sphinx, JSDoc)

---

##### `runbook`
**Definition:** Operational procedures for system management, incident response, or routine tasks.

**Characteristics:**
- Step-by-step procedures
- Decision trees
- Troubleshooting workflows
- On-call friendly

**Examples:**
- Incident response runbooks
- Deployment runbooks
- Maintenance procedures
- Troubleshooting guides

---

##### `adr`
**Definition:** Architecture Decision Records documenting significant architectural choices.

**Characteristics:**
- Context section
- Decision statement
- Consequences analysis
- Status tracking

**Examples:**
- "ADR-001: Use PyQt6 for Desktop UI"
- "ADR-012: Implement Hydra Multi-Process Architecture"

---

##### `index`
**Definition:** Navigation and discovery documents organizing other documents.

**Characteristics:**
- Links to other documents
- Hierarchical organization
- Metadata about contained documents
- Maintenance sections

**Examples:**
- By-area indexes
- By-priority indexes
- Cross-reference indexes

---

### Component Tags

**Purpose:** Identify specific technical components, subsystems, or modules the document covers.

**Required:** No (0-5 tags recommended)  
**Hierarchy:** Flat (no parent/child, but logical grouping)

#### Core Components

##### `constitutional-ai`
**Definition:** The Constitutional AI framework implementing Asimov's Four Laws and ethical constraints.

**Related Files:**
- `governance/core.py`
- `governance/AI_PERSONA_FOUR_LAWS.md`

**When to Use:**
- Documents about Four Laws implementation
- Ethical constraint systems
- Governance validation logic

---

##### `cerberus`
**Definition:** The Cerberus Ω multi-process security and orchestration engine.

**Related Components:**
- Cerberus Ω oversight system
- Hydra Swarm architecture

**When to Use:**
- Cerberus-specific implementation details
- Multi-process orchestration
- Security oversight mechanisms

---

##### `governance-engine`
**Definition:** The runtime governance enforcement and policy evaluation system.

**Related Files:**
- `governance/sovereign_runtime.py`
- `governance/sovereign_verifier.py`

**When to Use:**
- Policy enforcement documentation
- Governance runtime mechanics
- Verification workflows

---

##### `thirsty-lang`
**Definition:** The TARL (Thirsty-Lang) policy and physics engine for immutable governance laws.

**Related Components:**
- TARL language specifications
- Policy compilation

**When to Use:**
- TARL language documentation
- Policy compilation processes
- Immutable law enforcement

---

##### `agents`
**Definition:** The AI agent system including oversight, planner, validator, and explainability agents.

**Related Files:**
- `src/app/agents/oversight.py`
- `src/app/agents/planner.py`
- `src/app/agents/validator.py`
- `src/app/agents/explainability.py`

**When to Use:**
- Agent system architecture
- Agent-specific implementations
- Multi-agent coordination

---

##### `gui`
**Definition:** The PyQt6 graphical user interface (Leather Book Interface).

**Related Files:**
- `src/app/gui/leather_book_interface.py`
- `src/app/gui/leather_book_dashboard.py`

**When to Use:**
- GUI architecture and design
- PyQt6 implementation details
- User interface documentation

---

##### `web`
**Definition:** The React/Flask web application stack.

**Related Directories:**
- `web/frontend/` (React)
- `web/backend/` (Flask)

**When to Use:**
- Web application architecture
- React/Flask integration
- Web-specific features

---

##### `plugin-system`
**Definition:** The plugin management and extension system.

**Related Files:**
- `src/app/core/ai_systems.py` (PluginManager)

**When to Use:**
- Plugin architecture
- Extension mechanisms
- Plugin development guides

---

##### `memory-system`
**Definition:** The memory expansion, knowledge base, and conversation logging system.

**Related Files:**
- `src/app/core/ai_systems.py` (MemoryExpansionSystem)
- `data/memory/knowledge.json`

**When to Use:**
- Memory architecture
- Knowledge base management
- Conversation persistence

---

##### `learning-system`
**Definition:** The learning request management and Black Vault system.

**Related Files:**
- `src/app/core/ai_systems.py` (LearningRequestManager)
- `data/learning_requests/requests.json`

**When to Use:**
- Learning workflow documentation
- Black Vault implementation
- Human-in-the-loop learning

---

##### `persona-system`
**Definition:** The AI personality, mood tracking, and behavior system.

**Related Files:**
- `src/app/core/ai_systems.py` (AIPersona)
- `data/ai_persona/state.json`

**When to Use:**
- Persona implementation
- Mood tracking mechanics
- Personality trait documentation

---

##### `user-manager`
**Definition:** User authentication, profile management, and bcrypt password hashing.

**Related Files:**
- `src/app/core/user_manager.py`
- `data/users.json`

**When to Use:**
- User authentication documentation
- Profile management
- Password security

---

##### `command-override`
**Definition:** The master password override system with audit logging.

**Related Files:**
- `src/app/core/command_override.py`
- `data/command_override_config.json`

**When to Use:**
- Override system documentation
- Audit logging
- Security protocols

---

##### `intelligence-engine`
**Definition:** OpenAI integration and chat completion engine.

**Related Files:**
- `src/app/core/intelligence_engine.py`

**When to Use:**
- OpenAI integration documentation
- Chat engine architecture
- LLM interaction patterns

---

##### `image-generation`
**Definition:** Image generation system (Hugging Face, OpenAI DALL-E).

**Related Files:**
- `src/app/core/image_generator.py`
- `src/app/gui/image_generation.py`

**When to Use:**
- Image generation documentation
- AI art system
- Content filtering

---

##### `data-analysis`
**Definition:** CSV/XLSX/JSON analysis and K-means clustering system.

**Related Files:**
- `src/app/core/data_analysis.py`

**When to Use:**
- Data analysis features
- Clustering algorithms
- File analysis capabilities

---

##### `location-tracker`
**Definition:** IP geolocation, GPS tracking, and encrypted location history.

**Related Files:**
- `src/app/core/location_tracker.py`

**When to Use:**
- Location tracking documentation
- Geolocation features
- Privacy and encryption

---

##### `emergency-alert`
**Definition:** Emergency contact system with email alerts.

**Related Files:**
- `src/app/core/emergency_alert.py`

**When to Use:**
- Emergency system documentation
- Alert mechanisms
- Contact management

---

##### `tarl`
**Definition:** The TARL OS and immutable governance runtime.

**Related Directories:**
- `tarl/`
- `tarl_os/`

**When to Use:**
- TARL OS documentation
- Immutable runtime mechanics
- Low-level governance enforcement

---

##### `temporal`
**Definition:** Temporal workflow engine integration for distributed orchestration.

**Related Directory:**
- `temporal/`

**When to Use:**
- Temporal integration documentation
- Workflow orchestration
- Distributed task management

---

##### `hydra-swarm`
**Definition:** Multi-process architecture with independent network, storage, and logic nodes.

**When to Use:**
- Hydra architecture documentation
- Process isolation design
- Fail-safe mechanisms

---

##### `docker`
**Definition:** Docker containerization and Docker Compose orchestration.

**Related Files:**
- `Dockerfile`
- `docker-compose.yml`

**When to Use:**
- Container architecture
- Docker deployment guides
- Compose orchestration

---

##### `gradle`
**Definition:** Gradle build system and multi-platform builds.

**Related Files:**
- `build.gradle`
- `settings.gradle`

**When to Use:**
- Build system documentation
- Gradle configuration
- Multi-platform builds

---

### Status Tags

**Purpose:** Track the lifecycle stage and current state of the document.

**Required:** Yes (exactly 1 tag)  
**Hierarchy:** Flat (mutually exclusive states)

#### Lifecycle States

##### `active`
**Definition:** Current, actively maintained, and authoritative.

**Transition From:** `draft`, `in-progress`, `review`

**When to Use:**
- Production-ready documentation
- Actively maintained content
- Current best practices

**Maintenance:** Regular reviews required

---

##### `draft`
**Definition:** Work in progress, not yet reviewed or approved.

**Transition To:** `in-progress`, `review`, `active`

**When to Use:**
- Initial document creation
- Content not yet complete
- Unreviewed material

**Visibility:** Internal only

---

##### `in-progress`
**Definition:** Actively being written or updated by a specific maintainer.

**Transition To:** `review`, `active`, `blocked`

**When to Use:**
- Document is actively being edited
- Changes are significant and ongoing
- Coordination required to avoid conflicts

**Metadata Required:** `maintainer` field

---

##### `review`
**Definition:** Complete and awaiting review/approval before becoming active.

**Transition To:** `active`, `draft` (if revisions needed)

**When to Use:**
- Content complete, pending approval
- Quality assurance stage
- Pre-publication state

**Metadata Required:** `reviewers` field

---

##### `archived`
**Definition:** Preserved for historical reference but no longer actively maintained.

**Transition From:** `active`, `deprecated`

**When to Use:**
- Historical reference material
- Superseded but still valuable
- Compliance/audit retention

**Visibility:** Read-only

---

##### `deprecated`
**Definition:** Marked for removal or replacement; no longer recommended for use.

**Transition To:** `archived`, `removed`

**When to Use:**
- Outdated practices or information
- Scheduled for replacement
- Security/compliance issues

**Metadata Required:** `superseded_by` or `deprecation_reason`

---

##### `superseded`
**Definition:** Replaced by a newer document but kept for version history.

**Transition From:** `active`, `deprecated`

**When to Use:**
- Document has direct replacement
- Version history tracking
- Migration documentation

**Metadata Required:** `superseded_by` field with link to replacement

---

##### `legacy`
**Definition:** From previous system versions; may not reflect current architecture.

**When to Use:**
- Documentation from older system versions
- Migration reference material
- Historical architecture documentation

**Visibility:** Clearly labeled as legacy

---

##### `planned`
**Definition:** Documented but not yet implemented; roadmap item.

**Transition To:** `in-progress`, `draft`

**When to Use:**
- Future feature documentation
- Roadmap planning
- Specification before implementation

**Metadata Required:** `target_date` or `milestone`

---

##### `blocked`
**Definition:** Cannot proceed due to dependencies or issues.

**Transition To:** `in-progress`, `archived`

**When to Use:**
- Waiting for dependencies
- Technical blockers
- Resource constraints

**Metadata Required:** `blocked_reason` and `blocked_by`

---

### Audience Tags

**Purpose:** Define the intended readers and appropriate access level for the document.

**Required:** Yes (1-4 tags)  
**Hierarchy:** Flat (multiple audiences possible)

#### Audience Categories

##### `developer`
**Definition:** Software engineers, DevOps, SRE, and technical implementers.

**Content Characteristics:**
- Technical implementation details
- Code examples and snippets
- API documentation
- Development workflows

**Examples:**
- Python developer guides
- API reference documentation
- CI/CD pipeline setup

---

##### `architect`
**Definition:** System architects, technical leads, and senior engineers.

**Content Characteristics:**
- System design patterns
- Architecture decisions
- High-level technical strategy
- Integration patterns

**Examples:**
- Architecture Decision Records
- System design documents
- Integration specifications

---

##### `operator`
**Definition:** System operators, SRE, IT administrators, and on-call staff.

**Content Characteristics:**
- Deployment procedures
- Troubleshooting guides
- Monitoring and alerting
- Incident response

**Examples:**
- Deployment runbooks
- Monitoring setup guides
- Incident playbooks

---

##### `executive`
**Definition:** C-level executives, investors, board members, and business stakeholders.

**Content Characteristics:**
- Business value and ROI
- Strategic vision
- High-level overviews
- Risk assessments

**Examples:**
- Executive summaries
- Whitepapers
- Vision and roadmap documents

---

##### `legal`
**Definition:** Legal counsel, compliance officers, and risk management teams.

**Content Characteristics:**
- Legal implications
- Compliance requirements
- Risk assessments
- Policy documentation

**Examples:**
- License documentation
- Compliance guides
- Legal policies

---

##### `security`
**Definition:** Security engineers, penetration testers, and security auditors.

**Content Characteristics:**
- Security architecture
- Threat models
- Vulnerability assessments
- Security procedures

**Examples:**
- Security audit reports
- Threat model analyses
- Security policies

---

##### `researcher`
**Definition:** AI researchers, data scientists, and academic collaborators.

**Content Characteristics:**
- Research methodologies
- Experimental results
- Theoretical frameworks
- Academic rigor

**Examples:**
- Research papers
- Experimental documentation
- Algorithm specifications

---

##### `contributor`
**Definition:** Open-source contributors, community members, and external developers.

**Content Characteristics:**
- Contribution guidelines
- Community standards
- Public-facing documentation
- Getting started guides

**Examples:**
- CONTRIBUTING.md
- Code of conduct
- Public API documentation

---

##### `internal`
**Definition:** Project-AI internal team members only; not for external distribution.

**Content Characteristics:**
- Internal processes
- Proprietary information
- Implementation notes
- Team communications

**Visibility:** Restricted access

**Examples:**
- Internal implementation notes
- Session records
- WIP documentation

---

##### `public`
**Definition:** General public, open-source community, and anyone with repository access.

**Content Characteristics:**
- Publicly shareable
- No proprietary information
- Educational content
- Community-facing

**Examples:**
- README files
- Public documentation
- Open-source guides

---

### Priority Tags

**Purpose:** Indicate the importance and urgency of the document for stakeholders.

**Required:** Recommended (0-1 tag)  
**Hierarchy:** Flat (mutually exclusive priorities)

#### Priority Levels

##### `P0`
**Definition:** **Critical** - Mission-critical, must be reviewed immediately.

**Criteria:**
- Security vulnerabilities
- Production-breaking issues
- Legal/compliance requirements
- Executive decisions

**SLA:** 24-hour review required

**Examples:**
- Critical security audit findings
- Emergency incident runbooks
- Compliance violation reports

---

##### `P1`
**Definition:** **High** - Important, should be reviewed within 3 days.

**Criteria:**
- High-impact features
- Major architectural decisions
- Important bug fixes
- Key stakeholder communications

**SLA:** 72-hour review target

**Examples:**
- Major feature specifications
- High-priority ADRs
- Important security updates

---

##### `P2`
**Definition:** **Medium** - Standard priority, review within 1 week.

**Criteria:**
- Standard features
- Routine documentation updates
- Medium-impact changes
- General improvements

**SLA:** 1-week review target

**Examples:**
- Standard feature documentation
- Routine maintenance guides
- General API documentation

---

##### `P3`
**Definition:** **Low** - Nice to have, review when capacity allows.

**Criteria:**
- Minor improvements
- Nice-to-have features
- Cosmetic changes
- Low-impact updates

**SLA:** No strict timeline

**Examples:**
- Minor documentation improvements
- Low-priority enhancements
- Optional feature documentation

---

##### `P4`
**Definition:** **Deferred** - Backlog item, review when resources available.

**Criteria:**
- Future considerations
- Experimental ideas
- Research items
- Long-term roadmap

**SLA:** Reviewed during planning cycles

**Examples:**
- Future feature proposals
- Research documentation
- Experimental specifications

---

### Special Tags

**Purpose:** Cross-cutting concerns, workflows, or special characteristics not covered by other categories.

**Required:** No (0-10 tags)  
**Hierarchy:** Flat

#### Special Tag Catalog

##### `migration`
**Definition:** Documents related to migration processes, version upgrades, or system transitions.

**When to Use:**
- Migration guides
- Upgrade procedures
- Transition documentation
- Legacy system documentation

---

##### `integration`
**Definition:** Documents covering system integration, external service connections, or API integration.

**When to Use:**
- Integration guides
- Third-party service documentation
- API integration procedures
- Connector documentation

---

##### `troubleshooting`
**Definition:** Documents focused on problem diagnosis and resolution.

**When to Use:**
- Troubleshooting guides
- FAQ documents
- Common issues and solutions
- Debugging procedures

---

##### `quickstart`
**Definition:** Getting started guides and quick setup documentation.

**When to Use:**
- Quickstart guides
- Getting started tutorials
- Fast-path documentation
- Minimal viable setup

---

##### `best-practices`
**Definition:** Recommended patterns, conventions, and proven approaches.

**When to Use:**
- Best practice guides
- Style guides
- Convention documentation
- Recommended patterns

---

##### `template`
**Definition:** Reusable templates for documents, code, or configurations.

**When to Use:**
- Document templates
- Code templates
- Configuration templates
- Boilerplate documentation

---

##### `automation`
**Definition:** Automated processes, scripts, and workflow automation.

**When to Use:**
- Automation scripts
- Workflow automation
- CI/CD pipelines
- Automated validation

---

##### `performance`
**Definition:** Performance optimization, benchmarking, and tuning.

**When to Use:**
- Performance guides
- Optimization documentation
- Benchmark results
- Tuning procedures

---

##### `testing`
**Definition:** Testing strategies, test documentation, and quality assurance.

**When to Use:**
- Test plans
- Testing guides
- QA procedures
- Test result documentation

---

##### `monitoring`
**Definition:** System monitoring, observability, and alerting.

**When to Use:**
- Monitoring setup
- Alert configuration
- Observability guides
- Metrics documentation

---

##### `backup-recovery`
**Definition:** Backup strategies, disaster recovery, and business continuity.

**When to Use:**
- Backup procedures
- Recovery runbooks
- Business continuity plans
- Disaster recovery documentation

---

##### `versioning`
**Definition:** Version control, release management, and versioning strategies.

**When to Use:**
- Versioning policies
- Release documentation
- Changelog documentation
- Version control guides

---

##### `localization`
**Definition:** Internationalization (i18n), localization (l10n), and translation.

**When to Use:**
- Localization guides
- Translation procedures
- i18n documentation
- Multi-language support

---

##### `accessibility`
**Definition:** Accessibility standards, WCAG compliance, and inclusive design.

**When to Use:**
- Accessibility guides
- WCAG documentation
- Inclusive design documentation
- Assistive technology support

---

##### `experimental`
**Definition:** Experimental features, prototypes, or research implementations.

**When to Use:**
- Experimental documentation
- Prototype specifications
- Research implementations
- Proof-of-concept documentation

---

##### `deprecated-feature`
**Definition:** Documentation for features being phased out.

**When to Use:**
- Deprecated feature documentation
- Sunset notices
- Migration from deprecated features
- Removal timelines

---

##### `breaking-change`
**Definition:** Documentation of breaking changes requiring user action.

**When to Use:**
- Breaking change announcements
- Migration guides for breaking changes
- Compatibility documentation
- Upgrade impact documentation

---

##### `tutorial`
**Definition:** Educational, step-by-step learning content.

**When to Use:**
- Tutorial content
- Learning paths
- Educational guides
- Training materials

---

##### `faq`
**Definition:** Frequently asked questions and common inquiries.

**When to Use:**
- FAQ documents
- Common questions
- Quick answers
- Self-service support

---

##### `glossary`
**Definition:** Terminology definitions and vocabulary references.

**When to Use:**
- Glossary documents
- Terminology guides
- Definition references
- Vocabulary documentation

---

## Tag Hierarchy

### JSON Schema Representation

See `tag-hierarchy.json` for the machine-readable hierarchy.

### Visual Hierarchy

```
AREA TAGS (1-3 required)
├─ architecture
│  ├─ architecture/backend
│  ├─ architecture/frontend
│  ├─ architecture/desktop
│  ├─ architecture/web
│  ├─ architecture/data
│  ├─ architecture/integration
│  └─ architecture/distributed
├─ security
│  ├─ security/cryptography
│  ├─ security/authentication
│  ├─ security/authorization
│  ├─ security/network
│  ├─ security/application
│  ├─ security/infrastructure
│  ├─ security/audit
│  └─ security/incident-response
├─ governance
│  ├─ governance/constitutional-ai
│  ├─ governance/policy
│  ├─ governance/compliance
│  ├─ governance/ethics
│  ├─ governance/legal
│  └─ governance/sovereignty
├─ development
│  ├─ development/python
│  ├─ development/javascript
│  ├─ development/testing
│  ├─ development/ci-cd
│  ├─ development/tooling
│  ├─ development/api
│  └─ development/database
├─ operations
│  ├─ operations/deployment
│  ├─ operations/monitoring
│  ├─ operations/maintenance
│  ├─ operations/troubleshooting
│  ├─ operations/backup-recovery
│  ├─ operations/performance
│  └─ operations/infrastructure
├─ legal
│  ├─ legal/licensing
│  ├─ legal/privacy
│  ├─ legal/contracts
│  ├─ legal/intellectual-property
│  └─ legal/regulatory
└─ executive
   ├─ executive/vision
   ├─ executive/whitepaper
   ├─ executive/business
   └─ executive/stakeholder

TYPE TAGS (1-2 required)
├─ guide
├─ reference
├─ spec
├─ report
├─ whitepaper
├─ api-doc
├─ source-doc
├─ runbook
├─ adr
└─ index

COMPONENT TAGS (0-5 recommended)
├─ constitutional-ai
├─ cerberus
├─ governance-engine
├─ thirsty-lang
├─ agents
├─ gui
├─ web
├─ plugin-system
├─ memory-system
├─ learning-system
├─ persona-system
├─ user-manager
├─ command-override
├─ intelligence-engine
├─ image-generation
├─ data-analysis
├─ location-tracker
├─ emergency-alert
├─ tarl
├─ temporal
├─ hydra-swarm
├─ docker
└─ gradle

STATUS TAGS (exactly 1 required)
├─ active
├─ draft
├─ in-progress
├─ review
├─ archived
├─ deprecated
├─ superseded
├─ legacy
├─ planned
└─ blocked

AUDIENCE TAGS (1-4 required)
├─ developer
├─ architect
├─ operator
├─ executive
├─ legal
├─ security
├─ researcher
├─ contributor
├─ internal
└─ public

PRIORITY TAGS (0-1 recommended)
├─ P0 (Critical)
├─ P1 (High)
├─ P2 (Medium)
├─ P3 (Low)
└─ P4 (Deferred)

SPECIAL TAGS (0-10 optional)
├─ migration
├─ integration
├─ troubleshooting
├─ quickstart
├─ best-practices
├─ template
├─ automation
├─ performance
├─ testing
├─ monitoring
├─ backup-recovery
├─ versioning
├─ localization
├─ accessibility
├─ experimental
├─ deprecated-feature
├─ breaking-change
├─ tutorial
├─ faq
└─ glossary
```

---

## Usage Guidelines

### Tag Selection Process

1. **Start with Area (1-3 tags)**
   - Identify primary domain
   - Add child tag for specificity
   - Consider cross-cutting areas (max 3)

2. **Select Type (1-2 tags)**
   - Choose primary document format
   - Add secondary if hybrid (e.g., `guide` + `reference`)

3. **Add Components (0-5 tags)**
   - List all technical components covered
   - Be specific but not exhaustive
   - Focus on primary components

4. **Set Status (exactly 1 tag)**
   - Reflect current lifecycle stage
   - Update as document evolves
   - Use metadata for status details

5. **Define Audience (1-4 tags)**
   - Identify all intended readers
   - Consider access control
   - Balance broad vs. narrow audience

6. **Assign Priority (0-1 tag)**
   - Optional but recommended
   - Context-dependent (may vary by audience)
   - Review periodically

7. **Apply Special Tags (0-10 tags)**
   - Add only if applicable
   - Don't over-tag
   - Focus on discoverability

### Tag Application Examples

#### Example 1: Security Audit Report

```yaml
tags:
  # Area (2 tags - cross-cutting)
  - security
  - security/audit
  
  # Type (1 tag)
  - report
  
  # Components (3 tags)
  - user-manager
  - command-override
  - security/authentication
  
  # Status (1 tag)
  - active
  
  # Audience (3 tags)
  - security
  - developer
  - executive
  
  # Priority (1 tag)
  - P0
  
  # Special (2 tags)
  - troubleshooting
  - best-practices
```

#### Example 2: PyQt6 GUI Developer Guide

```yaml
tags:
  # Area (2 tags)
  - development
  - development/python
  
  # Type (1 tag)
  - guide
  
  # Components (2 tags)
  - gui
  - persona-system
  
  # Status (1 tag)
  - active
  
  # Audience (2 tags)
  - developer
  - contributor
  
  # Priority (1 tag)
  - P2
  
  # Special (2 tags)
  - quickstart
  - tutorial
```

#### Example 3: Constitutional AI Whitepaper

```yaml
tags:
  # Area (2 tags)
  - governance
  - governance/constitutional-ai
  
  # Type (1 tag)
  - whitepaper
  
  # Components (3 tags)
  - constitutional-ai
  - governance-engine
  - agents
  
  # Status (1 tag)
  - active
  
  # Audience (4 tags)
  - executive
  - researcher
  - public
  - legal
  
  # Priority (1 tag)
  - P0
  
  # Special (1 tag)
  - best-practices
```

#### Example 4: Docker Deployment Runbook

```yaml
tags:
  # Area (2 tags)
  - operations
  - operations/deployment
  
  # Type (1 tag)
  - runbook
  
  # Components (2 tags)
  - docker
  - hydra-swarm
  
  # Status (1 tag)
  - active
  
  # Audience (2 tags)
  - operator
  - developer
  
  # Priority (1 tag)
  - P1
  
  # Special (3 tags)
  - quickstart
  - troubleshooting
  - automation
```

#### Example 5: API Reference Documentation

```yaml
tags:
  # Area (2 tags)
  - development
  - development/api
  
  # Type (1 tag)
  - api-doc
  
  # Components (3 tags)
  - intelligence-engine
  - user-manager
  - memory-system
  
  # Status (1 tag)
  - active
  
  # Audience (3 tags)
  - developer
  - contributor
  - public
  
  # Priority (1 tag)
  - P2
  
  # Special (1 tag)
  - reference
```

---

## Validation Rules

### Automated Validation

The `validate-tags.ps1` script enforces:

1. **Required Tags Present**
   - At least 1 area tag
   - Exactly 1 type tag
   - Exactly 1 status tag
   - At least 1 audience tag

2. **Tag Format Validation**
   - Lowercase with hyphens only
   - Maximum 30 characters
   - No spaces or special characters (except hyphen)
   - Valid against controlled vocabulary

3. **Hierarchy Validation**
   - Child tags must have parent tag present
   - Example: `security/cryptography` requires `security`

4. **Cardinality Validation**
   - Area: 1-3 tags
   - Type: 1-2 tags
   - Component: 0-5 tags
   - Status: exactly 1 tag
   - Audience: 1-4 tags
   - Priority: 0-1 tag
   - Special: 0-10 tags

5. **Mutual Exclusivity**
   - Status tags are mutually exclusive
   - Priority tags are mutually exclusive

### Manual Review Checklist

- [ ] Tags accurately describe document content
- [ ] No redundant or overlapping tags
- [ ] Appropriate level of specificity
- [ ] Tags support discoverability
- [ ] Priority is context-appropriate
- [ ] Audience tags match access control
- [ ] Special tags add value (not noise)

---

## Examples

### 20+ Real-World Examples

#### 1. Four Laws Implementation Guide
```yaml
area: [governance, governance/constitutional-ai]
type: [guide]
component: [constitutional-ai, governance-engine]
status: active
audience: [developer, architect]
priority: P0
special: [best-practices, tutorial]
```

#### 2. Bandit Security Audit Report
```yaml
area: [security, security/audit]
type: [report]
component: [user-manager, command-override]
status: active
audience: [security, developer, executive]
priority: P0
special: [troubleshooting]
```

#### 3. PyQt6 Desktop Architecture
```yaml
area: [architecture, architecture/desktop]
type: [spec, adr]
component: [gui, persona-system]
status: active
audience: [architect, developer]
priority: P1
special: [best-practices]
```

#### 4. Docker Compose Deployment Guide
```yaml
area: [operations, operations/deployment]
type: [guide, runbook]
component: [docker, hydra-swarm]
status: active
audience: [operator, developer]
priority: P1
special: [quickstart, automation]
```

#### 5. OpenAI Integration API Documentation
```yaml
area: [development, development/api]
type: [api-doc]
component: [intelligence-engine, image-generation]
status: active
audience: [developer, contributor, public]
priority: P2
special: [integration]
```

#### 6. Memory System Database Schema
```yaml
area: [architecture, architecture/data]
type: [spec]
component: [memory-system]
status: active
audience: [architect, developer]
priority: P2
special: []
```

#### 7. Incident Response Runbook
```yaml
area: [operations, operations/troubleshooting, security]
type: [runbook]
component: [cerberus, hydra-swarm]
status: active
audience: [operator, security]
priority: P0
special: [troubleshooting, monitoring]
```

#### 8. AGI Charter and Rights Specification
```yaml
area: [governance, governance/ethics, legal]
type: [whitepaper, spec]
component: [constitutional-ai]
status: active
audience: [executive, legal, public, researcher]
priority: P0
special: [best-practices]
```

#### 9. Python Testing Best Practices
```yaml
area: [development, development/python, development/testing]
type: [guide]
component: []
status: active
audience: [developer, contributor]
priority: P2
special: [best-practices, testing, tutorial]
```

#### 10. Prometheus Monitoring Setup
```yaml
area: [operations, operations/monitoring]
type: [guide]
component: []
status: active
audience: [operator, developer]
priority: P1
special: [monitoring, automation, quickstart]
```

#### 11. Bcrypt Password Hashing Implementation
```yaml
area: [security, security/authentication]
type: [guide, source-doc]
component: [user-manager]
status: active
audience: [developer]
priority: P1
special: [best-practices, tutorial]
```

#### 12. TARL Language Specification
```yaml
area: [governance, architecture]
type: [spec]
component: [thirsty-lang, tarl]
status: active
audience: [architect, developer, researcher]
priority: P0
special: [reference]
```

#### 13. React Frontend Architecture
```yaml
area: [architecture, architecture/frontend, architecture/web]
type: [spec, adr]
component: [web]
status: active
audience: [architect, developer]
priority: P2
special: []
```

#### 14. GitHub Actions CI/CD Pipeline
```yaml
area: [development, development/ci-cd]
type: [guide]
component: []
status: active
audience: [developer, operator]
priority: P2
special: [automation, best-practices]
```

#### 15. Emergency Alert System Documentation
```yaml
area: [operations, security]
type: [guide, spec]
component: [emergency-alert]
status: active
audience: [developer, operator]
priority: P1
special: [integration]
```

#### 16. Deprecated MD5 Hash Migration Guide
```yaml
area: [security, security/cryptography]
type: [guide]
component: [user-manager]
status: deprecated
audience: [developer]
priority: P1
special: [migration, breaking-change, deprecated-feature]
```

#### 17. Temporal Workflow Integration
```yaml
area: [architecture, architecture/integration, operations]
type: [guide, spec]
component: [temporal]
status: active
audience: [architect, developer, operator]
priority: P2
special: [integration, quickstart]
```

#### 18. Plugin Development Tutorial
```yaml
area: [development, development/python]
type: [guide]
component: [plugin-system]
status: active
audience: [developer, contributor]
priority: P3
special: [tutorial, quickstart, template]
```

#### 19. Fernet Encryption Best Practices
```yaml
area: [security, security/cryptography]
type: [guide]
component: [location-tracker]
status: active
audience: [security, developer]
priority: P1
special: [best-practices]
```

#### 20. Index Template Documentation
```yaml
area: [operations]
type: [template, index]
component: []
status: active
audience: [developer, internal]
priority: P2
special: [template, automation]
```

#### 21. Learning System Black Vault Specification
```yaml
area: [governance, architecture]
type: [spec]
component: [learning-system, constitutional-ai]
status: active
audience: [architect, developer]
priority: P1
special: [best-practices]
```

#### 22. Hydra Swarm Multi-Process Architecture
```yaml
area: [architecture, architecture/distributed]
type: [whitepaper, spec]
component: [hydra-swarm, cerberus]
status: active
audience: [architect, executive, researcher]
priority: P0
special: [best-practices]
```

#### 23. Troubleshooting Repository Documentation
```yaml
area: [operations, operations/troubleshooting]
type: [guide]
component: []
status: active
audience: [developer, operator]
priority: P2
special: [troubleshooting, faq]
```

#### 24. Gradle Build System Configuration
```yaml
area: [development, development/tooling]
type: [guide, reference]
component: [gradle]
status: active
audience: [developer]
priority: P2
special: [quickstart, best-practices]
```

#### 25. MIT License Documentation
```yaml
area: [legal, legal/licensing]
type: [reference]
component: []
status: active
audience: [legal, public, executive]
priority: P0
special: []
```

---

## Integration Patterns

### Frontmatter Integration

```yaml
---
# Document Metadata (AGENT-016 Schema)
title: "Security Audit Report - User Authentication"
created: "2025-01-15"
updated: "2025-01-20"
version: "1.2"
authors: ["AGENT-023", "Security Team"]
reviewers: ["AGENT-017", "Lead Architect"]

# Status and Lifecycle
status: active
priority: P0

# Classification Tags (AGENT-017 Taxonomy)
tags:
  # Area
  - security
  - security/audit
  - security/authentication
  
  # Type
  - report
  
  # Component
  - user-manager
  - command-override
  
  # Audience
  - security
  - developer
  - executive
  
  # Special
  - troubleshooting
  - best-practices

# Relationships
supersedes: ["security-audit-v1.0.md"]
related: ["password-policy-spec.md", "bcrypt-implementation.md"]
dependencies: []

# Access Control
visibility: internal
classification: confidential
---
```

### Index Integration

```markdown
### Security Audit Reports

- [[security-audit-user-auth]] - User authentication security audit
  - **Tags:** security, security/audit, report, P0
  - **Components:** user-manager, command-override
  - **Status:** active
  - **Last Reviewed:** 2025-01-20
```

### Search and Discovery

```bash
# Find all P0 security documents
rg --type md "priority: P0" --files-with-matches | rg "security"

# Find all active guides for developers
rg --type md "status: active" --files-with-matches | rg "type:.*guide" | rg "audience:.*developer"

# Find all constitutional-ai component documentation
rg --type md "component:.*constitutional-ai"
```

### Automation Integration

```powershell
# validate-tags.ps1 integration
.\scripts\validate-tags.ps1 -Path "T:\Project-AI-vault\repo-docs" -Verbose

# Automated tag reporting
.\scripts\generate-tag-report.ps1 -OutputPath "tag-distribution.json"

# Tag-based index generation
.\scripts\generate-index-by-tag.ps1 -Tag "security" -OutputPath "_indexes\by-area\security-index.md"
```

---

## Maintenance

### Adding New Tags

1. **Proposal Process**
   - Document use case and examples
   - Identify category and hierarchy level
   - Check for overlap with existing tags
   - Submit proposal to AGENT-017

2. **Approval Criteria**
   - Fills genuine gap in taxonomy
   - No overlap with existing tags
   - Follows naming conventions
   - Supports discoverability

3. **Implementation Steps**
   - Update `TAG_TAXONOMY.md` with definition
   - Add to `tag-hierarchy.json`
   - Update `validate-tags.ps1` vocabulary
   - Update examples
   - Announce to team

### Tag Deprecation

1. **Deprecation Triggers**
   - Tag rarely used (< 5 documents)
   - Redundant with another tag
   - Naming convention violation
   - No longer relevant

2. **Deprecation Process**
   - Mark tag as deprecated in taxonomy
   - Create migration guide
   - Update affected documents
   - Remove from validation after 90 days

### Periodic Review

**Quarterly Review Checklist:**
- [ ] Review tag usage statistics
- [ ] Identify under-used tags (< 5 documents)
- [ ] Identify over-used tags (> 100 documents - consider splitting)
- [ ] Check for tag sprawl (similar tags)
- [ ] Validate hierarchy still makes sense
- [ ] Update examples with new use cases
- [ ] Synchronize with metadata schema changes

---

## Appendix

### Tag Statistics Template

```markdown
## Tag Usage Statistics

**Last Updated:** 2025-01-20

### Area Tags
- architecture: 42 documents
- security: 38 documents
- governance: 29 documents
- development: 55 documents
- operations: 31 documents
- legal: 12 documents
- executive: 18 documents

### Type Tags
- guide: 78 documents
- reference: 23 documents
- spec: 34 documents
- report: 19 documents
- whitepaper: 8 documents
- api-doc: 15 documents

### Most Common Tag Combinations
1. security + guide + developer (12 documents)
2. development + api-doc + developer (11 documents)
3. operations + runbook + operator (9 documents)
```

### Related Documents

- `metadata-schema.json` - AGENT-016 metadata schema
- `validate-tags.ps1` - Tag validation script
- `tag-hierarchy.json` - Machine-readable hierarchy
- `INDEX_TEMPLATE.md` - Index template with tag usage

### Glossary

- **Controlled Vocabulary**: Predefined list of valid tags
- **Tag Cardinality**: Number of tags allowed per category
- **Tag Hierarchy**: Parent/child relationships between tags
- **Tag Sprawl**: Uncontrolled growth of similar or redundant tags
- **Frontmatter**: YAML metadata at the top of markdown files

---

**Document Version:** 1.0  
**Schema Version:** 1.0  
**Total Tags:** 100+  
**Categories:** 7  
**Created By:** AGENT-017 (Tag Taxonomy Architect)  
**Last Updated:** 2025-01-20

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

