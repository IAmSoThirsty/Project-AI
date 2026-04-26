---
title: Pre-commit Hooks Relationships
description: Git pre-commit automation chains and hook dependencies
tags:
  - relationships
  - pre-commit
  - git-hooks
  - automation
created: 2025-02-08
agent: AGENT-063
---

# Pre-commit Hooks Relationships

## Overview

Project-AI uses **pre-commit** framework to enforce code quality and security checks before every commit. Configured via `.pre-commit-config.yaml`.

---

## 🎯 Pre-commit Configuration

**File**: `.pre-commit-config.yaml`

**Purpose**: Automated code quality gates executed on `git commit`

---

## 📋 Hook Chain

### Complete Hook Sequence

```yaml
repos:
  1. black (Python formatting)
  2. ruff (Python linting)
  3. isort (Import sorting)
  4. pre-commit-hooks (Generic checks)
  5. detect-secrets (Secret scanning)
```

### Execution Order (Sequential)

```
Git commit triggered
    ↓
1. Black Formatting
    ├─ Format Python files (PEP 8)
    ├─ Fix whitespace, quotes, line length
    └─ Modify files in-place
    ↓
2. Ruff Linting
    ├─ Check Python code quality
    ├─ Auto-fix safe violations (--fix)
    └─ Report unfixable issues
    ↓
3. isort Import Sorting
    ├─ Sort Python imports
    ├─ Group by stdlib, third-party, local
    └─ Use black-compatible profile
    ↓
4. Generic Hooks (pre-commit-hooks)
    ├─ end-of-file-fixer → Add EOF newline
    ├─ trailing-whitespace → Remove trailing spaces
    ├─ check-yaml → Validate YAML syntax
    ├─ check-added-large-files → Block large files
    ├─ check-merge-conflict → Detect merge markers
    └─ mixed-line-ending → Fix CRLF/LF issues
    ↓
5. Secret Detection
    ├─ Scan for credentials, API keys
    ├─ Check against baseline (.secrets.baseline)
    └─ Block commit if secrets found
    ↓
All hooks passed?
    ├─ Yes → Commit proceeds
    └─ No → Commit blocked, fixes/errors shown
```

---

## 🔧 Hook Details

### 1. Black (Python Formatting)

**Repository**: `https://github.com/psf/black`

**Version**: `24.1.0`

**Configuration**:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11
```

**Behavior**:
- Formats Python files to PEP 8 style
- Line length: 88 (configured in `pyproject.toml`)
- Auto-fixes: Whitespace, quotes, indentation, line breaks

**Files Modified**: Yes (auto-formats in-place)

**Relationships**:
- **Configured by**: `pyproject.toml` [tool.black]
- **Runs before**: Ruff (formatting before linting)
- **Compatible with**: Ruff line-length settings

---

### 2. Ruff (Python Linting)

**Repository**: `https://github.com/charliermarsh/ruff-pre-commit`

**Version**: `v0.20.0`

**Configuration**:
```yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.20.0
    hooks:
      - id: ruff
        args: ["--fix"]
```

**Behavior**:
- Lints Python code (100+ rules)
- Auto-fixes: Unused imports, whitespace, import order
- Reports: Logic errors, naming violations

**Files Modified**: Yes (auto-fixes safe violations)

**Relationships**:
- **Configured by**: `pyproject.toml` [tool.ruff]
- **Runs after**: Black (lint formatted code)
- **Rules**: E, W, F, I, N, UP, B, C4, SIM

**Auto-fixable Rules**:
- F401: Unused imports
- I001: Import sorting
- W291: Trailing whitespace
- UP032: f-string upgrades

**Non-fixable Rules** (require manual fix):
- F841: Unused variables
- E711: None comparison (is vs ==)
- N802: Function naming

---

### 3. isort (Import Sorting)

**Repository**: `https://github.com/pre-commit/mirrors-isort`

**Version**: `v5.12.0`

**Configuration**:
```yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

**Behavior**:
- Sorts Python imports into groups:
  1. Standard library
  2. Third-party packages
  3. Local modules
- Uses black-compatible profile (no conflicts)

**Files Modified**: Yes (auto-sorts imports)

**Relationships**:
- **Profile**: black (compatible with Black formatting)
- **Runs after**: Ruff (though Ruff also does import sorting)
- **Alternative**: Ruff I001 rule (can replace isort)

---

### 4. Pre-commit Hooks (Generic Checks)

**Repository**: `https://github.com/pre-commit/pre-commit-hooks`

**Version**: `v4.5.0`

**Configuration**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: mixed-line-ending
```

#### Hook Breakdown

##### `end-of-file-fixer`
- **Purpose**: Ensure files end with newline
- **Modifies**: Yes (adds EOF newline)
- **Languages**: All text files

##### `trailing-whitespace`
- **Purpose**: Remove trailing whitespace
- **Modifies**: Yes (removes trailing spaces)
- **Languages**: All text files

##### `check-yaml`
- **Purpose**: Validate YAML syntax
- **Modifies**: No (validation only)
- **Fails on**: Invalid YAML

##### `check-added-large-files`
- **Purpose**: Block large file commits (> 500 KB default)
- **Modifies**: No (blocks commit)
- **Prevents**: Accidental large file commits

##### `check-merge-conflict`
- **Purpose**: Detect unresolved merge markers
- **Modifies**: No (detects only)
- **Fails on**: `<<<<<<<`, `=======`, `>>>>>>>`

##### `mixed-line-ending`
- **Purpose**: Fix CRLF/LF inconsistencies
- **Modifies**: Yes (normalizes line endings)
- **Platform**: Auto-detect (Windows vs Unix)

---

### 5. Detect Secrets

**Repository**: `https://github.com/Yelp/detect-secrets`

**Version**: `v1.4.0`

**Configuration**:
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json
```

**Behavior**:
- Scans for secrets (API keys, passwords, tokens)
- Checks against baseline (`.secrets.baseline`)
- Excludes: package-lock.json (high false-positive rate)

**Files Modified**: No (security check only)

**Detects**:
- AWS keys, Azure credentials
- Private keys (RSA, SSH)
- Generic high-entropy strings
- Hardcoded passwords

**Baseline**: `.secrets.baseline` - Known false positives

**Relationships**:
- **Baseline file**: `.secrets.baseline`
- **Excludes**: `package-lock.json`
- **Blocks**: Commits with secrets

---

## 🔄 Hook Execution Flow

### Normal Commit (All Pass)

```
$ git commit -m "Add feature"

Black............................................................Passed
Ruff.............................................................Passed
isort............................................................Passed
end-of-file-fixer................................................Passed
trailing-whitespace..............................................Passed
check-yaml.......................................................Passed
check-added-large-files..........................................Passed
check-merge-conflict.............................................Passed
mixed-line-ending................................................Passed
detect-secrets...................................................Passed

[main abc1234] Add feature
 3 files changed, 42 insertions(+), 12 deletions(-)
```

**Result**: Commit successful

---

### Commit with Auto-fixes

```
$ git commit -m "Add feature"

Black............................................................Failed
- hook id: black
- files were modified by this hook

Reformatted src/app/main.py
All done! ✨ 1 file reformatted.

Ruff.............................................................Failed
- hook id: ruff
- files were modified by this hook

Fixed 3 errors in src/app/main.py:
  - Removed unused import
  - Fixed import order
  - Removed trailing whitespace
```

**Result**: Commit blocked, files auto-fixed

**Next Steps**:
1. Review auto-fixes: `git diff`
2. Stage fixed files: `git add .`
3. Retry commit: `git commit -m "Add feature"`

---

### Commit with Unfixable Errors

```
$ git commit -m "Add feature"

Ruff.............................................................Failed
- hook id: ruff
- exit code: 1

src/app/main.py:42:5: F841 Local variable `unused_var` is assigned but never used
src/app/main.py:56:9: E711 Comparison to `None` should be `cond is None`
```

**Result**: Commit blocked, manual fixes required

**Next Steps**:
1. Fix errors manually
2. Stage fixes: `git add .`
3. Retry commit

---

### Commit with Secrets Detected

```
$ git commit -m "Add config"

detect-secrets...................................................Failed
- hook id: detect-secrets
- exit code: 1

Secret detected in .env:
  Line 5: OPENAI_API_KEY=sk-1234567890abcdef...
```

**Result**: Commit blocked, secret detected

**Next Steps**:
1. Remove secret from file
2. Add to `.secrets.baseline` (if false positive)
3. Use environment variables instead
4. Retry commit

---

## 🛠️ Hook Management

### Install Pre-commit

```bash
# Install pre-commit package
pip install pre-commit

# Install git hooks
pre-commit install
```

**Result**: Hooks installed in `.git/hooks/pre-commit`

---

### Run Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Run on staged files only (default)
pre-commit run
```

**Use Cases**:
- Test hook configuration
- Bulk formatting
- CI/CD integration

---

### Update Hook Versions

```bash
# Update to latest versions
pre-commit autoupdate

# Check for updates
pre-commit autoupdate --freeze
```

**Result**: Updates `.pre-commit-config.yaml` with new versions

---

### Skip Hooks (Emergency)

```bash
# Skip all hooks (use with caution!)
git commit -m "Fix" --no-verify

# Skip specific checks (use environment variable)
SKIP=black,ruff git commit -m "Fix"
```

**Warning**: Only use for emergency fixes, run hooks manually after

---

## 📊 Hook Statistics

### Execution Times (Typical)

| Hook | Changed Files | All Files | Modifies |
|------|--------------|-----------|----------|
| black | < 1s | 3-5s | Yes |
| ruff | < 1s | 2-3s | Yes |
| isort | < 1s | 2-3s | Yes |
| end-of-file-fixer | < 1s | 1-2s | Yes |
| trailing-whitespace | < 1s | 1-2s | Yes |
| check-yaml | < 1s | < 1s | No |
| check-added-large-files | < 1s | N/A | No |
| check-merge-conflict | < 1s | < 1s | No |
| mixed-line-ending | < 1s | 1-2s | Yes |
| detect-secrets | 1-2s | 5-10s | No |

**Total Time**: 
- Changed files only: 5-10 seconds
- All files (`--all-files`): 20-30 seconds

---

### Auto-fix Success Rate

| Hook | Auto-fixable | Success Rate |
|------|--------------|--------------|
| black | 100% | 100% |
| ruff | ~60% | ~95% |
| isort | 100% | 100% |
| end-of-file-fixer | 100% | 100% |
| trailing-whitespace | 100% | 100% |
| mixed-line-ending | 100% | 100% |

**Overall**: ~85% of issues auto-fixed

---

## 🔗 Integration Points

### Pre-commit ↔ CI/CD

```
Local Development:
  git commit → pre-commit hooks → auto-fix → commit

GitHub Actions (CI):
  push → Codex Deus → Phase 4 (Linting)
      ├─ ruff (same version)
      ├─ black (same version)
      └─ detect-secrets (same baseline)
```

**Consistency**: Same tool versions ensure local = CI

---

### Pre-commit ↔ Make

```bash
# Makefile
precommit:
    pre-commit run --all-files

format:
    isort src tests --profile black
    ruff check . --fix
    black src tests
```

**Relationship**: 
- `make precommit` = Run all hooks
- `make format` = Subset (formatting only)

---

### Pre-commit ↔ NPM

```json
{
  "scripts": {
    "precommit": "pre-commit run --all-files"
  }
}
```

**Alternative**: Can run pre-commit via npm

---

## 🛡️ Security & Safety

### Secret Protection Layers

1. **Pre-commit**: detect-secrets (local)
2. **GitHub Actions**: Secret scanning (remote)
3. **Baseline**: `.secrets.baseline` (known false positives)

**Defense in Depth**: Multiple layers prevent secrets in commits

---

### File Integrity

**Protected by**:
- `check-added-large-files`: Prevents bloat
- `check-merge-conflict`: Prevents broken merges
- `end-of-file-fixer`: Ensures POSIX compliance

---

## 📈 Best Practices

### 1. Run Before Commit
```bash
# Check before committing
pre-commit run --all-files

# Commit with confidence
git commit -m "Feature"
```

---

### 2. Update Regularly
```bash
# Monthly update check
pre-commit autoupdate
```

---

### 3. Review Auto-fixes
```bash
# After auto-fix, review changes
git diff

# Stage and commit
git add .
git commit -m "Feature"
```

---

### 4. Emergency Bypass (Rare)
```bash
# Only for critical hotfixes
git commit --no-verify -m "HOTFIX: Critical bug"

# Run hooks manually after
pre-commit run --all-files
git commit --amend
```

---

## 🔍 Related Documentation

- **Linting**: See `06_linting.md`
- **Code Quality**: See `08_code-quality.md`
- **Automation Workflows**: See `04_automation-workflows.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
