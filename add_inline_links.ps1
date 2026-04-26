# AGENT-076: Inline Wiki Links Addition
# Adds inline wiki links throughout documentation

$replacements = @(
    # Core AI System references
    @{ Pattern = '(?<![\[])\bFourLaws\.validate_action\(\)'; Replacement = '[[relationships/core-ai/01-FourLaws-Relationship-Map|FourLaws]].validate_action()' },
    @{ Pattern = '(?<![\[])\bAIPersona system\b'; Replacement = '[[relationships/core-ai/02-AIPersona-Relationship-Map|AIPersona system]]' },
    @{ Pattern = '(?<![\[])\bMemoryExpansionSystem\b'; Replacement = '[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map|MemoryExpansionSystem]]' },
    @{ Pattern = '(?<![\[])\bLearningRequestManager\b'; Replacement = '[[relationships/core-ai/04-LearningRequestManager-Relationship-Map|LearningRequestManager]]' },
    @{ Pattern = '(?<![\[])\bPluginManager\b(?! \()'; Replacement = '[[relationships/core-ai/05-PluginManager-Relationship-Map|PluginManager]]' },
    @{ Pattern = '(?<![\[])\bCommandOverride system\b'; Replacement = '[[relationships/core-ai/06-CommandOverride-Relationship-Map|CommandOverride system]]' },
    
    # Governance references
    @{ Pattern = '(?<![\[])\bPipeline System\b'; Replacement = '[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]' },
    @{ Pattern = '(?<![\[])\bgovernance pipeline\b'; Replacement = '[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|governance pipeline]]' },
    @{ Pattern = '(?<![\[])\bPolicy Enforcement Points?\b'; Replacement = '[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS|Policy Enforcement Points]]' },
    @{ Pattern = '(?<![\[])\bauthorization flows?\b'; Replacement = '[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]' },
    @{ Pattern = '(?<![\[])\baudit trail\b'; Replacement = '[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]' },
    @{ Pattern = '(?<![\[])\baudit log\b'; Replacement = '[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit log]]' },
    
    # Constitutional references
    @{ Pattern = '(?<![\[])\bConstitutional AI\b'; Replacement = '[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]' },
    @{ Pattern = '(?<![\[])\bPlanetary Defense Core\b'; Replacement = '[[relationships/constitutional/01_constitutional_systems_overview|Planetary Defense Core]]' },
    @{ Pattern = '(?<![\[])\benforcement chains?\b'; Replacement = '[[relationships/constitutional/02_enforcement_chains|enforcement chains]]' },
    @{ Pattern = '(?<![\[])\bethics validation\b'; Replacement = '[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]' },
    @{ Pattern = '(?<![\[])\bBlack Vault\b'; Replacement = '[[relationships/core-ai/04-LearningRequestManager-Relationship-Map|Black Vault]]' }
)

$files = @()
$files += Get-ChildItem "T:\Project-AI-main\relationships\core-ai\*.md" -Exclude "README.md","MISSION_COMPLETE.md"
$files += Get-ChildItem "T:\Project-AI-main\relationships\governance\*.md" -Exclude "README.md","MISSION_COMPLETE.md"
$files += Get-ChildItem "T:\Project-AI-main\relationships\constitutional\*.md" -Exclude "README.md"

$totalReplacements = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    $fileReplacements = 0
    
    foreach ($rep in $replacements) {
        $newContent = $content -replace $rep.Pattern, $rep.Replacement
        if ($newContent -ne $content) {
            $matches = ([regex]::Matches($content, $rep.Pattern)).Count
            $fileReplacements += $matches
            $content = $newContent
        }
    }
    
    if ($content -ne $originalContent) {
        Set-Content $file.FullName -Value $content -NoNewline
        $totalReplacements += $fileReplacements
        Write-Host "✓ $($file.Name): $fileReplacements inline links added" -ForegroundColor Green
    }
}

Write-Host "`n✅ Total inline links added: $totalReplacements" -ForegroundColor Cyan
