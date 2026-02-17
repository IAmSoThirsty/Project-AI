# Code Validation Standards

## Overview

This document defines the comprehensive code validation standards for Project-AI. All code contributions MUST pass these validation checks before merging.

## Validation Tools

### 1. Ruff (Linting & Code Quality)

**Purpose:** Enforce Python code style, detect common errors, and maintain code quality.

**Configuration:** `pyproject.toml` - `[tool.ruff]` section

**Key Rules:**

- E: Errors (PEP8 violations)
- W: Warnings (PEP8 warnings)
- F: Pyflakes (unused imports, undefined names)
- I: isort (import sorting)
- N: pep8-naming (naming conventions)
- UP: pyupgrade (Python version upgrades)
- B: flake8-bugbear (likely bugs)
- C4: flake8-comprehensions (list/dict comprehensions)
- SIM: flake8-simplify (code simplification)

**Running:**

```bash

# Check for issues

ruff check .

# Auto-fix issues

ruff check . --fix --unsafe-fixes

# Show statistics

ruff check . --statistics
```

**CI/CD:** Runs automatically on every PR and push to main branches.

### 2. Black (Code Formatting)

**Purpose:** Enforce consistent Python code formatting.

**Configuration:** `pyproject.toml` - `[tool.black]` section

**Settings:**

- Line length: 88 characters
- Target Python version: 3.11+
- String normalization: enabled

**Running:**

```bash

# Check formatting

black --check src/ tests/ scripts/

# Apply formatting

black src/ tests/ scripts/
```

**CI/CD:** Runs in pre-commit hooks and CI pipeline.

### 3. MyPy (Type Checking)

**Purpose:** Static type checking to catch type-related bugs.

**Configuration:** Command-line arguments (consider adding mypy.ini)

**Key Checks:**

- Type annotation coverage
- Type compatibility
- Return type validation
- Argument type validation

**Running:**

```bash

# Check specific directory

mypy src/app/ --ignore-missing-imports

# Check with detailed output

mypy src/app/ --show-error-codes --pretty
```

**Current Issues:** ~7 type errors in core modules (see TODO list)

### 4. Pytest (Testing)

**Purpose:** Automated testing of all code functionality.

**Configuration:** `pyproject.toml` - `[tool.pytest.ini_options]` section

**Test Types:**

- Unit tests: Individual function/class testing
- Integration tests: Component interaction testing
- E2E tests: Full system testing
- Security tests: Attack simulation and validation

**Coverage Requirements:**

- Minimum: 80% line coverage
- Goal: 90%+ coverage for critical modules

**Running:**

```bash

# Run all tests

pytest

# Run with coverage

pytest --cov=src --cov-report=html

# Run specific test file

pytest tests/test_ai_systems.py -v

# Fast mode (core tests only)

pytest tests/test_ai_systems.py tests/test_user_manager.py
```

**Test Structure:**

- `tests/` - Main test directory
- `tests/unit/` - Unit tests
- `tests/integration/` - Integration tests
- `tests/e2e/` - End-to-end tests
- `tests/security/` - Security tests

### 5. Bandit (Security Scanning)

**Purpose:** Detect common security vulnerabilities in Python code.

**Configuration:** Command-line arguments

**Security Checks:**

- SQL injection vulnerabilities
- Command injection risks
- Hardcoded passwords/secrets
- Insecure cryptography
- Unsafe YAML/pickle usage
- Assert statements in production

**Running:**

```bash

# Basic scan

bandit -r src/ scripts/

# With severity filtering

bandit -r src/ --severity-level medium --confidence-level medium

# Generate report

bandit -r src/ -f json -o bandit_report.json
```

**CI/CD:** Runs on every PR with SARIF upload to GitHub Security.

## Comprehensive Validation Script

### Usage

Use the all-in-one validation script:

```bash

# Check mode (default)

python scripts/validate_all_code.py

# Fix mode (auto-fix where possible)

python scripts/validate_all_code.py --fix

# Fast mode (skip slow tests)

python scripts/validate_all_code.py --fast

# Generate JSON report

python scripts/validate_all_code.py --report
```

### What It Checks

1. ✅ Ruff linting (with auto-fix support)
1. ✅ Black formatting (with auto-fix support)
1. ✅ MyPy type checking
1. ✅ Bandit security scanning
1. ✅ Pytest test collection
1. ✅ Pytest test execution

### Exit Codes

- `0`: All validations passed
- `1`: One or more validations failed

## Pre-commit Hooks

### Installation

```bash

# Install pre-commit

pip install pre-commit

# Install hooks

pre-commit install

# Run manually on all files

pre-commit run --all-files
```

### Configured Hooks

1. **Ruff** - Linting and auto-formatting
1. **Black** - Code formatting
1. **MyPy** - Type checking
1. **Bandit** - Security scanning
1. **Standard checks** - YAML, JSON, trailing whitespace, etc.
1. **Markdown linting** - Documentation quality
1. **Docker linting** - Dockerfile best practices

### Configuration

See `.pre-commit-config.yaml` for full configuration.

## CI/CD Integration

### GitHub Actions Workflows

**Primary Workflow:** `.github/workflows/project-ai-monolith.yml`

**Validation Phases:**

1. **Static Analysis (Phase 3)**

   - Ruff linting
   - Output format: GitHub annotations

1. **Unit Tests (Phase 4)**

   - Pytest execution
   - Coverage reporting (XML + HTML)
   - Coverage threshold: 80%

1. **Security Scanning (Phase 2)**

   - CodeQL analysis
   - Bandit SARIF upload
   - Secret detection
   - Dependency audits

1. **Type Checking (Phase 4)**

   - MyPy validation
   - Type annotation coverage

### Workflow Triggers

- Push to `main`, `release`, `cerberus-integration` branches
- Pull requests to `main`, `release` branches
- Manual workflow dispatch
- Scheduled runs (daily at 2 AM UTC)

### Required Status Checks

Before merging to `main`:

- ✅ Ruff linting passes (or warnings only)
- ✅ Tests pass (minimum 80% coverage)
- ✅ Security scans complete (no critical issues)
- ✅ Type checking passes (or known issues only)

## Exception Handling

### When to Bypass Validation

**NEVER** bypass validation for:

- Security vulnerabilities
- Critical bugs
- Type safety issues

**MAY** bypass validation for:

- Urgent hotfixes (with post-merge fix required)
- Documentation-only changes (if validation fails on docs)
- Known false positives (document in code comments)

### Documenting Exceptions

Use inline comments:

```python

# ruff: noqa: E501 - Long URL in docstring, cannot be shortened

DOCUMENTATION_URL = "https://very-long-url..."

# type: ignore[union-attr] - False positive, type narrowing guarantees non-None

value = obj.get_value().upper()

# nosec B608 - SQL query uses parameterized query, safe from injection

cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## Monitoring and Metrics

### Coverage Tracking

- **Tool:** pytest-cov + Codecov
- **Target:** 80% minimum, 90% goal
- **Reports:** `htmlcov/index.html` (local), Codecov dashboard (CI)

### Quality Metrics

Track these metrics over time:

- Linting errors per 1000 lines
- Test coverage percentage
- Type annotation coverage
- Security vulnerability count
- Technical debt ratio

### Dashboards

- **GitHub Actions:** Check run summaries
- **Codecov:** Coverage trends and reports
- **GitHub Security:** CodeQL and SARIF alerts
- **Validation Reports:** `validation_report.json` (generated by script)

## Best Practices

### For Developers

1. **Run validation locally before pushing**

   ```bash
   python scripts/validate_all_code.py --fix
   ```

1. **Install pre-commit hooks**

   ```bash
   pre-commit install
   ```

1. **Fix issues incrementally**

   - Don't accumulate linting errors
   - Add types as you write code
   - Write tests alongside features

1. **Review validation reports**

   - Check CI logs for failures
   - Understand why checks failed
   - Fix root causes, not symptoms

### For Reviewers

1. **Verify validation passed**

   - Check GitHub Actions status
   - Review coverage reports
   - Check security scan results

1. **Look beyond automated checks**

   - Code readability
   - Algorithm efficiency
   - Architecture patterns
   - Edge case handling

1. **Ensure tests are meaningful**

   - Not just for coverage numbers
   - Test actual behavior
   - Include negative test cases

## Troubleshooting

### Common Issues

**Issue:** Ruff finds too many errors

- **Solution:** Run `ruff check . --fix` to auto-fix most issues
- **Alternative:** Fix categories incrementally (imports, then whitespace, etc.)

**Issue:** MyPy type errors

- **Solution:** Add type annotations, use `# type: ignore[code]` for false positives
- **Reference:** MyPy error codes - https://mypy.readthedocs.io/en/stable/error_codes.html

**Issue:** Tests fail in CI but pass locally

- **Solution:** Check environment differences (dependencies, file paths, env vars)
- **Debug:** Run `pytest -v --tb=long` for detailed output

**Issue:** Pre-commit hooks are slow

- **Solution:** Use `SKIP=` to skip specific hooks temporarily
- **Example:** `SKIP=mypy git commit -m "message"`

### Getting Help

1. Check this documentation first
1. Review CI/CD logs for detailed error messages
1. Run validation locally with `--report` flag for detailed analysis
1. Consult pyproject.toml and workflow files for configuration
1. Ask in #engineering Slack channel or open a GitHub discussion

## Continuous Improvement

### Quarterly Review

Every quarter, review and update:

- Linting rules (add/remove/adjust)
- Test coverage targets
- Security scanning tools
- Validation performance

### Metrics to Track

- Validation execution time
- False positive rate
- Developer satisfaction
- Bug escape rate

### Feedback Loop

- Collect developer feedback on validation pain points
- Adjust rules based on real-world usage
- Add new checks for recurring issues
- Remove checks that don't add value

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Black Documentation](https://black.readthedocs.io/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)

______________________________________________________________________

**Last Updated:** 2026-02-14 **Maintained By:** Project-AI Engineering Team **Review Cycle:** Quarterly
