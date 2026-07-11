# Tag Taxonomy System - Quick Start

> **Complete Tag Classification System for Project-AI Vault**
> **Version:** 1.0
> **Created:** 2025-01-20
> **Maintainer:** AGENT-017 (Tag Taxonomy Architect)

---

## What This System Provides

The Tag Taxonomy System delivers a comprehensive, production-ready tagging infrastructure for the Project-AI documentation vault with:

✅ **100+ standardized tags** across 7 categories
✅ **Hierarchical parent/child relationships** for precise classification
✅ **Automated validation** with PowerShell script
✅ **Machine-readable schema** (JSON) for tooling integration
✅ **Extensive documentation** with 25+ real-world examples
✅ **Integration with metadata schema** (AGENT-016)

---

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[TAG_TAXONOMY.md](TAG_TAXONOMY.md)** | Complete reference (1,500+ words) | All users - definitive guide |
| **[tag-hierarchy.json](tag-hierarchy.json)** | Machine-readable schema | Automation, validation scripts |
| **[TAG_USAGE_EXAMPLES.md](TAG_USAGE_EXAMPLES.md)** | 25+ real-world examples | Developers, content creators |
| **[TAG_VALIDATION_RULES.md](TAG_VALIDATION_RULES.md)** | Validation rules reference | Developers, CI/CD engineers |
| **[validate-tags.ps1](validate-tags.ps1)** | Validation automation script | CI/CD, pre-commit hooks |

---

## The 7 Tag Categories

### 1. **Area Tags** (1-3 required)
Primary domain/discipline classification.

```yaml
tags:
  - security              # Parent
  - security/audit        # Child (specific)
```

**Available:** architecture, security, governance, development, operations, legal, executive

---

### 2. **Type Tags** (1-2 required)
Document format and structure.

```yaml
tags:
  - guide                 # How-to instructions
  - reference            # Lookup material
```

**Available:** guide, reference, spec, report, whitepaper, api-doc, source-doc, runbook, adr, index

---

### 3. **Component Tags** (0-5 optional)
Specific technical components covered.

```yaml
tags:
  - gui                   # PyQt6 interface
  - persona-system        # AI personality system
```

**Available:** constitutional-ai, cerberus, gui, web, agents, user-manager, +20 more

---

### 4. **Status Tags** (exactly 1 required)
Lifecycle stage (mutually exclusive).

```yaml
tags:
  - active                # Current and maintained
```

**Available:** active, draft, in-progress, review, archived, deprecated, superseded, legacy, planned, blocked

---

### 5. **Audience Tags** (1-4 required)
Intended readers.

```yaml
tags:
  - developer             # Software engineers
  - operator              # SRE, ops teams
```

**Available:** developer, architect, operator, executive, legal, security, researcher, contributor, internal, public

---

### 6. **Priority Tags** (0-1 recommended)
Importance and urgency (mutually exclusive).

```yaml
tags:
  - P0                    # Critical, 24h review
```

**Available:** P0 (Critical), P1 (High), P2 (Medium), P3 (Low), P4 (Deferred)

---

### 7. **Special Tags** (0-10 optional)
Cross-cutting concerns.

```yaml
tags:
  - quickstart            # Getting started guide
  - troubleshooting       # Problem resolution
```

**Available:** migration, integration, troubleshooting, quickstart, best-practices, tutorial, automation, +15 more

---

## Quick Start: Tag Your First Document

### Step 1: Create Frontmatter

```yaml
---
title: "Your Document Title"
created: "2025-01-20"
updated: "2025-01-20"
status: active           # Also add to tags below
priority: P2             # Also add to tags below

tags:
  # REQUIRED: Area (1-3 tags)
  - development
  - development/python

  # REQUIRED: Type (1-2 tags)
  - guide

  # OPTIONAL: Component (0-5 tags)
  - gui

  # REQUIRED: Status (exactly 1 tag)
  - active

  # REQUIRED: Audience (1-4 tags)
  - developer
  - contributor

  # RECOMMENDED: Priority (0-1 tag)
  - P2

  # OPTIONAL: Special (0-10 tags)
  - quickstart
  - tutorial
---
```

### Step 2: Validate

```powershell
# Validate your document
.\validate-tags.ps1 -Path "your-document.md" -Verbose

# Generate HTML report
.\validate-tags.ps1 -Path "your-document.md" -OutputFormat HTML -ReportPath "report.html"
```

### Step 3: Fix Errors

Common fixes:
- Add parent tag if using child (e.g., `security` for `security/audit`)
- Ensure exactly 1 status tag
- Check spelling against taxonomy
- Use lowercase with hyphens only

---

## Example: Security Audit Report

```yaml
---
title: "2025 Security Audit - Authentication Systems"
created: "2025-01-15"
updated: "2025-01-20"
version: "1.2"
authors: ["Security Team", "AGENT-023"]
reviewers: ["AGENT-017", "Lead Architect"]

# Lifecycle
status: active
priority: P0

# Tags (AGENT-017 Taxonomy)
tags:
  # Area (2 tags - security focus)
  - security
  - security/audit

  # Type (1 tag - audit findings)
  - report

  # Component (3 tags - systems audited)
  - user-manager
  - command-override
  - persona-system

  # Audience (3 tags - broad reach)
  - security
  - developer
  - executive

  # Special (2 tags - actionable insights)
  - troubleshooting
  - best-practices

# Relationships
supersedes: []
related: ["PASSWORD_POLICY.md", "BCRYPT_IMPLEMENTATION.md"]
dependencies: []

# Access
visibility: internal
classification: confidential
---

# 2025 Security Audit - Authentication Systems

[Your content here...]
```

---

## Validation in CI/CD

### GitHub Actions

```yaml
# .github/workflows/validate-tags.yml
name: Validate Documentation Tags

on:
  pull_request:
    paths:
      - '**/*.md'
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Validate Tags
        shell: pwsh
        run: |
          .\T:\Project-AI-vault\validate-tags.ps1 `
            -Path "T:\Project-AI-vault\repo-docs" `
            -OutputFormat JSON `
            -ReportPath "validation-report.json"

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: tag-validation-report
          path: validation-report.json
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')

if [ -n "$STAGED_MD" ]; then
    echo "Validating tags in staged markdown files..."

    for file in $STAGED_MD; do
        pwsh -File T:\Project-AI-vault\validate-tags.ps1 -Path "$file"

        if [ $? -ne 0 ]; then
            echo "Tag validation failed for $file"
            exit 1
        fi
    done

    echo "Tag validation passed"
fi

exit 0
```

---

## Tag Statistics Dashboard

Generate usage statistics:

```powershell
# Count documents by category
$allDocs = Get-ChildItem -Path "T:\Project-AI-vault\repo-docs" -Filter "*.md" -Recurse
$tagCounts = @{}

foreach ($doc in $allDocs) {
    $tags = .\Get-DocumentTags.ps1 -Path $doc.FullName
    foreach ($tag in $tags) {
        $tagCounts[$tag]++
    }
}

# Display top tags
$tagCounts.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 20
```

---

## Integration with Obsidian

The tag taxonomy integrates seamlessly with Obsidian:

1. **Tag Pane:** All tags appear in Obsidian's tag pane
2. **Search:** Use tag search: `tag:#security/audit`
3. **Dataview:** Query by tags:
   ```dataview
   TABLE priority, status
   FROM #security AND #report
   WHERE priority = "P0"
   ```
4. **Graph View:** Visualize tag relationships

---

## Maintenance Workflow

### Adding New Tags

1. **Proposal:** Document use case and examples
2. **Update Taxonomy:** Add to `tag-hierarchy.json`
3. **Update Docs:** Add definition to `TAG_TAXONOMY.md`
4. **Update Script:** Ensure `validate-tags.ps1` recognizes it
5. **Add Examples:** Include in `TAG_USAGE_EXAMPLES.md`
6. **Announce:** Notify team of new tag availability

### Deprecating Tags

1. **Mark Deprecated:** Update `tag-hierarchy.json`
2. **Create Migration Guide:** Document replacement
3. **Update Documents:** Migrate to new tags
4. **Grace Period:** 90 days before removal
5. **Remove:** Delete from taxonomy after grace period

### Quarterly Audit

- [ ] Review tag usage statistics
- [ ] Identify under-used tags (< 5 documents)
- [ ] Identify over-used tags (> 100 documents - consider splitting)
- [ ] Check for tag sprawl (similar/redundant tags)
- [ ] Validate hierarchy makes sense
- [ ] Update examples
- [ ] Sync with metadata schema changes

---

## Troubleshooting

### "No tags found in frontmatter"

**Problem:** Script can't extract tags.

**Solution:**
- Ensure frontmatter between `---` markers
- Tags must be in `tags:` array
- Check indentation (2 spaces)
- Ensure line endings are consistent

---

### "Tag not in controlled vocabulary"

**Problem:** Tag not defined in taxonomy.

**Solution:**
- Check spelling: `developer` not `dev`
- Check case: `P0` not `p0`
- Verify in `TAG_TAXONOMY.md`
- Propose new tag if genuinely needed

---

### "Child tag requires parent"

**Problem:** Using `security/audit` without `security`.

**Solution:**
```yaml
# Add parent tag
tags:
  - security              # Parent
  - security/audit        # Child
```

---

### "Category allows only one tag"

**Problem:** Multiple status or priority tags.

**Solution:**
```yaml
# Remove duplicate (choose most accurate)
tags:
  - active    # Only one status
  - P0        # Only one priority
```

---

## Quality Gates

Before committing documentation:

✅ **Required:**
- [ ] All required categories have tags (area, type, status, audience)
- [ ] Tags follow format rules (lowercase, hyphens, max 30 chars)
- [ ] Tags exist in controlled vocabulary
- [ ] Child tags have parent tags present
- [ ] Exactly 1 status tag, 0-1 priority tag
- [ ] Validation script passes (exit code 0)

✅ **Recommended:**
- [ ] Priority tag assigned (P0-P4)
- [ ] Component tags identify technical systems
- [ ] Special tags enhance discoverability
- [ ] Tags accurately describe content

---

## Related Systems

This tag taxonomy integrates with:

- **AGENT-016 Metadata Schema:** Frontmatter structure
- **AGENT-002 Index System:** Document organization
- **Obsidian Vault:** Tag-based navigation
- **GitHub Actions:** Automated validation
- **Pre-commit Hooks:** Local validation

---

## Support

### Documentation
- [TAG_TAXONOMY.md](TAG_TAXONOMY.md) - Complete reference
- [TAG_USAGE_EXAMPLES.md](TAG_USAGE_EXAMPLES.md) - 25+ examples
- [TAG_VALIDATION_RULES.md](TAG_VALIDATION_RULES.md) - Validation details

### Tools
- [validate-tags.ps1](validate-tags.ps1) - Validation automation
- [tag-hierarchy.json](tag-hierarchy.json) - Machine-readable schema

### Contact
- Maintainer: AGENT-017 (Tag Taxonomy Architect)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-20 | Initial release: 100+ tags, 7 categories, validation automation |

---

## License

This taxonomy system is part of Project-AI and follows the MIT License.

---

**Last Updated:** 2025-01-20
**Schema Version:** 1.0
**Maintained By:** AGENT-017 (Tag Taxonomy Architect)
**Status:** Production-Ready

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
