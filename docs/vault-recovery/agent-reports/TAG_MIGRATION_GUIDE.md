# Tag Migration Guide v1.0 → v2.0

**Migration Date:** 2025-01-23  
**Prepared By:** AGENT-039 (Tag Taxonomy Refinement Specialist)  
**Status:** Ready for Implementation  
**Estimated Effort:** 4 weeks (phased approach)

---

## Executive Summary

This guide provides step-by-step migration from Tag Taxonomy v1.0 to v2.0, covering:

- **35 tag migrations** (non-standard → standard)
- **40 tag deprecations** (unused tags removed)
- **Component category removal** (0% adoption)
- **5 new tag additions** (filling identified gaps)

**Impact:**
- **78 files require updates** (templates, examples, indexes, source-docs)
- **Estimated time:** 30 minutes manual review + 2 hours automated migration
- **Risk:** Low (backward compatible, automated migration available)

**Benefits:**
- **Compliance increase:** 57% → 90% (target)
- **Tag adoption increase:** 21.7% → 65% (target)
- **Reduced complexity:** 120 → 85 tags (29% reduction)
- **Eliminated ambiguity:** Clear TYPE vs SPECIAL distinction

---

## Table of Contents

1. [Migration Overview](#migration-overview)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Phase 1: Fix Templates](#phase-1-fix-templates-week-1)
4. [Phase 2: Fix Metadata Examples](#phase-2-fix-metadata-examples-week-1-2)
5. [Phase 3: Deploy Validation](#phase-3-deploy-validation-week-2)
6. [Phase 4: Bulk Migration](#phase-4-bulk-migration-week-3)
7. [Phase 5: Enforcement](#phase-5-enforcement-week-4)
8. [Migration Scripts](#migration-scripts)
9. [Rollback Plan](#rollback-plan)
10. [Validation](#validation)

---

## Migration Overview

### Migration Types

#### Type 1: Naming Convention Fixes (21 tags)
**Issue:** Violates kebab-case, capitalization, or plural form rules  
**Action:** Rename tags automatically

| Old Tag | New Tag | Category | Issue | Count |
|---------|---------|----------|-------|-------|
| `api_reference` | `api-doc` | type | Underscore → hyphen | 4 |
| `Module` | `source-doc` | type | Capitalized + generic | 3 |
| `decision_record` | `adr` | type | Underscore + verbose | 1 |
| `specification` | `spec` | type | Verbose form | 1 |
| `"developer"` | `developer` | audience | Quoted (YAML error) | 3 |
| `"architect"` | `architect` | audience | Quoted (YAML error) | 4 |
| `"operator"` | `operator` | audience | Quoted (YAML error) | 1 |
| `"auditor"` | `security` or `legal` | audience | Quoted + non-standard | 1 |
| `"ai-engineer"` | `ai-engineer` | audience | Quoted (but add to taxonomy) | 1 |
| `developers` | `developer` | audience | Pluralized | 3 |
| `architects` | `architect` | audience | Pluralized | 2 |
| `security_engineer` | `security` | audience | Underscore + specific | 2 |
| `security-engineers` | `security` | audience | Hyphen + plural | 1 |
| `technical_lead` | `architect` | audience | Underscore + redundant | 1 |
| `gui-engineers` | `developer` | audience | Too specific | 1 |
| `maintainers` | `contributor` | audience | Generic → specific | 1 |
| `end_user` | `end-user` | audience | Underscore (add to taxonomy) | 1 |
| `policy_maker` | `executive` + `legal` | audience | Underscore + merge | 1 |
| `production` | `active` | status | Non-standard | 3 |
| `completed` | `active` | status | Non-standard | 1 |
| `Agent` | `source-doc` | type | Capitalized + generic | 0 |

---

#### Type 2: Category Reassignments (12 tags)
**Issue:** Tag used in wrong category (TYPE vs SPECIAL confusion)  
**Action:** Move tag to correct category

| Old Usage | New Usage | Rationale | Count |
|-----------|-----------|-----------|-------|
| `type: tutorial` | `type: guide` + `special: [tutorial]` | Tutorial is teaching method, not format | 1 |
| `type: faq` | `type: reference` + `special: [faq]` | FAQ is characteristic, not format | 1 |
| `type: glossary` | `type: reference` + `special: [glossary]` | Glossary is characteristic, not format | 1 |
| `type: troubleshooting` | `type: guide` + `special: [troubleshooting]` | Troubleshooting is purpose, not format | 0 |
| `type: audit` | `type: report` + `special: [audit]` | Audit is report type | 1 |
| `type: architecture` | `area: architecture` + `type: [appropriate]` | Architecture is domain, not type | 1 |
| `type: policy` | `area: [governance, governance/policy]` + `type: spec` | Policy is domain, not type | 1 |
| `type: by-area` | `type: index` | Index organization method | 2 |
| `type: master-index` | `type: index` | Redundant qualifier | 1 |
| `type: design` | `type: spec` OR new `type: design` | Design docs are specs | 1 |
| `type: playbook` | `type: runbook` OR new `type: playbook` | Broader than runbook? | 1 |
| `type: assessment` | `type: report` + `special: [assessment]` | Assessment is report type | 1 |

---

#### Type 3: New Tag Additions (5 tags)
**Issue:** Common patterns without taxonomy support  
**Action:** Add to taxonomy v2.0

| Tag | Category | Definition | Usage |
|-----|----------|------------|-------|
| `postmortem` | type | Incident postmortem, failure analysis, lessons learned | 1 (add to taxonomy) |
| `rfc` | type | Request for Comments, design proposals | 1 (add to taxonomy) |
| `changelog` | type | Version history, release notes | 1 (add to taxonomy) |
| `end-user` | audience | Non-technical application end users | 1 (add to taxonomy) |
| `ai-engineer` | audience | AI/ML engineers, data scientists | 1 (add to taxonomy) |

---

#### Type 4: Deprecations (40 tags)
**Issue:** Zero usage, redundant, or over-specific  
**Action:** Remove from taxonomy, prevent future use

**Area Children (31):**
```
architecture/integration, architecture/distributed,
security/cryptography, security/network, security/application, security/infrastructure,
governance/constitutional-ai, governance/legal, governance/sovereignty,
development/ci-cd, development/tooling, development/database,
operations/maintenance, operations/backup-recovery, operations/performance, operations/infrastructure
```
(See full list in TAG_USAGE_ANALYSIS.md)

**Status Tags (3):**
- `in-progress` → Use `draft` instead
- `legacy` → Use `archived` instead
- `planned` → Remove (don't document non-existent features)

**Component Category (23 tags):**
- ALL component tags deprecated (0% adoption)

**Priority Tags (0):**
- All P0-P4 retained despite P2-P4 having 0 usage (future-proofing)

---

## Pre-Migration Checklist

**Before starting migration:**

- [x] ✅ **Backup vault:**
  ```powershell
  Copy-Item -Path "T:\Project-AI-vault" -Destination "T:\Project-AI-vault-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')" -Recurse
  ```

- [ ] ✅ **Review TAG_USAGE_ANALYSIS.md:**
  - Understand current state
  - Identify affected files
  - Review recommendations

- [ ] ✅ **Review TAG_TAXONOMY_V2.md:**
  - Understand new structure
  - Learn TYPE vs SPECIAL decision tree
  - Familiarize with new tags

- [ ] ✅ **Test validation script:**
  ```powershell
  .\scripts\validate-tags-strict.ps1 -DryRun
  ```

- [ ] ✅ **Communicate to team:**
  - Announce migration timeline
  - Provide training on v2.0
  - Answer questions

- [ ] ✅ **Freeze documentation updates:**
  - No new docs during migration (or coordinate)
  - Complete in-flight PRs
  - Warn contributors

---

## Phase 1: Fix Templates (Week 1)

**Goal:** Update 4 template files to v2.0 standards

**Affected Files:**
1. `templates/module-doc-core-system.md`
2. `templates/module-doc-gui-component.md`
3. `templates/module-doc-agent.md`
4. `templates/agent-doc-task-report.md`

### Changes Required

#### Before (v1.0):
```yaml
---
type: Module
area: [development, development/python]
component: [core-system]
audience: ["developer", "architect"]
status: active
---
```

#### After (v2.0):
```yaml
---
type: source-doc
area: [development, development/python]
audience: [developer, architect]
status: active
---
```

**Changes:**
1. ✅ `type: Module` → `type: source-doc`
2. ✅ Remove `component:` field
3. ✅ Remove quotes from `audience:` array
4. ✅ Update documentation text explaining metadata

### Manual Steps

```powershell
# For each template file:

# 1. Open in editor
code templates/module-doc-core-system.md

# 2. Update frontmatter (see above)

# 3. Search for "type: Module" in documentation text
#    Replace with "type: source-doc"

# 4. Search for component references in docs
#    Update or remove

# 5. Validate
.\scripts\validate-tags-strict.ps1 templates/module-doc-core-system.md

# Repeat for all 4 templates
```

### Verification

```powershell
# Check all templates validate
Get-ChildItem templates/*.md | ForEach-Object {
    Write-Host "Validating $($_.Name)..."
    .\scripts\validate-tags-strict.ps1 $_.FullName
}
```

**Expected Result:** All templates pass validation

---

## Phase 2: Fix Metadata Examples (Week 1-2)

**Goal:** Update 20 metadata example files to v2.0 standards

**Affected Files:** `metadata-examples/*.md` (20 files)

### Migration Table

| File | Old Type | New Type | New Special | Notes |
|------|----------|----------|-------------|-------|
| 01-audit-example.md | audit | report | [audit] | Category reassignment |
| 02-tutorial-example.md | tutorial | guide | [tutorial] | Category reassignment |
| 03-architecture-example.md | architecture | spec | [] | Move to area: architecture |
| 04-api-reference-example.md | api_reference | api-doc | [] | Naming fix |
| 05-adr-example.md | decision_record | adr | [] | Naming fix |
| 06-runbook-example.md | runbook | runbook | [] | No change |
| 07-postmortem-example.md | postmortem | postmortem | [troubleshooting] | Add to taxonomy |
| 08-policy-example.md | policy | spec | [] | Move to area: governance |
| 09-specification-example.md | specification | spec | [] | Abbreviate |
| 10-faq-example.md | faq | reference | [faq] | Category reassignment |
| 11-glossary-example.md | glossary | reference | [glossary] | Category reassignment |
| 12-meeting-notes-example.md | meeting_notes | (decide) | [] | Add to taxonomy? |
| 13-whitepaper-example.md | whitepaper | whitepaper | [] | No change |
| 14-changelog-example.md | changelog | changelog | [versioning] | Add to taxonomy |
| 17-assessment-example.md | assessment | report | [assessment] | Report subtype |
| 18-rfc-example.md | rfc | rfc | [] | Add to taxonomy |
| 19-standard-example.md | standard | spec | [best-practices] | Spec with special |
| 20-design-example.md | design | spec | [best-practices] | Design = spec |
| 21-playbook-example.md | playbook | runbook | [] | Playbook = broader runbook |

### Automated Migration Script

```powershell
# migrate-examples.ps1

$examples = @(
    @{File='01-audit-example.md'; OldType='audit'; NewType='report'; NewSpecial='[audit]'},
    @{File='02-tutorial-example.md'; OldType='tutorial'; NewType='guide'; NewSpecial='[tutorial]'},
    @{File='03-architecture-example.md'; OldType='architecture'; NewType='spec'; NewSpecial='[]'; AddArea='architecture'},
    @{File='04-api-reference-example.md'; OldType='api_reference'; NewType='api-doc'; NewSpecial='[]'},
    @{File='05-adr-example.md'; OldType='decision_record'; NewType='adr'; NewSpecial='[]'},
    @{File='06-runbook-example.md'; OldType='runbook'; NewType='runbook'; NewSpecial='[]'},
    @{File='07-postmortem-example.md'; OldType='postmortem'; NewType='postmortem'; NewSpecial='[troubleshooting]'},
    @{File='08-policy-example.md'; OldType='policy'; NewType='spec'; NewSpecial='[]'; AddArea='governance, governance/policy'},
    @{File='09-specification-example.md'; OldType='specification'; NewType='spec'; NewSpecial='[]'},
    @{File='10-faq-example.md'; OldType='faq'; NewType='reference'; NewSpecial='[faq]'},
    @{File='11-glossary-example.md'; OldType='glossary'; NewType='reference'; NewSpecial='[glossary]'},
    @{File='14-changelog-example.md'; OldType='changelog'; NewType='changelog'; NewSpecial='[versioning]'},
    @{File='17-assessment-example.md'; OldType='assessment'; NewType='report'; NewSpecial='[assessment]'},
    @{File='18-rfc-example.md'; OldType='rfc'; NewType='rfc'; NewSpecial='[]'},
    @{File='19-standard-example.md'; OldType='standard'; NewType='spec'; NewSpecial='[best-practices]'},
    @{File='20-design-example.md'; OldType='design'; NewType='spec'; NewSpecial='[best-practices]'},
    @{File='21-playbook-example.md'; OldType='playbook'; NewType='runbook'; NewSpecial='[]'}
)

foreach ($ex in $examples) {
    $path = "T:\Project-AI-vault\metadata-examples\$($ex.File)"
    if (Test-Path $path) {
        $content = Get-Content $path -Raw
        
        # Replace type
        $content = $content -replace "type:\s*$($ex.OldType)", "type: $($ex.NewType)"
        
        # Add special if needed
        if ($ex.NewSpecial -ne '[]') {
            if ($content -notmatch 'special:') {
                # Add special field after type
                $content = $content -replace "(type:\s*$($ex.NewType))", "`$1`nspecial: $($ex.NewSpecial)"
            }
        }
        
        # Add area if needed
        if ($ex.AddArea) {
            if ($content -notmatch 'area:') {
                $content = $content -replace "(type:)", "area: [$($ex.AddArea)]`n`$1"
            }
        }
        
        Set-Content $path -Value $content
        Write-Host "✅ Migrated: $($ex.File)"
    } else {
        Write-Host "⚠️ Not found: $($ex.File)"
    }
}

Write-Host "`n✅ Migration complete. Run validation to verify."
```

### Manual Review Required

Some examples may need manual content updates beyond frontmatter:
- Update example text to reference correct tag names
- Add explanations for new `special:` usage
- Update TYPE vs SPECIAL examples

---

## Phase 3: Deploy Validation (Week 2)

**Goal:** Enable automated validation in CI/CD

### Step 1: Create Validation Script

**File:** `scripts/validate-tags-strict.ps1`

```powershell
# validate-tags-strict.ps1 - Tag Taxonomy v2.0 Validator

param(
    [string]$Path = "T:\Project-AI-vault",
    [switch]$Verbose = $false
)

# Load taxonomy
$taxonomy = Get-Content "T:\Project-AI-vault\tag-hierarchy.json" | ConvertFrom-Json

$errors = @()
$warnings = @()
$passed = @()

function Test-Tag {
    param($Tag, $Category, $File)
    
    # Format validation
    if ($Tag -notmatch '^[a-z0-9/-]+$') {
        return "Invalid format: '$Tag' (use lowercase, hyphens only)"
    }
    
    if ($Tag.Length -gt 30) {
        return "Tag too long: '$Tag' (max 30 chars)"
    }
    
    # Whitelist validation
    $validTags = $taxonomy.categories.$Category.tags.PSObject.Properties.Name
    if ($Tag -notin $validTags) {
        # Check child tags
        $allValid = @()
        foreach ($parent in $validTags) {
            $allValid += $parent
            if ($taxonomy.categories.$Category.tags.$parent.children) {
                $allValid += $taxonomy.categories.$Category.tags.$parent.children
            }
        }
        
        if ($Tag -notin $allValid) {
            return "Not in taxonomy: '$Tag' in category '$Category'"
        }
    }
    
    return $null
}

# Process markdown files
Get-ChildItem -Path $Path -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match '(?s)^---\s*\n(.*?)\n---') {
        $frontmatter = $matches[1]
        $fileErrors = @()
        
        # Validate each category
        foreach ($cat in @('area', 'type', 'status', 'audience', 'priority', 'special')) {
            # Extract tags
            $tags = @()
            if ($frontmatter -match "${cat}:\s*\[(.*?)\]") {
                $tags = $matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") }
            }
            elseif ($frontmatter -match "${cat}:\s*\n((?:\s*-\s*.+\n)+)") {
                $tagBlock = $matches[1]
                $tags = $tagBlock -split '\n' | ForEach-Object {
                    if ($_ -match '-\s*(.+)') { $matches[1].Trim() }
                } | Where-Object { $_ }
            }
            elseif ($frontmatter -match "${cat}:\s*([a-zA-Z0-9/_-]+)") {
                $tags = @($matches[1])
            }
            
            # Validate each tag
            foreach ($tag in $tags) {
                if ($tag) {
                    $error = Test-Tag -Tag $tag -Category $cat -File $_.Name
                    if ($error) {
                        $fileErrors += "  [$cat] $error"
                    }
                }
            }
        }
        
        if ($fileErrors.Count -gt 0) {
            $errors += @{File=$_.FullName; Errors=$fileErrors}
        } else {
            $passed += $_.Name
        }
    }
}

# Output report
Write-Host "`n=== TAG VALIDATION REPORT ===`n"

if ($errors.Count -gt 0) {
    Write-Host "❌ ERRORS ($($errors.Count) files):`n" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  $($err.File):" -ForegroundColor Yellow
        $err.Errors | ForEach-Object { Write-Host "    $_" }
        Write-Host ""
    }
}

if ($passed.Count -gt 0) {
    Write-Host "✅ PASSED ($($passed.Count) files)`n" -ForegroundColor Green
    if ($Verbose) {
        $passed | ForEach-Object { Write-Host "  $_" }
    }
}

$total = $errors.Count + $passed.Count
$compliance = if ($total -gt 0) { [math]::Round(($passed.Count / $total) * 100, 1) } else { 0 }
Write-Host "Compliance: $compliance% ($($passed.Count)/$total files)`n"

# Exit code
if ($errors.Count -gt 0) { exit 1 } else { exit 0 }
```

### Step 2: Integrate with CI/CD

**GitHub Actions** (.github/workflows/validate-tags.yml):

```yaml
name: Validate Tag Taxonomy

on:
  pull_request:
    paths:
      - '**.md'
      - 'tag-hierarchy.json'
      - 'scripts/validate-tags-strict.ps1'
  push:
    branches: [main, develop]

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tag validation
        shell: pwsh
        run: |
          cd T:\Project-AI-vault
          .\scripts\validate-tags-strict.ps1 -Verbose
      
      - name: Upload validation report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: tag-validation-errors
          path: tag-validation-report.txt
```

### Step 3: Test Validation

```powershell
# Dry run
.\scripts\validate-tags-strict.ps1 -Verbose

# Should report:
# - Errors in templates (if not yet migrated)
# - Errors in metadata-examples (if not yet migrated)
# - Passes for already-compliant files
```

---

## Phase 4: Bulk Migration (Week 3)

**Goal:** Migrate all remaining files automatically

### Step 1: Backup

```powershell
# Create timestamped backup
$backupPath = "T:\Project-AI-vault-pre-migration-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -Path "T:\Project-AI-vault" -Destination $backupPath -Recurse
Write-Host "✅ Backup created: $backupPath"
```

### Step 2: Run Migration Script

```powershell
# migrate-tags-v1-to-v2.ps1

param(
    [string]$Path = "T:\Project-AI-vault",
    [switch]$DryRun = $false
)

$migrations = @(
    # Type migrations
    @{Old='api_reference'; New='api-doc'; Category='type'; Pattern='type:\s*api_reference'},
    @{Old='Module'; New='source-doc'; Category='type'; Pattern='type:\s*Module'},
    @{Old='decision_record'; New='adr'; Category='type'; Pattern='type:\s*decision_record'},
    @{Old='specification'; New='spec'; Category='type'; Pattern='type:\s*specification'},
    @{Old='by-area'; New='index'; Category='type'; Pattern='type:\s*by-area'},
    @{Old='master-index'; New='index'; Category='type'; Pattern='type:\s*master-index'},
    
    # Status migrations
    @{Old='in-progress'; New='draft'; Category='status'; Pattern='status:\s*in-progress'},
    @{Old='legacy'; New='archived'; Category='status'; Pattern='status:\s*legacy'},
    @{Old='production'; New='active'; Category='status'; Pattern='status:\s*production'},
    @{Old='completed'; New='active'; Category='status'; Pattern='status:\s*completed'},
    
    # Audience migrations
    @{Old='developers'; New='developer'; Category='audience'; Pattern='developers'},
    @{Old='architects'; New='architect'; Category='audience'; Pattern='architects'},
    @{Old='security_engineer'; New='security'; Category='audience'; Pattern='security_engineer'},
    @{Old='security-engineers'; New='security'; Category='audience'; Pattern='security-engineers'},
    @{Old='technical_lead'; New='architect'; Category='audience'; Pattern='technical_lead'},
    @{Old='gui-engineers'; New='developer'; Category='audience'; Pattern='gui-engineers'},
    @{Old='maintainers'; New='contributor'; Category='audience'; Pattern='maintainers'},
    @{Old='end_user'; New='end-user'; Category='audience'; Pattern='end_user'},
    @{Old='policy_maker'; New='executive'; Category='audience'; Pattern='policy_maker'}
)

$stats = @{Modified=0; Errors=0; Skipped=0}

Get-ChildItem -Path $Path -Recurse -Filter "*.md" | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -Raw -ErrorAction Stop
        $originalContent = $content
        $fileModified = $false
        
        # Apply migrations
        foreach ($mig in $migrations) {
            if ($content -match $mig.Pattern) {
                $content = $content -replace $mig.Pattern, "$($mig.Category): $($mig.New)"
                $fileModified = $true
                if (-not $DryRun) {
                    Write-Host "[$($_.Name)] Migrated $($mig.Old) → $($mig.New)" -ForegroundColor Yellow
                }
            }
        }
        
        # Remove component field
        if ($content -match 'component:.*\n') {
            $content = $content -replace 'component:.*\n', ''
            $fileModified = $true
            if (-not $DryRun) {
                Write-Host "[$($_.Name)] Removed component field" -ForegroundColor Yellow
            }
        }
        
        # Remove quotes from arrays (YAML syntax fix)
        if ($content -match '\["[^"]+"\]') {
            $content = $content -replace '\["([^"]+)"\]', '[$1]'
            $content = $content -replace '",\s*"', ', '
            $fileModified = $true
            if (-not $DryRun) {
                Write-Host "[$($_.Name)] Removed quotes from arrays" -ForegroundColor Yellow
            }
        }
        
        # Write changes
        if ($fileModified) {
            if ($DryRun) {
                Write-Host "[DRY RUN] Would modify: $($_.FullName)" -ForegroundColor Cyan
                $stats.Modified++
            } else {
                Set-Content $_.FullName -Value $content -ErrorAction Stop
                Write-Host "✅ Modified: $($_.Name)" -ForegroundColor Green
                $stats.Modified++
            }
        } else {
            $stats.Skipped++
        }
        
    } catch {
        Write-Host "❌ Error processing $($_.Name): $_" -ForegroundColor Red
        $stats.Errors++
    }
}

Write-Host "`n=== MIGRATION SUMMARY ==="
Write-Host "Modified: $($stats.Modified) files"
Write-Host "Skipped: $($stats.Skipped) files"
Write-Host "Errors: $($stats.Errors) files"

if ($DryRun) {
    Write-Host "`n⚠️ DRY RUN MODE - No files were modified"
    Write-Host "Run without -DryRun to apply changes"
}
```

### Step 3: Execute Migration

```powershell
# Test first (dry run)
.\migrate-tags-v1-to-v2.ps1 -DryRun

# Review proposed changes

# Execute migration
.\migrate-tags-v1-to-v2.ps1

# Validate results
.\scripts\validate-tags-strict.ps1
```

### Step 4: Manual Review

**Review files that still fail validation:**

```powershell
.\scripts\validate-tags-strict.ps1 | Out-File migration-issues.txt

# Manually fix remaining issues
code migration-issues.txt
```

**Common manual fixes needed:**
- Complex frontmatter structures
- Multi-line YAML arrays
- Files with nested metadata
- Edge cases not covered by regex

---

## Phase 5: Enforcement (Week 4+)

**Goal:** Prevent regression to v1.0 patterns

### Step 1: Enable Blocking Validation

**Update .github/workflows/validate-tags.yml:**

```yaml
      - name: Block PR on validation failure
        if: failure()
        run: |
          echo "::error::Tag validation failed. Review tag-validation-report.txt"
          exit 1
```

### Step 2: Add Pre-Commit Hook

**.git/hooks/pre-commit:**

```bash
#!/bin/bash
# Pre-commit hook: Validate tag taxonomy

echo "Validating tag taxonomy..."
pwsh -File scripts/validate-tags-strict.ps1

if [ $? -ne 0 ]; then
    echo "❌ Tag validation failed. Fix errors before committing."
    echo "Run: pwsh scripts/validate-tags-strict.ps1 -Verbose"
    exit 1
fi

echo "✅ Tag validation passed"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### Step 3: Team Training

**Training Checklist:**
- [ ] Review TAG_TAXONOMY_V2.md with team
- [ ] Demo TYPE vs SPECIAL decision tree
- [ ] Show validation workflow (pre-commit + CI/CD)
- [ ] Practice: Convert v1.0 frontmatter to v2.0
- [ ] Q&A session
- [ ] Distribute quick reference card

**Quick Reference Card:**

```
TAG TAXONOMY V2.0 QUICK REFERENCE

Required Fields:
  area: [domain]            # 1-3 tags, hierarchical OK
  type: [format]            # 1-2 tags, flat
  status: active|draft|...  # Exactly 1, mutually exclusive
  audience: [who]           # 1-4 tags

Optional Fields:
  priority: P0|P1|P2|P3|P4  # 0-1 tag
  special: [characteristics] # 0-10 tags

Naming Rules:
  ✅ lowercase-with-hyphens
  ✅ singular (developer not developers)
  ✅ no quotes in arrays: [tag] not ["tag"]
  ❌ NO underscores, NO capitals, NO plurals

TYPE vs SPECIAL:
  TYPE = Document format (how to read it)
    - guide, reference, report, spec, api-doc, runbook, adr, ...
  SPECIAL = Characteristics (what it's about/for)
    - tutorial, quickstart, troubleshooting, performance, ...

Common Mistakes:
  ❌ type: tutorial  →  ✅ type: guide, special: [tutorial]
  ❌ type: faq       →  ✅ type: reference, special: [faq]
  ❌ ["developer"]   →  ✅ [developer]

Validation:
  pwsh scripts/validate-tags-strict.ps1
```

---

## Migration Scripts

### Full Migration Script Package

**scripts/migrate-all-v1-to-v2.ps1:**

```powershell
# Master migration script - Runs all phases

param(
    [switch]$DryRun = $false,
    [switch]$SkipBackup = $false,
    [switch]$Verbose = $false
)

Write-Host "=== TAG TAXONOMY MIGRATION: v1.0 → v2.0 ===" -ForegroundColor Cyan
Write-Host ""

# Phase 0: Backup
if (-not $SkipBackup) {
    Write-Host "[Phase 0] Creating backup..." -ForegroundColor Yellow
    $backupPath = "T:\Project-AI-vault-migration-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item -Path "T:\Project-AI-vault" -Destination $backupPath -Recurse
    Write-Host "✅ Backup created: $backupPath`n" -ForegroundColor Green
}

# Phase 1: Templates
Write-Host "[Phase 1] Migrating templates..." -ForegroundColor Yellow
.\scripts\migrate-templates.ps1 -DryRun:$DryRun
Write-Host ""

# Phase 2: Metadata Examples
Write-Host "[Phase 2] Migrating metadata examples..." -ForegroundColor Yellow
.\scripts\migrate-examples.ps1 -DryRun:$DryRun
Write-Host ""

# Phase 3: Bulk Migration
Write-Host "[Phase 3] Bulk migration of all files..." -ForegroundColor Yellow
.\scripts\migrate-tags-v1-to-v2.ps1 -DryRun:$DryRun
Write-Host ""

# Phase 4: Validation
Write-Host "[Phase 4] Running validation..." -ForegroundColor Yellow
.\scripts\validate-tags-strict.ps1 -Verbose:$Verbose

Write-Host ""
Write-Host "=== MIGRATION COMPLETE ===" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "⚠️ DRY RUN MODE - No changes were made" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to apply migration"
}
```

**Usage:**

```powershell
# Test migration (no changes)
.\scripts\migrate-all-v1-to-v2.ps1 -DryRun -Verbose

# Execute migration
.\scripts\migrate-all-v1-to-v2.ps1

# Execute without backup (if you already have one)
.\scripts\migrate-all-v1-to-v2.ps1 -SkipBackup
```

---

## Rollback Plan

**If migration fails or causes issues:**

### Option 1: Restore from Backup

```powershell
# List backups
Get-ChildItem T:\ -Filter "Project-AI-vault-*-backup-*" | 
    Select-Object Name, CreationTime

# Restore specific backup
$backupPath = "T:\Project-AI-vault-migration-backup-20250123-143022"

# Move current (failed) version
Move-Item "T:\Project-AI-vault" "T:\Project-AI-vault-failed-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Restore backup
Copy-Item $backupPath "T:\Project-AI-vault" -Recurse

Write-Host "✅ Rollback complete"
```

### Option 2: Revert Individual Files

```powershell
# Git revert (if using version control)
git checkout HEAD -- templates/*.md
git checkout HEAD -- metadata-examples/*.md

# Or restore from backup selectively
Copy-Item "$backupPath\templates" "T:\Project-AI-vault\templates" -Recurse -Force
```

### Option 3: Cherry-Pick Good Changes

```powershell
# Compare backup vs current
$backup = "T:\Project-AI-vault-migration-backup-20250123-143022"
$current = "T:\Project-AI-vault"

# Use Beyond Compare or similar
# bc "$backup" "$current"

# Manually copy over successfully migrated files
```

---

## Validation

### Post-Migration Validation Checklist

- [ ] ✅ **All templates validate:**
  ```powershell
  Get-ChildItem templates/*.md | ForEach-Object {
      .\scripts\validate-tags-strict.ps1 $_.FullName
  }
  ```

- [ ] ✅ **All metadata examples validate:**
  ```powershell
  Get-ChildItem metadata-examples/*.md | ForEach-Object {
      .\scripts\validate-tags-strict.ps1 $_.FullName
  }
  ```

- [ ] ✅ **Overall compliance ≥ 90%:**
  ```powershell
  .\scripts\validate-tags-strict.ps1
  # Should show: Compliance: 90%+ (target)
  ```

- [ ] ✅ **No non-standard tags in use:**
  ```powershell
  # Check for common v1.0 patterns
  Get-ChildItem -Recurse *.md | Select-String -Pattern 'api_reference|Module|decision_record'
  # Should return no matches
  ```

- [ ] ✅ **Component field removed:**
  ```powershell
  Get-ChildItem -Recurse *.md | Select-String -Pattern '^component:'
  # Should return no matches
  ```

- [ ] ✅ **Quoted tags removed:**
  ```powershell
  Get-ChildItem -Recurse *.md | Select-String -Pattern '\["[^"]+"\]'
  # Should return no matches (except in code blocks)
  ```

- [ ] ✅ **Manual spot checks:**
  - Open 5 random migrated files
  - Verify frontmatter looks correct
  - Verify content mentions correct tag names
  - Verify no broken links or references

---

## Success Criteria

**Migration is successful when:**

1. ✅ **Compliance ≥ 90%**
   - 90%+ of files pass strict validation
   - <10% of files need manual fixes

2. ✅ **Zero non-standard tags**
   - All tags in use exist in tag-hierarchy.json v2.0
   - No v1.0 deprecated tags remain

3. ✅ **Validation enforced**
   - CI/CD blocks non-compliant PRs
   - Pre-commit hook active
   - Team trained on v2.0

4. ✅ **Documentation updated**
   - TAG_TAXONOMY.md superseded by TAG_TAXONOMY_V2.md
   - tag-hierarchy.json updated to v2.0
   - Templates reference v2.0
   - Examples demonstrate v2.0

5. ✅ **No regressions**
   - All existing links still work
   - Obsidian vault loads without errors
   - Search/navigation functions correctly

---

## Timeline Summary

| Week | Phase | Effort | Deliverables |
|------|-------|--------|--------------|
| Week 1 | Fix Templates | 2 hours | 4 templates compliant |
| Week 1-2 | Fix Examples | 4 hours | 20 examples compliant |
| Week 2 | Deploy Validation | 3 hours | CI/CD + scripts active |
| Week 3 | Bulk Migration | 2 hours + review | All files migrated |
| Week 4 | Enforcement + Training | 4 hours | Team trained, hooks active |
| **Total** | **4 weeks** | **15 hours** | **v2.0 fully deployed** |

---

## Support

**Questions or issues during migration?**

- **Documentation:** TAG_TAXONOMY_V2.md, TAG_USAGE_ANALYSIS.md
- **Scripts:** scripts/validate-tags-strict.ps1, scripts/migrate-all-v1-to-v2.ps1
- **Contact:** AGENT-039 (Tag Taxonomy Refinement Specialist)
- **Escalation:** See TAG_USAGE_ANALYSIS.md recommendations section

---

**Migration Prepared By:** AGENT-039  
**Date:** 2025-01-23  
**Status:** Ready for Implementation  
**Version:** 1.0

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

