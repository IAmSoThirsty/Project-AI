# Stage 13 CLI Acceptance

**Status:** ACCEPTED FOR DEVELOPMENT

## Required Evidence

- [x] Installed Typer entrypoint reports development version `0.0.0.dev0`.
- [x] Public health, DOI, and replay reads use the API.
- [x] Audit, verdict, and canary commands use protected API routes.
- [x] Missing bearer authority fails before a protected network request.
- [x] Canary values are file-sourced and never appear in process arguments or output.
- [x] Canonical verdicts are limited to `ALLOW`, `DENY`, and `ESCALATE`.
- [x] API URLs reject non-HTTP schemes, embedded credentials, and host-relative escapes.
- [x] Gateway HTTP, transport, and JSON failures return concise nonzero errors.
- [x] No direct execution, capability, governance, Arbiter, or RLP dependency or command.
- [x] Ruff passes for `packages` and `tools`.
- [x] Strict MyPy passes for 40 Python source files.
- [x] CLI tests: `17 passed`; branch coverage: `92.36%`.
- [x] Full Python regression gate: `100 passed`.
- [x] Wheel and source distribution build at `0.0.0.dev0`.

The CLI does not expose an execute or actuate command. It may relay evidence to
authenticated Chimera routes, but it cannot instantiate governance authority
or submit work directly to the execution package.
