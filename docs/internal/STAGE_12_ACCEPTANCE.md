# Stage 12 API Acceptance

**Status:** ACCEPTED FOR DEVELOPMENT

## Required Evidence

- [x] Public `GET /health/live`, `GET /dois`, and `GET /replay/status` routes.
- [x] Bearer-authenticated Chimera verdict, canary, and audit routes.
- [x] Missing security configuration fails closed with HTTP 503.
- [x] Invalid bearer credentials fail with HTTP 401.
- [x] Verdict input is restricted to `ALLOW`, `DENY`, or `ESCALATE`.
- [x] Raw canary values are never persisted in audit evidence.
- [x] Audit reads verify the append-only hash chain before returning records.
- [x] Malformed audit JSON and hash tampering fail closed with HTTP 503.
- [x] The authoritative DOI complete catalog parses as 21 unique records.
- [x] Ruff passes for `packages` and `tools`.
- [x] Strict MyPy passes for 37 Python source files.
- [x] Stage-scoped pre-commit hooks pass in their isolated environments.
- [x] API tests: `9 passed`; branch coverage: `94.23%`.
- [x] Full Python regression gate: `83 passed`.
- [x] Wheel and source distribution build at `0.0.0.dev0`.

The global application starts without protected-route configuration so that
liveness remains observable, but every protected request returns 503 until
both an API token and an audit path are supplied. Default replay state is
`not_run` with `0/5`; a passing status must be injected from actual acceptance
evidence rather than inferred by the API.
