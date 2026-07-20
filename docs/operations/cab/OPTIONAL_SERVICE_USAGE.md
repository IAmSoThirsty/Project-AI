# Optional Service Usage Boundary

**Status:** Enforced portability contract for the v0.0.3 successor.

Project-AI may use the connected services named in
`OPTIONAL_SERVICE_USAGE.json`, but the repository does not transfer canonical
governance authority, startup authority, recovery authority, or its only copy
of evidence to any of them.

## Boundary

- Core execution, governance gates, tests, Helm rendering, audit evidence, and
  continuity remain usable from the repository and documented local toolchain.
- Every listed service is optional, replaceable, and activated only by an
  explicit operator action.
- A service outage may defer a mirror, notification, publication, render, or
  interactive check. It must not silently allow an action, erase evidence, or
  prevent local fail-closed operation.
- Neon is consumed only through the existing PostgreSQL DSN contract. Another
  compatible PostgreSQL provider may be selected without application changes.
- Vercel and Sites may deliver static portal copies. Kubernetes and local web
  delivery remain valid alternatives, and neither provider hosts canonical
  governance authority.
- GitHub may transport source, CI, OCI images, attestations, and releases. Local
  gates remain executable when GitHub is unavailable; publication is deferred.
- Slack, Linear, Notion, and Basic Memory Cloud may mirror operational records.
  The tracked CAB, continuity map, audit records, and release evidence remain
  the source of truth.
- Browser and Chrome are interactive acceptance surfaces. Automated web tests
  and builds are the deterministic baseline.
- Documents, PDF, Academic Writing Toolkit, and Template Creator may create or
  review presentation artifacts. Tracked Markdown and machine-readable evidence
  remain authoritative.

## Current connected inventory observed 2026-07-20

Read-only discovery found connected GitHub, Slack, Linear, Notion, Basic Memory
Cloud, and Vercel account/workspace surfaces. It found no existing Project-AI
Vercel project, Neon project, or Sites project. No vendor project, database,
site, message, task, page, or deployment was created by that discovery.

This inventory is time-specific and is not a production target approval. Real
resource identifiers belong in the approved target-environment record, not in
this portability contract.

## Verification

Run:

```powershell
uv run pytest tools/tests/test_verify_pre_deployment.py -q
uv run python tools/verify_pre_deployment.py --report
```

The first command verifies the service contract. The second keeps deployment
fail-closed until the separate target, backup, and release-evidence gates pass.
