---
title: "REPO STRUCTURE"
id: "repo-structure"
type: superseded
tags:
  - p3-archive
  - historical
  - archive
  - implementation
  - monitoring
  - testing
  - governance
  - ci-cd
  - security
  - architecture
created: 2026-02-10
last_verified: 2026-04-20
status: archived
archived_date: 2026-04-19
archive_reason: completed
superseded_by: docs/ARCHITECTURE_DESIGN_PATTERNS_EVALUATION.md
related_systems:
  - security-systems
  - test-framework
  - ci-cd-pipeline
  - architecture
stakeholders:
  - developer
  - architect
audience:
  - developer
  - architect
review_cycle: annually
historical_value: high
restore_candidate: false
path_confirmed: T:/Project-AI-main/docs/internal/archive/REPO_STRUCTURE.md
---
# Project-AI V1.0.0 - Complete Repository Tree

Generated: 2026-01-21 19:42:45

## Repository Statistics

- **Total Files:** 1530+
- **Code Files:** 500+
- **Documentation:** 230KB+ (60+ markdown files)
- **Test Scenarios:** 4250+ adversarial tests
- **Workflows:** 20+ GitHub Actions
- **Agents:** 33 implementations
- **Core Modules:** 53 system files

## Quick Navigation

### 🚀 Entry Points

- **Main Application:** `src/app/main.py`
- **CLI:** `src/app/cli.py` OR `python -m app.cli`
- **Docker:** `docker-compose.yml`
- **Tests:** `test_v1_launch.py`

### 📜 Essential Documents

- **AGI Charter:** `docs/AGI_CHARTER.md` ⭐
- **Deployment Guide:** `PRODUCTION_DEPLOYMENT.md` ⭐
- **README:** `README.md`
- **Architecture:** `docs/ARCHITECTURE_OVERVIEW.md`

### 🔐 Security & Governance

- **Codeowners:** `.github/CODEOWNERS`
- **Security Policy:** `SECURITY.md`
- **Workflows:** `.github/workflows/`

### 💾 Data Directories

- **Persona:** `data/ai_persona/state.json`
- **Memory:** `data/memory/knowledge.json`
- **Learning:** `data/learning_requests/`
- **Security:** `data/black_vault_secure/`

---

## Complete Tree Structure

See attached: REPO_TREE.txt (1530 lines, 46KB)

Key highlights:

- 18 data subdirectories (ai_persona, memory, learning_requests, etc.)
- 15 src/app subdirectories (core, agents, gui, web, etc.)
- 11 docs subdirectories (security, architecture, developer, etc.)
- 50+ GitHub workflow files
- 200+ adversarial test transcripts
- 33 agent implementations
- 53 core system modules

---

## Production Status

✅ **Dependencies:** Installed  
✅ **Environment:** Configured (.env)  
✅ **Data:** Initialized  
✅ **Tests:** Passing  
✅ **Docker:** Ready  
✅ **Monitoring:** Configured  
✅ **Security:** Active  
✅ **Governance:** Enforcing  

**V1.0.0: PRODUCTION READY** 🟢

For full tree, see REPO_TREE.txt
For deployment instructions, see PRODUCTION_DEPLOYMENT.md
