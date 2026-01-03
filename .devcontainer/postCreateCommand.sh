#!/bin/bash
set -e

echo "🚀 Setting up Project-AI development environment..."

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install Python requirements
echo "📦 Installing Python dependencies..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Install development tools
echo "🔧 Installing development tools..."
pip install ruff mypy black isort pytest pytest-cov pre-commit

# Install Node.js dependencies (if frontend exists)
echo "📦 Installing Node.js dependencies..."
if [ -f package.json ]; then
    npm install
fi

# Create necessary directories
echo "📁 Creating data and log directories..."
mkdir -p data logs
mkdir -p data/ai_persona data/memory data/learning_requests

# Set up pre-commit hooks (optional, can fail)
echo "🪝 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install || echo "⚠️  Pre-commit setup failed, continuing..."
fi

# Copy .env.example to .env if it doesn't exist
if [ -f .env.example ] && [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  CRITICAL: You MUST update .env with your own credentials!"
    echo "⚠️  NEVER commit .env to version control - it's in .gitignore"
    echo "⚠️  Generate new credentials - do NOT use examples from docs"
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🔐 SECURITY REQUIREMENTS - Please complete the following:"
echo ""
echo "1. 🔑 Generate and set your API keys in .env:"
echo "   - OPENAI_API_KEY (from https://platform.openai.com/api-keys)"
echo "   - HUGGINGFACE_API_KEY (from https://huggingface.co/settings/tokens)"
echo ""
echo "2. 🔐 Generate a NEW Fernet key (do NOT reuse examples):"
echo "   python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo "   Then set FERNET_KEY in .env with the generated value"
echo ""
echo "3. ⚠️  NEVER commit .env file to version control!"
echo "   - Verify .env is in .gitignore"
echo "   - If you accidentally commit secrets, rotate them immediately"
echo "   - Use tools/purge_git_secrets.ps1 to remove from history"
echo ""
echo "4. 🔄 Rotate credentials regularly (every 90 days minimum)"
echo ""
echo "🚀 To start the application:"
echo "   python -m src.app.main"
