# Repo-Docs Troubleshooting Guide

**AGENT-005: Repo Docs Linking Specialist**  
**Production-Grade Documentation**

---

## Overview

This guide addresses common issues when linking T:\Project-AI-main\docs to T:\Project-AI-vault\repo-docs using the `repo-docs-link-strategy.ps1` script.

---

## Quick Diagnosis

```powershell
# Check if repo-docs exists
Test-Path "T:\Project-AI-vault\repo-docs"

# Check link type
(Get-Item "T:\Project-AI-vault\repo-docs").LinkType

# Count accessible files
(Get-ChildItem "T:\Project-AI-vault\repo-docs" -Recurse -File).Count
```

**Expected**: 456 files accessible

---

## Common Issues & Solutions

### Issue 1: "Access Denied" or "Symlink Creation Failed"

**Symptom**: Script fails with permission errors when creating symbolic links.

**Cause**: Symbolic links require Administrator privileges on Windows.

**Solutions** (in order):

1. **Run as Administrator**:
   ```powershell
   # Right-click PowerShell -> "Run as Administrator"
   cd T:\Project-AI-vault
   .\repo-docs-link-strategy.ps1
   ```

2. **Use Junction (No Admin Required)**:
   ```powershell
   .\repo-docs-link-strategy.ps1 -Strategy Junction
   ```

3. **Use Copy Fallback**:
   ```powershell
   .\repo-docs-link-strategy.ps1 -Strategy Copy
   ```

4. **Enable Developer Mode** (Windows 10/11):
   - Settings → Update & Security → For developers
   - Enable "Developer Mode"
   - Restart PowerShell (non-admin will work)

---

### Issue 2: "Target Already Exists"

**Symptom**: Script fails because repo-docs directory already exists.

**Cause**: Previous execution created the directory.

**Solution**:

```powershell
# Force recreation
.\repo-docs-link-strategy.ps1 -Force

# Or manually remove first
Remove-Item "T:\Project-AI-vault\repo-docs" -Recurse -Force
.\repo-docs-link-strategy.ps1
```

---

### Issue 3: Junction Works But Files Not Accessible

**Symptom**: Junction created but file enumeration fails.

**Cause**: 
- Different drives (Junctions work best on same volume)
- NTFS permissions issues
- Antivirus blocking access

**Solutions**:

1. **Check if drives are different**:
   ```powershell
   # If source and target on different drives, use Copy
   .\repo-docs-link-strategy.ps1 -Strategy Copy
   ```

2. **Check NTFS permissions**:
   ```powershell
   # Verify you have read access to source
   $acl = Get-Acl "T:\Project-AI-main\docs"
   $acl.Access | Format-Table IdentityReference, FileSystemRights
   ```

3. **Disable antivirus temporarily** and re-run.

---

### Issue 4: Robocopy Fails or Incomplete Copy

**Symptom**: Copy strategy reports errors or missing files.

**Cause**:
- Insufficient disk space
- File locks (files in use)
- Permission issues on individual files

**Solutions**:

1. **Check disk space**:
   ```powershell
   Get-PSDrive T | Select-Object Name, Used, Free
   ```

2. **Review Robocopy log**:
   ```powershell
   # Find latest log
   Get-ChildItem "T:\Project-AI-vault\robocopy-*.log" | 
       Sort-Object LastWriteTime -Descending | 
       Select-Object -First 1 | 
       Get-Content -Tail 50
   ```

3. **Retry with exclusions**:
   ```powershell
   # Manually run robocopy with exclusions
   robocopy "T:\Project-AI-main\docs" "T:\Project-AI-vault\repo-docs" /MIR /XF *.tmp *.lock
   ```

---

### Issue 5: Validation Reports Inaccessible Files

**Symptom**: Script completes but validation shows some files inaccessible.

**Cause**:
- File locks
- Corrupted files
- Long path names (> 260 characters)

**Solutions**:

1. **Review validation report**:
   ```powershell
   $report = Get-Content "T:\Project-AI-vault\repo-docs-validation-report.json" | ConvertFrom-Json
   $report.Errors
   ```

2. **Enable long path support** (Windows 10+):
   ```powershell
   # Run as Admin
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
       -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

3. **Check specific files**:
   ```powershell
   # Test access to reported files
   foreach ($error in $report.Errors) {
       Write-Host "Testing: $error"
       Test-Path $error.Split('-')[0].Trim()
   }
   ```

---

### Issue 6: "Insufficient Disk Space"

**Symptom**: Script aborts with disk space error.

**Cause**: Copy strategy needs ~456 files worth of space.

**Solutions**:

1. **Use Junction/Symlink (No Space Needed)**:
   ```powershell
   # Run as Admin
   .\repo-docs-link-strategy.ps1 -Strategy SymbolicLink
   ```

2. **Free up space**:
   ```powershell
   # Find large files to remove
   Get-ChildItem "T:\Project-AI-vault" -Recurse -File | 
       Sort-Object Length -Descending | 
       Select-Object -First 10 | 
       Format-Table Name, @{L='Size(MB)';E={[math]::Round($_.Length/1MB,2)}}
   ```

3. **Use different target drive**:
   ```powershell
   .\repo-docs-link-strategy.ps1 -TargetPath "C:\vault-docs\repo-docs"
   ```

---

### Issue 7: Script Hangs or Takes Very Long

**Symptom**: Script appears frozen during copy operation.

**Cause**: Large directory copy with minimal progress feedback.

**Solutions**:

1. **Check if Robocopy is actually running**:
   ```powershell
   # In another PowerShell window
   Get-Process robocopy
   ```

2. **Monitor progress via log**:
   ```powershell
   # In another PowerShell window
   Get-Content "T:\Project-AI-vault\robocopy-*.log" -Wait -Tail 20
   ```

3. **Expected duration**: 2-10 minutes for 456 files (depends on file sizes).

---

## Strategy Comparison

| Strategy       | Admin Required | Disk Space | Speed     | Updates Source | Notes                              |
|----------------|----------------|------------|-----------|----------------|------------------------------------|
| SymbolicLink   | Yes            | None       | Instant   | Yes            | Best option if admin available     |
| Junction       | No             | None       | Instant   | Yes            | Works only on same volume          |
| Copy           | No             | Full copy  | 2-10 min  | No             | Most compatible, fallback option   |

---

## Advanced Troubleshooting

### Enable Debug Logging

```powershell
# Run with verbose output
.\repo-docs-link-strategy.ps1 -Verbose

# Examine detailed log
Get-Content "T:\Project-AI-vault\repo-docs-link-*.log" | Select-String "ERROR|WARNING"
```

### Test Individual Components

```powershell
# Test symlink capability
$testTarget = "T:\Project-AI-vault\_test_symlink"
New-Item -ItemType SymbolicLink -Path $testTarget -Target "T:\Project-AI-main\docs"
if ($?) {
    Write-Host "✓ Symlinks work" -ForegroundColor Green
    Remove-Item $testTarget
} else {
    Write-Host "✗ Symlinks require admin or Dev Mode" -ForegroundColor Red
}

# Test junction capability  
$testJunction = "T:\Project-AI-vault\_test_junction"
New-Item -ItemType Junction -Path $testJunction -Target "T:\Project-AI-main\docs"
if ($?) {
    Write-Host "✓ Junctions work" -ForegroundColor Green
    Remove-Item $testJunction
} else {
    Write-Host "✗ Junctions failed (check same volume)" -ForegroundColor Red
}
```

### Verify File Integrity

```powershell
# Compare source vs target file counts
$sourceCount = (Get-ChildItem "T:\Project-AI-main\docs" -Recurse -File).Count
$targetCount = (Get-ChildItem "T:\Project-AI-vault\repo-docs" -Recurse -File).Count

Write-Host "Source files: $sourceCount"
Write-Host "Target files: $targetCount"

if ($sourceCount -eq $targetCount) {
    Write-Host "✓ File counts match" -ForegroundColor Green
} else {
    Write-Host "✗ File count mismatch!" -ForegroundColor Red
}
```

---

## Recovery Procedures

### Full Reset

```powershell
# Remove repo-docs completely
if (Test-Path "T:\Project-AI-vault\repo-docs") {
    $item = Get-Item "T:\Project-AI-vault\repo-docs"
    if ($item.LinkType) {
        # It's a link - safe to remove
        Remove-Item "T:\Project-AI-vault\repo-docs" -Force
    } else {
        # It's a copy - will take time
        Remove-Item "T:\Project-AI-vault\repo-docs" -Recurse -Force
    }
}

# Clean up logs
Remove-Item "T:\Project-AI-vault\repo-docs-link-*.log" -ErrorAction SilentlyContinue
Remove-Item "T:\Project-AI-vault\robocopy-*.log" -ErrorAction SilentlyContinue
Remove-Item "T:\Project-AI-vault\repo-docs-validation-report.json" -ErrorAction SilentlyContinue

# Start fresh
.\repo-docs-link-strategy.ps1 -Strategy Auto
```

### Emergency Manual Copy

```powershell
# If script completely fails, manual robocopy
robocopy "T:\Project-AI-main\docs" "T:\Project-AI-vault\repo-docs" /E /COPY:DAT /DCOPY:T /R:2 /W:5 /MT:8

# Verify
(Get-ChildItem "T:\Project-AI-vault\repo-docs" -Recurse -File).Count
```

---

## Validation Checklist

After running the script, verify:

- [ ] `T:\Project-AI-vault\repo-docs` exists
- [ ] Directory contains 456 files
- [ ] Sample files are readable
- [ ] Validation report shows 100% accessibility
- [ ] Link type matches expected strategy (SymbolicLink/Junction/Copy)
- [ ] Source updates reflect in target (for links only)

**Quick validation**:
```powershell
# All-in-one check
$path = "T:\Project-AI-vault\repo-docs"
if (Test-Path $path) {
    $item = Get-Item $path
    $count = (Get-ChildItem $path -Recurse -File).Count
    Write-Host "✓ Exists: $path" -ForegroundColor Green
    Write-Host "  Type: $($item.LinkType ?? 'Directory')"
    Write-Host "  Files: $count (expected 456)"
    if ($count -eq 456) {
        Write-Host "✓ ALL DOCS ACCESSIBLE" -ForegroundColor Green
    }
} else {
    Write-Host "✗ repo-docs not found" -ForegroundColor Red
}
```

---

## Support Escalation

If issues persist after trying all solutions:

1. **Collect diagnostics**:
   ```powershell
   # Create support package
   $supportDir = "T:\Project-AI-vault\support-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
   New-Item -ItemType Directory -Path $supportDir
   
   # Copy logs
   Copy-Item "T:\Project-AI-vault\*.log" $supportDir
   Copy-Item "T:\Project-AI-vault\*-report.json" $supportDir
   
   # System info
   Get-ComputerInfo | Out-File "$supportDir\system-info.txt"
   Get-PSDrive | Out-File "$supportDir\drives.txt"
   
   Write-Host "Support package: $supportDir"
   ```

2. **Review system requirements**:
   - Windows 10/11 or Windows Server 2016+
   - PowerShell 5.1 or PowerShell 7+
   - NTFS file system on both drives
   - Network drives not recommended for symlinks

3. **Alternative approaches**:
   - Use network share: `\\server\Project-AI-main\docs`
   - Use cloud sync (OneDrive, Dropbox)
   - Use Git submodules
   - Manual periodic sync with robocopy scheduled task

---

## Best Practices

1. **Run as Administrator** for best results (enables symlinks)
2. **Use Auto strategy** to let script choose optimal method
3. **Check logs** after execution for warnings
4. **Verify validation report** shows 100% accessibility
5. **Test after Windows updates** (permissions may change)
6. **Backup before Force flag** if repo-docs contains custom additions

---

## Exit Codes

| Code | Meaning                      | Action Required                     |
|------|------------------------------|-------------------------------------|
| 0    | Success (all docs accessible)| None - mission accomplished         |
| 1    | Fatal error or no docs       | Check logs, see Issue solutions     |
| 2    | Partial success              | Review validation report for details|

---

## Related Files

- `repo-docs-link-strategy.ps1` - Main linking script
- `repo-docs-link-*.log` - Execution logs
- `repo-docs-validation-report.json` - Accessibility report
- `robocopy-*.log` - Robocopy operation logs (if Copy strategy used)

---

**Last Updated**: 2025-01-13  
**Agent**: AGENT-005  
**Version**: 1.0.0

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

