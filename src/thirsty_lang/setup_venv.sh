#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env bash

# Thirsty-lang Python Virtual Environment Setup Script
# This script creates and configures a Python virtual environment

set -e

VENV_DIR=".venv"
PYTHON_CMD="python3"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     💧 Thirsty-lang Python Environment Setup 💧           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3 is installed
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv $VENV_DIR
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"
echo ""

# Install core dependencies
echo "Installing core dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Core dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping..."
fi
echo ""

# Install development dependencies (optional)
if [ -f "requirements-dev.txt" ]; then
    read -p "Install development dependencies? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing development dependencies..."
        pip install -r requirements-dev.txt
        echo "✓ Development dependencies installed"
    fi
    echo ""
fi

# Create activation helper
cat > activate_venv.sh << 'EOF'
#!/usr/bin/env bash
# Helper script to activate the virtual environment
source .venv/bin/activate
echo "✓ Thirsty-lang Python environment activated"
echo "  Run 'deactivate' to exit the virtual environment"
EOF
chmod +x activate_venv.sh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 Setup Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source .venv/bin/activate"
echo "  OR"
echo "  ./activate_venv.sh"
echo ""
echo "To run Thirsty-lang with Python:"
echo "  python3 src/thirsty_interpreter.py examples/hello.thirsty"
echo ""
echo "To run the Python REPL:"
echo "  python3 src/thirsty_repl.py"
echo ""
echo "Stay hydrated! 💧✨"
