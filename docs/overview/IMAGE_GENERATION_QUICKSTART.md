# Image Generation Quick Start Guide

## Setup (One-Time)

### 1. Get API Keys

**Hugging Face** (Required for Stable Diffusion):

1. Visit https://huggingface.co/settings/tokens
2. Create account if needed
3. Click "New token"
4. Name: "Project-AI"
5. Type: Read
6. Click "Generate"
7. Copy the token (starts with `hf_`)

**OpenAI** (Optional for DALL-E 3):

1. Visit https://platform.openai.com/api-keys
2. Create account if needed
3. Click "Create new secret key"
4. Name: "Project-AI"
5. Copy the key (starts with `sk-`)
6. **Note**: DALL-E 3 requires paid plan

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

### 1. Launch Application

```powershell
# From project root
python -m src.app.main
```

### 2. Navigate to Image Generation

1. **Login** to the application
2. You'll see the **Dashboard** (6-zone layout)
3. Look at **top-right panel** ("Proactive Actions")
4. Click **"🎨 GENERATE IMAGES"** button

### 3. Generate Your First Image

**Left Page (Prompt Input)**:

1. **Enter prompt**: Type your image description
   - Example: "a cyberpunk city at night with neon lights"
2. **Select style**: Choose from dropdown
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

3. **Select size**: Choose image dimensions
   - 256x256 (fast, low quality)
   - 512x512 (balanced, recommended)
   - 768x768 (slower, higher quality)
   - 1024x1024 (slowest, highest quality)

4. **Select backend**:
   - Hugging Face (free, Stable Diffusion 2.1)
   - OpenAI (paid, DALL-E 3, highest quality)

5. **Click "Generate"**

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
2. Verify key format: `HUGGINGFACE_API_KEY=hf_...`
3. Restart application after editing .env

### "Generation failed: 401 Unauthorized"

**Problem**: Invalid API key

**Solution**:

1. Regenerate token at https://huggingface.co/settings/tokens
2. Update `.env` with new key
3. Restart application

### "Generation failed: 503 Service Unavailable"

**Problem**: Hugging Face API overloaded

**Solution**:

1. Wait 1-2 minutes
2. Try again
3. Try different time of day (less traffic)

### "Content filter: blocked keyword detected"

**Problem**: Prompt contains forbidden word

**Solution**:

1. Rephrase prompt without blocked keyword
2. Use synonyms or alternative descriptions
3. Check Content Safety section above

### Image Takes Forever

**Problem**: Large image size or slow backend

**Solution**:

1. Try 512x512 instead of 1024x1024
2. Hugging Face typically faster than DALL-E
3. Wait up to 60 seconds before retrying

### Image Not Displayed

**Problem**: Generation succeeded but not showing

**Solution**:

1. Check right page is visible
2. Try zooming to 100%
3. Check `data/generated_images/` folder
4. Restart application

## Advanced Usage

### Backend Comparison

| Feature       | Hugging Face | OpenAI DALL-E 3    |
| ------------- | ------------ | ------------------ |
| Cost          | **Free**     | Paid plan required |
| Speed         | 20-40 sec    | 30-60 sec          |
| Quality       | Good         | **Excellent**      |
| Max Size      | 768x768      | **1024x1024**      |
| Styles        | All presets  | All presets        |
| Prompt Length | 77 tokens    | **Unlimited**      |

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
2. Wait for completion
3. Modify prompt slightly
4. Generate again
5. Repeat as needed

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
2. **Test API keys**: Use Hugging Face web UI to verify token
3. **Review documentation**: `IMAGE_GENERATION_RESTORATION.md`
4. **Check GitHub issues**: Report bugs or request features

## Next Steps

Once comfortable with basic generation:

1. Experiment with style presets
2. Try different image sizes
3. Compare Hugging Face vs OpenAI
4. Explore prompt engineering techniques
5. Save your favorite generations

## Feature Roadmap

**Coming Soon**:

- [ ] Image history browser
- [ ] Negative prompt input
- [ ] Batch generation
- [ ] Image upscaling
- [ ] Image-to-image generation
- [ ] Inpainting (edit parts of images)
- [ ] Custom model support (LoRA)
- [ ] Video generation
- [ ] Animation sequences

Enjoy creating AI-generated art! 🎨
