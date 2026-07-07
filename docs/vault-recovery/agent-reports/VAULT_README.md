# Project-AI Documentation Vault - README

**Version:** 2.0.0  
**Status:** Production Ready  
**Last Updated:** 2026-04-20

---

## Overview

The Project-AI Documentation Vault is a comprehensive, schema-driven documentation repository with production-grade metadata infrastructure. All documents use YAML frontmatter validated against a comprehensive JSON Schema.

---

## Quick Start

### 1. Create a New Document

```yaml
---
title: "Your Document Title"
id: "your-document-id"  # kebab-case, unique
type: guide  # See document types below
version: "1.0.0"  # Semantic versioning
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: active  # draft, review, active, deprecated, archived
author:
  name: "Your Name"
  email: "you@project-ai.org"

# Add type-specific fields as needed
category: security
tags:
  - authentication
  - tutorial
difficulty: beginner  # For guides/tutorials
estimated_time: "PT45M"  # ISO 8601 duration
---

# Your Document Content

Write your documentation here...
```

### 2. Validate Your Document

```powershell
# Validate single file
.\scripts\validate-metadata.ps1 -File "path\to\your-doc.md"

# Validate all documents
.\scripts\validate-metadata.ps1 -Recursive

# Check relationships
.\scripts\validate-metadata.ps1 -Recursive -CheckRelationships
```

### 3. View Examples

Browse `metadata-examples/` directory for 22 complete examples covering all document types.

---

## Documentation

- **Complete Schema Reference**: `METADATA_SCHEMA.md` (7800+ words)
- **Versioning Policy**: `SCHEMA_VERSIONING_POLICY.md`
- **22 Examples**: `metadata-examples/` directory
- **Validation Script**: `scripts/validate-metadata.ps1`
- **Migration Script**: `scripts/migrate-metadata-v1-to-v2.ps1`

---

## Schema Coverage

- **Fields**: 50+ documented fields
- **Document Types**: 22 types
- **Examples**: 22 production-ready examples
- **Validation**: Automated JSON Schema validation
- **IDE Support**: VS Code and Obsidian integration

---

**See `METADATA_SCHEMA.md` for complete documentation.**

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

