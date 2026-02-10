# App Icon Design Specification

## Overview

The Project-AI application icon represents the fusion of security, cognition, and knowledge through a striking 3D design with contrasting hemispheres and a central orb.

## Visual Concept

### Core Design

A spherical icon split into two hemispheres with jagged, clashing boundaries, centered around a luminous white orb representing unified intelligence.

### Symbolic Meaning

- **Red Hemisphere:** Security, protection, firewall (Cerberus)
- **Blue Hemisphere:** Cognition, intelligence, analysis (Galahad/AI)
- **Gold Accents:** Knowledge, value, enlightenment
- **White Orb:** Pure intelligence, decision-making core (CodexDeus)
- **Black Background:** Void, infinite possibility, professionalism
- **Jagged Boundaries:** Tension, conflict resolution, deliberate choice

## Color Palette

| Color | Hex Code | RGB | Usage |
|-------|----------|-----|-------|
| **Security Red** | `#DC143C` | (220, 20, 60) | Left/top hemisphere |
| **Cognitive Blue** | `#1E90FF` | (30, 144, 255) | Right/bottom hemisphere |
| **Knowledge Gold** | `#FFD700` | (255, 215, 0) | Accent highlights, trim |
| **Pure White** | `#FFFFFF` | (255, 255, 255) | Center orb, highlights |
| **Deep Black** | `#000000` | (0, 0, 0) | Background, shadows |

### Gradient Specifications

**Red Hemisphere Gradient:**

- Start: `#FF6B6B` (lighter red)
- Mid: `#DC143C` (crimson)
- End: `#8B0000` (dark red)

**Blue Hemisphere Gradient:**

- Start: `#87CEEB` (light blue)
- Mid: `#1E90FF` (dodger blue)
- End: `#00008B` (dark blue)

**White Orb Glow:**

- Core: `#FFFFFF`
- Glow: `#F0F8FF` (alice blue) with 80% opacity
- Outer glow: Radial fade to transparent

## Dimensions

### Master Source

- **Resolution:** 1024x1024 pixels
- **Format:** PNG with alpha channel
- **Bit Depth:** 32-bit RGBA
- **DPI:** 300 for print quality

### Platform Requirements

**Windows (.ico)**

- 16x16, 32x32, 48x48, 256x256 (all in one .ico file)

**macOS (.icns)**

- 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024

**Linux (.png)**

- 16x16, 22x22, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512

**Android (mipmap-)**

- mdpi: 48x48
- hdpi: 72x72
- xhdpi: 96x96
- xxhdpi: 144x144
- xxxhdpi: 192x192

**Web/PWA**

- favicon.ico: 16x16, 32x32, 48x48
- apple-touch-icon.png: 180x180
- manifest icons: 192x192, 512x512

## 3D Rendering Specifications

### Modeling

- **Software:** Blender 3.x or Cinema 4D
- **Geometry:** Sphere subdivided to 4-5 levels
- **Hemisphere Split:** Boolean operation with jagged plane
- **Center Orb:** Separate emission sphere

### Materials

**Red Hemisphere:**

- Base Color: Red gradient
- Metallic: 0.3
- Roughness: 0.4
- Specular: 0.7

**Blue Hemisphere:**

- Base Color: Blue gradient
- Metallic: 0.3
- Roughness: 0.4
- Specular: 0.7

**Gold Accents:**

- Base Color: Gold `#FFD700`
- Metallic: 0.9
- Roughness: 0.2
- Specular: 1.0

**White Orb:**

- Emission Strength: 5.0
- Base Color: White
- Bloom effect enabled

**Jagged Boundary:**

- Displacement map: Procedural noise
- Edge highlighting: Gold trim (2px width)
- Normal map for depth

### Lighting Setup

**Three-Point Lighting:**

1. **Key Light:** 45° above, warm white (5000K), intensity 100%
2. **Fill Light:** Opposite side, cool white (6500K), intensity 60%
3. **Rim Light:** Behind, slightly blue-tinted, intensity 80%

**Environment:**

- HDRI: Studio black background
- Ambient Occlusion: Enabled, factor 0.8
- Global Illumination: Enabled

### Camera Settings

- **Angle:** 30° from vertical axis
- **Focal Length:** 50mm (normal perspective)
- **F-Stop:** f/8 (sharp focus throughout)
- **Focus:** Center of sphere

## Rendering Settings

**Final Output:**

- Resolution: 2048x2048 (scale down for master)
- Samples: 256 (Cycles renderer)
- Denoising: Enabled (OptiX or OpenImageIO)
- File Format: PNG, 16-bit color depth
- Alpha: Transparent background

**Variations:**

- Full color (primary)
- Monochrome (dark theme alternative)
- Flat design (simplified 2D version)
- Wordmark version (with "Project AI" text)

## File Structure

```
assets/icons/
├── source/
│   ├── icon_3d_model.blend          # Blender source file
│   ├── icon_master_2048x2048.png    # Master render
│   └── icon_variations/
│       ├── monochrome.png
│       ├── flat.png
│       └── wordmark.png
├── desktop/
│   ├── windows/
│   │   └── icon.ico
│   ├── macos/
│   │   └── icon.icns
│   └── linux/
│       └── icon_*.png (all sizes)
├── android/
│   └── mipmap-*dpi/
│       └── ic_launcher.png
└── web/
    ├── favicon.ico
    ├── apple-touch-icon.png
    └── icons/
        ├── icon-192.png
        └── icon-512.png
```

## Generation Script

The icon generation process is automated via `scripts/setup_icons.py`:

```bash
# Generate all platform icons from master source
python scripts/setup_icons.py --source assets/icons/source/icon_master_2048x2048.png

# Generate specific platform
python scripts/setup_icons.py --platform windows

# Regenerate all
python scripts/setup_icons.py --regenerate-all
```

## Brand Guidelines

### Usage Rules

- Always use on dark backgrounds for maximum impact
- Maintain minimum size of 16x16 pixels for legibility
- Do not rotate or skew the icon
- Do not change color palette
- Maintain aspect ratio (1:1)

### Clear Space

- Minimum padding: 10% of icon width on all sides
- Example: For 512px icon, maintain 51px clear space

### Incorrect Usage

- ❌ Don't place on busy backgrounds
- ❌ Don't use gradients as background
- ❌ Don't add drop shadows
- ❌ Don't outline the icon
- ❌ Don't combine with other logos

## Accessibility

**Color Blind Considerations:**

- Red-blue contrast ensures visibility for most types of color blindness
- Gold accents provide additional visual cues
- White center orb serves as recognizable landmark

**Low Vision:**

- High contrast ratio (>4.5:1) between elements
- Simple, recognizable shape even at small sizes
- Clear boundary definition

## Updates and Versioning

**Version History:**

- v1.0 (2026-02-05): Initial 3D design specification
- Future iterations should maintain core color scheme

**Source Control:**

- All source files tracked in git
- Release versions tagged with icon version
- Export script generates consistent outputs

---

**This icon represents the core philosophy of Project-AI: the harmonious yet deliberate clash between security and cognition, unified by intelligent decision-making.**
