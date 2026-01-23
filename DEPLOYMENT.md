# Deployment & Release Checklist

This document captures the manual steps required to create and ship the Project-AI desktop and web experiences so that every release is predictable.

## Desktop Application

1. **Install dependencies**

   ```powershell
   py -3.11 -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

1. **Run pytest suite**

   ```powershell
   $env:PYTHONPATH='src'
   python -m pytest --maxfail=1 --disable-warnings
   ```

1. **Build the PyQt6 executable**
   - Use `pyinstaller` (install via `pip install pyinstaller`) with a spec that includes `src/app/main.py`.
   - Example: `pyinstaller --onefile --name project-ai src/app/main.py`.
1. **Bundle assets**
   - Copy `data/`, `docs/`, and `web/` artifacts into the distributable folder.
   - Ensure `FERNET_KEY`, API keys, and overrides are provided via environment or secure secrets vault (do not hardcode them).
1. **Sign and publish**
   - Sign the executable using the organization’s code signing certificate.
   - Upload the installer/archive to the private release server or shared file storage.
   - Update release notes with new AI capabilities, vulnerability fixes, and CLI updates.

## Web Backend & Frontend

The repo ships minimal frontend/backed smoke scaffolds that are not production-grade yet, but the release steps below ensure the placeholders remain runnable.

1. **Web backend (Flask)**

   ```powershell
   $env:PYTHONPATH='web/backend'
   flask --app web.backend.app run
   ```

1. **Frontend**
   - Serve `web/frontend/index.html` via any static file server (e.g., `python -m http.server 3000`).
   - Validate the page loads and shows the smoke content.
1. **Integrate with desktop release**
   - Embed the Flask backend and front-end artifacts inside the `data/web` folder so the desktop app can point WebView/HTTP clients to `http://localhost:5000`.

## Release Checklist

- [ ] Update `README.md`, `PROGRAM_SUMMARY.md`, and developer docs with new features.
- [ ] Bump version metadata if stored in `setup.py`/`pyproject.toml` (add release tag if necessary).
- [ ] Re-run formatting (`ruff`, `black`, `isort`) and markdown lint before packaging.
- [ ] Publish artifacts along with changelog entries.
- [ ] Notify team members via Slack/email with release summary and testing status.
