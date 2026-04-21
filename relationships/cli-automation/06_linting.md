---
title: Linting Relationships
description: Code quality enforcement through linting tools and configurations
tags:
  - relationships
  - linting
  - code-quality
  - ruff
  - eslint
created: 2025-02-08
agent: AGENT-063
---

# Linting Relationships

## Overview

Project-AI uses **3 primary linting tools** with centralized configuration and automated enforcement:

1. **Ruff** - Python linting (fast, comprehensive)
2. **ESLint** - JavaScript/TypeScript linting
3. **Markdownlint** - Documentation linting

---

## 🎯 Ruff (Python Linting)

### Configuration

**File**: `pyproject.toml`

```toml
[tool.ruff]
exclude = [
    "*.md", "node_modules", ".venv", "venv",
    "__pycache__", ".git", "build", "dist"
]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",      # Errors
    "W",      # Warnings
    "F",      # Pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "SIM",    # flake8-simplify
]

ignore = [
    "E501",   # Line too long (handled by formatter)
    "D",      # Skip pydocstyle for now
    "SIM105", # Suppress contextlib suggestions
    "N807",   # __init__ in docs examples
    "N802",   # PyQt6 method names
]
```

### Rule Categories

| Category | Code | Purpose | Examples |
|----------|------|---------|----------|
| Errors | E | PEP 8 errors | E501 (line length), E711 (None comparison) |
| Warnings | W | PEP 8 warnings | W291 (trailing whitespace) |
| Pyflakes | F | Logic errors | F401 (unused import), F841 (unused variable) |
| isort | I | Import ordering | I001 (import order) |
| pep8-naming | N | Naming conventions | N802 (function names), N806 (variable names) |
| pyupgrade | UP | Python version upgrades | UP032 (f-strings) |
| flake8-bugbear | B | Bug patterns | B006 (mutable defaults) |
| flake8-comprehensions | C4 | List/dict comprehensions | C416 (unnecessary dict comp) |
| flake8-simplify | SIM | Code simplification | SIM108 (ternary operator) |

---

### Execution Methods

#### 1. NPM Script
```json
{
  "scripts": {
    "lint": "ruff check .",
    "format": "ruff check . --fix"
  }
}
```

**Triggers**:
- `npm run lint` - Check only
- `npm run format` - Check and auto-fix

---

#### 2. Make Target
```makefile
lint:
    ruff check .

format:
    isort src tests --profile black
    ruff check . --fix
    black src tests
```

**Triggers**:
- `make lint` - Ruff check
- `make format` - Full formatting (isort + ruff + black)

---

#### 3. Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.20.0
    hooks:
      - id: ruff
        args: ["--fix"]
```

**Triggers**: Automatic on `git commit`

**Behavior**: Auto-fixes issues before commit

---

#### 4. GitHub Actions
```yaml
# .github/workflows/codex-deus-ultimate.yml
jobs:
  ruff-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: chartboost/ruff-action@v1
```

**Triggers**: Push, pull request

**Behavior**: Fail workflow on violations

---

### Auto-fix Behavior

**Fixable Rules**:
- Import sorting (I001)
- Unused imports (F401)
- Whitespace (W291, W293)
- Quote normalization
- f-string upgrades (UP032)

**Non-fixable** (require manual fix):
- Unused variables (F841)
- Logic errors (E711, E712)
- Naming violations (N802, N806)

---

### Integration Points

```
Ruff Configuration (pyproject.toml)
    ↓
Execution Triggers:
    ├─ npm run lint/format
    ├─ make lint/format
    ├─ pre-commit (auto on commit)
    └─ GitHub Actions (CI)
    ↓
Linting Results:
    ├─ stdout (violations)
    ├─ Exit code (0 = pass, 1 = fail)
    └─ Auto-fixes (if --fix flag)
    ↓
Actions on Failure:
    ├─ CI: Fail workflow
    ├─ Pre-commit: Block commit
    └─ NPM: Return error code
```

---

## 📋 ESLint (JavaScript/TypeScript Linting)

### Configuration

**Files**: 
- `.eslintrc.json` (root)
- `desktop/.eslintrc.json` (desktop app)
- `web/.eslintrc.json` (web app)

**Root Configuration**:
```json
{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": 12
  }
}
```

**Desktop Configuration** (Electron):
```json
{
  "env": {
    "browser": true,
    "node": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": 2021,
    "sourceType": "module"
  }
}
```

---

### Execution Methods

#### 1. Manual Execution
```bash
npx eslint .
npx eslint . --fix
```

**Scope**: All JavaScript files

**Fix**: `--fix` flag for auto-fixable issues

---

#### 2. GitHub Actions
```yaml
jobs:
  eslint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npx eslint .
```

**Triggers**: Push, pull request (JS file changes)

---

### Rule Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| Possible Errors | Prevent bugs | no-console, no-debugger |
| Best Practices | Code quality | eqeqeq, no-eval |
| Variables | Scope issues | no-unused-vars, no-undef |
| Stylistic | Code style | quotes, semi, indent |

---

### Integration Points

```
ESLint Configuration (.eslintrc.json)
    ↓
Execution Triggers:
    ├─ npx eslint (manual)
    └─ GitHub Actions (CI)
    ↓
Linting Results:
    ├─ stdout (violations)
    ├─ Exit code (0 = pass, 1 = fail)
    └─ Auto-fixes (if --fix)
    ↓
Actions on Failure:
    └─ CI: Fail workflow
```

---

## 📝 Markdownlint (Documentation Linting)

### Configuration

**File**: `config/editor/.markdownlint.json`

```json
{
  "default": true,
  "MD013": false,
  "MD033": false,
  "MD041": false
}
```

**Disabled Rules**:
- **MD013**: Line length (allow long lines in docs)
- **MD033**: Inline HTML (allow for complex formatting)
- **MD041**: First line heading (flexible for frontmatter)

---

### Execution Methods

#### 1. NPM Script
```json
{
  "scripts": {
    "lint:markdown": "markdownlint README.md PROGRAM_SUMMARY.md docs --config .markdownlint.json"
  }
}
```

**Triggers**: `npm run lint:markdown`

**Scope**: 
- README.md
- PROGRAM_SUMMARY.md
- docs/ directory

---

#### 2. GitHub Actions
```yaml
jobs:
  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: articulate/actions-markdownlint@v1
        with:
          config: .markdownlint.json
```

**Triggers**: Push, pull request (Markdown file changes)

---

### Common Rules

| Rule | Code | Description |
|------|------|-------------|
| Headings | MD001-MD006 | Heading structure, style |
| Lists | MD029-MD032 | List formatting, nesting |
| Code blocks | MD031, MD040 | Fenced code block style |
| Links | MD034, MD051 | Link formatting |
| Whitespace | MD009, MD010, MD012 | Trailing spaces, tabs |

---

### Integration Points

```
Markdownlint Configuration (.markdownlint.json)
    ↓
Execution Triggers:
    ├─ npm run lint:markdown
    └─ GitHub Actions (CI)
    ↓
Linting Results:
    ├─ stdout (violations)
    └─ Exit code (0 = pass, 1 = fail)
    ↓
Actions on Failure:
    └─ CI: Fail workflow
```

---

## 🔄 Linting Workflow Integration

### Pre-commit Chain
```
Git commit triggered
    ↓
Pre-commit hooks (.pre-commit-config.yaml)
    ├─ black (Python formatting)
    ├─ ruff (Python linting + auto-fix)
    ├─ isort (Import sorting)
    ├─ trailing-whitespace (Remove trailing spaces)
    ├─ end-of-file-fixer (Add EOF newline)
    ├─ check-yaml (Validate YAML)
    └─ detect-secrets (Secret scanning)
    ↓
All hooks pass?
    ├─ Yes → Commit proceeds
    └─ No → Commit blocked, violations shown
```

---

### CI Linting Chain
```
GitHub Actions triggered (push/PR)
    ↓
Codex Deus Ultimate (Phase 4: Code Quality)
    ├─ ruff-lint (Python)
    ├─ eslint (JavaScript)
    └─ markdownlint (Docs)
    ↓
All linters pass?
    ├─ Yes → Continue to testing phase
    └─ No → Workflow fails, violations reported
    ↓
Auto-fix Phase (if failures)
    ├─ Run ruff check . --fix
    ├─ Create auto-fix commit
    └─ Push to branch
```

---

### Make Formatting Chain
```
make format executed
    ↓
Sequential formatting:
    1. isort src tests --profile black
       └─ Sort imports (PEP 8 order)
    2. ruff check . --fix
       └─ Fix linting violations
    3. black src tests
       └─ Format code (PEP 8 style)
    ↓
All files formatted
```

---

## 📊 Linting Statistics

### Coverage Scope

| Language | Tool | Files Scanned | Rules Enforced |
|----------|------|---------------|----------------|
| Python | Ruff | ~200+ .py files | 100+ rules |
| JavaScript | ESLint | ~50+ .js files | 50+ rules |
| Markdown | Markdownlint | ~100+ .md files | 30+ rules |

### Execution Frequency

| Trigger | Frequency | Scope |
|---------|-----------|-------|
| Pre-commit | Per commit | Changed files only |
| GitHub Actions | Per push/PR | All files |
| Manual (npm) | On-demand | Specified files |
| Manual (make) | On-demand | All Python files |

---

## 🛡️ Linting vs. Formatting

### Linting (Ruff, ESLint)
- **Detects**: Logic errors, code smells, anti-patterns
- **Examples**: Unused variables, missing imports, incorrect types
- **Auto-fix**: Limited (safe fixes only)

### Formatting (Black, Prettier)
- **Detects**: Style violations
- **Examples**: Whitespace, line length, quote style
- **Auto-fix**: Comprehensive (all style issues)

### Relationship
```
Formatting (Black) → Linting (Ruff) → Type Checking (mypy)
     Style                Logic              Types
```

**Order Matters**: Format first, then lint, then type check

---

## 🔗 Configuration Relationships

### Ruff ↔ Black Compatibility
```toml
# pyproject.toml
[tool.ruff]
line-length = 88  # Match Black's default

[tool.black]
line-length = 88
```

**Ensures**: No conflicts between Ruff and Black

---

### Ruff ↔ isort Integration
```toml
[tool.ruff.lint]
select = ["I"]  # Enable isort rules
```

**Relationship**: Ruff can replace isort (but isort still used in make format)

---

### Pre-commit ↔ CI Consistency
```yaml
# .pre-commit-config.yaml
- repo: https://github.com/charliermarsh/ruff-pre-commit
  rev: v0.20.0  # Same version as CI

# .github/workflows/codex-deus-ultimate.yml
- uses: chartboost/ruff-action@v1
  with:
    version: 0.20.0  # Matches pre-commit
```

**Ensures**: Consistent linting locally and in CI

---

## 📈 Linting Performance

### Execution Times

| Tool | Scope | Time (typical) |
|------|-------|----------------|
| Ruff | Full codebase | < 2 seconds |
| ESLint | JavaScript files | 5-10 seconds |
| Markdownlint | All docs | 2-5 seconds |
| Black | Python formatting | 3-5 seconds |
| Pre-commit (all) | Changed files | 10-30 seconds |

### Comparison: Ruff vs. Traditional Tools

| Metric | Ruff | Flake8 + isort + pyupgrade |
|--------|------|----------------------------|
| Speed | 10-100x faster | Baseline |
| Rules | 100+ | 80+ (combined) |
| Auto-fix | Yes | Limited |
| Single tool | Yes | No (3 tools) |

**Advantage**: Ruff consolidates multiple tools, dramatically faster

---

## 🔍 Related Documentation

- **Pre-commit Hooks**: See `09_pre-commit-hooks.md`
- **Code Quality**: See `08_code-quality.md`
- **Automation Workflows**: See `04_automation-workflows.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
