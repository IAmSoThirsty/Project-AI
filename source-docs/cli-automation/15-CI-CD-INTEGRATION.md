---
title: CI/CD Integration
type: technical-guide
audience: [devops, developers]
classification: P1-Developer
tags: [ci-cd, github-actions, automation]
created: 2024-01-20
status: current
---

# CI/CD Integration

**Continuous Integration and Deployment workflows.**

## GitHub Actions Workflows

### CI Pipeline

File: .github/workflows/ci.yml

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Lint
        run: ruff check .
      - name: Test
        run: pytest -v --cov
```

### Security Scanning

Workflows:
- codeql.yml - CodeQL analysis
- andit.yml - Python security scanning
- uto-security-fixes.yml - Automated security patches

### Pull Request Automation

File: .github/workflows/auto-pr-handler.yml

Features:
- Auto-review for Dependabot PRs
- Run linting and tests
- Auto-approve passing PRs
- Auto-merge patch/minor updates

## Integration with Automation Scripts

```yaml
- name: Process documentation
  run: |
    .\scripts\automation\batch-process.ps1 \
      -Pipeline @('ValidateTags', 'AddMetadata') \
      -Path ".\docs"
```

---

**AGENT-038: CLI & Automation Documentation Specialist**
