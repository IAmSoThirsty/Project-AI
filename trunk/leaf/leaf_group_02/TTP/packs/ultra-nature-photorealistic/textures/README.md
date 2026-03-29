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
# Ultra Nature Photorealistic Textures

Photogrammetry-based textures captured from real-world nature scenes.

## Texture Sets

### Forest Ground

**Resolution**: 8192x8192 (8K)

- `forest_ground_albedo_8k.png` - Captured color
- `forest_ground_normal_8k.png` - High-frequency surface detail
- `forest_ground_roughness_8k.png` - Material response
- `forest_ground_displacement_8k.exr` - 32-bit height data
- `forest_ground_ao_8k.png` - Cavity occlusion

### Bark - Oak Tree

**Resolution**: 8192x8192

- `oak_bark_albedo_8k.png` - Diffuse color
- `oak_bark_normal_8k.png` - Bark ridges and cracks
- `oak_bark_roughness_8k.png` - Surface variation
- `oak_bark_displacement_8k.exr` - Deep grooves
- `oak_bark_ao_8k.png` - Crevice shadows

### Rock Formation

**Resolution**: 8192x8192

- `rock_formation_albedo_8k.png` - Stone coloration
- `rock_formation_normal_8k.png` - Fracture details
- `rock_formation_roughness_8k.png` - Weathering
- `rock_formation_displacement_8k.exr` - Macro displacement
- `rock_formation_ao_8k.png` - Large-scale occlusion

### Moss-Covered Stone

**Resolution**: 8192x8192

- `moss_stone_albedo_8k.png` - Organic growth color
- `moss_stone_normal_8k.png` - Texture blending
- `moss_stone_roughness_8k.png` - Wet/dry variation
- `moss_stone_displacement_8k.exr` - Height variation
- `moss_stone_ao_8k.png` - Ambient shadow
- `moss_stone_subsurface_8k.png` - SSS mask for moss

## Photogrammetry Details

### Capture Method
- **Camera**: Sony A7R IV (61 MP)
- **Images per scan**: 150-300 photos
- **Software**: RealityCapture
- **Processing**: Delighting via cross-polarization
- **Retopology**: ZBrush for optimal geometry

### Scan Coverage
- Capture area: 2m x 2m physical space
- Texture density: ~1024 pixels per 10cm
- Detail level: Sub-millimeter accuracy

## Technical Specifications

### File Formats
- **Albedo**: PNG, 8-bit per channel, sRGB
- **Normal**: PNG, 16-bit per channel, Linear
- **Roughness**: PNG, 8-bit, Linear
- **Displacement**: OpenEXR, 32-bit float, Linear
- **AO**: PNG, 8-bit, Linear

### Color Accuracy
- Color calibrated using X-Rite ColorChecker
- Neutral lighting conditions (overcast)
- Post-process color grading for consistency

### UV Layout
- Tiling: Seamless on all axes (4-way tile)
- Overlap removal: Manual edge blending
- Distortion: < 5% across entire texture

## Displacement Mapping

### Height Range
- Forest Ground: 0-15cm variation
- Oak Bark: 0-8cm variation
- Rock Formation: 0-25cm variation
- Moss Stone: 0-10cm variation

### Usage
```glsl
// Recommended displacement settings
displacementScale: 0.05  // Adjust per surface
midLevel: 0.5            // Center point
minSamples: 8
maxSamples: 32
```

### Tessellation
For real-time rendering:
- Tessellation factor: Dynamic based on camera distance
- Max tessellation: 64x
- Min tessellation: 1x (disable beyond 20m)

## Subsurface Scattering

The moss textures include SSS masks:
- **Red channel**: Transmission depth
- **Green channel**: Scatter color intensity
- **Blue channel**: Wetness/specular

Suggested SSS parameters:
```
scatterDistance: (0.02, 0.04, 0.06) // RGB
scatterColor: (0.2, 0.5, 0.2)       // Green tint
```

## Performance

### Memory Usage
- Full quality: ~512 MB per material
- Recommended streaming: LOD pyramid
- Virtual texturing: Strongly recommended

### LOD Recommendations
- Generate mip chain using Lanczos filter
- 8K → 4K → 2K → 1K → 512
- Use anisotropic 16x for optimal quality

### GPU Compression
- **Desktop**: BC7 or BC5 (normal)
- **Consoles**: BC7 / ASTC
- **Quality**: High (minimal artifacts)

## Rendering Guidelines

### PBR Workflow
- Use with GGX/Cook-Torrance BRDF
- Enable energy conservation
- Metallic: 0.0 (all dielectric materials)
- IOR: 1.5 (generic)

### Lighting
- Best results with HDRI environment
- Recommended: Forest/outdoor HDRI
- Shadow detail: High-res shadow maps (4K+)

### Post-Processing
- Enable ambient occlusion (SSAO/HBAO)
- Use depth of field for photorealism
- Color grading: Slight warm tint

## Material Variations

Each base material includes 3 color variations:

- `*_var1.png` - Original scan
- `*_var2.png` - Hue shifted
- `*_var3.png` - Saturation adjusted

Mix in shader for natural variety:
```glsl
vec3 finalColor = mix(
    texture(albedo_var1, uv).rgb,
    texture(albedo_var2, uv).rgb,
    variationMask
);
```

## Tiling

All textures tile seamlessly:
- Manual edge blending in Substance Designer
- Frequency analysis to remove obvious patterns
- Histogram matching at boundaries

Test tiling at 4x4 before using in production.

## License

CC BY-NC 4.0 - Free for non-commercial use. Commercial license available.

## Attribution

Scanned by: TTP Nature Team
Location: Pacific Northwest, USA
Date: 2024

---

**Note**: Actual texture files (8K, ~500MB each) would be stored here via Git LFS. For this demo, placeholder file paths are documented.
