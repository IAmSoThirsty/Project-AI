#!/bin/bash
# IncrediBuild Installation Script
# This script sets up IncrediBuild dependencies

set -e

echo "=========================================="
echo "  IncrediBuild Installation"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install pyyaml boto3 redis

# Install sccache (distributed cache for Rust/C/C++)
echo ""
echo "Installing sccache..."
if command -v cargo &> /dev/null; then
    cargo install sccache
    echo "✅ sccache installed"
else
    echo "⚠️  Cargo not found, skipping sccache installation"
fi

# Install ccache (distributed cache for C/C++)
echo ""
echo "Installing ccache..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y ccache
    echo "✅ ccache installed"
elif command -v brew &> /dev/null; then
    brew install ccache
    echo "✅ ccache installed"
else
    echo "⚠️  Package manager not found, please install ccache manually"
fi

# Configure AWS CLI (if available)
echo ""
echo "Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI found"
    echo "Run 'aws configure' to set up credentials"
else
    echo "⚠️  AWS CLI not found"
    echo "Install with: pip install awscli"
fi

# Create directories
echo ""
echo "Creating IncrediBuild directories..."
mkdir -p ~/.cache/incredibuild
mkdir -p ~/.cache/sccache
mkdir -p ~/.cache/ccache

echo ""
echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Configure cloud credentials in incredibuild/config/incredibuild.yaml"
echo "  2. Run quickstart: python incredibuild/scripts/quickstart.py"
echo ""
