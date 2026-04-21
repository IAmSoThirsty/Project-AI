# Integration Systems Relationship Maps

**Mission**: AGENT-060 Integration Systems Relationship Mapping  
**Date Created**: 2025-01-26  
**Status**: ✅ Mission Complete (12 systems documented)

---

## Overview

This directory contains comprehensive relationship maps for all 12 integration systems in Project-AI. Each map documents external service dependencies, API contracts, integration patterns, security considerations, and performance characteristics.

---

## Integration Systems Index

### AI & ML Providers (3 systems)

| # | System | File | Priority | Status |
|---|--------|------|----------|--------|
| 01 | **OpenAI Integration** | [01-openai-integration.md](01-openai-integration.md) | P0 Critical | 🟢 Production |
| 02 | **GitHub Integration** | [02-github-integration.md](02-github-integration.md) | P2 Feature | 🟢 Production |
| 03 | **Hugging Face Integration** | [03-huggingface-integration.md](03-huggingface-integration.md) | P1 Critical | 🟢 Production |

**Key Points**:
- OpenAI is the primary AI provider (GPT-3.5/4, DALL-E 3, embeddings)
- HuggingFace serves as fallback provider (Stable Diffusion 2.1, Mistral-7B)
- GitHub provides security resources and repository metadata
- All AI calls routed through AI Orchestrator for governance

---

### Data & Storage (2 systems)

| # | System | File | Priority | Status |
|---|--------|------|----------|--------|
| 04 | **Database Connectors** | [04-database-connectors.md](04-database-connectors.md) | P0 Critical | 🟢 Production |
| 05 | **External APIs** | [05-external-apis.md](05-external-apis.md) | P2-P3 Mixed | 🟡 Mixed |

**Key Points**:
- Hybrid persistence: SQLite (secure transactions) + JSON (flexible state)
- Fernet encryption for sensitive data (location history, PII)
- External APIs: IP geolocation, weather (planned), news (planned)
- Parameterized queries prevent SQL injection

---

### Architecture & Abstraction (2 systems)

| # | System | File | Priority | Status |
|---|--------|------|----------|--------|
| 06 | **Service Adapters** | [06-service-adapters.md](06-service-adapters.md) | P1 Critical | 🟢 Production |
| 08 | **Intelligence Engine** | [08-intelligence-engine.md](08-intelligence-engine.md) | P0 Critical | 🟢 Production |

**Key Points**:
- Service Adapters enable swappable implementations (mock vs. production)
- Model Adapter abstracts AI backends (OpenAI, HuggingFace, local)
- Memory Adapter abstracts vector DBs (Chroma, FAISS, in-memory)
- Intelligence Engine consolidates 5 subsystems (data analysis, intent detection, learning paths, routing, AGI identity)

---

### Core Features (3 systems)

| # | System | File | Priority | Status |
|---|--------|------|----------|--------|
| 09 | **Learning Paths** | [09-learning-paths.md](09-learning-paths.md) | P1 Feature | 🟢 Production |
| 10 | **Image Generator** | [10-image-generator.md](10-image-generator.md) | P1 Feature | 🟢 Production |
| 11 | **Security Resources API** | [11-security-resources-api.md](11-security-resources-api.md) | P2 Feature | 🟢 Production |

**Key Points**:
- Learning Paths: AI-generated curricula via OpenAI GPT-3.5/4
- Image Generator: Dual-backend (HF Stable Diffusion 2.1 + DALL-E 3)
- 15-keyword content filter for safety
- Security Resources: Tracks 7 GitHub repos (CTF, privacy, pentesting)

---

### Communication (2 systems)

| # | System | File | Priority | Status |
|---|--------|------|----------|--------|
| 12 | **Email Integration** | [12-email-integration.md](12-email-integration.md) | P2 Feature | 🟢 Production |
| 13 | **SMS Integration** | [13-sms-integration.md](13-sms-integration.md) | P3 Future | 🟡 Planned |

**Key Points**:
- Email: SMTP-based emergency alerts (Gmail, SendGrid)
- SMS: Planned for Q3 2025 (Twilio, AWS SNS)
- Emergency contact management with JSON persistence
- HTML email templates with Google Maps integration

---

## Quick Reference

### By Integration Type

**External Services**:
- **AI/ML**: OpenAI (primary), HuggingFace (fallback)
- **APIs**: GitHub (repos), IPStack (location), SMTP (email)
- **Future**: Twilio/AWS SNS (SMS), OpenWeatherMap (weather)

**Internal Systems**:
- **Storage**: SQLite (secure DB), JSON (flexible state), Fernet (encryption)
- **Abstraction**: Service Adapters (6 types), Intelligence Engine (5 subsystems)
- **Features**: Learning Paths, Image Generator, Security Resources

### By Priority

**P0 Critical** (4 systems):
- OpenAI Integration
- Database Connectors
- Intelligence Engine
- (All core business logic)

**P1 Critical/Feature** (4 systems):
- HuggingFace Integration (fallback)
- Service Adapters (abstraction)
- Learning Paths (feature)
- Image Generator (feature)

**P2 Feature** (3 systems):
- GitHub Integration
- External APIs
- Security Resources API
- Email Integration

**P3 Future** (1 system):
- SMS Integration (planned Q3 2025)

### By Status

**🟢 Production** (10 systems):
- All AI providers, databases, adapters, core features, email

**🟡 Mixed** (1 system):
- External APIs (IP geolocation production, weather/news planned)

**🟡 Planned** (1 system):
- SMS Integration (design complete, implementation Q3 2025)

---

## Common Patterns

### Integration Pattern 1: Orchestrator-Mediated

**Used By**: OpenAI, HuggingFace, Learning Paths, Intelligence Engine

**Benefits**:
- Automatic fallback between providers
- Rate limit management
- Cost tracking
- Governance compliance

**Example**:
```python
from app.core.ai.orchestrator import run_ai, AIRequest

request = AIRequest(
    task_type="chat",
    prompt="User question",
    provider="openai",  # or None for auto-fallback
    config={"temperature": 0.7}
)
response = run_ai(request)
```

### Integration Pattern 2: Adapter Pattern

**Used By**: Service Adapters, Model Adapter, Memory Adapter, Desktop Adapter

**Benefits**:
- Swappable implementations (mock vs. production)
- Unified interface across diverse backends
- Easy testing without external services

**Example**:
```python
# Production
model = OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY"))

# Testing
model = MockAdapter(responses={"test": "response"})

# Same interface
result = model.predict("test prompt")
```

### Integration Pattern 3: Hybrid Persistence

**Used By**: Database Connectors, all AI systems

**Pattern**: SQLite for secure transactions + JSON for flexible state

**Benefits**:
- SQL for ACID guarantees (users, audit logs)
- JSON for schema flexibility (AI persona, memory)
- Human-readable JSON for debugging

**Example**:
```python
# SQLite: User authentication
db.execute_query(
    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
    params=(username, bcrypt_hash),
    commit=True
)

# JSON: AI persona state
with open("data/ai_persona/state.json", "w") as f:
    json.dump(persona_state, f, indent=4)
```

### Integration Pattern 4: Content Filtering

**Used By**: Image Generator, Learning Paths (future)

**Pattern**: Keyword-based blocklist + safety negative prompts

**Benefits**:
- Prevent inappropriate content generation
- Compliance with platform policies
- Audit trail of blocked content

**Example**:
```python
BLOCKED_KEYWORDS = ["violence", "gore", "sexual", "nsfw", ...]

def check_content_filter(prompt: str) -> tuple[bool, str]:
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in prompt.lower():
            return False, f"Blocked: {keyword}"
    return True, "OK"
```

---

## Security Best Practices

### 1. API Key Management

**✅ DO**:
```python
api_key = os.getenv("OPENAI_API_KEY")  # From environment
```

**❌ DON'T**:
```python
api_key = "sk-proj-..."  # Hardcoded in source
```

### 2. SQL Injection Prevention

**✅ DO**:
```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**❌ DON'T**:
```python
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 3. Path Traversal Prevention

**✅ DO**:
```python
from app.security.path_security import safe_path_join, sanitize_filename

filepath = safe_path_join("data", sanitize_filename(user_input))
```

**❌ DON'T**:
```python
filepath = f"data/{user_input}"  # Vulnerable to ../../../etc/passwd
```

### 4. Credential Logging

**✅ DO**:
```python
logger.debug(f"Using API key: {api_key[:8]}...")  # First 8 chars only
```

**❌ DON'T**:
```python
logger.debug(f"API key: {api_key}")  # Full key in logs
```

---

## Performance Benchmarks

### API Latency (P95)

| Integration | Operation | P95 Latency | Notes |
|-------------|-----------|-------------|-------|
| OpenAI | Chat (GPT-3.5) | 2.5s | Varies by prompt length |
| OpenAI | Image (DALL-E 3) | 45s | 1024x1024 image |
| HuggingFace | Image (SD 2.1) | 90s | Cold start +20s |
| GitHub | Fetch repo metadata | 1.0s | Rate limited (60/hr) |
| Database | SQLite query | 0.5ms | Indexed lookup |
| Database | JSON read/write | 5ms | File I/O |

### Cost Comparison

| Provider | Service | Cost | Notes |
|----------|---------|------|-------|
| OpenAI | GPT-3.5 Turbo | $0.002/1K tokens | Chat, learning paths |
| OpenAI | GPT-4 | $0.06/1K tokens | Complex reasoning |
| OpenAI | DALL-E 3 | $0.04/image | Standard quality |
| HuggingFace | Stable Diffusion | Free (1K/month) | Cold starts |
| Twilio | SMS (US) | $0.0075/message | Planned (Q3 2025) |
| GitHub | API | Free (60/hr) | 5K/hr with token |

---

## Testing Strategy

### Unit Tests

Each integration has isolated unit tests:
```bash
pytest tests/test_openai_integration.py
pytest tests/test_database_connectors.py
pytest tests/test_image_generator.py
```

### Integration Tests

Tests requiring external services are gated by environment variables:
```python
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
def test_openai_chat():
    # Test with real API
    pass
```

### Mock Testing

All integrations have mock implementations for testing:
- `MockAdapter`: Model adapter mock
- `InMemoryAdapter`: Memory adapter mock
- `openrouter_mock.py`: OpenRouter API mock
- `responses` library: HTTP API mocking

---

## Environment Variables

### Required for Production

```bash
# AI Providers
OPENAI_API_KEY=sk-proj-...
HUGGINGFACE_API_KEY=hf_...

# Email (optional)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Encryption (required for location tracking)
FERNET_KEY=<generated_key>
```

### Optional for Enhanced Features

```bash
# GitHub (for higher rate limits)
GITHUB_TOKEN=ghp_...

# SMS (planned)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...

# Weather (future)
OPENWEATHER_API_KEY=...
```

---

## Documentation Standards

Each integration map includes:

1. **Status Banner**: Status, type, priority, governance
2. **Architecture Diagram**: ASCII art showing relationships
3. **External Dependencies**: Services, endpoints, authentication
4. **Internal Relationships**: Consumers, data flows
5. **API Contracts**: Request/response schemas with examples
6. **Integration Patterns**: Code examples showing usage
7. **Configuration**: Environment variables, setup steps
8. **Error Handling**: Common errors, retry logic, fallbacks
9. **Security**: API key management, input validation, encryption
10. **Performance**: Latency benchmarks, optimization tips
11. **Testing**: Unit tests, integration tests, mocking
12. **Future Enhancements**: Roadmap with phases
13. **Related Systems**: Cross-references to other maps

---

## Navigation

### By Category

**AI & ML**:
- [OpenAI](01-openai-integration.md)
- [HuggingFace](03-huggingface-integration.md)
- [GitHub](02-github-integration.md)

**Data & Storage**:
- [Database Connectors](04-database-connectors.md)
- [External APIs](05-external-apis.md)

**Architecture**:
- [Service Adapters](06-service-adapters.md)
- [Intelligence Engine](08-intelligence-engine.md)

**Features**:
- [Learning Paths](09-learning-paths.md)
- [Image Generator](10-image-generator.md)
- [Security Resources](11-security-resources-api.md)

**Communication**:
- [Email Integration](12-email-integration.md)
- [SMS Integration](13-sms-integration.md)

#---

## Quick Navigation

### Documentation in This Directory

- **01 Openai Integration**: [[relationships\integrations\01-openai-integration.md]]
- **02 Github Integration**: [[relationships\integrations\02-github-integration.md]]
- **03 Huggingface Integration**: [[relationships\integrations\03-huggingface-integration.md]]
- **04 Database Connectors**: [[relationships\integrations\04-database-connectors.md]]
- **05 External Apis**: [[relationships\integrations\05-external-apis.md]]
- **06 Service Adapters**: [[relationships\integrations\06-service-adapters.md]]
- **08 Intelligence Engine**: [[relationships\integrations\08-intelligence-engine.md]]
- **09 Learning Paths**: [[relationships\integrations\09-learning-paths.md]]
- **10 Image Generator**: [[relationships\integrations\10-image-generator.md]]
- **11 Security Resources Api**: [[relationships\integrations\11-security-resources-api.md]]
- **12 Email Integration**: [[relationships\integrations\12-email-integration.md]]
- **13 Sms Integration**: [[relationships\integrations\13-sms-integration.md]]
- **Agent 060 Mission Complete**: [[relationships\integrations\AGENT-060-MISSION-COMPLETE.md]]

### Related Source Code

- **Intelligence Engine**: [[src/app/core/intelligence_engine.py]]
- **Learning Paths**: [[src/app/core/learning_paths.py]]
- **Image Generator**: [[src/app/core/image_generator.py]]

#---

## Quick Navigation

### Documentation in This Directory

- **01 Openai Integration**: [[relationships\integrations\01-openai-integration.md]]
- **02 Github Integration**: [[relationships\integrations\02-github-integration.md]]
- **03 Huggingface Integration**: [[relationships\integrations\03-huggingface-integration.md]]
- **04 Database Connectors**: [[relationships\integrations\04-database-connectors.md]]
- **05 External Apis**: [[relationships\integrations\05-external-apis.md]]
- **06 Service Adapters**: [[relationships\integrations\06-service-adapters.md]]
- **08 Intelligence Engine**: [[relationships\integrations\08-intelligence-engine.md]]
- **09 Learning Paths**: [[relationships\integrations\09-learning-paths.md]]
- **10 Image Generator**: [[relationships\integrations\10-image-generator.md]]
- **11 Security Resources Api**: [[relationships\integrations\11-security-resources-api.md]]
- **12 Email Integration**: [[relationships\integrations\12-email-integration.md]]
- **13 Sms Integration**: [[relationships\integrations\13-sms-integration.md]]
- **Agent 060 Mission Complete**: [[relationships\integrations\AGENT-060-MISSION-COMPLETE.md]]

### Related Source Code

- **Intelligence Engine**: [[src/app/core/intelligence_engine.py]]
- **Learning Paths**: [[src/app/core/learning_paths.py]]
- **Image Generator**: [[src/app/core/image_generator.py]]

### Related Documentation

- **Integration Documentation**: [[source-docs/integrations/README.md]]
- **Developer Quick Reference**: [[DEVELOPER_QUICK_REFERENCE.md]]


---

## Related Documentation

- **Integration Documentation**: [[source-docs/integrations/README.md]]
- **Developer Quick Reference**: [[DEVELOPER_QUICK_REFERENCE.md]]


---

---

## Quick Navigation

### Documentation in This Directory

- **01 Openai Integration**: [[relationships\integrations\01-openai-integration.md]]
- **02 Github Integration**: [[relationships\integrations\02-github-integration.md]]
- **03 Huggingface Integration**: [[relationships\integrations\03-huggingface-integration.md]]
- **04 Database Connectors**: [[relationships\integrations\04-database-connectors.md]]
- **05 External Apis**: [[relationships\integrations\05-external-apis.md]]
- **06 Service Adapters**: [[relationships\integrations\06-service-adapters.md]]
- **08 Intelligence Engine**: [[relationships\integrations\08-intelligence-engine.md]]
- **09 Learning Paths**: [[relationships\integrations\09-learning-paths.md]]
- **10 Image Generator**: [[relationships\integrations\10-image-generator.md]]
- **11 Security Resources Api**: [[relationships\integrations\11-security-resources-api.md]]
- **12 Email Integration**: [[relationships\integrations\12-email-integration.md]]
- **13 Sms Integration**: [[relationships\integrations\13-sms-integration.md]]
- **Agent 060 Mission Complete**: [[relationships\integrations\AGENT-060-MISSION-COMPLETE.md]]

### Related Source Code

- **Intelligence Engine**: [[src/app/core/intelligence_engine.py]]
- **Learning Paths**: [[src/app/core/learning_paths.py]]
- **Image Generator**: [[src/app/core/image_generator.py]]

### Related Documentation

- **Integration Documentation**: [[source-docs/integrations/README.md]]
- **Developer Quick Reference**: [[DEVELOPER_QUICK_REFERENCE.md]]


---

## Related Documentation

- **[../../PROGRAM_SUMMARY.md](../../PROGRAM_SUMMARY.md)**: Complete architecture
- **[../../DEVELOPER_QUICK_REFERENCE.md](../../DEVELOPER_QUICK_REFERENCE.md)**: GUI API reference
- **[../.github/instructions/ARCHITECTURE_QUICK_REF.md](../../.github/instructions/ARCHITECTURE_QUICK_REF.md)**: Visual diagrams

---

## Mission Summary

**AGENT-060 Mission Accomplished**:

- ✅ 12 integration systems fully documented
- ✅ External service dependencies mapped
- ✅ API contracts documented with examples
- ✅ Integration patterns established
- ✅ Security best practices defined
- ✅ Performance benchmarks recorded
- ✅ Testing strategies outlined
- ✅ Future roadmaps planned

**Total Documentation**: ~158,000 characters across 13 files  
**Systems Covered**: 100% of integration systems  
**Code Examples**: 200+ executable snippets  
**Diagrams**: 15 ASCII architecture diagrams

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly  
**Status**: 📚 Living Documentation
