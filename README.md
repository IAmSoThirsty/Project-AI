# Project AI

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
  - Save generated paths per user

- Data Analysis (feature #6)
  - Load CSV/XLSX/JSON
  - Basic statistics and missing value reports
  - Visualizations (scatter, histogram, boxplot, correlation)
  - Simple clustering (K-means) with PCA visualization

- Security Resources (feature #2)
  - Curated lists of security/CTF/privacy repos
  - Fetch repository details from GitHub API
  - Save favorites per user

- Location Tracking (feature #1)
  - IP-based fallback geolocation
  - Optional GPS reverse-geocoding support (via geopy)
  - Encrypted location history (Fernet)
  - Periodic recording when enabled (every 5 minutes)

- Emergency Alerts (feature #5)
  - Register emergency contacts per user

  # Project-AI — Desktop AI Assistant

   A Python desktop application providing a local AI assistant with a book-like UI.
   It was converted from a WinForms prototype and implements a prioritized feature set
   (learning paths, data analysis, security resources, location tracking, emergency
   alerts) using a PyQt6 GUI and a small collection of core modules.

  ## Highlights

  - Local user management (JSON-backed, hashed passwords).
  - Learning Paths: personalized learning path generation (OpenAI optional).
  - Data Analysis: load CSV/XLSX/JSON, basic summary stats, visualizations, clustering.
  - Security Resources: curated repo lists and favorites per user.
  - Location Tracking: encrypted location history (Fernet) and reverse-geocoding.
  - Emergency Alerts: send email alerts to registered contacts with last known location.

  ## Quick setup (Windows, PowerShell)

   1. Create and activate a virtual environment (recommended):

   ```powershell
   python -m venv .venv
   & .\.venv\Scripts\Activate.ps1
   ```

   Install dependencies (use the repo `requirements.txt`):

   ```powershell
   pip install -r requirements.txt
   ```

   3. Create a `.env` file in the repository root (or set OS environment variables).
      Minimal recommended variables:

  - `OPENAI_API_KEY` — optional, for the learning-paths and any OpenAI calls.
  - `SMTP_USERNAME` / `SMTP_PASSWORD` — for sending emergency alert emails.
  - `FERNET_KEY` — base64-encoded Fernet key. If omitted the app will generate a
     runtime key (not persistent across restarts).
  - `DATA_DIR` / `LOG_DIR` — optional directories (defaults: `data`, `logs`).

   Example `.env` lines (do not commit real secrets):

   ```text
   OPENAI_API_KEY=sk-...
   SMTP_USERNAME=you@example.com
   SMTP_PASSWORD=<app-password>
   FERNET_KEY=<base64-key>
   ```

   4. Run tests and lint (recommended before running the app):

   ```powershell
   $env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; python -m pytest -q
   $env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; flake8 src tests setup.py
   ```

  ## Run the application (PowerShell)

   Start the app from the repository root (ensure the venv is activated and PYTHONPATH is set):

   ```powershell
   $env:PYTHONPATH='src'; .\.venv\Scripts\Activate.ps1; python src/app/main.py
   ```

   Notes:
  - On first run the app will prompt to create an admin account (first-run onboarding).
  - The GUI uses PyQt6; the app expects a graphical desktop environment.

  ## Migration and utilities

  - `tools/migrate_users.py` — preview/apply migration of plaintext `password` fields
     in an existing `users.json` into `password_hash` entries. It creates a `.bak` when
     applying changes.

   Example preview:

   ```powershell
   python tools/migrate_users.py --users-file src/app/users.json
   ```

   Apply migration:

   ```powershell
   python tools/migrate_users.py --users-file src/app/users.json --apply
   ```

  ## Security notes

  - Do not commit API keys, passwords, or private Fernet keys to source control.
  - Use OS-level secrets or a secrets manager for production deployments.
  - The app uses pbkdf2_sha256 as the preferred hashing scheme and accepts bcrypt
     for legacy verification.

  ## Developer notes

  - Entry point: `src/app/main.py` (loads `.env` and starts the PyQt application).
  - Core modules live under `src/app/core/` and GUI components under `src/app/gui/`.
  - Tests: `tests/` (run with `python -m pytest` using PYTHONPATH=src).

   ---

   If you want, I can:
  - Add a GitHub Actions CI workflow to run pytest + flake8 on push/PR, or
  - Commit these README changes and create a branch with the lint fixes I made.

   Now I'll run the test suite and then start the application in the background so you can interact with the GUI if you're on the machine.
