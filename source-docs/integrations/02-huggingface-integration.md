# Hugging Face API Integration

## Overview

Project-AI integrates with Hugging Face's Inference API for machine learning model access, primarily for image generation via Stable Diffusion models. Hugging Face serves as the primary fallback provider when OpenAI services are unavailable, providing resilient AI capabilities with open-source models.

## Architecture

### Integration Stack

```
Application Layer
    ↓
AI Orchestrator (fallback coordinator)
    ↓
Image Generator (HuggingFace backend)
    ↓
Hugging Face Inference API
    ↓
Stable Diffusion 2.1 Model
```

### Key Components

1. **Image Generator** (`src/app/core/image_generator.py` [[src/app/core/image_generator.py]])
   - Dual-backend support (HuggingFace + OpenAI)
   - Stable Diffusion 2.1 integration
   - Content filtering and safety checks
   - Retry logic with exponential backoff

2. **AI Orchestrator** (`src/app/core/ai/orchestrator.py` [[src/app/core/ai/orchestrator.py]])
   - Automatic fallback from OpenAI to HuggingFace
   - Provider health monitoring
   - Request routing based on availability

3. **Model Hub Access**
   - Direct API access to `stabilityai/stable-diffusion-2-1`
   - Support for community-contributed models
   - Custom model deployment via private endpoints

## Configuration

### Environment Variables

```bash
# Required for HuggingFace integration
HUGGINGFACE_API_KEY=hf_...              # Get from https://huggingface.co/settings/tokens

# Optional configuration
IMAGE_API_MAX_RETRIES=3                 # Retry attempts for transient failures
IMAGE_API_BACKOFF_FACTOR=0.8            # Exponential backoff multiplier
HUGGINGFACE_ENDPOINT=https://api-inference.huggingface.co
```

### Setup Instructions

1. **Create Hugging Face Account**
   ```bash
   # Visit https://huggingface.co/join
   # Verify email address
   ```

2. **Generate Access Token**
   ```bash
   # Navigate to https://huggingface.co/settings/tokens
   # Create new token with "Read" permissions
   # Copy token to .env file as HUGGINGFACE_API_KEY
   ```

3. **Install Dependencies**
   ```bash
   pip install requests>=2.31.0
   pip install pillow>=10.0.0  # For image processing
   ```

4. **Verify Setup**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("HUGGINGFACE_API_KEY")
   assert api_key and api_key.startswith("hf_"), "Invalid HuggingFace API key"
   ```

## Usage Patterns

### 1. Image Generation with Stable Diffusion

```python
from app.core.image_generator import ImageGenerator, Backend, StylePreset

# Initialize generator
generator = ImageGenerator()

# Generate image with HuggingFace backend
image_path, metadata = generator.generate(
    prompt="A serene mountain landscape at sunset, photorealistic",
    style=StylePreset.PHOTOREALISTIC,
    size="512x512",  # Stable Diffusion 2.1 optimal resolution
    backend=Backend.HUGGINGFACE
)

print(f"Image saved to: {image_path}")
print(f"Model: {metadata['model']}")
print(f"Generation time: {metadata['generation_time']}s")
```

### 2. Direct API Call

```python
import requests
import os
from PIL import Image
from io import BytesIO

def generate_with_huggingface_direct(prompt: str) -> Image.Image:
    """Direct HuggingFace API call for image generation."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 50,
            "guidance_scale": 7.5,
            "negative_prompt": "blurry, low quality, distorted"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    
    # Response is binary image data
    image = Image.open(BytesIO(response.content))
    return image

# Usage
image = generate_with_huggingface_direct(
    "A futuristic cityscape at night with neon lights"
)
image.save("output.png")
```

### 3. Fallback Integration via Orchestrator

```python
from app.core.ai.orchestrator import run_ai, AIRequest

# Request will automatically fall back to HuggingFace if OpenAI fails
request = AIRequest(
    task_type="image",
    prompt="A majestic eagle soaring over mountains",
    model="stabilityai/stable-diffusion-2-1",
    config={
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "width": 768,
        "height": 768
    }
)

# Orchestrator tries OpenAI first, falls back to HuggingFace
response = run_ai(request)

if response.provider_used == "huggingface":
    print("Successfully generated via HuggingFace fallback")
    print(f"Image URL: {response.result}")
```

### 4. Custom Negative Prompts

```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()

# Advanced generation with custom negative prompts
image_path, metadata = generator.generate_with_huggingface(
    prompt="A photorealistic portrait of a wise old wizard",
    negative_prompt=(
        "cartoon, anime, sketch, drawing, illustration, "
        "blurry, low quality, distorted, deformed, "
        "duplicate, watermark, text"
    ),
    num_inference_steps=75,  # Higher = better quality
    guidance_scale=8.0,       # Higher = more prompt adherence
    width=768,
    height=768
)

print(f"Generated high-quality image: {image_path}")
```

### 5. Batch Generation

```python
from concurrent.futures import ThreadPoolExecutor
from app.core.image_generator import ImageGenerator

def generate_batch(prompts: list[str], backend=Backend.HUGGINGFACE) -> list[str]:
    """Generate multiple images in parallel."""
    generator = ImageGenerator()
    
    def generate_single(prompt: str) -> str:
        try:
            image_path, _ = generator.generate(
                prompt=prompt,
                backend=backend,
                size="512x512"
            )
            return image_path
        except Exception as e:
            print(f"Failed to generate '{prompt}': {e}")
            return None
    
    # Parallel generation (limit workers to avoid rate limits)
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(generate_single, prompts))
    
    return [r for r in results if r is not None]

# Usage
prompts = [
    "A serene forest scene",
    "A bustling city street",
    "A calm ocean sunset"
]

image_paths = generate_batch(prompts)
print(f"Generated {len(image_paths)} images")
```

## Supported Models

### Image Generation Models

| Model | Repository | Resolution | Use Case |
|-------|-----------|-----------|----------|
| Stable Diffusion 2.1 | `stabilityai/stable-diffusion-2-1` | 512×512, 768×768 | Default, photorealistic |
| Stable Diffusion XL | `stabilityai/stable-diffusion-xl-base-1.0` | 1024×1024 | High-resolution generation |
| Dreamlike Photoreal | `dreamlike-art/dreamlike-photoreal-2.0` | 512×512 | Photography style |
| Openjourney | `prompthero/openjourney` | 512×512 | Midjourney-style art |

### Configuration for Different Models

```python
model_configs = {
    "sd-2.1": {
        "model": "stabilityai/stable-diffusion-2-1",
        "optimal_size": (768, 768),
        "inference_steps": 50,
        "guidance_scale": 7.5
    },
    "sdxl": {
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "optimal_size": (1024, 1024),
        "inference_steps": 30,
        "guidance_scale": 5.0
    },
    "photoreal": {
        "model": "dreamlike-art/dreamlike-photoreal-2.0",
        "optimal_size": (512, 512),
        "inference_steps": 40,
        "guidance_scale": 8.0
    }
}

# Usage
def generate_with_model(prompt: str, model_name: str) -> str:
    config = model_configs[model_name]
    
    url = f"https://api-inference.huggingface.co/models/{config['model']}"
    # ... API call with config parameters
```

## Content Safety

### Built-in Safety Features

```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()

# Content filter checks before generation
is_safe, reason = generator.check_content_filter(
    "Generate a family-friendly image of a cat"
)

if not is_safe:
    raise ValueError(f"Content filter triggered: {reason}")

# Automatic negative prompts for safety
safe_negative_prompt = generator._get_safety_negative_prompt()
# Returns: "nsfw, explicit, violence, gore, ..."
```

### Blocked Keywords

The system maintains a blocklist for harmful content:

```python
BLOCKED_KEYWORDS = [
    "nsfw", "explicit", "violence", "gore", "weapon",
    "drug", "hate", "racist", "nude", "sexual",
    "blood", "death", "suicide", "self-harm", "terrorism"
]

def content_filter(prompt: str) -> tuple[bool, str]:
    """Check prompt against blocked keywords."""
    prompt_lower = prompt.lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt_lower:
            return False, f"Blocked keyword: {keyword}"
    
    return True, ""
```

### Custom Safety Layers

```python
from app.core.image_generator import ImageGenerator

class SafeImageGenerator(ImageGenerator):
    """Extended generator with additional safety checks."""
    
    def __init__(self):
        super().__init__()
        self.audit_log = []
    
    def generate(self, prompt: str, **kwargs):
        """Override with audit logging."""
        # Pre-generation audit
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "user": kwargs.get("user_id", "anonymous")
        })
        
        # Content moderation via external API (optional)
        if not self._external_moderation_check(prompt):
            raise ValueError("Content moderation failed")
        
        # Call parent implementation
        return super().generate(prompt, **kwargs)
    
    def _external_moderation_check(self, prompt: str) -> bool:
        """Optional: Use external moderation API."""
        # Integration with content moderation service
        return True
```

## Error Handling

### Retry Logic with Backoff

```python
from app.core.image_generator import _request_with_retries
import requests

# Built-in retry for transient errors
response = _request_with_retries(
    method="POST",
    url="https://api-inference.huggingface.co/models/...",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"inputs": prompt},
    timeout=60
)

# Handles:
# - 429 Too Many Requests (rate limiting)
# - 502 Bad Gateway (temporary server issues)
# - 503 Service Unavailable (model loading)
# - 504 Gateway Timeout (slow inference)
```

### Common Error Scenarios

| Error Code | Cause | Solution |
|-----------|-------|----------|
| `401 Unauthorized` | Invalid API key | Verify `HUGGINGFACE_API_KEY` |
| `429 Rate Limited` | Too many requests | Implement rate limiting, upgrade plan |
| `500 Internal Error` | Model inference failure | Retry or switch to different model |
| `503 Model Loading` | Cold start delay | Wait 20-30 seconds, automatic retry |

### Graceful Degradation

```python
from app.core.ai.orchestrator import run_ai, AIRequest

def generate_image_with_fallback(prompt: str) -> str:
    """Try HuggingFace, fall back to cached results."""
    try:
        # Primary: HuggingFace
        request = AIRequest(
            task_type="image",
            prompt=prompt,
            provider="huggingface"
        )
        response = run_ai(request)
        
        if response.status == "success":
            return response.result
    
    except Exception as e:
        logger.warning(f"HuggingFace generation failed: {e}")
    
    # Fallback: Return placeholder or cached image
    return get_cached_image(prompt) or generate_placeholder_image()

def get_cached_image(prompt: str) -> str | None:
    """Retrieve previously generated image for similar prompt."""
    # Implement semantic cache lookup
    pass

def generate_placeholder_image() -> str:
    """Generate simple placeholder when all services fail."""
    # Create solid color or pattern image
    pass
```

## Performance Optimization

### Model Cold Start Mitigation

```python
import requests
import time

def warmup_model(model_id: str = "stabilityai/stable-diffusion-2-1"):
    """Send warmup request to load model into memory."""
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    # Simple prompt to trigger model loading
    payload = {"inputs": "warmup test"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        # Model is now loaded and cached
        logger.info(f"Model {model_id} warmed up successfully")
    except requests.Timeout:
        logger.warning(f"Model {model_id} warmup timed out (may still be loading)")

# Call during application startup
warmup_model()
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=50)
def cached_generation(prompt_hash: str, model: str) -> str:
    """Cache generated images to avoid duplicate API calls."""
    # Actual generation logic
    pass

def generate_with_cache(prompt: str, model: str) -> str:
    """Generate image with caching."""
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    return cached_generation(prompt_hash, model)
```

### Parallel Generation

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def parallel_generate(prompts: list[str], max_workers: int = 3) -> list[bytes]:
    """Generate multiple images in parallel with rate limiting."""
    
    def generate_single(prompt: str) -> bytes:
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        return response.content
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(generate_single, prompts))
    
    return results
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from app.core.image_generator import ImageGenerator, Backend

class TestHuggingFaceIntegration:
    @patch('requests.post')
    def test_generate_with_huggingface(self, mock_post):
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n...'  # PNG header
        mock_post.return_value = mock_response
        
        # Test generation
        generator = ImageGenerator()
        image_path, metadata = generator.generate(
            prompt="Test prompt",
            backend=Backend.HUGGINGFACE
        )
        
        assert image_path.endswith('.png')
        assert metadata['backend'] == 'huggingface'
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_retry_on_503(self, mock_post):
        # Mock 503 response then success
        mock_post.side_effect = [
            MagicMock(status_code=503),
            MagicMock(status_code=200, content=b'...')
        ]
        
        generator = ImageGenerator()
        image_path, _ = generator.generate(
            prompt="Test",
            backend=Backend.HUGGINGFACE
        )
        
        assert mock_post.call_count == 2
```

### Integration Tests

```python
import pytest
import os
from app.core.image_generator import ImageGenerator, Backend

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("HUGGINGFACE_API_KEY"), reason="API key not set")
def test_huggingface_real_generation():
    """Test actual HuggingFace API call (requires valid key)."""
    generator = ImageGenerator()
    
    image_path, metadata = generator.generate(
        prompt="A simple test image of a red apple",
        backend=Backend.HUGGINGFACE,
        size="256x256"  # Small size for fast test
    )
    
    assert os.path.exists(image_path)
    assert metadata['backend'] == 'huggingface'
    assert metadata['model'] == 'stabilityai/stable-diffusion-2-1'
    
    # Cleanup
    os.remove(image_path)
```

## Monitoring

### Usage Tracking

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HuggingFaceUsageTracker:
    def __init__(self):
        self.usage_log = []
    
    def log_generation(self, model: str, prompt_tokens: int, success: bool):
        """Log HuggingFace API usage."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "success": success,
            "cost": self._calculate_cost(model, prompt_tokens)
        }
        self.usage_log.append(entry)
        logger.info(f"HuggingFace usage: {entry}")
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Estimate cost (HuggingFace API is free for basic usage)."""
        return 0.0  # Free tier

# Usage
tracker = HuggingFaceUsageTracker()
tracker.log_generation("stabilityai/stable-diffusion-2-1", 77, True)
```

### Health Monitoring

```python
import requests

def check_huggingface_health() -> dict:
    """Verify HuggingFace API connectivity and model status."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        return {"status": "unavailable", "reason": "API key not configured"}
    
    try:
        # Check model availability
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {"status": "healthy", "model_loaded": True}
        elif response.status_code == 503:
            return {"status": "loading", "model_loaded": False}
        else:
            return {"status": "error", "code": response.status_code}
    
    except Exception as e:
        return {"status": "error", "reason": str(e)}
```

## Migration Guide

### From OpenAI DALL-E to Stable Diffusion

**OpenAI DALL-E:**
```python
from openai import OpenAI

client = OpenAI()
response = client.images.generate(
    model="dall-e-3",
    prompt="A sunset over mountains",
    size="1024x1024"
)
image_url = response.data[0].url
```

**HuggingFace Stable Diffusion:**
```python
from app.core.image_generator import ImageGenerator, Backend

generator = ImageGenerator()
image_path, metadata = generator.generate(
    prompt="A sunset over mountains",
    backend=Backend.HUGGINGFACE,
    size="768x768"  # Optimal for SD 2.1
)
```

**Key Differences:**
- HuggingFace returns binary image data, not URLs
- Resolution limits differ (SD 2.1: 768×768 optimal, DALL-E 3: 1024×1024)
- Style handling differs (SD uses negative prompts, DALL-E uses style parameter)

## Troubleshooting

### Model Loading Delays

```python
# Problem: 503 Service Unavailable on first request
# Cause: Model cold start (can take 20-60 seconds)

# Solution: Implement retry with extended timeout
import time

def generate_with_cold_start_handling(prompt: str) -> bytes:
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json={"inputs": prompt}, timeout=60)
            
            if response.status_code == 503:
                wait_time = 20 * (attempt + 1)  # Increasing backoff
                logger.info(f"Model loading, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response.content
        
        except requests.Timeout:
            if attempt < max_retries - 1:
                continue
            raise
    
    raise RuntimeError("Model failed to load after retries")
```

### Rate Limit Management

```python
from datetime import datetime, timedelta
from collections import deque

class RateLimiter:
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        """Rate limiter for HuggingFace API (30 requests/minute on free tier)."""
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window)
        self.requests = deque()
    
    def can_make_request(self) -> bool:
        """Check if request can be made without hitting rate limit."""
        now = datetime.now()
        
        # Remove old requests outside time window
        while self.requests and now - self.requests[0] > self.time_window:
            self.requests.popleft()
        
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record a new request."""
        self.requests.append(datetime.now())

# Usage
limiter = RateLimiter()

if limiter.can_make_request():
    response = generate_image(prompt)
    limiter.record_request()
else:
    logger.warning("Rate limit reached, delaying request")
    time.sleep(60)
```

## References

- **HuggingFace Inference API**: https://huggingface.co/docs/api-inference
- **Stable Diffusion Models**: https://huggingface.co/stabilityai
- **API Pricing**: https://huggingface.co/pricing
- **Model Hub**: https://huggingface.co/models

## Related Documentation

- **03 Huggingface Integration**: [[relationships\integrations\03-huggingface-integration.md]]


- **02 Github Integration**: [[relationships\integrations\02-github-integration.md]]


- [01-openai-integration.md](./01-openai-integration.md) - Primary AI provider
- [03-ai-orchestrator.md](./03-ai-orchestrator.md) - Fallback coordination
- [04-image-generation.md](./04-image-generation.md) - Multi-backend image generation system
- [../architecture/ai-systems.md](../architecture/ai-systems.md) - AI systems overview
