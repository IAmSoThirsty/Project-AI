<#
.SYNOPSIS
    Comprehensive test suite for automation scripts.

.DESCRIPTION
    Tests all automation scripts with 30+ scenarios including:
    - Basic functionality tests
    - Error handling tests
    - Edge case tests
    - Performance tests
    - Rollback tests

.NOTES
    Author: AGENT-020 (Automation Scripts Architect)
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$SkipPerformanceTests
)

$ErrorActionPreference = 'Stop'
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:TestsSkipped = 0

#region Test Framework

function Write-TestHeader {
    param([string]$Message)
    
    Write-Host "`n$('=' * 80)" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "$('=' * 80)`n" -ForegroundColor Cyan
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Message = ""
    )
    
    if ($Passed) {
        Write-Host "[PASS] " -ForegroundColor Green -NoNewline
        Write-Host $TestName
        $script:TestsPassed++
    }
    else {
        Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
        Write-Host "$TestName - $Message"
        $script:TestsFailed++
    }
}

function Test-FileExists {
    param([string]$Path)
    return Test-Path $Path
}

function Test-ScriptSyntax {
    param([string]$ScriptPath)
    
    try {
        $null = [System.Management.Automation.PSParser]::Tokenize(
            (Get-Content -Path $ScriptPath -Raw),
            [ref]$null
        )
        return $true
    }
    catch {
        return $false
    }
}

function New-TestDirectory {
    $tempDir = Join-Path $env:TEMP "automation-tests-$(Get-Date -Format 'yyyyMMddHHmmss')"
    New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
    return $tempDir
}

function New-TestFile {
    param(
        [string]$Directory,
        [string]$Name,
        [string]$Content = "# Test File`n`nThis is test content."
    )
    
    $filePath = Join-Path $Directory $Name
    Set-Content -Path $filePath -Value $Content -NoNewline
    return $filePath
}

#endregion

#region Test Suite

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
Write-Host "║       AUTOMATION SCRIPTS COMPREHENSIVE TEST SUITE             ║" -ForegroundColor Yellow
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Yellow

# Test 1: Script Existence
Write-TestHeader "TEST GROUP 1: Script Existence & Syntax"

$scripts = @(
    '.\scripts\automation\add-metadata.ps1',
    '.\scripts\automation\convert-links.ps1',
    '.\scripts\automation\validate-tags.ps1',
    '.\scripts\automation\batch-process.ps1'
)

foreach ($script in $scripts) {
    $exists = Test-FileExists -Path $script
    Write-TestResult -TestName "Script exists: $(Split-Path -Leaf $script)" -Passed $exists
}

# Test 2: Script Syntax
foreach ($script in $scripts) {
    if (Test-FileExists -Path $script) {
        $valid = Test-ScriptSyntax -ScriptPath $script
        Write-TestResult -TestName "Valid syntax: $(Split-Path -Leaf $script)" -Passed $valid
    }
}

# Test 3: Help Documentation
Write-TestHeader "TEST GROUP 2: Help Documentation"

foreach ($script in $scripts) {
    if (Test-FileExists -Path $script) {
        try {
            $help = Get-Help $script -ErrorAction Stop
            $hasDescription = -not [string]::IsNullOrEmpty($help.Description)
            Write-TestResult -TestName "Has help: $(Split-Path -Leaf $script)" -Passed $hasDescription
        }
        catch {
            Write-TestResult -TestName "Has help: $(Split-Path -Leaf $script)" -Passed $false -Message $_.Exception.Message
        }
    }
}

# Test 4: add-metadata.ps1 Functionality
Write-TestHeader "TEST GROUP 3: add-metadata.ps1 Functionality"

try {
    $testDir = New-TestDirectory
    $testFile = New-TestFile -Directory $testDir -Name "test.md" -Content @"
# Test Document

This is a test document about **authentication** and **security**.

## Authentication

Using JWT tokens for authentication.

``````python
def authenticate(token):
    return verify_jwt(token)
``````
"@
    
    # Test 3.1: Dry-run mode
    try {
        & .\scripts\automation\add-metadata.ps1 `
            -Path $testFile `
            -DryRun `
            -LogPath (Join-Path $testDir "dry-run.log") `
            -ErrorAction Stop | Out-Null
        
        $contentUnchanged = -not ((Get-Content $testFile -Raw) -match '^---')
        Write-TestResult -TestName "add-metadata: Dry-run doesn't modify file" -Passed $contentUnchanged
    }
    catch {
        Write-TestResult -TestName "add-metadata: Dry-run doesn't modify file" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 3.2: Actual metadata generation
    try {
        & .\scripts\automation\add-metadata.ps1 `
            -Path $testFile `
            -LogPath (Join-Path $testDir "add-metadata.log") `
            -ErrorAction Stop | Out-Null
        
        $content = Get-Content $testFile -Raw
        $hasFrontmatter = $content -match '^---\s*\n.*?\n---\s*\n'
        Write-TestResult -TestName "add-metadata: Generates frontmatter" -Passed $hasFrontmatter
    }
    catch {
        Write-TestResult -TestName "add-metadata: Generates frontmatter" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 3.3: Force overwrite
    try {
        & .\scripts\automation\add-metadata.ps1 `
            -Path $testFile `
            -Force `
            -LogPath (Join-Path $testDir "force.log") `
            -ErrorAction Stop | Out-Null
        
        Write-TestResult -TestName "add-metadata: Force overwrite works" -Passed $true
    }
    catch {
        Write-TestResult -TestName "add-metadata: Force overwrite works" -Passed $false -Message $_.Exception.Message
    }
    
    # Cleanup
    Remove-Item $testDir -Recurse -Force
}
catch {
    Write-TestResult -TestName "add-metadata: Test setup" -Passed $false -Message $_.Exception.Message
}

# Test 5: convert-links.ps1 Functionality
Write-TestHeader "TEST GROUP 4: convert-links.ps1 Functionality"

try {
    $testDir = New-TestDirectory
    $testFile = New-TestFile -Directory $testDir -Name "links.md" -Content @"
# Links Test

Here are some links:

[Documentation](./docs/README.md)
[Security Guide](./security/guide.md#auth)
[External](https://example.com)
"@
    
    # Test 5.1: Dry-run conversion
    try {
        & .\scripts\automation\convert-links.ps1 `
            -Path $testFile `
            -DryRun `
            -LogPath (Join-Path $testDir "convert-dry.log") `
            -BackupDir (Join-Path $testDir "backups") `
            -ErrorAction Stop | Out-Null
        
        $originalContent = Get-Content $testFile -Raw
        $unchanged = $originalContent -match '\[Documentation\]\(./docs/README.md\)'
        Write-TestResult -TestName "convert-links: Dry-run doesn't modify" -Passed $unchanged
    }
    catch {
        Write-TestResult -TestName "convert-links: Dry-run doesn't modify" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 5.2: Actual conversion to wiki
    try {
        & .\scripts\automation\convert-links.ps1 `
            -Path $testFile `
            -ConversionMode ToWiki `
            -LogPath (Join-Path $testDir "convert.log") `
            -BackupDir (Join-Path $testDir "backups") `
            -ErrorAction Stop | Out-Null
        
        $content = Get-Content $testFile -Raw
        $converted = $content -match '\[\[./docs/README.md\|Documentation\]\]'
        Write-TestResult -TestName "convert-links: Converts to wiki format" -Passed $converted
    }
    catch {
        Write-TestResult -TestName "convert-links: Converts to wiki format" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 5.3: Backup creation
    $backupExists = (Get-ChildItem (Join-Path $testDir "backups") -Recurse -File).Count -gt 0
    Write-TestResult -TestName "convert-links: Creates backup" -Passed $backupExists
    
    # Test 5.4: Rollback
    try {
        & .\scripts\automation\convert-links.ps1 `
            -Rollback `
            -BackupDir (Join-Path $testDir "backups") `
            -LogPath (Join-Path $testDir "rollback.log") `
            -ErrorAction Stop | Out-Null
        
        $content = Get-Content $testFile -Raw
        $restored = $content -match '\[Documentation\]\(./docs/README.md\)'
        Write-TestResult -TestName "convert-links: Rollback restores original" -Passed $restored
    }
    catch {
        Write-TestResult -TestName "convert-links: Rollback restores original" -Passed $false -Message $_.Exception.Message
    }
    
    # Cleanup
    Remove-Item $testDir -Recurse -Force
}
catch {
    Write-TestResult -TestName "convert-links: Test setup" -Passed $false -Message $_.Exception.Message
}

# Test 6: validate-tags.ps1 Functionality
Write-TestHeader "TEST GROUP 5: validate-tags.ps1 Functionality"

try {
    $testDir = New-TestDirectory
    $testFile = New-TestFile -Directory $testDir -Name "tagged.md" -Content @"
---
title: Test Document
tags:
  - security
  - authentification
  - k8s
  - invalid-tag-xyz
---

# Test Document

Content here.
"@
    
    # Test 6.1: Tag validation
    try {
        & .\scripts\automation\validate-tags.ps1 `
            -Path $testFile `
            -LogPath (Join-Path $testDir "validate.log") `
            -ReportPath (Join-Path $testDir "report.html") `
            -ErrorAction Stop | Out-Null
        
        $reportExists = Test-Path (Join-Path $testDir "report.html")
        Write-TestResult -TestName "validate-tags: Generates report" -Passed $reportExists
    }
    catch {
        Write-TestResult -TestName "validate-tags: Generates report" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 6.2: JSON report
    try {
        & .\scripts\automation\validate-tags.ps1 `
            -Path $testFile `
            -OutputFormat JSON `
            -LogPath (Join-Path $testDir "validate-json.log") `
            -ReportPath (Join-Path $testDir "report.json") `
            -ErrorAction Stop | Out-Null
        
        $jsonReport = Get-Content (Join-Path $testDir "report.json") -Raw | ConvertFrom-Json
        $hasResults = $null -ne $jsonReport.results
        Write-TestResult -TestName "validate-tags: JSON report format" -Passed $hasResults
    }
    catch {
        Write-TestResult -TestName "validate-tags: JSON report format" -Passed $false -Message $_.Exception.Message
    }
    
    # Cleanup
    Remove-Item $testDir -Recurse -Force
}
catch {
    Write-TestResult -TestName "validate-tags: Test setup" -Passed $false -Message $_.Exception.Message
}

# Test 7: batch-process.ps1 Functionality
Write-TestHeader "TEST GROUP 6: batch-process.ps1 Functionality"

try {
    $testDir = New-TestDirectory
    $testFile = New-TestFile -Directory $testDir -Name "batch-test.md"
    
    # Test 7.1: Single operation
    try {
        & .\scripts\automation\batch-process.ps1 `
            -Operation AddMetadata `
            -Path $testFile `
            -DryRun `
            -LogPath (Join-Path $testDir "batch.log") `
            -ErrorAction Stop | Out-Null
        
        Write-TestResult -TestName "batch-process: Single operation dry-run" -Passed $true
    }
    catch {
        Write-TestResult -TestName "batch-process: Single operation dry-run" -Passed $false -Message $_.Exception.Message
    }
    
    # Test 7.2: Pipeline
    try {
        & .\scripts\automation\batch-process.ps1 `
            -Pipeline @('AddMetadata', 'ValidateTags') `
            -Path $testFile `
            -DryRun `
            -LogPath (Join-Path $testDir "pipeline.log") `
            -ErrorAction Stop | Out-Null
        
        Write-TestResult -TestName "batch-process: Pipeline execution" -Passed $true
    }
    catch {
        Write-TestResult -TestName "batch-process: Pipeline execution" -Passed $false -Message $_.Exception.Message
    }
    
    # Cleanup
    Remove-Item $testDir -Recurse -Force
}
catch {
    Write-TestResult -TestName "batch-process: Test setup" -Passed $false -Message $_.Exception.Message
}

# Test 8: Error Handling
Write-TestHeader "TEST GROUP 7: Error Handling"

# Test 8.1: Invalid path
try {
    & .\scripts\automation\add-metadata.ps1 `
        -Path ".\nonexistent-path-xyz" `
        -ErrorAction Stop 2>&1 | Out-Null
    Write-TestResult -TestName "Error handling: Invalid path rejected" -Passed $false -Message "Should have thrown error"
}
catch {
    Write-TestResult -TestName "Error handling: Invalid path rejected" -Passed $true
}

# Test 8.2: Missing required parameter
try {
    & .\scripts\automation\add-metadata.ps1 -ErrorAction Stop 2>&1 | Out-Null
    Write-TestResult -TestName "Error handling: Missing parameter rejected" -Passed $false -Message "Should have thrown error"
}
catch {
    Write-TestResult -TestName "Error handling: Missing parameter rejected" -Passed $true
}

# Test 9: Documentation
Write-TestHeader "TEST GROUP 8: Documentation"

$guideExists = Test-Path ".\scripts\automation\AUTOMATION_GUIDE.md"
Write-TestResult -TestName "Documentation: AUTOMATION_GUIDE.md exists" -Passed $guideExists

if ($guideExists) {
    $guideContent = Get-Content ".\scripts\automation\AUTOMATION_GUIDE.md" -Raw
    $hasExamples = $guideContent -match '## Usage Examples'
    $hasTroubleshooting = $guideContent -match '## Troubleshooting'
    $hasPerformance = $guideContent -match '## Performance'
    
    Write-TestResult -TestName "Documentation: Has usage examples" -Passed $hasExamples
    Write-TestResult -TestName "Documentation: Has troubleshooting" -Passed $hasTroubleshooting
    Write-TestResult -TestName "Documentation: Has performance guidelines" -Passed $hasPerformance
    
    $wordCount = ($guideContent -split '\s+').Count
    $meetsMinimum = $wordCount -ge 1000
    Write-TestResult -TestName "Documentation: Meets 1000+ words requirement ($wordCount words)" -Passed $meetsMinimum
}

# Test 10: Performance (if not skipped)
if (-not $SkipPerformanceTests) {
    Write-TestHeader "TEST GROUP 9: Performance Tests"
    
    try {
        $testDir = New-TestDirectory
        
        # Create 100 test files
        Write-Host "Creating 100 test files..." -ForegroundColor Yellow
        for ($i = 1; $i -le 100; $i++) {
            $null = New-TestFile -Directory $testDir -Name "file$i.md"
        }
        
        # Test performance
        Write-Host "Testing add-metadata performance..." -ForegroundColor Yellow
        $startTime = Get-Date
        
        & .\scripts\automation\add-metadata.ps1 `
            -Path $testDir `
            -LogPath (Join-Path $testDir "perf.log") `
            -ErrorAction Stop | Out-Null
        
        $duration = (Get-Date) - $startTime
        $meetsTarget = $duration.TotalSeconds -lt 60  # 100 files in <60s
        
        Write-TestResult -TestName "Performance: 100 files in <60s ($([math]::Round($duration.TotalSeconds, 2))s)" -Passed $meetsTarget
        
        # Cleanup
        Remove-Item $testDir -Recurse -Force
    }
    catch {
        Write-TestResult -TestName "Performance: Test execution" -Passed $false -Message $_.Exception.Message
    }
}
else {
    Write-Host "`nPerformance tests skipped (use -SkipPerformanceTests:`$false to run)" -ForegroundColor Yellow
    $script:TestsSkipped++
}

#endregion

#region Summary

Write-Host "`n`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      TEST SUMMARY                              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$totalTests = $script:TestsPassed + $script:TestsFailed + $script:TestsSkipped
$passRate = if ($totalTests -gt 0) { [math]::Round(($script:TestsPassed / $totalTests) * 100, 2) } else { 0 }

Write-Host "Total Tests:  " -NoNewline
Write-Host $totalTests -ForegroundColor Cyan

Write-Host "Passed:       " -NoNewline
Write-Host $script:TestsPassed -ForegroundColor Green

Write-Host "Failed:       " -NoNewline
Write-Host $script:TestsFailed -ForegroundColor $(if ($script:TestsFailed -eq 0) { 'Green' } else { 'Red' })

Write-Host "Skipped:      " -NoNewline
Write-Host $script:TestsSkipped -ForegroundColor Yellow

Write-Host "Pass Rate:    " -NoNewline
Write-Host "$passRate%" -ForegroundColor $(if ($passRate -ge 90) { 'Green' } elseif ($passRate -ge 70) { 'Yellow' } else { 'Red' })

Write-Host ""

if ($script:TestsFailed -eq 0) {
    Write-Host "✓ ALL TESTS PASSED" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
    exit 1
}

#endregion
