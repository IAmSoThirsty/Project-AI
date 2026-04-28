<#
.SYNOPSIS
    Validate P3 Archive Metadata Enrichment

.DESCRIPTION
    Validates that all archive files have proper P3 metadata schema
#>

$validationResults = @()
$archiveFiles = Get-ChildItem -Path "docs\internal\archive" -Filter "*.md"

foreach ($file in $archiveFiles) {
    $content = Get-Content $file.FullName -Raw
    
    $fileResult = @{
        File = $file.Name
        HasFrontmatter = $false
        HasP3Tag = $false
        HasLastVerified = $false
        HasCreated = $false
        HasRelatedSystems = $false
        HasStakeholders = $false
        HasReviewCycle = $false
        HasType = $false
        TypeValue = $null
        YamlValid = $true
        Errors = @()
    }
    
    # Check frontmatter exists
    if ($content -match '(?s)^---\s*[\r\n]+(.*?)[\r\n]+---') {
        $fileResult.HasFrontmatter = $true
        $yaml = $Matches[1]
        
        # Check required fields
        $fileResult.HasP3Tag = $yaml -match 'p3-archive'
        $fileResult.HasLastVerified = $yaml -match 'last_verified:\s*2026-04-20'
        $fileResult.HasCreated = $yaml -match 'created:\s*\d{4}-\d{2}-\d{2}'
        $fileResult.HasRelatedSystems = $yaml -match 'related_systems:'
        $fileResult.HasStakeholders = $yaml -match 'stakeholders:'
        $fileResult.HasReviewCycle = $yaml -match 'review_cycle:\s*annually'
        
        # Extract type
        if ($yaml -match 'type:\s*(\w+)') {
            $fileResult.HasType = $true
            $fileResult.TypeValue = $Matches[1]
        }
    } else {
        $fileResult.Errors += "No frontmatter found"
    }
    
    $validationResults += $fileResult
}

# Summary
$totalFiles = $validationResults.Count
$compliant = ($validationResults | Where-Object {
    $_.HasFrontmatter -and
    $_.HasP3Tag -and
    $_.HasLastVerified -and
    $_.HasCreated -and
    $_.HasRelatedSystems -and
    $_.HasStakeholders -and
    $_.HasReviewCycle -and
    $_.HasType
}).Count

Write-Host "=" * 80
Write-Host "P3 ARCHIVE METADATA VALIDATION REPORT"
Write-Host "=" * 80
Write-Host ""
Write-Host "📊 Total Files: $totalFiles"
Write-Host "✅ Fully Compliant: $compliant"
Write-Host "❌ Non-Compliant: $($totalFiles - $compliant)"
Write-Host ""

# Field compliance
Write-Host "Field Compliance:"
Write-Host "  • Frontmatter: $(($validationResults | Where-Object HasFrontmatter).Count)/$totalFiles"
Write-Host "  • p3-archive tag: $(($validationResults | Where-Object HasP3Tag).Count)/$totalFiles"
Write-Host "  • last_verified: $(($validationResults | Where-Object HasLastVerified).Count)/$totalFiles"
Write-Host "  • created: $(($validationResults | Where-Object HasCreated).Count)/$totalFiles"
Write-Host "  • related_systems: $(($validationResults | Where-Object HasRelatedSystems).Count)/$totalFiles"
Write-Host "  • stakeholders: $(($validationResults | Where-Object HasStakeholders).Count)/$totalFiles"
Write-Host "  • review_cycle: $(($validationResults | Where-Object HasReviewCycle).Count)/$totalFiles"
Write-Host "  • type: $(($validationResults | Where-Object HasType).Count)/$totalFiles"
Write-Host ""

# Type distribution
$typeDistribution = $validationResults | Where-Object HasType | Group-Object TypeValue
Write-Host "Type Distribution:"
foreach ($group in $typeDistribution | Sort-Object Count -Descending) {
    Write-Host "  • $($group.Name): $($group.Count) files"
}
Write-Host ""

# Files with superseded_by
$superseded = $validationResults | Where-Object { 
    $file = Get-Content "docs\internal\archive\$($_.File)" -Raw
    $file -match 'superseded_by:'
}
Write-Host "📎 Files with superseded_by: $($superseded.Count)"
Write-Host ""

# Errors
$filesWithErrors = $validationResults | Where-Object { $_.Errors.Count -gt 0 }
if ($filesWithErrors.Count -gt 0) {
    Write-Host "❌ Files with Errors:"
    foreach ($file in $filesWithErrors) {
        Write-Host "  • $($file.File): $($file.Errors -join ', ')"
    }
} else {
    Write-Host "✅ No errors detected"
}

Write-Host ""
Write-Host "=" * 80
Write-Host "VALIDATION COMPLETE"
Write-Host "=" * 80
