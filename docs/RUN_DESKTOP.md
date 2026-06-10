# Running the Desktop App — the verified path

This is the **tested, working procedure** for getting the Project-AI desktop
application running on a fresh machine. It was verified end-to-end on
2026-06-10 (Python 3.11, Linux, headless): full boot from tier registry →
Triumvirate → CognitionKernel → CouncilHub → security systems → desktop
adapter → `DashboardMainWindow` → `🎨 GUI launched - kernel governance active`.

If anything below fails, **do not debug by hand** — run the doctor, it will
tell you exactly what is missing and the exact command to fix it:

```bash
python scripts/desktop_doctor.py
```

---

## 1. Requirements

- **Python 3.11 or newer** (3.12 recommended)
- Windows, macOS, or Linux. On Linux, Qt needs system libraries (step 3).

## 2. Install Python dependencies

From the repository root:

```bash
python -m pip install -e .
```

This installs everything `src/app/main.py` needs, **including PyQt6**.
(Until 2026-06-10, PyQt6 — the GUI framework itself — was missing from
`pyproject.toml`, which is why fresh installs could never launch the app.
That is fixed; `uvicorn` and `fastapi` for the Triumvirate REST service are
also now declared.)

## 3. Linux only: Qt system libraries

PyQt6 needs native graphics libraries that pip cannot install:

```bash
sudo apt-get install -y libegl1 libgl1 libxkbcommon0 libxkbcommon-x11-0 \
    libdbus-1-3 libfontconfig1 libx11-xcb1 libxcb-cursor0 libxcb-icccm4 \
    libxcb-keysyms1 libxcb-shape0 libxcb-render-util0 libxcb-image0 \
    libxcb-randr0 libxcb-xinerama0
```

Windows and macOS need nothing here.

## 4. Launch

**From the repository root** (this matters — see "Why the path matters"):

```bash
# Linux / macOS
PYTHONPATH=src python -m app.main

# Windows (cmd)
set PYTHONPATH=src && python -m app.main

# Or, on any platform — diagnose and launch in one step:
python scripts/desktop_doctor.py --launch
```

Headless machine / SSH session (no display):

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m app.main
```

## 5. What success looks like

The log (also written to `logs/app.log`) ends with:

```
✅ All systems initialized and governed by CognitionKernel
✅ Desktop adapter initialized and routed through governance pipeline
🎨 GUI launched - kernel governance active
🔒 Security systems active and protecting
```

and the dashboard window opens.

---

## Why the path matters

The codebase currently uses **two import roots**:

- most of the app imports as `from app...` → requires `src/` on `sys.path`
  (that is what `PYTHONPATH=src` provides);
- `src/app/main.py` also imports `from src.cognition...` → requires the
  **repository root** on `sys.path` (running `python -m` from the repo root
  provides this automatically, because Python puts the current directory on
  the path).

Run from the repo root with `PYTHONPATH=src` and both are satisfied. Run from
anywhere else, or without `PYTHONPATH=src`, and you get
`ModuleNotFoundError: No module named 'app'` or
`No module named 'src'` — the two errors that have caused endless runaround.
`scripts/desktop_doctor.py` checks both roots and will name the problem
explicitly.

## Known non-fatal warnings

- `Triumvirate server could not start: No module named 'uvicorn'` — the
  REST sidecar on port 8001 is optional; in-process governance still runs.
  Fixed by `pip install -e .` (uvicorn/fastapi are now declared).
- `This plugin does not support propagateSizeHints()` — harmless Qt notice
  in offscreen mode.
