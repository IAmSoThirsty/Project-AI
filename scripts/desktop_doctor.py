#!/usr/bin/env python3
"""Desktop Doctor — one command that tells you exactly why the desktop app
won't start on this machine, and exactly how to fix it.

Usage:
    python scripts/desktop_doctor.py            # diagnose
    python scripts/desktop_doctor.py --launch   # diagnose, then launch the app

Stdlib only. This script must never itself fail with an ImportError.
Verified launch path (2026-06-10): Python 3.11+, `pip install -e .`,
Qt system libraries present -> `PYTHONPATH=src python -m app.main`.
"""

import argparse
import importlib
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO_ROOT, "src")

GREEN, RED, YELLOW, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[0m"
if platform.system() == "Windows" and not os.environ.get("WT_SESSION"):
    GREEN = RED = YELLOW = RESET = ""

# (import name, pip name) — every third-party import on app.main's startup path
REQUIRED = [
    ("dotenv", "python-dotenv"),
    ("PyQt6.QtWidgets", "PyQt6"),
    ("numpy", "numpy"),
    ("pandas", "pandas"),
    ("sklearn", "scikit-learn"),
    ("psutil", "psutil"),
    ("yaml", "PyYAML"),
    ("requests", "requests"),
    ("cryptography", "cryptography"),
    ("flask", "Flask"),
    ("typer", "typer"),
    ("rich", "rich"),
    ("matplotlib", "matplotlib"),
    ("passlib", "passlib"),
    ("httpx", "httpx"),
    ("defusedxml", "defusedxml"),
    ("joblib", "joblib"),
    ("geopy", "geopy"),
]
# Optional: the Triumvirate REST sidecar (app degrades gracefully without it)
OPTIONAL = [("uvicorn", "uvicorn"), ("fastapi", "fastapi")]

QT_LINUX_LIBS = (
    "libegl1 libgl1 libxkbcommon0 libxkbcommon-x11-0 libdbus-1-3 "
    "libfontconfig1 libx11-xcb1 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 "
    "libxcb-shape0 libxcb-render-util0 libxcb-image0 libxcb-randr0 libxcb-xinerama0"
)

def ok(msg):    print(f"  {GREEN}[OK]{RESET}   {msg}")
def fail(msg):  print(f"  {RED}[FAIL]{RESET} {msg}")
def warn(msg):  print(f"  {YELLOW}[WARN]{RESET} {msg}")

def check_python():
    print("\n-- Python --")
    v = sys.version_info
    if (v.major, v.minor) >= (3, 11):
        ok(f"Python {platform.python_version()}")
        return True
    fail(f"Python {platform.python_version()} — need 3.11 or newer")
    print("        FIX: install Python 3.12 from https://python.org and re-run")
    return False

def check_imports(items, optional=False):
    fixes = []
    for mod, pipname in items:
        try:
            importlib.import_module(mod)
            ok(mod)
        except ModuleNotFoundError:
            (warn if optional else fail)(f"{mod} — package not installed")
            fixes.append(pipname)
        except ImportError as e:
            # Package installed but a native library is missing (classic PyQt6-on-Linux)
            fail(f"{mod} — installed but failed to load: {e}")
            if "PyQt6" in mod and platform.system() == "Linux":
                print(f"        FIX: sudo apt-get install -y {QT_LINUX_LIBS}")
            else:
                print("        FIX: reinstall the package:"
                      f" {sys.executable} -m pip install --force-reinstall {pipname}")
    if fixes:
        print(f"\n        FIX: {sys.executable} -m pip install " + " ".join(fixes))
        print(f"        (or, from the repo root: {sys.executable} -m pip install -e .)")
    return not fixes

def check_app_import():
    print("\n-- Application import (src/app/main.py) --")
    # The app uses two import roots: `from app...` (needs src/ on the path)
    # and `from src.cognition...` (needs the repo root on the path).
    # Launching from the repo root with PYTHONPATH=src satisfies both.
    sys.path.insert(0, REPO_ROOT)
    sys.path.insert(0, SRC)
    try:
        importlib.import_module("app.main")
        ok("from app.main import main")
        return True
    except Exception as e:
        fail(f"app.main failed to import: {type(e).__name__}: {e}")
        import traceback
        tb = traceback.format_exc().strip().splitlines()
        print("        Last frames:")
        for line in tb[-6:]:
            print("        " + line)
        return False

def check_display():
    print("\n-- Display --")
    if platform.system() in ("Windows", "Darwin"):
        ok(f"{platform.system()} native display")
        return True
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        ok("X11/Wayland display detected")
        return True
    warn("No display detected (headless session)")
    print("        The GUI still runs offscreen for testing:")
    print("        QT_QPA_PLATFORM=offscreen python -m app.main")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--launch", action="store_true",
                        help="launch the desktop app if diagnosis passes")
    args = parser.parse_args()

    print("=" * 64)
    print("PROJECT-AI DESKTOP DOCTOR")
    print("=" * 64)
    print(f"Repo:   {REPO_ROOT}")
    print(f"Python: {sys.executable}")

    results = [check_python()]
    print("\n-- Required packages --")
    results.append(check_imports(REQUIRED))
    print("\n-- Optional (Triumvirate REST service) --")
    check_imports(OPTIONAL, optional=True)
    results.append(check_app_import())
    check_display()

    print("\n" + "=" * 64)
    if all(results):
        print(f"{GREEN}READY.{RESET} Launch the desktop app FROM THE REPO ROOT with:")
        if platform.system() == "Windows":
            print(r"    set PYTHONPATH=src && python -m app.main")
        else:
            print("    PYTHONPATH=src python -m app.main")
        print("    (or: python scripts/desktop_doctor.py --launch)")
        if args.launch:
            print("\nLaunching now...\n")
            env = dict(os.environ, PYTHONPATH=SRC)
            if platform.system() == "Linux" and not (
                os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
            ):
                env["QT_QPA_PLATFORM"] = "offscreen"
            sys.exit(subprocess.call([sys.executable, "-m", "app.main"],
                                     env=env, cwd=REPO_ROOT))
    else:
        print(f"{RED}NOT READY.{RESET} Apply the FIX lines above, then re-run:")
        print(f"    {sys.executable} scripts/desktop_doctor.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
