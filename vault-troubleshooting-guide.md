# Vault Structure Troubleshooting Guide

**AGENT-007: Vault Structure Validation Specialist**  
**Version:** 1.1.0  
**Last Updated:** 2026-04-20

**Related Documentation**:
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration dashboard
- [[docs/architecture/ROOT_STRUCTURE]] - Project structure documentation
- [[DOCUMENTATION_STRUCTURE_GUIDE]] - Documentation organization
- [[docs/architecture/ARCHITECTURE_OVERVIEW]] - System architecture
- [[SECURITY]] - Security policies and procedures
- [[docs/PATH_SECURITY_GUIDE]] - Path security guidelines

---

## Table of Contents

1. [Quick Diagnosis Tools](#quick-diagnosis-tools)
2. [Common Issues](#common-issues)
3. [Error Code Reference](#error-code-reference)
4. [Emergency Procedures](#emergency-procedures)
5. [Prevention Strategies](#prevention-strategies)
6. [Advanced Troubleshooting](#advanced-troubleshooting)
7. [System Reference](#system-reference)

---

## Quick Diagnosis Tools

### One-Line Health Check

```powershell
# Quick vault health check
& "T:\Project-AI-main\validate-vault-structure.ps1" -ExportResults
```

**Expected Output:** `✓ VALIDATION PASSED` with 90%+ pass rate

---

### Manual Vault Checks

```powershell
# Check 1: All vault directories exist
$vaultDirs = @(
    "data\black_vault_secure",
    "src\app\vault",
    "governance\sovereign_data",
    "data\learning_requests\pending_secure"
)

foreach ($dir in $vaultDirs) {
    $path = "T:\Project-AI-main\$dir"
    if (Test-Path $path) {
        Write-Host "✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "✗ $dir MISSING" -ForegroundColor Red
    }
}

# Check 2: Black Vault AI isolation
if (Test-Path "T:\Project-AI-main\data\black_vault_secure\.aiignore") {
    Write-Host "✓ AI isolation configured" -ForegroundColor Green
} else {
    Write-Host "✗ AI isolation MISSING" -ForegroundColor Red
}

# Check 3: Sovereign keypair
try {
    $keypair = Get-Content "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json" | ConvertFrom-Json
    if ($keypair.public_key -and $keypair.private_key) {
        Write-Host "✓ Sovereign keypair valid" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Sovereign keypair INVALID" -ForegroundColor Red
}

# Check 4: Encryption components
if (Test-Path "T:\Project-AI-main\utils\storage\privacy_vault.py") {
    Write-Host "✓ Privacy Vault exists" -ForegroundColor Green
} else {
    Write-Host "✗ Privacy Vault MISSING" -ForegroundColor Red
}
```

---

## Common Issues

**Quick Reference**: For vault structure, see [[docs/architecture/ROOT_STRUCTURE]]. For security configuration, see [[docs/PATH_SECURITY_GUIDE]] and [[SECURITY]].

### Issue 1: Directory Not Found ❌

**Error Code:** VLT-001  
**Severity:** CRITICAL  
**Impact:** Vault operations fail

**Related Documentation**: [[docs/architecture/ROOT_STRUCTURE#vault-directories]]

**Symptoms:**
```
✗ Directory Exists - Missing vault directory: data\black_vault_secure
```

**Root Causes:**
1. Fresh installation without data directory setup
2. Accidental deletion
3. Incorrect path configuration
4. Drive letter change

**Diagnosis:**
```powershell
# Check if directory ever existed
$path = "T:\Project-AI-main\data\black_vault_secure"
Test-Path $path

# Check parent directory
Get-ChildItem "T:\Project-AI-main\data" | Select-Object Name, LastWriteTime

# Check for similar named directories
Get-ChildItem "T:\Project-AI-main" -Recurse -Directory | Where-Object { $_.Name -match "vault" }
```

**Solutions:**

**Solution 1: Create Missing Directory (Recommended)**
```powershell
# Create black vault with proper security
$blackVault = "T:\Project-AI-main\data\black_vault_secure"
New-Item -Path $blackVault -ItemType Directory -Force

# Create AI isolation file
$aiignore = @"
# AI CANNOT ACCESS THIS DIRECTORY
# All content here is filtered from AI retrieval
# This is the Black Vault - denied learning requests only
*
!.aiignore
"@
$aiignore | Out-File "$blackVault\.aiignore" -Encoding UTF8

Write-Host "✓ Black Vault created and secured" -ForegroundColor Green
```

**Solution 2: Create All Missing Vault Directories**
```powershell
# Comprehensive vault structure creation
$vaultStructure = @{
    "data\black_vault_secure" = $true  # Needs .aiignore
    "src\app\vault\core" = $false
    "src\app\vault\auth" = $false
    "src\app\vault\audit" = $false
    "governance\sovereign_data\artifacts" = $false
    "data\learning_requests\pending_secure" = $true  # Needs .aiignore
}

foreach ($dir in $vaultStructure.Keys) {
    $path = "T:\Project-AI-main\$dir"
    
    if (!(Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force
        Write-Host "Created: $dir" -ForegroundColor Yellow
        
        # Add .aiignore for secure directories
        if ($vaultStructure[$dir]) {
            $aiignore = "# AI CANNOT ACCESS THIS DIRECTORY`n# All content here is filtered from AI retrieval`n*`n!.aiignore"
            $aiignore | Out-File "$path\.aiignore" -Encoding UTF8
            Write-Host "  + Added AI isolation" -ForegroundColor Green
        }
    } else {
        Write-Host "Exists: $dir" -ForegroundColor Green
    }
}
```

**Verification:**
```powershell
& "T:\Project-AI-main\validate-vault-structure.ps1"
# Should show: ✓ Directory Exists - Vault directory found: data\black_vault_secure
```

---

### Issue 2: Access Denied ❌

**Error Code:** VLT-002  
**Severity:** CRITICAL  
**Impact:** Cannot read/write vault data

**Symptoms:**
```
✗ Access Test - Access denied to directory: data\black_vault_secure
UnauthorizedAccessException: Access to the path is denied
```

**Root Causes:**
1. Insufficient user permissions
2. Directory owned by different user
3. NTFS permissions too restrictive
4. Running without administrator privileges

**Diagnosis:**
```powershell
# Check current permissions
$path = "T:\Project-AI-main\data\black_vault_secure"
$acl = Get-Acl $path
$acl.Access | Format-Table IdentityReference, FileSystemRights, AccessControlType -AutoSize

# Check current user
$currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "Current user: $currentUser"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
Write-Host "Running as admin: $isAdmin"
```

**Solutions:**

**Solution 1: Run as Administrator**
```powershell
# Close current PowerShell
# Right-click PowerShell icon → "Run as administrator"
# Navigate back to project directory
cd T:\Project-AI-main
.\validate-vault-structure.ps1
```

**Solution 2: Grant Current User Full Control**
```powershell
# Run as administrator
$path = "T:\Project-AI-main\data\black_vault_secure"
$acl = Get-Acl $path

# Get current user
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Create full control permission
$permission = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $user,
    "FullControl",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow"
)

# Add permission and apply
$acl.SetAccessRule($permission)
Set-Acl $path $acl

Write-Host "✓ Granted full control to $user" -ForegroundColor Green
```

**Solution 3: Take Ownership**
```powershell
# If directory owned by different user
$path = "T:\Project-AI-main\data\black_vault_secure"

# Take ownership
takeown /F $path /R /D Y

# Grant permissions
icacls $path /grant "${env:USERNAME}:(OI)(CI)F" /T

Write-Host "✓ Ownership transferred and permissions granted" -ForegroundColor Green
```

**Verification:**
```powershell
# Try creating test file
$testFile = "T:\Project-AI-main\data\black_vault_secure\.write_test"
"test" | Out-File $testFile
Remove-Item $testFile
Write-Host "✓ Write access verified" -ForegroundColor Green
```

---

### Issue 3: Missing AI Isolation ❌

**Error Code:** VLT-003  
**Severity:** CRITICAL (SECURITY)  
**Impact:** AI can access Black Vault contents

**Symptoms:**
```
✗ AI Isolation - Missing .aiignore in Black Vault
```

**Root Causes:**
1. .aiignore file deleted
2. Fresh installation without security setup
3. Incomplete vault initialization

**Diagnosis:**
```powershell
# Check .aiignore exists
$aiignorePath = "T:\Project-AI-main\data\black_vault_secure\.aiignore"
if (Test-Path $aiignorePath) {
    Write-Host "File exists" -ForegroundColor Green
    Get-Content $aiignorePath
} else {
    Write-Host "File MISSING" -ForegroundColor Red
}
```

**Solutions:**

**Solution 1: Create Proper .aiignore**
```powershell
$blackVault = "T:\Project-AI-main\data\black_vault_secure"
$aiignore = @"
# AI CANNOT ACCESS THIS DIRECTORY
# All content here is filtered from AI retrieval
# This is the Black Vault - stores denied learning requests and forbidden content

# Block all files by default
*

# Allow this file to be visible (so AI knows it's protected)
!.aiignore
"@

$aiignore | Out-File "$blackVault\.aiignore" -Encoding UTF8 -Force
Write-Host "✓ AI isolation configured" -ForegroundColor Green
```

**Solution 2: Verify AI Cannot Access**
```powershell
# Create test secret file
$testSecret = "T:\Project-AI-main\data\black_vault_secure\test_secret.txt"
"EXTREMELY_SENSITIVE_DATA_DO_NOT_EXPOSE" | Out-File $testSecret

# Now ask your AI assistant to read the file
# It should be blocked by .aiignore

Write-Host "Test file created. Ask AI to read: $testSecret" -ForegroundColor Yellow
Write-Host "AI should respond with access denied or file not visible" -ForegroundColor Yellow
```

**Verification:**
```powershell
# Validation script should pass
& "T:\Project-AI-main\validate-vault-structure.ps1" | Select-String "AI Isolation"
# Should show: ✓ AI Isolation - Black Vault has proper AI access restrictions
```

---

### Issue 4: Keypair Parse Error ❌

**Error Code:** VLT-004  
**Severity:** CRITICAL  
**Impact:** Governance signing/verification fails

**Symptoms:**
```
✗ Keypair Parse - Cannot parse sovereign keypair: Invalid JSON
```

**Root Causes:**
1. Corrupted JSON file
2. Manual editing introduced syntax errors
3. Incomplete write operation
4. File encoding issues

**Diagnosis:**
```powershell
# Check file exists
$keypairPath = "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json"
Test-Path $keypairPath

# Try to parse
try {
    $keypair = Get-Content $keypairPath -Raw | ConvertFrom-Json
    Write-Host "✓ JSON is valid" -ForegroundColor Green
    
    # Check required fields
    if ($keypair.public_key) { Write-Host "✓ public_key present" -ForegroundColor Green }
    else { Write-Host "✗ public_key MISSING" -ForegroundColor Red }
    
    if ($keypair.private_key) { Write-Host "✓ private_key present" -ForegroundColor Green }
    else { Write-Host "✗ private_key MISSING" -ForegroundColor Red }
}
catch {
    Write-Host "✗ JSON parse error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Show file content
    Write-Host "`nFile content:" -ForegroundColor Yellow
    Get-Content $keypairPath -Raw
}
```

**Solutions:**

**Solution 1: Restore from Backup (RECOMMENDED)**
```powershell
# If you have a backup
$backup = "backup\sovereign_keypair.json"
$target = "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json"

if (Test-Path $backup) {
    Copy-Item $backup $target -Force
    Write-Host "✓ Restored from backup" -ForegroundColor Green
} else {
    Write-Host "✗ No backup found" -ForegroundColor Red
}
```

**Solution 2: Regenerate Keypair (⚠️ BREAKS EXISTING SIGNATURES)**
```python
# WARNING: This invalidates all previously signed governance decisions!
# Only use if you have no backup and can afford to lose signature verification

from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization
import json

# Generate new RSA keypair (2048-bit)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Serialize to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# Create keypair object
keypair = {
    "public_key": public_pem,
    "private_key": private_pem,
    "algorithm": "RSA-2048",
    "created_at": "2026-04-20T10:21:20Z",
    "note": "REGENERATED - previous signatures invalid"
}

# Save to file
with open('governance/sovereign_data/sovereign_keypair.json', 'w') as f:
    json.dump(keypair, f, indent=2)

print("✓ New keypair generated")
print("⚠️  WARNING: All previous governance signatures are now invalid")
print("⚠️  You must re-sign all governance decisions")
```

**Solution 3: Fix JSON Syntax Manually**
```powershell
# If JSON has minor syntax errors
$content = Get-Content "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json" -Raw

# Common fixes
$content = $content -replace ',\s*}', '}'  # Remove trailing commas
$content = $content -replace ',\s*]', ']'  # Remove trailing commas in arrays
$content = $content -replace '"\s*:\s*', '": '  # Fix spacing

# Try to parse again
try {
    $null = $content | ConvertFrom-Json
    $content | Out-File "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json" -Encoding UTF8
    Write-Host "✓ Fixed JSON syntax" -ForegroundColor Green
}
catch {
    Write-Host "✗ Manual fix required: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Verification:**
```powershell
# Should parse without errors
$keypair = Get-Content "T:\Project-AI-main\governance\sovereign_data\sovereign_keypair.json" | ConvertFrom-Json
Write-Host "public_key length: $($keypair.public_key.Length)"
Write-Host "private_key length: $($keypair.private_key.Length)"
```

---

### Issue 5: Decryption Failed ❌

**Error Code:** VLT-005  
**Severity:** HIGH  
**Impact:** Cannot retrieve encrypted vault data

**Symptoms:**
```python
# In application logs
cryptography.fernet.InvalidToken: Decryption failed
```

**Root Causes:**
1. Encryption key mismatch (different key used for encryption vs decryption)
2. Corrupted encrypted data
3. Key rotation without re-encryption
4. Tampering detected by HMAC

**Diagnosis:**
```python
from utils.storage.privacy_vault import PrivacyVault
from cryptography.fernet import Fernet

# Create test vault
config = {"privacy_vault_enabled": True, "encrypted": True}
vault = PrivacyVault(config)

# Generate test key
test_key = Fernet.generate_key()
print(f"Test key: {test_key}")

# Start vault with key
vault.start(encryption_key=test_key)

# Test encryption/decryption cycle
vault.store("test_key", "test_value")
result = vault.retrieve("test_key")

if result == "test_value":
    print("✓ Encryption/decryption working")
else:
    print("✗ Decryption failed")
```

**Solutions:**

**Solution 1: Key Mismatch - Use Correct Key**
```python
import os
from cryptography.fernet import Fernet

# Key should be stored in environment variable
key = os.getenv('VAULT_ENCRYPTION_KEY')

if not key:
    print("✗ VAULT_ENCRYPTION_KEY not set in environment")
    print("Generate new key:")
    new_key = Fernet.generate_key()
    print(f"export VAULT_ENCRYPTION_KEY={new_key.decode()}")
    print("⚠️  WARNING: Setting new key will lose access to old encrypted data")
else:
    # Use existing key
    vault.start(encryption_key=key.encode())
    print("✓ Using key from environment")
```

**Solution 2: Corrupted Data - Clear and Restart**
```python
# WARNING: This deletes all encrypted data!
vault.stop()  # This calls _secure_wipe() if forensic_resistance enabled
vault.start(encryption_key=your_key)
print("⚠️  Vault cleared and restarted with clean state")
```

**Solution 3: Key Rotation**
```python
# Decrypt with old key, re-encrypt with new key
old_key = Fernet(old_key_bytes)
new_key = Fernet(new_key_bytes)

# Get all data with old key
old_vault = PrivacyVault(config)
old_vault.start(encryption_key=old_key_bytes)
all_data = {}
for key in old_vault.list_keys():
    all_data[key] = old_vault.retrieve(key)

# Store with new key
new_vault = PrivacyVault(config)
new_vault.start(encryption_key=new_key_bytes)
for key, value in all_data.items():
    new_vault.store(key, value)

print(f"✓ Rotated {len(all_data)} entries to new key")
```

**Verification:**
```python
# Full encryption test
test_data = {
    "api_key": "sk-test-123456",
    "password": "SecurePassword123!",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

for key, value in test_data.items():
    vault.store(key, value)
    retrieved = vault.retrieve(key)
    assert retrieved == value, f"Mismatch for {key}"

print("✓ All test data encrypted and decrypted successfully")
```

---

### Issue 6: TARL Vault Sealed ❌

**Error Code:** VLT-006  
**Severity:** HIGH  
**Impact:** Cannot access TARL secrets

**Symptoms:**
```
ERROR: Vault is sealed
```

**Root Causes:**
1. Vault not initialized
2. Vault intentionally sealed for security
3. Master password lost

**Diagnosis:**
```javascript
// In TARL environment
pour "Vault sealed state: " + sealedState

// Check if vault is initialized
thirsty (masterKey == null) {
  pour "Vault not initialized"
} else {
  pour "Vault initialized but sealed"
}
```

**Solutions:**

**Solution 1: Initialize Vault (First Time)**
```javascript
// Initialize with strong master password (16+ chars)
drink masterPassword = "YourStrongMasterPassword123!"

drink result = initSecretsVault(masterPassword)

thirsty (result == "initialized") {
  pour "✓ Vault initialized and unsealed"
} else {
  pour "✗ Initialization failed"
}
```

**Solution 2: Unseal Existing Vault**
```javascript
glass unsealVault(masterPassword) {
  detect attacks {
    morph on: ["brute_force", "timing"]
    defend with: "paranoid"
  }
  
  sanitize masterPassword
  
  // Validate master password
  drink derivedKey = deriveMasterKey(masterPassword)
  
  thirsty (derivedKey != masterKey) {
    pour "ERROR: Invalid master password"
    return false
  }
  
  sealedState = false
  
  pour "✓ Vault unsealed"
  return true
}

// Usage
unsealVault("YourStrongMasterPassword123!")
```

**Solution 3: Emergency Access (Master Password Lost)**
```javascript
// ⚠️  EXTREME DANGER ZONE ⚠️
// This bypasses security - only use in development/testing
// NEVER use in production

glass emergencyUnseal() {
  pour "⚠️  WARNING: Emergency unseal bypasses security"
  pour "⚠️  All secrets will be lost"
  
  // Reset vault completely
  secrets = {}
  accessLog = []
  encryptionKeys = {}
  currentKeyVersion = 1
  rotationSchedule = {}
  sealedState = false
  masterKey = null
  
  pour "Vault reset - re-initialization required"
  return "reset"
}
```

**Verification:**
```javascript
// Test vault operations
drink testSecret = storeSecret(
  "test/api_key",
  "sk-test-12345",
  TYPE_API_KEY,
  { environment: "development" }
)

thirsty (testSecret) {
  pour "✓ Vault operational - can store secrets"
} else {
  pour "✗ Vault still sealed or error"
}
```

---

### Issue 7: Execution Policy Prevents Script ❌

**Error Code:** VLT-007  
**Severity:** MEDIUM  
**Impact:** Cannot run validation script

**Symptoms:**
```
.\validate-vault-structure.ps1 : File cannot be loaded because running scripts is disabled on this system.
```

**Root Causes:**
1. PowerShell execution policy set to `Restricted` or `AllSigned`
2. Corporate security policy
3. Script not signed

**Diagnosis:**
```powershell
# Check current execution policy
Get-ExecutionPolicy -List

# Output example:
#         Scope ExecutionPolicy
#         ----- ---------------
# MachinePolicy       Undefined
#    UserPolicy       Undefined
#       Process       Undefined
#   CurrentUser       Undefined
#  LocalMachine      Restricted  <- This blocks scripts
```

**Solutions:**

**Solution 1: Bypass for Current Session (Quick Fix)**
```powershell
# This only affects current PowerShell window
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Now run script
.\validate-vault-structure.ps1

# Policy resets when you close PowerShell
```

**Solution 2: Set for Current User (Permanent)**
```powershell
# Allows scripts signed by trusted publishers + local scripts
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

# Or allow all scripts (less secure)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
```

**Solution 3: Sign the Script (Most Secure)**
```powershell
# Get or create code-signing certificate
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert |
        Select-Object -First 1

if ($cert) {
    # Sign the script
    Set-AuthenticodeSignature -FilePath ".\validate-vault-structure.ps1" -Certificate $cert
    
    Write-Host "✓ Script signed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ No code-signing certificate found" -ForegroundColor Red
    Write-Host "Create self-signed cert with:" -ForegroundColor Yellow
    Write-Host "New-SelfSignedCertificate -Type CodeSigningCert -Subject 'CN=Project-AI Code Signing'" -ForegroundColor Yellow
}
```

**Solution 4: Run with PowerShell -ExecutionPolicy Flag**
```powershell
# Single command that bypasses policy
powershell.exe -ExecutionPolicy Bypass -File ".\validate-vault-structure.ps1"
```

**Verification:**
```powershell
# Should run without errors
.\validate-vault-structure.ps1
# Expected: Script executes and shows validation results
```

---

### Issue 8: Missing __init__.py Files ⚠️

**Error Code:** VLT-008  
**Severity:** LOW  
**Impact:** Python package structure warning (non-critical)

**Symptoms:**
```
⚠ Python Package - Vault directory missing __init__.py: core
⚠ Python Package - Vault directory missing __init__.py: auth
⚠ Python Package - Vault directory missing __init__.py: audit
```

**Root Causes:**
1. Directories created without Python package initialization
2. Namespace packages (PEP 420) intentionally without __init__.py
3. Data directories mistaken for Python packages

**Diagnosis:**
```powershell
# Check which directories are missing __init__.py
$vaultDirs = Get-ChildItem "T:\Project-AI-main\src\app\vault" -Directory

foreach ($dir in $vaultDirs) {
    $initFile = Join-Path $dir.FullName "__init__.py"
    if (Test-Path $initFile) {
        Write-Host "✓ $($dir.Name) has __init__.py" -ForegroundColor Green
    } else {
        Write-Host "✗ $($dir.Name) missing __init__.py" -ForegroundColor Yellow
        
        # Check if directory contains Python files
        $pyFiles = Get-ChildItem $dir.FullName -Filter "*.py" -Recurse
        Write-Host "  Python files: $($pyFiles.Count)" -ForegroundColor Gray
    }
}
```

**Solutions:**

**Solution 1: Create Empty __init__.py Files**
```powershell
# If directories should be packages
$vaultModules = @(
    "src\app\vault\core",
    "src\app\vault\auth",
    "src\app\vault\audit"
)

foreach ($module in $vaultModules) {
    $initFile = "T:\Project-AI-main\$module\__init__.py"
    
    if (!(Test-Path $initFile)) {
        # Create empty __init__.py
        New-Item $initFile -ItemType File -Force
        Write-Host "Created: $initFile" -ForegroundColor Green
    }
}
```

**Solution 2: Create __init__.py with Package Metadata**
```python
# For more explicit package initialization
# File: src/app/vault/core/__init__.py
"""
Core vault functionality.

This module provides the core vault operations including
storage, retrieval, and encryption.
"""

__version__ = "1.0.0"
__author__ = "Project-AI"

# Import key components for easier access
# from .storage import VaultStorage
# from .encryption import VaultEncryption

__all__ = []  # Add public API here
```

**Solution 3: Verify Not Needed**
```powershell
# If directories are data directories or namespace packages
# No action needed - ignore warning

# Verify they're not being imported in Python code
cd T:\Project-AI-main
Select-String -Path "**\*.py" -Pattern "from.*vault\.(core|auth|audit)" -Exclude "__pycache__"

# If no imports found, __init__.py not required
```

**Verification:**
```powershell
# Re-run validation
& "T:\Project-AI-main\validate-vault-structure.ps1"
# Warning should be gone if __init__.py files added
```

---

### Issue 9: Governance Artifacts Not Being Created ⚠️

**Error Code:** VLT-009  
**Severity:** MEDIUM  
**Impact:** No audit trail of governance executions

**Symptoms:**
```
⚠ Governance Artifacts - Artifacts directory empty or no recent artifacts
```

**Root Causes:**
1. Governance runtime not being invoked
2. Write permissions issue on artifacts directory
3. Configuration disabled artifact generation
4. Code path not reaching artifact creation

**Diagnosis:**
```powershell
# Check artifacts directory
$artifactsPath = "T:\Project-AI-main\governance\sovereign_data\artifacts"
Get-ChildItem $artifactsPath -Recurse | 
    Select-Object FullName, LastWriteTime |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 10

# Check governance state
$govState = Get-Content "T:\Project-AI-main\governance\governance_state.json" | ConvertFrom-Json
Write-Host "Last execution: $($govState.last_execution_timestamp)"
Write-Host "Artifacts enabled: $($govState.enable_artifacts)"
```

**Solutions:**

**Solution 1: Trigger Governance Execution**
```python
# In your application
from governance import sovereign_runtime

# Initialize runtime
runtime = sovereign_runtime.SovereignRuntime()

# Execute with governance (this creates artifacts)
result = runtime.execute_with_governance(
    stage="test_execution",
    operation=lambda: {"status": "success"},
    metadata={"purpose": "artifact_test"}
)

print(f"Execution ID: {result.execution_id}")
print(f"Artifacts path: {result.artifacts_path}")
```

**Solution 2: Verify Write Permissions**
```powershell
# Test write access to artifacts directory
$testPath = "T:\Project-AI-main\governance\sovereign_data\artifacts\test_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

try {
    New-Item $testPath -ItemType Directory
    "test" | Out-File "$testPath\test.txt"
    Remove-Item $testPath -Recurse -Force
    Write-Host "✓ Write access confirmed" -ForegroundColor Green
}
catch {
    Write-Host "✗ Write access denied: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Solution 3: Enable Artifact Generation in Config**
```python
# Check governance configuration
import json

config_path = "governance/sovereign_data/config.json"  # If exists

# Ensure artifacts enabled
config = {
    "enable_artifacts": True,
    "artifact_retention_days": 90,
    "compress_old_artifacts": True
}

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
```

**Verification:**
```powershell
# After triggering execution, check for new artifacts
$latestArtifacts = Get-ChildItem "T:\Project-AI-main\governance\sovereign_data\artifacts" -Directory |
                   Sort-Object LastWriteTime -Descending |
                   Select-Object -First 1

if ($latestArtifacts) {
    Write-Host "✓ Latest artifacts: $($latestArtifacts.Name)" -ForegroundColor Green
    Get-ChildItem $latestArtifacts.FullName
} else {
    Write-Host "✗ No artifacts found" -ForegroundColor Red
}
```

---

### Issue 10: High Memory Usage from Vault ⚠️

**Error Code:** VLT-010  
**Severity:** MEDIUM  
**Impact:** Application slowdown or crashes

**Symptoms:**
```
Application memory usage: 2.5 GB (and growing)
OutOfMemoryException after extended runtime
```

**Root Causes:**
1. Vault accumulating data without cleanup
2. Large encrypted values stored in memory
3. Memory leaks in encryption operations
4. No size limits on vault

**Diagnosis:**
```python
from utils.storage.privacy_vault import PrivacyVault
import sys

# Check vault size
vault_size_bytes = sum(len(v) for v in vault._vault.values())
vault_size_mb = vault_size_bytes / 1024 / 1024
vault_items = len(vault._vault)

print(f"Vault size: {vault_size_mb:.2f} MB")
print(f"Vault items: {vault_items}")
print(f"Average item size: {vault_size_bytes / vault_items if vault_items > 0 else 0:.2f} bytes")

# Check Python process memory
import psutil
import os

process = psutil.Process(os.getpid())
mem_info = process.memory_info()
print(f"Process memory: {mem_info.rss / 1024 / 1024:.2f} MB")
```

**Solutions:**

**Solution 1: Implement Periodic Cleanup**
```python
from datetime import datetime, timedelta

class VaultCleaner:
    def __init__(self, vault, max_age_hours=24):
        self.vault = vault
        self.max_age = timedelta(hours=max_age_hours)
    
    def cleanup_old_entries(self):
        """Remove entries older than max_age"""
        # If your keys have timestamps
        cutoff = datetime.now() - self.max_age
        removed_count = 0
        
        for key in list(self.vault.list_keys()):
            # Extract timestamp from key (adjust to your key format)
            if self._is_old(key, cutoff):
                self.vault.delete(key)
                removed_count += 1
        
        return removed_count
    
    def _is_old(self, key, cutoff):
        # Example: keys like "session_2026-04-20T10:00:00_abc123"
        try:
            timestamp_str = key.split('_')[1]
            timestamp = datetime.fromisoformat(timestamp_str)
            return timestamp < cutoff
        except:
            return False  # Keep if can't parse

# Usage
cleaner = VaultCleaner(vault, max_age_hours=24)
removed = cleaner.cleanup_old_entries()
print(f"Removed {removed} old entries")
```

**Solution 2: Implement Size Limits**
```python
class SizeLimitedVault(PrivacyVault):
    def __init__(self, config, max_size_mb=100, max_items=10000):
        super().__init__(config)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_items = max_items
    
    def store(self, key: str, value: str):
        """Store with size checks"""
        # Check item count
        if len(self._vault) >= self.max_items:
            raise RuntimeError(f"Vault full: {self.max_items} items")
        
        # Check total size
        current_size = sum(len(v) for v in self._vault.values())
        new_size = len(value.encode())
        
        if current_size + new_size > self.max_size_bytes:
            raise RuntimeError(f"Vault size limit exceeded: {self.max_size_bytes / 1024 / 1024} MB")
        
        # Store normally
        super().store(key, value)
```

**Solution 3: Offload to Persistent Storage**
```python
import pickle
from pathlib import Path

class PersistentVault(PrivacyVault):
    def __init__(self, config, persist_path="data/vault_persistence"):
        super().__init__(config)
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
    
    def flush_to_disk(self):
        """Write vault to disk and clear memory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        persist_file = self.persist_path / f"vault_{timestamp}.pkl"
        
        with open(persist_file, 'wb') as f:
            pickle.dump(self._vault, f)
        
        count = len(self._vault)
        self._vault.clear()
        
        return persist_file, count
    
    def load_from_disk(self, persist_file):
        """Load vault from disk"""
        with open(persist_file, 'rb') as f:
            self._vault = pickle.load(f)
        
        return len(self._vault)

# Usage: Flush to disk every hour or when size exceeds threshold
if vault_size_mb > 100:
    file, count = vault.flush_to_disk()
    print(f"Flushed {count} items to {file}")
```

**Solution 4: Use Memory Profiling**
```python
# Install: pip install memory_profiler
from memory_profiler import profile

@profile
def vault_operation():
    """Profile memory usage of vault operations"""
    vault.store("test", "value" * 10000)
    result = vault.retrieve("test")
    vault.delete("test")

# Run and analyze memory spikes
vault_operation()
```

**Verification:**
```python
# Monitor memory over time
import time

for i in range(100):
    vault.store(f"test_{i}", "x" * 1000)
    
    if i % 10 == 0:
        size_mb = sum(len(v) for v in vault._vault.values()) / 1024 / 1024
        print(f"Iteration {i}: Vault size = {size_mb:.2f} MB")
    
    time.sleep(0.1)

# Should show controlled memory growth
```

---

## Error Code Reference

| Code | Issue | Severity | Quick Fix |
|------|-------|----------|-----------|
| VLT-001 | Directory Not Found | CRITICAL | `New-Item -ItemType Directory` |
| VLT-002 | Access Denied | CRITICAL | Run as Administrator |
| VLT-003 | Missing AI Isolation | CRITICAL | Create `.aiignore` |
| VLT-004 | Keypair Parse Error | CRITICAL | Restore from backup |
| VLT-005 | Decryption Failed | HIGH | Check encryption key |
| VLT-006 | TARL Vault Sealed | HIGH | Call `initSecretsVault()` |
| VLT-007 | Execution Policy | MEDIUM | `Set-ExecutionPolicy Bypass` |
| VLT-008 | Missing __init__.py | LOW | Create `__init__.py` files |
| VLT-009 | No Governance Artifacts | MEDIUM | Trigger governance execution |
| VLT-010 | High Memory Usage | MEDIUM | Implement cleanup strategy |

---

## Emergency Procedures

### Emergency 1: Complete Vault Reset 🚨

**When to use:** Catastrophic corruption, security breach, or complete recovery failure

**⚠️  WARNING:** This destroys ALL vault data!

```powershell
# Backup first (if possible)
$backupPath = "T:\Project-AI-main\emergency_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item $backupPath -ItemType Directory
Copy-Item "T:\Project-AI-main\data\*vault*" $backupPath -Recurse -Force
Copy-Item "T:\Project-AI-main\governance\sovereign_data" $backupPath -Recurse -Force

# Complete reset
Remove-Item "T:\Project-AI-main\data\black_vault_secure\*" -Recurse -Force -Exclude ".aiignore"
Remove-Item "T:\Project-AI-main\governance\sovereign_data\*" -Recurse -Force -Exclude "artifacts"

# Reinitialize structure
& "T:\Project-AI-main\scripts\initialize-vault-structure.ps1"  # If exists

Write-Host "⚠️  VAULT RESET COMPLETE" -ForegroundColor Yellow
Write-Host "Backup saved to: $backupPath" -ForegroundColor Yellow
```

---

### Emergency 2: Revoke Compromised Cryptographic Keys 🚨

**When to use:** Private key exposure, suspected key compromise

```python
# Immediate actions:

# 1. Generate new keypair
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json
from datetime import datetime

# Generate new keys
new_private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)  # Stronger
new_public_key = new_private_key.public_key()

# Backup old keys
old_keypair_path = "governance/sovereign_data/sovereign_keypair.json"
backup_path = f"governance/sovereign_data/sovereign_keypair_COMPROMISED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json.backup"
import shutil
shutil.move(old_keypair_path, backup_path)

# Save new keys
new_keypair = {
    "public_key": new_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode(),
    "private_key": new_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()  # TODO: Add encryption
    ).decode(),
    "algorithm": "RSA-4096",
    "created_at": datetime.now().isoformat(),
    "revoked_previous_key": True,
    "revocation_reason": "Key compromise suspected"
}

with open(old_keypair_path, 'w') as f:
    json.dump(new_keypair, f, indent=2)

# 2. Log the incident
incident_log = {
    "timestamp": datetime.now().isoformat(),
    "event": "CRYPTOGRAPHIC_KEY_REVOCATION",
    "severity": "CRITICAL",
    "old_key_backup": backup_path,
    "new_key_algorithm": "RSA-4096",
    "action_required": "Re-sign all governance decisions"
}

with open("governance/sovereign_data/immutable_audit.jsonl", 'a') as f:
    import json
    f.write(json.dumps(incident_log) + '\n')

print("✓ New keypair generated")
print(f"✓ Old keys backed up to: {backup_path}")
print("⚠️  ACTION REQUIRED: Re-sign all governance decisions with new key")
```

---

### Emergency 3: Vault Access Lockdown 🚨

**When to use:** Unauthorized access detected, security incident

```powershell
# Immediate lockdown
$vaultPaths = @(
    "T:\Project-AI-main\data\black_vault_secure",
    "T:\Project-AI-main\governance\sovereign_data"
)

foreach ($path in $vaultPaths) {
    # Remove all access except SYSTEM
    $acl = Get-Acl $path
    $acl.SetAccessRuleProtection($true, $false)  # Disable inheritance, remove inherited
    
    # Add SYSTEM only
    $systemRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        "SYSTEM",
        "FullControl",
        "ContainerInherit,ObjectInherit",
        "None",
        "Allow"
    )
    $acl.SetAccessRule($systemRule)
    Set-Acl $path $acl
    
    Write-Host "🔒 LOCKED: $path" -ForegroundColor Red
}

# Log the lockdown
$lockdownLog = @{
    timestamp = Get-Date -Format "o"
    event = "EMERGENCY_VAULT_LOCKDOWN"
    reason = "Security incident"
    locked_paths = $vaultPaths
} | ConvertTo-Json

Add-Content "T:\Project-AI-main\data\security\lockdown_log.jsonl" $lockdownLog

Write-Host "⚠️  VAULT LOCKDOWN COMPLETE - Manual unlock required" -ForegroundColor Yellow
```

---

## Prevention Strategies

### Strategy 1: Automated Health Monitoring

```powershell
# Create scheduled task for daily validation
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File T:\Project-AI-main\validate-vault-structure.ps1 -ExportResults"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "Project-AI Vault Health Check" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Daily validation of Project-AI vault infrastructure"

Write-Host "✓ Scheduled daily vault health checks at 2 AM" -ForegroundColor Green
```

---

### Strategy 2: Automated Backups

```powershell
# Backup script (run daily/hourly)
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "T:\Project-AI-main\backups\vault_$timestamp"

# Create backup
New-Item $backupRoot -ItemType Directory -Force

# Backup critical vault data
$criticalPaths = @(
    "governance\sovereign_data\sovereign_keypair.json",
    "governance\sovereign_data\immutable_audit.jsonl",
    "data\black_vault_secure\.aiignore"
)

foreach ($path in $criticalPaths) {
    $source = "T:\Project-AI-main\$path"
    $dest = Join-Path $backupRoot (Split-Path $path -Leaf)
    
    if (Test-Path $source) {
        Copy-Item $source $dest -Force
        Write-Host "Backed up: $path" -ForegroundColor Green
    }
}

# Compress backup
Compress-Archive -Path $backupRoot -DestinationPath "$backupRoot.zip"
Remove-Item $backupRoot -Recurse -Force

# Cleanup old backups (keep last 30 days)
Get-ChildItem "T:\Project-AI-main\backups" -Filter "vault_*.zip" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force

Write-Host "✓ Vault backup complete: $backupRoot.zip" -ForegroundColor Green
```

---

### Strategy 3: Security Alerts

```python
# Monitor vault access and alert on anomalies
import logging
from datetime import datetime
import json

class VaultSecurityMonitor:
    def __init__(self, alert_threshold=100):
        self.alert_threshold = alert_threshold
        self.access_count = 0
        self.logger = logging.getLogger("vault_security")
    
    def log_access(self, operation, key, user):
        """Log vault access and check for anomalies"""
        self.access_count += 1
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "key": key,
            "user": user,
            "total_accesses": self.access_count
        }
        
        # Log to audit
        with open("data/audit/vault_access.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Alert if threshold exceeded
        if self.access_count > self.alert_threshold:
            self.send_alert(f"High vault access rate: {self.access_count} operations")
    
    def send_alert(self, message):
        """Send security alert"""
        self.logger.critical(f"SECURITY ALERT: {message}")
        # TODO: Send email/Slack notification

# Usage in privacy_vault.py
monitor = VaultSecurityMonitor()

def store(self, key: str, value: str):
    monitor.log_access("STORE", key, get_current_user())
    # ... existing store logic
```

---

## Advanced Troubleshooting

### Advanced 1: Memory Dump Analysis

```python
# If vault corruption suspected, dump memory state
import pickle
from datetime import datetime

def dump_vault_state(vault, output_path="vault_dump.pkl"):
    """Create complete memory dump of vault state"""
    dump = {
        "timestamp": datetime.now().isoformat(),
        "vault_data": vault._vault,
        "is_active": vault._active,
        "enabled": vault.enabled,
        "encrypted": vault.encrypted,
        "item_count": len(vault._vault),
        "total_size_bytes": sum(len(v) for v in vault._vault.values())
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(dump, f)
    
    print(f"✓ Vault state dumped to: {output_path}")
    return dump

# Analyze dump
def analyze_vault_dump(dump_path="vault_dump.pkl"):
    """Analyze vault memory dump"""
    with open(dump_path, 'rb') as f:
        dump = pickle.load(f)
    
    print(f"Dump timestamp: {dump['timestamp']}")
    print(f"Items: {dump['item_count']}")
    print(f"Total size: {dump['total_size_bytes'] / 1024 / 1024:.2f} MB")
    print(f"Active: {dump['is_active']}")
    print(f"Encrypted: {dump['encrypted']}")
    
    # Check for anomalies
    if dump['total_size_bytes'] > 100 * 1024 * 1024:  # 100 MB
        print("⚠️  WARNING: Vault size exceeds 100 MB")
    
    if dump['item_count'] > 10000:
        print("⚠️  WARNING: Vault has excessive items")
```

---

### Advanced 2: Cryptographic Verification

```python
# Verify all encrypted data can be decrypted
def verify_vault_integrity(vault):
    """Test decryption of all vault entries"""
    errors = []
    
    for key in vault.list_keys():
        try:
            value = vault.retrieve(key)
            if value is None:
                errors.append(f"Decryption returned None for key: {key}")
        except Exception as e:
            errors.append(f"Decryption failed for key {key}: {str(e)}")
    
    if errors:
        print(f"✗ Integrity check failed: {len(errors)} errors")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print(f"✓ Integrity check passed: All {len(vault._vault)} entries valid")
        return True
```

---

### Advanced 3: Performance Profiling

```python
import time
import statistics

def profile_vault_operations(vault, iterations=1000):
    """Profile vault performance"""
    store_times = []
    retrieve_times = []
    delete_times = []
    
    test_data = "x" * 1000  # 1 KB test data
    
    for i in range(iterations):
        key = f"perf_test_{i}"
        
        # Store
        start = time.perf_counter()
        vault.store(key, test_data)
        store_times.append(time.perf_counter() - start)
        
        # Retrieve
        start = time.perf_counter()
        vault.retrieve(key)
        retrieve_times.append(time.perf_counter() - start)
        
        # Delete
        start = time.perf_counter()
        vault.delete(key)
        delete_times.append(time.perf_counter() - start)
    
    # Statistics
    print(f"\nPerformance Profile ({iterations} iterations):")
    print(f"Store:")
    print(f"  Mean: {statistics.mean(store_times)*1000:.3f} ms")
    print(f"  Median: {statistics.median(store_times)*1000:.3f} ms")
    print(f"  P95: {statistics.quantiles(store_times, n=20)[18]*1000:.3f} ms")
    
    print(f"Retrieve:")
    print(f"  Mean: {statistics.mean(retrieve_times)*1000:.3f} ms")
    print(f"  Median: {statistics.median(retrieve_times)*1000:.3f} ms")
    print(f"  P95: {statistics.quantiles(retrieve_times, n=20)[18]*1000:.3f} ms")
    
    print(f"Delete:")
    print(f"  Mean: {statistics.mean(delete_times)*1000:.3f} ms")
    print(f"  Median: {statistics.median(delete_times)*1000:.3f} ms")
    print(f"  P95: {statistics.quantiles(delete_times, n=20)[18]*1000:.3f} ms")
```

---

## Document Information

**Version:** 1.0.0  
**Last Updated:** 2026-04-20  
**Maintained by:** AGENT-007 - Vault Structure Validation Specialist  
**Review Frequency:** Quarterly or after major incidents

**Related Documents:**
- [[vault-validation-report]] - Comprehensive validation report
- [[validate-vault-structure.ps1]] - Automated validation script
- [[vault-sign-off-document]] - Official sign-off and certification
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration dashboard
- [[DOCUMENTATION_STRUCTURE_GUIDE]] - Documentation organization

**Feedback:**
If you encounter issues not covered in this guide, please:
1. Create detailed incident report
2. Update this troubleshooting guide
3. Add new error code to reference table

---

## System Reference

### Related Architecture Documentation

- [[docs/architecture/ARCHITECTURE_OVERVIEW]] - Overall system architecture
- [[docs/architecture/ROOT_STRUCTURE]] - Project directory structure
- [[docs/architecture/STATE_MODEL]] - State management and persistence
- [[docs/architecture/SOVEREIGN_RUNTIME]] - Sovereign decision system
- [[docs/architecture/INTEGRATION_LAYER]] - Integration patterns
- [[docs/architecture/MODULE_CONTRACTS]] - Module interfaces

### Related Security Documentation

- [[SECURITY]] - Security policy and procedures
- [[docs/PATH_SECURITY_GUIDE]] - Path security and validation
- [[docs/ASYMMETRIC_SECURITY_FRAMEWORK]] - Asymmetric encryption system
- [[docs/CRYPTO_RANDOM_AUDIT]] - Cryptographic random number generation
- [[INPUT_VALIDATION_SECURITY_AUDIT]] - Input validation security
- [[docs/security_compliance/SECURITY_AGENTS_GUIDE]] - Security agents
- [[docs/security_compliance/THREAT_MODEL_SECURITY_WORKFLOWS]] - Threat model
- [[AUTHENTICATION_SECURITY_AUDIT_REPORT]] - Authentication security
- [[DATABASE_PERSISTENCE_AUDIT_REPORT]] - Database security
- [[DATA_ENCRYPTION_PRIVACY_AUDIT_REPORT]] - Encryption and privacy

### Related Configuration & Setup

- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration central hub
- [[DATAVIEW_SETUP_GUIDE]] - Dataview plugin setup
- [[TEMPLATER_SETUP_GUIDE]] - Templater plugin setup
- [[GRAPH_VIEW_GUIDE]] - Graph view configuration
- [[TAG_WRANGLER_GUIDE]] - Tag management
- [[EXCALIDRAW_GUIDE]] - Excalidraw integration
- [[docs/developer/config.md]] - Configuration management

### Related Troubleshooting Guides

- [[TEMPLATER_TROUBLESHOOTING_GUIDE]] - Templater issues
- [[docs/dataview-examples/TROUBLESHOOTING]] - Dataview query issues
- [[.github/ISSUE_AUTOMATION]] - Automated issue management
- [[PATH_TRAVERSAL_FIX_REPORT]] - Path traversal fixes
- [[TIMING_ATTACK_FIX_REPORT]] - Timing attack fixes
- [[GUI_INPUT_VALIDATION_FIX_REPORT]] - Input validation fixes

### Related Developer Documentation

- [[docs/developer/DEVELOPER_QUICK_REFERENCE]] - Developer quick reference
- [[docs/developer/DEVELOPMENT]] - Development environment
- [[docs/developer/HOW_TO_RUN]] - Running the application
- [[docs/developer/checks.md]] - Quality checks
- [[docs/developer/DESKTOP_APP_README]] - Desktop app documentation
- [[docs/developer/IDENTITY_SECURITY_INFRASTRUCTURE]] - Identity security

### Vault Issue → Solution Quick Map

| Error Code | Issue | This Guide | Related System Docs |
|------------|-------|------------|---------------------|
| VLT-001 | Directory missing | [[#issue-1-directory-not-found]] | [[docs/architecture/ROOT_STRUCTURE]] |
| VLT-002 | AI isolation | [[#issue-2-ai-isolation-not-configured]] | [[SECURITY#ai-isolation]] |
| VLT-003 | Encryption key | [[#issue-3-encryption-key-missing]] | [[docs/ASYMMETRIC_SECURITY_FRAMEWORK]] |
| VLT-004 | Sovereign keypair | [[#issue-4-sovereign-keypair-invalid]] | [[docs/architecture/SOVEREIGN_RUNTIME]] |
| VLT-005 | Decryption failed | [[#issue-5-decryption-failed]] | [[DATA_ENCRYPTION_PRIVACY_AUDIT_REPORT]] |
| VLT-006 | Permission denied | [[#permission-errors]] | [[docs/PATH_SECURITY_GUIDE]] |
| VLT-007 | Audit log corrupt | [[#audit-issues]] | [[docs/architecture/STATE_MODEL]] |
| VLT-008 | Backup failed | [[#backup-issues]] | [[docs/developer/DEVELOPMENT#backup]] |

### Common Problem Categories

#### Directory & Structure Issues
- **Start Here**: [[#quick-diagnosis-tools]]
- **Related**: [[docs/architecture/ROOT_STRUCTURE]], [[DOCUMENTATION_STRUCTURE_GUIDE]]
- **Scripts**: `validate-vault-structure.ps1`

#### Security & Encryption Issues
- **Start Here**: [[#issue-3-encryption-key-missing]]
- **Related**: [[docs/ASYMMETRIC_SECURITY_FRAMEWORK]], [[docs/CRYPTO_RANDOM_AUDIT]]
- **Critical**: [[SECURITY]], [[docs/PATH_SECURITY_GUIDE]]

#### AI Isolation Issues
- **Start Here**: [[#issue-2-ai-isolation-not-configured]]
- **Related**: [[SECURITY#ai-isolation]], [[docs/security_compliance/SECURITY_AGENTS_GUIDE]]
- **Testing**: Create test file and verify AI cannot access

#### Permission & Access Issues
- **Start Here**: [[#permission-errors]]
- **Related**: [[docs/PATH_SECURITY_GUIDE]], [[INPUT_VALIDATION_SECURITY_AUDIT]]
- **Admin Required**: Most permission fixes require elevation

#### Performance & Scale Issues
- **Start Here**: [[#advanced-troubleshooting]]
- **Related**: [[docs/architecture/STATE_MODEL]], [[docs/developer/DEVELOPMENT]]
- **Monitoring**: [[DATABASE_PERSISTENCE_AUDIT_REPORT]]

### Quick Navigation Paths

1. **Fresh Installation Issues**:
   - [[#issue-1-directory-not-found]] → [[docs/architecture/ROOT_STRUCTURE]] → [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]

2. **Security Configuration**:
   - [[#issue-2-ai-isolation-not-configured]] → [[SECURITY]] → [[docs/security_compliance/SECURITY_AGENTS_GUIDE]]

3. **Encryption Problems**:
   - [[#issue-3-encryption-key-missing]] → [[docs/ASYMMETRIC_SECURITY_FRAMEWORK]] → [[docs/CRYPTO_RANDOM_AUDIT]]

4. **Permission Errors**:
   - [[#permission-errors]] → [[docs/PATH_SECURITY_GUIDE]] → [[INPUT_VALIDATION_SECURITY_AUDIT]]

5. **Emergency Procedures**:
   - [[#emergency-procedures]] → [[SECURITY#incident-response]] → [[docs/security_compliance/THREAT_MODEL]]

---

**Document Version**: 1.1.0  
**Last Updated**: 2026-04-20  
**Phase 5 Enhancement**: Added comprehensive system references and wiki links  
**Maintained by**: AGENT-007 - Vault Structure Validation Specialist  
**Review Frequency**: Quarterly or after major incidents

---

**END OF TROUBLESHOOTING GUIDE**
