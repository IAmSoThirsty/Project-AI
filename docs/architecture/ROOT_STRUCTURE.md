# Project-AI Root Directory Structure

After running `scripts/cleanup_root.ps1`, the root directory is organized as follows:

## Essential Files (Remain in Root)

### Core Documentation

- `README.md` - Project overview
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Community standards
- `CODEOWNERS` - Code ownership
- `LICENSE` / `LICENSE.txt` - Software license
- `QUICK_START.md` - Quick start guide
- `DEVELOPER_QUICK_REFERENCE.md` - Developer quick ref

### Build & Configuration

- `Dockerfile` - Docker containerization
- `docker-compose.yml` / `docker-compose.override.yml` - Docker compose
- `Makefile` - Build automation
- `build.gradle` / `settings.gradle` / `gradle.properties` - Gradle config
- `gradlew` / `gradlew.bat` - Gradle wrapper
- `setup.py` / `setup.cfg` / `pyproject.toml` - Python packaging
- `package.json` / `package-lock.json` - Node.js dependencies
- `requirements.txt` / `requirements-dev.txt` - Python dependencies
- `pytest.ini` - Test configuration
- `MANIFEST.in` - Package manifest

### Environment & Config

- `.gitignore` / `.gitattributes` / `.gitmodules` - Git config
- `.dockerignore` - Docker ignore rules
- `.python-version` - Python version
- `.pre-commit-config.yaml` - Pre-commit hooks
- `mcp.json` - MCP configuration
- `app-config.json` - App configuration
- `users.json` - User data

### Entry Points

- `bootstrap.py` - Bootstrap script
- `quickstart.py` - Quick start script
- `start_api.py` - API start script
- `test_*.py` - Root-level test files

---

## Organized Subdirectories

### `docs/archive/`

Historical implementation documentation, summaries, and completed feature docs:

- All `*_COMPLETE.md` files
- All `*_SUMMARY.md` files  
- All `*_IMPLEMENTATION*.md` files
- All `*_STATUS.md`, `*_ANALYSIS.md`, `*_FINDINGS.md` files
- Legacy documentation snapshots

### `docs/architecture/`

System architecture and design documentation:

- `AGENT_MODEL.md` - Agent architecture
- `CAPABILITY_MODEL.md` - Capability system
- `ENGINE_SPEC.md` - Engine specifications
- `IDENTITY_ENGINE.md` - Identity system
- `INTEGRATION_LAYER.md` - Integration architecture
- `MODULE_CONTRACTS.md` - Module interfaces
- `STATE_MODEL.md` - State management
- `WORKFLOW_ENGINE.md` - Workflow system
- `TARL_ARCHITECTURE.md` - TARL design
- `GOD_TIER_*.md` - God-tier architecture docs
- `PLATFORM_COMPATIBILITY.md` - Platform compatibility

### `docs/security/`

Security documentation and threat models:

- `CERBERUS_*.md` - Cerberus security system
- `SECURITY.md` - Security policy
- `SECURE-*.md` - Security guides
- `threat-model.md` - Threat modeling

### `docs/tarl/`

TARL (Triumvirate Autonomous Reasoning Layer) reference:

- `TARL_README.md` - TARL overview
- `TARL_CODE_EXAMPLES.md` - Code examples
- `TARL_TECHNICAL_DOCUMENTATION.md` - Technical docs
- `TARL_USAGE_SCENARIOS.md` - Usage scenarios
- `TARL_QUICK_REFERENCE.md` - Quick reference
- `TARL_PRODUCTIVITY_QUICK_REF.md` - Productivity tips

### `docs/deployment/`

Deployment guides and build documentation:

- `BUILD_AND_DEPLOYMENT.md` - Build & deployment guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `DEPLOYMENT_RELEASE_QUICKSTART.md` - Quick start
- `DEPLOY_CHECKLIST.md` - Deployment checklist
- `GRADLE_JAVASCRIPT_SETUP.md` - Gradle setup
- `RELEASE_BUILD_GUIDE.md` - Release build guide
- `RELEASE_NOTES_*.md` - Release notes

### `docs/api/`

API documentation and integration:

- `CONSTITUTION.md` - API constitution
- `INTEGRATION_PLAN.md` - Integration planning
- `CLI-CODEX.md` - CLI documentation
- `TRIUMVIRATE_*.md` - Triumvirate docs

### `docs/whitepapers/`

Technical whitepapers and research:

- `TECHNICAL_WHITE_PAPER.md` - Main whitepaper
- `TECHNICAL_WHITE_PAPER_SUMMARY.md` - Whitepaper summary
- `WHITEPAPER_SUMMARY.md` - Overview

### `config/examples/`

Example configuration files:

- `.env.example` - Environment example
- `.env.temporal.example` - Temporal config example
- `.pre-commit-config.yaml.example` - Pre-commit example
- `.projectai.toml.example` - Project AI config example

### `config/editor/`

Editor and linter configurations:

- `.editorconfig` - Editor configuration
- `.flake8` - Flake8 linter config
- `.markdownlint.json` - Markdown linter config
- `pyrightconfig.json` - Pyright type checker config

### `scripts/demo/`

Demonstration scripts:

- `demo_*.py` - All demo scripts

### `scripts/verify/`

Verification and testing scripts:

- `verify_*.py` - Verification scripts
- `verify-*.sh` - Shell verification scripts
- `verify_gradle_setup.ps1` - Gradle verification

### `scripts/install/`

Installation scripts:

- `install_*.ps1` - PowerShell installers

### `scripts/build/`

Build automation scripts:

- `build-all-platforms.*` - Cross-platform builds
- `extract_with_permissions.py` - Extraction utility

### `scripts/deploy/`

Deployment automation:

- `deploy_to_thirstysprojects.bat` - Deployment script

### `test-data/`

Test data, scenarios, and results:

- `adversarial_stress_tests_2000.json` - Stress test data
- `owasp_compliant_tests.json` - OWASP test data
- `white_hatter_scenarios.json` - Security scenarios
- `test_results.txt` - Test results

### `test-data/audit/`

Audit and compliance reports:

- `pip-audit-current.json` - Dependency audit
- `audit.log` - Audit log

---

## Benefits

✅ **Clean Root** - Only essential project files visible
✅ **Logical Organization** - Related docs grouped together
✅ **Easy Navigation** - Find documentation quickly
✅ **Better Git** - Cleaner diffs and history
✅ **Professional** - Industry-standard structure

---

## Running the Cleanup

```powershell
# Preview changes (dry run)
.\scripts\cleanup_root.ps1 -DryRun

# Apply cleanup
.\scripts\cleanup_root.ps1
```

The script automatically:

- Creates organized directory structure
- Moves files to appropriate locations
- Preserves essential root files
- Prevents duplicate moves
