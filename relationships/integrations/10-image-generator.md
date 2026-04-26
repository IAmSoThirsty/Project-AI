# Image Generator Integration Relationship Map

**Status**: 🟢 Production | **Type**: AI-Powered Feature  
**Priority**: P1 Feature | **Governance**: Content Filtered

---


## Navigation

**Location**: `relationships\integrations\10-image-generator.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

Dual-backend image generation system supporting:
1. **Hugging Face Stable Diffusion 2.1** (primary, free)
2. **OpenAI DALL-E 3** (secondary, paid)

Includes content filtering, style presets, and secure file storage.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  IMAGE GENERATOR                             │
│         src/app/core/image_generator.py                      │
│  ┌──────────────────────────────────────────┐              │
│  │ Content Filter (15 blocked keywords)     │              │
│  │ Style Presets (10 styles)                │              │
│  │ Dual Backend Support                     │              │
│  └──────────────────────────────────────────┘              │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌───────────────┐  ┌───────────────┐
│ HuggingFace   │  │ OpenAI        │
│ Stable        │  │ DALL-E 3      │
│ Diffusion 2.1 │  │               │
└───────────────┘  └───────────────┘
        │                 │
        ▼                 ▼
┌─────────────────────────────────┐
│   Output: data/images/*.png     │
│   Metadata: Generation history  │
└─────────────────────────────────┘
```

### GUI Layer

```
┌─────────────────────────────────────────────────────────────┐
│         IMAGE GENERATION INTERFACE                           │
│         src/app/gui/image_generation.py                      │
│  ┌───────────────────┐  ┌───────────────────┐              │
│  │ Left Panel        │  │ Right Panel       │              │
│  │ (Tron-themed)     │  │ (Image Display)   │              │
│  │ - Prompt input    │  │ - Generated image │              │
│  │ - Style selector  │  │ - Zoom controls   │              │
│  │ - Size selector   │  │ - Save/Copy       │              │
│  │ - Backend choice  │  │ - Metadata        │              │
│  └───────────────────┘  └───────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Functionality

### Generate Image

**Method**: `generate(prompt, style="photorealistic", size="512x512", backend="huggingface")`

**Backends**:
1. **HuggingFace** (`generate_with_huggingface()`): Free, 45-90s latency, cold start issues
2. **OpenAI** (`generate_with_openai()`): Paid ($0.04/image), 25-45s latency, reliable

**Flow**:
```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator(backend="huggingface")

# Generate image
filepath, message = generator.generate(
    prompt="A cyberpunk cityscape at night with neon lights",
    style="digital_art",
    size="512x512"
)

if filepath:
    print(f"Image saved to: {filepath}")
else:
    print(f"Error: {message}")
```

---

## Content Filtering

### Blocked Keywords (15 total)

```python
BLOCKED_KEYWORDS = [
    "violence", "gore", "blood", "weapon", "gun",
    "sexual", "nsfw", "explicit", "nude",
    "drug", "illegal", "hate", "racist", "terrorist", "bomb"
]
```

### Filter Implementation

```python
def check_content_filter(self, prompt: str) -> tuple[bool, str]:
    """Check if prompt passes content filter."""
    prompt_lower = prompt.lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt_lower:
            logger.warning(f"Content filter blocked: {keyword}")
            return False, f"Content blocked: {keyword}"
    
    return True, "OK"
```

### Safety Negative Prompts

```python
# Automatically added to all Stable Diffusion prompts
SAFETY_NEGATIVE_PROMPT = (
    "violence, gore, blood, weapon, gun, sexual, nsfw, explicit, nude, "
    "drug, illegal, hate, racist, blurry, low quality, distorted, deformed"
)
```

---

## Style Presets

### Available Styles (10)

```python
STYLE_PRESETS = {
    "photorealistic": "photorealistic, ultra detailed, high resolution, 8K",
    "digital_art": "digital art, concept art, trending on artstation",
    "oil_painting": "oil painting, classical art, impressionist style",
    "watercolor": "watercolor painting, soft colors, artistic",
    "anime": "anime style, manga art, vibrant colors",
    "sketch": "pencil sketch, hand drawn, black and white",
    "abstract": "abstract art, geometric shapes, modern art",
    "cyberpunk": "cyberpunk style, neon lights, futuristic city",
    "fantasy": "fantasy art, magical, ethereal, mystical",
    "minimalist": "minimalist design, simple, clean, monochrome"
}
```

### Usage

```python
# Style is prepended to prompt
prompt = "A cute robot"
style = "cyberpunk"

# Effective prompt sent to model:
# "cyberpunk style, neon lights, futuristic city A cute robot"
```

---

## Backend APIs

### Hugging Face Stable Diffusion 2.1

**Endpoint**: `POST https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1`

**Request**:
```python
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}
payload = {
    "inputs": prompt,
    "parameters": {
        "negative_prompt": SAFETY_NEGATIVE_PROMPT,
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=60)
```

**Response**: Binary PNG image data

**Error Handling**:
- **503 Service Unavailable**: Model loading (cold start), retry after 20s
- **401 Unauthorized**: Invalid API key
- **400 Bad Request**: Invalid parameters

### OpenAI DALL-E 3

**Endpoint**: `POST https://api.openai.com/v1/images/generations`

**Request**:
```python
client = openai.OpenAI(api_key=OPENAI_API_KEY)

response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",  # or "1792x1024", "1024x1792"
    quality="standard",  # or "hd"
    n=1
)

image_url = response.data[0].url
```

**Response**: URL to generated image (expires in 1 hour)

**Cost**: $0.04 per image (standard), $0.08 per image (HD)

---

## File Storage

### Output Directory

**Location**: `data/images/` (default)

**Filename Format**: `{sanitized_prompt}_{timestamp}.png`

**Example**: `cyberpunk_cityscape_1706270400.png`

### Secure Storage

```python
from app.security.path_security import safe_path_join, sanitize_filename

# Prevent path traversal
filename = sanitize_filename(f"{prompt[:30]}_{int(time.time())}.png")
filepath = safe_path_join(self.output_dir, filename)

# Save image
with open(filepath, "wb") as f:
    f.write(image_data)
```

### Generation History

**File**: `data/images/history.json`

**Schema**:
```json
{
    "generations": [
        {
            "timestamp": "2025-01-26T12:00:00Z",
            "prompt": "A cyberpunk cityscape",
            "style": "digital_art",
            "size": "512x512",
            "backend": "huggingface",
            "filepath": "data/images/cyberpunk_cityscape_1706270400.png",
            "success": true
        }
    ]
}
```

---

## GUI Integration

### Image Generation Interface

**Components**:

**Left Panel** (`ImageGenerationLeftPanel`):
- Prompt text area (multi-line)
- Style dropdown (10 presets)
- Size dropdown ("512x512", "768x768", "1024x1024")
- Backend choice (HuggingFace/OpenAI)
- Generate button

**Right Panel** (`ImageGenerationRightPanel`):
- Image display (QLabel with QPixmap)
- Zoom controls (+/- buttons)
- Metadata display (prompt, style, size, backend)
- Save button (save to custom location)
- Copy button (copy to clipboard)

### Async Generation

**QThread Worker** (`ImageGenerationWorker`):
```python
class ImageGenerationWorker(QThread):
    """Background worker to avoid blocking UI during 20-60s generation."""
    image_generated = pyqtSignal(str, dict)  # (filepath, metadata)
    
    def run(self):
        """Run generation in background thread."""
        generator = ImageGenerator(backend=self.backend)
        filepath, message = generator.generate(
            prompt=self.prompt,
            style=self.style,
            size=self.size
        )
        
        if filepath:
            metadata = {
                "prompt": self.prompt,
                "style": self.style,
                "size": self.size,
                "backend": self.backend
            }
            self.image_generated.emit(filepath, metadata)
```

---

## Configuration

### Environment Variables

```bash
# REQUIRED for HuggingFace backend
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx

# REQUIRED for OpenAI backend
OPENAI_API_KEY=sk-proj-...

# OPTIONAL
IMAGE_OUTPUT_DIR=data/images
IMAGE_API_MAX_RETRIES=3
IMAGE_API_BACKOFF_FACTOR=0.8
```

---

## Error Handling

### Retry Logic

```python
def _request_with_retries(method: str, url: str, **kwargs) -> requests.Response:
    """Retry with exponential backoff."""
    allowed_status_retry = {429, 502, 503, 504}
    attempt = 0
    
    while attempt < MAX_API_RETRIES:
        try:
            resp = requests.request(method, url, timeout=60, **kwargs)
            
            if resp.status_code == 200:
                return resp
            
            if resp.status_code in allowed_status_retry:
                # Retry with backoff
                time.sleep(BACKOFF_FACTOR ** attempt)
                attempt += 1
                continue
            
            # Non-retryable error
            return resp
        
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            time.sleep(BACKOFF_FACTOR ** attempt)
            attempt += 1
    
    raise RuntimeError(f"Failed after {MAX_API_RETRIES} retries")
```

---

## Performance

### Latency Benchmarks

| Backend | Size | Avg Latency | P95 Latency | Cold Start |
|---------|------|-------------|-------------|------------|
| HuggingFace SD 2.1 | 512x512 | 45s | 90s | +20s |
| OpenAI DALL-E 3 | 1024x1024 | 25s | 45s | None |

### Cost Comparison

| Backend | Cost/Image | Quality | Speed |
|---------|------------|---------|-------|
| HuggingFace | $0 (free tier) | Good | Slow (cold starts) |
| OpenAI | $0.04 (standard) | Excellent | Fast |
| OpenAI (HD) | $0.08 | Outstanding | Fast |

---

## Testing

```python
# tests/test_image_generator.py
def test_content_filter():
    generator = ImageGenerator()
    
    # Safe prompt
    is_safe, reason = generator.check_content_filter("A cute robot")
    assert is_safe is True
    
    # Blocked prompt
    is_safe, reason = generator.check_content_filter("A violent scene")
    assert is_safe is False
    assert "violence" in reason

@pytest.mark.skipif(not os.getenv("HUGGINGFACE_API_KEY"), reason="No API key")
def test_generate_huggingface():
    generator = ImageGenerator(backend="huggingface")
    filepath, message = generator.generate(
        prompt="A simple red circle",
        size="512x512"
    )
    
    assert filepath is not None
    assert os.path.exists(filepath)
```

---

## Security

### API Key Protection

```python
# NEVER log API keys
logger.debug(f"Using HF key: {api_key[:8]}...")  # Only first 8 chars
```

### File Permission Hardening

```python
import os
import stat

# Set restrictive permissions on images directory
os.chmod("data/images", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # 0700
```

---

## Future Enhancements

### Phase 1: Local Stable Diffusion ⏳ PLANNED
- Install `diffusers` library
- Load SD 2.1 locally (4GB GPU required)
- Instant generation (no API calls)

### Phase 2: Image Editing 🔮 FUTURE
- Inpainting: Edit parts of images
- Outpainting: Extend image borders
- Variations: Generate similar images

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: DALL-E 3 backend
- **[03-huggingface-integration.md](03-huggingface-integration.md)**: SD 2.1 backend
- **[04-database-connectors.md](04-database-connectors.md)**: Generation history storage

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly
