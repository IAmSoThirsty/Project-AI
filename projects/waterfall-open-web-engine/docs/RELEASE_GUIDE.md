<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / RELEASE_GUIDE.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / RELEASE_GUIDE.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Release Guide

Quick reference for creating releases of Thirstys Waterfall.

## Pre-Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with new version
- [ ] Version numbers updated in:
  - `setup.py`
  - `pyproject.toml`
  - `thirstys_waterfall/__init__.py` (if version is defined there)

## Creating a Release

### 1. Update Version

Update version in `setup.py` and `pyproject.toml`:

```python

# setup.py

version="1.0.0"

# pyproject.toml

[project]
version = "1.0.0"
```

### 2. Update CHANGELOG.md

Add a new section for the release:

```markdown

## [1.0.0] - 2026-02-12

### Added

- New feature 1
- New feature 2

### Fixed

- Bug fix 1
- Bug fix 2

```

### 3. Commit Changes

```bash
git add setup.py pyproject.toml CHANGELOG.md
git commit -m "Release v1.0.0"
git push origin main
```

### 4. Create and Push Tag

```bash

# Create annotated tag

git tag -a v1.0.0 -m "Release v1.0.0"

# Push tag to GitHub

git push origin v1.0.0
```

### 5. Automated Release

Once the tag is pushed, GitHub Actions will automatically:

1. Run all tests across platforms
2. Build source and wheel distributions
3. Build Docker images
4. Create GitHub Release with artifacts
5. Publish to PyPI (if configured)

## Manual Release (if needed)

### Build Packages

```bash

# Install build tools

pip install build wheel twine

# Build distributions

python -m build

# Check distributions

twine check dist/*
```

### Build Docker Image

```bash

# Build image

docker build -t thirstys-waterfall:1.0.0 .

# Tag as latest

docker tag thirstys-waterfall:1.0.0 thirstys-waterfall:latest

# Test image

docker run --rm thirstys-waterfall:1.0.0 thirstys-waterfall --help
```

### Publish to PyPI

```bash

# Upload to PyPI (requires API token)

twine upload dist/*

# Or upload to TestPyPI first

twine upload --repository testpypi dist/*
```

### Push Docker Image

```bash

# Tag for registry

docker tag thirstys-waterfall:1.0.0 yourusername/thirstys-waterfall:1.0.0
docker tag thirstys-waterfall:1.0.0 yourusername/thirstys-waterfall:latest

# Push to Docker Hub

docker push yourusername/thirstys-waterfall:1.0.0
docker push yourusername/thirstys-waterfall:latest
```

## Release Types

### Major Release (X.0.0)

Breaking changes, major new features:

```bash
git tag -a v2.0.0 -m "Major release: Breaking changes"
```

### Minor Release (x.Y.0)

New features, backwards compatible:

```bash
git tag -a v1.1.0 -m "Minor release: New features"
```

### Patch Release (x.y.Z)

Bug fixes, security patches:

```bash
git tag -a v1.0.1 -m "Patch release: Bug fixes"
```

## Post-Release

1. Verify release on GitHub
2. Test installation: `pip install thirstys-waterfall==1.0.0`
3. Test Docker image: `docker pull yourusername/thirstys-waterfall:1.0.0`
4. Update documentation if needed
5. Announce release

## Rollback

If a release has issues:

```bash

# Delete local tag

git tag -d v1.0.0

# Delete remote tag

git push origin :refs/tags/v1.0.0

# Delete GitHub release via web interface

# Unpublish from PyPI (contact PyPI support)

```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

## Secrets Configuration

For automated PyPI publishing, configure GitHub secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add secret: `PYPI_API_TOKEN`
3. Value: Your PyPI API token

For Docker Hub publishing:

1. Add secrets: `DOCKER_USERNAME` and `DOCKER_PASSWORD`
2. Update release workflow to include Docker push

## Troubleshooting

### Build Fails

```bash

# Clean and rebuild

rm -rf dist/ build/ *.egg-info
python -m build
```

### Docker Build Fails

```bash

# Clear Docker cache

docker builder prune

# Rebuild without cache

docker build --no-cache -t thirstys-waterfall:test .
```

### PyPI Upload Fails

```bash

# Check package

twine check dist/*

# Verify token

# Test with TestPyPI first

```

## Resources

- [GitHub Actions Workflows](.github/workflows/)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [CHANGELOG.md](CHANGELOG.md)
