#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env python3
"""
Quick start script for Project AI.
Checks environment, installs dependencies, and starts services.
"""

import subprocess
import sys


def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def check_node():
    """Check if Node.js is installed."""
    print("\n🟢 Checking Node.js...")
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("⚠️  Node.js not found (required for desktop app)")
    return False


def main():
    """Main setup routine."""
    print_header("🚀 Project AI - Quick Start")

    # Check environment
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Continuing without dependencies...")

    # Check Node.js
    has_node = check_node()

    # Print next steps
    print_header("✨ Setup Complete")
    print("Next steps:\n")
    print("  Backend API:")
    print("    python scripts/start_api.py\n")
    print("  Web Frontend:")
    print("    Open web/index.html in browser\n")

    if has_node:
        print("  Desktop App:")
        print("    cd desktop && npm install && npm run dev\n")

    print("  Run Tests:")
    print("    pytest tests/ -v\n")
    print("  Verify System:")
    print("    python scripts/maintenance/verify_system.py\n")

    print("📚 Documentation: docs/README.md")
    print("🏛️  Constitution: docs/CONSTITUTION.md\n")


if __name__ == "__main__":
    main()
