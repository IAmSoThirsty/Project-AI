#!/bin/bash
# Thirsty-lang GitHub Linguist Submission Script
# Automates the submission process to github/linguist repository

set -e  # Exit on error

LINGUIST_REPO="$1"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# Print header
echo "======================================================================"
echo "  Thirsty-lang GitHub Linguist Submission Tool"
echo "======================================================================"
echo ""

# Check if linguist repository path provided
if [ -z "$LINGUIST_REPO" ]; then
    print_error "Usage: $0 /path/to/linguist"
    print_info "Please provide the path to your forked linguist repository"
    echo ""
    echo "Example:"
    echo "  $0 ~/github/linguist"
    echo ""
    exit 1
fi

# Check if linguist repository exists
if [ ! -d "$LINGUIST_REPO" ]; then
    print_error "Linguist repository not found at: $LINGUIST_REPO"
    print_info "Please fork and clone https://github.com/github/linguist first"
    exit 1
fi

# Get submission directory
SUBMISSION_DIR="$(cd "$(dirname "$0")" && pwd)"
print_info "Submission package: $SUBMISSION_DIR"
print_info "Target repository: $LINGUIST_REPO"
echo ""

# Step 1: Add language definition
print_info "Step 1: Adding language definition to languages.yml..."

if [ ! -f "$LINGUIST_REPO/lib/linguist/languages.yml" ]; then
    print_error "languages.yml not found in linguist repository"
    exit 1
fi

# Append to languages.yml (user should review and place correctly)
echo "" >> "$LINGUIST_REPO/lib/linguist/languages.yml"
cat "$SUBMISSION_DIR/languages.yml" >> "$LINGUIST_REPO/lib/linguist/languages.yml"
print_success "Language definition added (please move to correct alphabetical position)"

# Step 2: Copy TextMate grammar
print_info "Step 2: Copying TextMate grammar..."

mkdir -p "$LINGUIST_REPO/vendor/grammars"
cp "$SUBMISSION_DIR/grammars/thirsty.tmLanguage.json" "$LINGUIST_REPO/vendor/grammars/thirsty.tmLanguage.json"
print_success "Grammar copied to vendor/grammars/"

# Step 3: Update grammars.yml
print_info "Step 3: Updating grammars.yml..."

if [ -f "$LINGUIST_REPO/grammars.yml" ]; then
    echo "vendor/grammars/thirsty.tmLanguage.json:" >> "$LINGUIST_REPO/grammars.yml"
    echo "  - source.thirsty" >> "$LINGUIST_REPO/grammars.yml"
    print_success "grammars.yml updated"
else
    print_warning "grammars.yml not found - you may need to add grammar reference manually"
fi

# Step 4: Copy sample files
print_info "Step 4: Copying sample files..."

mkdir -p "$LINGUIST_REPO/samples/Thirsty-lang"
cp "$SUBMISSION_DIR/samples"/*.thirsty* "$LINGUIST_REPO/samples/Thirsty-lang/"
SAMPLE_COUNT=$(ls "$LINGUIST_REPO/samples/Thirsty-lang" | wc -l)
print_success "Copied $SAMPLE_COUNT sample files"

# Summary
echo ""
echo "======================================================================"
echo "  Submission Package Installed"
echo "======================================================================"
echo ""
print_success "All files copied to linguist repository"
echo ""
print_info "Next steps:"
echo "  1. cd $LINGUIST_REPO"
echo "  2. Review and move language definition to correct position in languages.yml"
echo "  3. bundle install (if not already done)"
echo "  4. bundle exec rake test"
echo "  5. bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty"
echo "  6. git add -A"
echo "  7. git commit -m \"Add support for Thirsty-lang\""
echo "  8. git push origin add-thirsty-lang"
echo "  9. Create pull request on GitHub"
echo ""
print_info "Use the PR template in PR_TEMPLATE.md for your pull request description"
echo ""

# Optional: Run tests if in linguist directory
read -p "Run linguist tests now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running tests..."
    cd "$LINGUIST_REPO"
    
    if bundle exec rake test 2>&1 | tail -20; then
        print_success "Tests passed!"
    else
        print_warning "Some tests may have failed - review output above"
    fi
    
    print_info "Testing language detection..."
    bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty
fi

echo ""
print_success "Submission package ready! Good luck with your PR!"
echo ""
