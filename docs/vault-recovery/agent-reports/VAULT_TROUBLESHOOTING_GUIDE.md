# Vault Root Troubleshooting Guide

**Document Version:** 1.0.0
**Author:** AGENT-001 (Vault Root Directory Architect)
**Created:** 2026-04-20
**Purpose:** Comprehensive troubleshooting for common vault setup and validation issues

---

## Table of Contents

1. [Quick Diagnostic Checklist](#quick-diagnostic-checklist)
2. [Common Errors](#common-errors)
3. [Permission Issues](#permission-issues)
4. [Network Drive Problems](#network-drive-problems)
5. [Performance Issues](#performance-issues)
6. [Security and ACL Issues](#security-and-acl-issues)
7. [Script Execution Errors](#script-execution-errors)
8. [Recovery Procedures](#recovery-procedures)
9. [Advanced Diagnostics](#advanced-diagnostics)

---

## Quick Diagnostic Checklist

Run these commands to diagnose most issues:

```powershell
# 1. Verify PowerShell version
$PSVersionTable.PSVersion

# 2. Check if vault exists
Test-Path "T:\Project-AI-vault"

# 3. Test basic permissions
Get-Acl "T:\Project-AI-vault" | Select-Object Owner, Group

# 4. Check disk space
Get-Volume -DriveLetter T | Select-Object DriveLetter, SizeRemaining

# 5. Run validation
.\vault-validation-001.ps1 -ExportReport

# 6. Check logs
Get-Content "T:\Project-AI-vault\vault-setup.log" -Tail 50
```

---

## Common Errors

### Error 1: "Directory already exists"

**Full Error Message:**
```
Pre-flight checks FAILED:
  - Directory already exists: T:\Project-AI-vault (Use -Force to overwrite)
```

**Cause:** The vault directory already exists and `-Force` flag was not used

**Solutions:**

**Option A - Overwrite with backup:**
```powershell
.\vault-setup-001.ps1 -Force
# Creates backup: T:\Project-AI-vault.backup_YYYYMMDD_HHMMSS
```

**Option B - Use different path:**
```powershell
.\vault-setup-001.ps1 -VaultRoot "T:\Project-AI-vault-v2"
```

**Option C - Manual removal:**
```powershell
# Backup first if needed
Copy-Item "T:\Project-AI-vault" "T:\Project-AI-vault.manual_backup" -Recurse

# Remove
Remove-Item "T:\Project-AI-vault" -Recurse -Force

# Recreate
.\vault-setup-001.ps1
```

---

### Error 2: "Insufficient disk space"

**Full Error Message:**
```
Pre-flight checks FAILED:
  - Insufficient disk space: 0.5GB available, 1GB required
```

**Cause:** Less than 1GB free space on target drive

**Solutions:**

**Check disk usage:**
```powershell
Get-Volume -DriveLetter T | Format-List DriveLetter, SizeRemaining, Size
Get-ChildItem T:\ -Recurse -Force |
    Measure-Object -Property Length -Sum |
    Select-Object @{N='SizeGB';E={[math]::Round($_.Sum/1GB,2)}}
```

**Free up space:**
```powershell
# Find large files
Get-ChildItem T:\ -Recurse -File -Force |
    Sort-Object Length -Descending |
    Select-Object -First 20 FullName, @{N='SizeGB';E={[math]::Round($_.Length/1GB,2)}}

# Clean temp files
Remove-Item "T:\temp\*" -Recurse -Force -ErrorAction SilentlyContinue
```

**Use different drive:**
```powershell
.\vault-setup-001.ps1 -VaultRoot "D:\Project-AI-vault"
```

---

### Error 3: "No write permission on parent directory"

**Full Error Message:**
```
Pre-flight checks FAILED:
  - No write permission on parent directory: T:\
```

**Cause:** Current user lacks write permissions on T:\ drive

**Solutions:**

**Run as Administrator:**
```powershell
# Right-click PowerShell and "Run as Administrator"
# Then execute:
.\vault-setup-001.ps1
```

**Check current permissions:**
```powershell
$Acl = Get-Acl "T:\"
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Acl.Access | Where-Object { $_.IdentityReference.Value -eq $CurrentUser } |
    Format-Table IdentityReference, FileSystemRights, AccessControlType
```

**Request admin to grant permissions:**
```powershell
# Admin must run this:
$Acl = Get-Acl "T:\"
$User = "DOMAIN\Username"  # Replace with actual username
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $User, "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)
Set-Acl "T:\" $Acl
```

---

## Permission Issues

### Issue 1: Read Permission Denied

**Symptom:**
```
✗ [Permissions] Read permission - Access to the path 'T:\Project-AI-vault' is denied
```

**Diagnosis:**
```powershell
# Check who owns the directory
$Acl = Get-Acl "T:\Project-AI-vault"
Write-Host "Owner: $($Acl.Owner)"

# Check current user
$CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
Write-Host "Current User: $CurrentUser"

# Check if current user is in ACL
$Acl.Access | Where-Object { $_.IdentityReference.Value -match $env:USERNAME }
```

**Fix (Auto):**
```powershell
.\vault-validation-001.ps1 -FixIssues
```

**Fix (Manual):**
```powershell
$Acl = Get-Acl "T:\Project-AI-vault"
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $User, "Read", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)
Set-Acl "T:\Project-AI-vault" $Acl

# Verify
.\vault-validation-001.ps1
```

---

### Issue 2: Write Permission Denied

**Symptom:**
```
✗ [Permissions] Write permission - Access to the path is denied
```

**Quick Fix:**
```powershell
# Grant current user modify access
$Path = "T:\Project-AI-vault"
$Acl = Get-Acl $Path
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $User, "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)
Set-Acl $Path $Acl
```

**Verify:**
```powershell
# Test write access
$TestFile = "T:\Project-AI-vault\.__write_test__.tmp"
"test" | Out-File $TestFile
Remove-Item $TestFile
Write-Host "Write permission verified" -ForegroundColor Green
```

---

### Issue 3: Execute/Traverse Permission Denied

**Symptom:**
```
✗ [Permissions] Execute permission - Cannot access subdirectory
```

**Fix:**
```powershell
$Acl = Get-Acl "T:\Project-AI-vault"
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $User, "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)
Set-Acl "T:\Project-AI-vault" $Acl
```

---

## Network Drive Problems

### Problem 1: "Network path not found"

**Symptom:**
```
Directory creation failed: The network path was not found
```

**Diagnosis:**
```powershell
# Check if drive is mapped
Get-PSDrive | Where-Object { $_.Name -eq "T" }

# Check network connectivity
Test-NetConnection -ComputerName "server-name" -Port 445

# Verify share access
net use
```

**Fix:**

**Reconnect drive:**
```powershell
# Remove existing mapping
net use T: /delete

# Reconnect with credentials
net use T: \\server\share /user:DOMAIN\Username password /persistent:yes

# Or use GUI
New-PSDrive -Name T -PSProvider FileSystem -Root "\\server\share" -Persist
```

**Use UNC path directly:**
```powershell
.\vault-setup-001.ps1 -VaultRoot "\\server\share\Project-AI-vault"
```

---

### Problem 2: Network drive disconnects randomly

**Symptom:** Vault accessible sometimes but not consistently

**Fix:**

**Make persistent:**
```powershell
net use T: \\server\share /persistent:yes
```

**Auto-reconnect script:**
```powershell
# Add to login script or Task Scheduler
if (-not (Test-Path "T:\")) {
    net use T: \\server\share /user:DOMAIN\Username password /persistent:yes
}
```

**Increase network timeout:**
```powershell
# Modify registry (Admin required)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" `
    -Name "KeepConn" -Value 600
```

---

### Problem 3: "Access denied" on network share

**Fix:**

**Check share permissions:**
```powershell
# On file server (admin access required)
Get-SmbShareAccess -Name "share-name"

# Grant access
Grant-SmbShareAccess -Name "share-name" -AccountName "DOMAIN\Username" -AccessRight Full
```

**Check NTFS permissions:**
```powershell
# On share path
Get-Acl "\\server\share" | Select-Object -ExpandProperty Access
```

---

## Performance Issues

### Issue 1: Slow directory creation (>5000ms)

**Diagnosis:**
```powershell
# Check disk performance
winsat disk -drive T

# Check for antivirus interference
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath

# Check disk fragmentation (HDD only)
Optimize-Volume -DriveLetter T -Analyze
```

**Solutions:**

**Exclude from antivirus:**
```powershell
# Windows Defender (Admin required)
Add-MpPreference -ExclusionPath "T:\Project-AI-vault"
```

**Defragment (HDD):**
```powershell
Optimize-Volume -DriveLetter T -Defrag
```

**Disable indexing:**
```powershell
$Path = "T:\Project-AI-vault"
$Folder = Get-Item $Path
$Folder.Attributes = $Folder.Attributes -bor [System.IO.FileAttributes]::NotContentIndexed
```

---

### Issue 2: Slow file I/O operations

**Diagnosis:**
```powershell
# Benchmark current performance
Measure-Command {
    $TestFile = "T:\Project-AI-vault\benchmark.tmp"
    "x" * 10MB | Out-File $TestFile
    Remove-Item $TestFile
}
```

**Solutions:**

**Increase buffer size:**
```powershell
$PSDefaultParameterValues = @{
    'Out-File:BufferSize' = 65536
    'Set-Content:BufferSize' = 65536
}
```

**Use faster I/O methods:**
```powershell
# Instead of Out-File, use StreamWriter
$Path = "T:\Project-AI-vault\test.txt"
$Stream = [System.IO.StreamWriter]::new($Path)
$Stream.WriteLine("content")
$Stream.Close()
```

---

## Security and ACL Issues

### Issue 1: "World-writable" warning

**Symptom:**
```
⚠ [Security] World-writable check - Directory may be world-writable
```

**Diagnosis:**
```powershell
$Acl = Get-Acl "T:\Project-AI-vault"
$Acl.Access | Where-Object {
    $_.IdentityReference.Value -match "Everyone|Users" -and
    $_.FileSystemRights -match "FullControl|Modify|Write"
} | Format-Table IdentityReference, FileSystemRights, AccessControlType
```

**Fix (Recommended):**
```powershell
# Remove world-writable permissions
$Acl = Get-Acl "T:\Project-AI-vault"

# Disable inheritance and remove inherited rules
$Acl.SetAccessRuleProtection($true, $false)

# Add only required permissions
$Admins = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "BUILTIN\Administrators", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$System = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "NT AUTHORITY\SYSTEM", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$CurrentUser = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)

$Acl.SetAccessRule($Admins)
$Acl.SetAccessRule($System)
$Acl.SetAccessRule($CurrentUser)

Set-Acl "T:\Project-AI-vault" $Acl

# Verify
.\vault-validation-001.ps1
```

---

### Issue 2: ACL corruption or inheritance issues

**Symptom:** Permissions behave unexpectedly

**Reset to defaults:**
```powershell
# Backup current ACL
$BackupAcl = Get-Acl "T:\Project-AI-vault"
$BackupAcl | Export-Clixml "T:\acl_backup.xml"

# Reset to parent inheritance
$Acl = Get-Acl "T:\Project-AI-vault"
$Acl.SetAccessRuleProtection($false, $true)  # Enable inheritance
Set-Acl "T:\Project-AI-vault" $Acl

# Or restore from backup if needed
$RestoredAcl = Import-Clixml "T:\acl_backup.xml"
Set-Acl "T:\Project-AI-vault" $RestoredAcl
```

---

## Script Execution Errors

### Error 1: "Execution policy" error

**Full Error:**
```
.\vault-setup-001.ps1 : File cannot be loaded because running scripts is disabled on this system
```

**Check current policy:**
```powershell
Get-ExecutionPolicy -List
```

**Fix:**
```powershell
# Option A: User scope (no admin required)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Option B: Process scope (temporary, no admin required)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# Option C: System-wide (admin required)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
```

**Bypass for single script:**
```powershell
powershell.exe -ExecutionPolicy Bypass -File .\vault-setup-001.ps1
```

---

### Error 2: "Unauthorized Access" during rollback

**Symptom:** Rollback fails with access denied

**Cause:** Original directory has stricter permissions than backup

**Fix:**
```powershell
# Take ownership
$Acl = Get-Acl "T:\Project-AI-vault"
$User = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$Acl.SetOwner($User)
Set-Acl "T:\Project-AI-vault" $Acl

# Grant full control to current user
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl = Get-Acl "T:\Project-AI-vault"
$Acl.SetAccessRule($Rule)
Set-Acl "T:\Project-AI-vault" $Acl

# Retry rollback or manual restore
$BackupPath = "T:\Project-AI-vault.backup_YYYYMMDD_HHMMSS"  # Replace with actual
Remove-Item "T:\Project-AI-vault" -Recurse -Force
Move-Item $BackupPath "T:\Project-AI-vault"
```

---

## Recovery Procedures

### Procedure 1: Complete Vault Rebuild

**When to use:** Vault is corrupted or permissions are irreparably broken

**Steps:**

```powershell
# 1. Backup critical data
$BackupPath = "C:\Temp\vault-backup-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
if (Test-Path "T:\Project-AI-vault") {
    Copy-Item "T:\Project-AI-vault" $BackupPath -Recurse -Force
    Write-Host "Backup created: $BackupPath"
}

# 2. Force removal
Remove-Item "T:\Project-AI-vault" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Clean residual permissions
# (None needed for fresh directory)

# 4. Recreate vault
.\vault-setup-001.ps1

# 5. Restore data (excluding scripts which are recreated)
if (Test-Path $BackupPath) {
    Get-ChildItem $BackupPath -Exclude "vault-*.ps1", "vault-*.json", "vault-*.log" |
        Copy-Item -Destination "T:\Project-AI-vault" -Recurse -Force
}

# 6. Validate
.\vault-validation-001.ps1 -Strict -ExportReport
```

---

### Procedure 2: Permission Reset

**When to use:** Permissions are misconfigured but directory structure is intact

```powershell
# 1. Take ownership (Admin required)
$Path = "T:\Project-AI-vault"
takeown /F $Path /R /D Y

# 2. Reset to defaults
icacls $Path /reset /T

# 3. Re-apply proper permissions
$Acl = Get-Acl $Path
$Acl.SetAccessRuleProtection($true, $false)

# Add administrators
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "BUILTIN\Administrators", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)

# Add SYSTEM
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "NT AUTHORITY\SYSTEM", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)

# Add current user
$Rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    [System.Security.Principal.WindowsIdentity]::GetCurrent().Name,
    "Modify", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$Acl.SetAccessRule($Rule)

Set-Acl $Path $Acl

# 4. Validate
.\vault-validation-001.ps1
```

---

## Advanced Diagnostics

### Enable Debug Logging

**In vault-setup-001.ps1:**
```powershell
# Add at script start
$DebugPreference = "Continue"
$VerbosePreference = "Continue"

# Run with verbose output
.\vault-setup-001.ps1 -Verbose -Debug
```

### Trace Network Issues

```powershell
# Start network trace
netsh trace start capture=yes tracefile=C:\temp\nettrace.etl

# Perform operation
.\vault-setup-001.ps1 -VaultRoot "\\server\share\vault"

# Stop trace
netsh trace stop

# Analyze with Message Analyzer or Wireshark
```

### Performance Profiling

```powershell
# Profile script execution
Measure-Command { .\vault-setup-001.ps1 }

# Detailed profiling with timestamps
$Transcript = "C:\temp\profile.txt"
Start-Transcript $Transcript
.\vault-setup-001.ps1
Stop-Transcript

# Analyze timestamps in transcript
```

### ACL Deep Inspection

```powershell
$Acl = Get-Acl "T:\Project-AI-vault"

# Full ACL dump
$Acl | Format-List *

# Access rules detailed
$Acl.Access | Format-List *

# SDDL representation
$Acl.Sddl

# Convert SDDL to readable format
ConvertFrom-SddlString $Acl.Sddl | Format-List *
```

---

## Emergency Contact Script

```powershell
<#
.SYNOPSIS
    Emergency diagnostic script - Run when nothing else works
#>

$DiagPath = "C:\temp\vault-diag-$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"

@"
=== VAULT EMERGENCY DIAGNOSTICS ===
Timestamp: $(Get-Date -Format 'o')
User: $env:USERNAME
Computer: $env:COMPUTERNAME

=== POWERSHELL ===
$(Get-Host | Format-List | Out-String)
$($PSVersionTable | Format-List | Out-String)

=== EXECUTION POLICY ===
$(Get-ExecutionPolicy -List | Format-Table | Out-String)

=== VAULT PATH ===
Exists: $(Test-Path "T:\Project-AI-vault")
$(if (Test-Path "T:\Project-AI-vault") { Get-Item "T:\Project-AI-vault" | Format-List | Out-String })

=== ACL ===
$(if (Test-Path "T:\Project-AI-vault") { Get-Acl "T:\Project-AI-vault" | Format-List | Out-String })

=== DRIVE INFO ===
$(Get-Volume -DriveLetter T -ErrorAction SilentlyContinue | Format-List | Out-String)
$(Get-PSDrive -Name T -ErrorAction SilentlyContinue | Format-List | Out-String)

=== NETWORK ===
$(Get-NetAdapter | Format-Table | Out-String)
$(Test-NetConnection -ComputerName "server" -Port 445 -ErrorAction SilentlyContinue | Format-List | Out-String)

=== RECENT ERRORS ===
$(Get-EventLog -LogName System -EntryType Error -Newest 5 -ErrorAction SilentlyContinue | Format-List | Out-String)

"@ | Out-File $DiagPath

Write-Host "Diagnostics saved to: $DiagPath" -ForegroundColor Green
notepad $DiagPath
```

---

## Support Checklist

Before requesting support, collect this information:

- [ ] PowerShell version (`$PSVersionTable`)
- [ ] Operating system version (`systeminfo`)
- [ ] Vault validation report (JSON export)
- [ ] Full error message and stack trace
- [ ] Steps to reproduce
- [ ] vault-setup.log contents
- [ ] ACL information (`Get-Acl "T:\Project-AI-vault" | Format-List`)
- [ ] Disk space (`Get-Volume`)
- [ ] Network configuration (if using network drive)

**Generate support bundle:**
```powershell
$BundlePath = "C:\temp\vault-support-bundle-$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
$TempDir = "C:\temp\vault-support"

New-Item -Path $TempDir -ItemType Directory -Force | Out-Null

# Collect files
Copy-Item "T:\Project-AI-vault\vault-*.log" $TempDir -ErrorAction SilentlyContinue
Copy-Item "T:\Project-AI-vault\vault-*.json" $TempDir -ErrorAction SilentlyContinue

# System info
systeminfo > "$TempDir\systeminfo.txt"
$PSVersionTable | Out-File "$TempDir\psversion.txt"
Get-Acl "T:\Project-AI-vault" | Out-File "$TempDir\acl.txt"

# Create zip
Compress-Archive -Path "$TempDir\*" -DestinationPath $BundlePath -Force
Remove-Item $TempDir -Recurse -Force

Write-Host "Support bundle created: $BundlePath" -ForegroundColor Green
```

---

**END OF TROUBLESHOOTING GUIDE**

*For additional support, consult VAULT_ROOT_SETUP.md or escalate to infrastructure team.*

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
