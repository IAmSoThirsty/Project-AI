# Desktop Quickstart - Project-AI (Leather Book)

This quickstart helps you run the native desktop (PyQt6) Leather Book interface.

Prerequisites
- Python 3.12 or newer
- Virtualenv (recommended)
- PyQt6, cryptography, scikit-learn and other dependencies (see requirements.txt)

Create and activate a virtual environment (PowerShell):
```powershell
cd C:\Users\Jeremy\Documents\GitHub\Project-AI
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the desktop app:
```powershell
$env:PYTHONPATH='src'
python -m src.app.main
```

Troubleshooting
- If PyQt6 fails to install on Windows, ensure you have the latest pip:
```powershell
python -m pip install --upgrade pip
```

- If you see import errors, ensure PYTHONPATH is set to the project `src` directory.
- For GUI threading issues, the project uses QThread and pyqtSignal. Do not run long blocking code on the main thread.

Notes
- Use `launch-desktop.ps1` for a Windows-friendly launcher that sets env vars and starts the app.
- If you want to run with a `.env` file, the app will load OpenAI and Hugging Face keys automatically when present.

