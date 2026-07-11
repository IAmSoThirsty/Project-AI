#!/usr/bin/env bash
# RFC 3161 time-anchoring for the bundle (anchors "these bytes existed by T").
#
# Step 1 (OFFLINE, safe): build a timestamp request from the SEAL.json hash.
#   Nothing leaves the machine; the request contains only a SHA-256 digest.
# Step 2 (OUTWARD-FACING, opt-in): POST the request to a Time Stamping Authority.
#   This publishes the digest to a third party and is permanent. It runs ONLY
#   when you set TAAR_SUBMIT_TS=1, so submission is always an explicit choice.
#
# Usage:
#     ./anchor_timestamp.sh                 # build request only
#     TAAR_SUBMIT_TS=1 ./anchor_timestamp.sh   # also submit to the TSA
#   Override the TSA:  TAAR_TSA_URL=https://freetsa.org/tsr
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
seal="$here/taar-e2e-2026-07-10/SEAL.json"
tsq="$here/signatures/taar-e2e-2026-07-10.SEAL.json.tsq"
tsr="$here/signatures/taar-e2e-2026-07-10.SEAL.json.tsr"
tsa="${TAAR_TSA_URL:-https://freetsa.org/tsr}"

mkdir -p "$here/signatures"

# 1. Offline request (digest only, no network).
openssl ts -query -data "$seal" -sha256 -cert -out "$tsq"
echo "request -> ${tsq#"$here"/}  (SHA-256 of SEAL.json, no network used)"

# 2. Opt-in submission.
if [ "${TAAR_SUBMIT_TS:-0}" = "1" ]; then
  echo "submitting to TSA: $tsa (outward-facing, permanent)"
  curl -sSf -H "Content-Type: application/timestamp-query" \
    --data-binary @"$tsq" "$tsa" -o "$tsr"
  echo "response -> ${tsr#"$here"/}"
  echo "verify later with: openssl ts -verify -in '$tsr' -queryfile '$tsq' \\"
  echo "                     -CAfile <tsa-ca.pem> -untrusted <tsa-cert.pem>"
else
  echo "submission skipped. Set TAAR_SUBMIT_TS=1 to POST to $tsa (your choice)."
fi
