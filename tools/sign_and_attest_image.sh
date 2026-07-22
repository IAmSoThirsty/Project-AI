#!/usr/bin/env bash
#
# Sign and attest one published container image, then prove the artifacts are
# independently retrievable from the registry before reporting success.
#
# Usage: sign_and_attest_image.sh <digest-pinned-reference> <spdx-sbom-file>
#
# Every step is digest-pinned. Tags are never signed, attested, or verified: a tag
# is a mutable pointer and can resolve to a manifest other than the one that was
# signed, which is exactly how a signature can appear valid for the wrong artifact.
#
# The postcondition block at the end is the point of this script. The 2026-07-20
# audit discrepancy happened because the pipeline treated a zero exit code from
# `cosign sign` as proof that a signature existed. It is not. Only reading the
# artifact back out of the registry proves that.
#
set -euo pipefail

REF="${1:?usage: sign_and_attest_image.sh <digest-pinned-reference> <spdx-sbom-file>}"
SBOM_FILE="${2:?usage: sign_and_attest_image.sh <digest-pinned-reference> <spdx-sbom-file>}"

# Refuse anything that is not digest-pinned.
if [[ ! "$REF" =~ @sha256:[0-9a-f]{64}$ ]]; then
  echo "::error::refusing to sign a reference that is not digest-pinned: ${REF}" >&2
  exit 1
fi

if [[ ! -s "$SBOM_FILE" ]]; then
  echo "::error::SBOM predicate ${SBOM_FILE} is missing or empty; refusing to attest nothing" >&2
  exit 1
fi

: "${COSIGN_IDENTITY_REGEXP:?COSIGN_IDENTITY_REGEXP must be set}"
: "${COSIGN_OIDC_ISSUER:?COSIGN_OIDC_ISSUER must be set}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "${WORKDIR}"' EXIT
PROVENANCE_RAW="${WORKDIR}/provenance.raw.json"
PROVENANCE="${WORKDIR}/provenance.slsa.json"

echo "==> signing ${REF}"
cosign sign --yes "$REF"

echo "==> attesting SPDX SBOM for ${REF}"
cosign attest --yes --type spdxjson --predicate "$SBOM_FILE" "$REF"

# BuildKit (provenance: mode=max) already produced a real SLSA predicate and stored it
# inside the image index as an in-toto layer. That storage is informational only -- no
# standard verifier reads it -- so the predicate is extracted here and re-attested through
# cosign, which does produce independently verifiable evidence.
echo "==> extracting BuildKit SLSA provenance for ${REF}"
docker buildx imagetools inspect "$REF" --format '{{ json .Provenance }}' > "$PROVENANCE_RAW"

# Fail closed if the shape is not what we expect. buildx has changed this structure
# between versions; a silent empty predicate would attest nothing while exiting 0.
if ! jq -e '
      if type != "object" then empty
      elif has("SLSA") then .SLSA
      else
        (to_entries
         | map(select(.value | type == "object" and has("SLSA")))
         | if length > 0 then .[0].value.SLSA else empty end)
      end
    ' "$PROVENANCE_RAW" > "$PROVENANCE"; then
  echo "::error::could not extract a SLSA provenance predicate from buildx output for ${REF}." >&2
  echo "::error::buildx --format '{{ json .Provenance }}' returned:" >&2
  head -c 2000 "$PROVENANCE_RAW" >&2 || true
  exit 1
fi

if [[ ! -s "$PROVENANCE" ]]; then
  echo "::error::extracted SLSA provenance predicate is empty for ${REF}" >&2
  exit 1
fi

echo "==> attesting SLSA provenance for ${REF}"
cosign attest --yes --type slsaprovenance --predicate "$PROVENANCE" "$REF"

# ---------------------------------------------------------------------------------
# Postconditions. Success is defined as "the artifact is retrievable from the
# registry", not "the command exited 0".
# ---------------------------------------------------------------------------------
echo "==> verifying published signature is independently retrievable"
cosign verify \
  --certificate-identity-regexp "$COSIGN_IDENTITY_REGEXP" \
  --certificate-oidc-issuer "$COSIGN_OIDC_ISSUER" \
  "$REF" > /dev/null

for predicate_type in spdxjson slsaprovenance; do
  echo "==> verifying published ${predicate_type} attestation is independently retrievable"
  cosign verify-attestation \
    --type "$predicate_type" \
    --certificate-identity-regexp "$COSIGN_IDENTITY_REGEXP" \
    --certificate-oidc-issuer "$COSIGN_OIDC_ISSUER" \
    "$REF" > /dev/null
done

echo "==> OK: ${REF} is signed, attested, and all artifacts verified from the registry"
