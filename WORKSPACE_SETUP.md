# Workspace Setup

This repository supports an optional workspace mount for local scratch work,
but the tracked source tree remains canonical.

## Layout

- `workspace/` is disposable scratch space.
- `output/` is for generated artifacts.
- `tmp/` is for transient files.
- `.venv-linux/` is a local-only virtual environment.
- `.env.wsl` is a host-local environment shim.

## Typical local setup

```bash
mkdir -p workspace repositories projects notebooks artifacts
python Verify-SovereignLoaders.py
python scripts/verify/verify_thirsty_interpreter.py
```

## Recovery guidance

- Restore code from the canonical tracked tree first.
- Keep local-only runtime state out of git.
- Use allowlisted adds when repairing a wiped checkout.
- Prefer small verification steps after each recovery pass.
