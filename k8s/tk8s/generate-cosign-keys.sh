#!/bin/bash
set -euo pipefail

# Cosign Key Generation Script for TK8S
# Generates signing keys and updates Kyverno policy

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           TK8S Cosign Key Generation Script                          ║${NC}"
echo -e "${BLUE}║    Generate signing keys for image verification                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Directory to store keys (in .gitignore)
KEY_DIR="$(pwd)/.cosign-keys"
PRIVATE_KEY="${KEY_DIR}/cosign.key"
PUBLIC_KEY="${KEY_DIR}/cosign.pub"
KYVERNO_POLICY="$(pwd)/security/kyverno-policies.yaml"

# Check if cosign is installed
if ! command -v cosign &> /dev/null; then
    echo -e "${RED}❌ Cosign not found. Please run install-prerequisites.sh first.${NC}"
    exit 1
fi

# Create key directory
mkdir -p "${KEY_DIR}"

# Check if keys already exist
if [ -f "${PRIVATE_KEY}" ] && [ -f "${PUBLIC_KEY}" ]; then
    echo -e "${YELLOW}⚠️  Cosign keys already exist in ${KEY_DIR}${NC}"
    read -p "Do you want to regenerate them? (yes/no): " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        echo "Using existing keys."
        echo ""
    else
        echo "Regenerating keys..."
        rm -f "${PRIVATE_KEY}" "${PUBLIC_KEY}"
    fi
fi

# Generate keys if they don't exist
if [ ! -f "${PRIVATE_KEY}" ] || [ ! -f "${PUBLIC_KEY}" ]; then
    echo -e "${BLUE}🔐 Generating Cosign key pair...${NC}"
    echo ""
    echo "You will be prompted to set a password for the private key."
    echo "IMPORTANT: Remember this password - you'll need it for signing images."
    echo ""
    
    # Generate keys in the key directory
    cd "${KEY_DIR}"
    cosign generate-key-pair
    cd - > /dev/null
    
    echo ""
    echo -e "${GREEN}✅ Keys generated successfully${NC}"
    echo "  Private key: ${PRIVATE_KEY}"
    echo "  Public key: ${PUBLIC_KEY}"
    echo ""
fi

# Display public key
echo -e "${BLUE}📝 Public Key:${NC}"
echo "────────────────────────────────────────────────────────────────────"
cat "${PUBLIC_KEY}"
echo "────────────────────────────────────────────────────────────────────"
echo ""

# Check if Kyverno policy exists
if [ ! -f "${KYVERNO_POLICY}" ]; then
    echo -e "${YELLOW}⚠️  Kyverno policy file not found at: ${KYVERNO_POLICY}${NC}"
    echo "   Please ensure you're running this script from the k8s/tk8s directory."
    exit 1
fi

# Update Kyverno policy with public key
echo -e "${BLUE}🔧 Updating Kyverno policy with public key...${NC}"

# Create backup of policy file
cp "${KYVERNO_POLICY}" "${KYVERNO_POLICY}.backup"

# Read the public key
PUBLIC_KEY_CONTENT=$(cat "${PUBLIC_KEY}")

# Create temporary file with updated policy
python3 << EOF
import yaml
import sys

# Read the policy file
with open("${KYVERNO_POLICY}", 'r') as f:
    content = f.read()

# Replace the placeholder
public_key = """${PUBLIC_KEY_CONTENT}"""

# Find and replace the TODO section
import re
pattern = r'(publicKeys: \|-\s+-----BEGIN PUBLIC KEY-----\s+)# TODO: Replace with actual Cosign public key(\s+-----END PUBLIC KEY-----)'
replacement = r'\1' + public_key.strip().replace('-----BEGIN PUBLIC KEY-----', '').replace('-----END PUBLIC KEY-----', '').strip() + r'\2'

if '# TODO: Replace with actual Cosign public key' in content:
    # Replace the TODO line with actual key content
    lines = content.split('\n')
    new_lines = []
    skip_until_end = False
    
    for i, line in enumerate(lines):
        if '# TODO: Replace with actual Cosign public key' in line:
            # Add the public key content (indented properly)
            indent = ' ' * 14  # Match the YAML indentation
            key_lines = public_key.strip().split('\n')
            for key_line in key_lines:
                if '-----BEGIN PUBLIC KEY-----' not in key_line and '-----END PUBLIC KEY-----' not in key_line:
                    new_lines.append(indent + key_line.strip())
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    with open("${KYVERNO_POLICY}", 'w') as f:
        f.write(content)
    
    print("✅ Policy updated successfully")
    sys.exit(0)
else:
    print("⚠️  Placeholder not found or already replaced")
    sys.exit(0)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Kyverno policy updated with public key${NC}"
    echo "   Backup saved to: ${KYVERNO_POLICY}.backup"
else
    echo -e "${RED}❌ Failed to update Kyverno policy${NC}"
    mv "${KYVERNO_POLICY}.backup" "${KYVERNO_POLICY}"
    exit 1
fi

echo ""

# Instructions for GitHub Secrets
echo -e "${BLUE}📝 GitHub Secrets Configuration:${NC}"
echo ""
echo "Add the following secrets to your GitHub repository:"
echo "  Settings > Secrets and variables > Actions > New repository secret"
echo ""
echo "1. COSIGN_PRIVATE_KEY"
echo "   Value: (paste the entire contents of ${PRIVATE_KEY})"
echo ""
echo "2. COSIGN_PASSWORD"
echo "   Value: (the password you set during key generation)"
echo ""
echo "To view the private key:"
echo "  cat ${PRIVATE_KEY}"
echo ""

# Security warnings
echo -e "${YELLOW}⚠️  SECURITY WARNINGS:${NC}"
echo "  1. NEVER commit the private key (cosign.key) to Git"
echo "  2. The .cosign-keys directory is in .gitignore"
echo "  3. Store the private key securely (e.g., password manager)"
echo "  4. Rotate keys periodically (recommended: every 90 days)"
echo "  5. Backup the private key in a secure location"
echo ""

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Key Generation Complete!                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Next steps:"
echo "  1. Add secrets to GitHub repository (see instructions above)"
echo "  2. Deploy TK8S: ./deploy-tk8s.sh"
echo "  3. Validate: python validate_tk8s.py"
echo ""
