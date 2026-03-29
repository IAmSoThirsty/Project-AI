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
# Ultra Nature Photorealistic Pack

**Version:** 1.0.0
**Quality Tier:** Ultra
**License:** CC-BY-4.0

## Overview

Professional ultra-high resolution 8K photogrammetry-based nature textures for AAA game development and cinematic production. This pack represents the highest fidelity level available in the TTP repository, featuring photo-scanned organic materials captured from real-world environments.

## Technical Specifications

- **Resolution Range:** 4K - 8K (4096×4096 to 8192×8192)
- **Bit Depth:** 16-bit per channel (EXR format)
- **Color Space:** ACEScg for maximum dynamic range
- **Compression:** DWAA/PIZ optimized for production pipelines
- **Total Size:** ~53 GB
- **Asset Count:** 4 base materials (with LOD variants)

## What's Included

### Bark Textures
- **Oak Bark (Aged)**
  - Albedo map (8K EXR)
  - Normal map - OpenGL format (8K EXR)
  - Displacement map with 0-50mm range (8K EXR, 32-bit)
  - ORM packed map (Occlusion/Roughness/Metallic) (8K EXR)
  - Complete LOD chain: 8K → 4K → 2K → 1K

### Material Properties
- **Seamlessly Tileable:** All textures tile without visible seams
- **Physically Accurate:** Captured using calibrated photogrammetry workflow
- **Sub-millimeter Detail:** Displacement maps provide accurate surface detail
- **Seasonal Variations:** Multiple weathering states and seasonal adaptations

## Capture Details

### Equipment & Process
- **Camera:** Canon EOS R5 with RF 24-70mm f/2.8 L
- **Capture Method:** Multi-angle photogrammetry (350 photos per scan)
- **Processing:** RealityCapture 2024 + Substance Designer 2024
- **Location:** Pacific Northwest, USA
- **Calibration:** Color-calibrated workflow with X-Rite ColorChecker

### Accuracy
- **Mesh Resolution:** 10M polygons (before decimation)
- **Texture Reconstruction:** Sub-millimeter accuracy
- **Processing Time:** 48 hours per material

## Engine Integration

### Unity HDRP
```csharp
// Recommended import settings
TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
importer.textureType = TextureImporterType.Default;
importer.sRGBTexture = true; // For albedo only
importer.maxTextureSize = 8192;
importer.textureCompression = TextureImporterCompression.CompressedHQ;
importer.mipmapEnabled = true;
```

### Unreal Engine 5
- **Nanite Support:** Full support with virtual textures
- **Recommended Settings:**
  - Compression: BC7 for albedo, BC5 for normal, BC4 for packed maps
  - LOD Group: WorldDetailEpic
  - Mipmap Generation: SimpleAverage
  - Virtual Texturing: Enabled

### Displacement Setup
- **Subdivision Level:** 6-8 recommended
- **Displacement Range:** 0-50mm (stored in linear space)
- **Mid-level:** 0.5 (50% gray = 25mm)
- **Subdivision Type:** Adaptive for best performance

## Performance Considerations

### Memory Usage (8K)
- Albedo (8K, BC7): ~85 MB
- Normal (8K, BC5): ~85 MB
- ORM Packed (8K, BC4): ~42 MB
- Displacement (8K, uncompressed): ~256 MB (offline rendering only)
- **Total per material:** ~470 MB

### Optimization Recommendations
1. Use LOD system - switch to 4K at medium distance, 2K at far distance
2. Enable virtual texturing for streaming
3. Use displacement only for hero shots or close-ups
4. Consider BC7 compression for real-time applications

## Attribution Requirements

Under CC-BY-4.0 license, you must provide attribution:

```
Oak Bark textures from Ultra Nature Photorealistic Pack
by Thirsty Studios (IAmSoThirsty)
Licensed under CC-BY-4.0
https://github.com/IAmSoThirsty/TTP
```

## Support & Documentation

- **Issues:** https://github.com/IAmSoThirsty/TTP/issues
- **Email:** nature@thirstystudios.example.com
- **Installation Guide:** [docs/installation-guide.md](docs/installation-guide.md)
- **Usage Examples:** [docs/usage-examples.md](docs/usage-examples.md)

## Changelog

### Version 1.0.0 (2026-02-18)
- Initial release
- Oak bark textures (aged variant)
- Complete PBR workflow with displacement
- LOD variants (8K, 4K, 2K, 1K)

## Future Additions
- Birch bark
- Pine bark
- Moss-covered variations
- Seasonal variants (winter, autumn)
- Damaged/diseased states
