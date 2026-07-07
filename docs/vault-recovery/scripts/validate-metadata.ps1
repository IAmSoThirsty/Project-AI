# Project-AI Metadata Validation Script
# Version: 1.0.0
# Validates YAML frontmatter against metadata schema

param(
    [Parameter(Mandatory=$false)]
    [string]$File,
    
    [Parameter(Mandatory=$false)]
    [switch]$Recursive,
    
    [Parameter(Mandatory=$false)]
    [switch]$CheckRelationships,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# Configuration
$VaultPath = "T:\Project-AI-vault"
$SchemaPath = Join-Path $VaultPath "schemas\metadata-schema.json"
$ErrorCount = 0
$WarningCount = 0
$ValidatedCount = 0

# Colors
function Write-Success { param($msg) Write-Host $msg -ForegroundColor Green }
function Write-Error-Custom { param($msg) Write-Host $msg -ForegroundColor Red }
function Write-Warning-Custom { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }

# Extract YAML frontmatter from Markdown file
function Get-YamlFrontmatter {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    if ($content -match '(?s)^---\s*\n(.*?)\n---') {
        return $matches[1]
    }
    return $null
}

# Parse YAML to hashtable
function ConvertFrom-Yaml {
    param([string]$YamlContent)
    
    try {
        # Simple YAML parser (for basic validation)
        # In production, use a proper YAML library
        $lines = $YamlContent -split "`n"
        $result = @{}
        $currentKey = $null
        $indent = 0
        
        foreach ($line in $lines) {
            if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
            
            if ($line -match '^([a-z_]+):\s*(.*)$') {
                $key = $matches[1]
                $value = $matches[2]
                
                if ($value) {
                    # Simple value
                    $result[$key] = $value.Trim('"', "'")
                } else {
                    # Complex value (array or object)
                    $currentKey = $key
                    $result[$key] = @()
                }
            }
        }
        
        return $result
    }
    catch {
        Write-Error-Custom "YAML parsing error: $_"
        return $null
    }
}

# Validate required fields
function Test-RequiredFields {
    param($Metadata)
    
    $requiredFields = @('title', 'id', 'type', 'version', 'created_date', 'updated_date', 'status', 'author')
    $errors = @()
    
    foreach ($field in $requiredFields) {
        if (-not $Metadata.ContainsKey($field)) {
            $errors += "Missing required field: $field"
        }
    }
    
    return $errors
}

# Validate ID format (kebab-case)
function Test-IdFormat {
    param([string]$Id)
    
    if ($Id -notmatch '^[a-z0-9]+(-[a-z0-9]+)*$') {
        return "ID must be kebab-case (lowercase letters, numbers, hyphens only)"
    }
    return $null
}

# Validate SemVer format
function Test-SemVerFormat {
    param([string]$Version)
    
    if ($Version -notmatch '^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$') {
        return "Version must follow Semantic Versioning (e.g., 1.0.0, 2.1.3-beta.1)"
    }
    return $null
}

# Validate ISO 8601 date format
function Test-DateFormat {
    param([string]$Date)
    
    try {
        [DateTime]::Parse($Date) | Out-Null
        return $null
    }
    catch {
        return "Date must be ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"
    }
}

# Validate enum values
function Test-EnumValue {
    param([string]$Value, [string[]]$AllowedValues, [string]$FieldName)
    
    if ($Value -notin $AllowedValues) {
        return "${FieldName} must be one of: $($AllowedValues -join ', ')"
    }
    return $null
}

# Validate document type specific requirements
function Test-TypeSpecificFields {
    param($Metadata)
    
    $errors = @()
    $type = $Metadata['type']
    
    switch ($type) {
        'audit' {
            $required = @('auditor', 'audit_date', 'findings', 'risk_level')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Audit documents require field: $field"
                }
            }
        }
        'tutorial' {
            $required = @('difficulty', 'estimated_time', 'prerequisites')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Tutorial documents require field: $field"
                }
            }
        }
        'guide' {
            $required = @('difficulty', 'estimated_time', 'category')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Guide documents require field: $field"
                }
            }
        }
        'postmortem' {
            $required = @('incident_date', 'severity', 'root_cause', 'timeline', 'action_items')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Postmortem documents require field: $field"
                }
            }
        }
        'decision_record' {
            $required = @('decision_date', 'decision_maker', 'options_considered')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Decision record documents require field: $field"
                }
            }
        }
        'policy' {
            $required = @('category', 'compliance', 'enforcement_level')
            foreach ($field in $required) {
                if (-not $Metadata.ContainsKey($field)) {
                    $errors += "Policy documents require field: $field"
                }
            }
        }
    }
    
    return $errors
}

# Validate single file
function Test-MetadataFile {
    param([string]$FilePath)
    
    Write-Info "`nValidating: $FilePath"
    
    # Extract YAML frontmatter
    $yaml = Get-YamlFrontmatter -FilePath $FilePath
    if (-not $yaml) {
        Write-Error-Custom "  ❌ No YAML frontmatter found"
        return $false
    }
    
    # Parse YAML
    $metadata = ConvertFrom-Yaml -YamlContent $yaml
    if (-not $metadata) {
        Write-Error-Custom "  ❌ Failed to parse YAML"
        return $false
    }
    
    # Validate required fields
    $errors = Test-RequiredFields -Metadata $metadata
    
    # Validate ID format
    if ($metadata.ContainsKey('id')) {
        $idError = Test-IdFormat -Id $metadata['id']
        if ($idError) { $errors += $idError }
    }
    
    # Validate version format
    if ($metadata.ContainsKey('version')) {
        $versionError = Test-SemVerFormat -Version $metadata['version']
        if ($versionError) { $errors += $versionError }
    }
    
    # Validate date formats
    if ($metadata.ContainsKey('created_date')) {
        $dateError = Test-DateFormat -Date $metadata['created_date']
        if ($dateError) { $errors += "created_date: $dateError" }
    }
    if ($metadata.ContainsKey('updated_date')) {
        $dateError = Test-DateFormat -Date $metadata['updated_date']
        if ($dateError) { $errors += "updated_date: $dateError" }
    }
    
    # Validate status enum
    if ($metadata.ContainsKey('status')) {
        $statusError = Test-EnumValue -Value $metadata['status'] `
            -AllowedValues @('draft', 'review', 'active', 'deprecated', 'archived') `
            -FieldName 'status'
        if ($statusError) { $errors += $statusError }
    }
    
    # Validate type-specific requirements
    if ($metadata.ContainsKey('type')) {
        $typeErrors = Test-TypeSpecificFields -Metadata $metadata
        $errors += $typeErrors
    }
    
    # Check if deprecated documents have superseded_by
    if ($metadata['status'] -eq 'deprecated' -and -not $metadata.ContainsKey('superseded_by')) {
        $errors += "Deprecated documents must specify 'superseded_by' field"
    }
    
    # Report results
    if ($errors.Count -eq 0) {
        Write-Success "  ✓ Valid"
        return $true
    }
    else {
        Write-Error-Custom "  ❌ Validation failed:"
        foreach ($error in $errors) {
            Write-Error-Custom "     - $error"
        }
        return $false
    }
}

# Main execution
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Project-AI Metadata Validation                           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Check schema exists
if (-not (Test-Path $SchemaPath)) {
    Write-Error-Custom "Schema not found: $SchemaPath"
    exit 1
}

# Get files to validate
$filesToValidate = @()
if ($File) {
    if (-not (Test-Path $File)) {
        Write-Error-Custom "File not found: $File"
        exit 1
    }
    $filesToValidate += $File
}
elseif ($Recursive) {
    $filesToValidate = Get-ChildItem -Path $VaultPath -Filter "*.md" -Recurse | Select-Object -ExpandProperty FullName
}
else {
    $filesToValidate = Get-ChildItem -Path $VaultPath -Filter "*.md" | Select-Object -ExpandProperty FullName
}

Write-Info "Found $($filesToValidate.Count) Markdown files to validate`n"

# Validate each file
foreach ($filePath in $filesToValidate) {
    $isValid = Test-MetadataFile -FilePath $filePath
    $ValidatedCount++
    if (-not $isValid) {
        $ErrorCount++
    }
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Validation Summary                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$passedCount = $ValidatedCount - $ErrorCount
$passRate = if ($ValidatedCount -gt 0) { [math]::Round(($passedCount / $ValidatedCount) * 100, 1) } else { 0 }

Write-Host "`nTotal Files:    $ValidatedCount" -ForegroundColor White
Write-Success "Passed:         $passedCount ($passRate%)"
if ($ErrorCount -gt 0) {
    Write-Error-Custom "Failed:         $ErrorCount"
}
if ($WarningCount -gt 0) {
    Write-Warning-Custom "Warnings:       $WarningCount"
}

# Exit code
if ($ErrorCount -gt 0) {
    Write-Host "`n❌ Validation completed with errors`n" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "`n✅ All validations passed!`n" -ForegroundColor Green
    exit 0
}
