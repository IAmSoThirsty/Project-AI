#!/usr/bin/env bash
# [Setup Native Linux Substrate]           [2026-04-03 19:30]
#                                          Status: Active
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p logs
mkdir -p output
mkdir -p tmp
mkdir -p data/genesis_pins
mkdir -p data/tsa_anchors
mkdir -p data/sovereign_audit
mkdir -p Claude
mkdir -p Codex

if [[ "${CREATE_VENV:-0}" == "1" && ! -d ".venv-linux" ]]; then
  python3 -m venv .venv-linux
fi

if [[ -d ".venv-linux/bin" ]]; then
  # shellcheck disable=SC1091
  source .venv-linux/bin/activate
fi

if [[ "${INSTALL_DEPS:-0}" == "1" ]]; then
  python3 -m pip install --upgrade pip
  if [[ -f requirements.txt ]]; then
    python3 -m pip install -r requirements.txt
  fi
  if [[ -f requirements-dev.txt ]]; then
    python3 -m pip install -r requirements-dev.txt
  fi
fi

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

python3 Verify-SovereignLoaders.py
python3 scripts/verify/verify_thirsty_interpreter.py
