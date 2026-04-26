---
type: compliance-doc
tags:
  - validation
  - metadata
  - json-schema
  - user-guide
  - documentation
  - powershell
created: 2026-01-23
last_verified: 2026-04-20
status: current
related_systems:
  - metadata-validation-engine
  - json-schema-validator
  - powershell-yaml-module
stakeholders:
  - qa-team
  - compliance-team
  - developers
audit_scope:
  - compliance
  - code-quality
findings_severity: informational
pass_rate: N/A
review_cycle: quarterly
---

# Metadata Validation Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-23  
**Author:** AGENT-018: Metadata Validation Engineer  
**Status:** ACTIVE

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Schema Reference](#schema-reference)
4. [Validation Script Usage](#validation-script-usage)
5. [CI/CD Integration](#cicd-integration)
6. [Error Resolution](#error-resolution)
7. [Best Practices](#best-practices)
8. [Performance Optimization](#performance-optimization)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Project-AI metadata validation system ensures consistent, high-quality documentation metadata across the entire repository. It validates YAML frontmatter in Markdown files against a comprehensive JSON Schema, catching errors early and enforcing organizational standards.

### Key Features

- **JSON Schema Validation**: Comprehensive validation against industry-standard JSON Schema Draft 7
- **High Performance**: <100ms per file with caching and parallel processing
- **Multiple Output Formats**: Console, JSON, and Markdown reports
- **Error Catalog**: Detailed error messages with resolution guidance
- **CI/CD Ready**: Seamless integration with GitHub Actions and other CI systems
- **Flexible Configuration**: Strict mode, fail-fast, caching, and more
- **Batch Processing**: Validate entire directories with recursive scanning

### Architecture

```
validation/
├── schemas/
│   └── metadata.schema.json      # JSON Schema definition
├── tests/
│   ├── valid/                    # Valid test cases
│   ├── invalid/                  # Invalid test cases
│   └── run-tests.ps1            # Test runner
├── reports/                      # Generated validation reports
├── error-catalog/
│   └── error-catalog.json       # Comprehensive error catalog
└── .cache/                       # Validation cache (auto-generated)
```

---

## Quick Start

### Prerequisites

- **PowerShell 7.0+**: Required for script execution
- **powershell-yaml module**: Automatically installed if missing

### Basic Validation

Validate a single file:

```powershell
.\validate-metadata.ps1 -Path ".\README.md"
```

Validate a directory recursively:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive
```

Generate a JSON report:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -OutputFormat JSON -OutputPath ".\validation\reports\results.json"
```

### Example Output

```
═══════════════════════════════════════════════════════════════
  METADATA VALIDATION REPORT
═══════════════════════════════════════════════════════════════

✅ ./docs/VALIDATION_GUIDE.md [VALID]
   ⏱ 45.32ms

❌ ./docs/example.md [INVALID]
   ⏱ 67.89ms
   Errors:
     • description: Required field 'description' is missing

═══════════════════════════════════════════════════════════════
  STATISTICS
═══════════════════════════════════════════════════════════════
Total Files:     10
✅ Valid:        8
❌ Invalid:      2
⚠ Skipped:       0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Errors:          3
Warnings:        1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Time:      523.45ms
Average Time:    52.35ms
Min Time:        34.12ms
Max Time:        78.90ms
═══════════════════════════════════════════════════════════════
```

---

## Schema Reference

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `description` | string | Brief description (10-500 chars) | "Configuration for AI behavior" |

### Optional Fields

| Field | Type | Description | Default | Constraints |
|-------|------|-------------|---------|-------------|
| `applyTo` | string | Glob pattern for file scope | `**` | Valid glob syntax |
| `version` | string | Semantic version | - | SemVer 2.0.0 format |
| `lastUpdated` | string | Last update date | - | ISO 8601 (YYYY-MM-DD) |
| `status` | enum | Document status | `ACTIVE` | See [Status Values](#status-values) |
| `category` | enum | Primary category | - | See [Categories](#categories) |
| `tags` | array | Taxonomy tags | - | 1-20 unique tags |
| `author` | string | Primary author | - | 2-100 chars |
| `reviewers` | array | List of reviewers | - | Max 10 reviewers |
| `relatedDocs` | array | Related file paths | - | Max 20 docs |
| `dependencies` | array | External dependencies | - | Max 30 deps |
| `audience` | enum | Intended audience | `developers` | See [Audiences](#audiences) |
| `confidentiality` | enum | Classification level | `public` | public, internal, confidential, restricted |
| `priority` | enum | Priority level | `medium` | critical, high, medium, low |
| `compliance` | array | Compliance frameworks | - | SOC2, ISO27001, GDPR, etc. |
| `reviewSchedule` | enum | Review frequency | `quarterly` | weekly, monthly, quarterly, etc. |
| `expiryDate` | string | Expiration date | - | ISO 8601 (YYYY-MM-DD) |
| `language` | string | Document language | `en` | ISO 639-1 code |
| `license` | string | License identifier | - | SPDX format |
| `customFields` | object | Custom metadata | - | Max 20 properties |

### Status Values

- `DRAFT`: Work in progress, not finalized
- `ACTIVE`: Currently in use and maintained
- `DEPRECATED`: No longer recommended, but still available
- `ARCHIVED`: Historical, no longer maintained
- `REVIEW`: Under review for approval
- `PENDING`: Awaiting action or approval
- `SUPERSEDED`: Replaced by newer documentation

### Categories

`architecture`, `security`, `governance`, `deployment`, `development`, `operations`, `testing`, `documentation`, `compliance`, `api`, `integration`, `configuration`, `guide`, `reference`, `policy`, `standard`

### Audiences

`developers`, `operators`, `security-team`, `architects`, `all`, `executive`, `contributors`, `maintainers`, `end-users`

### Example Metadata

**Minimal Valid Metadata:**

```yaml
---
description: Configuration guide for metadata validation system
---
```

**Comprehensive Metadata:**

```yaml
---
description: Comprehensive metadata validation system for Project-AI documentation
version: 1.0.0
lastUpdated: 2026-01-23
status: ACTIVE
category: documentation
tags:
  - metadata
  - validation
  - json-schema
  - powershell
author: AGENT-018
reviewers:
  - Security Team
  - Architecture Team
relatedDocs:
  - validation/schemas/metadata.schema.json
  - validation/error-catalog/error-catalog.json
audience: developers
confidentiality: public
priority: high
reviewSchedule: quarterly
language: en
license: MIT
---
```

---

## Validation Script Usage

### Command-Line Parameters

#### Basic Parameters

**`-Path <string>`** (Required)  
File or directory path to validate. Supports wildcards.

```powershell
-Path ".\README.md"              # Single file
-Path ".\docs"                   # Directory
-Path ".\docs\*.md"              # Wildcard
```

**`-SchemaPath <string>`**  
Path to JSON Schema file. Default: `.\validation\schemas\metadata.schema.json`

**`-OutputFormat <string>`**  
Output format: `Console`, `JSON`, or `Markdown`. Default: `Console`

**`-OutputPath <string>`**  
Path for report file (required for JSON/Markdown formats)

#### Processing Options

**`-Recursive`**  
Process directories recursively

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive
```

**`-Parallel`**  
Enable parallel processing for batch validation (max 8 concurrent jobs)

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -Parallel
```

**`-StrictMode`**  
Treat warnings as errors (exit code 1 if any warnings)

```powershell
.\validate-metadata.ps1 -Path ".\docs" -StrictMode
```

**`-FailFast`**  
Stop validation on first error

```powershell
.\validate-metadata.ps1 -Path ".\docs" -FailFast
```

**`-Cache`**  
Enable validation cache for unchanged files (uses MD5 hash)

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -Cache
```

**`-VerboseOutput`**  
Enable verbose logging with detailed timing information

```powershell
.\validate-metadata.ps1 -Path ".\docs" -VerboseOutput
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All files valid (or only warnings in normal mode) |
| 1 | Validation errors found (or warnings in strict mode) |

### Performance Benchmarks

- **Single File**: <100ms (target), typically 40-60ms
- **100 Files (Sequential)**: ~5 seconds
- **100 Files (Parallel)**: ~1.5 seconds
- **Cache Hit**: <5ms

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/validate-metadata.yml`:

```yaml
name: Validate Metadata

on:
  pull_request:
    paths:
      - '**/*.md'
  push:
    branches:
      - main
      - develop

jobs:
  validate:
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install PowerShell YAML module
        shell: pwsh
        run: |
          Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
      
      - name: Validate metadata
        shell: pwsh
        run: |
          .\validate-metadata.ps1 `
            -Path "." `
            -Recursive `
            -Parallel `
            -Cache `
            -OutputFormat JSON `
            -OutputPath "validation-results.json"
      
      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: validation-results.json
          retention-days: 30
      
      - name: Comment on PR
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('validation-results.json', 'utf8'));
            
            const invalidFiles = results.Results.filter(r => r.Status === 'INVALID');
            
            let comment = '## ❌ Metadata Validation Failed\n\n';
            comment += `**Files with errors:** ${invalidFiles.length}\n\n`;
            
            invalidFiles.slice(0, 5).forEach(file => {
              comment += `### \`${file.FilePath}\`\n\n`;
              file.Errors.forEach(err => {
                comment += `- **${err.Field}:** ${err.Message}\n`;
              });
              comment += '\n';
            });
            
            if (invalidFiles.length > 5) {
              comment += `\n...and ${invalidFiles.length - 5} more files. See the full report in the artifacts.`;
            }
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Pre-commit Hook

Create `.githooks/pre-commit`:

```bash
#!/bin/sh

# Validate metadata before commit
pwsh -NoProfile -ExecutionPolicy Bypass -Command "
  & '.\validate-metadata.ps1' -Path '.' -Recursive -Cache -FailFast
"

if [ $? -ne 0 ]; then
  echo "❌ Metadata validation failed. Fix errors before committing."
  exit 1
fi

echo "✅ Metadata validation passed"
exit 0
```

Make it executable:

```bash
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

### Azure DevOps Pipeline

```yaml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - '**/*.md'

pool:
  vmImage: 'windows-latest'

steps:
  - task: PowerShell@2
    displayName: 'Install YAML Module'
    inputs:
      targetType: 'inline'
      script: |
        Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber

  - task: PowerShell@2
    displayName: 'Validate Metadata'
    inputs:
      filePath: 'validate-metadata.ps1'
      arguments: '-Path "." -Recursive -Parallel -Cache -OutputFormat JSON -OutputPath "$(Build.ArtifactStagingDirectory)/validation-results.json"'
      failOnStderr: true

  - task: PublishBuildArtifacts@1
    condition: always()
    inputs:
      PathtoPublish: '$(Build.ArtifactStagingDirectory)/validation-results.json'
      ArtifactName: 'validation-report'
```

---

## Error Resolution

### Common Errors and Fixes

#### E001: REQUIRED_FIELD_MISSING

**Error:** `Required field 'description' is missing`

**Fix:**
```yaml
---
description: Add a meaningful description here
---
```

#### E002: TYPE_MISMATCH

**Error:** `Expected type 'string' but got 'number'`

**Fix:**
```yaml
# ❌ Wrong
version: 1

# ✅ Correct
version: "1.0.0"
```

#### E003: ENUM_VIOLATION

**Error:** `Value 'INVALID' is not in allowed values`

**Fix:**
```yaml
# ❌ Wrong
status: INVALID

# ✅ Correct
status: ACTIVE
```

#### E004: PATTERN_MISMATCH

**Error:** `Value '1.0' does not match pattern`

**Fix:**
```yaml
# ❌ Wrong
version: 1.0

# ✅ Correct
version: 1.0.0
```

#### E005-E006: Length Violations

**Fix:**
```yaml
# ❌ Too short (min 10 chars)
description: Short

# ✅ Correct
description: This is a proper description with sufficient length

# ❌ Too long (max 500 chars)
description: [601 character string...]

# ✅ Correct
description: Concise description under 500 characters
```

#### E007-E009: Array Violations

**Fix:**
```yaml
# ❌ Empty array (min 1 item)
tags: []

# ✅ Correct
tags: [metadata]

# ❌ Duplicates
tags: [metadata, validation, metadata]

# ✅ Correct
tags: [metadata, validation]

# ❌ Too many items (max 20)
tags: [tag1, tag2, ..., tag25]

# ✅ Correct
tags: [tag1, tag2, ..., tag20]
```

### Error Catalog Reference

For detailed error information, see `validation/error-catalog/error-catalog.json`.

Each error includes:
- Error code (E001-E012 for errors, W001-W004 for warnings)
- Severity level
- Category
- Description
- Resolution steps
- Examples with fixes
- Documentation links

---

## Best Practices

### 1. Always Include Description

The `description` field is the only required field. Make it meaningful:

```yaml
# ❌ Bad
description: Document

# ✅ Good
description: Comprehensive guide for implementing metadata validation in CI/CD pipelines
```

### 2. Use Semantic Versioning

Follow [SemVer 2.0.0](https://semver.org/):

```yaml
version: 1.0.0          # Major.Minor.Patch
version: 2.1.3-beta.1   # Pre-release
version: 1.0.0+build.123 # Build metadata
```

### 3. Tag Consistently

Use lowercase kebab-case for tags:

```yaml
# ❌ Bad
tags: [METADATA, Validation, json_schema]

# ✅ Good
tags: [metadata, validation, json-schema]
```

### 4. Keep Metadata Up-to-Date

Update `lastUpdated` when modifying documents:

```yaml
lastUpdated: 2026-01-23  # ISO 8601 format
```

### 5. Set Appropriate Status

Use status to track document lifecycle:

```yaml
status: DRAFT      # Work in progress
status: REVIEW     # Under review
status: ACTIVE     # Published and maintained
status: DEPRECATED # Being phased out
status: ARCHIVED   # Historical reference
```

### 6. Specify Audience

Help readers identify relevance:

```yaml
audience: developers        # Code implementation
audience: operators         # Deployment and ops
audience: security-team     # Security policies
audience: all              # General information
```

### 7. Use Custom Fields Sparingly

Keep custom metadata organized:

```yaml
customFields:
  projectPhase: alpha
  estimatedEffort: 40h
  technicalDebt: low
```

---

## Performance Optimization

### Caching Strategy

Enable caching for repeated validations:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -Cache
```

**How it works:**
- Calculates MD5 hash of each file
- Skips validation if hash matches cached result
- Invalidates cache on file changes or schema updates
- Cache stored in `validation/.cache/validation-cache.json`

**Performance gain:** ~95% faster for unchanged files

### Parallel Processing

Use parallel mode for large repositories:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -Parallel
```

**Performance gain:** ~3-4x faster for 50+ files

**Considerations:**
- Uses max 8 concurrent jobs
- Requires PowerShell 7.0+
- Memory usage increases with parallelism

### Incremental Validation

Validate only changed files in CI/CD:

```bash
# Get changed files in PR
changed_files=$(git diff --name-only origin/main...HEAD | grep '\.md$')

# Validate only changed files
for file in $changed_files; do
  pwsh validate-metadata.ps1 -Path "$file"
done
```

### Performance Monitoring

Use `-VerboseOutput` to identify slow validations:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -VerboseOutput
```

Checks files exceeding 100ms threshold and logs warnings.

---

## Advanced Features

### Custom Schema Extensions

Create project-specific schemas by extending the base schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "allOf": [
    { "$ref": "./metadata.schema.json" },
    {
      "properties": {
        "projectSpecific": {
          "type": "string",
          "enum": ["value1", "value2"]
        }
      }
    }
  ]
}
```

### Multiple Output Formats

Generate both JSON and Markdown reports:

```powershell
# JSON for programmatic processing
.\validate-metadata.ps1 -Path ".\docs" -OutputFormat JSON -OutputPath "results.json"

# Markdown for human review
.\validate-metadata.ps1 -Path ".\docs" -OutputFormat Markdown -OutputPath "REPORT.md"
```

### Strict Mode Enforcement

Enforce zero-tolerance for warnings:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -StrictMode
```

Useful for critical documentation requiring perfect compliance.

### Fail-Fast for CI/CD

Stop on first error to save CI/CD time:

```powershell
.\validate-metadata.ps1 -Path ".\docs" -Recursive -FailFast
```

---

## Troubleshooting

### Issue: YAML Parsing Fails

**Symptoms:** Error message about YAML syntax

**Causes:**
- Incorrect indentation
- Missing quotes around special characters
- Unescaped colons in values

**Solutions:**
1. Validate YAML syntax with online validator
2. Use 2-space indentation consistently
3. Quote strings with colons: `description: "Config: Advanced"`
4. Check for unclosed quotes

### Issue: No Metadata Found

**Symptoms:** Warning "No YAML frontmatter found"

**Causes:**
- Missing `---` delimiters
- Frontmatter not at start of file
- Content before first delimiter

**Solutions:**
```markdown
---
description: Must be at line 1
---

# Document content starts here
```

### Issue: Validation is Slow

**Symptoms:** Validation takes >1 second per file

**Causes:**
- No caching enabled
- Sequential processing
- Large number of files

**Solutions:**
1. Enable caching: `-Cache`
2. Enable parallel processing: `-Parallel`
3. Use incremental validation in CI/CD
4. Check for regex performance issues in custom schemas

### Issue: Module Installation Fails

**Symptoms:** Error about missing powershell-yaml module

**Solutions:**
```powershell
# Install manually
Install-Module -Name powershell-yaml -Scope CurrentUser -Force

# Import manually
Import-Module powershell-yaml
```

### Issue: Permission Errors

**Symptoms:** Access denied when writing reports or cache

**Solutions:**
1. Run PowerShell as Administrator
2. Check directory permissions
3. Ensure output directory exists:
   ```powershell
   New-Item -ItemType Directory -Force -Path ".\validation\reports"
   ```

### Getting Help

For additional support:

1. Check error catalog: `validation/error-catalog/error-catalog.json`
2. Run with verbose output: `-VerboseOutput`
3. Review test cases: `validation/tests/`
4. Consult schema documentation: `validation/schemas/metadata.schema.json`

---

## Conclusion

The Project-AI metadata validation system provides enterprise-grade validation for documentation metadata, ensuring consistency, quality, and compliance across the repository. By following this guide, teams can maintain high standards for documentation while automating validation workflows.

### Key Takeaways

- ✅ Always include the required `description` field
- ✅ Use semantic versioning and ISO 8601 dates
- ✅ Enable caching and parallel processing for performance
- ✅ Integrate validation into CI/CD pipelines
- ✅ Review error catalog for resolution guidance
- ✅ Use strict mode for critical documentation

### Next Steps

1. Run initial validation: `.\validate-metadata.ps1 -Path "." -Recursive`
2. Fix any errors using the error catalog
3. Set up CI/CD integration
4. Configure pre-commit hooks
5. Train team on metadata standards

---

**Document Metadata:**

```yaml
---
description: Comprehensive guide for implementing and using the metadata validation system
version: 1.0.0
lastUpdated: 2026-01-23
status: ACTIVE
category: documentation
tags:
  - metadata
  - validation
  - json-schema
  - powershell
  - guide
author: AGENT-018
audience: developers
confidentiality: public
priority: high
reviewSchedule: quarterly
language: en
license: MIT
---
```
