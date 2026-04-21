# ImageGeneration - AI Image Generation UI

**Module:** `src/app/gui/image_generation.py`  
**Lines of Code:** 450  
**Type:** PyQt6 Dual-Panel Image Generation Interface  
**Last Updated:** 2025-01-20

---

## Overview

`ImageGenerationInterface` provides a Tron-themed dual-panel UI for AI image generation with prompt input, style presets, backend selection (Hugging Face Stable Diffusion 2.1 / OpenAI DALL-E 3), content filtering, and asynchronous generation with progress tracking.

### Design Philosophy

- **Metaphor:** AI art studio with control panel (left) and canvas (right)
- **Layout:** Dual-page split (40% controls, 60% display)
- **Safety:** Content filtering with 15 blocked keywords
- **UX:** Non-blocking generation (20-60 second operations)

---

## Dual-Panel Architecture

### Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│           ImageGenerationInterface (QWidget)                  │
│  QHBoxLayout (stretch: 1:2)                                  │
│                                                              │
│  ┌────────────────────┬─────────────────────────────────┐  │
│  │ Left Panel (Tron)  │ Right Panel (Display)           │  │
│  │ (40% width)        │ (60% width)                     │  │
│  │                    │                                 │  │
│  │ ┌────────────────┐ │ ┌─────────────────────────────┐│  │
│  │ │ 🎨 AI IMAGE    │ │ │ Generated Image             ││  │
│  │ │    GENERATOR   │ │ │                             ││  │
│  │ └────────────────┘ │ │                             ││  │
│  │                    │ │                             ││  │
│  │ Enter Prompt:      │ │    [Image Display Area]     ││  │
│  │ ┌────────────────┐ │ │                             ││  │
│  │ │ QTextEdit      │ │ │                             ││  │
│  │ │ (multi-line)   │ │ │                             ││  │
│  │ └────────────────┘ │ │                             ││  │
│  │                    │ │                             ││  │
│  │ Select Style:      │ └─────────────────────────────┘│  │
│  │ [Photorealistic ▼] │                                 │  │
│  │                    │ Prompt: A serene...             │  │
│  │ Backend:           │ Generated: 2025-01-20 14:30     │  │
│  │ [Hugging Face ▼]   │                                 │  │
│  │                    │ [ 💾 Save ] [ 📋 Copy ]         │  │
│  │ [⚡ GENERATE]      │                                 │  │
│  │                    │                                 │  │
│  │ Status: Ready      │                                 │  │
│  │                    │                                 │  │
│  │ [📜 VIEW HISTORY]  │                                 │  │
│  │                    │                                 │  │
│  │ ⚠️ Content filter  │                                 │  │
│  │    enabled         │                                 │  │
│  └────────────────────┴─────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. ImageGenerationWorker [[src/app/gui/image_generation.py]] (QThread)

**Purpose:** Background thread for non-blocking image generation (20-60s operations).

#### Class Definition

```python
class ImageGenerationWorker(QThread):
    """Worker thread for image generation to prevent UI blocking."""
    
    finished = pyqtSignal(dict)    # Emits result dict on completion
    progress = pyqtSignal(str)     # Emits status updates
```

#### Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `generator` | `ImageGenerator` [[src/app/core/image_generator.py]] | Core generation system instance |
| `prompt` | `str` | User prompt text (3-1000 chars) |
| `style` | `ImageStyle` | Style preset enum |

#### Run Method

```python
def run(self):
    """Run generation in background."""
    try:
        self.progress.emit("Initializing generation...")
        result = self.generator.generate(self.prompt, self.style)
        self.finished.emit(result)
    except Exception as e:
        logger.error("Generation worker error: %s", e)
        self.finished.emit({"success": False, "error": str(e)})
```

**Result Dictionary:**
```python
# Success
{
    "success": True,
    "filepath": "/path/to/generated_image.png",
    "prompt": "A serene mountain landscape...",
    "style": "photorealistic",
    "timestamp": "2025-01-20 14:30:45",
    "backend": "huggingface",
    "filtered": False
}

# Failure (content filter)
{
    "success": False,
    "filtered": True,
    "error": "Content filter: Prompt contains inappropriate keyword 'violence'"
}

# Failure (API error)
{
    "success": False,
    "filtered": False,
    "error": "Hugging Face API rate limit exceeded"
}
```

---

### 2. ImageGenerationLeftPanel [[src/app/gui/image_generation.py]] (QFrame)

**Purpose:** Tron-themed input panel with prompt entry, style/backend selectors, and action buttons.

#### Signals

```python
class ImageGenerationLeftPanel(QFrame):
    generate_requested = pyqtSignal(str, str)  # (prompt, style_value)
```

#### UI Components

##### Title Label

```python
title = QLabel("🎨 AI IMAGE GENERATOR")
title.setAlignment(Qt.AlignmentFlag.AlignCenter)
title.setStyleSheet(
    f"color: {TRON_GREEN}; "
    f"text-shadow: 0px 0px 20px {TRON_GREEN};"
)
```

**Styling:**
- Font: 18pt bold
- Color: TRON_GREEN (#00ff00)
- Glow effect: 20px shadow

---

##### Prompt Input (QTextEdit)

```python
self.prompt_input = QTextEdit()
self.prompt_input.setPlaceholderText(
    "Describe the image you want to generate...\n\n"
    "Example: A serene mountain landscape at sunset with reflection in a lake"
)
self.prompt_input.setMinimumHeight(150)
```

**Validation:**
```python
# On generate button click
prompt = sanitize_input(
    self.prompt_input.toPlainText().strip(),
    max_length=1000
)
if not validate_length(prompt, min_len=3, max_len=1000):
    self.status_label.setText("⚠️ Prompt must be 3-1000 characters")
    return
```

**Styling:**
```python
QTextEdit {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #00ffff;
    border-radius: 5px;
    padding: 10px;
    font-size: 12pt;
}
```

---

##### Style Selector (QComboBox)

```python
self.style_combo = QComboBox()
for style in ImageStyle:
    self.style_combo.addItem(
        style.value.replace("_", " ").title(),
        style.value
    )
```

**Available Styles (10 presets):**
1. Photorealistic
2. Digital Art
3. Oil Painting
4. Watercolor
5. Anime
6. Sketch
7. Abstract
8. Cyberpunk
9. Fantasy
10. Minimalist

**Styling:**
```python
QComboBox {
    background-color: #1a1a1a;
    color: #00ffff;
    border: 2px solid #00ffff;
    border-radius: 5px;
    padding: 8px;
    font-size: 11pt;
}
```

---

##### Backend Selector (QComboBox)

```python
self.backend_combo = QComboBox()
self.backend_combo.addItem("Hugging Face (Stable Diffusion)", "huggingface")
self.backend_combo.addItem("OpenAI (DALL-E 3)", "openai")
```

**Backend Details:**

| Backend | Model | Resolution | Speed | Cost |
|---------|-------|------------|-------|------|
| Hugging Face | Stable Diffusion 2.1 | 512x512 | 20-40s | Free |
| OpenAI | DALL-E 3 | 1024x1024 | 30-60s | $0.04/image |

---

##### Generate Button

```python
self.generate_btn = QPushButton("⚡ GENERATE IMAGE")
self.generate_btn.setMinimumHeight(50)
self.generate_btn.clicked.connect(self._on_generate)
```

**State Management:**
```python
def set_generating(self, generating: bool):
    """Set UI state for generation."""
    self.generate_btn.setEnabled(not generating)
    self.prompt_input.setEnabled(not generating)
    self.style_combo.setEnabled(not generating)
    self.backend_combo.setEnabled(not generating)
    
    if generating:
        self.status_label.setText("🔄 Generating...")
        self.status_label.setStyleSheet(
            f"color: {TRON_GREEN}; font-weight: bold;"
        )
    else:
        self.status_label.setText("Ready")
```

**Button Styling:**
```python
QPushButton {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #00ff00;
    border-radius: 5px;
    padding: 12px;
    font-size: 12pt;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00ff00;
    color: #0a0a0a;
}
```

---

##### Status Label

```python
self.status_label = QLabel("Ready")
self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
```

**Status States:**
- Ready: "Ready" (TRON_CYAN)
- Generating: "🔄 Generating..." (TRON_GREEN, bold)
- Success: "✅ Generation complete!" (TRON_GREEN)
- Error: "❌ Error: {message}" (#ff4444, red)
- Filtered: "🚫 Blocked: {reason}" (#ff4444, red)

---

##### History Button

```python
self.history_btn = QPushButton("📜 VIEW HISTORY")
self.history_btn.setMinimumHeight(40)
```

**Purpose:** Open history panel showing past generations (not implemented in current version).

---

##### Content Filter Notice

```python
info_label = QLabel(
    "⚠️ Content filtering enabled\n"
    "All images comply with safety guidelines"
)
info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
info_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 9pt;")
```

---

### 3. ImageGenerationRightPanel [[src/app/gui/image_generation.py]] (QFrame)

**Purpose:** Display generated images with metadata and action buttons.

#### UI Components

##### Image Display (QScrollArea + QLabel)

```python
scroll = QScrollArea()
scroll.setWidgetResizable(True)

self.image_label = QLabel("No image generated yet")
self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
self.image_label.setMinimumSize(512, 512)

scroll.setWidget(self.image_container)
```

**Display States:**

**Idle:**
```
┌───────────────────────────┐
│                           │
│                           │
│  No image generated yet   │
│                           │
│                           │
└───────────────────────────┘
```

**Generating:**
```
┌───────────────────────────┐
│                           │
│      ⚡ Generating...     │
│                           │
│  This may take 20-60s     │
│                           │
└───────────────────────────┘
```

**Success:**
```
┌───────────────────────────┐
│   [Generated Image]       │
│                           │
│   [512x512 or 1024x1024]  │
│                           │
└───────────────────────────┘
```

**Error:**
```
┌───────────────────────────┐
│                           │
│     ❌ Failed to          │
│     display image         │
│                           │
└───────────────────────────┘
```

---

##### Metadata Label

```python
self.metadata_label = QLabel("")
self.metadata_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
self.metadata_label.setWordWrap(True)
```

**Display Format:**
```
Prompt: A serene mountain landscape at sunset with...
Generated: 2025-01-20 14:30:45
```

---

##### Action Buttons

```python
self.save_btn = QPushButton("💾 Save")
self.save_btn.setEnabled(False)

self.copy_btn = QPushButton("📋 Copy")
self.copy_btn.setEnabled(False)
```

**State Management:**
- Disabled by default (gray)
- Enabled after successful generation
- Disabled again on error/filter

**Button Actions:**
- **Save:** Open file dialog to save image to disk
- **Copy:** Copy image to clipboard

---

#### Display Methods

##### `display_image(filepath, metadata)`

**Purpose:** Load and display generated image with metadata.

```python
def display_image(self, filepath: str, metadata: dict):
    """Display generated image."""
    try:
        pixmap = QPixmap(filepath)
        if pixmap.isNull():
            raise ValueError("Failed to load image")
        
        # Scale to fit while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            800,
            800,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet("")
        
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
    
    except Exception as e:
        logger.error("Error displaying image: %s", e)
        self.show_error("Failed to display image")
```

---

##### `show_error(message)`

**Purpose:** Display error message in image area.

```python
def show_error(self, message: str):
    """Show error message."""
    self.image_label.setText(f"❌ {message}")
    self.image_label.setStyleSheet(
        "color: #ff4444; font-size: 12pt; padding: 50px;"
    )
    self.metadata_label.setText("")
    self.save_btn.setEnabled(False)
    self.copy_btn.setEnabled(False)
```

---

##### `show_generating()`

**Purpose:** Display generating state.

```python
def show_generating(self):
    """Show generating state."""
    self.image_label.setText("⚡ Generating...\n\nThis may take 20-60 seconds")
    self.image_label.setStyleSheet(
        f"color: {TRON_GREEN}; font-size: 14pt; padding: 50px;"
    )
    self.metadata_label.setText("")
```

---

### 4. ImageGenerationInterface (Main Container)

**Purpose:** Top-level container managing left/right panels and generation workflow.

#### Initialization

```python
class ImageGenerationInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generator = ImageGenerator(backend=ImageGenerationBackend.HUGGINGFACE)
        self.worker = None
        self.setup_ui()
```

#### UI Setup

```python
def setup_ui(self):
    """Setup UI."""
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

## Generation Workflow

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User enters prompt in left panel                         │
│ 2. User selects style preset (e.g., "Photorealistic")       │
│ 3. User selects backend (Hugging Face / OpenAI)             │
│ 4. User clicks "⚡ GENERATE IMAGE" button                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ ImageGenerationLeftPanel._on_generate()                      │
│                                                              │
│ 1. Sanitize prompt (sanitize_input, max 1000 chars)         │
│ 2. Validate prompt length (3-1000 chars)                    │
│ 3. Emit generate_requested signal                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ ImageGenerationInterface._start_generation()                 │
│                                                              │
│ 1. Convert style string to ImageStyle enum                  │
│ 2. Set left panel to "generating" state (disable inputs)    │
│ 3. Show "⚡ Generating..." in right panel                    │
│ 4. Create ImageGenerationWorker thread                      │
│ 5. Connect worker signals (finished, progress)              │
│ 6. Start worker thread                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ ImageGenerationWorker.run() (Background Thread)              │
│                                                              │
│ 1. Emit progress signal: "Initializing generation..."       │
│ 2. Call ImageGenerator.generate(prompt, style)              │
│    ├─> Check content filter (15 blocked keywords)           │
│    ├─> Add safety negative prompts                          │
│    ├─> Route to backend (HuggingFace or OpenAI)             │
│    └─> Save image to data/images/                           │
│ 3. Emit finished signal with result dict                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ ImageGenerationInterface._on_generation_complete()           │
│                                                              │
│ 1. Re-enable left panel inputs                              │
│ 2. Check result["success"]                                  │
│    ├─> Success: Display image in right panel                │
│    │    ├─> Load QPixmap from filepath                      │
│    │    ├─> Scale to 800x800 (maintain aspect ratio)        │
│    │    ├─> Update metadata label                           │
│    │    └─> Enable Save/Copy buttons                        │
│    └─> Failure: Show error message                          │
│         ├─> Filtered: "🚫 Blocked: {reason}"                │
│         └─> Error: "❌ Error: {error}"                      │
└─────────────────────────────────────────────────────────────┘
```

### Code Implementation

```python
def _start_generation(self, prompt: str, style_value: str):
    """Start image generation."""
    try:
        # Convert style string to enum
        style = ImageStyle(style_value)
        
        # Show generating state
        self.right_panel.show_generating()
        
        # Create and start worker
        self.worker = ImageGenerationWorker(self.generator, prompt, style)
        self.worker.finished.connect(self._on_generation_complete)
        self.worker.progress.connect(self.left_panel.set_status)
        self.worker.start()
    
    except Exception as e:
        logger.error("Error starting generation: %s", e)
        self.left_panel.set_status(f"Error: {e}", is_error=True)
        self.left_panel.set_generating(False)

def _on_generation_complete(self, result: dict):
    """Handle generation completion."""
    self.left_panel.set_generating(False)
    
    if result["success"]:
        self.left_panel.set_status("✅ Generation complete!")
        self.right_panel.display_image(result["filepath"], result)
    else:
        error_msg = result.get("error", "Unknown error")
        if result.get("filtered"):
            self.left_panel.set_status(f"🚫 Blocked: {error_msg}", is_error=True)
        else:
            self.left_panel.set_status(f"❌ Error: {error_msg}", is_error=True)
        self.right_panel.show_error(error_msg)
```

---

## Content Safety System

### Blocked Keywords (15 total)

```python
# In ImageGenerator.check_content_filter()
BLOCKED_KEYWORDS = [
    "violence", "explicit", "nsfw", "gore", "weapon",
    "drug", "hate", "offensive", "disturbing", "illegal",
    "inappropriate", "adult", "sexual", "nude", "blood"
]
```

### Filter Check

```python
def check_content_filter(self, prompt: str) -> tuple[bool, str]:
    """Check if prompt contains inappropriate content."""
    prompt_lower = prompt.lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt_lower:
            return False, f"Prompt contains inappropriate keyword '{keyword}'"
    
    return True, ""
```

### Safety Negative Prompts

```python
# Auto-appended to all prompts
SAFETY_NEGATIVE_PROMPT = (
    "violence, gore, explicit, nsfw, inappropriate, disturbing, "
    "offensive, illegal, adult content"
)
```

---

## Backend Integration

### Hugging Face (Stable Diffusion 2.1)

**API Endpoint:** `https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1`

**Request:**
```python
payload = {
    "inputs": prompt,
    "parameters": {
        "negative_prompt": SAFETY_NEGATIVE_PROMPT,
        "num_inference_steps": 50,
        "guidance_scale": 7.5
    }
}
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
response = requests.post(API_URL, headers=headers, json=payload)
```

**Response:** Binary image data (PNG format, 512x512)

---

### OpenAI (DALL-E 3)

**API Call:**
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

**Response:** URL to generated image (1024x1024)

---

## Styling System (Tron Theme)

### Color Constants

```python
TRON_GREEN = "#00ff00"   # Primary accent
TRON_CYAN = "#00ffff"    # Secondary accent
TRON_BLACK = "#0a0a0a"   # Dark background
TRON_DARK = "#1a1a1a"    # Lighter dark background
```

### Panel Styling

```python
# Left Panel
QFrame {
    background-color: #0a0a0a;
    border-right: 2px solid #00ffff;
}

# Right Panel
QFrame {
    background-color: #1a1a1a;
    border-left: 2px solid #00ffff;
}
```

### Glow Effects

```python
# Title glow
text-shadow: 0px 0px 20px #00ff00;

# Button glow on hover
text-shadow: 0px 0px 15px #00ffff;
```

---

## Error Handling

### Common Errors

**API Rate Limit:**
```python
{
    "success": False,
    "error": "Hugging Face API rate limit exceeded. Try again in 60 seconds.",
    "filtered": False
}
```

**Invalid API Key:**
```python
{
    "success": False,
    "error": "OpenAI API authentication failed. Check OPENAI_API_KEY in .env",
    "filtered": False
}
```

**Content Filter:**
```python
{
    "success": False,
    "filtered": True,
    "error": "Content filter: Prompt contains inappropriate keyword 'violence'"
}
```

**Network Error:**
```python
{
    "success": False,
    "error": "Network connection failed. Check internet connection.",
    "filtered": False
}
```

---

## Testing Considerations

### Unit Tests

```python
def test_worker_success():
    """Test worker emits success result."""
    generator = ImageGenerator()
    worker = ImageGenerationWorker(generator, "Test prompt", ImageStyle.PHOTOREALISTIC)
    spy = QSignalSpy(worker.signals.finished)
    
    worker.run()
    
    assert spy.count() == 1
    result = spy[0][0]
    assert result["success"] == True

def test_content_filter():
    """Test content filter blocks inappropriate prompts."""
    left_panel = ImageGenerationLeftPanel()
    left_panel.prompt_input.setText("Generate violent image")
    
    # Trigger generation
    left_panel._on_generate()
    
    # Should be blocked
    assert "Blocked" in left_panel.status_label.text()
```

---

## Cross-References

- **Core System:** See `image_generator.md` (ImageGenerator, ImageStyle)
- **Dashboard Integration:** See `leather_book_dashboard.md` (ProactiveActionsPanel [[src/app/gui/leather_book_dashboard.py]])
- **Security:** See `data_validation.md` (sanitize_input [[src/app/security/data_validation.py]], validate_length [[src/app/security/data_validation.py]])

---

**Document Status:** ✅ Complete  
**Code Coverage:** 100% (all components documented)  
**Last Reviewed:** 2025-01-20 by AGENT-032


---


---

## 📚 Related Documentation

### Cross-References

- [[relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md|06 Image Generation Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/image_generation.py]] - Implementation file
