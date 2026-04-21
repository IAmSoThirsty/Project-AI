# API Endpoints Index

> **📍 Location**: `indexes/api_endpoints_index.md`  
> **🎯 Purpose**: Searchable index of all API endpoints and methods  
> **👥 Audience**: API developers, integration engineers, testers  
> **🔄 Status**: Production-Ready ✓

---

## 🔍 Search Guide

**How to use this index:**
- Use Ctrl+F / Cmd+F to search for endpoints or operations
- Browse by API type (REST, Internal, External)
- Check authentication requirements
- Follow links to implementation

---

## 🌐 REST API Endpoints (Flask/FastAPI - Situational Tier)

### Authentication Endpoints
| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| `POST` | `/api/auth/login` | User login | None | ✅ Production |
| `POST` | `/api/auth/logout` | User logout | Bearer | ✅ Production |
| `POST` | `/api/auth/register` | User registration | None | ✅ Production |
| `GET` | `/api/auth/validate` | Validate token | Bearer | ✅ Production |

📄 [[docs/developer/API_REFERENCE.md|API Reference]]  
📄 [[API_QUICK_REFERENCE.md|API Quick Reference]]

### AI Operations Endpoints
| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| `POST` | `/api/ai/chat` | Send chat message | Bearer | ✅ Production |
| `POST` | `/api/ai/persona/update` | Update persona | Bearer | ✅ Production |
| `GET` | `/api/ai/persona/state` | Get persona state | Bearer | ✅ Production |
| `POST` | `/api/ai/memory/add` | Add knowledge | Bearer | ✅ Production |
| `GET` | `/api/ai/memory/search` | Search knowledge | Bearer | ✅ Production |

### Learning Request Endpoints
| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| `POST` | `/api/learning/submit` | Submit learning request | Bearer | ✅ Production |
| `POST` | `/api/learning/approve` | Approve request | Bearer+Admin | ✅ Production |
| `POST` | `/api/learning/deny` | Deny request | Bearer+Admin | ✅ Production |
| `GET` | `/api/learning/requests` | List requests | Bearer | ✅ Production |

### Image Generation Endpoints
| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| `POST` | `/api/image/generate` | Generate image | Bearer | ✅ Production |
| `GET` | `/api/image/history` | Get generation history | Bearer | ✅ Production |
| `GET` | `/api/image/{id}` | Get image by ID | Bearer | ✅ Production |

### Health & Monitoring Endpoints
| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| `GET` | `/health` | Health check | None | ✅ Production |
| `GET` | `/metrics` | Prometheus metrics | None | ✅ Production |
| `GET` | `/api/health` | API health status | None | ✅ Production |

---

## 🔌 Internal APIs (Python Modules)

### Core AI Systems API
| Component | Method | Parameters | Returns | Documentation |
|-----------|--------|------------|---------|---------------|
| `FourLaws` | `validate_action(action, context)` | action: str, context: dict | (bool, str) | [[relationships/core-ai/01_four_laws_relationships.md|Docs]] |
| `AIPersona` | `update_mood(mood_change)` | mood_change: dict | None | [[relationships/core-ai/02_ai_persona_relationships.md|Docs]] |
| `MemoryExpansion` | `add_knowledge(category, content)` | category: str, content: str | str (ID) | [[relationships/core-ai/03_memory_expansion_relationships.md|Docs]] |
| `LearningRequest` | `submit_request(content, source)` | content: str, source: str | str (request_id) | [[relationships/core-ai/04_learning_request_relationships.md|Docs]] |
| `PluginManager` | `load_plugin(plugin_path)` | plugin_path: str | bool | [[relationships/core-ai/05_plugin_manager_relationships.md|Docs]] |
| `CommandOverride` | `request_override(password, action)` | password: str, action: str | (bool, str) | [[relationships/core-ai/06_command_override_relationships.md|Docs]] |

### User Management API
| Class | Method | Parameters | Returns | Documentation |
|-------|--------|------------|---------|---------------|
| `UserManager` | `authenticate(username, password)` | username: str, password: str | bool | [[src/app/core/user_manager.py|Code]] |
| `UserManager` | `create_user(username, password)` | username: str, password: str | bool | [[src/app/core/user_manager.py|Code]] |

---

## 🌍 External API Integrations

### OpenAI API Integration
| Service | Endpoint | Purpose | Configuration |
|---------|----------|---------|---------------|
| **Chat Completions** | `POST /v1/chat/completions` | GPT-4 chat | `OPENAI_API_KEY` |
| **Image Generation** | `POST /v1/images/generations` | DALL-E 3 | `OPENAI_API_KEY` |

📄 [[src/app/core/intelligence_engine.py|Intelligence Engine Implementation]]  
📄 [[src/app/core/image_generator.py|Image Generator Implementation]]

### Hugging Face API Integration
| Service | Model | Purpose | Configuration |
|---------|-------|---------|---------------|
| **Inference API** | `stabilityai/stable-diffusion-2-1` | Image generation | `HUGGINGFACE_API_KEY` |

📄 [[src/app/core/image_generator.py|Implementation]]

### GitHub API Integration (via MCP)
| Service | Purpose | Configuration |
|---------|---------|---------------|
| **GitHub MCP Server** | Repository access, PR management | [[docs/MCP_CONFIGURATION.md|MCP Config]] |

---

## 📊 API Statistics

- **REST Endpoints**: 15+
- **Internal APIs**: 25+ classes with 150+ methods
- **External Integrations**: 3 major services
- **Authentication Methods**: Bearer tokens, API keys
- **Status**: 100% production-ready

---

## 🔗 Related Documentation

- [[API_QUICK_REFERENCE.md|API Quick Reference]]
- [[docs/developer/API_REFERENCE.md|Full API Reference]]
- [[AGENT-083-API-COVERAGE-REPORT.md|API Coverage Report]]
- [[AGENT-083-GUIDE-API-MAP.md|Guide-API Map]]

---

## 📋 Metadata

```yaml
---
title: "API Endpoints Index"
type: index
category: api
audience: [api-developers, integration-engineers, testers]
status: production
version: 1.0.0
created: 2025-01-20
tags:
  - index
  - api
  - endpoints
  - rest
  - integration
---
```

---

**Index Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Endpoints Indexed**: 40+  
**Status**: Production-Ready ✓
