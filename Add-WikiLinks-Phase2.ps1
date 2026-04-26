# AGENT-073 Phase 2: Add Additional Cross-Reference Links
# Comprehensive inline linking for system mentions

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

# Additional inline link patterns (case-sensitive to avoid duplicates)
$InlineLinkPatterns = @{
    # Security Systems
    "HoneypotDetector" = "src/app/core/honeypot_detector.py"
    "ThreatDetectionEngine" = "kernel/threat_detection.py"
    "IncidentResponder" = "src/app/core/incident_responder.py"
    "SecurityResources" = "src/app/core/security_resources.py"
    "LocationTracker" = "src/app/core/location_tracker.py"
    "EmergencyAlert" = "src/app/core/emergency_alert.py"
    "AuthenticationSystem" = "src/app/core/security/auth.py"
    
    # Cerberus Components
    "LockdownController" = "src/app/core/cerberus_lockdown_controller.py"
    "RuntimeManager" = "src/app/core/cerberus_runtime_manager.py"
    "TemplateRenderer" = "src/app/core/cerberus_template_renderer.py"
    "AgentProcess" = "src/app/core/cerberus_agent_process.py"
    "CerberusObservability" = "src/app/core/cerberus_observability.py"
    
    # Agent Systems
    "CognitionKernel" = "src/app/core/cognition_kernel.py"
    "KernelRoutedAgent" = "src/app/core/kernel_integration.py"
    "CouncilHub" = "src/app/core/council_hub.py"
    "Triumvirate" = "src/app/core/triumvirate.py"
    "FourLaws" = "src/app/core/ai_systems.py"
    "AIPersona" = "src/app/core/ai_systems.py"
    "MemoryExpansionSystem" = "src/app/core/ai_systems.py"
    "OversightAgent" = "src/app/agents/oversight.py"
    "PlannerAgent" = "src/app/agents/planner_agent.py"
    "ValidatorAgent" = "src/app/agents/validator.py"
    "ExplainabilityAgent" = "src/app/agents/explainability.py"
}

# Documentation cross-references
$DocCrossRefs = @{
    "relationships\security\01_security_system_overview.md" = @(
        "relationships\security\02_threat_models.md"
        "relationships\security\03_defense_layers.md"
        "relationships\security\04_incident_response_chains.md"
    )
    "relationships\security\02_threat_models.md" = @(
        "relationships\security\01_security_system_overview.md"
        "relationships\security\03_defense_layers.md"
    )
    "relationships\security\03_defense_layers.md" = @(
        "relationships\security\01_security_system_overview.md"
        "relationships\security\02_threat_models.md"
    )
    "source-docs\security\01-cerberus-hydra-defense.md" = @(
        "source-docs\security\02-lockdown-controller.md"
        "source-docs\security\03-runtime-manager.md"
        "source-docs\security\04-observability-metrics.md"
    )
    "source-docs\agents\oversight_agent.md" = @(
        "source-docs\agents\planner_agent.md"
        "source-docs\agents\validator_agent.md"
        "source-docs\agents\explainability_agent.md"
    )
    "source-docs\agents\planner_agent.md" = @(
        "source-docs\agents\oversight_agent.md"
        "source-docs\agents\validator_agent.md"
    )
}

$script:LinkCount = 0
$script:DocsUpdated = @()

function Add-InlineSystemLinks {
    param(
        [string]$Content,
        [string]$FilePath
    )
    
    $modified = $false
    
    foreach ($keyword in $InlineLinkPatterns.Keys) {
        $sourcePath = $InlineLinkPatterns[$keyword]
        
        # Skip if this exact wiki link already exists
        if ($Content -match [regex]::Escape("[[$sourcePath]]")) {
            continue
        }
        
        # Skip if this keyword is part of an existing wiki link
        if ($Content -match "\[\[[^\]]*$([regex]::Escape($keyword))") {
            continue
        }
        
        # Pattern: keyword not already in backticks or wiki links
        $pattern = "(?<!\[)(?<!`)\b$([regex]::Escape($keyword))\b(?!`|]|\|)"
        
        if ($Content -match $pattern) {
            # Replace first occurrence with wiki link
            $wikiLink = "[[$sourcePath|$keyword]]"
            $Content = $Content -replace $pattern, $wikiLink, 1
            $script:LinkCount++
            $modified = $true
        }
    }
    
    return @{
        Content = $Content
        Modified = $modified
    }
}

function Add-RelatedDocumentationLinks {
    param(
        [string]$Content,
        [string]$FilePath
    )
    
    $relativePath = $FilePath -replace [regex]::Escape($PSScriptRoot + "\"), ""
    
    # Check if we have cross-refs for this doc
    if (-not $DocCrossRefs.ContainsKey($relativePath)) {
        return $Content
    }
    
    # Skip if section already exists
    if ($Content -match "## Related Relationship Documentation" -or $Content -match "## Related Agent Documentation") {
        return $Content
    }
    
    $sectionTitle = if ($relativePath -match "security") {
        "## Related Security Documentation"
    } else {
        "## Related Agent Documentation"
    }
    
    $section = @"

---

$sectionTitle

"@
    
    foreach ($relatedDoc in $DocCrossRefs[$relativePath]) {
        $docName = [System.IO.Path]::GetFileNameWithoutExtension($relatedDoc)
        $displayName = $docName -replace "_", " " -replace "-", " "
        $section += "`n- [[$relatedDoc|$displayName]]"
        $script:LinkCount++
    }
    
    $section += "`n`n---`n"
    
    # Insert before ## Source Code References or at end
    if ($Content -match '(?m)^## 📁 Source Code References') {
        $insertBefore = $Matches[0]
        $Content = $Content -replace [regex]::Escape($insertBefore), ($section + $insertBefore)
    } elseif ($Content -match '(?m)^## (See Also|References)') {
        $insertBefore = $Matches[0]
        $Content = $Content -replace [regex]::Escape($insertBefore), ($section + $insertBefore)
    } else {
        $Content += $section
    }
    
    return $Content
}

function Add-ImplementationBacklinks {
    param(
        [string]$Content,
        [string]$FilePath
    )
    
    # Only for source-docs files
    if ($FilePath -notmatch "source-docs") {
        return $Content
    }
    
    # Skip if backlink section already exists
    if ($Content -match "## 📚 Referenced In Relationship Maps") {
        return $Content
    }
    
    $category = if ($FilePath -match "security") { "security" } else { "agents" }
    
    $section = @"

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:

"@
    
    if ($category -eq "security") {
        $section += @"
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]
"@
        $script:LinkCount += 7
    } else {
        $section += @"
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration Architecture]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]
"@
        $script:LinkCount += 3
    }
    
    $section += "`n`n---`n"
    
    # Insert before ## See Also or at end
    if ($Content -match '(?m)^## (See Also|Related|References)') {
        $insertBefore = $Matches[0]
        $Content = $Content -replace [regex]::Escape($insertBefore), ($section + $insertBefore)
    } else {
        $Content += $section
    }
    
    return $Content
}

function Process-File {
    param(
        [string]$FilePath
    )
    
    Write-Host "Processing: $FilePath" -ForegroundColor Cyan
    
    $content = Get-Content -Path $FilePath -Raw -Encoding UTF8
    $originalContent = $content
    
    # Add inline system links
    $result = Add-InlineSystemLinks -Content $content -FilePath $FilePath
    $content = $result.Content
    
    # Add related documentation links
    $content = Add-RelatedDocumentationLinks -Content $content -FilePath $FilePath
    
    # Add implementation backlinks
    $content = Add-ImplementationBacklinks -Content $content -FilePath $FilePath
    
    if ($content -ne $originalContent) {
        if (-not $DryRun) {
            Set-Content -Path $FilePath -Value $content -Encoding UTF8 -NoNewline
        }
        $script:DocsUpdated += $FilePath
        Write-Host "  ✅ Updated" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  ℹ️  No additional changes" -ForegroundColor Gray
        return $false
    }
}

# Main execution
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "AGENT-073 Phase 2: Additional Cross-Reference Links" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE" -ForegroundColor Magenta
    Write-Host ""
}

# Process all documentation files
$allDocs = @()
$allDocs += Get-ChildItem -Path (Join-Path $PSScriptRoot "relationships\security") -Filter "*.md" | Where-Object { $_.Name -notin @("MISSION_COMPLETE.md", "README.md") }
$allDocs += Get-ChildItem -Path (Join-Path $PSScriptRoot "source-docs\security") -Filter "*.md" | Where-Object { $_.Name -ne "README.md" }
$allDocs += Get-ChildItem -Path (Join-Path $PSScriptRoot "relationships\agents") -Filter "*.md" | Where-Object { $_.Name -ne "README.md" }
$allDocs += Get-ChildItem -Path (Join-Path $PSScriptRoot "source-docs\agents") -Filter "*.md" | Where-Object { $_.Name -notin @("COMPLETION_CHECKLIST.md", "MISSION_SUMMARY.md", "VALIDATION_REPORT.md", "INDEX.md", "README.md") }

foreach ($doc in $allDocs) {
    Process-File -FilePath $doc.FullName
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "PHASE 2 SUMMARY" -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow
Write-Host "Additional Links Added: $script:LinkCount"
Write-Host "Additional Docs Updated: $($script:DocsUpdated.Count)"
Write-Host ""

if ($script:LinkCount -ge 100) {
    Write-Host "✅ Phase 2 Complete - Substantial additional linking achieved" -ForegroundColor Green
} else {
    Write-Host "⚠️ Phase 2 Complete - Some additional links added" -ForegroundColor Yellow
}
