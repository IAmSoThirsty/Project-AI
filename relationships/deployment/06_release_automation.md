# 06: Release Automation Relationships

**Document**: Automated Release Build and Distribution  
**System**: Version Bumping, Changelog Generation, GitHub Releases  
**Related Systems**: CI/CD, Desktop Packaging, Docker Registry

---


## Navigation

**Location**: `relationships\deployment\06_release_automation.md`

**Parent**: [[relationships\deployment\README.md]]


## Release Automation Flow

```
┌──────────────────────────────────────────────────────────┐
│              RELEASE AUTOMATION PIPELINE                  │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Developer Creates Git Tag                               │
│  └─→ git tag v1.0.1                                      │
│  └─→ git push origin v1.0.1                              │
│           ↓                                               │
│  ┌─────────────────────────────────────┐                 │
│  │  GitHub Actions Trigger             │                 │
│  │  (on: push tags: 'v*')             │                 │
│  └──────────────┬──────────────────────┘                 │
│                 ↓                                         │
│  ┌──────────────────────────────────────────┐            │
│  │  Build Release Artifacts                 │            │
│  │                                          │            │
│  │  1. Extract version from tag (v1.0.1)  │            │
│  │  2. Update version in files:            │            │
│  │     • pyproject.toml                    │            │
│  │     • package.json                      │            │
│  │     • src/app/__version__.py            │            │
│  │  3. Build artifacts:                    │            │
│  │     • Desktop installers (Win/Mac/Linux)│            │
│  │     • Android APK                       │            │
│  │     • Docker images                     │            │
│  │     • Python wheel (.whl)               │            │
│  │  4. Generate checksums (SHA256)         │            │
│  └──────────────┬───────────────────────────┘            │
│                 ↓                                         │
│  ┌──────────────────────────────────────────┐            │
│  │  Generate Release Notes                  │            │
│  │                                          │            │
│  │  • Parse CHANGELOG.md                   │            │
│  │  • Extract section for v1.0.1           │            │
│  │  • Generate commit summary since v1.0.0 │            │
│  │  • List contributors                     │            │
│  └──────────────┬───────────────────────────┘            │
│                 ↓                                         │
│  ┌──────────────────────────────────────────┐            │
│  │  Create GitHub Release                   │            │
│  │                                          │            │
│  │  • Title: "Project-AI v1.0.1"          │            │
│  │  • Body: Release notes (Markdown)       │            │
│  │  • Assets:                              │            │
│  │    - Project-AI-Setup.exe (Windows)     │            │
│  │    - ProjectAI.dmg (macOS)              │            │
│  │    - project-ai.AppImage (Linux)        │            │
│  │    - legion_mini-release.apk (Android)  │            │
│  │    - project_ai-1.0.1-py3-none-any.whl  │            │
│  │    - checksums.txt                      │            │
│  │  • Pre-release: false                   │            │
│  │  • Draft: false                         │            │
│  └──────────────┬───────────────────────────┘            │
│                 ↓                                         │
│  ┌──────────────────────────────────────────┐            │
│  │  Publish to Package Managers             │            │
│  │                                          │            │
│  │  • PyPI: twine upload dist/*.whl        │            │
│  │  • Docker Hub: docker push v1.0.1       │            │
│  │  • Homebrew: Update formula             │            │
│  │  • Chocolatey: Update package           │            │
│  └──────────────────────────────────────────┘            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Version Management

### Semantic Versioning
```
Version Format: MAJOR.MINOR.PATCH
    v1.0.1
     │ │ │
     │ │ └─→ Patch: Backward-compatible bug fixes
     │ └───→ Minor: New features (backward-compatible)
     └─────→ Major: Breaking changes

Pre-release Tags:
    v1.0.1-alpha.1  (alpha testing)
    v1.0.1-beta.2   (beta testing)
    v1.0.1-rc.3     (release candidate)
```

### Version Bump Workflow
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract Version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Update Version Files
        run: |
          VERSION=${{ steps.version.outputs.version }}
          sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
          sed -i "s/\"version\": .*/\"version\": \"$VERSION\",/" package.json
          echo "__version__ = '$VERSION'" > src/app/__version__.py
      
      - name: Commit Version Bump
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add .
          git commit -m "chore: Bump version to ${{ steps.version.outputs.version }}"
          git push origin main
```

## Changelog Generation

### Conventional Commits
```
Commit Types:
    feat:     New feature
    fix:      Bug fix
    docs:     Documentation
    style:    Formatting
    refactor: Code refactoring
    perf:     Performance improvement
    test:     Test additions
    chore:    Maintenance tasks

Example Commits:
    feat(auth): Add biometric login support
    fix(gui): Resolve window positioning issue on multi-monitor
    docs(api): Update OpenAI integration guide
    perf(memory): Optimize knowledge base search (30% faster)
```

### Auto-Generated Changelog
```bash
# Using git-chglog or conventional-changelog
git-chglog --next-tag v1.0.1 > CHANGELOG.md
```

### CHANGELOG.md Format
```markdown
# Changelog

## [1.0.1] - 2026-04-20

### Added
- feat(desktop): Portable USB installer with Legion Mini wizard
- feat(security): Fernet encryption for location history

### Fixed
- fix(auth): Password timing attack vulnerability (CVE-2024-XXXX)
- fix(gui): Dashboard panel rendering on high-DPI displays

### Changed
- perf(ai): Optimize persona state loading (50ms → 10ms)
- refactor(core): Extract command override to separate module

### Security
- Upgrade cryptography to 42.0.5 (fixes CVE-2024-YYYY)
- Enable SHA-256 for master password hashing

### Deprecated
- Deprecate MD5 hash usage (use SHA-256)

### Removed
- Remove deprecated `LegacyAuthManager` class

## [1.0.0] - 2026-04-01
Initial release
```

## Build Script Integration

### Cross-Platform Build
```powershell
# scripts/build_release.ps1
param(
    [string]$Version
)

Write-Host "Building Project-AI v$Version"

# Build Windows Installer
Write-Host "Building Windows installer..."
pyinstaller project-ai.spec
makensis project-ai-installer.nsi
Move-Item "Output\Project AI Setup.exe" "dist\Project-AI-$Version-Setup.exe"

# Build macOS DMG
if ($IsMacOS) {
    Write-Host "Building macOS DMG..."
    pyinstaller project-ai.spec --windowed
    create-dmg dist/ProjectAI.app
    Move-Item "ProjectAI.dmg" "dist/ProjectAI-$Version.dmg"
}

# Build Linux AppImage
if ($IsLinux) {
    Write-Host "Building Linux AppImage..."
    pyinstaller project-ai.spec
    appimagetool dist/project-ai dist/project-ai-$Version.AppImage
}

# Build Android APK
Write-Host "Building Android APK..."
./gradlew :legion_mini:assembleRelease
Move-Item "android/legion_mini/build/outputs/apk/release/legion_mini-release.apk" `
          "dist/legion_mini-$Version.apk"

# Build Python Wheel
Write-Host "Building Python wheel..."
python -m build --wheel
Move-Item "dist/project_ai-$Version-py3-none-any.whl" "dist/"

# Generate Checksums
Write-Host "Generating checksums..."
Get-ChildItem dist/*.exe, dist/*.dmg, dist/*.AppImage, dist/*.apk, dist/*.whl |
    ForEach-Object {
        $hash = Get-FileHash -Algorithm SHA256 -Path $_.FullName
        "$($hash.Hash)  $($_.Name)" | Out-File -Append "dist/checksums.txt"
    }

Write-Host "Release build complete: dist/"
```

## GitHub Release Creation

### Release API Workflow
```yaml
- name: Create GitHub Release
  uses: actions/create-release@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
    tag_name: ${{ github.ref }}
    release_name: Project-AI ${{ steps.version.outputs.version }}
    body_path: RELEASE_NOTES.md
    draft: false
    prerelease: false

- name: Upload Release Assets
  uses: actions/upload-release-asset@v1
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  with:
    upload_url: ${{ steps.create_release.outputs.upload_url }}
    asset_path: ./dist/Project-AI-${{ steps.version.outputs.version }}-Setup.exe
    asset_name: Project-AI-Setup.exe
    asset_content_type: application/octet-stream
```

### Asset Upload Loop
```yaml
- name: Upload All Release Assets
  run: |
    for file in dist/*; do
      gh release upload ${{ github.ref_name }} "$file" --clobber
    done
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Package Manager Distribution

### PyPI Publication
```yaml
- name: Publish to PyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    user: __token__
    password: ${{ secrets.PYPI_API_TOKEN }}
    packages_dir: dist/
    skip_existing: false
```

### Docker Image Tags
```bash
# Tag and push Docker images
VERSION=1.0.1
docker build -t projectai/backend:$VERSION .
docker tag projectai/backend:$VERSION projectai/backend:latest
docker tag projectai/backend:$VERSION projectai/backend:1.0
docker tag projectai/backend:$VERSION projectai/backend:1

docker push projectai/backend:$VERSION
docker push projectai/backend:latest
docker push projectai/backend:1.0
docker push projectai/backend:1
```

### Homebrew Formula Update
```ruby
# homebrew-project-ai/project-ai.rb
class ProjectAi < Formula
  desc "Self-aware AI assistant with ethical decision-making"
  homepage "https://github.com/IAmSoThirsty/Project-AI"
  url "https://github.com/IAmSoThirsty/Project-AI/releases/download/v1.0.1/project-ai-1.0.1.tar.gz"
  sha256 "abc123..."
  license "MIT"

  depends_on "python@3.11"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/project-ai", "--version"
  end
end
```

### Chocolatey Package
```xml
<!-- project-ai.nuspec -->
<package>
  <metadata>
    <id>project-ai</id>
    <version>1.0.1</version>
    <title>Project-AI</title>
    <authors>IAmSoThirsty</authors>
    <description>Self-aware AI assistant</description>
    <projectUrl>https://github.com/IAmSoThirsty/Project-AI</projectUrl>
    <tags>ai assistant ethics pyqt6</tags>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

## Release Notification

### Slack Notification
```yaml
- name: Notify Slack of Release
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "🎉 New Release: Project-AI v${{ steps.version.outputs.version }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Release Notes*\n${{ steps.changelog.outputs.notes }}"
            }
          },
          {
            "type": "actions",
            "elements": [
              {
                "type": "button",
                "text": {"type": "plain_text", "text": "View Release"},
                "url": "https://github.com/IAmSoThirsty/Project-AI/releases/tag/${{ github.ref_name }}"
              }
            ]
          }
        ]
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Rollback Procedure

### Release Rollback
```bash
# Delete bad release
gh release delete v1.0.2 --yes

# Delete tag
git tag -d v1.0.2
git push origin :refs/tags/v1.0.2

# Recreate release with fix
git tag v1.0.3
git push origin v1.0.3
```

## Related Systems

- `04_desktop_packaging.md` - Desktop installer builds
- `05_cicd_pipelines.md` - CI/CD automation
- `02_docker_relationships.md` - Docker image tagging

---

**Status**: ✅ Complete  
**Coverage**: Version management, changelog generation, GitHub Releases, package distribution
