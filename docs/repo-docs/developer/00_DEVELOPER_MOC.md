# Developer Resources MOC - Development & Contribution Guide

> **📍 Location**: `docs/developer/00_DEVELOPER_MOC.md`  
> **🎯 Purpose**: Comprehensive developer resources and quick-start guides  
> **👥 Audience**: Developers, contributors, technical users  
> **🔄 Status**: Production-Ready ✓

---

## 🗺️ Developer Navigation

```
Developer Resources
│
├─🚀 QUICK STARTS
│  ├─ [[DESKTOP_APP_QUICKSTART.md|Desktop Quickstart]] ⭐ Start Here
│  ├─ [[docs/developer/OPERATOR_QUICKSTART.md|Operator Quickstart]]
│  ├─ [[quickstart.py|Quick Start Script]]
│  └─ [[bootstrap.py|Bootstrap Script]]
│
├─📖 CORE DOCUMENTATION
│  ├─ [[DEVELOPER_QUICK_REFERENCE.md|Developer Quick Reference]] ⭐ Main Guide
│  ├─ [[PROGRAM_SUMMARY.md|Program Summary]]
│  ├─ [[.github/instructions/ARCHITECTURE_QUICK_REF.md|Architecture Reference]]
│  └─ [[.github/instructions/IMPLEMENTATION_SUMMARY.md|Implementation Summary]]
│
├─🤝 CONTRIBUTING
│  ├─ [[docs/developer/CONTRIBUTING.md|Contributing Guide]] ⭐ Main
│  ├─ [[CONTRIBUTING.md|Contribution Standards]]
│  ├─ [[CODE_OF_CONDUCT.md|Code of Conduct]]
│  └─ [[CODEOWNERS|Code Owners]]
│
├─🔌 API DOCUMENTATION
│  ├─ [[API_QUICK_REFERENCE.md|API Quick Reference]] ⭐ Main
│  ├─ [[docs/developer/API_REFERENCE.md|Full API Reference]]
│  ├─ [[AGENT-083-API-COVERAGE-REPORT.md|API Coverage]]
│  └─ [[AGENT-083-GUIDE-API-MAP.md|Guide-API Map]]
│
├─🏗️ ARCHITECTURE
│  ├─ [[docs/architecture/00_ARCHITECTURE_MOC.md|Architecture MOC]]
│  ├─ [[AGENT-080-CONCEPT-CODE-MAP.md|Concept-Code Map]]
│  ├─ [[COMPONENT_DEPENDENCY_GRAPH.md|Dependency Graph]]
│  └─ [[DESIGN_PATTERN_USAGE_MATRIX.md|Design Patterns]]
│
├─🚢 DEPLOYMENT
│  ├─ [[docs/developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md|Infrastructure Guide]] ⭐
│  ├─ [[docs/developer/EXAMPLE_DEPLOYMENTS.md|Example Deployments]]
│  ├─ [[docs/developer/DEPLOYMENT_GUIDE.md|Deployment Guide]]
│  └─ [[docs/developer/KUBERNETES_MONITORING_GUIDE.md|Kubernetes Guide]]
│
├─🧪 TESTING
│  ├─ [[relationships/testing/00_TESTING_MOC.md|Testing MOC]]
│  ├─ [[relationships/testing/01_test_strategy.md|Test Strategy]]
│  ├─ [[MODULE_COVERAGE_MATRIX.md|Coverage Matrix]]
│  └─ [[TEST_DOCUMENTATION_ENRICHMENT_REPORT.md|Test Docs]]
│
├─🔧 DEVELOPMENT TOOLS
│  ├─ [[docs/MCP_QUICKSTART.md|MCP Quickstart]]
│  ├─ [[docs/MCP_CONFIGURATION.md|MCP Configuration]]
│  ├─ [[docs/DATAVIEW_SETUP_GUIDE.md|Dataview Setup]]
│  └─ [[TEMPLATER_QUICK_REFERENCE.md|Templater Reference]]
│
├─📚 LEARNING PATHS
│  ├─ [[AGENT-084-LEARNING-PATHS.md|Learning Paths]] ⭐ Main
│  ├─ [[AGENT-084-MISSION-COMPLETE.md|Learning Resources]]
│  └─ [[docs/developer/AI_SAFETY_OVERVIEW.md|AI Safety Overview]]
│
└─🆘 TROUBLESHOOTING
   ├─ [[AGENT-085-COMMON-ISSUES-INDEX.md|Common Issues]] ⭐ Main
   ├─ [[AGENT-085-PROBLEM-SYSTEM-MAP.md|Problem System Map]]
   └─ [[vault-troubleshooting-guide.md|Vault Troubleshooting]]
```

---

## 🎯 Quick Start Matrix

| Goal | Start Here | Next Steps | Time |
|------|-----------|------------|------|
| **Run Desktop App** | [[DESKTOP_APP_QUICKSTART.md|Desktop Quickstart]] | [[DEVELOPER_QUICK_REFERENCE.md|Dev Guide]] | 5 min |
| **Deploy to Production** | [[docs/developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md|Infrastructure Guide]] | [[docs/developer/EXAMPLE_DEPLOYMENTS.md|Examples]] | 30 min |
| **Contribute Code** | [[docs/developer/CONTRIBUTING.md|Contributing Guide]] | [[CODE_OF_CONDUCT.md|Code of Conduct]] | 10 min |
| **Build Feature** | [[DEVELOPER_QUICK_REFERENCE.md|Dev Guide]] | [[.github/instructions/ARCHITECTURE_QUICK_REF.md|Architecture]] | 15 min |
| **Write Tests** | [[relationships/testing/01_test_strategy.md|Test Strategy]] | [[MODULE_COVERAGE_MATRIX.md|Coverage]] | 15 min |
| **Fix Security Issue** | [[docs/security_compliance/INCIDENT_PLAYBOOK.md|Incident Playbook]] | [[SECURITY.md|Security Policy]] | 20 min |

---

## 🔧 Development Environment Setup

### Prerequisites
```bash
# Python 3.11+
python --version

# Install dependencies
pip install -r requirements.txt

# Optional: Development dependencies
pip install -r requirements-dev.txt
```

📄 [[DESKTOP_APP_QUICKSTART.md|Complete Setup Guide]]

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...

# Optional
FERNET_KEY=<generated_key>
SMTP_USERNAME=<email>
SMTP_PASSWORD=<password>
```

📄 [[.env.example|Environment Template]]

### Running the Application
```bash
# Desktop (PyQt6)
python -m src.app.main

# Tests
pytest -v

# Linting
ruff check .
```

📄 [[DEVELOPER_QUICK_REFERENCE.md|Full Development Workflow]]

---

## 📐 API Reference Quick Links

### Core AI Systems API
| System | Module | Key Methods | Documentation |
|--------|--------|-------------|---------------|
| **FourLaws** | `ai_systems.py` | `validate_action()` | [[relationships/core-ai/01_four_laws_relationships.md|Docs]] |
| **AIPersona** | `ai_systems.py` | `update_mood()`, `get_state()` | [[relationships/core-ai/02_ai_persona_relationships.md|Docs]] |
| **Memory** | `ai_systems.py` | `add_knowledge()`, `search()` | [[relationships/core-ai/03_memory_expansion_relationships.md|Docs]] |
| **Learning** | `ai_systems.py` | `submit_request()`, `approve()` | [[relationships/core-ai/04_learning_request_relationships.md|Docs]] |
| **Plugins** | `ai_systems.py` | `load_plugin()`, `enable()` | [[relationships/core-ai/05_plugin_manager_relationships.md|Docs]] |
| **Override** | `command_override.py` | `request_override()` | [[relationships/core-ai/06_command_override_relationships.md|Docs]] |

📄 [[API_QUICK_REFERENCE.md|Complete API Reference]]

### GUI Components API
| Component | File | Signals | Documentation |
|-----------|------|---------|---------------|
| **LeatherBookInterface** | `leather_book_interface.py` | `user_logged_in` | [[relationships/gui/01_leather_book_interface.md|Docs]] |
| **Dashboard** | `leather_book_dashboard.py` | `command_sent` | [[relationships/gui/02_leather_book_dashboard.md|Docs]] |
| **PersonaPanel** | `persona_panel.py` | `persona_updated` | [[relationships/gui/03_persona_panel.md|Docs]] |
| **ImageGen** | `image_generation.py` | `image_generated` | [[relationships/gui/04_image_generation_ui.md|Docs]] |

📄 [[relationships/gui/00_MASTER_INDEX.md|GUI Components Index]]

---

## 🎓 Developer Learning Paths

### Path 1: Beginner Developer (1-2 weeks)
1. **Setup** (Day 1-2)
   - [[DESKTOP_APP_QUICKSTART.md|Desktop Quickstart]]
   - [[DEVELOPER_QUICK_REFERENCE.md|Developer Guide]]

2. **Understanding Core** (Day 3-5)
   - [[PROGRAM_SUMMARY.md|Program Summary]]
   - [[relationships/core-ai/00-INDEX.md|Core AI Systems]]

3. **First Contribution** (Week 2)
   - [[docs/developer/CONTRIBUTING.md|Contributing Guide]]
   - [[AGENT-085-COMMON-ISSUES-INDEX.md|Common Issues]]

### Path 2: Full-Stack Developer (2-4 weeks)
1. **Architecture Understanding** (Week 1)
   - [[.github/instructions/ARCHITECTURE_QUICK_REF.md|Architecture Quick Ref]]
   - [[AGENT-080-CONCEPT-CODE-MAP.md|Concept-Code Map]]
   - [[COMPONENT_DEPENDENCY_GRAPH.md|Dependencies]]

2. **Backend Development** (Week 2)
   - [[relationships/core-ai/00-INDEX.md|Core AI MOC]]
   - [[relationships/data/00_DATA_MOC.md|Data MOC]]
   - [[API_QUICK_REFERENCE.md|API Reference]]

3. **Frontend Development** (Week 3)
   - [[relationships/gui/00_MASTER_INDEX.md|GUI MOC]]
   - [[GUI_ARCHITECTURE_EVALUATION_REPORT.md|GUI Architecture]]

4. **Integration & Testing** (Week 4)
   - [[relationships/testing/00_TESTING_MOC.md|Testing MOC]]
   - [[relationships/integrations/00_INTEGRATION_MOC.md|Integration MOC]]

### Path 3: DevOps Engineer (1-2 weeks)
1. **Infrastructure** (Week 1)
   - [[docs/developer/INFRASTRUCTURE_PRODUCTION_GUIDE.md|Infrastructure Guide]]
   - [[docs/developer/EXAMPLE_DEPLOYMENTS.md|Example Deployments]]
   - [[docs/developer/KUBERNETES_MONITORING_GUIDE.md|Kubernetes Guide]]

2. **Operations** (Week 2)
   - [[docs/operations/00_OPERATIONS_MOC.md|Operations MOC]]
   - [[docs/developer/DEPLOYMENT_GUIDE.md|Deployment Guide]]
   - [[relationships/monitoring/00_MONITORING_MOC.md|Monitoring MOC]]

---

## 🧪 Testing Guide

### Running Tests
```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_ai_systems.py -v

# With coverage
pytest --cov=src --cov-report=html
```

### Test Structure
```
tests/
├─ test_ai_systems.py        # Core AI tests (14 tests)
├─ test_user_manager.py       # User auth tests
├─ test_command_override.py   # Override tests
└─ ...
```

📄 [[relationships/testing/01_test_strategy.md|Test Strategy]]  
📄 [[MODULE_COVERAGE_MATRIX.md|Coverage Matrix]]

---

## 🔍 Code Navigation Tips

### Finding Code
```bash
# Find by function name
grep -r "validate_action" src/

# Find by class
grep -r "class FourLaws" src/

# Find by import
grep -r "from app.core import" src/
```

### Understanding Relationships
- **Concept to Code**: [[AGENT-080-CONCEPT-CODE-MAP.md|421 bidirectional links]]
- **Dependencies**: [[COMPONENT_DEPENDENCY_GRAPH.md|Dependency Graph]]
- **Integration Points**: [[INTEGRATION_POINTS_CATALOG.md|Catalog]]

---

## 🛠️ Development Workflows

### Adding New Feature
1. Review [[docs/developer/CONTRIBUTING.md|Contributing Guide]]
2. Check [[DESIGN_PATTERN_USAGE_MATRIX.md|Design Patterns]]
3. Implement with tests
4. Update documentation
5. Submit PR

### Fixing Bug
1. Check [[AGENT-085-COMMON-ISSUES-INDEX.md|Common Issues]]
2. Write failing test
3. Fix bug
4. Verify test passes
5. Submit PR

### Security Fix
1. Review [[docs/security_compliance/INCIDENT_PLAYBOOK.md|Incident Playbook]]
2. Assess impact
3. Implement fix
4. Security audit
5. Emergency PR

---

## 📋 Code Quality Standards

### Linting
```bash
# Ruff (configured in pyproject.toml)
ruff check .
ruff check . --fix

# Type checking
mypy src/
```

### Security Scanning
```bash
# Bandit security scan
bandit -r src/

# Dependency audit
pip-audit
```

📄 [[CODE_QUALITY_REPORT.md|Quality Report]]

---

## 🔗 Related Documentation

### Architecture
- [[docs/architecture/00_ARCHITECTURE_MOC.md|Architecture MOC]]
- [[relationships/core-ai/00-INDEX.md|Core AI MOC]]

### Operations
- [[docs/operations/00_OPERATIONS_MOC.md|Operations MOC]]

### Security
- [[docs/security_compliance/00_SECURITY_MOC.md|Security MOC]]

---

## 📋 Metadata

```yaml
---
title: "Developer Resources MOC"
type: moc
category: developer
audience: [developers, contributors, technical-users]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - moc
  - developer
  - contributing
  - api
  - testing
  - deployment
related_mocs:
  - "[[docs/00_INDEX.md|Master Index]]"
  - "[[docs/architecture/00_ARCHITECTURE_MOC.md|Architecture MOC]]"
  - "[[docs/operations/00_OPERATIONS_MOC.md|Operations MOC]]"
  - "[[relationships/testing/00_TESTING_MOC.md|Testing MOC]]"
---
```

---

**MOC Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Status**: Production-Ready ✓
