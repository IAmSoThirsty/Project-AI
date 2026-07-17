# Integration Verification — Cerberus (00-Active) and Thirstys-Waterfall

- **Status:** VERIFICATION COMPLETE; integration NOT executed (planning/verification only,
  per user directive 2026-07-17: "look at two more repos and verify a plan for integration").
- **Repos reviewed (read-only):**
  - `T:\00-Active\Cerberus` (`cerberus-guard-bot` 0.1.0, branch `main`, HEAD `4d3400c`)
  - `T:\01-Projects\Thirstys-waterfall` (`thirstys-waterfall` 1.0.0, branch `main`,
    HEAD `0158ec8`, **dirty worktree** — another agent (Sol5.6-codex) is actively working it)
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

## Part 2 — Thirstys-Waterfall integration plan (proposed; no prior plan existed)

### What the repo actually is (verified)

A standalone privacy/network-actuation suite: 18 module categories
(`firewalls`, `vpn`, `network`, `wifi_network`, `remote_access`, `browser`, `privacy`,
`ad_annihilator`, `ai_assistant`, `consigliere`, ...), central `orchestrator.py` with a
global `kill_switch.py`, own web UI (`web/`), Kubernetes kustomize manifests
(`bridge/base` + overlays), single runtime dependency (`cryptography`), Python ≥3.8.
Docs claim 309/309 tests passing — **not executed in this verification** (foreign repo,
active worktree; would require its own isolated environment).

### Why it must NOT be vendored into the workspace now

1. **It actuates the real world** (VPN state, firewall rules, Wi-Fi, remote access).
   Under PAB's constitution every consequential effect must route through
   governance → capability → `ExecutionGate`. Vendoring 97 modules without gating them
   would import a large ungoverned actuation surface — the exact anti-pattern ADR-002's
   context names for global-scenario egress.
2. **Active foreign lane:** the worktree is dirty (another agent mid-work). Any move
   now risks clobbering in-flight changes.
3. Scale: 97 modules across 18 categories versus the workspace's port-wave discipline.

### Recommended integration shape

- **W0 (now):** Waterfall remains a standalone external application. No cross-repo
  imports in either direction. Coordinate any code movement with its active agent.
- **W1 (first real slice, machine lane):** a thin governed adapter package
  (`packages/waterfall-adapter`) exposing a *small allowlist* of consequential
  operations (e.g. `vpn.connect`, `firewall.rule_change`, `kill_switch.trigger`) as
  `ActionRequest`s through the canonical gate, mirroring the SWR pattern: server-side
  scoped one-use capability, governance recheck, durable receipt, Chimera audit. The
  adapter talks to Waterfall over its local API/CLI; Waterfall itself never holds PAB
  authority and PAB never embeds Waterfall's kill switch (it stays local-sovereign).
- **W2:** read-only observability in the module catalog
  (`/api/v1/modules` entry, `interface_status="backend_only"` → external service) and,
  later, optional MCP tools for status reads only.
- **Prerequisite:** ADR-002 (per-program machine credentials) should land before W1 so
  the adapter authenticates as its own program, not the shared token.

### Acceptance criteria for W1 (when scheduled)

- [ ] Deny-by-default proven: no gate/authority → no Waterfall call (tests mirror the
      cross-engine dispatcher suite).
- [ ] Every executed operation produces governance-evidence + event hashes in the audit
      chain.
- [ ] Kill-switch semantics documented: PAB can *request* it through the gate; Waterfall
      retains independent local authority to trigger it.

---

## Verification commands executed

- Structure/git: directory listings; `git log/status/branch` on both repos.
- Collision proof: external Cerberus `pytest` run inside a PAB-package environment
  (collection fails resolving `cerberus.config` to the PAB file — see Part 1).
- PAB-side facts: `packages/cerberus` pyproject + module tree; `accounts` import of
  `PasswordHasher`; `.project-ai/automation/quarantine` existence.

## Not executed (would be required for full claims)

- The two repos' own CI suites in their own isolated environments (their green claims
  are recorded, not re-proven).
- Any code movement, dependency change, or adapter implementation.
