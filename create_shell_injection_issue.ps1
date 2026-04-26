#!/usr/bin/env pwsh
# Script to create GitHub issue for Shell Injection Vulnerabilities (B602)
# Usage: .\create_shell_injection_issue.ps1

Write-Host "Creating GitHub Issue for Shell Injection Vulnerabilities..." -ForegroundColor Cyan

# Check if gh CLI is authenticated
$ghStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ GitHub CLI is not authenticated. Please run: gh auth login" -ForegroundColor Red
    exit 1
}

# Read the issue body from file
$issueFilePath = Join-Path $PSScriptRoot "ISSUE_SHELL_INJECTION_B602.md"
if (-not (Test-Path $issueFilePath)) {
    Write-Host "❌ Issue file not found: $issueFilePath" -ForegroundColor Red
    exit 1
}

$issueContent = Get-Content -Path $issueFilePath -Raw

# Extract the body content (skip metadata sections)
$bodyStart = $issueContent.IndexOf("## 🔴 CRITICAL SECURITY VULNERABILITY")
$bodyEnd = $issueContent.IndexOf("## Manual Issue Creation Instructions")
if ($bodyEnd -eq -1) {
    $bodyEnd = $issueContent.Length
}
$issueBody = $issueContent.Substring($bodyStart, $bodyEnd - $bodyStart).Trim()

Write-Host "📝 Issue Title: [CRITICAL] Shell Injection Vulnerabilities (B602) - 10 instances" -ForegroundColor Yellow
Write-Host "🏷️  Labels: security, critical, vulnerability" -ForegroundColor Yellow
Write-Host "📦 Repository: IAmSoThirsty/Project-AI" -ForegroundColor Yellow
Write-Host ""
Write-Host "Creating issue..." -ForegroundColor Green

try {
    # Create the issue
    $result = gh issue create `
        --repo IAmSoThirsty/Project-AI `
        --title "[CRITICAL] Shell Injection Vulnerabilities (B602) - 10 instances" `
        --label "security,critical,vulnerability" `
        --body $issueBody
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Issue created successfully!" -ForegroundColor Green
        Write-Host "🔗 Issue URL: $result" -ForegroundColor Cyan
        
        # Parse issue number from URL
        if ($result -match '#(\d+)') {
            $issueNumber = $matches[1]
            Write-Host "📋 Issue Number: #$issueNumber" -ForegroundColor Cyan
        }
        
        # Output for automation
        Write-Output $result
    } else {
        Write-Host "❌ Failed to create issue" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error creating issue: $_" -ForegroundColor Red
    exit 1
}
