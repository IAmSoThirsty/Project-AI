<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / CONTRIBUTING.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / CONTRIBUTING.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Contributing to Cerberus

Thank you for your interest in contributing to Cerberus! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip or uv for package management

### Setup Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/Cerberus.git
cd Cerberus
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -e ".[dev]"
```

4. **Verify installation**

```bash
pytest tests/
ruff check src tests
mypy src
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Follow the existing code style
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_hub.py

# Run with coverage
pytest --cov=cerberus --cov-report=term-missing
```

### 4. Lint and Format

```bash
# Check code style
ruff check src tests

# Auto-fix issues
ruff check --fix src tests

# Type check
mypy src
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve issue with spawn rate limiting"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use docstrings for all public functions and classes

### Code Quality

- Write tests for all new functionality
- Maintain or improve code coverage
- No `# type: ignore` comments without justification
- No hardcoded credentials or secrets

### Testing

- Write unit tests for all new code
- Use descriptive test names
- Group related tests in classes
- Mock external dependencies

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include examples in docstrings
- Update relevant documentation in `docs/`

## Project Structure

```
Cerberus/
├── src/cerberus/           # Main package code
│   ├── guardians/          # Guardian implementations
│   ├── hub/                # Hub coordinator
│   ├── security/           # Security modules
│   ├── config.py           # Configuration management
│   └── logging_config.py   # Logging setup
├── tests/                  # Test files
├── docs/                   # Documentation
├── .github/                # GitHub workflows
└── pyproject.toml          # Project configuration
```

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** that demonstrate the fix or feature
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** (if applicable)
5. **Request review** from maintainers

### PR Requirements

- All tests must pass
- Code coverage should not decrease
- No merge conflicts with main branch
- At least one approval from a maintainer

## Security Contributions

If you're contributing security-related changes:

1. Follow secure coding practices
2. Never commit credentials or secrets
3. Document security implications
4. Consider edge cases and attack vectors

For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## Configuration Guidelines

When adding new configuration options:

1. Add to `CerberusSettings` in `src/cerberus/config.py`
2. Include validation and reasonable defaults
3. Document the setting in code and README
4. Add environment variable support with `CERBERUS_` prefix

## Adding New Guardians

To add a new guardian type:

1. Create a new class inheriting from `BaseGuardian`
2. Implement the `analyze` method
3. Add tests in `tests/test_guardians.py`
4. Update documentation

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v0.1.0 -m "Release 0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Create GitHub release

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Join our community chat (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Cerberus! 🐺
