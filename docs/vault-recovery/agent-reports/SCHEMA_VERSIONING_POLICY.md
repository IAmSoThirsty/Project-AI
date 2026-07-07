# Project-AI Metadata Schema Versioning Policy

**Version:** 1.0.0  
**Effective Date:** 2026-04-20  
**Status:** Active  
**Owner:** Architecture Team

---

## Table of Contents

1. [Purpose](#purpose)
2. [Versioning Strategy](#versioning-strategy)
3. [Version Numbering](#version-numbering)
4. [Change Categories](#change-categories)
5. [Deprecation Process](#deprecation-process)
6. [Migration Support](#migration-support)
7. [Compatibility Guarantees](#compatibility-guarantees)
8. [Release Process](#release-process)
9. [Version History](#version-history)

---

## Purpose

This document establishes the versioning policy for the Project-AI Documentation Metadata Schema. The policy ensures:

- **Predictable Evolution**: Clear rules for schema changes
- **Backward Compatibility**: Existing documents remain valid
- **Migration Support**: Tools and guidance for upgrades
- **Forward Compatibility**: Graceful handling of unknown fields
- **Transparency**: Documented rationale for all changes

---

## Versioning Strategy

### Semantic Versioning

The metadata schema follows **Semantic Versioning 2.0.0** (`MAJOR.MINOR.PATCH`):

```
MAJOR.MINOR.PATCH[-prerelease][+metadata]
```

**Example Versions:**
- `1.0.0` - Initial production release
- `1.1.0` - Added optional fields (backward compatible)
- `2.0.0` - Changed required fields (breaking change)
- `2.0.0-beta.1` - Pre-release version
- `2.0.0+20260420` - Build metadata

### Version Components

#### MAJOR Version (X.0.0)

**Incremented when:**
- Removing required fields
- Changing field data types (e.g., string → integer)
- Removing enum values
- Changing field names (without migration path)
- Breaking validation rules

**Example:**
```yaml
# v1.0.0
status: draft  # Enum: draft, active, archived

# v2.0.0 (BREAKING)
status: draft  # Enum: draft, review, active, deprecated, archived
# Added 'review' and 'deprecated' (OK)
# Removed 'archived' (BREAKING - documents using it would fail)
```

**Migration Required:** Yes

#### MINOR Version (1.X.0)

**Incremented when:**
- Adding new optional fields
- Adding new enum values
- Adding new document types
- Relaxing validation rules
- Adding backward-compatible features

**Example:**
```yaml
# v1.0.0
# No review_status field

# v1.1.0 (BACKWARD COMPATIBLE)
review_status:  # NEW optional field
  reviewed: true
  reviewers: []
```

**Migration Required:** No (but recommended)

#### PATCH Version (1.0.X)

**Incremented when:**
- Documentation fixes
- Clarifications in field descriptions
- Example updates
- Typo corrections
- Schema comment improvements

**No schema changes** - Only documentation updates.

**Migration Required:** No

### Pre-release Versions

**Format:** `MAJOR.MINOR.PATCH-identifier`

**Identifiers:**
- `alpha.N` - Early testing, unstable
- `beta.N` - Feature complete, testing phase
- `rc.N` - Release candidate, final testing

**Example:** `2.0.0-beta.1`, `2.1.0-rc.2`

**Stability:** Not recommended for production use

### Build Metadata

**Format:** `MAJOR.MINOR.PATCH+metadata`

**Example:** `1.0.0+20260420`, `2.0.0+build.123`

**Purpose:** CI/CD tracking, build identification

---

## Change Categories

### Breaking Changes (Major)

**Definition:** Changes that invalidate existing documents or require manual updates.

**Examples:**
1. **Removing Required Field**
   ```yaml
   # BEFORE (v1.0.0)
   required: [title, id, type, author, created_date]
   
   # AFTER (v2.0.0)
   required: [title, id, type, created_date]  # Removed 'author'
   ```

2. **Changing Field Type**
   ```yaml
   # BEFORE
   estimated_time: "45 minutes"  # String
   
   # AFTER
   estimated_time: 45  # Integer (minutes)
   ```

3. **Renaming Field Without Alias**
   ```yaml
   # BEFORE
   document_type: audit
   
   # AFTER
   type: audit  # 'document_type' no longer recognized
   ```

**Policy:** Breaking changes require:
- 6-month deprecation notice
- Migration script
- Major version bump
- Comprehensive changelog

### Non-Breaking Changes (Minor)

**Definition:** Additions that enhance schema without breaking existing documents.

**Examples:**
1. **Adding Optional Field**
   ```yaml
   # v1.1.0 adds optional field
   test_coverage:
     has_tests: true
     coverage_percent: 85
   ```

2. **Adding Enum Value**
   ```yaml
   # BEFORE
   classification: [public, internal, confidential]
   
   # AFTER (v1.2.0)
   classification: [public, internal, confidential, secret]
   ```

3. **Relaxing Validation**
   ```yaml
   # BEFORE
   title: {maxLength: 100}
   
   # AFTER (v1.3.0)
   title: {maxLength: 200}  # More permissive
   ```

**Policy:** Non-breaking changes:
- Announced 30 days before release
- Minor version bump
- Optional adoption

### Documentation Changes (Patch)

**Definition:** Updates that don't change schema behavior.

**Examples:**
- Improved field descriptions
- Additional examples
- Clarified validation rules
- Fixed typos
- Updated FAQs

**Policy:** Patch changes:
- No announcement required
- No migration needed
- Immediate adoption

---

## Deprecation Process

### Deprecation Timeline

```
Month 0: Deprecation announced
  ↓
Month 1-6: Deprecation period
  - Warnings emitted by tools
  - Migration script available
  - Documentation updated
  ↓
Month 6: Removal in next major version
  - Field removed from schema
  - Validation fails for deprecated usage
  - Migration mandatory
```

### Deprecation Announcement

**Format:**
```markdown
## Deprecation Notice: Field 'old_field'

**Deprecated In:** v1.5.0  
**Removal In:** v2.0.0  
**Replacement:** Use 'new_field' instead  
**Migration Script:** migrate-v1.5-to-v2.0.ps1  
**Rationale:** [Explanation of why field is deprecated]
```

**Channels:**
- Schema changelog
- GitHub discussions
- Documentation site
- Validation tool warnings

### Deprecation Markers

**In JSON Schema:**
```json
{
  "old_field": {
    "type": "string",
    "deprecated": true,
    "description": "DEPRECATED: Use 'new_field' instead. Will be removed in v2.0.0"
  }
}
```

**In YAML Schema:**
```yaml
old_field:
  type: string
  deprecated: true
  x-deprecated-reason: "Replaced by 'new_field' for consistency"
  x-removed-in: "2.0.0"
```

---

## Migration Support

### Migration Scripts

**Provided For:**
- All major version upgrades
- Any minor version with recommended changes
- Field renames and restructuring

**Script Requirements:**
1. Dry-run mode (`-DryRun` flag)
2. Backup creation (`-Backup` flag)
3. Validation after migration
4. Detailed logging
5. Rollback instructions

**Example:**
```powershell
# Dry run to preview changes
.\migrate-metadata-v1-to-v2.ps1 -DryRun

# Create backup and migrate
.\migrate-metadata-v1-to-v2.ps1 -Backup

# Validate results
.\validate-metadata.ps1 -Recursive
```

### Migration Documentation

**Included In Each Migration:**
1. **Changelog**: What changed and why
2. **Breaking Changes**: List of incompatibilities
3. **Field Mappings**: Old → New field mappings
4. **Manual Steps**: Changes requiring human review
5. **Validation**: How to verify successful migration
6. **Rollback**: How to undo migration

---

## Compatibility Guarantees

### Backward Compatibility

**Within Same Major Version:**
- ✅ Documents valid in v1.0.0 remain valid in v1.x.x
- ✅ New optional fields can be ignored
- ✅ Parsers must ignore unknown fields

**Example:**
```yaml
# Document created with v1.0.0
title: "My Document"
id: "my-doc"
type: guide
# ... other v1.0.0 fields ...

# Valid in v1.5.0 even without new optional fields
# Validator: "Unknown field 'review_status' in v1.0.0 doc → Ignore"
```

### Forward Compatibility

**Unknown Fields:**
- Parsers MUST ignore unknown fields
- Validators MAY warn about unknown fields
- Exporters SHOULD preserve unknown fields

**Example:**
```yaml
# Document with v2.0.0 features
review_status:
  reviewed: true

# Parsed by v1.x.x validator
# → Unknown field 'review_status' → Warning → Continue
```

**Custom Fields:**
- Must use `x-` prefix to avoid collisions
- Preserved across versions
- Not validated by schema

### Cross-Version Compatibility

| Document Version | Schema v1.x | Schema v2.x | Schema v3.x |
|------------------|-------------|-------------|-------------|
| v1.x documents   | ✅ Valid     | ✅ Valid     | ⚠️ Deprecated |
| v2.x documents   | ⚠️ Unknown  | ✅ Valid     | ✅ Valid     |
| v3.x documents   | ❌ Invalid  | ⚠️ Unknown  | ✅ Valid     |

---

## Release Process

### Pre-Release Checklist

- [ ] All changes documented in CHANGELOG.md
- [ ] Migration script created (if major version)
- [ ] All examples updated
- [ ] JSON Schema updated
- [ ] YAML Schema updated
- [ ] Documentation updated
- [ ] Validation tests pass
- [ ] Migration tests pass
- [ ] Community review (14 days for major, 7 days for minor)

### Release Steps

1. **Prepare Release**
   - Update version numbers
   - Finalize changelog
   - Tag Git commit

2. **Publish Schemas**
   - Update JSON Schema URL
   - Update YAML Schema URL
   - Deploy documentation

3. **Announce Release**
   - GitHub release notes
   - Documentation site
   - Community discussions

4. **Monitor Adoption**
   - Track validation errors
   - Collect feedback
   - Patch if needed

### Release Frequency

- **Major Versions:** Annually or as needed
- **Minor Versions:** Quarterly or as needed
- **Patch Versions:** As needed (documentation fixes)

---

## Version History

### Version 2.0.0 (2026-04-20) - Current

**Changes:**
- Added 15 new optional fields
- Restructured document type taxonomy
- Enhanced relationship specifications
- Added compliance field
- Added review_status object

**Breaking Changes:** None (fully backward compatible)

**Migration:** Optional (recommended for new features)

### Version 1.1.0 (2026-02-15)

**Changes:**
- Added `review_status` field
- Added `test_coverage` field
- Added `keywords` array
- Expanded enum values for `audience`

**Breaking Changes:** None

### Version 1.0.0 (2025-12-01)

**Changes:**
- Initial production release
- 30 core fields defined
- 15 document types supported
- JSON Schema v2020-12 validation

---

## Policy Review

**Review Cycle:** Annual  
**Next Review:** 2027-04-20  
**Owner:** Architecture Team  
**Approval:** Principal Architect

**Changes to This Policy:**
- Proposed changes discussed in GitHub
- 30-day review period
- Approval by Principal Architect required
- Version bumped per Semantic Versioning

---

## Contact

**Questions or Feedback:**
- GitHub Discussions: `github.com/project-ai/vault/discussions`
- Email: `architecture@project-ai.org`
- Documentation: `docs.project-ai.org/metadata-schema`

---

**Document Version:** 1.0.0  
**Schema Version Covered:** 2.0.0  
**Last Updated:** 2026-04-20  
**Status:** Active  
**License:** MIT

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

