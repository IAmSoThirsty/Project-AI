# CI/CD Pipeline Architecture

**Document Type:** Technical Reference  
**Component:** Continuous Integration / Continuous Deployment  
**Status:** Production  
**Version:** 2.0.0  
**Last Updated:** 2025-01-26  
**Author:** AGENT-046  
**Audience:** DevOps Engineers, Platform Engineers, Release Managers  
**Scope:** GitHub Actions workflows, automated testing, security scanning, SBOM generation  
**Related Docs:**
- `02-docker-deployment-guide.md`
- `04-testing-infrastructure.md`
- `07-security-scanning.md`

---

## Table of Contents

1. [CI/CD Strategy Overview](#cicd-strategy-overview)
2. [Workflow Architecture](#workflow-architecture)
3. [Documentation Truth Gates](#documentation-truth-gates)
4. [SBOM Generation](#sbom-generation)
5. [Root Structure Enforcement](#root-structure-enforcement)
6. [Thirsty-Lang CI Pipeline](#thirsty-lang-ci-pipeline)
7. [Security Workflows](#security-workflows)
8. [Workflow Orchestration](#workflow-orchestration)
9. [Secrets Management](#secrets-management)
10. [Deployment Automation](#deployment-automation)
11. [Monitoring & Alerts](#monitoring--alerts)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## CI/CD Strategy Overview

### Philosophy and Principles

Project-AI implements a **multi-layered CI/CD strategy** with the following principles:

1. **Documentation First**: Code-documentation alignment verified before tests
2. **Security by Default**: Every commit scanned for vulnerabilities
3. **Shift-Left Testing**: Catch issues in development, not production
4. **Immutable Artifacts**: SBOM and security reports generated for every build
5. **Automated Compliance**: Regulatory requirements enforced via CI

**NOT a Traditional CI/CD Pipeline:**
- Governance checks run before tests (not after)
- Documentation truth gates enforce alignment
- Security scanning is blocking (not advisory)
- SBOM generation is mandatory (not optional)

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMMIT / PULL REQUEST                         │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────▼─────────┐
    │  Pre-Checks      │
    │  - Lint MD files │
    │  - Format check  │
    └────────┬─────────┘
             │
    ┌────────▼─────────────────────────────────────────┐
    │  Documentation Truth Gates                       │
    │  - Planned vs Implemented check                  │
    │  - Version consistency                           │
    │  - Archive index validation                      │
    │  - Link integrity                                │
    └────────┬─────────────────────────────────────────┘
             │
    ┌────────▼─────────┐
    │  SBOM Generation │
    │  - Python deps   │
    │  - Node.js deps  │
    │  - CycloneDX     │
    └────────┬─────────┘
             │
    ┌────────▼─────────────────────────┐
    │  Root Structure Enforcement      │
    │  - Required directories exist    │
    │  - README completeness           │
    │  - License file present          │
    └────────┬─────────────────────────┘
             │
    ┌────────▼─────────┐
    │  Build & Test    │
    │  - Unit tests    │
    │  - Integration   │
    │  - E2E tests     │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  Security Scan   │
    │  - Bandit        │
    │  - CodeQL        │
    │  - Trivy         │
    └────────┬─────────┘
             │
    ┌────────▼─────────┐
    │  Deploy          │
    │  - Docker build  │
    │  - Tag & push    │
    │  - Kubernetes    │
    └──────────────────┘
```

### Workflow Categories

| Category | Workflows | Trigger | Purpose |
|----------|-----------|---------|---------|
| **Documentation** | `doc-code-alignment.yml` | PR, Push, Weekly | Verify docs match code |
| **Compliance** | `generate-sbom.yml` | Dependency changes, Weekly | Generate SBOM |
| **Quality** | `enforce-root-structure.yml` | PR, Push | Enforce repo standards |
| **Build** | `thirsty-lang/ci.yml` | PR, Push | Build & test Thirsty-Lang |
| **Security** | `auto-security-fixes.yml`, `auto-bandit-fixes.yml` | Daily, PR | Scan for vulnerabilities |
| **Deployment** | `codex-deus-ultimate.yml` | Push to main | Deploy to production |

---

## Workflow Architecture

### GitHub Actions Structure

```
.github/
├── workflows/
│   ├── doc-code-alignment.yml          # Documentation truth gates
│   ├── generate-sbom.yml               # SBOM generation
│   ├── enforce-root-structure.yml      # Repository standards
│   ├── codex-deus-ultimate.yml         # God-tier deployment
│   ├── validate-metadata.yml           # Metadata validation
│   └── nextjs.yml                      # Next.js deployment
├── Monolith/                           # Archived workflows
│   ├── AUTO_PR_SYSTEM.md
│   ├── RED_TEAMING_FRAMEWORK.md
│   └── SECURITY_CHECKLIST.md
└── README.md                           # Workflow documentation
```

### Workflow Components

#### Triggers

```yaml
on:
  pull_request:
    paths:
      - '**.md'         # Markdown files
      - '**.py'         # Python files
      - 'tarl/**'       # TARL policies
  push:
    branches:
      - main
      - develop
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:      # Manual trigger
```

**Trigger Types:**
1. **Pull Request**: Run on code review
2. **Push**: Run on commit to main/develop
3. **Schedule**: Run periodically (cron syntax)
4. **Workflow Dispatch**: Manual execution

#### Jobs

```yaml
jobs:
  validate:
    name: Validate Documentation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run validation
        run: |
          python scripts/validate_docs.py
```

**Job Structure:**
- `name`: Human-readable job name
- `runs-on`: Runner environment (ubuntu-latest, macos-latest, windows-latest)
- `steps`: Sequential operations
- `needs`: Job dependencies
- `if`: Conditional execution

#### Actions

**Common Actions Used:**
```yaml
# Checkout repository
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history for diff

# Setup Python
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Setup Node.js
- uses: actions/setup-node@v4
  with:
    node-version: '18'
    cache: 'npm'

# Upload artifacts
- uses: actions/upload-artifact@v3
  with:
    name: sbom-files
    path: docs/security_compliance/sbom/
    retention-days: 90
```

---

## Documentation Truth Gates

### Purpose and Rationale

**Problem:** Documentation frequently becomes outdated as code evolves.

**Solution:** Automated gates that fail CI if:
- Documentation claims a feature is "planned" but it's already implemented
- Version numbers are inconsistent across files
- Archive files are missing from the index
- Internal links are broken

**File:** `.github/workflows/doc-code-alignment.yml`

### Workflow Configuration

```yaml
name: Documentation Truth Gates

on:
  pull_request:
    paths:
      - '**.md'
      - '**.py'
      - 'tarl/**'
      - 'src/thirsty_lang/**'
  push:
    branches:
      - main
      - develop
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  validate-doc-code-alignment:
    name: Validate Documentation-Code Alignment
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
```

### Validation Checks

#### 1. Planned vs Implemented Features

**Purpose:** Detect features marked as "planned" that are actually implemented.

```yaml
- name: Check for "planned" features with implementation
  continue-on-error: true
  run: |
    echo "🔍 Checking for 'planned' features that are actually implemented..."
    
    VIOLATIONS=0
    
    # Files to check
    DOC_FILES=(
      "src/thirsty_lang/docs/SPECIFICATION.md"
      "tarl/README.md"
      "docs/developer/tarl/TARL_README.md"
    )
    
    for doc in "${DOC_FILES[@]}"; do
      if [ ! -f "$doc" ]; then
        continue
      fi
      
      echo "Checking: $doc"
      
      # Look for "planned" or "not yet implemented" near feature keywords
      if grep -in "planned\|not yet implemented\|todo.*implement" "$doc" | grep -v "^#" | head -5; then
        echo "⚠️  Found 'planned' markers in $doc"
        echo "   → Verify these features are truly unimplemented"
      fi
    done
    
    echo "✅ Planned feature check complete"
```

**What It Checks:**
- Searches for "planned", "not yet implemented", "TODO: implement"
- Ignores commented lines (starting with #)
- Reports first 5 matches per file
- **Non-blocking:** Set to `continue-on-error: true`

**False Positives:**
- Roadmap documents (intentionally list future plans)
- Historical context ("this was planned but...")

#### 2. Version Consistency

**Purpose:** Ensure version numbers match across files.

```yaml
- name: Validate version consistency
  continue-on-error: true
  run: |
    echo "🔍 Validating version numbers across documentation..."
    
    # Extract versions from different files
    TARL_README_VERSION=$(grep -m 1 "Version.*[0-9]" tarl/README.md | grep -oP '\d+\.\d+\.\d+' || echo "not-found")
    TARL_CORE_VERSION=$(grep -m 1 "TARL_VERSION.*=.*[\"']" tarl/core.py | grep -oP '\d+\.\d+' || echo "not-found")
    TARL_SYSTEM_VERSION=$(grep -m 1 "VERSION.*=.*[\"']" tarl/system.py | grep -oP '\d+\.\d+\.\d+' || echo "not-found")
    
    echo "  TARL README version: $TARL_README_VERSION"
    echo "  TARL core.py version: $TARL_CORE_VERSION (Policy system)"
    echo "  TARL system.py version: $TARL_SYSTEM_VERSION (Language VM)"
    
    # Check pyproject.toml version
    if [ -f "pyproject.toml" ]; then
      PYPROJECT_VERSION=$(grep -m 1 '^version = ' pyproject.toml | grep -oP '\d+\.\d+\.\d+' || echo "not-found")
      echo "  pyproject.toml version: $PYPROJECT_VERSION"
    fi
    
    echo "✅ Version consistency check complete"
```

**What It Checks:**
- `tarl/README.md` - Documentation version
- `tarl/core.py` - TARL policy version
- `tarl/system.py` - TARL VM version
- `pyproject.toml` - Package version

**Note:** Intentionally different subsystems may have different versions.

#### 3. Implementation Documentation Check

**Purpose:** Ensure implemented features are documented.

```yaml
- name: Check for implemented features without "Implemented" tag
  continue-on-error: true
  run: |
    echo "🔍 Checking for implemented features not marked as such..."
    
    # Check Thirsty-Lang keywords in implementation vs docs
    IMPLEMENTED_KEYWORDS=()
    
    if [ -f "src/thirsty_lang/src/index.js" ]; then
      # Extract implemented keywords from code
      while IFS= read -r keyword; do
        IMPLEMENTED_KEYWORDS+=("$keyword")
      done < <(grep -oP "startsWith\(['\"](\w+)" src/thirsty_lang/src/index.js | cut -d"'" -f2 | cut -d'"' -f2 | sort -u)
      
      echo "Found ${#IMPLEMENTED_KEYWORDS[@]} implemented keywords in Thirsty-Lang"
      
      # Check if these are documented
      if [ -f "src/thirsty_lang/docs/SPECIFICATION.md" ]; then
        for keyword in "${IMPLEMENTED_KEYWORDS[@]}"; do
          if ! grep -q "$keyword" src/thirsty_lang/docs/SPECIFICATION.md; then
            echo "⚠️  Keyword '$keyword' implemented but not in SPECIFICATION.md"
          fi
        done
      fi
    fi
    
    echo "✅ Implementation documentation check complete"
```

**What It Checks:**
- Extracts keywords from JavaScript implementation
- Verifies each keyword is documented in SPECIFICATION.md
- Reports undocumented keywords

#### 4. Archive Index Validation

**Purpose:** Ensure archived documents are indexed.

```yaml
- name: Validate archive references
  run: |
    echo "🔍 Validating that archived docs are properly indexed..."
    
    # Check if ARCHIVE_INDEX.md exists
    if [ ! -f "docs/internal/archive/ARCHIVE_INDEX.md" ]; then
      echo "❌ ARCHIVE_INDEX.md is missing!"
      echo "   → Run: create docs/internal/archive/ARCHIVE_INDEX.md"
      exit 1
    fi
    
    # Count files in archive
    ARCHIVE_FILES=$(find docs/internal/archive -type f \( -name "*.md" -o -name "*.txt" \) | wc -l)
    INDEX_ENTRIES=$(grep -c "\.md\|\.txt" docs/internal/archive/ARCHIVE_INDEX.md || echo "0")
    
    echo "  Archive files: $ARCHIVE_FILES"
    echo "  Index entries: ~$INDEX_ENTRIES"
    
    if [ $ARCHIVE_FILES -gt $((INDEX_ENTRIES + 20)) ]; then
      echo "⚠️  Archive has significantly more files than index entries"
      echo "   → Consider updating ARCHIVE_INDEX.md"
    else
      echo "✅ Archive index appears current"
    fi
```

**What It Checks:**
- ARCHIVE_INDEX.md file exists
- Counts files in archive directory
- Compares file count to index entries
- Warns if >20 files are missing from index

**Blocking:** This check will fail CI if ARCHIVE_INDEX.md is missing.

#### 5. Link Integrity Check

**Purpose:** Detect broken internal links.

```yaml
- name: Check for common documentation issues
  run: |
    echo "🔍 Checking for common documentation issues..."
    
    ISSUES=0
    
    # Check for broken internal links (basic check)
    echo "Checking for potentially broken links..."
    while IFS= read -r file; do
      while IFS= read -r link; do
        # Extract file path from markdown link
        target=$(echo "$link" | sed -n 's/.*(\([^)]*\)).*/\1/p' | cut -d'#' -f1)
        
        # Skip external links
        if [[ "$target" =~ ^https?:// ]]; then
          continue
        fi
        
        # Skip if empty or anchor-only
        if [ -z "$target" ] || [[ "$target" =~ ^# ]]; then
          continue
        fi
        
        # Resolve relative path
        dir=$(dirname "$file")
        full_path="$dir/$target"
        
        if [ ! -f "$full_path" ] && [ ! -d "$full_path" ]; then
          echo "⚠️  Broken link in $file: $target"
          ISSUES=$((ISSUES + 1))
        fi
      done < <(grep -o '\[.*\](.*)'  "$file" | head -20)
    done < <(find docs -name "*.md" -type f | head -10)
    
    if [ $ISSUES -gt 0 ]; then
      echo "⚠️  Found $ISSUES potential link issues (sample check)"
    else
      echo "✅ No obvious link issues found (sample check)"
    fi
```

**What It Checks:**
- Extracts markdown links: `[text](path)`
- Resolves relative paths
- Skips external URLs and anchor links
- Verifies file/directory exists
- **Limited Scope:** Only checks first 10 markdown files, 20 links each

**Limitations:**
- Does not check anchor validity (`#section`)
- Does not validate external URLs
- Sample check (not exhaustive)

### Summary Report

```yaml
- name: Summary
  if: always()
  run: |
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "📊 DOCUMENTATION TRUTH GATES SUMMARY"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "✅ Planned vs Implemented check: COMPLETE"
    echo "✅ Version consistency check: COMPLETE"  
    echo "✅ Implementation documentation check: COMPLETE"
    echo "✅ Archive index validation: COMPLETE"
    echo "✅ Common issues check: COMPLETE"
    echo ""
    echo "Documentation alignment validation finished."
    echo "Review warnings above for potential improvements."
    echo "═══════════════════════════════════════════════════════════"
```

**Always Runs:** `if: always()` ensures summary is printed even if previous steps fail.

---

## SBOM Generation

### Purpose and Compliance

**Software Bill of Materials (SBOM)** is a machine-readable inventory of all software dependencies. Required for:

1. **Supply Chain Security**: Track dependency vulnerabilities
2. **Regulatory Compliance**: Executive Order 14028, EU Cyber Resilience Act
3. **License Compliance**: Identify license obligations
4. **Incident Response**: Quickly identify affected systems

**File:** `.github/workflows/generate-sbom.yml`

### Workflow Configuration

```yaml
name: Generate SBOM (Software Bill of Materials)

on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'requirements.txt'
      - 'requirements-dev.txt'
      - 'package.json'
      - 'pyproject.toml'
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM UTC
  workflow_dispatch:  # Manual trigger

permissions:
  contents: write
  security-events: write
```

**Triggers:**
- Dependency file changes (requirements.txt, package.json, pyproject.toml)
- Weekly schedule (Monday 2 AM UTC)
- Manual dispatch

**Permissions:**
- `contents: write` - Commit SBOM files
- `security-events: write` - Upload to GitHub Security tab

### Python SBOM Generation

```yaml
jobs:
  generate-python-sbom:
    name: Generate Python Dependencies SBOM
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install cyclonedx-bom
        run: |
          pip install cyclonedx-bom
      
      - name: Generate CycloneDX SBOM for Python
        run: |
          mkdir -p docs/security_compliance/sbom
          
          echo "📦 Generating Python SBOM..."
          if [ ! -f requirements.txt ]; then
            echo "⚠️  requirements.txt not found, skipping Python SBOM"
            exit 0
          fi
          
          cyclonedx-py requirements \
            --requirements-file requirements.txt \
            --output-format json \
            --output-file docs/security_compliance/sbom/python-sbom.json || {
            echo "⚠️  Failed to generate Python SBOM, but continuing..."
            exit 0
          }
          
          # Also generate XML format
          if [ -f requirements.txt ]; then
            cyclonedx-py requirements \
              --requirements-file requirements.txt \
              --output-format xml \
              --output-file docs/security_compliance/sbom/python-sbom.xml || true
          fi
          
          echo "✅ Python SBOM generated"
```

**CycloneDX Tool:**
- Industry-standard SBOM format (OWASP)
- Supports JSON and XML output
- Includes component metadata (name, version, license, hashes)

**Output Files:**
- `docs/security_compliance/sbom/python-sbom.json`
- `docs/security_compliance/sbom/python-sbom.xml`
- `docs/security_compliance/sbom/python-dev-sbom.json`

### Node.js SBOM Generation

```yaml
generate-nodejs-sbom:
  name: Generate Node.js Dependencies SBOM
  runs-on: ubuntu-latest
  if: hashFiles('package.json') != ''
  
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
    
    - name: Install cyclonedx-npm
      run: |
        npm install -g @cyclonedx/cyclonedx-npm
    
    - name: Generate CycloneDX SBOM for Node.js
      run: |
        mkdir -p docs/security_compliance/sbom
        
        echo "📦 Generating Node.js SBOM..."
        cyclonedx-npm \
          --output-file docs/security_compliance/sbom/nodejs-sbom.json \
          --output-format JSON
        
        echo "✅ Node.js SBOM generated"
```

**Conditional Execution:** `if: hashFiles('package.json') != ''` - Only runs if `package.json` exists.

### SBOM Metadata

```yaml
- name: Add SBOM metadata
  run: |
    cat > docs/security_compliance/sbom/README.md << 'EOF'
# Software Bill of Materials (SBOM)

**Last Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")  
**Format**: CycloneDX 1.4+

## Purpose

This directory contains machine-readable Software Bill of Materials (SBOM) files for Project-AI dependencies. These files enable:

- **Supply chain security**: Track all dependencies and their versions
- **Vulnerability scanning**: Automated security analysis
- **License compliance**: Track dependency licenses
- **Audit trail**: Historical record of dependency changes

## Files

### Python Dependencies

- `python-sbom.json` - Production Python dependencies (CycloneDX JSON)
- `python-sbom.xml` - Production Python dependencies (CycloneDX XML)
- `python-dev-sbom.json` - Development Python dependencies

### Node.js Dependencies

- `nodejs-sbom.json` - Node.js dependencies (if applicable)

## Verification

To verify the SBOM:

\`\`\`bash
# Install CycloneDX CLI
npm install -g @cyclonedx/cyclonedx-cli

# Validate SBOM
cyclonedx validate --input-file python-sbom.json
\`\`\`

## Update Frequency

SBOMs are automatically regenerated:
- On dependency file changes (requirements.txt, package.json)
- Weekly (Monday 2 AM UTC)
- On manual workflow trigger

## Standards Compliance

- **Format**: CycloneDX 1.4+ (OWASP standard)
- **Alternative**: SPDX format available on request
- **Specification**: https://cyclonedx.org/specification/overview/

## Integration

SBOMs can be ingested by:
- Dependency-Track (https://dependencytrack.org/)
- GitHub Dependency Graph
- Third-party security scanning tools

---

**Maintained by**: Automated CI workflow  
**Contact**: security@project-ai.dev
EOF
    
    echo "✅ SBOM README created"
```

### Committing SBOMs

```yaml
- name: Commit SBOM files
  if: github.event_name != 'pull_request'
  run: |
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    
    git add docs/security_compliance/sbom/
    
    if git diff --staged --quiet; then
      echo "No changes to SBOM files"
    else
      git commit -m "chore: Update SBOM files [automated]"
      git push
      echo "✅ SBOM files committed"
    fi
```

**Protection:** Only commits on push events, not PRs (prevents conflicts).

---

## Root Structure Enforcement

### Purpose

**Problem:** Inconsistent repository structure makes navigation difficult.

**Solution:** Automated checks that verify:
- Required directories exist (docs/, src/, tests/, scripts/)
- README.md is complete with all required sections
- LICENSE file is present
- .gitignore covers common patterns

**File:** `.github/workflows/enforce-root-structure.yml`

### Required Directories

```yaml
- name: Check required directories
  run: |
    REQUIRED_DIRS=(
      "src"
      "tests"
      "docs"
      "scripts"
      ".github/workflows"
      "data"
    )
    
    MISSING=()
    
    for dir in "${REQUIRED_DIRS[@]}"; do
      if [ ! -d "$dir" ]; then
        MISSING+=("$dir")
      fi
    done
    
    if [ ${#MISSING[@]} -gt 0 ]; then
      echo "❌ Missing required directories:"
      printf '   - %s\n' "${MISSING[@]}"
      exit 1
    else
      echo "✅ All required directories present"
    fi
```

### README Completeness

```yaml
- name: Check README completeness
  run: |
    REQUIRED_SECTIONS=(
      "## Installation"
      "## Usage"
      "## Features"
      "## Contributing"
      "## License"
    )
    
    MISSING=()
    
    for section in "${REQUIRED_SECTIONS[@]}"; do
      if ! grep -q "$section" README.md; then
        MISSING+=("$section")
      fi
    done
    
    if [ ${#MISSING[@]} -gt 0 ]; then
      echo "⚠️  README.md missing sections:"
      printf '   - %s\n' "${MISSING[@]}"
    else
      echo "✅ README.md contains all required sections"
    fi
```

**Non-Blocking:** Missing sections are warnings, not errors.

---

## Thirsty-Lang CI Pipeline

### Build and Test Pipeline

**File:** `src/thirsty_lang/.github/workflows/ci.yml`

```yaml
name: Thirsty-lang CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [14.x, 16.x, 18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    
    - name: Install dependencies
      run: npm install
    
    - name: Run tests
      run: npm test
    
    - name: Run linter
      run: node src/linter.js examples/*.thirsty || true
    
    - name: Check formatting
      run: node src/formatter.js examples/hello.thirsty --check || true
```

**Matrix Strategy:** Tests across Node.js 14, 16, 18, and 20.

### Build and Package

```yaml
build:
  name: Build & Package
  runs-on: ubuntu-latest
  needs: test
  
  steps:
  - uses: actions/checkout@v3
  
  - name: Setup Node.js
    uses: actions/setup-node@v3
    with:
      node-version: '18.x'
  
  - name: Install dependencies
    run: npm install
  
  - name: Build package
    run: npm run build
  
  - name: Archive artifacts
    uses: actions/upload-artifact@v3
    with:
      name: thirsty-lang-build
      path: |
        src/
        examples/
        docs/
        package.json
        README.md
```

**Dependency:** `needs: test` ensures tests pass before building.

### Documentation Deployment

```yaml
docs:
  name: Generate Documentation
  runs-on: ubuntu-latest
  
  steps:
  - uses: actions/checkout@v3
  
  - name: Setup Node.js
    uses: actions/setup-node@v3
    with:
      node-version: '18.x'
  
  - name: Generate docs
    run: |
      node src/doc-generator.js examples/hello.thirsty docs/auto-generated
  
  - name: Deploy to GitHub Pages
    if: github.ref == 'refs/heads/main'
    uses: peaceiris/actions-gh-pages@v3
    with:
      github_token: ${{ secrets.GITHUB_TOKEN }}
      publish_dir: ./docs/auto-generated
```

**Conditional Deployment:** Only deploys to GitHub Pages on pushes to `main`.

---

## Security Workflows

### Automated Security Scanning

Project-AI has multiple security workflows (documented separately):

1. **Bandit** - Python security linter
2. **CodeQL** - Semantic code analysis
3. **Trivy** - Container vulnerability scanner
4. **pip-audit** - Python dependency scanner

**See:** `07-security-scanning.md` for detailed documentation.

### Auto Security Fixes Workflow

**File:** `.github/workflows/auto-security-fixes.yml`

**Features:**
- Daily scheduled scans
- Automatic issue creation for vulnerabilities
- Auto-fix PRs for known vulnerabilities
- SARIF upload to GitHub Security tab

**Triggers:**
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:
```

---

## Workflow Orchestration

### Codex Deus Ultimate Workflow

**File:** `.github/workflows/codex-deus-ultimate.yml`

**Purpose:** God-tier deployment orchestration (86KB configuration).

**Features:**
- Multi-stage deployment pipeline
- Environment-specific configurations
- Automated rollback on failure
- Slack/Discord notifications
- Comprehensive error handling

**Size:** 86.4 KB (too large to view in one go).

**View Sections:**
```bash
# View first 100 lines
head -n 100 .github/workflows/codex-deus-ultimate.yml

# Search for specific jobs
grep -n "jobs:" .github/workflows/codex-deus-ultimate.yml

# Extract job names
yq eval '.jobs | keys' .github/workflows/codex-deus-ultimate.yml
```

---

## Secrets Management

### GitHub Secrets

**Required Secrets:**
```yaml
secrets:
  OPENAI_API_KEY:
    description: "OpenAI API key for AI services"
    required: true
  
  DEEPSEEK_API_KEY:
    description: "DeepSeek API key (optional)"
    required: false
  
  SLACK_WEBHOOK_URL:
    description: "Slack webhook for notifications"
    required: false
  
  DOCKER_HUB_TOKEN:
    description: "Docker Hub access token"
    required: true
  
  KUBECONFIG:
    description: "Kubernetes cluster config"
    required: true
```

**Setting Secrets:**
```bash
# Via GitHub CLI
gh secret set OPENAI_API_KEY

# Via GitHub UI
# Settings → Secrets and variables → Actions → New repository secret
```

### Secret Scanning

**GitHub Secret Scanning:**
- Automatically detects committed secrets
- Sends alerts to repository admins
- Supports 200+ secret patterns

**Prevention:**
```bash
# Use git-secrets to prevent commits
git secrets --install
git secrets --register-aws
```

---

## Deployment Automation

### Deployment Strategies

#### 1. Manual Deployment

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production
      version:
        description: 'Version to deploy'
        required: true
```

#### 2. Automatic Deployment

```yaml
on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'

jobs:
  deploy:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/web-backend \
            web-backend=projectai/web-backend:${{ github.ref_name }}
```

### Environment Protection

```yaml
jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.projectai.example.com
    
    steps:
      - name: Deploy
        run: |
          echo "Deploying to production..."
```

**Protection Rules:**
- Required reviewers (2+ approvals)
- Wait timer (10 minutes)
- Restricted branches (main only)

---

## Monitoring & Alerts

### Workflow Status Notifications

```yaml
- name: Notify on success
  if: success()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{
        "text": "✅ Deployment successful",
        "blocks": [{
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Deployment Status: Success*\n\nCommit: `${{ github.sha }}`\nEnvironment: `production`"
          }
        }]
      }'

- name: Notify on failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{
        "text": "❌ Deployment failed",
        "blocks": [{
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Deployment Status: Failure*\n\nCommit: `${{ github.sha }}`\nCheck logs: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
          }
        }]
      }'
```

### Metrics Collection

```yaml
- name: Collect deployment metrics
  run: |
    echo "deployment_time_seconds $SECONDS" >> metrics.txt
    echo "commit_sha ${{ github.sha }}" >> metrics.txt
    
    # Send to Prometheus Pushgateway
    cat metrics.txt | curl --data-binary @- \
      http://pushgateway:9091/metrics/job/github-actions
```

---

## Best Practices

### 1. Workflow Organization

✅ **DO:**
- Use descriptive job and step names
- Group related workflows in subdirectories
- Document workflow purpose in comments
- Use matrix builds for multi-version testing
- Cache dependencies to speed up builds

❌ **DON'T:**
- Create monolithic workflows (>1000 lines)
- Hard-code secrets in workflow files
- Run workflows on every commit (use path filters)
- Skip security scanning to save time

### 2. Performance Optimization

✅ **DO:**
```yaml
# Cache dependencies
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# Conditional execution
- name: Run expensive test
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  run: npm run test:integration

# Parallel jobs
jobs:
  lint:
    runs-on: ubuntu-latest
  test:
    runs-on: ubuntu-latest
  security:
    runs-on: ubuntu-latest
```

### 3. Error Handling

✅ **DO:**
```yaml
- name: Deploy
  run: |
    set -e  # Exit on error
    set -u  # Exit on undefined variable
    set -o pipefail  # Exit on pipe failure
    
    kubectl apply -f deployment.yaml
  continue-on-error: false
  
- name: Rollback on failure
  if: failure()
  run: |
    kubectl rollout undo deployment/web-backend
```

---

## Troubleshooting

### Common Issues

#### 1. Workflow Not Triggering

**Symptom:** Push to main doesn't trigger workflow.

**Diagnosis:**
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'src/**'  # Too restrictive?
```

**Solution:** Remove path filters or add missing paths.

#### 2. Permission Denied

**Symptom:** `Error: Resource not accessible by integration`

**Solution:**
```yaml
permissions:
  contents: write      # Required for git push
  pull-requests: write  # Required for PR comments
  security-events: write  # Required for SARIF upload
```

#### 3. Secrets Not Available

**Symptom:** `Error: Secret OPENAI_API_KEY not found`

**Diagnosis:**
```bash
# Check if secret is set
gh secret list

# View workflow run logs
gh run view <run-id> --log
```

**Solution:**
- Ensure secret is set at repository/organization level
- Check secret name matches exactly (case-sensitive)
- Verify environment matches (production vs staging)

#### 4. Timeout

**Symptom:** Workflow times out after 6 hours.

**Solution:**
```yaml
jobs:
  long-running:
    timeout-minutes: 360  # Set explicit timeout (6 hours max)
```

---

## Summary

**CI/CD Strategy:**
- ✅ Documentation-first validation
- ✅ Automated SBOM generation
- ✅ Multi-layered security scanning
- ✅ Repository structure enforcement
- ✅ Deployment automation with rollback

**Key Workflows:**
- `doc-code-alignment.yml` - Documentation truth gates
- `generate-sbom.yml` - Supply chain security
- `enforce-root-structure.yml` - Repository standards
- `ci.yml` - Build and test Thirsty-Lang
- `codex-deus-ultimate.yml` - God-tier deployment

**Production Readiness:**
- 5+ active workflows
- Daily security scans
- Weekly SBOM updates
- Automated compliance checks
- Environment protection rules

**Next Steps:**
- Review `04-testing-infrastructure.md` for test strategies
- See `07-security-scanning.md` for vulnerability detection
- Check `06-deployment-strategies.md` for rollout patterns

---

**Document Metadata:**
- **Word Count:** 5,984 words
- **Code Examples:** 42
- **Workflow Files:** 7
- **Diagrams:** 1
- **Last Reviewed:** 2025-01-26
- **Next Review:** 2025-04-26

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

