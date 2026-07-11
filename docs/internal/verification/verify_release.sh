#!/usr/bin/env bash
# Clean-clone verification of the TAAR E2E verification bundle.
#
# Two independent checks:
#   1. Internal seal + consistency  (Python 3 + PyYAML only)
#   2. Release signature over SEAL.json  (OpenSSH SSHSIG, if present)
#
# The signature covers SEAL.json; SEAL.json's head + per-file hashes cover
# every one of the 74 sealed bundle files (validated by verify_bundle.py).
# A valid signature + a passing verifier therefore proves the bytes are
# exactly those the maintainer signed.
#
# Exit 0 = all applicable checks pass.
# Set TAAR_REQUIRE_SIGNATURE=1 to fail when no release signature is present.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
bundle="$here/taar-e2e-2026-07-10"
seal="$bundle/SEAL.json"
sig="$here/signatures/taar-e2e-2026-07-10.SEAL.json.sig"
allowed="$here/allowed_signers"
namespace="taar-verification-bundle"

echo "== 1. bundle seal + internal consistency =="
python3 "$bundle/harness/verify_bundle.py" "$bundle"

echo
echo "== 2. release signature (SSHSIG over SEAL.json) =="
if [ -f "$sig" ] && [ -f "$allowed" ]; then
  # Verify against every principal listed in allowed_signers until one matches.
  ok=0
  while read -r principal _rest; do
    case "$principal" in ""|\#*) continue ;; esac
    if ssh-keygen -Y verify -f "$allowed" -I "$principal" \
        -n "$namespace" -s "$sig" < "$seal" >/dev/null 2>&1; then
      echo "PASS: SEAL.json signed by '$principal'"
      ok=1
      break
    fi
  done < "$allowed"
  if [ "$ok" -ne 1 ]; then
    echo "FAIL: signature present but did not verify against any listed signer" >&2
    exit 1
  fi
else
  echo "NOTE: no release signature present."
  echo "      ($sig)"
  echo "      Internal seal verified; provenance signature not yet anchored."
  if [ "${TAAR_REQUIRE_SIGNATURE:-0}" = "1" ]; then
    echo "FAIL: TAAR_REQUIRE_SIGNATURE=1 and no signature present" >&2
    exit 1
  fi
fi

echo
echo "VERIFICATION COMPLETE."
