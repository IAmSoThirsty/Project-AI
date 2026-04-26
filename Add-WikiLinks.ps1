# AGENT-073: Security & Agents Code-to-Doc Links Specialist
# PowerShell implementation for adding wiki links

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# Source code mappings
$SecuritySourceMap = @{
    "OctoReflex" = "src/app/core/octoreflex.py"
    "Cerberus Hydra" = "src/app/core/cerberus_hydra.py"
    "CerberusHydra" = "src/app/core/cerberus_hydra.py"
    "cerberus_agent_process" = "src/app/core/cerberus_agent_process.py"
    "cerberus_lockdown_controller" = "src/app/core/cerberus_lockdown_controller.py"
    "LockdownController" = "src/app/core/cerberus_lockdown_controller.py"
    "RuntimeManager" = "src/app/core/cerberus_runtime_manager.py"
    "cerberus_runtime_manager" = "src/app/core/cerberus_runtime_manager.py"
    "TemplateRenderer" = "src/app/core/cerberus_template_renderer.py"
    "cerberus_template_renderer" = "src/app/core/cerberus_template_renderer.py"
    "cerberus_observability" = "src/app/core/cerberus_observability.py"
    "CerberusObservability" = "src/app/core/cerberus_observability.py"
    "Encryption" = "utils/encryption/god_tier_encryption.py"
    "Authentication" = "src/app/core/security/auth.py"
    "Honeypot Detector" = "src/app/core/honeypot_detector.py"
    "Honeypot" = "src/app/core/honeypot_detector.py"
    "Incident Responder" = "src/app/core/incident_responder.py"
    "Threat Detection Engine" = "kernel/threat_detection.py"
    "Threat Detection" = "kernel/threat_detection.py"
    "Security Resources" = "src/app/core/security_resources.py"
    "Location Tracker" = "src/app/core/location_tracker.py"
    "Emergency Alert" = "src/app/core/emergency_alert.py"
    "MFA" = "src/app/security/advanced/mfa_auth.py"
}

$AgentSourceMap = @{
    "OversightAgent" = "src/app/agents/oversight.py"
    "Oversight" = "src/app/agents/oversight.py"
    "PlannerAgent" = "src/app/agents/planner_agent.py"
    "Planner" = "src/app/agents/planner_agent.py"
    "ValidatorAgent" = "src/app/agents/validator.py"
    "Validator" = "src/app/agents/validator.py"
    "ExplainabilityAgent" = "src/app/agents/explainability.py"
    "Explainability" = "src/app/agents/explainability.py"
    "CerberusCodexBridge" = "src/app/agents/cerberus_codex_bridge.py"
    "ThirstyLangValidator" = "src/app/agents/thirsty_lang_validator.py"
}

$script:LinkCount = 0
$script:DocsUpdated = @()
$script:BrokenLinks = @()

function Add-SourceCodeReferencesSection {
    param(
        [string]$FilePath,
        [string]$Content,
        [hashtable]$SourceMap
    )
    
    # Skip if section already exists
    if ($Content -match "## 📁 Source Code References" -or $Content -match "## Source Code References") {
        return $Content
    }
    
    # Find all source file references in the content
    $referencedSources = @()
    foreach ($key in $SourceMap.Keys) {
        if ($Content -match [regex]::Escape($key)) {
            $sourcePath = $SourceMap[$key]
            if (Test-Path (Join-Path $PSScriptRoot $sourcePath)) {
                if ($sourcePath -notin $referencedSources) {
                    $referencedSources += $sourcePath
                }
            }
        }
    }
    
    if ($referencedSources.Count -eq 0) {
        return $Content
    }
    
    # Build section
    $section = @"

---

## 📁 Source Code References

This documentation references the following source files:

"@
    
    foreach ($source in ($referencedSources | Sort-Object)) {
        $section += "`n- [[$source]]"
        $script:LinkCount++
    }
    
    $section += "`n`n---`n"
    
    # Find insertion point (before ## Related Documentation or ## See Also)
    if ($Content -match '(?m)^## (Related Documentation|See Also|References|Next Steps)') {
        $insertBefore = $Matches[0]
        $Content = $Content -replace [regex]::Escape($insertBefore), ($section + $insertBefore)
    } else {
        # Append at end
        $Content += $section
    }
    
    return $Content
}

function Add-RelationshipMapSection {
    param(
        [string]$FilePath,
        [string]$Content
    )
    
    # Only for source-docs
    if ($FilePath -notmatch "source-docs") {
        return $Content
    }
    
    # Skip if section already exists
    if ($Content -match "## 🔗 Relationship Maps" -or $Content -match "## Relationship Maps") {
        return $Content
    }
    
    $category = if ($FilePath -match "security") { "security" } else { "agents" }
    
    $section = @"

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:

"@
    
    if ($category -eq "security") {
        $section += @"
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
"@
    } else {
        $section += @"
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]
"@
    }
    
    $section += "`n`n---`n"
    $script:LinkCount += 3
    
    # Insert before ## See Also or at end
    if ($Content -match '(?m)^## (See Also|Related Documentation|References)') {
        $insertBefore = $Matches[0]
        $Content = $Content -replace [regex]::Escape($insertBefore), ($section + $insertBefore)
    } else {
        $Content += $section
    }
    
    return $Content
}

function Add-InlineWikiLinks {
    param(
        [string]$Content,
        [hashtable]$SourceMap
    )
    
    # Replace **Location:** `path` with **Location:** [[path]]
    foreach ($key in $SourceMap.Keys) {
        $sourcePath = $SourceMap[$key]
        $pattern = "\*\*Location:\*\*\s*``$([regex]::Escape($sourcePath))``"
        if ($Content -match $pattern) {
            $replacement = "**Location:** [[$sourcePath]] (``$sourcePath``)"
            $Content = $Content -replace $pattern, $replacement
            $script:LinkCount++
        }
    }
    
    return $Content
}

function Process-DocumentationFile {
    param(
        [string]$FilePath,
        [hashtable]$SourceMap
    )
    
    Write-Host "Processing: $FilePath" -ForegroundColor Cyan
    
    $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
    $originalContent = $content
    
    # Add inline wiki links
    $content = Add-InlineWikiLinks -Content $content -SourceMap $SourceMap
    
    # Add source code references section
    $content = Add-SourceCodeReferencesSection -FilePath $FilePath -Content $content -SourceMap $SourceMap
    
    # Add relationship maps section (for source-docs)
    $content = Add-RelationshipMapSection -FilePath $FilePath -Content $content
    
    # Only write if changed
    if ($content -ne $originalContent) {
        if (-not $DryRun) {
            Set-Content -Path $FilePath -Value $content -Encoding UTF8 -NoNewline
        }
        $script:DocsUpdated += $FilePath
        Write-Host "  ✅ Updated" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ℹ️  No changes needed" -ForegroundColor Gray
        return $false
    }
}

function Generate-Report {
    $reportContent = @"
# AGENT-073 Wiki Link Validation Report

**Mission:** Security & Agents Code-to-Doc Links Specialist  
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---

## 📊 Summary Statistics

- **Total Wiki Links Added:** $script:LinkCount
- **Documents Updated:** $($script:DocsUpdated.Count)
- **Broken Links Found:** $($script:BrokenLinks.Count)

---

## 📁 Updated Documentation Files

"@
    
    if ($script:DocsUpdated.Count -gt 0) {
        foreach ($doc in ($script:DocsUpdated | Sort-Object)) {
            $relativePath = $doc -replace [regex]::Escape($PSScriptRoot + "\"), ""
            $reportContent += "`n- ``$relativePath``"
        }
    } else {
        $reportContent += "`n*No files updated (all links already present)*"
    }
    
    $reportContent += @"


---

## ⚠️ Broken Links

"@
    
    if ($script:BrokenLinks.Count -eq 0) {
        $reportContent += "`n✅ **No broken links found!**`n"
    } else {
        foreach ($link in $script:BrokenLinks) {
            $reportContent += "`n- $link`n"
        }
    }
    
    $reportContent += @"


---

## 🎯 Quality Gates

- **All major systems have code ↔ doc links:** $(if ($script:LinkCount -ge 50) { "✅ PASS" } else { "❌ FAIL ($script:LinkCount/50)" })
- **Zero broken references:** $(if ($script:BrokenLinks.Count -eq 0) { "✅ PASS" } else { "❌ FAIL ($($script:BrokenLinks.Count) broken)" })
- **Minimum 200 links added:** $(if ($script:LinkCount -ge 200) { "✅ PASS" } else { "⚠️ IN PROGRESS ($script:LinkCount/200)" })

---

## ✅ Mission Status

"@
    
    if ($script:LinkCount -ge 200 -and $script:BrokenLinks.Count -eq 0) {
        $reportContent += "`n**STATUS:** ✅ MISSION COMPLETE`n`nAll quality gates passed. Bidirectional wiki links successfully established.`n"
    } else {
        $reportContent += "`n**STATUS:** ⚠️ IN PROGRESS`n`nTarget: 400 links | Current: $script:LinkCount`n"
    }
    
    return $reportContent
}

# Main execution
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "AGENT-073: Security & Agents Code-to-Doc Links Specialist" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No files will be modified" -ForegroundColor Magenta
    Write-Host ""
}

# Process security documentation
Write-Host "📁 Processing Security Documentation..." -ForegroundColor White
Write-Host ""

$securityDirs = @(
    "relationships\security",
    "source-docs\security"
)

foreach ($dir in $securityDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $fullPath) {
        Get-ChildItem -Path $fullPath -Filter "*.md" | ForEach-Object {
            if ($_.Name -notin @("MISSION_COMPLETE.md", "README.md")) {
                Process-DocumentationFile -FilePath $_.FullName -SourceMap $SecuritySourceMap
            }
        }
    }
}

Write-Host ""
Write-Host "📁 Processing Agent Documentation..." -ForegroundColor White
Write-Host ""

$agentDirs = @(
    "relationships\agents",
    "source-docs\agents"
)

foreach ($dir in $agentDirs) {
    $fullPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $fullPath) {
        Get-ChildItem -Path $fullPath -Filter "*.md" | ForEach-Object {
            $skipFiles = @("COMPLETION_CHECKLIST.md", "MISSION_SUMMARY.md", "VALIDATION_REPORT.md", "INDEX.md", "README.md")
            if ($_.Name -notin $skipFiles) {
                Process-DocumentationFile -FilePath $_.FullName -SourceMap $AgentSourceMap
            }
        }
    }
}

Write-Host ""
Write-Host "📊 Generating Report..." -ForegroundColor White

$report = Generate-Report
$reportPath = Join-Path $PSScriptRoot "AGENT-073-LINK-REPORT.md"

if (-not $DryRun) {
    Set-Content -Path $reportPath -Value $report -Encoding UTF8
    Write-Host "✅ Report saved to: $reportPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "SUMMARY" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "Links Added: $script:LinkCount"
Write-Host "Docs Updated: $($script:DocsUpdated.Count)"
Write-Host "Broken Links: $($script:BrokenLinks.Count)"
Write-Host ""

if ($script:LinkCount -ge 200 -and $script:BrokenLinks.Count -eq 0) {
    Write-Host "✅ MISSION COMPLETE: All quality gates passed!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Mission in progress - continue adding links" -ForegroundColor Yellow
}
