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
# VR Cinematics PBR Textures

High-fidelity PBR textures optimized for VR and cinematic rendering.

## Texture Sets

### Sci-Fi Corridor

**Base Resolution**: 4096x4096 (with LOD chain)

#### LOD 0 (4096x4096)
- `scifi_corridor_albedo_lod0.png` - Base color with detail
- `scifi_corridor_normal_lod0.png` - High-detail normal map
- `scifi_corridor_roughness_lod0.png` - Roughness variation
- `scifi_corridor_metallic_lod0.png` - Metallic mask
- `scifi_corridor_ao_lod0.png` - Ambient occlusion
- `scifi_corridor_height_lod0.png` - Displacement/parallax

#### LOD 1 (2048x2048)
- `scifi_corridor_albedo_lod1.png`
- `scifi_corridor_normal_lod1.png`
- `scifi_corridor_roughness_lod1.png`
- `scifi_corridor_metallic_lod1.png`
- `scifi_corridor_ao_lod1.png`

#### LOD 2 (1024x1024)
- `scifi_corridor_albedo_lod2.png`
- `scifi_corridor_normal_lod2.png`
- `scifi_corridor_roughness_lod2.png`
- `scifi_corridor_metallic_lod2.png`

#### LOD 3 (512x512)
- `scifi_corridor_albedo_lod3.png`
- `scifi_corridor_normal_lod3.png`

### Holographic Panels

**Base Resolution**: 2048x2048

- `hologram_panel_albedo.png` - Transparent blue base
- `hologram_panel_emission.png` - Glowing UI elements
- `hologram_panel_opacity.png` - Alpha mask
- `hologram_panel_normal.png` - Surface detail

### Metal Grating

**Base Resolution**: 4096x4096

- `metal_grating_albedo.png` - Weathered metal
- `metal_grating_normal.png` - Deep grooves and scratches
- `metal_grating_roughness.png` - Varied surface finish
- `metal_grating_metallic.png` - Full metallic
- `metal_grating_ao.png` - Cavity shadows
- `metal_grating_height.png` - Parallax displacement

## PBR Workflow

These textures follow the **Metallic-Roughness** PBR workflow:

- **Albedo**: Pure diffuse color, no lighting information
- **Normal**: Tangent-space normal map (OpenGL format, Y+)
- **Roughness**: 0 = mirror smooth, 1 = completely rough
- **Metallic**: 0 = dielectric, 1 = conductor
- **AO**: Multiplied with indirect lighting only
- **Height**: For parallax occlusion mapping

## Technical Specs

### Color Spaces
- Albedo: sRGB
- Normal: Linear RGB
- Roughness: Linear Grayscale
- Metallic: Linear Grayscale
- AO: Linear Grayscale
- Height: Linear Grayscale
- Emission: sRGB

### Formats
- File Type: PNG (16-bit for normal/height where beneficial)
- Compression: Lossless
- Alpha: Straight alpha (not premultiplied)

### Texture Packing Options

For performance, you can pack channels:

**Option 1: ORM Packing**
- R: Ambient Occlusion
- G: Roughness
- M: Metallic

**Option 2: ARM Packing**
- R: Ambient Occlusion
- G: Roughness
- B: Metallic

## VR Optimization

### LOD Strategy
- LOD 0: Within 2 meters
- LOD 1: 2-5 meters
- LOD 2: 5-10 meters
- LOD 3: 10+ meters

### Memory Budget
- Full quality (all LODs): ~180 MB
- Runtime memory (LOD 0-2): ~65 MB
- Streaming: Load LOD 3 first, upgrade as needed

### Rendering Settings
- **Anisotropic Filtering**: 16x recommended
- **Mip Maps**: Generate using box filter
- **Compression**: BC7 (DirectX) / ASTC (Mobile VR)

## Material Parameters

Suggested shader parameters:

```glsl
// Sci-Fi Corridor
baseColorFactor: (1.0, 1.0, 1.0, 1.0)
metallicFactor: 1.0  // Use texture
roughnessFactor: 1.0 // Use texture
normalScale: 1.5     // Enhanced detail
occlusionStrength: 0.8

// Holographic Panels
baseColorFactor: (0.3, 0.7, 1.0, 0.5)
emissiveFactor: (0.0, 0.5, 1.0)
alphaMode: BLEND

// Metal Grating
metallicFactor: 1.0
roughnessFactor: 0.4  // Override for consistent look
parallaxScale: 0.03   // Subtle depth
```

## Performance Notes

- Use texture streaming for LOD management
- Combine emission with bloom post-process
- Consider virtual texturing for large scenes
- Normal map compression artifacts minimal with BC7

## License

CC BY 4.0 - Attribution required for commercial use.

---

**Note**: Actual texture files would be stored here. For this demo, placeholder file paths are documented.
