# Smoke Check Guide

This checklist helps you verify the key stacks quickly before opening a full issue.

## Desktop / Core app

1. Ensure Python 3.12 and dependencies are setup:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. Confirm `.env` keys are present:

   - `PYTHONPATH=src` before running the app or tests
   - Optional secrets: `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY`, `FERNET_KEY`

3. Run the smoke test suite:

   ```powershell
   $env:PYTHONPATH='src'
   python -m pytest tests/test_data_analysis.py -q
   ```

4. Start the desktop UI (will surface missing config early):

   ```powershell
   $env:PYTHONPATH='src'; python -m src.app.main
   ```

## Web backend / frontend

1. Start the Flask backend:

   ```powershell
   cd web/backend
   flask run
   ```

2. Start the React frontend (requires Node):

   ```powershell
   cd ../frontend
   npm install
   npm run dev
   ```

3. Verify shared modules load by running the backend tests (when available).

## Coverage artifacts

- After running tests locally, capture coverage for upload (CI uses the same command):

  ```powershell
  $env:PYTHONPATH='src'; python -m pytest tests/ --cov=src/app/core --cov-report=xml:reports/coverage.xml --cov-report=html:htmlcov -q
  ```

- Inspect `htmlcov/index.html` to ensure the modules you care about are green.
