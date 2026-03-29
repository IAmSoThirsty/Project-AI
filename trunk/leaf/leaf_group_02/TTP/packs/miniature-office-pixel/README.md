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
# Miniature Office Pixel Texture Pack

A charming pixel-art texture pack designed for miniature office environments, perfect for indie games, pixel art projects, and retro-styled applications.

## Overview

This pack provides a comprehensive collection of pixel-perfect textures for creating detailed office scenes with a nostalgic, retro aesthetic.

## Specifications

- **Resolution**: 16x16 to 64x64 pixels
- **Format**: PNG with transparency support
- **Style**: Retro pixel art
- **Color Palette**: Limited, carefully curated colors
- **Pixel Density**: Consistent across all assets

## Contents

### Furniture
- Desks (various styles: modern, vintage, executive)
- Office chairs (task chairs, executive chairs)
- Filing cabinets
- Bookshelves
- Meeting tables

### Equipment
- Desktop computers (monitors, keyboards, mice)
- Laptops
- Telephones (desk phones, modern handsets)
- Printers and copiers
- Desk lamps

### Decorations
- Potted plants
- Picture frames
- Wall calendars
- Coffee mugs
- Office supplies (pens, papers, folders)

### Environment
- **Floors**: Carpet patterns, tile, hardwood
- **Walls**: Plain colors, wallpaper patterns, brick
- **Windows**: Various styles with transparency

## Usage Guidelines

### Rendering Settings
```
Texture Filtering: NEAREST (Point filtering)
Mipmaps: Disabled
Anti-aliasing: Disabled on textures
```

### Import Settings (Unity Example)
```
Filter Mode: Point (no filter)
Compression: None or Truecolor
Max Size: 64 (or original size)
```

### Import Settings (Unreal Engine Example)
```
Mip Gen Settings: NoMipmaps
Texture Group: 2D Pixels (Unfiltered)
Compression Settings: UserInterface2D
```

## Example Projects

This pack is ideal for:
- Isometric office management games
- Top-down office simulators
- Retro-styled business applications
- Pixel art visual novels
- 2D office-themed puzzle games

## Color Palette

The pack uses a carefully selected limited color palette to maintain visual consistency:
- Neutral tones for furniture
- Warm wood colors
- Cool metal grays
- Accent colors for decorations

## File Naming Convention

Textures follow this naming pattern:
```
[category]-[item]-[variant]-[size].png

Examples:
furniture-desk-modern-32.png
equipment-computer-monitor-64.png
decoration-plant-small-16.png
```

## Tips for Best Results

1. **Maintain pixel-perfect alignment** - Position objects on whole pixel coordinates
2. **Disable texture filtering** - Use nearest-neighbor sampling
3. **Consistent scaling** - Keep all objects at the same pixel-per-unit ratio
4. **Lighting** - Use flat or simple lighting to preserve pixel art style
5. **Camera** - Use orthographic projection for best results

## Attribution

While not required by the MIT license, we appreciate attribution in your projects:
```
Textures from TTP - Thirsty's Texture Packs
https://github.com/IAmSoThirsty/TTP
```

## Version History

- **v1.0.0** - Initial release with core office assets

## Contributing

Want to add more pixel art assets? See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../../LICENSE) for full text.
