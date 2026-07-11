# 📑 Quick Reference: Index System

> **One-page guide to navigating the Project-AI Obsidian Vault**

## 🗂️ Index Types

| Type | Location | Use When |
|------|----------|----------|
| **Domain** | `by-area/` | Working in specific area (security, api, etc.) |
| **Type** | `by-type/` | Need specific doc type (runbook, guide, ADR) |
| **Priority** | `by-priority/` | Sprint planning, triage, focusing on critical |
| **Status** | `by-status/` | Finding current vs deprecated docs |
| **Cross-Ref** | `cross-reference/` | Impact analysis, dependency tracking |

## 🚀 Common Workflows

### New Feature Development
```
1. by-area/{domain}-domain-index.md → Find standards
2. by-type/specification-type-index.md → Find templates
3. cross-reference/{domain}-dependencies-index.md → Check impacts
```

### Incident Response
```
1. by-type/runbook-type-index.md → P0 runbooks
2. by-area/{affected-system}-domain-index.md → Context
3. by-type/troubleshooting-guide-type-index.md → Deep dive
```

### Code Review
```
1. by-area/security-domain-index.md → Security standards
2. by-type/adr-type-index.md → Architectural decisions
3. by-status/deprecated-status-index.md → Avoid old patterns
```

### Sprint Planning
```
1. by-priority/p0-critical-priority-index.md → Blockers first
2. by-priority/p1-high-priority-index.md → High value next
3. by-status/in-progress-status-index.md → Resume work
```

## 📝 Creating New Index

```bash
# 1. Copy template
cp _indexes/templates/INDEX_TEMPLATE.md _indexes/by-area/my-domain-index.md

# 2. Edit: Replace all {placeholders}

# 3. Validate
powershell _indexes/verify-indexes.ps1
```

## ✅ Naming Rules

**Pattern:** `{scope}-{type}-index.md`

**Valid:**
- ✅ `security-domain-index.md`
- ✅ `runbook-type-index.md`
- ✅ `p0-critical-priority-index.md`

**Invalid:**
- ❌ `Security-Index.md` (uppercase)
- ❌ `security_index.md` (underscore)
- ❌ `security.md` (no -index suffix)

## 🔍 Finding Documents

### Strategy 1: Start with Priority
```
1. Open p0-critical-priority-index.md
2. Read all P0 docs (essential knowledge)
3. Drop to P1 if time permits
```

### Strategy 2: Start with Domain
```
1. Open {your-domain}-domain-index.md
2. Browse sections (Specs, Guides, Runbooks)
3. Follow cross-references to related domains
```

### Strategy 3: Start with Task
```
Task: Fix security bug
→ by-area/security-domain-index.md
→ Find threat model, standards, audit reports
→ Follow cross-ref to implementation guides
```

## 📊 Index Anatomy

```yaml
---
index_type: "by-area"           # Dimension
index_scope: "security"         # Domain/category
last_updated: "2024-01-15"      # ISO date
maintainer: "AGENT-XXX"         # Owner
total_documents: 42             # Count
---

# Security Domain Index

## Section Name (P0)
- [[document]] - Description (P0, Active)
  - **Key Topics:** topic1, topic2
  - **Dependencies:** [[prereq1]]
```

## 🛠️ Tools

| Tool | Purpose | Command |
|------|---------|---------|
| **verify-indexes.ps1** | Validate all indexes | `powershell _indexes/verify-indexes.ps1` |
| **validate_index_names.py** | Check naming conventions | `python scripts/validate_index_names.py` |

## 🔗 Key Files

- **README.md** - Complete system guide (3,500+ words)
- **NAVIGATION_PLAN.md** - Detailed workflows (4,500+ words)
- **NAMING_CONVENTIONS.md** - Naming rules (3,700+ words)
- **INDEX_TEMPLATE.md** - Template for new indexes
- **.index-schema.json** - Validation schema

## 💡 Tips

1. **Bookmark frequently used indexes** (security, your domain, P0)
2. **Use Obsidian Quick Switcher** (`Ctrl+O`) to jump to indexes
3. **Check cross-references** when planning changes
4. **Verify status** before relying on documentation
5. **Start with P0** when time-limited

## ⚠️ Common Issues

| Problem | Solution |
|---------|----------|
| Can't find document | Try multiple index types (domain, type, priority) |
| Too many results | Add priority filter (P0/P1 only) |
| Conflicting info | Active > Deprecated, Higher priority > Lower |
| Broken link | Check deprecated/archived indexes |

## 📞 Help

- **Full Documentation:** `_indexes/README.md`
- **Navigation Examples:** `_indexes/NAVIGATION_PLAN.md`
- **Naming Rules:** `_indexes/NAMING_CONVENTIONS.md`
- **Template:** `_indexes/templates/INDEX_TEMPLATE.md`

---

**Quick Start:** Open `README.md` for complete guide | **Need Help?** See `NAVIGATION_PLAN.md` for examples

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
