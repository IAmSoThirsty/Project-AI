# Project-AI v1.0.0 - Package Build & Deployment Guide

**Version:** 1.0.0 **Date:** January 28, 2026 **Status:** Production Ready

______________________________________________________________________

## 📦 Package Information

### Distribution Files

- **Wheel (Binary):** `project_ai-1.0.0-py3-none-any.whl` (528 KB)
- **Source Distribution:** `project_ai-1.0.0.tar.gz` (1.4 MB)

### Package Metadata

- **Name:** project-ai
- **Version:** 1.0.0
- **License:** MIT
- **Python:** >=3.11
- **Platform:** Any (Linux, macOS, Windows, Docker)

______________________________________________________________________

## 🔨 Building from Source

### Prerequisites

```bash

# Install build tools

pip install build twine

# Optional: Install development dependencies

pip install -r requirements-dev.txt
```

### Build Process

#### 1. Clean Previous Builds

```bash

# Remove old build artifacts

rm -rf build/ dist/ *.egg-info
```

#### 2. Build Distributions

```bash

# Build both source and wheel distributions

python -m build

# Output:

# - dist/project_ai-1.0.0-py3-none-any.whl

# - dist/project_ai-1.0.0.tar.gz

```

#### 3. Verify Build

```bash

# Check distribution contents

tar -tzf dist/project_ai-1.0.0.tar.gz | head -20
unzip -l dist/project_ai-1.0.0-py3-none-any.whl | head -20

# Verify package metadata

twine check dist/*
```

Expected output:

```
Checking dist/project_ai-1.0.0-py3-none-any.whl: PASSED
Checking dist/project_ai-1.0.0.tar.gz: PASSED
```

______________________________________________________________________

## 📤 Publishing to PyPI

### TestPyPI (Recommended First)

#### 1. Create TestPyPI Account

- Visit: https://test.pypi.org/account/register/
- Verify email
- Generate API token: https://test.pypi.org/manage/account/token/

#### 2. Configure Credentials

```bash

# Option 1: Use .pypirc file

cat > ~/.pypirc << EOF
[testpypi]
username = __token__
password = pypi-YOUR-TEST-PYPI-TOKEN-HERE
EOF

# Option 2: Use environment variables

export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-TEST-PYPI-TOKEN-HERE
```

#### 3. Upload to TestPyPI

```bash

# Upload distributions

twine upload --repository testpypi dist/*

# Expected output:

# Uploading distributions to https://test.pypi.org/legacy/

# Uploading project_ai-1.0.0-py3-none-any.whl

# Uploading project_ai-1.0.0.tar.gz

```

#### 4. Test Installation from TestPyPI

```bash

# Create test environment

python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI

pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ project-ai

# Verify installation

python -c "import project_ai; print(project_ai.__version__)"

# Expected output: 1.0.0

# Test basic functionality

python -m pytest --version
python -c "from api import main; print('API import successful')"
```

### Production PyPI

#### 1. Create PyPI Account

- Visit: https://pypi.org/account/register/
- Verify email
- Enable 2FA (required for project maintainers)
- Generate API token: https://pypi.org/manage/account/token/

#### 2. Configure Production Credentials

```bash

# Add to ~/.pypirc

cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-PYPI-TOKEN-HERE
EOF

# Or use environment variables

export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-PRODUCTION-PYPI-TOKEN-HERE
```

#### 3. Upload to Production PyPI

```bash

# Upload distributions

twine upload dist/*

# Expected output:

# Uploading distributions to https://upload.pypi.org/legacy/

# Uploading project_ai-1.0.0-py3-none-any.whl

# Uploading project_ai-1.0.0.tar.gz

```

#### 4. Verify Production Release

```bash

# Visit package page

open https://pypi.org/project/project-ai/

# Install from PyPI

pip install project-ai

# Verify installation

python -c "import project_ai; print(project_ai.__version__)"
```

______________________________________________________________________

## 🏷️ GitHub Release

### Create Release Tag

#### 1. Verify Current State

```bash

# Check current branch and status

git status
git log --oneline -5

# Ensure working directory is clean

# If not, commit or stash changes

```

#### 2. Create Annotated Tag

```bash

# Create v1.0.0 tag with release notes

git tag -a v1.0.0 -m "v1.0.0: Production Release - Complete Security Testing & Infrastructure

## Highlights

- Triumvirate Governance Model (Galahad, Cerberus, CodexDeus)
- 8-Layer Security Architecture
- TARL Policy Engine (v1.0 + v2.0)
- FastAPI REST API with governance enforcement
- Multi-platform support (Python, JS, Kotlin, C#, Shell, HTML)
- 100+ comprehensive test suite
- Complete documentation (60+ files)

## Security & Compliance

- ASL-3 Compliant (30+ security controls)
- NIST AI RMF adherence
- OWASP LLM Top 10 protection
- Red team tested (2000+ scenarios)

See RELEASE_NOTES_v1.0.0.md for complete details."

# Verify tag

git tag -n v1.0.0
```

#### 3. Push Tag to Remote

```bash

# Push tag to GitHub

git push origin v1.0.0

# Or push all tags

git push --tags
```

### Create GitHub Release

#### Option 1: GitHub Web UI

1. Navigate to: https://github.com/IAmSoThirsty/Project-AI/releases/new
1. Select tag: `v1.0.0`
1. Release title: `v1.0.0 - Production Release`
1. Copy content from `RELEASE_NOTES_v1.0.0.md` into description
1. Upload build artifacts:
   - `dist/project_ai-1.0.0-py3-none-any.whl`
   - `dist/project_ai-1.0.0.tar.gz`
   - Generate checksums (see below)
1. Check "Set as the latest release"
1. Click "Publish release"

#### Option 2: GitHub CLI

```bash

# Install GitHub CLI if needed

# brew install gh  # macOS

# apt install gh    # Ubuntu/Debian

# Authenticate

gh auth login

# Create release

gh release create v1.0.0 \
  --title "v1.0.0 - Production Release" \
  --notes-file RELEASE_NOTES_v1.0.0.md \
  dist/project_ai-1.0.0-py3-none-any.whl \
  dist/project_ai-1.0.0.tar.gz \
  CHECKSUMS.txt
```

### Generate Checksums

```bash

# Generate SHA256 checksums

cd dist
sha256sum project_ai-1.0.0-py3-none-any.whl > ../CHECKSUMS.txt
sha256sum project_ai-1.0.0.tar.gz >> ../CHECKSUMS.txt

# On macOS, use:

# shasum -a 256 project_ai-1.0.0-py3-none-any.whl > ../CHECKSUMS.txt

# shasum -a 256 project_ai-1.0.0.tar.gz >> ../CHECKSUMS.txt

cd ..
cat CHECKSUMS.txt
```

### Sign Release Artifacts (Optional but Recommended)

```bash

# Install GPG if needed

# brew install gnupg  # macOS

# apt install gnupg   # Ubuntu/Debian

# Generate GPG key (if you don't have one)

gpg --gen-key

# Sign distributions

gpg --detach-sign --armor dist/project_ai-1.0.0-py3-none-any.whl
gpg --detach-sign --armor dist/project_ai-1.0.0.tar.gz

# Verify signatures

gpg --verify dist/project_ai-1.0.0-py3-none-any.whl.asc dist/project_ai-1.0.0-py3-none-any.whl
gpg --verify dist/project_ai-1.0.0.tar.gz.asc dist/project_ai-1.0.0.tar.gz

# Upload .asc files to GitHub release

gh release upload v1.0.0 dist/*.asc
```

______________________________________________________________________

## 🚢 Docker Hub Publishing

### Build and Tag Images

```bash

# Build production image

docker build -t iamsoothirsty/project-ai:1.0.0 .
docker build -t iamsoothirsty/project-ai:latest .

# Build API image (if separate)

docker build -f Dockerfile.api -t iamsoothirsty/project-ai-api:1.0.0 .
docker build -f Dockerfile.api -t iamsoothirsty/project-ai-api:latest .
```

### Push to Docker Hub

```bash

# Login to Docker Hub

docker login

# Push versioned images

docker push iamsoothirsty/project-ai:1.0.0
docker push iamsoothirsty/project-ai:latest

# Push API images

docker push iamsoothirsty/project-ai-api:1.0.0
docker push iamsoothirsty/project-ai-api:latest
```

### Verify Docker Images

```bash

# Pull and test

docker pull iamsoothirsty/project-ai:1.0.0
docker run --rm iamsoothirsty/project-ai:1.0.0 python -c "import project_ai; print(project_ai.__version__)"

# Expected output: 1.0.0

```

______________________________________________________________________

## 📋 Release Checklist

### Pre-Release

- [x] All version strings updated to 1.0.0
- [x] CHANGELOG.md updated with complete v1.0.0 notes
- [x] RELEASE_NOTES_v1.0.0.md created
- [x] All tests passing (or documented exceptions)
- [x] Security audit completed
- [x] Documentation reviewed and updated
- [x] MANIFEST.in includes all necessary files
- [x] Dependencies pinned and verified

### Build Phase

- [x] Build environment clean (`rm -rf build/ dist/ *.egg-info`)
- [x] Source distribution built successfully
- [x] Wheel distribution built successfully
- [x] Distribution contents verified
- [x] Package metadata validated (`twine check`)
- [x] Test installation from built distributions

### Publishing Phase

- [ ] TestPyPI upload successful (recommended)
- [ ] Test installation from TestPyPI verified
- [ ] Production PyPI upload completed
- [ ] GitHub release tag created (v1.0.0)
- [ ] GitHub release published with artifacts
- [ ] Release notes added to GitHub release
- [ ] Checksums generated and uploaded
- [ ] Artifacts signed (optional)
- [ ] Docker images built and pushed (optional)

### Post-Release

- [ ] Installation verified from PyPI
- [ ] Documentation site updated (if applicable)
- [ ] Social media announcement (if applicable)
- [ ] Community notifications (Discord, Twitter, etc.)
- [ ] Monitor for issues and user feedback
- [ ] Update project board/roadmap for next version

______________________________________________________________________

## 🔍 Troubleshooting

### Common Build Issues

#### Issue: "ModuleNotFoundError" during build

**Solution:**

```bash

# Install all dependencies

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Issue: "MANIFEST.in not found" warning

**Solution:**

```bash

# Ensure MANIFEST.in exists and has correct content

cat MANIFEST.in
```

#### Issue: Build includes unwanted files

**Solution:**

```bash

# Update MANIFEST.in to exclude files

# Add lines like:

# global-exclude *.pyc

# global-exclude __pycache__

```

### Common Upload Issues

#### Issue: "403 Forbidden" during upload

**Solution:**

- Verify API token is correct
- Check token permissions
- Ensure package name is available (not already taken)

#### Issue: "Package version already exists"

**Solution:**

- PyPI does not allow re-uploading the same version
- Increment version number
- Or delete old version (only possible within 24 hours)

#### Issue: twine hangs during upload

**Solution:**

```bash

# Try with verbose output

twine upload --verbose dist/*

# Or specify repository URL explicitly

twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

______________________________________________________________________

## 📊 Package Statistics

### Distribution Sizes

- **Wheel:** 528 KB
- **Source Tarball:** 1.4 MB

### Included Components

- Python source files (core system)
- JavaScript/TypeScript (web frontend)
- Kotlin (Android app)
- Shell scripts (deployment)
- HTML/CSS (web UI)
- Configuration files
- Documentation (60+ files)
- Examples and demos
- Docker configurations
- Kubernetes/Helm charts

### Dependencies

- **Production:** 30+ packages (Flask, FastAPI, PyQt6, scikit-learn, etc.)
- **Development:** 10+ packages (pytest, ruff, black, etc.)

______________________________________________________________________

## 🔐 Security Notes

### API Token Security

- **Never commit** tokens to version control
- Store tokens in `~/.pypirc` with chmod 600
- Use environment variables in CI/CD
- Rotate tokens regularly
- Use scoped tokens (limited to specific projects)

### Package Signing

- Sign all release artifacts with GPG
- Publish public key to keyservers
- Include signature verification instructions
- Consider using sigstore for additional verification

### Dependency Security

```bash

# Audit dependencies before release

pip-audit

# Check for known vulnerabilities

safety check

# Update dependencies if needed

pip-compile --upgrade requirements.in
```

______________________________________________________________________

## 📚 Additional Resources

### Official Documentation

- **PyPI Documentation:** https://packaging.python.org/
- **Twine Guide:** https://twine.readthedocs.io/
- **GitHub Releases:** https://docs.github.com/en/repositories/releasing-projects-on-github

### Project Links

- **Repository:** https://github.com/IAmSoThirsty/Project-AI
- **PyPI Package:** https://pypi.org/project/project-ai/ (after publishing)
- **Documentation:** https://github.com/IAmSoThirsty/Project-AI/tree/main/docs
- **Issues:** https://github.com/IAmSoThirsty/Project-AI/issues

______________________________________________________________________

## 📝 Notes

### Version Policy

- **Major (1.x.x):** Breaking changes, major features
- **Minor (x.1.x):** New features, backward compatible
- **Patch (x.x.1):** Bug fixes, security patches

### Release Cadence

- **Major releases:** Annually or as needed
- **Minor releases:** Quarterly or as features complete
- **Patch releases:** As needed for critical fixes

### Support Policy

- **Latest major version:** Full support
- **Previous major version:** Security updates only (12 months)
- **Older versions:** End of life (no support)

______________________________________________________________________

**Last Updated:** January 28, 2026 **Maintainer:** Project-AI Team **Contact:** https://github.com/IAmSoThirsty/Project-AI/issues
