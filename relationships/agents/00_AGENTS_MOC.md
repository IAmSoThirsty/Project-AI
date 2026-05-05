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
├─🤖 GOVERNANCE AGENTS (implemented 2026-05-03)
│  ├─ [[01_oversight_agent.md|Oversight Agent]] ✓ Implemented
│  │     deny-rate monitor · 5-min sliding window · JSON drift alerts
│  │     src/app/agents/oversight.py
│  ├─ [[03_validator_agent.md|Validator Agent]] ✓ Implemented
│  │     schema registry · 4 named schemas · type/range/allowlist checks
│  │     src/app/agents/validator.py
│  ├─ [[04_explainability_agent.md|Explainability Agent]] ✓ Implemented
│  │     natural-language decision formatter · trace summarizer
│  │     src/app/agents/explainability.py
│  └─ [[02_planner_agent.md|Planner Agent]] ✓ Active
│        task decomposition · OpenAI GPT · memory integration
│        src/app/agents/planner_agent.py
│
├─🔒 PRIVACY & SECURITY AGENTS (wired 2026-05-03)
│  ├─ Consigliere (ThirstyConsigliere) ✓ Wired → CouncilHub
│  │     privacy-first strategy engine · Code of Omertà
│  │     Fernet encryption shim · src/app/agents/consigliere/
│  ├─ CerberusCodexBridge ✓ Wired → GateGuardian
│  │     threat-engagement bridge (Cerberus→Codex defense)
│  │     src/app/agents/cerberus_codex_bridge.py
│  └─ ThirstyLangValidator ✓ Wired → TarlRuntime
│        UTF validation — all 6 tiers (T1–T6) via Python subprocess
│        src/app/agents/thirsty_lang_validator.py · validates: src/utf/
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

| Agent | Primary Function | Source | Status |
|-------|-----------------|--------|--------|
| **OversightAgent** | Deny-rate monitor, 5-min window, drift alerts | `src/app/agents/oversight.py` | ✅ Implemented |
| **ValidatorAgent** | Schema registry, type/range/allowlist validation | `src/app/agents/validator.py` | ✅ Implemented |
| **ExplainabilityAgent** | NL decision formatter, trace summarizer | `src/app/agents/explainability.py` | ✅ Implemented |
| **PlannerAgent** | Task decomposition, OpenAI GPT, memory | `src/app/agents/planner_agent.py` | ✅ Active |
| **ThirstyConsigliere** | Privacy-first strategy, Code of Omertà | `src/app/agents/consigliere/` | ✅ Wired → CouncilHub |
| **CerberusCodexBridge** | Threat-engagement bridge | `src/app/agents/cerberus_codex_bridge.py` | ✅ Wired → GateGuardian |
| **ThirstyLangValidator** | UTF validation — T1–T6 Python tiers | `src/app/agents/thirsty_lang_validator.py` · `src/utf/` | ✅ Wired → TarlRuntime |

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
