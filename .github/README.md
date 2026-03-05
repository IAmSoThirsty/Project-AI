<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `.github/` — GitHub Configuration

> **CI/CD workflows, issue templates, PR templates, and GitHub-specific automation.**

## Contents

- **`workflows/`** — GitHub Actions CI/CD pipelines
- **`ISSUE_TEMPLATE/`** — Issue templates for bug reports, feature requests
- **`PULL_REQUEST_TEMPLATE/`** — PR templates with checklist
- **Security policies** — `SECURITY.md`, `CODEOWNERS`
- **Automation scripts** — Python helpers for GitHub API interactions

## Key Workflows

Workflows enforce the Iron Path on every commit:

1. Lint and format check
2. Unit test suite
3. Security scanning
4. Constitutional invariant verification
5. Build artifact generation
