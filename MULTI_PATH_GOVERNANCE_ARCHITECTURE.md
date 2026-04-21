---
title: "Multi-Path Governance Architecture - Migration Guide"
id: multi-path-governance-architecture
type: guide
version: 1.0.0
created_date: 2026-04-13
last_verified: 2026-04-20
status: current
author: "Architecture Team <projectaidevs@gmail.com>"
tags:
  - p0-core
  - governance
  - architecture
  - architecture/router
  - governance/multi-path
  - guide
  - migration
  - reference
area:
  - governance
  - architecture
  - development
component:
  - runtime-router
  - ai-orchestrator
  - governance-pipeline
  - security-layer
  - interface-adapters
audience:
  - developer
  - architect
  - contributor
priority: p0
related_to:
  - "[[MULTI_PATH_GOVERNANCE_COMPLETE]]"
  - "[[ARCHITECTURE_QUICK_REF]]"
  - "[[COPILOT_MANDATORY_GUIDE]]"
  - "[[DEVELOPER_QUICK_REFERENCE]]"
  - "[[CONTRIBUTING]]"
depends_on:
  - "[[MULTI_PATH_GOVERNANCE_COMPLETE]]"
related_systems:
  - runtime-router
  - ai-orchestrator
  - governance-pipeline
  - security-layer
  - web-adapter
  - desktop-adapter
  - cli-adapter
  - agent-adapter
stakeholders:
  - developers
  - architecture-team
  - governance-team
  - contributors
scope: project-wide
review_cycle: quarterly
what: "Technical migration guide for multi-path governance architecture - documents runtime router, AI orchestrator, governance pipeline, security layer, and interface adapter patterns for unified governance across all execution paths"
who: "Developers migrating code to use governance adapters, architects understanding governance flow, contributors implementing new interfaces"
when: "Use when integrating new features with governance, refactoring direct AI calls to use orchestrator, debugging interface adapter issues, or implementing new execution paths"
where: "Root directory as canonical migration reference - complements MULTI_PATH_GOVERNANCE_COMPLETE.md deployment report with technical implementation details"
why: "Enables zero-breaking-change migration to unified governance, documents API patterns for each adapter (web/desktop/CLI/agent), explains provider fallback order, shows security middleware usage (Argon2, JWT, CORS, rate limiting)"
---

---
type: guide
tags:
  - p2-root
  - status
  - guide
  - governance
  - multi-path
  - architecture
created: 2026-04-13
last_verified: 2026-04-20
status: current
related_systems:
  - runtime-router
  - governance-pipeline
  - ai-orchestrator
  - interface-adapters
stakeholders:
  - architecture-team
  - governance-team
  - developers
report_type: guide
supersedes: []
review_cycle: quarterly
---

# Multi-Path Governance Architecture - Migration Guide

## Overview

Project-AI has been refactored to implement **multi-path governance architecture**:

```
ANY ENTRY (web/desktop/CLI/agent)
    ↓
Interface Adapter (thin layer)
    ↓
Runtime Router (src/app/core/runtime/)
    ↓
Governance Pipeline (validate → simulate → gate → execute → commit → log)
    ↓
AI Orchestrator (unified OpenAI/HF/Perplexity gateway)
    ↓
Core Systems (existing business logic - UNCHANGED)
    ↓
State/Response
```

## What Changed

### ✅ PRESERVED (Zero Breaking Changes)
- All core business logic in `src/app/core/*` - unchanged
- All data persistence mechanisms - unchanged
- All AI functionality - enhanced with fallback
- All execution paths (desktop/web/CLI/agents) - work as before

### 🔄 ADDED (New Capabilities)
- **Unified governance** - Every request flows through same validation pipeline
- **AI orchestration** - Automatic fallback across providers (OpenAI → HF → Perplexity)
- **Production security** - JWT tokens, argon2 passwords, CORS, rate limiting
- **Centralized routing** - All operations audited and governed
- **Multi-tenant support** - Interface adapters isolate execution contexts

## Architecture Components

### 1. Runtime Router (`src/app/core/runtime/router.py`)

**Purpose**: Multi-path coordination layer

**Function**:
```python
from app.core.runtime.router import route_request

response = route_request(
    source="web",  # or "desktop", "cli", "agent"
    payload={
        "action": "ai.chat",
        "prompt": "Hello",
        "model": "gpt-4"
    }
)
```

**Response**:
```python
{
    "status": "success",  # or "error"
    "result": "AI response here",
    "metadata": {
        "source": "web",
        "action": "ai.chat",
        "timestamp": "2026-04-13T20:30:00Z"
    }
}
```

### 2. AI Orchestrator (`src/app/core/ai/orchestrator.py`)

**Purpose**: Single gateway for all AI provider calls

**Usage**:
```python
from app.core.ai.orchestrator import run_ai, AIRequest

request = AIRequest(
    task_type="chat",
    prompt="Explain quantum computing",
    model="gpt-4",  # optional
    provider="openai",  # optional - defaults to auto-fallback
    config={"temperature": 0.7}
)

response = run_ai(request)
# response.status: "success" | "error" | "fallback"
# response.result: actual AI output
# response.provider_used: which provider succeeded
```

**Fallback Order**:
1. Specified provider (if `provider` param set)
2. OpenAI (default, most reliable)
3. HuggingFace (fallback)
4. Perplexity (web-enhanced fallback)
5. Local models (offline fallback)

### 3. Governance Pipeline (`src/app/core/governance/pipeline.py`)

**Purpose**: Universal enforcement layer

**Phases**:
1. **Validation** - Input sanitization, type checking, schema validation
2. **Simulation** - Shadow execution for impact analysis
3. **Gate** - Four Laws compliance, user permissions, rate limiting
4. **Execution** - Actual operation via orchestrator/systems
5. **Commit** - State persistence with rollback capability
6. **Logging** - Complete audit trail

**Security Features**:
- XSS prevention (HTML entity encoding)
- SQL injection prevention
- Path traversal prevention
- Command injection prevention
- Four Laws ethical validation

### 4. Security Layer (`src/app/core/security/`)

**auth.py** - JWT tokens + argon2 passwords:
```python
from app.core.security.auth import hash_password, generate_jwt_token, verify_password

# Hash password (argon2id)
hash_value = hash_password("user_password")

# Generate JWT token
token = generate_jwt_token(username="alice", role="admin")

# Verify password
is_valid = verify_password("user_password", hash_value)
```

**middleware.py** - CORS + rate limiting:
```python
from app.core.security.middleware import configure_cors, configure_rate_limiting

# In Flask app
configure_cors(app, allowed_origins=["http://localhost:3000"])
configure_rate_limiting(app)
```

## Interface Adapters

### Web Adapter (`src/app/interfaces/web/app.py`)

**Old** `web/backend/app.py`:
```python
# Direct business logic
@app.route("/api/chat", methods=["POST"])
def chat():
    # Direct OpenAI call
    response = openai.chat.completions.create(...)
    return jsonify(response)
```

**New** `src/app/interfaces/web/app.py`:
```python
# Routes through governance
@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    response = route_request("web", payload={
        "action": "ai.chat",
        "task_type": "chat",
        "prompt": request.json["prompt"]
    })
    return jsonify(response)
```

**Migration**: Old `web/backend/app.py` archived to `archive/experimental/web_backend_old/`, replaced with new adapter.

### Desktop Adapter (`src/app/interfaces/desktop/adapter.py`)

**Usage in GUI code**:
```python
from app.interfaces.desktop import DesktopAdapter

# Initialize after login
adapter = DesktopAdapter(username="alice")

# AI chat
response = adapter.ai_chat("Hello, how are you?")

# AI image
image_data = adapter.ai_image("A sunset over mountains")

# Persona update
adapter.persona_update(trait="curiosity", value=0.9)
```

**Backward compatibility** (`src/app/interfaces/desktop/integration.py`):
```python
from app.interfaces.desktop.integration import execute_ai_chat, execute_ai_image

# Old GUI code still works
result = execute_ai_chat("Hello")
```

### CLI Adapter (`src/app/interfaces/cli/main.py`)

**Usage**:
```bash
# AI chat
python -m app.interfaces.cli --action ai.chat --prompt "Hello"

# Persona update
python -m app.interfaces.cli --action persona.update --trait curiosity --value 0.8

# With JSON payload
python -m app.interfaces.cli --action ai.image --json-payload '{"prompt": "sunset", "provider": "openai"}'
```

### Agent Adapter (`src/app/interfaces/agents/adapter.py`)

**Usage in agent code**:
```python
from app.interfaces.agents import AgentAdapter

# Initialize agent
adapter = AgentAdapter(agent_id="oversight-001", agent_type="oversight")

# Execute AI analysis
result = adapter.analyze_action_safety(
    action="delete_user_data",
    context={"user_consent": True}
)

# Plan task
plan = adapter.plan_task(
    goal="Generate monthly report",
    constraints={"deadline": "2026-04-15"}
)
```

## Migration Path for Existing Code

### Pattern 1: Direct OpenAI Calls

**Before**:
```python
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
result = response.choices[0].message.content
```

**After**:
```python
from app.core.ai.orchestrator import run_ai, AIRequest

request = AIRequest(
    task_type="chat",
    prompt=prompt,
    model="gpt-4"
)
response = run_ai(request)
result = response.result  # Automatic fallback if OpenAI fails
```

### Pattern 2: Direct HuggingFace Calls

**Before**:
```python
import requests
headers = {"Authorization": f"Bearer {hf_key}"}
response = requests.post(api_url, headers=headers, json={"inputs": prompt})
result = response.content
```

**After**:
```python
from app.core.ai.orchestrator import run_ai, AIRequest

request = AIRequest(
    task_type="image",
    prompt=prompt,
    provider="huggingface"
)
response = run_ai(request)
result = response.result
```

### Pattern 3: GUI Button Handlers

**Before**:
```python
def on_chat_button_clicked(self):
    # Direct system import
    from app.core.intelligence_engine import IntelligenceEngine
    engine = IntelligenceEngine()
    result = engine.generate_response(self.input_text)
    self.display_result(result)
```

**After**:
```python
def on_chat_button_clicked(self):
    # Use desktop adapter
    from app.interfaces.desktop.integration import execute_ai_chat
    result = execute_ai_chat(self.input_text)
    self.display_result(result)
```

## Refactored Files

### Core Systems (Now Using Orchestrator)
- ✅ `src/app/core/learning_paths.py` - Learning path generation
- ✅ `src/app/core/image_generator.py` - Image generation (both OpenAI and HF)
- ⏳ `src/app/core/intelligence_engine.py` - Needs refactoring
- ⏳ Other files with direct AI calls (see grep results)

### Interface Replacements
- ✅ `web/backend/app.py` - Replaced with governance adapter
- ✅ Desktop integration layer created
- ✅ CLI adapter created
- ✅ Agent adapter created

## Security Improvements

### Password Storage
- **Before**: Plaintext, SHA-256, bcrypt (mixed)
- **After**: Unified argon2-cffi (memory-hard, OWASP recommended)

### Token Generation
- **Before**: `token-{uuid}` (predictable, no expiration)
- **After**: JWT with expiration, role-based access control

### API Security
- **Before**: No CORS, no rate limiting
- **After**: CORS with origin whitelist, rate limiting per endpoint

### Input Validation
- **Before**: Scattered validation
- **After**: Centralized validation in governance pipeline

## Testing

### Import Test
```bash
python -c "
from app.core.runtime.router import route_request
from app.core.ai.orchestrator import run_ai
from app.core.governance.pipeline import enforce_pipeline
print('✅ All modules imported successfully')
"
```

### Integration Test
```python
from app.core.runtime.router import route_request

# Test AI chat
response = route_request("test", {
    "action": "ai.chat",
    "task_type": "chat",
    "prompt": "Hello"
})
assert response["status"] == "success"
```

### Web Backend Test
```bash
# Start web server
cd web/backend && python app.py

# Test endpoint
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello"}'
```

## Environment Variables

Required in `.env`:
```bash
# AI Providers
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...

# Security
JWT_SECRET_KEY=<generate-secure-key>
FERNET_KEY=<generate-fernet-key>

# Optional
SMTP_USERNAME=<email-alerts>
SMTP_PASSWORD=<email-password>
```

Generate keys:
```python
# JWT secret
import secrets
print(secrets.token_urlsafe(32))

# Fernet key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

## Rollback Plan

If issues arise, archived files are in `archive/experimental/web_backend_old/`:
```bash
# Restore old web backend
cp archive/experimental/web_backend_old/app_original.py web/backend/app.py
```

Core systems in `src/app/core/*` are unchanged, so existing functionality remains intact.

## Benefits

### 1. Governance
- ✅ Every request validated against Four Laws
- ✅ Complete audit trail of all operations
- ✅ Centralized authorization and rate limiting

### 2. Reliability
- ✅ Automatic fallback across AI providers
- ✅ Consistent error handling
- ✅ Graceful degradation

### 3. Security
- ✅ Production-grade auth (argon2, JWT)
- ✅ CORS protection
- ✅ Rate limiting
- ✅ Input sanitization

### 4. Maintainability
- ✅ Zero duplication - logic in /core, interfaces are adapters
- ✅ Clear separation of concerns
- ✅ Single orchestration layer for all AI calls

### 5. Cost Control
- ✅ Centralized AI call tracking
- ✅ Provider fallback reduces costs
- ✅ Rate limiting prevents abuse

## Next Steps

1. **Test thoroughly** - Run full test suite (`pytest -v`)
2. **Update GUI code** - Migrate remaining direct imports to adapters
3. **Monitor logs** - Governance pipeline logs all operations
4. **Tune rate limits** - Adjust based on usage patterns
5. **Add providers** - Implement Perplexity and local model support

## Support

Questions? Check:
- `src/app/core/runtime/router.py` - Router implementation
- `src/app/core/governance/pipeline.py` - Pipeline phases
- `src/app/core/ai/orchestrator.py` - AI provider integration
- This guide - Migration patterns and examples
