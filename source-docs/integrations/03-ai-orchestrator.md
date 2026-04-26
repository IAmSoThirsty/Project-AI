# AI Orchestrator - Unified Provider Coordination

## Overview

The AI Orchestrator (`src/app/core/ai/orchestrator.py` [[src/app/core/ai/orchestrator.py]]) is Project-AI's central coordination layer for all AI provider interactions. It provides unified request/response interfaces, automatic provider fallback, governance compliance enforcement, and consistent error handling across OpenAI, HuggingFace, Perplexity, and local models.

## Architecture

### Core Design Principles

1. **Single Entry Point**: All AI operations flow through `run_ai()`
2. **Provider Abstraction**: Consumers never directly import provider SDKs
3. **Automatic Fallback**: Sequential provider attempts on failure
4. **Governance Integration**: Constitutional validation before execution
5. **Observability**: Structured logging and metrics collection

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (learning_paths, intelligence_engine, image_generator)      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Orchestrator                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  AIRequest   │  │  run_ai()    │  │  AIResponse  │      │
│  │  Dataclass   │─▶│  Coordinator │─▶│  Dataclass   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────┬──────────────┬──────────────┬────────────────┘
               │              │              │
               ▼              ▼              ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
│ OpenAI Provider  │  │ HuggingFace  │  │ Perplexity   │
└──────────────────┘  └──────────────┘  └──────────────┘
```

## Core Data Structures

### AIRequest

Encapsulates all information needed for an AI operation:

```python
from dataclasses import dataclass
from typing import Any, Literal

@dataclass
class AIRequest:
    """Unified request structure for all AI operations."""
    
    # Required fields
    task_type: Literal["chat", "completion", "image", "embedding", "analysis"]
    prompt: str
    
    # Optional fields
    model: str | None = None              # e.g., "gpt-4", "gpt-3.5-turbo"
    provider: AIProvider | None = None    # Force specific provider
    config: dict[str, Any] | None = None  # Provider-specific parameters
    context: dict[str, Any] | None = None # Additional context (user_id, etc.)

# Type alias for supported providers
AIProvider = Literal["openai", "huggingface", "perplexity", "local"]
```

**Usage Example:**
```python
from app.core.ai.orchestrator import AIRequest

# Chat request (auto-selects best provider)
request = AIRequest(
    task_type="chat",
    prompt="Explain quantum entanglement",
    model="gpt-4",
    context={"user_id": "user123", "session_id": "sess456"}
)

# Image generation request (force specific provider)
image_request = AIRequest(
    task_type="image",
    prompt="A serene landscape painting",
    provider="huggingface",  # Force HuggingFace
    config={"num_inference_steps": 50, "guidance_scale": 7.5}
)

# Embedding request with custom config
embedding_request = AIRequest(
    task_type="embedding",
    prompt="Machine learning is a subset of AI",
    model="text-embedding-ada-002",
    config={"encoding_format": "float"}
)
```

### AIResponse

Structured response with metadata and provenance:

```python
@dataclass
class AIResponse:
    """Unified response structure from AI operations."""
    
    status: Literal["success", "error", "fallback"]  # Operation outcome
    result: Any                                       # Generated content
    provider_used: AIProvider                         # Which provider succeeded
    metadata: dict[str, Any]                          # Request details, timing
    error: str | None = None                          # Error message if failed
```

**Response Patterns:**
```python
# Success response
response = AIResponse(
    status="success",
    result="Quantum entanglement is...",
    provider_used="openai",
    metadata={
        "model": "gpt-4",
        "tokens_used": 150,
        "latency_ms": 1200,
        "timestamp": "2024-01-15T10:30:00Z"
    },
    error=None
)

# Fallback response (OpenAI failed, HuggingFace succeeded)
response = AIResponse(
    status="fallback",
    result="Generated image URL",
    provider_used="huggingface",
    metadata={
        "attempted_providers": ["openai", "huggingface"],
        "fallback_reason": "OpenAI rate limit exceeded"
    }
)

# Error response (all providers failed)
response = AIResponse(
    status="error",
    result=None,
    provider_used="openai",  # Last attempted provider
    metadata={"attempts": 4},
    error="All providers failed: Network timeout"
)
```

## Fallback Strategy

### Provider Cascade

The orchestrator attempts providers in priority order:

```python
def run_ai(request: AIRequest) -> AIResponse:
    """Execute with automatic fallback."""
    
    # If specific provider requested, try only that
    if request.provider:
        return _call_provider(request.provider, request)
    
    # Auto-fallback: Try each provider in sequence
    providers: list[AIProvider] = [
        "openai",      # Primary: Most reliable, best quality
        "huggingface", # Secondary: Open-source models
        "perplexity",  # Tertiary: Web-enhanced responses
        "local"        # Last resort: Offline capability
    ]
    
    last_error = None
    for provider in providers:
        try:
            logger.info(f"Attempting provider: {provider}")
            response = _call_provider(provider, request)
            
            if response.status == "success":
                logger.info(f"Success with provider: {provider}")
                return response
        
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            last_error = e
            continue
    
    # All providers exhausted
    raise RuntimeError(f"All providers failed. Last error: {last_error}")
```

### Fallback Decision Matrix

| Primary Fails | Reason | Fallback Action |
|--------------|--------|-----------------|
| OpenAI | Rate limit (429) | Wait + retry, then HuggingFace |
| OpenAI | Authentication (401) | Skip to HuggingFace |
| OpenAI | Service outage (500) | Immediate HuggingFace fallback |
| HuggingFace | Model loading (503) | Retry with backoff, then Perplexity |
| HuggingFace | Invalid token (401) | Skip to Perplexity |
| Perplexity | Network timeout | Skip to local models |
| All providers | Total failure | Return cached result or error |

## Provider Implementations

### OpenAI Provider

```python
def _call_openai(request: AIRequest) -> AIResponse:
    """Execute request via OpenAI API."""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        
        client = OpenAI(api_key=api_key)
        
        # Route by task type
        if request.task_type in ["chat", "completion", "analysis"]:
            model = request.model or "gpt-4"
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": request.prompt}],
                **(request.config or {})
            )
            result = response.choices[0].message.content
            
            return AIResponse(
                status="success",
                result=result,
                provider_used="openai",
                metadata={
                    "model": model,
                    "tokens": response.usage.total_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
        
        elif request.task_type == "image":
            model = request.model or "dall-e-3"
            response = client.images.generate(
                model=model,
                prompt=request.prompt,
                **(request.config or {})
            )
            
            return AIResponse(
                status="success",
                result=response.data[0].url,
                provider_used="openai",
                metadata={"model": model, "revised_prompt": response.data[0].revised_prompt}
            )
        
        elif request.task_type == "embedding":
            model = request.model or "text-embedding-ada-002"
            response = client.embeddings.create(
                model=model,
                input=request.prompt,
                **(request.config or {})
            )
            
            return AIResponse(
                status="success",
                result=response.data[0].embedding,
                provider_used="openai",
                metadata={"model": model, "dimensions": len(response.data[0].embedding)}
            )
        
        else:
            raise ValueError(f"Unsupported task type: {request.task_type}")
    
    except Exception as e:
        logger.error(f"OpenAI provider error: {e}")
        raise
```

### HuggingFace Provider

```python
def _call_huggingface(request: AIRequest) -> AIResponse:
    """Execute request via HuggingFace Inference API."""
    try:
        import requests
        
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY not set")
        
        # Model selection
        if request.task_type == "image":
            model = request.model or "stabilityai/stable-diffusion-2-1"
        elif request.task_type == "chat":
            model = request.model or "mistralai/Mistral-7B-Instruct-v0.2"
        else:
            raise ValueError(f"HuggingFace: Unsupported task {request.task_type}")
        
        # API call
        url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        payload = {
            "inputs": request.prompt,
            **(request.config or {})
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse response based on task type
        if request.task_type == "image":
            # Binary image data
            result = response.content
        else:
            # JSON response
            result = response.json()
        
        return AIResponse(
            status="success",
            result=result,
            provider_used="huggingface",
            metadata={"model": model}
        )
    
    except Exception as e:
        logger.error(f"HuggingFace provider error: {e}")
        raise
```

### Perplexity Provider

```python
def _call_perplexity(request: AIRequest) -> AIResponse:
    """Execute request via Perplexity API (web-enhanced)."""
    try:
        import requests
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise RuntimeError("PERPLEXITY_API_KEY not set")
        
        # Perplexity specializes in web-augmented chat
        if request.task_type not in ["chat", "completion", "analysis"]:
            raise ValueError(f"Perplexity only supports chat tasks")
        
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model or "pplx-70b-online",
            "messages": [{"role": "user", "content": request.prompt}],
            **(request.config or {})
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        return AIResponse(
            status="success",
            result=data["choices"][0]["message"]["content"],
            provider_used="perplexity",
            metadata={
                "model": data["model"],
                "citations": data.get("citations", [])  # Web sources
            }
        )
    
    except Exception as e:
        logger.error(f"Perplexity provider error: {e}")
        raise
```

### Local Provider (Fallback)

```python
def _call_local(request: AIRequest) -> AIResponse:
    """Execute using local models (offline fallback)."""
    try:
        logger.info("Using local fallback provider")
        
        # Placeholder for local model inference
        # In production, integrate with:
        # - llama.cpp for local LLMs
        # - Stable Diffusion local deployment
        # - Sentence transformers for embeddings
        
        if request.task_type == "chat":
            result = f"Local response to: {request.prompt[:50]}..."
        else:
            result = "Local model not available for this task"
        
        return AIResponse(
            status="success",
            result=result,
            provider_used="local",
            metadata={"model": "local-fallback"}
        )
    
    except Exception as e:
        logger.error(f"Local provider error: {e}")
        raise
```

## Usage Patterns

### 1. Basic Chat Completion

```python
from app.core.ai.orchestrator import run_ai, AIRequest

# Simple chat with auto-fallback
request = AIRequest(
    task_type="chat",
    prompt="What is the capital of France?"
)

response = run_ai(request)
print(f"Answer: {response.result}")
print(f"Provider: {response.provider_used}")
```

### 2. Forced Provider Selection

```python
# Force HuggingFace even if OpenAI is available
request = AIRequest(
    task_type="image",
    prompt="A futuristic city",
    provider="huggingface",  # No fallback
    config={"num_inference_steps": 50}
)

try:
    response = run_ai(request)
except RuntimeError as e:
    print(f"Forced provider failed: {e}")
```

### 3. Advanced Configuration

```python
# Chat with temperature, max tokens, system message
request = AIRequest(
    task_type="chat",
    prompt="Write a poem about AI",
    model="gpt-4",
    config={
        "temperature": 0.9,
        "max_tokens": 200,
        "top_p": 0.95,
        "frequency_penalty": 0.5
    },
    context={
        "user_id": "user123",
        "conversation_id": "conv456",
        "timestamp": datetime.now().isoformat()
    }
)

response = run_ai(request)
```

### 4. Embedding Generation

```python
# Generate embeddings for semantic search
request = AIRequest(
    task_type="embedding",
    prompt="Machine learning enables computers to learn from data",
    model="text-embedding-ada-002"
)

response = run_ai(request)
embedding = response.result  # List of 1536 floats
```

### 5. Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_batch(prompts: list[str]) -> list[AIResponse]:
    """Process multiple prompts in parallel."""
    
    def process_single(prompt: str) -> AIResponse:
        request = AIRequest(task_type="chat", prompt=prompt)
        return run_ai(request)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        responses = list(executor.map(process_single, prompts))
    
    return responses

prompts = [
    "Explain photosynthesis",
    "What is quantum computing?",
    "How does DNS work?"
]

results = process_batch(prompts)
```

## Error Handling

### Exception Hierarchy

```python
class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass

class ProviderUnavailableError(AIProviderError):
    """Raised when provider cannot be reached."""
    pass

class ProviderAuthenticationError(AIProviderError):
    """Raised when API key is invalid."""
    pass

class ProviderRateLimitError(AIProviderError):
    """Raised when rate limit is exceeded."""
    pass
```

### Graceful Error Recovery

```python
from app.core.ai.orchestrator import run_ai, AIRequest

def safe_ai_call(request: AIRequest, default_response: str = "Unable to generate response") -> str:
    """AI call with graceful fallback."""
    try:
        response = run_ai(request)
        
        if response.status == "success":
            return response.result
        else:
            logger.warning(f"AI call failed: {response.error}")
            return default_response
    
    except Exception as e:
        logger.error(f"Critical AI error: {e}")
        return default_response

# Usage
result = safe_ai_call(
    AIRequest(task_type="chat", prompt="Hello"),
    default_response="I'm currently unavailable"
)
```

## Performance Optimization

### Request Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=200)
def cached_ai_call(request_hash: str) -> AIResponse:
    """Cache AI responses to avoid duplicate API calls."""
    # Implementation would deserialize request from hash
    pass

def smart_ai_call(request: AIRequest) -> AIResponse:
    """Call AI with caching."""
    # Create deterministic hash
    request_str = f"{request.task_type}:{request.prompt}:{request.model}"
    request_hash = hashlib.sha256(request_str.encode()).hexdigest()
    
    return cached_ai_call(request_hash)
```

### Load Balancing

```python
import random

def load_balanced_run_ai(request: AIRequest) -> AIResponse:
    """Distribute load across available providers."""
    # Check provider health
    available_providers = []
    
    for provider in ["openai", "huggingface", "perplexity"]:
        if check_provider_health(provider):
            available_providers.append(provider)
    
    if not available_providers:
        raise RuntimeError("No providers available")
    
    # Random selection for load distribution
    request.provider = random.choice(available_providers)
    
    return run_ai(request)
```

## Testing

### Mock Orchestrator

```python
import pytest
from unittest.mock import patch
from app.core.ai.orchestrator import run_ai, AIRequest, AIResponse

@patch('app.core.ai.orchestrator._call_openai')
def test_successful_openai_call(mock_openai):
    # Mock response
    mock_openai.return_value = AIResponse(
        status="success",
        result="Test response",
        provider_used="openai",
        metadata={}
    )
    
    # Test
    request = AIRequest(task_type="chat", prompt="test")
    response = run_ai(request)
    
    assert response.status == "success"
    assert response.provider_used == "openai"
    mock_openai.assert_called_once()

@patch('app.core.ai.orchestrator._call_openai')
@patch('app.core.ai.orchestrator._call_huggingface')
def test_fallback_to_huggingface(mock_hf, mock_openai):
    # OpenAI fails, HuggingFace succeeds
    mock_openai.side_effect = RuntimeError("API error")
    mock_hf.return_value = AIResponse(
        status="success",
        result="Fallback response",
        provider_used="huggingface",
        metadata={}
    )
    
    request = AIRequest(task_type="chat", prompt="test")
    response = run_ai(request)
    
    assert response.provider_used == "huggingface"
    mock_openai.assert_called_once()
    mock_hf.assert_called_once()
```

## Migration Guide

### From Direct Provider Calls

**Before (Direct OpenAI):**
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

**After (Orchestrator):**
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
- Automatic fallback if OpenAI fails
- Governance compliance
- Consistent error handling
- Usage tracking

## References

- [OpenAI Integration](./01-openai-integration.md)
- [HuggingFace Integration](./02-huggingface-integration.md)
- [Model Providers](./model-providers.md)
- [Governance System](../architecture/governance.md)

## Related Documentation

- `src/app/core/ai/orchestrator.py` [[src/app/core/ai/orchestrator.py]] - Implementation
- `src/app/core/model_providers.py` [[src/app/core/model_providers.py]] - Provider interfaces
- `src/app/core/learning_paths.py` [[src/app/core/learning_paths.py]] - Consumer example
- `src/app/core/intelligence_engine.py` [[src/app/core/intelligence_engine.py]] - Complex consumer
