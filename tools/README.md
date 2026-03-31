<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `tools/` — Developer & Maintenance Tools

> **CLI utilities, code quality tools, and maintenance scripts for Project-AI developers.**

## Tools

### Code Quality

| Tool | Purpose |
|---|---|
| `fix_whitespace.py` | Fix trailing whitespace and line endings |
| `reflow_markdown.py` | Reformat markdown files to consistent style |
| `import_test.py` | Verify all imports resolve correctly |
| `check_large_files_for_lfs.py` | Detect files that should be tracked by Git LFS |

### Security Scanning

| Tool | Purpose |
|---|---|
| `secret_scan.py` | Scan for hardcoded secrets, API keys, tokens |
| `enhanced_secret_scan.py` | Enhanced secret scanner with pattern matching |
| `run_security_audit.sh` | Full security audit pipeline |
| `purge_git_secrets.ps1` / `.sh` | Purge secrets from git history |
| `SECURITY_SCANNING.md` | Security scanning documentation |

### FourLaws Reporting

| Tool | Purpose |
|---|---|
| `merge_fourlaws_artifacts.py` | Merge FourLaws test artifacts into report |
| `regenerate_fourlaws_report.ps1` | Regenerate the FourLaws compliance report |
| `regenerate_and_commit_fourlaws_report.ps1` | Regenerate + auto-commit |

### Testing & Benchmarking

| Tool | Purpose |
|---|---|
| `count_parametrize_cases.py` | Count parametrized test cases |
| `simulate_defensive_tests.py` | Simulate defensive test scenarios |
| `benchmark-optimized.js` | JavaScript performance benchmark |
| `prune_test_artifacts.py` | Clean up stale test artifacts |

### Dev Environment

| Tool | Purpose |
|---|---|
| `setup_designer_env.ps1` / `.bat` | Set up the designer development environment |
| `install_dev_tools.sh` | Install development dependencies |
| `launch-dev-ui.bat` | Launch the development UI |
