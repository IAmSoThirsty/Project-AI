<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Project AI UI Textures

Modern UI texture atlas for AI-themed applications and games.

## Texture Atlases

### Main UI Atlas

**Resolution**: 2048x2048

- `ui_atlas_main.png` - Primary UI elements atlas
- `ui_atlas_main.json` - Sprite sheet coordinates (JSON)

#### Elements Included
- Buttons (normal, hover, pressed, disabled states)
- Panels and borders
- Progress bars
- Icons (64 common icons)
- Input fields
- Checkboxes and radio buttons
- Sliders
- Tabs and windows

### Icons Atlas

**Resolution**: 1024x1024

- `icons_atlas_tech.png` - Technology-themed icons (32x32 each)
- `icons_atlas_tech.json` - Icon coordinates

Icons: AI brain, network nodes, data flow, analytics, settings, etc.

### Glowing Elements

**Resolution**: 1024x1024

- `glow_elements_albedo.png` - Glowing UI pieces
- `glow_elements_emission.png` - Emission map for bloom
- `glow_elements_opacity.png` - Alpha channel

Elements: Holographic effects, neon borders, light trails

## SVG Sources

For scalability, source SVG files included:

- `ui_buttons.svg` - Button designs
- `ui_icons.svg` - All icons as vectors
- `ui_panels.svg` - Panel and frame designs

Use these for regenerating atlases at different resolutions.

## Color Scheme

### Primary Colors
- **Cyan Accent**: #00F0FF
- **Purple Highlight**: #A855F7
- **Dark Background**: #0A0E1A
- **Panel Gray**: #1A1F2E
- **Text White**: #F0F0F0

### Gradients
- Header: Linear from #1A1F2E to #0A0E1A
- Buttons: Radial glow with cyan center
- Progress: Animated cyan-to-purple gradient

## Technical Specs

### Atlas Format
- PNG with transparency
- Premultiplied alpha
- sRGB color space

### JSON Format (Sprite Coordinates)
```json
{
  "frames": {
    "button_normal.png": {
      "frame": {"x": 0, "y": 0, "w": 256, "h": 64},
      "spriteSourceSize": {"x": 0, "y": 0, "w": 256, "h": 64},
      "sourceSize": {"w": 256, "h": 64}
    }
  }
}
```

## Usage in Engines

### Unity
```csharp
// Load sprite atlas
SpriteAtlas atlas = Resources.Load<SpriteAtlas>("ui_atlas_main");
Sprite buttonSprite = atlas.GetSprite("button_normal");
```

### Unreal Engine
```cpp
// Use texture atlas UV coordinates
UTexture2D* Atlas = LoadObject<UTexture2D>(nullptr, TEXT("/Game/UI/ui_atlas_main"));
// Apply UV offset and scale from JSON
```

### Web (Three.js)
```javascript
const textureLoader = new THREE.TextureLoader();
const atlas = textureLoader.load('ui_atlas_main.png');
// Use UV coordinates from JSON for sprite rendering
```

## 9-Slice Scaling

UI panels use 9-slice technique:

```
Corner sizes: 32x32 pixels
Edge sizes: Variable
Center: Tileable
```

Coordinates in `ui_atlas_main.json` include border hints.

## Animation

Some elements include multiple frames for animation:

- **Loading Spinner**: 12 frames (30° rotation each)
- **Progress Bar Fill**: 8 frames (pulsing glow)
- **Button Hover**: 4 frames (smooth transition)

Use sprite sheet animation or shader-based effects.

## Glow Effects

### Emission Setup
```glsl
vec3 emission = texture(glow_elements_emission, uv).rgb;
fragColor.rgb += emission * glowIntensity;
```

### Recommended Post-Processing
- Bloom threshold: 0.8
- Bloom intensity: 1.5
- Bloom scatter: 0.7

## Accessibility

All UI elements include:
- High contrast (4.5:1 minimum)
- Clear focus indicators
- Colorblind-friendly palette
- Scalable vector sources (SVG)

## Localization

Text elements separated from UI chrome:
- Use font rendering for text
- UI elements support RTL layouts
- Icons are culture-neutral

## Platform Optimization

### Mobile
- Use half-resolution (1024x1024) for atlas
- Compress with ASTC or ETC2
- Reduce emission intensity

### Desktop
- Full 2K resolution
- BC7 compression
- Enhanced glow effects

### Web
- WebP format with fallback to PNG
- Lazy load secondary atlases
- Sprite sheet preloading

## Customization

### Recoloring
Use HSV shift to match your theme:
```glsl
vec3 tint = rgb2hsv(originalColor);
tint.x += hueShift;  // Change color
tint.y *= saturation; // Adjust vibrancy
vec3 finalColor = hsv2rgb(tint);
```

### Adding Elements
1. Edit SVG source files
2. Export to PNG at 2K
3. Update JSON coordinates
4. Rebuild atlas using tools

## Build Script

Regenerate atlas from SVGs:
```bash
# Install dependencies
npm install svg-sprite-generator

# Build atlas
npm run build-atlas

# Output: ui_atlas_main.png + ui_atlas_main.json
```

## License

MIT License - Use freely in projects.

---

**Note**: Actual texture files would be stored here. For this demo, placeholder file paths are documented.
