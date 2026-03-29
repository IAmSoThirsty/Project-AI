<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->

<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `scripts/` — Operational Scripts

> **Every script in one place.** Build, deploy, validate, audit, train, benchmark — if it runs from the command line, it lives here.

## Categories

### 🔨 Build & Release

| Script | Purpose |
|---|---|
| `build_production.ps1` | Full production build pipeline |
| `build_release.sh` / `.bat` | Platform-specific release builds |
| `build_standalone.py` | Standalone executable builder |
| `build_sovereign_agent.py` | Build the sovereign agent package |
| `build_training_data.py` | Generate training datasets |
| `freeze_seal.py` | Freeze and cryptographically seal a build |

### 🚀 Deployment

| Script | Purpose |
|---|---|
| `deploy_complete.ps1` | Full deployment pipeline |
| `deploy_sovereign.sh` | Linux sovereign deployment |
| `deploy_shortcut.ps1` | Desktop shortcut deployment |
| `deploy-monitoring.sh` | Monitoring stack deployment |
| `hydra50_deploy.py` | Hydra-50 engine deployment |
| `create_installation_usb.ps1` | USB installer creation |
| `create_portable_usb.ps1` | Portable USB deployment |
| `create_universal_usb.ps1` | Universal USB installer |
| `install_desktop.ps1` | Desktop installation |
| `install-shortcuts.py` | Shortcut installer |

### 🛡️ Security & Validation

| Script | Purpose |
|---|---|
| `validate_all_code.py` | Full codebase validation |
| `validate_production_claims.py` | Verify production readiness claims |
| `validate_release.py` | Release validation checks |
| `verify_job_board.py` | Job board integrity verification |
| `verify-supply-chain.sh` | Supply chain verification |
| `audit_sovereign.py` | Sovereign architecture audit |
| `backup_audit.py` | Audit backup verification |
| `sarif_exporter.py` | SARIF security report exporter |
| `run_security_validation_tests.sh` | Security test suite |
| `run_security_worker.py` | Security worker process |
| `run_asl_assessment.py` | ASL safety assessment |
| `run_asl3_security.py` | ASL-3 security validation |

### 🧠 AI & Training

| Script | Purpose |
|---|---|
| `train_sovereign.py` | Model training pipeline |
| `merge_and_quantize.py` | Model merge and quantization |
| `generate_modelfile.py` | Ollama modelfile generation |
| `deepseek_v32_cli.py` | DeepSeek V32 CLI interface |
| `populate_cybersecurity_knowledge.py` | Cybersecurity knowledge base |
| `run_cbrn_classifier.py` | CBRN threat classifier |
| `run_novel_scenarios.py` | Novel scenario generator |
| `run_red_hat_expert_simulations.py` | Red Hat expert simulations |
| `run_red_team_stress_tests.py` | Red team stress testing |
| `run_robustness_benchmarks.py` | Robustness benchmarking |

### 🔧 Utilities & Maintenance

| Script | Purpose |
|---|---|
| `start_api.py` | Start the Legion API server |
| `quickstart.py` | Quick start guide runner |
| `bootstrap.py` | Bootstrap environment setup |
| `healthcheck.py` | System health check |
| `cleanup_root.ps1` | Root directory cleanup |
| `setup_temporal.py` | Temporal service setup |
| `sync_sovereign_workspace.py` | Workspace sync |
| `update_doc_headers.py` | Batch update document headers |
| `update_standard_status.py` | Update status across files |
| `fix_syntax_errors.py` | Auto-fix syntax errors |
| `fix_logging_performance.py` | Logging performance optimization |
| `fix_assert_statements.py` | Assert statement cleanup |

### 📊 Demos & Showcases

| Script | Purpose |
|---|---|
| `demo_cybersecurity_knowledge.py` | Cybersecurity knowledge demo |
| `demo_security_features.py` | Security features showcase |
| `redteam_workflow.py` | Red team workflow demonstration |

### 🧬 Code Generation

| Script | Purpose |
|---|---|
| `generate_cerberus_languages.py` | Generate Cerberus language bindings |
| `generate_cli_docs.py` | Auto-generate CLI documentation |
| `apply_safe_framing.py` | Apply safe framing to codebase |
| `run_comprehensive_expansion.py` | Comprehensive feature expansion |

## Usage

```powershell
# Start the API server
python scripts/start_api.py

# Run production build
powershell scripts/build_production.ps1

# Validate the codebase
python scripts/validate_all_code.py

# Health check
python scripts/healthcheck.py
```
