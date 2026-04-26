<#
.SYNOPSIS
    Orchestrates bulk automation operations across documentation.

.DESCRIPTION
    Orchestrator for batch processing that pipelines multiple automation scripts,
    tracks progress, handles errors, supports recovery, and enables parallel execution.

.PARAMETER Operation
    Operation to perform: AddMetadata, ConvertLinks, ValidateTags, or Pipeline.

.PARAMETER Path
    Path to file or directory to process.

.PARAMETER Pipeline
    Array of operations to execute in sequence (e.g., @('ValidateTags', 'AddMetadata', 'ConvertLinks')).

.PARAMETER Parallel
    Enable parallel execution for independent operations.

.PARAMETER MaxParallelJobs
    Maximum number of parallel jobs. Default: 4

.PARAMETER DryRun
    Preview operations without making changes.

.PARAMETER LogPath
    Path to orchestrator log file. Default: .\automation-logs\batch-process.log

.PARAMETER StopOnError
    Stop processing if any operation fails.

.PARAMETER SaveCheckpoint
    Save progress checkpoints for recovery.

.PARAMETER ResumeFromCheckpoint
    Resume from last checkpoint.

.EXAMPLE
    .\batch-process.ps1 -Operation AddMetadata -Path ".\docs" -DryRun
    Preview metadata generation for all docs.

.EXAMPLE
    .\batch-process.ps1 -Pipeline @('ValidateTags', 'AddMetadata', 'ConvertLinks') -Path ".\wiki"
    Execute validation, metadata generation, and link conversion in sequence.

.EXAMPLE
    .\batch-process.ps1 -Operation AddMetadata -Path ".\docs" -Parallel -MaxParallelJobs 8
    Process metadata in parallel with 8 concurrent jobs.

.NOTES
    Author: AGENT-020 (Automation Scripts Architect)
    Version: 1.0.0
    Production-ready critical infrastructure.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(ParameterSetName = 'Single')]
    [ValidateSet('AddMetadata', 'ConvertLinks', 'ValidateTags')]
    [string]$Operation,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path $_ })]
    [string]$Path,

    [Parameter(ParameterSetName = 'Pipeline')]
    [ValidateSet('AddMetadata', 'ConvertLinks', 'ValidateTags')]
    [string[]]$Pipeline,

    [Parameter()]
    [switch]$Parallel,

    [Parameter()]
    [ValidateRange(1, 16)]
    [int]$MaxParallelJobs = 4,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [string]$LogPath = ".\automation-logs\batch-process.log",

    [Parameter()]
    [switch]$StopOnError,

    [Parameter()]
    [switch]$SaveCheckpoint,

    [Parameter()]
    [switch]$ResumeFromCheckpoint,

    [Parameter()]
    [string]$CheckpointPath = ".\automation-logs\checkpoint.json",

    [Parameter()]
    [hashtable]$ScriptParameters = @{},

    [Parameter()]
    [int]$RetryAttempts = 3,

    [Parameter()]
    [int]$RetryDelaySeconds = 5,

    [Parameter()]
    [switch]$GenerateReport,

    [Parameter()]
    [string]$ReportPath = ".\automation-reports\batch-report.html"
)

$ErrorActionPreference = 'Stop'
$script:TotalOperations = 0
$script:CompletedOperations = 0
$script:FailedOperations = 0
$script:StartTime = Get-Date
$script:OperationResults = @()

#region Configuration

$script:ScriptMapping = @{
    AddMetadata  = '.\scripts\automation\add-metadata.ps1'
    ConvertLinks = '.\scripts\automation\convert-links.ps1'
    ValidateTags = '.\scripts\automation\validate-tags.ps1'
}

$script:DefaultParameters = @{
    AddMetadata = @{
        LogPath = ".\automation-logs\add-metadata-batch.log"
    }
    ConvertLinks = @{
        LogPath       = ".\automation-logs\convert-links-batch.log"
        BackupDir     = ".\automation-backups\convert-links"
        ValidateLinks = $true
    }
    ValidateTags = @{
        LogPath    = ".\automation-logs\validate-tags-batch.log"
        ReportPath = ".\automation-reports\tag-validation-batch.html"
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
Batch Processing Log - Started: $timestamp
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

#region Checkpoint Functions

function Save-Checkpoint {
    param(
        [Parameter(Mandatory)]
        [hashtable]$State
    )
    
    try {
        $checkpointDir = Split-Path -Parent $CheckpointPath
        if ($checkpointDir -and -not (Test-Path $checkpointDir)) {
            New-Item -Path $checkpointDir -ItemType Directory -Force | Out-Null
        }
        
        $checkpoint = @{
            Timestamp          = (Get-Date).ToString('o')
            State              = $State
            TotalOperations    = $script:TotalOperations
            CompletedOperations = $script:CompletedOperations
            FailedOperations   = $script:FailedOperations
        }
        
        $checkpoint | ConvertTo-Json -Depth 10 | Set-Content -Path $CheckpointPath
        Write-Log "Checkpoint saved: $CheckpointPath" -Level DEBUG
    }
    catch {
        Write-Log "Failed to save checkpoint: $_" -Level WARN
    }
}

function Load-Checkpoint {
    param([string]$Path)
    
    try {
        if (-not (Test-Path $Path)) {
            Write-Log "No checkpoint found at: $Path" -Level WARN
            return $null
        }
        
        $checkpoint = Get-Content -Path $Path -Raw | ConvertFrom-Json
        Write-Log "Loaded checkpoint from: $Path" -Level INFO
        Write-Log "Checkpoint timestamp: $($checkpoint.Timestamp)" -Level INFO
        
        return $checkpoint
    }
    catch {
        Write-Log "Failed to load checkpoint: $_" -Level ERROR
        return $null
    }
}

#endregion

#region Operation Execution

function Invoke-OperationWithRetry {
    param(
        [Parameter(Mandatory)]
        [string]$OperationName,
        
        [Parameter(Mandatory)]
        [string]$ScriptPath,
        
        [Parameter(Mandatory)]
        [string]$TargetPath,
        
        [hashtable]$Parameters = @{},
        
        [int]$MaxRetries = 3
    )
    
    $attempt = 0
    $success = $false
    $lastError = $null
    
    while ($attempt -lt $MaxRetries -and -not $success) {
        $attempt++
        
        try {
            Write-Log "Executing $OperationName (attempt $attempt/$MaxRetries)" -Level INFO
            
            # Build parameter hashtable
            $scriptParams = @{
                Path = $TargetPath
            }
            
            # Merge default and custom parameters
            $defaultParams = $script:DefaultParameters[$OperationName]
            if ($defaultParams) {
                foreach ($key in $defaultParams.Keys) {
                    $scriptParams[$key] = $defaultParams[$key]
                }
            }
            
            if ($Parameters) {
                foreach ($key in $Parameters.Keys) {
                    $scriptParams[$key] = $Parameters[$key]
                }
            }
            
            if ($DryRun) {
                $scriptParams['DryRun'] = $true
            }
            
            # Execute script
            $startTime = Get-Date
            $output = & $ScriptPath @scriptParams 2>&1
            $endTime = Get-Date
            $duration = $endTime - $startTime
            
            # Check exit code
            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null) {
                Write-Log "$OperationName completed successfully (${duration}s)" -Level SUCCESS
                $success = $true
                
                return @{
                    Success   = $true
                    Operation = $OperationName
                    Duration  = $duration
                    Output    = $output
                    Attempts  = $attempt
                }
            }
            else {
                throw "Script exited with code: $LASTEXITCODE"
            }
        }
        catch {
            $lastError = $_
            Write-Log "$OperationName failed (attempt $attempt): $_" -Level ERROR
            
            if ($attempt -lt $MaxRetries) {
                Write-Log "Retrying in $RetryDelaySeconds seconds..." -Level WARN
                Start-Sleep -Seconds $RetryDelaySeconds
            }
        }
    }
    
    Write-Log "$OperationName failed after $MaxRetries attempts" -Level ERROR
    
    return @{
        Success   = $false
        Operation = $OperationName
        Error     = $lastError
        Attempts  = $attempt
    }
}

function Invoke-SingleOperation {
    param(
        [Parameter(Mandatory)]
        [string]$OperationName,
        
        [Parameter(Mandatory)]
        [string]$TargetPath,
        
        [hashtable]$Parameters = @{}
    )
    
    try {
        $scriptPath = $script:ScriptMapping[$OperationName]
        
        if (-not (Test-Path $scriptPath)) {
            throw "Script not found: $scriptPath"
        }
        
        Write-Log "Starting operation: $OperationName on $TargetPath" -Level INFO
        
        $result = Invoke-OperationWithRetry `
            -OperationName $OperationName `
            -ScriptPath $scriptPath `
            -TargetPath $TargetPath `
            -Parameters $Parameters `
            -MaxRetries $RetryAttempts
        
        $script:OperationResults += $result
        
        if ($result.Success) {
            $script:CompletedOperations++
        }
        else {
            $script:FailedOperations++
            
            if ($StopOnError) {
                throw "Operation failed: $OperationName"
            }
        }
        
        return $result
    }
    catch {
        Write-Log "Critical error in operation: $OperationName - $_" -Level ERROR
        $script:FailedOperations++
        throw
    }
}

function Invoke-PipelineOperations {
    param(
        [Parameter(Mandatory)]
        [string[]]$Operations,
        
        [Parameter(Mandatory)]
        [string]$TargetPath
    )
    
    Write-Log "Starting pipeline with $($Operations.Count) operations" -Level INFO
    
    $pipelineResults = @()
    
    for ($i = 0; $i -lt $Operations.Count; $i++) {
        $operation = $Operations[$i]
        $stepNumber = $i + 1
        
        Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
        Write-Host "PIPELINE STEP $stepNumber/$($Operations.Count): $operation" -ForegroundColor Cyan
        Write-Host "$('=' * 80)`n" -ForegroundColor Cyan
        
        try {
            $result = Invoke-SingleOperation -OperationName $operation -TargetPath $TargetPath
            $pipelineResults += $result
            
            if ($SaveCheckpoint) {
                Save-Checkpoint -State @{
                    Pipeline         = $Operations
                    CurrentStep      = $stepNumber
                    CompletedSteps   = $Operations[0..($i)]
                    RemainingSteps   = $Operations[($i + 1)..($Operations.Count - 1)]
                }
            }
            
            if (-not $result.Success -and $StopOnError) {
                Write-Log "Pipeline stopped due to error in: $operation" -Level ERROR
                break
            }
        }
        catch {
            Write-Log "Pipeline step failed: $operation - $_" -Level ERROR
            
            if ($StopOnError) {
                throw
            }
        }
    }
    
    return $pipelineResults
}

function Invoke-ParallelOperations {
    param(
        [Parameter(Mandatory)]
        [string]$OperationName,
        
        [Parameter(Mandatory)]
        [string]$DirectoryPath
    )
    
    Write-Log "Starting parallel execution: $OperationName" -Level INFO
    Write-Log "Max parallel jobs: $MaxParallelJobs" -Level INFO
    
    $files = Get-ChildItem -Path $DirectoryPath -Filter "*.md" -Recurse -File
    $totalFiles = $files.Count
    
    Write-Log "Processing $totalFiles files in parallel" -Level INFO
    
    $jobs = @()
    $results = @()
    $currentFile = 0
    
    foreach ($file in $files) {
        $currentFile++
        
        # Wait if max jobs reached
        while ($jobs.Count -ge $MaxParallelJobs) {
            $completedJobs = $jobs | Where-Object { $_.State -eq 'Completed' }
            
            foreach ($job in $completedJobs) {
                $jobResult = Receive-Job -Job $job
                $results += $jobResult
                Remove-Job -Job $job
                $jobs = $jobs | Where-Object { $_.Id -ne $job.Id }
            }
            
            Start-Sleep -Milliseconds 100
        }
        
        # Start new job
        $scriptPath = $script:ScriptMapping[$OperationName]
        $params = @{
            Path = $file.FullName
        }
        
        if ($DryRun) {
            $params['DryRun'] = $true
        }
        
        $job = Start-Job -ScriptBlock {
            param($Script, $Params)
            & $Script @Params
        } -ArgumentList $scriptPath, $params
        
        $jobs += $job
        
        $percentComplete = [math]::Round(($currentFile / $totalFiles) * 100, 2)
        Write-Progress -Activity "Parallel processing" `
            -Status "$currentFile of $totalFiles files ($percentComplete%)" `
            -PercentComplete $percentComplete
    }
    
    # Wait for remaining jobs
    Write-Log "Waiting for remaining jobs to complete..." -Level INFO
    $jobs | Wait-Job | ForEach-Object {
        $results += Receive-Job -Job $_
        Remove-Job -Job $_
    }
    
    Write-Progress -Activity "Parallel processing" -Completed
    
    Write-Log "Parallel execution completed" -Level SUCCESS
    
    return $results
}

#endregion

#region Report Generation

function New-BatchReport {
    param([array]$Results)
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Batch Processing Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .summary { background: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary-item { display: inline-block; margin-right: 30px; }
        .summary-label { color: #666; font-size: 14px; }
        .summary-value { font-size: 28px; font-weight: bold; color: #2196F3; }
        .success { color: green; }
        .failed { color: red; }
        table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #2196F3; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .timeline { background: white; padding: 20px; border-radius: 5px; }
        .timeline-item { padding: 10px; margin: 5px 0; border-left: 4px solid #2196F3; }
    </style>
</head>
<body>
    <h1>Batch Processing Report</h1>
    
    <div class="summary">
        <div class="summary-item">
            <div class="summary-label">Total Operations</div>
            <div class="summary-value">$script:TotalOperations</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Completed</div>
            <div class="summary-value success">$script:CompletedOperations</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Failed</div>
            <div class="summary-value failed">$script:FailedOperations</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">Duration</div>
            <div class="summary-value">$((Get-Date) - $script:StartTime | Select-Object -ExpandProperty TotalMinutes | ForEach-Object { [math]::Round($_, 2) }) min</div>
        </div>
    </div>
    
    <h2>Operation Results</h2>
    <table>
        <tr>
            <th>Operation</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Attempts</th>
        </tr>
"@
    
    foreach ($result in $Results) {
        $status = if ($result.Success) { "<span class='success'>✓ Success</span>" } else { "<span class='failed'>✗ Failed</span>" }
        $duration = if ($result.Duration) { "$([math]::Round($result.Duration.TotalSeconds, 2))s" } else { "N/A" }
        
        $html += @"
        <tr>
            <td>$($result.Operation)</td>
            <td>$status</td>
            <td>$duration</td>
            <td>$($result.Attempts)</td>
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

function Export-BatchReport {
    param([array]$Results)
    
    try {
        $reportDir = Split-Path -Parent $ReportPath
        if ($reportDir -and -not (Test-Path $reportDir)) {
            New-Item -Path $reportDir -ItemType Directory -Force | Out-Null
        }
        
        $report = New-BatchReport -Results $Results
        Set-Content -Path $ReportPath -Value $report -NoNewline
        
        Write-Log "Report generated: $ReportPath" -Level SUCCESS
    }
    catch {
        Write-Log "Failed to generate report: $_" -Level ERROR
    }
}

#endregion

#region Summary

function Show-Summary {
    $duration = (Get-Date) - $script:StartTime
    
    $summary = @"

$('=' * 80)
BATCH PROCESSING SUMMARY
$('=' * 80)
Total Operations: $script:TotalOperations
Completed:        $script:CompletedOperations
Failed:           $script:FailedOperations
Success Rate:     $(if ($script:TotalOperations -gt 0) { [math]::Round(($script:CompletedOperations / $script:TotalOperations) * 100, 2) } else { 0 })%
Duration:         $($duration.ToString('hh\:mm\:ss'))
Mode:             $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })
$('=' * 80)

"@
    
    Write-Host $summary
    Write-Log $summary -Level INFO
}

#endregion

#region Main Execution

try {
    Write-Host "`n=== Batch Processing Tool ===" -ForegroundColor Cyan
    Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'LIVE' })`n" -ForegroundColor Yellow
    
    Initialize-Logging -LogFile $LogPath
    Write-Log "Starting batch processing" -Level INFO
    
    # Resume from checkpoint if requested
    if ($ResumeFromCheckpoint) {
        $checkpoint = Load-Checkpoint -Path $CheckpointPath
        
        if ($checkpoint -and $checkpoint.State.Pipeline) {
            Write-Log "Resuming from checkpoint" -Level INFO
            $Pipeline = $checkpoint.State.RemainingSteps
            
            if ($Pipeline.Count -eq 0) {
                Write-Log "All operations already completed" -Level SUCCESS
                exit 0
            }
        }
    }
    
    # Determine operation mode
    if ($Pipeline) {
        $script:TotalOperations = $Pipeline.Count
        Write-Log "Pipeline mode: $($Pipeline -join ' -> ')" -Level INFO
        
        $results = Invoke-PipelineOperations -Operations $Pipeline -TargetPath $Path
    }
    elseif ($Operation) {
        $script:TotalOperations = 1
        Write-Log "Single operation mode: $Operation" -Level INFO
        
        if ($Parallel -and (Get-Item $Path).PSIsContainer) {
            $results = Invoke-ParallelOperations -OperationName $Operation -DirectoryPath $Path
        }
        else {
            $results = @(Invoke-SingleOperation -OperationName $Operation -TargetPath $Path)
        }
    }
    else {
        throw "No operation specified. Use -Operation or -Pipeline parameter."
    }
    
    # Generate report if requested
    if ($GenerateReport) {
        Export-BatchReport -Results $script:OperationResults
    }
    
    # Show summary
    Show-Summary
    
    Write-Log "Batch processing completed" -Level SUCCESS
    
    # Clean up checkpoint if successful
    if ($SaveCheckpoint -and $script:FailedOperations -eq 0) {
        Remove-Item -Path $CheckpointPath -Force -ErrorAction SilentlyContinue
        Write-Log "Checkpoint removed (all operations successful)" -Level DEBUG
    }
    
    exit 0
}
catch {
    Write-Log "Critical error: $_" -Level ERROR
    Write-Log $_.ScriptStackTrace -Level ERROR
    Show-Summary
    exit 1
}

#endregion
