#!/usr/bin/env bash
set -euo pipefail

# Lightweight quality gate runner for common repo workflows.

if [[ -f package.json ]] && command -v npm >/dev/null 2>&1; then
  if npm run | grep -q "lint"; then
    npm run lint
  fi
fi

if [[ -f pyproject.toml ]] && command -v ruff >/dev/null 2>&1; then
  ruff check .
fi

if [[ -f pyproject.toml ]] && command -v pytest >/dev/null 2>&1; then
  pytest -q
fi
