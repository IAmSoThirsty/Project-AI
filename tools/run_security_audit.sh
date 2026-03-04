#                                           [2026-03-03 13:45]
#                                          Productivity: Active
#!/bin/bash
# Comprehensive security audit script for Project-AI
# Runs all available security scanners and generates reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORT_DIR="$PROJECT_ROOT/security-reports"

echo "🔐 Project-AI Security Audit"
echo "=============================="
echo ""

# Create report directory
mkdir -p "$REPORT_DIR"
echo "📁 Reports will be saved to: $REPORT_DIR"
echo ""

# Check if required tools are installed
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        echo "⚠️  $1 not found. Install with: pip install $2"
        return 1
    fi
    return 0
}

# Track scan results
SCAN_PASSED=0
SCAN_FAILED=0
SCAN_WARNINGS=0

# 1. Enhanced secret scanner
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  Running Enhanced Secret Scanner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python "$SCRIPT_DIR/enhanced_secret_scan.py" --report "$REPORT_DIR/enhanced-scan.json"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "✅ Enhanced scan: PASSED (no secrets found)"
    ((SCAN_PASSED++))
elif [ $RESULT -eq 1 ]; then
    echo "⚠️  Enhanced scan: WARNING (secrets found)"
    ((SCAN_WARNINGS++))
else
    echo "❌ Enhanced scan: FAILED (critical secrets found)"
    ((SCAN_FAILED++))
fi
echo ""

# 2. Bandit
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Running Bandit (Python Security Linter)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_tool "bandit" "bandit"; then
    bandit -r "$PROJECT_ROOT/src/" "$PROJECT_ROOT/tools/" "$PROJECT_ROOT/scripts/" \
        -f json -o "$REPORT_DIR/bandit-report.json" 2>&1 || true
    bandit -r "$PROJECT_ROOT/src/" "$PROJECT_ROOT/tools/" "$PROJECT_ROOT/scripts/" \
        -f txt 2>&1 | tee "$REPORT_DIR/bandit-report.txt" || true
    echo "✅ Bandit: Report generated"
    ((SCAN_PASSED++))
else
    echo "⚠️  Bandit: SKIPPED (not installed)"
    ((SCAN_WARNINGS++))
fi
echo ""

# 3. detect-secrets
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  Running detect-secrets"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_tool "detect-secrets" "detect-secrets"; then
    cd "$PROJECT_ROOT"
    detect-secrets scan --all-files --force-use-all-plugins \
        --exclude-files '\.lock$' \
        --exclude-files '\.pyc$' \
        --exclude-files 'node_modules/' \
        --exclude-files '\.git/' \
        > "$REPORT_DIR/secrets.baseline" || true
    
    if [ -s "$REPORT_DIR/secrets.baseline" ]; then
        echo "📊 Secrets baseline created: $REPORT_DIR/secrets.baseline"
        # Count findings
        FINDING_COUNT=$(grep -c '"is_secret": true' "$REPORT_DIR/secrets.baseline" || echo "0")
        if [ "$FINDING_COUNT" -gt 0 ]; then
            echo "⚠️  detect-secrets: Found $FINDING_COUNT potential secrets"
            ((SCAN_WARNINGS++))
        else
            echo "✅ detect-secrets: No secrets found"
            ((SCAN_PASSED++))
        fi
    else
        echo "✅ detect-secrets: No secrets found"
        ((SCAN_PASSED++))
    fi
else
    echo "⚠️  detect-secrets: SKIPPED (not installed)"
    ((SCAN_WARNINGS++))
fi
echo ""

# 4. TruffleHog (limited depth to avoid long scans)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Running TruffleHog (Git History Scanner)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_tool "trufflehog3" "truffleHog3"; then
    cd "$PROJECT_ROOT"
    trufflehog3 -v --max-depth 50 -r . > "$REPORT_DIR/trufflehog-report.txt" 2>&1 || true
    
    if [ -s "$REPORT_DIR/trufflehog-report.txt" ]; then
        FINDING_COUNT=$(grep -c "Reason:" "$REPORT_DIR/trufflehog-report.txt" || echo "0")
        if [ "$FINDING_COUNT" -gt 0 ]; then
            echo "⚠️  TruffleHog: Found $FINDING_COUNT potential secrets in git history"
            ((SCAN_WARNINGS++))
        else
            echo "✅ TruffleHog: No secrets found in git history"
            ((SCAN_PASSED++))
        fi
    else
        echo "✅ TruffleHog: No secrets found"
        ((SCAN_PASSED++))
    fi
else
    echo "⚠️  TruffleHog: SKIPPED (not installed)"
    ((SCAN_WARNINGS++))
fi
echo ""

# 5. pip-audit (dependency vulnerabilities)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  Running pip-audit (Dependency Vulnerabilities)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if check_tool "pip-audit" "pip-audit"; then
    pip-audit --desc --format json > "$REPORT_DIR/pip-audit.json" 2>&1 || true
    pip-audit --desc > "$REPORT_DIR/pip-audit.txt" 2>&1 || true
    
    VULN_COUNT=$(grep -c '"vulnerabilities"' "$REPORT_DIR/pip-audit.json" || echo "0")
    if [ "$VULN_COUNT" -gt 0 ]; then
        echo "⚠️  pip-audit: Found vulnerabilities in dependencies"
        ((SCAN_WARNINGS++))
    else
        echo "✅ pip-audit: No vulnerabilities found"
        ((SCAN_PASSED++))
    fi
else
    echo "⚠️  pip-audit: SKIPPED (not installed)"
    ((SCAN_WARNINGS++))
fi
echo ""

# Generate summary report
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Security Audit Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Results:"
echo "  ✅ Passed:   $SCAN_PASSED"
echo "  ⚠️  Warnings: $SCAN_WARNINGS"
echo "  ❌ Failed:   $SCAN_FAILED"
echo ""
echo "Reports saved to: $REPORT_DIR"
echo ""

# List generated reports
if [ -d "$REPORT_DIR" ]; then
    echo "Generated reports:"
    ls -lh "$REPORT_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'
    echo ""
fi

# Overall result
if [ $SCAN_FAILED -gt 0 ]; then
    echo "❌ Security audit FAILED - Critical issues found!"
    echo "   Review reports and rotate any exposed credentials immediately."
    exit 1
elif [ $SCAN_WARNINGS -gt 0 ]; then
    echo "⚠️  Security audit completed with WARNINGS"
    echo "   Review reports and address findings as needed."
    exit 0
else
    echo "✅ Security audit PASSED - No issues found!"
    exit 0
fi
