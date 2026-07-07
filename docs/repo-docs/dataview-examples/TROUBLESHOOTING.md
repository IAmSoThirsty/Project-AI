# Dataview Troubleshooting Guide

**Comprehensive diagnostic and resolution guide for Obsidian Dataview plugin issues**

**Related Documentation**:
- [[DATAVIEW_SETUP_GUIDE]] - Installation and configuration guide
- [[docs/dataview-examples/QUICK_REFERENCE]] - Query syntax reference
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration dashboard
- [[vault-troubleshooting-guide]] - General vault troubleshooting
- [[docs/architecture/STATE_MODEL]] - State management architecture

---

## Table of Contents
1. [[#quick-diagnostics|Quick Diagnostics]]
2. [[#installation-issues|Installation Issues]]
3. [[#query-errors|Query Errors]]
4. [[#performance-problems|Performance Problems]]
5. [[#dataviewjs-issues|DataviewJS Issues]]
6. [[#configuration-problems|Configuration Problems]]
7. [[#platform-specific-issues|Platform-Specific Issues]]
8. [[#advanced-debugging|Advanced Debugging]]
9. [[#system-reference|System Reference]]

---

## Quick Diagnostics

### Symptom Checker

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| Query shows as plain text | Plugin not enabled | Settings → Community Plugins → Enable Dataview |
| "No results found" | Wrong path/no matching files | Verify `FROM` path exists |
| Red error message | Syntax error | Check query syntax (commas, quotes, operators) |
| Query takes > 5s | Performance issue | Add `LIMIT`, narrow `FROM` path |
| JavaScript shows as text | DataviewJS disabled | Settings → Dataview → Enable DataviewJS |
| Fields show as null | Frontmatter mismatch | Check field names (case-sensitive) |
| Query doesn't update | Auto-refresh disabled | Settings → Dataview → Enable refresh |

### System Health Check

Run this PowerShell script to verify installation:

```powershell
# Check plugin installation
$pluginPath = ".obsidian\plugins\dataview"

Write-Host "=== Dataview Health Check ===" -ForegroundColor Cyan

# 1. Check directory exists
if (Test-Path $pluginPath) {
    Write-Host "✅ Plugin directory exists" -ForegroundColor Green
} else {
    Write-Host "❌ Plugin directory not found" -ForegroundColor Red
    Write-Host "   Run: New-Item -Path '$pluginPath' -ItemType Directory -Force"
    exit 1
}

# 2. Check required files
$requiredFiles = @("main.js", "manifest.json", "styles.css", "data.json")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $pluginPath $file
    if (Test-Path $filePath) {
        $size = (Get-Item $filePath).Length
        Write-Host "✅ $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "❌ $file missing" -ForegroundColor Red
    }
}

# 3. Check community plugins enabled
$communityPluginsPath = ".obsidian\community-plugins.json"
if (Test-Path $communityPluginsPath) {
    $plugins = Get-Content $communityPluginsPath | ConvertFrom-Json
    if ($plugins -contains "dataview") {
        Write-Host "✅ Dataview is enabled" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Dataview not in enabled list" -ForegroundColor Yellow
        Write-Host "   Add 'dataview' to $communityPluginsPath"
    }
} else {
    Write-Host "⚠️ Community plugins file not found" -ForegroundColor Yellow
}

# 4. Validate configuration
$configPath = Join-Path $pluginPath "data.json"
if (Test-Path $configPath) {
    try {
        $config = Get-Content $configPath | ConvertFrom-Json
        Write-Host "✅ Configuration valid" -ForegroundColor Green
        Write-Host "   - DataviewJS: $($config.enableDataviewJs)"
        Write-Host "   - Refresh interval: $($config.refreshInterval)ms"
    } catch {
        Write-Host "❌ Configuration JSON invalid" -ForegroundColor Red
    }
}

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
```

---

## Installation Issues

**Quick Reference**: For complete installation instructions, see [[DATAVIEW_SETUP_GUIDE]]. For vault structure, see [[docs/architecture/ROOT_STRUCTURE]] and [[OBSIDIAN_VAULT_MASTER_DASHBOARD]].

### Issue 1: Plugin Not Appearing in Settings

**Symptoms:**
- Dataview not listed in Community Plugins
- No Dataview settings page

**Diagnosis:**
```powershell
# Check plugin files
Get-ChildItem -Path ".obsidian\plugins\dataview" -Recurse
```

**Solutions:**

1. **Verify File Integrity:**
   ```powershell
   # Check main.js size (should be ~2.3 MB)
   $mainJs = ".obsidian\plugins\dataview\main.js"
   if (Test-Path $mainJs) {
       $size = (Get-Item $mainJs).Length / 1MB
       Write-Host "main.js size: $([math]::Round($size, 2)) MB"
   }
   ```

2. **Re-download Plugin:**
   ```powershell
   $url = "https://github.com/blacksmithgu/obsidian-dataview/releases/latest/download"
   Invoke-WebRequest -Uri "$url/main.js" -OutFile ".obsidian\plugins\dataview\main.js"
   Invoke-WebRequest -Uri "$url/manifest.json" -OutFile ".obsidian\plugins\dataview\manifest.json"
   Invoke-WebRequest -Uri "$url/styles.css" -OutFile ".obsidian\plugins\dataview\styles.css"
   ```

3. **Restart Obsidian:**
   - Completely close Obsidian (check Task Manager)
   - Relaunch application

4. **Check Safe Mode:**
   - Settings → Community Plugins
   - Ensure "Restricted Mode" is **OFF**

### Issue 2: Permission Errors

**Symptoms:**
- "Access denied" when enabling plugin
- Files won't download

**Solutions:**

1. **Run PowerShell as Administrator:**
   ```powershell
   # Right-click PowerShell → "Run as Administrator"
   New-Item -Path ".obsidian\plugins\dataview" -ItemType Directory -Force
   ```

2. **Check File Permissions:**
   ```powershell
   # Get current permissions
   Get-Acl ".obsidian\plugins\dataview" | Format-List
   
   # Grant full control to current user
   $acl = Get-Acl ".obsidian\plugins\dataview"
   $permission = "$env:USERNAME","FullControl","ContainerInherit,ObjectInherit","None","Allow"
   $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule $permission
   $acl.SetAccessRule($accessRule)
   Set-Acl ".obsidian\plugins\dataview" $acl
   ```

3. **Antivirus Interference:**
   - Temporarily disable antivirus
   - Add `.obsidian` folder to exclusion list
   - Re-enable after installation

---

## Query Errors

### Error 1: "Evaluation Error: ... is not defined"

**Example:**
```
Evaluation Error: status is not defined
```

**Cause:** Field referenced in query doesn't exist in frontmatter

**Diagnosis:**
```dataview
TABLE file.frontmatter
FROM "docs/dataview-examples"
LIMIT 1
```

**Solutions:**

1. **Verify Field Names:**
   ```yaml
   # In note frontmatter
   ---
   status: active    # ✅ Correct
   Status: active    # ❌ Wrong (case-sensitive)
   ---
   ```

2. **Use Default Values:**
   ```dataview
   TABLE default(status, "unknown") as "Status"
   FROM "docs/dataview-examples"
   ```

3. **Check Field Exists Before Using:**
   ```dataview
   TABLE status
   FROM "docs/dataview-examples"
   WHERE status  # Only show notes with status field
   ```

### Error 2: "Parsing Error: Expected ... but got ..."

**Example:**
```
Parsing Error: Expected ',' but got 'priority'
```

**Cause:** Missing comma between fields

**Fix:**
```dataview
❌ TABLE status priority due
✅ TABLE status, priority, due
```

### Error 3: "FROM clause is required"

**Cause:** Missing or malformed FROM clause

**Fix:**
```dataview
❌ TABLE status WHERE type = "project"
✅ TABLE status FROM "docs" WHERE type = "project"

❌ FROM docs/examples
✅ FROM "docs/examples"
```

### Error 4: "Unknown field: ..."

**Cause:** Typo in field name or field doesn't exist

**Diagnosis:**
```dataview
TABLE file.frontmatter
FROM "docs/dataview-examples"
WHERE file.name = "project-alpha"
```

**Solution:**
```dataview
# Check available fields
TABLE keys(file.frontmatter) as "Available Fields"
FROM "docs/dataview-examples"
LIMIT 1
```

---

## Performance Problems

**Quick Reference**: For performance optimization, see [[docs/architecture/STATE_MODEL#performance]] and [[docs/developer/DEVELOPMENT#optimization]].

### Issue 1: Queries Taking > 1 Second

**Symptoms:**
- UI freezes when opening note with queries
- High CPU usage
- "Loading..." message persists

**Diagnosis:**
```powershell
# Count total notes in vault
(Get-ChildItem -Path . -Recurse -Filter "*.md").Count
```

**Solutions:**

1. **Narrow Search Path:**
   ```dataview
   ❌ FROM ""                    # Scans entire vault
   ✅ FROM "docs/dataview-examples"  # Scans specific folder
   ```

2. **Add LIMIT Clause:**
   ```dataview
   TABLE status, priority
   FROM "docs"
   LIMIT 50  # Prevent rendering 1000+ rows
   ```

3. **Increase Refresh Interval:**
   ```json
   // .obsidian/plugins/dataview/data.json
   {
     "refreshInterval": 5000  // 5 seconds instead of 2.5
   }
   ```

4. **Disable Auto-Refresh for Heavy Queries:**
   ```markdown
   <!-- Disable refresh during editing -->
   <!-- dataview-refresh: false -->
   
   ```dataview
   [Heavy query here]
   ```
   ```

5. **Optimize Filters:**
   ```dataview
   ❌ WHERE contains(file.path, "project")
   ✅ WHERE type = "project"  # Direct field comparison is faster
   ```

### Issue 2: Memory Usage Growing Over Time

**Symptoms:**
- Obsidian using > 1 GB RAM
- Performance degrades over time
- Frequent crashes

**Solutions:**

1. **Restart Obsidian Daily:**
   - Close completely (check Task Manager)
   - Clears cached query results

2. **Reduce Concurrent Queries:**
   ```markdown
   # Instead of 10 queries on one page
   # Split into multiple pages with 2-3 queries each
   ```

3. **Disable Inline Queries:**
   ```json
   {
     "enableInlineDataview": false  // If not used
   }
   ```

4. **Clear Obsidian Cache:**
   ```powershell
   # Close Obsidian first
   Remove-Item -Path ".obsidian\workspace" -Force
   Remove-Item -Path ".obsidian\workspace.json" -Force
   ```

---

## DataviewJS Issues

### Issue 1: JavaScript Code Displays as Text

**Symptoms:**
```
const projects = dv.pages()...
```
Shows as plain text instead of executing

**Solutions:**

1. **Enable DataviewJS:**
   - Settings → Dataview → Enable DataviewJS ✅
   - Restart Obsidian

2. **Correct Code Block Syntax:**
   ```markdown
   ❌ ```javascript
      const pages = dv.pages();
      ```
   
   ✅ ```dataviewjs
      const pages = dv.pages();
      ```
   ```

3. **Check View Mode:**
   - DataviewJS only runs in **Reading View**
   - Press Ctrl+E to toggle view modes

### Issue 2: "dv is not defined"

**Cause:** Trying to use DataviewJS API in wrong context

**Fix:**
```markdown
❌ Inline: `const pages = dv.pages();`
✅ Code block:
```dataviewjs
const pages = dv.pages();
dv.list(pages);
```
```

### Issue 3: Errors in Console

**Diagnosis:**
1. Press Ctrl+Shift+I (Developer Tools)
2. Check Console tab for errors
3. Look for red error messages

**Common Errors:**

```javascript
// ❌ TypeError: Cannot read property 'budget' of undefined
const total = projects.reduce((sum, p) => sum + p.budget, 0);

// ✅ Handle undefined/null values
const total = projects.reduce((sum, p) => sum + (p.budget || 0), 0);
```

```javascript
// ❌ SyntaxError: Unexpected token
dv.paragraph("Text with "quotes" inside")

// ✅ Escape quotes or use backticks
dv.paragraph("Text with \"quotes\" inside")
dv.paragraph(`Text with "quotes" inside`)
```

---

## Configuration Problems

### Issue 1: Settings Not Persisting

**Symptoms:**
- Change settings in Obsidian
- Settings revert after restart

**Solutions:**

1. **Check File Permissions:**
   ```powershell
   Test-Path ".obsidian\plugins\dataview\data.json" -PathType Leaf
   ```

2. **Manually Edit Configuration:**
   ```powershell
   # Backup first
   Copy-Item ".obsidian\plugins\dataview\data.json" -Destination "data.json.backup"
   
   # Edit with text editor
   notepad ".obsidian\plugins\dataview\data.json"
   ```

3. **Validate JSON:**
   ```powershell
   Get-Content ".obsidian\plugins\dataview\data.json" | ConvertFrom-Json
   # If no error, JSON is valid
   ```

### Issue 2: Corrupted Configuration

**Symptoms:**
- Dataview won't load
- Error: "Failed to load plugin"

**Fix:**

1. **Restore Default Configuration:**
   ```powershell
   @"
   {
     "renderNullAs": "\\-",
     "taskCompletionTracking": true,
     "taskCompletionUseEmojiShorthand": false,
     "taskCompletionText": "completion",
     "taskCompletionDateFormat": "yyyy-MM-dd",
     "recursiveSubTaskCompletion": false,
     "warnOnEmptyResult": true,
     "refreshEnabled": true,
     "refreshInterval": 2500,
     "defaultDateFormat": "MMMM dd, yyyy",
     "defaultDateTimeFormat": "h:mm a - MMMM dd, yyyy",
     "maxRecursiveRenderDepth": 4,
     "tableIdColumnName": "File",
     "tableGroupColumnName": "Group",
     "showResultCount": true,
     "allowHtml": true,
     "inlineQueryPrefix": "=",
     "inlineJsQueryPrefix": "$=",
     "inlineQueriesInCodeblocks": true,
     "enableInlineDataview": true,
     "enableDataviewJs": true,
     "enableInlineDataviewJs": true,
     "prettyRenderInlineFields": true,
     "prettyRenderInlineFieldsInLivePreview": true,
     "dataviewJsKeyword": "dataviewjs"
   }
   "@ | Out-File -FilePath ".obsidian\plugins\dataview\data.json" -Encoding UTF8
   ```

2. **Restart Obsidian**

---

## Platform-Specific Issues

### Windows Issues

**Issue:** File path separators causing errors

**Fix:**
```dataview
❌ FROM "docs/examples"  # May fail on Windows
✅ FROM "docs\examples"   # Use backslashes
✅ FROM "docs/examples"   # OR use forward slashes (Obsidian normalizes)
```

**Issue:** PowerShell execution policy

**Fix:**
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Mobile (iOS/Android) Issues

**Issue:** DataviewJS disabled on mobile

**Cause:** Mobile app has security restrictions

**Workaround:**
- Use DQL (Dataview Query Language) instead of DataviewJS
- DQL works on all platforms

**Issue:** Performance worse on mobile

**Solutions:**
- Reduce `refreshInterval` to 5000ms
- Use LIMIT clauses aggressively
- Avoid complex calculations

---

## Advanced Debugging

### Enable Debug Logging

1. Open Developer Console (Ctrl+Shift+I)
2. Run in Console:
   ```javascript
   app.plugins.plugins.dataview.settings.loggingLevel = "debug"
   ```
3. Check Console for detailed logs

### Test Query Incrementally

```markdown
## Step 1: Test basic query
```dataview
TABLE file.name
FROM ""
LIMIT 5
```

## Step 2: Add specific path
```dataview
TABLE file.name
FROM "docs/dataview-examples"
```

## Step 3: Add fields
```dataview
TABLE status, priority
FROM "docs/dataview-examples"
```

## Step 4: Add filters
```dataview
TABLE status, priority
FROM "docs/dataview-examples"
WHERE status = "active"
```
```

### Isolate Problem Queries

```powershell
# Create test vault
New-Item -Path "test-vault" -ItemType Directory
New-Item -Path "test-vault\.obsidian\plugins\dataview" -ItemType Directory -Force

# Copy plugin files
Copy-Item ".obsidian\plugins\dataview\*" -Destination "test-vault\.obsidian\plugins\dataview\" -Recurse

# Open test vault in Obsidian
# Test problematic query in isolation
```

### Performance Profiling

```dataviewjs
// Measure query execution time
const start = Date.now();

const projects = dv.pages('"docs/dataview-examples"')
  .where(p => p.type === "project");

const duration = Date.now() - start;

dv.paragraph(`**Query executed in ${duration}ms**`);
dv.table(["File", "Status"], 
  projects.array().map(p => [p.file.link, p.status]));
```

---

## Error Reference

### Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `Evaluation Error: status is not defined` | Field missing in frontmatter | Add field or use `default()` |
| `Parsing Error: Expected ','` | Missing comma between fields | Add comma: `TABLE a, b` |
| `FROM clause is required` | Missing FROM | Add: `FROM "path"` |
| `Path does not exist` | Wrong folder path | Verify path with `Get-ChildItem` |
| `TypeError: Cannot read property` | Null/undefined value | Use `|| 0` or `default()` |
| `Maximum call stack size exceeded` | Infinite recursion | Reduce `maxRecursiveRenderDepth` |
| `Query timed out` | Query too complex | Add LIMIT, narrow path |

---

## Recovery Procedures

### Complete Plugin Reset

```powershell
# 1. Backup configuration
Copy-Item ".obsidian\plugins\dataview" -Destination "dataview-backup" -Recurse

# 2. Remove plugin
Remove-Item -Path ".obsidian\plugins\dataview" -Recurse -Force

# 3. Reinstall
New-Item -Path ".obsidian\plugins\dataview" -ItemType Directory -Force
$url = "https://github.com/blacksmithgu/obsidian-dataview/releases/latest/download"
Invoke-WebRequest -Uri "$url/main.js" -OutFile ".obsidian\plugins\dataview\main.js"
Invoke-WebRequest -Uri "$url/manifest.json" -OutFile ".obsidian\plugins\dataview\manifest.json"
Invoke-WebRequest -Uri "$url/styles.css" -OutFile ".obsidian\plugins\dataview\styles.css"

# 4. Restore configuration (if backup was good)
Copy-Item "dataview-backup\data.json" -Destination ".obsidian\plugins\dataview\data.json"
```

### Vault Integrity Check

```powershell
# Check for corrupted markdown files
Get-ChildItem -Path . -Recurse -Filter "*.md" | ForEach-Object {
    try {
        $content = Get-Content $_.FullName -ErrorAction Stop
        Write-Host "✅ $($_.Name)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($_.Name) - CORRUPTED" -ForegroundColor Red
    }
}
```

---

## Getting Help

### Before Asking for Help

Provide this information:

1. **System Details:**
   ```powershell
   # OS version
   [System.Environment]::OSVersion.VersionString
   
   # Obsidian version (from Settings → About)
   # Dataview version (from manifest.json)
   ```

2. **Error Message:**
   - Full text from query error
   - Console errors (Ctrl+Shift+I)

3. **Sample Query:**
   - Minimal reproducible example
   - Sample note frontmatter

4. **Steps Taken:**
   - List troubleshooting steps already attempted

### Support Channels

1. **Official Dataview Issues:**
   - https://github.com/blacksmithgu/obsidian-dataview/issues

2. **Obsidian Community Forum:**
   - https://forum.obsidian.md/tag/dataview

3. **Discord:**
   - Obsidian Members Group (invite in forum)

---

## Preventive Maintenance

### Weekly Tasks

```powershell
# 1. Backup configuration
Copy-Item ".obsidian\plugins\dataview\data.json" -Destination "backups\dataview-$(Get-Date -Format 'yyyy-MM-dd').json"

# 2. Check for updates
# Settings → Community Plugins → Check for updates

# 3. Validate critical queries
# Run test suite (see Query Library)
```

### Monthly Tasks

- Review slow queries (> 500ms)
- Archive old notes to reduce vault size
- Clean up unused frontmatter fields
- Update query documentation

---

## Version Compatibility

| Dataview Version | Obsidian Version | Notes |
|------------------|------------------|-------|
| 0.5.68 (current) | 0.13.11+ | Full feature support |
| 0.5.x | 0.12.0+ | Stable |
| 0.4.x | 0.10.0+ | Legacy, upgrade recommended |

**Upgrade Path:**
1. Backup configuration
2. Download latest release
3. Replace plugin files
4. Test critical queries
5. Report breaking changes to GitHub

---

## System Reference

### Related Architecture Documentation

- [[docs/architecture/ARCHITECTURE_OVERVIEW]] - Overall system architecture
- [[docs/architecture/STATE_MODEL]] - State management and caching
- [[docs/architecture/WORKFLOW_ENGINE]] - Query execution engine
- [[docs/architecture/MODULE_CONTRACTS]] - Module interfaces
- [[docs/architecture/ROOT_STRUCTURE]] - Project structure

### Related Setup & Configuration

- [[DATAVIEW_SETUP_GUIDE]] - Complete installation guide
- [[docs/dataview-examples/QUICK_REFERENCE]] - Query syntax reference
- [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] - Vault configuration hub
- [[TEMPLATER_SETUP_GUIDE]] - Templater integration
- [[docs/developer/config.md]] - Configuration management

### Related Troubleshooting Guides

- [[vault-troubleshooting-guide]] - Vault structure issues
- [[TEMPLATER_TROUBLESHOOTING_GUIDE]] - Templater integration
- [[GRAPH_VIEW_GUIDE]] - Graph view troubleshooting
- [[TAG_WRANGLER_GUIDE]] - Tag management
- [[.github/ISSUE_AUTOMATION]] - Automated issue handling

### Related Developer Documentation

- [[docs/developer/DEVELOPER_QUICK_REFERENCE]] - Developer reference
- [[docs/developer/DEVELOPMENT]] - Development environment
- [[docs/developer/HOW_TO_RUN]] - Running the application
- [[docs/developer/checks.md]] - Quality checks
- [[docs/developer/api.md]] - API documentation

### Related Performance Documentation

- [[docs/architecture/STATE_MODEL#performance-optimization]] - Caching strategies
- [[docs/developer/DEVELOPMENT#performance-tuning]] - Performance tuning
- [[docs/reports/DATABASE_PERSISTENCE_AUDIT_REPORT]] - Database performance

### Common Problem → Solution Map

| Problem Category | This Guide Section | Related System Documentation |
|------------------|-------------------|------------------------------|
| Plugin not appearing | [[#issue-1-plugin-not-appearing-in-settings]] | [[DATAVIEW_SETUP_GUIDE]], [[vault-troubleshooting-guide]] |
| Query shows as text | [[#quick-diagnostics]] | [[OBSIDIAN_VAULT_MASTER_DASHBOARD]] |
| Field not defined error | [[#error-1-evaluation-error-is-not-defined]] | [[docs/dataview-examples/QUICK_REFERENCE#frontmatter]] |
| Parsing errors | [[#error-2-parsing-error-expected-but-got]] | [[docs/dataview-examples/QUICK_REFERENCE#syntax]] |
| Slow queries | [[#issue-1-queries-taking-1-second]] | [[docs/architecture/STATE_MODEL#performance]] |
| DataviewJS not working | [[#issue-1-javascript-code-displays-as-text]] | [[docs/developer/DEVELOPMENT#javascript]] |
| Settings not persisting | [[#issue-1-settings-not-persisting]] | [[docs/developer/config.md]] |
| Platform-specific errors | [[#platform-specific-issues]] | [[docs/architecture/PLATFORM_COMPATIBILITY]] |

### Quick Navigation Paths

1. **Installation Issues**:
   - [[#installation-issues]] → [[DATAVIEW_SETUP_GUIDE]] → [[vault-troubleshooting-guide]]

2. **Query Syntax Errors**:
   - [[#query-errors]] → [[docs/dataview-examples/QUICK_REFERENCE]] → [[docs/developer/api.md]]

3. **Performance Problems**:
   - [[#performance-problems]] → [[docs/architecture/STATE_MODEL]] → [[docs/developer/DEVELOPMENT]]

4. **DataviewJS Issues**:
   - [[#dataviewjs-issues]] → [[docs/developer/DEVELOPMENT#javascript]] → [[docs/developer/checks.md]]

5. **Configuration Issues**:
   - [[#configuration-problems]] → [[docs/developer/config.md]] → [[OBSIDIAN_VAULT_MASTER_DASHBOARD]]

### Error Code Quick Reference

| Error Message | Likely Cause | Quick Fix | Documentation |
|---------------|--------------|-----------|---------------|
| "is not defined" | Missing frontmatter field | Add field or use `default()` | [[#error-1-evaluation-error-is-not-defined]] |
| "Expected ','" | Missing comma | Add comma between fields | [[#error-2-parsing-error-expected-but-got]] |
| "FROM clause required" | Missing FROM | Add `FROM "path"` | [[#error-3-from-clause-is-required]] |
| "Query timed out" | Query too complex | Add LIMIT, narrow path | [[#issue-1-queries-taking-1-second]] |
| "dv is not defined" | DataviewJS context issue | Use code block, not inline | [[#issue-2-dv-is-not-defined]] |

### Integration Points

- **Templater Integration**: [[TEMPLATER_TROUBLESHOOTING_GUIDE#issue-13-dataview-integration]]
- **Graph View**: [[GRAPH_VIEW_GUIDE#dataview-integration]]
- **Tag Wrangler**: [[TAG_WRANGLER_GUIDE#dataview-compatibility]]
- **Excalidraw**: [[EXCALIDRAW_GUIDE#dataview-queries]]

---

**Document Version**: 1.1.0  
**Last Updated**: 2026-04-20  
**Phase 5 Enhancement**: Added comprehensive system references and wiki links  
**Supports**: Dataview 0.5.68, Obsidian 0.13.11+
