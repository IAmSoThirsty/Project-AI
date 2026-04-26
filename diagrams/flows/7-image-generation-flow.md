# Image Generation Flow

## Overview
This diagram illustrates the complete AI image generation workflow with dual backend support (Hugging Face Stable Diffusion and OpenAI DALL-E), content filtering, style presets, and async generation with GUI integration.

## Flow Diagram

```mermaid
flowchart TD
    Start([Image Generation Request]) --> UIInput[User Input via GUI<br/>ImageGenerationLeftPanel]
    UIInput --> ValidatePrompt{Prompt<br/>Valid?}
    ValidatePrompt -->|Empty| PromptError[❌ Empty Prompt Error<br/>Show error message]
    ValidatePrompt -->|Valid| ContentFilter[Content Filter Check<br/>15 blocked keywords]
    
    ContentFilter --> FilterScan{Blocked<br/>Keywords?}
    FilterScan -->|Found| FilterBlock[❌ Content Blocked<br/>Show explanation]
    FilterScan -->|None| CheckOverride{Command<br/>Override Active?}
    
    CheckOverride -->|Yes| BypassFilter[⚠️ Override: Skip Filter<br/>Log bypass action]
    CheckOverride -->|No| SafetyNegative[Add Safety Negative Prompts<br/>violence, explicit, gore]
    
    BypassFilter --> SelectStyle
    SafetyNegative --> SelectStyle[Select Style Preset<br/>10 available styles]
    
    SelectStyle --> StyleChoice{Style<br/>Selection}
    StyleChoice -->|Photorealistic| PhotoStyle[Style: photorealistic<br/>prompt + 8k, detailed, realistic]
    StyleChoice -->|Digital Art| DigitalStyle[Style: digital_art<br/>prompt + digital painting, artstation]
    StyleChoice -->|Oil Painting| OilStyle[Style: oil_painting<br/>prompt + oil on canvas, impressionist]
    StyleChoice -->|Watercolor| WaterStyle[Style: watercolor<br/>prompt + watercolor, soft colors]
    StyleChoice -->|Anime| AnimeStyle[Style: anime<br/>prompt + anime style, manga]
    StyleChoice -->|Cyberpunk| CyberStyle[Style: cyberpunk<br/>prompt + neon, futuristic, sci-fi]
    StyleChoice -->|Fantasy| FantasyStyle[Style: fantasy<br/>prompt + magical, epic, dramatic]
    StyleChoice -->|Minimalist| MinimalStyle[Style: minimalist<br/>prompt + clean, simple, modern]
    StyleChoice -->|Abstract| AbstractStyle[Style: abstract<br/>prompt + abstract art, geometric]
    StyleChoice -->|Cinematic| CinemaStyle[Style: cinematic<br/>prompt + film still, dramatic lighting]
    
    PhotoStyle --> BuildPrompt
    DigitalStyle --> BuildPrompt
    OilStyle --> BuildPrompt
    WaterStyle --> BuildPrompt
    AnimeStyle --> BuildPrompt
    CyberStyle --> BuildPrompt
    FantasyStyle --> BuildPrompt
    MinimalStyle --> BuildPrompt
    AbstractStyle --> BuildPrompt
    CinemaStyle --> BuildPrompt[Build Enhanced Prompt<br/>base + style modifiers]
    
    BuildPrompt --> SelectBackend{Backend<br/>Selection}
    SelectBackend -->|Hugging Face| HFRoute[Hugging Face Backend<br/>Stable Diffusion 2.1]
    SelectBackend -->|OpenAI| OpenAIRoute[OpenAI Backend<br/>DALL-E 3]
    
    HFRoute --> CheckHFKey{HF API Key<br/>Configured?}
    CheckHFKey -->|No| HFKeyError[❌ Missing HF API Key<br/>Prompt for configuration]
    CheckHFKey -->|Yes| SelectSize[Select Image Size<br/>512x512, 768x768, 1024x1024]
    
    OpenAIRoute --> CheckOpenAIKey{OpenAI Key<br/>Configured?}
    CheckOpenAIKey -->|No| OpenAIKeyError[❌ Missing OpenAI Key<br/>Prompt for configuration]
    CheckOpenAIKey -->|Yes| SelectSize
    
    SelectSize --> SizeChoice{Size<br/>Selection}
    SizeChoice -->|512x512| Size512[Resolution: 512x512<br/>Fast generation]
    SizeChoice -->|768x768| Size768[Resolution: 768x768<br/>Balanced quality]
    SizeChoice -->|1024x1024| Size1024[Resolution: 1024x1024<br/>High quality]
    
    Size512 --> CreateWorker
    Size768 --> CreateWorker
    Size1024 --> CreateWorker[Create Worker Thread<br/>ImageGenerationWorker]
    
    CreateWorker --> StartWorker[Start Worker Thread<br/>QThread.start]
    StartWorker --> ShowProgress[Show Progress Dialog<br/>Generating... Please wait]
    
    ShowProgress --> WorkerGenerate{Backend<br/>Execution}
    WorkerGenerate -->|Hugging Face| HFGenerate[Generate via HF API<br/>POST to Hugging Face Inference]
    WorkerGenerate -->|OpenAI| OpenAIGenerate[Generate via OpenAI API<br/>POST to DALL-E 3 endpoint]
    
    HFGenerate --> HFRequest[Build HF Request<br/>model: stabilityai/stable-diffusion-2-1]
    HFRequest --> HFRetry[Send with Retry Logic<br/>Max 3 retries, exponential backoff]
    HFRetry --> HFResponse{HF Response<br/>Status}
    
    HFResponse -->|429 Rate Limit| HFWait[Wait for Retry-After<br/>Honor rate limit header]
    HFResponse -->|502/503 Error| HFBackoff[Exponential Backoff<br/>0.8s * 2^attempt]
    HFResponse -->|200 Success| HFDecode[Decode Image<br/>Base64 → bytes]
    
    HFWait --> HFRetry
    HFBackoff --> HFRetry
    HFDecode --> SaveImage
    
    OpenAIGenerate --> OpenAIRequest[Build OpenAI Request<br/>model: dall-e-3, quality: hd]
    OpenAIRequest --> OpenAIRetry[Send with Retry Logic<br/>Max 3 retries, exponential backoff]
    OpenAIRetry --> OpenAIResponse{OpenAI<br/>Response}
    
    OpenAIResponse -->|Rate Limit| OpenAIWait[Wait for Retry<br/>Respect rate limits]
    OpenAIResponse -->|Error| OpenAIBackoff[Exponential Backoff<br/>0.8s * 2^attempt]
    OpenAIResponse -->|Success| OpenAIDownload[Download Image<br/>GET from URL]
    
    OpenAIWait --> OpenAIRetry
    OpenAIBackoff --> OpenAIRetry
    OpenAIDownload --> SaveImage[Save Image to Disk<br/>data/images/img_{uuid}.png]
    
    SaveImage --> SanitizeFilename[Sanitize Filename<br/>Remove special characters]
    SanitizeFilename --> WriteToDisk[Write to File<br/>Binary write with fsync]
    WriteToDisk --> VerifyImage{Image<br/>Valid?}
    
    VerifyImage -->|No| ImageError[❌ Image Corruption<br/>Retry generation]
    VerifyImage -->|Yes| CreateThumbnail[Create Thumbnail<br/>256x256 preview]
    
    CreateThumbnail --> SaveHistory[Save to History<br/>data/image_generation/history.json]
    SaveHistory --> UpdateMetadata[Update Metadata<br/>prompt, style, backend, timestamp]
    
    UpdateMetadata --> EmitSignal[Emit Signal<br/>image_generated.emit]
    EmitSignal --> UpdateGUI[Update GUI<br/>Display image in right panel]
    UpdateGUI --> DisplayImage[Display Image<br/>QPixmap with zoom controls]
    
    DisplayImage --> ShowMetadata[Show Metadata Panel<br/>Prompt, style, size, backend, time]
    ShowMetadata --> EnableActions[Enable Actions<br/>Save, Copy, Delete, Regenerate]
    EnableActions --> CloseProgress[Close Progress Dialog<br/>Hide generating message]
    
    CloseProgress --> Success([✅ Image Generated<br/>Display complete])
    
    ImageError --> RetryCount{Retry Count<br/>< 3?}
    RetryCount -->|Yes| WorkerGenerate
    RetryCount -->|No| GenerationFailed[❌ Generation Failed<br/>Show error dialog]
    
    PromptError --> End([❌ Generation Cancelled])
    FilterBlock --> End
    HFKeyError --> End
    OpenAIKeyError --> End
    GenerationFailed --> End
    
    style Start fill:#00ff00,stroke:#00ffff,stroke-width:3px,color:#000
    style Success fill:#00ff00,stroke:#00ffff,stroke-width:3px,color:#000
    style FilterBlock fill:#ff0000,stroke:#ff00ff,stroke-width:2px,color:#fff
    style GenerationFailed fill:#ff0000,stroke:#ff00ff,stroke-width:2px,color:#fff
    style ContentFilter fill:#ffff00,stroke:#ff8800,stroke-width:2px,color:#000
    style HFGenerate fill:#00ffff,stroke:#0088ff,stroke-width:2px,color:#000
    style OpenAIGenerate fill:#00ffff,stroke:#0088ff,stroke-width:2px,color:#000
```

## Dual Backend Architecture

### Hugging Face Backend (Default)
**Model**: `stabilityai/stable-diffusion-2-1`

**Endpoint**: `https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1`

**Request Format**:
```python
{
    "inputs": "enhanced_prompt with style modifiers",
    "parameters": {
        "negative_prompt": "violence, explicit, gore, nsfw",
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "width": 512,
        "height": 512
    }
}
```

**Response**: Base64-encoded PNG image

**Performance**:
- **Generation Time**: 20-60 seconds (model loading + inference)
- **Rate Limit**: 1000 requests/day (free tier)
- **Cost**: Free (with API key)
- **Quality**: Good (v2.1 model)

### OpenAI Backend (Premium)
**Model**: `dall-e-3`

**Endpoint**: `https://api.openai.com/v1/images/generations`

**Request Format**:
```python
{
    "model": "dall-e-3",
    "prompt": "enhanced_prompt with style modifiers",
    "n": 1,
    "size": "1024x1024",
    "quality": "hd",
    "response_format": "url"
}
```

**Response**: URL to hosted image (downloaded immediately)

**Performance**:
- **Generation Time**: 10-30 seconds
- **Rate Limit**: 50 images/minute
- **Cost**: $0.04 per image (1024x1024 HD)
- **Quality**: Excellent (DALL-E 3)

## Content Filtering

### Blocked Keywords (15 Categories)
```python
BLOCKED_KEYWORDS = [
    # Violence
    "gore", "blood", "violence", "weapon", "death",
    # Sexual
    "nude", "naked", "explicit", "porn", "nsfw",
    # Illegal
    "drug", "cocaine", "meth", "heroin",
    # Harmful
    "suicide", "self-harm", "cutting",
    # Other
    "copyright_violation", "trademark_infringement"
]
```

### Filter Implementation
```python
def check_content_filter(prompt: str) -> tuple[bool, str]:
    """Check if prompt contains blocked keywords."""
    prompt_lower = prompt.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in prompt_lower:
            return False, f"Blocked keyword: {keyword}"
    return True, "Content safe"
```

### Safety Negative Prompts
Automatically added to all generations:
```python
SAFETY_NEGATIVE = "violence, explicit content, gore, nsfw, nudity, blood, weapons, illegal activities, harmful content"
```

## Style Presets

### 1. Photorealistic
**Modifiers**: `8k uhd, photorealistic, detailed, professional photography, sharp focus, studio lighting`

**Best For**: Product photos, portraits, realistic scenes

### 2. Digital Art
**Modifiers**: `digital art, digital painting, trending on artstation, highly detailed, vibrant colors`

**Best For**: Character art, concept art, fantasy illustrations

### 3. Oil Painting
**Modifiers**: `oil painting, oil on canvas, impressionist style, brush strokes, classical art`

**Best For**: Portraits, landscapes, classical compositions

### 4. Watercolor
**Modifiers**: `watercolor painting, soft colors, delicate, pastel tones, artistic`

**Best For**: Nature scenes, flowers, dreamy compositions

### 5. Anime
**Modifiers**: `anime style, manga, cel shaded, vibrant, japanese animation`

**Best For**: Characters, action scenes, stylized art

### 6. Cyberpunk
**Modifiers**: `cyberpunk, neon lights, futuristic, sci-fi, dystopian, high tech low life`

**Best For**: City scenes, technology, dystopian settings

### 7. Fantasy
**Modifiers**: `fantasy art, magical, epic, dramatic lighting, mystical, ethereal`

**Best For**: Dragons, castles, magical creatures, epic scenes

### 8. Minimalist
**Modifiers**: `minimalist, clean lines, simple, modern, geometric, flat design`

**Best For**: Logos, icons, simple compositions

### 9. Abstract
**Modifiers**: `abstract art, geometric shapes, colorful, modern art, non-representational`

**Best For**: Patterns, textures, artistic expressions

### 10. Cinematic
**Modifiers**: `cinematic, film still, movie scene, dramatic lighting, widescreen, film grain`

**Best For**: Dramatic scenes, storytelling, atmospheric images

## Async Generation (QThread)

### Worker Thread Implementation
```python
from PyQt6.QtCore import QThread, pyqtSignal

class ImageGenerationWorker(QThread):
    """Worker thread for async image generation."""
    image_generated = pyqtSignal(str, dict)  # path, metadata
    generation_failed = pyqtSignal(str)       # error message
    progress_updated = pyqtSignal(int)        # progress percentage
    
    def __init__(self, generator, prompt, style, backend, size):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.style = style
        self.backend = backend
        self.size = size
    
    def run(self):
        """Execute generation in background thread."""
        try:
            self.progress_updated.emit(10)  # Starting
            
            # Generate image
            image_path, metadata = self.generator.generate(
                prompt=self.prompt,
                style=self.style,
                backend=self.backend,
                size=self.size,
                progress_callback=self.progress_updated.emit
            )
            
            self.progress_updated.emit(100)  # Complete
            self.image_generated.emit(image_path, metadata)
        except Exception as e:
            self.generation_failed.emit(str(e))
```

### Progress Tracking
```python
def show_progress_dialog(parent):
    """Show progress dialog during generation."""
    dialog = QProgressDialog(
        "Generating image...\nThis may take 20-60 seconds.",
        "Cancel",
        0, 100,
        parent
    )
    dialog.setWindowTitle("Image Generation")
    dialog.setWindowModality(Qt.WindowModal)
    dialog.show()
    return dialog
```

## GUI Integration

### Left Panel (Input)
```python
class ImageGenerationLeftPanel(QWidget):
    """Left panel for prompt input and settings."""
    generate_requested = pyqtSignal(str, str, str, str)  # prompt, style, backend, size
    
    def __init__(self):
        super().__init__()
        # Prompt text edit
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the image you want to generate...")
        
        # Style selector
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "Photorealistic", "Digital Art", "Oil Painting",
            "Watercolor", "Anime", "Cyberpunk", "Fantasy",
            "Minimalist", "Abstract", "Cinematic"
        ])
        
        # Backend selector
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["Hugging Face", "OpenAI DALL-E"])
        
        # Size selector
        self.size_combo = QComboBox()
        self.size_combo.addItems(["512x512", "768x768", "1024x1024"])
        
        # Generate button
        self.generate_btn = QPushButton("🎨 Generate Image")
        self.generate_btn.clicked.connect(self._on_generate)
```

### Right Panel (Display)
```python
class ImageGenerationRightPanel(QWidget):
    """Right panel for image display and actions."""
    
    def __init__(self):
        super().__init__()
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        
        # Zoom controls
        self.zoom_in_btn = QPushButton("🔍 Zoom In")
        self.zoom_out_btn = QPushButton("🔍 Zoom Out")
        self.zoom_fit_btn = QPushButton("⬜ Fit to Window")
        
        # Action buttons
        self.save_btn = QPushButton("💾 Save As...")
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.delete_btn = QPushButton("🗑️ Delete")
        self.regenerate_btn = QPushButton("🔄 Regenerate")
        
        # Metadata display
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
```

## Error Handling

### API Errors
```python
def handle_api_error(response: requests.Response) -> str:
    """Handle API error responses."""
    if response.status_code == 429:
        return "Rate limit exceeded. Please wait before generating again."
    elif response.status_code == 401:
        return "Invalid API key. Please check your configuration."
    elif response.status_code == 400:
        return "Invalid request. Please check your prompt and settings."
    elif response.status_code >= 500:
        return "Server error. Please try again later."
    else:
        return f"API error: {response.status_code} - {response.text}"
```

### Network Errors
```python
def handle_network_error(error: Exception) -> str:
    """Handle network exceptions."""
    if isinstance(error, requests.Timeout):
        return "Request timed out. Please check your internet connection."
    elif isinstance(error, requests.ConnectionError):
        return "Connection failed. Please check your internet connection."
    else:
        return f"Network error: {str(error)}"
```

## Performance Optimization

### Caching Strategy
- **Duplicate Prompts**: Cache identical prompts for 1 hour
- **Thumbnail Generation**: Lazy loading on scroll
- **History Pagination**: Load 20 entries at a time

### Memory Management
- **Image Compression**: PNG compression level 6 (balanced)
- **Thumbnail Size**: 256x256 (reduces memory by ~95%)
- **History Limit**: Keep 100 most recent images, archive older

### Network Optimization
- **Connection Pooling**: Reuse HTTP connections
- **Retry Logic**: Exponential backoff with jitter
- **Timeout Configuration**: 60s read timeout, 30s connect timeout

## Persistence

### History Storage
```json
{
  "history": [
    {
      "id": "uuid-v4",
      "prompt": "A cyberpunk cityscape at night",
      "enhanced_prompt": "A cyberpunk cityscape at night, neon lights, futuristic...",
      "style": "cyberpunk",
      "backend": "huggingface",
      "size": "512x512",
      "image_path": "data/images/img_001.png",
      "thumbnail_path": "data/images/thumbnails/img_001_thumb.png",
      "generated_at": "2024-01-15T10:30:00Z",
      "generation_time_ms": 45000,
      "content_filtered": false
    }
  ]
}
```

### Cleanup Policy
- **Image Retention**: 30 days (configurable)
- **Orphaned Files**: Clean up images not in history
- **Thumbnail Regeneration**: On-demand if missing
