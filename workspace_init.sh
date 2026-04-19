#!/usr/bin/env bash
# (Workspace Genesis Engine)                [2026-04-09 04:12]
#                                          Status: Active
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/app/workspace}"

mkdir -p "$WORKSPACE_ROOT/repositories"
mkdir -p "$WORKSPACE_ROOT/projects"
mkdir -p "$WORKSPACE_ROOT/notebooks"
mkdir -p "$WORKSPACE_ROOT/artifacts"

if [[ ! -d "$WORKSPACE_ROOT/.git" ]]; then
  git -C "$WORKSPACE_ROOT" init >/dev/null
fi

git -C "$WORKSPACE_ROOT" status --short || true
echo "WORKSPACE_READY:$WORKSPACE_ROOT"
