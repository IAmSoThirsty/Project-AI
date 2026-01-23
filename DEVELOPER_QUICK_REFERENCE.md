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

CI

- GitHub Actions will run lint, tests, Codacy analysis and a Docker smoke test on PRs.

Secrets

- Do not store secrets in repo. Use GitHub Secrets for CI and a secure secret store for deployments.

Troubleshooting

- If persistence fails on a fresh clone, ensure `data/` exists or the application will create it at runtime.
