---
title: Metadata Management System
type: technical-reference
audience: [developers, technical-writers, documentation-team]
classification: P0-Core
tags: [metadata, frontmatter, yaml, automation, documentation]
created: 2024-01-20
last_verified: 2024-01-20
status: current
related_systems: [automation, documentation, taxonomy]
---

# Metadata Management System

**Automated YAML frontmatter generation and validation for documentation.**

## Executive Summary

The metadata management system provides:
- **Automatic generation** - Extract metadata from content
- **Taxonomy enforcement** - Validate tags against defined taxonomies
- **Relationship mapping** - Build document relationship graphs
- **Schema validation** - Ensure consistent metadata structure
- **Bulk operations** - Process thousands of files efficiently

**Primary Tool:** `add-metadata.ps1`  
**Location:** `scripts/automation/`

---

## Metadata Schema

### Standard Frontmatter Structure

```yaml
---
title: Authentication Security Guide
type: technical-guide
audience: [developers, security-team]
classification: P0-Core
tags: [authentication, security, jwt, oauth]
created: 2024-01-15
last_verified: 2024-01-20
modified: 2024-01-20
status: current
related_systems: [user-management, api-gateway, authorization]
stakeholders: [security-team, backend-team]
review_cycle: quarterly
requires_admin: false
related:
  - type: reference
    path: ./authorization.md
    description: Authorization system documentation
  - type: dependency
    path: ./user-manager.md
    description: User management implementation
  - type: extension
    path: ./oauth-integration.md
    description: OAuth 2.0 integration guide
---

# Authentication Security Guide

Content starts here...
```

### Field Definitions

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `title` | String | ✅ | Document title | "Authentication Security Guide" |
| `type` | String | ✅ | Document type | "technical-guide" |
| `audience` | Array | ✅ | Target audiences | ["developers", "security-team"] |
| `classification` | String | ✅ | Priority/classification | "P0-Core" |
| `tags` | Array | ✅ | Content tags | ["authentication", "security"] |
| `created` | Date | ✅ | Creation date (ISO 8601) | "2024-01-15" |
| `last_verified` | Date | ✅ | Last verification date | "2024-01-20" |
| `modified` | Date | ❌ | Last modification date | "2024-01-20" |
| `status` | String | ✅ | Document status | "current" |
| `related_systems` | Array | ❌ | Related system components | ["user-management"] |
| `stakeholders` | Array | ❌ | Responsible teams/individuals | ["security-team"] |
| `review_cycle` | String | ❌ | Review frequency | "quarterly" |
| `requires_admin` | Boolean | ❌ | Admin privileges required | false |
| `related` | Array | ❌ | Related documents | See structure below |

---

## Document Types

### Type Taxonomy

```yaml
types:
  # Technical Documentation
  - technical-guide         # How-to guides for developers
  - technical-reference     # API/system reference documentation
  - architecture-doc        # System architecture documentation
  
  # User Documentation
  - user-guide              # End-user documentation
  - quickstart              # Getting started guides
  - tutorial                # Step-by-step tutorials
  
  # Governance & Process
  - governance-policy       # Governance policies
  - process-doc             # Process documentation
  - standard                # Standards and conventions
  
  # Project Management
  - project-plan            # Project planning documents
  - status-report           # Status and progress reports
  - meeting-notes           # Meeting minutes
  
  # Quality Assurance
  - test-plan               # Testing documentation
  - validation-report       # Validation and verification reports
  - audit-report            # Audit findings and reports
```

### Type Selection Guidelines

**Technical Guide** (`technical-guide`):
- How-to implement features
- Integration guides
- Best practices documentation

**Technical Reference** (`technical-reference`):
- API documentation
- Configuration reference
- Command-line tool reference

**Architecture Doc** (`architecture-doc`):
- System design documents
- Component interaction diagrams
- Technology stack decisions

---

## Classification System

### P0-P4 Priority System

| Classification | Meaning | Review Cycle | Example |
|----------------|---------|--------------|---------|
| `P0-Core` | Core functionality, critical path | Monthly | Authentication, data persistence |
| `P1-Developer` | Developer tools, essential features | Quarterly | Build system, testing framework |
| `P2-Root-Reports` | Root-level reports and documentation | Quarterly | Architecture overview, status reports |
| `P3-Archive` | Historical/archived documentation | Annual | Old design docs, deprecated features |
| `P4-Temporal` | Temporary or WIP documentation | On-demand | Draft proposals, temporary notes |

### Classification Selection

```powershell
# Determine classification based on content
if ($content -match "authentication|authorization|security|data-persistence") {
    $classification = "P0-Core"
} elseif ($content -match "build|test|development|tooling") {
    $classification = "P1-Developer"
} elseif ($content -match "architecture|overview|status|report") {
    $classification = "P2-Root-Reports"
} elseif ($content -match "archived|deprecated|obsolete") {
    $classification = "P3-Archive"
} else {
    $classification = "P4-Temporal"
}
```

---

## Audience Targeting

### Audience Taxonomy

```yaml
audiences:
  # Technical Roles
  - developers              # Software developers
  - devops                  # DevOps engineers
  - security-team           # Security engineers
  - qa-team                 # QA engineers
  - system-administrators   # Sysadmins
  
  # Business Roles
  - product-managers        # Product management
  - project-managers        # Project management
  - stakeholders            # Business stakeholders
  
  # Specialized Roles
  - auditors                # Compliance auditors
  - architects              # System architects
  - technical-writers       # Documentation team
  
  # End Users
  - end-users               # Application end users
  - administrators          # Application administrators
```

### Multi-Audience Documents

```yaml
# Document for multiple audiences
audience: [developers, security-team, auditors]

# Audience-specific sections marked in content
## For Developers
Implementation details...

## For Security Team
Security considerations...

## For Auditors
Compliance evidence...
```

---

## Tag System

### Tag Taxonomy

```yaml
categories:
  # Security
  security:
    - authentication
    - authorization
    - encryption
    - audit-trail
    - compliance
  
  # Architecture
  architecture:
    - design-patterns
    - microservices
    - api-design
    - data-flow
    - component-interaction
  
  # Development
  development:
    - build-system
    - testing
    - debugging
    - deployment
    - ci-cd
  
  # Documentation
  documentation:
    - api-docs
    - user-guide
    - architecture-docs
    - process-docs
  
  # Automation
  automation:
    - scripts
    - workflows
    - batch-processing
    - ci-cd
```

### Tag Validation

```powershell
# Validate tags against taxonomy
function Test-TagValidity {
    param(
        [string[]]$Tags,
        [hashtable]$Taxonomy
    )
    
    $invalidTags = @()
    $suggestions = @{}
    
    foreach ($tag in $Tags) {
        $isValid = $false
        
        # Check if tag exists in taxonomy
        foreach ($category in $Taxonomy.Keys) {
            if ($Taxonomy[$category] -contains $tag) {
                $isValid = $true
                break
            }
        }
        
        if (-not $isValid) {
            $invalidTags += $tag
            
            # Find similar tags (Levenshtein distance)
            $allValidTags = $Taxonomy.Values | ForEach-Object { $_ }
            $similarTag = Find-SimilarTag -Tag $tag -ValidTags $allValidTags
            $suggestions[$tag] = $similarTag
        }
    }
    
    return @{
        IsValid = ($invalidTags.Count -eq 0)
        InvalidTags = $invalidTags
        Suggestions = $suggestions
    }
}
```

---

## Relationship Mapping

### Relationship Types

```yaml
related:
  # Reference relationships
  - type: reference
    path: ./related-doc.md
    description: Referenced documentation
  
  # Dependency relationships
  - type: dependency
    path: ./prerequisite.md
    description: Required prerequisite knowledge
  
  # Extension relationships
  - type: extension
    path: ./advanced-topics.md
    description: Advanced topics building on this
  
  # Alternative relationships
  - type: alternative
    path: ./other-approach.md
    description: Alternative implementation approach
  
  # Supersedes relationships
  - type: supersedes
    path: ./old-version.md
    description: Replaces older documentation
```

### Relationship Graph Generation

```powershell
# Build relationship graph
function Build-RelationshipGraph {
    param([string]$Path)
    
    $graph = @{}
    $files = Get-ChildItem -Path $Path -Recurse -Filter "*.md"
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        $frontmatter = Extract-Frontmatter -Content $content
        
        if ($frontmatter.related) {
            $graph[$file.FullName] = @{
                Title = $frontmatter.title
                Related = $frontmatter.related
                IncomingLinks = @()
            }
        }
    }
    
    # Build incoming link references
    foreach ($file in $graph.Keys) {
        foreach ($rel in $graph[$file].Related) {
            $targetPath = Join-Path (Split-Path $file) $rel.path
            if ($graph.ContainsKey($targetPath)) {
                $graph[$targetPath].IncomingLinks += @{
                    From = $file
                    Type = $rel.type
                }
            }
        }
    }
    
    return $graph
}
```

---

## Metadata Generation

### Automatic Extraction

```powershell
# Extract metadata from content
function Extract-Metadata {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    $metadata = @{}
    
    # Extract title (first H1 heading)
    if ($content -match '(?m)^#\s+(.+)$') {
        $metadata['title'] = $matches[1].Trim()
    }
    
    # Determine type based on content and filename
    $metadata['type'] = Determine-DocumentType -Content $content -FileName (Split-Path $FilePath -Leaf)
    
    # Extract tags from content (# tag references)
    $tags = [regex]::Matches($content, '(?m)#(\w+)') | ForEach-Object { $_.Groups[1].Value }
    $metadata['tags'] = $tags | Select-Object -Unique
    
    # Determine audience from content analysis
    $metadata['audience'] = Determine-Audience -Content $content
    
    # Determine classification
    $metadata['classification'] = Determine-Classification -Content $content
    
    # Timestamps
    $fileInfo = Get-Item $FilePath
    $metadata['created'] = $fileInfo.CreationTime.ToString('yyyy-MM-dd')
    $metadata['modified'] = $fileInfo.LastWriteTime.ToString('yyyy-MM-dd')
    $metadata['last_verified'] = (Get-Date).ToString('yyyy-MM-dd')
    
    # Status determination
    $metadata['status'] = if ($fileInfo.LastWriteTime -gt (Get-Date).AddDays(-30)) { "current" } else { "needs-review" }
    
    return $metadata
}
```

### Manual Override

```powershell
# Override automatic metadata with manual values
.\scripts\automation\add-metadata.ps1 `
    -Path ".\docs\security\auth.md" `
    -OverrideTitle "Authentication System V2" `
    -OverrideType "technical-reference" `
    -OverrideAudience @('developers', 'security-team') `
    -OverrideTags @('authentication', 'oauth', 'jwt') `
    -Force
```

---

## Validation and Quality Control

### Schema Validation

```powershell
# Validate frontmatter schema
function Test-FrontmatterSchema {
    param([hashtable]$Frontmatter)
    
    $required = @('title', 'type', 'audience', 'classification', 'tags', 'created', 'last_verified', 'status')
    $missing = @()
    
    foreach ($field in $required) {
        if (-not $Frontmatter.ContainsKey($field)) {
            $missing += $field
        }
    }
    
    # Validate field types
    $typeErrors = @()
    
    if ($Frontmatter['audience'] -isnot [Array]) {
        $typeErrors += "audience must be an array"
    }
    
    if ($Frontmatter['tags'] -isnot [Array]) {
        $typeErrors += "tags must be an array"
    }
    
    if ($Frontmatter['created'] -notmatch '^\d{4}-\d{2}-\d{2}$') {
        $typeErrors += "created must be ISO 8601 date (YYYY-MM-DD)"
    }
    
    return @{
        IsValid = ($missing.Count -eq 0 -and $typeErrors.Count -eq 0)
        MissingFields = $missing
        TypeErrors = $typeErrors
    }
}
```

### Quality Metrics

```powershell
# Generate metadata quality report
function Get-MetadataQualityReport {
    param([string]$Path)
    
    $files = Get-ChildItem -Path $Path -Recurse -Filter "*.md"
    $report = @{
        TotalFiles = $files.Count
        WithFrontmatter = 0
        ValidSchema = 0
        CompleteMetadata = 0
        AverageTagCount = 0
        AverageRelationshipCount = 0
    }
    
    $totalTags = 0
    $totalRelationships = 0
    
    foreach ($file in $files) {
        $content = Get-Content $file.FullName -Raw
        
        if ($content -match '(?ms)^---\s*\n(.+?)\n---') {
            $report.WithFrontmatter++
            
            $frontmatter = ConvertFrom-Yaml $matches[1]
            $validation = Test-FrontmatterSchema -Frontmatter $frontmatter
            
            if ($validation.IsValid) {
                $report.ValidSchema++
            }
            
            # Check completeness (all optional fields present)
            $optional = @('modified', 'related_systems', 'stakeholders', 'review_cycle', 'related')
            $present = ($optional | Where-Object { $frontmatter.ContainsKey($_) }).Count
            
            if ($present -eq $optional.Count) {
                $report.CompleteMetadata++
            }
            
            $totalTags += ($frontmatter.tags ?? @()).Count
            $totalRelationships += ($frontmatter.related ?? @()).Count
        }
    }
    
    $report.AverageTagCount = [Math]::Round($totalTags / $report.WithFrontmatter, 2)
    $report.AverageRelationshipCount = [Math]::Round($totalRelationships / $report.WithFrontmatter, 2)
    
    return $report
}
```

---

## Best Practices

### ✅ DO

- **Use consistent formatting** - YAML with proper indentation
- **Keep tags specific** - Use taxonomy-defined tags
- **Update last_verified** - On content review
- **Add relationships** - Link related documents
- **Review quarterly** - Keep metadata current

### ❌ DON'T

- **Don't use free-form tags** - Follow taxonomy
- **Don't skip required fields** - Validate schema
- **Don't duplicate content in metadata** - Keep DRY
- **Don't forget to update modified date** - Automate if possible
- **Don't ignore validation warnings** - Fix issues promptly

---

## Related Documentation

- **[02-AUTOMATION-SCRIPTS.md](./02-AUTOMATION-SCRIPTS.md)** - Automation scripts
- **[06-BATCH-PROCESSING.md](./06-BATCH-PROCESSING.md)** - Batch processing
- **[scripts/automation/AUTOMATION_GUIDE.md](../../scripts/automation/AUTOMATION_GUIDE.md)** - Complete guide

---

**AGENT-038: CLI & Automation Documentation Specialist**  
*Automated metadata management system.*
