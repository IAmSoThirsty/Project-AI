# Contributing to Project-AI

Thank you for your interest. To contribute:

- Fork the repository.
- Create a branch with a descriptive name.
- Run tests locally: `pytest -q`.
- Run linters: `ruff check .` and `mypy src`.
- Open a pull request describing your changes.

Development setup:

```bash
python -m venv .venv
source .venv/bin/activate  # windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

## Windows Developers: Cygwin Installation (Optional but Recommended)

For Windows contributors, installing Cygwin provides unified GNU toolchain access and compatibility with Unix-based development workflows. This is **optional** but recommended for better development experience.

**Automated Installation (Headless)**:

```powershell
# Download Cygwin installer
Invoke-WebRequest -Uri https://www.cygwin.com/setup-x86_64.exe -OutFile setup-x86_64.exe

# Install with common development packages (silent mode)
.\setup-x86_64.exe --quiet-mode --no-shortcuts --no-desktop --no-startmenu `
  --site https://mirrors.kernel.org/sourceware/cygwin/ `
  --root C:\cygwin64 --packages git,make,gcc-core,python39,python39-pip
```

**Manual Installation**:

1. Download Cygwin installer from <https://www.cygwin.com/>
1. Run the installer and select the following packages:
   - `git` - Version control
   - `make` - Build automation
   - `gcc-core` - C compiler
   - `python39` - Python 3.9
   - `python39-pip` - Python package manager
   - `bash` - Unix shell
1. Add `C:\cygwin64\bin` to your system PATH

**Important Notes**:

- Non-Windows platforms (Linux, macOS) do not need Cygwin and should use native tools
- CI/CD workflows automatically detect the platform and use appropriate tools
- If you encounter issues with Cygwin, you can still develop using Windows native tools (Git Bash, PowerShell, WSL)

## CLI Development Guidelines

### Adding New CLI Commands

When adding new CLI commands or modifying existing ones:

1. **Follow the CLI-CODEX**: Review [CLI-CODEX.md](CLI-CODEX.md) for best practices
1. **Use Command Groups**: Organize commands into logical groups (user, memory, learning, plugin, system, ai)
1. **Add Tests**: Create tests in `tests/test_cli.py` using Typer's CliRunner
1. **Update Documentation**: Run `python scripts/generate_cli_docs.py` to update auto-generated docs
1. **Add Examples**: Include usage examples in `docs/cli/README.md`

### CLI Testing Checklist

Before submitting a PR with CLI changes:

- [ ] Run CLI tests: `pytest tests/test_cli.py -v`
- [ ] Test help output: `python -m app.cli [command] --help`
- [ ] Test with various inputs (valid, invalid, edge cases)
- [ ] Generate updated docs: `python scripts/generate_cli_docs.py`
- [ ] Update `CHANGELOG.md` with CLI changes
- [ ] Test shell completion (if modified)
- [ ] Test configuration file loading (if modified)

### CLI Code Style

- Use descriptive command and option names
- Provide clear help text for all commands and options
- Include docstrings for all command functions
- Use type hints for all parameters
- Handle errors gracefully with informative messages

### Example CLI Command

```python
@user_app.command()
def create(
    username: str = typer.Argument(..., help="Username to create."),
    email: str = typer.Option(..., "--email", "-e", help="User email address."),
    admin: bool = typer.Option(False, "--admin", help="Create as admin user."),
):
    """Create a new user account.
    
    This command creates a new user with the specified username and email.
    Optionally, the user can be created with admin privileges.
    """
    try:
        # Implementation here
        typer.echo(f"✓ Created user: {username}")
    except Exception as e:
        typer.echo(f"✗ Error: {e}", err=True)
        raise typer.Exit(1)
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
