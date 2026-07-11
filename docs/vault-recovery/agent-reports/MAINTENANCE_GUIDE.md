# Maintenance Guide: Keeping Your Vault Healthy

**Daily, Weekly, and Monthly Vault Care** 🔧

**Version:** 1.0.0
**Last Updated:** 2026-04-20
**Estimated Reading Time:** 12 minutes
**Audience:** All vault users, contributors, maintainers
**Prerequisites:** Basic vault familiarity

---

## Table of Contents

1. [Maintenance Philosophy](#maintenance-philosophy)
2. [Daily Maintenance Tasks](#daily-maintenance-tasks)
3. [Weekly Maintenance Tasks](#weekly-maintenance-tasks)
4. [Monthly Maintenance Tasks](#monthly-maintenance-tasks)
5. [Quality Checks](#quality-checks)
6. [Updating Metadata](#updating-metadata)
7. [Handling Broken Links](#handling-broken-links)
8. [Vault Health Monitoring](#vault-health-monitoring)
9. [Automation and Scripts](#automation-and-scripts)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## Maintenance Philosophy

**Vault maintenance** isn't just housekeeping - it's continuous quality improvement that ensures:

✅ **Discoverability** - Users can find documents quickly
✅ **Accuracy** - Information remains current and correct
✅ **Consistency** - Standards are enforced uniformly
✅ **Performance** - Queries run fast, searches return results
✅ **Trust** - Users rely on documentation quality

### The 80/20 Rule

**20% of maintenance** prevents **80% of problems**

Focus on:
1. **Metadata validation** (prevents discovery issues)
2. **Link integrity** (prevents broken navigation)
3. **Status updates** (prevents stale content)
4. **Tag consistency** (prevents classification drift)

### Maintenance Principles

**1. Little and Often**
- 5 minutes daily beats 2 hours monthly
- Prevention cheaper than correction

**2. Automate What You Can**
- Use Dataview queries for monitoring
- Scripts for bulk operations
- CI/CD for validation

**3. Fix Forward**
- Update docs when you find errors
- Don't wait for "maintenance day"
- Leave vault better than you found it

**4. Measure and Track**
- Monitor vault health metrics
- Track improvement over time
- Celebrate quality wins

---

## Daily Maintenance Tasks

**Time Investment:** 5-10 minutes per day

### Task 1: Review Recent Changes (2 minutes)

**Purpose:** Stay aware of vault updates and catch issues early

**Steps:**

1. Open your dashboard or create this query:

```dataviewjs
// Documents created/updated in last 24 hours
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);

dv.table(
  ["Document", "Action", "Author", "Time"],
  dv.pages()
    .where(p => p.updated_date >= yesterday || p.created_date >= yesterday)
    .sort(p => p.updated_date, 'desc')
    .limit(20)
    .map(p => {
      const action = p.created_date >= yesterday ? "Created" : "Updated";
      return [p.file.link, action, p.author, p.updated_date];
    })
);
```

2. Scan for:
   - Unexpected changes
   - Missing metadata
   - Obvious errors
   - Documents in wrong folders

3. Fix immediately if < 2 minutes
   - Otherwise add to weekly tasks

**Frequency:** Daily (start of day)

### Task 2: Check Your Contributions (1 minute)

**Purpose:** Ensure your recent work is complete

**Query:**

```dataviewjs
// My documents from last 7 days
const sevenDays = new Date();
sevenDays.setDate(sevenDays.getDate() - 7);

const myAuthorId = "AGENT-048"; // Change to your ID

dv.table(
  ["Document", "Status", "Updated"],
  dv.pages()
    .where(p => p.author === myAuthorId && p.updated_date >= sevenDays)
    .map(p => [p.file.link, p.status, p.updated_date])
);
```

**Check for:**
- [ ] Status still "draft"? → Change to "active" or "review"
- [ ] Missing tags? → Add appropriate tags
- [ ] TODOs left? → Complete or remove
- [ ] Broken links? → Fix or update

**Frequency:** Daily (end of day)

### Task 3: Triage New Documents (2 minutes)

**Purpose:** Ensure new documents meet quality standards

**Query:**

```dataviewjs
// New documents from last 24 hours
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);

dv.table(
  ["Document", "Author", "Status", "Has Tags?", "Has Metadata?"],
  dv.pages()
    .where(p => p.created_date >= yesterday)
    .map(p => [
      p.file.link,
      p.author || "❌",
      p.status || "❌",
      p.tags ? "✅" : "❌",
      (p.type && p.area && p.audience) ? "✅" : "❌"
    ])
);
```

**Actions:**
- If missing metadata: Add frontmatter
- If missing tags: Add from taxonomy
- If status is blank: Set to "draft" minimum
- If author missing: Add creator info

**Frequency:** Daily (when you see new docs)

---

## Weekly Maintenance Tasks

**Time Investment:** 30-45 minutes per week

### Task 1: Validate Metadata Completeness (10 minutes)

**Purpose:** Ensure all documents have required metadata

**Query:**

```dataviewjs
// Documents missing required fields
const requiredFields = ['type', 'area', 'status', 'audience', 'tags'];

dv.table(
  ["Document", "Missing Fields", "Author"],
  dv.pages()
    .where(p => {
      return requiredFields.some(field => !p[field]);
    })
    .map(p => {
      const missing = requiredFields.filter(f => !p[f]);
      return [p.file.link, missing.join(", "), p.author || "Unknown"];
    })
);
```

**Fix Process:**

1. Open each document
2. Add missing frontmatter fields
3. Reference [METADATA_GUIDE.md](METADATA_GUIDE.md) for values
4. Update `updated_date` to today
5. Save and validate

**Target:** Zero documents missing required fields

**Frequency:** Weekly (Monday morning)

### Task 2: Check for Broken Links (10 minutes)

**Purpose:** Maintain navigation integrity

**Method 1: Obsidian Built-In**

```
Steps:
1. Ctrl+P → Command palette
2. Type "Check for broken links"
3. Review list of broken links
4. Fix each one:
   - Update link target
   - Remove obsolete link
   - Create missing document
```

**Method 2: Dataview Query**

```dataviewjs
// Find orphaned documents (no backlinks)
dv.table(
  ["Orphan Document", "Created", "Status"],
  dv.pages()
    .where(p => {
      const backlinks = dv.app.metadataCache.getBacklinksForFile(p.file);
      return backlinks.count() === 0;
    })
    .sort(p => p.created_date, 'desc')
    .map(p => [p.file.link, p.created_date, p.status])
);
```

**Fix Strategy:**

- **Broken outbound links:** Update to correct target or remove
- **Orphaned documents:** Link from relevant index or MOC
- **Duplicate links:** Consolidate where appropriate

**Frequency:** Weekly (Wednesday)

### Task 3: Review Draft Documents (10 minutes)

**Purpose:** Move documents through the workflow

**Query:**

```dataviewjs
// Draft documents older than 7 days
const weekAgo = new Date();
weekAgo.setDate(weekAgo.getDate() - 7);

dv.table(
  ["Document", "Author", "Created", "Days in Draft"],
  dv.pages()
    .where(p => p.status === "draft" && p.created_date < weekAgo)
    .sort(p => p.created_date, 'asc')
    .map(p => {
      const days = Math.floor((Date.now() - new Date(p.created_date)) / (1000*60*60*24));
      return [p.file.link, p.author, p.created_date, days];
    })
);
```

**Actions:**

- **Complete?** → Change status to "review" or "active"
- **Abandoned?** → Delete or archive
- **Blocked?** → Document blocker, set status to "blocked"
- **In progress?** → Add TODO comments for next steps

**Target:** No drafts older than 30 days

**Frequency:** Weekly (Friday)

### Task 4: Tag Consistency Check (10 minutes)

**Purpose:** Enforce tag taxonomy standards

**Query:**

```dataviewjs
// Documents with non-standard tags
const officialTags = ["architecture", "security", "documentation", /* add all official tags */];

dv.table(
  ["Document", "Non-Standard Tags"],
  dv.pages()
    .where(p => p.tags && p.tags.some(t => !officialTags.includes(t)))
    .map(p => {
      const invalid = p.tags.filter(t => !officialTags.includes(t));
      return [p.file.link, invalid.join(", ")];
    })
);
```

**Fix Process:**

1. Compare tags against [TAG_TAXONOMY.md](TAG_TAXONOMY.md)
2. Replace non-standard tags with official equivalents
3. Document new tags if they represent valid new categories
4. Update tag taxonomy if needed

**Reference:** `TAG_TAXONOMY.md` for complete official list

**Frequency:** Weekly (Friday)

---

## Monthly Maintenance Tasks

**Time Investment:** 2-3 hours per month

### Task 1: Update Stale Documents (60 minutes)

**Purpose:** Refresh outdated content

**Query:**

```dataviewjs
// Documents not updated in 90+ days
const ninetyDays = new Date();
ninetyDays.setDate(ninetyDays.getDate() - 90);

dv.table(
  ["Document", "Last Updated", "Days Stale", "Status"],
  dv.pages()
    .where(p => p.updated_date < ninetyDays && p.status === "active")
    .sort(p => p.updated_date, 'asc')
    .map(p => {
      const days = Math.floor((Date.now() - new Date(p.updated_date)) / (1000*60*60*24));
      return [p.file.link, p.updated_date, days, p.status];
    })
);
```

**Review Process:**

1. Open document
2. Check if content is still accurate
3. Options:
   - **Still accurate:** Update `updated_date`, add "Reviewed: YYYY-MM-DD" note
   - **Needs updates:** Make changes, update date
   - **Outdated:** Mark as `status: deprecated`, create replacement
   - **Historical:** Move to `status: archived`

**Target:** All active docs reviewed within 180 days

**Frequency:** Monthly (first week)

### Task 2: Vault Health Report (30 minutes)

**Purpose:** Generate metrics and identify trends

**Create Monthly Health Dashboard:**

```markdown
# Vault Health Report: <Month> <Year>

## Document Statistics

### Total Documents
\`\`\`dataviewjs
dv.paragraph(`Total: ${dv.pages().length} documents`);
\`\`\`

### By Status
\`\`\`dataviewjs
const statuses = dv.pages().groupBy(p => p.status || "Unknown");
dv.table(
  ["Status", "Count", "Percentage"],
  statuses.map(s => [
    s.key,
    s.rows.length,
    `${((s.rows.length / dv.pages().length) * 100).toFixed(1)}%`
  ])
);
\`\`\`

### By Area
\`\`\`dataviewjs
const areas = dv.pages()
  .flatMap(p => p.area ? (Array.isArray(p.area) ? p.area : [p.area]) : [])
  .groupBy(a => a);

dv.table(
  ["Area", "Count"],
  areas.sort(a => a.rows.length, 'desc')
);
\`\`\`

## Quality Metrics

### Metadata Completeness
\`\`\`dataviewjs
const total = dv.pages().length;
const complete = dv.pages()
  .where(p => p.type && p.area && p.status && p.audience && p.tags)
  .length;

dv.paragraph(`${complete} / ${total} (${((complete/total)*100).toFixed(1)}%)`);
\`\`\`

### Documents with Broken Links
\`\`\`dataviewjs
// Count broken links
dv.paragraph(`Total broken links: [manual count]`);
\`\`\`

### Orphaned Documents
\`\`\`dataviewjs
const orphans = dv.pages()
  .where(p => {
    const backlinks = dv.app.metadataCache.getBacklinksForFile(p.file);
    return backlinks.count() === 0;
  });

dv.paragraph(`Orphaned: ${orphans.length}`);
\`\`\`

## Activity Metrics

### Documents Created This Month
\`\`\`dataviewjs
const thisMonth = new Date();
thisMonth.setDate(1);

const created = dv.pages()
  .where(p => p.created_date >= thisMonth)
  .length;

dv.paragraph(`Created: ${created}`);
\`\`\`

### Documents Updated This Month
\`\`\`dataviewjs
const updated = dv.pages()
  .where(p => p.updated_date >= thisMonth)
  .length;

dv.paragraph(`Updated: ${updated}`);
\`\`\`

## Issues to Address

### Missing Required Metadata
\`\`\`dataviewjs
const requiredFields = ['type', 'area', 'status', 'audience', 'tags'];
const missing = dv.pages()
  .where(p => requiredFields.some(f => !p[f]));

dv.list(missing.file.link);
\`\`\`

### Stale Active Documents (180+ days)
\`\`\`dataviewjs
const sixMonths = new Date();
sixMonths.setDate(sixMonths.getDate() - 180);

const stale = dv.pages()
  .where(p => p.status === "active" && p.updated_date < sixMonths);

dv.list(stale.file.link);
\`\`\`

## Recommendations

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

**Save as:** `reports/VAULT_HEALTH_YYYY-MM.md`

**Frequency:** Monthly (last day)

### Task 3: Taxonomy Review (30 minutes)

**Purpose:** Evolve tag taxonomy based on usage

**Analysis:**

1. Generate tag usage report:

```dataviewjs
// Tag frequency analysis
const allTags = dv.pages()
  .flatMap(p => p.tags || [])
  .groupBy(t => t);

dv.table(
  ["Tag", "Usage Count", "% of Docs"],
  allTags
    .sort(t => t.rows.length, 'desc')
    .map(t => [
      t.key,
      t.rows.length,
      `${((t.rows.length / dv.pages().length) * 100).toFixed(1)}%`
    ])
);
```

2. Identify issues:
   - Tags used <3 times (candidates for removal)
   - Very similar tags (consolidate?)
   - Missing categories (gaps in taxonomy?)
   - Overused tags (need subtags?)

3. Update `TAG_TAXONOMY.md` if changes warranted

**Frequency:** Monthly (third week)

### Task 4: Archive Old Content (30 minutes)

**Purpose:** Move historical content out of active vault

**Query:**

```dataviewjs
// Deprecated docs older than 90 days
const ninetyDays = new Date();
ninetyDays.setDate(ninetyDays.getDate() - 90);

dv.table(
  ["Document", "Deprecated Date", "Replacement"],
  dv.pages()
    .where(p => p.status === "deprecated" && p.updated_date < ninetyDays)
    .map(p => [p.file.link, p.updated_date, p.replacement || "None"])
);
```

**Archive Process:**

1. Verify replacement exists
2. Update links to point to replacement
3. Move to `archive/` folder
4. Update status to "archived"
5. Add archive date to frontmatter

**Frequency:** Monthly (end of month)

---

## Quality Checks

### Metadata Quality Checklist

Run monthly:

- [ ] **Frontmatter present**: All docs have YAML frontmatter
- [ ] **Required fields**: type, area, status, audience, tags
- [ ] **Valid status**: Only official values (active/draft/review/etc.)
- [ ] **Valid tags**: All tags from official taxonomy
- [ ] **Date format**: YYYY-MM-DD (ISO 8601)
- [ ] **Version format**: Semantic versioning (1.2.3)
- [ ] **Arrays**: Proper syntax `[item1, item2]`

### Content Quality Checklist

Sample 10 random documents monthly:

- [ ] **Title matches purpose**: H1 accurately describes content
- [ ] **TOC present**: For docs >1000 words
- [ ] **Headers logical**: Hierarchical structure (H2 > H3)
- [ ] **Links work**: No broken wiki links
- [ ] **Examples included**: Code/config examples where appropriate
- [ ] **No TODOs**: All placeholders filled in
- [ ] **Spelling/grammar**: Clean, professional
- [ ] **Formatting consistent**: Tables, lists, code blocks formatted

### Link Quality Checklist

Weekly:

- [ ] **No broken links**: All wiki links resolve
- [ ] **No orphans**: All docs linked from somewhere
- [ ] **Bidirectional**: Important docs linked both ways
- [ ] **Index coverage**: All docs in relevant MOC/index
- [ ] **External links valid**: HTTP links return 200

---

## Updating Metadata

### When to Update Metadata

**Always update `updated_date` when:**
- Editing content
- Fixing typos
- Updating examples
- Adding sections
- Restructuring

**Update `version` when:**
- Major rewrite: Bump major (1.x.x → 2.0.0)
- New section: Bump minor (1.2.x → 1.3.0)
- Typos/fixes: Bump patch (1.2.3 → 1.2.4)

**Update `status` when:**
- Completing draft → `status: active`
- Submitting for review → `status: review`
- Replacing with new version → `status: deprecated`
- Moving to archive → `status: archived`

**Update `tags` when:**
- Adding new content area
- Document scope changes
- Tag taxonomy updates
- Improving discoverability

### Bulk Metadata Updates

**Using PowerShell:**

```powershell
# Update all drafts older than 30 days to "stale" status
$files = Get-ChildItem -Path "T:\Project-AI-vault" -Filter "*.md" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw

    # Check if draft and old
    if ($content -match 'status: draft' -and
        $content -match 'created_date: (\d{4}-\d{2}-\d{2})') {

        $created = [datetime]::Parse($matches[1])
        $daysSince = (Get-Date) - $created

        if ($daysSince.Days -gt 30) {
            # Add stale tag
            $content = $content -replace 'tags: \[', 'tags: [incomplete, '
            Set-Content -Path $file.FullName -Value $content
            Write-Host "Updated: $($file.Name)"
        }
    }
}
```

**Using Dataview + Manual:**

1. Generate list with query
2. Open each document
3. Update frontmatter
4. Save

**Safety:** Always backup before bulk operations!

---

## Handling Broken Links

### Types of Broken Links

**1. Renamed Files**

```markdown
Before: [[UserManager.md]]
After:  [[USER_MANAGER.md]]

Fix: Update all references to new name
```

**2. Moved Files**

```markdown
Before: [[authentication.md]]
Moved:  source-docs/core/authentication.md

Fix: Update path or use file name only (Obsidian resolves)
```

**3. Deleted Files**

```markdown
Link: [[deprecated-feature.md]]
Status: File deleted

Fix Options:
1. Create redirect/stub: "This feature removed in v2.0"
2. Remove link if obsolete
3. Link to replacement document
```

**4. Typos**

```markdown
Wrong: [[Authetication]]
Right: [[Authentication]]

Fix: Correct spelling
```

### Link Repair Process

**Step 1: Identify Broken Links**

```
Method A: Obsidian built-in
  Ctrl+P → "Check for broken links"

Method B: Graph view
  Orphaned nodes = no incoming links
  Click to inspect
```

**Step 2: Categorize**

- **Easy fix** (typo, rename): Fix immediately
- **Requires decision** (deleted file): Add to review list
- **Systemic** (many instances): Script bulk update

**Step 3: Fix**

```
For each broken link:
  1. Locate all instances (Ctrl+Shift+F)
  2. Determine correct target
  3. Update or remove
  4. Verify with "Check broken links" again
```

**Step 4: Prevent**

```
Prevention strategies:
  1. Use file search when creating links (Ctrl+O)
  2. Avoid manual path typing
  3. Test links before publishing
  4. Run weekly link check
```

---

## Vault Health Monitoring

### Key Health Metrics

**1. Metadata Completeness**
```
Target: 100% of active docs
Current: [Run query to measure]
Trend: [Track monthly]
```

**2. Link Integrity**
```
Target: 0 broken links
Current: [Run check]
Trend: [Track weekly]
```

**3. Staleness**
```
Target: <10% docs older than 180 days
Current: [Run query]
Trend: [Track monthly]
```

**4. Coverage**
```
Target: All components documented
Current: [Manual audit]
Trend: [Track quarterly]
```

**5. Orphan Rate**
```
Target: <5% orphan documents
Current: [Run query]
Trend: [Track monthly]
```

### Health Dashboard

**Create:** `VAULT_HEALTH_DASHBOARD.md`

**Contents:**

1. Real-time metrics (Dataview queries)
2. Trend charts (manual or scripted)
3. Action items (what needs fixing)
4. Historical data (monthly snapshots)

**Usage:**

- Review daily for quick status
- Deep dive weekly for issues
- Monthly reports for trends

**See:** `VAULT_HEALTH_DASHBOARD.md` in vault root

---

## Automation and Scripts

### Automated Validation Scripts

**Location:** `scripts/validate-*.ps1`

**Available Scripts:**

1. **validate-metadata.ps1**
   - Checks frontmatter completeness
   - Validates against schema
   - Reports errors

2. **validate-tags.ps1**
   - Compares tags to taxonomy
   - Finds non-standard tags
   - Suggests corrections

3. **validate-links.ps1**
   - Scans for broken wiki links
   - Checks external URL health
   - Generates repair report

4. **vault-health-report.ps1**
   - Comprehensive metrics
   - Exports to JSON/CSV
   - Trends over time

**Running Scripts:**

```powershell
# From vault root
.\scripts\validate-metadata.ps1

# With output
.\scripts\validate-metadata.ps1 > reports/metadata-validation.txt

# All validations
.\scripts\run-all-validations.ps1
```

### CI/CD Integration

**GitHub Actions:**

```yaml
name: Vault Validation

on:
  push:
    branches: [main]
  pull_request:

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2

      - name: Validate Metadata
        run: .\scripts\validate-metadata.ps1

      - name: Check Links
        run: .\scripts\validate-links.ps1

      - name: Tag Compliance
        run: .\scripts\validate-tags.ps1
```

**Benefits:**

- Catches issues before merge
- Enforces standards automatically
- Generates compliance reports

---

## Troubleshooting Common Issues

### Issue: "Search is slow"

**Cause:** Large vault, unoptimized queries

**Solutions:**

1. Rebuild search index
   - Settings → Files & Links → Rebuild index

2. Optimize Dataview queries
   - Limit scope: `dv.pages("#tag")` not `dv.pages()`
   - Add limits: `.limit(50)`

3. Reduce vault size
   - Archive old content
   - Move large assets out

### Issue: "Metadata validation fails"

**Cause:** YAML syntax errors

**Solutions:**

1. Check delimiters
   - Must be `---` on their own lines

2. Validate YAML
   - Use: http://www.yamllint.com/

3. Check array syntax
   - `[item1, item2]` not `item1 item2`

4. Quote special characters
   - `title: "User's Guide"` not `title: User's Guide`

### Issue: "Too many orphan documents"

**Cause:** Missing navigation structure

**Solutions:**

1. Create MOCs (Maps of Content)
   - Index documents by topic
   - Link to all relevant docs

2. Add to existing indexes
   - Find appropriate MOC
   - Add link with context

3. Cross-link related docs
   - Add "See Also" sections
   - Link from implementation to design docs

### Issue: "Tag taxonomy drift"

**Cause:** Contributors using custom tags

**Solutions:**

1. Document official taxonomy clearly
   - Keep TAG_TAXONOMY.md updated
   - Share with all contributors

2. Automate validation
   - Run validate-tags.ps1 weekly
   - Flag non-standard tags

3. Provide guidance
   - Templates include common tags
   - Examples in documentation

---

## Summary: Maintenance Checklist

### Daily (5-10 min)
- [ ] Review recent changes
- [ ] Check your contributions
- [ ] Triage new documents

### Weekly (30-45 min)
- [ ] Validate metadata completeness
- [ ] Check for broken links
- [ ] Review draft documents
- [ ] Tag consistency check

### Monthly (2-3 hours)
- [ ] Update stale documents
- [ ] Generate health report
- [ ] Review tag taxonomy
- [ ] Archive old content

### Quarterly (4-6 hours)
- [ ] Deep content audit
- [ ] Schema updates
- [ ] Template improvements
- [ ] Documentation strategy review

---

**Maintenance Success Criteria:**

✅ 100% metadata completeness
✅ 0 broken links
✅ <5% orphaned documents
✅ <10% stale content (180+ days)
✅ Weekly quality checks performed
✅ Monthly health report generated

---

**Next Steps:**

- **Start small:** Daily tasks this week
- **Build habit:** Weekly tasks next week
- **Scale up:** Monthly tasks next month
- **Automate:** Implement validation scripts

**Related Documentation:**

- [VAULT_HEALTH_DASHBOARD.md](VAULT_HEALTH_DASHBOARD.md)
- [METADATA_GUIDE.md](METADATA_GUIDE.md)
- [TAG_REFERENCE.md](TAG_REFERENCE.md)
- `scripts/` folder for automation

---

**Document Metadata:**

```yaml
---
type: guide
area: [documentation, operations]
component: vault
status: active
audience: [user, developer, contributor, operator]
priority: high
tags: [maintenance, quality, monitoring, automation, operations]
version: 1.0.0
created_date: 2026-04-20
updated_date: 2026-04-20
author: AGENT-048
word_count: 3700
---
```

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
