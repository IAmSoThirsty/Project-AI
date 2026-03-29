#!/bin/bash
# Thirstys Waterfall - Linux/macOS Installation Script
# Run with: bash install.sh

set -e

echo "================================="
echo "Thirstys Waterfall Installer"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo -e "${GREEN}✓ Platform: $PLATFORM${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}pip3 not found, installing...${NC}"
    python3 -m ensurepip --default-pip
fi

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install package
echo ""
echo "Installing Thirstys Waterfall..."
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    # Install from local source
    echo "Installing from local source..."
    pip3 install -e .
else
    # Install from PyPI
    echo "Installing from PyPI..."
    pip3 install thirstys-waterfall
fi

# Platform-specific dependencies
echo ""
echo "Checking platform-specific dependencies..."

if [ "$PLATFORM" = "Linux" ]; then
    echo -e "${YELLOW}For full VPN and firewall functionality, you may need to install:${NC}"
    echo "  sudo apt-get install wireguard-tools openvpn nftables strongswan"
    echo ""
    read -p "Install these dependencies now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo apt-get update
        sudo apt-get install -y wireguard-tools openvpn nftables strongswan || echo -e "${YELLOW}Some packages may not be available on your distribution${NC}"
    fi
elif [ "$PLATFORM" = "macOS" ]; then
    echo -e "${YELLOW}For full VPN functionality, you may need to install:${NC}"
    echo "  brew install wireguard-tools openvpn"
    echo ""
    if command -v brew &> /dev/null; then
        read -p "Install these dependencies now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            brew install wireguard-tools openvpn || echo -e "${YELLOW}Some packages may already be installed${NC}"
        fi
    else
        echo -e "${YELLOW}Homebrew not found. Install from https://brew.sh${NC}"
    fi
fi

# Verify installation
echo ""
echo "Verifying installation..."
if command -v thirstys-waterfall &> /dev/null; then
    echo -e "${GREEN}✓ Thirstys Waterfall installed successfully!${NC}"
    echo ""
    echo "Usage:"
    echo "  thirstys-waterfall --help    # Show help"
    echo "  thirstys-waterfall --status  # Show status"
    echo ""
    echo "Python API:"
    echo "  from thirstys_waterfall import ThirstysWaterfall"
    echo "  waterfall = ThirstysWaterfall()"
    echo "  waterfall.start()"
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    echo "Try running: python3 -m pip install --user -e ."
    exit 1
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Review examples/ directory for usage examples"
echo "  3. Read the documentation in README.md"
echo ""
