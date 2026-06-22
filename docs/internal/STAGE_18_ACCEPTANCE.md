# Stage 18 Acceptance Gate

**Status:** in progress

## Gate Scripts

- `tools/acceptance_gate.ps1` - Windows PowerShell
- `tools/acceptance_gate.sh` - POSIX-compatible shell

Both gates require a clean checkout and run the same development-checkpoint
contract: locked dependency installation, policy and secret scanning, lint,
format, strict typing, tests with 80% branch coverage, the 312-case security
matrix, Arbiter baseline, canonical replay, frozen and legacy provenance,
Android, Rust, Node, PyQt/PyInstaller, CycloneDX SBOM, seven-service Compose,
Helm, and Kubernetes client validation.

## Security-Suite Provenance

The published `asymmetric Offense.txt` gives an aggregate 312-vector matrix
across nine categories but the legacy repository contains detailed descriptions
for only 51 vectors. `governance.build_attack_catalog()` deterministically
reconstructs exactly the published category counts and varies failed security
proof combinations within each category. Each case is routed through the real
`GovernanceEngine` and `ExecutionGate`, must receive `DENY`, must not invoke its
executor, and must leave its otherwise-valid capability unconsumed.

This is acceptance evidence for a reconstructed matrix. It is not represented
as recovery of unpublished original attack payloads.

## Current In-Place Evidence

- Strict MyPy: 70 source files, no issues.
- Pytest: 447 passed with tool-test discovery enabled.
- Branch coverage: 89.41%.
- Security matrix: 312/312 blocked.
- Canonical replay: 5/5 invariants passed.
- Frozen history: 2,264/2,264 chain sections verified previously and retained
  in the gate.
- Legacy source snapshot: unchanged at
  `3fa803ab9a3751217b58c9e591cf3f515da5ab02`.
- Compose: 7/7 healthy and container security settings verified.

## Environment Finding

On this machine, `os.fsync()` against `T:\Temp` can block indefinitely while
the same durability flush succeeds on `C:\tmp`. The Arbiter file ledger keeps
its `fsync`; both acceptance scripts isolate temporary test files to
`C:\tmp\project-ai-acceptance-temp` on Windows. Final acceptance runs from a
separate clean checkout on `C:` so Gradle and packaging outputs do not encounter
the same Dev Drive write-flush issue.

## Pending Evidence

- Full PowerShell gate from a clean checkout.
- Full POSIX-compatible gate from the same clean checkout.
- Local `main` fast-forward, remote push, and observed CI result.

This record becomes accepted only after both clean-checkout gates pass.
