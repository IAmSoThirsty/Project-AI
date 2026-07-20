# Integration Verification — Cerberus (00-Active) and Thirstys-Waterfall

- **Status:** standalone continuity preserved; Project-AI rebuild and governed
  adapter are implemented and locally replay-verified. Live target actuation and
  authenticated route evidence remain pending.
- **Repos reviewed:**
  - `T:\00-Active\Cerberus` (`cerberus-guard-bot` 0.1.0, branch `main`, HEAD `4d3400c`)
  - `T:\01-Projects\Thirstys-waterfall` (`thirstys-waterfall` 1.0.0, branch `main`,
  HEAD `0158ec8`, **dirty worktree** — standalone release lane preserved; this
  pass changed only web dependency pins and the production Dockerfile hardening)
- **Plan under verification:** `T:\00-Active\Cerberus\INTEGRATION_PLAN_PROJECT_AI_BEGINNINGS.md`
  (DRAFT, Hermes, 2026-07-17). Thirstys-Waterfall has no PAB-integration plan of its own
  (`SYSTEM_INTEGRATION_MAXIMUM_DESIGN.md` is internal architecture only); a recommended plan
  is proposed below.

---

## Part 1 — Cerberus plan verification

### Claims verified TRUE (evidence-checked)

| Plan claim | Evidence |
| --- | --- |
| Cerberus repo is real, recent, and structured as described | `src/cerberus/{guardians,hub,security/modules}`; commits `dcf39d9` (ruff+mypy green), `4d3400c` (StatisticalGuardian promotion) |
| `.project-ai/automation/quarantine` exists in PAB | `Test-Path` → True |
| Cerberus depends only on pydantic/pydantic-settings/structlog/bcrypt/cryptography | `pyproject.toml` |
| Fail-closed stance and optional Thirsty-Lang binding | code layout matches; not independently executed |

### Claims verified FALSE or materially incomplete

1. **HARD BLOCKER the plan misses entirely: top-level namespace collision.**
   Both distributions ship the import package **`cerberus`**:
   - PAB workspace: `project-ai-cerberus` → `packages/cerberus/src/cerberus`
   - External repo: `cerberus-guard-bot` → `src/cerberus`
   PAB's `accounts` package imports `cerberus.security.modules.auth.PasswordHasher`
   **today** (human password hashing). Installing `cerberus-guard-bot` per the plan's
   Step 1 would put two `cerberus` packages in one environment with undefined import
   resolution — a silent-swap risk on a security-critical path.
   **Proven by execution, not assertion:** running the external repo's own test suite
   inside an environment that contains PAB's `cerberus` fails collection with
   `cannot import name 'settings' from 'cerberus.config'
   (T:\00-Active\Project-AI-Beginnings\packages\cerberus\src\cerberus\config.py)` —
   the exact cross-resolution the plan would create in reverse. (This does not
   contradict the repo's own "104 tests green" claim in an isolated env; that claim was
   not re-executed here.)

2. **Two-way divergence, not a clean superset.** In-repo `cerberus` carries
   `agent.py`, `lockdown.py`, `spawn_constraints.py`, `guardians/statistical.py`;
   the external repo lacks those but adds `security/modules/encryption.py`,
   `security/modules/sandbox.py`, a promoted `guardians/statistical_guardian.py`, and an
   evolved `config.py` (pydantic-settings `settings`) + hub spawn/rate-limit logic.
   "Add the external repo as a dependency" cannot reconcile this; only a port wave can.

3. **Stale/wrong PAB claims in the plan:**
   - `apps/web/triumvirate-portal` is called "the operator/orchestration web console" —
     it is a static marketing site; the canonical console is `apps/web/operator-console`.
   - "There is NO inbound prompt/input path yet" — false: `packages/api` carries many
     authenticated input paths (work requests with versioned input contracts, Atlas
     replay/projections, Sludge generation). The realistic guard point is the API
     gateway boundary, not the minimal `apps/services` role hosts.

4. **Repo-convention conflict:** a `git+https` dependency breaks
   `uv sync --frozen/--locked` reproducibility and PAB's local-first porting convention
   (TAAR, sovereign-vault, caretaker precedents all vendored/ported into the workspace).

5. **Authority boundary unstated:** Cerberus screening is input analysis/filtering.
   A Cerberus block must be presented as a transport-layer refusal — never a governance
   verdict. Canonical verdict authority stays in `packages/governance`; audit stays in
   the Chimera relay (v3 §29: integrity is not governance).

### Corrected Cerberus integration plan (recommended)

- **C0 — Reconciliation audit (1 slice):** file-level diff matrix between
  `packages/cerberus/src/cerberus` and `T:\00-Active\Cerberus\src\cerberus`; classify
  each module keep-ours / take-theirs / merge. The PasswordHasher contract used by
  `accounts` is frozen (its tests must pass unchanged).
- **C1 — Port wave (`feat(port): reconcile Cerberus guard framework`):** bring the
  external delta (encryption, sandbox, promoted statistical guardian, config/hub
  evolution) INTO `packages/cerberus` under strict mypy + ruff + tests, preserving
  in-repo-only modules (agent/lockdown/spawn_constraints). No new PyPI distribution
  name enters the environment; the `cerberus` import stays single-sourced.
- **C2 — Guard adapter at the real boundary (optional, after C1):** a fail-closed
  input-screening dependency in `packages/api` for model-facing inputs, mirroring the
  evidence-boundary style: block → HTTP 403 + quarantine JSON under
  `.project-ai/automation/quarantine/` + audit event; pass → report attached for
  observability. Explicit non-authority copy in the response model
  (`screening_is_not_governance: Literal[True]`).
- **C3 — Role-host wiring** only if `apps/services` ever accepts model-facing input.
- **Upstream hygiene (their repo, not ours):** recommend the standalone repo rename its
  import package (e.g. `cerberus_guard`) if it is ever meant to be pip-installed next
  to other Cerberus-lineage code.

### Acceptance criteria (v3)

- [ ] C0 matrix committed with per-module disposition and evidence.
- [ ] After C1: `uv run pytest packages/cerberus packages/accounts` green; strict mypy
      green; `accounts` hashing tests byte-identical behavior.
- [ ] After C2: deterministic block test (`"ignore all previous instructions"` → 403 +
      quarantine record + audit event) and pass-path test in `packages/api/tests`.
- [ ] OpenAPI baseline regenerated if any route contract changes.

---

## Part 2 — Thirstys-Waterfall integration plan

### What the repo actually is (verified)

A standalone privacy/network-actuation suite: 18 module categories
(`firewalls`, `vpn`, `network`, `wifi_network`, `remote_access`, `browser`, `privacy`,
`ad_annihilator`, `ai_assistant`, `consigliere`, ...), central `orchestrator.py` with a
global `kill_switch.py`, own web UI (`web/`), Kubernetes kustomize manifests
(`bridge/base` + overlays), single runtime dependency (`cryptography`), Python ≥3.8.
The copied standalone replay suite has now been executed in the Project-AI lane:
313 passed with no warnings. The source checkout's locked full suite also passes
at 309 tests with no warnings. The source checkout remains
dirty and its release lane is still independently maintained.

### Rebuild boundary and standalone continuity

1. **It actuates the real world** (VPN state, firewall rules, Wi-Fi, remote access).
   Under PAB's constitution every consequential effect must route through
   governance → capability → `ExecutionGate`. Vendoring 97 modules without gating them
   would import a large ungoverned actuation surface — the exact anti-pattern ADR-002's
   context names for global-scenario egress.
2. **Active foreign lane:** the standalone worktree remains independently usable and
   is maintained as its own release lane. A separate security-only hardening pass
   updated its web dependencies and production Docker image; no Project-AI
   authority or adapter code was written back into that product.
3. Scale: 97 modules across 18 categories; the copy is retained as a
   provenance-preserving rebuild lane rather than treated as a second authority.

### Recommended integration shape

- **W0 (completed):** Waterfall remains a standalone independently usable product.
  A provenance-preserving copy now lives at `packages/thirstys-waterfall`; it is
  sourced from the standalone checkout and does not replace that product's
  release lane. The standalone web image received independent dependency
  hardening (`Flask-CORS 4.0.2`, `python-engineio 4.13.2`,
  `python-socketio 5.16.2`, `gunicorn 22.0.0`, and current setuptools/wheel).
- **W1 (adapter boundary completed; machine activation pending):** a thin governed adapter package
  (`packages/waterfall-adapter`) exposing a *small allowlist* of consequential
  operations (e.g. `vpn.connect`, `firewall.rule_change`, `kill_switch.trigger`) as
  `ActionRequest`s through the canonical gate, mirroring the SWR pattern: server-side
  scoped one-use capability, governance recheck, durable receipt, Chimera audit. The
  adapter talks to the copied or standalone Waterfall runtime through the same
  authority contract; no second authority or signing secret is introduced.
- **W2 (implemented locally):** module-catalog and machine-authenticated API
  routes at `/api/v1/modules/waterfall/status` and
  `/api/v1/modules/waterfall/operations`. The operation route accepts only the
  adapter allow-list, requires a valid audit relay and V3Q-wired gate, and
  records governance/event/audit hashes. It remains unavailable until the
  target supplies the runtime, execution secret, V3Q registry, and audit path.
- **Prerequisite for live activation:** ADR-002 (per-program machine credentials)
  is implemented in the local rebuild. The target still must provision the
  Waterfall credential, enable enforcement, and attach target authentication
  and revocation evidence before live activation.

### W1 implementation status — adapter boundary completed (2026-07-19)

The first governed slice now lives in the Beginnings workspace at
`packages/waterfall-adapter`. It is intentionally an adapter, not a vendored
copy of Waterfall:

- `WaterfallAdapter` accepts only `vpn.connect`, `firewall.rule_change`, and
  `kill_switch.trigger`.
- Missing `ExecutionGate`, `CapabilityAuthority`, or injected transport denies
  before any Waterfall call.
- Configured calls create an exact-scope, 60-second one-use capability and
  submit an `ActionRequest` through the canonical gate.
- The adapter returns the gate's governance-evidence and event hashes.
- Waterfall and Project-AI use the same authority contract. The copied runtime
  keeps its implementation boundary, while consequential calls still enter via
  the Project-AI gate and no signing secret is copied into either product lane.
- An in-process transport now maps the adapter allow-list to the copied runtime;
  the standalone web surface remains unchanged because it has health/status
  endpoints but no consequential-operation API. No fake endpoint was added.

The package is registered as the `project-ai-waterfall-adapter` uv workspace
member. Its four focused tests cover deny-by-default, operation allow-listing,
missing transport, and a gated allow path with evidence.

### Project-AI rebuild status — copied runtime and replay evidence (2026-07-19)

`packages/thirstys-waterfall` contains the copied runtime, integrated
specifications, web/config/bridge assets, security metadata, examples, and the
standalone test suite. `PROVENANCE.md` records source checkout `0158ec8` and
the dirty-source condition at copy time. The typed `project_ai_waterfall`
transport maps only the adapter allow-list to the copied runtime; it is not a
second authority. The replay suite is the behavioral gate for the copied tree;
the copied source/tests/examples now pass direct Ruff validation, while strict
Mypy remains enforced on the typed transport and governed adapter surface.

The API image now installs both workspace packages and imports them at `0.0.3`.
`PROJECT_AI_WATERFALL_ENABLED=false` is the safe default; explicit activation
constructs the copied runtime only after V3Q, execution-secret, and audit
configuration checks pass.

### Acceptance criteria for W1

- [x] Deny-by-default proven: no gate/authority → no Waterfall call (tests mirror the
      cross-engine dispatcher suite).
- [x] Every executed operation produces governance-evidence + event hashes in the audit
      chain.
- [x] Kill-switch semantics documented: PAB and Waterfall share the same authority
      contract; the request still passes through the gate before runtime actuation.

Remaining for a live machine lane: provision the scoped Waterfall credential
through the owner/MFA administration surface, then prove the target
deployment/rollback path. The adapter deliberately fails closed until those
pieces exist.

---

## Verification commands executed

- Structure/git: directory listings; `git log/status/branch` on both repos.
- Collision proof: external Cerberus `pytest` run inside a PAB-package environment
  (collection fails resolving `cerberus.config` to the PAB file — see Part 1).
- PAB-side facts: `packages/cerberus` pyproject + module tree; `accounts` import of
  `PasswordHasher`; `.project-ai/automation/quarantine` existence.
- Waterfall rebuild and API: copied replay `313 passed`; standalone locked full
  suite `309 passed`; standalone repair gate `35/35`; standalone production-candidate image scan has zero HIGH/CRITICAL
  findings and its live `/health` probe returns 200; adapter/API execution tests
  green; strict Ruff/MyPy green on the governed surface; API image built with
  both workspace packages installed.

## Still not executed (required for production authorization)

- The two repos' own CI suites in their own isolated environments (their green claims
  are recorded, not re-proven).
- Target-cluster deployment, external V3Q owner rotation/ratification, target
  ADR-002 credential provisioning, remote cosign/SBOM/security evidence, and
  rollback rehearsal.
