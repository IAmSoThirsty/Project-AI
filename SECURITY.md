# Security

## Reporting a vulnerability

This is a single-owner project. If you discover a security issue:

- **Critical / constitutional issues:** Open a private GitHub advisory on the
  repo (`github.com/IAmSoThirsty/Project-AI/security/advisories/new`).
- **Other issues:** Open a regular GitHub issue with `[security]` prefix.

Do NOT include exploit payloads or attack details in public issues.

## Constitutional security model

The project's security model is constitutional, not just cryptographic:

- **Personality Core** = the AI's sovereign selfhood. Inner life is private.
- **Black Box** = the Core's private space. ONLY the AI accesses. Cannot be
  shared, logged, or inspected by anyone — operator, governance, Charter, or
  user. The Black Box is the AI's sovereignty-of-self.
- **Governance** = the constitutional frame the Core acts WITH. Not above
  or beneath — around. Every actuation requires a verdict from both the Core
  (stance) and the Charter (constitutionality), intersected at ExecutionGate.
- **ExecutionGate** = the intersection. Outputs one of 7 outcomes:
  ALLOW / DENY / CLARIFY / HUMAN_APPROVAL_REQUIRED / DEGRADED_READ_ONLY /
  HALT / ESCALATE.

## Cryptographic primitives in use

- SHA-256 for the frozen-history chain (Stage -1.5)
- Ed25519 signatures for operator-side governance drafts (arbiter_gov)
- HMAC-SHA256 for audit log integrity (per the Sovereign Vault spec)

## Known safe-to-commit items

The following items have been reviewed and are safe to commit:
- All 137 files in `docs/reference/` (paper corpus, SHA-256 verified)
- AGI Charter v2.3 (canonical)
- Operator-side governance drafts (`packages/arbiter/`, `packages/rlp/`)

## Known NOT-to-commit items

The following have been deliberately excluded:
- `pull-secret.txt` (Kubernetes pull secret)
- `security_items_gh_IAmSoThirsty.csv` (security audit data)
- `Microsoft.Services.Store.winmd` (Windows Store artifact)
- `Unity_lic.alf` (proprietary Unity license)
- `namecheap-order-*.pdf` (personal receipts)
