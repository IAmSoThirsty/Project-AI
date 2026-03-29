<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Out-Dated(archive) -->
# Release Guide - Thirsty-lang

This guide explains how to prepare, package, and release Thirsty-lang for production use.

## 🚀 Release Checklist

### Pre-Release

- [ ] All tests passing (`npm test`, `npm run test:all`)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with new version
- [ ] VERSION.txt matches package.json version
- [ ] All examples are working
- [ ] Security features are tested
- [ ] README badges are current

### Version Update

- [ ] Update version in `package.json`
- [ ] Update version in `VERSION.txt`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Commit version changes: `git commit -am "Release vX.X.X"`
- [ ] Create git tag: `git tag vX.X.X`
- [ ] Push commits and tags: `git push && git push --tags`

### NPM Publishing

- [ ] Verify npm credentials: `npm whoami`
- [ ] Test package locally: `npm pack`
- [ ] Inspect package contents: `tar -tzf thirsty-lang-*.tgz`
- [ ] Publish to npm: `npm publish`
- [ ] Verify on npm: `npm view thirsty-lang`

### Post-Release

- [ ] Create GitHub Release with release notes
- [ ] Update documentation site
- [ ] Announce release on social media
- [ ] Test installation: `npm install -g thirsty-lang`
- [ ] Verify CLI commands work globally

## 📦 NPM Package Contents

The published npm package includes:

### Core Files

- `src/` - All source code files
- `examples/` - Example Thirsty-lang programs
- `docs/` - Documentation files
- `package.json` - Package metadata

### Tools & Utilities

- `tools/` - Benchmark and utility scripts
- `playground/` - Web-based playground
- `vscode-extension/` - VS Code extension
- `tarl/` - T.A.R.L. integration files

### Documentation

- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- `TUTORIAL.md` - Learning guide
- `QUICKSTART.md` - Getting started
- `DOCUMENTATION.md` - Full documentation
- `DOCKER.md` - Docker guide
- `PYTHON_SETUP.md` - Python setup
- `OPERATIONS.md` - Operations guide
- `SECURITY_API.md` - Security reference
- `TARL_INTEGRATION.md` - T.A.R.L. guide

### Configuration

- `Dockerfile` - Docker configuration
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Python dev dependencies

### Legal

- `LICENSE` - License file
- `AUTHORS.txt` - Contributors
- `DEPENDENCIES.txt` - Dependency info

## 🔧 Release Commands

### Manual Release Process

```bash

# 1. Ensure everything is committed

git status

# 2. Run all tests

npm test
npm run test:all

# 3. Update version (patch/minor/major)

npm version patch  # or minor, or major

# This automatically runs tests, commits, and creates a tag

# 4. Push to GitHub

git push && git push --tags

# 5. Publish to NPM

npm publish

# 6. Verify installation

npm install -g thirsty-lang@latest
thirsty --version
```

### Automated Release Process

The project includes GitHub Actions workflows:

1. **CI/CD Pipeline** (`.github/workflows/ci.yml`)
   - Runs on every push and PR
   - Tests on multiple Node.js versions
   - Builds and archives artifacts
   - Generates documentation

2. **NPM Publishing** (`.github/workflows/publish.yml`)
   - Triggers on GitHub Releases
   - Runs tests before publishing
   - Publishes to NPM registry
   - Uploads release assets

#### Using GitHub Actions

1. **Create a Release on GitHub:**

   ```bash

   # Tag and push

   git tag v2.0.0
   git push origin v2.0.0

   # Create release via GitHub UI or CLI

   gh release create v2.0.0 --title "v2.0.0" --notes "Release notes..."
   ```

2. **The workflow will automatically:**
   - Run all tests
   - Verify package contents
   - Publish to NPM
   - Attach tarball to release

## 🔐 NPM Publishing Setup

### First-Time Setup

1. **Create NPM Account** (if needed)

   ```bash
   npm adduser
   ```

2. **Generate NPM Token** (for CI/CD)
   - Log in to npmjs.com
   - Navigate to Access Tokens
   - Generate new token (Automation type)
   - Add to GitHub Secrets as `NPM_TOKEN`

3. **Configure GitHub Secrets**
   - Repository Settings → Secrets → Actions
   - Add `NPM_TOKEN` with your npm token

### Testing Package Before Publishing

```bash

# Create a test package

npm pack

# Inspect contents

tar -tzf thirsty-lang-2.0.0.tgz

# Test installation locally

npm install -g ./thirsty-lang-2.0.0.tgz

# Test CLI commands

thirsty --help
thirsty examples/hello.thirsty
thirsty-repl
```

## 📊 Version Numbering

Thirsty-lang follows [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes
- **Minor** (x.X.0): New features, backwards compatible
- **Patch** (x.x.X): Bug fixes, backwards compatible

### Current Version: 2.0.0

```bash

# Increment versions

npm version patch  # 2.0.0 → 2.0.1
npm version minor  # 2.0.0 → 2.1.0
npm version major  # 2.0.0 → 3.0.0
```

## 🎯 Release Types

### Stable Releases

- Tagged as `vX.X.X`
- Published with `latest` tag on npm
- Announced publicly
- Full release notes

### Beta Releases

```bash
npm version prerelease --preid=beta

# 2.0.0 → 2.0.1-beta.0

npm publish --tag beta
```

### Release Candidates

```bash
npm version prerelease --preid=rc

# 2.0.0 → 2.0.1-rc.0

npm publish --tag rc
```

## 🧪 Post-Release Verification

After publishing, verify the release:

```bash

# Install globally

npm install -g thirsty-lang@latest

# Check version

thirsty --version

# Should output: 2.0.0 (or current version)

# Test commands

thirsty examples/hello.thirsty
thirsty-repl
thirsty-debug
thirsty-pkg init

# Test REPL

thirsty-repl
> drink x = 5
> pour x

# Uninstall test

npm uninstall -g thirsty-lang
```

## 📝 Release Notes Template

```markdown

## [X.X.X] - YYYY-MM-DD

### Added

- New features added in this release

### Changed

- Changes to existing functionality

### Deprecated

- Features that will be removed in future releases

### Removed

- Features removed in this release

### Fixed

- Bug fixes

### Security

- Security vulnerability fixes

```

## 🔗 Useful Links

- **NPM Package**: https://www.npmjs.com/package/thirsty-lang
- **GitHub Repository**: https://github.com/IAmSoThirsty/Thirsty-lang
- **GitHub Releases**: https://github.com/IAmSoThirsty/Thirsty-lang/releases
- **Documentation**: https://github.com/IAmSoThirsty/Thirsty-lang#readme
- **Issue Tracker**: https://github.com/IAmSoThirsty/Thirsty-lang/issues

## 🆘 Troubleshooting

### "You do not have permission to publish"

- Ensure you're logged in: `npm whoami`
- Check package name isn't taken
- Verify npm account has 2FA enabled

### "Version already published"

- Can't republish same version
- Increment version and try again
- Use `npm version` to bump version

### "Tests failed during prepublishOnly"

- All tests must pass before publishing
- Fix failing tests
- Run `npm test` locally first

### "Tag already exists"

- Delete remote tag: `git push --delete origin vX.X.X`
- Delete local tag: `git tag -d vX.X.X`
- Create new tag with corrected version

## 🏁 Production Ready!

Thirsty-lang is now **100% Real Production** ready with:

✅ Complete npm package configuration
✅ Automated CI/CD pipeline
✅ NPM publishing workflow
✅ Comprehensive testing
✅ Full documentation
✅ CLI tools and utilities
✅ Security features (T.A.R.L.)
✅ Docker support
✅ Python implementation
✅ VS Code extension
✅ Web playground
✅ Example programs

**Ready to hydrate the world! 💧🚀**
