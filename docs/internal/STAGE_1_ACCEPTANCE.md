# Stage 1 - Repository Skeleton Acceptance

**Status:** COMPLETE
**Verified:** 2026-06-20

## Evidence

The existing Stage 0-labeled commits jointly contain the planned Stage 1
skeleton. History is preserved as written; this record supplies the missing
stage mapping.

Required root files present:

- `.dockerignore`
- `.editorconfig`
- `.gitattributes`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.python-version`
- `.github/CODEOWNERS`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `README.md`
- `SECURITY.md`

## Acceptance

- [x] `LICENSE` contains the MIT License.
- [x] `.venv/` is ignored by `.gitignore`.
- [x] Line-ending policy is committed in `.gitattributes` and `.editorconfig`.
- [x] Secret, merge-conflict, TOML, YAML, lint, type, and branch checks are declared in pre-commit configuration.
- [x] No existing commit was relabeled or rewritten.
