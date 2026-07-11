#!/usr/bin/env bash
# Sign the TAAR E2E verification bundle with a SEPARATELY CONTROLLED release key.
#
# Run this on a machine you control, with a private key you generated and hold
# (never in this repo, never in CI). SSHSIG (OpenSSH >= 8.0) is used so no PKI
# or keyring is required.
#
#   Generate a release key once:
#     ssh-keygen -t ed25519 -f taar-release-key -C "release@your-identity"
#   Then publish taar-release-key.pub in allowed_signers (see SIGNING.md).
#
# Usage:
#     ./sign_release.sh <path-to-private-key>
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
key="${1:?usage: sign_release.sh <ssh_ed25519_private_key>}"
seal="$here/taar-e2e-2026-07-10/SEAL.json"
namespace="taar-verification-bundle"
dest="$here/signatures/taar-e2e-2026-07-10.SEAL.json.sig"

mkdir -p "$here/signatures"
# ssh-keygen writes "<file>.sig" next to the target; move it OUT of the sealed
# directory so the bundle SEAL stays valid.
ssh-keygen -Y sign -f "$key" -n "$namespace" "$seal"
mv "$seal.sig" "$dest"

echo "signed -> ${dest#"$here"/}"
echo "fingerprint: $(ssh-keygen -lf "$key" | awk '{print $2}')"
echo "next: add your public key to allowed_signers, commit both, then run verify_release.sh"
