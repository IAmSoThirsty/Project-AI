<#
.SYNOPSIS
    Bulk add YAML frontmatter metadata to archive documentation files.

.DESCRIPTION
    Production-ready script to process 134 archive files with standardized
    archive metadata including status, archived_date, archive_reason,
    superseded_by, historical_value, and restore_candidate fields.

.PARAMETER DryRun
    Preview changes without modifying files.

.PARAMETER ConfigPath
    Path to archive metadata configuration JSON.

.PARAMETER LogPath
    Path to log file.

.EXAMPLE
    .\process-archive-metadata.ps1 -DryRun
    Preview metadata generation for all archive files.

.EXAMPLE
    .\process-archive-metadata.ps1 -ConfigPath ".\archive-metadata-config.json"
    Process all archive files with production metadata.

.NOTES
    Author: AGENT-031 (P3 Archive Documentation Metadata Specialist)
    Version: 1.0.0
    Complies with: AGENT_IMPLEMENTATION_STANDARD.md
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [string]$ConfigPath = ".\scripts\automation\archive-metadata-config.json",

    [Parameter()]
    [string]$LogPath = ".\automation-logs\archive-metadata-$(Get-Date -Format 'yyyyMMdd-HHmmss').log",

    [Parameter()]
    [string]$ArchivePath = ".\docs\internal\archive",

    [Parameter()]
    [int]$SpotCheckPercent = 10
)

#region Configuration
$ErrorActionPreference = 'Stop'
$script:ProcessedFiles = 0
$script:SkippedFiles = 0
$script:ErrorFiles = 0
$script:ProcessingLog = @()

# Archive metadata schema
$script:ArchiveSchema = @{
    status = 'archived'
    type = 'historical_record'
    archived_date = $null  # Set per-file from LastWriteTime
    archive_reason = $null # Auto-detect from content/filename
    superseded_by = $null  # Wiki link to replacement if exists
    historical_value = $null # high/medium/low assessment
    restore_candidate = $false
    audience = @('developer', 'architect')
    tags = @('historical', 'archive')
}
#endregion

#region Logging Functions
function Write-Log {
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet('INFO', 'WARN', 'ERROR', 'SUCCESS')]
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    $color = switch ($Level) {
        'INFO'    { 'Cyan' }
        'WARN'    { 'Yellow' }
        'ERROR'   { 'Red' }
        'SUCCESS' { 'Green' }
    }
    Write-Host $logEntry -ForegroundColor $color
    
    # Add to log collection
    $script:ProcessingLog += $logEntry
    
    # Write to log file
    if ($LogPath) {
        $logDir = Split-Path -Path $LogPath -Parent
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
        Add-Content -Path $LogPath -Value $logEntry -Encoding UTF8
    }
}
#endregion

#region Metadata Generation Functions
function Get-ArchiveReason {
    param(
        [string]$FileName,
        [string]$Content
    )
    
    # Pattern matching for archive reasons
    $patterns = @{
        'completed' = @('COMPLETE', 'FINISHED', 'DONE', 'implementation done', 'successfully completed')
        'superseded' = @('superseded', 'replaced by', 'newer docs', 'migrated to documentation')
        'deprecated' = @('deprecated', 'obsolete', 'no longer used', 'discontinued')
        'migrated' = @('moved to', 'migrated to', 'now in', 'relocated to')
    }
    
    foreach ($reason in $patterns.Keys) {
        foreach ($pattern in $patterns[$reason]) {
            if ($Content -match [regex]::Escape($pattern) -or $FileName -match [regex]::Escape($pattern)) {
                return $reason
            }
        }
    }
    
    return 'completed'  # Default for archive files
}

function Get-HistoricalValue {
    param(
        [string]$FileName,
        [string]$Content
    )
    
    $highValuePatterns = @('architecture', 'security', 'incident', 'audit', 'charter', 'governance', 'constitutional')
    $mediumValuePatterns = @('implementation', 'summary', 'report', 'analysis', 'testing', 'adversarial')
    
    foreach ($pattern in $highValuePatterns) {
        if ($FileName -match $pattern -or $Content -match $pattern) {
            return 'high'
        }
    }
    
    foreach ($pattern in $mediumValuePatterns) {
        if ($FileName -match $pattern -or $Content -match $pattern) {
            return 'medium'
        }
    }
    
    return 'low'
}

function Get-SupersededBy {
    param(
        [string]$FileName,
        [string]$Content
    )
    
    # Known supersession mappings from ARCHIVE_INDEX.md
    $supersessionMap = @{
        'CI_CHECK_ISSUES.md' = '[[CI Pipeline Documentation]]'
        'COMPLETE_REPOSITORY_AUDIT.md' = '[[Repository Audit Report]]'
        'IMPLEMENTATION_SUMMARY.md' = '[[CHANGELOG]]'
        'MISSION_STATUS.txt' = '[[CHANGELOG]]'
        'SUPER_KERNEL_SUMMARY.md' = '[[Super Kernel Architecture]]'
        'CONTRARIAN_FIREWALL_COMPLETE.md' = '[[Contrarian Firewall Security]]'
        'IMPLEMENTATION_COMPLETE_PLANETARY_DEFENSE.md' = '[[Planetary Defense System]]'
        'IMPLEMENTATION_COMPLETE_WATCHTOWER.md' = '[[Watchtower Monitoring]]'
        'HEALTH_REPORT_SUMMARY.md' = '[[Health Monitoring System]]'
        'PHASE4_ACADEMIC_RIGOR_COMPLETE.md' = '[[Academic Documentation Standards]]'
        'PHASE5_EXTERNAL_DELIVERABLES_COMPLETE.md' = '[[External Deployment Guide]]'
        'REVIEWER_TRAP_IMPLEMENTATION.md' = '[[AI Takeover Reviewer Trap]]'
    }
    
    # Check known mappings
    if ($supersessionMap.ContainsKey($FileName)) {
        return $supersessionMap[$FileName]
    }
    
    # Pattern detection in content
    if ($Content -match 'superseded by\s+(.+?)[\n\r]') {
        return "[[$(($matches[1] -replace '[^\w\s-]', '').Trim())]]"
    }
    
    if ($Content -match 'replaced by\s+(.+?)[\n\r]') {
        return "[[$(($matches[1] -replace '[^\w\s-]', '').Trim())]]"
    }
    
    return $null
}

function Get-AdditionalTags {
    param(
        [string]$FileName,
        [string]$Content
    )
    
    $tags = @('historical', 'archive')
    
    # Tag detection patterns
    $tagPatterns = @{
        'security' = @('security', 'audit', 'vulnerability', 'cryptography', 'firewall', 'defense')
        'testing' = @('test', 'adversarial', 'validation', 'verification')
        'implementation' = @('implementation', 'complete', 'deployed')
        'monitoring' = @('monitoring', 'watchtower', 'health', 'observability')
        'ci-cd' = @('ci', 'cd', 'pipeline', 'workflow', 'automation')
        'governance' = @('governance', 'policy', 'constitutional', 'charter', 'ethics')
        'architecture' = @('architecture', 'design', 'kernel', 'structure')
    }
    
    foreach ($tag in $tagPatterns.Keys) {
        foreach ($pattern in $tagPatterns[$tag]) {
            if ($FileName -match $pattern -or $Content -match $pattern) {
                if ($tags -notcontains $tag) {
                    $tags += $tag
                }
                break
            }
        }
    }
    
    return $tags
}

function Generate-FrontmatterYAML {
    param(
        [Parameter(Mandatory)]
        [System.IO.FileInfo]$File,
        
        [Parameter(Mandatory)]
        [string]$Content
    )
    
    # Extract title from first heading or filename
    $title = $File.BaseName -replace '_', ' ' -replace '-', ' '
    if ($Content -match '^#\s+(.+)$') {
        $title = $matches[1].Trim()
    }
    
    # Generate metadata fields
    $archivedDate = $File.LastWriteTime.ToString('yyyy-MM-dd')
    $archiveReason = Get-ArchiveReason -FileName $File.Name -Content $Content
    $historicalValue = Get-HistoricalValue -FileName $File.Name -Content $Content
    $supersededBy = Get-SupersededBy -FileName $File.Name -Content $Content
    $tags = Get-AdditionalTags -FileName $File.Name -Content $Content
    
    # Build frontmatter
    $frontmatter = @"
---
title: "$title"
id: "$($File.BaseName.ToLower() -replace '_', '-')"
type: historical_record
status: archived
archived_date: $archivedDate
archive_reason: $archiveReason
historical_value: $historicalValue
restore_candidate: false
audience:
  - developer
  - architect
tags:
$(($tags | ForEach-Object { "  - $_" }) -join "`n")
"@

    if ($supersededBy) {
        $frontmatter += "`nsuperseded_by: $supersededBy"
    }
    
    $frontmatter += "`npath_confirmed: $($File.FullName -replace '\\', '/')"
    $frontmatter += "`n---`n"
    
    return $frontmatter
}
#endregion

#region File Processing Functions
function Process-ArchiveFile {
    param(
        [Parameter(Mandatory)]
        [System.IO.FileInfo]$File
    )
    
    try {
        Write-Log "Processing: $($File.Name)" -Level INFO
        
        # Read file content
        $content = Get-Content -Path $File.FullName -Raw -Encoding UTF8
        
        # Check if frontmatter already exists
        if ($content -match '^---\s*\n') {
            Write-Log "  Skipping (already has frontmatter): $($File.Name)" -Level WARN
            $script:SkippedFiles++
            return
        }
        
        # Generate frontmatter
        $frontmatter = Generate-FrontmatterYAML -File $File -Content $content
        
        # Combine frontmatter + existing content
        $newContent = $frontmatter + "`n" + $content
        
        if ($DryRun) {
            Write-Log "  [DRY RUN] Would add frontmatter to: $($File.Name)" -Level INFO
            Write-Host "`n--- Preview for $($File.Name) ---" -ForegroundColor Magenta
            Write-Host ($frontmatter -split "`n" | Select-Object -First 15 | Out-String) -ForegroundColor Gray
            Write-Host "---`n" -ForegroundColor Magenta
        }
        else {
            # Write updated content back to file
            Set-Content -Path $File.FullName -Value $newContent -Encoding UTF8 -NoNewline
            Write-Log "  SUCCESS: Added frontmatter to $($File.Name)" -Level SUCCESS
        }
        
        $script:ProcessedFiles++
    }
    catch {
        Write-Log "  ERROR processing $($File.Name): $($_.Exception.Message)" -Level ERROR
        $script:ErrorFiles++
    }
}
#endregion

#region Main Execution
function Start-ArchiveMetadataProcessing {
    Write-Log "=== Archive Metadata Processing Started ===" -Level INFO
    Write-Log "Archive Path: $ArchivePath" -Level INFO
    Write-Log "Dry Run: $DryRun" -Level INFO
    Write-Log "Log Path: $LogPath" -Level INFO
    
    # Validate paths
    if (-not (Test-Path $ArchivePath)) {
        Write-Log "Archive path not found: $ArchivePath" -Level ERROR
        return
    }
    
    # Get all markdown files
    $files = Get-ChildItem -Path $ArchivePath -Filter "*.md" -Recurse -File
    Write-Log "Found $($files.Count) markdown files to process" -Level INFO
    
    # Process each file
    foreach ($file in $files) {
        Process-ArchiveFile -File $file
    }
    
    # Summary
    Write-Log "`n=== Processing Summary ===" -Level SUCCESS
    Write-Log "Total Files: $($files.Count)" -Level INFO
    Write-Log "Processed: $script:ProcessedFiles" -Level SUCCESS
    Write-Log "Skipped: $script:SkippedFiles" -Level WARN
    Write-Log "Errors: $script:ErrorFiles" -Level ERROR
    
    if (-not $DryRun) {
        Write-Log "`nSpot-check validation recommended: $([Math]::Ceiling($files.Count * $SpotCheckPercent / 100)) files" -Level INFO
    }
    
    Write-Log "Log saved to: $LogPath" -Level INFO
}

# Execute
Start-ArchiveMetadataProcessing
#endregion
