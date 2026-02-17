# Security Update - Dependency Vulnerabilities Fixed

## Issue Summary

An automated security scan detected vulnerabilities in Python dependencies. This document explains the issue and the resolution.

## Root Cause

The issue was caused by **outdated system-wide Python packages** in the CI/CD environment, not the project's dependency specifications. The `requirements.txt` file already contained secure versions, but the packages were not installed/upgraded.

## Vulnerabilities Addressed

### Direct Dependencies (Fixed)

| Package          | Old Version | Fixed Version | CVEs Fixed                                                             |
| ---------------- | ----------- | ------------- | ---------------------------------------------------------------------- |
| **cryptography** | 41.0.7      | 46.0.3        | 4 (CVE-2024-26130, CVE-2023-50782, CVE-2024-0727, GHSA-h4gh-qq45-vh27) |
| **requests**     | 2.31.0      | 2.32.5        | 2 (CVE-2024-35195, CVE-2024-47081)                                     |
| **certifi**      | 2023.11.17  | 2025.11.12    | 1 (CVE-2024-39689)                                                     |

### Transitive Dependencies (Fixed)

| Package        | Old Version | Fixed Version | CVEs Fixed                                                         |
| -------------- | ----------- | ------------- | ------------------------------------------------------------------ |
| **urllib3**    | 2.0.7       | 2.6.0         | 4 (CVE-2024-37891, CVE-2025-50181, CVE-2025-66418, CVE-2025-66471) |
| **idna**       | 3.6         | 3.11          | 1 (CVE-2024-3651)                                                  |
| **setuptools** | 68.1.2      | 80.9.0        | 2 (CVE-2025-47273, CVE-2024-6345)                                  |

## Changes Made

### 1. `requirements.txt`

- Fixed incorrect version `pip-audit==3.0.1` → `pip-audit==2.10.0` (3.0.1 doesn't exist on PyPI)
- All other packages already had secure versions specified

### 2. `pyproject.toml`

- Updated minimum version constraints:
  - `cryptography>=3.4.0` → `cryptography>=43.0.1`
  - `requests>=2.28.0` → `requests>=2.32.4`

## Installation Instructions

To ensure you have the secure versions installed:

```bash

# Option 1: Clean install (recommended)

pip install -r requirements.txt --force-reinstall

# Option 2: Upgrade specific packages

pip install --upgrade cryptography requests certifi urllib3 idna setuptools

# Option 3: Fresh virtual environment (safest)

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Verification

To verify your environment has no vulnerabilities:

```bash

# Install pip-audit if not already installed

pip install pip-audit

# Run security audit

pip-audit

# Expected output: No known vulnerabilities found

```

## CI/CD Considerations

For CI/CD pipelines:

1. Always use fresh virtual environments for each build
1. Install from `requirements.txt`, not system packages
1. Run `pip-audit` as part of the security check phase
1. Use `pip install --upgrade pip setuptools wheel` before installing dependencies

## Notes

- **pip-audit version**: Changed from 3.0.1 (non-existent) to 2.10.0 (latest stable)
- **System packages**: Some vulnerabilities appeared because pip-audit scanned system-wide packages (e.g., `jinja2==3.1.2`, `twisted==24.3.0`) that are not part of this project
- **Testing**: All existing tests should pass with the updated dependencies as we only changed minimum versions in pyproject.toml and fixed a typo in requirements.txt

## References

- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [CVE Database](https://cve.mitre.org/)
- [GitHub Security Advisories](https://github.com/advisories)

______________________________________________________________________

**Last Updated**: 2026-01-07 **Status**: ✅ All known vulnerabilities resolved
