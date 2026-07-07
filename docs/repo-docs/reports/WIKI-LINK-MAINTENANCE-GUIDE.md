# Wiki Link Maintenance Guide

**Created by**: AGENT-072  
**Purpose**: Guide for maintaining and extending wiki links in the Project-AI Obsidian vault  
**Date**: 2026-04-20

---

## Quick Reference

### Wiki Link Format

✅ **Correct**:
```markdown
[[src/app/core/ai_systems.py]]
[[relationships/core-ai/01-FourLaws-Relationship-Map.md]]
[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Governance Overview]]
[[source-docs/core/01-ai_systems.md#fourlaws-system]]
```

❌ **Incorrect**:
```markdown
[[ai_systems.py]]  # Missing path
[[relationships/core-ai/01-FourLaws-Relationship-Map]]  # Missing .md
[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]  # Wrong brackets
```

---

## Adding New Links

### 1. Source Code Links

**Pattern**: Link from documentation to Python files

```markdown
The [[src/app/core/ai_systems.py|FourLaws system]] implements ethics validation.

See [[src/app/agents/oversight.py]] for safety monitoring.
```

**Rules**:
- Always use full path from repository root
- Include `.py` extension
- Use `|alias` for human-readable text

### 2. Cross-Documentation Links

**Pattern**: Link between relationship maps and source docs

```markdown
For implementation details, see [[source-docs/core/01-ai_systems.md]].

This system is part of the [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|governance framework]].
```

**Rules**:
- Always include `.md` extension
- Use relative paths for same-directory links
- Use full paths for cross-directory links

### 3. Anchor Links

**Pattern**: Link to specific sections

```markdown
See the [[relationships/core-ai/01-FourLaws-Relationship-Map.md#risk-assessment--mitigation|risk assessment]].
```

**Format**: `[[path/to/file.md#section-header|Display Text]]`

---

## Backlinks

### Adding "Related Documentation" Sections

**Template**:
```markdown
---

## Related Documentation

- [[source-docs/core/01-ai_systems.md]]
- [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]]
- [[relationships/constitutional/01_constitutional_systems_overview.md]]
```

**Placement**: Add at end of file, before final `---`

**When to Add**:
- Relationship maps should link to source docs
- Source docs should link back to relationship maps
- Cross-system documentation should link bidirectionally

---

## Validation

### Manual Check

1. **Click every link** in Obsidian to verify it resolves
2. **Check Graph View** to ensure connections appear
3. **Test backlinks** panel shows incoming references

### Automated Validation

Run PowerShell script:

```powershell
# Validate all wiki links
$brokenLinks = @()
Get-ChildItem -Path "relationships", "source-docs" -Filter "*.md" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $links = [regex]::Matches($content, '\[\[([^\|\]]+)(\|[^\]]+)?\]\]')
    
    foreach ($match in $links) {
        $target = $match.Groups[1].Value -replace '/', '\'
        $targetPath = Join-Path (Get-Location) $target
        
        if (-not (Test-Path $targetPath)) {
            $brokenLinks += @{
                File = $_.Name
                Target = $match.Groups[1].Value
            }
        }
    }
}

if ($brokenLinks.Count -gt 0) {
    Write-Host "⚠️ Broken links found:" -ForegroundColor Red
    $brokenLinks | ForEach-Object {
        Write-Host "  $($_.File) -> $($_.Target)" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ All links valid!" -ForegroundColor Green
}
```

---

## Common Patterns

### Linking Core AI Systems

**Six core systems in `ai_systems.py`**:

```markdown
- [[src/app/core/ai_systems.py|FourLaws]]
- [[src/app/core/ai_systems.py|AIPersona]]
- [[src/app/core/ai_systems.py|MemoryExpansionSystem]]
- [[src/app/core/ai_systems.py|LearningRequestManager]]
- [[src/app/core/ai_systems.py|PluginManager]]
- [[src/app/core/ai_systems.py|CommandOverrideSystem]]
```

**Extended CommandOverride**:

```markdown
[[src/app/core/command_override.py|Extended CommandOverride]]
```

### Linking Agents

```markdown
- [[src/app/agents/oversight.py|Oversight Agent]]
- [[src/app/agents/planner.py|Planner Agent]]
- [[src/app/agents/validator.py|Validator Agent]]
- [[src/app/agents/explainability.py|Explainability Agent]]
```

### Linking GUI Components

```markdown
- [[src/app/gui/leather_book_interface.py|Leather Book Interface]]
- [[src/app/gui/persona_panel.py|Persona Panel]]
- [[src/app/gui/dashboard_handlers.py|Dashboard Handlers]]
```

### Linking Relationship Maps

**Core AI**:
```markdown
[[relationships/core-ai/01-FourLaws-Relationship-Map.md]]
[[relationships/core-ai/02-AIPersona-Relationship-Map.md]]
```

**Governance**:
```markdown
[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]]
[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md]]
```

**Constitutional**:
```markdown
[[relationships/constitutional/01_constitutional_systems_overview.md]]
[[relationships/constitutional/02_enforcement_chains.md]]
```

---

## Troubleshooting

### Link Not Resolving

**Issue**: Link appears but doesn't navigate

**Diagnosis**:
1. Check if file exists: `Test-Path "path\to\file.md"`
2. Verify path uses forward slashes: `[[path/to/file.md]]`
3. Ensure `.md` extension included
4. Check for typos in filename

**Fix**:
```markdown
# Before
[[relationships/governance/GOVERNANCE_SYSTEMS]]

# After
[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]]
```

### Broken Backlinks

**Issue**: Backlink panel shows "No backlinks"

**Diagnosis**:
1. Verify linking file uses correct path
2. Check if linking file is in vault
3. Ensure link syntax is `[[...]]` not `[...]`

**Fix**: Add `.md` to all documentation links

### Anchor Not Found

**Issue**: Link navigates to file but not section

**Diagnosis**:
1. View raw markdown of target file
2. Find actual header text
3. Convert to lowercase, replace spaces with hyphens

**Example**:
```markdown
# Header: "Risk Assessment & Mitigation"
# Anchor: #risk-assessment--mitigation

[[file.md#risk-assessment--mitigation]]
```

---

## Best Practices

### DO ✅

- **Use full paths** from repository root for source code
- **Include `.md` extension** for all documentation links
- **Add backlinks** when creating relationship maps
- **Test links** before committing documentation
- **Use aliases** for readability: `[[long/path.md|Short Name]]`
- **Keep link text semantic**: describe what the link points to

### DON'T ❌

- **Don't use relative paths** for source code (`../core/file.py`)
- **Don't omit `.md`** from documentation links
- **Don't create circular references** (A→B, B→A with same alias)
- **Don't link to non-existent files** (check existence first)
- **Don't over-link**: only link first mention or contextually important
- **Don't use hardcoded line numbers** in links (fragile)

---

## Updating After Code Changes

### File Renamed

**Example**: `ai_systems.py` → `ai_core_systems.py`

**Impact**: All links to old file will break

**Solution**:
```powershell
# Find all references
grep -r "ai_systems.py" relationships/ source-docs/

# Update links
# [[src/app/core/ai_systems.py]] → [[src/app/core/ai_core_systems.py]]
```

### File Moved

**Example**: `src/app/core/governance.py` → `src/app/core/governance/pipeline.py`

**Impact**: Path-based links will break

**Solution**: Update all references with new path

### Module Refactored

**Example**: `ai_systems.py` split into 6 separate files

**Impact**: Need to update links to point to specific files

**Strategy**:
1. Create new links for each split module
2. Add deprecation notice to old link
3. Update all references over time

---

## Statistics (As of 2026-04-20)

**Current Coverage**:
- Total Links: 832
- Source Code Links: 130
- Relationship Maps: 594
- Documentation Links: 12
- Other: 96

**Files Enhanced**: 31/36 (86.1%)

**Validation**: 743/832 valid (89.3%)

**Forward-References**: 89 (to be resolved in Phase 6)

---

## Future Enhancements

### Planned Improvements

1. **Semantic Search**: Add search aliases to common files
2. **Tag Integration**: Link to files by tag (`#core-ai`, `#governance`)
3. **MOC Creation**: Map of Content files for major subsystems
4. **Link Analytics**: Track most-referenced files for refactoring priority
5. **Automated Validation**: CI/CD check for broken links

### Template for New Relationship Maps

```markdown
---
title: "SystemName - Relationship Map"
agent: AGENT-XXX
mission: System Relationship Mapping
created: YYYY-MM-DD
status: Active
---

# SystemName - Comprehensive Relationship Map

## Executive Summary

[Description with links to related systems]

**Source Code**: [[src/app/core/filename.py]]

---

## 1. WHAT: Component Functionality

[Content with inline links to dependencies]

---

## Related Documentation

- [[source-docs/core/XX-system.md]]
- [[relationships/core-ai/XX-System-Relationship-Map.md]]

---
```

---

## Contact

**Maintainer**: AGENT-072  
**Questions**: See `AGENT-072-LINK-REPORT.md` for detailed documentation  
**Updates**: Follow Obsidian vault Phase 6-7 for link resolution

---

**Version**: 1.0  
**Last Updated**: 2026-04-20  
**Next Review**: Phase 6 completion (GUI/Agent relationships)
