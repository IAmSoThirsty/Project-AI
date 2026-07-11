# External Trust Anchoring — TAAR E2E Verification Bundle

This document turns the self-verifying bundle at `taar-e2e-2026-07-10/` into
externally anchored, third-party-checkable provenance. It defines the signer
identity, the trust chain, and the exact procedures for signing, publishing,
CI verification, tagged release, and optional time/transparency anchoring.

## Trust chain

```
release key (separately controlled, published out-of-band)
   │  SSHSIG signature, namespace "taar-verification-bundle"
   ▼
signatures/taar-e2e-2026-07-10.SEAL.json.sig   ──signs──▶  taar-e2e-2026-07-10/SEAL.json
                                                                │ head_sha256 + per-file SHA-256
                                                                ▼
                                                    all 74 sealed bundle files
                                                    (validated by harness/verify_bundle.py)
```

A verifier that (a) confirms the SSHSIG signature over `SEAL.json` by a trusted
identity and (b) runs `verify_bundle.py` to confirm every file matches
`SEAL.json` has proven the bundle bytes are exactly those the key holder signed.
The current sealed root is:

- `SEAL.json` head: `68491f96a53a20a2134c1d0d5febe2c9c2a62792cec4f8fc218fa4d2ccdc5010`
- committed at: `20bdb39c` (`docs(taar): add sealed reproducible verification bundle …`)

## Signer identity  (fill in when the key is created)

| Field | Value |
|---|---|
| Signer name | _to be completed by the release-key holder_ |
| Principal / identity | `release@REPLACE-WITH-YOUR-IDENTITY` (must match `allowed_signers`) |
| Key type | ssh-ed25519 |
| Key fingerprint (`ssh-keygen -lf`) | `SHA256:…` |
| Public key published at | e.g. `https://github.com/<user>.keys`, personal domain `/.well-known`, this table |

The public key lives in `allowed_signers` (template: `allowed_signers.EXAMPLE`).
Publishing it in at least one independent, key-holder-controlled location is what
makes the identity externally anchored rather than self-asserted.

---

## 1. Sign the bundle  (maintainer, with the separately controlled key)

Generate the key once, on a machine you control — never in this repo, never in
CI:

```
ssh-keygen -t ed25519 -f taar-release-key -C "release@your-identity"
```

Publish the public key, record it in `allowed_signers`, then sign:

```
cp allowed_signers.EXAMPLE allowed_signers
#   edit allowed_signers: set your principal + paste taar-release-key.pub
./sign_release.sh /path/to/taar-release-key
git add allowed_signers signatures/taar-e2e-2026-07-10.SEAL.json.sig
git commit -m "chore(taar): anchor E2E bundle with release-key signature"
```

`sign_release.sh` uses SSHSIG (`ssh-keygen -Y sign`, namespace
`taar-verification-bundle`) and writes the detached signature to
`signatures/` — outside the sealed directory, so the SEAL stays valid.

## 2. Verify  (anyone, from a clean clone)

```
git clone <repo> && cd <repo>
python3 -m pip install pyyaml          # the only dependency
./docs/internal/verification/verify_release.sh
```

`verify_release.sh` runs both checks. To require the signature (fail if absent
or invalid): `TAAR_REQUIRE_SIGNATURE=1 ./verify_release.sh`. The raw commands,
if you prefer to run them by hand:

```
python3 docs/internal/verification/taar-e2e-2026-07-10/harness/verify_bundle.py \
        docs/internal/verification/taar-e2e-2026-07-10
ssh-keygen -Y verify -f docs/internal/verification/allowed_signers \
  -I <principal> -n taar-verification-bundle \
  -s docs/internal/verification/signatures/taar-e2e-2026-07-10.SEAL.json.sig \
  < docs/internal/verification/taar-e2e-2026-07-10/SEAL.json
```

## 3. Clean-clone CI

`.github/workflows/verify-taar-bundle.yaml` runs the standalone verifier on a
fresh checkout (Python + PyYAML in an isolated venv), with `contents: read`,
`persist-credentials: false`, and a SHA-pinned checkout — the same hardening
TAAR's own Workflow Guardian looks for. The signature step is informational
until a key is anchored; set `TAAR_REQUIRE_SIGNATURE: "1"` in the workflow once
`allowed_signers` + the `.sig` are committed to make provenance a hard gate.

## 4. Tagged release

Build the deterministic archive (exact bundle + verifier + this kit) from a tag
and publish it:

```
git tag -a taar-verify-2026-07-10 -m "TAAR E2E verification bundle 2026-07-10"
git push origin taar-verify-2026-07-10                       # outward-facing
./build_release_archive.sh taar-verify-2026-07-10
gh release create taar-verify-2026-07-10 \
  taar-e2e-2026-07-10-release.tar.gz taar-e2e-2026-07-10-release.tar.gz.sha256 \
  signatures/taar-e2e-2026-07-10.SEAL.json.sig \
  --title "TAAR E2E verification bundle — 2026-07-10" \
  --notes-file SIGNING.md
```

`git archive` is reproducible for a fixed tree, so anyone can rebuild the
archive from the tag and confirm the published SHA-256. If this feature branch
is squash-merged, re-create the tag on the merge commit before pushing.

## 5. Optional: time + transparency anchoring

RFC 3161 timestamp (anchors "these bytes existed by time T"):

```
./anchor_timestamp.sh                    # offline: builds the .tsq request (digest only)
TAAR_SUBMIT_TS=1 ./anchor_timestamp.sh   # outward-facing: POSTs to a TSA (freeTSA by default)
```

Sigstore transparency log (public, append-only inclusion proof) — requires
`rekor-cli`/`cosign` (not bundled here):

```
rekor-cli upload \
  --artifact docs/internal/verification/taar-e2e-2026-07-10/SEAL.json \
  --public-key taar-release-key.pub \
  --signature signatures/taar-e2e-2026-07-10.SEAL.json.sig \
  --pki-format=ssh
# returns a log index + inclusion proof; record both in this file.
```

---

## Status — done vs. requires the key holder

| Tier | In-repo now | Requires the separately controlled key / your credentials |
|---|---|---|
| Self-verifying seal | ✅ `SEAL.json` + `verify_bundle.py` (committed, passing) | — |
| Signing machinery | ✅ `sign_release.sh` / `verify_release.sh` (SSHSIG, demo-proven) | ✅ sign `SEAL.json` with your key; commit `.sig` + `allowed_signers` |
| Signer identity published | ✅ template + procedure | ✅ generate key, publish pubkey out-of-band, fill the identity table |
| Clean-clone CI | ✅ workflow committed (seal always; signature when present) | flip `TAAR_REQUIRE_SIGNATURE` to `1` after signing |
| Tagged release | ✅ deterministic `build_release_archive.sh`; local tag command | ✅ `git push` the tag; `gh release create` (outward-facing) |
| RFC 3161 timestamp | ✅ offline request builder | ✅ `TAAR_SUBMIT_TS=1` to submit (outward-facing, permanent) |
| Transparency log | ✅ documented command | ✅ install `rekor-cli`, upload (outward-facing, permanent) |

By design, no key material or authoritative signature is generated inside this
repository or CI: a release key that an agent or the repo could hold would not
be "separately controlled." Everything an independent party can check without a
secret is committed and passing; everything that asserts your identity or
publishes to the outside world is a command for you to run.
