<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `codeql-custom-queries-python/` — CodeQL Custom Queries

> **Custom CodeQL security queries for Python code analysis.** These queries extend GitHub's default CodeQL analysis with Project-AI-specific security checks.

## Usage

These queries are automatically picked up by the CodeQL GitHub Action defined in `.github/workflows/`. They scan for:

- Improper audit logging
- FourLaws bypass attempts
- Policy enforcement gaps
- Constitutional invariant violations
- Cerberus perimeter weaknesses
