<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / CONTRIBUTING.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / CONTRIBUTING.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Contributing to TTP - Thirsty's Texture Packs

Thank you for your interest in contributing to Thirsty's Texture Packs! This document provides guidelines for contributing to this project.

## How to Contribute

### Adding New Texture Packs

1. **Create Pack Directory**
   ```bash
   mkdir -p packs/[your-pack-name]/textures
   ```

2. **Add Pack Metadata**
   Create a `pack.json` file in your pack directory with the following structure:
   ```json
   {
     "name": "Your Pack Name",
     "version": "1.0.0",
     "description": "Description of your texture pack",
     "author": "Your Name",
     "license": "MIT",
     "tags": ["tag1", "tag2"],
     "target_projects": ["project-name"],
     "resolution": "1024x1024",
     "format": "png"
   }
   ```

3. **Add Pack Documentation**
   Create a `README.md` in your pack directory explaining:
   - Purpose of the pack
   - Supported resolutions
   - File formats
   - Usage examples
   - Attribution requirements (if any)

4. **Organize Textures**
   Place texture files in the `textures/` subdirectory with clear, descriptive names:
   - Use lowercase with hyphens: `office-desk-wood.png`
   - Include resolution in filename if multiple versions: `wall-brick-1024.png`
   - Group related textures in subdirectories

### Submitting Texture Improvements

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/improve-office-textures`
3. Make your changes
4. Ensure all textures meet quality standards (see below)
5. Commit with clear messages: `git commit -m "Add improved desk textures"`
6. Push to your fork: `git push origin feature/improve-office-textures`
7. Open a Pull Request

## Quality Standards

### Texture Requirements

- **File Formats**: PNG (with transparency), JPG (opaque), or industry-standard formats
- **Naming Convention**: Descriptive, lowercase, hyphen-separated
- **Resolution**: Clearly documented, power-of-2 dimensions preferred
- **Color Space**: sRGB for albedo/diffuse, linear for normal/roughness/metallic
- **File Size**: Optimized for web/game use (use appropriate compression)

### For Pixel Art Packs
- No anti-aliasing or smoothing
- Consistent pixel size across pack
- Clear pixel grid alignment

### For VR/High-Res Packs
- Minimum 2K resolution for primary surfaces
- Include mipmaps or allow for auto-generation
- PBR textures should include: Albedo, Normal, Roughness, Metallic, AO

### For AI/UI Packs
- Vector formats (SVG) when possible
- Multiple color variations
- Scalable designs

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Credit original work appropriately
- Follow licensing requirements

## Reporting Issues

When reporting issues, please include:
- Pack name and version
- Description of the problem
- Expected vs actual behavior
- Screenshots (if applicable)
- Steps to reproduce

## Questions?

Feel free to open an issue for any questions or clarifications needed.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
