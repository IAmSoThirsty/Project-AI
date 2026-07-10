# Agent Specifications

44 agents in the seed registry: 22 reader→writer pairs. Autonomy level 0
for all (propose/report only). All classifications escalate at runtime.

## Facility pairs

| Reader | Writer | Builtin | Schedule | Default class |
|---|---|---|---|---|
| heartbeat-reader | heartbeat-report-writer | heartbeat_check | every 5 min | OPEN |
| lock-reader | lock-report-writer | lock_check | every 5 min | OPEN |
| runaway-reader | runaway-report-writer | runaway_check | every 5 min | OPEN |
| phantom-reader (watcher) | phantom-report-writer | phantom_check | every 5 min | OPEN→BLACK on findings |
| path-drift-reader | path-drift-report-writer | path_drift_check | hourly | OPEN |
| secret-reader | secret-report-writer | secret_check | nightly | SECRET |
| governance-reader | governance-digest-writer | governance_check | every 6 h | OPEN |
| overnight-reader | morning-brief-writer | overnight_check | daily 06:00 | OPEN |

Notes: phantom-report is the only task holding `black_evidence_allowed`.
secret-reader is the only agent with `secret_access`; all values redacted
at capture. morning-brief-writer consumes overnight + governance +
git-status evidence.

## External-command pairs

| Reader | Commands | Schedule |
|---|---|---|
| git-status-reader | git status --porcelain=v1; git branch --show-current; git rev-parse HEAD | hourly |
| ruff-reader | uv run ruff check . --output-format=json | every 3 h |
| mypy-reader | uv run mypy . --show-error-codes --no-error-summary | every 4 h |
| pytest-collect-reader | uv run pytest --collect-only -q | every 3 h |

git-status-reader is the only agent with `git_allowed` (read-only git).
A missing tool (uv absent) is a FAILED run, not a crash; a nonzero lint
exit is a finding, not a failure.

## Workflow Guardian pairs (10)

workflow, workflow-permission, workflow-secret, workflow-action-pin,
workflow-injection, workflow-runner, workflow-artifact, workflow-deploy,
workflow-schedule, workflow-dag — each `<base>-reader` →
`<base>-report-writer`, hourly, builtin `workflow_*_check`, reading only
`.github/workflows/**`. See docs/GITHUB_WORKFLOW_GUARDIAN.md.
