# sovereign_vault

Object-level narrow-release vault architecture. Built against the 12
blind-spot corrections you gave, plus the concrete Document 1 additions
(TPM NVRAM counters, memfd_create IPC, in-toto/Cosign admission seams,
seccomp/namespace hardening). Composes with CBCC rather than
reimplementing it — CBCC's Shamir sealing and audit chain are seams
(`interfaces.py`), not duplicated here.

No "unlock." No "mount." No "session." Only:

    verify -> authorize -> release (locked memory) -> zeroize

27/27 tests passing (`pytest tests/ -v`). Two real bugs caught and fixed
during build — see "Bugs caught by the test suite" below.

## VERIFIED / SEAM / LIMITATION register

Mapped 1:1 against your original list.

| # | Blind spot | Status | Where |
|---|---|---|---|
| 1 | USB token not a strong root alone | **VERIFIED** — `combine_factors()` is an AND-combine of token+TPM+operator shares; refuses with <2 factors or any factor <16 bytes | `primitives.py` |
| 2 | Anti-rollback protection | **VERIFIED** (local) — monotonic sequence, hash-linked, Ed25519-signed checkpoints; `verify_advance()` rejects sequence <= last observed even with a valid signature | `state.py` |
| | | **SEAM** — external witness anchoring (so an attacker with full local disk access can't replay a self-consistent old chain) | `state.ExternalWitness` (raises `NotImplementedError` by default) |
| | | **SEAM** — TPM NVRAM hardware monotonic counter (Document 1's addition) is not wired; local hash-chain is what's implemented | — |
| 3 | Recovery is part of the attack surface | **VERIFIED** — m-of-n quorum (threshold >= 2 enforced), duplicate-approver rejection, stale-approval rejection, distinct `RECOVERY_EXECUTED` audit event, epoch bump invalidates all derived keys by construction | `recovery.py`, `keys.py` |
| 4 | Metadata leakage | **VERIFIED** — dual index: full encrypted index + separate opaque exposure index (UUID + coarse enum category + padded size bucket), cryptographically bound so they can't diverge undetected | `metadata.py` |
| 5 | Key hierarchy compartmentalization | **VERIFIED** — HKDF-SHA-512 tree, one branch per purpose (vault/tool/record/audit-signing/metadata/recovery-wrap/token-binding), epoch folded into every branch | `keys.py` |
| 6 | Audit integrity AND availability | **VERIFIED** — every security-relevant operation checks `has_capacity()` first and fails closed (`AuditUnavailableError`); tamper responses escalate to SEAL if the audit write itself can't be recorded | `admission.py`, `release.py`, `tamper.py` |
| 7 | Mounting is dangerous | **VERIFIED** — no mount primitive exists in this package; `ObjectReleaseManager.release()` is a context manager that decrypts exactly one object into `SecureBuffer` and zeroizes on exit, success or exception | `release.py` |
| | | **PARTIAL** — real Linux `memfd_create` + `F_SEAL_*` helper included for cross-process hand-off | `release.transfer_via_memfd` |
| 8 | Vault process isolation | **SEAM** (deploy-layer, not Python-enforceable from inside) — systemd hardening unit provided: `NoNewPrivileges`, capability drop, `PrivateNetwork`, namespace isolation, seccomp filter, `MemoryDenyWriteExecute` | `deploy/vault.service` |
| 9 | Tamper handling (hardware + software) | **VERIFIED** — policy table (not hardcoded), 5 graduated response tiers (REATTEST < REGENERATE_COMPONENT < SEAL < REVOKE < FORCE_RECOVERY), unconfigured events escalate to REVOKE (not the mildest tier), audit-unavailable-during-tamper escalates to SEAL | `tamper.py` |
| 10 | Backups can silently defeat the design | **VERIFIED** — `export_bundle()` refuses to write without every required component present; `import_bundle()` runs the *same* `verify_advance()` rollback check as any other untrusted state input, rejects cross-vault restore, rejects pre-recovery-epoch restore | `backup.py` |
| 11 | Vault should verify what it stores | **VERIFIED** — `admit_object()` requires matching sha256, an authority-token-verified approval, audit capacity, and a `ProvenanceVerifier` pass before anything is written; produces a signed `ADMISSION_APPROVED` event | `admission.py` |
| | | **SEAM** — actual SBOM/in-toto/Cosign verification logic | `admission.ProvenanceVerifier` (fails closed by default) |
| 12 | Formal deny condition for uncertainty | **VERIFIED** — `RuntimeConditions` has no default-True field; every field starts `None` (UNKNOWN) and `require_all()` raises on any UNKNOWN *or* False field; `TrustedClock` rejects a missing NTP reference and rejects both forward and backward drift beyond threshold | `deny.py` |

Final correction ("design around narrowly authorized release, not
unlocking") — this is the load-bearing design decision of the whole
package, not a bolt-on: there is no vault-wide unlock function anywhere
in this code.

## ARDA scoping note

Document 2 specified a general-purpose, multi-domain regenerative
defense framework (endpoint/K8s/API-gateway/identity/CI-CD recovery,
with its own metrics and adversarial-analysis writeup). That generic
framework is **not built here** — it's a separate deliverable, out of
scope for a vault module.

What *is* built is the piece of ARDA that's actually useful to this
vault: a fifth, non-nuclear tamper-response tier (`REGENERATE_COMPONENT`)
that rebuilds one injured component (e.g. the release conduit) from a
signed blueprint under fresh attestation, instead of jumping straight to
SEAL/REVOKE/FORCE_RECOVERY for a localized fault. It enforces ARDA's hard
rules structurally:

- blueprint signer must be in a trusted set that **excludes** the
  injured component's own key (constructor raises if the set is empty)
- `reintegrate` is unreachable in the code path unless `attest` already
  passed — no flag to bypass, it's sequencing
- a `LoopGuard` caps regenerations per component per time window and
  escalates to `SafeHaltError` (→ your caller should route that to
  `FORCE_RECOVERY`) rather than looping forever
- successful regeneration is logged as "rebuild passed attestation," never
  as "compromise understood" or "vault is clean" — see the `note` field
  on the `REGENERATION_COMPLETE` audit event

If you want the full generic ARDA framework (stages/metrics/adversarial
analysis/pseudocode across all five application domains) as its own
document, that's a separate build.

## Honest limitations (not hidden in the code)

- **SecureBuffer / zeroization**: CPython does not guarantee plaintext
  never gets copied by the allocator or interpreter. `mlock` is
  best-effort (Linux-only, silently no-ops elsewhere), and byte-level
  overwrite is real but not a substitute for a hardware enclave. Stated
  in `buffer.py`'s docstring, not glossed over.
- **Anti-rollback is local-only** until you wire an `ExternalWitness`.
  Local hash-chain + signature stops naive replay; it does not stop an
  attacker with full control of local disk restoring an internally
  self-consistent older chain, unless checkpoints are anchored
  externally (TPM NVRAM counter or a witness log).
- **`_zero()` in `keys.py` is a documented no-op** for the same CPython
  immutability reason — real transient-key hygiene for the one key that
  matters most (RootKEK) is enforced via `SecureBuffer`/`RootKekSession`,
  not by this function; it exists so intermediate branch keys aren't
  silently held in scope indefinitely, not as a security boundary.
- **No literal process sandboxing from inside Python.** `deploy/` gives
  you a real systemd unit; this package cannot enforce namespace/seccomp
  isolation on itself from user space.

## Bugs caught by the test suite

1. `TamperHandler.handle()`: when the audit chain had no reserved
   capacity, the code correctly escalated the *response* to SEAL, but
   then unconditionally called `audit.append()` for the escalated event —
   which itself raises `AuditUnavailableError` (capacity is still zero),
   so the handler raised the wrong exception type and the SEAL never
   completed. Fixed to catch the append failure and still apply SEAL —
   audit unavailability is the *reason* to seal, not a reason sealing can
   be skipped.
2. Test-file bug, not package bug: `execute_recovery` was used in tests
   without being imported. Caught immediately by `NameError` — no
   ambiguity, fixed by adding it to the import line.

## Quickstart

```python
from sovereign_vault.vault import SovereignVault
from sovereign_vault.state import AntiRollbackState
from sovereign_vault.primitives import SigningIdentity, combine_factors
from sovereign_vault.reference_adapters import (
    AllowAllAuthorityProvider, AlwaysAttestProvider, InMemoryAuditChain,
)

# --- reference adapters below are TEST-ONLY; wire real CBCC/TPM/
# STATE_REGISTER adapters via interfaces.py for production ---

root_kek = combine_factors(
    b"usb-token-share-................",
    b"tpm-sealed-share-................",
    b"operator-secret-................",
    info=b"vault-root:my-vault",
)

vault = SovereignVault(
    vault_id="my-vault",
    authority=AllowAllAuthorityProvider(),      # SEAM: real STATE_REGISTER/T.A.R.L.
    audit=InMemoryAuditChain(),                 # SEAM: real CBCC audit chain
    attestation=AlwaysAttestProvider(),          # SEAM: real TPM attestation
    provenance=...,                              # SEAM: real SBOM/signature verifier
    rollback_state=AntiRollbackState(signer=SigningIdentity.generate()),
)
vault.bootstrap(root_kek, initial_state_summary={"created": True})
```

See `tests/test_vault.py` for the full admit -> release -> tamper ->
regenerate -> recover -> backup lifecycle exercised end to end.
