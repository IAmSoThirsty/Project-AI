# 🔗 Repo-Docs Quick Reference Card

**AGENT-005 Deliverable** | Production-Ready | Version 1.0.0

---

## 📍 Location

```
T:\Project-AI-vault\repo-docs  →  T:\Project-AI-main\docs
```

**Type**: Symbolic Link  
**Files**: 463 documents (100% accessible)  
**Disk Space**: ~0 MB (link only)

---

## ⚡ Quick Commands

### Access Documentation
```powershell
cd T:\Project-AI-vault\repo-docs
explorer .
```

### Validate Accessibility
```powershell
cd T:\Project-AI-vault
.\validate-repo-docs.ps1
```

### Recreate Link (if needed)
```powershell
.\repo-docs-link-strategy.ps1 -Force
```

### Troubleshooting
```powershell
# Check link status
(Get-Item "T:\Project-AI-vault\repo-docs").LinkType

# Count files
(Get-ChildItem "T:\Project-AI-vault\repo-docs" -Recurse -File).Count

# Read troubleshooting guide
notepad TROUBLESHOOTING_REPO_DOCS.md
```

---

## 📊 Key Metrics

| Metric               | Value          |
|----------------------|----------------|
| Total Files          | 463            |
| Accessibility        | 100%           |
| Broken Links         | 0              |
| Strategy             | SymbolicLink   |
| Disk Space Used      | ~0 MB          |
| Last Validated       | 2026-04-20     |

---

## 🛠️ Available Scripts

### 1. `repo-docs-link-strategy.ps1`
**Purpose**: Create/recreate repo-docs with fallback  
**Usage**:
```powershell
.\repo-docs-link-strategy.ps1              # Auto mode
.\repo-docs-link-strategy.ps1 -Force       # Force recreation
.\repo-docs-link-strategy.ps1 -Strategy Copy  # Use copy instead
```

### 2. `validate-repo-docs.ps1`
**Purpose**: Verify accessibility and integrity  
**Usage**:
```powershell
.\validate-repo-docs.ps1           # Quick check
.\validate-repo-docs.ps1 -Detailed # Full analysis
```

---

## 🚨 Common Issues

| Issue                    | Solution                              |
|--------------------------|---------------------------------------|
| "Access Denied"          | Run as Admin or use -Strategy Copy   |
| "Target already exists"  | Use -Force flag                       |
| Files not accessible     | Run validate script, check logs       |
| Link broken              | Re-run linking script                 |

**Full Guide**: `TROUBLESHOOTING_REPO_DOCS.md` (7 issues, 20+ solutions)

---

## 📁 Directory Structure

```
repo-docs/
├── architecture/          # Architecture docs
├── developer/             # Developer guides
├── executive/             # Executive summaries
├── governance/            # Governance policies
├── security_compliance/   # Security docs
├── operations/            # Operations guides
├── reports/               # Analysis reports
├── internal/              # Internal docs
├── gradle/                # Gradle documentation
├── legal/                 # Legal docs
├── assets/                # Images, diagrams
├── archive/               # Archived content
└── [More directories...]
```

---

## 🎯 Validation Checklist

After any changes, verify:

- [ ] `repo-docs` exists: `Test-Path "T:\Project-AI-vault\repo-docs"`
- [ ] Is a link: `(Get-Item "...").LinkType -eq 'SymbolicLink'`
- [ ] File count ~460: `(Get-ChildItem -Recurse -File).Count`
- [ ] Files readable: `.\validate-repo-docs.ps1`
- [ ] No errors: Check validation report JSON

---

## 📄 Documentation Files

| File                                | Purpose                           |
|-------------------------------------|-----------------------------------|
| `AGENT_005_VALIDATION_REPORT.md`    | Full validation report            |
| `TROUBLESHOOTING_REPO_DOCS.md`      | Issue resolution guide            |
| `repo-docs-validation-report.json`  | Machine-readable validation data  |
| `repo-docs-link-*.log`              | Execution logs (timestamped)      |

---

## 🔐 Production Features

✅ **Fallback Chain**: SymbolicLink → Junction → Robocopy  
✅ **Error Handling**: Comprehensive logging & validation  
✅ **Zero Downtime**: Link updates instantly from source  
✅ **No Data Loss**: Force flag requires explicit confirmation  
✅ **Audit Trail**: Timestamped logs and JSON reports  
✅ **Self-Validating**: Automated accessibility testing  

---

## 💡 Pro Tips

1. **Run as Admin** for best results (enables SymbolicLink)
2. **Use Auto mode** - script picks optimal strategy
3. **Validate after Windows updates** - permissions may change
4. **Check logs** for warnings even if script succeeds
5. **Keep troubleshooting guide handy** for quick reference

---

## 🆘 Emergency Recovery

```powershell
# Full reset
Remove-Item "T:\Project-AI-vault\repo-docs" -Force
.\repo-docs-link-strategy.ps1

# Manual copy (if all else fails)
robocopy "T:\Project-AI-main\docs" "T:\Project-AI-vault\repo-docs" /E /MT:8
```

---

## ✅ Current Status

**Last Validated**: 2026-04-20 10:21:05  
**Status**: ✅ **FULLY OPERATIONAL**  
**Files**: 463/463 accessible (100%)  
**Errors**: 0  
**Strategy**: SymbolicLink  

---

**Need Help?** → Read `TROUBLESHOOTING_REPO_DOCS.md`  
**Detailed Report** → Read `AGENT_005_VALIDATION_REPORT.md`  
**Quick Check** → Run `.\validate-repo-docs.ps1`

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

