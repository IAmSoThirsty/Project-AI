# AGENT-075: Quick Reference Guide

**Wiki Link System for Project-AI Infrastructure Documentation**

---

## 📚 What Was Created

AGENT-075 created **1,334 bidirectional wiki links** connecting:
- Source code files (`src/app/core/*.py`)
- Documentation files (`relationships/*`, `source-docs/*`)
- Configuration files (`docker-compose.yml`, `.github/workflows/*`)

---

## 🚀 Quick Start

### For Obsidian Users

1. **Open Project-AI in Obsidian**
   ```
   File → Open Vault → Select T:\Project-AI-main
   ```

2. **Navigate Using Wiki Links**
   - Click any `[[link]]` to jump to that file
   - Use `Ctrl+Click` to open in new pane
   - Press `Ctrl+O` for quick file switcher

3. **Explore the Graph**
   - Press `Ctrl+G` to open graph view
   - See visual connections between all docs

4. **Use Backlinks**
   - Toggle right sidebar for backlinks panel
   - See all files linking to current document

### For Developers (Without Obsidian)

1. **Find Source Documentation**
   ```
   src/app/core/ai_systems.py
     → Documented in: source-docs/data-models/02-ai-persona-model.md
     → Relationships: relationships/data/01-PERSISTENCE-PATTERNS.md
   ```

2. **Navigate Relationships**
   - Start at any README.md
   - Look for "Quick Navigation" or "See Also" sections
   - Follow wiki links to explore related content

3. **Use Search**
   ```bash
   # Find all references to a file
   grep -r "ai_systems.py" relationships/ source-docs/
   ```

---

## 📖 Wiki Link Syntax

### Basic Format
```markdown
[[path/to/file.md]]              # Link to file
[[src/app/core/ai_systems.py]]   # Link to source code
[[docker-compose.yml]]           # Link to config file
```

### How to Read Links

**In Documentation**:
```markdown
The AI Persona system is implemented in `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]].
```
- Backticked text: Human-readable reference
- `[[...]]`: Clickable link in Obsidian

**In Navigation Sections**:
```markdown
### Related Documentation
- **Data Models Index**: [[source-docs/data-models/00-index.md]]
- **Persistence Patterns**: [[relationships/data/01-PERSISTENCE-PATTERNS.md]]
```

---

## 🗺️ Navigation Patterns

### Pattern 1: Source Code → Documentation

```
1. Open source file: src/app/core/user_manager.py
2. Search for "user-management-model.md"
3. Open: source-docs/data-models/01-user-management-model.md
4. Scroll to "Related Documentation" section
5. Follow links to relationship maps
```

### Pattern 2: Documentation → Source Code

```
1. Open any relationship doc
2. Look for code snippets with links:
   `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]]
3. In Obsidian: Click the link
4. Without Obsidian: Open the file path directly
```

### Pattern 3: Cross-Documentation

```
relationships/data/01-PERSISTENCE-PATTERNS.md
  ↓ (See Also section)
source-docs/data-models/05-data-persistence-layer-model.md
  ↓ (Related Documentation)
relationships/configuration/02_environment_manager_relationships.md
```

---

## 🎯 Key Entry Points

### For System Architecture
- **Start**: `relationships/data/00-DATA-INFRASTRUCTURE-OVERVIEW.md`
- **Links to**: All 12 data systems, encryption chains, sync strategies

### For Configuration
- **Start**: `relationships/configuration/README.md`
- **Links to**: Environment variables, secrets, feature flags

### For Deployment
- **Start**: `relationships/deployment/README.md`
- **Links to**: Docker, Kubernetes, CI/CD pipelines

### For Integrations
- **Start**: `relationships/integrations/README.md`
- **Links to**: OpenAI, GitHub, HuggingFace integrations

---

## 📊 Link Statistics by Directory

| Directory | Links | Top Entry Point |
|-----------|-------|----------------|
| `relationships/data` | 263 | `00-DATA-INFRASTRUCTURE-OVERVIEW.md` |
| `relationships/configuration` | 239 | `README.md` |
| `relationships/integrations` | 133 | `01-openai-integration.md` |
| `source-docs/data-models` | 93 | `00-index.md` |
| `source-docs/configuration` | 80 | `INDEX.md` |
| `source-docs/deployment` | 56 | `README.md` |
| `source-docs/integrations` | 49 | `README.md` |
| `relationships/deployment` | 46 | `README.md` |

---

## 🔧 Maintenance Scripts

### Validate All Links
```bash
py agent_075_link_system.py
```
**Output**: Validation report showing any broken links

### Add Links to New Files
```bash
py agent_075_phase2_links.py
```
**Output**: Adds navigation sections to new documentation

---

## 💡 Pro Tips

### 1. Use Full-Text Search
```bash
# Find all docs about a topic
grep -r "encryption" relationships/ source-docs/
```

### 2. Follow the README Trail
```
Start at any README.md → Check "Quick Navigation" → Follow links
```

### 3. Explore Source-Docs First
Source-docs are implementation-focused. Start there for code details.
Relationships are system-level. Start there for architecture.

### 4. Look for "See Also" Sections
Every major document has cross-references at the bottom.

---

## 🐛 Known Issues

### Pre-Existing Broken Links
- 288 broken links from previous agents (AGENT-058, AGENT-060, AGENT-062)
- Use Obsidian format with aliases: `[[path|alias]]`
- Reference non-existent `../security/` documentation
- **Not created by AGENT-075** - require separate cleanup mission

### Validation Exclusions
Wiki links in code blocks are excluded from validation (intentional).

---

## 📞 Support

### Questions About Links?
1. Check `AGENT-075-MISSION-COMPLETE.md` for full documentation
2. Review `AGENT-075-LINK-REPORT.md` for technical details
3. Run validation: `py agent_075_link_system.py`

### Found a Broken Link?
1. Check if it's in the pre-existing broken links list
2. If new, run validation script to verify
3. Report or fix using the automation scripts

---

## 🎓 Example Workflows

### Workflow 1: Understanding AI Persona System
```
1. Start: relationships/data/README.md
2. Click: [[relationships/data/00-DATA-INFRASTRUCTURE-OVERVIEW.md]]
3. Find "AI Persona" section
4. Click: [[source-docs/data-models/02-ai-persona-model.md]]
5. Click: [[src/app/core/ai_systems.py]]
6. Review implementation
```

### Workflow 2: Setting Up Deployment
```
1. Start: relationships/deployment/README.md
2. Click: [[relationships/deployment/02_docker_relationships.md]]
3. Click: [[docker-compose.yml]]
4. Click: [[source-docs/deployment/01_docker_architecture.md]]
5. Follow deployment guide
```

### Workflow 3: Integrating OpenAI
```
1. Start: relationships/integrations/README.md
2. Click: [[relationships/integrations/01-openai-integration.md]]
3. See API contracts and usage patterns
4. Click: [[src/app/core/intelligence_engine.py]]
5. Click: [[source-docs/integrations/01-openai-integration.md]]
6. Review configuration details
```

---

**Created by**: AGENT-075 - Infrastructure Code-to-Doc Links Specialist  
**Last Updated**: 2026-04-21  
**Total Links**: 1,334 wiki links across 104 files  
**Status**: ✅ Production-Ready
