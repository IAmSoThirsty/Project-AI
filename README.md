# Project AI
# Project-AI — Desktop AI Assistant

This repository contains a Python desktop application that provides a personal AI assistant with features adapted from a WinForms prototype. The app is designed for member-only use and can be extended for mobile later.

## High-level features

- User management
  - Local JSON-backed user profiles
  - Persona and preference settings
  - (Encrypted) storage support for sensitive data

- Chat / AI Tutor
  - Conversational interface
  - AI Code Tutor (via OpenAI GPT models)
  - Intent detection using a scikit-learn model

- Learning Paths (feature #3 implemented first)
  - Generate personalized learning paths via OpenAI
  - **Offline mode**: Template-based learning paths for common topics (Python, Programming, Data Science, Web Development, Machine Learning, Cybersecurity)
  - Save generated paths per user

- Data Analysis (feature #6)
  - Load CSV/XLSX/JSON
  - Basic statistics and missing value reports
  - Visualizations (scatter, histogram, boxplot, correlation)
  - Simple clustering (K-means) with PCA visualization
  - **Works fully offline** - all processing is local

- Security Resources (feature #2)
  - Curated lists of security/CTF/privacy repos
  - Fetch repository details from GitHub API
  - **Offline mode**: Built-in cache of popular security repositories
  - Save favorites per user

- Location Tracking (feature #1)
  - IP-based fallback geolocation
  - Optional GPS reverse-geocoding support (via geopy)
  - Encrypted location history (Fernet)
  - Periodic recording when enabled (every 5 minutes)
  - **Offline mode**: Uses cached last-known location when offline

- Emergency Alerts (feature #5)
  - Register emergency contacts per user
  - Send email alerts to contacts with last known location
  - Alert logging and history

## Offline Mode

The application is designed to work offline with graceful degradation:

- **Network Status Indicator**: The status bar shows current connectivity status (🌐 Online or 📴 Offline Mode)
- **Learning Paths**: When offline or without API key, provides template-based learning paths for common topics
- **Security Resources**: Uses built-in cache for repository information when GitHub API is unavailable
- **Location Tracking**: Falls back to last known location when geolocation APIs are unavailable
- **Data Analysis**: Works fully offline as all processing is done locally
- **Intent Detection**: Uses local scikit-learn model, works offline

### Offline-compatible features summary

| Feature | Online | Offline |
|---------|--------|---------|
| Learning Paths | AI-generated via OpenAI | Template-based paths |
| Security Resources | Live GitHub data | Cached repository info |
| Location Tracking | IP geolocation | Last known location |
| Data Analysis | ✓ | ✓ (fully local) |
| Intent Detection | ✓ | ✓ (fully local) |
| Emergency Alerts | ✓ (requires SMTP) | Logs locally |

## Files of interest

- `src/app/main.py` — Application entrypoint. Loads environment variables.
- `src/app/gui/dashboard.py` — Main UI (PyQt6) with tabs for all features.
- `src/app/core/intent_detection.py` — Simple scikit-learn pipeline for intent detection.
- `src/app/core/user_manager.py` — User profile and persistence; uses Fernet key from environment if available.
- `src/app/core/learning_paths.py` — Learning path generation using OpenAI (with offline fallback templates).
- `src/app/core/data_analysis.py` — Data analysis utilities and plotting helpers.
- `src/app/core/security_resources.py` — Security resources manager and GitHub lookup (with offline cache).
- `src/app/core/location_tracker.py` — Tracking and encrypted history (with offline fallback).
- `src/app/core/emergency_alert.py` — Emergency alert sending and logging.
- `src/app/core/network_utils.py` — Network connectivity detection utilities.

## Environment variables (.env)

Create a `.env` file in the repository root or set OS-level environment variables. The app loads the `.env` automatically.

Required / recommended variables:

- `OPENAI_API_KEY` — (optional) API key for OpenAI if you want to use auto-generated learning paths and code tutor.
- `SMTP_USERNAME` — Email address used to send emergency alerts.
- `SMTP_PASSWORD` — Password (or app-specific password) for the SMTP account.
- `FERNET_KEY` — Base64-encoded Fernet key used to encrypt location history and other secrets. If omitted, the app will generate a key on first run but it will not be reproducible across restarts.
- `DATA_DIR` — Optional path for app data (default: `data`).
- `LOG_DIR` — Optional log directory (default: `logs`).

A sample `.env` was added to the repository with placeholders and a generated `FERNET_KEY`.

## Setup and run

Create and activate a Python virtual environment (the repo already includes a `.venv` if you followed prior steps):

powershell

1. python -m venv .venv
& .venv\Scripts\Activate.ps1
pip install -r requirements.txt  # or use setup.py / pip install -e .

2. Populate `.env` (or set OS env vars):

OPENAI_API_KEY=sk-...
SMTP_USERNAME=<your.email@example.com>
SMTP_PASSWORD=app-or-real-password
FERNET_KEY=<>

1. Run the app:

```powershell
python src/app/main.py
```

## Notes on security

- The included Fernet key in the example `.env` is for convenience only. For production, keep your key secret and rotate as needed.
- Do not commit real API keys or passwords to source control. Use a secret manager or OS-level environment variables when deploying.
- Emails for emergency alerts require correct SMTP settings and credentials (e.g., Gmail may need an app password and "Less secure apps" settings disabled).

## How the env vars are used in-app

- `main.py` uses `python-dotenv` to load `.env` at startup.
- `user_manager` and `location_tracker` prefer `FERNET_KEY` from env to make encryption consistent across runs.
- `learning_paths` uses `OPENAI_API_KEY` for OpenAI requests.
- `emergency_alert` uses `SMTP_USERNAME` / `SMTP_PASSWORD` for sending emails.

or

## Quick start (book UI and first-run onboarding)

Run the application:

```powershell
python src/app/main.py
```

1. On first run, the app will detect no users and prompt you to create a secure admin account (username + password). Create the admin account when prompted.

2. After creating the admin account, return to the login screen and sign in with that account. The Login dialog will switch to a "Table of Contents" view (the book's TOC). Select a chapter and click "Open Chapter" — the Dashboard will open with that chapter active.

3. Admins can manage users from the "Users" tab (create/delete accounts, approve registrations, set roles and profile picture paths).

Migration tool: If you previously had plaintext passwords saved in `users.json`, use the migration preview tool to see which users would be migrated and optionally apply it (it creates a `.bak` backup):

```powershell
python tools/migrate_users.py --users-file src/app/users.json
# or to apply the changes
python tools/migrate_users.py --users-file src/app/users.json --apply
```

Security reminder: The app now uses bcrypt-hashed passwords stored under `password_hash`. Keep `FERNET_KEY` and other secrets out of source control and rotate keys as needed.

## Next steps / optional improvements

- Replace direct OpenAI calls with a pluggable provider interface (local model, Hugging Face, etc.).
- Add a proper login screen and protect the app with a stronger authentication flow.
- Implement a secure secrets storage backend instead of `.env` (Azure Key Vault, HashiCorp Vault, or platform secrets).
- Add unit tests for core modules (user_manager, location_tracker, emergency_alert).

If you'd like, I can:

- Wire up a more robust login flow (persist sessions, hashed passwords),
- Add a settings dialog to manage SMTP/OpenAI keys from the GUI,
- Or implement mobile integration scaffolding (React Native / Flutter bridge).
