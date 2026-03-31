#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/bin/bash
# Test script for automated workflows
# This script validates the automation setup without triggering actual runs

set -e

echo "🔍 Testing Project-AI Automation Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} Found: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        return 1
    fi
}

# Function to validate YAML
validate_yaml() {
    if python3 -c "import yaml; yaml.safe_load(open('$1'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Valid YAML: $1"
        return 0
    else
        echo -e "${RED}✗${NC} Invalid YAML: $1"
        return 1
    fi
}

# Check workflow files
echo "📁 Checking Workflow Files"
echo "----------------------------"
check_file ".github/workflows/auto-pr-handler.yml"
check_file ".github/workflows/auto-security-fixes.yml"
check_file ".github/workflows/auto-bandit-fixes.yml"
check_file ".github/dependabot.yml"
check_file ".github/AUTOMATION.md"
echo ""

# Validate YAML syntax
echo "📝 Validating YAML Syntax"
echo "-------------------------"
validate_yaml ".github/workflows/auto-pr-handler.yml"
validate_yaml ".github/workflows/auto-security-fixes.yml"
validate_yaml ".github/workflows/auto-bandit-fixes.yml"
validate_yaml ".github/dependabot.yml"
echo ""

# Check for required tools
echo "🔧 Checking Required Tools"
echo "---------------------------"
TOOLS=("python3" "pip" "git" "gh")
for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Found: $tool"
    else
        echo -e "${YELLOW}⚠${NC} Not found: $tool (optional for local dev)"
    fi
done
echo ""

# Check Python packages for security scanning
echo "📦 Checking Security Tools"
echo "---------------------------"
PACKAGES=("bandit" "pip-audit" "safety" "ruff")
for package in "${PACKAGES[@]}"; do
    if python3 -m pip show "$package" &> /dev/null; then
        echo -e "${GREEN}✓${NC} Installed: $package"
    else
        echo -e "${YELLOW}⚠${NC} Not installed: $package (can be installed with: pip install $package)"
    fi
done
echo ""

# Check GitHub CLI authentication (if available)
if command -v gh &> /dev/null; then
    echo "🔐 Checking GitHub CLI Authentication"
    echo "--------------------------------------"
    if gh auth status &> /dev/null; then
        echo -e "${GREEN}✓${NC} GitHub CLI is authenticated"
    else
        echo -e "${YELLOW}⚠${NC} GitHub CLI not authenticated (run: gh auth login)"
    fi
    echo ""
fi

# Summary
echo "✅ Automation Setup Validation Complete"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Review the automation documentation in .github/AUTOMATION.md"
echo "2. Test workflows manually: gh workflow run <workflow-name>"
echo "3. Monitor the Actions tab after pushing changes"
echo ""
echo "For troubleshooting, check the workflow logs in the GitHub Actions tab."
