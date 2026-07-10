# Releasing TAAR

Manual checklist for publishing a release. Nothing here is automated —
TAAR does not ship itself.

## Preflight (local)

    python -m pytest -q
    python -m pip install . --target=%TEMP%\taar-smoke   # or a fresh venv
    taar status                                          # from the fresh install

Confirm the branch is `main` and the working tree is clean.

## GitHub

The repo is <https://github.com/IAmSoThirsty/TAAR> (matches `[project.urls]`
in pyproject.toml). It already holds an unrelated initial commit containing
the LICENSE, which the local tree does not have — merge it in rather than
force-pushing over it.

1. Connect and reconcile histories:

       git remote add origin https://github.com/IAmSoThirsty/TAAR.git
       git pull origin main --allow-unrelated-histories   # brings in LICENSE
       git push -u origin main

2. Tag and push the release tag consumers pin to:

       git tag v0.1.0
       git push origin v0.1.0

3. Create a GitHub Release from the tag. Optionally publish the action to
   the Marketplace (requires the release; `action.yml` branding is set).

The `taar-self-test` workflow runs on push to `main` and on PRs.

## PyPI

The GitHub Action installs from its own checkout and does not need PyPI.
PyPI only serves `pip install taar-agent-taskforce`.

Publishing is automated: `.github/workflows/publish.yml` builds and uploads
to PyPI via trusted publishing (OIDC, no API token) whenever a GitHub
Release is published. The trusted publisher is configured on pypi.org
(project `taar-agent-taskforce`, owner `IAmSoThirsty`, repository `TAAR`,
workflow `publish.yml`, environment `pypi`) and the `pypi` environment
exists in the GitHub repo settings.

Manual fallback:

    python -m pip install build twine
    python -m build
    python -m twine upload dist/*

## Version bumps

Update `version` in pyproject.toml and `__version__` in taar/__init__.py
together, then repeat from Preflight with the new tag.
