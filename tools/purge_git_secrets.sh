#!/bin/bash
# Git Secret Purge Script (Bash version of purge_git_secrets.ps1)
# Removes .env file from entire git history using git-filter-repo
#
# Usage: ./tools/purge_git_secrets.sh [--dry-run]

set -e

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
DRY_RUN=false

# Parse arguments
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
fi

echo "RepoRoot: $REPO_ROOT"
cd "$REPO_ROOT"

# Check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "ERROR: Required command '$1' not found on PATH. Install it and re-run."
        exit 1
    fi
}

check_command git

# Check for git-filter-repo
if ! command -v git-filter-repo &> /dev/null; then
    echo "ERROR: git-filter-repo not found. Install one of:"
    echo "  - pip install git-filter-repo"
    echo "  - brew install git-filter-repo (macOS)"
    echo "  - apt install git-filter-repo (Debian/Ubuntu)"
    echo "Then re-run this script."
    exit 2
fi

# Safety: require clean working tree
if [[ -n $(git status --porcelain) ]]; then
    echo "ERROR: Working tree not clean. Commit/stash changes first:"
    git status --short
    exit 3
fi

echo "Creating backup tag pre-purge..."
git tag -f pre-secret-purge

if [[ "$DRY_RUN" == "true" ]]; then
    echo "DRY RUN: would run git-filter-repo to remove .env history."
    exit 0
fi

echo "Rewriting history to remove .env from all commits..."
echo "⚠️  WARNING: This rewrites ALL branches/tags in the local clone."
# Remove the file from all history
# Note: this rewrites ALL branches/tags in the local clone.
git filter-repo --path .env --invert-paths --force

echo "Repacking repository..."
git reflog expire --expire=now --all
# Aggressive GC after rewrite
git gc --prune=now --aggressive

echo ""
echo "================================================================================"
echo "DONE. Next steps:"
echo "================================================================================"
echo ""
echo "  1) Force push:  git push --force --all origin"
echo "  2) Force push tags: git push --force --tags origin"
echo ""
echo "⚠️  CRITICAL: Rotate ALL exposed credentials IMMEDIATELY:"
echo ""
echo "3) ROTATE OPENAI_API_KEY:"
echo "   - Go to: https://platform.openai.com/api-keys"
echo "   - REVOKE the old key (search for exposed key prefix)"
echo "   - Create NEW API key with appropriate permissions"
echo "   - Update .env file with new key"
echo "   - Test application works with new key"
echo ""
echo "4) ROTATE SMTP/Email Credentials:"
echo "   - For Gmail: https://myaccount.google.com/apppasswords"
echo "   - REVOKE old app password"
echo "   - Generate NEW app password"
echo "   - Update SMTP_PASSWORD in .env"
echo "   - Consider changing SMTP_USERNAME if exposed"
echo ""
echo "5) ROTATE FERNET_KEY:"
echo "   - Generate new key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
echo "   - ⚠️  WARNING: Rotating Fernet key makes old encrypted data unreadable!"
echo "   - BEFORE rotating: Decrypt all existing data with old key"
echo "   - Update FERNET_KEY in .env with new key"
echo "   - Re-encrypt all data with new key"
echo ""
echo "6) ROTATE HUGGINGFACE_API_KEY (if exposed):"
echo "   - Go to: https://huggingface.co/settings/tokens"
echo "   - DELETE the old token"
echo "   - Create NEW token with appropriate permissions"
echo "   - Update HUGGINGFACE_API_KEY in .env"
echo ""
echo "7) ROTATE Command Override Password (if set):"
echo "   - Use command override UI to set NEW master password"
echo "   - Update COMMAND_OVERRIDE_PASSWORD in .env (if stored there)"
echo "   - Review command_override_audit.log for suspicious activity"
echo ""
echo "8) Verify rotation complete:"
echo "   - Test application with all new credentials"
echo "   - Check no old credentials remain in code/config"
echo "   - Run: python tools/enhanced_secret_scan.py"
echo "   - Document rotation date and next rotation due date"
echo ""
echo "9) Additional security measures:"
echo "   - Enable 2FA on all external accounts (OpenAI, Hugging Face, etc.)"
echo "   - Review access logs for unauthorized usage"
echo "   - Monitor API usage for anomalies"
echo "   - Set up billing alerts (prevent surprise charges)"
echo "   - Add pre-commit hooks to prevent future secret commits"
echo ""
echo "📋 Rotation Checklist:"
echo "  [ ] Git history purged and force-pushed"
echo "  [ ] OpenAI API key revoked and rotated"
echo "  [ ] SMTP credentials rotated"
echo "  [ ] Fernet key rotated (with data migration)"
echo "  [ ] Hugging Face token rotated (if applicable)"
echo "  [ ] Command override password changed"
echo "  [ ] Application tested with new credentials"
echo "  [ ] Secret scanning run (no findings)"
echo "  [ ] Team notified of credential rotation"
echo "  [ ] Documented rotation date and reason"
echo ""
echo "⏰ Set calendar reminder: Rotate credentials again in 90 days"
echo ""
echo "================================================================================"
