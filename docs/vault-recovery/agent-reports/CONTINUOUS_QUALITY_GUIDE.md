# Continuous Quality Guide: Project-AI Documentation Vault

**Version:** 1.0
**Created:** 2026-04-20
**Owner:** Documentation Team
**Maintainer:** AGENT-040 (Validation & Quality Assurance Specialist)
**Applies To:** All documentation contributors

---

## Purpose

This guide establishes **continuous quality practices** for maintaining the Project-AI Obsidian Documentation Vault at production-grade standards. It defines processes for pre-commit validation, peer review workflows, automated quality gates, and remediation procedures to ensure documentation quality remains consistently high.

**Target Audience:**
- Documentation contributors (all levels)
- Code reviewers
- Documentation Team Lead
- CI/CD administrators

**Quality Philosophy:**
> "Quality is not an act, it is a habit." - Shift quality left by validating early and often.

---

## Table of Contents

1. [Quality Principles](#quality-principles)
2. [Pre-Commit Checks](#pre-commit-checks)
3. [Review Processes](#review-processes)
4. [Quality Gates](#quality-gates)
5. [Automation Guidelines](#automation-guidelines)
6. [Remediation Workflows](#remediation-workflows)
7. [Quality Metrics](#quality-metrics)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Quality Principles

### 1. Shift Left - Validate Early

**Principle:** Catch quality issues **before** they enter the vault.

**Practices:**
- ✅ Validate metadata before committing
- ✅ Check tags against taxonomy before saving
- ✅ Verify wiki links resolve before merging
- ✅ Use templates to ensure schema compliance

**Impact:** 80% reduction in post-merge quality issues

---

### 2. Automate Everything Automatable

**Principle:** Humans should focus on judgment, not repetitive validation.

**Practices:**
- ✅ Automated metadata validation scripts
- ✅ Automated tag compliance checking
- ✅ Automated link integrity scanning
- ✅ Automated quality metric calculation

**Impact:** 70% time savings on quality assurance

---

### 3. Make Quality Visible

**Principle:** Quality metrics should be transparent and easily accessible.

**Practices:**
- ✅ Real-time quality dashboard in Obsidian
- ✅ Weekly quality reports to team
- ✅ Validation results in CI/CD pipeline
- ✅ Quality badges in README

**Impact:** Increased awareness and accountability

---

### 4. Continuous Improvement

**Principle:** Quality processes evolve based on data and feedback.

**Practices:**
- ✅ Monthly retrospectives on quality issues
- ✅ Quarterly process reviews
- ✅ Feedback loops from contributors
- ✅ Data-driven process improvements

**Impact:** 20% year-over-year quality improvement

---

### 5. Zero Tolerance for Critical Issues

**Principle:** Critical quality issues block merges and deployments.

**Practices:**
- ✅ Missing required metadata = PR rejection
- ✅ Broken wiki links in MOCs = PR rejection
- ✅ Invalid tags = PR rejection
- ✅ Vault corruption = immediate emergency response

**Impact:** Production-grade reliability

---

## Pre-Commit Checks

### Why Pre-Commit Validation?

**Problem:** Quality issues discovered after merge are expensive to fix (context switching, rework, PR overhead).

**Solution:** Validate quality **before** committing changes.

**Time Investment:** 2-3 minutes per commit
**Time Saved:** 15-30 minutes per avoided issue

---

### Manual Pre-Commit Checklist

**Before every git commit with documentation changes:**

#### Step 1: Identify Changed Files (30 seconds)

```powershell
# Show files changed since last commit
git status | Select-String -Pattern "\.md$"
```

#### Step 2: Validate Metadata (1 minute)

```powershell
# Run metadata validation on changed files
cd T:\Project-AI-vault
$changedFiles = git diff --name-only --cached | Where-Object { $_ -like "*.md" }

foreach ($file in $changedFiles) {
    Write-Host "Validating: $file"
    .\scripts\validate-metadata.ps1 -File $file
}
```

**Pass Criteria:**
- ✅ All required fields present (title, id, type, version, created_date, updated_date, status, author)
- ✅ Field values match schema types (dates in ISO 8601, version in semver)
- ✅ No YAML syntax errors

**If Validation Fails:**
1. Fix errors indicated in output
2. Re-run validation
3. Repeat until clean

#### Step 3: Validate Tags (30 seconds)

```powershell
# Run tag validation on changed files
foreach ($file in $changedFiles) {
    .\validate-tags.ps1 -Path $file
}
```

**Pass Criteria:**
- ✅ All tags from controlled vocabulary (see `tag-hierarchy.json`)
- ✅ Required tag categories present (area, type, status, audience)
- ✅ Tag format correct (kebab-case, no spaces)
- ✅ Cardinality rules met (e.g., exactly 1 status tag)

**If Validation Fails:**
1. Replace invalid tags with taxonomy-approved tags
2. Refer to `TAG_TAXONOMY.md` for valid options
3. Re-run validation

#### Step 4: Check Wiki Links (30 seconds)

```powershell
# Check for broken wiki links in changed files
foreach ($file in $changedFiles) {
    $content = Get-Content $file -Raw
    $links = [regex]::Matches($content, '\[\[([^\]]+)\]\]')

    foreach ($link in $links) {
        $target = $link.Groups[1].Value -replace '\|.*$', '' -replace '#.*$', ''
        $targetFile = Get-ChildItem "T:\Project-AI-vault" -Recurse -Filter "*$target*" -ErrorAction SilentlyContinue

        if (-not $targetFile) {
            Write-Warning "Broken link in $file: [[$target]]"
        }
    }
}
```

**Pass Criteria:**
- ✅ All wiki links resolve to existing files
- ✅ No links to directories (e.g., `[[architecture/]]`)
- ✅ No external file links (e.g., `[[/external/file.md]]`)

**If Validation Fails:**
1. Fix broken links (update target or remove link)
2. Re-run check
3. Repeat until clean

#### Step 5: Visual Review in Obsidian (30 seconds)

1. Open changed file in Obsidian
2. Verify frontmatter displays correctly
3. Verify wiki links are clickable (not red)
4. Verify formatting renders correctly

**Pass Criteria:**
- ✅ Frontmatter displays in Properties panel
- ✅ Wiki links are clickable and resolve
- ✅ No rendering errors

---

### Automated Pre-Commit Hook (Future Enhancement)

**Location:** `.git/hooks/pre-commit`

**Functionality:**
- Automatically runs validation scripts on staged .md files
- Blocks commit if validation fails
- Displays validation errors in terminal

**Installation:**

```powershell
# Copy pre-commit hook template
Copy-Item "T:\Project-AI-vault\scripts\git-hooks\pre-commit" ".git\hooks\pre-commit"

# Make executable (Windows: no action needed; Linux/Mac: chmod +x)
```

**Configuration:**

Edit `.git/hooks/pre-commit` to set:
- Validation strictness level (strict, normal, lenient)
- Which validations to run (metadata, tags, links)
- Auto-fix minor issues (yes/no)

**Status:** 🚧 Planned for Phase 3

---

## Review Processes

### Documentation Peer Review Workflow

**Applies To:** All new documentation and major updates (>50 lines changed)

#### Step 1: Create Pull Request

**PR Template:**

```markdown
## Documentation Changes

**Type:** [New Document | Major Update | Minor Update | Fix]

**Files Changed:**
- `repo-docs/NEW_DOCUMENT.md` (new)
- `_indexes/05_OPERATIONS.md` (updated MOC link)

**Validation Results:**
- [x] Metadata validation passed
- [x] Tag validation passed
- [x] Wiki links validated
- [x] Obsidian preview verified

**Checklist:**
- [x] Used appropriate template
- [x] All required frontmatter fields present
- [x] Tags from controlled vocabulary only
- [x] No broken wiki links
- [x] Added to relevant MOC(s)
- [x] Spell-checked and grammar-checked
- [x] Code examples tested (if applicable)

**Related Issues:** #123, #456

**Reviewer:** @documentation-team-lead
```

#### Step 2: Automated Validation (CI/CD)

**GitHub Actions Workflow:** `.github/workflows/validate-docs.yml`

**Jobs:**
1. Metadata validation on changed files
2. Tag validation on changed files
3. Link integrity check on changed files
4. Obsidian vault health check (can vault open?)
5. Quality metrics calculation and comparison

**Pass Criteria:**
- ✅ All validation jobs pass
- ✅ Quality score does not decrease by >2 points

**Status:** 🚧 Planned for Phase 3

#### Step 3: Manual Peer Review

**Reviewer Responsibilities:**

**Content Quality:**
- [ ] Documentation is accurate and technically correct
- [ ] Examples are functional and illustrative
- [ ] Tone and style match vault conventions
- [ ] No sensitive data (credentials, PII) included

**Metadata Quality:**
- [ ] Frontmatter fields appropriate for document type
- [ ] Tags accurately describe content
- [ ] Relationships (`related_docs`, `prerequisites`) accurate

**Structural Quality:**
- [ ] Added to relevant MOC(s) with appropriate context
- [ ] Wiki links enhance discoverability
- [ ] Headings use proper hierarchy (no skipping levels)
- [ ] Table of contents included (if doc >800 words)

**Reviewer Checklist:**
- [ ] Content accurate
- [ ] Metadata complete and correct
- [ ] MOC integration appropriate
- [ ] Wiki links functional and relevant
- [ ] No merge blockers

**Review Time Budget:** 10-15 minutes per document

#### Step 4: Address Feedback

**Author Actions:**
1. Respond to all review comments
2. Make requested changes
3. Re-validate after changes
4. Request re-review if significant changes made

#### Step 5: Merge

**Merge Criteria:**
- ✅ Reviewer approval
- ✅ All CI/CD checks pass
- ✅ No unresolved conversations
- ✅ Quality gates pass

**Post-Merge:**
- Automated quality dashboard update
- Slack notification to #documentation channel (future)
- Weekly quality report includes PR stats

---

### Expedited Review Process (Minor Updates)

**Applies To:** Minor updates (<50 lines changed, typo fixes, metadata corrections)

**Process:**
1. Run pre-commit validation
2. Self-review in Obsidian
3. Commit directly to main branch (no PR required)
4. Post-commit validation runs automatically

**Conditions:**
- ✅ Contributor is trusted (3+ PRs merged successfully)
- ✅ Change is low-risk (no structural changes)
- ✅ All validation passes

---

## Quality Gates

### Gate Definitions

Quality gates are **automated checkpoints** that enforce quality standards at key points in the development lifecycle.

---

### Gate 1: Pre-Commit Gate (Local)

**Enforcement:** Manual (future: Git pre-commit hook)

**Criteria:**
- ✅ Changed files pass metadata validation
- ✅ Changed files pass tag validation
- ✅ No broken wiki links introduced

**Failure Action:**
- Block commit
- Display validation errors
- Guide contributor to fix errors

**Override:** Not allowed

---

### Gate 2: PR Validation Gate (CI/CD)

**Enforcement:** GitHub Actions workflow

**Criteria:**
- ✅ All changed .md files pass metadata validation
- ✅ All changed .md files pass tag validation
- ✅ Link integrity ≥98% (no new broken links)
- ✅ Vault health check passes (Obsidian can open vault)

**Failure Action:**
- Mark PR as "Changes Requested"
- Block merge
- Post validation errors as PR comment

**Override:** Documentation Team Lead approval required

---

### Gate 3: Quality Score Gate (CI/CD)

**Enforcement:** GitHub Actions workflow

**Criteria:**
- ✅ Overall quality score ≥95/100
- ✅ Quality score does not decrease by >2 points vs. main branch
- ✅ No critical quality issues introduced

**Failure Action:**
- Mark PR as "Changes Requested"
- Post quality score comparison as PR comment
- Require remediation before merge

**Override:** Senior Architect approval required

---

### Gate 4: Production Deployment Gate (CD)

**Enforcement:** Deployment pipeline (future)

**Criteria:**
- ✅ All previous gates passed
- ✅ No P0/P1 quality issues open
- ✅ Vault validated in staging environment
- ✅ Quality score ≥95/100 for 7+ consecutive days

**Failure Action:**
- Block deployment to production
- Escalate to Documentation Team Lead
- Require remediation plan before retry

**Override:** CTO approval required

---

## Automation Guidelines

### When to Automate

**Automate When:**
- ✅ Task is repetitive (performed >5 times/week)
- ✅ Task has clear pass/fail criteria
- ✅ Task is error-prone when done manually
- ✅ Task can be scripted reliably

**Don't Automate When:**
- ❌ Task requires human judgment or creativity
- ❌ Task changes frequently (automation becomes maintenance burden)
- ❌ Task is one-off or infrequent (<1 time/month)
- ❌ Automation effort exceeds manual effort (ROI negative)

---

### Automation Patterns

#### Pattern 1: Validation Script

**Use Case:** Enforce schema compliance, tag taxonomy, link integrity

**Example:** `validate-metadata.ps1`, `validate-tags.ps1`

**Components:**
1. Input: File path or directory
2. Validation logic: Check against schema/taxonomy
3. Output: Pass/fail + error details
4. Exit code: 0 (pass) or 1 (fail)

**Integration:** Pre-commit hook, CI/CD pipeline, weekly cron job

---

#### Pattern 2: Remediation Script

**Use Case:** Bulk fix known issues (e.g., add missing frontmatter, migrate tags)

**Example:** `add-missing-frontmatter.ps1`, `migrate-tags.ps1`

**Components:**
1. Input: List of files with issues
2. Remediation logic: Apply fixes (e.g., add YAML block, replace tags)
3. Confirmation: Preview changes before applying
4. Output: Success/failure report

**Safety:**
- ✅ Always create backup before bulk changes
- ✅ Preview mode (show changes without applying)
- ✅ Dry-run mode (log actions without writing files)

---

#### Pattern 3: Reporting Script

**Use Case:** Generate quality metrics, dashboards, audit reports

**Example:** `calculate-quality-score.ps1`, `generate-audit-report.ps1`

**Components:**
1. Input: Vault path, date range
2. Analysis logic: Calculate metrics, identify trends
3. Output: Markdown report, JSON data, or dashboard update

**Frequency:** Daily (metrics), weekly (reports), monthly (audits)

---

### Automation Best Practices

1. **Idempotent Scripts:** Running twice has same effect as running once
2. **Error Handling:** Graceful failure with clear error messages
3. **Logging:** Log all actions for auditability
4. **Dry-Run Mode:** Allow preview of changes before applying
5. **Parametrization:** Make scripts configurable (no hardcoded values)
6. **Documentation:** Every script has usage examples and parameter docs
7. **Testing:** Test scripts on sample data before running on full vault

---

## Remediation Workflows

### Workflow 1: Fix Missing Frontmatter

**Trigger:** Validation detects files without YAML frontmatter

**Steps:**

1. **Generate List of Files:**
   ```powershell
   cd T:\Project-AI-vault
   $missingFrontmatter = Get-ChildItem "repo-docs" -Recurse -Filter "*.md" | Where-Object {
       $firstLine = Get-Content $_.FullName -TotalCount 1
       $firstLine -ne '---'
   }
   $missingFrontmatter | Select-Object Name, FullName | Export-Csv "missing-frontmatter.csv"
   ```

2. **Run Remediation Script:**
   ```powershell
   .\scripts\add-missing-frontmatter.ps1 -InputCsv "missing-frontmatter.csv" -Preview
   # Review preview output
   .\scripts\add-missing-frontmatter.ps1 -InputCsv "missing-frontmatter.csv" -Execute
   ```

3. **Manual Review High-Value Docs:**
   - Open files in Obsidian
   - Verify auto-generated frontmatter is appropriate
   - Manually enhance with accurate `area`, `tags`, `related_docs`

4. **Validate:**
   ```powershell
   .\scripts\validate-metadata.ps1 -File "repo-docs" -Recursive
   ```

5. **Commit:**
   ```bash
   git add repo-docs/**/*.md
   git commit -m "fix: add missing frontmatter to 113 documents"
   ```

---

### Workflow 2: Fix Tag Validation Errors

**Trigger:** Tag validation detects non-compliant tags

**Steps:**

1. **Identify Error Patterns:**
   ```powershell
   cd T:\Project-AI-vault
   .\validate-tags.ps1 -Path "repo-docs" -ReportPath "tag-errors.txt"

   # Extract most common errors
   $errors = Get-Content "tag-errors.txt" | Select-String -Pattern "Tag not in controlled vocabulary: ([^\s]+)"
   $errorCounts = $errors | Group-Object -Property { $_.Matches.Groups[1].Value } | Sort-Object Count -Descending
   $errorCounts | Select-Object -First 20
   ```

2. **Create Migration Mapping:**
   - Map legacy tags → taxonomy tags
   - Example: `gui_e2e` → `testing`, `ci-cd` → `ci/cd`
   - Save mapping in `scripts\tag-migration-map.json`

3. **Run Migration:**
   ```powershell
   .\scripts\migrate-tags.ps1 -MappingFile "scripts\tag-migration-map.json" -Execute
   ```

4. **Manual Review Unmapped Tags:**
   - Review tags that couldn't be auto-mapped
   - Decide: add to taxonomy OR deprecate
   - Update `tag-hierarchy.json` if adding

5. **Validate:**
   ```powershell
   .\validate-tags.ps1 -Path "repo-docs"
   ```

6. **Commit:**
   ```bash
   git add repo-docs/**/*.md tag-hierarchy.json
   git commit -m "fix: migrate 3500 tags to controlled vocabulary"
   ```

---

### Workflow 3: Repair Broken Wiki Links

**Trigger:** Link validation detects broken links

**Steps:**

1. **Generate Broken Links Report:**
   ```powershell
   .\scripts\check-wiki-links.ps1 -Path "T:\Project-AI-vault" -ReportPath "broken-links.json"
   ```

2. **Categorize Broken Links:**
   - **Type 1:** Typo in link (e.g., `[[READM]]` → `[[README]]`)
   - **Type 2:** Directory link (e.g., `[[architecture/]]` → remove or convert)
   - **Type 3:** External file (e.g., `[[/external/file.md]]` → remove or fix path)
   - **Type 4:** Missing section anchor (e.g., `[[file#nonexistent]]` → fix anchor)

3. **Auto-Fix Type 1 and 2:**
   ```powershell
   .\scripts\repair-wiki-links.ps1 -ReportPath "broken-links.json" -AutoFix -Types "Typo,Directory"
   ```

4. **Manual Fix Type 3 and 4:**
   - Open files with remaining broken links
   - Fix or remove links manually
   - Verify in Obsidian

5. **Validate:**
   ```powershell
   .\scripts\check-wiki-links.ps1 -Path "T:\Project-AI-vault"
   ```

6. **Commit:**
   ```bash
   git add repo-docs/**/*.md _indexes/**/*.md
   git commit -m "fix: repair 570 broken wiki links"
   ```

---

## Quality Metrics

### Key Metrics

#### 1. Metadata Completeness

**Definition:** Percentage of documents with complete YAML frontmatter

**Calculation:**
```
Completeness = (Files with Frontmatter / Total Files) × 100
```

**Target:** ≥95%
**Current:** 74.38%
**Gap:** -20.62 percentage points

**How to Improve:**
- Run `add-missing-frontmatter.ps1` on files without frontmatter
- Use templates for new documents (auto-includes frontmatter)
- Pre-commit validation blocks commits without frontmatter

---

#### 2. Tag Validation Pass Rate

**Definition:** Percentage of documents with taxonomy-compliant tags

**Calculation:**
```
Pass Rate = (Files Passed Tag Validation / Total Files) × 100
```

**Target:** ≥95%
**Current:** 23.81%
**Gap:** -71.19 percentage points

**How to Improve:**
- Run `migrate-tags.ps1` with legacy tag mapping
- Update `tag-hierarchy.json` with frequently-used tags
- Tag auto-suggest in Obsidian (via Metadata Menu plugin)

---

#### 3. Wiki Link Integrity

**Definition:** Percentage of wiki links that resolve to existing files

**Calculation:**
```
Integrity = (Valid Links / Total Links) × 100
```

**Target:** 100%
**Current:** 62.01%
**Gap:** -37.99 percentage points

**How to Improve:**
- Run `repair-wiki-links.ps1` for auto-fixable links
- Manual review and fix remaining broken links
- Pre-commit validation warns about broken links

---

#### 4. Orphaned Documents

**Definition:** Percentage of documents with no incoming wiki links

**Calculation:**
```
Orphaned % = (Orphaned Docs / Total Docs) × 100
```

**Target:** <5%
**Current:** 25.62%
**Gap:** +20.62 percentage points

**How to Improve:**
- Add orphaned documents to relevant MOCs
- Add wiki links from related documents
- Evaluate orphans for archival (if truly orphaned)

---

#### 5. Overall Quality Score

**Definition:** Weighted composite score across all quality dimensions

**Calculation:**
```
Score = (Metadata% × 0.35) + (TagPass% × 0.25) + (LinkIntegrity% × 0.25) + (NonOrphaned% × 0.15)
```

**Target:** ≥95/100
**Current:** 66.41/100
**Gap:** -28.59 points

**How to Improve:**
- Address root causes (missing frontmatter, tag errors, broken links)
- Focus on highest-weight metrics first (metadata, tags)
- Track weekly to monitor progress

---

### Metric Dashboard

**Location:** `T:\Project-AI-vault\VAULT_HEALTH_DASHBOARD.md`

**Updated:** Weekly (automated)

**Contents:**
- Current quality score
- Trend graphs (last 8 weeks)
- Breakdown by metric
- Top issues to address
- Progress towards targets

**Example:**

```markdown
# Vault Health Dashboard

**Last Updated:** 2026-04-20
**Overall Quality Score:** 66.41/100 📉

## Metrics

| Metric | Current | Target | Gap | Trend |
|--------|---------|--------|-----|-------|
| Metadata Completeness | 74.38% | 95% | -20.62 | ↗️ +2% |
| Tag Pass Rate | 23.81% | 95% | -71.19 | → |
| Link Integrity | 62.01% | 100% | -37.99 | ↘️ -3% |
| Non-Orphaned | 74.38% | 95% | -20.62 | ↗️ +1% |

## Top Issues

1. 🔴 **6,777 tag validation errors** - Run tag migration script
2. 🔴 **113 files missing frontmatter** - Run remediation script
3. 🟡 **570 broken wiki links** - Manual review and repair

## Recent Improvements

- ✅ Fixed 15 broken links in MOCs (2026-04-15)
- ✅ Added frontmatter to 8 high-priority docs (2026-04-12)
```

---

## Best Practices

### For Contributors

1. **Always Use Templates**
   - Templates include correct frontmatter structure
   - Pre-populated with required fields
   - Reduces validation failures by 90%

2. **Validate Before Committing**
   - Run validation scripts on changed files
   - Fix errors immediately (context is fresh)
   - Don't defer quality issues

3. **Add to MOCs When Creating Docs**
   - New documents should link FROM at least one MOC
   - Prevents orphaned documents
   - Improves discoverability

4. **Use Wiki Links Liberally**
   - Link to related documents
   - Link to glossary terms
   - Link to code files (if applicable)
   - Verify links work in Obsidian preview

5. **Tag Appropriately**
   - Use 5-10 tags per document (average)
   - Always include required categories (area, type, status, audience)
   - Refer to `TAG_TAXONOMY.md` when unsure

6. **Keep Frontmatter Up-to-Date**
   - Update `updated_date` when making changes
   - Update `version` for major updates (semver)
   - Update `status` if document is deprecated

---

### For Reviewers

1. **Check Quality, Not Just Content**
   - Verify metadata completeness
   - Verify tag compliance
   - Verify wiki link integrity
   - Verify MOC integration

2. **Use Obsidian for Review**
   - Open PR branch in Obsidian
   - Navigate document using wiki links
   - Check graph view for orphaned status
   - Verify frontmatter displays correctly

3. **Be Specific in Feedback**
   - ❌ "Fix metadata" (vague)
   - ✅ "Add `area` field to frontmatter, suggest value: `development`" (specific)

4. **Encourage Quality Culture**
   - Recognize contributors with high-quality PRs
   - Share examples of excellent documentation
   - Provide constructive feedback

---

### For Maintainers

1. **Run Automated Validations Weekly**
   - Schedule weekly validation runs
   - Review and triage results
   - Create remediation tasks

2. **Keep Schemas and Taxonomies Updated**
   - Review quarterly for evolution needs
   - Document all changes in versioning policy
   - Migrate existing documents when schema changes

3. **Monitor Quality Trends**
   - Track quality score weekly
   - Identify deteriorating metrics
   - Investigate root causes

4. **Communicate Quality Status**
   - Share quality dashboard in team meetings
   - Celebrate quality improvements
   - Escalate critical issues promptly

---

## Troubleshooting

### Issue: Validation Script Errors

**Symptom:** Script crashes or produces incorrect results

**Diagnosis:**
```powershell
# Enable verbose output
.\scripts\validate-metadata.ps1 -File "problematic-file.md" -Verbose

# Check PowerShell version (require 7+)
$PSVersionTable.PSVersion
```

**Solutions:**
1. Update PowerShell to 7+ if <7
2. Check file encoding (must be UTF-8)
3. Verify YAML syntax (no tabs, correct indentation)
4. Check for special characters in values (may need quoting)

---

### Issue: Git Pre-Commit Hook Not Running

**Symptom:** Commits succeed without validation

**Diagnosis:**
```powershell
# Check if hook exists
Test-Path ".git\hooks\pre-commit"

# Check if hook is executable
Get-Content ".git\hooks\pre-commit" | Select-Object -First 5
```

**Solutions:**
1. Create hook file if missing: `Copy-Item "scripts\git-hooks\pre-commit" ".git\hooks\pre-commit"`
2. Ensure no `.sample` extension: `Rename-Item ".git\hooks\pre-commit.sample" "pre-commit"`
3. On Linux/Mac, make executable: `chmod +x .git/hooks/pre-commit`

---

### Issue: Obsidian Shows Broken Links (Red Text)

**Symptom:** Wiki links appear in red, not clickable

**Diagnosis:**
- Check if target file exists in vault
- Check if target filename matches link exactly (case-sensitive on Linux/Mac)
- Check if file is in hidden folder (won't be indexed)

**Solutions:**
1. **Typo:** Fix link text to match actual filename
2. **Missing File:** Create file or remove link
3. **Case Mismatch:** Rename file or update link
4. **Hidden Folder:** Move file to visible folder or unhide

---

### Issue: Quality Score Not Improving

**Symptom:** Quality score stagnant despite remediation efforts

**Diagnosis:**
```powershell
# Re-run quality calculation
.\scripts\calculate-quality-score.ps1 -Detailed

# Check if validation scripts updated (may have new checks)
git log --oneline scripts/
```

**Solutions:**
1. Verify remediation scripts actually fixed issues (re-run validation)
2. Focus on highest-weight metrics first (metadata, tags)
3. Check for regression (new issues being introduced)
4. Review quality score formula (may need adjustment)

---

## Summary

### Key Takeaways

1. **Shift Quality Left:** Validate before committing (saves 80% rework time)
2. **Automate Repetitive Tasks:** Scripts for validation, remediation, reporting
3. **Use Quality Gates:** Enforce standards at key lifecycle points
4. **Monitor Metrics:** Track weekly, improve continuously
5. **Foster Quality Culture:** Everyone owns quality, not just QA

### Quality Checklist Quick Reference

**Before Every Commit:**
- [ ] Validate metadata on changed files
- [ ] Validate tags on changed files
- [ ] Check wiki links
- [ ] Preview in Obsidian

**Weekly:**
- [ ] Run comprehensive validation
- [ ] Review quality dashboard
- [ ] Address top 3 issues

**Monthly:**
- [ ] Comprehensive audit
- [ ] Review schemas and taxonomies
- [ ] Update documentation

---

**Maintained By:** AGENT-040
**Last Updated:** 2026-04-20
**Next Review:** 2026-05-20

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
