# Build & Package Management

**Document Type:** Technical Reference  
**Component:** Build System & Dependency Management  
**Status:** Production  
**Version:** 2.0.0  
**Last Updated:** 2025-01-26  
**Author:** AGENT-046  
**Audience:** Developers, Build Engineers, Package Maintainers  
**Scope:** pyproject.toml, package.json, requirements management, build workflows  
**Related Docs:**
- `02-docker-deployment-guide.md`
- `03-ci-cd-pipelines.md`
- `06-environment-configuration.md`

---

## Table of Contents

1. [Build System Overview](#build-system-overview)
2. [Python Package Management](#python-package-management)
3. [Node.js Package Management](#node-js-package-management)
4. [Dependency Resolution](#dependency-resolution)
5. [Build Scripts](#build-scripts)
6. [Version Management](#version-management)
7. [Distribution](#distribution)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Build System Overview

### Multi-Language Project Structure

Project-AI is a **polyglot project** with multiple package managers:

```
Project-AI/
├── Python Core (pyproject.toml)
│   ├── Desktop Application (PyQt6)
│   ├── Web Backend (Flask)
│   └── Core AI Systems
│
├── Node.js Tools (package.json)
│   ├── Test Runners
│   ├── Markdown Linting
│   └── TARL Build System
│
└── Thirsty-Lang (src/thirsty_lang/package.json)
    └── Custom Language Runtime
```

**Build Strategy:**
1. **Python-First**: Core application is Python
2. **Node.js for Tooling**: Tests, linting, documentation
3. **Isolated Dependencies**: Each subsystem manages its own deps

---

## Python Package Management

### pyproject.toml

**File:** `pyproject.toml`

**Purpose:** Modern Python packaging standard (PEP 518, PEP 621).

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project-ai"
version = "1.0.0"
description = "Comprehensive AI assistant with advanced features"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Project AI Team"}]
keywords = ["ai", "assistant", "pyqt6", "machine-learning"]
dynamic = ["scripts"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Android",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: JavaScript",
    "Programming Language :: Java",
    "Programming Language :: Rust",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Desktop Environment",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
]
```

**Key Sections:**

#### 1. Build System

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"
```

**Components:**
- `requires`: Build dependencies (tools needed to build package)
- `build-backend`: Backend API for building (setuptools, flit, poetry, hatch)

**Why setuptools:**
- Industry standard
- Broad compatibility
- Extensive plugin ecosystem

#### 2. Project Metadata

```toml
[project]
name = "project-ai"                 # PyPI package name (must be unique)
version = "1.0.0"                   # Semantic versioning
description = "..."                 # One-line description
readme = "README.md"                # Long description (uploaded to PyPI)
requires-python = ">=3.11"          # Minimum Python version
license = {text = "MIT"}            # License identifier
authors = [{name = "..."}]          # Package authors
keywords = [...]                    # PyPI search keywords
```

**Classifiers:**
- Used for PyPI categorization
- Help users find packages
- Indicate supported platforms, Python versions, development status

**Trove Classifiers Reference:** https://pypi.org/classifiers/

#### 3. Dependencies

```toml
dependencies = [
    "Flask>=3.0.0",
    "scikit-learn>=1.0.0",
    "geopy>=2.0.0",
    "cryptography>=43.0.1",        # Security-critical: pinned version
    "openai>=0.27.0",
    "python-dotenv>=0.19.0",
    "requests>=2.32.4",            # Security fix: CVE-2024-35195
    "numpy>=1.20.0",
    "pandas>=1.0.0",
    "matplotlib>=3.5.0",
    "PyPDF2>=3.0.0",
    "passlib>=1.7.0",
    "bcrypt>=5.0.0",
    "httpx>=0.24.0",
    "defusedxml>=0.7.0",           # Security: Prevent XML attacks
    "typer>=0.9.0",
    "temporalio>=1.5.0",
    "protobuf>=4.0.0",
    "PyYAML>=6.0.0",
]
```

**Dependency Specification:**
- `package`: Any version (not recommended)
- `package>=1.0.0`: Minimum version
- `package>=1.0.0,<2.0.0`: Version range
- `package==1.0.0`: Exact version (use sparingly)

**Pinning Strategy:**
- **Production:** Pin exact versions in `requirements.txt`
- **Library:** Use flexible ranges in `pyproject.toml`
- **Security-Critical:** Pin to patched versions

#### 4. Optional Dependencies

```toml
[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",              # Linting & formatting
    "pytest>=7.0.0",            # Testing framework
    "pytest-cov>=4.0.0",        # Coverage reporting
    "black>=22.0.0",            # Code formatter (legacy)
    "flake8>=7.0.0",            # Linter (legacy, prefer ruff)
]
```

**Usage:**
```bash
# Install core dependencies only
pip install .

# Install with dev dependencies
pip install .[dev]

# Install multiple extras
pip install .[dev,docs,testing]
```

**Use Cases:**
- `dev`: Development tools (linters, formatters, test runners)
- `docs`: Documentation generation (Sphinx, mkdocs)
- `testing`: Testing dependencies (pytest, coverage, mocks)
- `gui`: GUI dependencies (PyQt6, only for desktop)

### Tool Configuration

#### Ruff (Linter & Formatter)

```toml
[tool.ruff]
exclude = [
    "*.md",                    # Exclude markdown files
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "build",
    "dist"
]

line-length = 88              # Black compatibility
target-version = "py311"      # Target Python 3.11

[tool.ruff.lint]
select = [
    "E",      # Errors (PEP 8)
    "W",      # Warnings
    "F",      # Pyflakes (unused imports, undefined names)
    "I",      # isort (import sorting)
    "N",      # pep8-naming (naming conventions)
    "UP",     # pyupgrade (modern Python syntax)
    "B",      # flake8-bugbear (common bugs)
    "C4",     # flake8-comprehensions (list/dict comprehensions)
    "SIM",    # flake8-simplify (simplification suggestions)
]

ignore = [
    "E501",   # Line too long (handled by formatter)
    "D",      # Skip all pydocstyle rules for now
    "SIM105", # Suppress contextlib suggestions
    "N807",   # __init__ in documentation examples
    "N802",   # eventFilter is a PyQt6 method name (can't change)
]
```

**Ruff Benefits:**
- 10-100x faster than flake8 + isort + black
- Single tool for linting and formatting
- Drop-in replacement for multiple tools

**Running Ruff:**
```bash
# Lint
ruff check .

# Lint and auto-fix
ruff check . --fix

# Format code
ruff format .
```

#### Pytest Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]            # Where to find tests
python_files = "test_*.py"       # Test file pattern
addopts = "--strict-markers -v"  # Always use these options
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
]
```

**Custom Markers:**
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Exclude slow tests
pytest -m "not slow"
```

#### Black Configuration (Legacy)

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

**Note:** Ruff format is replacing Black in the Project-AI codebase.

### requirements.txt

**File:** `requirements.txt`

**Purpose:** Pin exact versions for production deployments.

```
Flask==3.0.0
scikit-learn==1.3.2
geopy==2.4.1
cryptography==43.0.1
openai==1.12.0
python-dotenv==1.0.0
requests==2.32.4
numpy==1.26.3
pandas==2.1.4
matplotlib==3.8.2
PyPDF2==3.0.1
passlib==1.7.4
bcrypt==5.0.0
httpx==0.27.0
defusedxml==0.7.1
typer==0.9.0
temporalio==1.5.0
protobuf==4.25.1
PyYAML==6.0.1
```

**Why Pin Versions:**
- Reproducible builds (same versions everywhere)
- Prevent breaking changes from dependency updates
- Security: Ensure patched versions are used

**Generation:**
```bash
# Generate from current environment
pip freeze > requirements.txt

# Generate from pyproject.toml (with versions)
pip-compile pyproject.toml
```

**requirements-dev.txt:**
```
# Include production dependencies
-r requirements.txt

# Add development tools
ruff==0.1.14
pytest==8.0.0
pytest-cov==4.1.0
black==24.1.1
flake8==7.0.0
```

### Build Commands

**Install Dependencies:**
```bash
# Install from requirements.txt (production)
pip install -r requirements.txt

# Install from pyproject.toml (development)
pip install -e .             # Editable install
pip install -e .[dev]        # With dev dependencies
```

**Build Package:**
```bash
# Build source distribution and wheel
python -m build

# Output:
# dist/
# ├── project_ai-1.0.0-py3-none-any.whl
# └── project_ai-1.0.0.tar.gz
```

**Install Locally:**
```bash
# Install wheel
pip install dist/project_ai-1.0.0-py3-none-any.whl

# Install from source
pip install .
```

---

## Node.js Package Management

### package.json

**File:** `package.json`

```json
{
  "name": "project-ai",
  "version": "1.0.0",
  "description": "Comprehensive AI assistant with advanced features",
  "main": "src/app/main.py",
  "scripts": {
    "test": "npm run test:js && npm run test:python",
    "test:js": "node --test src/**/*.test.js",
    "test:python": "pytest -q",
    "lint": "ruff check .",
    "format": "ruff check . --fix",
    "dev": "docker-compose up",
    "build": "docker build -t project-ai:latest .",
    "lint:markdown": "markdownlint README.md PROGRAM_SUMMARY.md docs docs/developer --config .markdownlint.json",
    "tarl:build": "python -m tarl.build.cli build",
    "tarl:clean": "python -m tarl.build.cli clean",
    "tarl:list": "python -m tarl.build.cli list",
    "tarl:cache": "python -m tarl.build.cli cache stats"
  },
  "keywords": [
    "ai",
    "assistant",
    "pyqt6",
    "machine-learning",
    "desktop"
  ],
  "author": "Project AI Team",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/IAmSoThirsty/Project-AI"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "devDependencies": {
    "markdownlint-cli": "^0.47.0"
  }
}
```

**Key Sections:**

#### Scripts

```json
"scripts": {
  "test": "npm run test:js && npm run test:python",
  "test:js": "node --test src/**/*.test.js",
  "test:python": "pytest -q",
  "lint": "ruff check .",
  "format": "ruff check . --fix",
  "dev": "docker-compose up",
  "build": "docker build -t project-ai:latest .",
  "lint:markdown": "markdownlint README.md ...",
  "tarl:build": "python -m tarl.build.cli build",
  "tarl:clean": "python -m tarl.build.cli clean",
  "tarl:list": "python -m tarl.build.cli list",
  "tarl:cache": "python -m tarl.build.cli cache stats"
}
```

**Script Patterns:**
- `test`: Run all tests
- `test:<type>`: Run specific test type (js, python)
- `lint`: Check code quality
- `format`: Auto-fix code quality issues
- `dev`: Start development environment
- `build`: Build production artifacts
- `<namespace>:<action>`: Namespaced commands (tarl:build, tarl:clean)

**Running Scripts:**
```bash
npm run test          # Run all tests
npm run lint          # Lint code
npm run tarl:build    # Run TARL build
```

#### Engines

```json
"engines": {
  "node": ">=18.0.0"
}
```

**Purpose:** Specify required Node.js version.

**Enforcement:**
```bash
# Warn if wrong Node version
npm install

# Enforce strict version
npm config set engine-strict true
```

#### Dependencies vs devDependencies

```json
{
  "dependencies": {
    // Runtime dependencies (needed in production)
    "express": "^4.18.0"
  },
  "devDependencies": {
    // Development-only dependencies
    "markdownlint-cli": "^0.47.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
```

**When to Use Which:**
- `dependencies`: Required to run the application
- `devDependencies`: Required to develop/test (not needed in production)

**Installation:**
```bash
# Install all dependencies (dev + production)
npm install

# Install production only (skip devDependencies)
npm install --production
```

### package-lock.json

**File:** `package-lock.json`

**Purpose:** Lock exact versions of dependencies and sub-dependencies.

**Key Features:**
- **Deterministic Installs**: Same versions across all environments
- **Integrity Hashes**: Verify packages haven't been tampered with
- **Dependency Tree**: Complete dependency graph with versions

**Should You Commit:**
- ✅ **YES** for applications (reproducible builds)
- ❌ **NO** for libraries (allow flexibility)

**Regeneration:**
```bash
# Delete lock file and regenerate
rm package-lock.json
npm install

# Update specific package
npm update markdownlint-cli
```

---

## Dependency Resolution

### Python Dependency Resolution

**Order of Precedence:**
1. `requirements.txt` (if present) - Exact versions
2. `pyproject.toml` - Version ranges
3. Transitive dependencies (resolved by pip)

**Conflict Resolution:**
```bash
# Check for conflicts
pip check

# Output conflicts
pip list --outdated
```

**Example Conflict:**
```
Package A requires: numpy>=1.20.0,<2.0.0
Package B requires: numpy>=1.24.0
Resolution: Install numpy==1.24.0 (satisfies both)
```

### Node.js Dependency Resolution

**Algorithm:**
1. Check `package-lock.json` (if present)
2. Resolve version ranges from `package.json`
3. Flatten dependency tree (npm v3+)
4. Deduplicate packages

**Conflict Resolution:**
```bash
# View dependency tree
npm ls

# Check for duplicates
npm dedupe

# Audit for vulnerabilities
npm audit

# Fix vulnerabilities
npm audit fix
```

---

## Build Scripts

### Python Build Scripts

**File:** `scripts/build_production.ps1`

```powershell
# Build production-ready Python package
param(
    [string]$Version = "1.0.0"
)

Write-Host "Building Project-AI v$Version"

# Clean previous builds
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# Install build dependencies
python -m pip install --upgrade build wheel

# Build package
python -m build

Write-Host "✅ Build complete: dist/project_ai-$Version-py3-none-any.whl"
```

**Usage:**
```powershell
.\scripts\build_production.ps1 -Version "1.0.1"
```

### TARL Build Scripts

**NPM Scripts:**
```json
"tarl:build": "python -m tarl.build.cli build",
"tarl:clean": "python -m tarl.build.cli clean",
"tarl:list": "python -m tarl.build.cli list",
"tarl:cache": "python -m tarl.build.cli cache stats"
```

**Usage:**
```bash
npm run tarl:build       # Build TARL policies
npm run tarl:clean       # Clean build artifacts
npm run tarl:list        # List available policies
npm run tarl:cache       # Show cache statistics
```

---

## Version Management

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`

**Examples:**
- `1.0.0` - Initial release
- `1.0.1` - Patch (bug fix)
- `1.1.0` - Minor (new features, backward compatible)
- `2.0.0` - Major (breaking changes)

**Rules:**
1. **MAJOR:** Breaking changes (API incompatibility)
2. **MINOR:** New features (backward compatible)
3. **PATCH:** Bug fixes (backward compatible)

**Pre-release Versions:**
- `1.0.0-alpha.1` - Alpha release
- `1.0.0-beta.2` - Beta release
- `1.0.0-rc.1` - Release candidate

### Version Bump Workflow

```bash
# Manual version bump
# 1. Update pyproject.toml
[project]
version = "1.0.1"

# 2. Update package.json
"version": "1.0.1"

# 3. Create git tag
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# 4. Build and publish
python -m build
twine upload dist/*
```

**Automated Version Bump:**
```bash
# Using bump2version
pip install bump2version

# Bump patch version (1.0.0 → 1.0.1)
bump2version patch

# Bump minor version (1.0.1 → 1.1.0)
bump2version minor

# Bump major version (1.1.0 → 2.0.0)
bump2version major
```

---

## Distribution

### PyPI Publication

**Setup:**
```bash
# Install twine
pip install twine

# Create .pypirc (optional)
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-...  # Your PyPI token
EOF
```

**Build & Publish:**
```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to Test PyPI (dry run)
twine upload --repository testpypi dist/*

# Upload to Production PyPI
twine upload dist/*
```

**GitHub Actions Automation:**
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install build dependencies
        run: pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: twine upload dist/*
```

### Docker Hub Publication

```bash
# Build Docker image
docker build -t projectai/desktop:1.0.0 .

# Tag latest
docker tag projectai/desktop:1.0.0 projectai/desktop:latest

# Login
docker login

# Push
docker push projectai/desktop:1.0.0
docker push projectai/desktop:latest
```

---

## Troubleshooting

### Common Issues

#### 1. Dependency Conflicts

**Symptom:** `ERROR: package-a 1.0.0 has requirement package-b>=2.0.0, but you'll have package-b 1.5.0 which is incompatible.`

**Solution:**
```bash
# Create fresh virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies fresh
pip install -r requirements.txt
```

#### 2. Build Failures

**Symptom:** `error: command 'gcc' failed with exit status 1`

**Solution (Missing System Dependencies):**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# MacOS
xcode-select --install

# Windows
# Install Microsoft C++ Build Tools
```

#### 3. Import Errors After Install

**Symptom:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Install in editable mode
pip install -e .

# Or add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

---

## Best Practices

### 1. Virtual Environments

✅ **DO:**
```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

❌ **DON'T:**
- Install packages globally (use virtual environments)
- Commit `.venv/` to git (add to .gitignore)

### 2. Dependency Management

✅ **DO:**
- Pin security-critical packages to specific versions
- Use version ranges for flexibility
- Run `pip install --upgrade` regularly
- Audit dependencies for vulnerabilities

❌ **DON'T:**
- Use `package==*` (any version)
- Skip security updates
- Ignore deprecation warnings

### 3. Build Reproducibility

✅ **DO:**
```bash
# Lock all dependency versions
pip freeze > requirements.txt

# Include lock file in git
git add requirements.txt package-lock.json

# Document Python version
echo "3.11" > .python-version
```

---

## Summary

**Build System:**
- ✅ pyproject.toml for Python packaging
- ✅ package.json for Node.js tooling
- ✅ requirements.txt for pinned versions
- ✅ Ruff for linting and formatting
- ✅ Pytest for testing

**Key Files:**
- `pyproject.toml` - Python package metadata and configuration
- `package.json` - Node.js scripts and dependencies
- `requirements.txt` - Pinned Python dependencies
- `pytest.ini` - Test configuration

**Build Workflow:**
1. Install dependencies (`pip install -r requirements.txt`)
2. Lint code (`ruff check .`)
3. Run tests (`pytest`)
4. Build package (`python -m build`)
5. Publish (`twine upload dist/*`)

**Next Steps:**
- Review `06-environment-configuration.md` for environment setup
- See `03-ci-cd-pipelines.md` for automated builds
- Check `02-docker-deployment-guide.md` for containerization

---

**Document Metadata:**
- **Word Count:** 3,847 words
- **Code Examples:** 45
- **Configuration Files:** 8
- **Last Reviewed:** 2025-01-26
- **Next Review:** 2025-04-26

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

