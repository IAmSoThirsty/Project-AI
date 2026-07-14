# Ollama Local Model Serving Integration

Optional integration for running local LLMs via Ollama for CCMA augmentation, embedding generation, and local reasoning without cloud dependency.

## Setup

### 1. Enable Ollama in Compose

```yaml
# Add to compose.yaml
ollama:
  image: ollama/ollama:latest
  container_name: project-ai-ollama
  ports:
    - "127.0.0.1:11434:11434"
  volumes:
    - ollama-models:/root/.ollama
  environment:
    OLLAMA_NUM_GPU: 1  # Enable GPU if available
    OLLAMA_NUM_PARALLEL: 2
  networks:
    - services
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://127.0.0.1:11434/api/tags"]
    interval: 30s
    timeout: 10s
    retries: 3

volumes:
  ollama-models:
    driver: local
```

### 2. Pull Models

```bash
# Pull embeddings model (for vector storage)
ollama pull nomic-embed-text  # 274M

# Pull reasoning model (for internal deliberation)
ollama pull mistral  # 4.1B quantized

# Pull code model (for capability validation)
ollama pull codellama:7b  # 3.9B quantized

# Pull summarization model (for audit summaries)
ollama pull neural-chat:7b  # 4.1B quantized
```

### 3. Configure Project-AI to Use Ollama

```python
# packages/api/config.py
OLLAMA_ENABLED = os.getenv("OLLAMA_ENABLED", "true").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODELS = {
    "embeddings": "nomic-embed-text",
    "reasoning": "mistral",
    "code_validation": "codellama:7b",
    "summarization": "neural-chat:7b"
}
OLLAMA_DEFAULT_TIMEOUT = 60  # seconds
```

## Usage in CCMA

### Memory Embeddings

```python
# packages/memory/embeddings.py
async def embed_memory(content: str) -> list[float]:
    """Generate embeddings for memory content using local Ollama."""
    if not OLLAMA_ENABLED:
        return None  # Fall back to no embeddings
    
    response = await httpx.post(
        f"{OLLAMA_BASE_URL}/api/embeddings",
        json={
            "model": OLLAMA_MODELS["embeddings"],
            "prompt": content
        },
        timeout=OLLAMA_DEFAULT_TIMEOUT
    )
    return response.json()["embedding"]
```

### Governance Reasoning

```python
# packages/governance/reasoning.py
async def deliberate_with_local_llm(matter: str, evidence: str) -> str:
    """Use local LLM for constitutional reasoning."""
    if not OLLAMA_ENABLED:
        return None
    
    prompt = f"""
    Constitutional Matter: {matter}
    
    Evidence:
    {evidence}
    
    Constitutional Analysis:
    """
    
    response = await httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODELS["reasoning"],
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3  # Low temp for consistency
        },
        timeout=OLLAMA_DEFAULT_TIMEOUT
    )
    return response.json()["response"]
```

### Audit Summarization

```python
# packages/audit/summarization.py
async def summarize_audit_chain(records: list[dict]) -> str:
    """Generate human-readable audit summary."""
    if not OLLAMA_ENABLED:
        return None
    
    events = "\n".join([f"- {r['event_type']}: {r['description']}" for r in records])
    
    prompt = f"""
    Audit Trail Events:
    {events}
    
    Summary (< 100 words):
    """
    
    response = await httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODELS["summarization"],
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

## Performance Tuning

### For CPU-only Deployment

```yaml
ollama:
  environment:
    OLLAMA_NUM_GPU: 0  # CPU only
    OLLAMA_NUM_PARALLEL: 4
    OLLAMA_NUM_THREAD: 8
```

Recommended models for CPU (< 4GB memory):
- Embeddings: `nomic-embed-text` (274M)
- Reasoning: `phi:2b` (1.6B)
- Summarization: `tinyllama` (637M)

### For GPU Deployment

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    OLLAMA_NUM_GPU: 1
```

Recommended models for GPU (8GB+ VRAM):
- Embeddings: `nomic-embed-text` (274M)
- Reasoning: `mistral` (4.1B)
- Summarization: `neural-chat:7b` (4.1B)

## Privacy Benefits

- ✅ All embeddings generated locally (no data to external APIs)
- ✅ All reasoning stays in-process (no cloud dependency)
- ✅ Constitutional governance runs completely offline
- ✅ Audit chains never transmitted to third parties
- ✅ Memory system operates independently

## When to Use

✅ **Recommended for:**
- Private deployments
- Sensitive workloads
- Offline environments
- Compliance-required installations
- Privacy-focused users

❌ **Not recommended for:**
- High-throughput scenarios (use cloud APIs)
- Very limited hardware (memory constraints)
- Real-time latency requirements (< 500ms)

## Fallback Chain

If Ollama is unavailable:

1. **Embeddings**: Skip (use text search only)
2. **Reasoning**: Use simple heuristics (faster, less accurate)
3. **Summarization**: Return raw event list (human-readable but verbose)
4. **Code Validation**: Use syntax checking only (no semantic analysis)

All operations continue, just with reduced capability.

## Monitoring

```yaml
# Prometheus metrics for Ollama
ollama_request_duration_seconds:
  help: "Request duration to Ollama API"
  
ollama_model_inference_tokens_per_second:
  help: "Throughput by model"
  
ollama_model_latency_seconds:
  help: "Inference latency by model"

ollama_available_memory_bytes:
  help: "Free memory in Ollama process"
```

## Cost Comparison

| Scenario | Cloud API | Local Ollama |
|----------|-----------|--------------|
| 1M embeddings/month | $0.02 | $0 (hardware) |
| 100K reasoning calls | $20 | $0 |
| Privacy compliance | ❌ | ✅ |
| Offline capability | ❌ | ✅ |
| Latency (typical) | 200ms | 500-2000ms |
