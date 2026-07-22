# Dependency Disposition — v0.0.3 Successor / v0.0.2 Baseline

**Status:** Final disposition recorded 2026-07-22. The current owner-operator
authorized closure of the two legacy Dependabot PRs; this record is not a
general dependency-risk acceptance.

## Open dependency changes observed 2026-07-19

| PR | Scope | Current state |
|---|---|---|
| [#509](https://github.com/IAmSoThirsty/Project-AI/pull/509) | Pip group across 2 directories, 9 updates | Closed 2026-07-22 at `2026-07-22T08:22:30Z` as superseded; it targets `master` and changes retired paths outside the active workspace dependency closure. |
| [#510](https://github.com/IAmSoThirsty/Project-AI/pull/510) | npm/yarn group across 3 directories, 12 updates | Closed 2026-07-22 at `2026-07-22T08:22:32Z` as superseded; it targets `master` and retired root/desktop/web lockfiles outside the active pnpm workspace. |

Both PRs predate v0.0.2, target remote `master`, are not contained in commit
`82aa1476657e16a1d38caccba38357c83380a3e3`, and currently report an unstable
merge state. They are not merge-ready.

**Live refresh 2026-07-19:** both PR check sets still include failures from the
remote Codex Deus workflow (latest observed run `29709754498`, preceded by
`29698528738` and `29686790959`; the workflow
is rejected before checkout because
`actions/checkout@v4` and artifact actions are not pinned to full-length SHAs),
and PR #510 also reports a CircleCI error. These failures are remote workflow
evidence, not evidence that either dependency update is safe to merge.

## Current audit finding and remediation

The first successful local OSV audit found `PYSEC-2026-3447` in locked
`setuptools 82.0.1`; the fixed version is `83.0.0`. The remediation working
tree upgrades that lock entry and the repeat Python audit reports no known
vulnerabilities. `pnpm audit --audit-level=moderate` and pinned `cargo audit`
also report no known vulnerabilities. Containerized Trivy 0.63.0 scanned all
eight locally available v0.0.2 GHCR image digests with zero HIGH/CRITICAL
findings when unfixed findings were ignored. These are local/superseded-image
results, not immutable successor CI or successor-image evidence.

## Final disposition

- Both PRs were closed with recorded GitHub comments. The machine-readable
  record is `docs/operations/cab/DEPENDABOT_DISPOSITION_2026-07-22.json`.
- The existence of the two PRs is no longer a release blocker. Merging either
  would create a different candidate and was not justified because each targets
  the retired `master` line rather than the active workspace.
- The locked v0.0.2 environment is superseded because it contains the affected
  setuptools version. Do not accept v0.0.2 as deployable merely because the
  broader Dependabot PRs are deferred.
- The successor still requires remote security workflows and exact successor-
  image vulnerability artifacts. That evidence is a CAB blocker independent
  of whether these PRs merge.
- Do not merge either PR into the v0.0.2 release line. Review, repair, test, and
  merge them through a later release candidate.
- Failed PR checks must be triaged; do not auto-merge based only on Dependabot
  generation.

## Residual risk acceptance

| Question | Required answer |
|---|---|
| Are any updates security fixes for vulnerabilities present in v0.0.2? | Yes: setuptools must be at least 83.0.0; remediated locally outside the Dependabot PRs |
| Is v0.0.2 allowed to deploy with the locked versions? | No under this pack; it is superseded by the required successor candidate |
| Risk owner | TBD |
| Acceptance expiry/review date | TBD |
| Follow-up release target | TBD |

## Completed disposition criteria

- [x] Each named PR was inspected for target, changed paths, commit, and remote
      state.
- [x] Each named PR has an explicit final disposition recorded locally and on
      GitHub.
- [x] Active pnpm dependency closure was frozen-installed and the applicable web
      lint, test, build, and visual gates passed.
- [ ] Current Python, Node, Rust, and exact-image scans complete successfully
      against the final committed release candidate. This is separate from the
      disposition of the two legacy PRs.
