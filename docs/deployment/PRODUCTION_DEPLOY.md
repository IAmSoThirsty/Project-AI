# Production Deployment

> **Scope:** deploying the Project-AI development stack to a production-like
> single-host Compose environment. For K8s / Helm, see `HELM_DEPLOY.md`.
> **Pre-requisite:** the 4 canonical gates are green per
> `PRE_DEPLOYMENT_CHECKLIST.md`.

**This document describes the deployment procedure. It does not authorize
or claim a deployment; only the project owner can do that.** See
`docs/internal/REBUILD_EXECUTION_PLAN.md` for the deployment-authority
chain.

---

## 0. Pre-flight (verify before deploying)

```bash
# 1. Repo is clean and on the expected commit
cd T:/00-Active/Project-AI-Beginnings
git status --short            # must be empty
git rev-parse HEAD            # record this SHA
git log --oneline -1          # confirm commit message

# 2. The 4 canonical gates are green
uv sync --frozen --all-extras --all-packages
uv run python tools/verify_pre_deployment.py
uv run ruff check .
uv run ruff format --check .
uv run mypy --ignore-missing-imports packages/*/src apps/desktop/src apps/services/src tools
uv run pytest -q --tb=short

# 3. Frozen-history chain is intact
python tools/verify_frozen_history.py
# Expected: 2264/2264 chain links verified

# 4. Canonical replay is 5/5
python tools/canonical_replay.py
# Expected: 5/5 invariants passed
```

If any of the above fails, **stop**. Do not deploy a system whose gates
are red. See `docs/runbooks/INCIDENT_RESPONSE.md` for the matching
diagnostic.

---

## 1. Configure secrets

Production requires a real bearer token. Generate one:

```bash
# Generate a 64-char hex token (32 bytes of entropy)
openssl rand -hex 32
```

Store the token in a secret manager. For the Compose stack, set it in
a local `.env` (gitignored):

```bash
# .env (gitignored)
PROJECT_AI_API_TOKEN=<the-hex-token>
```

**Do not commit `.env`.** Verify with `git status --short` after
creation; the file must be in `.gitignore`.

---

## 2. Build the images

```bash
cd T:/00-Active/Project-AI-Beginnings

# Validate the Compose file
docker compose config --quiet

# Build all 7 service images (parallel)
docker compose build --parallel
```

Expected output: 7 images built successfully, one per service
(`api`, `docs-portal`, `proof-portal`, `swr`, `atlas`, `arbiter-rlp`,
`genesis`).

**If a build fails:** see `docs/runbooks/INCIDENT_RESPONSE.md` §"Compose
service won't start" for the diagnostic table.

---

## 3. Start the stack

```bash
# Start all services (detached, wait for healthy)
docker compose up -d --wait --wait-timeout 240
```

The `--wait` flag blocks until all healthchecks pass (or the timeout
expires). The default 240s is generous; the stack typically reaches
healthy in <60s.

**Verify:**
```bash
docker compose ps
# All services should be "Up (healthy)"

# Spot-check the API
curl -sS http://127.0.0.1:8000/health/live
# Expected: {"status":"live","version":"0.0.0.dev0"}
```

---

## 4. Smoke test the protected routes

```bash
# Load the token from the local .env
export $(grep -E '^PROJECT_AI_API_TOKEN=' .env | xargs)

# Public route (no token)
curl -sS http://127.0.0.1:8000/dois | python -m json.tool | head -20

# Protected route (with token)
curl -sS -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     "http://127.0.0.1:8000/audit?limit=5" | python -m json.tool

# Atlas subordination proof
curl -sS http://127.0.0.1:8000/atlas/status | python -m json.tool
```

If any of the above fails with 401, the token is mismatched between
client and server. If 503, the server's `PROJECT_AI_API_TOKEN` or
`PROJECT_AI_AUDIT_PATH` is not configured.

---

## 5. Run a sample scenario (end-to-end)

```bash
# Run the CLI's verdict relay
project-ai verdict act-smoke-001 ALLOW --source deployment-smoke

# Run a SWR scenario (requires swr.scenario.record capability)
# (production: issue a real token via the capability authority; dev:
#  this may not be wired — see packages/swr README §"Why recording
#  requires the gate")

# Confirm the audit chain advanced
curl -sS -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     "http://127.0.0.1:8000/audit?limit=3" | python -m json.tool
```

---

## 6. Persist + observe

The audit log is at `${PROJECT_AI_AUDIT_PATH:-/data/chimera-audit.jsonl}`
inside the API container. For persistence across container restarts,
mount a host volume (Compose does this via the `audit-data` named
volume by default).

For long-term archival:
```bash
# Copy the audit log out of the container
docker compose cp api:/data/chimera-audit.jsonl \
    /var/log/project-ai/audit-$(date +%Y%m%d).jsonl

# Verify the chain (downstream tool; the container's chain is
# already verified by tools/verify_frozen_history.py)
sha256sum /var/log/project-ai/audit-*.jsonl
```

---

## 7. Rollback

If the deployment needs to be rolled back:

```bash
# 1. Stop the new stack
docker compose down

# 2. Check out the previous good commit
cd T:/00-Active/Project-AI-Beginnings
git log --oneline -10   # find the previous good SHA
git checkout <previous-good-sha>

# 3. Rebuild + restart
docker compose build --parallel
docker compose up -d --wait --wait-timeout 240

# 4. Verify
curl -sS http://127.0.0.1:8000/health/live
python tools/canonical_replay.py
```

**Note:** the audit log is append-only and survives rollback (it lives
in a named volume). The previous deployment's audit records remain
intact and verifiable.

---

## 8. Post-deployment

After a successful deployment:

1. **Update the continuity map:** `docs/operations/CONTINUITY_MAP.md`
   — append a Session Update with the deploy SHA, timestamp, and any
   observed incidents.
2. **Tag the release** (per project owner's release flow): see
   `docs/internal/REBUILD_EXECUTION_PLAN.md` for the tag policy.
3. **Monitor:** see `docs/operations/PERFORMANCE_SLOS.md` for the
   observability targets and `docs/runbooks/INCIDENT_RESPONSE.md`
   for the on-call procedures.

---

## 9. Source of truth

- `compose.yaml` — the deployment manifest
- `docker/*.Dockerfile` — per-service image builds
- `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` — the gate
- `docs/deployment/ENVIRONMENT_VARIABLES.md` — env-var reference
- `docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md` — start/verify/inspect/stop
- `docs/runbooks/INCIDENT_RESPONSE.md` — incident diagnostics
