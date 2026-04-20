---
name: quality-gate
description: 'Run lint, type, test, and security checks for changed files. Use for pre-PR validation and release hardening.'
argument-hint: 'Optional scope such as python, javascript, or full'
user-invocable: true
---

# Quality Gate Skill

## When To Use
- Before opening a pull request.
- After touching multiple languages in this monorepo.
- When you need a repeatable quality and security check workflow.

## Procedure
1. Run [quality-gate script](./scripts/run-quality-gate.sh).
2. Capture failures and map them to changed files.
3. Apply focused fixes and rerun only relevant checks.
4. Summarize residual risks and skipped checks.

## Notes
- Prefer repository task wrappers over ad-hoc commands.
- Keep remediation changes small and scoped to detected issues.
