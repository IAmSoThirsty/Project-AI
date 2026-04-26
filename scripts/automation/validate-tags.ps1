<#
.SYNOPSIS
    Validates tags in documentation files against a taxonomy.

.DESCRIPTION
    Scans documentation files for tags, validates them against a defined taxonomy,
    identifies invalid tags, suggests corrections, and generates batch reports.

.PARAMETER Path
    Path to file or directory to validate.

.PARAMETER TaxonomyPath
    Path to taxonomy definition file (YAML/JSON).

.PARAMETER LogPath
    Path to log file. Default: .\automation-logs\validate-tags.log

.PARAMETER ReportPath
    Path to output validation report. Default: .\automation-reports\tag-validation.html

.PARAMETER FixInvalidTags
    Automatically fix invalid tags with suggestions.

.PARAMETER Interactive
    Prompt for confirmation before fixing tags.

.PARAMETER OutputFormat
    Report format: HTML, JSON, or CSV. Default: HTML

.EXAMPLE
    .\validate-tags.ps1 -Path ".\docs" -TaxonomyPath ".\taxonomy.yml"
    Validate all tags in docs directory.

.EXAMPLE
    .\validate-tags.ps1 -Path ".\wiki" -FixInvalidTags -Interactive
    Validate and interactively fix invalid tags.

.EXAMPLE
    .\validate-tags.ps1 -Path ".\docs" -ReportPath ".\report.json" -OutputFormat JSON
    Generate JSON validation report.

.NOTES
    Author: AGENT-020 (Automation Scripts Architect)
    Version: 1.0.0
    Production-ready critical infrastructure.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateScript({ Test-Path $_ })]
    [string]$Path,

    [Parameter()]
    [ValidateScript({ 
        if ($_ -and -not (Test-Path $_)) {
            throw "Taxonomy file not found: $_"
        }
        $true
    })]
    [string]$TaxonomyPath,

    [Parameter()]
    [string]$LogPath = ".\automation-logs\validate-tags.log",

    [Parameter()]
    [string]$ReportPath = ".\automation-reports\tag-validation.html",

    [Parameter()]
    [switch]$FixInvalidTags,

    [Parameter()]
    [switch]$Interactive,

    [Parameter()]
    [ValidateSet('HTML', 'JSON', 'CSV')]
    [string]$OutputFormat = 'HTML',

    [Parameter()]
    [int]$SuggestionThreshold = 70,

    [Parameter()]
    [switch]$StrictMode,

    [Parameter()]
    [switch]$CheckDuplicates,

    [Parameter()]
    [switch]$CheckCasing,

    [Parameter()]
    [int]$MinSimilarity = 60
)

$ErrorActionPreference = 'Stop'
$script:TotalFiles = 0
$script:FilesWithIssues = 0
$script:InvalidTags = 0
$script:FixedTags = 0
$script:ValidationResults = @()
$script:StartTime = Get-Date

#region Configuration

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
        'security'       = @('authentication', 'authorization', 'encryption', 'audit', 'compliance', 'vulnerability', 'penetration-testing', 'threat-modeling')
        'architecture'   = @('design', 'patterns', 'components', 'integration', 'microservices', 'api', 'event-driven', 'serverless')
        'testing'        = @('unit', 'integration', 'e2e', 'performance', 'security-testing', 'automation', 'tdd', 'bdd')
        'deployment'     = @('ci-cd', 'docker', 'kubernetes', 'cloud', 'production', 'staging', 'blue-green', 'canary')
        'ai-systems'     = @('ml', 'nlp', 'ethics', 'persona', 'learning', 'agents', 'training', 'inference')
        'infrastructure' = @('database', 'cache', 'messaging', 'storage', 'networking', 'dns', 'load-balancing')
        'development'    = @('coding', 'refactoring', 'code-review', 'git', 'branching', 'versioning', 'standards')
        'monitoring'     = @('metrics', 'logging', 'tracing', 'alerting', 'dashboards', 'apm', 'observability')
        'governance'     = @('policy', 'compliance', 'audit', 'risk-management', 'data-governance', 'access-control')
        'documentation'  = @('readme', 'wiki', 'api-docs', 'guides', 'tutorials', 'runbooks', 'architecture-docs')
    }
    
    aliases = @{
        'auth'    = 'authentication'
        'authz'   = 'authorization'
        'k8s'     = 'kubernetes'
        'db'      = 'database'
        'ci'      = 'ci-cd'
        'cd'      = 'ci-cd'
        'ml'      = 'machine-learning'
        'ai'      = 'artificial-intelligence'
    }
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
Tag Validation Log - Started: $timestamp
Command: $($PSCmdlet.MyInvocation.Line)
$('=' * 80)

"@
        Add-Content -Path $LogFile -Value $header
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
        # Fail silently
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
            '.json' { $content | ConvertFrom-Json -AsHashtable }
            '.yml'  { ConvertFrom-Yaml $content }
            '.yaml' { ConvertFrom-Yaml $content }
            default { throw "Unsupported taxonomy format: $extension" }
        }
        
        Write-Log "Taxonomy loaded: $($taxonomy.tags.Count) categories" -Level SUCCESS
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
    
    $result = @{
        categories = @()
        tags       = @{}
        aliases    = @{}
    }
    
    $currentSection = $null
    $currentCategory = $null
    $lines = $Content -split "`n"
    
    foreach ($line in $lines) {
        $line = $line.Trim()
        
        if ($line -match '^(categories|tags|aliases):$') {
            $currentSection = $matches[1]
            $currentCategory = $null
        }
        elseif ($line -match '^\s*(\w+):$' -and $currentSection -eq 'tags') {
            $currentCategory = $matches[1]
            $result.tags[$currentCategory] = @()
        }
        elseif ($line -match '^\s*-\s*(.+)$') {
            $value = $matches[1].Trim()
            if ($currentSection -eq 'categories') {
                $result.categories += $value
            }
            elseif ($currentSection -eq 'tags' -and $currentCategory) {
                $result.tags[$currentCategory] += $value
            }
        }
        elseif ($line -match '^\s*(\w+):\s*(.+)$' -and $currentSection -eq 'aliases') {
            $result.aliases[$matches[1]] = $matches[2].Trim()
        }
    }
    
    return $result
}

function Get-AllValidTags {
    param([hashtable]$Taxonomy)
    
    $allTags = @()
    
    # Add all tags from all categories
    foreach ($category in $Taxonomy.tags.Keys) {
        $allTags += $Taxonomy.tags[$category]
    }
    
    # Add categories themselves as valid tags
    $allTags += $Taxonomy.categories
    
    return $allTags | Sort-Object -Unique
}

#endregion

#region String Similarity Functions

function Get-LevenshteinDistance {
    param(
        [string]$String1,
        [string]$String2
    )
    
    $len1 = $String1.Length
    $len2 = $String2.Length
    $distance = New-Object 'int[,]' ($len1 + 1), ($len2 + 1)
    
    for ($i = 0; $i -le $len1; $i++) {
        $distance[$i, 0] = $i
    }
    
    for ($j = 0; $j -le $len2; $j++) {
        $distance[0, $j] = $j
    }
    
    for ($i = 1; $i -le $len1; $i++) {
        for ($j = 1; $j -le $len2; $j++) {
            $cost = if ($String1[$i - 1] -eq $String2[$j - 1]) { 0 } else { 1 }
            
            $distance[$i, $j] = [Math]::Min(
                [Math]::Min(
                    $distance[$i - 1, $j] + 1,
                    $distance[$i, $j - 1] + 1
                ),
                $distance[$i - 1, $j - 1] + $cost
            )
        }
    }
    
    return $distance[$len1, $len2]
}

function Get-SimilarityPercentage {
    param(
        [string]$String1,
        [string]$String2
    )
    
    $maxLen = [Math]::Max($String1.Length, $String2.Length)
    if ($maxLen -eq 0) { return 100 }
    
    $distance = Get-LevenshteinDistance -String1 $String1 -String2 $String2
    $similarity = (1 - ($distance / $maxLen)) * 100
    
    return [Math]::Round($similarity, 2)
}

function Find-SimilarTags {
    param(
        [string]$Tag,
        [array]$ValidTags,
        [int]$MinSimilarity = 60
    )
    
    $suggestions = @()
    
    foreach ($validTag in $ValidTags) {
        $similarity = Get-SimilarityPercentage -String1 $Tag.ToLower() -String2 $validTag.ToLower()
        
        if ($similarity -ge $MinSimilarity) {
            $suggestions += @{
                Tag        = $validTag
                Similarity = $similarity
            }
        }
    }
    
    return $suggestions | Sort-Object -Property Similarity -Descending
}

#endregion

#region Validation Functions

function Get-FileTags {
    param([string]$FilePath)
    
    try {
        $content = Get-Content -Path $FilePath -Raw
        
        # Extract YAML frontmatter
        if ($content -match '^---\s*\n(.*?)\n---\s*\n') {
            $frontmatter = $matches[1]
            
            # Parse tags
            $tags = @()
            if ($frontmatter -match '(?ms)^tags:\s*\n((?:\s+-\s+.+\n?)+)') {
                $tagSection = $matches[1]
                $tags = [regex]::Matches($tagSection, '^\s+-\s+(.+)$', 'Multiline') |
                    Select-Object -ExpandProperty Groups |
                    Where-Object { $_.Index -gt 0 } |
                    Select-Object -ExpandProperty Value |
                    ForEach-Object { $_.Trim() }
            }
            elseif ($frontmatter -match '^tags:\s*\[(.+)\]') {
                $tags = $matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") }
            }
            
            return $tags
        }
        
        return @()
    }
    catch {
        Write-Log "Error reading tags from: $FilePath - $_" -Level ERROR
        return @()
    }
}

function Test-TagValidity {
    param(
        [string]$Tag,
        [array]$ValidTags,
        [hashtable]$Taxonomy
    )
    
    # Check if tag is valid
    if ($Tag -in $ValidTags) {
        return @{
            Valid = $true
            Tag   = $Tag
        }
    }
    
    # Check if tag is an alias
    if ($Taxonomy.aliases.ContainsKey($Tag)) {
        return @{
            Valid       = $true
            Tag         = $Tag
            IsAlias     = $true
            Canonical   = $Taxonomy.aliases[$Tag]
        }
    }
    
    # Check casing if enabled
    if ($CheckCasing) {
        $correctCase = $ValidTags | Where-Object { $_.ToLower() -eq $Tag.ToLower() }
        if ($correctCase) {
            return @{
                Valid        = $false
                Tag          = $Tag
                Issue        = 'CasingError'
                Correction   = $correctCase
            }
        }
    }
    
    # Find similar tags
    $suggestions = Find-SimilarTags -Tag $Tag -ValidTags $ValidTags -MinSimilarity $MinSimilarity
    
    return @{
        Valid       = $false
        Tag         = $Tag
        Issue       = 'InvalidTag'
        Suggestions = $suggestions
    }
}

function Validate-FileTags {
    param(
        [string]$FilePath,
        [array]$ValidTags,
        [hashtable]$Taxonomy
    )
    
    try {
        $tags = Get-FileTags -FilePath $FilePath
        
        if ($tags.Count -eq 0) {
            return @{
                FilePath    = $FilePath
                HasTags     = $false
                ValidTags   = @()
                InvalidTags = @()
                Issues      = @()
            }
        }
        
        $validationResults = @{
            FilePath    = $FilePath
            HasTags     = $true
            ValidTags   = @()
            InvalidTags = @()
            Issues      = @()
        }
        
        # Check duplicates if enabled
        if ($CheckDuplicates) {
            $duplicates = $tags | Group-Object | Where-Object { $_.Count -gt 1 }
            if ($duplicates) {
                $validationResults.Issues += @{
                    Type = 'Duplicates'
                    Tags = $duplicates.Name
                }
            }
        }
        
        # Validate each tag
        foreach ($tag in $tags) {
            $result = Test-TagValidity -Tag $tag -ValidTags $ValidTags -Taxonomy $Taxonomy
            
            if ($result.Valid) {
                $validationResults.ValidTags += $tag
                
                if ($result.IsAlias) {
                    $validationResults.Issues += @{
                        Type      = 'Alias'
                        Tag       = $tag
                        Canonical = $result.Canonical
                    }
                }
            }
            else {
                $validationResults.InvalidTags += $tag
                $validationResults.Issues += $result
            }
        }
        
        return $validationResults
    }
    catch {
        Write-Log "Error validating file: $FilePath - $_" -Level ERROR
        return $null
    }
}

#endregion

#region Fix Functions

function Fix-FileTags {
    param(
        [Parameter(Mandatory)]
        [hashtable]$ValidationResult
    )
    
    try {
        $filePath = $ValidationResult.FilePath
        $content = Get-Content -Path $filePath -Raw
        
        if ($content -notmatch '^---\s*\n(.*?)\n---\s*\n') {
            Write-Log "No frontmatter found in: $filePath" -Level WARN
            return $false
        }
        
        $fixed = 0
        $originalContent = $content
        
        foreach ($issue in $ValidationResult.Issues) {
            if ($issue.Type -eq 'Duplicates') {
                # Remove duplicates
                # Implementation would involve rewriting frontmatter
                Write-Log "Duplicate tags found: $($issue.Tags -join ', ')" -Level WARN
            }
            elseif ($issue.Issue -eq 'CasingError') {
                # Fix casing
                $content = $content -replace "\b$($issue.Tag)\b", $issue.Correction
                Write-Log "Fixed casing: $($issue.Tag) -> $($issue.Correction)" -Level INFO
                $fixed++
            }
            elseif ($issue.IsAlias) {
                # Replace alias with canonical
                $content = $content -replace "\b$($issue.Tag)\b", $issue.Canonical
                Write-Log "Replaced alias: $($issue.Tag) -> $($issue.Canonical)" -Level INFO
                $fixed++
            }
            elseif ($issue.Issue -eq 'InvalidTag' -and $issue.Suggestions.Count -gt 0) {
                # Use best suggestion if similarity is high enough
                $bestSuggestion = $issue.Suggestions[0]
                
                if ($bestSuggestion.Similarity -ge $SuggestionThreshold) {
                    if ($Interactive) {
                        Write-Host "`nInvalid tag: '$($issue.Tag)' in $filePath" -ForegroundColor Yellow
                        Write-Host "Suggestion: '$($bestSuggestion.Tag)' (${$bestSuggestion.Similarity}% similar)" -ForegroundColor Cyan
                        $response = Read-Host "Apply suggestion? (y/n)"
                        
                        if ($response -match '^y(es)?$') {
                            $content = $content -replace "\b$($issue.Tag)\b", $bestSuggestion.Tag
                            Write-Log "Fixed tag: $($issue.Tag) -> $($bestSuggestion.Tag)" -Level SUCCESS
                            $fixed++
                        }
                    }
                    else {
                        $content = $content -replace "\b$($issue.Tag)\b", $bestSuggestion.Tag
                        Write-Log "Auto-fixed tag: $($issue.Tag) -> $($bestSuggestion.Tag)" -Level SUCCESS
                        $fixed++
                    }
                }
            }
        }
        
        if ($content -ne $originalContent) {
            Set-Content -Path $filePath -Value $content -NoNewline
            Write-Log "Fixed $fixed tags in: $filePath" -Level SUCCESS
            $script:FixedTags += $fixed
            return $true
        }
        
        return $false
    }
    catch {
        Write-Log "Error fixing tags in: $($ValidationResult.FilePath) - $_" -Level ERROR
        return $false
    }
}

#endregion

#region Report Generation

function New-HtmlReport {
    param([array]$Results)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Tag Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .summary { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary-item { display: inline-block; margin-right: 30px; }
        .summary-value { font-size: 24px; font-weight: bold; color: #2196F3; }
        table { width: 100%; border-collapse: collapse; background: white; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #2196F3; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .valid { color: green; }
        .invalid { color: red; }
        .warning { color: orange; }
        .issue-list { margin: 5px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <h1>Tag Validation Report</h1>
    <div class="summary">
        <div class="summary-item">
            <div>Total Files</div>
            <div class="summary-value">$script:TotalFiles</div>
        </div>
        <div class="summary-item">
            <div>Files with Issues</div>
            <div class="summary-value">$script:FilesWithIssues</div>
        </div>
        <div class="summary-item">
            <div>Invalid Tags</div>
            <div class="summary-value">$script:InvalidTags</div>
        </div>
        <div class="summary-item">
            <div>Fixed Tags</div>
            <div class="summary-value">$script:FixedTags</div>
        </div>
    </div>
    <table>
        <tr>
            <th>File</th>
            <th>Valid Tags</th>
            <th>Invalid Tags</th>
            <th>Issues</th>
        </tr>
"@
    
    foreach ($result in $Results) {
        if (-not $result.HasTags) { continue }
        
        $issuesHtml = ""
        if ($result.Issues.Count -gt 0) {
            $issuesHtml = "<ul class='issue-list'>"
            foreach ($issue in $result.Issues) {
                if ($issue.Type -eq 'Duplicates') {
                    $issuesHtml += "<li class='warning'>Duplicates: $($issue.Tags -join ', ')</li>"
                }
                elseif ($issue.Issue -eq 'CasingError') {
                    $issuesHtml += "<li class='warning'>Casing: $($issue.Tag) → $($issue.Correction)</li>"
                }
                elseif ($issue.Issue -eq 'InvalidTag') {
                    $suggestions = $issue.Suggestions | Select-Object -First 3 | ForEach-Object { "$($_.Tag) ($($_.Similarity)%)" }
                    $issuesHtml += "<li class='invalid'>Invalid: $($issue.Tag) (suggestions: $($suggestions -join ', '))</li>"
                }
            }
            $issuesHtml += "</ul>"
        }
        
        $html += @"
        <tr>
            <td>$($result.FilePath -replace [regex]::Escape((Get-Location).Path), '.')</td>
            <td class='valid'>$($result.ValidTags.Count)</td>
            <td class='invalid'>$($result.InvalidTags.Count)</td>
            <td>$issuesHtml</td>
        </tr>
"@
    }
    
    $html += @"
    </table>
    <p><small>Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</small></p>
</body>
</html>
"@
    
    return $html
}

function New-JsonReport {
    param([array]$Results)
    
    $report = @{
        timestamp      = (Get-Date).ToString('o')
        summary        = @{
            totalFiles      = $script:TotalFiles
            filesWithIssues = $script:FilesWithIssues
            invalidTags     = $script:InvalidTags
            fixedTags       = $script:FixedTags
        }
        results        = $Results
    }
    
    return $report | ConvertTo-Json -Depth 10
}

function New-CsvReport {
    param([array]$Results)
    
    $csvData = @()
    
    foreach ($result in $Results) {
        if (-not $result.HasTags) { continue }
        
        $csvData += [PSCustomObject]@{
            FilePath       = $result.FilePath -replace [regex]::Escape((Get-Location).Path), '.'
            ValidTagCount  = $result.ValidTags.Count
            InvalidTagCount = $result.InvalidTags.Count
            ValidTags      = $result.ValidTags -join '; '
            InvalidTags    = $result.InvalidTags -join '; '
            IssueCount     = $result.Issues.Count
        }
    }
    
    return $csvData | ConvertTo-Csv -NoTypeInformation
}

function Export-Report {
    param(
        [array]$Results,
        [string]$Path,
        [string]$Format
    )
    
    try {
        $reportDir = Split-Path -Parent $Path
        if ($reportDir -and -not (Test-Path $reportDir)) {
            New-Item -Path $reportDir -ItemType Directory -Force | Out-Null
        }
        
        $reportContent = switch ($Format) {
            'HTML' { New-HtmlReport -Results $Results }
            'JSON' { New-JsonReport -Results $Results }
            'CSV'  { New-CsvReport -Results $Results }
        }
        
        Set-Content -Path $Path -Value $reportContent -NoNewline
        Write-Log "Report generated: $Path" -Level SUCCESS
    }
    catch {
        Write-Log "Failed to generate report: $_" -Level ERROR
    }
}

#endregion

#region File Processing

function Process-File {
    param([string]$FilePath)
    
    try {
        $script:TotalFiles++
        
        Write-Log "Validating: $FilePath" -Level DEBUG
        
        $result = Validate-FileTags -FilePath $FilePath -ValidTags $script:ValidTags -Taxonomy $script:Taxonomy
        
        if (-not $result) {
            return
        }
        
        $script:ValidationResults += $result
        
        if ($result.InvalidTags.Count -gt 0 -or $result.Issues.Count -gt 0) {
            $script:FilesWithIssues++
            $script:InvalidTags += $result.InvalidTags.Count
            
            Write-Log "Found $($result.InvalidTags.Count) invalid tags in: $FilePath" -Level WARN
            
            if ($FixInvalidTags) {
                Fix-FileTags -ValidationResult $result
            }
        }
    }
    catch {
        Write-Log "Error processing file: $FilePath - $_" -Level ERROR
    }
}

function Process-Directory {
    param([string]$DirectoryPath)
    
    Write-Log "Scanning directory: $DirectoryPath" -Level INFO
    
    $files = Get-ChildItem -Path $DirectoryPath -Filter "*.md" -Recurse -File
    $totalFiles = $files.Count
    
    Write-Log "Found $totalFiles markdown files" -Level INFO
    
    $currentFile = 0
    foreach ($file in $files) {
        $currentFile++
        $percentComplete = [math]::Round(($currentFile / $totalFiles) * 100, 2)
        
        Write-Progress -Activity "Validating tags" `
            -Status "File $currentFile of $totalFiles ($percentComplete%)" `
            -PercentComplete $percentComplete `
            -CurrentOperation $file.Name
        
        Process-File -FilePath $file.FullName
    }
    
    Write-Progress -Activity "Validating tags" -Completed
}

#endregion

#region Main Execution

try {
    Write-Host "`n=== Tag Validation Tool ===" -ForegroundColor Cyan
    
    Initialize-Logging -LogFile $LogPath
    Write-Log "Starting tag validation" -Level INFO
    
    # Load taxonomy
    $script:Taxonomy = Import-Taxonomy -Path $TaxonomyPath
    $script:ValidTags = Get-AllValidTags -Taxonomy $script:Taxonomy
    
    Write-Log "Loaded $($script:ValidTags.Count) valid tags" -Level INFO
    
    # Process
    $item = Get-Item -Path $Path
    
    if ($item.PSIsContainer) {
        Process-Directory -DirectoryPath $Path
    }
    else {
        Process-File -FilePath $Path
    }
    
    # Generate report
    Export-Report -Results $script:ValidationResults -Path $ReportPath -Format $OutputFormat
    
    # Summary
    $duration = (Get-Date) - $script:StartTime
    
    $summary = @"

$('=' * 80)
VALIDATION SUMMARY
$('=' * 80)
Total Files:      $script:TotalFiles
Files with Issues: $script:FilesWithIssues
Invalid Tags:     $script:InvalidTags
Fixed Tags:       $script:FixedTags
Duration:         $($duration.ToString('mm\:ss'))
Report:           $ReportPath
$('=' * 80)

"@
    
    Write-Host $summary
    Write-Log $summary -Level INFO
    Write-Log "Tag validation completed" -Level SUCCESS
    
    exit 0
}
catch {
    Write-Log "Critical error: $_" -Level ERROR
    Write-Log $_.ScriptStackTrace -Level ERROR
    exit 1
}

#endregion
