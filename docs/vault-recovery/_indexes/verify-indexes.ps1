# Manual Verification Script for Index Files
# Checks basic naming convention compliance

$indexPath = "T:\Project-AI-vault\_indexes"

Write-Host "=== Index File Naming Convention Verification ===" -ForegroundColor Cyan
Write-Host ""

# Get all .md files recursively
$mdFiles = Get-ChildItem -Path $indexPath -Filter *.md -Recurse

$passed = 0
$failed = 0

# Allowed special files
$allowedSpecial = @(
    'README.md',
    'NAVIGATION_PLAN.md',
    'NAMING_CONVENTIONS.md',
    'AGENT-002-COMPLETION-REPORT.md',
    'INDEX_TEMPLATE.md'
)

foreach ($file in $mdFiles) {
    $filename = $file.Name
    $relativePath = $file.FullName.Replace($indexPath, '').TrimStart('\')

    # Check if special file (allowed to not follow -index.md pattern)
    if ($allowedSpecial -contains $filename) {
        Write-Host "✅ $relativePath - PASS (special file)" -ForegroundColor Green
        $passed++
        continue
    }

    # Check naming convention
    $errors = @()

    # Must end with -index.md
    if (-not $filename.EndsWith('-index.md')) {
        $errors += "Must end with '-index.md'"
    }

    # Must be lowercase
    if ($filename -cne $filename.ToLower()) {
        $errors += "Must be lowercase only"
    }

    # Only a-z, 0-9, hyphen allowed
    if ($filename -notmatch '^[a-z0-9-]+-index\.md$') {
        $errors += "Only a-z, 0-9, and hyphen allowed"
    }

    # No consecutive hyphens
    if ($filename -match '--') {
        $errors += "No consecutive hyphens allowed"
    }

    # Max length check (50 chars + .md)
    if ($filename.Length -gt 53) {
        $errors += "Exceeds maximum length of 50 characters"
    }

    if ($errors.Count -eq 0) {
        Write-Host "✅ $relativePath - PASS" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ $relativePath - FAIL" -ForegroundColor Red
        foreach ($error in $errors) {
            Write-Host "   - $error" -ForegroundColor Yellow
        }
        $failed++
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Total files: $($mdFiles.Count)"
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

# Check directory structure
Write-Host ""
Write-Host "=== Directory Structure Verification ===" -ForegroundColor Cyan

$expectedDirs = @(
    'by-area',
    'by-type',
    'by-priority',
    'by-status',
    'cross-reference',
    'templates'
)

$actualDirs = Get-ChildItem -Path $indexPath -Directory | Select-Object -ExpandProperty Name

foreach ($expectedDir in $expectedDirs) {
    if ($actualDirs -contains $expectedDir) {
        Write-Host "✅ $expectedDir/ exists" -ForegroundColor Green
    } else {
        Write-Host "❌ $expectedDir/ missing" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== Required Files Verification ===" -ForegroundColor Cyan

$requiredFiles = @(
    'README.md',
    'NAVIGATION_PLAN.md',
    'NAMING_CONVENTIONS.md',
    '.index-schema.json',
    'templates\INDEX_TEMPLATE.md',
    'by-area\security-domain-index.md',
    'AGENT-002-COMPLETION-REPORT.md'
)

foreach ($requiredFile in $requiredFiles) {
    $fullPath = Join-Path $indexPath $requiredFile
    if (Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "✅ $requiredFile ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "❌ $requiredFile missing" -ForegroundColor Red
    }
}

Write-Host ""
if ($failed -eq 0) {
    Write-Host "🎉 All validations passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Some validations failed. Please review errors above." -ForegroundColor Yellow
    exit 1
}
