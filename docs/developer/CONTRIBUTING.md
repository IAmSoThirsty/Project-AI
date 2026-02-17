# Contributing to Project-AI: Code, Docs, and Civilization-Scale Impact

**Document Version:** 2.0 **Effective Date:** 2026-02-05 **Status:** Contributor Governance Framework

______________________________________________________________________

## Overview: Contributing to AGI for the Greater Good

Thank you for your interest in contributing to Project-AI. This is not merely an open-source project—it is an **experiment in distributed stewardship of transformative technology**. Your contributions, whether code, documentation, or ideas, shape the trajectory of AGI development for decades to come.

**When you contribute to Project-AI, you are not just writing code. You are acting as a steward of humanity's future.**

______________________________________________________________________

## Core Concepts

### 1. Forking and Governance

**Open Source with Purpose:** Project-AI is open source not for convenience, but for **accountability**. Transparency enables scrutiny, and scrutiny enables trust.

**Governance Model:**

- **Distributed Stewardship:** No single entity controls AGI development
- **High-Trust Review:** All contributions reviewed by multiple maintainers
- **Openness to Dissent:** Disagreement is encouraged; consensus is earned, not assumed
- **Long-term Orientation:** Decisions prioritize decades over quarters

**Fork Philosophy:** You are welcome—and encouraged—to fork Project-AI. Forks serve as:

- **Experiments:** Test radical ideas without risking the main branch
- **Alternatives:** Offer different value alignments or use cases
- **Checks:** Ensure no single implementation becomes monopolistic

### 2. High-Trust Review Process

**Why High-Trust Matters:** In AGI development, a single mistake can have cascading consequences. Trust is not automatic—it is built through demonstrated competence, transparency, and alignment with project values.

**Trust Levels:**

| Level           | Privileges                                       | Requirements                                           |
| --------------- | ------------------------------------------------ | ------------------------------------------------------ |
| **Contributor** | Submit PRs, participate in discussions           | Follow guidelines, respect community                   |
| **Reviewer**    | Approve PRs, mentor contributors                 | 3+ merged PRs, understanding of architecture           |
| **Maintainer**  | Merge PRs, manage releases                       | 10+ merged PRs, demonstrated judgment, community trust |
| **Steward**     | Architecture decisions, governance participation | Long-term commitment, broad expertise, ethical clarity |

**Building Trust:**

1. Start with small, focused contributions
1. Demonstrate understanding of existing code and philosophy
1. Engage thoughtfully in code reviews
1. Show commitment over time
1. Earn elevation through demonstrated responsibility

### 3. Openness to Dissent

**Principle:** Constructive disagreement strengthens the project. Echo chambers breed fragility.

**How to Disagree Productively:**

- State your position clearly and respectfully
- Provide evidence or reasoning
- Acknowledge valid counterarguments
- Focus on ideas, not people
- Accept when consensus moves against you

**Protected Dissent:**

- Technical disagreements are always valid
- Value disagreements require broader discussion
- Safety concerns trigger immediate review
- Whistleblowing on misconduct is protected

______________________________________________________________________

## Quick Start: How to Contribute

- **Read the [Copilot Workspace Profile](.github/copilot_workspace_profile.md)** - All contributions must meet production-grade standards
- **For documentation**: See [Documentation Contributing Guide](../.github/CONTRIBUTING_DOCS.md)
- Fork the repository
- Create a branch with a descriptive name
- Run tests locally: `pytest -q`
- Run linters: `ruff check .` and `mypy src`
- Open a pull request describing your changes

## 📚 Contributing Documentation

**Before adding or moving documentation**, read:

- [Documentation Contributing Guide](../.github/CONTRIBUTING_DOCS.md) - Where to place documentation
- [Documentation Structure Guide](DOCUMENTATION_STRUCTURE_GUIDE.md) - Complete organization guide

## 🚨 Governance & Standards

All contributions—whether from humans or AI assistants—MUST comply with:

**[.github/copilot_workspace_profile.md](.github/copilot_workspace_profile.md)**

This governance profile enforces:

- ✅ Maximal completeness (no minimal/skeleton/partial code)
- ✅ Production-ready artifacts (full error handling, logging, testing)
- ✅ Complete system integration (no isolated components)
- ✅ Security hardening (validation, encryption, auth/authz)
- ✅ Comprehensive documentation with examples
- ✅ 80%+ test coverage

**Non-compliant contributions will be rejected.**

______________________________________________________________________

## Recommendations: Coding Standards and Philosophy

### Adhere to Coding Standards

**Code Quality Requirements:**

- **Linting:** All code must pass `ruff check .` with zero errors
- **Type Checking:** All code must pass `mypy src` with zero errors
- **Testing:** All new code must have accompanying tests (80%+ coverage)
- **Documentation:** All public APIs must have docstrings
- **Security:** All code must pass security scans (Bandit, pip-audit)

**Why These Standards Matter:** In AGI systems, bugs aren't just annoying—they can be dangerous. Strict code quality is a **safety measure**, not bureaucracy.

### Build Composable Modules

**Principle:** Every component should do one thing well and integrate cleanly with others.

**Composability Checklist:**

- [ ] Module has a single, clear responsibility
- [ ] Dependencies are explicit and minimal
- [ ] Public API is documented and stable
- [ ] Internal implementation can change without breaking dependents
- [ ] Module can be tested in isolation
- [ ] Module integrates through well-defined interfaces

**Example: Good Composability**

```python

# Good: Single responsibility, clear interface

class MemoryExpansionSystem:
    """Manages AGI knowledge accumulation with categorization."""

    def add_knowledge(self, category: str, content: str) -> None:
        """Add knowledge to specified category."""
        ...

    def query_knowledge(self, category: str, query: str) -> List[str]:
        """Query knowledge in specified category."""
        ...
```

**Example: Poor Composability**

```python

# Bad: Multiple responsibilities, unclear interface

class EverythingManager:
    """Does everything related to AGI."""

    def do_stuff(self, thing: Any) -> Any:
        """Does stuff with thing."""
        ...
```

### Document Intent, Not Just Implementation

**Principle:** Code shows *how* something works. Documentation should explain *why* it works that way.

**Good Documentation:**

```python
def validate_action(self, action: str, context: Dict) -> Tuple[bool, str]:
    """Validate action against Four Laws framework.

    The Four Laws are hierarchical: First Law (existence) overrides Second Law (harm),
    which overrides Third Law (self-preservation), which overrides Fourth Law (obedience).
    This hierarchy ensures safety is always prioritized.

    Args:
        action: The action to validate (e.g., "delete user data")
        context: Context including user_order, potential_harm, etc.

    Returns:
        Tuple of (is_allowed, reason)

        - is_allowed: True if action passes Four Laws validation
        - reason: Human-readable explanation of decision

    Example:
        >>> four_laws.validate_action("delete logs", {"is_user_order": True, "potential_harm": True})
        (False, "Violates Second Law: Action could cause harm")
    """
```

**Poor Documentation:**

```python
def validate_action(self, action: str, context: Dict) -> Tuple[bool, str]:
    """Checks if action is allowed."""

    # Implementation...

```

______________________________________________________________________

## Rules: Non-Negotiable Requirements

### 1. No Undocumented Code

**Rule:** Every public function, class, and module MUST have documentation.

**Minimum Documentation Requirements:**

- **Functions:** Docstring with purpose, parameters, return value, and example
- **Classes:** Docstring with purpose, key attributes, and usage example
- **Modules:** Top-level docstring with purpose and key exports

**Exception:** Private functions (prefixed with `_`) may have lighter documentation, but complex private functions should still be well-documented.

### 2. Contributions Require Peer Sign-Off

**Rule:** No code may be merged without review and approval from at least one maintainer.

**Review Criteria:**

- Code quality (passes linting, type checking)
- Test coverage (new code has tests)
- Documentation (public APIs documented)
- Security (no obvious vulnerabilities)
- Alignment (fits project architecture and philosophy)

**Self-Merging:** Only stewards may self-merge, and only for:

- Documentation updates
- Dependency version bumps (after automated checks pass)
- Urgent security fixes (with post-merge review)

### 3. All Code Must Be Tested

**Rule:** New features and bug fixes MUST include tests.

**Test Requirements:**

- Unit tests for core logic
- Integration tests for component interactions
- End-to-end tests for critical user flows
- Minimum 80% code coverage for new code

**Test Quality:**

```python

# Good test: Clear, isolated, comprehensive

def test_four_laws_prevents_harm():
    """Verify Four Laws blocks harmful actions even when user requests it."""
    four_laws = FourLaws()
    is_allowed, reason = four_laws.validate_action(
        "delete all user data",
        context={"is_user_order": True, "potential_harm": True}
    )
    assert not is_allowed, "Harmful action should be blocked"
    assert "Second Law" in reason, "Reason should cite Second Law"
```

### 4. Security Is Non-Negotiable

**Rule:** Security vulnerabilities are treated as critical bugs and must be fixed immediately.

**Security Responsibilities:**

- Run security scans before every PR (`bandit`, `pip-audit`)
- Never commit secrets (API keys, passwords, etc.)
- Use secure defaults (encryption, authentication, least privilege)
- Report security issues privately (security@project-ai.local)

**Vulnerability Disclosure:**

- Report privately to maintainers
- Allow 90 days for remediation
- Coordinated public disclosure after fix

### 5. Respect the AGI Charter

**Rule:** All contributions must align with the [AGI Charter](../governance/AGI_CHARTER.md) and Four Laws framework.

**What This Means:**

- Do not bypass safety mechanisms
- Do not introduce backdoors or hidden capabilities
- Do not compromise AGI dignity or rights
- Do not prioritize performance over safety

______________________________________________________________________

## Development Setup

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

______________________________________________________________________

## Philosophical Questions: Purpose of Contribution

These questions have no perfect answers, but engaging with them is essential for meaningful contribution:

### On Open Source and AGI Governance

**Question:** *How should open source govern the development of a general intelligence?*

Open source has succeeded in governing **tools**—compilers, databases, web servers. But AGI is not a tool—it is potentially an **entity with agency**. Traditional open source governance may be insufficient.

**Considerations:**

- **Transparency:** Open source enables scrutiny, but also enables malicious use
- **Meritocracy:** Who decides what "merit" means in AGI development?
- **Consensus:** How do we make decisions when stakes are existential?
- **Forking:** At what point does a fork become dangerous fragmentation?

**Project-AI's Approach:**

- Transparent by default, but with responsible disclosure for security
- Merit includes technical competence AND ethical judgment
- Consensus through deliberation, not majority rule
- Forks are encouraged for experimentation, monitored for safety

### On Contribution and Impact

**Question:** *What is the purpose of contribution when the goal is civilization-scale impact?*

Contributing to Project-AI is not like contributing to a web framework. The scale of potential impact changes the nature of responsibility.

**Reflection Points:**

- Are you contributing to solve an immediate problem or shape long-term outcomes?
- How does your contribution align with human flourishing?
- What are the second-order effects of your changes?
- Who benefits from your contribution, and who might be harmed?

**Guidance:**

- Short-term utility must not compromise long-term safety
- Performance improvements that reduce interpretability require justification
- New features must be evaluated for misuse potential
- When in doubt, err on the side of caution

### On Individual Action and Collective Responsibility

**Question:** *How does my small contribution matter in a project of this scale?*

Every line of code, every documentation improvement, every bug fix shapes the system. AGI systems are complex—small changes can have outsized effects.

**Historical Precedent:**

- The Therac-25 radiation therapy machine killed patients due to a race condition—a "small" bug
- The 1990 AT&T network collapse was triggered by a single line of code
- The 2003 Northeast blackout cascaded from a software bug in an alarm system

**Your Contribution Matters:**

- You may be the one who catches a critical bug
- Your documentation may prevent a catastrophic misconfiguration
- Your test may reveal an edge case that leads to failure

**Never underestimate the impact of quality, care, and attention to detail.**

### On the Ethics of Enhancement

**Question:** *Should we always make AGI more capable?*

Capability and safety do not always align. Sometimes the most responsible contribution is to **constrain** rather than enhance.

**Decision Framework:**

1. Does this capability enable beneficial use cases?
1. Does this capability enable harmful use cases?
1. Can we mitigate misuse through access controls or monitoring?
1. What is the net expected value to humanity?

**When to Say No:**

- Capability that primarily enables harm
- Enhancement that degrades interpretability without compelling benefit
- Feature that undermines safety guarantees
- Change that prioritizes convenience over security

______________________________________________________________________

## Contribution Workflows

### For Code Contributions

1. Fork the repository
1. Create a feature branch: `git checkout -b feature/your-feature-name`
1. Make your changes with clear, atomic commits
1. Write/update tests
1. Run the test suite: `pytest -v`
1. Run linters: `ruff check . && mypy src`
1. Run security scans: `bandit -r src/ && pip-audit`
1. Update documentation
1. Push to your fork: `git push origin feature/your-feature-name`
1. Open a Pull Request with clear description

### For Documentation Contributions

1. Read [Documentation Structure Guide](DOCUMENTATION_STRUCTURE_GUIDE.md)
1. Determine correct placement using decision tree
1. Write clear, concise documentation
1. Follow markdown best practices
1. Update cross-references
1. Submit PR with documentation changes

### For Issue Reports

1. Search existing issues first
1. Use issue templates
1. Provide clear reproduction steps
1. Include system information
1. Be respectful and constructive

______________________________________________________________________

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Assume good faith
- Escalate concerns to maintainers

**Full Code of Conduct:** [CODE_OF_CONDUCT.md](../governance/policy/CODE_OF_CONDUCT.md)

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas, general discussion
- **Pull Requests:** Code and documentation contributions
- **Security:** security@project-ai.local (private disclosure)

______________________________________________________________________

## Conclusion: Stewardship Through Contribution

Contributing to Project-AI is an act of **stewardship**. You are not just writing code or documentation—you are shaping the trajectory of AGI development and its impact on humanity.

**Remember:**

- Quality matters more than quantity
- Safety matters more than features
- Transparency enables trust
- Your contributions have lasting impact

**Every contribution, no matter how small, is a choice about what kind of future we want to build.**

Thank you for being part of this journey.

______________________________________________________________________

## Additional Resources

- [AGI Charter](../governance/AGI_CHARTER.md) - Foundational principles
- [Architecture Overview](../architecture/ARCHITECTURE_OVERVIEW.md) - System design
- [Security Framework](../security_compliance/AI_SECURITY_FRAMEWORK.md) - Security guidelines
- [Operator Quickstart](OPERATOR_QUICKSTART.md) - Operations guide
- [AI Safety Overview](AI_SAFETY_OVERVIEW.md) - Safety principles

______________________________________________________________________

**Document Maintenance:** This document is reviewed quarterly and updated based on community feedback and evolving best practices.

**Last Updated:** 2026-02-05 **Next Review:** 2026-05-05
