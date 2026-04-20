# Project Guidelines

## Build and Test
- Prefer this command order for validation after edits: `python -m taar.cli run` (or `make taar` / `npm run taar`) -> targeted language checks -> `./gradlew check` for full-repo verification.
- When Python code changes, run: `ruff check .`, `mypy src`, `pytest -q` (or `pytest -v` when debugging), and `bandit -r src/` plus `pip-audit` for security checks.
- When JavaScript or Electron code changes, run: `npm run lint` and `npm run test`.
- When Markdown changes, run: `npm run lint:markdown`.
- Prefer existing task wrappers over ad-hoc scripts: `Makefile`, `package.json`, and Gradle tasks in `build.gradle.kts`.

## Architecture
- Treat this repository as a polyglot monorepo with clear boundaries.
- Core application logic lives under `src/app/core`.
- Language/runtime implementation lives under `src/thirsty_lang`.
- Security-sensitive paths live under `src/security` and `security/`.
- Governance and policy/runtime orchestration live under `governance/`.
- Use these maps before large edits: `COMPONENT_MAP.md` and `DIRECTORY_INDEX.md`.

## Conventions
- Do not overstate security outcomes. Follow claim language and evidence requirements in `.github/SECURITY_VALIDATION_POLICY.md`.
- Prefer small, focused changes and avoid broad refactors unless explicitly requested.
- Keep generated/disposable artifacts out of committed changes (`workspace/`, `output/`, `tmp/`, `.venv-linux/`, `.env.wsl`).
- Respect formatting and lint toolchain already used by the repo (`black`, `ruff`, `isort`, pre-commit hooks).
- If command behavior conflicts across docs, prefer the stricter/newer constraint from config files (`package.json`, `pyproject.toml`, `build.gradle.kts`) and note the mismatch in your summary.

## Documentation Links
- Start here for onboarding and workflows: `README.md`, `WORKSPACE_SETUP.md`, `DEVELOPER_QUICK_REFERENCE.md`, `CONTRIBUTING.md`.
- Use documentation indexes rather than duplicating long guidance: `docs/README.md`, `docs/TECHNICAL_DOCUMENTATION_INDEX.md`, `docs/TECHNICAL_SPECS_INDEX.md`.
- For automation and governance policy details, link to `.github/README.md` and `.github/copilot_workspace_profile.md`.