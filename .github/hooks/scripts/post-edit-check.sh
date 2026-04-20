#!/usr/bin/env bash
set -euo pipefail

# Keep hook behavior deterministic and fast. Avoid long-running checks here.
# This script is intentionally lightweight and non-blocking for unsupported setups.

if [[ -f package.json ]] && command -v npm >/dev/null 2>&1; then
  if npm run | grep -q "lint:markdown"; then
    npm run lint:markdown >/dev/null 2>&1 || true
  fi
fi

exit 0
