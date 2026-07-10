# GitHub Workflow Guardian

TAAR does not replace GitHub Actions. It verifies workflows before they
run, explains what they can do, classifies risk, detects unsafe workflow
patterns, and produces evidence.

**It does not run your deployment. It tells you whether your automation is
allowed to exist in the shape it currently has.**

## Commands

    taar workflows scan        inspect .github/workflows/*.yml (exit 1 on critical)
    taar workflows explain     triggers, jobs, permissions, secrets, runners, actions
    taar workflows classify    OPEN / CONTROLLED / RESTRICTED / SECRET / PHANTOM / BLACK
    taar workflows harden      DRAFT patch suggestions only — nothing applied
    taar workflows evidence    run workflow-reader through the governed executor

`scan` accepts `--category` with: permissions, secrets, pins, injection,
runners, artifacts, deploy, schedule, dag, or all.

## Agent pairs

| Pair | Detects |
|---|---|
| workflow-reader → workflow-report-writer | full summary: triggers, jobs, runners, actions, permissions, secrets, artifacts |
| workflow-permission-reader → workflow-permission-report-writer | write-all, contents/packages/id-token: write, missing permissions blocks |
| workflow-secret-reader → workflow-secret-report-writer | secrets usage, env exposure, unsafe echoing, risky pull_request_target |
| workflow-action-pin-reader → workflow-action-pin-report-writer | unpinned actions, floating refs, branch refs, non-SHA third-party actions |
| workflow-injection-reader → workflow-injection-report-writer | shell injection from github context: issue titles, PR bodies, branch names, commit messages |
| workflow-runner-reader → workflow-runner-report-writer | self-hosted runners, privileged containers, Docker socket exposure |
| workflow-artifact-reader → workflow-artifact-report-writer | unsafe upload/download paths, missing retention, workflow_run artifact trust |
| workflow-deploy-reader → workflow-deploy-report-writer | deployment jobs, missing environment gates, production exposure |
| workflow-schedule-reader → workflow-schedule-report-writer | scheduled workflows, high-frequency cron, unattended automation |
| workflow-dag-reader → workflow-dag-report-writer | triggers → jobs → steps → permissions → secrets → artifacts map |

Every pair runs through the same governed executor: admission, lock,
evidence bundle, hash, audit, classification. A workflow report is not an
opinion — it is evidence.

## Classification of the workflow surface

- Any critical finding → RESTRICTED; critical in the secrets category → SECRET.
- Any high finding → at least CONTROLLED.
- Unparseable workflow file → BLACK.
- Nothing found → OPEN.

## Hardening is draft-only

`taar workflows harden` prints suggestions and creates no patch files.
Auto-applying workflow changes is autonomy the first swarm does not have,
and the phantom/governance watchers flag any patch artifact as critical.
