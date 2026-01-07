# Contributing to Project-AI

Thank you for your interest. To contribute:

- Fork the repository.
- Create a branch with a descriptive name.
- Run tests locally: `pytest -q`.
- Run linters: `ruff check .` and `mypy src`.
- Open a pull request describing your changes.

Development setup:

```
python -m venv .venv
source .venv/bin/activate  # windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Automated Workflows

This repository uses automated workflows to handle PRs and security alerts:

- **Pull requests** are automatically reviewed and tested
- **Dependabot PRs** for patch/minor updates are auto-merged after passing checks
- **Security scans** run daily and create issues for vulnerabilities
- **Code quality checks** run on every PR

For details, see [.github/AUTOMATION.md](.github/AUTOMATION.md).

### Working with Automation

- PRs from Dependabot are automatically reviewed and merged if safe
- Add `auto-merge` label to your PR to enable automatic merging (use with caution)
- Security issues are auto-created with `security` and `automated` labels
- Check workflow logs in the Actions tab if something goes wrong

### Local Security Scanning

Before pushing, run security checks locally:

```bash
# Bandit security scan
bandit -r src/ -f screen

# Dependency vulnerability check
pip-audit

# Alternative dependency check
safety check
```
