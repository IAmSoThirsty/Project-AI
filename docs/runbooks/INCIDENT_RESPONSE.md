# Incident Response Runbook

> **Scope:** production-like incidents in the Project-AI development stack.
> **Audience:** operators on call.
> **Authority:** the diagnostic commands in this runbook are non-mutating
> (read-only) unless explicitly labeled `[MUTATES]`.

**When in doubt:** stop mutating the system, capture state, escalate.

---

## 0. First-response checklist (any incident)

Before diving into a specific scenario, run these four diagnostics in order.
Each takes <10 seconds and gives you the system-wide picture.

```bash
# 1. Are the containers running?
docker compose ps

# 2. Is the API gateway live?
curl -sS http://127.0.0.1:8000/health/live

# 3. What does the recent audit log look like?
tail -50 "${PROJECT_AI_AUDIT_PATH:-/data/chimera-audit.jsonl}"

# 4. Frozen-history chain still intact?
python tools/verify_frozen_history.py
```

If all four pass, the system is nominally healthy. If any fail, jump to the
matching section below.

---

## 1. Service X is unhealthy

**Symptom:** `docker compose ps` shows a service in `Restarting` or
`Exit 1` state; or its healthcheck reports `unhealthy`.

**Diagnostic:**
```bash
# Recent logs for the failing service
docker compose logs --tail=200 <service>

# Is it OOM-killed?
docker compose inspect <service> --format '{{.State.Status}} {{.State.ExitCode}}'
dmesg | tail -50 | grep -i oom
```

**Common root causes:**

| Symptom in logs | Root cause | Fix |
|---|---|---|
| `ModuleNotFoundError: <package>` | uv sync drift | `uv sync --frozen --all-extras --all-packages` then `docker compose up -d --build` |
| `Permission denied` on `/data` | Wrong UID | The API container runs as UID 10001; `chown -R 10001:10001 /data` on the host |
| `bind: address already in use` on port 8000 | Stale host process | `netstat -ano | grep 8000` then kill the PID |
| `out of memory` | Memory leak or undersized container | Check `docker stats`; restart with `--memory=512m` flag |
| `connection refused` to internal adapter | Adapter not started | Check `docker compose ps` for the adapter; the API `depends_on: { condition: service_healthy }` should block startup until it's healthy |

**Postmortem:** capture the failing service's last 1000 log lines and the
`docker compose inspect` output before restarting.

---

## 2. Audit chain is broken

**Symptom:** `python tools/verify_frozen_history.py` reports chain mismatch;
or `GET /replay/status` returns `chain_intact: false`; or
`tools/canonical_replay.py` fails.

**This is a tamper-evidence alarm.** Do not restart services; do not
"regenerate" the chain; do not push to clear the error.

**Diagnostic:**
```bash
# Which record is broken?
python tools/verify_frozen_history.py 2>&1 | grep -E "FAIL|mismatch|broken"
# Read the failing record
cat docs/internal/frozen-history/RECORD_<id>.json
# Read the previous record (the one whose hash was expected)
cat docs/internal/frozen-history/RECORD_<id-1>.json
```

**Root cause taxonomy:**

| Cause | Evidence | Action |
|---|---|---|
| Accidental edit of a file in `docs/internal/frozen-history/` | The file's content no longer matches its declared hash | Revert the change (`git checkout HEAD -- docs/internal/frozen-history/`) and re-run the verifier |
| Compromised system | The file's content is plausibly altered AND the edit timestamp predates the verifier's last good run | **Escalate.** This is a security incident, not a docs incident. |
| Corrupted `chimera-audit.jsonl` | Tail of the audit log is missing a closing brace or has duplicate `hash` fields | Stop writes to the log (`chmod 000` the file), preserve the corrupt copy, restore from the most recent verified snapshot in `docs/audit/` |
| Tool bug | Verifier reports failure but `sha256sum` on every record matches `RECORDS.sha256` | Open an issue with the verifier output and a `sha256sum` of the chain directory; treat as a P2 bug |

**Postmortem:** the audit chain is the system's tamper-evidence primitive.
Any break — even a "harmless" one — must be root-caused and recorded in
`docs/audit/wiki-vs-papers-discrepancies.md` (or a new incident-specific
file) before the system is declared healthy again.

---

## 3. Capability token rejected

**Symptom:** `ExecutionGate.submit_action` returns `DENY` with reason
"executor failed: CapabilityError" or similar; CLI `audit` shows
`executor_failed` events.

**Diagnostic:**
```bash
# 1. Is the token env var set?
echo "${PROJECT_AI_API_TOKEN:+set to length ${#PROJECT_AI_API_TOKEN}}"

# 2. Does the gateway see the same token?
curl -sS -H "Authorization: Bearer $PROJECT_AI_API_TOKEN" \
     http://127.0.0.1:8000/health/live
# If this returns 401, the token is mismatched between client and server.

# 3. Recent capability-related audit events
project-ai audit --limit 100 | python -m json.tool | grep -i capabilit
```

**Common root causes:**

| Cause | Evidence | Fix |
|---|---|---|
| Server `PROJECT_AI_API_TOKEN` empty or unset | `GET /audit` returns 503 "Protected API surfaces are not configured" | Set the env var on the server side and restart the API container |
| Client `PROJECT_AI_API_TOKEN` empty or unset | CLI prints "PROJECT_AI_API_TOKEN is required for this command" | Export the env var in the operator's shell |
| Token mismatch | CLI gets 401 "Invalid bearer token" | Compare the literal token strings (the gateway uses `hmac.compare_digest`, so even a 1-char mismatch rejects) |
| Token expired | (N/A — the API gateway does not issue tokens; it consumes them. If the calling system issued a short-lived token, check its TTL.) | Reissue from the calling system |
| Token scope mismatch | Gateway returns 401 but the token is valid for a different service | Reissue with the correct scope |

**Postmortem:** if this is a recurring failure (≥3 in 24h), open an issue.
The API gateway does not implement token rotation; if your upstream
issuance system rotates tokens, the operator must coordinate the rotation
window with the gateway's restart.

---

## 4. Compose service won't start

**Symptom:** `docker compose up -d` hangs on a service, or a service exits
immediately after starting.

**Diagnostic:**
```bash
# Validate the compose file
docker compose config --quiet

# Try a single service with verbose output
docker compose up <service>

# Check for port conflicts
netstat -ano | grep -E ':(8000|4173|4174|8080) '
```

**Common root causes:**

| Cause | Evidence | Fix |
|---|---|---|
| Port already bound | `bind: address already in use` in logs | Kill the conflicting process or change the host binding in `compose.yaml` |
| Image not built | `image not found` | `docker compose build` first |
| `uv.lock` out of sync with `pyproject.toml` | `uv sync` fails inside the build | `uv lock` to regenerate the lock, commit, rebuild |
| Healthcheck timeout | Service is healthy but takes >30s to start | Increase `start_period` in the healthcheck stanza |
| Missing `.env` | Compose refuses to start because of unset `${VAR}` | Copy `.env.example` to `.env` and set required values |

**Postmortem:** if a single service consistently fails to start, the
build is the suspect; `docker compose build --no-cache <service>` to rule
out a stale layer.

---

## 5. Atlas replay fails

**Symptom:** `tools/canonical_replay.py` reports `<N>/5 invariants passed`
where `N < 5`; or `GET /replay/status` returns `chain_intact: false`.

**Diagnostic:**
```bash
# Run the canonical replay with verbose output
python tools/canonical_replay.py --verbose

# Check the atlas audit log for the most recent replay event
tail -20 docs/internal/audit/atlas-audit.jsonl 2>/dev/null
```

**Common root causes:**

| Cause | Evidence | Fix |
|---|---|---|
| Atlas module not initialized | `AtlasInitError` in replay output | Restart the API service so `get_atlas()` factory runs |
| Replay bundle corrupted | `ReplaySystemError: hash mismatch` | Re-load the bundle from the most recent verified snapshot in `docs/audit/` |
| Subordination notice tampered | `ReplaySystemError: subordination notice mismatch` | **Stop.** The notice is bound to every replay hash. Revert the notice source. |
| Phase-mismatch (replay is for an older atlas version) | `ReplaySystemError: schema version mismatch` | Load a replay bundle from the same atlas version |

**Postmortem:** replay is the system's reconstruction primitive. Any
replay failure is a P1 incident.

---

## 6. Pytest suite fails after a commit

**Symptom:** `uv run pytest` shows failures or errors that were not present
in the previous baseline.

**Diagnostic:**
```bash
# Run with the same scope as the canonical gate
uv run pytest packages/ tools/tests/ -q --tb=short

# Compare to the last known-good count
git log --oneline -1 docs/internal/STAGE_*_ACCEPTANCE.md
```

**Common root causes:**

| Cause | Evidence | Fix |
|---|---|---|
| Genuine regression from your commit | Test failure names match files you touched | Fix the regression; do not silence the test |
| Pre-existing baseline drift | Failures exist at HEAD and at the pre-commit HEAD (`git stash`, re-run, compare) | Document as "pre-existing drift, out of scope for this wave" in the acceptance record |
| Test ordering | Test fails in isolation but passes in the full suite | Add the missing fixture or test ordering; do not `--randomly-seed` to paper over it |
| Environment drift | `uv.lock` and `pyproject.toml` disagree | `uv lock && uv sync --frozen` |

**Postmortem:** if pre-existing drift is found, fix it as a separate
`fix(types):` or `fix(test):` commit before the wave can land on a green
baseline. Per skill pitfall 16, "claim a verification failure is 'new'
without proving the baseline" is a failure mode.

---

## 7. CI is red on `main`

**Symptom:** a commit to `main` shows red CI; the local gates are green.

**Diagnostic:**
```bash
# Compare local gates to CI's last reported job
gh run list --limit 5
gh run view <run-id> --log-failed

# Re-run the failing job locally with the same command
# (the CI workflow files are the source of truth for command + scope)
cat .github/workflows/ci.yaml
```

**Common root causes:**

| Cause | Evidence | Fix |
|---|---|---|
| Pinning mismatch | Local uses different Python/Node/Rust than CI | Match the CI pins in your local `.python-version`, `rust-toolchain.toml`, `.nvmrc` |
| Caching difference | CI's `uv` cache is stale | `gh workflow run ci.yaml --ref main` to retrigger; cache rebuilds |
| Workflow file changed but job not re-triggered | Empty diff in source, but `.github/workflows/` shows recent change | The change is the cause; revert or fix |
| External blocker (e.g., GitHub billing lock) | CI jobs never start; status is "queued" indefinitely | See `docs/operations/CONTINUITY_MAP.md` for the current external-blocker list |

**Postmortem:** if the red CI was caused by a local-green / CI-red drift,
that's a gap in the verification recipe. Update the canonical gate
commands (in `STAGE_*_ACCEPTANCE.md` templates) to match the CI workflow
exactly.

---

## 8. Escalation

If you cannot resolve within 30 minutes:

1. Capture the diagnostic output from the matching section above.
2. Open a `P1` issue with the diagnostic output, the timestamp, and the
   service(s) affected.
3. Do not push to `main` until the issue is triaged.

The repo is single-owner; escalation here is asynchronous (issue tracker).
For constitutional / security incidents, use the private advisory channel
per `SECURITY.md` (root) — do not file a public issue.
