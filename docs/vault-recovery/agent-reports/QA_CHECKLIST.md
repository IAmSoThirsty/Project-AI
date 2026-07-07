# Project-AI Vault Quality Assurance Checklist

**Version:** 1.0  
**Created:** 2026-04-20  
**Owner:** Documentation Team  
**Maintainer:** AGENT-040 (Validation & Quality Assurance Specialist)  
**Review Cadence:** Monthly

---

## Purpose

This QA checklist defines daily, weekly, and monthly quality assurance procedures for the Project-AI Obsidian Documentation Vault. It ensures continuous quality monitoring, early detection of issues, and proactive maintenance of vault health.

**Scope:**
- 441+ repository documentation files
- 19+ MOC/index files
- Metadata schema compliance
- Tag taxonomy adherence
- Wiki link integrity
- Obsidian infrastructure health

---

## Table of Contents

1. [Daily Checks](#daily-checks)
2. [Weekly Checks](#weekly-checks)
3. [Monthly Audits](#monthly-audits)
4. [Quarterly Reviews](#quarterly-reviews)
5. [Automated vs Manual Tasks](#automated-vs-manual-tasks)
6. [Quality Gates](#quality-gates)
7. [Issue Escalation](#issue-escalation)

---

## Daily Checks

**Frequency:** Every day before close of business  
**Time Required:** 5-10 minutes  
**Owner:** Any contributor who made documentation changes that day  
**Automation Level:** 80% automated

### Checklist

#### 1. New/Modified Files Validation

**Automated:**
- [ ] Run `validate-metadata.ps1` on files changed today
- [ ] Run `validate-tags.ps1` on files changed today
- [ ] Check for broken wiki links in changed files

**Command:**
```powershell
cd T:\Project-AI-vault
$today = (Get-Date).Date
$changedFiles = git diff --name-only HEAD@{1} HEAD | Where-Object { $_ -like "*.md" }

foreach ($file in $changedFiles) {
    .\scripts\validate-metadata.ps1 -File $file
    .\validate-tags.ps1 -Path $file
}
```

**Manual:**
- [ ] Review validation output for errors
- [ ] Fix any errors found before end of day
- [ ] Commit fixes with message: "fix: metadata/tag validation for [filename]"

**Pass Criteria:**
- ✅ Zero validation errors on changed files
- ✅ All required frontmatter fields present
- ✅ All tags from controlled vocabulary
- ✅ No broken wiki links introduced

---

#### 2. Git Status Check

**Automated:**
- [ ] Check for uncommitted changes
- [ ] Check for merge conflicts

**Command:**
```powershell
git status
git log --oneline -5
```

**Manual:**
- [ ] Review uncommitted changes
- [ ] Ensure no sensitive data in commits
- [ ] Verify commit messages follow convention

**Pass Criteria:**
- ✅ No uncommitted changes at end of day
- ✅ All commits have descriptive messages
- ✅ No merge conflicts

---

#### 3. Obsidian Health Check

**Automated:**
- [ ] Verify Obsidian vault opens without errors
- [ ] Check for plugin errors in console

**Manual:**
- [ ] Open vault in Obsidian
- [ ] Verify no error dialogs
- [ ] Check console (Ctrl+Shift+I) for errors

**Pass Criteria:**
- ✅ Vault opens cleanly (<5 seconds)
- ✅ No error dialogs
- ✅ No console errors

---

## Weekly Checks

**Frequency:** Every Monday morning  
**Time Required:** 30-45 minutes  
**Owner:** Documentation Team Lead or designated QA person  
**Automation Level:** 60% automated

### Checklist

#### 1. Comprehensive Metadata Validation

**Automated:**
- [ ] Run `validate-metadata.ps1` on entire `repo-docs/` directory
- [ ] Generate validation report JSON
- [ ] Compare with previous week's results

**Command:**
```powershell
cd T:\Project-AI-vault\scripts
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
.\validate-metadata.ps1 -File "T:\Project-AI-vault\repo-docs" -Recursive `
    -OutputFormat JSON `
    -ReportPath "T:\Project-AI-vault\validation-reports\metadata-$timestamp.json"

# Compare with previous week
$current = Get-Content "T:\Project-AI-vault\validation-reports\metadata-$timestamp.json" | ConvertFrom-Json
$previous = Get-Content (Get-ChildItem "T:\Project-AI-vault\validation-reports" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 1 -First 1).FullName | ConvertFrom-Json

Write-Output "=== WEEKLY COMPARISON ==="
Write-Output "Errors: $($current.totalErrors) (prev: $($previous.totalErrors)) - Delta: $($current.totalErrors - $previous.totalErrors)"
Write-Output "Pass Rate: $($current.passRate)% (prev: $($previous.passRate)%) - Delta: $($current.passRate - $previous.passRate)%"
```

**Manual:**
- [ ] Review validation report
- [ ] Identify top 5 most common errors
- [ ] Create remediation tasks in backlog if error count increased

**Pass Criteria:**
- ✅ Metadata pass rate ≥ 95%
- ✅ Total errors trending downward (or stable at <50)
- ✅ No new error categories introduced

---

#### 2. Tag Taxonomy Compliance

**Automated:**
- [ ] Run `validate-tags.ps1` on entire vault
- [ ] Generate tag validation report
- [ ] Identify tags not in controlled vocabulary

**Command:**
```powershell
cd T:\Project-AI-vault
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
.\validate-tags.ps1 -Path "T:\Project-AI-vault\repo-docs" `
    -ReportPath "validation-reports\tags-$timestamp.txt" `
    -OutputFormat Text

# Extract uncontrolled tags
$report = Get-Content "validation-reports\tags-$timestamp.txt" -Raw
$uncontrolledTags = [regex]::Matches($report, 'Tag not in controlled vocabulary: ([^\s]+)') | 
    ForEach-Object { $_.Groups[1].Value } | 
    Sort-Object -Unique

Write-Output "=== UNCONTROLLED TAGS DETECTED ==="
$uncontrolledTags
```

**Manual:**
- [ ] Review uncontrolled tags
- [ ] Decide: add to taxonomy OR mark for deprecation
- [ ] Update `tag-hierarchy.json` if adding tags
- [ ] Create migration tasks for deprecated tags

**Pass Criteria:**
- ✅ Tag validation pass rate ≥ 95%
- ✅ <10 uncontrolled tags in use
- ✅ All high-frequency tags in controlled vocabulary

---

#### 3. Wiki Link Integrity Check

**Automated:**
- [ ] Scan all markdown files for wiki links
- [ ] Validate each link target exists
- [ ] Generate broken link report

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\check-wiki-links.ps1 -Path "T:\Project-AI-vault" -Recursive `
    -ReportPath "validation-reports\links-$(Get-Date -Format 'yyyyMMdd').json"

# Summary
$report = Get-Content "validation-reports\links-$(Get-Date -Format 'yyyyMMdd').json" | ConvertFrom-Json
Write-Output "=== LINK INTEGRITY REPORT ==="
Write-Output "Total Links: $($report.totalLinks)"
Write-Output "Broken Links: $($report.brokenLinks)"
Write-Output "Integrity: $([math]::Round((1 - ($report.brokenLinks / $report.totalLinks)) * 100, 2))%"
```

**Manual:**
- [ ] Review broken links report
- [ ] Categorize broken links (external, typo, missing file)
- [ ] Fix critical broken links (in MOCs, high-traffic docs)
- [ ] Create repair tasks for remaining broken links

**Pass Criteria:**
- ✅ Link integrity ≥ 98%
- ✅ Zero broken links in MOC files
- ✅ Zero broken links in high-priority documents

---

#### 4. Orphaned Documents Detection

**Automated:**
- [ ] Identify documents with no incoming links
- [ ] Identify documents with no outgoing links
- [ ] Identify documents with no frontmatter

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\detect-orphans.ps1 -Path "T:\Project-AI-vault\repo-docs" `
    -ReportPath "validation-reports\orphans-$(Get-Date -Format 'yyyyMMdd').txt"

$report = Get-Content "validation-reports\orphans-$(Get-Date -Format 'yyyyMMdd').txt" -Raw
Write-Output $report
```

**Manual:**
- [ ] Review orphaned documents list
- [ ] Evaluate each orphan: integrate OR archive
- [ ] Add wiki links to orphans from relevant MOCs
- [ ] Add frontmatter to orphans without metadata

**Pass Criteria:**
- ✅ <5% orphaned documents (target: <22 files)
- ✅ All orphans reviewed and categorized
- ✅ High-value orphans integrated into vault structure

---

#### 5. MOC Coverage Review

**Automated:**
- [ ] Count documents linked from each MOC
- [ ] Identify MOCs with <10 links
- [ ] Identify domains with no MOC

**Command:**
```powershell
cd T:\Project-AI-vault
$mocs = Get-ChildItem "_indexes" -Filter "*.md" | Where-Object { $_.Name -like "*_*.md" }

foreach ($moc in $mocs) {
    $content = Get-Content $moc.FullName -Raw
    $linkCount = ([regex]::Matches($content, '\[\[([^\]]+)\]\]')).Count
    
    Write-Output "$($moc.Name): $linkCount links"
    
    if ($linkCount -lt 10) {
        Write-Warning "MOC $($moc.Name) has <10 links - may need expansion"
    }
}
```

**Manual:**
- [ ] Review MOC link counts
- [ ] Identify gaps in MOC coverage
- [ ] Plan MOC expansion for under-represented domains
- [ ] Update MOC content if needed

**Pass Criteria:**
- ✅ All 9 primary MOCs have ≥10 links
- ✅ All major domains covered by at least one MOC
- ✅ No MOC unchanged for >3 months (if domain is active)

---

#### 6. Quality Metrics Dashboard Update

**Automated:**
- [ ] Calculate vault-wide quality score
- [ ] Update quality metrics dashboard
- [ ] Generate trend graphs

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\calculate-quality-score.ps1 `
    -OutputPath "VAULT_HEALTH_DASHBOARD.md" `
    -IncludeTrends

# Display summary
Get-Content "VAULT_HEALTH_DASHBOARD.md" | Select-String -Pattern "OVERALL QUALITY SCORE" -Context 5
```

**Manual:**
- [ ] Review quality score trend (compare to previous weeks)
- [ ] Identify areas of improvement or degradation
- [ ] Escalate if quality score drops >5 points

**Pass Criteria:**
- ✅ Overall quality score ≥ 95/100
- ✅ Quality score stable or improving week-over-week
- ✅ No metric category below 90%

---

## Monthly Audits

**Frequency:** First Monday of each month  
**Time Required:** 2-3 hours  
**Owner:** Documentation Team Lead + Senior Architect  
**Automation Level:** 40% automated

### Checklist

#### 1. Comprehensive Vault Audit

**Automated:**
- [ ] Run all validation scripts on entire vault
- [ ] Generate comprehensive audit report
- [ ] Compare metrics to previous month

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\run-monthly-audit.ps1 `
    -VaultPath "T:\Project-AI-vault" `
    -OutputPath "audit-reports\monthly-audit-$(Get-Date -Format 'yyyy-MM').md"
```

**Manual:**
- [ ] Review audit report in detail
- [ ] Identify systemic issues (recurring errors, patterns)
- [ ] Document findings in audit report
- [ ] Present findings to team in monthly review meeting

**Pass Criteria:**
- ✅ All quality gates passed
- ✅ No systemic issues identified
- ✅ Quality trending upward or stable

---

#### 2. Tag Taxonomy Review

**Automated:**
- [ ] Generate tag usage statistics
- [ ] Identify unused tags (0 occurrences)
- [ ] Identify overused tags (>50% of documents)

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\analyze-tag-usage.ps1 `
    -TaxonomyPath "tag-hierarchy.json" `
    -VaultPath "T:\Project-AI-vault\repo-docs" `
    -OutputPath "audit-reports\tag-usage-$(Get-Date -Format 'yyyy-MM').json"
```

**Manual:**
- [ ] Review tag usage statistics
- [ ] Evaluate unused tags for deprecation
- [ ] Evaluate if new tags needed for emerging domains
- [ ] Propose tag taxonomy updates
- [ ] Update `tag-hierarchy.json` with approved changes

**Pass Criteria:**
- ✅ <10% unused tags (target: <13 tags)
- ✅ Tag distribution balanced (no single tag >50% usage)
- ✅ Taxonomy covers all active documentation domains

---

#### 3. Metadata Schema Review

**Automated:**
- [ ] Generate field usage statistics
- [ ] Identify documents with minimal metadata (<8 fields)
- [ ] Identify custom fields usage (`x-*` prefix)

**Command:**
```powershell
cd T:\Project-AI-vault
.\scripts\analyze-metadata-usage.ps1 `
    -SchemaPath "schemas\metadata-schema.json" `
    -VaultPath "T:\Project-AI-vault\repo-docs" `
    -OutputPath "audit-reports\metadata-usage-$(Get-Date -Format 'yyyy-MM').json"
```

**Manual:**
- [ ] Review field usage statistics
- [ ] Evaluate if schema needs new fields
- [ ] Evaluate if any fields are obsolete
- [ ] Propose schema updates (bump to v2.1 if needed)
- [ ] Document schema evolution decisions

**Pass Criteria:**
- ✅ All required fields used in ≥95% of documents
- ✅ Optional fields used where appropriate
- ✅ <5% documents with custom fields (unless justified)

---

#### 4. MOC Structure Review

**Automated:**
- [ ] Generate MOC statistics (size, link count, coverage)
- [ ] Identify redundant links across MOCs
- [ ] Identify missing cross-references between MOCs

**Manual:**
- [ ] Review each MOC for clarity and organization
- [ ] Evaluate if MOC structure needs reorganization
- [ ] Check if new MOCs needed for emerging domains
- [ ] Update MOC README with any structural changes

**Pass Criteria:**
- ✅ All MOCs up-to-date (updated within last 3 months)
- ✅ Clear separation of concerns between MOCs
- ✅ Adequate cross-referencing between related MOCs

---

#### 5. Obsidian Configuration Review

**Automated:**
- [ ] Verify all configured plugins still enabled
- [ ] Check for plugin updates available
- [ ] Verify workspace layout integrity

**Manual:**
- [ ] Test core workflows in Obsidian (search, graph, navigation)
- [ ] Verify Dataview queries still functional
- [ ] Check for performance issues (slow search, graph rendering)
- [ ] Update plugins if security/feature updates available

**Pass Criteria:**
- ✅ All core plugins functional
- ✅ Vault opens in <5 seconds
- ✅ Search returns results in <500ms
- ✅ Graph renders in <10 seconds

---

#### 6. Documentation Completeness Review

**Automated:**
- [ ] Check for missing critical documentation (gaps)
- [ ] Verify all templates up-to-date
- [ ] Check validation scripts still functional

**Manual:**
- [ ] Review recent project changes for doc updates needed
- [ ] Check if any new document types need templates
- [ ] Verify QA checklist still relevant (this document!)
- [ ] Update documentation roadmap

**Pass Criteria:**
- ✅ All major features documented
- ✅ All templates validated and functional
- ✅ No documentation gaps for recent features (last 3 months)

---

## Quarterly Reviews

**Frequency:** First Monday of Q1, Q2, Q3, Q4  
**Time Required:** 4-6 hours  
**Owner:** Documentation Team + Architecture Team  
**Automation Level:** 20% automated

### Checklist

#### 1. Strategic Vault Review

**Focus Areas:**
- [ ] Vault growth trends (file count, size)
- [ ] Quality trends (quarterly comparison)
- [ ] Tag taxonomy evolution
- [ ] Schema evolution
- [ ] MOC coverage adequacy

**Deliverable:** Quarterly Vault Health Report (presentation to leadership)

---

#### 2. Schema Evolution Planning

**Activities:**
- [ ] Review schema change requests from last quarter
- [ ] Evaluate schema version bump (major, minor, patch)
- [ ] Plan schema migration if needed
- [ ] Update schema documentation

**Deliverable:** Schema Evolution Roadmap (next 6 months)

---

#### 3. Automation Improvement Planning

**Activities:**
- [ ] Review manual tasks that could be automated
- [ ] Evaluate new Obsidian plugins for potential adoption
- [ ] Plan improvements to validation scripts
- [ ] Evaluate CI/CD integration opportunities

**Deliverable:** Automation Roadmap (next 6 months)

---

#### 4. Quality Process Review

**Activities:**
- [ ] Review effectiveness of daily/weekly/monthly checks
- [ ] Evaluate if quality gates are appropriate
- [ ] Gather feedback from documentation contributors
- [ ] Update QA checklist based on lessons learned

**Deliverable:** Updated QA Checklist (this document!)

---

## Automated vs Manual Tasks

### Fully Automated Tasks (90-100% automation)

**Daily:**
- Metadata validation on changed files
- Tag validation on changed files
- Git status checks

**Weekly:**
- Comprehensive metadata validation
- Tag taxonomy compliance scan
- Wiki link integrity check
- Quality metrics calculation

**Monthly:**
- Comprehensive audit report generation
- Tag usage statistics
- Metadata usage statistics

**Tools Required:**
- PowerShell 7+
- Git
- JSON Schema validator
- Obsidian CLI (if available)

---

### Semi-Automated Tasks (40-70% automation)

**Daily:**
- Obsidian health check (manual verification)

**Weekly:**
- Orphaned documents review (automated detection + manual triage)
- MOC coverage review (automated counting + manual evaluation)
- Broken link remediation (automated detection + manual fixing)

**Monthly:**
- Tag taxonomy review (automated stats + manual decision-making)
- Metadata schema review (automated stats + manual planning)
- MOC structure review (automated stats + manual reorganization)

**Tools Required:**
- PowerShell scripts + manual judgment
- Obsidian UI for manual verification

---

### Fully Manual Tasks (0-30% automation)

**Weekly:**
- MOC content quality review
- High-priority broken link fixes

**Monthly:**
- Schema evolution planning
- Documentation gap analysis
- Quality process improvements

**Quarterly:**
- Strategic vault review
- Roadmap planning

**Tools Required:**
- Human expertise and judgment
- Obsidian UI for navigation and review

---

## Quality Gates

### Gate 1: Daily Commit Gate

**Applied:** Before each git commit with documentation changes

**Criteria:**
- ✅ Changed files pass metadata validation
- ✅ Changed files pass tag validation
- ✅ No broken wiki links introduced

**Enforcement:** Manual (pre-commit checklist) OR Git pre-commit hook (future)

**Failure Action:** Fix errors before committing

---

### Gate 2: Weekly Quality Gate

**Applied:** Every Monday morning

**Criteria:**
- ✅ Metadata pass rate ≥ 95%
- ✅ Tag pass rate ≥ 95%
- ✅ Link integrity ≥ 98%
- ✅ Orphaned documents <5%
- ✅ Overall quality score ≥ 95/100

**Enforcement:** Manual review by Documentation Team Lead

**Failure Action:**
- If 1-2 criteria fail: Create remediation tasks, review next week
- If 3+ criteria fail: Escalate to team, pause new doc creation, focus on remediation

---

### Gate 3: Monthly Audit Gate

**Applied:** First Monday of each month

**Criteria:**
- ✅ All weekly gates passed for 3+ weeks in row
- ✅ Tag taxonomy stable (no major changes needed)
- ✅ Schema stable (no breaking changes needed)
- ✅ MOCs comprehensive and up-to-date
- ✅ No systemic quality issues identified

**Enforcement:** Formal audit review meeting

**Failure Action:**
- Document issues in audit report
- Create improvement plan with timeline
- Schedule follow-up review in 2 weeks

---

### Gate 4: Quarterly Strategic Gate

**Applied:** First Monday of each quarter

**Criteria:**
- ✅ All monthly audits passed
- ✅ Quality trending upward or stable
- ✅ Documentation coverage adequate for all features
- ✅ Automation coverage ≥60%
- ✅ Team satisfaction with QA process ≥80%

**Enforcement:** Formal quarterly review meeting with leadership

**Failure Action:**
- Strategic improvement plan
- Resource allocation review
- Process overhaul if needed

---

## Issue Escalation

### Severity Levels

**Critical (P0) - Immediate Escalation**

**Examples:**
- Vault won't open in Obsidian
- Metadata schema corruption
- >50% validation failure rate
- Data loss or corruption

**Escalation Path:**
1. Immediate notification to Documentation Team Lead
2. Pause all documentation work
3. Emergency remediation within 4 hours

---

**High (P1) - Same-Day Escalation**

**Examples:**
- Quality score drops >10 points
- New systemic validation issue
- Critical documents missing metadata
- Broken links in main MOCs

**Escalation Path:**
1. Notify Documentation Team Lead within 2 hours
2. Create remediation task (due within 24 hours)
3. Root cause analysis required

---

**Medium (P2) - Weekly Escalation**

**Examples:**
- Quality score drops 5-10 points
- Tag taxonomy needs updates
- Orphaned documents increase
- Specific domain lacking coverage

**Escalation Path:**
1. Add to weekly QA review agenda
2. Create remediation task (due within 1 week)
3. Monitor in next weekly check

---

**Low (P3) - Monthly Escalation**

**Examples:**
- Individual document missing optional metadata
- Single broken link in low-traffic doc
- Unused tags in taxonomy
- Minor formatting inconsistencies

**Escalation Path:**
1. Add to monthly audit backlog
2. Batch remediation during monthly maintenance
3. No urgent action required

---

## Checklist Maintenance

**This QA Checklist is a living document.**

**Update Triggers:**
- Quarterly review identifies process improvements
- New automation capabilities available
- Schema or taxonomy major version changes
- Team feedback on effectiveness

**Update Process:**
1. Propose changes in quarterly review meeting
2. Get approval from Documentation Team Lead
3. Update this document (increment version)
4. Communicate changes to all contributors
5. Train team on new procedures

**Version History:**
- v1.0 (2026-04-20): Initial release by AGENT-040

---

## Quick Reference

### Daily (5-10 min)
✅ Validate changed files  
✅ Check git status  
✅ Verify Obsidian opens

### Weekly (30-45 min)
✅ Full metadata validation  
✅ Tag compliance check  
✅ Link integrity scan  
✅ Orphan detection  
✅ MOC coverage review  
✅ Update quality dashboard

### Monthly (2-3 hours)
✅ Comprehensive audit  
✅ Tag taxonomy review  
✅ Schema review  
✅ MOC structure review  
✅ Obsidian config review  
✅ Documentation completeness

### Quarterly (4-6 hours)
✅ Strategic vault review  
✅ Schema evolution planning  
✅ Automation roadmap  
✅ Process improvement

---

**Maintained By:** AGENT-040  
**Last Updated:** 2026-04-20  
**Next Review:** 2026-07-20 (Quarterly)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

