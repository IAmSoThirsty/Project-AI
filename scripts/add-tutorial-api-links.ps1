<#
.SYNOPSIS
    Batch add API reference links to tutorial/guide documentation files.

.DESCRIPTION
    This script systematically adds wiki links from tutorial files to API
    documentation, creating comprehensive navigation between guides and
    implementation details. Part of AGENT-083 mission.

.PARAMETER DryRun
    Preview changes without modifying files

.PARAMETER TutorialPattern
    Pattern to match tutorial files (default: "*QUICKSTART*.md,*GUIDE*.md")

.EXAMPLE
    .\add-tutorial-api-links.ps1 -DryRun
    Preview changes without modification

.EXAMPLE
    .\add-tutorial-api-links.ps1
    Execute all changes

.NOTES
    Author: AGENT-083 (Tutorial to API Links Specialist)
    Mission: Phase 5 Cross-Linking
    Target: ~400 bidirectional wiki links
#>

param(
    [switch]$DryRun = $false,
    [string]$DocsPath = "T:\Project-AI-main\docs\developer",
    [int]$LinksTarget = 400
)

# Color output helpers
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Warning { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }

# Module to API mapping
$apiModuleMap = @{
    # Core AI Systems (src/app/core/ai_systems.py)
    "AIPersona" = @{
        module = "core/ai_systems.py"
        description = "Personality management and mood tracking"
        keywords = @("personality", "trait", "mood", "persona", "emotion")
    }
    "FourLaws" = @{
        module = "core/ai_systems.py"
        description = "Ethical validation framework (Asimov's Laws)"
        keywords = @("ethics", "four laws", "asimov", "validate action", "harm")
    }
    "MemoryExpansionSystem" = @{
        module = "core/ai_systems.py"
        description = "Conversation logging and knowledge base"
        keywords = @("memory", "knowledge base", "conversation", "persistent")
    }
    "LearningRequestManager" = @{
        module = "core/ai_systems.py"
        description = "Human-in-the-loop learning approval"
        keywords = @("learning request", "black vault", "approval", "fingerprint")
    }
    "CommandOverride" = @{
        module = "core/ai_systems.py"
        description = "Basic override system"
        keywords = @("override", "master password", "safety protocol")
    }
    "PluginManager" = @{
        module = "core/ai_systems.py"
        description = "Plugin loading and management"
        keywords = @("plugin", "enable", "disable", "load plugin")
    }
    
    # User Management
    "UserManager" = @{
        module = "core/user_manager.py"
        description = "User authentication and profiles"
        keywords = @("user", "authentication", "login", "password", "bcrypt")
    }
    
    # Extended Systems
    "CommandOverrideSystem" = @{
        module = "core/command_override.py"
        description = "Extended master password system with 10+ safety protocols"
        keywords = @("command override", "master password", "audit log", "protocol")
    }
    "IntelligenceEngine" = @{
        module = "core/intelligence_engine.py"
        description = "OpenAI chat integration"
        keywords = @("openai", "gpt", "chat", "response", "intelligence")
    }
    "ImageGenerator" = @{
        module = "core/image_generator.py"
        description = "Dual-backend image generation (HF + OpenAI)"
        keywords = @("image generation", "stable diffusion", "dall-e", "huggingface")
    }
    "DataAnalyzer" = @{
        module = "core/data_analysis.py"
        description = "CSV/XLSX/JSON analysis with clustering"
        keywords = @("data analysis", "csv", "xlsx", "json", "clustering")
    }
    "SecurityResourceFetcher" = @{
        module = "core/security_resources.py"
        description = "GitHub API security resources"
        keywords = @("security", "ctf", "github", "resources")
    }
    "LocationTracker" = @{
        module = "core/location_tracker.py"
        description = "IP geolocation and GPS tracking"
        keywords = @("location", "geolocation", "gps", "tracking")
    }
    "EmergencyAlert" = @{
        module = "core/emergency_alert.py"
        description = "Emergency contact and email alerts"
        keywords = @("emergency", "alert", "email", "contact")
    }
    
    # GUI Modules
    "LeatherBookInterface" = @{
        module = "gui/leather_book_interface.py"
        description = "Main application window (PyQt6)"
        keywords = @("main window", "application", "interface", "login")
    }
    "LeatherBookDashboard" = @{
        module = "gui/leather_book_dashboard.py"
        description = "6-zone dashboard layout"
        keywords = @("dashboard", "6-zone", "layout", "proactive")
    }
    "PersonaPanel" = @{
        module = "gui/persona_panel.py"
        description = "AI configuration UI (4 tabs)"
        keywords = @("persona panel", "configuration", "ui", "sliders")
    }
    "ImageGenerationUI" = @{
        module = "gui/image_generation.py"
        description = "Image generation interface"
        keywords = @("image ui", "generation interface", "prompt input")
    }
    
    # Agent Modules
    "Oversight" = @{
        module = "agents/oversight.py"
        description = "Action oversight and safety validation"
        keywords = @("oversight", "action", "safety", "monitor")
    }
    "Planner" = @{
        module = "agents/planner.py"
        description = "Task planning and decomposition"
        keywords = @("planner", "planning", "decomposition", "task")
    }
    "Validator" = @{
        module = "agents/validator.py"
        description = "Input/output validation"
        keywords = @("validator", "validation", "input", "output")
    }
    "Explainability" = @{
        module = "agents/explainability.py"
        description = "Decision explanation generation"
        keywords = @("explainability", "explanation", "decision", "reasoning")
    }
}

# Statistics
$stats = @{
    FilesProcessed = 0
    LinksAdded = 0
    ApiSectionsAdded = 0
    ErrorsFound = 0
}

function Add-ApiLink {
    param(
        [string]$FilePath,
        [string]$ModuleName,
        [string]$Context
    )
    
    if (-not $apiModuleMap.ContainsKey($ModuleName)) {
        Write-Warning "Unknown module: $ModuleName"
        return $null
    }
    
    $module = $apiModuleMap[$ModuleName]
    $link = "[[API_QUICK_REFERENCE#$($module.module)|$ModuleName]]"
    
    return $link
}

function Add-ApiReferenceSection {
    param(
        [string]$FilePath,
        [string[]]$Modules
    )
    
    $apiSection = @"

---

## API Reference

This section provides direct links to the API documentation for modules referenced in this guide.

### Core Modules

"@
    
    foreach ($moduleName in $Modules) {
        if ($apiModuleMap.ContainsKey($moduleName)) {
            $module = $apiModuleMap[$moduleName]
            $link = "[[API_QUICK_REFERENCE#$($module.module)|$moduleName]]"
            $apiSection += @"

- **$link** - $($module.description)
"@
        }
    }
    
    $apiSection += @"


### Related Documentation

- **[[API_QUICK_REFERENCE]]** - Complete API reference (339 modules)
- **[[PROGRAM_SUMMARY]]** - Comprehensive architecture documentation
- **[[DEVELOPER_QUICK_REFERENCE]]** - Developer commands and workflows
- **[[ARCHITECTURE_QUICK_REF]]** - Visual architecture diagrams

---

**Quick Navigation**:
- [[API_QUICK_REFERENCE|→ Full API Reference]]
- [[PROGRAM_SUMMARY|→ Complete Documentation]]
"@
    
    return $apiSection
}

function Process-TutorialFile {
    param([string]$FilePath)
    
    Write-Info "Processing: $((Split-Path -Leaf $FilePath))"
    
    $content = Get-Content -Path $FilePath -Raw
    $originalContent = $content
    $modulesReferenced = @()
    $linksAdded = 0
    
    # Detect modules by keyword matching
    foreach ($moduleName in $apiModuleMap.Keys) {
        $module = $apiModuleMap[$moduleName]
        foreach ($keyword in $module.keywords) {
            if ($content -match [regex]::Escape($keyword)) {
                if ($modulesReferenced -notcontains $moduleName) {
                    $modulesReferenced += $moduleName
                }
            }
        }
    }
    
    # Add API links to first mention of each module
    foreach ($moduleName in $modulesReferenced) {
        $module = $apiModuleMap[$moduleName]
        $link = "[[API_QUICK_REFERENCE#$($module.module)|$moduleName]]"
        
        # Find first occurrence and add link
        foreach ($keyword in $module.keywords) {
            $pattern = "(?<![[])\b$keyword\b(?![])])"
            if ($content -match $pattern) {
                # Replace first occurrence only
                $content = $content -replace $pattern, "$keyword ($link)", 1
                $linksAdded++
                break
            }
        }
    }
    
    # Add API Reference section if not present
    if ($content -notmatch "## API Reference" -and $modulesReferenced.Count -gt 0) {
        $apiSection = Add-ApiReferenceSection -FilePath $FilePath -Modules $modulesReferenced
        
        # Insert before final line (usually version/status)
        if ($content -match "---\s*$") {
            $content = $content -replace "(---\s*)$", "$apiSection`n`n`$1"
        }
        else {
            $content += "`n$apiSection"
        }
        
        $stats.ApiSectionsAdded++
    }
    
    # Write changes
    if ($content -ne $originalContent) {
        if (-not $DryRun) {
            Set-Content -Path $FilePath -Value $content -NoNewline
            Write-Success "Updated: $((Split-Path -Leaf $FilePath)) (+$linksAdded links, $($modulesReferenced.Count) modules)"
        }
        else {
            Write-Info "Would update: $((Split-Path -Leaf $FilePath)) (+$linksAdded links, $($modulesReferenced.Count) modules)"
        }
        
        $stats.LinksAdded += $linksAdded
        $stats.FilesProcessed++
    }
    else {
        Write-Info "No changes needed: $((Split-Path -Leaf $FilePath))"
    }
}

# Main execution
Write-Host "`n═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  AGENT-083: Tutorial to API Links Specialist" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Magenta

if ($DryRun) {
    Write-Warning "DRY RUN MODE - No files will be modified`n"
}

# Find all tutorial/guide files
$tutorialFiles = @()
$tutorialFiles += Get-ChildItem -Path "$DocsPath" -Filter "*QUICKSTART*.md" -Recurse
$tutorialFiles += Get-ChildItem -Path "$DocsPath" -Filter "*GUIDE*.md" -Recurse
$tutorialFiles += Get-ChildItem -Path "$DocsPath" -Filter "README.md" -Recurse
$tutorialFiles = $tutorialFiles | Sort-Object -Unique -Property FullName

Write-Info "Found $($tutorialFiles.Count) tutorial/guide files"
Write-Info "Target links: $LinksTarget"
Write-Info "API modules available: $($apiModuleMap.Count)`n"

# Process each file
foreach ($file in $tutorialFiles) {
    try {
        Process-TutorialFile -FilePath $file.FullName
    }
    catch {
        Write-Error "Error processing $($file.Name): $_"
        $stats.ErrorsFound++
    }
}

# Report statistics
Write-Host "`n═══════════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  Mission Statistics" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Magenta

Write-Info "Files Processed: $($stats.FilesProcessed)"
Write-Success "Links Added: $($stats.LinksAdded) / $LinksTarget ($(([math]::Round(($stats.LinksAdded / $LinksTarget) * 100, 1)))%)"
Write-Success "API Sections Added: $($stats.ApiSectionsAdded)"

if ($stats.ErrorsFound -gt 0) {
    Write-Error "Errors Encountered: $($stats.ErrorsFound)"
}
else {
    Write-Success "Errors Encountered: 0"
}

# Progress assessment
$coverage = ($stats.LinksAdded / $LinksTarget) * 100
if ($coverage -ge 95) {
    Write-Host "`n✅ MISSION STATUS: COMPLETE (≥95% coverage)" -ForegroundColor Green
}
elseif ($coverage -ge 75) {
    Write-Host "`n🚧 MISSION STATUS: IN PROGRESS (≥75% coverage)" -ForegroundColor Yellow
}
else {
    Write-Host "`n🔴 MISSION STATUS: NEEDS WORK (<75% coverage)" -ForegroundColor Red
}

if ($DryRun) {
    Write-Host "`nTo apply changes, run without -DryRun flag`n" -ForegroundColor Cyan
}
else {
    Write-Host "`n✓ Changes applied successfully`n" -ForegroundColor Green
}
