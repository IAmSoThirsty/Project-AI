# Deployment & Release Checklist

This document captures the deployment and release process for Project-AI. For detailed automated build instructions, see [RELEASE_BUILD_GUIDE.md](docs/historical/RELEASE_BUILD_GUIDE.md).

## Automated Release Process (Recommended)

The recommended way to create releases is using the automated build system:

### Quick Release

```bash
# 1. Ensure all changes are committed
git add .
git commit -m "Release v1.0.0"
git push

# 2. Create and push version tag
git tag v1.0.0
git push origin v1.0.0
```

The GitHub Actions workflow automatically:
- Validates all dependencies
- Builds backend, web, Android, and desktop artifacts
- Packages monitoring agents and documentation
- Runs validation checks
- Creates release archives
- Generates JSON reports with checksums
- Creates GitHub release with all artifacts
- Triggers artifact signing with Sigstore

### Manual Build

For local builds or testing:

```bash
# Linux/macOS
./scripts/build_release.sh

# Windows
scripts\build_release.bat
```

See [RELEASE_BUILD_GUIDE.md](docs/historical/RELEASE_BUILD_GUIDE.md) for complete instructions.

## Manual Deployment (Legacy)

## Desktop Application

1. **Install dependencies**

   ```powershell
   py -3.11 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

1. **Run pytest suite**

   ```powershell
   $env:PYTHONPATH='src'
   python -m pytest --maxfail=1 --disable-warnings
   ```

1. **Build the PyQt6 executable**
   - Use `pyinstaller` (install via `pip install pyinstaller`) with a spec that includes `src/app/main.py`.
   - Example: `pyinstaller --onefile --name project-ai src/app/main.py`.
1. **Bundle assets**
   - Copy `data/`, `docs/`, and `web/` artifacts into the distributable folder.
   - Ensure `FERNET_KEY`, API keys, and overrides are provided via environment or secure secrets vault (do not hardcode them).
1. **Sign and publish**
   - Sign the executable using the organization’s code signing certificate.
   - Upload the installer/archive to the private release server or shared file storage.
   - Update release notes with new AI capabilities, vulnerability fixes, and CLI updates.

## Web Backend & Frontend

The repo ships minimal frontend/backed smoke scaffolds that are not production-grade yet, but the release steps below ensure the placeholders remain runnable.

1. **Web backend (Flask)**

   ```powershell
   $env:PYTHONPATH='web/backend'
   flask --app web.backend.app run
   ```

1. **Frontend**
   - Serve `web/frontend/index.html` via any static file server (e.g., `python -m http.server 3000`).
   - Validate the page loads and shows the smoke content.
1. **Integrate with desktop release**
   - Embed the Flask backend and front-end artifacts inside the `data/web` folder so the desktop app can point WebView/HTTP clients to `http://localhost:5000`.

## Release Checklist

### Automated Release
- [ ] Update `README.md`, `PROGRAM_SUMMARY.md`, and developer docs with new features
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Bump version in `pyproject.toml` and `package.json`
- [ ] Run formatting (`ruff check . --fix`) and markdown lint
- [ ] Run full test suite: `pytest`
- [ ] Commit all changes
- [ ] Create and push version tag: `git tag v1.0.0 && git push origin v1.0.0`
- [ ] Verify GitHub Actions workflow completes successfully
- [ ] Verify release artifacts are uploaded to GitHub release
- [ ] Verify artifact signatures are present
- [ ] Test installation from release package
- [ ] Notify team members via Slack/email with release summary

### Manual Release
- [ ] Follow all automated release steps above
- [ ] Run `./scripts/build_release.sh` (or `.bat` on Windows)
- [ ] Review `releases/validation-report-v*.json` for any issues
- [ ] Review `releases/release-summary-v*.json` for completeness
- [ ] Manually create GitHub release and upload artifacts
- [ ] Publish artifacts along with changelog entries
- [ ] Notify team members via Slack/email with release summary and testing status

## Validation

After building, validate the release package:

```bash
python3 scripts/validate_release.py releases/project-ai-v1.0.0 --version 1.0.0
```

This checks:
- Directory structure completeness
- Backend API artifacts (api, tarl, governance, config, utils, kernel)
- Web frontend files
- Android APK (if built)
- Desktop installers (if built)
- Monitoring agents configuration
- Complete documentation
- MANIFEST.in compliance

## Distribution Package Contents

A complete release includes:

```
project-ai-v1.0.0/
├── backend/          # Python FastAPI with TARL governance
├── web/             # Browser-based interface
├── android/         # APK for Android 7.0+ devices
├── desktop/         # Electron apps for Win/Mac/Linux
├── monitoring/      # Prometheus, Grafana, AlertManager
├── docs/           # Complete documentation
├── README.md       # Release overview
├── CONSTITUTION.md # AGI charter
├── CHANGELOG.md    # Version history
├── LICENSE         # MIT license
└── SECURITY.md     # Security policies
```

## Support

For detailed build instructions, troubleshooting, and CI/CD integration:
- See [RELEASE_BUILD_GUIDE.md](docs/historical/RELEASE_BUILD_GUIDE.md)
- See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) for deployment
- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
