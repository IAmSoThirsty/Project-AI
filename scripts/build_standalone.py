# [2026-03-04 10:45]
# Productivity: Active
# Project-AI Standalone Build Orchestrator (Python API)

import os
import subprocess
import sys


def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    print("--- Project-AI Sovereign Build (Python) ---")
    print(f"Working Directory: {root}")

    # 1. Ensure internal dependencies are installed
    venv_name = ".venv_prod"
    venv_dir = os.path.join(root, venv_name)
    venv_python = (
        os.path.join(venv_dir, "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(venv_dir, "bin", "python")
    )

    if not os.path.exists(venv_dir):
        print(f"[1/3] Creating fresh venv: {venv_name}...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    print("[2/3] Installing dependencies in fresh environment...")
    if not run_cmd(
        [
            venv_python,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
            "PyQt6",
            "PyInstaller",
        ]
    ):
        print("Failed to install dependencies.")
        sys.exit(1)

    # 2. Run PyInstaller
    print("[2/3] Building executable...")
    # Using python -m PyInstaller is safer than searching for the script
    build_cmd = [
        venv_python,
        "-m",
        "PyInstaller",
        "src/app/main.py",
        "--name",
        "ProjectAI",
        "--onedir",
        "--windowed",
        "--add-data",
        f"src/app/gui{os.pathsep}src/app/gui",
        "--hidden-import",
        "PyQt6",
        "--clean",
        "--noconfirm",
    ]

    if not run_cmd(build_cmd):
        print("PyInstaller build failed.")
        sys.exit(1)

    # 3. Verify and Prep dist
    dist_dir = os.path.join(root, "dist", "ProjectAI")
    if os.path.exists(dist_dir):
        print(f"--- Build Successful: {dist_dir} ---")
    else:
        print("Error: Build produced no output.")
        sys.exit(1)


if __name__ == "__main__":
    main()
