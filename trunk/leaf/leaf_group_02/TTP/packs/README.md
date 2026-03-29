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
# TTP Example Assets

This directory contains example texture assets for the TTP repository.

## Structure

Each texture pack contains a `textures/` subdirectory with:
- Actual texture image files (PNG, EXR, etc.)
- README.md documenting the textures
- Preview images for gallery display

## Texture Files (Managed by Git LFS)

Due to the large size of texture files, all images are managed using Git Large File Storage (LFS). See `/docs/GIT_LFS.md` for setup instructions.

### File Sizes

Example packs with placeholder documentation:

1. **miniature-office-pixel** (~5 MB total)
   - 16 texture files ranging from 16x16 to 64x64 pixels
   - Pixel-perfect PNG files, uncompressed

2. **vr-cinematics** (~180 MB total)
   - Complete LOD chain from 4K to 512px
   - PBR texture sets (albedo, normal, roughness, metallic, AO, height)
   - Includes emission maps for glowing elements

3. **ultra-nature-photorealistic** (~2 GB total)
   - 8K photogrammetry textures
   - 32-bit EXR displacement maps
   - Multiple material variations

4. **project-ai** (~50 MB total)
   - UI elements in multiple formats
   - 2K texture atlases
   - SVG source files

5. **stylized-fantasy** (~100 MB total)
   - Hand-painted 2K textures
   - Stylized PBR workflow

6. **industrial-pbr** (~150 MB total)
   - 4K cinematic quality
   - Weathering and wear detail

## Repository Setup for Actual Assets

To use this repository with real texture files:

1. **Install Git LFS**
   ```bash
   git lfs install
   ```

2. **Verify LFS tracking**
   ```bash
   cat .gitattributes
   ```

3. **Add texture files**
   ```bash
   # Add textures to appropriate pack directory
   cp my-texture.png packs/pack-name/textures/

   # Git will automatically track via LFS
   git add packs/pack-name/textures/my-texture.png
   git commit -m "Add texture asset"
   ```

4. **Check LFS status**
   ```bash
   git lfs ls-files
   ```

## Creating New Packs

To create a new texture pack with assets:

1. **Create pack directory structure**
   ```bash
   mkdir -p packs/my-new-pack/textures
   ```

2. **Add pack.json metadata**
   ```bash
   cp schemas/pack-schema-v1.json packs/my-new-pack/pack.json
   # Edit pack.json with your pack details
   ```

3. **Add texture files**
   ```bash
   # Copy your texture files
   cp ~/my-textures/* packs/my-new-pack/textures/
   ```

4. **Create texture README**
   ```bash
   # Document your textures
   vim packs/my-new-pack/textures/README.md
   ```

5. **Validate pack**
   ```bash
   python tools/validate_pack.py packs/my-new-pack/ --strict
   ```

## Best Practices

### File Naming
- Use descriptive names: `metal_rough_albedo_2k.png`
- Include resolution in name for clarity
- Use lowercase with underscores
- Include map type: `_albedo`, `_normal`, `_roughness`

### Organization
```
packs/
  my-pack/
    pack.json              # Metadata
    preview.png            # Gallery preview (1920x1080)
    textures/
      README.md            # Texture documentation
      material_name/       # Group by material
        albedo_2k.png
        normal_2k.png
        roughness_2k.png
        metallic_2k.png
```

### Optimization
- Compress textures appropriately
- Generate mip-map chains offline
- Use appropriate bit depth (8-bit for most, 16-bit for normals)
- Consider packed textures (ORM) for efficiency

### Documentation
- Document PBR workflow used
- Specify color spaces for each map
- Include recommended shader settings
- Note any special material properties

## Asset Licenses

Each pack includes licensing information in `pack.json`:
- `license`: SPDX license identifier
- `license_file`: Path to detailed license
- `attribution`: Required attribution text

Common licenses:
- `MIT` - Permissive, commercial use allowed
- `CC-BY-4.0` - Attribution required
- `CC-BY-NC-4.0` - Non-commercial only
- `CC0-1.0` - Public domain

## Tools

### Validation
```bash
# Validate pack structure and metadata
python tools/validate_pack.py packs/my-pack/

# Strict mode (checks assets exist)
python tools/validate_pack.py packs/my-pack/ --strict

# Check specific features
python tools/validate_pack.py packs/my-pack/ --check-assets
```

### Texture Processing
```bash
# Generate mipmaps (example)
python tools/generate_mipmaps.py packs/my-pack/textures/*.png

# Compress for distribution
python tools/compress_pack.py packs/my-pack/ --format=bc7
```

## Contributing Assets

To contribute new texture packs:

1. Ensure you have rights to distribute the assets
2. Follow the pack schema specification
3. Include comprehensive documentation
4. Validate your pack before submission
5. Create pull request with pack details

See `CONTRIBUTING.md` for detailed guidelines.

## License

Each texture pack has its own license. See individual `pack.json` files for details.

---

**Note**: This is a demonstration repository. Actual texture files are replaced with documentation placeholders. In a production environment, this directory would contain hundreds of megabytes to gigabytes of real texture data managed via Git LFS.
