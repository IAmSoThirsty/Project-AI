# Troubleshooting Checklist

## Environment sanity

- Confirm you are on Python 3.12 and the virtual environment is activated:

  ```powershell
  python --version
  & .\.venv\Scripts\Activate.ps1
  ```

- Verify required packages are installed:

  ```powershell
  pip install -r requirements.txt
  ```

- If cryptography complains about Fernet, regenerate a key:

  ```powershell
  python - <<'PY'
  from cryptography.fernet import Fernet
  print(Fernet.generate_key().decode())
  PY
  ```

## Application issues

- **App refuses to start / PyQt errors**: ensure `PYTHONPATH=src` and the `.env` file contains `FERNET_KEY`, `OPENAI_API_KEY`, and `HUGGINGFACE_API_KEY` when the features are enabled.
- **Data persistence is blank**: check `data/` and `logs/` directories for permissions; delete corrupted JSON files and rerun to rebuild.
- **Image generation fails with HTTP errors**: confirm `HUGGINGFACE_API_KEY` and `OPENAI_API_KEY` are valid and the network allows outbound HTTPS calls.

## Testing & coverage

- If pytest fails due to imports, rerun with `PYTHONPATH=src`:

  ```powershell
  $env:PYTHONPATH='src'
  python -m pytest tests/ -q
  ```

- Coverage reports not generating? Ensure `reports/` and `htmlcov/` are created before running coverage and that the `tests/` directory is in the command.

## Web frontend / backend

- Flask backend not starting? Check `FLASK_APP` and run:

  ```powershell
  set FLASK_APP=web/backend/app.py
  flask run
  ```

- React frontend missing modules? Remove `node_modules` and reinstall:

  ```powershell
  cd web/frontend
  rm -r node_modules
  npm install
  npm run lint
  ```
