# Project-AI Operator Console

The operator console is the canonical human-facing web application for Project-AI.
This is an implementation foundation, not a production-ready operator product.

## Implemented routes

- `/command-center` — live gateway, replay, audit-chain, and evidence summary.
- `/evidence` — replay status and DOI evidence registry.
- `/evidence/audit` — verified audit-chain evidence with stable hash-cursor paging;
  query, event, actor, account, operation, resource, verdict, severity, and bounded
  time filters; normalized record detail; permission-filtered safe raw JSON; integrity
  lockdown; and permission-gated redacted export of up to 500 matching records through
  the signed-in human session. Interactive search returns fixed summaries and uses a
  same-origin POST body so raw relay fields and identifiers do not enter list payloads or
  access URLs. Raw-identifier filters require `audit.raw_view`; restricted roles search
  only visible summary fields so result counts cannot reveal withheld values. Each export
  carries the normalized filter manifest, a records digest, and a hash-linked server audit
  receipt.
- `/sign-in`, `/setup`, `/recover` — local Owner entry and recovery flows.
- `/profile/security` — active-session revocation, logout, and password change.
- `/profile/preferences` — browser-local density and reduced-motion controls.
- `/inbox`, `/requests` — durable, allowlisted, non-actuating human request,
  creator-cancellation, and review workflow.
- `/governance`, `/security`, `/simulations`, `/system/health` — server-backed module
  maturity, authority-boundary, and health views.
- `/simulations/swr` — canonical scenario catalog and the first reviewed,
  execution-gate-backed analytical workflow with durable receipts.
- `/administration/accounts` — permission-enforced account, role, status, recovery-code,
  and authentication-event administration.

The application shell includes `Ctrl/Cmd+K` screen search and a live work
notification panel populated from the signed-in account's visible submitted
requests. Its liveness-derived gateway indicator distinguishes checking, live,
stale, unavailable, and browser-offline states without treating liveness as whole-system
health. The Command Center separately labels partial, stale, and offline snapshots and
retains their last-observed time. These functions do not introduce a second authority
path.

Initial reads on the work queue, evidence registry, account-security,
administration, and module-catalog routes fail closed. While a read is pending, the
console shows an explicit loading state. If it fails, record counts and consequential
controls are hidden instead of being rendered as verified-empty or healthy state. A
successful zero-record response is labeled separately. System Health also elevates any
non-healthy surface as partial evidence.

Before authentication, the assurance rail reads the server-provided
`PROJECT_AI_INSTANCE_NAME` from `GET /api/v1/instance`. It labels the target as a local
sovereign instance and distinguishes the human access path
`identity → authentication → server session → workspace` from the governed execution
path `server service identity → governance policy → scoped capability → execution gate`.
The browser receives neither the service identity nor an execution capability.

## Authority boundary

The console observes and requests through API surfaces. It does not grant
governance authority, mint capabilities, or bypass the execution gate. Human
identity, actor identity, capability, governance verdicts, and execution remain
separate concerns.

## Run locally

From the repository root:

```powershell
$env:PROJECT_AI_ACCOUNT_DB = ".local/project-ai-accounts.db"
$env:PROJECT_AI_INSTANCE_NAME = "PROJECT-AI-LOCAL"
$env:PROJECT_AI_SETUP_SECRET = "replace-with-a-one-time-random-secret"
$env:PROJECT_AI_MFA_KEY = "replace-with-a-Fernet-key"
$env:PROJECT_AI_WORKFLOW_DB = ".local/project-ai-workflows.db"
$env:PROJECT_AI_AUDIT_PATH = ".local/chimera-audit.jsonl"
$env:PROJECT_AI_EXECUTION_SECRET = "replace-with-at-least-32-random-bytes"
uv run uvicorn project_ai_api.app:app --host 127.0.0.1 --port 8000
pnpm --filter @project-ai/operator-console dev
```

Open `http://127.0.0.1:4175/`. The first loopback visit requires the setup secret
and creates the exactly-once local Owner. Recovery codes are shown once. For HTTPS
deployments, set `PROJECT_AI_SESSION_COOKIE_SECURE=true`.

The Help control resolves to `/docs/` in a production build, matching the Helm
ingress. During local development it resolves to the docs portal's standard
`http://127.0.0.1:4173/` address. Set `VITE_DOCS_URL` when the docs portal is
served somewhere else.

## Verify

```powershell
pnpm --filter @project-ai/operator-console lint
pnpm --filter @project-ai/operator-console test
pnpm --filter @project-ai/operator-console build
pnpm --filter @project-ai/operator-console exec playwright install chromium
pnpm web:visual
uv run pytest packages/accounts/tests packages/workflows/tests packages/swr/tests packages/api/tests -q
```

`pnpm web:visual` builds and serves the production bundle, installs deterministic API
fixtures in Chromium, and compares thirteen desktop/mobile/modal states with reviewed
Windows and Linux baselines. Failure traces, actual images, and pixel diffs are written
under ignored `output/playwright/`. Use
`tools/update_operator_console_visual_baselines.ps1` only after intentionally reviewing
a UI change; it regenerates both platform baseline sets through local Chromium and the
digest-pinned Linux container documented in `tests/visual/README.md`.

Unit coverage includes negative initial-read and verified-empty contracts for the work
queue, evidence sources, account security, administration, module catalogs, and partial
system health. These tests prevent unavailable data from silently becoming zero counts,
disabled-authenticator claims, or exposed mutation controls.

## Not implemented

Managed PostgreSQL TLS/credential rotation and live-cluster restore drills, durable
notification history, global record search, additional module-specific execution
workflows, assistive-technology acceptance, additional module/role state coverage, and final
production security acceptance remain open work. The test suite runs axe-core checks on every implemented authenticated route plus
the consequential auth and workflow states. A local rendered-browser pass covers all
16 authenticated routes for color contrast, 320/768/1440-pixel reflow, and native 200%
browser zoom without document-level overflow. Manual NVDA and TalkBack acceptance is
still required; the exact current evidence is recorded in
`docs/operations/CONTINUITY_MAP.md`. See
`docs/operations/HUMAN_INTERFACE_IMPLEMENTATION_PLAN.md`.

Request detail does include stable human-review receipt digests. These prove the
displayed durable review fields; they are deliberately labeled as human decision
receipts and are not execution receipts or governance verdicts. SWR execution receipts
are separately labeled and contain the actual execution-gate and durable-audit evidence.
