# Index File Naming Convention Guide

## Purpose

This document defines mandatory naming conventions for all index files in the Project-AI Obsidian Vault. Consistent naming enables predictability, automation, and reduces cognitive load when navigating the vault.

**Scope:** All files in `_indexes/` directory and subdirectories.

**Enforcement:** Automated validation scripts check compliance with these rules.

---

## Core Naming Pattern

### Standard Format

```
{scope}-{type}-index.md
```

**Components:**
- `{scope}`: Domain, category, or focus area (lowercase, kebab-case)
- `{type}`: Index dimension type (lowercase, kebab-case)
- `-index`: Required suffix for all index files
- `.md`: Markdown file extension

**Character Set:** `a-z`, `0-9`, `-` (hyphen)

**Case:** Lowercase only (no uppercase, camelCase, PascalCase, or snake_case)

**Length:** Maximum 50 characters (excluding `.md` extension)

---

## Naming Rules by Index Type

### 1. by-area/ (Domain-Based Indexes)

**Pattern:** `{domain}-domain-index.md`

**Examples:**
```
security-domain-index.md
architecture-domain-index.md
api-domain-index.md
infrastructure-domain-index.md
testing-domain-index.md
governance-domain-index.md
data-domain-index.md
frontend-domain-index.md
backend-domain-index.md
devops-domain-index.md
```

**Rules:**
- Domain name should be singular (e.g., `security`, not `securities`)
- Use `-domain-index` suffix for clarity
- Common abbreviations allowed if widely understood:
  - `api` (not `application-programming-interface`)
  - `ui` (not `user-interface`)
  - `db` (not `database`)
  - `ci-cd` (not `continuous-integration-continuous-deployment`)

**Invalid Examples:**
```
❌ Security-Index.md          (uppercase S)
❌ security_domain_index.md   (snake_case)
❌ securityIndex.md           (camelCase)
❌ security.md                (missing -domain-index suffix)
❌ securities-domain-index.md (plural domain name)
```

---

### 2. by-type/ (Document Type Indexes)

**Pattern:** `{document-type}-type-index.md`

**Examples:**
```
specification-type-index.md
guide-type-index.md
reference-type-index.md
adr-type-index.md
report-type-index.md
runbook-type-index.md
standard-type-index.md
template-type-index.md
tutorial-type-index.md
troubleshooting-type-index.md
```

**Rules:**
- Document type should match actual document naming (e.g., ADRs named `adr-001-*`, so use `adr-type-index`)
- Use singular form (e.g., `guide`, not `guides`)
- Use `-type-index` suffix for clarity
- Abbreviations allowed for document types:
  - `adr` (Architecture Decision Record)
  - `api-spec` (API Specification)
  - `sop` (Standard Operating Procedure)

**Invalid Examples:**
```
❌ guides-type-index.md       (plural)
❌ guide-index.md             (missing -type suffix)
❌ GuideTypeIndex.md          (PascalCase)
❌ guide_type_index.md        (snake_case)
```

---

### 3. by-priority/ (Priority-Based Indexes)

**Pattern:** `{priority-level}-priority-index.md`

**Examples:**
```
p0-critical-priority-index.md
p1-high-priority-index.md
p2-medium-priority-index.md
p3-low-priority-index.md
```

**Alternative Pattern (Descriptive):**
```
critical-priority-index.md
high-priority-index.md
medium-priority-index.md
low-priority-index.md
```

**Rules:**
- Use `p0`, `p1`, `p2`, `p3` prefixes (lowercase) OR descriptive names
- Include priority descriptor (critical/high/medium/low) for clarity
- Use `-priority-index` suffix
- Consistent pattern across all priority levels

**Invalid Examples:**
```
❌ P0-priority-index.md       (uppercase P)
❌ p0-index.md                (missing descriptive term)
❌ priority-p0-index.md       (wrong order)
❌ p0-critical.md             (missing -index suffix)
```

---

### 4. by-status/ (Lifecycle Status Indexes)

**Pattern:** `{status}-status-index.md`

**Examples:**
```
active-status-index.md
planned-status-index.md
in-progress-status-index.md
review-status-index.md
archived-status-index.md
deprecated-status-index.md
superseded-status-index.md
```

**Rules:**
- Status name should match metadata `status` field values
- Use hyphenated multi-word statuses (e.g., `in-progress`, not `inprogress` or `in_progress`)
- Use `-status-index` suffix
- Status names are descriptive, not abbreviated

**Invalid Examples:**
```
❌ Active-Status-Index.md     (uppercase)
❌ active.md                  (missing -status-index suffix)
❌ status-active-index.md     (wrong order)
❌ inprogress-status-index.md (missing hyphen)
```

---

### 5. cross-reference/ (Relationship Indexes)

**Pattern:** `{scope}-{relationship-type}-index.md`

**Examples:**
```
authentication-dependencies-index.md
api-conflicts-index.md
architecture-alternatives-index.md
security-complements-index.md
deployment-prerequisites-index.md
frontend-backend-integration-index.md
```

**Relationship Types:**
- `dependencies` - What this scope depends on
- `conflicts` - Conflicting or contradictory documents
- `alternatives` - Alternative approaches considered
- `complements` - Documents that work together
- `prerequisites` - Required reading order
- `integration` - Integration points between scopes

**Rules:**
- Scope comes first, relationship type second
- Relationship type should be plural (e.g., `dependencies`, not `dependency`)
- Use descriptive, semantic relationship names
- Multi-scope indexes: Use `{scope1}-{scope2}-{relationship}-index.md`

**Invalid Examples:**
```
❌ dependencies-authentication-index.md  (wrong order)
❌ auth-deps-index.md                    (unclear abbreviations)
❌ authentication-dependency-index.md    (singular relationship type)
❌ authentication-depends-on-index.md    (verbose, use -dependencies)
```

---

## Special Cases

### Custom/Temporary Indexes

**Pattern:** `custom-{purpose}-index.md`

**Location:** `_indexes/custom/` (create subdirectory if needed)

**Examples:**
```
custom-sprint-2024-01-index.md
custom-security-audit-q1-index.md
custom-onboarding-backend-index.md
custom-migration-plan-index.md
```

**Rules:**
- Prefix with `custom-` for clarity
- Include context (date, sprint, team, project)
- Still follow kebab-case and lowercase rules
- Clean up when no longer needed

---

### Template Files

**Pattern:** `{template-purpose}-TEMPLATE.md`

**Location:** `_indexes/templates/`

**Examples:**
```
INDEX_TEMPLATE.md
by-area-TEMPLATE.md
by-type-TEMPLATE.md
by-priority-TEMPLATE.md
```

**Rules:**
- `TEMPLATE` suffix in UPPERCASE for high visibility
- Main template: `INDEX_TEMPLATE.md` (all caps)
- Specialized templates: `{type}-TEMPLATE.md`

---

### Schema/Configuration Files

**Pattern:** `.{config-name}.{extension}`

**Examples:**
```
.index-schema.json
.validation-rules.yaml
.naming-config.json
```

**Rules:**
- Prefix with `.` (hidden file)
- Use descriptive name
- Appropriate extension (`.json`, `.yaml`, `.md`)

---

## Multi-Word Components

### Handling Multi-Word Scopes

Use hyphens to separate words within a scope:

**Correct:**
```
✅ authentication-authorization-domain-index.md
✅ continuous-integration-domain-index.md
✅ user-interface-domain-index.md
✅ data-encryption-privacy-domain-index.md
```

**Incorrect:**
```
❌ authenticationAuthorization-domain-index.md  (camelCase)
❌ authentication_authorization-domain-index.md (mixed case)
❌ authauth-domain-index.md                     (unclear abbreviation)
```

### Abbreviation Guidelines

**Use Common Abbreviations:**
- `api` for Application Programming Interface
- `ui` for User Interface
- `db` for Database
- `auth` for Authentication (when used with another word, e.g., `api-auth`)
- `ci-cd` for Continuous Integration/Continuous Deployment
- `adr` for Architecture Decision Record

**Avoid Unclear Abbreviations:**
- ❌ `sec` (security or section?)
- ❌ `arch` (architecture or archive?)
- ❌ `inf` (infrastructure or information?)
- ❌ `auth` alone (authentication or authorization or authority?)

**When in Doubt:** Spell it out fully.

---

## Validation Rules

### Automated Checks

All index files are validated against these rules:

```python
import re

def validate_index_filename(filename: str) -> tuple[bool, list[str]]:
    """
    Validate index filename against naming conventions.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Rule 1: Must end with -index.md
    if not filename.endswith('-index.md'):
        errors.append("Must end with '-index.md'")
    
    # Rule 2: Must be lowercase
    if filename != filename.lower():
        errors.append("Must be lowercase only")
    
    # Rule 3: Only a-z, 0-9, hyphen, and .md
    if not re.match(r'^[a-z0-9-]+-index\.md$', filename):
        errors.append("Only a-z, 0-9, and hyphen allowed")
    
    # Rule 4: Must not have consecutive hyphens
    if '--' in filename:
        errors.append("No consecutive hyphens allowed")
    
    # Rule 5: Must not start or end with hyphen (before -index.md)
    name_part = filename.replace('-index.md', '')
    if name_part.startswith('-') or name_part.endswith('-'):
        errors.append("Cannot start or end with hyphen")
    
    # Rule 6: Maximum length (50 chars before .md)
    if len(filename) > 53:  # 50 + .md = 53
        errors.append("Maximum 50 characters (excluding .md)")
    
    # Rule 7: Minimum length (3 chars before -index.md)
    if len(name_part) < 3:
        errors.append("Minimum 3 characters required")
    
    return (len(errors) == 0, errors)
```

### Manual Review Checklist

- [ ] Filename follows `{scope}-{type}-index.md` pattern
- [ ] All lowercase (no uppercase letters)
- [ ] Uses hyphens, not underscores or spaces
- [ ] Ends with `-index.md`
- [ ] Under 50 characters (excluding `.md`)
- [ ] Descriptive and unambiguous
- [ ] Matches index type subdirectory
- [ ] No unclear abbreviations

---

## Migration Guide

### Renaming Existing Indexes

If existing indexes don't follow conventions:

**Process:**
1. **Create mapping file**: Document old → new names
2. **Create new index**: Copy content, update metadata
3. **Update all references**: Search vault for `[[old-name]]`, replace with `[[new-name]]`
4. **Add redirect**: Add note in old file pointing to new file
5. **Deprecate old file**: Move to `_indexes/deprecated/`
6. **After 30 days**: Delete old file if no references remain

**Example:**
```markdown
Old: Security_Index.md
New: security-domain-index.md

Migration:
1. Create: _indexes/by-area/security-domain-index.md
2. Search vault for: [[Security_Index]]
3. Replace with: [[security-domain-index]]
4. Add to Security_Index.md:
   > **DEPRECATED:** This index has been renamed to [[security-domain-index]]
5. Move Security_Index.md to _indexes/deprecated/
6. Delete after 30 days if no references
```

---

## Common Naming Patterns

### Domain Indexes (by-area/)

```
{domain}-domain-index.md

Examples:
- security-domain-index.md
- api-domain-index.md
- infrastructure-domain-index.md
- testing-domain-index.md
- documentation-domain-index.md
```

### Type Indexes (by-type/)

```
{document-type}-type-index.md

Examples:
- specification-type-index.md
- guide-type-index.md
- adr-type-index.md
- runbook-type-index.md
```

### Priority Indexes (by-priority/)

```
{priority-level}-priority-index.md

Examples:
- p0-critical-priority-index.md
- p1-high-priority-index.md
- p2-medium-priority-index.md
- p3-low-priority-index.md
```

### Status Indexes (by-status/)

```
{status}-status-index.md

Examples:
- active-status-index.md
- deprecated-status-index.md
- archived-status-index.md
- in-progress-status-index.md
```

### Cross-Reference Indexes (cross-reference/)

```
{scope}-{relationship}-index.md

Examples:
- authentication-dependencies-index.md
- api-conflicts-index.md
- architecture-alternatives-index.md
```

---

## Best Practices

### DO:
- ✅ Use descriptive, semantic names
- ✅ Be consistent with existing indexes in same subdirectory
- ✅ Use standard abbreviations (api, ui, db, ci-cd)
- ✅ Keep names concise but clear
- ✅ Run validation before committing

### DON'T:
- ❌ Use uppercase letters
- ❌ Use underscores or spaces
- ❌ Create ambiguous abbreviations
- ❌ Exceed 50 character limit
- ❌ Omit `-index` suffix
- ❌ Use file name as only documentation (add metadata too)

---

## Troubleshooting

### Issue: Validation Fails with "Must be lowercase"

**Cause:** Filename contains uppercase letters.

**Solution:** Rename file to all lowercase.
```
❌ Security-Domain-Index.md
✅ security-domain-index.md
```

### Issue: Validation Fails with "Only a-z, 0-9, and hyphen allowed"

**Cause:** Filename contains underscores, spaces, or special characters.

**Solution:** Replace with hyphens.
```
❌ security_domain_index.md
❌ security domain index.md
✅ security-domain-index.md
```

### Issue: Validation Fails with "Must end with '-index.md'"

**Cause:** Missing required suffix.

**Solution:** Add `-index.md` suffix.
```
❌ security-domain.md
❌ security.md
✅ security-domain-index.md
```

### Issue: Name Seems Too Long

**Cause:** Over 50 characters.

**Solution:** Use abbreviations or restructure.
```
❌ continuous-integration-continuous-deployment-domain-index.md (62 chars)
✅ ci-cd-domain-index.md (20 chars)
```

### Issue: Unclear if Name is Descriptive Enough

**Test:** Ask: "Would someone unfamiliar with the project understand what this index contains?"

**Examples:**
```
❌ stuff-domain-index.md          (too vague)
❌ things-type-index.md            (meaningless)
❌ misc-domain-index.md            (miscellaneous is a code smell)
✅ security-domain-index.md        (clear domain)
✅ runbook-type-index.md           (clear type)
```

---

## Validation Script

Location: `scripts/validate-index-names.py`

**Usage:**
```bash
# Validate all indexes
python scripts/validate-index-names.py

# Validate specific file
python scripts/validate-index-names.py _indexes/by-area/security-domain-index.md

# Auto-fix naming issues (prompts for confirmation)
python scripts/validate-index-names.py --fix

# Check without fixing
python scripts/validate-index-names.py --check-only
```

**Sample Output:**
```
✅ _indexes/by-area/security-domain-index.md - PASS
❌ _indexes/by-area/Security_Index.md - FAIL
   - Must be lowercase only
   - Must end with '-index.md'
   - Only a-z, 0-9, and hyphen allowed
   
Suggested fix: security-index.md or security-domain-index.md
```

---

## Summary Quick Reference

| Index Type | Pattern | Example |
|------------|---------|---------|
| Domain (by-area) | `{domain}-domain-index.md` | `security-domain-index.md` |
| Type (by-type) | `{type}-type-index.md` | `runbook-type-index.md` |
| Priority (by-priority) | `{level}-priority-index.md` | `p0-critical-priority-index.md` |
| Status (by-status) | `{status}-status-index.md` | `active-status-index.md` |
| Cross-Ref (cross-reference) | `{scope}-{relation}-index.md` | `api-dependencies-index.md` |
| Custom | `custom-{purpose}-index.md` | `custom-sprint-2024-01-index.md` |
| Template | `{name}-TEMPLATE.md` | `INDEX_TEMPLATE.md` |

**Character Set:** `a-z`, `0-9`, `-` (hyphen only)

**Required Suffix:** `-index.md`

**Max Length:** 50 characters (excluding `.md`)

**Case:** Lowercase only

---

**Version:** 1.0  
**Last Updated:** 2024-01-15  
**Maintainer:** AGENT-002 (Indexes Subdirectory Specialist)  
**Enforcement:** Automated validation in CI/CD pipeline  
**Related Documents:**
- [[_indexes/README.md]] - Index system overview
- [[_indexes/.index-schema.json]] - JSON schema for validation
- `scripts/validate-index-names.py` - Automated validation script

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

