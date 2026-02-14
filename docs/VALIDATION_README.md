# Code Validation Quick Start

This project uses comprehensive code validation to maintain high quality and security standards.

## Quick Commands

```bash
# Python validation
ruff check .                          # Check for issues
ruff check . --fix                    # Auto-fix issues
black src/ tests/ scripts/            # Format code
mypy src/app/ --ignore-missing-imports  # Type check
pytest                                # Run tests

# JavaScript validation (if Node.js is installed)
npm run lint:js                       # Check JavaScript
npm run lint:js:fix                   # Fix JavaScript issues

# All-in-one validation
python scripts/validate_all_code.py           # Check everything
python scripts/validate_all_code.py --fix     # Fix what's possible
python scripts/validate_all_code.py --fast    # Quick check (core tests only)
python scripts/validate_all_code.py --report  # Generate JSON report

# NPM shortcuts
npm run validate                      # Same as python script
npm run validate:fast                 # Fast mode
npm run validate:fix                  # Fix mode
```

## Pre-commit Hooks

Install once to run validation automatically on every commit:

```bash
pip install pre-commit
pre-commit install
```

Now every commit will automatically:
- Run ruff linting with auto-fix
- Format code with black
- Check types with mypy
- Scan for security issues with bandit
- Validate YAML, JSON, Markdown

## What Gets Validated

### Python
- **Style & Quality:** Ruff (3000+ rules)
- **Formatting:** Black (consistent style)
- **Type Safety:** MyPy (static type checking)
- **Security:** Bandit (vulnerability scanning)
- **Tests:** Pytest (80%+ coverage target)

### JavaScript
- **Style & Quality:** ESLint (Airbnb config)
- **Formatting:** Prettier
- **Tests:** Node.js test runner

### Configuration Files
- **YAML:** Syntax and formatting validation
- **JSON:** Syntax validation
- **TOML:** Syntax validation
- **Markdown:** Linting and formatting

## CI/CD Integration

Validation runs automatically on:
- Every push to main branches
- Every pull request
- Daily at 2 AM UTC (comprehensive scan)

Required checks before merge:
- ✅ Ruff linting passes (or warnings only)
- ✅ Tests pass with 80%+ coverage
- ✅ Security scans pass (no critical issues)

## Documentation

For detailed documentation, see:
- **[VALIDATION_STANDARDS.md](docs/VALIDATION_STANDARDS.md)** - Complete validation guide
- **[pyproject.toml](pyproject.toml)** - Python tool configuration
- **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Pre-commit hook configuration
- **[package.json](package.json)** - JavaScript validation scripts

## Current Status

**Linting:** 432 issues remaining (from 3043)
- Most are style preferences or require manual review
- See [VALIDATION_STANDARDS.md](docs/VALIDATION_STANDARDS.md) for details

**Testing:** 5625 tests collected
- Core tests: 13/13 passing
- Some tests require additional dependencies

**Type Checking:** MyPy infrastructure in place
- ~7 type errors in core modules to address

## Getting Help

1. **Quick help:** `python scripts/validate_all_code.py --help`
2. **Detailed docs:** See [docs/VALIDATION_STANDARDS.md](docs/VALIDATION_STANDARDS.md)
3. **Tool docs:**
   - [Ruff](https://docs.astral.sh/ruff/)
   - [Black](https://black.readthedocs.io/)
   - [MyPy](https://mypy.readthedocs.io/)
   - [Pytest](https://docs.pytest.org/)
   - [ESLint](https://eslint.org/)

## Contributing

Before submitting a PR:
1. Run `python scripts/validate_all_code.py --fix`
2. Fix any remaining issues
3. Ensure tests pass
4. Update documentation if needed

The CI/CD pipeline will validate your changes automatically.
