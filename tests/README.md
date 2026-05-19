<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `tests/` — Test Suite

> **232 test files. 18 test categories. Everything from unit tests to adversarial red-team stress tests.**

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific category
pytest tests/security/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest tests/ --cov=project_ai --cov-report=html

# Run PowerShell E2E suite
powershell scripts/run_e2e_tests.ps1
```

## Test Categories

### Infrastructure

| Directory | Tests | Focus |
|---|---:|---|
| `e2e/` | 6 | End-to-end integration flows |
| `integration/` | 2 | Cross-module integration |
| `kernel/` | 3 | Kernel subsystem verification |
| `agents/` | 2 | Agent coordinator tests |
| `plugins/` | 2 | Plugin system tests |
| `utils/` | 2 | Utility function tests |

### Security & Adversarial

| Directory | Tests | Focus |
|---|---:|---|
| `security/` | 1 | Core security tests |
| `chaos/` | 1 | Chaos engineering / fault injection |
| `attack_vectors/` | — | Attack vector definitions |
| `inspection/` | 3 | Code inspection / static analysis |

### Monitoring & Performance

| Directory | Tests | Focus |
|---|---:|---|
| `monitoring/` | 1 | Monitoring stack tests |
| `load/` | — | Load testing configurations |
| `manual/` | 3 | Manual verification scripts |

### Specialized

| Directory | Tests | Focus |
|---|---:|---|
| `gradle_evolution/` | 9 | Gradle bridge verification |
| `temporal/` | 5 | Temporal workflow tests |
| `gui_e2e/` | 1 | GUI end-to-end tests |

## Key Test Files (Root Level)

### Constitutional & Governance

| Test File | What It Validates |
|---|---|
| `test_four_laws_*.py` (8 files) | FourLaws invariant enforcement |
| `test_humanity_first_invariants.py` | Humanity-first policy |
| `test_governance_manager.py` | Governance system |
| `test_policy_guard.py` | Policy guard mechanisms |
| `test_invariants.py` | System invariants |
| `test_iron_path.py` | Iron Path execution |
| `test_irreversibility_locks.py` | Irreversibility guarantees |

### Security

| Test File | What It Validates |
|---|---|
| `test_cerberus_*.py` (2 files) | Cerberus security perimeter |
| `test_god_tier_*.py` (4 files) | God-tier security systems |
| `test_attack_simulation_suite.py` | Simulated attack scenarios |
| `test_red_team_stress_tests.py` | Red team operations |
| `test_adversarial_emotional_manipulation.py` | Social engineering defense |
| `test_anti_sovereign_stress_tests.py` | Sovereignty violation tests |
| `test_ed25519_crypto.py` | Cryptographic verification |
| `test_asymmetric_security.py` | Asymmetric security model |

### Core Systems

| Test File | What It Validates |
|---|---|
| `test_shadow_thirst.py` | Shadow Thirst VM |
| `test_shadow_execution.py` | Shadow plane execution |
| `test_shadow_operational_semantics.py` | Shadow VM semantics |
| `test_tarl_*.py` (6 files) | T.A.R.L. orchestration |
| `test_psia_*.py` (11 files) | PSIA framework |
| `test_cognition_kernel.py` | Cognition kernel |
| `test_sovereign_*.py` (5 files) | Sovereign runtime |

### Integration & API

| Test File | What It Validates |
|---|---|
| `test_api.py` | API endpoints |
| `test_cli.py` / `test_cli_commands.py` | CLI interface |
| `test_mcp_server.py` | MCP server |
| `test_web_backend.py` / `test_web_frontend.py` | Web stack |
| `test_deepseek_*.py` (2 files) | DeepSeek integration |
| `test_codex_*.py` (2 files) | Codex integration |

## Conventions

- **Naming**: `test_<module>_<aspect>.py`
- **Framework**: `pytest` with `conftest.py` for shared fixtures
- **Coverage target**: Full statement + branch coverage
- **Stress tests**: Suffixed with `_stress` or `_1000`
- **Uniqueness**: `check_uniqueness.py` and `verify_test_uniqueness.py` ensure no duplicate test IDs
