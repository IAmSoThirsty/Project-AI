#!/bin/bash
# Cross-platform build script for Project-AI
# Supports Linux, macOS, and Windows (via WSL/Git Bash)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
BUILD_DIR="$PROJECT_ROOT/dist"
VERSION=$(grep "version" pyproject.toml | head -1 | cut -d'"' -f2)

echo "=========================================="
echo "Project-AI Build Script v$VERSION"
echo "=========================================="
echo ""

# Detect OS
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="linux";;
    Darwin*)    OS="macos";;
    CYGWIN*|MINGW*|MSYS*) OS="windows";;
esac

echo "Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "[1/6] Checking prerequisites..."
if ! command_exists python3; then
    echo "❌ Python 3 not found. Please install Python 3.11 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "[2/6] Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo ""
    echo "[2/6] Using existing virtual environment..."
fi

# Activate virtual environment
echo ""
echo "[3/6] Activating virtual environment..."
if [ "$OS" = "windows" ]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi
echo "✓ Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "[4/6] Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -e .
pip install pyinstaller
echo "✓ Dependencies installed"

# Build with PyInstaller
echo ""
echo "[5/6] Building executable..."
if [ -f "project-ai.spec" ]; then
    pyinstaller project-ai.spec --clean --noconfirm
else
    echo "⚠️  project-ai.spec not found, creating basic executable..."
    pyinstaller src/app/main.py \
        --name ProjectAI \
        --onedir \
        --windowed \
        --add-data "data:data" \
        --hidden-import PyQt6 \
        --clean \
        --noconfirm
fi
echo "✓ Executable built"

# Create distributable archive
echo ""
echo "[6/6] Creating distribution archive..."
cd "$BUILD_DIR"

case "$OS" in
    linux)
        tar -czf "ProjectAI-$VERSION-linux-x86_64.tar.gz" ProjectAI/
        echo "✓ Created ProjectAI-$VERSION-linux-x86_64.tar.gz"
        ;;
    macos)
        if [ -d "ProjectAI.app" ]; then
            hdiutil create -volname "Project-AI" -srcfolder ProjectAI.app -ov -format UDZO "ProjectAI-$VERSION-macos.dmg"
            echo "✓ Created ProjectAI-$VERSION-macos.dmg"
        else
            tar -czf "ProjectAI-$VERSION-macos.tar.gz" ProjectAI/
            echo "✓ Created ProjectAI-$VERSION-macos.tar.gz"
        fi
        ;;
    windows)
        zip -r "ProjectAI-$VERSION-windows.zip" ProjectAI/
        echo "✓ Created ProjectAI-$VERSION-windows.zip"
        ;;
esac

cd "$PROJECT_ROOT"

echo ""
echo "=========================================="
echo "✓ Build completed successfully!"
echo "=========================================="
echo ""
echo "Distribution package location:"
echo "  $BUILD_DIR"
echo ""
echo "To run the application:"
echo "  $BUILD_DIR/ProjectAI/ProjectAI"
echo ""
