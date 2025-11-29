# AI Agent Instructions Index

This directory contains instructions and guidelines for AI coding agents working on Project-AI.

## 📋 Files

### 1. `copilot-instructions.md` (Main File)
**Primary instructions for GitHub Copilot and AI agents**

Contains:
- Project overview and architecture
- Six core AI systems explained
- Data persistence patterns
- Development workflows (run, test, lint)
- Project-specific conventions
- Integration points (OpenAI, web version, plugins)
- Critical gotchas (7 common mistakes)
- Deployment workflows
- Environment setup

**Use when**: You need to understand the overall project structure, coding patterns, or how to run/test the application.

### 2. `ARCHITECTURE_QUICK_REF.md` (Visual Guide)
**Visual architecture reference with diagrams and data flows**

Contains:
- System overview diagram
- Data flow patterns (user actions, learning requests, persistence)
- Testing strategy matrix
- Integration point examples
- Common commands cheat sheet
- Security layers diagram
- Documentation hierarchy

**Use when**: You need to visualize system architecture, understand data flows, or need quick command reference.

### 3. `codacy.instructions.md` (Code Quality)
**Codacy integration rules and automated analysis**

Contains:
- Post-edit analysis requirements
- Dependency security checks
- CLI installation guidance
- Repository setup workflow

**Use when**: Making file edits or adding dependencies. MUST run `codacy_cli_analyze` after edits.

## 🎯 Quick Navigation by Task

| Task | Primary File | Secondary File |
|------|-------------|----------------|
| **Understanding project structure** | copilot-instructions.md | ARCHITECTURE_QUICK_REF.md |
| **Adding new features** | copilot-instructions.md | ARCHITECTURE_QUICK_REF.md |
| **Running tests** | copilot-instructions.md | - |
| **Fixing bugs** | copilot-instructions.md | - |
| **Visualizing data flows** | ARCHITECTURE_QUICK_REF.md | - |
| **After editing files** | codacy.instructions.md | - |
| **Adding dependencies** | codacy.instructions.md | copilot-instructions.md |
| **Deployment** | copilot-instructions.md | ../DESKTOP_APP_QUICKSTART.md |

## 🔗 Related Documentation

Located in project root:

- `PROGRAM_SUMMARY.md` - Complete architecture (600+ lines)
- `DEVELOPER_QUICK_REFERENCE.md` - GUI component API
- `AI_PERSONA_IMPLEMENTATION.md` - Persona system details
- `LEARNING_REQUEST_IMPLEMENTATION.md` - Learning workflow
- `DESKTOP_APP_QUICKSTART.md` - Installation guide
- `web/DEPLOYMENT.md` - Web deployment guide

## 📝 How to Use These Instructions

### For AI Coding Agents
1. **Start here**: Read `copilot-instructions.md` first
2. **Visualize**: Use `ARCHITECTURE_QUICK_REF.md` for system understanding
3. **Code quality**: Follow `codacy.instructions.md` after every edit
4. **Deep dive**: Consult root-level docs for detailed specifications

### For Human Developers
1. **Quick start**: `../DESKTOP_APP_QUICKSTART.md`
2. **Architecture**: `ARCHITECTURE_QUICK_REF.md`
3. **Conventions**: `copilot-instructions.md` (sections: Conventions, Gotchas)
4. **GUI development**: `../DEVELOPER_QUICK_REFERENCE.md`

## 🚦 Priority Rules

When in doubt, follow this priority order:

1. **Critical Gotchas** (copilot-instructions.md) - Avoid breaking changes
2. **Data Persistence** - Always call `_save_state()` after modifications
3. **Module Imports** - Always use `python -m src.app.main`
4. **Code Quality** - Run Codacy analysis after edits
5. **Testing** - Use `tempfile.TemporaryDirectory()` for isolated tests

---

**Last Updated**: November 29, 2025  
**Maintainer**: Project-AI Team
