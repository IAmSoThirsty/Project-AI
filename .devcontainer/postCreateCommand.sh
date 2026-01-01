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
    echo "⚠️  Remember to update .env with your API keys!"
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🔑 Don't forget to set your API keys in .env:"
echo "   - OPENAI_API_KEY"
echo "   - HUGGINGFACE_API_KEY"
echo "   - FERNET_KEY (generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
echo ""
echo "🚀 To start the application:"
echo "   python -m src.app.main"
