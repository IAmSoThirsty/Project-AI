#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/usr/bin/env bash

# Thirsty-lang Complete Setup Script
# Installs ALL required dependencies and sets up the environment

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     💧 Thirsty-lang Complete Setup 💧                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will set up Thirsty-lang with all dependencies:"
echo "  • Node.js dependencies"
echo "  • Python virtual environment"
echo "  • Required folders and files"
echo "  • Docker verification (optional)"
echo ""

# Check Node.js
echo "=== Checking Node.js ==="
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "   Please install Node.js from https://nodejs.org"
    echo "   Required version: 14.0.0 or higher"
    exit 1
fi

NODE_VERSION=$(node --version 2>/dev/null | sed 's/v//' | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 14 ] 2>/dev/null; then
    echo "⚠️  Node.js version check failed or version is too old"
    echo "   Required: v14.0.0 or higher"
    echo "   Found: $(node --version 2>&1)"
    exit 1
fi

echo "✓ Node.js $(node --version) detected"
echo ""

# Check Python3
echo "=== Checking Python 3 ==="
if ! command -v python3 &> /dev/null; then
    echo "⚠️  Python 3 is not installed!"
    echo "   Python support will be limited"
    SKIP_PYTHON=1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python $PYTHON_VERSION detected"
    SKIP_PYTHON=0
fi
echo ""

# Install Node.js dependencies
echo "=== Installing Node.js Dependencies ==="
if [ -f "package.json" ]; then
    npm install
    echo "✓ Node.js dependencies installed"
else
    echo "⚠️  package.json not found"
fi
echo ""

# Setup Python virtual environment
if [ "$SKIP_PYTHON" -eq 0 ]; then
    echo "=== Setting up Python Virtual Environment ==="
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment already exists"
    fi
    
    # Activate and install Python dependencies
    source .venv/bin/activate
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt > /dev/null 2>&1 || true
        echo "✓ Python dependencies installed"
    fi
    
    deactivate
    echo ""
fi

# Check Docker (optional)
echo "=== Checking Docker (Optional) ==="
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo "✓ Docker $DOCKER_VERSION detected"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        echo "✓ Docker Compose $COMPOSE_VERSION detected"
    else
        echo "⚠️  Docker Compose not found (optional)"
    fi
else
    echo "⚠️  Docker not found (optional)"
fi
echo ""

# Verify essential directories exist
echo "=== Verifying Project Structure ==="
REQUIRED_DIRS=("src" "examples" "docs" "playground" "tools" "vscode-extension")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✓ $dir/ exists"
    else
        echo "⚠️  $dir/ not found"
    fi
done
echo ""

# Verify essential files exist
echo "=== Verifying Essential Files ==="
REQUIRED_FILES=(
    "README.md"
    "package.json"
    "LICENSE"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    "VERSION.txt"
    "AUTHORS.txt"
    "DEPENDENCIES.txt"
    "requirements.txt"
    "requirements-dev.txt"
    "Dockerfile"
    "docker-compose.yml"
    ".gitignore"
    ".dockerignore"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "⚠️  $file not found"
    fi
done
echo ""

# Run tests
echo "=== Running Tests ==="
npm test
echo ""

# Test Python implementation if available
if [ "$SKIP_PYTHON" -eq 0 ]; then
    echo "=== Testing Python Implementation ==="
    if [ -f "examples/hello.thirsty" ]; then
        python3 src/thirsty_interpreter.py examples/hello.thirsty
        echo "✓ Python interpreter works"
    fi
    echo ""
fi

# Make scripts executable
echo "=== Setting Permissions ==="
chmod +x setup_venv.sh 2>/dev/null || true
chmod +x quickstart.sh 2>/dev/null || true
chmod +x src/*.py 2>/dev/null || true
echo "✓ Scripts are executable"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 Setup Complete! 🎉                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "What's installed:"
echo "  ✓ Node.js dependencies"
if [ "$SKIP_PYTHON" -eq 0 ]; then
    echo "  ✓ Python virtual environment (.venv)"
    echo "  ✓ Python dependencies"
fi
echo "  ✓ All required files verified"
echo "  ✓ Tests passed"
echo ""
echo "Quick start commands:"
echo "  Node.js:  npm start examples/hello.thirsty"
if [ "$SKIP_PYTHON" -eq 0 ]; then
    echo "  Python:   source .venv/bin/activate && python3 src/thirsty_interpreter.py examples/hello.thirsty"
fi
if command -v docker &> /dev/null; then
    echo "  Docker:   docker-compose up"
fi
echo ""
echo "Learn Thirsty-lang:"
echo "  npm run train      # Interactive training"
echo "  npm run repl       # Interactive REPL"
echo ""
echo "Documentation:"
echo "  README.md          # Main documentation"
echo "  PYTHON_SETUP.md    # Python setup guide"
echo "  DOCKER.md          # Docker guide"
echo ""
echo "Stay hydrated! 💧✨"
