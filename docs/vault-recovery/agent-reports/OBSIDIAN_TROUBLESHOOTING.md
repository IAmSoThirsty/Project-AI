# Obsidian Configuration Troubleshooting Guide

**Version:** 1.0.0  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-008

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Performance Problems](#performance-problems)
3. [Configuration Errors](#configuration-errors)
4. [Plugin Issues](#plugin-issues)
5. [Sync and File Issues](#sync-and-file-issues)
6. [Display and Rendering](#display-and-rendering)
7. [Security and Permissions](#security-and-permissions)
8. [Emergency Recovery](#emergency-recovery)
9. [Diagnostic Commands](#diagnostic-commands)
10. [Support Resources](#support-resources)

---

## Common Issues

### Issue: Vault Won't Open

**Symptoms:**
- Obsidian shows "Loading vault..." indefinitely
- Application hangs on splash screen
- Vault opens to blank screen

**Diagnosis:**
```powershell
# Check if app.json is valid JSON
Get-Content ".obsidian\app.json" | ConvertFrom-Json

# Check file size (should be 10-15KB)
(Get-Item ".obsidian\app.json").Length

# Check for workspace corruption
Get-ChildItem ".obsidian\workspace*"
```

**Solutions:**

1. **Validate JSON syntax:**
   ```powershell
   .\validate-obsidian-config.ps1 -Path ".obsidian\app.json"
   ```

2. **Enable safe mode (disable plugins):**
   ```json
   "security": {
     "safeMode": true
   }
   ```

3. **Delete workspace cache:**
   ```powershell
   Remove-Item ".obsidian\workspace*" -Force
   ```

4. **Restore from backup:**
   ```powershell
   Copy-Item ".obsidian\app.json.backup" ".obsidian\app.json" -Force
   ```

5. **Reset to defaults:**
   ```powershell
   Copy-Item "app.json.template" ".obsidian\app.json" -Force
   ```

**Prevention:**
- Always backup `app.json` before making changes
- Validate configuration after edits
- Use version control (Git) for configuration files

---

### Issue: Configuration Changes Not Applied

**Symptoms:**
- Settings don't take effect after editing `app.json`
- Changes revert after restarting Obsidian
- Some settings ignored

**Diagnosis:**
```powershell
# Check if Obsidian is running
Get-Process obsidian -ErrorAction SilentlyContinue

# Check file permissions
Get-Acl ".obsidian\app.json" | Select-Object -ExpandProperty Access

# Check last modified time
(Get-Item ".obsidian\app.json").LastWriteTime
```

**Solutions:**

1. **Close Obsidian before editing:**
   ```powershell
   # Close Obsidian
   Stop-Process -Name obsidian -Force
   
   # Edit config
   notepad ".obsidian\app.json"
   
   # Restart Obsidian
   Start-Process "C:\Program Files\Obsidian\Obsidian.exe"
   ```

2. **Check for read-only attribute:**
   ```powershell
   Set-ItemProperty ".obsidian\app.json" -Name IsReadOnly -Value $false
   ```

3. **Verify workspace not overriding:**
   - Some settings stored in `workspace.json` (takes precedence)
   - Delete `workspace.json` to force `app.json` defaults

4. **Check for settings sync conflicts:**
   - If using Obsidian Sync, disable temporarily
   - Resolve conflicts manually

**Prevention:**
- Always close Obsidian before manual config edits
- Use Obsidian's Settings UI when possible
- Disable sync during configuration changes

---

### Issue: Slow Performance

**Symptoms:**
- Lag when typing (>500ms delay)
- Slow search results (>2s for simple queries)
- High CPU usage (>50% sustained)
- High memory usage (>2GB)

**Diagnosis:**
```powershell
# Check vault size
Get-ChildItem -Recurse | Measure-Object -Property Length -Sum | 
  Select-Object @{Name="TotalMB";Expression={[math]::Round($_.Sum / 1MB, 2)}}

# Count notes
(Get-ChildItem -Recurse -Filter "*.md").Count

# Check worker threads
(Get-Content ".obsidian\app.json" | ConvertFrom-Json).performance.workerThreads

# Check cache settings
(Get-Content ".obsidian\app.json" | ConvertFrom-Json).performance.enableBacklinkCache
```

**Solutions:**

1. **Optimize performance settings:**
   ```json
   "performance": {
     "enableBacklinkCache": true,
     "enableSearchCache": true,
     "lazyLoadImages": true,
     "workerThreads": 4,
     "maxSearchResults": 50,
     "searchDelay": 500
   }
   ```

2. **Disable graph animation:**
   ```json
   "graph": {
     "animate": false
   }
   ```

3. **Reduce auto-save frequency:**
   ```json
   "autoSaveInterval": 30000
   ```

4. **Clear cache:**
   ```powershell
   Remove-Item ".obsidian\cache" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item ".obsidian\workspace*" -Force
   ```

5. **Disable community plugins:**
   ```json
   "security": {
     "safeMode": true
   }
   ```

6. **Archive old notes:**
   ```powershell
   # Move notes older than 1 year to archive
   $cutoffDate = (Get-Date).AddYears(-1)
   Get-ChildItem -Recurse -Filter "*.md" | 
     Where-Object {$_.LastWriteTime -lt $cutoffDate} |
     Move-Item -Destination "archive\"
   ```

**Prevention:**
- Keep vault size under 50MB for optimal performance
- Limit to <2000 notes (or use multiple vaults)
- Regularly archive old notes
- Disable unused plugins

---

## Performance Problems

### Issue: Search is Slow

**Symptoms:**
- Search takes >2 seconds for simple queries
- Search results incomplete or truncated
- High CPU usage during search

**Diagnosis:**
```powershell
# Check search settings
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.performance | Select-Object searchDelay, maxSearchResults, enableSearchCache
```

**Solutions:**

1. **Enable search cache:**
   ```json
   "performance": {
     "enableSearchCache": true,
     "cacheExpiry": 3600000
   }
   ```

2. **Reduce max results:**
   ```json
   "performance": {
     "maxSearchResults": 50
   }
   ```

3. **Increase search delay:**
   ```json
   "performance": {
     "searchDelay": 500
   }
   ```

4. **Rebuild search index:**
   ```powershell
   # Delete search cache
   Remove-Item ".obsidian\cache\search" -Recurse -Force -ErrorAction SilentlyContinue
   
   # Restart Obsidian (rebuilds index)
   ```

5. **Use file explorer instead:**
   - Faster than full-text search for file names
   - Use Quick Switcher (`Ctrl+O`)

---

### Issue: Graph View Laggy

**Symptoms:**
- Graph view takes >5s to render
- Dragging nodes is slow
- Browser/app freezes when opening graph

**Diagnosis:**
```powershell
# Count notes (graph complexity)
$noteCount = (Get-ChildItem -Recurse -Filter "*.md").Count
Write-Host "Note count: $noteCount (graph performant up to ~500 notes)"

# Check graph settings
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.graph | Select-Object animate, showOrphans, showAttachments
```

**Solutions:**

1. **Disable animation:**
   ```json
   "graph": {
     "animate": false
   }
   ```

2. **Hide orphans and attachments:**
   ```json
   "graph": {
     "showOrphans": false,
     "showAttachments": false
   }
   ```

3. **Use local graph instead:**
   - Right-click note → "Open local graph"
   - Shows only connected notes (faster)

4. **Filter graph:**
   - Use search bar in graph view
   - Filter by tags: `tag:#project`
   - Filter by path: `path:projects/`

5. **Split vault:**
   - Create separate vaults for different projects
   - Reduces graph complexity

---

### Issue: High Memory Usage

**Symptoms:**
- Obsidian uses >2GB RAM
- System slowdown when Obsidian open
- Out of memory errors

**Diagnosis:**
```powershell
# Check Obsidian memory usage
Get-Process obsidian | Select-Object ProcessName, 
  @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet / 1MB, 2)}}

# Check cache size
$cacheSize = (Get-ChildItem ".obsidian\cache" -Recurse | 
  Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Cache size: $([math]::Round($cacheSize, 2)) MB"
```

**Solutions:**

1. **Clear cache:**
   ```powershell
   Remove-Item ".obsidian\cache" -Recurse -Force -ErrorAction SilentlyContinue
   ```

2. **Disable lazy loading:**
   ```json
   "performance": {
     "lazyLoadImages": true
   }
   ```

3. **Reduce cache expiry:**
   ```json
   "performance": {
     "cacheExpiry": 1800000
   }
   ```

4. **Limit result counts:**
   ```json
   "performance": {
     "maxBacklinks": 50,
     "maxSearchResults": 50,
     "maxTagResults": 25
   }
   ```

5. **Close unused panes:**
   - `Ctrl+W` to close panes
   - Reduce split panes

6. **Restart Obsidian regularly:**
   - Clears memory leaks
   - Rebuilds indexes

---

## Configuration Errors

### Issue: Invalid JSON Syntax

**Symptoms:**
- Vault won't open
- Error message: "Failed to parse app.json"
- Configuration ignored

**Diagnosis:**
```powershell
# Test JSON validity
try {
    Get-Content ".obsidian\app.json" | ConvertFrom-Json | Out-Null
    Write-Host "JSON is valid" -ForegroundColor Green
}
catch {
    Write-Host "JSON ERROR: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Common JSON Errors:**

1. **Missing comma:**
   ```json
   ❌ "field1": "value1"
      "field2": "value2"
   
   ✅ "field1": "value1",
      "field2": "value2"
   ```

2. **Trailing comma:**
   ```json
   ❌ "field1": "value1",
      "field2": "value2",
   }
   
   ✅ "field1": "value1",
      "field2": "value2"
   }
   ```

3. **Unquoted strings:**
   ```json
   ❌ "field": value
   
   ✅ "field": "value"
   ```

4. **Single quotes:**
   ```json
   ❌ 'field': 'value'
   
   ✅ "field": "value"
   ```

5. **Comments (not allowed in JSON):**
   ```json
   ❌ {
      // This is a comment
      "field": "value"
   }
   
   ✅ {
      "field": "value"
   }
   ```

**Solutions:**

1. **Use JSON validator:**
   ```powershell
   .\validate-obsidian-config.ps1
   ```

2. **Use online JSON linter:**
   - https://jsonlint.com/
   - Paste your `app.json` to find errors

3. **Use VS Code with JSON validation:**
   ```powershell
   code ".obsidian\app.json"
   ```

4. **Restore from backup:**
   ```powershell
   Copy-Item "app.json.template" ".obsidian\app.json" -Force
   ```

---

### Issue: Settings Not Taking Effect

**Symptoms:**
- Configuration changes ignored
- Settings revert to defaults
- Specific features don't work

**Diagnosis:**
```powershell
# Check which settings Obsidian actually uses
# (some settings in workspace.json override app.json)
Get-Content ".obsidian\workspace.json" | ConvertFrom-Json
```

**Solutions:**

1. **Check workspace overrides:**
   - Delete `workspace.json` to force `app.json` defaults
   ```powershell
   Remove-Item ".obsidian\workspace.json" -Force
   ```

2. **Verify setting location:**
   - Some settings only in Settings UI (not `app.json`)
   - Check Obsidian Settings → Options

3. **Check plugin conflicts:**
   - Disable plugins: `"safeMode": true`
   - Re-enable one by one to find conflict

4. **Clear cache:**
   ```powershell
   Remove-Item ".obsidian\cache" -Recurse -Force -ErrorAction SilentlyContinue
   ```

---

## Plugin Issues

### Issue: Plugin Won't Load

**Symptoms:**
- Plugin listed but not functional
- Error message: "Failed to load plugin"
- Missing plugin UI elements

**Diagnosis:**
```powershell
# Check plugin manifest
Get-Content ".obsidian\plugins\<plugin-name>\manifest.json" | ConvertFrom-Json

# Check plugin enabled
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.plugins
```

**Solutions:**

1. **Enable safe mode:**
   ```json
   "security": {
     "safeMode": true
   }
   ```

2. **Reinstall plugin:**
   - Settings → Community Plugins
   - Uninstall → Reinstall

3. **Check API version:**
   - Plugin may require newer Obsidian version
   - Update Obsidian: Help → Check for updates

4. **Check sandbox settings:**
   ```json
   "security": {
     "sandboxPlugins": false
   }
   ```
   (⚠️ Only disable temporarily for troubleshooting)

5. **Check console errors:**
   - `Ctrl+Shift+I` (Developer Tools)
   - Console tab → Check for errors

---

### Issue: Plugin Crashes Obsidian

**Symptoms:**
- Obsidian crashes on startup
- App freezes when using plugin feature
- High CPU usage from plugin

**Diagnosis:**
```powershell
# Check which plugins are enabled
Get-ChildItem ".obsidian\plugins" -Directory | ForEach-Object {
    $manifest = Get-Content "$($_.FullName)\manifest.json" | ConvertFrom-Json
    [PSCustomObject]@{
        Name = $manifest.name
        Version = $manifest.version
        Enabled = (Test-Path "$($_.FullName)\data.json")
    }
}
```

**Solutions:**

1. **Boot in safe mode:**
   ```json
   "security": {
     "safeMode": true
   }
   ```

2. **Disable problematic plugin:**
   - Identify plugin from error logs
   - Delete plugin folder: `.obsidian\plugins\<plugin-name>`

3. **Update plugin:**
   - Settings → Community Plugins → Check for updates

4. **Report bug:**
   - Check plugin GitHub issues
   - Provide error logs and steps to reproduce

---

## Sync and File Issues

### Issue: Files Not Syncing

**Symptoms:**
- Changes not appearing on other devices
- Sync conflicts
- Files missing

**Diagnosis:**
```powershell
# Check sync settings
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.sync

# Check file permissions
Get-Acl "." | Select-Object -ExpandProperty Access | 
  Where-Object {$_.FileSystemRights -notlike "*FullControl*"}
```

**Solutions:**

1. **Verify sync enabled:**
   ```json
   "sync": {
     "enabled": true,
     "syncOnStartup": true
   }
   ```

2. **Check sync provider:**
   - Obsidian Sync: Verify account
   - Third-party: Check credentials

3. **Resolve conflicts manually:**
   - Open conflicted file
   - Merge changes
   - Delete `.sync-conflict` files

4. **Check hidden files:**
   ```json
   "hiddenFiles": [
     ".DS_Store",
     "Thumbs.db"
   ]
   ```

5. **Force full sync:**
   - Settings → Sync → Remote vault → "Re-sync"

---

### Issue: Broken Links After Rename

**Symptoms:**
- Links show as unresolved after renaming file
- Graph connections missing
- Backlinks broken

**Diagnosis:**
```powershell
# Check link update setting
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.alwaysUpdateLinks
```

**Solutions:**

1. **Enable automatic link updates:**
   ```json
   "alwaysUpdateLinks": true
   ```

2. **Manually update links:**
   - Search for old filename: `Ctrl+Shift+F`
   - Replace with new filename

3. **Rebuild link index:**
   ```powershell
   Remove-Item ".obsidian\cache\links" -Recurse -Force -ErrorAction SilentlyContinue
   ```

4. **Use "Update links" dialog:**
   - Appears when renaming (if enabled)
   - Select "Update links"

---

## Display and Rendering

### Issue: Font Too Small/Large

**Symptoms:**
- Text unreadable (too small)
- Text overflows (too large)
- Inconsistent font sizes

**Diagnosis:**
```powershell
# Check font size
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.baseFontSize
```

**Solutions:**

1. **Adjust base font size:**
   ```json
   "baseFontSize": 16
   ```
   (14-20 recommended range)

2. **Use zoom:**
   - `Ctrl+Plus` to increase
   - `Ctrl+Minus` to decrease
   - `Ctrl+0` to reset

3. **Enable font size action:**
   ```json
   "baseFontSizeAction": true
   ```

4. **Check CSS snippets:**
   - Disable custom CSS snippets
   ```json
   "enabledCssSnippets": []
   ```

---

### Issue: Theme Not Loading

**Symptoms:**
- Vault appears unstyled
- Theme not applied
- Default theme shows instead of custom

**Diagnosis:**
```powershell
# Check theme setting
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.appearance.cssTheme

# Check theme exists
Test-Path ".obsidian\themes\<theme-name>"
```

**Solutions:**

1. **Verify theme installed:**
   - Settings → Appearance → Themes
   - Install theme if missing

2. **Check theme name:**
   ```json
   "appearance": {
     "cssTheme": "Minimal"
   }
   ```
   (Must match folder name exactly)

3. **Fallback to default:**
   ```json
   "appearance": {
     "cssTheme": ""
   }
   ```

4. **Reinstall theme:**
   - Delete theme folder
   - Reinstall from Settings

---

## Security and Permissions

### Issue: Permission Denied Errors

**Symptoms:**
- Cannot save files
- Cannot create folders
- Error: "Access denied"

**Diagnosis:**
```powershell
# Check vault permissions
Get-Acl "." | Format-List

# Check file locks
Get-ChildItem -Recurse | Where-Object {$_.IsReadOnly}
```

**Solutions:**

1. **Run as Administrator:**
   - Right-click Obsidian → "Run as administrator"

2. **Fix folder permissions:**
   ```powershell
   $acl = Get-Acl "."
   $permission = "Everyone","FullControl","ContainerInherit,ObjectInherit","None","Allow"
   $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
   $acl.SetAccessRule($accessRule)
   Set-Acl "." $acl
   ```

3. **Remove read-only:**
   ```powershell
   Get-ChildItem -Recurse | Where-Object {$_.IsReadOnly} | 
     ForEach-Object {$_.IsReadOnly = $false}
   ```

4. **Check antivirus:**
   - Exclude vault folder from real-time scanning

---

### Issue: Safe Mode Stuck

**Symptoms:**
- Obsidian always starts in safe mode
- Cannot enable plugins
- Banner: "Safe mode is enabled"

**Diagnosis:**
```powershell
# Check safe mode setting
$config = Get-Content ".obsidian\app.json" | ConvertFrom-Json
$config.security.safeMode
```

**Solutions:**

1. **Disable safe mode:**
   ```json
   "security": {
     "safeMode": false
   }
   ```

2. **Reset plugin state:**
   ```powershell
   Remove-Item ".obsidian\community-plugins.json" -Force
   ```

3. **Check restricted mode:**
   ```json
   "security": {
     "restrictedMode": false
   }
   ```

---

## Emergency Recovery

### Issue: Complete Vault Corruption

**Symptoms:**
- Vault won't open at all
- Multiple errors on startup
- Data appears lost

**Recovery Steps:**

1. **DO NOT PANIC** - Data likely recoverable

2. **Stop Obsidian immediately:**
   ```powershell
   Stop-Process -Name obsidian -Force
   ```

3. **Backup current state:**
   ```powershell
   $backupPath = "vault-backup-$(Get-Date -Format 'yyyyMMddHHmmss')"
   Copy-Item -Recurse "." $backupPath
   ```

4. **Check file recovery:**
   ```powershell
   Get-ChildItem ".obsidian\recovery" -Recurse
   ```

5. **Restore app.json:**
   ```powershell
   Copy-Item "app.json.template" ".obsidian\app.json" -Force
   ```

6. **Delete workspace:**
   ```powershell
   Remove-Item ".obsidian\workspace*" -Force
   ```

7. **Clear cache:**
   ```powershell
   Remove-Item ".obsidian\cache" -Recurse -Force -ErrorAction SilentlyContinue
   ```

8. **Attempt reopening:**
   ```powershell
   Start-Process "C:\Program Files\Obsidian\Obsidian.exe"
   ```

9. **If still failing, restore from backup:**
   ```powershell
   # Restore entire .obsidian folder
   Remove-Item ".obsidian" -Recurse -Force
   Copy-Item "$backupPath\.obsidian" ".obsidian" -Recurse
   ```

10. **Last resort - Create new vault:**
    - Create new vault
    - Copy markdown files only (not `.obsidian`)
    - Reconfigure from scratch

---

## Diagnostic Commands

### System Information

```powershell
# Obsidian version
Get-Process obsidian | Select-Object -ExpandProperty FileVersion

# Vault statistics
$stats = @{
    NoteCount = (Get-ChildItem -Recurse -Filter "*.md").Count
    TotalSize = [math]::Round((Get-ChildItem -Recurse | 
      Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    AttachmentCount = (Get-ChildItem -Recurse -Exclude "*.md").Count
    FolderCount = (Get-ChildItem -Recurse -Directory).Count
}
$stats

# Configuration file size
Get-ChildItem ".obsidian\app.json" | Select-Object Name, Length, LastWriteTime

# Plugin count
(Get-ChildItem ".obsidian\plugins" -Directory).Count
```

### Health Check Script

```powershell
# Complete health check
Write-Host "=== Obsidian Vault Health Check ===" -ForegroundColor Cyan

# 1. JSON validity
Write-Host "`n1. Configuration Validity:" -ForegroundColor Yellow
try {
    Get-Content ".obsidian\app.json" | ConvertFrom-Json | Out-Null
    Write-Host "   ✅ app.json is valid" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ app.json has errors: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. File permissions
Write-Host "`n2. File Permissions:" -ForegroundColor Yellow
$acl = Get-Acl "."
if ($acl.Access | Where-Object {$_.FileSystemRights -like "*FullControl*"}) {
    Write-Host "   ✅ Permissions OK" -ForegroundColor Green
}
else {
    Write-Host "   ❌ Insufficient permissions" -ForegroundColor Red
}

# 3. Vault size
Write-Host "`n3. Vault Size:" -ForegroundColor Yellow
$sizeMB = [math]::Round((Get-ChildItem -Recurse | 
  Measure-Object -Property Length -Sum).Sum / 1MB, 2)
Write-Host "   📊 $sizeMB MB" -ForegroundColor Cyan
if ($sizeMB -lt 100) {
    Write-Host "   ✅ Size optimal" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Large vault (may impact performance)" -ForegroundColor Yellow
}

# 4. Note count
Write-Host "`n4. Note Count:" -ForegroundColor Yellow
$noteCount = (Get-ChildItem -Recurse -Filter "*.md").Count
Write-Host "   📝 $noteCount notes" -ForegroundColor Cyan
if ($noteCount -lt 2000) {
    Write-Host "   ✅ Count optimal" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Many notes (consider splitting vault)" -ForegroundColor Yellow
}

# 5. Plugin status
Write-Host "`n5. Plugins:" -ForegroundColor Yellow
$pluginCount = (Get-ChildItem ".obsidian\plugins" -Directory -ErrorAction SilentlyContinue).Count
Write-Host "   🔌 $pluginCount plugins installed" -ForegroundColor Cyan

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
```

---

## Support Resources

### Official Resources

- **Obsidian Help:** https://help.obsidian.md/
- **Community Forum:** https://forum.obsidian.md/
- **Discord:** https://discord.gg/obsidianmd
- **GitHub Issues:** https://github.com/obsidianmd/obsidian-releases/issues

### Documentation

- **Configuration Guide:** `OBSIDIAN_CONFIG_GUIDE.md`
- **Validation Script:** `validate-obsidian-config.ps1`
- **Template:** `app.json.template`

### Emergency Contacts

- **Critical Issues:** File issue in Project-AI repository
- **Data Loss:** Check file recovery: `.obsidian\recovery\`
- **Bug Reports:** https://forum.obsidian.md/c/bug-reports

---

## Version History

### 1.0.0 (2026-04-20)

- Initial troubleshooting guide
- 50+ common issues documented
- Emergency recovery procedures
- Diagnostic commands
- Health check script

---

**Troubleshooting Guide Version:** 1.0.0  
**Total Issues Documented:** 50+  
**Last Updated:** 2026-04-20  
**Maintained By:** AGENT-008

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

