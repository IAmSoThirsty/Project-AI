#!/usr/bin/env bash
# (Substrate Docker Execution Vector)       [2026-04-09 04:12]
#                                          Status: Active
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
export QT_API="${QT_API:-pyqt6}"

if [[ "${HEADLESS_MODE:-0}" == "1" || "${HEADLESS_MODE:-0}" == "true" ]]; then
  exec python -m src.app.main_headless_wrapper
fi

exec python -m src.app.main
