# Thirsty's Gradle: God Tier Monolithic Build System

## 🎯 Overview

**Thirsty's Gradle** is a monolithic, enterprise-grade build orchestration system purpose-built for Project-AI. It unifies all build, test, lint, quality, packaging, and deployment logic across Python, Android, Electron Desktop, Documentation, USB/portable distributions, and future modules into a single, extensible Gradle Kotlin DSL orchestration.

### Philosophy

- **Maximum Density**: One God Tier build entrypoint coordinates everything
- **Zero Fragmentation**: No scattered build scripts, unified orchestration
- **Auto-Discovery**: Automatically detects and integrates modules and subsystems
- **Production-Grade**: No stubs, todos, or placeholders - everything fully implemented
- **Backwards Compatible**: Retains all legacy scripts while providing unified interface

## 🏗️ Architecture

### Core Components

```
build.gradle.kts          # Main monolithic build orchestration (1300+ lines)
settings.gradle.kts       # Module discovery and dependency management
gradle/                   # Gradle wrapper and configuration
  └── wrapper/
gradle.properties         # Project-wide Gradle properties
```

### Module Integration

The build system automatically discovers and integrates:

1. **Python Backend** (`src/app/`, `api/`, `tarl/`, `kernel/`, `engines/`)
   - Virtual environment management
   - Dependency installation (pip)
   - Linting (ruff, black, mypy)
   - Testing (pytest with parallel execution)
   - Security scanning (pip-audit, bandit)
   - Package building (wheel/sdist)
   - Application execution

2. **Android** (`android/`, `app/`)
   - Debug/Release APK builds
   - Unit testing
   - Lint checks
   - Build artifact management

3. **Electron Desktop** (`desktop/`)
   - TypeScript/Vite compilation
   - Multi-platform packaging (Windows, macOS, Linux)
   - Development server
   - Release builds

4. **Documentation** (`docs/`)
   - Sphinx/MkDocs build integration
   - Markdown linting
   - Link verification
   - Publishing automation

5. **USB/Portable Distributions** (`scripts/`)
   - Installation USB creation
   - Portable package generation
   - Universal multi-platform packages

6. **Testing Infrastructure** (`tests/`, `e2e/`, `adversarial_tests/`)
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Adversarial/red-team tests
   - Performance benchmarks

7. **CI/CD Integration**
   - GitHub Actions workflows
   - Docker containerization
   - Release automation
   - Artifact publishing

## 🚀 Quick Start

### Prerequisites

- **JDK 11+** (for Gradle)
- **Python 3.11+** (auto-detected)
- **Node.js 20+** (auto-installed by Gradle)
- **Android SDK** (optional, for Android builds)
- **Docker** (optional, for containerization)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/IAmSoThirsty/Project-AI.git
   cd Project-AI
   ```

2. **Verify Gradle installation**:
   ```bash
   ./gradlew --version
   # or on Windows:
   gradlew.bat --version
   ```

3. **View available tasks**:
   ```bash
   ./gradlew godTierHelp
   # or
   ./gradlew tasks --all
   ```

### First Build

```bash
# Full build (all modules)
./gradlew buildAll

# With checks (lint + test)
./gradlew check

# Clean build
./gradlew clean buildAll
```

## 📋 Core Commands

### God Tier Unified Commands

These commands coordinate across ALL modules:

```bash
# Clean all build artifacts
./gradlew clean

# Run all checks (lint, test, security)
./gradlew check

# Build all modules
./gradlew buildAll

# Full release pipeline
./gradlew release
```

### Python Backend

```bash
# Setup and dependencies
./gradlew pythonVenvCreate       # Create virtual environment
./gradlew pythonInstall          # Install dependencies

# Development
./gradlew pythonLint             # Lint with ruff
./gradlew pythonLintFix          # Auto-fix lint issues
./gradlew pythonFormat           # Format with black
./gradlew pythonTypeCheck        # Type check with mypy

# Testing
./gradlew pythonTest             # Run all tests
./gradlew pythonTestUnit         # Unit tests only
./gradlew pythonTestIntegration  # Integration tests

# Security
./gradlew pythonSecurityScan     # Dependency vulnerability scan
./gradlew securityScanBandit     # Bandit security scanner

# Build and run
./gradlew pythonBuild            # Build Python package
./gradlew pythonRun              # Run desktop app
./gradlew pythonRunApi           # Run API server
```

### Android

```bash
./gradlew androidBuild           # Debug build
./gradlew androidBuildRelease    # Release build
./gradlew androidTest            # Run tests
./gradlew androidLint            # Run lint checks
./gradlew androidClean           # Clean Android artifacts
```

### Electron Desktop

```bash
./gradlew desktopInstall         # Install dependencies
./gradlew desktopBuild           # Build application
./gradlew desktopPackageWin      # Package for Windows
./gradlew desktopPackageMac      # Package for macOS
./gradlew desktopPackageLinux    # Package for Linux
./gradlew desktopPackageAll      # Package for all platforms
```

### Documentation

```bash
./gradlew docsBuild              # Build documentation
./gradlew docsVerify             # Verify links and structure
./gradlew docsPublish            # Publish documentation artifacts
./gradlew npmLintMarkdown        # Lint markdown files
```

### Testing

```bash
./gradlew testAll                # All tests (all modules)
./gradlew testE2E                # End-to-end tests
./gradlew testAdversarial        # Red-team/adversarial tests
./gradlew testPerformance        # Performance benchmarks
```

### Quality & Security

```bash
./gradlew lintAll                # All linters
./gradlew formatAll              # Auto-format all code
./gradlew securityScanAll        # Comprehensive security scan
./gradlew sbomGenerate           # Generate SBOM
```

### USB/Portable Distribution

```bash
./gradlew usbCreateInstaller     # Installation USB
./gradlew usbCreatePortable      # Portable USB package
./gradlew usbCreateUniversal     # Universal multi-platform USB
```

### Docker

```bash
./gradlew dockerBuild            # Build Docker image
./gradlew dockerCompose          # Start compose environment
./gradlew dockerComposeDown      # Stop compose environment
./gradlew dockerPush             # Push to registry
```

### Release & Publishing

```bash
./gradlew releaseCollectArtifacts  # Collect all artifacts
./gradlew releaseGitHubRelease     # Create GitHub release
./gradlew release                  # Full release pipeline
```

## 🎛️ Configuration

### gradle.properties

Project-wide configuration:

```properties
# Project metadata
projectVersion=1.0.0
group=ai.project

# Python configuration
pythonExec=python
pythonVersion=3.11

# Node.js configuration
nodeVersion=20.11.0
npmVersion=10.2.4

# Test configuration
testParallelism=8

# Docker configuration
dockerRegistry=ghcr.io/iamsothirsty

# CI mode
ci=false
```

### Environment Variables

Optional environment variables:

```bash
# Android SDK location
export ANDROID_SDK_ROOT=/path/to/android/sdk
export ANDROID_HOME=/path/to/android/sdk

# CI mode
export CI=true

# Python executable override
export PYTHON_EXEC=python3.11

# Docker registry
export DOCKER_REGISTRY=ghcr.io/myorg
```

## 🔧 Advanced Usage

### Parallel Execution

Gradle automatically parallelizes independent tasks:

```bash
# Use all CPU cores
./gradlew buildAll --parallel

# Limit parallelism
./gradlew buildAll --max-workers=4
```

### Build Cache

Build cache is enabled by default for faster builds:

```bash
# Cache location: .gradle/build-cache
# Retention: 30 days
# No configuration needed - automatic
```

### Incremental Builds

Gradle tracks inputs/outputs for incremental builds:

```bash
# Only rebuild changed components
./gradlew pythonBuild

# Force full rebuild
./gradlew clean pythonBuild
```

### Profile Builds

Analyze build performance:

```bash
./gradlew buildAll --profile

# Report: build/reports/profile/
```

### Continuous Build

Watch for changes and rebuild automatically:

```bash
./gradlew pythonBuild --continuous
```

### Dry Run

Preview tasks without executing:

```bash
./gradlew release --dry-run
```

## 📊 Reports & Artifacts

### Build Outputs

```
build/
├── outputs/              # Build output directory
├── artifacts/            # Release artifacts
│   ├── release/          # Versioned releases
│   ├── docs/             # Documentation
│   └── sbom/             # Software Bill of Materials
├── reports/              # All reports
│   ├── pytest/           # Python test reports
│   │   ├── junit.xml
│   │   ├── coverage.xml
│   │   └── coverage/     # HTML coverage
│   ├── security/         # Security scan reports
│   │   ├── python/
│   │   └── bandit/
│   └── profile/          # Build performance
└── docs/                 # Generated documentation
```

### Artifact Structure

```
build/artifacts/release/1.0.0/
├── python/               # Python wheels/sdist
├── desktop/              # Electron packages
│   ├── win/              # Windows installer
│   ├── mac/              # macOS DMG
│   └── linux/            # Linux AppImage
├── android/              # Android APKs/AABs
└── docs/                 # Documentation bundle
```

## 🔌 Extensibility

### Adding New Modules

The system auto-discovers modules. To add a new module:

1. **Create module directory** with appropriate build files
2. **Add to discovery logic** in `build.gradle.kts` if needed
3. **Create module-specific tasks** following existing patterns
4. **Integrate with unified commands** (`buildAll`, `testAll`, etc.)

Example for a new Rust module:

```kotlin
// In build.gradle.kts

if (file("rust_module").exists()) {
    discoveredModules.add("rust-module")
    
    tasks.register<Exec>("rustBuild") {
        group = "rust"
        description = "Build Rust module"
        
        workingDir = file("rust_module")
        commandLine("cargo", "build", "--release")
    }
    
    // Add to buildAll
    tasks.named("buildAll").configure {
        dependsOn("rustBuild")
    }
}
```

### Custom Task Types

Create reusable task types:

```kotlin
// Custom task type for multi-platform builds
abstract class MultiPlatformBuildTask : DefaultTask() {
    @Input
    abstract val platforms: ListProperty<String>
    
    @TaskAction
    fun execute() {
        platforms.get().forEach { platform ->
            project.exec {
                commandLine("build-for-$platform")
            }
        }
    }
}

// Register task
tasks.register<MultiPlatformBuildTask>("myMultiBuild") {
    platforms.set(listOf("windows", "linux", "macos"))
}
```

### Plugin Development

Create custom Gradle plugins for complex logic:

```kotlin
// In buildSrc/src/main/kotlin/MyPlugin.kt
class MyPlugin : Plugin<Project> {
    override fun apply(project: Project) {
        project.tasks.register("myCustomTask") {
            doLast {
                println("Custom plugin task executed")
            }
        }
    }
}

// Apply in build.gradle.kts
apply<MyPlugin>()
```

## 🔄 CI/CD Integration

### GitHub Actions

The build system integrates with existing GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Build
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
      - name: Build
        run: ./gradlew check buildAll
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: artifacts
          path: build/artifacts/
```

### Automated Releases

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
      - name: Full Release
        run: ./gradlew release
        env:
          CI: true
      - name: Create GitHub Release
        run: ./gradlew releaseGitHubRelease
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Docker Integration

```yaml
# .github/workflows/docker.yml
name: Docker
on: [push]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
      - name: Build Docker Image
        run: ./gradlew dockerBuild
      - name: Push to Registry
        run: ./gradlew dockerPush
        env:
          DOCKER_REGISTRY: ghcr.io/iamsothirsty
```

## 🐛 Troubleshooting

### Common Issues

#### Python Virtual Environment Not Found

```bash
# Recreate virtual environment
./gradlew pythonVenvCreate --rerun-tasks
```

#### Node.js Download Failed

```bash
# Clear Gradle cache
rm -rf .gradle/nodejs .gradle/npm
./gradlew npmInstall --refresh-dependencies
```

#### Android SDK Not Found

```bash
# Set environment variable
export ANDROID_SDK_ROOT=/path/to/android/sdk
./gradlew androidBuild
```

#### Permission Denied (Linux/macOS)

```bash
# Make gradlew executable
chmod +x gradlew
./gradlew buildAll
```

#### Build Cache Issues

```bash
# Clear build cache
rm -rf .gradle/build-cache
./gradlew buildAll
```

### Debug Mode

Enable detailed logging:

```bash
# Debug output
./gradlew buildAll --debug > build.log

# Info level
./gradlew buildAll --info

# Stack traces
./gradlew buildAll --stacktrace
```

### Clean Slate

Complete reset:

```bash
# Remove all caches and artifacts
./gradlew clean
rm -rf .gradle build dist .venv node_modules
./gradlew buildAll
```

## 📚 Migration Guide

### From Existing Build Systems

#### From Makefile

Old:
```bash
make test
make lint
make build
```

New:
```bash
./gradlew pythonTest
./gradlew pythonLint
./gradlew pythonBuild
```

#### From npm scripts

Old:
```bash
npm run test
npm run build
npm run dev
```

New:
```bash
./gradlew npmTest
./gradlew npmBuild
./gradlew npmDev
```

#### From Python setup.py

Old:
```bash
python setup.py test
python setup.py build
python -m pip install -e .
```

New:
```bash
./gradlew pythonTest
./gradlew pythonBuild
./gradlew pythonInstall
```

### Backwards Compatibility

All legacy scripts remain functional:

- `Makefile` - Still works
- `package.json` scripts - Still work
- `pyproject.toml` - Still used by Gradle
- `scripts/*.sh` - Still executable
- Android `build.gradle` - Integrated, not replaced

The Gradle system **wraps and orchestrates** existing tools rather than replacing them.

## 🎓 Best Practices

### Development Workflow

1. **Start with install**:
   ```bash
   ./gradlew pythonInstall npmInstall desktopInstall
   ```

2. **Develop with checks**:
   ```bash
   ./gradlew pythonTest --continuous
   ```

3. **Pre-commit validation**:
   ```bash
   ./gradlew lintAll testAll
   ```

4. **Before push**:
   ```bash
   ./gradlew check
   ```

### Release Workflow

1. **Update version** in `gradle.properties`:
   ```properties
   projectVersion=1.1.0
   ```

2. **Run release pipeline**:
   ```bash
   ./gradlew release
   ```

3. **Verify artifacts**:
   ```bash
   ls -R build/artifacts/release/1.1.0/
   ```

4. **Publish**:
   ```bash
   ./gradlew releaseGitHubRelease
   ```

### Performance Tips

- **Use build cache**: Enabled by default
- **Parallel execution**: `--parallel` flag
- **Incremental builds**: Don't clean unless necessary
- **Selective execution**: Run only what changed
- **Profile builds**: Use `--profile` to identify bottlenecks

## 🔐 Security

### Security Scanning

The build system includes comprehensive security scanning:

```bash
# Python dependency vulnerabilities
./gradlew pythonSecurityScan

# Python code security issues
./gradlew securityScanBandit

# All security scans
./gradlew securityScanAll
```

### SBOM Generation

Generate Software Bill of Materials for compliance:

```bash
./gradlew sbomGenerate

# Output: build/artifacts/sbom/
#   - python-dependencies.txt
#   - npm-dependencies.json
```

### Secure Releases

Release pipeline includes:
- Dependency vulnerability scanning
- Code security analysis
- SBOM generation
- Artifact integrity verification

## 📖 Additional Resources

### Documentation

- **Architecture Reference**: `.github/ARCHITECTURE_QUICK_REF.md`
- **Developer Guide**: `DEVELOPER_QUICK_REFERENCE.md`
- **API Documentation**: `docs/README.md`
- **Security Guide**: `SECURITY.md`

### Community

- **Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Discussions**: https://github.com/IAmSoThirsty/Project-AI/discussions
- **Contributing**: `CODE_OF_CONDUCT.md`

### Related Tools

- **Gradle**: https://gradle.org/
- **Gradle Kotlin DSL**: https://docs.gradle.org/current/userguide/kotlin_dsl.html
- **Node Gradle Plugin**: https://github.com/node-gradle/gradle-node-plugin

## 🏆 God Tier Features

### Maximum Density

Single entry point for ALL operations:
- 1 command to clean everything: `./gradlew clean`
- 1 command to test everything: `./gradlew testAll`
- 1 command to build everything: `./gradlew buildAll`
- 1 command to release everything: `./gradlew release`

### Auto-Discovery

Automatically discovers and integrates:
- New modules (just create directories)
- New test suites (pytest auto-discovery)
- New plugins (TARL, custom engines)
- New platforms (extend existing patterns)

### Zero Configuration

Works out of the box:
- No setup required beyond JDK
- Auto-installs Node.js
- Auto-creates Python venv
- Auto-detects Android SDK
- Sensible defaults for everything

### Production-Ready

Enterprise-grade implementation:
- Comprehensive error handling
- Detailed logging and reporting
- Artifact management
- Security scanning
- SBOM generation
- CI/CD integration

### Extensible Architecture

Easy to extend:
- Plugin system
- Custom task types
- Module discovery
- Hook points everywhere
- Well-documented patterns

---

## ⚡ Quick Reference Card

```bash
# GOD TIER COMMANDS
./gradlew clean               # Clean everything
./gradlew check               # Lint + Test + Security
./gradlew buildAll            # Build all modules
./gradlew release             # Full release pipeline

# DEVELOPMENT
./gradlew pythonRun           # Run desktop app
./gradlew pythonRunApi        # Run API server
./gradlew desktopBuild        # Build Electron app

# TESTING
./gradlew testAll             # All tests
./gradlew pythonTest          # Python tests
./gradlew testE2E             # E2E tests

# QUALITY
./gradlew lintAll             # All linters
./gradlew formatAll           # Auto-format
./gradlew securityScanAll     # Security scans

# PACKAGING
./gradlew desktopPackageAll   # Desktop (all platforms)
./gradlew androidBuildRelease # Android release
./gradlew usbCreateUniversal  # USB installer

# HELP
./gradlew godTierHelp         # This system's help
./gradlew tasks --all         # All available tasks
```

---

**Thirsty's Gradle - Where Maximum Density Meets God Tier Engineering** 🚀

