# Version/Release Search Queries

Search documents by version number, release identifier, or version history.

## Query 1: Documents by Version Number

```dataview
TABLE 
  metadata_version as "Version",
  metadata_status as "Status",
  metadata_owner as "Owner",
  file.mtime as "Last Modified"
FROM ""
WHERE metadata_version
SORT metadata_version DESC
```

**Version Format:**
- Semantic versioning: `1.2.3` (major.minor.patch)
- Date-based: `2024.03.15`
- Custom: `v1.0.0-beta`

---

## Query 2: Latest Version of Each Document

```dataview
TABLE 
  metadata_version as "Latest Version",
  file.mtime as "Released",
  metadata_owner as "Owner",
  metadata_release as "Release"
FROM ""
WHERE metadata_version AND contains(metadata_status, "published")
SORT metadata_version DESC
LIMIT 20
```

**Latest Versions:**
- Filter by published status
- Sort by version descending
- Show most recent releases

---

## Query 3: Documents by Release Identifier

```dataview
TABLE 
  metadata_release as "Release",
  metadata_version as "Version",
  metadata_status as "Status",
  file.name as "Document"
FROM ""
WHERE contains(metadata_release, "v2024.1")
SORT file.name ASC
```

**Release Tracking:**
- Group documents by release
- Track release contents
- Version bundles

---

## Query 4: Version History Tracking

```dataview
TABLE 
  metadata_version as "Current Version",
  metadata_version_history as "History",
  file.mtime as "Last Updated",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_version_history
SORT file.mtime DESC
LIMIT 30
```

**Historical Tracking:**
- Track version changes over time
- Audit version progression
- Change frequency analysis

---

## Query 5: Documents with Multiple Versions

```dataview
TABLE 
  file.name as "Document",
  metadata_version as "Version",
  metadata_previous_version as "Previous",
  metadata_release as "Release"
FROM ""
WHERE metadata_previous_version
SORT file.mtime DESC
```

**Version Chains:**
- Link versions together
- Track version evolution
- Migration paths

---

## Query 6: Version by Release Date

```dataview
TABLE 
  metadata_version as "Version",
  metadata_release_date as "Released",
  metadata_release as "Release Name",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_release_date
SORT metadata_release_date DESC
```

**Release Timeline:**
- Track release dates
- Version chronology
- Release cadence analysis

---

## Query 7: Major Version Groups

```dataview
TABLE 
  length(rows) as "Document Count",
  rows.metadata_version as "Versions"
FROM ""
WHERE metadata_version
GROUP BY metadata_version[0:1]
SORT metadata_version[0:1] DESC
```

**Major Version Grouping:**
- Extract major version number
- Count docs per major version
- Version distribution

---

## Query 8: Beta/RC/Stable Version Filter

```dataview
TABLE 
  metadata_version as "Version",
  metadata_version_stability as "Stability",
  metadata_status as "Status",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_version_stability, "beta")
SORT file.mtime DESC
```

**Stability Levels:**
- `alpha`: Early development
- `beta`: Feature complete, testing
- `rc`: Release candidate
- `stable`: Production ready

---

## Query 9: Version with Breaking Changes

```dataview
TABLE 
  metadata_version as "Version",
  metadata_breaking_changes as "Breaking Changes",
  metadata_release_date as "Released",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_breaking_changes
SORT metadata_release_date DESC
```

**Breaking Changes:**
- Track API/behavior changes
- Migration guidance
- Deprecation notices

---

## Query 10: Documents Missing Version

```dataview
TABLE 
  file.name as "Document",
  file.folder as "Location",
  metadata_status as "Status",
  file.mtime as "Modified"
FROM ""
WHERE contains(metadata_status, "published") AND (!metadata_version OR metadata_version = "")
SORT file.mtime DESC
```

**Data Quality:**
- Published docs without versions
- Enforce versioning standards
- Incomplete metadata

---

## Query 11: Version Comparison (Side by Side)

```dataview
TABLE 
  metadata_version as "Current",
  metadata_previous_version as "Previous",
  metadata_changelog as "Changes",
  file.mtime as "Updated"
FROM ""
WHERE metadata_previous_version AND metadata_changelog
SORT file.mtime DESC
LIMIT 20
```

**Change Tracking:**
- Compare versions
- Changelog summaries
- Version diffs

---

## Query 12: Release Notes by Version

```dataview
TABLE 
  metadata_version as "Version",
  metadata_release_notes as "Release Notes",
  metadata_release_date as "Released",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_release_notes
SORT metadata_release_date DESC
```

**Release Documentation:**
- Version-specific release notes
- What's new summaries
- User-facing changes

---

## Query 13: Version by Document Type

```dataview
TABLE 
  metadata_type as "Type",
  metadata_version as "Version",
  length(rows) as "Count"
FROM ""
WHERE metadata_version AND metadata_type
GROUP BY metadata_type, metadata_version
SORT metadata_type ASC, metadata_version DESC
```

**Type-Version Matrix:**
- Cross-reference type and version
- Version coverage by type
- Documentation completeness

---

## Query 14: Deprecated Versions

```dataview
TABLE 
  metadata_version as "Version",
  metadata_deprecated_date as "Deprecated",
  metadata_replacement_version as "Replaced By",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_deprecated_date
SORT metadata_deprecated_date DESC
```

**Version Lifecycle:**
- Track deprecated versions
- Migration paths
- End-of-life planning

---

## Query 15: Version with Dependencies

```dataview
TABLE 
  metadata_version as "Version",
  metadata_dependencies as "Dependencies",
  metadata_compatible_versions as "Compatible With",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_dependencies OR metadata_compatible_versions
SORT file.mtime DESC
```

**Dependency Management:**
- Track version dependencies
- Compatibility matrices
- Integration planning

---

## Query 16: Latest Stable Release

```dataview
TABLE 
  metadata_version as "Version",
  metadata_release as "Release",
  metadata_release_date as "Released",
  metadata_owner as "Owner"
FROM ""
WHERE contains(metadata_status, "published") 
  AND contains(metadata_version_stability, "stable")
SORT metadata_release_date DESC
LIMIT 1
```

**Current Production:**
- Identify latest stable version
- Production deployment reference
- Recommended version

---

## Query 17: Pre-Release Versions

```dataview
TABLE 
  metadata_version as "Version",
  metadata_version_stability as "Stability",
  metadata_release_date as "Released",
  metadata_owner as "Owner"
FROM ""
WHERE metadata_version_stability 
  AND !contains(metadata_version_stability, "stable")
SORT metadata_release_date DESC
```

**Early Access:**
- Alpha, beta, RC versions
- Pre-release tracking
- Testing coordination

---

## Query 18: Version Release Velocity

```dataview
TABLE 
  metadata_release as "Release",
  length(rows) as "Versions",
  min(rows.metadata_release_date) as "Start Date",
  max(rows.metadata_release_date) as "End Date"
FROM ""
WHERE metadata_release AND metadata_release_date
GROUP BY metadata_release
SORT max(rows.metadata_release_date) DESC
```

**Release Metrics:**
- Versions per release
- Release duration
- Velocity analysis

---

## Semantic Versioning Standard

```
MAJOR.MINOR.PATCH

1.0.0 -> Initial release
1.1.0 -> New features (backward compatible)
1.1.1 -> Bug fixes (backward compatible)
2.0.0 -> Breaking changes
```

### Version Increment Rules

| Type | Increment | Description |
|------|-----------|-------------|
| MAJOR | X.0.0 | Breaking changes, incompatible API |
| MINOR | 1.X.0 | New features, backward compatible |
| PATCH | 1.0.X | Bug fixes, backward compatible |

## Expected Metadata Fields

```yaml
---
# Version Information
metadata_version: "1.2.3"
metadata_version_stability: alpha|beta|rc|stable
metadata_previous_version: "1.1.0"
metadata_version_history: ["1.0.0", "1.1.0", "1.2.0", "1.2.3"]

# Release Information
metadata_release: "v2024.1"
metadata_release_date: YYYY-MM-DD
metadata_release_notes: "Brief summary of changes"

# Change Tracking
metadata_changelog: "[[CHANGELOG-1.2.3]]"
metadata_breaking_changes: true|false
metadata_breaking_change_description: "Removed deprecated API endpoints"

# Dependencies
metadata_dependencies: ["library-1:2.0.0", "library-2:3.1.0"]
metadata_compatible_versions: ["1.0.x", "1.1.x", "1.2.x"]

# Deprecation
metadata_deprecated_date: YYYY-MM-DD
metadata_replacement_version: "2.0.0"
metadata_end_of_life_date: YYYY-MM-DD

# Context
metadata_status: draft|review|published|deprecated
metadata_owner: team-name or person-name
metadata_type: documentation|code|configuration|report
---
```

## Version Lifecycle States

| State | Stability | Description | Audience |
|-------|-----------|-------------|----------|
| `alpha` | Unstable | Early development, frequent changes | Developers only |
| `beta` | Experimental | Feature complete, testing phase | Early adopters |
| `rc` | Stable | Release candidate, final testing | QA teams |
| `stable` | Production | Production ready, fully supported | All users |
| `deprecated` | End-of-life | Obsolete, use replacement | Migration only |

## Version Management Best Practices

1. **Semantic Versioning**: Follow SemVer 2.0.0 standard
2. **Changelog**: Maintain changelog for every version
3. **Breaking Changes**: Clearly document API breaks
4. **Deprecation Policy**: 2-version deprecation window
5. **LTS Versions**: Long-term support for major versions
6. **Release Notes**: User-facing summaries for each release
7. **Version Tags**: Git tags for each release
8. **Compatibility Matrix**: Document version dependencies

## Version Branching Strategy

```
main (stable releases)
  └── develop (next version)
      ├── feature/new-feature
      ├── bugfix/critical-fix
      └── release/1.2.0 (release candidate)
```

## Release Checklist

- [ ] Version number updated (SemVer)
- [ ] Changelog updated with changes
- [ ] Release notes written
- [ ] Breaking changes documented
- [ ] Dependencies updated
- [ ] Tests passing (100% coverage)
- [ ] Documentation updated
- [ ] Migration guide created (if breaking)
- [ ] Git tag created
- [ ] Release published

## Performance Optimization

1. **Index Version Field**: Automatically indexed by Dataview
2. **Limit Results**: Use `LIMIT` for large repositories
3. **Folder Scoping**: Narrow with `FROM "folder/path"`
4. **Version Sorting**: Dataview handles version sorting natively

## Testing Checklist

- [ ] Query returns results in <1 second
- [ ] Version sorting is correct (semantic)
- [ ] Missing versions handled gracefully
- [ ] Version history displayed properly
- [ ] Release filtering works correctly
- [ ] Stability levels recognized

## Troubleshooting

**Incorrect Version Sorting:**
- Use semantic versioning format: `1.2.3`
- Pad version numbers: `01.02.03` (if needed)
- Use `SORT metadata_version DESC` explicitly

**Missing Versions:**
- Verify metadata field name: `metadata_version`
- Check YAML frontmatter format
- Ensure quotes around version strings

**Performance Issues:**
- Add `LIMIT` clause
- Narrow folder scope
- Reduce version history complexity
- Use indexed fields
