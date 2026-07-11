# project-ai-cerberus

Multi-agent runtime surface for Project-AI Beginnings. Closes Q5 from
`docs/operations/LEGACY_GAP_INVENTORY.md` §8.

Two layers live here:

1. **Canonical runtime primitives** (original stage-19.5F port of legacy
   `src/app/core/cerberus_*`, 19 files / ~6,910 LOC in legacy): the typed
   surface and fail-closed primitives (`agent`, `spawn_constraints`,
   `lockdown`).
2. **Cerberus Guard Bot** (ported 2026-07-11 from the standalone
   [IAmSoThirsty/Cerberus](https://github.com/IAmSoThirsty/Cerberus) repo,
   local clone at `T:\01-Projects\Cerberus`): a multi-guardian
   threat-analysis surface — four guardian styles, a spawning hub
   coordinator with token-bucket and per-source rate limiting, typed
   settings, and structured JSON logging. Rebuilt stdlib-only: upstream's
   pydantic-settings config became a validated frozen dataclass and
   structlog was replaced with stdlib logging. The hub optionally wires
   into the canonical `LockdownController` so a max-guardian escalation
   halts every consumer of that controller (single lockdown authority).

## Architectural invariants (AGENTS.md)

- **Downward-only deps**: cerberus imports only kernel + governance +
  execution + capability + stdlib. No upward imports.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- **Fail-closed**: spawn constraints reject unknown agent types, missing
  capabilities, and any unsatisfied invariant; never silent ALLOW.
  Guard Bot: invalid settings raise CerberusConfigError; a HIGH/CRITICAL
  ThreatReport must block by construction; max-guardian breach halts the hub.
- **Pluggable seams**: SpawnPolicy and LockdownTrigger Protocols; the hub
  accepts injected CerberusSettings and an optional LockdownController.
- **Single audit chain**: all spawn attempts and lockdown events route
  through ExecutionGate (via capability.consume).
- **Strict typing**: mypy --strict clean.
- **No import side effects**: importing `cerberus` configures nothing;
  call `cerberus.logging_config.configure_logging()` explicitly.

## Modules

Canonical primitives:

- `agent` — `CerberusAgent`: lightweight per-agent state holder (id, role,
  state, revision). State in kernel.StateRegister.
- `spawn_constraints` — `SpawnConstraints` + `SpawnPolicy` Protocol:
  fail-closed gate evaluating (agent_type, requested_capability,
  parent_chain) against a pluggable policy.
- `lockdown` — `LockdownController` + `LockdownTrigger` Protocol:
  emergency halt for the cerberus runtime. Once locked, no further
  spawns allowed until manual unlock.

Guard Bot port:

- `config` — `CerberusSettings` frozen dataclass with `CERBERUS_*` env
  overrides (`from_env`) and process-wide accessors
  (`get_settings` / `set_settings` / `reset_settings`).
- `logging_config` — `JsonFormatter` (UTC timestamps, `extra_fields`
  passthrough), `PlainFormatter`, idempotent `configure_logging`.
- `guardians` — `Guardian` ABC + `ThreatReport`/`ThreatLevel`, with four
  styles: `StrictGuardian` (explicit patterns/blocklists),
  `PatternGuardian` (contextual manipulation patterns),
  `HeuristicGuardian` (weighted scoring), `StatisticalGuardian`
  (z-score anomaly detection; repaired from upstream, which shipped it
  calling a nonexistent helper).
- `hub` — `HubCoordinator`: aggregates guardian verdicts, spawns
  `spawn_factor` guardians per detected bypass (token-bucket +
  per-source rate limited), and fail-closes at `max_guardians` —
  activating the wired `LockdownController` when one is provided.
- `main` — demonstration entry point (`python -m cerberus.main`).

Guard Bot security modules (`cerberus.security`, stdlib-only subset):

- `input_validation` — `InputValidator`: SQLi/XSS/command/LDAP/NoSQL/path/XXE
  plus prompt-injection & jailbreak detection and HTML/JSON/XML/CSV checks.
- `rbac` — `RBACManager`, `Role`, `Permission`, `User`: role-based access
  control with parent-role inheritance and default roles.
- `rate_limiter` — `RateLimiter`, `TokenBucket`, `SlidingWindowCounter`, and
  the `rate_limit` decorator.
- `threat_detector` — `ThreatDetector`: signature + per-source behavioral
  detection (rapid-repeat, identical-repeat).
- `audit_logger` — `AuditLogger`: HMAC-signed tamper-evident JSON audit log
  with rotation and integrity verification (context manager; call `close()`
  before removing the log dir on Windows).
- `auth` — `AuthManager`, `PasswordHasher`, `PasswordPolicy`: PBKDF2-HMAC-SHA256
  hashing (rebuilt off upstream bcrypt), sessions, and account lockout.
- `monitoring` — `AlertManager`, `SecurityMonitor`: alerting, z-score metric
  anomaly detection, incidents, and a Prometheus text exporter.

## Honest scope (Guard Bot port)

- Upstream's duplicate legacy modules (`hub.py` shadowed by `hub/`,
  `pattern_guardian.py` / `heuristic_guardian.py` superseded by
  `pattern.py` / `heuristic.py`) were not ported; only the live module
  set was.
- Upstream `main.py` imported a nonexistent `Thirsty_Lang` module and
  could not run; the demo was rebuilt without it.
- The hub's initial pool remains Strict/Heuristic/Pattern (upstream
  behavior); `StatisticalGuardian` is exported but not in the default
  spawn pool.
- `cerberus.security` ports 7 of upstream's 9 modules (stdlib-only). The
  prompt-injection regexes were fixed: upstream's `(previous|all)` form
  failed to match "ignore all previous instructions" — now an optional
  all/previous group matches it, consistent with the wave-1 StrictGuardian.
  `auth` was rebuilt on stdlib PBKDF2 (upstream used bcrypt, which is not a
  workspace dependency). `AuditLogger` gained a `close()`/context manager so
  its file handle is released (upstream leaked it).
- Deferred: `encryption` (needs `cryptography` as a declared dependency +
  a `uv.lock` update, outside the frozen workflow) and `sandbox` (Unix-only
  `resource` limits plus arbitrary-code `exec()` — a dual-use liability not
  appropriate for the canonical governance surface).
