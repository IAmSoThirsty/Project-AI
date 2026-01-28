# 🔐 Security Scanning Guide

This directory contains tools and configurations for scanning the Project-AI codebase for security vulnerabilities, hardcoded secrets, and compliance issues.

---

## 📋 Available Tools

### 1. Enhanced Secret Scanner

**File**: `tools/enhanced_secret_scan.py`

Comprehensive scanner that detects:

- API keys (OpenAI, AWS, Hugging Face, GitHub, Google, etc.)
- Passwords and authentication tokens
- Encryption keys (Fernet, JWT, RSA, SSH, PGP)
- Database connection strings
- Bearer tokens and OAuth secrets

**Usage:**
```bash
# Scan entire repository
python tools/enhanced_secret_scan.py

# Generate JSON report
python tools/enhanced_secret_scan.py --report scan-results.json

# Scan specific directory
python tools/enhanced_secret_scan.py --root src/
```

**Exit Codes:**

- `0` - No secrets found (success)
- `1` - Medium/High secrets found (warning)
- `2` - Critical secrets found (failure)

---

### 2. Bandit (Python Security Linter)

Scans Python code for common security issues like SQL injection, hardcoded passwords, insecure crypto usage.

**Installation:**
```bash
pip install bandit
```

**Usage:**
```bash
# Scan with default settings
bandit -r src/ tests/ tools/

# Generate JSON report
bandit -r src/ -f json -o bandit-report.json

# Scan with specific severity
bandit -r src/ --severity-level high

# Exclude test files
bandit -r src/ -x tests/
```

**Common Issues Detected:**

- B201: Flask app with debug=True
- B301: Pickle usage (insecure)
- B303: Insecure MD5/SHA1 usage
- B304: Insecure cipher modes
- B501: Request without SSL verification
- B506: YAML load without SafeLoader

---

### 3. detect-secrets

Prevents committing secrets by maintaining a baseline of known secrets.

**Installation:**
```bash
pip install detect-secrets
```

**Usage:**
```bash
# Create baseline of current secrets
detect-secrets scan > .secrets.baseline

# Audit baseline (review findings)
detect-secrets audit .secrets.baseline

# Scan for new secrets
detect-secrets scan --baseline .secrets.baseline
```

**Integration:**
```bash
# Add to pre-commit hook
detect-secrets-hook --baseline .secrets.baseline
```

---

### 4. TruffleHog

Scans git history for high-entropy strings and secrets.

**Installation:**
```bash
pip install truffleHog3
```

**Usage:**
```bash
# Scan entire git history
trufflehog3 -v -r https://github.com/IAmSoThirsty/Project-AI

# Scan specific branch
trufflehog3 -v -r . --branch main

# Only show verified secrets
trufflehog3 -r . --only-verified
```

---

### 5. git-secrets

Prevents committing secrets to git repositories.

**Installation:**
```bash
# macOS
brew install git-secrets

# Linux
git clone https://github.com/awslabs/git-secrets
cd git-secrets
sudo make install
```

**Setup:**
```bash
# Install hooks in repository
git secrets --install

# Register AWS patterns
git secrets --register-aws

# Add custom patterns
git secrets --add 'sk-[a-zA-Z0-9]{32,}'  # OpenAI keys
git secrets --add 'hf_[a-zA-Z0-9]{32,}'  # Hugging Face tokens

# Scan repository
git secrets --scan
```

---

## 🔄 Automated Scanning

### GitHub Actions

The repository includes automated secret scanning via GitHub Actions.

**Workflow**: `.github/workflows/security-secret-scan.yml`

**Triggers:**

- Push to main/develop branches
- Pull requests
- Daily at 2 AM UTC
- Manual dispatch

**Scans Performed:**

1. Bandit (Python security)
1. detect-secrets (baseline checking)
1. TruffleHog (git history)
1. Enhanced secret scanner (comprehensive)

**Artifacts:**

- `bandit-report.json` - Bandit findings
- `.secrets.baseline` - detect-secrets baseline
- `enhanced-scan-report.json` - Detailed scan results

---

### Pre-commit Hooks

Install pre-commit hooks to prevent committing secrets.

**Setup:**
```bash
# Install pre-commit
pip install pre-commit

# Copy example configuration
cp .pre-commit-config.yaml.example .pre-commit-config.yaml

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Configured Hooks:**

- `detect-secrets` - Prevent secret commits
- `bandit` - Python security checks
- `git-secrets` - AWS/API key detection
- `check-added-large-files` - Prevent large file commits
- `detect-private-key` - Find private keys
- `ruff` - Python linting

---

## 📊 Running Full Security Audit

**Comprehensive security scan:**

```bash
#!/bin/bash
# Run all security scanners

echo "🔍 Starting comprehensive security scan..."

# 1. Enhanced secret scanner
echo "1️⃣ Running enhanced secret scanner..."
python tools/enhanced_secret_scan.py --report enhanced-scan.json

# 2. Bandit
echo "2️⃣ Running Bandit..."
bandit -r src/ tools/ scripts/ -f json -o bandit-report.json

# 3. detect-secrets
echo "3️⃣ Running detect-secrets..."
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline

# 4. TruffleHog (on recent commits)
echo "4️⃣ Running TruffleHog..."
trufflehog3 -v -r . --max-depth 50

# 5. pip-audit (dependency vulnerabilities)
echo "5️⃣ Running pip-audit..."
pip-audit --desc

# 6. Safety (dependency vulnerabilities)
echo "6️⃣ Running Safety..."
safety check --json

echo "✅ Security scan complete!"
echo "📄 Reports generated:"
echo "  - enhanced-scan.json"
echo "  - bandit-report.json"
echo "  - .secrets.baseline"
```

**Save as**: `tools/run_security_audit.sh`

**Run:**
```bash
chmod +x tools/run_security_audit.sh
./tools/run_security_audit.sh
```

---

## 🚨 If Secrets Are Found

### Immediate Actions

1. **DO NOT COMMIT** - Cancel the commit immediately
1. **Review findings** - Determine if they are real secrets or false positives
1. **Remove secrets** - Replace with environment variables
1. **Rotate credentials** - If secret was previously committed, rotate immediately

### For Real Secrets

```bash
# 1. Remove secret from code
#    Replace with: os.getenv("SECRET_NAME")

# 2. Add to .env file (not committed)
echo "SECRET_NAME=actual_secret_value" >> .env

# 3. Add to .env.example (committed)
echo "SECRET_NAME=your_secret_here" >> .env.example

# 4. If already committed to git history
# Windows PowerShell:
.\tools\purge_git_secrets.ps1

# Linux/macOS/WSL:
./tools/purge_git_secrets.sh

# See docs/security/SECRET_MANAGEMENT.md for complete instructions

# 5. Rotate the credential
#    See credential-specific rotation instructions in SECRET_MANAGEMENT.md
```

### For False Positives

**Option 1: Allowlist the file**

Edit `tools/enhanced_secret_scan.py`:
```python
ALLOWED_FILES = [
    "your_file.py",  # Reason: Contains test data, not real secrets
]
```

**Option 2: Update baseline**

For detect-secrets:
```bash
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
# Mark false positives as "no" in audit
```

**Option 3: Add inline comment**

For Bandit:
```python
# nosec B105 - This is test data, not a real secret
password = "test_password_for_unit_tests"
```

---

## 📈 Best Practices

### During Development

1. **Scan before committing**

   ```bash
   python tools/enhanced_secret_scan.py
   ```

1. **Use pre-commit hooks**

   ```bash
   pre-commit run --all-files
   ```

1. **Review scan results**
   - Don't ignore warnings
   - Fix or document each finding

### In Code Reviews

1. **Check for secrets** - Even if scanner missed them
1. **Verify environment variables** - All secrets use `os.getenv()`
1. **Review .env.example** - Updated with new secrets (placeholders only)
1. **Check documentation** - No real credentials in docs

### In CI/CD

1. **Automated scanning** - Every PR and commit
1. **Fail on critical** - Block merges with critical secrets
1. **Report findings** - Make visible to team
1. **Rotate on exposure** - Immediate rotation procedures

---

## 📋 Scan Frequency

| Scan Type | Frequency | Trigger |
|-----------|-----------|---------|
| Pre-commit hooks | Every commit | Developer local |
| Enhanced scanner | Every PR | GitHub Actions |
| Bandit | Every PR | GitHub Actions |
| TruffleHog | Daily | GitHub Actions |
| Full audit | Weekly | Manual |
| Dependency scan | Weekly | GitHub Actions |

---

## 🔧 Configuration

### Bandit Configuration

File: `pyproject.toml`

```toml
[tool.bandit]
exclude_dirs = ["tests/", ".venv/", "venv/"]
skips = ["B101"]  # Skip assert_used in tests

[tool.bandit.assert_used]
skips = ["*/test_*.py", "test_*.py"]
```

### detect-secrets Configuration

File: `.secrets.baseline`

Generated with:
```bash
detect-secrets scan --all-files --force-use-all-plugins > .secrets.baseline
```

Update baseline:
```bash
detect-secrets scan --baseline .secrets.baseline
```

### Enhanced Scanner Configuration

File: `tools/enhanced_secret_scan.py`

Customize:

- `PATTERNS` - Add/modify detection patterns
- `EXCLUDE_PATTERNS` - Exclude files/directories
- `ALLOWED_FILES` - Allow specific files
- `DOCUMENTATION_DIRS` - Lenient checking for docs

---

## 📞 Support

**Questions?**

- Read: `docs/security/SECRET_MANAGEMENT.md`
- Issues: GitHub Issues with `security` label
- Urgent: Contact security team immediately

**Resources:**

- [OWASP Top 10](https://owasp.org/Top10/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [AWS Secrets Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)

---

**Remember**: Security is everyone's responsibility. When in doubt, scan it out! 🔐
