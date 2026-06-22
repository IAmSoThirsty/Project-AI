# Stage 16 CI Acceptance

**Status:** accepted with Stage 18 supplement

The original Stage 16 commit introduced four jobs. Stage 18 auditing found that
Android, desktop packaging, Kubernetes, live Compose health, coverage, secret
scanning, canonical replay, and SBOM generation were not represented. The
workflow is now expanded without rewriting the original commit.

## Eight Jobs

| Job | Required checks |
|---|---|
| `python` | locked workspace, pre-commit/gitleaks, Ruff, strict MyPy, 80% branch coverage, 312 security cases, canonical 5/5 replay, frozen history |
| `rust` | format, Clippy with warnings denied, workspace tests |
| `node` | locked install, lint, tests, both portal builds |
| `android` | declared API 34 SDK, unit tests, debug assembly |
| `desktop` | PyQt6 offscreen source smoke, unsigned PyInstaller onedir build and smoke |
| `compose` | config, seven-image build, seven healthy services, container hardening inspection |
| `kubernetes` | Helm lint and Kubernetes client dry run |
| `sbom` | reproducible validated CycloneDX Python-workspace SBOM artifact |

## Current Local Evidence

- Ruff: all checks passed; 87 files formatted.
- Strict MyPy: no issues in 70 source files.
- Pytest: 447 passed with tool-test discovery enabled.
- Combined branch coverage: 89.41%.
- Asymmetric suite: 312/312 blocked through governance and execution.
- Canonical replay: 5/5 invariants passed.
- Compose: 7/7 healthy with read-only roots, all capabilities dropped, and
  `no-new-privileges` verified.

The final clean-checkout PowerShell and POSIX results are recorded in
`STAGE_18_ACCEPTANCE.md`; this file does not claim remote CI success before the
workflow is pushed and observed.
