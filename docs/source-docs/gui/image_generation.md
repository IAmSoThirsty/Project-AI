---
title: "Image Generation Interface - Dual-Panel AI Image Generator"
id: "gui-image-generation"
type: "api_reference"
version: "2.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "AGENT-034"
contributors: ["Architecture Team", "GUI Team"]
category: "gui-documentation"
tags: ["pyqt6", "gui", "image-generation", "stable-diffusion", "dalle", "async-worker"]
technologies: ["Python 3.11+", "PyQt6", "QThread", "Hugging Face", "OpenAI DALL-E"]
related_docs:
  - "gui-leather-book-dashboard"
  - "core-image-generator"
  - "security-content-filtering"
description: "Complete API reference for the image generation interface with dual-panel layout, async generation, content filtering, and style presets"
security_classification: "internal"
review_status: "peer-reviewed"
audience: ["developers", "gui-engineers", "ml-engineers"]
---

# Image Generation Interface - Dual-Panel AI Image Generator

**Module:** `src/app/gui/image_generation.py`
**Lines of Code:** 378
**Primary Classes:** `ImageGenerationInterface`, `ImageGenerationWorker`, `ImageGenerationLeftPanel`, `ImageGenerationRightPanel`
**Design Pattern:** Dual-panel layout with async worker thread

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Dual-Panel Layout](#dual-panel-layout)
3. [PyQt6 Architecture](#pyqt6-architecture)
4. [API Reference](#api-reference)
5. [Async Generation Worker](#async-generation-worker)
6. [Content Filtering](#content-filtering)
7. [Style Presets](#style-presets)
8. [Backend Integration](#backend-integration)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)

---

## Component Overview

### Purpose

The `ImageGenerationInterface` provides a production-ready GUI for AI image generation with:

- **Dual backends**: Hugging Face Stable Diffusion 2.1 + OpenAI DALL-E 3
- **Async generation**: Non-blocking UI during 20-60 second generation
- **Content filtering**: 15 blocked keywords + safety negative prompts
- **Style presets**: 10 predefined artistic styles
- **Generation history**: JSON-persisted generation log

### UX Goals

- **No UI blocking**: Long generation times handled in background thread
- **Instant feedback**: Status updates during generation
- **Visual styling**: Tron-themed left panel + neutral right panel
- **Easy saving**: One-click save/copy buttons

### Design Philosophy

> "Image generation should feel magical yet safe—users create freely within ethical boundaries, with zero wait on the UI thread."

---

## Dual-Panel Layout

### ASCII Layout Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  ImageGenerationInterface (QWidget)                      │
│                      QHBoxLayout (spacing: 0, margin: 0)                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────┬──────────────────────────────────┐   │
│  │ LEFT PANEL                   │ RIGHT PANEL                      │   │
│  │ ImageGenerationLeftPanel     │ ImageGenerationRightPanel        │   │
│  │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │   │
│  │ TRON THEME (#0a0a0a)        │ NEUTRAL THEME (#1a1a1a)          │   │
│  │                              │                                  │   │
│  │ 🎨 AI IMAGE GENERATOR        │ Generated Image                  │   │
│  │                              │ ┌────────────────────────────┐   │   │
│  │ Enter Image Prompt:          │ │                            │   │   │
│  │ ┌──────────────────────────┐ │ │  [Image Display Area]      │   │   │
│  │ │ A serene mountain        │ │ │                            │   │   │
│  │ │ landscape at sunset      │ │ │  512x512 or 800x800        │   │   │
│  │ │ with reflection in lake  │ │ │                            │   │   │
│  │ └──────────────────────────┘ │ │  (QLabel with QPixmap)     │   │   │
│  │                              │ │                            │   │   │
│  │ Select Style Preset:         │ │                            │   │   │
│  │ [Photorealistic       ▼]     │ └────────────────────────────┘   │   │
│  │                              │                                  │   │
│  │ Generation Backend:          │ Prompt: A serene mountain...     │   │
│  │ [Hugging Face         ▼]     │ Generated: 2026-04-20 10:30 AM   │   │
│  │                              │                                  │   │
│  │ [⚡ GENERATE IMAGE]           │ [💾 Save]  [📋 Copy]             │   │
│  │                              │                                  │   │
│  │ Status: 🔄 Generating...     │                                  │   │
│  │                              │                                  │   │
│  │ [📜 VIEW HISTORY]            │                                  │   │
│  │                              │                                  │   │
│  │ ⚠️ Content filtering enabled │                                  │   │
│  │ All images comply with       │                                  │   │
│  │ safety guidelines            │                                  │   │
│  │                              │                                  │   │
│  │ Ratio: 1                     │ Ratio: 2                         │   │
│  └──────────────────────────────┴──────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Layout Hierarchy

```python
QWidget (ImageGenerationInterface)
└── QHBoxLayout [margin: 0, spacing: 0]
    ├── ImageGenerationLeftPanel (QFrame) [stretch: 1]
    │   └── QVBoxLayout
    │       ├── QLabel (title)
    │       ├── QTextEdit (prompt_input)
    │       ├── QComboBox (style_combo)
    │       ├── QComboBox (backend_combo)
    │       ├── QPushButton (generate_btn)
    │       ├── QLabel (status_label)
    │       └── QPushButton (history_btn)
    └── ImageGenerationRightPanel (QFrame) [stretch: 2]
        └── QVBoxLayout
            ├── QLabel (title)
            ├── QScrollArea
            │   └── QLabel (image_label) [displays QPixmap]
            ├── QLabel (metadata_label)
            └── QHBoxLayout
                ├── QPushButton (save_btn)
                └── QPushButton (copy_btn)
```

---

## PyQt6 Architecture

### Class Definitions

```python
class ImageGenerationWorker(QThread):
    """Worker thread for async image generation."""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

class ImageGenerationLeftPanel(QFrame):
    """Left panel (Tron themed) for prompt input and controls."""
    generate_requested = pyqtSignal(str, str)  # (prompt, style)

class ImageGenerationRightPanel(QFrame):
    """Right panel for displaying generated images."""

class ImageGenerationInterface(QWidget):
    """Main interface with dual-panel layout."""
```

---

## API Reference

### ImageGenerationInterface

#### `__init__(parent=None)`

**Description:** Initialize dual-panel image generation interface.

**Initialization Sequence:**
1. Create `ImageGenerator` with default backend (Hugging Face)
2. Initialize `worker = None`
3. Call `setup_ui()`

**Example:**
```python
interface = ImageGenerationInterface()
interface.show()
```

---

#### `setup_ui()`

**Description:** Setup dual-panel layout.

**Layout:**
```python
layout = QHBoxLayout(self)
layout.setSpacing(0)
layout.setContentsMargins(0, 0, 0, 0)

# Left panel (prompt input)
self.left_panel = ImageGenerationLeftPanel()
self.left_panel.generate_requested.connect(self._start_generation)
layout.addWidget(self.left_panel, stretch=1)

# Right panel (image display)
self.right_panel = ImageGenerationRightPanel()
layout.addWidget(self.right_panel, stretch=2)
```

---

#### `_start_generation(prompt: str, style_value: str)`

**Description:** Start async image generation.

**Parameters:**
- `prompt` (str): Image description (3-1000 chars)
- `style_value` (str): Style enum value (e.g., "photorealistic")

**Behavior:**
1. Convert style string to `ImageStyle` enum
2. Show generating state on right panel
3. Create `ImageGenerationWorker`
4. Connect signals:
   - `finished` → `_on_generation_complete`
   - `progress` → `left_panel.set_status`
5. Start worker thread

**Example:**
```python
self.left_panel.generate_requested.connect(self._start_generation)
```

---

#### `_on_generation_complete(result: dict)`

**Description:** Handle generation completion.

**Parameters:**
- `result` (dict): Generation result with keys:
  - `success` (bool): True if generated successfully
  - `filepath` (str): Path to generated image
  - `error` (str): Error message if failed
  - `filtered` (bool): True if blocked by content filter

**Success Path:**
```python
if result["success"]:
    self.left_panel.set_status("✅ Generation complete!")
    self.right_panel.display_image(result["filepath"], result)
```

**Failure Paths:**
```python
if result.get("filtered"):
    self.left_panel.set_status(f"🚫 Blocked: {error_msg}", is_error=True)
else:
    self.left_panel.set_status(f"❌ Error: {error_msg}", is_error=True)
self.right_panel.show_error(error_msg)
```

---

### ImageGenerationWorker

#### `__init__(generator, prompt, style)`

**Description:** Initialize worker thread for generation.

**Parameters:**
- `generator` (ImageGenerator): Generator instance
- `prompt` (str): Image prompt
- `style` (ImageStyle): Style enum

**Signals:**
- `finished = pyqtSignal(dict)` - Result on completion
- `progress = pyqtSignal(str)` - Status updates

---

#### `run()`

**Description:** Execute generation in background thread.

**Behavior:**
```python
try:
    self.progress.emit("Initializing generation...")
    result = self.generator.generate(self.prompt, self.style)
    self.finished.emit(result)
except Exception as e:
    logger.error("Generation worker error: %s", e)
    self.finished.emit({"success": False, "error": str(e)})
```

**Duration:** 20-60 seconds (varies by backend and complexity)

---

### ImageGenerationLeftPanel

#### `__init__(parent=None)`

**Description:** Initialize Tron-themed left panel.

**Tron Color Scheme:**
```python
TRON_GREEN = "#00ff00"
TRON_CYAN = "#00ffff"
TRON_BLACK = "#0a0a0a"
TRON_DARK = "#1a1a1a"
```

**Components:**
- Title: "🎨 AI IMAGE GENERATOR" (18pt, bold, green glow)
- Prompt input: `QTextEdit` (150px height, placeholder text)
- Style combo: `QComboBox` (10 style options)
- Backend combo: `QComboBox` (Hugging Face / OpenAI)
- Generate button: "⚡ GENERATE IMAGE" (50px height)
- Status label: "Ready" (cyan text)
- History button: "📜 VIEW HISTORY" (40px height)
- Info label: Content filtering notice

---

#### `_on_generate()`

**Description:** Handle generate button click.

**Validation:**
```python
# Sanitize and validate prompt
prompt = sanitize_input(
    self.prompt_input.toPlainText().strip(),
    max_length=1000
)
if not validate_length(prompt, min_len=3, max_len=1000):
    self.status_label.setText("⚠️ Prompt must be 3-1000 characters")
    self.status_label.setStyleSheet("color: #ff4444; font-size: 10pt;")
    return
```

**Emission:**
```python
style = self.style_combo.currentData()
self.generate_requested.emit(prompt, style)
self.set_generating(True)
```

---

#### `set_generating(generating: bool)`

**Description:** Update UI for generating state.

**Parameters:**
- `generating` (bool): True if generating, False if idle

**UI Changes:**
```python
self.generate_btn.setEnabled(not generating)
self.prompt_input.setEnabled(not generating)
self.style_combo.setEnabled(not generating)
self.backend_combo.setEnabled(not generating)

if generating:
    self.status_label.setText("🔄 Generating...")
    self.status_label.setStyleSheet(
        f"color: {TRON_GREEN}; font-size: 10pt; font-weight: bold;"
    )
else:
    self.status_label.setText("Ready")
    self.status_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 10pt;")
```

---

#### `set_status(message: str, is_error: bool = False)`

**Description:** Set status label text and color.

**Parameters:**
- `message` (str): Status message
- `is_error` (bool): True for red color, False for green

**Example:**
```python
self.left_panel.set_status("✅ Generation complete!")
self.left_panel.set_status("❌ Failed to connect", is_error=True)
```

---

### ImageGenerationRightPanel

#### `__init__(parent=None)`

**Description:** Initialize neutral-themed right panel.

**Components:**
- Title: "Generated Image" (16pt, bold, cyan)
- Scroll area: Contains image label
- Image label: `QLabel` with QPixmap (512x512 minimum)
- Metadata label: Prompt + timestamp (9pt, cyan)
- Save button: "💾 Save" (disabled until image generated)
- Copy button: "📋 Copy" (disabled until image generated)

---

#### `display_image(filepath: str, metadata: dict)`

**Description:** Display generated image.

**Parameters:**
- `filepath` (str): Path to generated image file
- `metadata` (dict): Generation metadata (prompt, timestamp, etc.)

**Behavior:**
```python
pixmap = QPixmap(filepath)
if pixmap.isNull():
    raise ValueError("Failed to load image")

# Scale to fit (max 800x800, maintain aspect ratio)
scaled_pixmap = pixmap.scaled(
    800, 800,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)

self.image_label.setPixmap(scaled_pixmap)

# Update metadata
prompt = metadata.get("prompt", "Unknown")
timestamp = metadata.get("timestamp", "")
self.metadata_label.setText(
    f"Prompt: {prompt[:100]}...\n"
    f"Generated: {timestamp}"
)

# Enable buttons
self.save_btn.setEnabled(True)
self.copy_btn.setEnabled(True)
```

---

#### `show_error(message: str)`

**Description:** Display error message.

**Behavior:**
```python
self.image_label.setText(f"❌ {message}")
self.image_label.setStyleSheet(
    "color: #ff4444; font-size: 12pt; padding: 50px;"
)
self.metadata_label.setText("")
self.save_btn.setEnabled(False)
self.copy_btn.setEnabled(False)
```

---

#### `show_generating()`

**Description:** Display generating state.

**Behavior:**
```python
self.image_label.setText("⚡ Generating...\n\nThis may take 20-60 seconds")
self.image_label.setStyleSheet(
    f"color: {TRON_GREEN}; font-size: 14pt; padding: 50px;"
)
self.metadata_label.setText("")
```

---

## Async Generation Worker

### Thread Safety

**QThread Pattern:**
```python
class ImageGenerationWorker(QThread):
    # Signals are thread-safe
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def run(self):
        # Runs in background thread
        result = self.generator.generate(self.prompt, self.style)
        # Signal emission is thread-safe
        self.finished.emit(result)
```

**UI Updates:**
```python
# NEVER update UI directly from worker thread
# ❌ self.label.setText("Done")  # Crashes!

# ✅ Use signals instead
self.progress.emit("Done")  # Safe
```

---

### Progress Updates

**Worker emits progress:**
```python
self.progress.emit("Initializing generation...")
# ... generation happens ...
self.progress.emit("Applying style...")
```

**UI receives progress:**
```python
worker.progress.connect(self.left_panel.set_status)
```

---

## Content Filtering

### Blocked Keywords

**15 categories:**
```python
BLOCKED_KEYWORDS = [
    "violence", "gore", "blood",
    "sexual", "nude", "explicit",
    "hate", "racist", "offensive",
    "drugs", "weapons", "illegal",
    "disturbing", "graphic", "shocking"
]
```

### Safety Negative Prompts

**Automatically added:**
```python
negative_prompt = (
    "violence, gore, blood, sexual content, nudity, "
    "hate symbols, drugs, weapons, graphic, disturbing"
)
```

### Filter Flow

```python
is_safe, reason = generator.check_content_filter(prompt)
if not is_safe:
    return {
        "success": False,
        "filtered": True,
        "error": f"Content filter: {reason}"
    }
```

---

## Style Presets

### 10 Available Styles

| Style | Value | Description |
|-------|-------|-------------|
| Photorealistic | `photorealistic` | Lifelike, photo-quality images |
| Digital Art | `digital_art` | Modern digital illustration |
| Oil Painting | `oil_painting` | Classic oil painting aesthetic |
| Watercolor | `watercolor` | Soft watercolor painting |
| Anime | `anime` | Japanese anime/manga style |
| Sketch | `sketch` | Pencil sketch drawing |
| Abstract | `abstract` | Non-representational art |
| Cyberpunk | `cyberpunk` | Futuristic neon aesthetic |
| Fantasy | `fantasy` | Magical, fantastical elements |
| Minimalist | `minimalist` | Clean, simple design |

### Style Application

**Prompt modification:**
```python
style_suffix = {
    "photorealistic": ", photorealistic, 8k, high detail",
    "oil_painting": ", oil painting, classical art style",
    "anime": ", anime style, manga art",
    # ... etc.
}

final_prompt = f"{user_prompt}{style_suffix[style]}"
```

---

## Backend Integration

### Hugging Face (Stable Diffusion 2.1)

**API:**
```python
url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
payload = {"inputs": prompt}

response = requests.post(url, headers=headers, json=payload)
image_bytes = response.content
```

**Advantages:**
- Free tier available
- Fast inference (~20-30 seconds)
- Good quality

**Disadvantages:**
- Requires API key
- Rate limits on free tier

---

### OpenAI (DALL-E 3)

**API:**
```python
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt,
    size="1024x1024",
    quality="standard",
    n=1
)
image_url = response.data[0].url
```

**Advantages:**
- Highest quality
- Excellent prompt adherence
- Built-in safety filter

**Disadvantages:**
- Paid only (~$0.04/image)
- Slower (~40-60 seconds)

---

## Usage Examples

### Example 1: Basic Usage

```python
from app.gui.image_generation import ImageGenerationInterface

interface = ImageGenerationInterface()
interface.show()
```

---

### Example 2: Pre-fill Prompt

```python
interface = ImageGenerationInterface()
interface.left_panel.prompt_input.setText(
    "A futuristic city with flying cars at sunset"
)
interface.left_panel.style_combo.setCurrentText("Cyberpunk")
interface.show()
```

---

### Example 3: Custom Backend

```python
from app.core.image_generator import ImageGenerator, ImageGenerationBackend

interface = ImageGenerationInterface()
interface.generator = ImageGenerator(backend=ImageGenerationBackend.OPENAI)
interface.show()
```

---

### Example 4: Handling Generation Result

```python
def on_generation_complete(result: dict):
    if result["success"]:
        print(f"Image saved to: {result['filepath']}")
        # Auto-save to custom location
        import shutil
        shutil.copy(result['filepath'], "my_images/generated.png")
    else:
        print(f"Generation failed: {result['error']}")

interface = ImageGenerationInterface()
interface._on_generation_complete = on_generation_complete
interface.show()
```

---

## Troubleshooting

### Issue 1: UI Freezes During Generation

**Symptom:** Interface unresponsive for 20-60 seconds

**Cause:** Not using worker thread

**Solution:**
```python
# ✅ Correct (async)
worker = ImageGenerationWorker(generator, prompt, style)
worker.finished.connect(self._on_generation_complete)
worker.start()

# ❌ Wrong (blocks UI)
result = generator.generate(prompt, style)  # DON'T DO THIS!
```

---

### Issue 2: Content Filter Blocks Valid Prompts

**Symptom:** Harmless prompts rejected

**Cause:** Overly strict keyword matching

**Debug:**
```python
from app.core.image_generator import ImageGenerator

generator = ImageGenerator()
is_safe, reason = generator.check_content_filter("your prompt here")
print(f"Safe: {is_safe}, Reason: {reason}")
```

**Solution:**
```python
# Refine keyword list in src/app/core/image_generator.py
BLOCKED_KEYWORDS = [
    # Remove overly broad keywords
    # "graphic",  # Too broad, blocks "graphic design"
]
```

---

### Issue 3: API Key Errors

**Symptom:** "Unauthorized" or "Invalid API key"

**Cause:** Missing or invalid API keys in `.env`

**Solution:**
```bash
# .env file
HUGGINGFACE_API_KEY=hf_...
OPENAI_API_KEY=sk-...
```

**Verification:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"HF Key: {os.getenv('HUGGINGFACE_API_KEY')[:10]}...")
print(f"OpenAI Key: {os.getenv('OPENAI_API_KEY')[:10]}...")
```

---

### Issue 4: Images Not Displaying

**Symptom:** Blank image area after generation

**Cause:** QPixmap load failure

**Debug:**
```python
pixmap = QPixmap(filepath)
if pixmap.isNull():
    print(f"Failed to load image: {filepath}")
    import os
    print(f"File exists: {os.path.exists(filepath)}")
```

**Solution:**
```python
# Ensure filepath is valid PNG/JPG
if not filepath.endswith(('.png', '.jpg', '.jpeg')):
    raise ValueError("Invalid image format")
```

---

## Performance Metrics

| Metric | Hugging Face | OpenAI DALL-E |
|--------|--------------|---------------|
| Generation time | 20-30s | 40-60s |
| Image quality | Good | Excellent |
| Cost per image | Free (limited) | ~$0.04 |
| Max resolution | 512x512 | 1024x1024 |
| API rate limit | 1000/day (free) | Pay-per-use |
| Content filter | Manual | Built-in |

---

## Related Documentation

- **[Core Image Generator](../core/image_generator.md)** - Backend implementation
- **[Leather Book Dashboard](./leather_book_dashboard.md)** - Integration point
- **Security Content Filtering** - `docs/SECURITY_CONTENT_FILTERING.md`
- **Hugging Face API** - <https://huggingface.co/docs>
- **OpenAI DALL-E** - <https://platform.openai.com/docs>

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0.0 | 2026-04-20 | Complete API documentation, dual-panel UI | AGENT-034 |
| 1.5.0 | 2026-03-20 | Added OpenAI backend, style presets | GUI Team |
| 1.0.0 | 2026-02-25 | Initial Hugging Face implementation | Architecture Team |

---

## License

**Copyright © 2026 Project-AI Team**
Internal documentation - Not for public distribution

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
