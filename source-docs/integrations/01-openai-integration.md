# OpenAI API Integration

## Overview

Project-AI integrates with OpenAI's API for advanced language model capabilities, including chat completions, image generation (DALL-E 3), and embeddings. The integration is orchestrated through a unified AI orchestration layer that provides governance, fallback mechanisms, and consistent error handling.

## Architecture

### Integration Layers

```
Application Layer
    ↓
AI Orchestrator (app.core.ai.orchestrator)
    ↓
OpenAI Provider (app.core.model_providers)
    ↓
OpenAI SDK (openai package)
    ↓
OpenAI API (api.openai.com)
```

### Key Components

1. **AI Orchestrator** (`src/app/core/ai/orchestrator.py` [[src/app/core/ai/orchestrator.py]])
   - Unified entry point for all AI operations
   - Provider fallback logic (OpenAI → HuggingFace → Perplexity → Local)
   - Request/response dataclass structures
   - Error handling and retry logic

2. **OpenAI Provider** (`src/app/core/model_providers.py` [[src/app/core/model_providers.py]])
   - Implements `ModelProvider` abstract interface
   - Wraps OpenAI SDK for governance compliance
   - Provides chat completion, image generation, and embedding methods
   - Handles API key management from environment variables

3. **Service Modules** (consumers of OpenAI API)
   - `learning_paths.py`: Learning path generation using GPT models
   - `intelligence_engine.py`: Chat interface and query routing
   - `image_generator.py`: DALL-E 3 image generation backend
   - `constitutional_model.py`: Constitutional reasoning with GPT-4
   - Various agent modules for specialized AI tasks

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key from platform.openai.com

# Optional
IMAGE_API_MAX_RETRIES=3                  # Retry attempts for transient failures
IMAGE_API_BACKOFF_FACTOR=0.8             # Exponential backoff multiplier
```

### Setup Instructions

1. **Obtain API Key**
   ```bash
   # Visit https://platform.openai.com/api-keys
   # Create new secret key
   # Copy to .env file
   ```

2. **Install Dependencies**
   ```bash
   pip install openai>=1.0.0
   ```

3. **Verify Configuration**
   ```python
   from app.core.model_providers import OpenAIProvider
   
   provider = OpenAIProvider()
   assert provider.is_available(), "OpenAI API key not configured"
   ```

## Usage Patterns

### 1. Chat Completion via Orchestrator (RECOMMENDED)

```python
from app.core.ai.orchestrator import run_ai, AIRequest, AIResponse

# Create request
request = AIRequest(
    task_type="chat",
    prompt="Explain quantum computing in simple terms",
    model="gpt-4",  # or "gpt-3.5-turbo"
    provider="openai",  # Optional: auto-fallback if omitted
    context={"user_id": "user123", "conversation_id": "conv456"}
)

# Execute with governance and fallback
response: AIResponse = run_ai(request)

if response.status == "success":
    print(f"Response: {response.result}")
    print(f"Provider: {response.provider_used}")
else:
    print(f"Error: {response.error}")
```

### 2. Direct Provider Access (LEGACY)

```python
from app.core.model_providers import OpenAIProvider

provider = OpenAIProvider()

# Chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"}
]

response = provider.chat_completion(
    messages=messages,
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=500
)
print(response)
```

### 3. Learning Path Generation

```python
from app.core.learning_paths import LearningPathManager

manager = LearningPathManager(provider="openai")

# Generate structured learning path
path = manager.generate_path(
    interest="Python web development",
    skill_level="beginner",
    model="gpt-3.5-turbo"
)

# Save to user profile
manager.save_path(
    username="john_doe",
    interest="Python web development",
    path_content=path
)
```

### 4. Image Generation (DALL-E 3)

```python
from app.core.image_generator import ImageGenerator, Backend

generator = ImageGenerator()

# Generate with OpenAI backend
image_path, metadata = generator.generate(
    prompt="A serene mountain landscape at sunset",
    style="photorealistic",
    size="1024x1024",
    backend=Backend.OPENAI
)

print(f"Generated: {image_path}")
print(f"Model: {metadata['backend']}")
```

### 5. Constitutional Reasoning

```python
from app.core.constitutional_model import ConstitutionalModel

model = ConstitutionalModel()

# Evaluate decision against constitutional principles
result = model.evaluate_action(
    action="Delete user data without consent",
    context={"user_requested": False, "legal_obligation": False}
)

print(f"Allowed: {result['allowed']}")
print(f"Reasoning: {result['reasoning']}")
```

## API Models

### Chat Models

| Model | Context Window | Use Case | Cost |
|-------|---------------|----------|------|
| `gpt-4` | 8,192 tokens | Complex reasoning, constitutional logic | High |
| `gpt-4-32k` | 32,768 tokens | Long-context analysis, document review | Very High |
| `gpt-3.5-turbo` | 4,096 tokens | General chat, learning paths, quick queries | Low |
| `gpt-3.5-turbo-16k` | 16,384 tokens | Medium-length conversations | Medium |

### Image Models

| Model | Resolution | Use Case |
|-------|-----------|----------|
| `dall-e-3` | 1024x1024, 1024x1792, 1792x1024 | High-quality image generation |
| `dall-e-2` | 256x256, 512x512, 1024x1024 | Fast prototyping, lower cost |

### Embedding Models

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| `text-embedding-ada-002` | 1,536 | Semantic search, knowledge base indexing |
| `text-embedding-3-small` | 512 | Cost-effective embeddings |
| `text-embedding-3-large` | 3,072 | High-accuracy semantic tasks |

## Error Handling

### Retry Logic

The integration implements automatic retry with exponential backoff for transient errors:

```python
# In image_generator.py
def _request_with_retries(method: str, url: str, **kwargs) -> requests.Response:
    """Retry logic for 429, 502, 503, 504 status codes."""
    allowed_status_retry = {429, 502, 503, 504}
    
    for attempt in range(1, MAX_API_RETRIES + 1):
        response = requests.request(method, url, **kwargs)
        
        if response.status_code not in allowed_status_retry:
            return response
        
        # Honor Retry-After header if present
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            time.sleep(int(retry_after))
            continue
        
        # Exponential backoff
        backoff = BACKOFF_FACTOR * (2 ** (attempt - 1))
        time.sleep(backoff)
    
    response.raise_for_status()
    return response
```

### Common Error Scenarios

| Error Code | Cause | Mitigation |
|-----------|-------|------------|
| `401 Unauthorized` | Invalid API key | Verify `OPENAI_API_KEY` in `.env` [[.env]] |
| `429 Too Many Requests` | Rate limit exceeded | Automatic retry with backoff |
| `500 Internal Server Error` | OpenAI service issue | Fallback to HuggingFace provider |
| `503 Service Unavailable` | Temporary outage | Retry up to 3 times |

### Error Logging

```python
import logging

logger = logging.getLogger(__name__)

try:
    response = run_ai(request)
except RuntimeError as e:
    logger.error(f"OpenAI API call failed: {e}", exc_info=True)
    # Fallback to cached response or user notification
```

## Security Considerations

### API Key Management

1. **Never hardcode API keys**
   ```python
   # ❌ WRONG
   api_key = "sk-proj-abc123..."
   
   # ✅ CORRECT
   api_key = os.getenv("OPENAI_API_KEY")
   ```

2. **Use .env file with .gitignore**
   ```bash
   # .env
   OPENAI_API_KEY=sk-proj-...
   
   # .gitignore
   .env
   *.env
   ```

3. **Rotate keys periodically**
   - Generate new key in OpenAI dashboard
   - Update `.env` [[.env]] file
   - Revoke old key

### Content Filtering

```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()

# Content safety check before generation
is_safe, reason = generator.check_content_filter(
    "A photorealistic image of..."
)

if not is_safe:
    raise ValueError(f"Content filter triggered: {reason}")
```

### Rate Limiting

```python
from app.core.ai.orchestrator import run_ai, AIRequest
import time

# Implement client-side rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 0.5  # 500ms between requests

def rate_limited_ai_call(request: AIRequest):
    global last_request_time
    
    elapsed = time.time() - last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    
    response = run_ai(request)
    last_request_time = time.time()
    
    return response
```

## Performance Optimization

### Model Selection Strategy

```python
def select_optimal_model(task_complexity: str, context_size: int) -> str:
    """Select most cost-effective model for task."""
    if task_complexity == "high" or context_size > 8000:
        return "gpt-4"
    elif context_size > 4000:
        return "gpt-3.5-turbo-16k"
    else:
        return "gpt-3.5-turbo"  # Most cost-effective

# Usage
request = AIRequest(
    task_type="chat",
    prompt=user_query,
    model=select_optimal_model("medium", len(user_query))
)
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_ai_response(prompt_hash: str, model: str) -> str:
    """Cache frequently requested completions."""
    request = AIRequest(
        task_type="chat",
        prompt=prompt_hash,  # Original prompt stored separately
        model=model
    )
    response = run_ai(request)
    return response.result

# Usage
prompt = "What is Python?"
prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
result = cached_ai_response(prompt_hash, "gpt-3.5-turbo")
```

### Token Management

```python
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Estimate token count before API call."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def truncate_to_limit(text: str, max_tokens: int, model: str) -> str:
    """Truncate text to fit token limit."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
    
    truncated_tokens = tokens[:max_tokens]
    return encoding.decode(truncated_tokens)

# Usage
prompt = "..." # Long text
estimated = estimate_tokens(prompt)

if estimated > 4000:
    prompt = truncate_to_limit(prompt, 4000, "gpt-3.5-turbo")
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from app.core.model_providers import OpenAIProvider

class TestOpenAIProvider:
    @patch('app.core.model_providers.OpenAI')
    def test_chat_completion_success(self, mock_openai):
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Test
        provider = OpenAIProvider(api_key="test-key")
        result = provider.chat_completion(
            messages=[{"role": "user", "content": "Hi"}],
            model="gpt-3.5-turbo"
        )
        
        assert result == "Hello!"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_is_available_without_key(self):
        provider = OpenAIProvider(api_key=None)
        assert not provider.is_available()
```

### Integration Tests

```python
import pytest
import os
from app.core.ai.orchestrator import run_ai, AIRequest

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="API key not set")
def test_openai_chat_completion():
    """Test actual OpenAI API call (requires valid key)."""
    request = AIRequest(
        task_type="chat",
        prompt="Say 'Integration test passed'",
        model="gpt-3.5-turbo",
        provider="openai"
    )
    
    response = run_ai(request)
    
    assert response.status == "success"
    assert response.provider_used == "openai"
    assert "test" in response.result.lower()
```

## Monitoring

### Usage Tracking

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIUsageTracker:
    def __init__(self):
        self.usage_log = []
    
    def log_request(self, model: str, tokens: int, cost: float):
        """Log API usage for cost tracking."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tokens": tokens,
            "cost": cost
        }
        self.usage_log.append(entry)
        logger.info(f"OpenAI usage: {entry}")
    
    def get_daily_cost(self) -> float:
        """Calculate total cost for current day."""
        today = datetime.now().date()
        return sum(
            e["cost"] for e in self.usage_log
            if datetime.fromisoformat(e["timestamp"]).date() == today
        )
```

### Health Checks

```python
from app.core.model_providers import OpenAIProvider

def check_openai_health() -> dict:
    """Verify OpenAI API connectivity."""
    provider = OpenAIProvider()
    
    if not provider.is_available():
        return {"status": "unavailable", "reason": "API key not configured"}
    
    try:
        # Minimal test request
        response = provider.chat_completion(
            messages=[{"role": "user", "content": "ping"}],
            model="gpt-3.5-turbo",
            max_tokens=5
        )
        return {"status": "healthy", "latency_ms": 150}
    except Exception as e:
        return {"status": "error", "reason": str(e)}
```

## Migration Guide

### From Direct OpenAI Calls to Orchestrator

**Before:**
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

**After:**
```python
from app.core.ai.orchestrator import run_ai, AIRequest

request = AIRequest(
    task_type="chat",
    prompt="Hello",
    model="gpt-3.5-turbo"
)
response = run_ai(request)
print(response.result)
```

**Benefits:**
- Automatic provider fallback
- Governance compliance
- Consistent error handling
- Usage tracking

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set" error**
   ```bash
   # Verify .env file exists
   cat .env | grep OPENAI_API_KEY
   
   # Reload environment
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

2. **"Model not found" error**
   ```python
   # Check available models
   from openai import OpenAI
   client = OpenAI()
   models = client.models.list()
   print([m.id for m in models.data if m.id.startswith('gpt')])
   ```

3. **Rate limit exceeded**
   ```python
   # Implement exponential backoff
   import time
   from openai import RateLimitError
   
   for attempt in range(3):
       try:
           response = run_ai(request)
           break
       except RateLimitError:
           time.sleep(2 ** attempt)
   ```

## References

- **OpenAI API Documentation**: https://platform.openai.com/docs
- **OpenAI Python SDK**: https://github.com/openai/openai-python
- **Rate Limits**: https://platform.openai.com/docs/guides/rate-limits
- **Pricing**: https://openai.com/pricing

## Related Documentation

- **01 Openai Integration**: [[relationships\integrations\01-openai-integration.md]]


- [02-huggingface-integration.md](./02-huggingface-integration.md) - HuggingFace fallback provider
- [03-ai-orchestrator.md](./03-ai-orchestrator.md) - Unified AI coordination layer
- [04-image-generation.md](./04-image-generation.md) - Multi-backend image generation
- [../architecture/ai-systems.md](../architecture/ai-systems.md) - Core AI systems overview
