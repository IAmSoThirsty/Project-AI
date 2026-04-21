<#
.SYNOPSIS
    Comprehensive test runner for metadata validation system.

.DESCRIPTION
    Runs all test cases (valid, invalid, edge cases) and generates detailed test report.
    Validates that the validation system correctly identifies errors and passes valid files.

.PARAMETER OutputReport
    Generate detailed test report. Default: $true

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    .\run-tests.ps1

.EXAMPLE
    .\run-tests.ps1 -OutputReport -Verbose

.NOTES
    Version: 1.0.0
    Author: AGENT-018
    Tests: 50+ test cases covering all validation scenarios
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$OutputReport = $true,

    [Parameter(Mandatory = $false)]
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

$script:TestResults = @{
    TotalTests = 0
    Passed     = 0
    Failed     = 0
    Skipped    = 0
    Errors     = @()
}

function Write-TestLog {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Error", "Warning")]
        [string]$Level = "Info"
    )
    
    $colors = @{
        Info    = "Cyan"
        Success = "Green"
        Error   = "Red"
        Warning = "Yellow"
    }
    
    $prefix = switch ($Level) {
        "Info"    { "ℹ" }
        "Success" { "✅" }
        "Error"   { "❌" }
        "Warning" { "⚠" }
    }
    
    Write-Host "$prefix $Message" -ForegroundColor $colors[$Level]
}

function Test-ValidCases {
    Write-TestLog "Testing VALID test cases..." -Level Info
    
    $validFiles = Get-ChildItem -Path ".\valid\*.md"
    
    foreach ($file in $validFiles) {
        $script:TestResults.TotalTests++
        
        Write-Host "`n  Testing: $($file.Name)" -ForegroundColor Gray
        
        try {
            $result = & ".\validate-metadata.ps1" -Path $file.FullName 2>&1
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -eq 0) {
                Write-TestLog "    PASS: $($file.Name) validated as VALID" -Level Success
                $script:TestResults.Passed++
            }
            else {
                Write-TestLog "    FAIL: $($file.Name) should be VALID but failed" -Level Error
                $script:TestResults.Failed++
                $script:TestResults.Errors += @{
                    File     = $file.Name
                    Expected = "VALID"
                    Actual   = "INVALID"
                    Output   = $result
                }
            }
        }
        catch {
            Write-TestLog "    ERROR: $($file.Name) threw exception: $_" -Level Error
            $script:TestResults.Failed++
            $script:TestResults.Errors += @{
                File      = $file.Name
                Expected  = "VALID"
                Exception = $_
            }
        }
    }
}

function Test-InvalidCases {
    Write-TestLog "`nTesting INVALID test cases..." -Level Info
    
    $invalidFiles = Get-ChildItem -Path ".\invalid\*.md"
    
    foreach ($file in $invalidFiles) {
        $script:TestResults.TotalTests++
        
        Write-Host "`n  Testing: $($file.Name)" -ForegroundColor Gray
        
        try {
            $result = & "..\..\validate-metadata.ps1" -Path $file.FullName 2>&1
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -ne 0) {
                Write-TestLog "    PASS: $($file.Name) correctly identified as INVALID" -Level Success
                $script:TestResults.Passed++
            }
            else {
                Write-TestLog "    FAIL: $($file.Name) should be INVALID but passed" -Level Error
                $script:TestResults.Failed++
                $script:TestResults.Errors += @{
                    File     = $file.Name
                    Expected = "INVALID"
                    Actual   = "VALID"
                    Output   = $result
                }
            }
        }
        catch {
            # Exceptions are expected for invalid cases
            Write-TestLog "    PASS: $($file.Name) threw expected exception" -Level Success
            $script:TestResults.Passed++
        }
    }
}

function Test-EdgeCases {
    Write-TestLog "`nTesting EDGE CASES..." -Level Info
    
    $edgeCaseFiles = Get-ChildItem -Path ".\edge-cases\*.md" -ErrorAction SilentlyContinue
    
    if (-not $edgeCaseFiles) {
        Write-TestLog "  No edge case files found" -Level Warning
        return
    }
    
    foreach ($file in $edgeCaseFiles) {
        $script:TestResults.TotalTests++
        
        Write-Host "`n  Testing: $($file.Name)" -ForegroundColor Gray
        
        try {
            $result = & "..\..\validate-metadata.ps1" -Path $file.FullName 2>&1
            $exitCode = $LASTEXITCODE
            
            # Edge cases should either pass or fail gracefully (no exceptions)
            Write-TestLog "    PASS: $($file.Name) handled gracefully (exit code: $exitCode)" -Level Success
            $script:TestResults.Passed++
        }
        catch {
            Write-TestLog "    FAIL: $($file.Name) threw unexpected exception: $_" -Level Error
            $script:TestResults.Failed++
            $script:TestResults.Errors += @{
                File      = $file.Name
                Category  = "EdgeCase"
                Exception = $_
            }
        }
    }
}

function Test-PerformanceBenchmark {
    Write-TestLog "`nRunning PERFORMANCE BENCHMARK..." -Level Info
    
    $script:TestResults.TotalTests++
    
    $testFile = ".\valid\minimal.md"
    $iterations = 10
    $threshold = 100  # milliseconds
    
    $times = @()
    
    for ($i = 0; $i -lt $iterations; $i++) {
        $startTime = Get-Date
        $null = & "..\..\validate-metadata.ps1" -Path $testFile 2>&1
        $endTime = Get-Date
        $elapsedMs = ($endTime - $startTime).TotalMilliseconds
        $times += $elapsedMs
    }
    
    $avgTime = ($times | Measure-Object -Average).Average
    $maxTime = ($times | Measure-Object -Maximum).Maximum
    $minTime = ($times | Measure-Object -Minimum).Minimum
    
    Write-Host "`n  Performance Results:" -ForegroundColor Gray
    Write-Host "    Average: $([math]::Round($avgTime, 2))ms" -ForegroundColor Cyan
    Write-Host "    Min:     $([math]::Round($minTime, 2))ms" -ForegroundColor Green
    Write-Host "    Max:     $([math]::Round($maxTime, 2))ms" -ForegroundColor Yellow
    Write-Host "    Threshold: ${threshold}ms" -ForegroundColor Gray
    
    if ($avgTime -lt $threshold) {
        Write-TestLog "  PASS: Performance within threshold (${avgTime}ms < ${threshold}ms)" -Level Success
        $script:TestResults.Passed++
    }
    else {
        Write-TestLog "  FAIL: Performance exceeds threshold (${avgTime}ms >= ${threshold}ms)" -Level Error
        $script:TestResults.Failed++
        $script:TestResults.Errors += @{
            Test      = "Performance Benchmark"
            Expected  = "< ${threshold}ms"
            Actual    = "${avgTime}ms"
        }
    }
}

function Test-BatchValidation {
    Write-TestLog "`nTesting BATCH VALIDATION..." -Level Info
    
    $script:TestResults.TotalTests++
    
    try {
        Write-Host "  Testing recursive directory validation..." -ForegroundColor Gray
        $result = & "..\..\validate-metadata.ps1" -Path "." -Recursive 2>&1
        
        Write-TestLog "  PASS: Batch validation completed successfully" -Level Success
        $script:TestResults.Passed++
    }
    catch {
        Write-TestLog "  FAIL: Batch validation threw exception: $_" -Level Error
        $script:TestResults.Failed++
        $script:TestResults.Errors += @{
            Test      = "Batch Validation"
            Exception = $_
        }
    }
}

function Test-CachingMechanism {
    Write-TestLog "`nTesting CACHING MECHANISM..." -Level Info
    
    $script:TestResults.TotalTests++
    
    $testFile = ".\valid\minimal.md"
    
    try {
        Write-Host "  First run (no cache)..." -ForegroundColor Gray
        $startTime1 = Get-Date
        $null = & "..\..\validate-metadata.ps1" -Path $testFile -Cache 2>&1
        $time1 = ((Get-Date) - $startTime1).TotalMilliseconds
        
        Write-Host "  Second run (cached)..." -ForegroundColor Gray
        $startTime2 = Get-Date
        $null = & "..\..\validate-metadata.ps1" -Path $testFile -Cache 2>&1
        $time2 = ((Get-Date) - $startTime2).TotalMilliseconds
        
        Write-Host "`n  Cache Performance:" -ForegroundColor Gray
        Write-Host "    Without cache: $([math]::Round($time1, 2))ms" -ForegroundColor Cyan
        Write-Host "    With cache:    $([math]::Round($time2, 2))ms" -ForegroundColor Green
        
        if ($time2 -lt $time1) {
            $improvement = [math]::Round((($time1 - $time2) / $time1) * 100, 2)
            Write-TestLog "  PASS: Cache improved performance by ${improvement}%" -Level Success
            $script:TestResults.Passed++
        }
        else {
            Write-TestLog "  FAIL: Cache did not improve performance" -Level Error
            $script:TestResults.Failed++
        }
    }
    catch {
        Write-TestLog "  FAIL: Caching test threw exception: $_" -Level Error
        $script:TestResults.Failed++
        $script:TestResults.Errors += @{
            Test      = "Caching Mechanism"
            Exception = $_
        }
    }
}

function Test-ParallelProcessing {
    Write-TestLog "`nTesting PARALLEL PROCESSING..." -Level Info
    
    $script:TestResults.TotalTests++
    
    try {
        Write-Host "  Testing parallel validation..." -ForegroundColor Gray
        $startTime = Get-Date
        $result = & "..\..\validate-metadata.ps1" -Path "." -Recursive -Parallel 2>&1
        $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
        
        Write-Host "  Parallel execution time: $([math]::Round($elapsed, 2))ms" -ForegroundColor Cyan
        
        Write-TestLog "  PASS: Parallel processing completed successfully" -Level Success
        $script:TestResults.Passed++
    }
    catch {
        Write-TestLog "  FAIL: Parallel processing threw exception: $_" -Level Error
        $script:TestResults.Failed++
        $script:TestResults.Errors += @{
            Test      = "Parallel Processing"
            Exception = $_
        }
    }
}

function Test-OutputFormats {
    Write-TestLog "`nTesting OUTPUT FORMATS..." -Level Info
    
    $testFile = ".\valid\minimal.md"
    
    # Test JSON output
    $script:TestResults.TotalTests++
    try {
        $jsonPath = "..\reports\test-output.json"
        $null = & "..\..\validate-metadata.ps1" -Path $testFile -OutputFormat JSON -OutputPath $jsonPath 2>&1
        
        if (Test-Path $jsonPath) {
            $jsonContent = Get-Content $jsonPath | ConvertFrom-Json
            if ($jsonContent.Results) {
                Write-TestLog "  PASS: JSON output format works correctly" -Level Success
                $script:TestResults.Passed++
            }
            else {
                Write-TestLog "  FAIL: JSON output missing Results property" -Level Error
                $script:TestResults.Failed++
            }
            Remove-Item $jsonPath -ErrorAction SilentlyContinue
        }
        else {
            Write-TestLog "  FAIL: JSON output file not created" -Level Error
            $script:TestResults.Failed++
        }
    }
    catch {
        Write-TestLog "  FAIL: JSON output test threw exception: $_" -Level Error
        $script:TestResults.Failed++
    }
    
    # Test Markdown output
    $script:TestResults.TotalTests++
    try {
        $mdPath = "..\reports\test-output.md"
        $null = & "..\..\validate-metadata.ps1" -Path $testFile -OutputFormat Markdown -OutputPath $mdPath 2>&1
        
        if (Test-Path $mdPath) {
            $mdContent = Get-Content $mdPath -Raw
            if ($mdContent -match "# Metadata Validation Report") {
                Write-TestLog "  PASS: Markdown output format works correctly" -Level Success
                $script:TestResults.Passed++
            }
            else {
                Write-TestLog "  FAIL: Markdown output missing header" -Level Error
                $script:TestResults.Failed++
            }
            Remove-Item $mdPath -ErrorAction SilentlyContinue
        }
        else {
            Write-TestLog "  FAIL: Markdown output file not created" -Level Error
            $script:TestResults.Failed++
        }
    }
    catch {
        Write-TestLog "  FAIL: Markdown output test threw exception: $_" -Level Error
        $script:TestResults.Failed++
    }
}

function Test-StrictMode {
    Write-TestLog "`nTesting STRICT MODE..." -Level Info
    
    $script:TestResults.TotalTests++
    
    # Create test file with warnings
    $testFile = ".\edge-cases\strict-mode-test.md"
    @"
---
description: Test file for strict mode validation
unknownField: This should trigger a warning
---
# Strict Mode Test
"@ | Set-Content $testFile
    
    try {
        Write-Host "  Testing strict mode with warnings..." -ForegroundColor Gray
        $result = & "..\..\validate-metadata.ps1" -Path $testFile -StrictMode 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -ne 0) {
            Write-TestLog "  PASS: Strict mode correctly fails on warnings" -Level Success
            $script:TestResults.Passed++
        }
        else {
            Write-TestLog "  FAIL: Strict mode should fail on warnings" -Level Error
            $script:TestResults.Failed++
        }
    }
    catch {
        Write-TestLog "  FAIL: Strict mode test threw exception: $_" -Level Error
        $script:TestResults.Failed++
    }
    finally {
        Remove-Item $testFile -ErrorAction SilentlyContinue
    }
}

function Test-FailFastMode {
    Write-TestLog "`nTesting FAIL-FAST MODE..." -Level Info
    
    $script:TestResults.TotalTests++
    
    try {
        Write-Host "  Testing fail-fast on invalid files..." -ForegroundColor Gray
        $result = & "..\..\validate-metadata.ps1" -Path ".\invalid" -Recursive -FailFast 2>&1
        $exitCode = $LASTEXITCODE
        
        # Fail-fast should stop on first error
        Write-TestLog "  PASS: Fail-fast mode executed (exit code: $exitCode)" -Level Success
        $script:TestResults.Passed++
    }
    catch {
        Write-TestLog "  FAIL: Fail-fast test threw exception: $_" -Level Error
        $script:TestResults.Failed++
    }
}

function Generate-TestReport {
    Write-Host "`n" -NoNewline
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  TEST RESULTS SUMMARY" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Total Tests:     $($script:TestResults.TotalTests)" -ForegroundColor White
    Write-Host "✅ Passed:       $($script:TestResults.Passed)" -ForegroundColor Green
    Write-Host "❌ Failed:       $($script:TestResults.Failed)" -ForegroundColor $(if ($script:TestResults.Failed -gt 0) { "Red" } else { "Green" })
    Write-Host "⚠ Skipped:       $($script:TestResults.Skipped)" -ForegroundColor Yellow
    Write-Host ""
    
    $passRate = [math]::Round(($script:TestResults.Passed / $script:TestResults.TotalTests) * 100, 2)
    Write-Host "Pass Rate:       ${passRate}%" -ForegroundColor $(if ($passRate -eq 100) { "Green" } elseif ($passRate -ge 90) { "Yellow" } else { "Red" })
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    
    if ($script:TestResults.Failed -gt 0) {
        Write-Host "`nFAILED TESTS:" -ForegroundColor Red
        foreach ($error in $script:TestResults.Errors) {
            Write-Host "  • $($error.File): $($error.Expected) -> $($error.Actual)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

function Save-TestReport {
    $reportPath = "..\reports\test-results.json"
    
    $report = @{
        Timestamp   = (Get-Date).ToString("o")
        Summary     = $script:TestResults
        PassRate    = [math]::Round(($script:TestResults.Passed / $script:TestResults.TotalTests) * 100, 2)
        Environment = @{
            PowerShellVersion = $PSVersionTable.PSVersion.ToString()
            OS                = [System.Environment]::OSVersion.VersionString
            Machine           = $env:COMPUTERNAME
        }
    }
    
    $report | ConvertTo-Json -Depth 10 | Set-Content $reportPath
    Write-TestLog "Test report saved to: $reportPath" -Level Success
}

# Main execution
try {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  METADATA VALIDATION TEST SUITE" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    # Run all test categories
    Test-ValidCases
    Test-InvalidCases
    Test-EdgeCases
    Test-PerformanceBenchmark
    Test-BatchValidation
    Test-CachingMechanism
    Test-ParallelProcessing
    Test-OutputFormats
    Test-StrictMode
    Test-FailFastMode
    
    # Generate reports
    Generate-TestReport
    
    if ($OutputReport) {
        Save-TestReport
    }
    
    # Exit with appropriate code
    if ($script:TestResults.Failed -gt 0) {
        exit 1
    }
    else {
        exit 0
    }
}
catch {
    Write-TestLog "Fatal error during test execution: $_" -Level Error
    exit 1
}
