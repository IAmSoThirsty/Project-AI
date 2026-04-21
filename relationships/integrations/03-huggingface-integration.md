# Hugging Face Integration Relationship Map

**Status**: 🟢 Production | **Type**: External AI Service  
**Priority**: P1 Critical (Fallback Provider) | **Governance**: Orchestrator-Governed

---


## Navigation

**Location**: `relationships\integrations\03-huggingface-integration.md`

**Parent**: [[relationships\integrations\README.md]]


## External Service Dependencies

### Primary Endpoint
- **Service**: Hugging Face Inference API (https://api-inference.huggingface.co)
- **Authentication**: Bearer Token (HUGGINGFACE_API_KEY)
- **Protocol**: REST/HTTP
- **Rate Limits**: Free tier = 1,000 requests/month, Pro = 50,000 requests/month

### Models Used
1. **stabilityai/stable-diffusion-2-1**: Image generation (primary)
2. **sentence-transformers/all-MiniLM-L6-v2**: Text embeddings (fallback)
3. **facebook/bart-large-cnn**: Text summarization (fallback)
4. **mistralai/Mistral-7B-Instruct-v0.1**: Chat completions (fallback)

---

## Internal Relationships

### Core Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATOR (Hub)                     │
│              src/app/core/ai/orchestrator.py                 │
│         ┌────────────────────────────────────┐              │
│         │ Fallback Provider (rank 2)         │              │
│         └────────────────────────────────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ HF Inference  │ │ Image Gen     │ │ Text Models   │
│ API Client    │ │ (SD 2.1)      │ │ (Mistral 7B)  │
└───────────────┘ └───────────────┘ └───────────────┘
```

### Dependency Graph

**PRIMARY USE CASE**: Image Generation (Stable Diffusion 2.1)

1. **Image Generator** (`src/app/core/image_generator.py` [[src/app/core/image_generator.py]])
   - Purpose: Generate images via Stable Diffusion 2.1
   - Backend: `huggingface` (dual-backend with OpenAI DALL-E)
   - Flow: Prompt → ImageGenerator → HF API → Binary image data

**FALLBACK USE CASE**: When OpenAI unavailable

2. **Intelligence Engine** (`src/app/core/intelligence_engine.py` [[src/app/core/intelligence_engine.py]])
   - Purpose: Fallback chat completions
   - Models: Mistral-7B-Instruct
   - Flow: Query → Orchestrator → [OpenAI fails] → HuggingFace

3. **RAG System** (`src/app/core/rag_system.py` [[src/app/core/rag_system.py]])
   - Purpose: Fallback embeddings
   - Models: sentence-transformers/all-MiniLM-L6-v2
   - Flow: Text → RAG → [OpenAI fails] → HuggingFace embeddings

---

## API Contracts

### Stable Diffusion Image Generation

```python
# REQUEST
POST https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1
Headers: {
    "Authorization": "Bearer hf_xxxxxxxxxxxxx",
    "Content-Type": "application/json"
}
Body: {
    "inputs": "A photorealistic cyberpunk cityscape at night",
    "parameters": {
        "negative_prompt": "blurry, low quality, distorted",
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    }
}

# RESPONSE
Content-Type: image/png
Body: <binary PNG data>
```

### Chat Completion (Mistral-7B)

```python
# REQUEST
POST https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1
Headers: {
    "Authorization": "Bearer hf_xxxxxxxxxxxxx"
}
Body: {
    "inputs": "<s>[INST] User question here [/INST]",
    "parameters": {
        "max_new_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.95
    }
}

# RESPONSE
{
    "generated_text": "Assistant response here..."
}
```

### Text Embeddings

```python
# REQUEST
POST https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2
Headers: {
    "Authorization": "Bearer hf_xxxxxxxxxxxxx"
}
Body: {
    "inputs": "Text to embed"
}

# RESPONSE
[
    [0.012, -0.045, 0.089, ...]  # 384 dimensions
]
```

---

## Integration Patterns

### Pattern 1: Image Generation (Primary)

**Implementation**: `ImageGenerator.generate_with_huggingface()`

```python
def generate_with_huggingface(self, prompt, style="photorealistic", size="512x512"):
    """Generate image via Hugging Face Stable Diffusion 2.1."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        return None, "HUGGINGFACE_API_KEY not set"
    
    # Build negative prompt for quality
    negative_prompt = "blurry, low quality, distorted, deformed"
    
    # Apply style preset
    if style in STYLE_PRESETS:
        prompt = f"{STYLE_PRESETS[style]} {prompt}"
    
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    width, height = map(int, size.split("x"))
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "width": width,
            "height": height
        }
    }
    
    response = _request_with_retries("post", url, headers=headers, json=payload)
    
    if response.status_code == 200:
        # Save image
        filename = sanitize_filename(f"{prompt[:30]}_{int(time.time())}.png")
        filepath = safe_path_join(self.output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(response.content)
        
        return filepath, "Image generated successfully"
    else:
        return None, f"HF API error: {response.status_code}"
```

### Pattern 2: Fallback Chat (Orchestrator-Driven)

**Implementation**: `ai/orchestrator.py._call_huggingface()`

```python
def _call_huggingface(request: AIRequest) -> AIResponse:
    """Call Hugging Face Inference API."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise RuntimeError("HUGGINGFACE_API_KEY not set")
    
    model = request.model or "mistralai/Mistral-7B-Instruct-v0.1"
    url = f"https://api-inference.huggingface.co/models/{model}"
    
    # Format prompt for Mistral instruction format
    formatted_prompt = f"<s>[INST] {request.prompt} [/INST]"
    
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.95
        }
    }
    
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        return AIResponse(
            status="success",
            result=data.get("generated_text", ""),
            provider_used="huggingface",
            metadata={"model": model}
        )
    else:
        raise RuntimeError(f"HF API error: {response.status_code}")
```

---

## Configuration

### Environment Variables

```bash
# REQUIRED
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx  # Get from https://huggingface.co/settings/tokens

# OPTIONAL
HF_DEFAULT_IMAGE_MODEL=stabilityai/stable-diffusion-2-1
HF_DEFAULT_CHAT_MODEL=mistralai/Mistral-7B-Instruct-v0.1
HF_DEFAULT_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_MAX_RETRIES=3
HF_TIMEOUT=60
```

### Token Generation

1. Sign up at https://huggingface.co
2. Go to https://huggingface.co/settings/tokens
3. Click "New token"
4. Select "Read" scope
5. Copy token to `.env` [[.env]] file

---

## Error Handling

### Common Errors

1. **503 Service Unavailable**: Model loading (cold start)
   - **Mitigation**: Retry after 20 seconds, model warm-up time

2. **401 Unauthorized**: Invalid API key
   - **Mitigation**: Validate key on startup, log error

3. **400 Bad Request**: Invalid parameters
   - **Mitigation**: Validate prompt length, image dimensions

4. **429 Rate Limit**: Quota exceeded
   - **Mitigation**: Fallback to local model, log warning

### Retry Logic

```python
# Cold start handling (unique to HuggingFace)
def _request_with_cold_start_retry(url, headers, payload):
    """Handle HF model cold starts with extended retry."""
    for attempt in range(3):
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 503:
            # Model loading, wait and retry
            logger.warning(f"Model loading (attempt {attempt+1}/3)")
            time.sleep(20)  # Wait for model to load
            continue
        
        return response
    
    raise RuntimeError("Model failed to load after 3 attempts")
```

---

## Security

### API Key Management

- **Storage**: Environment variable (.env file)
- **Rotation**: Manual via HuggingFace dashboard
- **Scoping**: Use "Read" scope (not "Write")

### Content Filtering

```python
# Same as OpenAI (shared filter in image_generator.py)
BLOCKED_KEYWORDS = [
    "violence", "gore", "sexual", "nsfw", "explicit",
    "weapon", "drug", "illegal", "hate", "racist"
]
```

---

## Performance

### Latency Benchmarks

| Operation | Model | Avg Latency | P95 Latency | Notes |
|-----------|-------|-------------|-------------|-------|
| Image Gen (SD 2.1) | stable-diffusion-2-1 | 45s | 90s | Cold start: +20s |
| Chat | Mistral-7B | 5s | 10s | Cold start: +15s |
| Embeddings | all-MiniLM-L6-v2 | 0.8s | 1.5s | Cold start: +5s |

### Cold Start Mitigation

**Problem**: First request to a model takes 15-60s (model loading)

**Solutions**:
1. **Pre-warm models**: Send dummy requests during startup
2. **Paid tier**: Use HuggingFace Pro (models stay warm)
3. **Local fallback**: Use local Stable Diffusion for instant generation

---

## Testing

### Integration Tests

```python
# tests/test_huggingface_integration.py
def test_image_generation():
    generator = ImageGenerator(backend="huggingface")
    filepath, message = generator.generate(
        prompt="A cute robot",
        style="digital_art",
        size="512x512"
    )
    
    assert filepath is not None
    assert os.path.exists(filepath)
    assert message == "Image generated successfully"

def test_fallback_to_huggingface():
    # Mock OpenAI failure
    with patch("openai.OpenAI") as mock:
        mock.side_effect = Exception("OpenAI down")
        
        request = AIRequest(task_type="chat", prompt="Test")
        response = run_ai(request)
        
        assert response.provider_used == "huggingface"
        assert response.status == "fallback"
```

---

## Monitoring

### Metrics

- **Cold Start Rate**: % of requests with >10s latency
- **Fallback Usage**: Requests to HF vs. OpenAI
- **Error Rate**: Failed requests / total requests
- **Cost**: API calls vs. quota limit

### Alerts

- **High Cold Start Rate**: >50% → Consider HF Pro
- **Quota Low**: <100 requests remaining
- **High Error Rate**: >10% failures

---

## Cost Analysis

### Free Tier
- **Limit**: 1,000 requests/month
- **Cost**: $0
- **Cold starts**: Frequent

### Pro Tier
- **Limit**: 50,000 requests/month
- **Cost**: $9/month
- **Cold starts**: Rare
- **ROI**: Worth it if >50 image generations/month

---

## Future Enhancements

### Phase 1: Local Stable Diffusion ⏳ PLANNED
- Add local SD 2.1 via `diffusers` library
- Instant generation (no cold starts)
- Zero API costs

### Phase 2: Model Selection 🔮 FUTURE
- Support multiple SD models (SD XL, SD 3)
- Dynamic model selection based on prompt
- Quality vs. speed trade-offs

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: Primary provider
- **[10-image-generator.md](10-image-generator.md)**: Dual-backend architecture
- **[08-intelligence-engine.md](08-intelligence-engine.md)**: Fallback chat

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
