#!/usr/bin/env bash
set -euo pipefail

echo "Installing developer tools..."
python -m pip install --upgrade pip
pip install pre-commit ruff black isort

echo "Installing pre-commit hooks..."
pre-commit install || true

echo "Developer tools installed. Run 'make precommit' to run hooks on all files or 'pre-commit run --all-files'." 
