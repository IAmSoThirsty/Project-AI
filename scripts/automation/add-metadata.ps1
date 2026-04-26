<#
.SYNOPSIS
    Generates YAML frontmatter metadata for documentation files.

.DESCRIPTION
    Analyzes file content and generates appropriate YAML frontmatter with tags,
    relationships, path confirmations, and metadata. Supports dry-run mode,
    comprehensive error handling, and logging.

.PARAMETER Path
    Path to the file or directory to process. Can be a single file or directory
    for batch processing.

.PARAMETER DryRun
    If specified, shows what would be done without making changes.

.PARAMETER Force
    If specified, overwrites existing frontmatter.

.PARAMETER TaxonomyPath
    Path to the taxonomy definition file (YAML/JSON).

.PARAMETER LogPath
    Path to the log file. Defaults to automation-logs\add-metadata.log

.PARAMETER Interactive
    If specified, prompts for confirmation before each file.

.PARAMETER OutputFormat
    Format for generated metadata (YAML or JSON). Default: YAML

.EXAMPLE
    .\add-metadata.ps1 -Path ".\docs\README.md" -DryRun
    Preview metadata generation for a single file.

.EXAMPLE
    .\add-metadata.ps1 -Path ".\docs" -Force -LogPath ".\logs\metadata.log"
    Process all files in docs directory, overwriting existing frontmatter.

.EXAMPLE
    .\add-metadata.ps1 -Path ".\wiki" -Interactive -TaxonomyPath ".\taxonomy.yml"
    Process wiki with interactive prompts using custom taxonomy.

.NOTES
    Author: AGENT-020 (Automation Scripts Architect)
    Version: 1.0.0
    Production-ready critical infrastructure.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromPipeline = $true)]
    [ValidateScript({ Test-Path $_ })]
    [string]$Path,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Force,

    [Parameter()]
    [ValidateScript({ 
        if ($_ -and -not (Test-Path $_)) {
            throw "Taxonomy file not found: $_"
        }
        $true
    })]
    [string]$TaxonomyPath,

    [Parameter()]
    [string]$LogPath = ".\automation-logs\add-metadata.log",

    [Parameter()]
    [switch]$Interactive,

    [Parameter()]
    [ValidateSet('YAML', 'JSON')]
    [string]$OutputFormat = 'YAML',

    [Parameter()]
    [int]$MaxFileSize = 10MB,

    [Parameter()]
    [string[]]$ExcludePatterns = @('*.tmp', '*.bak', '*~'),

    [Parameter()]
    [switch]$GenerateRelationships,

    [Parameter()]
    [switch]$SuggestCategories,

    [Parameter()]
    [int]$MaxTags = 10
)

#region Configuration
$ErrorActionPreference = 'Stop'
$script:ProcessedFiles = 0
$script:SkippedFiles = 0
$script:ErrorFiles = 0
$script:StartTime = Get-Date

# Default taxonomy categories
$script:DefaultTaxonomy = @{
    categories = @(
        'architecture',
        'security',
        'infrastructure',
        'documentation',
        'development',
        'testing',
        'deployment',
        'monitoring',
        'governance',
        'ai-systems'
    )
    
    tags = @{
        security     = @('authentication', 'authorization', 'encryption', 'audit', 'compliance', 'vulnerability')
        architecture = @('design', 'patterns', 'components', 'integration', 'microservices', 'api')
        testing      = @('unit', 'integration', 'e2e', 'performance', 'security-testing', 'automation')
        deployment   = @('ci-cd', 'docker', 'kubernetes', 'cloud', 'production', 'staging')
        ai           = @('ml', 'nlp', 'ethics', 'persona', 'learning', 'agents')
    }

    status = @('draft', 'review', 'approved', 'deprecated', 'archived')
}

# Keyword to category mapping
$script:KeywordMapping = @{
    'authentication|login|password|oauth|jwt|session' = 'security/authentication'
    'encryption|decrypt|cipher|crypto|tls|ssl'        = 'security/encryption'
    'docker|container|kubernetes|k8s|helm'            = 'deployment/containers'
    'test|spec|assert|mock|fixture'                   = 'testing'
    'api|endpoint|rest|graphql|grpc'                  = 'architecture/api'
    'ai|ml|model|neural|learning|intelligence'        = 'ai-systems'
    'database|sql|nosql|postgres|mongo|redis'         = 'infrastructure/database'
    'pipeline|ci|cd|github actions|jenkins'           = 'deployment/ci-cd'
    'monitoring|metrics|logs|alerts|observability'    = 'monitoring'
    'policy|governance|compliance|audit'              = 'governance'
}

#endregion

#region Logging Functions

function Initialize-Logging {
    param([string]$LogFile)
    
    try {
        $logDir = Split-Path -Parent $LogFile
        if ($logDir -and -not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
        
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $header = @"
$('=' * 80)
Metadata Generation Log - Started: $timestamp
Command: $($PSCmdlet.MyInvocation.Line)
$('=' * 80)

"@
        Add-Content -Path $LogFile -Value $header
        Write-Verbose "Logging initialized: $LogFile"
    }
    catch {
        Write-Warning "Failed to initialize logging: $_"
    }
}

function Write-Log {
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        
        [ValidateSet('INFO', 'WARN', 'ERROR', 'SUCCESS', 'DEBUG')]
        [string]$Level = 'INFO',
        
        [string]$LogFile = $LogPath
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    try {
        Add-Content -Path $LogFile -Value $logEntry -ErrorAction SilentlyContinue
    }
    catch {
        # Fail silently if logging fails
    }
    
    switch ($Level) {
        'ERROR'   { Write-Host $logEntry -ForegroundColor Red }
        'WARN'    { Write-Host $logEntry -ForegroundColor Yellow }
        'SUCCESS' { Write-Host $logEntry -ForegroundColor Green }
        'DEBUG'   { Write-Verbose $logEntry }
        default   { Write-Host $logEntry }
    }
}

#endregion

#region Taxonomy Functions

function Import-Taxonomy {
    param([string]$Path)
    
    if (-not $Path) {
        Write-Log "Using default taxonomy" -Level DEBUG
        return $script:DefaultTaxonomy
    }
    
    try {
        Write-Log "Loading taxonomy from: $Path" -Level INFO
        
        $content = Get-Content -Path $Path -Raw
        $extension = [System.IO.Path]::GetExtension($Path).ToLower()
        
        $taxonomy = switch ($extension) {
            '.json' { $content | ConvertFrom-Json }
            '.yml'  { ConvertFrom-Yaml $content }
            '.yaml' { ConvertFrom-Yaml $content }
            default { throw "Unsupported taxonomy format: $extension" }
        }
        
        Write-Log "Taxonomy loaded successfully" -Level SUCCESS
        return $taxonomy
    }
    catch {
        Write-Log "Failed to load taxonomy: $_" -Level ERROR
        Write-Log "Falling back to default taxonomy" -Level WARN
        return $script:DefaultTaxonomy
    }
}

function ConvertFrom-Yaml {
    param([string]$Content)
    
    # Simple YAML parser for basic structures
    $result = @{}
    $currentSection = $null
    $lines = $Content -split "`n"
    
    foreach ($line in $lines) {
        $line = $line.Trim()
        if ($line -match '^(\w+):$') {
            $currentSection = $matches[1]
            $result[$currentSection] = @()
        }
        elseif ($line -match '^\s*-\s*(.+)$' -and $currentSection) {
            $result[$currentSection] += $matches[1].Trim()
        }
    }
    
    return $result
}

#endregion

#region Content Analysis Functions

function Get-FileMetadata {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath
    )
    
    try {
        $file = Get-Item -Path $FilePath
        $content = Get-Content -Path $FilePath -Raw -ErrorAction Stop
        
        # Check if file already has frontmatter
        $hasFrontmatter = $content -match '^---\s*\n.*?\n---\s*\n'
        
        $metadata = @{
            FileName        = $file.Name
            FilePath        = $file.FullName
            RelativePath    = $file.FullName -replace [regex]::Escape((Get-Location).Path), '.'
            FileSize        = $file.Length
            Created         = $file.CreationTime
            Modified        = $file.LastWriteTime
            Extension       = $file.Extension
            HasFrontmatter  = $hasFrontmatter
            Content         = $content
            LineCount       = ($content -split "`n").Count
            WordCount       = ($content -split '\s+').Count
        }
        
        return $metadata
    }
    catch {
        Write-Log "Error reading file metadata: $FilePath - $_" -Level ERROR
        throw
    }
}

function Analyze-ContentKeywords {
    param(
        [Parameter(Mandatory)]
        [string]$Content,
        
        [hashtable]$Taxonomy
    )
    
    $keywords = @()
    $categories = @()
    $tags = @()
    
    # Extract technical terms and acronyms
    $technicalTerms = [regex]::Matches($Content, '\b[A-Z]{2,}\b') | 
        Select-Object -ExpandProperty Value | 
        Sort-Object -Unique
    
    # Extract heading-based keywords
    $headings = [regex]::Matches($Content, '^#{1,6}\s+(.+)$', 'Multiline') |
        Select-Object -ExpandProperty Groups |
        Where-Object { $_.Index -gt 0 } |
        Select-Object -ExpandProperty Value
    
    # Combine all potential keywords
    $allText = ($Content + " " + ($headings -join ' ')).ToLower()
    
    # Match against keyword mapping
    foreach ($pattern in $script:KeywordMapping.Keys) {
        if ($allText -match $pattern) {
            $category = $script:KeywordMapping[$pattern]
            if ($category -notin $categories) {
                $categories += $category
            }
        }
    }
    
    # Extract code blocks and language indicators
    $codeBlocks = [regex]::Matches($Content, '```(\w+)') |
        Select-Object -ExpandProperty Groups |
        Where-Object { $_.Index -gt 0 } |
        Select-Object -ExpandProperty Value |
        Sort-Object -Unique
    
    if ($codeBlocks) {
        $tags += $codeBlocks | ForEach-Object { "lang-$_" }
    }
    
    return @{
        Categories      = $categories | Select-Object -First 3
        TechnicalTerms  = $technicalTerms | Select-Object -First 10
        CodeLanguages   = $codeBlocks
        SuggestedTags   = $tags | Select-Object -First $MaxTags
    }
}

function Find-RelatedFiles {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        
        [string]$Content
    )
    
    $related = @()
    $directory = Split-Path -Parent $FilePath
    
    # Find markdown links in content
    $links = [regex]::Matches($Content, '\[([^\]]+)\]\(([^)]+\.md)\)') |
        Select-Object -ExpandProperty Groups |
        Where-Object { $_.Index -gt 0 -and $_.Value -match '\.md$' } |
        Select-Object -ExpandProperty Value |
        Sort-Object -Unique
    
    foreach ($link in $links) {
        $linkPath = Join-Path $directory $link
        if (Test-Path $linkPath) {
            $related += @{
                Type = 'reference'
                Path = $linkPath -replace [regex]::Escape((Get-Location).Path), '.'
            }
        }
    }
    
    # Find files in same directory
    $siblings = Get-ChildItem -Path $directory -Filter "*.md" -File |
        Where-Object { $_.FullName -ne $FilePath } |
        Select-Object -First 5
    
    foreach ($sibling in $siblings) {
        $related += @{
            Type = 'sibling'
            Path = $sibling.FullName -replace [regex]::Escape((Get-Location).Path), '.'
        }
    }
    
    return $related
}

#endregion

#region Frontmatter Generation

function New-Frontmatter {
    param(
        [Parameter(Mandatory)]
        [hashtable]$Metadata,
        
        [hashtable]$Analysis,
        
        [array]$Related,
        
        [string]$Format = 'YAML'
    )
    
    $frontmatter = [ordered]@{
        title         = $Metadata.FileName -replace '\.\w+$', '' -replace '[-_]', ' '
        created       = $Metadata.Created.ToString('yyyy-MM-dd')
        modified      = $Metadata.Modified.ToString('yyyy-MM-dd')
        path          = $Metadata.RelativePath
        categories    = $Analysis.Categories
        tags          = $Analysis.SuggestedTags
        status        = 'draft'
        word_count    = $Metadata.WordCount
        line_count    = $Metadata.LineCount
    }
    
    if ($Analysis.CodeLanguages) {
        $frontmatter['languages'] = $Analysis.CodeLanguages
    }
    
    if ($Related -and $GenerateRelationships) {
        $frontmatter['related'] = $Related | ForEach-Object {
            @{
                type = $_.Type
                path = $_.Path
            }
        }
    }
    
    if ($Format -eq 'YAML') {
        return ConvertTo-YamlFrontmatter $frontmatter
    }
    else {
        return ConvertTo-JsonFrontmatter $frontmatter
    }
}

function ConvertTo-YamlFrontmatter {
    param([hashtable]$Data)
    
    $yaml = @("---")
    
    foreach ($key in $Data.Keys) {
        $value = $Data[$key]
        
        if ($value -is [array]) {
            if ($value.Count -eq 0) {
                $yaml += "${key}: []"
            }
            else {
                $yaml += "${key}:"
                foreach ($item in $value) {
                    if ($item -is [hashtable]) {
                        $yaml += "  - type: $($item.type)"
                        $yaml += "    path: $($item.path)"
                    }
                    else {
                        $yaml += "  - $item"
                    }
                }
            }
        }
        elseif ($value -is [hashtable]) {
            $yaml += "${key}:"
            foreach ($subKey in $value.Keys) {
                $yaml += "  ${subKey}: $($value[$subKey])"
            }
        }
        else {
            $yaml += "${key}: $value"
        }
    }
    
    $yaml += "---"
    $yaml += ""
    
    return $yaml -join "`n"
}

function ConvertTo-JsonFrontmatter {
    param([hashtable]$Data)
    
    $json = $Data | ConvertTo-Json -Depth 10 -Compress
    return "<!-- METADATA`n$json`n-->`n`n"
}

#endregion

#region File Processing

function Add-FrontmatterToFile {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        
        [Parameter(Mandatory)]
        [string]$Frontmatter,
        
        [switch]$Force
    )
    
    try {
        $content = Get-Content -Path $FilePath -Raw
        
        # Check if frontmatter already exists
        if ($content -match '^---\s*\n.*?\n---\s*\n' -and -not $Force) {
            Write-Log "File already has frontmatter: $FilePath (use -Force to overwrite)" -Level WARN
            return $false
        }
        
        # Remove existing frontmatter if Force is specified
        if ($Force -and $content -match '^---\s*\n.*?\n---\s*\n') {
            $content = $content -replace '^---\s*\n.*?\n---\s*\n', ''
            Write-Log "Removed existing frontmatter from: $FilePath" -Level INFO
        }
        
        # Add new frontmatter
        $newContent = $Frontmatter + $content.TrimStart()
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would add frontmatter to: $FilePath" -Level INFO
            Write-Host "`nGenerated frontmatter:" -ForegroundColor Cyan
            Write-Host $Frontmatter -ForegroundColor Gray
            return $true
        }
        
        if ($Interactive) {
            Write-Host "`nGenerated frontmatter for: $FilePath" -ForegroundColor Cyan
            Write-Host $Frontmatter -ForegroundColor Gray
            $response = Read-Host "Apply this frontmatter? (y/n)"
            if ($response -notmatch '^y(es)?$') {
                Write-Log "Skipped by user: $FilePath" -Level INFO
                return $false
            }
        }
        
        # Create backup
        $backupPath = "$FilePath.bak"
        Copy-Item -Path $FilePath -Destination $backupPath -Force
        Write-Log "Created backup: $backupPath" -Level DEBUG
        
        # Write updated content
        Set-Content -Path $FilePath -Value $newContent -NoNewline
        Write-Log "Added frontmatter to: $FilePath" -Level SUCCESS
        
        return $true
    }
    catch {
        Write-Log "Error processing file: $FilePath - $_" -Level ERROR
        throw
    }
}

function Process-File {
    param([string]$FilePath)
    
    try {
        Write-Log "Processing: $FilePath" -Level INFO
        
        # Validate file
        $file = Get-Item -Path $FilePath
        
        if ($file.Length -gt $MaxFileSize) {
            Write-Log "File too large (>$MaxFileSize): $FilePath" -Level WARN
            $script:SkippedFiles++
            return
        }
        
        # Check exclusion patterns
        foreach ($pattern in $ExcludePatterns) {
            if ($file.Name -like $pattern) {
                Write-Log "Excluded by pattern '$pattern': $FilePath" -Level DEBUG
                $script:SkippedFiles++
                return
            }
        }
        
        # Get metadata and analyze content
        $metadata = Get-FileMetadata -FilePath $FilePath
        $analysis = Analyze-ContentKeywords -Content $metadata.Content -Taxonomy $script:Taxonomy
        
        # Find related files if requested
        $related = $null
        if ($GenerateRelationships) {
            $related = Find-RelatedFiles -FilePath $FilePath -Content $metadata.Content
        }
        
        # Generate frontmatter
        $frontmatter = New-Frontmatter -Metadata $metadata -Analysis $analysis -Related $related -Format $OutputFormat
        
        # Add to file
        $success = Add-FrontmatterToFile -FilePath $FilePath -Frontmatter $frontmatter -Force:$Force
        
        if ($success) {
            $script:ProcessedFiles++
        }
        else {
            $script:SkippedFiles++
        }
    }
    catch {
        Write-Log "Failed to process file: $FilePath - $_" -Level ERROR
        $script:ErrorFiles++
    }
}

function Process-Directory {
    param([string]$DirectoryPath)
    
    Write-Log "Processing directory: $DirectoryPath" -Level INFO
    
    $files = Get-ChildItem -Path $DirectoryPath -Filter "*.md" -Recurse -File
    $totalFiles = $files.Count
    
    Write-Log "Found $totalFiles markdown files" -Level INFO
    
    $currentFile = 0
    foreach ($file in $files) {
        $currentFile++
        $percentComplete = [math]::Round(($currentFile / $totalFiles) * 100, 2)
        
        Write-Progress -Activity "Processing files" `
            -Status "File $currentFile of $totalFiles ($percentComplete%)" `
            -PercentComplete $percentComplete `
            -CurrentOperation $file.Name
        
        Process-File -FilePath $file.FullName
    }
    
    Write-Progress -Activity "Processing files" -Completed
}

#endregion

#region Main Execution

function Show-Summary {
    $duration = (Get-Date) - $script:StartTime
    
    $summary = @"

$('=' * 80)
PROCESSING SUMMARY
$('=' * 80)
Total Files:      $($script:ProcessedFiles + $script:SkippedFiles + $script:ErrorFiles)
Processed:        $script:ProcessedFiles
Skipped:          $script:SkippedFiles
Errors:           $script:ErrorFiles
Duration:         $($duration.ToString('mm\:ss'))
Mode:             $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })
$('=' * 80)

"@
    
    Write-Host $summary
    Write-Log $summary -Level INFO
}

# Main execution
try {
    Write-Host "`n=== Metadata Generation Tool ===" -ForegroundColor Cyan
    Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })`n" -ForegroundColor Yellow
    
    # Initialize logging
    Initialize-Logging -LogFile $LogPath
    Write-Log "Starting metadata generation" -Level INFO
    Write-Log "Target: $Path" -Level INFO
    
    # Load taxonomy
    $script:Taxonomy = Import-Taxonomy -Path $TaxonomyPath
    
    # Process path
    $item = Get-Item -Path $Path
    
    if ($item.PSIsContainer) {
        Process-Directory -DirectoryPath $Path
    }
    else {
        Process-File -FilePath $Path
    }
    
    # Show summary
    Show-Summary
    
    Write-Log "Metadata generation completed" -Level SUCCESS
    
    exit 0
}
catch {
    Write-Log "Critical error: $_" -Level ERROR
    Write-Log $_.ScriptStackTrace -Level ERROR
    Show-Summary
    exit 1
}
finally {
    # Cleanup
    if (Test-Path variable:script:Taxonomy) {
        Remove-Variable -Name Taxonomy -Scope script -ErrorAction SilentlyContinue
    }
}

#endregion
