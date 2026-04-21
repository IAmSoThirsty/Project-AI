# OpenAI Integration Relationship Map

**Status**: 🟢 Production | **Type**: External AI Service  
**Priority**: P0 Critical | **Governance**: Orchestrator-Governed

---


## Navigation

**Location**: `relationships\integrations\01-openai-integration.md`

**Parent**: [[relationships\integrations\README.md]]


## External Service Dependencies

### Primary Endpoint
- **Service**: OpenAI API (https://api.openai.com)
- **Authentication**: Bearer Token (OPENAI_API_KEY)
- **Protocol**: REST/HTTP
- **Rate Limits**: Model-dependent (TPM/RPM)

### Models Used
1. **GPT-3.5-turbo**: Default chat, learning paths, intelligence
2. **GPT-4**: Advanced reasoning, complex analysis
3. **DALL-E 3**: Image generation (via `image_generator.py`)
4. **text-embedding-ada-002**: Vector embeddings (via `rag_system.py`)

---

## Internal Relationships

### Core Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATOR (Hub)                     │
│              src/app/core/ai/orchestrator.py                 │
│         ┌────────────────────────────────────┐              │
│         │ Governance, Fallback, Rate Limits  │              │
│         └────────────────────────────────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ OpenAI SDK    │ │ Model Provider│ │ Direct Clients│
│ openai.OpenAI │ │ Adapter Wrapper│ │ (Legacy)      │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Dependency Graph

**CONSUMERS (6 core systems)**:

1. **Intelligence Engine** (`src/app/core/intelligence_engine.py` [[src/app/core/intelligence_engine.py]])
   - Purpose: Chat completions, data analysis, Q&A
   - Models: gpt-3.5-turbo, gpt-4
   - Flow: User query → IntelligenceRouter → Orchestrator → OpenAI

2. **Learning Paths** (`src/app/core/learning_paths.py` [[src/app/core/learning_paths.py]])
   - Purpose: Generate personalized learning curricula
   - Models: gpt-3.5-turbo
   - Flow: Interest → LearningPathManager → Orchestrator → OpenAI

3. **Image Generator** (`src/app/core/image_generator.py` [[src/app/core/image_generator.py]])
   - Purpose: DALL-E 3 image generation
   - Models: dall-e-3
   - Flow: Prompt → ImageGenerator → Orchestrator → OpenAI DALL-E

4. **RAG System** (`src/app/core/rag_system.py` [[src/app/core/rag_system.py]])
   - Purpose: Vector embeddings for retrieval-augmented generation
   - Models: text-embedding-ada-002
   - Flow: Text → RAG → OpenAI Embeddings → Vector DB

5. **Constitutional Model** (`src/app/core/constitutional_model.py` [[src/app/core/constitutional_model.py]])
   - Purpose: Ethics validation, Asimov's Laws reasoning
   - Models: gpt-4
   - Flow: Action → ConstitutionalValidator → OpenAI → Ethics Score

6. **Memory Engine** (`src/app/core/memory_engine.py` [[src/app/core/memory_engine.py]])
   - Purpose: Semantic memory, reflection summaries
   - Models: gpt-3.5-turbo, text-embedding-ada-002
   - Flow: Conversation → MemoryEngine → OpenAI → Embeddings

---

## API Contracts

### Chat Completion Contract

```python
# REQUEST SCHEMA
{
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"}
    ],
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# RESPONSE SCHEMA
{
    "id": "chatcmpl-xxx",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "gpt-3.5-turbo",
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "Response text"
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 50,
        "completion_tokens": 100,
        "total_tokens": 150
    }
}
```

### Image Generation Contract

```python
# REQUEST SCHEMA
{
    "model": "dall-e-3",
    "prompt": "Detailed image description",
    "size": "1024x1024",  # or "1792x1024", "1024x1792"
    "quality": "standard",  # or "hd"
    "n": 1
}

# RESPONSE SCHEMA
{
    "created": 1234567890,
    "data": [{
        "url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
        "revised_prompt": "Enhanced prompt used for generation"
    }]
}
```

### Embeddings Contract

```python
# REQUEST SCHEMA
{
    "model": "text-embedding-ada-002",
    "input": "Text to embed"
}

# RESPONSE SCHEMA
{
    "object": "list",
    "data": [{
        "object": "embedding",
        "index": 0,
        "embedding": [0.001, -0.002, 0.003, ...]  # 1536 dimensions
    }],
    "model": "text-embedding-ada-002",
    "usage": {
        "prompt_tokens": 5,
        "total_tokens": 5
    }
}
```

---

## Integration Patterns

### Pattern 1: Orchestrator-Mediated (MANDATORY)

**Status**: ✅ Production Standard (Post-Refactor)

```python
from app.core.ai.orchestrator import run_ai, AIRequest

# CORRECT: Governed, rate-limited, fallback-enabled
request = AIRequest(
    task_type="chat",
    prompt="User question",
    model="gpt-3.5-turbo",
    provider="openai",
    config={"temperature": 0.7}
)
response = run_ai(request)
```

**Benefits**:
- ✅ Automatic fallback to HuggingFace/Perplexity
- ✅ Rate limit management
- ✅ Cost tracking
- ✅ Governance compliance
- ✅ Error handling

### Pattern 2: Direct SDK (DEPRECATED)

**Status**: ⚠️ Legacy (Pre-Refactor)

```python
import openai

# DEPRECATED: No governance, no fallback
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Question"}]
)
```

**Issues**:
- ❌ No fallback if OpenAI down
- ❌ No rate limit protection
- ❌ No cost tracking
- ❌ No governance

### Pattern 3: Provider Adapter (TRANSITIONAL)

**Status**: 🔄 Refactored to use Orchestrator

```python
from app.core.model_providers import OpenAIProvider

# TRANSITIONAL: Wraps orchestrator for backward compatibility
provider = OpenAIProvider()
response = provider.chat_completion(
    messages=[{"role": "user", "content": "Question"}],
    model="gpt-3.5-turbo"
)
```

---

## Configuration

### Environment Variables

```bash
# REQUIRED
OPENAI_API_KEY=sk-proj-...  # Get from https://platform.openai.com/api-keys

# OPTIONAL
OPENAI_ORG_ID=org-...       # For organization accounts
OPENAI_DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=60
```

### Cost Management

```python
# Cost tracking (in orchestrator)
COST_PER_1K_TOKENS = {
    "gpt-3.5-turbo": {"prompt": 0.0015, "completion": 0.002},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "dall-e-3": {"standard": 0.04, "hd": 0.08},
    "text-embedding-ada-002": {"prompt": 0.0001}
}
```

---

## Error Handling

### Common Errors

1. **401 Unauthorized**: Invalid API key
   - **Mitigation**: Validate key on startup, fallback to HuggingFace

2. **429 Rate Limit**: Too many requests
   - **Mitigation**: Exponential backoff, retry with Retry-After header

3. **500 Server Error**: OpenAI service outage
   - **Mitigation**: Auto-fallback to Perplexity or HuggingFace

4. **Content Filter**: Prompt/output blocked
   - **Mitigation**: Log violation, return filtered response

### Retry Logic

```python
# Implemented in image_generator.py and orchestrator.py
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.8  # 0.8s, 1.6s, 3.2s

for attempt in range(MAX_RETRIES):
    try:
        response = client.chat.completions.create(...)
        break
    except openai.RateLimitError as e:
        if "retry-after" in e.headers:
            time.sleep(int(e.headers["retry-after"]))
        else:
            time.sleep(BACKOFF_FACTOR ** attempt)
```

---

## Security

### API Key Management

- **Storage**: Environment variable (.env file, NOT committed)
- **Rotation**: Manual via OpenAI dashboard
- **Scoping**: Use least-privilege API keys (not root keys)

### Data Privacy

- **PII Filtering**: No user PII sent in prompts (enforced by `path_security.py`)
- **Logging**: API keys never logged (redacted in logs)
- **Encryption**: TLS 1.2+ for all API calls

### Content Filtering

```python
# Implemented in image_generator.py
BLOCKED_KEYWORDS = [
    "violence", "gore", "sexual", "nsfw", "explicit",
    "weapon", "drug", "illegal", "hate", "racist"
]

def check_content_filter(prompt: str) -> tuple[bool, str]:
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in prompt.lower():
            return False, f"Blocked keyword: {keyword}"
    return True, ""
```

---

## Performance

### Latency Benchmarks

| Operation | Model | Avg Latency | P95 Latency |
|-----------|-------|-------------|-------------|
| Chat (short) | gpt-3.5-turbo | 1.2s | 2.5s |
| Chat (long) | gpt-3.5-turbo | 3.5s | 6.0s |
| Chat (complex) | gpt-4 | 8.0s | 15.0s |
| Image Gen | dall-e-3 | 25s | 45s |
| Embeddings | ada-002 | 0.5s | 1.0s |

### Optimization Strategies

1. **Caching**: Store embeddings in vector DB (avoid re-embedding)
2. **Batching**: Batch embeddings (up to 2048 inputs per request)
3. **Streaming**: Use streaming for chat (better UX)
4. **Model Selection**: Use gpt-3.5-turbo for simple tasks

---

## Testing

### Integration Tests

```python
# tests/test_openai_integration.py
def test_openai_chat():
    request = AIRequest(
        task_type="chat",
        prompt="Hello, world!",
        provider="openai"
    )
    response = run_ai(request)
    assert response.status == "success"
    assert response.provider_used == "openai"
    assert len(response.result) > 0

def test_openai_fallback_on_failure():
    # Mock OpenAI failure
    with patch("openai.OpenAI") as mock:
        mock.side_effect = Exception("API down")
        request = AIRequest(task_type="chat", prompt="Test")
        response = run_ai(request)
        # Should fallback to HuggingFace
        assert response.status == "fallback"
        assert response.provider_used == "huggingface"
```

### Mocking

```python
# Use openrouter_mock.py for testing without API calls
from app.core.openrouter_mock import MockOpenRouterProvider

provider = MockOpenRouterProvider()
response = provider.chat_completion(
    messages=[{"role": "user", "content": "Test"}]
)
# Returns pre-defined mock responses
```

---

## Monitoring

### Metrics

- **Request Count**: Total API calls per day
- **Error Rate**: Failed requests / total requests
- **Latency**: P50, P95, P99 response times
- **Cost**: Daily spend by model
- **Fallback Rate**: % of requests using fallback providers

### Alerts

- **High Error Rate**: >5% failures → Alert + auto-fallback
- **High Cost**: >$50/day → Alert ops team
- **High Latency**: P95 >10s → Check OpenAI status

---

## Migration Path

### Phase 1: Orchestrator Rollout ✅ COMPLETE
- Replace direct OpenAI calls with orchestrator
- Add fallback to HuggingFace/Perplexity
- Implement rate limiting

### Phase 2: Cost Optimization 🔄 IN PROGRESS
- Add caching layer
- Implement batching
- Monitor usage patterns

### Phase 3: Multi-Provider ⏳ PLANNED
- Add Anthropic Claude
- Add Google Gemini
- Dynamic provider selection based on cost/latency

---

## Related Systems

### Integration Layer (Same Category)
- **[02-github-integration.md](02-github-integration.md)**: GitHub API for security resources
- **[03-huggingface-integration.md](03-huggingface-integration.md)**: Fallback provider for AI models
- **[06-service-adapters.md](06-service-adapters.md)**: Model adapter abstraction pattern
- **[08-intelligence-engine.md](08-intelligence-engine.md)**: Primary consumer of OpenAI services
- **[09-learning-paths.md](09-learning-paths.md)**: Learning path generation via GPT-3.5/4
- **[10-image-generator.md](10-image-generator.md)**: DALL-E 3 image generation integration

### API Layer (External Interface)
- **[../../source-docs/api/01-API-OVERVIEW.md](../../source-docs/api/01-API-OVERVIEW.md)**: Multi-path API architecture overview
- **[../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md](../../source-docs/api/02-FASTAPI-MAIN-ROUTES.md)**: OpenAI services exposed via FastAPI endpoints
- **[../../source-docs/api/06-FLASK-WEB-BACKEND.md](../../source-docs/api/06-FLASK-WEB-BACKEND.md)**: Flask routes OpenAI via orchestrator
- **[../../source-docs/api/07-RUNTIME-ROUTER.md](../../source-docs/api/07-RUNTIME-ROUTER.md)**: Router coordinates OpenAI requests across paths
- **[../../source-docs/api/08-GOVERNANCE-PIPELINE.md](../../source-docs/api/08-GOVERNANCE-PIPELINE.md)**: Governance validates OpenAI operations
- **[../../source-docs/api/09-SECURITY-AUTH.md](../../source-docs/api/09-SECURITY-AUTH.md)**: JWT authentication for API access
- **[../../source-docs/api/12-API-CLIENT-EXAMPLES.md](../../source-docs/api/12-API-CLIENT-EXAMPLES.md)**: Python/JS clients for OpenAI endpoints

### Web Layer (User Interface)
- **[../web/01_flask_api_architecture.md](../web/01_flask_api_architecture.md)**: Flask backend consumes OpenAI via orchestrator
- **[../web/02_react_frontend_architecture.md](../web/02_react_frontend_architecture.md)**: React UI consumes OpenAI chat/image endpoints
- **[../web/04_api_routes_controllers.md](../web/04_api_routes_controllers.md)**: API routes integrate OpenAI services
- **[../web/09_request_flow_state_propagation.md](../web/09_request_flow_state_propagation.md)**: Request flow from UI to OpenAI
- **[../../source-docs/web/01_FLASK_BACKEND_API.md](../../source-docs/web/01_FLASK_BACKEND_API.md)**: Flask API reference for OpenAI endpoints
- **[../../source-docs/web/05_API_CLIENT_INTEGRATION.md](../../source-docs/web/05_API_CLIENT_INTEGRATION.md)**: Axios client integration patterns

### CLI Layer (Automation)
- **[../cli-automation/01_cli-interface.md](../cli-automation/01_cli-interface.md)**: CLI can invoke OpenAI via API
- **[../cli-automation/04_automation-workflows.md](../cli-automation/04_automation-workflows.md)**: Workflows may test OpenAI integration

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **01 Openai Integration**: [[source-docs\integrations\01-openai-integration.md]]
- **02 Huggingface Integration**: [[source-docs\integrations\02-huggingface-integration.md]]
- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **11 Openrouter Integration**: [[source-docs\integrations\11-openrouter-integration.md]]
- **12 Perplexity Integration**: [[source-docs\integrations\12-perplexity-integration.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
