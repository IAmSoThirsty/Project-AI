# Project-AI Operator Console

The operator console is the canonical human-facing web application for Project-AI.
This is an implementation foundation, not a production-ready operator product.

## Implemented routes

- `/command-center` — live gateway, replay, audit-chain, and evidence summary.
- `/evidence` — replay status and DOI evidence registry.
- `/evidence/audit` — verified audit-chain evidence with server-backed search,
  event filtering, pagination, and bounded JSON page export through the signed-in
  human session.
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
requests. These functions do not introduce a second authority path.

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

## Verify

```powershell
pnpm --filter @project-ai/operator-console lint
pnpm --filter @project-ai/operator-console test
pnpm --filter @project-ai/operator-console build
uv run pytest packages/accounts/tests packages/workflows/tests packages/swr/tests packages/api/tests -q
```

## Not implemented

Managed PostgreSQL TLS/credential rotation and live-cluster restore drills, durable
notification history, global record search, additional module-specific execution
workflows, full-route and rendered color-contrast accessibility coverage, assistive-
technology acceptance, and final production security acceptance remain open work. The
test suite runs axe-core checks on sign-in, Command Center, request detail, and the SWR
execution receipt; browser rendering is still required for color contrast. See
`docs/operations/HUMAN_INTERFACE_IMPLEMENTATION_PLAN.md`.

Request detail does include stable human-review receipt digests. These prove the
displayed durable review fields; they are deliberately labeled as human decision
receipts and are not execution receipts or governance verdicts. SWR execution receipts
are separately labeled and contain the actual execution-gate and durable-audit evidence.
