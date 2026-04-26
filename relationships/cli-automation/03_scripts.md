---
title: Scripts Relationships
description: Script dependencies, automation chains, and execution flows
tags:
  - relationships
  - scripts
  - automation
  - dependencies
created: 2025-02-08
agent: AGENT-063
---

# Scripts Relationships

## Overview

Project-AI contains **93 automation scripts** across multiple languages (PowerShell, Shell, Python, Batch) organized into functional categories.

## 📁 Script Organization

### Directory Structure
```
scripts/
├── automation/          # Metadata & batch processing (11 files)
├── deploy/              # Deployment scripts
├── hooks/               # Git hooks (1 file)
├── install/             # Installation scripts (2 files)
├── verify/              # Verification scripts (2 files)
└── [root scripts]       # Core automation (50+ files)
```

### Script Inventory by Type
- **PowerShell (.ps1)**: 19 scripts
- **Shell (.sh)**: 6 scripts
- **Python (.py)**: 50 scripts
- **Batch (.bat)**: 4 scripts
- **YAML (.yml)**: 1 script
- **Markdown (.md)**: 10 documentation files
- **JSON (.json)**: 1 configuration file

---

## 🎯 Critical Script Categories

### 1. Launcher Scripts

#### `launch-desktop.ps1`
**Purpose**: Launch desktop application (Windows)

**Dependencies**:
- Python 3.11+
- PyQt6
- src/app/main.py

**Execution Flow**:
```powershell
1. Set environment variables
2. Check Python installation
3. Activate virtual environment (if exists)
4. Execute: python -m src.app.main
5. Monitor process
```

**Triggers**:
- Manual: `.\scripts\launch-desktop.ps1`
- Shortcut: Desktop launcher icon

**Output**: Desktop application window

**Relationships**:
- **Calls**: Python CLI entry point
- **Depends**: Virtual environment setup
- **Enables**: Desktop application launch

---

#### `launch-desktop.bat`
**Purpose**: Simple Windows launcher

**Execution Flow**:
```batch
@echo off
python -m src.app.main
pause
```

**Triggers**: Double-click or command line

**Relationships**:
- **Alternative**: PowerShell launcher
- **Calls**: Same Python entry point

---

### 2. Installation Scripts

#### `install/install_desktop.ps1`
**Purpose**: Desktop environment installation

**Dependencies**:
- Python 3.11+
- pip
- requirements.txt

**Execution Flow**:
```powershell
1. Verify Python version
2. Create virtual environment (.venv)
3. Activate venv
4. Upgrade pip
5. Install requirements
6. Verify PyQt6 installation
7. Create desktop shortcuts
```

**Triggers**: Initial setup

**Output**:
- Virtual environment
- Installed dependencies
- Desktop shortcuts

**Relationships**:
- **Creates**: `.venv/`
- **Installs**: dependencies from `requirements.txt`
- **Enables**: `launch-desktop.ps1`

---

#### `install/install_jdk21_clean.ps1`
**Purpose**: Clean JDK 21 installation for Gradle

**Dependencies**:
- Windows
- Internet connection (for download)

**Execution Flow**:
```powershell
1. Remove existing JDK installations
2. Download JDK 21
3. Install to standard location
4. Set JAVA_HOME
5. Update PATH
6. Verify installation
```

**Triggers**: Gradle build setup

**Output**: JDK 21 installed and configured

**Relationships**:
- **Enables**: Gradle builds
- **Sets**: JAVA_HOME environment variable
- **Alternative**: `install_java_for_gradle.ps1`

---

### 3. Build Scripts

#### `build_production.ps1`
**Purpose**: Multi-platform production builds

**Parameters**:
- `-Desktop`: Build desktop app
- `-Android`: Build Android APK
- `-Portable`: Create portable package
- `-All`: Build all platforms

**Execution Flow**:
```powershell
1. Set JAVA_HOME for Gradle
2. Build Android APK (if requested)
   ├─ gradlew :legion_mini:assembleDebug
   └─ gradlew :legion_mini:assembleRelease
3. Build Desktop app (if requested)
   ├─ npm install (desktop/)
   ├─ npm run build
   └─ Create distribution
4. Create portable package (if requested)
   ├─ Package scripts
   ├─ Include launchers
   └─ Create archive
```

**Dependencies**:
- Gradle + JDK 17
- Node.js + npm
- Python 3.11+

**Output**:
- Android APKs
- Desktop executables
- Portable archives

**Relationships**:
- **Calls**: Gradle, npm, Python
- **Generates**: Build artifacts
- **Triggers**: GitHub Actions workflows

---

#### `build_release.sh` / `build_release.bat`
**Purpose**: Cross-platform release builds

**Execution Flow**:
```bash
#!/bin/bash
1. Clean previous builds
2. Run tests
3. Build Docker image
4. Tag with version
5. Push to registry (optional)
```

**Dependencies**:
- Docker
- pytest
- Build tools

**Relationships**:
- **Calls**: Docker build
- **Verifies**: Tests pass
- **Alternative**: `build_release.bat` (Windows)

---

### 4. Deployment Scripts

#### `deploy/deploy_complete.ps1`
**Purpose**: Complete deployment pipeline

**Execution Flow**:
```powershell
1. Run pre-deployment checks
2. Build production artifacts
3. Deploy to target environment
4. Run post-deployment validation
5. Monitor deployment health
```

**Dependencies**:
- Build scripts
- Deployment targets configured
- Monitoring tools

**Relationships**:
- **Calls**: `build_production.ps1`
- **Triggers**: Post-deploy hooks
- **Monitors**: Deployment health

---

#### `deploy-monitoring.sh`
**Purpose**: Deploy monitoring stack (Prometheus, Grafana)

**Execution Flow**:
```bash
1. Deploy Prometheus
   ├─ Apply config from config/prometheus/
   └─ Start Prometheus server
2. Deploy Grafana
   ├─ Apply dashboards from config/grafana/
   └─ Configure datasources
3. Deploy Alertmanager
   └─ Apply config from config/alertmanager/
4. Verify deployment
```

**Dependencies**:
- Helm (Kubernetes)
- Docker Compose (standalone)
- Monitoring configurations

**Output**: Monitoring stack deployed

**Relationships**:
- **Uses**: `helm/project-ai-monitoring/`
- **Configures**: Prometheus, Grafana, Alertmanager
- **Enables**: System monitoring

---

### 5. Automation Scripts (`scripts/automation/`)

#### `add-metadata.ps1`
**Purpose**: Generate YAML frontmatter for documentation

**Parameters**:
- `-Path`: File or directory to process
- `-DryRun`: Preview without changes
- `-Force`: Overwrite existing frontmatter
- `-TaxonomyPath`: Custom taxonomy file
- `-Interactive`: Prompt for confirmation

**Execution Flow**:
```powershell
1. Load taxonomy (if provided)
2. Scan files in path
3. For each file:
   a. Analyze content
   b. Generate metadata
   c. Create YAML frontmatter
   d. Insert at file start (or update)
4. Log results
```

**Dependencies**:
- PowerShell 5.1+
- YAML parser (optional)

**Output**: Files with YAML frontmatter

**Relationships**:
- **Used by**: GitHub Actions metadata workflow
- **Processes**: Markdown files
- **Logs**: `automation-logs/add-metadata.log`

---

#### `process-archive-metadata.ps1`
**Purpose**: Process P3 archive metadata in bulk

**Execution Flow**:
```powershell
1. Load config from archive-metadata-config.json
2. Scan archive directory
3. For each file:
   a. Extract metadata
   b. Enrich with taxonomy
   c. Validate against schema
   d. Update metadata
4. Generate reports
```

**Dependencies**:
- `archive-metadata-config.json`
- PowerShell 7+

**Output**: Enriched archive files

**Relationships**:
- **Calls**: `Enrich-P3ArchiveMetadata.ps1`
- **Uses**: `archive-metadata-config.json`
- **Generates**: Automation reports

---

#### `batch-process.ps1`
**Purpose**: Batch processing automation

**Parameters**: Configurable via JSON

**Execution Flow**:
```powershell
1. Load batch configuration
2. Process items in parallel
3. Handle errors gracefully
4. Generate summary report
```

**Relationships**:
- **Generic**: Reusable for multiple tasks
- **Configurable**: Via JSON config files

---

#### `validate-tags.ps1`
**Purpose**: Validate YAML frontmatter tags against taxonomy

**Execution Flow**:
```powershell
1. Load taxonomy definition
2. Scan files for YAML frontmatter
3. Extract tags from each file
4. Validate against taxonomy
5. Report violations
```

**Output**: Validation report

**Relationships**:
- **Enforces**: Tag taxonomy
- **Used by**: CI validation workflows
- **Depends**: `sample-taxonomy.yml`

---

### 6. Verification Scripts (`scripts/verify/`)

#### `verify_gradle_setup.ps1`
**Purpose**: Verify Gradle and Java configuration

**Execution Flow**:
```powershell
1. Check JAVA_HOME
2. Verify Java version
3. Test Gradle wrapper
4. Run Gradle tasks list
5. Report configuration status
```

**Dependencies**:
- JDK 17+
- Gradle wrapper

**Output**: Configuration verification report

**Relationships**:
- **Verifies**: Build environment
- **Prerequisite**: Build scripts

---

#### `verify-platforms.sh`
**Purpose**: Verify multi-platform build capabilities

**Execution Flow**:
```bash
1. Check Docker availability
2. Verify Node.js version
3. Check Python version
4. Test Gradle build
5. Verify Android SDK (if needed)
```

**Output**: Platform capability report

**Relationships**:
- **Prerequisite**: Multi-platform builds
- **Verifies**: All build dependencies

---

### 7. Git Hooks (`scripts/hooks/`)

#### `pre-commit-root-structure.sh`
**Purpose**: Enforce root directory structure

**Execution Flow**:
```bash
#!/bin/bash
1. Get list of staged files
2. Check for root-level file additions
3. Validate against allowed structure
4. Reject commit if violations found
```

**Triggers**: Git pre-commit event

**Output**: Pass/fail commit validation

**Relationships**:
- **Enforced by**: `.pre-commit-config.yaml`
- **Prevents**: Root directory pollution
- **Triggers**: GitHub Actions workflow

---

### 8. Testing & Security Scripts

#### `run_e2e_tests.ps1`
**Purpose**: Execute end-to-end test suite

**Execution Flow**:
```powershell
1. Start test environment (Docker)
2. Wait for services to be ready
3. Run e2e test suite
4. Collect test results
5. Generate coverage report
6. Cleanup test environment
```

**Dependencies**:
- Docker Compose
- pytest
- E2E test suite

**Output**: Test results and coverage

**Relationships**:
- **Uses**: `docker-compose.yml`
- **Generates**: `test-artifacts/`
- **Called by**: CI workflows

---

#### `run_security_worker.py`
**Purpose**: Execute security scans

**Execution Flow**:
```python
1. Load security scan configuration
2. Run vulnerability scans:
   ├─ Bandit (Python)
   ├─ pip-audit (dependencies)
   └─ Custom security checks
3. Generate SARIF reports
4. Upload to GitHub Security tab
```

**Dependencies**:
- bandit
- pip-audit
- SARIF exporter

**Output**: SARIF reports

**Relationships**:
- **Called by**: GitHub Actions security workflows
- **Generates**: `security/` reports
- **Integrates**: GitHub Advanced Security

---

### 9. Utility Scripts

#### `cleanup_root.ps1`
**Purpose**: Clean root directory clutter

**Execution Flow**:
```powershell
1. Identify temporary files
2. Remove build artifacts
3. Clean cache directories
4. Preserve important files
5. Log cleanup actions
```

**Output**: Clean root directory

**Relationships**:
- **Called by**: Weekly maintenance workflow
- **Preserves**: Data, configs, source

---

#### `create_universal_usb.ps1`
**Purpose**: Create universal USB installer

**Execution Flow**:
```powershell
1. Format USB drive
2. Copy portable binaries
3. Include launchers for all platforms
4. Add documentation
5. Create autorun files
```

**Dependencies**:
- `create_portable_usb.ps1`
- `create_installation_usb.ps1`

**Output**: Universal USB installer

**Relationships**:
- **Combines**: Portable + installation modes
- **Calls**: Sub-scripts for each mode

---

## 🔄 Script Dependency Chains

### Build Chain
```
build_production.ps1
    ├─> install/install_jdk21_clean.ps1 (prerequisite)
    ├─> gradlew :legion_mini:assembleRelease
    ├─> npm install (desktop)
    └─> npm run build
```

### Deployment Chain
```
deploy/deploy_complete.ps1
    ├─> build_production.ps1 -All
    ├─> deploy-monitoring.sh
    └─> Post-deploy validation scripts
```

### Metadata Processing Chain
```
automation/process-archive-metadata.ps1
    ├─> Enrich-P3ArchiveMetadata.ps1
    ├─> automation/add-metadata.ps1
    └─> automation/validate-tags.ps1
```

### Testing Chain
```
run_e2e_tests.ps1
    ├─> Docker Compose up
    ├─> pytest (E2E suite)
    ├─> Coverage generation
    └─> Docker Compose down
```

---

## 📊 Script Execution Matrix

| Script | Trigger | Frequency | Dependencies | Output |
|--------|---------|-----------|--------------|--------|
| launch-desktop.ps1 | Manual | On-demand | Python, PyQt6 | Desktop app |
| build_production.ps1 | Manual/CI | Per release | Gradle, npm | Build artifacts |
| deploy_complete.ps1 | Manual | Per deployment | Build scripts | Deployed system |
| add-metadata.ps1 | Manual/CI | Per commit | PowerShell | Enriched docs |
| run_e2e_tests.ps1 | CI | Per PR | Docker | Test results |
| verify_gradle_setup.ps1 | Setup | Once | JDK, Gradle | Verification report |

---

## 🔗 Integration Points

### Scripts → CLI
- `launch-desktop.ps1` → `python -m src.app.main`
- `deepseek_v32_cli.py` → Model inference
- `inspection_cli.py` → Repository audit

### Scripts → GitHub Actions
- `build_release.sh` → Build workflow
- `run_security_worker.py` → Security scan workflow
- `deploy-monitoring.sh` → Deployment workflow

### Scripts → Build Tools
- `build_production.ps1` → Gradle + npm
- `verify_gradle_setup.ps1` → Gradle verification
- `build_release.sh` → Docker build

### Scripts → Configuration
- `add-metadata.ps1` → `sample-taxonomy.yml`
- `process-archive-metadata.ps1` → `archive-metadata-config.json`
- `deploy-monitoring.sh` → `helm/project-ai-monitoring/`

---

## 🛡️ Security & Validation

### Input Validation
- All PowerShell scripts use `[CmdletBinding(SupportsShouldProcess)]`
- Path validation before file operations
- Parameter type enforcement

### Error Handling
- Try-catch blocks in critical sections
- Logging to `automation-logs/`
- Exit codes: 0 (success), 1 (error)

### Execution Safety
- DryRun modes for destructive operations
- Interactive confirmations (optional)
- Rollback capabilities

---

## 📈 Script Performance

### Execution Times (Typical)
- **launch-desktop.ps1**: < 5 seconds
- **build_production.ps1 -All**: 5-10 minutes
- **deploy_complete.ps1**: 10-20 minutes
- **add-metadata.ps1 (batch)**: 1-5 minutes
- **run_e2e_tests.ps1**: 5-15 minutes

### Optimization Patterns
- Parallel processing where possible
- Caching (build artifacts, dependencies)
- Incremental builds
- Conditional execution (path-based)

---

## 🔍 Related Documentation

- **CLI Interface**: See `01_cli-interface.md`
- **Automation Workflows**: See `04_automation-workflows.md`
- **Build Tools**: See `05_build-tools.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
