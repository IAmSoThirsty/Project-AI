# Dependency Disposition — v0.0.3 Successor / v0.0.2 Baseline

**Status:** Proposed disposition; technical evidence current; change owner
acceptance pending.

## Open dependency changes observed 2026-07-19

| PR | Scope | Current state |
|---|---|---|
| [#509](https://github.com/IAmSoThirsty/Project-AI/pull/509) | Pip group across 2 directories, 9 updates | Open, non-draft, `UNSTABLE`; branch `dependabot/pip/pip-819fd62d25` targets `master` (updated 2026-07-13) |
| [#510](https://github.com/IAmSoThirsty/Project-AI/pull/510) | npm/yarn group across 3 directories, 12 updates | Open, non-draft, `UNSTABLE`; branch `dependabot/npm_and_yarn/npm_and_yarn-93676e20c0` targets `master` (updated 2026-07-14) |

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

## Proposed disposition

- The existence of the PRs is **not by itself a blocker** to a successor
  release. Merging them would create a different candidate and remains out of
  scope for this change.
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

## Exit criteria

- [ ] Current Python, Node, Rust, and exact-image scans complete successfully
      against the committed successor candidate.
- [ ] Each dependency update is classified security/bug/compatibility/tooling.
- [ ] Any vulnerability affecting v0.0.2 is fixed in a new candidate or accepted
      explicitly with owner, compensating control, and expiry.
- [ ] PR checks are repaired and green before merge.
- [ ] CAB/change owner records whether the residual dependency risk is accepted.
