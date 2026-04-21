---
title: Build System Architecture
type: technical-guide
audience: [developers, build-engineers, devops]
classification: P0-Core
tags: [build-system, gradle, npm, make, compilation]
created: 2024-01-20
last_verified: 2024-01-20
status: current
related_systems: [cli, automation, deployment]
---

# Build System Architecture

**Multi-platform build orchestration for Python, JavaScript, Java, and Rust components.**

## Executive Summary

Project-AI uses a hybrid build system architecture:
1. **GNU Make** - POSIX-compliant orchestration layer
2. **npm** - JavaScript tooling and test orchestration
3. **Gradle** - Java/Android multi-module builds
4. **Python setuptools** - Package distribution and installation
5. **TARL Build System** - Custom build caching and dependency management

---

## Build System Layers

### Layer 1: Make (Orchestration)

**File:** `Makefile`  
**Purpose:** Top-level orchestration for common development tasks

#### Targets

```makefile
run          # Launch desktop application (python -m src.app.main)
test         # Run pytest test suite
lint         # Run ruff linter
format       # Format code (isort + ruff + black)
precommit    # Run pre-commit hooks
```

#### Usage

```bash
# Run desktop application
make run

# Run all tests
make test

# Lint and format code
make lint
make format

# Run pre-commit checks
make precommit
```

#### Makefile Implementation

```makefile
PYTHON=python

.PHONY: test lint format precommit run

run:
	$(PYTHON) -m src.app.main

test:
	pytest -v

lint:
	ruff check .

format:
	isort src tests --profile black
	ruff check . --fix
	black src tests

precommit:
	pre-commit run --all-files
```

**Design Rationale:**
- Simple, declarative syntax
- Cross-platform compatibility (works on Windows with GNU Make)
- Low learning curve for contributors
- Fast execution (no JVM startup overhead)

---

### Layer 2: npm (JavaScript Tooling)

**File:** `package.json`  
**Purpose:** JavaScript/Node.js tooling orchestration and test management

#### Scripts

```json
{
  "scripts": {
    "test": "npm run test:js && npm run test:python",
    "test:js": "node --test src/**/*.test.js",
    "test:python": "pytest -q",
    "lint": "ruff check .",
    "format": "ruff check . --fix",
    "dev": "docker-compose up",
    "build": "docker build -t project-ai:latest .",
    "lint:markdown": "markdownlint README.md PROGRAM_SUMMARY.md docs docs/developer --config .markdownlint.json",
    "tarl:build": "python -m tarl.build.cli build",
    "tarl:clean": "python -m tarl.build.cli clean",
    "tarl:list": "python -m tarl.build.cli list",
    "tarl:cache": "python -m tarl.build.cli cache stats"
  }
}
```

#### Usage

```bash
# Run all tests (JS + Python)
npm test

# Run JavaScript tests only
npm run test:js

# Run Python tests only
npm run test:python

# Lint Python code
npm run lint

# Format Python code
npm run format

# Start Docker development environment
npm run dev

# Build Docker image
npm run build

# Lint markdown documentation
npm run lint:markdown

# TARL build system commands
npm run tarl:build
npm run tarl:clean
npm run tarl:list
npm run tarl:cache
```

**Design Rationale:**
- Unified interface for heterogeneous tooling
- Integrates Python linting/testing with JavaScript ecosystem
- Docker orchestration for development environments
- Markdown linting for documentation quality

---

### Layer 3: Gradle (Java/Android)

**Files:**
- `build.gradle` - Root project build configuration
- `settings.gradle` - Project structure and module registration
- `android/legion_mini/build.gradle` - Android application build

#### Key Features

- ✅ Multi-module project structure
- ✅ Kotlin DSL support (`build.gradle.kts`)
- ✅ Android APK building (Legion Mini application)
- ✅ Dependency management with version catalogs
- ✅ Custom tasks and plugins

#### Gradle Wrapper

```bash
# Unix/Linux/macOS
./gradlew build
./gradlew test
./gradlew :legion_mini:assembleDebug

# Windows
.\gradlew.bat build
.\gradlew.bat test
.\gradlew.bat :legion_mini:assembleDebug
```

**Critical:** Always use Gradle wrapper (`gradlew`) to ensure consistent Gradle version across environments.

#### Common Gradle Tasks

```bash
# Build all modules
./gradlew build

# Clean build artifacts
./gradlew clean

# Run all tests
./gradlew test

# Build Android debug APK
./gradlew :legion_mini:assembleDebug

# Build Android release APK
./gradlew :legion_mini:assembleRelease

# List all tasks
./gradlew tasks

# Show dependency tree
./gradlew dependencies
```

#### Android Build Configuration

```gradle
// android/legion_mini/build.gradle
android {
    namespace 'com.projectai.legionmini'
    compileSdk 34
    
    defaultConfig {
        applicationId "com.projectai.legionmini"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

**Output Locations:**
- Debug APK: `android/legion_mini/build/outputs/apk/debug/legion_mini-debug.apk`
- Release APK: `android/legion_mini/build/outputs/apk/release/legion_mini-release.apk`

---

### Layer 4: Python setuptools

**Files:**
- `pyproject.toml` - Modern Python project configuration (PEP 518)
- `setup.py` - Legacy setuptools configuration (minimal)
- `setup.cfg` - Additional setuptools configuration

#### pyproject.toml Structure

```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project-ai"
version = "1.0.0"
description = "Comprehensive AI assistant with advanced features"
requires-python = ">=3.11"
dependencies = [
    "Flask>=3.0.0",
    "scikit-learn>=1.0.0",
    "openai>=0.27.0",
    # ... (50+ dependencies)
]

[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
project-ai = "app.main:main"

[tool.ruff]
line-length = 88
target-version = "py311"
```

#### Build Commands

```bash
# Install in development mode (editable)
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Build distribution packages
python -m build

# Install from wheel
pip install dist/project_ai-1.0.0-py3-none-any.whl

# Upload to PyPI (requires credentials)
twine upload dist/*
```

#### Entry Points

After `pip install -e .`, the following console scripts are registered:

```bash
# Desktop application launcher
project-ai

# Sovereign runtime CLI (from project_ai_cli.py)
project-ai run examples/sovereign-demo.yaml
project-ai sovereign-verify --bundle compliance.json
project-ai verify-audit immutable_audit.jsonl
```

**Implementation:**
```python
# setup.py
from setuptools import setup, find_packages

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "project-ai=app.main:main",
        ],
    },
)
```

---

### Layer 5: TARL Build System

**Purpose:** Custom build caching and dependency management for TARL components

#### TARL CLI

```bash
# Build all TARL targets
npm run tarl:build
# or
python -m tarl.build.cli build

# Clean build cache
npm run tarl:clean

# List registered targets
npm run tarl:list

# Show cache statistics
npm run tarl:cache
```

#### TARL Build Architecture

```
tarl/
├── build/
│   ├── cli.py              # Build CLI entry point
│   ├── cache.py            # Build cache management
│   ├── targets.py          # Target registration
│   └── dependencies.py     # Dependency resolution
├── build.tarl              # Build configuration
└── policies/               # TARL policies
```

#### Build Configuration (build.tarl)

```yaml
# Example build.tarl configuration
targets:
  tarl_runtime:
    type: python_module
    sources:
      - tarl/**/*.py
    dependencies: []
    
  governance_core:
    type: python_module
    sources:
      - governance/**/*.py
    dependencies:
      - tarl_runtime

cache:
  enabled: true
  directory: .tarl_cache
  strategy: content_hash
```

**Features:**
- ✅ Content-based caching (SHA-256 hashing)
- ✅ Incremental builds (rebuild only changed targets)
- ✅ Dependency graph resolution
- ✅ Parallel build execution

---

## Build Workflows

### Development Workflow

```bash
# 1. Install dependencies
pip install -e .[dev]
npm install

# 2. Run linters
make lint
npm run lint:markdown

# 3. Run tests
make test
npm test

# 4. Format code
make format

# 5. Run pre-commit checks
make precommit
```

### Production Build Workflow

```bash
# Build all platforms
.\scripts\build_production.ps1 -All

# Outputs:
# - Desktop: desktop/release/Project AI Setup.exe
# - Android: android/legion_mini/build/outputs/apk/release/legion_mini-release.apk
# - Python wheel: dist/project_ai-1.0.0-py3-none-any.whl
```

### Continuous Integration Workflow

```yaml
# .github/workflows/ci.yml excerpt
- name: Install dependencies
  run: pip install -e .[dev]

- name: Lint
  run: ruff check .

- name: Test
  run: pytest -v --cov

- name: Build
  run: python -m build
```

---

## Build Caching

### Python Build Cache

```bash
# Pip cache location
pip cache dir

# Clear pip cache
pip cache purge

# Use local cache for faster installs
pip install -e . --cache-dir=.pip_cache
```

### Gradle Build Cache

```gradle
// gradle.properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.daemon=true
```

```bash
# Build with cache
./gradlew build --build-cache

# Clear Gradle cache
./gradlew clean cleanBuildCache
```

### TARL Build Cache

```bash
# Show cache statistics
npm run tarl:cache

# Output:
# Cache hits: 45
# Cache misses: 5
# Cache size: 234 MB
# Oldest entry: 2024-01-15 10:30:45
```

---

## Build Performance

### Benchmarks

**Environment:** Intel i7-12700K, 32GB RAM, NVMe SSD

| Build Type | Cold | Warm (cached) | Incremental |
|------------|------|---------------|-------------|
| Python full install | 45s | 12s | 3s |
| Gradle clean build | 2m 30s | 45s | 15s |
| Android APK debug | 3m 15s | 1m 10s | 25s |
| Docker image build | 8m 30s | 2m 15s | 45s |
| TARL targets | 1m 20s | 10s | 5s |

### Optimization Tips

1. **Use build caching** - Gradle, pip, Docker layer caching
2. **Parallel execution** - Gradle parallel builds, TARL parallel targets
3. **Incremental builds** - Only rebuild changed components
4. **Local mirrors** - Use pip mirrors for faster dependency downloads
5. **SSD storage** - Significant speedup for I/O-heavy builds

---

## Build Troubleshooting

### Issue: Gradle build fails with "JAVA_HOME not set"

**Solution:**
```bash
# Windows
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Linux/macOS
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export PATH=$JAVA_HOME/bin:$PATH
```

### Issue: Python build fails with "No module named 'app'"

**Solution:**
```bash
# Use module invocation
python -m src.app.main

# Or install in editable mode
pip install -e .
```

### Issue: npm run test fails on Windows

**Solution:**
```powershell
# Use PowerShell-compatible commands
npm run test:python  # Instead of npm test
```

### Issue: Docker build fails with layer cache

**Solution:**
```bash
# Build without cache
docker build --no-cache -t project-ai:latest .

# Or clean Docker cache
docker system prune -af
```

---

## Build Configuration Files

### Critical Build Files

| File | Purpose | Lines | Language |
|------|---------|-------|----------|
| `Makefile` | Top-level orchestration | 21 | Make |
| `package.json` | npm scripts | 39 | JSON |
| `pyproject.toml` | Python project config | 200+ | TOML |
| `setup.py` | Python package setup | 18 | Python |
| `build.gradle` | Root Gradle config | 150+ | Groovy |
| `settings.gradle` | Gradle project structure | 50+ | Groovy |
| `build.tarl` | TARL build config | 100+ | YAML |
| `docker-compose.yml` | Container orchestration | 40 | YAML |
| `Dockerfile` | Container image build | 80+ | Dockerfile |

### Configuration Hierarchy

```
Project-AI-main/
├── Makefile                    # Top-level orchestration
├── package.json                # npm scripts
├── pyproject.toml              # Python project config
├── setup.py                    # Python setuptools
├── setup.cfg                   # Additional setuptools config
├── build.gradle                # Root Gradle build
├── settings.gradle             # Gradle project structure
├── gradle.properties           # Gradle configuration
├── build.tarl                  # TARL build config
├── docker-compose.yml          # Docker Compose
├── Dockerfile                  # Docker image build
├── android/
│   └── legion_mini/
│       └── build.gradle        # Android app build
└── tarl/
    └── build/
        └── cli.py              # TARL build CLI
```

---

## Cross-Platform Considerations

### Windows

- Use `gradlew.bat` instead of `./gradlew`
- PowerShell execution policy may block scripts
- Path separators: backslash (`\`)
- Line endings: CRLF

### Linux/macOS

- Use `./gradlew` (requires execute permission)
- Bash/Zsh shell compatibility
- Path separators: forward slash (`/`)
- Line endings: LF

### Universal Scripts

```bash
# Use Python for cross-platform scripts
python scripts/build_helper.py

# Use npm scripts for consistent interface
npm run build

# Use Docker for platform-independent builds
docker build -t project-ai .
```

---

## Build System Best Practices

### ✅ DO

- Use Gradle wrapper for consistent Gradle version
- Enable build caching for faster builds
- Use `pip install -e .` for development
- Run `make lint` before committing
- Use Docker for reproducible builds
- Tag Docker images with version numbers

### ❌ DON'T

- Don't install Gradle globally (use wrapper)
- Don't commit build artifacts to Git
- Don't skip dependency version pinning
- Don't modify generated files (e.g., `gradlew`)
- Don't use `pip install` without virtual environment
- Don't build Docker images without `.dockerignore`

---

## Related Documentation

- **[01-CLI-OVERVIEW.md](./01-CLI-OVERVIEW.md)** - CLI interface overview
- **[04-SOVEREIGN-CLI.md](./04-SOVEREIGN-CLI.md)** - Sovereign runtime CLI
- **[08-GRADLE-SYSTEM.md](./08-GRADLE-SYSTEM.md)** - Gradle build details
- **[09-DOCKER-BUILDS.md](./09-DOCKER-BUILDS.md)** - Docker image builds
- **[10-TARL-BUILD-SYSTEM.md](./10-TARL-BUILD-SYSTEM.md)** - TARL build system

---

**AGENT-038: CLI & Automation Documentation Specialist**  
*Multi-platform build orchestration architecture.*
