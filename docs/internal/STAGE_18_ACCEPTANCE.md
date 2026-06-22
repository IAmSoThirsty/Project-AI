# Stage 18 Acceptance Gate

**Status:** accepted locally

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

## Clean-Checkout Results

- Detached worktree: `C:\tmp\project-ai-final-baa98e2`
- Runtime commit: `baa98e2`
- PowerShell: `ALL CHECKS PASSED (2026-06-22 04:29:41Z)`
- Git Bash: `ALL CHECKS PASSED (Mon Jun 22 04:39:49 UTC 2026)`
- Pytest: `447 passed`; combined branch coverage: `89.41%`.
- Asymmetric matrix: `312 passed`.
- Arbiter baseline: `12 passed`.
- Canonical replay: `5/5 invariants passed`.
- Frozen history: `2,264/2,264`; legacy source unchanged before and after.
- Android: unit tests and debug assembly succeeded with `41` Gradle tasks.
- Rust: format, Clippy, and `3` tests passed.
- Web: both portals linted, tested (`4` tests), and built.
- Desktop: source and unsigned PyInstaller onedir offscreen smokes passed.
- SBOM: reproducible validated CycloneDX JSON generated.
- Compose: seven images built; `7/7` services healthy and hardened.
- Kubernetes: Helm lint passed; `14` resources passed client dry-run.
- Both gates ended with no tracked or untracked checkout writes.

The first PowerShell attempt identified an unset Android SDK environment. The
installed API 34 SDK was confirmed at `%LOCALAPPDATA%\Android\Sdk`; commit
`c3f81ae` added deterministic discovery to both gate paths, after which both
complete gates passed.

A later evidence-only commit rerun exposed that `kubectl apply
--dry-run=client` still fetched OpenAPI from the active kubeconfig server. The
server was stale and returned EOF, making the nominal client-only check depend
on external cluster state. Both gates and CI now use `--validate=false` for the
client dry-run. `helm lint` remains the preceding chart validation step.
Both complete gates then passed from the detached `baa98e2` worktree.

## Pending Checkpoint Evidence

- Local `main` fast-forward.
- Existing GitHub remote configuration and `main` push.
- Observed remote CI result.

No tag, release, package publication, image publication, or deployment is part
of this checkpoint.
