# Agent Systems MOC - AI Agent Capabilities & Workflows

> **📍 Location**: `relationships/agents/00_AGENTS_MOC.md`  
> **🎯 Purpose**: Comprehensive AI agent systems documentation  
> **👥 Audience**: AI researchers, developers, system architects  
> **🔄 Status**: Production-Ready ✓

---

## 🗺️ Agent Architecture

```
AI Agent Systems
│
├─🤖 FOUR SPECIALIZED AGENTS
│  ├─ [[01_oversight_agent.md|Oversight Agent]] - Action safety validation
│  ├─ [[02_planner_agent.md|Planner Agent]] - Task decomposition
│  ├─ [[03_validator_agent.md|Validator Agent]] - Input/output validation
│  └─ [[04_explainability_agent.md|Explainability Agent]] - Decision explanations
│
├─⚖️ ETHICS & GOVERNANCE
│  ├─ [[relationships/core-ai/01_four_laws_relationships.md|FourLaws Framework]]
│  ├─ [[relationships/constitutional/01_constitutional_systems_overview.md|Constitutional AI]]
│  └─ [[relationships/governance/00_GOVERNANCE_MOC.md|Governance MOC]]
│
├─📚 KNOWLEDGE & LEARNING
│  ├─ [[relationships/core-ai/03_memory_expansion_relationships.md|Memory System]]
│  ├─ [[relationships/core-ai/04_learning_request_relationships.md|Learning System]]
│  └─ [[relationships/data/00_DATA_MOC.md|Data Systems]]
│
└─🔌 INTEGRATION
   ├─ [[relationships/integrations/00_INTEGRATION_MOC.md|Integration MOC]]
   └─ [[INTEGRATION_POINTS_CATALOG.md|Integration Catalog]]
```

---

## 🎯 Agent Capabilities Matrix

| Agent | Primary Function | Tools | Integration | Status |
|-------|------------------|-------|-------------|--------|
| **Oversight** | Safety validation | FourLaws, Constitutional AI | All actions | ✅ Active |
| **Planner** | Task decomposition | OpenAI GPT, Memory | Complex tasks | ✅ Active |
| **Validator** | Input/output validation | Regex, Schema validation | All I/O | ✅ Active |
| **Explainability** | Decision transparency | Logging, Analysis | All decisions | ✅ Active |

---

## 📋 Metadata

```yaml
---
title: "Agent Systems MOC"
type: moc
category: agents
audience: [ai-researchers, developers, architects]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - moc
  - agents
  - ai-systems
related_mocs:
  - "[[docs/00_INDEX.md|Master Index]]"
  - "[[relationships/core-ai/00-INDEX.md|Core AI MOC]]"
  - "[[relationships/governance/00_GOVERNANCE_MOC.md|Governance MOC]]"
---
```

---

**MOC Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Status**: Production-Ready ✓
