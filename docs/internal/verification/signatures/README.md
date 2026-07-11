# signatures/

Authoritative provenance artifacts for the sealed bundle land here. They live
OUTSIDE `taar-e2e-2026-07-10/` on purpose — adding any file inside the sealed
directory would change its SEAL.

Expected contents once a maintainer anchors the release:

| File | Produced by | Proves |
|---|---|---|
| `taar-e2e-2026-07-10.SEAL.json.sig` | `sign_release.sh` (SSHSIG) | the release key signed SEAL.json |
| `taar-e2e-2026-07-10.SEAL.json.tsq` | `anchor_timestamp.sh` (offline) | the RFC 3161 request (digest only) |
| `taar-e2e-2026-07-10.SEAL.json.tsr` | `anchor_timestamp.sh` (opt-in submit) | a TSA's signed timestamp over the digest |

The matching public key belongs in `../allowed_signers`. See `../SIGNING.md`
for the identity, fingerprint, and the full verification procedure.

This directory is intentionally empty of signatures in-repo until the holder of
the separately controlled key signs; the bundle's internal SEAL is already
self-verifying without it (`../verify_release.sh`).
