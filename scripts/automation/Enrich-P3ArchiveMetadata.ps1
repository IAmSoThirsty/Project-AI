<#
.SYNOPSIS
    AGENT-015: P3 Archive Bulk Metadata Enrichment Script (PowerShell)

.DESCRIPTION
    Enhances existing archive file metadata with P3-specific fields:
    - Adds p3-archive tag
    - Adds last_verified: 2026-04-20
    - Adds created date from git history
    - Adds superseded_by (if applicable)
    - Adds related_systems, stakeholders, review_cycle
    - Maps type: historical_record -> type: archived
#>

param(
    [string]$ArchiveDir = "docs\internal\archive",
    [switch]$DryRun = $false
)

# Constants
$LAST_VERIFIED = "2026-04-20"
$P3_TAG = "p3-archive"

# Superseded mapping
$SupersededMapping = @{
    "PROGRAM_SUMMARY.md" = "docs/DEVELOPER_QUICK_REFERENCE.md"
    "REPO_STRUCTURE.md" = "docs/ARCHITECTURE_DESIGN_PATTERNS_EVALUATION.md"
    "SECURITY_SUMMARY.md" = "SECURITY.md"
    "GITHUB_UPDATE_GUIDE.md" = "CONTRIBUTING.md"
}

function Get-GitCreationDate {
    param([string]$FilePath)
    
    try {
        $gitLog = git log --format=%ai --reverse -- $FilePath 2>$null
        if ($gitLog) {
            $firstCommit = ($gitLog -split "`n")[0]
            return ($firstCommit -split " ")[0]
        }
    } catch {
        # Silently fail
    }
    return $null
}

function Parse-Frontmatter {
    param([string]$Content)
    
    # Handle mixed line endings - normalize to array
    if ($Content -match '(?s)^---\s*[\r\n]+(.*?)[\r\n]+---\s*[\r\n]+(.*)$') {
        $yamlContent = $Matches[1]
        $bodyContent = $Matches[2]
        
        # Parse YAML manually (simple key-value pairs)
        $metadata = @{}
        $lines = $yamlContent -split "`n"
        $currentKey = $null
        $currentList = @()
        
        foreach ($line in $lines) {
            $line = $line.Trim()
            
            # Handle list items
            if ($line -match '^\s*-\s+(.+)$') {
                $currentList += $Matches[1]
            }
            # Handle key-value pairs
            elseif ($line -match '^(\w+):\s*(.*)$') {
                # Save previous list if exists
                if ($currentKey -and $currentList.Count -gt 0) {
                    $metadata[$currentKey] = $currentList
                    $currentList = @()
                }
                
                $currentKey = $Matches[1]
                $value = $Matches[2]
                
                if ($value) {
                    $metadata[$currentKey] = $value
                }
            }
        }
        
        # Save last list if exists
        if ($currentKey -and $currentList.Count -gt 0) {
            $metadata[$currentKey] = $currentList
        }
        
        return @{
            Metadata = $metadata
            Body = $bodyContent
        }
    }
    
    return $null
}

function Determine-ArchiveType {
    param(
        [hashtable]$Metadata,
        [string]$FileName
    )
    
    $archiveReason = $Metadata['archive_reason']
    
    if ($archiveReason -eq 'superseded' -or $SupersededMapping.ContainsKey($FileName)) {
        return 'superseded'
    }
    elseif ($archiveReason -eq 'deprecated') {
        return 'legacy'
    }
    elseif ($archiveReason -eq 'completed') {
        return 'archived'
    }
    else {
        return 'historical'
    }
}

function Enrich-Metadata {
    param(
        [hashtable]$Metadata,
        [string]$FilePath,
        [string]$FileName
    )
    
    $changes = @()
    
    # 1. Update type to P3 taxonomy
    $newType = Determine-ArchiveType -Metadata $Metadata -FileName $FileName
    if ($Metadata['type'] -ne $newType) {
        $Metadata['type'] = $newType
        $changes += "Updated: type"
    }
    
    # 2. Add/update tags with p3-archive
    if ($Metadata.ContainsKey('tags')) {
        $tags = $Metadata['tags']
        if ($tags -is [string]) {
            $tags = @($tags)
        }
        if ($tags -notcontains $P3_TAG) {
            $tags = @($P3_TAG) + $tags
            $Metadata['tags'] = $tags
            $changes += "Added: p3-archive tag"
        }
    }
    
    # 3. Add created date from git
    if (-not $Metadata.ContainsKey('created')) {
        $createdDate = Get-GitCreationDate -FilePath $FilePath
        if ($createdDate) {
            $Metadata['created'] = $createdDate
            $changes += "Added: created"
        }
    }
    
    # 4. Add last_verified
    if ($Metadata['last_verified'] -ne $LAST_VERIFIED) {
        $Metadata['last_verified'] = $LAST_VERIFIED
        $changes += "Updated: last_verified"
    }
    
    # 5. Add superseded_by if applicable
    if ($SupersededMapping.ContainsKey($FileName) -and -not $Metadata.ContainsKey('superseded_by')) {
        $Metadata['superseded_by'] = $SupersededMapping[$FileName]
        $changes += "Added: superseded_by"
        if ($Metadata['type'] -ne 'superseded') {
            $Metadata['type'] = 'superseded'
        }
    }
    
    # 6. Add related_systems
    if (-not $Metadata.ContainsKey('related_systems')) {
        $systems = @()
        $tags = $Metadata['tags']
        
        if ($tags -contains 'security') { $systems += 'security-systems' }
        if ($tags -contains 'testing') { $systems += 'test-framework' }
        if ($tags -contains 'ci-cd') { $systems += 'ci-cd-pipeline' }
        if ($tags -contains 'architecture') { $systems += 'architecture' }
        
        if ($systems.Count -eq 0) {
            $systems = @('historical-reference')
        }
        
        $Metadata['related_systems'] = $systems
        $changes += "Added: related_systems"
    }
    
    # 7. Add stakeholders
    if (-not $Metadata.ContainsKey('stakeholders')) {
        if ($Metadata.ContainsKey('audience')) {
            $Metadata['stakeholders'] = $Metadata['audience']
        } else {
            $Metadata['stakeholders'] = @('historical-reference')
        }
        $changes += "Added: stakeholders"
    }
    
    # 8. Add review_cycle
    if (-not $Metadata.ContainsKey('review_cycle')) {
        $Metadata['review_cycle'] = 'annually'
        $changes += "Added: review_cycle"
    }
    
    # 9. Ensure archive_reason exists
    if (-not $Metadata.ContainsKey('archive_reason')) {
        $Metadata['archive_reason'] = 'completed'
        $changes += "Added: archive_reason"
    }
    
    return @{
        Metadata = $Metadata
        Changes = $changes
    }
}

function Format-Frontmatter {
    param([hashtable]$Metadata)
    
    $fieldOrder = @(
        'title', 'id', 'type', 'tags', 'created', 'last_verified',
        'status', 'archived_date', 'archive_reason', 'superseded_by',
        'related_systems', 'stakeholders', 'audience', 'review_cycle',
        'historical_value', 'restore_candidate', 'path_confirmed'
    )
    
    $yaml = "---`n"
    
    # Add fields in order
    foreach ($field in $fieldOrder) {
        if ($Metadata.ContainsKey($field)) {
            $value = $Metadata[$field]
            
            if ($value -is [array]) {
                $yaml += "$field`:`n"
                foreach ($item in $value) {
                    $yaml += "  - $item`n"
                }
            } else {
                $yaml += "$field`: $value`n"
            }
        }
    }
    
    # Add remaining fields
    foreach ($key in $Metadata.Keys) {
        if ($key -notin $fieldOrder) {
            $value = $Metadata[$key]
            if ($value -is [array]) {
                $yaml += "$key`:`n"
                foreach ($item in $value) {
                    $yaml += "  - $item`n"
                }
            } else {
                $yaml += "$key`: $value`n"
            }
        }
    }
    
    $yaml += "---`n"
    return $yaml
}

function Process-File {
    param(
        [System.IO.FileInfo]$File,
        [switch]$DryRun
    )
    
    $result = @{
        File = $File.Name
        Status = 'unknown'
        Changes = @()
        Errors = @()
    }
    
    try {
        # Read file
        $content = Get-Content -Path $File.FullName -Raw -Encoding UTF8
        
        # Parse frontmatter
        $parsed = Parse-Frontmatter -Content $content
        
        if (-not $parsed) {
            $result['Status'] = 'no_frontmatter'
            $result['Errors'] += "No valid frontmatter found"
            return $result
        }
        
        # Enrich metadata
        $enriched = Enrich-Metadata -Metadata $parsed.Metadata -FilePath $File.FullName -FileName $File.Name
        
        $result['Changes'] = $enriched.Changes
        
        # Write back if not dry run
        if (-not $DryRun -and $enriched.Changes.Count -gt 0) {
            $newFrontmatter = Format-Frontmatter -Metadata $enriched.Metadata
            $newContent = $newFrontmatter + $parsed.Body
            Set-Content -Path $File.FullName -Value $newContent -Encoding UTF8 -NoNewline
            $result['Status'] = 'enriched'
        }
        elseif ($enriched.Changes.Count -gt 0) {
            $result['Status'] = 'would_enrich'
        }
        else {
            $result['Status'] = 'no_changes'
        }
    }
    catch {
        $result['Status'] = 'error'
        $result['Errors'] += $_.Exception.Message
    }
    
    return $result
}

# Main execution
Write-Host "=" * 80
Write-Host "AGENT-015: P3 Archive Bulk Metadata Enrichment"
Write-Host "=" * 80
Write-Host ""

# Find all markdown files
$mdFiles = Get-ChildItem -Path $ArchiveDir -Filter "*.md" | Sort-Object Name
$totalFiles = $mdFiles.Count

Write-Host "📁 Found $totalFiles markdown files in $ArchiveDir"
Write-Host ""

# Process files
$results = @()
$i = 0

foreach ($file in $mdFiles) {
    $i++
    Write-Host "[$i/$totalFiles] Processing: $($file.Name)..." -NoNewline
    
    $result = Process-File -File $file -DryRun:$DryRun
    $results += $result
    
    switch ($result['Status']) {
        'enriched' {
            Write-Host " ✅ ($($result['Changes'].Count) changes)" -ForegroundColor Green
        }
        'no_changes' {
            Write-Host " ⏭️  (already compliant)" -ForegroundColor Gray
        }
        'error' {
            Write-Host " ❌ $($result['Errors'][0])" -ForegroundColor Red
        }
        default {
            Write-Host " ⚠️  $($result['Status'])" -ForegroundColor Yellow
        }
    }
}

# Summary
Write-Host ""
Write-Host "=" * 80
Write-Host "ENRICHMENT SUMMARY"
Write-Host "=" * 80

$enriched = $results | Where-Object { $_['Status'] -eq 'enriched' }
$noChanges = $results | Where-Object { $_['Status'] -eq 'no_changes' }
$errors = $results | Where-Object { $_['Status'] -eq 'error' }

Write-Host "✅ Enriched: $($enriched.Count)" -ForegroundColor Green
Write-Host "⏭️  No changes needed: $($noChanges.Count)" -ForegroundColor Gray
Write-Host "❌ Errors: $($errors.Count)" -ForegroundColor Red
Write-Host "📊 Total processed: $totalFiles"
Write-Host ""

if ($enriched.Count -gt 0) {
    Write-Host "Most common changes:"
    $allChanges = @{}
    foreach ($r in $enriched) {
        foreach ($change in $r['Changes']) {
            if (-not $allChanges.ContainsKey($change)) {
                $allChanges[$change] = 0
            }
            $allChanges[$change]++
        }
    }
    
    $allChanges.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10 | ForEach-Object {
        Write-Host "  • $($_.Key): $($_.Value) files"
    }
}

Write-Host ""
Write-Host "=" * 80
Write-Host "✅ BULK ENRICHMENT COMPLETE"
Write-Host "=" * 80
