#!/usr/bin/env bash
# Produce the deterministic release archive containing the exact sealed bundle,
# the verifier, and the signing/anchoring kit, straight from a git ref.
#
# `git archive` is reproducible for a given tree (no wall-clock mtimes), so the
# archive SHA-256 is stable for a given tag and independently recomputable.
#
# Usage:
#     ./build_release_archive.sh [git-ref] [output.tar.gz]
# Default ref: the tag taar-verify-2026-07-10 (fallback HEAD).
set -euo pipefail

ref="${1:-taar-verify-2026-07-10}"
out="${2:-taar-e2e-2026-07-10-release.tar.gz}"
repo_root="$(git rev-parse --show-toplevel)"

if ! git -C "$repo_root" rev-parse -q --verify "$ref" >/dev/null; then
  echo "ref '$ref' not found; falling back to HEAD" >&2
  ref="HEAD"
fi

git -C "$repo_root" archive --format=tar.gz \
  --prefix="taar-e2e-2026-07-10-release/" "$ref" \
  -- docs/internal/verification > "$out"

sha256sum "$out" | tee "$out.sha256"
echo "archive ref: $ref  ($(git -C "$repo_root" rev-parse "$ref"))"
echo "wrote $out (+ $out.sha256)"
