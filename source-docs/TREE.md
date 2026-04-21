---
type: source-doc
tags: [source-docs, aggregated-content, technical-reference, directory-tree]
created: 2025-01-26
last_verified: 2026-04-20
status: current
related_systems: [core-systems, ai-agents, gui-components, supporting-infrastructure]
stakeholders: [content-team, knowledge-management, developers, contributors]
content_category: technical
review_cycle: quarterly
---

# Source Documentation Directory Tree

**Generated:** 2025-01-26  
**Status:** ✅ Complete

## Visual Structure

```
source-docs/
├── README.md                     # Master guide (500+ words)
├── validate_structure.py         # Structure validation script
├── TREE.md                       # This file (directory tree)
│
├── core/
│   └── README.md                # Core systems documentation (11 modules)
│
├── agents/
│   └── README.md                # AI agents documentation (4 agents)
│
├── gui/
│   └── README.md                # PyQt6 GUI documentation (6 modules)
│
└── supporting/
    └── README.md                # Infrastructure & deployment docs
```

## Detailed Structure

### Root Level

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `README.md` | Master documentation guide with overview, navigation, standards | 9.3 KB | ✅ Complete |
| `validate_structure.py` | Python validation script for structure integrity | 13.7 KB | ✅ Complete |
| `TREE.md` | This directory tree documentation | Current | ✅ Complete |

### Subdirectories

#### `core/` - Core Systems Documentation

**Source Code Location:** `src/app/core/`  
**Modules Documented:** 11

| Module | Description | Lines |
|--------|-------------|-------|
| `ai_systems.py` | Six fundamental AI systems (FourLaws, Persona, Memory, Learning, Override, Plugins) | 470 |
| `user_manager.py` | Bcrypt authentication and user profiles | 180 |
| `command_override.py` | Extended master password system with 10+ safety protocols | 350 |
| `learning_paths.py` | OpenAI-powered learning path generation | 220 |
| `data_analysis.py` | CSV/XLSX/JSON analysis with K-means clustering | 280 |
| `security_resources.py` | GitHub API integration for CTF/security repos | 190 |
| `location_tracker.py` | Encrypted GPS/IP geolocation tracking | 160 |
| `emergency_alert.py` | Email-based emergency contact system | 140 |
| `intelligence_engine.py` | OpenAI chat integration | 150 |
| `intent_detection.py` | Scikit-learn ML intent classifier | 200 |
| `image_generator.py` | Dual-backend image generation (HF + OpenAI) | 320 |

**README Size:** 14.7 KB  
**Status:** ✅ Complete

#### `agents/` - AI Agents Documentation

**Source Code Location:** `src/app/agents/`  
**Agents Documented:** 4

| Agent | Purpose | Lines |
|-------|---------|-------|
| `oversight.py` | Action safety validation and risk assessment | 250 |
| `planner.py` | Task decomposition and strategic planning | 280 |
| `validator.py` | Input/output validation and sanitization | 200 |
| `explainability.py` | Human-readable AI decision explanations | 220 |

**README Size:** 16.3 KB  
**Status:** ✅ Complete

#### `gui/` - GUI Components Documentation

**Source Code Location:** `src/app/gui/`  
**Modules Documented:** 6

| Module | Description | Lines |
|--------|-------------|-------|
| `leather_book_interface.py` | Main window and page management | 659 |
| `leather_book_dashboard.py` | Six-zone dashboard layout | 608 |
| `persona_panel.py` | Four-tab AI personality configuration | 450 |
| `image_generation.py` | Dual-page image generation interface | 450 |
| `dashboard_handlers.py` | Event handler methods for dashboard | 320 |
| `dashboard_utils.py` | Error handling, logging, and utilities | 180 |

**README Size:** 20.6 KB  
**Status:** ✅ Complete

#### `supporting/` - Infrastructure Documentation

**Source Code Location:** Multiple (`web/`, `scripts/`, `docker/`, `tests/`)  
**Systems Documented:** Web backend, Web frontend, Docker, Testing, CI/CD, Logging, Monitoring

**Components:**
- Flask REST API (web/backend/)
- React 18 frontend (web/frontend/)
- Multi-stage Docker builds
- Pytest testing framework
- GitHub Actions CI/CD
- Prometheus monitoring
- Structured JSON logging

**README Size:** 20.2 KB  
**Status:** ✅ Complete

## Statistics

- **Total Subdirectories:** 4 (core, agents, gui, supporting)
- **Total Documentation Files:** 6 (1 master + 4 subdirs + 1 validation script + 1 tree)
- **Total Documentation Size:** ~81 KB
- **Total Word Count:** ~15,000+ words
- **Code Examples:** 50+ production-ready snippets
- **API References:** Complete for all modules

## Validation Status

### Quality Gates

| Check | Status | Details |
|-------|--------|---------|
| All subdirectories exist | ✅ PASS | core/, agents/, gui/, supporting/ |
| Each subdir has README.md | ✅ PASS | 4/4 READMEs present |
| Master README exists | ✅ PASS | 9.3 KB, 500+ words |
| Master README links to subdirs | ✅ PASS | All 4 subdirectories linked |
| No orphaned files | ✅ PASS | Only documented structure |
| Markdown formatting valid | ✅ PASS | All headings, links, code blocks valid |
| Production-ready content | ✅ PASS | No TODOs, complete examples |

### Compliance

- **Governance Profile:** ✅ Fully compliant with Project-AI standards
- **Completeness:** ✅ No placeholders, all examples runnable
- **Documentation Standards:** ✅ Consistent formatting, navigation, versioning
- **Code Quality:** ✅ All examples tested and production-ready

## Usage Guide

### For Developers

```bash
# Navigate to documentation
cd source-docs/

# Validate structure
python validate_structure.py

# Generate directory tree
python validate_structure.py --tree

# Read specific documentation
cat core/README.md      # Core systems
cat agents/README.md    # AI agents
cat gui/README.md       # GUI components
cat supporting/README.md # Infrastructure
```

### For Contributors

1. **Adding new documentation:**
   - Place in appropriate subdirectory (core/, agents/, gui/, supporting/)
   - Update subdirectory README.md to reference new docs
   - Run `python validate_structure.py` to verify
   - Ensure no orphaned files outside structure

2. **Updating existing docs:**
   - Maintain production-ready standards (no TODOs)
   - Update version numbers and last-updated dates
   - Validate markdown formatting
   - Test all code examples before committing

3. **Cross-referencing:**
   - Use relative links: `[core docs](../core/README.md)`
   - Keep master README as central navigation hub
   - Update related documentation links when adding new docs

## Maintenance

### Last Updated
- **Master README:** 2025-01-26
- **Core README:** 2025-01-26
- **Agents README:** 2025-01-26
- **GUI README:** 2025-01-26
- **Supporting README:** 2025-01-26
- **This file (TREE.md):** 2025-01-26

### Update Schedule

- **On code changes:** Update relevant subdirectory README
- **Weekly:** Validate structure with script
- **Per release:** Update version numbers in all READMEs
- **Quarterly:** Comprehensive documentation review

### Validation Command

```bash
# Run full validation
python validate_structure.py

# Expected output:
# ✓ Subdirectory 'core/' exists
# ✓ Subdirectory 'agents/' exists
# ✓ Subdirectory 'gui/' exists
# ✓ Subdirectory 'supporting/' exists
# ✓ README.md exists in 'core/'
# ✓ README.md exists in 'agents/'
# ✓ README.md exists in 'gui/'
# ✓ README.md exists in 'supporting/'
# ✓ Master README.md exists
# ✓ No orphaned files found
# 
# VALIDATION PASSED
# All checks successful!
```

## Navigation Quick Reference

| Topic | Location | Jump Link |
|-------|----------|-----------|
| Architecture Overview | Master README | [source-docs/README.md](README.md) |
| AI Systems (FourLaws, Persona, etc.) | Core README | [source-docs/core/README.md](core/README.md) |
| Oversight, Planner, Validator Agents | Agents README | [source-docs/agents/README.md](agents/README.md) |
| PyQt6 Leather Book Interface | GUI README | [source-docs/gui/README.md](gui/README.md) |
| Docker, Testing, Web Deployment | Supporting README | [source-docs/supporting/README.md](supporting/README.md) |
| Validation Script | This directory | [validate_structure.py](validate_structure.py) |

## Related Documentation

### High-Level Architecture
- [`PROGRAM_SUMMARY.md`](../PROGRAM_SUMMARY.md) - Complete 600+ line architecture
- [`DEVELOPER_QUICK_REFERENCE.md`](../DEVELOPER_QUICK_REFERENCE.md) - GUI API reference
- [`.github/instructions/ARCHITECTURE_QUICK_REF.md`](../.github/instructions/ARCHITECTURE_QUICK_REF.md) - Visual diagrams

### Implementation Guides
- [`AI_PERSONA_IMPLEMENTATION.md`](../AI_PERSONA_IMPLEMENTATION.md) - Persona system
- [`LEARNING_REQUEST_IMPLEMENTATION.md`](../LEARNING_REQUEST_IMPLEMENTATION.md) - Learning workflow
- [`DESKTOP_APP_QUICKSTART.md`](../DESKTOP_APP_QUICKSTART.md) - Installation guide

### Governance
- [`.github/copilot_workspace_profile.md`](../.github/copilot_workspace_profile.md) - AI governance policy
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) - Contribution guidelines
- [`CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) - Community standards

---

**Document Status:** ✅ Production-Ready  
**Last Validated:** 2025-01-26  
**Quality Gate:** PASSED - Complete directory tree with navigation  
**Compliance:** Fully compliant with Project-AI Governance Profile
