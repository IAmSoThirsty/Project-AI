<#
.SYNOPSIS
    Comprehensive metadata validation system for Project-AI documentation.

.DESCRIPTION
    Validates YAML frontmatter metadata in Markdown files against JSON Schema.
    Provides detailed error reporting, batch processing, and performance metrics.
    
    Features:
    - JSON Schema validation with detailed error messages
    - Batch processing with parallel validation
    - Performance benchmarking (<100ms per file)
    - Multiple output formats (JSON, Markdown, Console)
    - Integration with CI/CD pipelines
    - Comprehensive error catalog
    - Cache support for improved performance

.PARAMETER Path
    File or directory path to validate. Supports wildcards.

.PARAMETER SchemaPath
    Path to JSON Schema file. Defaults to ./validation/schemas/metadata.schema.json

.PARAMETER OutputFormat
    Output format: Console, JSON, or Markdown. Default: Console

.PARAMETER OutputPath
    Path for output report file (required for JSON/Markdown formats)

.PARAMETER Recursive
    Process directories recursively

.PARAMETER Parallel
    Enable parallel processing for batch validation

.PARAMETER StrictMode
    Enable strict validation mode (warnings become errors)

.PARAMETER FailFast
    Stop validation on first error

.PARAMETER Cache
    Enable validation cache for unchanged files

.PARAMETER Verbose
    Enable verbose output with detailed timing information

.EXAMPLE
    .\validate-metadata.ps1 -Path ".\README.md"
    Validate a single file

.EXAMPLE
    .\validate-metadata.ps1 -Path ".\docs" -Recursive -Parallel
    Validate all Markdown files in docs directory recursively with parallel processing

.EXAMPLE
    .\validate-metadata.ps1 -Path ".\docs" -OutputFormat JSON -OutputPath ".\validation\reports\results.json"
    Generate JSON report

.EXAMPLE
    .\validate-metadata.ps1 -Path ".\docs" -StrictMode -FailFast
    Strict validation with fail-fast behavior

.NOTES
    Version: 1.0.0
    Author: AGENT-018: Metadata Validation Engineer
    Created: 2026-01-23
    Performance Target: <100ms per file
    Dependencies: PowerShell 7.0+, powershell-yaml module

.LINK
    https://github.com/project-ai/validation
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path,

    [Parameter(Mandatory = $false)]
    [string]$SchemaPath = ".\validation\schemas\metadata.schema.json",

    [Parameter(Mandatory = $false)]
    [ValidateSet("Console", "JSON", "Markdown")]
    [string]$OutputFormat = "Console",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath,

    [Parameter(Mandatory = $false)]
    [switch]$Recursive,

    [Parameter(Mandatory = $false)]
    [switch]$Parallel,

    [Parameter(Mandatory = $false)]
    [switch]$StrictMode,

    [Parameter(Mandatory = $false)]
    [switch]$FailFast,

    [Parameter(Mandatory = $false)]
    [switch]$Cache,

    [Parameter(Mandatory = $false)]
    [switch]$VerboseOutput
)

#region Configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$script:Config = @{
    PerformanceThreshold = 100  # milliseconds
    MaxParallelJobs      = 8
    CachePath            = ".\validation\.cache\validation-cache.json"
    ErrorCatalogPath     = ".\validation\error-catalog\error-catalog.json"
    SchemaVersion        = "1.0.0"
}

$script:Statistics = @{
    TotalFiles       = 0
    ValidFiles       = 0
    InvalidFiles     = 0
    SkippedFiles     = 0
    TotalErrors      = 0
    TotalWarnings    = 0
    TotalTime        = 0
    AverageTime      = 0
    MaxTime          = 0
    MinTime          = [double]::MaxValue
}

$script:ValidationResults = @()
$script:ErrorCatalog = @{}
#endregion

#region Helper Functions

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success", "Debug")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $colors = @{
        Info    = "Cyan"
        Warning = "Yellow"
        Error   = "Red"
        Success = "Green"
        Debug   = "Gray"
    }
    
    $prefix = switch ($Level) {
        "Info"    { "ℹ" }
        "Warning" { "⚠" }
        "Error"   { "❌" }
        "Success" { "✅" }
        "Debug"   { "🔍" }
    }
    
    if ($VerboseOutput -or $Level -ne "Debug") {
        Write-Host "[$timestamp] $prefix $Message" -ForegroundColor $colors[$Level]
    }
}

function Test-YamlModule {
    Write-Log "Checking for powershell-yaml module..." -Level Debug
    
    if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
        Write-Log "powershell-yaml module not found. Installing..." -Level Warning
        try {
            Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
            Import-Module powershell-yaml -Force
            Write-Log "Successfully installed powershell-yaml module" -Level Success
        }
        catch {
            Write-Log "Failed to install powershell-yaml module: $_" -Level Error
            throw "Required module 'powershell-yaml' is not available. Install it with: Install-Module powershell-yaml"
        }
    }
    else {
        Import-Module powershell-yaml -Force
        Write-Log "powershell-yaml module loaded" -Level Debug
    }
}

function Get-MarkdownFiles {
    param([string]$SearchPath, [bool]$RecursiveSearch)
    
    Write-Log "Searching for Markdown files in: $SearchPath" -Level Debug
    
    if (Test-Path $SearchPath -PathType Leaf) {
        if ($SearchPath -match '\.md$') {
            return @(Get-Item $SearchPath)
        }
        else {
            Write-Log "File is not a Markdown file: $SearchPath" -Level Warning
            return @()
        }
    }
    
    $searchParams = @{
        Path    = $SearchPath
        Filter  = "*.md"
        File    = $true
    }
    
    if ($RecursiveSearch) {
        $searchParams.Recurse = $true
    }
    
    $files = Get-ChildItem @searchParams -ErrorAction SilentlyContinue
    Write-Log "Found $($files.Count) Markdown files" -Level Debug
    return $files
}

function Extract-YamlFrontmatter {
    param([string]$FilePath)
    
    $content = Get-Content $FilePath -Raw
    
    # Match YAML frontmatter between --- delimiters
    $pattern = '(?ms)^---\s*\r?\n(.+?)\r?\n---'
    $match = [regex]::Match($content, $pattern)
    
    if (-not $match.Success) {
        return $null
    }
    
    $yamlContent = $match.Groups[1].Value
    
    try {
        $metadata = ConvertFrom-Yaml $yamlContent -ErrorAction Stop
        return $metadata
    }
    catch {
        Write-Log "Failed to parse YAML in $FilePath : $_" -Level Debug
        return $null
    }
}

function Load-JsonSchema {
    param([string]$SchemaFilePath)
    
    Write-Log "Loading JSON Schema from: $SchemaFilePath" -Level Debug
    
    if (-not (Test-Path $SchemaFilePath)) {
        throw "Schema file not found: $SchemaFilePath"
    }
    
    try {
        $schemaContent = Get-Content $SchemaFilePath -Raw | ConvertFrom-Json
        Write-Log "JSON Schema loaded successfully (version: $($schemaContent.version))" -Level Success
        return $schemaContent
    }
    catch {
        throw "Failed to load JSON Schema: $_"
    }
}

function Validate-MetadataAgainstSchema {
    param(
        [hashtable]$Metadata,
        [PSCustomObject]$Schema,
        [string]$FilePath
    )
    
    $errors = @()
    $warnings = @()
    
    # Check required fields
    if ($Schema.required) {
        foreach ($requiredField in $Schema.required) {
            if (-not $Metadata.ContainsKey($requiredField)) {
                $errors += @{
                    Field   = $requiredField
                    Error   = "REQUIRED_FIELD_MISSING"
                    Message = "Required field '$requiredField' is missing"
                    Path    = $FilePath
                }
            }
        }
    }
    
    # Validate each field present in metadata
    foreach ($key in $Metadata.Keys) {
        $value = $Metadata[$key]
        
        if (-not $Schema.properties.$key) {
            if (-not $Schema.additionalProperties) {
                $warnings += @{
                    Field   = $key
                    Warning = "UNKNOWN_FIELD"
                    Message = "Field '$key' is not defined in schema"
                    Path    = $FilePath
                }
            }
            continue
        }
        
        $fieldSchema = $Schema.properties.$key
        
        # Type validation
        $validationError = Validate-FieldType -Field $key -Value $value -FieldSchema $fieldSchema -FilePath $FilePath
        if ($validationError) {
            $errors += $validationError
        }
        
        # Enum validation
        if ($fieldSchema.enum -and $value -notin $fieldSchema.enum) {
            $errors += @{
                Field   = $key
                Error   = "ENUM_VIOLATION"
                Message = "Value '$value' is not in allowed values: $($fieldSchema.enum -join ', ')"
                Path    = $FilePath
            }
        }
        
        # Pattern validation
        if ($fieldSchema.pattern -and $value -is [string]) {
            if ($value -notmatch $fieldSchema.pattern) {
                $errors += @{
                    Field   = $key
                    Error   = "PATTERN_MISMATCH"
                    Message = "Value '$value' does not match pattern: $($fieldSchema.pattern)"
                    Path    = $FilePath
                }
            }
        }
        
        # String length validation
        if ($value -is [string]) {
            if ($fieldSchema.minLength -and $value.Length -lt $fieldSchema.minLength) {
                $errors += @{
                    Field   = $key
                    Error   = "MIN_LENGTH_VIOLATION"
                    Message = "Value length ($($value.Length)) is less than minimum ($($fieldSchema.minLength))"
                    Path    = $FilePath
                }
            }
            if ($fieldSchema.maxLength -and $value.Length -gt $fieldSchema.maxLength) {
                $errors += @{
                    Field   = $key
                    Error   = "MAX_LENGTH_VIOLATION"
                    Message = "Value length ($($value.Length)) exceeds maximum ($($fieldSchema.maxLength))"
                    Path    = $FilePath
                }
            }
        }
        
        # Array validation
        if ($value -is [array]) {
            if ($fieldSchema.minItems -and $value.Count -lt $fieldSchema.minItems) {
                $errors += @{
                    Field   = $key
                    Error   = "MIN_ITEMS_VIOLATION"
                    Message = "Array has $($value.Count) items, minimum is $($fieldSchema.minItems)"
                    Path    = $FilePath
                }
            }
            if ($fieldSchema.maxItems -and $value.Count -gt $fieldSchema.maxItems) {
                $errors += @{
                    Field   = $key
                    Error   = "MAX_ITEMS_VIOLATION"
                    Message = "Array has $($value.Count) items, maximum is $($fieldSchema.maxItems)"
                    Path    = $FilePath
                }
            }
            if ($fieldSchema.uniqueItems -and ($value | Group-Object | Where-Object Count -gt 1)) {
                $errors += @{
                    Field   = $key
                    Error   = "UNIQUE_ITEMS_VIOLATION"
                    Message = "Array contains duplicate items"
                    Path    = $FilePath
                }
            }
        }
    }
    
    return @{
        Errors   = $errors
        Warnings = $warnings
    }
}

function Validate-FieldType {
    param(
        [string]$Field,
        $Value,
        [PSCustomObject]$FieldSchema,
        [string]$FilePath
    )
    
    $expectedType = $FieldSchema.type
    
    # Determine actual type
    $actualType = "unknown"
    
    if ($Value -is [string]) {
        $actualType = "string"
    }
    elseif ($Value -is [int] -or $Value -is [long] -or $Value -is [double] -or $Value -is [decimal]) {
        $actualType = "number"
    }
    elseif ($Value -is [bool]) {
        $actualType = "boolean"
    }
    elseif ($Value -is [array] -or $Value -is [System.Collections.ArrayList] -or $Value -is [System.Collections.Generic.List[object]]) {
        $actualType = "array"
    }
    elseif ($Value -is [hashtable] -or $Value -is [System.Collections.Specialized.OrderedDictionary]) {
        $actualType = "object"
    }
    elseif ($null -ne $Value -and $Value.GetType().Name -eq "Object[]") {
        $actualType = "array"
    }
    
    if ($expectedType -and $actualType -ne $expectedType) {
        return @{
            Field   = $Field
            Error   = "TYPE_MISMATCH"
            Message = "Expected type '$expectedType' but got '$actualType'"
            Path    = $FilePath
        }
    }
    
    return $null
}

function Test-ValidationCache {
    param([string]$FilePath, [string]$FileHash)
    
    if (-not $Cache) { return $false }
    
    if (-not (Test-Path $script:Config.CachePath)) {
        return $false
    }
    
    try {
        $cacheData = Get-Content $script:Config.CachePath | ConvertFrom-Json
        $cacheEntry = $cacheData.$FilePath
        
        if ($cacheEntry -and $cacheEntry.Hash -eq $FileHash -and $cacheEntry.SchemaVersion -eq $script:Config.SchemaVersion) {
            Write-Log "Cache hit for: $FilePath" -Level Debug
            return $true
        }
    }
    catch {
        Write-Log "Cache read error: $_" -Level Debug
    }
    
    return $false
}

function Update-ValidationCache {
    param([string]$FilePath, [string]$FileHash, [bool]$IsValid)
    
    if (-not $Cache) { return }
    
    $cacheDir = Split-Path $script:Config.CachePath -Parent
    if (-not (Test-Path $cacheDir)) {
        New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    }
    
    $cacheData = @{}
    if (Test-Path $script:Config.CachePath) {
        try {
            $cacheData = Get-Content $script:Config.CachePath | ConvertFrom-Json -AsHashtable
        }
        catch {
            Write-Log "Cache load error, creating new cache" -Level Debug
        }
    }
    
    $cacheData[$FilePath] = @{
        Hash          = $FileHash
        SchemaVersion = $script:Config.SchemaVersion
        IsValid       = $IsValid
        Timestamp     = (Get-Date).ToString("o")
    }
    
    $cacheData | ConvertTo-Json -Depth 10 | Set-Content $script:Config.CachePath
}

function Validate-File {
    param([System.IO.FileInfo]$File, [PSCustomObject]$Schema)
    
    $startTime = Get-Date
    $relativePath = $File.FullName.Replace((Get-Location).Path, ".").Replace("\", "/")
    
    Write-Log "Validating: $relativePath" -Level Debug
    
    # Calculate file hash for caching
    $fileHash = (Get-FileHash -Path $File.FullName -Algorithm MD5).Hash
    
    if (Test-ValidationCache -FilePath $relativePath -FileHash $fileHash) {
        $script:Statistics.SkippedFiles++
        Write-Log "Skipped (cached): $relativePath" -Level Debug
        return $null
    }
    
    # Extract metadata
    $metadata = Extract-YamlFrontmatter -FilePath $File.FullName
    
    if ($null -eq $metadata) {
        $result = @{
            FilePath   = $relativePath
            Status     = "NO_METADATA"
            Message    = "No YAML frontmatter found"
            Errors     = @()
            Warnings   = @()
            Time       = ((Get-Date) - $startTime).TotalMilliseconds
        }
        $script:Statistics.SkippedFiles++
        return $result
    }
    
    # Validate against schema
    $validation = Validate-MetadataAgainstSchema -Metadata $metadata -Schema $Schema -FilePath $relativePath
    
    $elapsedMs = ((Get-Date) - $startTime).TotalMilliseconds
    
    $isValid = $validation.Errors.Count -eq 0 -and (-not $StrictMode -or $validation.Warnings.Count -eq 0)
    
    # Update cache
    Update-ValidationCache -FilePath $relativePath -FileHash $fileHash -IsValid $isValid
    
    # Update statistics
    if ($isValid) {
        $script:Statistics.ValidFiles++
    }
    else {
        $script:Statistics.InvalidFiles++
    }
    
    $script:Statistics.TotalErrors += $validation.Errors.Count
    $script:Statistics.TotalWarnings += $validation.Warnings.Count
    $script:Statistics.TotalTime += $elapsedMs
    
    if ($elapsedMs -gt $script:Statistics.MaxTime) {
        $script:Statistics.MaxTime = $elapsedMs
    }
    if ($elapsedMs -lt $script:Statistics.MinTime) {
        $script:Statistics.MinTime = $elapsedMs
    }
    
    # Performance warning
    if ($elapsedMs -gt $script:Config.PerformanceThreshold) {
        Write-Log "Performance warning: $relativePath took ${elapsedMs}ms (threshold: $($script:Config.PerformanceThreshold)ms)" -Level Warning
    }
    
    return @{
        FilePath   = $relativePath
        Status     = if ($isValid) { "VALID" } else { "INVALID" }
        Errors     = $validation.Errors
        Warnings   = $validation.Warnings
        Time       = $elapsedMs
        Metadata   = $metadata
    }
}

#endregion

#region Output Formatters

function Format-ConsoleOutput {
    param([array]$Results)
    
    Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  METADATA VALIDATION REPORT" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    
    foreach ($result in $Results) {
        $statusColor = switch ($result.Status) {
            "VALID"       { "Green" }
            "INVALID"     { "Red" }
            "NO_METADATA" { "Yellow" }
        }
        
        $statusSymbol = switch ($result.Status) {
            "VALID"       { "✅" }
            "INVALID"     { "❌" }
            "NO_METADATA" { "⚠" }
        }
        
        Write-Host "$statusSymbol $($result.FilePath) " -NoNewline
        Write-Host "[$($result.Status)]" -ForegroundColor $statusColor
        Write-Host "   ⏱ $([math]::Round($result.Time, 2))ms" -ForegroundColor Gray
        
        if ($result.Errors.Count -gt 0) {
            Write-Host "   Errors:" -ForegroundColor Red
            foreach ($error in $result.Errors) {
                Write-Host "     • $($error.Field): $($error.Message)" -ForegroundColor Red
            }
        }
        
        if ($result.Warnings.Count -gt 0) {
            Write-Host "   Warnings:" -ForegroundColor Yellow
            foreach ($warning in $result.Warnings) {
                Write-Host "     • $($warning.Field): $($warning.Message)" -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
    }
    
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  STATISTICS" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Total Files:     $($script:Statistics.TotalFiles)" -ForegroundColor White
    Write-Host "✅ Valid:        $($script:Statistics.ValidFiles)" -ForegroundColor Green
    Write-Host "❌ Invalid:      $($script:Statistics.InvalidFiles)" -ForegroundColor Red
    Write-Host "⚠ Skipped:       $($script:Statistics.SkippedFiles)" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "Errors:          $($script:Statistics.TotalErrors)" -ForegroundColor $(if ($script:Statistics.TotalErrors -gt 0) { "Red" } else { "White" })
    Write-Host "Warnings:        $($script:Statistics.TotalWarnings)" -ForegroundColor $(if ($script:Statistics.TotalWarnings -gt 0) { "Yellow" } else { "White" })
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host "Total Time:      $([math]::Round($script:Statistics.TotalTime, 2))ms" -ForegroundColor White
    Write-Host "Average Time:    $([math]::Round($script:Statistics.TotalTime / [math]::Max($script:Statistics.TotalFiles, 1), 2))ms" -ForegroundColor White
    Write-Host "Min Time:        $([math]::Round($script:Statistics.MinTime, 2))ms" -ForegroundColor White
    Write-Host "Max Time:        $([math]::Round($script:Statistics.MaxTime, 2))ms" -ForegroundColor White
    Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
}

function Format-JsonOutput {
    param([array]$Results, [string]$OutputFile)
    
    $report = @{
        Timestamp  = (Get-Date).ToString("o")
        Schema     = $SchemaPath
        Statistics = $script:Statistics
        Results    = $Results
    }
    
    $report | ConvertTo-Json -Depth 10 | Set-Content $OutputFile
    Write-Log "JSON report saved to: $OutputFile" -Level Success
}

function Format-MarkdownOutput {
    param([array]$Results, [string]$OutputFile)
    
    $md = @"
# Metadata Validation Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Schema:** ``$SchemaPath``  
**Mode:** $(if ($StrictMode) { "Strict" } else { "Normal" })

---

## Summary

| Metric | Value |
|--------|-------|
| Total Files | $($script:Statistics.TotalFiles) |
| ✅ Valid | $($script:Statistics.ValidFiles) |
| ❌ Invalid | $($script:Statistics.InvalidFiles) |
| ⚠ Skipped | $($script:Statistics.SkippedFiles) |
| Errors | $($script:Statistics.TotalErrors) |
| Warnings | $($script:Statistics.TotalWarnings) |

### Performance Metrics

| Metric | Value |
|--------|-------|
| Total Time | $([math]::Round($script:Statistics.TotalTime, 2))ms |
| Average Time | $([math]::Round($script:Statistics.TotalTime / [math]::Max($script:Statistics.TotalFiles, 1), 2))ms |
| Min Time | $([math]::Round($script:Statistics.MinTime, 2))ms |
| Max Time | $([math]::Round($script:Statistics.MaxTime, 2))ms |

---

## Validation Results

"@
    
    foreach ($result in $Results) {
        $statusIcon = switch ($result.Status) {
            "VALID"       { "✅" }
            "INVALID"     { "❌" }
            "NO_METADATA" { "⚠" }
        }
        
        $md += @"

### $statusIcon ``$($result.FilePath)``

- **Status:** $($result.Status)
- **Validation Time:** $([math]::Round($result.Time, 2))ms

"@
        
        if ($result.Errors.Count -gt 0) {
            $md += "`n**Errors:**`n`n"
            foreach ($error in $result.Errors) {
                $md += "- **$($error.Field):** $($error.Message) ``[$($error.Error)]```n"
            }
        }
        
        if ($result.Warnings.Count -gt 0) {
            $md += "`n**Warnings:**`n`n"
            foreach ($warning in $result.Warnings) {
                $md += "- **$($warning.Field):** $($warning.Message) ``[$($warning.Warning)]```n"
            }
        }
    }
    
    $md += @"

---

**Validation completed at:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
    
    $md | Set-Content $OutputFile
    Write-Log "Markdown report saved to: $OutputFile" -Level Success
}

#endregion

#region Main Execution

function Start-Validation {
    Write-Log "Starting metadata validation..." -Level Info
    Write-Log "Schema: $SchemaPath" -Level Info
    Write-Log "Target: $Path" -Level Info
    
    # Initialize
    Test-YamlModule
    $schema = Load-JsonSchema -SchemaFilePath $SchemaPath
    
    # Get files
    $files = Get-MarkdownFiles -SearchPath $Path -RecursiveSearch $Recursive
    $script:Statistics.TotalFiles = $files.Count
    
    if ($files.Count -eq 0) {
        Write-Log "No Markdown files found to validate" -Level Warning
        return
    }
    
    Write-Log "Found $($files.Count) files to validate" -Level Info
    
    # Validate files
    if ($Parallel -and $files.Count -gt 1) {
        Write-Log "Using parallel processing with max $($script:Config.MaxParallelJobs) jobs" -Level Info
        
        $script:ValidationResults = $files | ForEach-Object -ThrottleLimit $script:Config.MaxParallelJobs -Parallel {
            $result = & $using:Function:Validate-File -File $_ -Schema $using:schema
            if ($result) { $result }
        }
    }
    else {
        foreach ($file in $files) {
            $result = Validate-File -File $file -Schema $schema
            
            if ($result) {
                $script:ValidationResults += $result
                
                if ($FailFast -and $result.Status -eq "INVALID") {
                    Write-Log "Fail-fast mode: Stopping on first error" -Level Error
                    break
                }
            }
        }
    }
    
    # Calculate final statistics
    if ($script:Statistics.MinTime -eq [double]::MaxValue) {
        $script:Statistics.MinTime = 0
    }
    
    # Generate output
    switch ($OutputFormat) {
        "Console" {
            Format-ConsoleOutput -Results $script:ValidationResults
        }
        "JSON" {
            if (-not $OutputPath) {
                throw "OutputPath is required for JSON format"
            }
            Format-JsonOutput -Results $script:ValidationResults -OutputFile $OutputPath
            Format-ConsoleOutput -Results $script:ValidationResults
        }
        "Markdown" {
            if (-not $OutputPath) {
                throw "OutputPath is required for Markdown format"
            }
            Format-MarkdownOutput -Results $script:ValidationResults -OutputFile $OutputPath
            Format-ConsoleOutput -Results $script:ValidationResults
        }
    }
    
    # Exit code
    if ($script:Statistics.InvalidFiles -gt 0) {
        Write-Log "Validation completed with errors" -Level Error
        exit 1
    }
    elseif ($script:Statistics.TotalWarnings -gt 0 -and $StrictMode) {
        Write-Log "Validation completed with warnings (strict mode)" -Level Error
        exit 1
    }
    else {
        Write-Log "Validation completed successfully" -Level Success
        exit 0
    }
}

# Execute
try {
    Start-Validation
}
catch {
    Write-Log "Fatal error: $_" -Level Error
    Write-Log $_.ScriptStackTrace -Level Debug
    exit 1
}

#endregion
