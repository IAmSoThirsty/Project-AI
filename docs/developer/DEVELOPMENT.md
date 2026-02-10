# Development (canonical)

This document is the canonical developer setup and workflow for Project-AI.

## Supported versions

- Python: 3.11 (recommended)
- Node: 18+ (only required for `web/frontend`)

## Environment setup (Windows PowerShell)

### 1) Create and activate a virtualenv

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Install dependencies

**Runtime + tests:**

```powershell
pip install -r requirements.txt
```

**Optional dev tooling (Qt Designer + lock tooling):**

```powershell
pip install -r requirements-dev.txt
```

### 3) Using the lock file (recommended for reproducibility)

If you want a reproducible installation (CI-style), install from the lock:

```powershell
pip install --require-hashes -r requirements.lock
```

## Running the application

```powershell
$env:PYTHONPATH='src'
python -m src.app.main
```

## Running tests

```powershell
$env:PYTHONPATH='src'
pytest -q
```

## Linting / formatting

```powershell
ruff check .
```

## FourLaws test run report

After running the FourLaws suites, regenerate and commit the consolidated report:

```powershell
powershell -ExecutionPolicy Bypass -File tools/regenerate_and_commit_fourlaws_report.ps1
```

Artifacts are created locally under `test-artifacts/` and are ignored by git. The consolidated report is committed under `docs/security/`.
