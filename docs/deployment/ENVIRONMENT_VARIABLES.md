# Environment Variables

> **Source of truth:** the application call sites, `.env.example`, Compose,
> and Helm templates. This document is a prose map; update it when a runtime
> variable or secret-file binding changes.

**Do not commit real credentials.** The `.env.example` file is a template;
real values go in a local `.env` (gitignored) or in a secret manager.

---

## 0. Categories

| Category | Where consumed | Required? |
|---|---|---|
| **API gateway auth** | `PROJECT_AI_API_TOKEN` on the server | Development fallback only; production uses durable per-program credentials |
| **Machine credential enforcement** | `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED` on the server | Set `true` in production after provisioning per-program credentials; rejects the shared bootstrap token |
| **Audit persistence** | `PROJECT_AI_AUDIT_PATH` on the server | Required for protected routes |
| **CLI client** | `PROJECT_AI_API_URL`, `PROJECT_AI_API_TOKEN` on the client | Required for protected CLI commands |
| **Desktop smoke mode** | `PROJECT_AI_DESKTOP_SMOKE`, `QT_QPA_PLATFORM` | Optional, used in CI / offscreen validation |
| **DOI registry path** | `PROJECT_AI_DOI_REGISTRY` on the server | Optional, defaults to `docs/reference/DOI_REGISTRY.md` in the container |
| **Rust toolchain (dev only)** | `RUSTUP_TOOLCHAIN` | Optional, for Windows-vs-Linux cargo selection |

---

## 1. API gateway auth

### `PROJECT_AI_API_TOKEN`

| Property | Value |
|---|---|
| Type | string (non-empty) |
| Default | empty (server) |
| Required for | protected API routes only when durable machine credentials are not configured/enforced |
| Where set on the server | container env, mounted secret file, or `.env` consumed by Compose |
| Where set on the client | shell env (preferred) or `--api-token` flag (avoid — leaks to shell history) |
| Comparison | constant-time `hmac.compare_digest` |

**Behavior when empty:** in development fallback mode, protected routes return
`503 Service Unavailable` with `detail: "Protected API surfaces are not
configured"`. In production durable-credential mode, this value is intentionally
absent and machine routes authenticate against the account store.
This is intentional — it is **not** an unauthenticated state. The
caller cannot bypass the 503 by omitting the `Authorization` header;
the server is refusing to serve the protected surface, not asking for
credentials.

**Generation:** any non-empty string. For production, use
`openssl rand -hex 32` (64-char hex) and store in a secret manager.

### `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED`

The shared API token is a development/bootstrap credential. Production
protected routes must use credentials created through the owner/MFA-protected
machine-credential administration API. Set this variable to `true` after
provisioning per-program credentials so the shared token cannot silently remain
in service. Each route enforces its required scope (`evidence.read`,
`evidence.write`, or `analysis.generate`). Raw credential tokens are returned
only once at creation and are never stored.

### Mounted secret files

The API accepts the following `_FILE` alternatives so orchestrators can mount
secrets without exposing their values in container environment variables:

| Direct value | File path variable |
|---|---|
| `PROJECT_AI_API_TOKEN` | `PROJECT_AI_API_TOKEN_FILE` |
| `PROJECT_AI_DATABASE_URL` | `PROJECT_AI_DATABASE_URL_FILE` |
| `PROJECT_AI_SETUP_SECRET` | `PROJECT_AI_SETUP_SECRET_FILE` |
| `PROJECT_AI_MFA_KEY` | `PROJECT_AI_MFA_KEY_FILE` |
| `PROJECT_AI_EXECUTION_SECRET` | `PROJECT_AI_EXECUTION_SECRET_FILE` |

### Waterfall integration

`PROJECT_AI_WATERFALL_ENABLED` defaults to `false`. Set it to `true` only in an
approved target after the copied/standalone runtime configuration, V3Q public
registry, execution secret, and audit path are all present. When enabled,
`PROJECT_AI_WATERFALL_CONFIG` may point to the server-side Waterfall JSON
configuration; it is never supplied by a browser. Startup fails closed if
Waterfall is enabled without a 32-byte execution secret, a valid audit relay,
or a configured V3Q trusted-key registry.

Each file must contain a non-empty UTF-8 value. Setting both the direct value
and its `_FILE` alternative is rejected at startup. The production Helm chart
mounts the configured existing Secret read-only at
`/var/run/secrets/project-ai` and uses only `_FILE` variables.

### `PROJECT_AI_AUDIT_PATH`

| Property | Value |
|---|---|
| Type | filesystem path (writable) |
| Default | none (server) |
| Required for | protected API routes (Chimera audit emission) |
| Where set | container env; for the Compose stack it is `/data/chimera-audit.jsonl` (mounted from the `audit-data` volume) |

**Behavior when empty:** same as above — `503 Service Unavailable`.

**Format:** newline-delimited JSON (JSONL). One audit record per line.
The container runs as UID 10001, so the host path must be writable by
that UID, or mounted as a named volume.

---

## 2. CLI client

### `PROJECT_AI_API_URL`

| Property | Value |
|---|---|
| Type | URL |
| Default | `http://127.0.0.1:8000` |
| Required for | all CLI commands that talk to the gateway |
| Override | `--api-url` flag |

### `PROJECT_AI_API_TOKEN` (client side)

| Property | Value |
|---|---|
| Type | string |
| Default | empty |
| Required for | protected CLI commands (`audit`, `verdict`, `canary`, `atlas-sludge`) |
| Override | `--api-token` flag (avoid) |

**Behavior when missing on a protected command:** the CLI exits
non-zero with the message `PROJECT_AI_API_TOKEN is required for this
command`. The error is unambiguous; do not retry without setting
the env var.

---

## 3. Desktop smoke mode (CI only)

### `PROJECT_AI_DESKTOP_SMOKE`

| Property | Value |
|---|---|
| Type | flag (`1` to enable) |
| Default | unset |
| Required for | CI offscreen PyQt6 validation |
| Effect | loads the desktop app in a non-interactive test mode |

### `QT_QPA_PLATFORM`

| Property | Value |
|---|---|
| Type | string |
| Common values | `offscreen` (CI), `windows` (default on Windows), `xcb` (Linux) |
| Effect | selects the Qt platform abstraction plugin |

For CI: set both to `PROJECT_AI_DESKTOP_SMOKE=1 QT_QPA_PLATFORM=offscreen`.

---

## 4. DOI registry

### `PROJECT_AI_DOI_REGISTRY` (server side)

| Property | Value |
|---|---|
| Type | filesystem path |
| Default | `docs/reference/DOI_REGISTRY.md` (resolved relative to the repo root in the container) |
| Required for | `GET /dois` returning the catalog |
| Effect | overrides the default DOI registry path; useful for staged releases |

---

## 5. Rust toolchain (dev only)

### `RUSTUP_TOOLCHAIN`

| Property | Value |
|---|---|
| Type | string |
| Default | `rust-toolchain.toml` pin (`stable-x86_64-pc-windows-gnu` on Windows dev) |
| When to override | when running `cargo` on Linux (set to `stable`); when CI uses a different toolchain than the local pin |
| Where documented | `rust-toolchain.toml` at repo root |

---

## 6. Production checklist (env vars)

Before declaring a deployment production-ready, confirm:

- [ ] `PROJECT_AI_MACHINE_CREDENTIALS_REQUIRED=true` is set in production.
- [ ] One scoped machine credential is provisioned per approved program through
      the owner/MFA administration API; raw tokens are held only by the approved
      secret manager or client runtime.
- [ ] `PROJECT_AI_API_TOKEN` is absent from the production API environment/file
      unless an explicit, time-bounded bootstrap exception is approved.
- [ ] `PROJECT_AI_AUDIT_PATH` points to a writable path; the host directory is owned by UID 10001 (Compose) or the equivalent service account (K8s)
- [ ] `PROJECT_AI_DOI_REGISTRY` (if overridden) points to a verified copy of `docs/reference/DOI_REGISTRY.md`
- [ ] `.env` (local) or the K8s Secret is **not** committed
- [ ] `gitleaks` and `detect-private-key` pre-commit hooks are enabled (see `docs/security.md` §"Secret Scanning")

## 7. Source of truth

- `.env.example` — the template
- `compose.yaml` — the `${VAR}` references
- `helm/project-ai/templates/api.yaml` — production Secret mounts
- `packages/api/src/project_ai_api/app.py` — the `os.getenv` call sites
- `packages/cli/src/project_ai_cli/app.py` — the CLI env-var reads
- `docs/operator.md` — the operator-side install commands

If you add a runtime variable, update every applicable source above in the
same change.
Raw credential tokens are returned only once at creation and are never stored.
