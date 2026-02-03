# Release Build Guide for Project-AI

## Overview

This guide explains how to build and release the complete Project-AI distribution package, which includes:

- Backend API (Python FastAPI with TARL governance)
- Web Frontend (HTML/CSS/JS)
- Android App (APK)
- Desktop Apps (Windows, macOS, Linux)
- Monitoring Agents (Prometheus, Grafana, AlertManager)
- Complete Documentation

## Prerequisites

### Required

- **Python 3.11+** - For backend and build scripts
- **Git** - For version control and tagging

### Optional (for full build)

- **Node.js 18+** and **npm** - For desktop app builds
- **Docker** - For containerized deployment
- **Java 17+** - For Android APK builds
- **Gradle** - For Android builds (wrapper included)
- **7-Zip** (Windows only) - For creating ZIP archives on Windows

## Quick Start

### Automated Build (GitHub Actions)

The easiest way to create a release is using GitHub Actions:

1. **Create and push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. The `build-release.yml` workflow automatically:
   - Validates dependencies
   - Builds all platform artifacts
   - Runs validation checks
   - Creates archives
   - Generates JSON reports
   - Creates GitHub release
   - Triggers artifact signing

3. **Manual trigger (optional):**
   - Go to Actions → Build Release Package
   - Click "Run workflow"
   - Enter version number (e.g., `1.0.0`)
   - Click "Run workflow"

### Local Build

#### Linux/macOS

```bash
# Make scripts executable (first time only)
chmod +x scripts/build_release.sh
chmod +x scripts/validate_release.py

# Run the build
./scripts/build_release.sh
```

#### Windows

```batch
REM Run from project root
scripts\build_release.bat
```

## Build Process

### Phase 1: Dependency Validation

The build script automatically checks for:

- ✅ Python 3.x (required)
- ⚠️ Node.js (optional - for desktop builds)
- ⚠️ npm (optional - for desktop builds)
- ⚠️ Docker (optional - for containerization)
- ⚠️ Gradle wrapper (for Android builds)

**If required dependencies are missing, the build will fail with an error.**

### Phase 2: Platform Builds

#### Backend API
- Copies: `api/`, `tarl/`, `governance/`, `config/`, `utils/`, `kernel/`
- Creates startup scripts: `start.sh`, `start.bat`
- Includes: `requirements.txt`, `.env` template

#### Web Frontend
- Copies all web assets
- Creates deployment guide: `DEPLOY.md`

#### Android App
- Runs: `./gradlew assembleDebug` (if available)
- Output: `project-ai-v1.0.0-debug.apk`
- Creates: `INSTALL.md` guide

#### Desktop Apps
- Runs: `npm install && npm run build` (if available)
- Outputs platform-specific installers
- Creates: `INSTALL.md` guide

#### Monitoring Agents
- Copies monitoring configurations
- Creates: `README.md` for monitoring setup

### Phase 3: Security Cleanup

The script automatically removes:
- `*.key` files
- `*.pem` files (not from signing)
- `secrets.*` files
- Clears sensitive values in `.env` files

### Phase 4: Archive Creation

Creates two archive formats:
- `project-ai-v1.0.0.tar.gz` (Linux/macOS preferred)
- `project-ai-v1.0.0.zip` (cross-platform)

### Phase 5: Validation

Runs `validate_release.py` to check:
- Directory structure completeness
- Backend artifacts presence
- Web frontend files
- Android APK (if built)
- Desktop installers (if built)
- Documentation completeness
- MANIFEST.in compliance

### Phase 6: Report Generation

Creates two JSON reports:

#### `release-summary-v1.0.0.json`
```json
{
  "version": "1.0.0",
  "build_date": "2024-01-28",
  "build_duration_seconds": 127,
  "artifacts": {
    "backend": { "included": true, ... },
    "web": { "included": true, ... },
    "android": { "included": true, "apk_count": 1 },
    "desktop": { "included": true, "installer_count": 3 },
    "monitoring": { "included": true },
    "documentation": { "included": true }
  },
  "checksums": { ... }
}
```

#### `validation-report-v1.0.0.json`
```json
{
  "validation_passed": true,
  "errors": [],
  "warnings": ["Desktop: No installers found"],
  "summary": {
    "total_checks": 25,
    "errors": 0,
    "warnings": 1
  }
}
```

## Output Structure

After a successful build:

```
releases/
├── project-ai-v1.0.0/           # Full distribution
│   ├── backend/
│   │   ├── api/
│   │   ├── tarl/
│   │   ├── governance/
│   │   ├── config/
│   │   ├── start.sh
│   │   ├── start.bat
│   │   └── requirements.txt
│   ├── web/
│   │   ├── index.html
│   │   └── DEPLOY.md
│   ├── android/
│   │   ├── project-ai-v1.0.0-debug.apk
│   │   └── INSTALL.md
│   ├── desktop/
│   │   ├── *.exe (Windows)
│   │   ├── *.dmg (macOS)
│   │   ├── *.AppImage (Linux)
│   │   └── INSTALL.md
│   ├── monitoring/
│   │   └── README.md
│   ├── docs/
│   ├── README.md
│   ├── CONSTITUTION.md
│   ├── CHANGELOG.md
│   ├── LICENSE
│   └── SECURITY.md
├── project-ai-v1.0.0.tar.gz     # Archive (Linux/Mac)
├── project-ai-v1.0.0.zip        # Archive (Windows/cross-platform)
├── release-summary-v1.0.0.json  # Build metadata
├── validation-report-v1.0.0.json # Validation results
├── SHA256SUMS                    # Checksums
└── SHA512SUMS                    # Checksums
```

## Validation

### Manual Validation

Run validation independently:

```bash
python3 scripts/validate_release.py releases/project-ai-v1.0.0 --version 1.0.0
```

Output options:
```bash
# Human-readable output (default)
python3 scripts/validate_release.py releases/project-ai-v1.0.0

# JSON output to stdout
python3 scripts/validate_release.py releases/project-ai-v1.0.0 --json

# JSON output to file
python3 scripts/validate_release.py releases/project-ai-v1.0.0 --output report.json
```

### Validation Checks

The validator performs 8 categories of checks:

1. **Directory Structure** - Verifies all expected directories exist
2. **Backend** - Checks API, TARL, governance modules, startup scripts
3. **Web Frontend** - Verifies index.html and deployment guide
4. **Android** - Checks for APK files and installation guide
5. **Desktop** - Verifies installers for various platforms
6. **Documentation** - Ensures all required docs are present
7. **MANIFEST.in** - Validates against package manifest
8. **Dependencies** - Checks requirements.txt and dependency files

Exit codes:
- `0` - Validation passed (warnings allowed)
- `1` - Validation failed (errors found)

## Checksums and Verification

### Generate Checksums

Checksums are automatically generated during build:

```bash
cd releases
sha256sum project-ai-v1.0.0.tar.gz > SHA256SUMS
sha512sum project-ai-v1.0.0.tar.gz > SHA512SUMS
```

### Verify Checksums

```bash
cd releases
sha256sum -c SHA256SUMS
sha512sum -c SHA512SUMS
```

Expected output:
```
project-ai-v1.0.0.tar.gz: OK
project-ai-v1.0.0.zip: OK
```

## GitHub Release Process

### Automated (Recommended)

1. **Create and push tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Workflow automatically:**
   - Builds complete distribution
   - Validates artifacts
   - Creates GitHub release
   - Uploads all artifacts
   - Triggers signing workflow

### Manual Release Creation

If you built locally and want to create a release manually:

1. **Create release on GitHub:**
   - Go to Releases → Draft a new release
   - Create tag: `v1.0.0`
   - Fill in release notes

2. **Upload artifacts:**
   - `project-ai-v1.0.0.tar.gz`
   - `project-ai-v1.0.0.zip`
   - `release-summary-v1.0.0.json`
   - `validation-report-v1.0.0.json`
   - `SHA256SUMS`
   - `SHA512SUMS`

3. **Publish release**

## Artifact Signing

Release artifacts are signed using Sigstore Cosign:

1. The `build-release.yml` workflow triggers `sign-release-artifacts.yml`
2. Artifacts are signed with keyless signing (OIDC)
3. Signatures and certificates are uploaded to the release

**Note:** Signing is automatic for tagged releases. Manual builds require manual signing.

## Troubleshooting

### Build Fails: Missing Dependencies

**Error:**
```
ERROR: Missing required dependencies. Please install them first.
```

**Solution:**
Install Python 3.11+:
```bash
# Ubuntu/Debian
sudo apt install python3.11

# macOS
brew install python@3.11

# Windows
# Download from python.org
```

### Build Fails: Android Build Error

**Error:**
```
⚠ Android APK build skipped (Gradle not available)
```

**Solution:**
This is a warning, not an error. To build Android:
```bash
# Install Java 17
sudo apt install openjdk-17-jdk

# Run Gradle build
./gradlew assembleDebug
```

### Build Fails: Desktop Build Error

**Error:**
```
⚠ Desktop builds not found - run npm run build first
```

**Solution:**
```bash
cd desktop
npm install
npm run build
cd ..
```

### Validation Fails: Missing Files

**Error:**
```
✗ Backend: Missing start.sh
```

**Solution:**
Check that all source files exist in the project root before building. Re-run the build script.

### Windows: Archive Creation Failed

**Error:**
```
WARNING 7-Zip not found - skipping archive creation
```

**Solution:**
Install 7-Zip from https://www.7-zip.org/ or manually create ZIP:
```batch
REM Using PowerShell
powershell Compress-Archive -Path releases\project-ai-v1.0.0 -DestinationPath releases\project-ai-v1.0.0.zip
```

### Checksums Don't Match

**Error:**
```
project-ai-v1.0.0.tar.gz: FAILED
```

**Solution:**
Re-download the file or rebuild the release. The archive may have been corrupted during transfer.

## Best Practices

### Version Numbering

Follow Semantic Versioning (SemVer):
- **Major** (1.0.0): Breaking changes
- **Minor** (1.1.0): New features, backward compatible
- **Patch** (1.0.1): Bug fixes

### Pre-Release Testing

Before creating a release:
1. Run full test suite: `pytest`
2. Run linting: `ruff check .`
3. Test the build script locally
4. Validate the generated package
5. Test installation from the package

### Release Checklist

- [ ] Update CHANGELOG.md with release notes
- [ ] Update version in pyproject.toml
- [ ] Update version in package.json
- [ ] Run full test suite
- [ ] Build release package
- [ ] Validate release package
- [ ] Create and push git tag
- [ ] Verify GitHub Actions workflow
- [ ] Verify release artifacts uploaded
- [ ] Verify artifact signatures
- [ ] Test installation from release
- [ ] Announce release

### Security Considerations

1. **Never commit secrets** to the repository
2. **Review .env files** before release
3. **Check for hardcoded credentials** in code
4. **Verify sensitive file cleanup** in release package
5. **Use signed releases** for distribution
6. **Verify checksums** before installation

## CI/CD Integration

### GitHub Actions

The build-release.yml workflow integrates with:
- `sign-release-artifacts.yml` - Artifact signing
- `ci-consolidated.yml` - CI tests
- `security-consolidated.yml` - Security scans

### Custom CI/CD

To integrate with other CI/CD systems:

```yaml
# Example: GitLab CI
build-release:
  stage: build
  image: ubuntu:22.04
  script:
    - apt-get update && apt-get install -y python3 git zip
    - pip3 install -r requirements.txt
    - chmod +x scripts/build_release.sh
    - ./scripts/build_release.sh
  artifacts:
    paths:
      - releases/
    expire_in: 90 days
```

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Email**: projectaidevs@gmail.com
- **Documentation**: See DEPLOYMENT.md, PRODUCTION_DEPLOYMENT.md

## Version History

- **v1.0.0** (2024-01-28)
  - Initial automated release build system
  - Full platform support (Backend, Web, Android, Desktop)
  - Validation and reporting
  - GitHub Actions integration
  - Artifact signing with Sigstore
