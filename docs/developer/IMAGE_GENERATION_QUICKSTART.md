---
type: quickstart
tags: [p1-developer, image-generation, ai-art, stable-diffusion, dalle, huggingface, openai]
created: 2026-04-20
last_verified: 2026-04-20
status: current
related_systems: [image-generator, stable-diffusion, dalle-3, huggingface-api, openai-api]
stakeholders: [developers, content-creators, ai-artists]
audience: beginner
prerequisites: [python-basics, api-keys-huggingface, api-keys-openai-optional]
estimated_time: 10 minutes
review_cycle: monthly
api_modules:
  - "[[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator]]"
  - "[[API_QUICK_REFERENCE#gui/image_generation.py|ImageGenerationUI]]"
  - "[[API_QUICK_REFERENCE#gui/leather_book_dashboard.py|LeatherBookDashboard]]"
---
# Image Generation Quick Start Guide

## Setup (One-Time)

### 1. Get API Keys

**Hugging Face** (Required for Stable Diffusion):

1. Visit https://huggingface.co/settings/tokens
1. Create account if needed
1. Click "New token"
1. Name: "Project-AI"
1. Type: Read
1. Click "Generate"
1. Copy the token (starts with `hf_`)

**OpenAI** (Optional for DALL-E 3):

1. Visit https://platform.openai.com/api-keys
1. Create account if needed
1. Click "Create new secret key"
1. Name: "Project-AI"
1. Copy the key (starts with `sk-`)
1. **Note**: DALL-E 3 requires paid plan

### 2. Configure Environment

Create or edit `.env` file in project root:

```bash
# Required
HUGGINGFACE_API_KEY=hf_your_token_here

# Optional (for DALL-E 3)
OPENAI_API_KEY=sk_your_key_here

# Other existing keys (don't remove)
FERNET_KEY=...
```

### 3. Verify Setup

```powershell
# Check .env file exists
cat .env

# Should see HUGGINGFACE_API_KEY=hf_...
```

## Using Image Generation

The image generation system uses [[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator]] class with dual backend support (Hugging Face Stable Diffusion 2.1 and OpenAI DALL-E 3).

### 1. Launch Application

```powershell
# From project root
python -m src.app.main
```

### 2. Navigate to Image Generation

The [[API_QUICK_REFERENCE#gui/leather_book_dashboard.py|LeatherBookDashboard]] includes a **Proactive Actions Panel** with image generation access:

1. **Login** to the application
1. You'll see the **Dashboard** (6-zone layout)
1. Look at **top-right panel** ("Proactive Actions")
1. Click **"🎨 GENERATE IMAGES"** button (triggers [[API_QUICK_REFERENCE#gui/image_generation.py|ImageGenerationUI]])

### 3. Generate Your First Image

**Left Page (Prompt Input)**:

1. **Enter prompt**: Type your image description
   - Example: "a cyberpunk city at night with neon lights"
   
1. **Select style**: Choose from dropdown
   - photorealistic
   - digital_art
   - oil_painting
   - watercolor
   - anime
   - sketch
   - abstract
   - cyberpunk
   - fantasy
   - minimalist

1. **Select size**: Choose image dimensions
   - 256x256 (fast, low quality)
   - 512x512 (balanced, recommended)
   - 768x768 (slower, higher quality)
   - 1024x1024 (slowest, highest quality)

1. **Select backend**:
   - Hugging Face (free, Stable Diffusion 2.1)
   - OpenAI (paid, DALL-E 3, highest quality)

1. **Click "Generate"**

**Right Page (Image Display)**:

- Wait 20-60 seconds (progress shown)
- Image appears on right side
- Metadata displayed below image

### 4. Interact with Generated Image

**Zoom Controls**:

- 25% (thumbnail view)
- 50% (half size)
- 100% (original size)
- 200% (2x zoom)

**Save Image**:

- Click **"Save Image"** button
- Choose location and filename
- Saves as PNG file

**Copy to Clipboard**:

- Click **"Copy to Clipboard"** button
- Paste in any application (Ctrl+V)

**Return to Dashboard**:

- Click **"Return to Dashboard"** button
- Or click dashboard button in navigation

## Example Prompts

### Photorealistic

```
"a serene mountain landscape at sunset with dramatic clouds"
"portrait of a wise elderly person with detailed wrinkles"
"modern architecture building with glass facades"
```

### Digital Art

```
"fantasy dragon flying over medieval castle"
"sci-fi spaceship in deep space nebula"
"magical forest with glowing mushrooms"
```

### Cyberpunk

```
"neon-lit city street with flying cars"
"hacker in dark room with glowing monitors"
"futuristic megacity skyline at night"
```

### Oil Painting

```
"still life with flowers in vase on wooden table"
"impressionist garden with water lilies"
"portrait in the style of Renaissance masters"
```

### Anime

```
"anime character with blue hair in school uniform"
"chibi characters having tea party"
"action scene with energy blasts"
```

## Tips for Best Results

### Good Prompts

✅ **Be specific**: "red sports car on mountain road at sunset"
✅ **Include style**: "watercolor painting of lavender field"
✅ **Add mood**: "mysterious foggy forest with eerie lighting"
✅ **Specify details**: "close-up portrait with blue eyes and freckles"

### Avoid

❌ **Vague prompts**: "something cool"
❌ **Too short**: "car"
❌ **Contradictions**: "bright dark scene"
❌ **Forbidden content**: See Content Safety below

### Style Matching

- **Photorealistic**: Real-world scenes, portraits, nature
- **Digital Art**: Fantasy, sci-fi, concept art
- **Oil Painting**: Classical subjects, portraits, landscapes
- **Watercolor**: Soft scenes, nature, florals
- **Anime**: Characters, action, stylized scenes
- **Cyberpunk**: Futuristic cities, tech, neon
- **Abstract**: Shapes, colors, non-representational
- **Minimalist**: Simple, clean, essential elements

## Content Safety

The [[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator.check_content_filter()]] method blocks prompts containing forbidden keywords.

### Blocked Keywords (15 total)

The system automatically blocks prompts containing:

- Violence, gore, blood
- Explicit, nude, nsfw
- Hate, weapon, illegal
- Drugs, terror
- And more...

### What Happens When Blocked

- Error message: "Content filter: blocked keyword detected"
- Image not generated
- No API call made
- Try rephrasing your prompt

### Safe Alternatives

- Instead of "violent battle" → "epic fantasy duel"
- Instead of "scary horror" → "mysterious dark mansion"
- Instead of "explicit scene" → "artistic figure study"

## Troubleshooting

### "API key not found"

**Problem**: Missing or incorrect API key in .env

**Solution**:

1. Check `.env` file exists in project root
1. Verify key format: `HUGGINGFACE_API_KEY=hf_...`
1. Restart application after editing .env

### "Generation failed: 401 Unauthorized"

**Problem**: Invalid API key

**Solution**:

1. Regenerate token at https://huggingface.co/settings/tokens
1. Update `.env` with new key
1. Restart application

### "Generation failed: 503 Service Unavailable"

**Problem**: Hugging Face API overloaded

**Solution**:

1. Wait 1-2 minutes
1. Try again
1. Try different time of day (less traffic)

### "Content filter: blocked keyword detected"

**Problem**: Prompt contains forbidden word

**Solution**:

1. Rephrase prompt without blocked keyword
1. Use synonyms or alternative descriptions
1. Check Content Safety section above

### Image Takes Forever

**Problem**: Large image size or slow backend

**Solution**:

1. Try 512x512 instead of 1024x1024
1. Hugging Face typically faster than DALL-E
1. Wait up to 60 seconds before retrying

### Image Not Displayed

**Problem**: Generation succeeded but not showing

**Solution**:

1. Check right page is visible
1. Try zooming to 100%
1. Check `data/generated_images/` folder
1. Restart application

## Advanced Usage

### Backend Comparison

| Feature | Hugging Face | OpenAI DALL-E 3 |
|---------|-------------|-----------------|
| Cost | **Free** | Paid plan required |
| Speed | 20-40 sec | 30-60 sec |
| Quality | Good | **Excellent** |
| Max Size | 768x768 | **1024x1024** |
| Styles | All presets | All presets |
| Prompt Length | 77 tokens | **Unlimited** |

### Generation History

**Location**: `data/image_history.json`

**Format**:
```json
[
  {
    "image_path": "data/generated_images/image_1234567890.png",
    "metadata": {
      "prompt": "cyberpunk city at night",
      "style": "cyberpunk",
      "backend": "huggingface",
      "size": "512x512",
      "timestamp": "2024-01-01 12:00:00"
    }
  }
]
```

### Batch Generation (Future Feature)

Not yet implemented. To generate multiple:

1. Generate first image
1. Wait for completion
1. Modify prompt slightly
1. Generate again
1. Repeat as needed

## Performance Notes

### Generation Times

- **256x256**: 15-20 seconds
- **512x512**: 20-40 seconds (recommended)
- **768x768**: 40-60 seconds
- **1024x1024**: 60-90 seconds

### Memory Usage

- **Application**: ~100MB base
- **During generation**: +200MB
- **Generated images**: 2-5MB each

### Disk Space

- Each 512x512 PNG: ~2MB
- Each 1024x1024 PNG: ~5MB
- History JSON: <1MB

## Keyboard Shortcuts

Currently no keyboard shortcuts implemented.

**Suggestion for future**:

- `Ctrl+G`: Generate
- `Ctrl+S`: Save image
- `Ctrl+C`: Copy to clipboard
- `Ctrl+D`: Return to dashboard
- `F11`: Full screen image

## FAQ

**Q: Can I generate videos?**
A: Not yet. Video generation is a future enhancement.

**Q: Can I edit generated images?**
A: Not yet. Image-to-image and inpainting are future features.

**Q: How many images can I generate?**
A: Unlimited (subject to API rate limits).

**Q: Are images stored in the cloud?**
A: No. All images saved locally in `data/generated_images/`.

**Q: Can I use generated images commercially?**
A: Check Hugging Face and OpenAI terms of service for license details.

**Q: Why is my prompt being rejected?**
A: Content filter blocks 15 forbidden keywords for safety.

**Q: Can I use my own Stable Diffusion model?**
A: Not yet. Custom model support is a future enhancement.

**Q: Does this work offline?**
A: No. Requires internet connection for API calls.

## Getting Help

1. **Check logs**: `logs/` directory
1. **Test API keys**: Use Hugging Face web UI to verify token
1. **Review documentation**: [[IMAGE_GENERATION_RESTORATION]]
1. **Check GitHub issues**: Report bugs or request features

---

## API Reference

### Core Image Generation Module

**[[API_QUICK_REFERENCE#core/image_generator.py|ImageGenerator]]** - Dual-backend image generation system

Located in: `src/app/core/image_generator.py` (220 LOC)

#### Key Methods

- **`generate(prompt, style, size, backend)`** - Generate image with specified parameters
  - `prompt` (str): Image description
  - `style` (str): Style preset (photorealistic, digital_art, oil_painting, watercolor, anime, sketch, abstract, cyberpunk, fantasy, minimalist)
  - `size` (str): Image dimensions ("256x256", "512x512", "768x768", "1024x1024")
  - `backend` (str): "huggingface" or "openai"
  - Returns: `(image_path, metadata)` or `(None, error_message)`

- **`check_content_filter(prompt)`** - Validate prompt safety
  - Blocks 15 forbidden keywords (violence, gore, blood, explicit, nude, nsfw, hate, weapon, illegal, drugs, terror, etc.)
  - Returns: `(is_safe: bool, reason: str)`
  - Automatically adds negative prompts for safety

- **`generate_with_huggingface(prompt, size)`** - Hugging Face Stable Diffusion 2.1 backend
  - Free API (requires `HUGGINGFACE_API_KEY`)
  - Model: `stabilityai/stable-diffusion-2-1`
  - Max size: 768x768
  - Generation time: 20-40 seconds

- **`generate_with_openai(prompt, size)`** - OpenAI DALL-E 3 backend
  - Paid API (requires `OPENAI_API_KEY` and active plan)
  - Highest quality output
  - Max size: 1024x1024
  - Generation time: 30-60 seconds
  - Prompt length: Unlimited

#### Style Presets

Each style preset automatically appends style-specific prompts:

```python
STYLE_PRESETS = {
    "photorealistic": "photorealistic, highly detailed, 8k resolution",
    "digital_art": "digital art, concept art, trending on artstation",
    "oil_painting": "oil painting, canvas texture, classical art style",
    "watercolor": "watercolor painting, soft colors, artistic",
    "anime": "anime style, manga illustration, vibrant colors",
    "sketch": "pencil sketch, hand-drawn, artistic sketch",
    "abstract": "abstract art, modern, geometric shapes",
    "cyberpunk": "cyberpunk style, neon lights, futuristic",
    "fantasy": "fantasy art, magical, ethereal, detailed",
    "minimalist": "minimalist design, simple, clean lines"
}
```

#### Content Filtering

**Blocked Keywords** (15 total):
```python
BLOCKED_KEYWORDS = [
    "violence", "gore", "blood", "explicit", "nude", "nsfw",
    "hate", "weapon", "illegal", "drugs", "terror", 
    # + 4 more sensitive terms
]
```

**Safety Negative Prompts**:
```python
SAFETY_NEGATIVE_PROMPTS = [
    "violence", "gore", "blood", "nsfw", "explicit content",
    "disturbing", "inappropriate"
]
```

#### Generation History

Automatically tracked in `data/image_history.json`:

```json
[
  {
    "image_path": "data/generated_images/image_1234567890.png",
    "metadata": {
      "prompt": "cyberpunk city at night",
      "style": "cyberpunk",
      "backend": "huggingface",
      "size": "512x512",
      "timestamp": "2024-01-01 12:00:00"
    }
  }
]
```

### GUI Module

**[[API_QUICK_REFERENCE#gui/image_generation.py|ImageGenerationUI]]** - Image generation interface

Located in: `src/app/gui/image_generation.py` (450 LOC)

#### Components

- **`ImageGenerationLeftPanel`** - Prompt input page (Tron-themed)
  - Prompt text area (`QPlainTextEdit`)
  - Style selector dropdown (`QComboBox`)
  - Size selector dropdown (`QComboBox`)
  - Backend choice (`QRadioButton` group)
  - Generate button (triggers async generation)

- **`ImageGenerationRightPanel`** - Image display page
  - Image display area (`QLabel` with scaled pixmap)
  - Zoom controls (25%, 50%, 100%, 200%)
  - Save button (opens `QFileDialog`)
  - Copy to clipboard button
  - Metadata display (prompt, style, backend, size, timestamp)

- **`ImageGenerationWorker`** - Async generation thread (`QThread`)
  - Runs image generation in background to prevent UI blocking
  - Emits `image_generated` signal with `(image_path, metadata)`
  - Emits `generation_failed` signal with error message
  - Typical generation time: 20-60 seconds

#### Signals

```python
class ImageGenerationUI(QWidget):
    image_generated = pyqtSignal(str, dict)  # (image_path, metadata)
    generation_failed = pyqtSignal(str)      # (error_message)
    return_to_dashboard = pyqtSignal()       # Navigate back
```

#### Usage Example

```python
# From dashboard, navigate to image generation
image_gen_ui = ImageGenerationUI()
image_gen_ui.image_generated.connect(display_image_callback)
image_gen_ui.return_to_dashboard.connect(switch_to_dashboard)
main_window.add_page(image_gen_ui)
```

### Dashboard Integration

**[[API_QUICK_REFERENCE#gui/leather_book_dashboard.py|LeatherBookDashboard]]** - Main dashboard

The **ProactiveActionsPanel** includes image generation button:

```python
class ProactiveActionsPanel(QWidget):
    image_gen_requested = pyqtSignal()  # Emitted when button clicked
    
    def __init__(self):
        # ...
        self.image_gen_button = QPushButton("🎨 GENERATE IMAGES")
        self.image_gen_button.clicked.connect(
            lambda: self.image_gen_requested.emit()
        )
```

#### Dashboard Flow

1. User clicks "🎨 GENERATE IMAGES" button
2. Dashboard emits `image_gen_requested` signal
3. Main window (`LeatherBookInterface`) switches to page 2
4. `ImageGenerationUI` is displayed
5. User generates image
6. User clicks "Return to Dashboard"
7. Main window switches back to page 1 (dashboard)

### Configuration & Environment

**Required Environment Variables** (`.env` file):

```bash
# Required for Hugging Face backend
HUGGINGFACE_API_KEY=hf_your_token_here

# Optional for OpenAI DALL-E 3 backend
OPENAI_API_KEY=sk_your_key_here
```

**Get API Keys**:
- Hugging Face: https://huggingface.co/settings/tokens (free)
- OpenAI: https://platform.openai.com/api-keys (paid plan required for DALL-E 3)

### Data Storage

**Generated Images**: `data/generated_images/`
- Filenames: `image_<timestamp>.png`
- Format: PNG (lossless compression)
- Size: 2-5MB per image (depends on resolution)

**Generation History**: `data/image_history.json`
- JSON array of generation metadata
- Includes prompt, style, backend, size, timestamp
- Used for history browsing (future feature)

### Performance Characteristics

**Generation Times** (approximate):

| Size | Hugging Face | OpenAI |
|------|-------------|---------|
| 256x256 | 15-20 sec | 25-30 sec |
| 512x512 | 20-40 sec | 30-45 sec |
| 768x768 | 40-60 sec | 45-60 sec |
| 1024x1024 | N/A (not supported) | 60-90 sec |

**Memory Usage**:
- Application base: ~100MB
- During generation: +200MB
- Generated images: 2-5MB each (stored on disk)

**API Rate Limits**:
- Hugging Face: ~1,000 requests/month (free tier)
- OpenAI: Varies by plan (pay-per-use)

### Error Handling

Common errors and solutions:

```python
# API key not found
if not os.getenv("HUGGINGFACE_API_KEY"):
    return None, "Error: HUGGINGFACE_API_KEY not found in .env"

# Content filter triggered
is_safe, reason = self.check_content_filter(prompt)
if not is_safe:
    return None, f"Content filter: {reason}"

# API request failed
try:
    response = requests.post(api_url, ...)
    response.raise_for_status()
except requests.HTTPError as e:
    return None, f"Generation failed: {e}"
```

### Threading Pattern

**CRITICAL**: Always use `QThread` for background generation:

```python
# CORRECT: Async generation with QThread
worker = ImageGenerationWorker(prompt, style, size, backend)
worker.image_generated.connect(self.on_image_generated)
worker.generation_failed.connect(self.on_generation_failed)
worker.start()  # Non-blocking

# WRONG: Never use threading.Thread in PyQt6
# threading.Thread(target=generate_image).start()  # ❌ Will crash
```

### Related Documentation

- **Image Generation Restoration**: [[IMAGE_GENERATION_RESTORATION]] (troubleshooting guide)
- **Desktop App Quickstart**: [[DESKTOP_APP_QUICKSTART]] (setup and installation)
- **GUI Architecture**: [[PROGRAM_SUMMARY]] → GUI Development section
- **PyQt6 Threading**: [[COPILOT_MANDATORY_GUIDE]] → PyQt6 threading gotchas
- **Environment Setup**: [[DEVELOPER_QUICK_REFERENCE]] → Environment Setup

### Source Code Locations

```
src/app/
├── core/
│   └── image_generator.py          # 220 LOC - ImageGenerator class
└── gui/
    ├── image_generation.py         # 450 LOC - ImageGenerationUI
    ├── leather_book_dashboard.py   # 608 LOC - Dashboard with ProactiveActions
    └── leather_book_interface.py   # 659 LOC - Main window with page switching
```

### Future Enhancements (Roadmap)

Planned features:

- [ ] **Image History Browser** - Browse previously generated images
- [ ] **Negative Prompt Input** - Manual negative prompt control
- [ ] **Batch Generation** - Generate multiple images from prompts list
- [ ] **Image Upscaling** - Upscale 512x512 → 2048x2048
- [ ] **Image-to-Image** - Use existing image as base
- [ ] **Inpainting** - Edit parts of generated images
- [ ] **Custom Models** - Support for LoRA and fine-tuned models
- [ ] **Video Generation** - Animate image sequences
- [ ] **Advanced Style Mixing** - Combine multiple style presets

See [[PROGRAM_SUMMARY]] → Image Generation System for implementation details.

---

**Quick Navigation**:
- [[#Setup (One-Time)|↑ Setup]]
- [[#Using Image Generation|↑ Usage]]
- [[#Troubleshooting|↑ Troubleshooting]]
- [[API_QUICK_REFERENCE|→ Full API Reference]]
- [[IMAGE_GENERATION_RESTORATION|→ Restoration Guide]]
- [[PROGRAM_SUMMARY|→ Complete Documentation]]

---

Enjoy creating AI-generated art! 🎨
