# Image Generation UI Relationships Map

## Component: Image Generation Interface
**File:** `src/app/gui/image_generation.py`  
**Lines:** 450+  
**Role:** Dual-page image generation UI with async worker pattern

---

## 1. ARCHITECTURE OVERVIEW

### Three Core Classes
```
image_generation.py
├── ImageGenerationWorker (QThread)
│   ├── Signals: finished, progress
│   ├── Purpose: Async image generation (20-60s operations)
│   └── Prevents UI blocking during generation
│
├── ImageGenerationLeftPanel (QFrame)
│   ├── Signal: generate_requested(str, str)
│   ├── Purpose: Prompt input, style/size selection
│   └── Tron-themed prompt interface
│
├── ImageGenerationRightPanel (QFrame)
│   ├── No signals (display only)
│   ├── Purpose: Image display, zoom controls, metadata
│   └── Shows generated images with save/copy options
│
└── ImageGenerationInterface (QWidget)
    ├── Purpose: Container + worker management
    ├── Layout: Horizontal (left 1:2 right)
    └── Coordinates left panel → worker → right panel flow
```

---

## 2. IMAGEGENERATIONWORKER RELATIONSHIPS

### Class Definition
```python
class ImageGenerationWorker(QThread):
    """Worker thread for image generation to prevent UI blocking."""
    # Lines 36-58
```

### Signal Definitions
```python
# Lines 39-40
finished = pyqtSignal(dict)  # Emits result dict on completion
progress = pyqtSignal(str)   # Emits status updates during generation
```

### Constructor
```python
def __init__(self, generator: ImageGenerator, prompt: str, style: ImageStyle):
    """Initialize worker."""
    super().__init__()
    self.generator = generator  # ImageGenerator instance from core
    self.prompt = prompt        # User's prompt text
    self.style = style          # ImageStyle enum (photorealistic, anime, etc.)
```

### Execution Flow
```
ImageGenerationInterface creates worker
        ↓
Worker thread starts
        ↓
run() method executes in background
        ↓
Emit progress: "Initializing generation..."
        ↓
Call generator.generate(prompt, style)
        ↓
Generation takes 20-60 seconds (external API call)
        ↓
PATH 1: Success
    ├── result = {"success": True, "filepath": "...", "metadata": {...}}
    └── finished.emit(result)
        ↓
PATH 2: Error
    ├── Exception caught
    ├── logger.error("Generation worker error: %s", e)
    ├── result = {"success": False, "error": str(e)}
    └── finished.emit(result)
        ↓
Worker thread terminates
```

### Core Integration
```python
# Line 24: Import
from app.core.image_generator import (
    ImageGenerationBackend,
    ImageGenerator,
    ImageStyle,
)

# Worker calls ImageGenerator.generate()
# ImageGenerator routes to:
# ├── Hugging Face Stable Diffusion 2.1 (default)
# └── OpenAI DALL-E 3 (if backend selected)
```

---

## 3. IMAGEGENERATIONLEFTPANEL RELATIONSHIPS

### Class Definition
```python
class ImageGenerationLeftPanel(QFrame):
    """Left panel (Tron themed) for prompt input and controls."""
    # Lines 60-180
```

### Signal Definition
```python
# Line 63
generate_requested = pyqtSignal(str, str)  # (prompt, style)
```

### Component Structure
```
ImageGenerationLeftPanel
├── Tron Styling
│   ├── background: TRON_BLACK (#0a0a0a)
│   ├── border-right: 2px solid TRON_CYAN (#00ffff)
│   ├── text: TRON_CYAN for labels, TRON_GREEN for input
│   └── buttons: TRON_GREEN border, hover → green background
│
├── Layout: QVBoxLayout
│   ├── Title: "🎨 IMAGE GENERATION"
│   │   └── Font: 16pt bold, TRON_CYAN
│   │
│   ├── Prompt Section
│   │   ├── Label: "Enter Prompt:"
│   │   └── prompt_input (QTextEdit)
│   │       ├── max_height: 150px
│   │       ├── placeholder: "Describe the image you want..."
│   │       └── style: TRON_DARK bg, TRON_GREEN text, TRON_CYAN border
│   │
│   ├── Style Section
│   │   ├── Label: "Style:"
│   │   └── style_combo (QComboBox)
│   │       └── options: 10 styles (photorealistic, digital_art, oil_painting, etc.)
│   │
│   ├── Size Section
│   │   ├── Label: "Size:"
│   │   └── size_combo (QComboBox)
│   │       └── options: "512x512", "768x768", "1024x1024"
│   │
│   ├── Backend Section
│   │   ├── Label: "Backend:"
│   │   └── backend_combo (QComboBox)
│   │       └── options: "Hugging Face (Stable Diffusion)", "OpenAI (DALL-E 3)"
│   │
│   ├── generate_btn (QPushButton)
│   │   ├── text: "🚀 GENERATE IMAGE"
│   │   └── style: Large, bold, Tron green theme
│   │
│   ├── status_label (QLabel)
│   │   ├── text: Status updates ("Ready", "Generating...", "✅ Complete")
│   │   └── color: TRON_CYAN (success) or red (error)
│   │
│   └── Stretch (pushes controls to top)
```

### Generate Button Flow
```
User fills prompt_input
        ↓
User selects style (optional, default: photorealistic)
        ↓
User selects size (optional, default: 512x512)
        ↓
User selects backend (optional, default: Hugging Face)
        ↓
User clicks generate_btn
        ↓
_on_generate() method called (line 160)
        ↓
Validate prompt:
├── prompt = prompt_input.toPlainText().strip()
├── if not prompt: show warning → return
└── sanitize_input(prompt, max_length=2000)
        ↓
Get selections:
├── style = style_combo.currentText()
└── size = size_combo.currentText()
        ↓
Disable button: generate_btn.setEnabled(False)
        ↓
Emit signal: generate_requested.emit(prompt, style)
        ↓
Wait for completion (handled by parent Interface)
```

### Status Update Methods
```python
def set_status(self, message: str, is_error: bool = False):
    """Update status label with message."""
    self.status_label.setText(message)
    if is_error:
        self.status_label.setStyleSheet("color: #ff0000;")  # Red
    else:
        self.status_label.setStyleSheet("color: #00ffff;")  # Cyan

def set_generating(self, generating: bool):
    """Update UI state during generation."""
    self.generate_btn.setEnabled(not generating)
    if generating:
        self.status_label.setText("⏳ Generating image...")
```

### Signal/Slot Connections
```python
# Line 175: Button clicked
generate_btn.clicked.connect(self._on_generate)

# External connection in ImageGenerationInterface (line 409)
self.left_panel.generate_requested.connect(self._start_generation)
```

### Security Integration
```python
# Lines 25-26: Import
from app.security.data_validation import sanitize_input, validate_length

# In _on_generate():
prompt = sanitize_input(
    self.prompt_input.toPlainText().strip(),
    max_length=2000
)
if not validate_length(prompt, min_len=1, max_len=2000):
    QMessageBox.warning(self, "Input Error", "Prompt too long/short")
    return
```

---

## 4. IMAGEGENERATIONRIGHTPANEL RELATIONSHIPS

### Class Definition
```python
class ImageGenerationRightPanel(QFrame):
    """Right panel for generated image display."""
    # Lines 180-395
```

### Component Structure
```
ImageGenerationRightPanel
├── Layout: QVBoxLayout
│   ├── Title: "GENERATED IMAGE"
│   │   └── Font: 14pt bold, TRON_GREEN
│   │
│   ├── image_display (QScrollArea)
│   │   ├── Purpose: Scrollable image container
│   │   ├── Contains: image_label (QLabel) for QPixmap
│   │   └── Zoom: Supports image scaling
│   │
│   ├── Controls Layout (QHBoxLayout)
│   │   ├── zoom_in_btn (QPushButton) - "🔍 Zoom In"
│   │   ├── zoom_out_btn (QPushButton) - "🔍 Zoom Out"
│   │   ├── save_btn (QPushButton) - "💾 Save"
│   │   └── copy_btn (QPushButton) - "📋 Copy"
│   │
│   └── metadata_text (QTextEdit)
│       ├── read_only: True
│       ├── max_height: 120px
│       └── content: Generation metadata (prompt, style, size, timestamp)
```

### Display Methods

#### show_generating()
```python
def show_generating(self):
    """Show generating state."""
    self.image_label.setText("⏳ Generating image...\nThis may take 20-60 seconds")
    self.image_label.setStyleSheet("color: #00ffff; font-size: 16pt;")
    self.current_image_path = None
    self._update_button_states()
```

#### display_image()
```python
def display_image(self, image_path: str, metadata: dict):
    """Display generated image with metadata."""
    # Load image
    pixmap = QPixmap(image_path)
    if pixmap.isNull():
        self.show_error("Failed to load image")
        return
    
    # Store path and pixmap
    self.current_image_path = image_path
    self.original_pixmap = pixmap
    self.current_zoom = 1.0
    
    # Display at original size
    self.image_label.setPixmap(pixmap)
    self.image_label.resize(pixmap.size())
    
    # Format metadata
    metadata_text = f"""
    **Prompt:** {metadata.get('prompt', 'N/A')}
    **Style:** {metadata.get('style', 'N/A')}
    **Size:** {metadata.get('size', 'N/A')}
    **Backend:** {metadata.get('backend', 'N/A')}
    **Generated:** {metadata.get('timestamp', 'N/A')}
    """
    self.metadata_text.setMarkdown(metadata_text)
    
    # Enable controls
    self._update_button_states()
```

#### show_error()
```python
def show_error(self, error_message: str):
    """Show error state."""
    self.image_label.setText(f"❌ Error:\n{error_message}")
    self.image_label.setStyleSheet("color: #ff0000; font-size: 14pt;")
    self.current_image_path = None
    self._update_button_states()
```

### Zoom Control Flow
```
User clicks zoom_in_btn
        ↓
_zoom_in() method called
        ↓
Increase zoom: self.current_zoom *= 1.2
        ↓
Scale pixmap: scaled_pixmap = self.original_pixmap.scaled(
    self.original_pixmap.size() * self.current_zoom,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation
)
        ↓
Update display: self.image_label.setPixmap(scaled_pixmap)
        ↓
Scroll area auto-adjusts to new size
```

### Save Flow
```
User clicks save_btn
        ↓
_save_image() method called
        ↓
Check if image loaded: if not self.current_image_path: return
        ↓
Open QFileDialog.getSaveFileName()
├── Default name: f"generated_image_{timestamp}.png"
├── Filter: "Images (*.png *.jpg *.jpeg)"
└── Returns: (save_path, selected_filter)
        ↓
If path selected:
├── Copy file: shutil.copy(self.current_image_path, save_path)
└── Show success: QMessageBox.information("Image saved successfully")
        ↓
If error:
└── Show error: QMessageBox.critical("Failed to save image")
```

### Copy Flow
```
User clicks copy_btn
        ↓
_copy_image() method called
        ↓
Check if image loaded: if not self.current_image_path: return
        ↓
Load pixmap: pixmap = QPixmap(self.current_image_path)
        ↓
Copy to clipboard: QApplication.clipboard().setPixmap(pixmap)
        ↓
Show status: self.metadata_text.append("\n✅ Image copied to clipboard")
```

---

## 5. IMAGEGENERATIONINTERFACE RELATIONSHIPS

### Class Definition
```python
class ImageGenerationInterface(QWidget):
    """Main container for image generation UI."""
    # Lines 395-450
```

### Component Structure
```
ImageGenerationInterface
├── Layout: QHBoxLayout (horizontal split)
│   ├── left_panel (ImageGenerationLeftPanel) - stretch=1
│   └── right_panel (ImageGenerationRightPanel) - stretch=2
│
├── generator: ImageGenerator (core system instance)
└── worker: ImageGenerationWorker | None (current generation task)
```

### Initialization Flow
```
ImageGenerationInterface.__init__()
        ↓
Create ImageGenerator instance from core
        ↓
setup_ui()
├── Create horizontal layout
├── Create left panel (prompt input)
├── Create right panel (image display)
├── Add panels to layout (1:2 ratio)
└── Connect left_panel.generate_requested signal
        ↓
Interface ready for user interaction
```

### Generation Flow (Complete)
```
USER ACTION: Clicks "GENERATE IMAGE" in left panel
        ↓
ImageGenerationLeftPanel.generate_requested.emit(prompt, style)
        ↓
ImageGenerationInterface._start_generation(prompt, style_value)
        ↓
Convert style string to ImageStyle enum:
style = ImageStyle(style_value)
        ↓
Update right panel: show_generating()
        ↓
Create worker thread:
worker = ImageGenerationWorker(self.generator, prompt, style)
        ↓
Connect worker signals:
├── worker.finished.connect(self._on_generation_complete)
└── worker.progress.connect(self.left_panel.set_status)
        ↓
Start worker: worker.start()
        ↓
UI remains responsive during 20-60s generation
        ↓
Worker emits progress updates:
├── "Initializing generation..."
├── "Generating with Stable Diffusion..."
└── "Processing result..."
        ↓
PATH 1: Success
    ├── worker.finished.emit({"success": True, "filepath": "...", ...})
    ├── _on_generation_complete(result) called
    ├── left_panel.set_status("✅ Generation complete!")
    ├── right_panel.display_image(result["filepath"], result)
    └── left_panel.set_generating(False)
        ↓
PATH 2: Error
    ├── worker.finished.emit({"success": False, "error": "...", "filtered": True/False})
    ├── _on_generation_complete(result) called
    ├── If filtered: left_panel.set_status("🚫 Blocked: {error}", is_error=True)
    ├── Else: left_panel.set_status("❌ Error: {error}", is_error=True)
    ├── right_panel.show_error(error_msg)
    └── left_panel.set_generating(False)
        ↓
Worker thread terminates
        ↓
Interface ready for next generation
```

---

## 6. SIGNAL/SLOT ARCHITECTURE

### Signal Chain Diagram
```
┌─────────────────────────────────────────────────────────┐
│         ImageGenerationLeftPanel                         │
│    (User Input: prompt, style, size, backend)           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ generate_btn.clicked
                       ▼
              _on_generate() validates input
                       │
                       │ generate_requested.emit(prompt, style)
                       ▼
┌─────────────────────────────────────────────────────────┐
│        ImageGenerationInterface                          │
│   (Coordinates worker + panels)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ _start_generation(prompt, style)
                       ▼
              Create ImageGenerationWorker
                       │
                       ├── worker.progress → left_panel.set_status()
                       └── worker.finished → _on_generation_complete()
                       │
                       │ worker.start()
                       ▼
┌─────────────────────────────────────────────────────────┐
│       ImageGenerationWorker (QThread)                    │
│   (Background: 20-60s API call)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ run() executes generator.generate()
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
    SUCCESS PATH               ERROR PATH
         │                            │
         │ finished.emit(            │ finished.emit(
         │   {"success": True, ...}) │   {"success": False, ...})
         │                            │
         └─────────────┬──────────────┘
                       │
                       ▼
        _on_generation_complete(result)
                       │
         ┌─────────────┴──────────────┐
         │                            │
         ▼                            ▼
┌──────────────────┐        ┌──────────────────┐
│  Left Panel      │        │  Right Panel     │
│  (Status Update) │        │  (Image Display) │
└──────────────────┘        └──────────────────┘
```

### Signal Connections (Lines 409, 427-428)
```python
# In ImageGenerationInterface.setup_ui()
self.left_panel.generate_requested.connect(self._start_generation)

# In ImageGenerationInterface._start_generation()
self.worker.finished.connect(self._on_generation_complete)
self.worker.progress.connect(self.left_panel.set_status)
```

---

## 7. CORE SYSTEM INTEGRATION

### ImageGenerator Integration
```python
# From app.core.image_generator

# ImageGenerator provides:
class ImageGenerator:
    def generate(
        self,
        prompt: str,
        style: ImageStyle = ImageStyle.PHOTOREALISTIC,
        size: str = "512x512",
        backend: ImageGenerationBackend = ImageGenerationBackend.HUGGINGFACE,
    ) -> dict:
        """Generate image with content filtering and safety checks."""
        # Returns: {"success": True/False, "filepath": "...", "metadata": {...}}
```

### Content Filtering (Core System)
```python
# In ImageGenerator.generate()
1. Check content filter: is_safe, reason = self.check_content_filter(prompt)
   ├── 15 blocked keywords: "nude", "naked", "violence", "blood", etc.
   └── If unsafe: return {"success": False, "filtered": True, "error": reason}

2. Add safety negative prompt:
   negative_prompt = "nsfw, nude, naked, violence, blood, gore, weapons"

3. Call backend (Hugging Face or OpenAI)
   ├── Hugging Face: stabilityai/stable-diffusion-2-1
   └── OpenAI: dall-e-3

4. Save result to generated_images/ directory

5. Store in generation history (JSON persistence)

6. Return result dict with filepath and metadata
```

---

## 8. STYLE SYSTEM

### Available Styles (ImageStyle Enum)
```python
# From app.core.image_generator.ImageStyle

class ImageStyle(Enum):
    PHOTOREALISTIC = "photorealistic"
    DIGITAL_ART = "digital_art"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    ANIME = "anime"
    SKETCH = "sketch"
    ABSTRACT = "abstract"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MINIMALIST = "minimalist"
```

### Style Application
```python
# ImageGenerator adds style to prompt:
styled_prompt = f"{prompt}, {style.value} style"

# Examples:
# "A cat on a roof, photorealistic style"
# "A cat on a roof, anime style"
# "A cat on a roof, cyberpunk style"
```

---

## 9. PARENT INTEGRATION

### In LeatherBookInterface [[src/app/gui/leather_book_interface.py]] (Lines 187-193)
```python
def switch_to_image_generation(self):
    """Switch to image generation interface."""
    from app.gui.image_generation import ImageGenerationInterface
    
    image_gen = ImageGenerationInterface()
    
    self._set_stack_page(image_gen, 2)
    # Adds to QStackedWidget page 2, replaces existing content
```

### Navigation Flow
```
LeatherBookDashboard (page 1)
        ↓
User clicks "🎨 GENERATE IMAGES" button
        ↓
ProactiveActionsPanel.image_gen_requested.emit()
        ↓
LeatherBookInterface.switch_to_image_generation()
        ↓
ImageGenerationInterface created and shown (page 2)
        ↓
User generates images
        ↓
User navigates back (via dashboard button or back action)
        ↓
Interface.switch_to_dashboard() → page 1
        ↓
ImageGenerationInterface destroyed (Qt parent-child ownership)
```

---

## 10. FILE SYSTEM RELATIONSHIPS

### Generated Images Storage
```
Project-AI-main/
└── generated_images/
    ├── generated_20260420_123456_abc123.png
    ├── generated_20260420_123512_def456.png
    └── ...
```

### Image Naming Convention
```python
# In ImageGenerator.generate()
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_id = hashlib.md5(prompt.encode()).hexdigest()[:6]
filename = f"generated_{timestamp}_{unique_id}.png"
filepath = os.path.join("generated_images", filename)
```

### Generation History (JSON)
```json
// data/image_generation/history.json
{
  "generations": [
    {
      "timestamp": "2026-04-20T12:34:56",
      "prompt": "A cat on a roof, photorealistic style",
      "style": "photorealistic",
      "size": "512x512",
      "backend": "huggingface",
      "filepath": "generated_images/generated_20260420_123456_abc123.png",
      "success": true
    }
  ]
}
```

---

## 11. ERROR HANDLING PATTERNS

### Input Validation Errors
```python
# In ImageGenerationLeftPanel._on_generate()
if not prompt:
    QMessageBox.warning(self, "Input Required", "Please enter a prompt")
    return

if not validate_length(prompt, min_len=1, max_len=2000):
    QMessageBox.warning(self, "Input Error", "Prompt too long")
    return
```

### Content Filter Errors
```python
# In ImageGenerator.generate()
is_safe, reason = self.check_content_filter(prompt)
if not is_safe:
    return {
        "success": False,
        "filtered": True,
        "error": reason
    }

# In ImageGenerationInterface._on_generation_complete()
if result.get("filtered"):
    self.left_panel.set_status(f"🚫 Blocked: {error_msg}", is_error=True)
```

### Backend API Errors
```python
# In ImageGenerationWorker.run()
try:
    result = self.generator.generate(self.prompt, self.style)
    self.finished.emit(result)
except Exception as e:
    logger.error("Generation worker error: %s", e)
    self.finished.emit({"success": False, "error": str(e)})
```

---

## 12. PERFORMANCE CONSIDERATIONS

### Thread Safety
- **Worker thread**: All heavy computation (API calls) in background
- **Signal emission**: Thread-safe via PyQt6 event loop
- **UI updates**: Only in main thread via signal callbacks

### UI Responsiveness
```python
# CORRECT: UI updates in main thread via signals
worker.progress.connect(self.left_panel.set_status)

# WRONG: Direct UI update from worker thread (would crash)
# self.left_panel.set_status("Generating...")  # In worker.run()
```

### Memory Management
- Original pixmap stored for zoom operations
- Only one scaled pixmap in memory at a time
- Worker self-destructs after completion (QThread behavior)

---

## 13. TESTING STRATEGIES

### Unit Tests for Components
```python
def test_left_panel_signal_emission():
    """Test generate_requested signal emission."""
    panel = ImageGenerationLeftPanel()
    
    received = []
    panel.generate_requested.connect(
        lambda p, s: received.append((p, s))
    )
    
    panel.prompt_input.setText("Test prompt")
    panel.style_combo.setCurrentText("photorealistic")
    panel.generate_btn.click()
    
    assert len(received) == 1
    assert received[0] == ("Test prompt", "photorealistic")

def test_worker_success():
    """Test successful image generation."""
    generator = Mock()
    generator.generate.return_value = {
        "success": True,
        "filepath": "test.png",
        "metadata": {}
    }
    
    worker = ImageGenerationWorker(generator, "Test", ImageStyle.PHOTOREALISTIC)
    
    results = []
    worker.finished.connect(results.append)
    
    worker.run()
    
    assert len(results) == 1
    assert results[0]["success"] is True

def test_content_filter():
    """Test content filtering in generation."""
    panel = ImageGenerationLeftPanel()
    panel.prompt_input.setText("nude person")  # Should be filtered
    
    # Should show error when generation attempted
    # (Actual filtering done in core ImageGenerator)
```

### Integration Tests
```python
def test_end_to_end_generation(qtbot):
    """Test complete generation flow."""
    interface = ImageGenerationInterface()
    qtbot.addWidget(interface)
    
    # Mock generator for fast test
    interface.generator.generate = Mock(return_value={
        "success": True,
        "filepath": "test.png",
        "metadata": {"prompt": "Test"}
    })
    
    # Enter prompt
    interface.left_panel.prompt_input.setText("Test prompt")
    
    # Click generate
    qtbot.mouseClick(
        interface.left_panel.generate_btn,
        Qt.MouseButton.LeftButton
    )
    
    # Wait for worker completion
    qtbot.wait(1000)
    
    # Verify image displayed
    assert interface.right_panel.current_image_path == "test.png"
```

---

## SUMMARY

**ImageGenerationInterface** provides a production-grade image generation UI with:

**3 Core Components:**
1. **ImageGenerationWorker** [[src/app/gui/image_generation.py]] (QThread)
   - Async image generation (20-60s operations)
   - Thread-safe signal emission
   - Prevents UI blocking

2. **ImageGenerationLeftPanel** [[src/app/gui/image_generation.py]] (Prompt Input)
   - Tron-themed interface (TRON_GREEN, TRON_CYAN)
   - Prompt input (QTextEdit, max 2000 chars)
   - 10 style options (photorealistic, anime, cyberpunk, etc.)
   - Size selection (512x512, 768x768, 1024x1024)
   - Backend choice (Hugging Face Stable Diffusion 2.1, OpenAI DALL-E 3)
   - Status updates with progress messages

3. **ImageGenerationRightPanel** [[src/app/gui/image_generation.py]] (Image Display)
   - Scrollable image display with zoom controls
   - Save image (QFileDialog)
   - Copy to clipboard
   - Metadata display (prompt, style, size, timestamp)

**Key Features:**
- **Content Filtering**: 15 blocked keywords, safety negative prompts
- **Dual Backend**: Hugging Face (default) + OpenAI DALL-E 3
- **Style Presets**: 10 artistic styles with prompt enhancement
- **Async Architecture**: Non-blocking UI during generation
- **Security**: Input sanitization, length validation
- **Persistence**: Generation history stored in JSON

**Signal Architecture:**
- **generate_requested**: Left panel → Interface (prompt + style)
- **finished**: Worker → Interface (result dict)
- **progress**: Worker → Left panel (status updates)

**Integration:**
- **Parent**: LeatherBookInterface (page 2 navigation)
- **Core System**: ImageGenerator (src/app/core/image_generator.py)
- **File System**: generated_images/ directory + history.json
- **Security**: data_validation module (sanitize_input, validate_length)

**Performance:**
- Thread-safe: All UI updates via main thread signals
- Memory efficient: Single scaled pixmap, original cached for zoom
- Responsive: UI never freezes during 20-60s generation

**Total UI Components:**
- 2 panels (left input, right display)
- 1 worker thread
- 8 buttons (generate, zoom in/out, save, copy, style/size/backend combos)
- 3 text inputs (prompt, status, metadata)
- 2 signals (generate_requested, finished)


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/gui/image_generation.md|Image Generation]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/image_generation.py]] - Implementation file
- [[src/app/core/image_generator.py]] - Implementation file


---

## RELATED SYSTEMS

### Core AI Integration

| Component | Core AI System | Integration | Reference |
|-----------|----------------|-------------|-----------|
| **ImageGenerationWorker** | Core ImageGenerator | Async generation (20-60s) | Section 2 (Worker) |
| **Content Filtering** | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Validates prompts don't violate laws | Section 4 (filtering) |
| **Override System** | [[../core-ai/06-CommandOverride-Relationship-Map\|CommandOverride]] | Admin can bypass content filters | Section 4 (admin) |
| **History Persistence** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Stores generation metadata | Section 5 (persistence) |

### Agent System Integration

| Operation | Agent System | Purpose | Reference |
|-----------|--------------|---------|-----------|
| **Prompt Validation** | [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation\|ValidatorAgent]] | Sanitizes user input | Section 3 (input) |
| **Content Safety** | [[../agents/VALIDATION_CHAINS#layer-2-oversightagent-compliance-validation\|OversightAgent]] | Checks 15 blocked keywords | Section 4 (safety) |
| **Ethical Review** | [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws]] | Prevents harmful imagery | Section 4 (ethics) |
| **Async Coordination** | [[../agents/AGENT_ORCHESTRATION#lifecycle-state-management\|Agent Lifecycle]] | Worker thread management | Section 2 (async) |

### Content Safety Pipeline

```
User Prompt → sanitize_input() → 
[[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent.validate_schema()]] → 
check_content_filter() (15 keywords) → 
[[../agents/VALIDATION_CHAINS#layer-2-oversightagent-compliance-validation|OversightAgent.check_policy()]] → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|FourLaws.validate_action()]] → 
Generate Image or Reject
```

### Blocked Content Keywords

Protected by [[../core-ai/01-FourLaws-Relationship-Map#first-law|First Law]] (prevent human harm):
- Violence-related: violence, blood, gore, weapons, assault, murder
- Adult content: nude, naked, sexual, explicit
- Disturbing: death, suicide, self-harm, hate

Override requires [[../core-ai/06-CommandOverride-Relationship-Map#master-password|Master Password]].

### Generation Workflow

```
Prompt Input (LeftPanel) → validate → 
ImageGenerationWorker.run() → 
[[../agents/VALIDATION_CHAINS|Validation Chain]] → 
Backend API Call (HF/OpenAI) → 
Save Image → history.json → 
finished.emit() → Display (RightPanel)
```

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with Core AI and Agent systems