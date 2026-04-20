<#
.SYNOPSIS
    Converts markdown-style links to wiki-style links in documentation files.

.DESCRIPTION
    Converts standard markdown links [text](url) to wiki-style links [[url|text]].
    Includes backup, rollback, validation, and comprehensive error handling.

.PARAMETER Path
    Path to file or directory to process.

.PARAMETER DryRun
    Preview changes without modifying files.

.PARAMETER BackupDir
    Directory for backups. Default: .\automation-backups

.PARAMETER LogPath
    Path to log file. Default: .\automation-logs\convert-links.log

.PARAMETER ValidateLinks
    Validate that linked files exist before conversion.

.PARAMETER ConversionMode
    Conversion mode: 'ToWiki' or 'ToMarkdown'. Default: ToWiki

.PARAMETER Rollback
    Rollback files from backup.

.PARAMETER Interactive
    Prompt for confirmation for each file.

.EXAMPLE
    .\convert-links.ps1 -Path ".\docs" -DryRun
    Preview link conversions without making changes.

.EXAMPLE
    .\convert-links.ps1 -Path ".\wiki" -ValidateLinks -BackupDir ".\backups"
    Convert links with validation and custom backup location.

.EXAMPLE
    .\convert-links.ps1 -Rollback -BackupDir ".\backups"
    Restore files from backup.

.NOTES
    Author: AGENT-020 (Automation Scripts Architect)
    Version: 1.0.0
    Production-ready critical infrastructure.
#>

[CmdletBinding(SupportsShouldProcess, DefaultParameterSetName = 'Convert')]
param(
    [Parameter(Mandatory = $true, Position = 0, ParameterSetName = 'Convert')]
    [ValidateScript({ Test-Path $_ })]
    [string]$Path,

    [Parameter(ParameterSetName = 'Convert')]
    [switch]$DryRun,

    [Parameter()]
    [string]$BackupDir = ".\automation-backups",

    [Parameter()]
    [string]$LogPath = ".\automation-logs\convert-links.log",

    [Parameter(ParameterSetName = 'Convert')]
    [switch]$ValidateLinks,

    [Parameter(ParameterSetName = 'Convert')]
    [ValidateSet('ToWiki', 'ToMarkdown')]
    [string]$ConversionMode = 'ToWiki',

    [Parameter(Mandatory = $true, ParameterSetName = 'Rollback')]
    [switch]$Rollback,

    [Parameter(ParameterSetName = 'Convert')]
    [switch]$Interactive,

    [Parameter(ParameterSetName = 'Convert')]
    [string[]]$ExcludePatterns = @('*.tmp', '*.bak', '*~'),

    [Parameter(ParameterSetName = 'Convert')]
    [switch]$PreserveFragments,

    [Parameter(ParameterSetName = 'Convert')]
    [switch]$SkipExternalLinks,

    [Parameter()]
    [int]$BackupRetentionDays = 30
)

$ErrorActionPreference = 'Stop'
$script:ProcessedFiles = 0
$script:SkippedFiles = 0
$script:ErrorFiles = 0
$script:TotalConversions = 0
$script:FailedConversions = 0
$script:StartTime = Get-Date

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
Link Conversion Log - Started: $timestamp
Mode: $ConversionMode
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

#region Backup Functions

function Initialize-BackupDirectory {
    param([string]$BackupPath)
    
    try {
        if (-not (Test-Path $BackupPath)) {
            New-Item -Path $BackupPath -ItemType Directory -Force | Out-Null
            Write-Log "Created backup directory: $BackupPath" -Level INFO
        }
        
        # Clean old backups
        $cutoffDate = (Get-Date).AddDays(-$BackupRetentionDays)
        Get-ChildItem -Path $BackupPath -Recurse -File |
            Where-Object { $_.LastWriteTime -lt $cutoffDate } |
            Remove-Item -Force
        
        return $true
    }
    catch {
        Write-Log "Failed to initialize backup directory: $_" -Level ERROR
        return $false
    }
}

function New-FileBackup {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        
        [Parameter(Mandatory)]
        [string]$BackupPath
    )
    
    try {
        $file = Get-Item -Path $FilePath
        $relativePath = $file.FullName -replace [regex]::Escape((Get-Location).Path), ''
        $relativePath = $relativePath.TrimStart('\', '/')
        
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFileName = "$($file.BaseName)_$timestamp$($file.Extension)"
        $backupSubDir = Split-Path -Parent $relativePath
        $backupFullDir = Join-Path $BackupPath $backupSubDir
        
        if (-not (Test-Path $backupFullDir)) {
            New-Item -Path $backupFullDir -ItemType Directory -Force | Out-Null
        }
        
        $backupFilePath = Join-Path $backupFullDir $backupFileName
        Copy-Item -Path $FilePath -Destination $backupFilePath -Force
        
        Write-Log "Created backup: $backupFilePath" -Level DEBUG
        return $backupFilePath
    }
    catch {
        Write-Log "Failed to create backup for: $FilePath - $_" -Level ERROR
        throw
    }
}

function Restore-FromBackup {
    param([string]$BackupPath)
    
    try {
        Write-Log "Starting rollback from: $BackupPath" -Level INFO
        
        if (-not (Test-Path $BackupPath)) {
            Write-Log "Backup directory not found: $BackupPath" -Level ERROR
            return $false
        }
        
        $backupFiles = Get-ChildItem -Path $BackupPath -Recurse -File
        $restored = 0
        
        foreach ($backupFile in $backupFiles) {
            try {
                # Extract original filename (remove timestamp)
                $originalName = $backupFile.Name -replace '_\d{8}_\d{6}', ''
                $relativePath = $backupFile.DirectoryName -replace [regex]::Escape($BackupPath), ''
                $relativePath = $relativePath.TrimStart('\', '/')
                
                $originalPath = Join-Path (Get-Location) $relativePath
                $originalPath = Join-Path $originalPath $originalName
                
                if (Test-Path $originalPath) {
                    Copy-Item -Path $backupFile.FullName -Destination $originalPath -Force
                    Write-Log "Restored: $originalPath" -Level SUCCESS
                    $restored++
                }
            }
            catch {
                Write-Log "Failed to restore: $backupFile - $_" -Level ERROR
            }
        }
        
        Write-Log "Restored $restored files from backup" -Level SUCCESS
        return $true
    }
    catch {
        Write-Log "Rollback failed: $_" -Level ERROR
        return $false
    }
}

#endregion

#region Link Conversion Functions

function ConvertTo-WikiLink {
    param(
        [Parameter(Mandatory)]
        [string]$MarkdownLink
    )
    
    try {
        # Match: [text](url) or [text](url#fragment)
        if ($MarkdownLink -match '^\[([^\]]+)\]\(([^)]+)\)$') {
            $text = $matches[1]
            $url = $matches[2]
            
            # Handle fragments
            $fragment = ''
            if ($url -match '^([^#]+)(#.+)$') {
                $url = $matches[1]
                $fragment = $matches[2]
            }
            
            # Skip external links if requested
            if ($SkipExternalLinks -and $url -match '^https?://') {
                return @{
                    Success  = $false
                    Reason   = 'External link'
                    Original = $MarkdownLink
                }
            }
            
            # Convert to wiki format
            if ($PreserveFragments -and $fragment) {
                $wikiLink = "[[$url$fragment|$text]]"
            }
            else {
                $wikiLink = "[[$url|$text]]"
            }
            
            return @{
                Success   = $true
                Original  = $MarkdownLink
                Converted = $wikiLink
                Text      = $text
                Url       = $url
                Fragment  = $fragment
            }
        }
        
        return @{
            Success  = $false
            Reason   = 'Invalid format'
            Original = $MarkdownLink
        }
    }
    catch {
        Write-Log "Error converting link: $MarkdownLink - $_" -Level ERROR
        return @{
            Success  = $false
            Reason   = $_.Exception.Message
            Original = $MarkdownLink
        }
    }
}

function ConvertTo-MarkdownLink {
    param(
        [Parameter(Mandatory)]
        [string]$WikiLink
    )
    
    try {
        # Match: [[url|text]] or [[url#fragment|text]]
        if ($WikiLink -match '^\[\[([^\]|]+)(?:\|([^\]]+))?\]\]$') {
            $url = $matches[1]
            $text = if ($matches[2]) { $matches[2] } else { $url }
            
            $markdownLink = "[$text]($url)"
            
            return @{
                Success   = $true
                Original  = $WikiLink
                Converted = $markdownLink
                Text      = $text
                Url       = $url
            }
        }
        
        return @{
            Success  = $false
            Reason   = 'Invalid format'
            Original = $WikiLink
        }
    }
    catch {
        Write-Log "Error converting link: $WikiLink - $_" -Level ERROR
        return @{
            Success  = $false
            Reason   = $_.Exception.Message
            Original = $WikiLink
        }
    }
}

function Test-LinkTarget {
    param(
        [Parameter(Mandatory)]
        [string]$Link,
        
        [Parameter(Mandatory)]
        [string]$BaseDir
    )
    
    try {
        # Skip external links
        if ($Link -match '^https?://') {
            return @{
                Exists = $true
                Type   = 'External'
            }
        }
        
        # Remove fragment
        $cleanLink = $Link -replace '#.*$', ''
        
        # Resolve path
        $linkPath = Join-Path $BaseDir $cleanLink
        
        if (Test-Path $linkPath) {
            return @{
                Exists = $true
                Type   = 'Local'
                Path   = $linkPath
            }
        }
        
        return @{
            Exists = $false
            Type   = 'Local'
            Path   = $linkPath
        }
    }
    catch {
        return @{
            Exists = $false
            Type   = 'Unknown'
            Error  = $_.Exception.Message
        }
    }
}

#endregion

#region File Processing

function Convert-LinksInFile {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath,
        
        [Parameter(Mandatory)]
        [string]$Mode
    )
    
    try {
        $content = Get-Content -Path $FilePath -Raw
        $originalContent = $content
        $conversions = 0
        $failures = 0
        
        $baseDir = Split-Path -Parent $FilePath
        
        if ($Mode -eq 'ToWiki') {
            # Find all markdown links: [text](url)
            $pattern = '\[([^\]]+)\]\(([^)]+)\)'
            $matches = [regex]::Matches($content, $pattern)
            
            Write-Log "Found $($matches.Count) markdown links in: $FilePath" -Level DEBUG
            
            foreach ($match in $matches) {
                $result = ConvertTo-WikiLink -MarkdownLink $match.Value
                
                if ($result.Success) {
                    # Validate link if requested
                    if ($ValidateLinks) {
                        $validation = Test-LinkTarget -Link $result.Url -BaseDir $baseDir
                        if (-not $validation.Exists) {
                            Write-Log "Broken link detected: $($result.Url) in $FilePath" -Level WARN
                            $failures++
                            continue
                        }
                    }
                    
                    $content = $content.Replace($result.Original, $result.Converted)
                    $conversions++
                    Write-Log "Converted: $($result.Original) -> $($result.Converted)" -Level DEBUG
                }
                else {
                    Write-Log "Failed to convert: $($result.Original) - $($result.Reason)" -Level WARN
                    $failures++
                }
            }
        }
        elseif ($Mode -eq 'ToMarkdown') {
            # Find all wiki links: [[url|text]]
            $pattern = '\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
            $matches = [regex]::Matches($content, $pattern)
            
            Write-Log "Found $($matches.Count) wiki links in: $FilePath" -Level DEBUG
            
            foreach ($match in $matches) {
                $result = ConvertTo-MarkdownLink -WikiLink $match.Value
                
                if ($result.Success) {
                    # Validate link if requested
                    if ($ValidateLinks) {
                        $validation = Test-LinkTarget -Link $result.Url -BaseDir $baseDir
                        if (-not $validation.Exists) {
                            Write-Log "Broken link detected: $($result.Url) in $FilePath" -Level WARN
                            $failures++
                            continue
                        }
                    }
                    
                    $content = $content.Replace($result.Original, $result.Converted)
                    $conversions++
                    Write-Log "Converted: $($result.Original) -> $($result.Converted)" -Level DEBUG
                }
                else {
                    Write-Log "Failed to convert: $($result.Original) - $($result.Reason)" -Level WARN
                    $failures++
                }
            }
        }
        
        return @{
            Modified     = $content -ne $originalContent
            NewContent   = $content
            Conversions  = $conversions
            Failures     = $failures
        }
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
        
        # Check exclusion patterns
        $file = Get-Item -Path $FilePath
        foreach ($pattern in $ExcludePatterns) {
            if ($file.Name -like $pattern) {
                Write-Log "Excluded by pattern '$pattern': $FilePath" -Level DEBUG
                $script:SkippedFiles++
                return
            }
        }
        
        # Convert links
        $result = Convert-LinksInFile -FilePath $FilePath -Mode $ConversionMode
        
        if (-not $result.Modified) {
            Write-Log "No changes needed: $FilePath" -Level DEBUG
            $script:SkippedFiles++
            return
        }
        
        Write-Log "Found $($result.Conversions) conversions, $($result.Failures) failures" -Level INFO
        
        if ($DryRun) {
            Write-Log "[DRY RUN] Would convert $($result.Conversions) links in: $FilePath" -Level INFO
            $script:TotalConversions += $result.Conversions
            $script:FailedConversions += $result.Failures
            return
        }
        
        if ($Interactive) {
            Write-Host "`nFile: $FilePath" -ForegroundColor Cyan
            Write-Host "Conversions: $($result.Conversions), Failures: $($result.Failures)" -ForegroundColor Yellow
            $response = Read-Host "Apply changes? (y/n)"
            if ($response -notmatch '^y(es)?$') {
                Write-Log "Skipped by user: $FilePath" -Level INFO
                $script:SkippedFiles++
                return
            }
        }
        
        # Create backup
        $backup = New-FileBackup -FilePath $FilePath -BackupPath $BackupDir
        
        # Write changes
        Set-Content -Path $FilePath -Value $result.NewContent -NoNewline
        Write-Log "Converted $($result.Conversions) links in: $FilePath" -Level SUCCESS
        
        $script:ProcessedFiles++
        $script:TotalConversions += $result.Conversions
        $script:FailedConversions += $result.Failures
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
        
        Write-Progress -Activity "Converting links" `
            -Status "File $currentFile of $totalFiles ($percentComplete%)" `
            -PercentComplete $percentComplete `
            -CurrentOperation $file.Name
        
        Process-File -FilePath $file.FullName
    }
    
    Write-Progress -Activity "Converting links" -Completed
}

#endregion

#region Summary

function Show-Summary {
    $duration = (Get-Date) - $script:StartTime
    
    $summary = @"

$('=' * 80)
CONVERSION SUMMARY
$('=' * 80)
Mode:             $ConversionMode
Total Files:      $($script:ProcessedFiles + $script:SkippedFiles + $script:ErrorFiles)
Processed:        $script:ProcessedFiles
Skipped:          $script:SkippedFiles
Errors:           $script:ErrorFiles
Conversions:      $script:TotalConversions
Failed:           $script:FailedConversions
Duration:         $($duration.ToString('mm\:ss'))
Run Mode:         $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })
Backup Dir:       $BackupDir
$('=' * 80)

"@
    
    Write-Host $summary
    Write-Log $summary -Level INFO
}

#endregion

#region Main Execution

try {
    Write-Host "`n=== Link Conversion Tool ===" -ForegroundColor Cyan
    
    if ($Rollback) {
        Write-Host "Mode: ROLLBACK`n" -ForegroundColor Yellow
        Initialize-Logging -LogFile $LogPath
        
        $success = Restore-FromBackup -BackupPath $BackupDir
        
        if ($success) {
            Write-Log "Rollback completed successfully" -Level SUCCESS
            exit 0
        }
        else {
            Write-Log "Rollback failed" -Level ERROR
            exit 1
        }
    }
    
    Write-Host "Mode: $ConversionMode $(if ($DryRun) { '(DRY RUN)' })`n" -ForegroundColor Yellow
    
    # Initialize
    Initialize-Logging -LogFile $LogPath
    Write-Log "Starting link conversion" -Level INFO
    Write-Log "Target: $Path" -Level INFO
    Write-Log "Conversion mode: $ConversionMode" -Level INFO
    
    # Initialize backup
    if (-not $DryRun) {
        $backupReady = Initialize-BackupDirectory -BackupPath $BackupDir
        if (-not $backupReady) {
            throw "Failed to initialize backup directory"
        }
    }
    
    # Process
    $item = Get-Item -Path $Path
    
    if ($item.PSIsContainer) {
        Process-Directory -DirectoryPath $Path
    }
    else {
        Process-File -FilePath $Path
    }
    
    # Show summary
    Show-Summary
    
    Write-Log "Link conversion completed" -Level SUCCESS
    
    exit 0
}
catch {
    Write-Log "Critical error: $_" -Level ERROR
    Write-Log $_.ScriptStackTrace -Level ERROR
    Show-Summary
    exit 1
}

#endregion
