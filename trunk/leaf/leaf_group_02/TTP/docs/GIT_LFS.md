<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / GIT_LFS.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / GIT_LFS.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Git LFS Setup for TTP

This repository uses Git Large File Storage (LFS) to efficiently manage texture asset files.

## What is Git LFS?

Git LFS replaces large files (like texture images) with text pointers inside Git, while storing the actual file contents on a remote server. This keeps your repository small and fast while still versioning large assets.

## Installation

### Install Git LFS

```bash
# macOS
brew install git-lfs

# Ubuntu/Debian
sudo apt-get install git-lfs

# Windows
# Download from https://git-lfs.github.com/

# Initialize Git LFS
git lfs install
```

## Tracked File Types

The following file types are automatically tracked by Git LFS (see `.gitattributes`):

### Texture Formats
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TGA (`.tga`)
- TIFF (`.tiff`, `.tif`)
- OpenEXR (`.exr`)
- HDR (`.hdr`)
- Photoshop (`.psd`)

### Archives
- ZIP (`.zip`)
- Tar GZ (`.tar.gz`)
- 7-Zip (`.7z`)

### 3D Models
- FBX (`.fbx`)
- OBJ (`.obj`)
- glTF (`.gltf`, `.glb`)

### Videos
- MP4 (`.mp4`)
- MOV (`.mov`)
- AVI (`.avi`)

### Fonts
- TrueType (`.ttf`)
- OpenType (`.otf`)
- WOFF (`.woff`, `.woff2`)

## Usage

### Adding Files

Git LFS tracks files automatically based on `.gitattributes`. Just add and commit as normal:

```bash
# Add texture files
git add packs/*/textures/*.png

# Commit
git commit -m "Add new texture assets"

# Push (LFS files uploaded automatically)
git push
```

### Verifying LFS Tracking

```bash
# List all files tracked by LFS
git lfs ls-files

# Check if a specific file is tracked
git lfs ls-files | grep texture.png

# Show LFS tracking patterns
cat .gitattributes
```

### Pulling LFS Files

```bash
# Pull all LFS files
git lfs pull

# Pull specific files
git lfs pull --include="packs/*/textures/*"

# Pull files matching a pattern
git lfs pull --include="*.png,*.jpg"
```

### Migration (Converting Existing Files)

If you have existing large files in your repository:

```bash
# Migrate all PNG files to LFS
git lfs migrate import --include="*.png"

# Migrate files from specific path
git lfs migrate import --include="packs/*/textures/*" --include-ref=refs/heads/main

# Migrate and rewrite history (use with caution)
git lfs migrate import --include="*.png,*.jpg" --everything
```

## Best Practices

### File Organization

Store texture assets in pack directories:
```
packs/
  pack-name/
    textures/
      albedo.png       # Tracked by LFS
      normal.png       # Tracked by LFS
      roughness.png    # Tracked by LFS
    pack.json          # Not tracked by LFS (small JSON file)
```

### Naming Conventions

Use descriptive names:
- `albedo.png` or `base_color.png`
- `normal.png` or `normal_map.png`
- `roughness.png` or `roughness_map.png`
- `metallic.png` or `metallic_map.png`

### File Sizes

- Optimize textures before committing
- Use appropriate compression
- Consider resolution vs. file size
- Typical sizes:
  - Pixel tier: < 1 MB per texture
  - Standard: 1-10 MB per texture
  - High: 10-50 MB per texture
  - Cinematic/Ultra: 50-200 MB per texture

### Performance

```bash
# Fetch only pointers, not file contents
git lfs fetch --all

# Prune old LFS objects
git lfs prune

# Check LFS cache size
du -sh .git/lfs
```

## Bandwidth and Storage

Git LFS uses bandwidth when:
- Pushing new/modified LFS files
- Pulling LFS files
- Cloning repository

GitHub LFS quotas:
- Free tier: 1 GB storage, 1 GB/month bandwidth
- Pro: 50 GB storage, 50 GB/month bandwidth
- See [GitHub pricing](https://docs.github.com/en/billing/managing-billing-for-git-large-file-storage/about-billing-for-git-large-file-storage)

## Troubleshooting

### LFS not tracking files

```bash
# Verify .gitattributes
cat .gitattributes

# Re-initialize LFS
git lfs install --force

# Track files manually
git lfs track "*.png"
```

### Large repository size

```bash
# Check what's taking space
git lfs ls-files --size

# Prune old objects
git lfs prune

# Migrate history
git lfs migrate import --everything --include="*.png,*.jpg"
```

### Slow clones

```bash
# Clone without LFS files initially
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/user/ttp.git

# Pull LFS files later
cd ttp
git lfs pull
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Checkout with LFS
  uses: actions/checkout@v4
  with:
    lfs: true

# Or pull LFS files separately
- name: Checkout
  uses: actions/checkout@v4

- name: Pull LFS files
  run: git lfs pull
```

### Docker

```dockerfile
# In Dockerfile
RUN apt-get update && apt-get install -y git-lfs
RUN git lfs install
RUN git lfs pull
```

## Resources

- [Git LFS Documentation](https://git-lfs.github.com/)
- [GitHub LFS Guide](https://docs.github.com/en/repositories/working-with-files/managing-large-files)
- [GitLab LFS Guide](https://docs.gitlab.com/ee/topics/git/lfs/)

## License

MIT License - See LICENSE file for details.
