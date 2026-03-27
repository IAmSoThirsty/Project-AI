<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / DEVELOPER_QUICK_REFERENCE.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / DEVELOPER_QUICK_REFERENCE.md # -->
<!-- # ============================================================================ #

<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
# Developer Quick Reference

Essential commands for development

Environment

- Create `.env` in repository root with required keys (do NOT commit):
  - `OPENAI_API_KEY`
  - `HUGGINGFACE_API_KEY`
  - `FERNET_KEY`

Run

- Desktop UI: `python -m src.app.main`
- Tests: `pytest -v`

Linting & Formatting

- `ruff check .` and `ruff check . --fix`
- `isort src tests --profile black`
- `black src tests`
- `pre-commit` hooks configured in `.pre-commit-config.yaml`

CI & Validation

- GitHub Actions will run lint, tests, Codacy analysis and a Docker smoke test on PRs.
- **Architect Audit**: `python tools/architect_agent.py`
- **Logic Proof**: `python sovereign_runtime_proof.py`

Secrets

- Do not store secrets in repo. Use GitHub Secrets for CI and a secure secret store for deployments.

Troubleshooting

- If persistence fails on a fresh clone, ensure `data/` exists or the application will create it at runtime.
