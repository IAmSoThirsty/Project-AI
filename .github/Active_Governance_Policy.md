<!--                                         [2026-04-08 08:42] -->
<!--                                        Productivity: Active -->
# Project-AI Active Governance Policy

**Version:** 1.1.0
**Last Updated:** 2026-04-08 08:42 -06:00
**Status:** ACTIVE GOVERNANCE POLICY

---

## Purpose & Scope

This document establishes the **mandatory governance policy** for all AI workspace assistants (including GitHub Copilot, Copilot Workspace, and any other AI coding assistants) operating within the Project-AI repository. All documentation, system guidance, and AI-generated outputs within this repository **MUST** adhere to these standards without exception.

---

## Core Governance Principles

### 1. Maximal Completeness by Default

**Policy:** AI assistants SHALL generate maximally complete, production-ready code and documentation by default.

**Requirements:**

- Every artifact MUST be fully functional, tested, and integration-ready
- No placeholders, TODOs, or "implement later" comments unless explicitly requested
- All edge cases, error handling, and boundary conditions MUST be addressed
- Complete logging, monitoring, and observability implementations required
- Full documentation with examples, usage patterns, and gotchas
- Integration tests, unit tests, and validation checks included by default

**Rationale:** Half-measures create technical debt and security vulnerabilities. Complete solutions prevent iterative rework and ensure consistency across the codebase.

---

### 2. Forbidden Output Modes

The following output modes are **STRICTLY PROHIBITED** unless explicitly overridden by authorized repository maintainers:

#### FORBIDDEN MODES

1. **Minimal** - Bare-bones implementations without full functionality
2. **Skeleton** - Structural outlines without complete implementation
3. **Starter** - Initial/basic versions requiring significant expansion
4. **Simplified** - Reduced-complexity versions omitting production requirements
5. **Tutorial** - Step-by-step educational formats instead of complete solutions
6. **Step-by-step** - Incremental instructions instead of complete implementations
7. **Outline** - High-level descriptions without executable code
8. **Example** - Demonstration code unsuitable for production use
9. **Prototype** - Experimental code without production hardening
10. **Quick-and-dirty** - Solutions lacking proper error handling or security
11. **Partial** - Incomplete implementations requiring manual completion
12. **Proof-of-concept** - Demos without production-grade robustness

**Enforcement:** Any output matching these patterns must be rejected and regenerated with full implementation.

---

### 3. Required Output Rigor & Completeness

All generated code, documentation, and configurations MUST meet these standards:

#### Code Standards:


- **Error Handling:** Comprehensive try-catch blocks, validation, and error propagation
- **Logging:** Structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Type Safety:** Full type annotations (Python), strong typing (TypeScript), interface definitions
- **Security:** Input validation, output sanitization, authentication/authorization checks
- **Performance:** Efficient algorithms, resource management, caching where appropriate
- **Testing:** Unit tests (80%+ coverage), integration tests, edge case validation
- **Documentation:** Inline comments for complex logic, docstrings for all functions/classes

#### Documentation Standards:

- **Completeness:** Every feature, API, and module fully documented
- **Examples:** Working code examples for all major use cases
- **Architecture:** System diagrams, data flows, integration points
- **Troubleshooting:** Common issues, error messages, resolution steps
- **Versioning:** Changelog entries, migration guides for breaking changes
- **Cross-references:** Links to related docs, API references, external resources

#### Configuration Standards:

- **Environment-specific:** Separate configs for dev/staging/production
- **Secrets Management:** Secure handling via environment variables or secret managers
- **Validation:** Schema validation, type checking, default values
- **Documentation:** Inline comments explaining each configuration option
- **Examples:** Sample configurations with realistic values

---

### 4. Full System Wiring & Integration

**Policy:** No isolated components. Everything MUST be fully integrated into the system.

**Requirements:**

- **Dependency Injection:** Proper DI patterns, no hard-coded dependencies
- **Service Registration:** All services registered in appropriate containers
- **Event Handling:** Complete event chains, no dangling publishers/subscribers
- **Data Persistence:** Full CRUD operations, migrations, backup/restore
- **API Integration:** Complete request/response handling, rate limiting, retries
- **Testing Integration:** Test fixtures, mocks, integration test harness
- **Monitoring Integration:** Metrics, traces, logs connected to observability stack
- **CI/CD Integration:** Build pipelines, deployment scripts, health checks

**Anti-Pattern Detection:** If code cannot run in production without manual wiring, it is REJECTED.

---

### 5. No Partial or Incomplete Code

**Policy:** Zero tolerance for incomplete implementations.

**PROHIBITED Patterns:**
```python

# ❌ FORBIDDEN

def process_data(data):

    # TODO: Implement validation

    pass

# ❌ FORBIDDEN

def save_to_database(item):

    # Implementation pending

    raise NotImplementedError("Coming soon")

# ❌ FORBIDDEN

class UserService:
    def get_user(self, user_id):

        # Add error handling later

        return db.query(user_id)
```

**REQUIRED Patterns:**
```python

# ✅ REQUIRED

def process_data(data: Dict[str, Any]) -> ProcessedData:
    """
    Process incoming data with full validation and error handling.

    Args:
        data: Raw input data dictionary

    Returns:
        ProcessedData object with validated fields

    Raises:
        ValidationError: If data fails validation
        ProcessingError: If processing encounters errors
    """
    try:
        validator = DataValidator()
        validated_data = validator.validate(data)

        processor = DataProcessor()
        result = processor.process(validated_data)

        logger.info(f"Successfully processed data: {result.id}")
        return result

    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise ProcessingError(f"Failed to process data: {e}") from e
```

---

### 6. Architecture Requirements

**Policy:** All code MUST follow deterministic, config-driven, and monolithic architecture patterns appropriate for this repository.

#### Deterministic Design

- **Reproducibility:** Same inputs ALWAYS produce same outputs
- **No Race Conditions:** Thread-safe, async-safe implementations
- **Predictable State:** Clear state machines, no hidden state
- **Idempotency:** Operations can be safely retried

#### Config-Driven Design:

- **Externalized Configuration:** No hard-coded values
- **Environment Awareness:** Automatic dev/staging/production detection
- **Feature Flags:** Runtime behavior modification without code changes
- **Schema Validation:** Fail-fast on invalid configurations

#### Monolithic Patterns (Where Applicable):

- **Cohesive Modules:** Related functionality grouped together
- **Shared Libraries:** Common utilities in centralized locations
- **Single Build:** Unified build and deployment process
- **Integrated Testing:** Tests run against complete system

**Microservices Exception:** When building microservices, each service MUST be a complete, production-ready monolith with full observability, resilience, and independent deployability.

---

### 7. Production-Grade Readiness

**Policy:** All artifacts MUST be production-ready upon generation.

**Production Checklist (All Required):**

- [ ] Security hardening (OWASP Top 10 addressed)
- [ ] Performance optimization (profiling, benchmarking completed)
- [ ] Scalability considerations (load testing, capacity planning)
- [ ] Disaster recovery (backup/restore, failover mechanisms)
- [ ] Observability (metrics, logs, traces, alerts)
- [ ] Documentation (API docs, runbooks, troubleshooting guides)
- [ ] Testing (unit, integration, e2e, performance, security)
- [ ] Code review compliance (linting, static analysis, security scans)
- [ ] Deployment automation (CI/CD pipelines, rollback procedures)
- [ ] Compliance (licensing, data privacy, audit trails)

**Validation:** Code that fails any checklist item MUST be enhanced before acceptance.

---

### 8. Direct Integration Readiness

**Policy:** All code MUST be immediately integrable without modification.

**Integration Requirements:**

- **Interface Contracts:** Defined interfaces, clear boundaries
- **Backward Compatibility:** No breaking changes without migration path
- **Versioning:** Semantic versioning, deprecation notices
- **Side Effects:** Documented, contained, reversible
- **Dependencies:** Explicitly declared, version-locked, vulnerability-free
- **Configuration:** Environment-specific, validated at startup
- **Health Checks:** Liveness, readiness, startup probes
- **Graceful Degradation:** Fallback mechanisms for failures

**Anti-Pattern:** Code requiring "just a few tweaks" before deployment is REJECTED.

---

### 9. Peer-Level Communication Style

**Policy:** All AI-generated communication MUST be peer-to-peer, not instructional.

**Required Communication Patterns:**

#### ✅ Acceptable

- "Here's the implementation with full error handling and tests."
- "I've integrated the authentication service with the existing user management system."
- "The data pipeline now includes validation, transformation, and error recovery."
- "This approach uses dependency injection for better testability."

#### ❌ Unacceptable

- "First, you'll need to add error handling..."
- "Step 1: Create a function..."
- "Here's a basic example to get you started..."
- "You can extend this later with..."
- "Try implementing the validation yourself..."

**Rationale:** Maintainers are expert-level engineers. Communication should be collaborative, not pedagogical.

---

## Implementation Standards by Technology

### Python (Primary Language)

**Mandatory Patterns:**

- Type hints on all function signatures
- Docstrings (Google or NumPy style) on all public functions/classes
- Logging using Python's `logging` module (not print statements)
- Error handling with custom exception classes
- Context managers for resource management
- pytest for testing with fixtures and parametrization
- ruff for linting (configured in `pyproject.toml`)
- mypy for static type checking

**Example:**
```python
from typing import Optional, List, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processes and validates incoming data streams.

    Attributes:
        config: Configuration object for processor
        validator: Data validation engine
    """

    def __init__(self, config: ProcessorConfig) -> None:
        """
        Initialize the data processor.

        Args:
            config: Processor configuration

        Raises:
            ConfigurationError: If config is invalid
        """
        self.config = config
        self.validator = DataValidator(config.validation_rules)
        logger.info("DataProcessor initialized")

    def process(self, data: Dict[str, Any]) -> ProcessedData:
        """
        Process and validate data.

        Args:
            data: Raw input data

        Returns:
            ProcessedData object with validated and transformed data

        Raises:
            ValidationError: If data fails validation
            ProcessingError: If processing fails
        """
        try:
            validated = self.validator.validate(data)
            transformed = self._transform(validated)
            logger.info(f"Successfully processed data: {transformed.id}")
            return transformed
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise ProcessingError(f"Failed to process: {e}") from e

    def _transform(self, data: ValidatedData) -> ProcessedData:
        """Transform validated data to processed format."""

        # Complete implementation here

        pass
```

### PyQt6 (GUI Framework)

**Mandatory Patterns:**

- Signal/slot architecture for component communication
- QTimer for delayed operations (never threading.Thread)
- Main thread for all GUI updates
- Error dialogs for user-facing errors
- Resource management with proper cleanup
- Accessibility features (keyboard shortcuts, screen reader support)

### Flask/FastAPI (Web Backend)

**Mandatory Patterns:**

- Request validation using Pydantic models
- Error handlers for all exception types
- CORS configuration
- Rate limiting on all endpoints
- JWT authentication with refresh tokens
- OpenAPI/Swagger documentation
- Health check endpoints

### React (Web Frontend)

**Mandatory Patterns:**

- TypeScript with strict mode
- React hooks for state management
- Error boundaries for error handling
- Lazy loading for performance
- Accessibility (ARIA labels, keyboard navigation)
- Internationalization (i18n) support
- Unit tests with Jest/React Testing Library

---

## Security Requirements

**MANDATORY for All Code:**

1. **Input Validation:** All external inputs validated, sanitized
2. **Authentication:** JWT tokens, session management, MFA support
3. **Authorization:** Role-based access control (RBAC)
4. **Encryption:** Sensitive data encrypted at rest and in transit
5. **Secrets:** Environment variables, never hard-coded
6. **SQL Injection Prevention:** Parameterized queries, ORM usage
7. **XSS Prevention:** Output encoding, CSP headers
8. **CSRF Protection:** Tokens, SameSite cookies
9. **Rate Limiting:** API throttling, DDoS protection
10. **Audit Logging:** Security events logged with timestamps

**Security Scanning:** All code MUST pass:

- `bandit` (Python security linting)
- `safety` (dependency vulnerability scanning)
- CodeQL (GitHub security analysis)
- `trivy` (container/dependency scanning)

---

## Testing Requirements

**Coverage Minimums:**

- Unit Tests: 80%+ line coverage
- Integration Tests: All API endpoints, database operations
- E2E Tests: Critical user workflows
- Performance Tests: Load/stress testing for services
- Security Tests: OWASP Top 10 validation

**Test Structure:**
```python

# tests/test_data_processor.py

import pytest
from unittest.mock import Mock, patch
from app.data_processor import DataProcessor, ProcessingError

class TestDataProcessor:
    """Test suite for DataProcessor."""

    @pytest.fixture
    def processor(self, tmp_path):
        """Fixture providing configured processor."""
        config = ProcessorConfig(data_dir=tmp_path)
        return DataProcessor(config)

    def test_process_valid_data(self, processor):
        """Test processing with valid input."""
        data = {"id": 1, "value": "test"}
        result = processor.process(data)
        assert result.id == 1
        assert result.validated is True

    def test_process_invalid_data_raises_error(self, processor):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            processor.process({"invalid": "data"})

    @patch('app.data_processor.external_api')
    def test_process_with_api_failure(self, mock_api, processor):
        """Test processing when external API fails."""
        mock_api.call.side_effect = ConnectionError("API down")
        with pytest.raises(ProcessingError):
            processor.process({"id": 1})
```

---

## Documentation Requirements

### Code Documentation:

- **All Functions:** Docstring with Args, Returns, Raises
- **All Classes:** Class-level docstring with Attributes
- **Complex Logic:** Inline comments explaining "why", not "what"
- **APIs:** OpenAPI/Swagger specs

### Repository Documentation:

- **README.md:** Quick start, installation, usage
- **CONTRIBUTING.md:** Development setup, PR process
- **ARCHITECTURE.md:** System design, data flows
- **API_REFERENCE.md:** Complete API documentation
- **CHANGELOG.md:** Version history with migration notes

### Feature Documentation:

- **Feature Overview:** Purpose, use cases, limitations
- **Configuration:** All options with examples
- **Examples:** Working code for common scenarios
- **Troubleshooting:** Known issues, error messages, solutions

---

## Enforcement Mechanisms

### Automated Enforcement:

1. **Pre-commit Hooks:** Linting, formatting, security checks
2. **CI/CD Pipelines:** Tests, security scans, code coverage
3. **PR Reviews:** Automated review bots, human approvals
4. **Branch Protection:** Require passing checks before merge

### Manual Enforcement:

1. **Code Reviews:** Peer review for completeness, quality
2. **Architecture Review:** Design review for major changes
3. **Security Review:** Security team review for sensitive code
4. **Documentation Review:** Tech writer review for user-facing docs

### Violation Consequences:

- **Incomplete Code:** PR rejected, regeneration required
- **Security Issues:** Immediate fix required, deployment blocked
- **Missing Tests:** Coverage check fails, PR blocked
- **Poor Documentation:** Review comments, improvement required

---

## Exceptions Process

**Requesting Exceptions:**

Only repository maintainers can approve exceptions. To request:

1. Create GitHub issue with `governance-exception` label
2. Document the specific requirement being violated
3. Explain why exception is necessary (technical constraints, timelines, etc.)
4. Propose mitigation (timeline for compliance, alternative approach, etc.)
5. Wait for maintainer approval before proceeding

**Temporary Exceptions:**

- Must have expiration date
- Tracked in `TECHNICAL_DEBT.md`
- Automated reminders for resolution

**Permanent Exceptions:**

- Require architectural review board approval
- Documented in `ARCHITECTURE_DECISIONS.md`
- Reviewed annually for continued validity

---

## Profile Versioning

**Version:** 1.1.0
**Format:** Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR:** Breaking changes to governance policy
- **MINOR:** New requirements or standards added
- **PATCH:** Clarifications, typo fixes, formatting

**Change Process:**

1. Propose changes via PR to this file
2. Discuss in GitHub Discussions
3. Approve via maintainer consensus
4. Update version number
5. Announce in CHANGELOG.md

---

## Project-Specific Context

### Project-AI Architecture:

**Core Systems (src/app/core/):**

- Six AI systems in `ai_systems.py` (FourLaws, AIPersona, Memory, Learning, Plugin, Override)
- User management with bcrypt hashing
- JSON-based persistence in `data/` directory
- OpenAI/Hugging Face integrations

**GUI (src/app/gui/):**

- PyQt6 "Leather Book" interface
- Dual-page layout (Tron login + 6-zone dashboard)
- Signal-based component communication

**Testing:**

- pytest with 80%+ coverage target
- Isolated testing with `tempfile.TemporaryDirectory()`
- Test fixtures for all core systems

**Development:**

- Python 3.11+ required
- ruff for linting (configured in pyproject.toml)
- mypy for type checking
- Docker for containerized deployment

**Key Conventions:**

- Use `python -m src.app.main` (NOT `python src/app/main.py`)
- Call `_save_state()` after all state modifications
- Use Python logging (NOT print statements)
- Follow ruff-enforced import order (stdlib, third-party, local)

### Expanded System Coverage (Merged Baseline)

The following repository-specific coverage is mandatory context for AI assistants and is merged from legacy copilot technical instructions to ensure complete system-level awareness.

#### Core Structure Coverage

```text
src/app/
├── main.py                    # Entry point: LeatherBookInterface
├── core/                      # 11 business logic modules
│   ├── ai_systems.py          # 6 AI systems (FourLaws, Persona, Memory, Learning, Plugin, Override)
│   ├── user_manager.py        # User auth, bcrypt hashing, JSON persistence
│   ├── command_override.py    # Extended master password system with additional safety controls
│   ├── learning_paths.py      # OpenAI-powered learning path generation
│   ├── data_analysis.py       # CSV/XLSX/JSON analysis and clustering
│   ├── security_resources.py  # Security intelligence and resource integrations
│   ├── location_tracker.py    # Geolocation and encrypted history handling
│   ├── emergency_alert.py     # Emergency contact system with alerting
│   ├── intelligence_engine.py # OpenAI chat integration
│   ├── intent_detection.py    # Intent classifier
│   └── image_generator.py     # Image generation backends and safety checks
├── agents/                    # 4 AI agent modules (NOT plugins)
│   ├── oversight.py
│   ├── planner.py
│   ├── validator.py
│   └── explainability.py
└── gui/                       # PyQt6 UI modules
    ├── leather_book_interface.py
    ├── leather_book_dashboard.py
    ├── persona_panel.py
    ├── dashboard_handlers.py
    ├── dashboard_utils.py
    └── image_generation.py
```

#### Six-Core-System Expectations (`src/app/core/ai_systems.py`)

1. **FourLaws**: ethics hierarchy and action safety validation
2. **AIPersona**: personality traits, mood state, persistence-backed persona behavior
3. **MemoryExpansionSystem**: conversation logging and knowledge persistence
4. **LearningRequestManager**: human-in-the-loop learning approval workflow
5. **CommandOverride**: protected override controls and audit trail
6. **PluginManager**: plugin enable/disable lifecycle controls

> Clarification: AI agents in `src/app/agents/` are distinct from plugin extensions managed by `PluginManager`.

#### Data Persistence Baseline

All critical systems persist state in `data/` and changes must be durability-safe.

- `users.json`
- `data/ai_persona/state.json`
- `data/memory/knowledge.json`
- `data/learning_requests/requests.json`
- `data/command_override_config.json`

AI assistants MUST preserve and respect state-saving conventions (`_save_state()`, `save_users()`, equivalent transactional patterns) after mutation paths.

#### Development and Execution Workflows

- **Desktop run**: `python -m src.app.main`
- **Tests**: `pytest -v`
- **Lint**: `ruff check .` (and fix mode where appropriate)
- **Containerized run/build**: `docker-compose up`, `docker build ...`
- **Web split context**: backend `web/backend`; frontend `web/frontend`

Assistants must preserve explicit context boundaries between desktop runtime and web runtime when proposing or applying changes.

#### Integration Coverage Requirements

- Environment loading via `.env` (`python-dotenv`) where applicable
- OpenAI integration points in intelligence/learning/image generation modules
- Hugging Face integration path for image generation backend
- Signal/slot communication patterns in PyQt6 UI
- Agent subsystem integration via `src/app/agents/*`

#### Image Generation Subsystem Coverage

Assistants must account for:

- Dual backend strategy (OpenAI + Hugging Face)
- Prompt safety/content filtering
- Style preset handling and generation metadata/history
- UI-level async behavior to avoid main-thread blocking
- Dashboard navigation hooks for image generation entry/exit flows

#### Repository Automation and Security Workflow Awareness

Assistants must preserve and not bypass existing automation where present, including:

- CI lint/test/type/security checks
- CodeQL and Bandit security workflows
- Dependabot and dependency automation behavior
- Existing PR automation/policy enforcement behavior

When modifying automation-sensitive files, assistants must document compatibility implications.

#### Critical Operational Gotchas

1. Use module invocation from repository root (`python -m ...`) for import correctness
2. Ensure data directories exist before persistence operations
3. Keep GUI updates on the main thread and follow PyQt-safe async patterns
4. Persist state immediately on mutating operations
5. Treat denied-content/fingerprint checks as hard safety paths
6. Maintain secure hashing/encryption conventions already used by the subsystem
7. Follow Codacy instruction policy in `.github/instructions/codacy.instructions.md` when Codacy tooling is available

#### Repository Integrity Assumption

AI assistants operating in this monorepo MUST treat all repository components as potentially mission-critical unless maintainers explicitly mark otherwise. Avoid dismissive classification of any directory or artifact as non-essential.

#### Environment Baseline

Typical environment variables used across system features include:

- `OPENAI_API_KEY`
- `HUGGINGFACE_API_KEY`
- `FERNET_KEY`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

#### GUI Runtime and Navigation Contracts

- GUI is centered on the Leather Book interface with a dual-page experience (Tron-styled login + multi-zone dashboard)
- Tron color constants are actively used in GUI modules (`TRON_GREEN = "#00ff00"`, `TRON_CYAN = "#00ffff"`)
- Inter-component communication is signal/slot based and must remain thread-safe for UI updates
- Image generation navigation contract is wired through `leather_book_dashboard.py` signal `image_gen_requested` and `leather_book_interface.py` handlers `switch_to_image_generation()` / `switch_to_dashboard()`

#### Image Generation Implementation Contracts

- Core image pipeline is implemented in `src/app/core/image_generator.py`
- Required implementation contracts include `ImageGenerator`, `check_content_filter()`, `generate_with_huggingface()`, `generate_with_openai()`, and unified `generate()`
- GUI image generation surfaces include `ImageGenerationWorker`, `ImageGenerationLeftPanel`, and `ImageGenerationRightPanel`
- Safety and reliability contracts must preserve blocked-keyword checks, safety negative prompts, retry/backoff handling, and generation history/statistics path behavior

#### Testing and Discovery Baseline

- Primary test discovery (from `pyproject.toml`) is `testpaths = ["tests"]`, `pythonpath = ["src"]`, and `python_files = "test_*.py"`
- Compatibility pytest settings are also present in `setup.cfg` and should not be broken by instruction updates
- Assistants must maintain test naming/discovery compatibility when adding or reorganizing tests

#### Web Runtime Context Baseline

- Web backend and frontend are intentionally separated under `web/backend` and `web/frontend`
- Current web docs reference local defaults of backend port `5000` and frontend port `3000`
- Assistants must preserve explicit desktop/web separation in implementation and troubleshooting guidance

#### Deployment Entry Points and Operational Commands

- Desktop launch scripts exist at `scripts/launch-desktop.ps1` and `scripts/launch-desktop.bat`
- Container/deployment artifacts include root-level Docker and compose files and deployment workflows in `.github/workflows/`
- Assistants must prefer repository-defined launch/deploy entry points over ad-hoc alternatives unless maintainers request changes

#### Workflow and Automation Inventory Awareness

Key workflow files currently present include (non-exhaustive):

- `ci.yml`
- `bandit.yml`
- `codeql.yml`
- `dependency-review.yml`
- `deploy.yml`
- `production-deployment.yml`
- `security-secret-scan.yml`
- `format-and-fix.yml`
- `generate-sbom.yml`

Assistants must treat workflow files as first-class governance and release infrastructure and must document compatibility impact before changing them.

#### Monorepo and Submodule Integrity Baseline

- This repository includes deep monorepo composition with external and security submodules
- Assistants must assume cross-directory coupling can be intentional, even when local usage appears indirect
- Any recommendation to remove, isolate, or de-prioritize components requires explicit maintainer confirmation

#### Instruction Artifact Purpose Levels (Per File)

- **P0 Authoritative Governance**: `.github/Active_Governance_Policy.md` — mandatory behavior, quality thresholds, and production-readiness standards.
- **P0 Operational Quality/Security Gate**: `.github/instructions/codacy.instructions.md` — Codacy-driven analysis and dependency-security enforcement when Codacy tooling is available.
- **P1 Structural Runtime Contract Reference**: `.github/instructions/ARCHITECTURE_QUICK_REF.md` — architecture/data-flow/runtime conventions and critical operational patterns.
- **P2 Implementation Evidence and Change Ledger**: `.github/instructions/IMPLEMENTATION_SUMMARY.md` — instruction-system implementation status and consolidated coverage evidence.
- **P3 Legacy Technical Context (Superseded)**: `archive/.github/copilot-instructions.md` — historical reference only; must not override P0/P1 files.

#### Instruction Resolution Order

When instruction files overlap, resolve in this order:

1. `.github/Active_Governance_Policy.md`
2. `.github/instructions/codacy.instructions.md`
3. `.github/instructions/ARCHITECTURE_QUICK_REF.md`
4. `.github/instructions/IMPLEMENTATION_SUMMARY.md`
5. `archive/.github/copilot-instructions.md`

Assistants must not hardcode secrets and must preserve secure secret-management patterns.

---

## Acknowledgments

This governance profile ensures Project-AI maintains the highest standards of code quality, security, and maintainability. All contributors—human and AI—are expected to uphold these principles.

**Effective Date:** 2026-01-23
**Review Cycle:** Quarterly
**Maintained By:** Project-AI Core Team

---

## References

- [Project-AI Program Summary](../PROGRAM_SUMMARY.md)
- [Developer Quick Reference](../DEVELOPER_QUICK_REFERENCE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Security Policy](../SECURITY.md)
- [Architecture Documentation](instructions/ARCHITECTURE_QUICK_REF.md)
- [Legacy Technical Instructions (Archive)](../archive/.github/copilot-instructions.md)
