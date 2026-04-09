#!/usr/bin/env bash
# [Run Headless]                            [2026-04-09 04:10]
#                                          Status: Active
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export HEADLESS_MODE=1
export QT_API="${QT_API:-pyqt6}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

exec python -m src.app.main_headless_wrapper
