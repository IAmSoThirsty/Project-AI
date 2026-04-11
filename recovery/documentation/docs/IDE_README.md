# IDE Readme

This repository treats the source tree as canonical. IDE and workspace helpers
are auxiliary and should not replace the tracked operational substrate.

Canonical surfaces:

- `src/`
- `web/`
- `desktop/`
- `engines/`
- `octoreflex/`
- `tarl_os/`
- `scripts/`
- `docs/`
- `tests/`
- `canonical/`
- `validation_evidence/`

Auxiliary surfaces:

- `.agent/`
- `.agents/`
- `.antigravity/`
- `.codacy/`
- `.devcontainer/`
- `Claude/`
- `Codex/`
- `workspace/`

Recovery rules:

- Do not commit secrets, caches, generated artifacts, or private keys.
- Prefer path allowlists over blanket `git add .`.
- Treat `IDE_Work_Spaces/` as a legacy mirror, not a canonical source tree.
- Use `workspace/` only for local scratch work.
