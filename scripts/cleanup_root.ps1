# Root Directory Cleanup Script
# Organizes all loose documentation and config files into proper subdirectories

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project-AI Root Directory Cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be moved" -ForegroundColor Yellow
    Write-Host ""
}

# Define organization structure
$organization = @{
    "docs/archive"      = @(
        "*_COMPLETE.md",
        "*_SUMMARY.md",
        "*_IMPLEMENTATION*.md",
        "*_STATUS.md",
        "*_FINDINGS.md",
        "*_ANALYSIS.md",
        "*_GUIDE.md",
        "*_WHITEPAPER.md",
        "*_QUICKSTART.md",
        "*_QUICK_REF*.md",
        "ACTIONABLE_*.md",
        "ALL_PATCHES*.md",
        "AUTOMATED_*.md",
        "BADGE_*.md",
        "CHECKSUMS.txt",
        "CLEANUP_*.md",
        "CRITICAL_*.md",
        "DEFENSE_*.md",
        "DIAGNOSTIC_*.md",
        "DOMAIN_*.md",
        "ENHANCED_*.md",
        "EXHAUSTIVE_*.md",
        "FINAL_*.md",
        "GITHUB_*.md",
        "GLOBAL_*.md",
        "GOD_TIER_*.md",
        "GUI_*.md",
        "MASTER_*.md",
        "OPERATIONAL_*.md",
        "OWASP_*.md",
        "PACE_*.md",
        "PERPLEXITY_*.md",
        "PRODUCTION_*.md",
        "PROGRAM_*.md",
        "PROJECT_AI_*.md",
        "RELEASE_*.md",
        "REPO_*.md",
        "RESTORATION_*.md",
        "ROBOTIC_*.md",
        "SECURITY_*.md",
        "SOVEREIGN_*.md",
        "STRESS_*.md",
        "TARL_*_COMPLETE.md",
        "TARL_*_IMPLEMENTATION*.md",
        "TARL_*_ENHANCEMENT*.md",
        "TARL_PATCH*.md",
        "TARL_ORCHESTRATION*.md",
        "TEMPORAL_*.md",
        "TESTING_*.md",
        "THIRSTY_LANG_*.md",
        "UNIQUENESS_*.md",
        "WEB_*.md",
        "WIRED_*.md",
        "uniqueness_report.txt",
        "REPO_TREE.txt"
    )
    "docs/architecture" = @(
        "AGENT_MODEL.md",
        "CAPABILITY_MODEL.md",
        "ENGINE_SPEC.md",
        "IDENTITY_ENGINE.md",
        "INTEGRATION_LAYER.md",
        "MODULE_CONTRACTS.md",
        "PROJECT_STRUCTURE.md",
        "STATE_MODEL.md",
        "TARL_ARCHITECTURE.md",
        "WORKFLOW_ENGINE.md",
        "GOD_TIER_DISTRIBUTED_ARCHITECTURE.md",
        "GOD_TIER_INTELLIGENCE_SYSTEM.md",
        "GOD_TIER_PLATFORM_IMPLEMENTATION.md",
        "PLATFORM_COMPATIBILITY.md"
    )
    "docs/security"     = @(
        "CERBERUS_*.md",
        "SECURE-*.md",
        "SECURITY.md",
        "threat-model.md"
    )
    "docs/tarl"         = @(
        "TARL_README.md",
        "TARL_CODE_EXAMPLES.md",
        "TARL_TECHNICAL_DOCUMENTATION.md",
        "TARL_USAGE_SCENARIOS.md",
        "TARL_QUICK_REFERENCE.md",
        "TARL_PRODUCTIVITY_QUICK_REF.md"
    )
    "docs/deployment"   = @(
        "BUILD_AND_DEPLOYMENT.md",
        "DEPLOYMENT.md",
        "DEPLOYMENT_GUIDE.md",
        "DEPLOYMENT_RELEASE_QUICKSTART.md",
        "DEPLOYMENT_SOLUTIONS.md",
        "DEPLOY_CHECKLIST.md",
        "DEPLOY_TO_THIRSTYSPROJECTS.md",
        "DEPLOYMENT_READY_THIRSTYSPROJECTS.md",
        "GRADLE_JAVASCRIPT_SETUP.md",
        "RELEASE_BUILD_GUIDE.md",
        "RELEASE_NOTES_*.md"
    )
    "docs/api"          = @(
        "CONSTITUTION.md",
        "INTEGRATION_PLAN.md",
        "CLI-CODEX.md",
        "TRIUMVIRATE_*.md"
    )
    "docs/whitepapers"  = @(
        "TECHNICAL_WHITE_PAPER.md",
        "TECHNICAL_WHITE_PAPER_SUMMARY.md",
        "WHITEPAPER_SUMMARY.md"
    )
    "config/examples"   = @(
        ".env.example",
        ".env.temporal.example",
        ".pre-commit-config.yaml.example",
        ".projectai.toml.example"
    )
    "config/editor"     = @(
        ".editorconfig",
        ".flake8",
        ".markdownlint.json",
        "pyrightconfig.json"
    )
    "scripts/demo"      = @(
        "demo_*.py"
    )
    "scripts/verify"    = @(
        "verify_*.py",
        "verify-*.sh",
        "verify_gradle_setup.ps1"
    )
    "scripts/install"   = @(
        "install_*.ps1"
    )
    "scripts/build"     = @(
        "build-all-platforms.*",
        "extract_with_permissions.py"
    )
    "scripts/deploy"    = @(
        "deploy_to_thirstysprojects.bat"
    )
    "test-data"         = @(
        "adversarial_stress_tests_2000.json",
        "owasp_compliant_tests.json",
        "white_hatter_scenarios.json",
        "test_results.txt"
    )
    "test-data/audit"   = @(
        "pip-audit-current.json",
        "audit.log"
    )
}

# Keep in root (essential files)
$keepInRoot = @(
    "README.md",
    "LICENSE*",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "CODEOWNERS",
    "QUICK_START.md",
    "Dockerfile",
    "docker-compose*.yml",
    ".dockerignore",
    ".gitignore",
    ".gitattributes",
    ".gitmodules",
    "Makefile",
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
    "pytest.ini",
    "requirements*.txt",
    "requirements*.in",
    "requirements*.lock",
    "package*.json",
    "build.gradle",
    "settings.gradle",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    "MANIFEST.in",
    ".python-version",
    ".pre-commit-config.yaml",
    "mcp.json",
    "app-config.json",
    "users.json",
    "*.code-workspace",
    "*.prompt.yml",
    "bootstrap.py",
    "quickstart.py",
    "start_api.py",
    "test_*.py",
    "ProjectAI-H323-Security-Capability-Profile-extension.py",
    "DEVELOPER_QUICK_REFERENCE.md"
)

$moveCount = 0
$skipCount = 0

foreach ($targetDir in $organization.Keys) {
    $patterns = $organization[$targetDir]
    
    foreach ($pattern in $patterns) {
        $files = Get-ChildItem -Path "." -File -Filter $pattern -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            $fileName = $file.Name
            
            # Check if file should stay in root
            $shouldKeep = $false
            foreach ($keepPattern in $keepInRoot) {
                if ($fileName -like $keepPattern) {
                    $shouldKeep = $true
                    break
                }
            }
            
            if ($shouldKeep) {
                $skipCount++
                Write-Host "  [SKIP] $fileName (essential file)" -ForegroundColor Gray
                continue
            }
            
            # Create target directory
            $fullTargetDir = Join-Path $PWD $targetDir
            if (-not (Test-Path $fullTargetDir)) {
                if (-not $DryRun) {
                    New-Item -ItemType Directory -Path $fullTargetDir -Force | Out-Null
                }
                Write-Host "  [DIR] Created $targetDir" -ForegroundColor Cyan
            }
            
            # Move file
            $targetPath = Join-Path $fullTargetDir $fileName
            if ($DryRun) {
                Write-Host "  [MOVE] $fileName → $targetDir/" -ForegroundColor Yellow
            }
            else {
                if (Test-Path $targetPath) {
                    Write-Host "  [SKIP] $fileName (already exists in target)" -ForegroundColor Gray
                    $skipCount++
                }
                else {
                    Move-Item -Path $file.FullName -Destination $targetPath -Force
                    Write-Host "  [MOVE] $fileName → $targetDir/" -ForegroundColor Green
                    $moveCount++
                }
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files moved: $moveCount" -ForegroundColor Green
Write-Host "Files skipped: $skipCount" -ForegroundColor Yellow
Write-Host ""

if ($DryRun) {
    Write-Host "This was a DRY RUN. Run without -DryRun to apply changes." -ForegroundColor Yellow
}
else {
    Write-Host "Root directory cleaned!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Organized structure:" -ForegroundColor Cyan
    Write-Host "  docs/archive/       - Historical implementation docs" -ForegroundColor White
    Write-Host "  docs/architecture/  - System design & architecture" -ForegroundColor White
    Write-Host "  docs/security/      - Security documentation" -ForegroundColor White
    Write-Host "  docs/tarl/          - TARL reference docs" -ForegroundColor White
    Write-Host "  docs/deployment/    - Deployment guides" -ForegroundColor White
    Write-Host "  docs/api/           - API documentation" -ForegroundColor White
    Write-Host "  docs/whitepapers/   - Technical whitepapers" -ForegroundColor White
    Write-Host "  config/examples/    - Example configurations" -ForegroundColor White
    Write-Host "  config/editor/      - Editor configurations" -ForegroundColor White
    Write-Host "  scripts/demo/       - Demo scripts" -ForegroundColor White
    Write-Host "  scripts/verify/     - Verification scripts" -ForegroundColor White
    Write-Host "  scripts/install/    - Installation scripts" -ForegroundColor White
    Write-Host "  scripts/build/      - Build scripts" -ForegroundColor White
    Write-Host "  scripts/deploy/     - Deployment scripts" -ForegroundColor White
    Write-Host "  test-data/          - Test data & results" -ForegroundColor White
    Write-Host "  test-data/audit/    - Audit reports" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
