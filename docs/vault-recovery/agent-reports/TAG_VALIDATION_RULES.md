# Tag Validation Rules

> **Automated Validation Reference**
> **Version:** 1.0
> **Last Updated:** 2025-01-20
> **Tool:** validate-tags.ps1

---

## Overview

This document defines the validation rules enforced by `validate-tags.ps1` to ensure tag consistency, compliance with taxonomy, and discoverability across the vault.

---

## Validation Categories

### 1. Tag Format Validation

**Rule:** Tags must follow naming conventions

**Checks:**
- ✓ Lowercase letters only (a-z)
- ✓ Hyphens allowed (-)
- ✓ Forward slashes allowed for hierarchy (/)
- ✓ Numbers allowed (0-9)
- ✗ Uppercase letters (A-Z)
- ✗ Spaces
- ✗ Special characters (!@#$%^&*()[]{}|\\;:'",.<>?~`)
- ✗ Underscores (_)

**Maximum Length:** 30 characters

**Pattern:** `^[a-z0-9-/]+$`

**Examples:**
```yaml
# Valid
- security
- security/authentication
- development/ci-cd
- P0
- api-doc

# Invalid
- Security (uppercase)
- security_audit (underscore)
- security.audit (period)
- "security audit" (spaces)
- very-long-tag-name-that-exceeds-the-maximum-allowed-length (too long)
```

**Error Messages:**
- `Tag 'Security' contains invalid characters. Use lowercase, hyphens, and forward slashes only.`
- `Tag 'very-long-tag-name-that-exceeds-the-maximum-allowed-length' exceeds maximum length of 30 characters.`

---

### 2. Controlled Vocabulary Validation

**Rule:** Tags must exist in tag-hierarchy.json

**Checks:**
- ✓ Tag is defined in one of the 7 categories
- ✓ Parent tags are valid
- ✓ Child tags are valid
- ✗ Tags not in taxonomy

**Valid Tag Count:** 100+ tags across 7 categories

**Examples:**
```yaml
# Valid (in taxonomy)
- security
- security/cryptography
- guide
- active
- developer
- P0

# Invalid (not in taxonomy)
- security/malware (not defined)
- tutorial-guide (not defined, should be separate: tutorial, guide)
- dev (abbreviation, should be: developer)
- p0 (lowercase, should be: P0)
```

**Error Messages:**
- `Tag 'security/malware' is not in the controlled vocabulary. See TAG_TAXONOMY.md for valid tags.`
- `Tag 'dev' is not in the controlled vocabulary. Did you mean 'developer'?`

---

### 3. Hierarchy Validation

**Rule:** Child tags require parent tag to be present

**Checks:**
- ✓ If tag contains `/`, parent tag must be in tags array
- ✗ Child tag without parent

**Examples:**
```yaml
# Valid
tags:
  - security
  - security/cryptography
  - architecture
  - architecture/distributed

# Invalid
tags:
  - security/cryptography  # Missing parent 'security'
  - architecture/backend   # Missing parent 'architecture'
```

**Error Messages:**
- `Child tag 'security/cryptography' requires parent tag 'security' to be present.`
- `Child tag 'architecture/backend' requires parent tag 'architecture' to be present.`

---

### 4. Cardinality Validation

**Rule:** Minimum and maximum tag counts per category

| Category | Required | Min | Max |
|----------|----------|-----|-----|
| Area | Yes | 1 | 3 |
| Type | Yes | 1 | 2 |
| Component | No | 0 | 5 |
| Status | Yes | 1 | 1 |
| Audience | Yes | 1 | 4 |
| Priority | No | 0 | 1 |
| Special | No | 0 | 10 |

**Examples:**

**Valid:**
```yaml
tags:
  # Area (2 tags, within 1-3 range)
  - security
  - security/audit

  # Type (1 tag, within 1-2 range)
  - report

  # Component (2 tags, within 0-5 range)
  - user-manager
  - command-override

  # Status (1 tag, exactly 1)
  - active

  # Audience (2 tags, within 1-4 range)
  - security
  - developer

  # Priority (1 tag, within 0-1 range)
  - P0

  # Special (2 tags, within 0-10 range)
  - troubleshooting
  - best-practices
```

**Invalid:**
```yaml
# Area: 0 tags (requires at least 1)
# Type: 0 tags (requires at least 1)
# Status: 2 tags (requires exactly 1)
tags:
  - active
  - draft
  - developer

# Area: 4 tags (exceeds maximum of 3)
tags:
  - security
  - architecture
  - development
  - operations
  - guide
  - active
  - developer
```

**Error Messages:**
- `Category 'area' requires at least 1 tag(s), found 0.`
- `Category 'status' allows maximum 1 tag(s), found 2.`
- `Category 'area' allows maximum 3 tag(s), found 4.`

---

### 5. Mutual Exclusivity Validation

**Rule:** Some categories allow only one tag (mutually exclusive)

**Mutually Exclusive Categories:**
- **Status** (exactly 1 tag)
- **Priority** (0 or 1 tag)

**Examples:**

**Valid:**
```yaml
# Status: 1 tag (mutually exclusive)
tags:
  - active

# Priority: 1 tag
tags:
  - P0

# Priority: 0 tags (optional)
tags:
  - security
  - guide
  - active
  - developer
```

**Invalid:**
```yaml
# Status: 2 tags (mutually exclusive violated)
tags:
  - active
  - draft

# Priority: 2 tags (mutually exclusive violated)
tags:
  - P0
  - P1
```

**Error Messages:**
- `Category 'status' allows only one tag (mutually exclusive), found: active, draft.`
- `Category 'priority' allows only one tag (mutually exclusive), found: P0, P1.`

---

### 6. Required Metadata Validation

**Rule:** Some status tags require additional metadata fields

**Status-Specific Requirements:**

| Status | Required Metadata Fields |
|--------|--------------------------|
| `in-progress` | `maintainer` |
| `review` | `reviewers` |
| `deprecated` | `superseded_by` OR `deprecation_reason` |
| `superseded` | `superseded_by` |
| `planned` | `target_date` OR `milestone` |
| `blocked` | `blocked_reason`, `blocked_by` |

**Examples:**

**Valid:**
```yaml
---
status: in-progress
maintainer: "AGENT-017"

tags:
  - in-progress
  # ...
---
```

```yaml
---
status: deprecated
superseded_by: "[[new-document.md]]"
deprecation_reason: "Security vulnerability fixed in v2.0"

tags:
  - deprecated
  # ...
---
```

**Invalid:**
```yaml
---
status: in-progress
# Missing 'maintainer' field

tags:
  - in-progress
  # ...
---
```

```yaml
---
status: deprecated
# Missing 'superseded_by' or 'deprecation_reason'

tags:
  - deprecated
  # ...
---
```

**Error Messages (Warnings):**
- `Status 'in-progress' requires metadata field 'maintainer'.`
- `Status 'deprecated' requires metadata field 'superseded_by' or 'deprecation_reason'.`

---

## Validation Severity Levels

### Errors (Exit Code 1)

**Blocking issues that must be fixed:**
- Invalid tag format
- Tag not in controlled vocabulary
- Hierarchy violations (child without parent)
- Cardinality violations (too few/many required tags)
- Mutual exclusivity violations

### Warnings (Exit Code 0)

**Non-blocking issues to review:**
- Missing recommended categories (e.g., priority)
- Missing required metadata for status tags
- No tags found in frontmatter

---

## Validation Workflow

### Manual Validation

```powershell
# Validate single file
.\validate-tags.ps1 -Path "document.md"

# Validate with verbose output
.\validate-tags.ps1 -Path "document.md" -Verbose

# Validate directory recursively
.\validate-tags.ps1 -Path "T:\Project-AI-vault\repo-docs"
```

### Automated Validation

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate staged markdown files
STAGED_MD_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')

if [ -n "$STAGED_MD_FILES" ]; then
    echo "Validating tags in staged markdown files..."

    for file in $STAGED_MD_FILES; do
        pwsh -File T:\Project-AI-vault\validate-tags.ps1 -Path "$file"

        if [ $? -ne 0 ]; then
            echo "Tag validation failed for $file"
            echo "Fix errors and try again, or use 'git commit --no-verify' to skip validation"
            exit 1
        fi
    done

    echo "Tag validation passed"
fi

exit 0
```

**GitHub Actions:**
```yaml
name: Validate Tags

on:
  pull_request:
    paths:
      - '**/*.md'
  push:
    branches:
      - main

jobs:
  validate-tags:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Validate Document Tags
        shell: pwsh
        run: |
          $result = .\T:\Project-AI-vault\validate-tags.ps1 `
            -Path "T:\Project-AI-vault\repo-docs" `
            -OutputFormat JSON `
            -ReportPath "validation-report.json"

          if ($LASTEXITCODE -ne 0) {
            Write-Error "Tag validation failed"
            exit 1
          }

      - name: Upload Validation Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.json
```

---

## Validation Report Formats

### Text Format (Default)

```
================================================================================
TAG VALIDATION REPORT
================================================================================

Files Processed:      42
Files with Errors:    3
Files with Warnings:  5
Total Errors:         8
Total Warnings:       12
Validation Date:      2025-01-20 14:30:00
Taxonomy Version:     1.0

================================================================================
ERRORS
================================================================================

File:     T:\Project-AI-vault\repo-docs\security-audit.md
Category: Vocabulary
Message:  Tag 'security/malware' is not in the controlled vocabulary.
Time:     2025-01-20 14:30:01
--------------------------------------------------------------------------------

File:     T:\Project-AI-vault\repo-docs\api-guide.md
Category: Cardinality
Message:  Category 'status' requires at least 1 tag(s), found 0.
Time:     2025-01-20 14:30:02
--------------------------------------------------------------------------------

================================================================================
✗ VALIDATION FAILED - Fix errors above before committing
================================================================================
```

### JSON Format

```json
{
  "Summary": {
    "FilesProcessed": 42,
    "FilesWithErrors": 3,
    "FilesWithWarnings": 5,
    "TotalErrors": 8,
    "TotalWarnings": 12,
    "ValidationDate": "2025-01-20 14:30:00",
    "TaxonomyVersion": "1.0"
  },
  "Errors": [
    {
      "File": "T:\\Project-AI-vault\\repo-docs\\security-audit.md",
      "Category": "Vocabulary",
      "Message": "Tag 'security/malware' is not in the controlled vocabulary.",
      "Severity": "Error",
      "Timestamp": "2025-01-20 14:30:01"
    }
  ],
  "Warnings": [
    {
      "File": "T:\\Project-AI-vault\\repo-docs\\draft-doc.md",
      "Category": "RequiredMetadata",
      "Message": "Status 'in-progress' requires metadata field 'maintainer'.",
      "Severity": "Warning",
      "Timestamp": "2025-01-20 14:30:05"
    }
  ]
}
```

### HTML Format

Interactive HTML report with:
- Summary dashboard
- Color-coded errors/warnings
- Filterable by category
- Clickable file paths
- Exportable results

---

## Common Validation Errors and Fixes

### Error: Missing Required Tags

**Problem:**
```yaml
tags:
  - security
  - report
  # Missing status, audience
```

**Fix:**
```yaml
tags:
  - security
  - report
  - active        # Add status
  - developer     # Add audience
```

---

### Error: Child Without Parent

**Problem:**
```yaml
tags:
  - security/cryptography  # Missing parent
  - guide
```

**Fix:**
```yaml
tags:
  - security               # Add parent
  - security/cryptography
  - guide
```

---

### Error: Multiple Status Tags

**Problem:**
```yaml
tags:
  - active
  - draft  # Conflict
```

**Fix:**
```yaml
tags:
  - active  # Choose one
```

---

### Error: Invalid Tag Format

**Problem:**
```yaml
tags:
  - Security  # Uppercase
  - security_audit  # Underscore
```

**Fix:**
```yaml
tags:
  - security
  - security/audit
```

---

### Error: Tag Not in Vocabulary

**Problem:**
```yaml
tags:
  - sec  # Abbreviation
  - tutorial-guide  # Combined, not defined
```

**Fix:**
```yaml
tags:
  - security  # Full word
  - guide     # Separate tags
  - tutorial  # (in special tags)
```

---

## Validation Script Usage

### Basic Usage

```powershell
# Validate current directory
.\validate-tags.ps1 -Path .

# Validate specific file
.\validate-tags.ps1 -Path "document.md"

# Validate with verbose output
.\validate-tags.ps1 -Path "document.md" -Verbose
```

### Advanced Usage

```powershell
# Generate JSON report
.\validate-tags.ps1 -Path . -OutputFormat JSON -ReportPath "report.json"

# Generate HTML report
.\validate-tags.ps1 -Path . -OutputFormat HTML -ReportPath "report.html"

# Fix issues automatically (when possible)
.\validate-tags.ps1 -Path . -Fix
```

### Exit Codes

- **0**: Validation passed (no errors, may have warnings)
- **1**: Validation failed (errors found)

### CI/CD Integration

```powershell
# In CI pipeline
.\validate-tags.ps1 -Path "T:\Project-AI-vault\repo-docs"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Tag validation failed - see errors above"
    exit 1
}

Write-Host "Tag validation passed" -ForegroundColor Green
```

---

## Maintenance

### Adding New Tags

1. Update `tag-hierarchy.json` with new tag definition
2. Update `TAG_TAXONOMY.md` with documentation
3. Run validation on existing documents
4. Update examples if needed

### Deprecating Tags

1. Mark tag as deprecated in `tag-hierarchy.json`
2. Create migration guide
3. Update affected documents
4. Remove from vocabulary after 90 days

### Schema Versioning

- Current Version: 1.0
- Version in `tag-hierarchy.json`: `metadata.schemaVersion`
- Breaking changes require major version bump
- Additive changes require minor version bump

---

## Troubleshooting

### Issue: Validation script fails to load taxonomy

**Symptom:**
```
Taxonomy file not found: T:\Project-AI-vault\tag-hierarchy.json
```

**Solution:**
```powershell
# Specify taxonomy path explicitly
.\validate-tags.ps1 -Path "." -TaxonomyPath "T:\Project-AI-vault\tag-hierarchy.json"
```

---

### Issue: False positives for valid tags

**Symptom:**
```
Tag 'security/cryptography' is not in the controlled vocabulary.
```

**Solution:**
- Verify tag exists in `tag-hierarchy.json`
- Check for typos (cryptography vs. cryptograhy)
- Ensure parent tag is valid

---

### Issue: Performance with large directories

**Symptom:**
Validation takes > 5 minutes for 1000+ files

**Solution:**
```powershell
# Validate in batches
$files = Get-ChildItem -Path "." -Filter "*.md" -Recurse
$batches = $files | Group-Object -Property {[math]::Floor($_ / 100)}

foreach ($batch in $batches) {
    .\validate-tags.ps1 -Path $batch.Group
}
```

---

**Version:** 1.0
**Last Updated:** 2025-01-20
**See Also:** TAG_TAXONOMY.md, tag-hierarchy.json, validate-tags.ps1

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
