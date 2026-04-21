---
type: compliance-doc
tags:
  - cicd
  - automation
  - github-actions
  - azure-devops
  - gitlab-ci
  - jenkins
  - circleci
  - validation
  - integration
created: 2026-01-23
last_verified: 2026-04-20
status: current
related_systems:
  - github-actions
  - azure-devops
  - gitlab-ci
  - jenkins
  - circleci
  - metadata-validation-system
stakeholders:
  - qa-team
  - compliance-team
  - devops-team
audit_scope:
  - compliance
  - code-quality
findings_severity: informational
pass_rate: N/A
review_cycle: quarterly
---

# CI/CD Integration Guide

**Version:** 1.0.0  
**Last Updated:** 2026-01-23  
**Status:** ACTIVE

---

## Overview

This guide provides comprehensive instructions for integrating the metadata validation system into various CI/CD platforms, including GitHub Actions, Azure DevOps, GitLab CI, Jenkins, and CircleCI.

---

## Table of Contents

1. [GitHub Actions](#github-actions)
2. [Azure DevOps](#azure-devops)
3. [GitLab CI](#gitlab-ci)
4. [Jenkins](#jenkins)
5. [CircleCI](#circleci)
6. [Pre-commit Hooks](#pre-commit-hooks)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## GitHub Actions

### Basic Workflow

Create `.github/workflows/validate-metadata.yml`:

```yaml
name: Validate Metadata

on:
  pull_request:
    paths:
      - '**/*.md'
  push:
    branches:
      - main
      - develop
  workflow_dispatch:

permissions:
  contents: read
  pull-requests: write

jobs:
  validate:
    name: Validate Documentation Metadata
    runs-on: windows-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Install PowerShell YAML module
        shell: pwsh
        run: |
          Write-Host "Installing powershell-yaml module..."
          Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
          Write-Host "✅ Module installed successfully"
      
      - name: Validate metadata (strict mode)
        shell: pwsh
        run: |
          .\validate-metadata.ps1 `
            -Path "." `
            -Recursive `
            -Parallel `
            -Cache `
            -StrictMode `
            -OutputFormat JSON `
            -OutputPath "validation-results.json"
      
      - name: Upload validation report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: validation-report-${{ github.run_number }}
          path: validation-results.json
          retention-days: 30
      
      - name: Generate summary
        if: always()
        shell: pwsh
        run: |
          if (Test-Path "validation-results.json") {
            $results = Get-Content "validation-results.json" | ConvertFrom-Json
            
            $summary = @"
          ## 📊 Metadata Validation Results
          
          | Metric | Value |
          |--------|-------|
          | Total Files | $($results.Statistics.TotalFiles) |
          | ✅ Valid | $($results.Statistics.ValidFiles) |
          | ❌ Invalid | $($results.Statistics.InvalidFiles) |
          | ⚠ Skipped | $($results.Statistics.SkippedFiles) |
          | Errors | $($results.Statistics.TotalErrors) |
          | Warnings | $($results.Statistics.TotalWarnings) |
          
          ### Performance
          - Average Time: $([math]::Round($results.Statistics.TotalTime / [math]::Max($results.Statistics.TotalFiles, 1), 2))ms per file
          - Total Time: $([math]::Round($results.Statistics.TotalTime, 2))ms
          "@
            
            $summary >> $env:GITHUB_STEP_SUMMARY
          }
      
      - name: Comment on PR
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            
            if (!fs.existsSync('validation-results.json')) {
              console.log('No results file found');
              return;
            }
            
            const results = JSON.parse(fs.readFileSync('validation-results.json', 'utf8'));
            const invalidFiles = results.Results.filter(r => r.Status === 'INVALID');
            
            if (invalidFiles.length === 0) {
              console.log('No invalid files found');
              return;
            }
            
            let comment = '## ❌ Metadata Validation Failed\n\n';
            comment += `**Files with errors:** ${invalidFiles.length}\n\n`;
            
            const maxFilesToShow = 5;
            invalidFiles.slice(0, maxFilesToShow).forEach(file => {
              comment += `### 📄 \`${file.FilePath}\`\n\n`;
              
              if (file.Errors && file.Errors.length > 0) {
                comment += '**Errors:**\n';
                file.Errors.forEach(err => {
                  comment += `- **${err.Field}:** ${err.Message} \`[${err.Error}]\`\n`;
                });
              }
              
              if (file.Warnings && file.Warnings.length > 0) {
                comment += '\n**Warnings:**\n';
                file.Warnings.forEach(warn => {
                  comment += `- **${warn.Field}:** ${warn.Message} \`[${warn.Warning}]\`\n`;
                });
              }
              
              comment += '\n';
            });
            
            if (invalidFiles.length > maxFilesToShow) {
              comment += `\n...and ${invalidFiles.length - maxFilesToShow} more files. `;
              comment += 'See the full report in the [workflow artifacts](';
              comment += `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}).\n`;
            }
            
            comment += '\n---\n\n';
            comment += '💡 **Quick Fix Guide:**\n';
            comment += '1. Review the error catalog: `validation/error-catalog/error-catalog.json`\n';
            comment += '2. Run locally: `.\validate-metadata.ps1 -Path "." -Recursive`\n';
            comment += '3. See validation guide: `validation/VALIDATION_GUIDE.md`\n';
            
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Incremental Validation (Changed Files Only)

```yaml
      - name: Get changed Markdown files
        id: changed-files
        uses: tj-actions/changed-files@v41
        with:
          files: '**/*.md'
      
      - name: Validate changed files only
        if: steps.changed-files.outputs.any_changed == 'true'
        shell: pwsh
        run: |
          $files = "${{ steps.changed-files.outputs.all_changed_files }}" -split ' '
          
          foreach ($file in $files) {
            Write-Host "Validating: $file"
            .\validate-metadata.ps1 -Path $file -FailFast
          }
```

---

## Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - '**/*.md'
    exclude:
      - '**/node_modules/**'

pool:
  vmImage: 'windows-latest'

variables:
  - name: validationReportPath
    value: '$(Build.ArtifactStagingDirectory)/validation-results.json'

steps:
  - checkout: self
    fetchDepth: 0
  
  - task: PowerShell@2
    displayName: 'Install PowerShell YAML Module'
    inputs:
      targetType: 'inline'
      script: |
        Write-Host "Installing powershell-yaml module..."
        Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
        Write-Host "✅ Module installed"
      pwsh: true
  
  - task: PowerShell@2
    displayName: 'Validate Metadata'
    inputs:
      filePath: 'validate-metadata.ps1'
      arguments: >
        -Path "."
        -Recursive
        -Parallel
        -Cache
        -StrictMode
        -OutputFormat JSON
        -OutputPath "$(validationReportPath)"
      pwsh: true
      failOnStderr: false
  
  - task: PublishBuildArtifacts@1
    displayName: 'Publish Validation Report'
    condition: always()
    inputs:
      PathtoPublish: '$(validationReportPath)'
      ArtifactName: 'validation-report'
      publishLocation: 'Container'
  
  - task: PowerShell@2
    displayName: 'Generate Test Results'
    condition: always()
    inputs:
      targetType: 'inline'
      script: |
        if (Test-Path "$(validationReportPath)") {
          $results = Get-Content "$(validationReportPath)" | ConvertFrom-Json
          
          Write-Host "##vso[task.setvariable variable=ValidFiles]$($results.Statistics.ValidFiles)"
          Write-Host "##vso[task.setvariable variable=InvalidFiles]$($results.Statistics.InvalidFiles)"
          Write-Host "##vso[task.setvariable variable=TotalErrors]$($results.Statistics.TotalErrors)"
          
          if ($results.Statistics.InvalidFiles -gt 0) {
            Write-Host "##vso[task.complete result=Failed;]Validation failed: $($results.Statistics.InvalidFiles) invalid files"
          }
        }
      pwsh: true
```

---

## GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - validate

validate-metadata:
  stage: validate
  image: mcr.microsoft.com/powershell:latest
  
  before_script:
    - pwsh -Command "Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber"
  
  script:
    - |
      pwsh -Command "
        .\validate-metadata.ps1 `
          -Path '.' `
          -Recursive `
          -Parallel `
          -Cache `
          -OutputFormat JSON `
          -OutputPath 'validation-results.json'
      "
  
  artifacts:
    when: always
    paths:
      - validation-results.json
    expire_in: 30 days
    reports:
      junit: validation-results.xml
  
  rules:
    - changes:
        - '**/*.md'
      when: always
    - when: manual
  
  allow_failure: false
```

---

## Jenkins

Create `Jenkinsfile`:

```groovy
pipeline {
    agent {
        label 'windows'
    }
    
    triggers {
        pollSCM('H/5 * * * *')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                powershell '''
                    Write-Host "Installing powershell-yaml module..."
                    Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
                    Write-Host "✅ Module installed"
                '''
            }
        }
        
        stage('Validate Metadata') {
            steps {
                powershell '''
                    .\\validate-metadata.ps1 `
                        -Path "." `
                        -Recursive `
                        -Parallel `
                        -Cache `
                        -StrictMode `
                        -OutputFormat JSON `
                        -OutputPath "validation-results.json"
                '''
            }
        }
        
        stage('Publish Results') {
            steps {
                archiveArtifacts artifacts: 'validation-results.json', allowEmptyArchive: false
                
                powershell '''
                    $results = Get-Content "validation-results.json" | ConvertFrom-Json
                    
                    $summary = @"
                    Metadata Validation Results
                    ============================
                    Total Files: $($results.Statistics.TotalFiles)
                    Valid: $($results.Statistics.ValidFiles)
                    Invalid: $($results.Statistics.InvalidFiles)
                    Errors: $($results.Statistics.TotalErrors)
                    Warnings: $($results.Statistics.TotalWarnings)
                    "@
                    
                    Write-Host $summary
                    
                    if ($results.Statistics.InvalidFiles -gt 0) {
                        error("Validation failed: $($results.Statistics.InvalidFiles) invalid files")
                    }
                '''
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext(
                subject: "Metadata Validation Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Check console output at ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

---

## CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

executors:
  windows-executor:
    machine:
      image: windows-server-2022-gui:current
    resource_class: windows.medium
    shell: powershell.exe -ExecutionPolicy Bypass

jobs:
  validate-metadata:
    executor: windows-executor
    
    steps:
      - checkout
      
      - run:
          name: Install PowerShell YAML Module
          command: |
            Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber
      
      - run:
          name: Validate Metadata
          command: |
            .\validate-metadata.ps1 `
              -Path "." `
              -Recursive `
              -Parallel `
              -Cache `
              -OutputFormat JSON `
              -OutputPath "validation-results.json"
      
      - store_artifacts:
          path: validation-results.json
          destination: validation-report
      
      - store_test_results:
          path: validation-results.json

workflows:
  version: 2
  validate:
    jobs:
      - validate-metadata:
          filters:
            branches:
              only:
                - main
                - develop
```

---

## Pre-commit Hooks

### Git Hook (Bash)

Create `.githooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Running metadata validation..."

# Get staged Markdown files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.md$')

if [ -z "$STAGED_FILES" ]; then
  echo "✅ No Markdown files to validate"
  exit 0
fi

# Validate each file
pwsh -NoProfile -ExecutionPolicy Bypass -Command "
  \$failedFiles = @()
  
  foreach (\$file in ('$STAGED_FILES' -split '\\n')) {
    if (-not \$file) { continue }
    
    Write-Host \"Validating: \$file\"
    
    try {
      & '.\validate-metadata.ps1' -Path \$file -FailFast 2>&1 | Out-Null
      
      if (\$LASTEXITCODE -ne 0) {
        \$failedFiles += \$file
      }
    }
    catch {
      \$failedFiles += \$file
    }
  }
  
  if (\$failedFiles.Count -gt 0) {
    Write-Host \"❌ Validation failed for:\" -ForegroundColor Red
    \$failedFiles | ForEach-Object { Write-Host \"  • \$_\" -ForegroundColor Red }
    Write-Host \"\"
    Write-Host \"Fix errors before committing. Run:\" -ForegroundColor Yellow
    Write-Host \"  .\validate-metadata.ps1 -Path <file>\" -ForegroundColor Cyan
    exit 1
  }
  
  Write-Host \"✅ All metadata valid\" -ForegroundColor Green
  exit 0
"

EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo ""
  echo "💡 To skip validation, use: git commit --no-verify"
  exit 1
fi

exit 0
```

Make executable:

```bash
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

### PowerShell Hook

Create `.githooks/pre-commit.ps1`:

```powershell
#!/usr/bin/env pwsh

Write-Host "🔍 Running metadata validation..." -ForegroundColor Cyan

# Get staged Markdown files
$stagedFiles = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.md$' }

if (-not $stagedFiles) {
    Write-Host "✅ No Markdown files to validate" -ForegroundColor Green
    exit 0
}

$failedFiles = @()

foreach ($file in $stagedFiles) {
    Write-Host "Validating: $file" -ForegroundColor Gray
    
    try {
        & ".\validate-metadata.ps1" -Path $file -FailFast 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            $failedFiles += $file
        }
    }
    catch {
        $failedFiles += $file
    }
}

if ($failedFiles.Count -gt 0) {
    Write-Host "`n❌ Validation failed for:" -ForegroundColor Red
    $failedFiles | ForEach-Object { Write-Host "  • $_" -ForegroundColor Red }
    Write-Host "`nFix errors before committing. Run:" -ForegroundColor Yellow
    Write-Host "  .\validate-metadata.ps1 -Path <file>" -ForegroundColor Cyan
    Write-Host "`n💡 To skip validation, use: git commit --no-verify" -ForegroundColor Gray
    exit 1
}

Write-Host "✅ All metadata valid" -ForegroundColor Green
exit 0
```

---

## Best Practices

### 1. Cache Validation Results

Enable caching in CI/CD to speed up validations:

```yaml
- name: Cache validation results
  uses: actions/cache@v3
  with:
    path: validation/.cache
    key: validation-cache-${{ hashFiles('**/*.md') }}
    restore-keys: |
      validation-cache-
```

### 2. Fail Fast in PR Pipelines

Use fail-fast mode for quick feedback:

```powershell
.\validate-metadata.ps1 -Path "." -Recursive -FailFast
```

### 3. Full Validation on Main Branch

Run comprehensive validation on main branch:

```powershell
.\validate-metadata.ps1 -Path "." -Recursive -Parallel -StrictMode
```

### 4. Generate Reports as Artifacts

Always upload validation reports:

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: validation-report
    path: validation-results.json
```

### 5. Notify on Failures

Configure notifications for validation failures:

```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1.24.0
  with:
    payload: |
      {
        "text": "Metadata validation failed in ${{ github.repository }}"
      }
```

---

## Troubleshooting

### Issue: Module Installation Fails

**Solution:**
```yaml
- name: Install Module with Retry
  shell: pwsh
  run: |
    $maxRetries = 3
    $retryCount = 0
    
    while ($retryCount -lt $maxRetries) {
      try {
        Install-Module -Name powershell-yaml -Scope CurrentUser -Force -AllowClobber -ErrorAction Stop
        break
      }
      catch {
        $retryCount++
        Write-Host "Retry $retryCount of $maxRetries..."
        Start-Sleep -Seconds 5
      }
    }
```

### Issue: Performance Degradation

**Solution:** Use incremental validation and caching:

```yaml
- name: Validate Changed Files Only
  run: |
    $changedFiles = git diff --name-only HEAD~1 HEAD | Where-Object { $_ -match '\.md$' }
    foreach ($file in $changedFiles) {
      .\validate-metadata.ps1 -Path $file -Cache
    }
```

### Issue: Windows Runner Unavailable

**Solution:** Use Docker with PowerShell image:

```yaml
runs-on: ubuntu-latest
container:
  image: mcr.microsoft.com/powershell:latest
```

---

## Conclusion

Integrating metadata validation into CI/CD pipelines ensures consistent documentation quality across all commits and pull requests. Choose the platform-specific configuration that matches your infrastructure and customize as needed.

### Key Takeaways

- ✅ Automate validation in all CI/CD pipelines
- ✅ Use caching for performance optimization
- ✅ Generate and archive validation reports
- ✅ Configure pre-commit hooks for early feedback
- ✅ Enable strict mode for critical branches
- ✅ Provide clear failure messages and resolution steps

---

**Document Metadata:**

```yaml
---
description: Comprehensive guide for integrating metadata validation into CI/CD pipelines
version: 1.0.0
lastUpdated: 2026-01-23
status: ACTIVE
category: deployment
tags:
  - cicd
  - automation
  - github-actions
  - azure-devops
  - gitlab
  - jenkins
  - validation
author: AGENT-018
audience: operators
confidentiality: public
priority: high
reviewSchedule: quarterly
language: en
---
```
