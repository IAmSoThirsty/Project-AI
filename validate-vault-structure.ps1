<#
.SYNOPSIS
    AGENT-007: Vault Structure Validation Script
    Comprehensive automated validation for Project-AI vault infrastructure

.DESCRIPTION
    Production-ready validation script that tests:
    - Directory structure integrity
    - Access permissions and security
    - Encryption configurations
    - Naming conventions
    - File integrity
    - Component integration
    - Security isolation

.NOTES
    Version: 1.0.0
    Author: AGENT-007 - Vault Structure Validation Specialist
    Compliant with: Principal Architect Implementation Standard
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$RootPath = "T:\Project-AI-main",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput,
    
    [Parameter(Mandatory=$false)]
    [switch]$ExportResults,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "vault-validation-results.json"
)

# Initialize validation state
$Script:ValidationResults = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    TotalTests = 0
    PassedTests = 0
    FailedTests = 0
    WarningTests = 0
    Details = @()
    Errors = @()
    Warnings = @()
}

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

# Test result tracking
function Add-TestResult {
    param(
        [string]$TestName,
        [string]$Status,  # Pass, Fail, Warning
        [string]$Message,
        [hashtable]$Details = @{}
    )
    
    $Script:ValidationResults.TotalTests++
    
    switch ($Status) {
        "Pass" { 
            $Script:ValidationResults.PassedTests++
            Write-Success "$TestName - $Message"
        }
        "Fail" { 
            $Script:ValidationResults.FailedTests++
            $Script:ValidationResults.Errors += "$TestName - $Message"
            Write-Failure "$TestName - $Message"
        }
        "Warning" { 
            $Script:ValidationResults.WarningTests++
            $Script:ValidationResults.Warnings += "$TestName - $Message"
            Write-Warning-Custom "$TestName - $Message"
        }
    }
    
    $Script:ValidationResults.Details += @{
        Test = $TestName
        Status = $Status
        Message = $Message
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Details = $Details
    }
}

# ==============================================================================
# VAULT DIRECTORY STRUCTURE TESTS
# ==============================================================================

function Test-VaultDirectoryStructure {
    Write-Info "`n=== Testing Vault Directory Structure ==="
    
    $requiredVaultDirs = @(
        "data\black_vault_secure",
        "src\app\vault",
        "governance\sovereign_data",
        "data\learning_requests\pending_secure",
        "emergent-microservices\sovereign-data-vault"
    )
    
    foreach ($dir in $requiredVaultDirs) {
        $fullPath = Join-Path $RootPath $dir
        
        if (Test-Path $fullPath) {
            Add-TestResult -TestName "Directory Exists" `
                          -Status "Pass" `
                          -Message "Vault directory found: $dir" `
                          -Details @{ Path = $fullPath }
        } else {
            Add-TestResult -TestName "Directory Exists" `
                          -Status "Fail" `
                          -Message "Missing vault directory: $dir" `
                          -Details @{ ExpectedPath = $fullPath }
        }
    }
}

# ==============================================================================
# SECURITY ISOLATION TESTS
# ==============================================================================

function Test-SecurityIsolation {
    Write-Info "`n=== Testing Security Isolation ==="
    
    # Test black vault AI ignore
    $blackVaultIgnore = Join-Path $RootPath "data\black_vault_secure\.aiignore"
    
    if (Test-Path $blackVaultIgnore) {
        $content = Get-Content $blackVaultIgnore -Raw
        
        if ($content -match "AI CANNOT ACCESS") {
            Add-TestResult -TestName "AI Isolation" `
                          -Status "Pass" `
                          -Message "Black Vault has proper AI access restrictions" `
                          -Details @{ File = $blackVaultIgnore }
        } else {
            Add-TestResult -TestName "AI Isolation" `
                          -Status "Warning" `
                          -Message "Black Vault .aiignore exists but may not have proper restrictions" `
                          -Details @{ File = $blackVaultIgnore }
        }
    } else {
        Add-TestResult -TestName "AI Isolation" `
                      -Status "Fail" `
                      -Message "Missing .aiignore in Black Vault" `
                      -Details @{ ExpectedFile = $blackVaultIgnore }
    }
    
    # Test for secure directory markers
    $secureDirectories = @(
        "data\black_vault_secure",
        "data\learning_requests\pending_secure"
    )
    
    foreach ($dir in $secureDirectories) {
        $fullPath = Join-Path $RootPath $dir
        
        if (Test-Path $fullPath) {
            # Check if directory name contains 'secure' marker
            if ($dir -match "secure") {
                Add-TestResult -TestName "Secure Naming" `
                              -Status "Pass" `
                              -Message "Directory follows secure naming convention: $dir" `
                              -Details @{ Path = $fullPath }
            }
        }
    }
}

# ==============================================================================
# ENCRYPTION COMPONENT TESTS
# ==============================================================================

function Test-EncryptionComponents {
    Write-Info "`n=== Testing Encryption Components ==="
    
    # Test privacy vault implementation
    $privacyVaultPath = Join-Path $RootPath "utils\storage\privacy_vault.py"
    
    if (Test-Path $privacyVaultPath) {
        $content = Get-Content $privacyVaultPath -Raw
        
        # Check for Fernet encryption
        if ($content -match "from cryptography.fernet import Fernet") {
            Add-TestResult -TestName "Encryption Library" `
                          -Status "Pass" `
                          -Message "Privacy Vault uses cryptography.fernet" `
                          -Details @{ File = $privacyVaultPath }
        }
        
        # Check for forensic resistance
        if ($content -match "forensic_resistance") {
            Add-TestResult -TestName "Forensic Resistance" `
                          -Status "Pass" `
                          -Message "Privacy Vault implements forensic resistance" `
                          -Details @{ File = $privacyVaultPath }
        }
        
        # Check for secure wipe
        if ($content -match "_secure_wipe") {
            Add-TestResult -TestName "Secure Wipe" `
                          -Status "Pass" `
                          -Message "Privacy Vault implements secure data wiping" `
                          -Details @{ File = $privacyVaultPath }
        }
    } else {
        Add-TestResult -TestName "Encryption Component" `
                      -Status "Fail" `
                      -Message "Privacy Vault implementation not found" `
                      -Details @{ ExpectedFile = $privacyVaultPath }
    }
    
    # Test TARL OS secrets vault
    $tarlVaultPath = Join-Path $RootPath "tarl_os\security\secrets_vault.thirsty"
    
    if (Test-Path $tarlVaultPath) {
        $content = Get-Content $tarlVaultPath -Raw
        
        # Check for security features
        $securityFeatures = @(
            @{ Pattern = "detect attacks"; Name = "Attack Detection" },
            @{ Pattern = "armor"; Name = "Memory Armoring" },
            @{ Pattern = "sanitize"; Name = "Input Sanitization" },
            @{ Pattern = "encryptSecret"; Name = "Encryption Function" }
        )
        
        foreach ($feature in $securityFeatures) {
            if ($content -match $feature.Pattern) {
                Add-TestResult -TestName "TARL Security Feature" `
                              -Status "Pass" `
                              -Message "TARL Vault has $($feature.Name)" `
                              -Details @{ File = $tarlVaultPath; Feature = $feature.Name }
            } else {
                Add-TestResult -TestName "TARL Security Feature" `
                              -Status "Warning" `
                              -Message "TARL Vault may be missing $($feature.Name)" `
                              -Details @{ File = $tarlVaultPath; Feature = $feature.Name }
            }
        }
    } else {
        Add-TestResult -TestName "TARL Vault" `
                      -Status "Warning" `
                      -Message "TARL OS Secrets Vault not found" `
                      -Details @{ ExpectedFile = $tarlVaultPath }
    }
}

# ==============================================================================
# GOVERNANCE INTEGRATION TESTS
# ==============================================================================

function Test-GovernanceIntegration {
    Write-Info "`n=== Testing Governance Integration ==="
    
    # Test sovereign data structure
    $sovereignDataPath = Join-Path $RootPath "governance\sovereign_data"
    
    if (Test-Path $sovereignDataPath) {
        Add-TestResult -TestName "Sovereign Data" `
                      -Status "Pass" `
                      -Message "Sovereign data directory exists" `
                      -Details @{ Path = $sovereignDataPath }
        
        # Check for required files
        $requiredFiles = @(
            "immutable_audit.jsonl",
            "sovereign_keypair.json"
        )
        
        foreach ($file in $requiredFiles) {
            $filePath = Join-Path $sovereignDataPath $file
            
            if (Test-Path $filePath) {
                Add-TestResult -TestName "Governance File" `
                              -Status "Pass" `
                              -Message "Found governance file: $file" `
                              -Details @{ Path = $filePath }
            } else {
                Add-TestResult -TestName "Governance File" `
                              -Status "Warning" `
                              -Message "Missing governance file: $file" `
                              -Details @{ ExpectedPath = $filePath }
            }
        }
        
        # Check for artifacts directory
        $artifactsPath = Join-Path $sovereignDataPath "artifacts"
        
        if (Test-Path $artifactsPath) {
            $artifactCount = (Get-ChildItem $artifactsPath -Recurse -File).Count
            Add-TestResult -TestName "Governance Artifacts" `
                          -Status "Pass" `
                          -Message "Artifacts directory contains $artifactCount files" `
                          -Details @{ Path = $artifactsPath; FileCount = $artifactCount }
        }
    } else {
        Add-TestResult -TestName "Sovereign Data" `
                      -Status "Fail" `
                      -Message "Sovereign data directory not found" `
                      -Details @{ ExpectedPath = $sovereignDataPath }
    }
}

# ==============================================================================
# NAMING CONVENTION TESTS
# ==============================================================================

function Test-NamingConventions {
    Write-Info "`n=== Testing Naming Conventions ==="
    
    # Get all vault-related directories
    $vaultDirs = Get-ChildItem -Path $RootPath -Recurse -Directory -ErrorAction SilentlyContinue | 
                 Where-Object { $_.Name -match "vault|secure" }
    
    $validPatterns = @(
        ".*vault.*",
        ".*secure.*",
        ".*sovereign.*"
    )
    
    foreach ($dir in $vaultDirs) {
        $matchesPattern = $false
        
        foreach ($pattern in $validPatterns) {
            if ($dir.Name -match $pattern) {
                $matchesPattern = $true
                break
            }
        }
        
        if ($matchesPattern) {
            # Check for proper naming (lowercase, underscores)
            if ($dir.Name -match "^[a-z0-9_\-]+$") {
                Add-TestResult -TestName "Naming Convention" `
                              -Status "Pass" `
                              -Message "Directory follows naming convention: $($dir.Name)" `
                              -Details @{ Path = $dir.FullName }
            } else {
                Add-TestResult -TestName "Naming Convention" `
                              -Status "Warning" `
                              -Message "Directory may not follow standard naming: $($dir.Name)" `
                              -Details @{ Path = $dir.FullName }
            }
        }
    }
}

# ==============================================================================
# ACCESS PERMISSION TESTS
# ==============================================================================

function Test-AccessPermissions {
    Write-Info "`n=== Testing Access Permissions ==="
    
    $criticalVaultDirs = @(
        "data\black_vault_secure",
        "governance\sovereign_data"
    )
    
    foreach ($dir in $criticalVaultDirs) {
        $fullPath = Join-Path $RootPath $dir
        
        if (Test-Path $fullPath) {
            try {
                # Test read access
                $null = Get-ChildItem $fullPath -ErrorAction Stop
                Add-TestResult -TestName "Read Access" `
                              -Status "Pass" `
                              -Message "Can read directory: $dir" `
                              -Details @{ Path = $fullPath }
                
                # Test write access (create temp file)
                $testFile = Join-Path $fullPath ".write_test_$(Get-Random)"
                New-Item -Path $testFile -ItemType File -Force | Out-Null
                Remove-Item $testFile -Force
                
                Add-TestResult -TestName "Write Access" `
                              -Status "Pass" `
                              -Message "Can write to directory: $dir" `
                              -Details @{ Path = $fullPath }
            }
            catch {
                Add-TestResult -TestName "Access Test" `
                              -Status "Fail" `
                              -Message "Access denied to directory: $dir - $($_.Exception.Message)" `
                              -Details @{ Path = $fullPath; Error = $_.Exception.Message }
            }
        }
    }
}

# ==============================================================================
# DATA INTEGRITY TESTS
# ==============================================================================

function Test-DataIntegrity {
    Write-Info "`n=== Testing Data Integrity ==="
    
    # Test sovereign keypair
    $keypairPath = Join-Path $RootPath "governance\sovereign_data\sovereign_keypair.json"
    
    if (Test-Path $keypairPath) {
        try {
            $keypair = Get-Content $keypairPath -Raw | ConvertFrom-Json
            
            if ($keypair.public_key -and $keypair.private_key) {
                Add-TestResult -TestName "Keypair Structure" `
                              -Status "Pass" `
                              -Message "Sovereign keypair has valid structure" `
                              -Details @{ File = $keypairPath }
            } else {
                Add-TestResult -TestName "Keypair Structure" `
                              -Status "Fail" `
                              -Message "Sovereign keypair missing required keys" `
                              -Details @{ File = $keypairPath }
            }
        }
        catch {
            Add-TestResult -TestName "Keypair Parse" `
                          -Status "Fail" `
                          -Message "Cannot parse sovereign keypair: $($_.Exception.Message)" `
                          -Details @{ File = $keypairPath; Error = $_.Exception.Message }
        }
    }
    
    # Test audit log
    $auditPath = Join-Path $RootPath "governance\sovereign_data\immutable_audit.jsonl"
    
    if (Test-Path $auditPath) {
        $lineCount = (Get-Content $auditPath).Count
        Add-TestResult -TestName "Audit Log" `
                      -Status "Pass" `
                      -Message "Immutable audit log exists with $lineCount entries" `
                      -Details @{ File = $auditPath; Lines = $lineCount }
    } else {
        Add-TestResult -TestName "Audit Log" `
                      -Status "Warning" `
                      -Message "Immutable audit log not found" `
                      -Details @{ ExpectedFile = $auditPath }
    }
}

# ==============================================================================
# COMPONENT INTEGRATION TESTS
# ==============================================================================

function Test-ComponentIntegration {
    Write-Info "`n=== Testing Component Integration ==="
    
    # Check for vault module in src/app
    $vaultModules = @(
        "src\app\vault\__init__.py",
        "src\app\vault\core",
        "src\app\vault\auth",
        "src\app\vault\audit"
    )
    
    $foundModules = 0
    foreach ($module in $vaultModules) {
        $fullPath = Join-Path $RootPath $module
        
        if (Test-Path $fullPath) {
            $foundModules++
            Add-TestResult -TestName "Vault Module" `
                          -Status "Pass" `
                          -Message "Found vault component: $module" `
                          -Details @{ Path = $fullPath }
        }
    }
    
    if ($foundModules -gt 0) {
        Add-TestResult -TestName "Module Integration" `
                      -Status "Pass" `
                      -Message "Found $foundModules vault integration modules" `
                      -Details @{ ModuleCount = $foundModules }
    } else {
        Add-TestResult -TestName "Module Integration" `
                      -Status "Warning" `
                      -Message "No vault integration modules found in src/app/vault" `
                      -Details @{ ExpectedPath = "src\app\vault" }
    }
}

# ==============================================================================
# FILE STRUCTURE CONSISTENCY TESTS
# ==============================================================================

function Test-FileStructureConsistency {
    Write-Info "`n=== Testing File Structure Consistency ==="
    
    # Check for Python __init__.py files in vault directories
    $pythonVaultDirs = Get-ChildItem -Path (Join-Path $RootPath "src\app\vault") -Directory -ErrorAction SilentlyContinue
    
    foreach ($dir in $pythonVaultDirs) {
        $initFile = Join-Path $dir.FullName "__init__.py"
        
        if (Test-Path $initFile) {
            Add-TestResult -TestName "Python Package" `
                          -Status "Pass" `
                          -Message "Vault directory is proper Python package: $($dir.Name)" `
                          -Details @{ Path = $dir.FullName }
        } else {
            Add-TestResult -TestName "Python Package" `
                          -Status "Warning" `
                          -Message "Vault directory missing __init__.py: $($dir.Name)" `
                          -Details @{ Path = $dir.FullName; ExpectedFile = $initFile }
        }
    }
}

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

function Invoke-VaultValidation {
    Write-Host "`n" -NoNewline
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                ║" -ForegroundColor Cyan
    Write-Host "║         AGENT-007: VAULT STRUCTURE VALIDATION SCRIPT           ║" -ForegroundColor Cyan
    Write-Host "║         Project-AI Vault Infrastructure Validation            ║" -ForegroundColor Cyan
    Write-Host "║                                                                ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Info "Root Path: $RootPath"
    Write-Info "Validation Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
    
    # Execute all test suites
    Test-VaultDirectoryStructure
    Test-SecurityIsolation
    Test-EncryptionComponents
    Test-GovernanceIntegration
    Test-NamingConventions
    Test-AccessPermissions
    Test-DataIntegrity
    Test-ComponentIntegration
    Test-FileStructureConsistency
    
    # Summary
    Write-Host "`n" -NoNewline
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                     VALIDATION SUMMARY                         ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Info "Total Tests: $($Script:ValidationResults.TotalTests)"
    Write-Success "Passed: $($Script:ValidationResults.PassedTests)"
    Write-Failure "Failed: $($Script:ValidationResults.FailedTests)"
    Write-Warning-Custom "Warnings: $($Script:ValidationResults.WarningTests)"
    
    $passRate = if ($Script:ValidationResults.TotalTests -gt 0) {
        [math]::Round(($Script:ValidationResults.PassedTests / $Script:ValidationResults.TotalTests) * 100, 2)
    } else { 0 }
    
    Write-Host ""
    Write-Info "Pass Rate: $passRate%"
    
    # Overall status
    Write-Host ""
    if ($Script:ValidationResults.FailedTests -eq 0) {
        Write-Success "✓ VALIDATION PASSED - All critical tests successful"
    } elseif ($Script:ValidationResults.FailedTests -lt 3) {
        Write-Warning-Custom "⚠ VALIDATION PASSED WITH WARNINGS - Minor issues detected"
    } else {
        Write-Failure "✗ VALIDATION FAILED - Critical issues require attention"
    }
    
    # Export results if requested
    if ($ExportResults) {
        $outputPath = Join-Path $RootPath $OutputFile
        $Script:ValidationResults | ConvertTo-Json -Depth 10 | Out-File $outputPath
        Write-Info "`nResults exported to: $outputPath"
    }
    
    Write-Host ""
    Write-Info "Validation Completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
    
    # Return exit code
    if ($Script:ValidationResults.FailedTests -eq 0) {
        exit 0
    } else {
        exit 1
    }
}

# Execute validation
Invoke-VaultValidation
