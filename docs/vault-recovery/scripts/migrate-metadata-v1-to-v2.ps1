# Project-AI Metadata Migration Script v1 to v2
# Version: 1.0.0
# Migrates metadata from schema v1.x to v2.0

param(
    [Parameter(Mandatory=$false)]
    [string]$SourceDir = "T:\Project-AI-vault",

    [Parameter(Mandatory=$false)]
    [switch]$DryRun,

    [Parameter(Mandatory=$false)]
    [switch]$Backup,

    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# Configuration
$BackupDir = Join-Path $SourceDir "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$MigrationCount = 0
$ErrorCount = 0

# Colors
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Warning-Custom { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Project-AI Metadata Migration (v1 → v2)                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Create backup if requested
if ($Backup -and -not $DryRun) {
    Write-Info "Creating backup at: $BackupDir"
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Copy-Item -Path "$SourceDir\*.md" -Destination $BackupDir -Recurse
    Write-Success "✓ Backup created"
}

# Get all Markdown files
$files = Get-ChildItem -Path $SourceDir -Filter "*.md" -Recurse
Write-Info "Found $($files.Count) Markdown files`n"

# Migration mappings
$fieldMigrations = @{
    # v1 field → v2 field mappings
    'document_type' = 'type'
    'last_modified' = 'updated_date'
    'create_date' = 'created_date'
}

$newOptionalFields = @(
    'review_status',
    'test_coverage',
    'compliance',
    'dependencies',
    'metrics'
)

# Migrate single file
function Migrate-MetadataFile {
    param([string]$FilePath)

    Write-Info "Migrating: $FilePath"

    try {
        $content = Get-Content $FilePath -Raw

        # Extract frontmatter
        if ($content -notmatch '(?s)^---\s*\n(.*?)\n---(.*)$') {
            Write-Warning-Custom "  ⚠ No frontmatter found, skipping"
            return $false
        }

        $frontmatter = $matches[1]
        $body = $matches[2]
        $modified = $false

        # Apply field migrations
        foreach ($oldField in $fieldMigrations.Keys) {
            $newField = $fieldMigrations[$oldField]
            if ($frontmatter -match "${oldField}:") {
                $frontmatter = $frontmatter -replace "${oldField}:", "${newField}:"
                Write-Verbose "  Renamed $oldField → $newField"
                $modified = $true
            }
        }

        # Add version if missing
        if ($frontmatter -notmatch 'version:') {
            $frontmatter += "`nversion: ""1.0.0"""
            Write-Verbose "  Added version field"
            $modified = $true
        }

        # Add status if missing
        if ($frontmatter -notmatch 'status:') {
            $frontmatter += "`nstatus: active"
            Write-Verbose "  Added status field"
            $modified = $true
        }

        # Add recommended v2 fields (commented out)
        if ($modified) {
            $recommendations = @"

# Recommended v2 fields (uncomment and fill):
# review_status:
#   reviewed: false
#   reviewers: []
# dependencies: []
# keywords: []
# audience: []
"@
            $frontmatter += $recommendations
        }

        if ($modified) {
            if (-not $DryRun) {
                $newContent = "---`n$frontmatter`n---$body"
                Set-Content -Path $FilePath -Value $newContent -NoNewline
                Write-Success "  ✓ Migrated"
            }
            else {
                Write-Info "  [DRY RUN] Would migrate"
            }
            return $true
        }
        else {
            Write-Info "  → Already v2 compatible"
            return $false
        }
    }
    catch {
        Write-Error-Custom "  ❌ Migration failed: $_"
        return $false
    }
}

# Process each file
foreach ($file in $files) {
    $wasMigrated = Migrate-MetadataFile -FilePath $file.FullName
    if ($wasMigrated) {
        $MigrationCount++
    }
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Migration Summary                                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`nTotal Files:    $($files.Count)" -ForegroundColor White
Write-Success "Migrated:       $MigrationCount"
Write-Info "Unchanged:      $($files.Count - $MigrationCount)"
if ($ErrorCount -gt 0) {
    Write-Error-Custom "Errors:         $ErrorCount"
}

if ($DryRun) {
    Write-Host "`n🔍 Dry run completed - no files were modified" -ForegroundColor Yellow
    Write-Host "   Run without -DryRun to apply changes`n" -ForegroundColor Yellow
}
elseif ($Backup) {
    Write-Host "`n💾 Backup saved to: $BackupDir`n" -ForegroundColor Cyan
}

if ($MigrationCount -gt 0 -and -not $DryRun) {
    Write-Success "`n✅ Migration completed successfully!`n"
    Write-Info "Next steps:"
    Write-Info "  1. Run validation: .\validate-metadata.ps1 -Recursive"
    Write-Info "  2. Review migrated files"
    Write-Info "  3. Fill in recommended v2 fields`n"
}

# Exit code
exit ($ErrorCount -gt 0 ? 1 : 0)
