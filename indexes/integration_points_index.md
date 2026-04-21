# Integration Points Index

> **📍 Location**: `indexes/integration_points_index.md`  
> **🎯 Purpose**: Index of all external integrations and protocols  
> **👥 Audience**: Integration engineers, API developers  
> **🔄 Status**: Production-Ready ✓

---

## 🌐 External API Integrations

| Service | Purpose | Protocol | Authentication | Status | Documentation |
|---------|---------|----------|----------------|--------|---------------|
| **OpenAI** | GPT-4, DALL-E 3 | REST | API Key | ✅ Active | [[src/app/core/intelligence_engine.py|Code]] |
| **Hugging Face** | Stable Diffusion | REST | API Key | ✅ Active | [[src/app/core/image_generator.py|Code]] |
| **GitHub** | Version control | REST | OAuth | ✅ Active | [[docs/MCP_CONFIGURATION.md|MCP]] |
| **Temporal** | Workflow orchestration | gRPC | mTLS | ✅ Active | [[docs/developer/TEMPORAL_SETUP.md|Setup]] |

---

## 🔌 MCP Servers

| Server | Purpose | Configuration | Status |
|--------|---------|---------------|--------|
| **OpenRouter** | AI model routing | [[mcp.json|Config]] | ✅ Active |
| **GitHub** | Repository access | [[mcp.json|Config]] | ✅ Active |
| **IDE** | Editor integration | [[mcp.json|Config]] | ✅ Active |

---

## 📋 Metadata

```yaml
---
title: "Integration Points Index"
type: index
category: integration
audience: [integration-engineers, api-developers]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - index
  - integration
  - apis
  - protocols
---
```

---

**Status**: Production-Ready ✓
