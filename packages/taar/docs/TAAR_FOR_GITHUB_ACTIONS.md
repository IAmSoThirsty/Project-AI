# TAAR for GitHub Actions

Two ways to use TAAR against GitHub workflows.

## 1. Local workflow guardian

    pip install taar-agent-taskforce
    cd your-repo
    taar workflows explain
    taar workflows scan
    taar workflows classify
    taar workflows harden

No registry needed for direct workflow commands. For governed evidence
bundles (`taar workflows evidence`), seed the repo first with `taar init`.

## 2. GitHub Action wrapper

`action.yml` at the repo root wraps the CLI as a composite action:

    name: CI with TAAR gate
    on:
      pull_request:
    permissions:
      contents: read
    jobs:
      guard:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.12"
          - uses: IAmSoThirsty/TAAR@v0.1.0
            with:
              category: all
              fail-on-critical: "true"

Inputs: `category` (default all), `fail-on-critical` (default true — the
job fails if any critical finding is present).

Pin the action to a release tag (`@v0.1.0`), not a branch — the same rule
TAAR's own scanner enforces for third-party actions. The action installs
TAAR from its own checkout, so the CLI version always matches the pinned
tag. Python 3.12+ must already be on the runner (the `setup-python` step
above); the action fails fast with instructions if it is not.

## Examples

    examples/github-actions-basic/       TAAR as a CI gate
    examples/github-actions-dangerous/   intentionally unsafe patterns TAAR flags
    examples/github-actions-hardened/    the corrected counterpart (scans OPEN)

## Why this exists

Workflow security is a real, documented pain point: broad GITHUB_TOKEN
permissions, script injection from untrusted context, unpinned third-party
actions, secret exposure through pull_request_target, compromised
runners, and artifact trust. TAAR gives GitHub Actions a local governance
and evidence layer: deny-by-default reading of what the automation is
actually allowed to do, with classified, hash-sealed evidence you can put
in front of a reviewer.
