# Cerberus Reconciliation Matrix (C0)

- **Status:** COMPLETE (this document is the C0 deliverable of the corrected Cerberus
  integration plan in `INTEGRATION_VERIFICATION_CERBERUS_WATERFALL.md`).
- **Trees compared:**
  - Ours: `packages/cerberus/src/cerberus` at PAB `main` `0ab1bbae`
    (ported wave `fcf0ec72`, later hardened in `23c4b9b4`).
  - Theirs: `T:\00-Active\Cerberus\src\cerberus` (`cerberus-guard-bot` 0.1.0) at `4d3400c`.
- **Method:** full file inventory both trees; `git diff --no-index` per shared file;
  public-surface extraction (classes / defs / module constants) diffed per module; targeted
  source reads for every candidate delta. Evidence quoted per row.
- **Frozen contract:** `cerberus.security.modules.auth.PasswordHasher` — imported by
  `packages/accounts` for human password hashing. Its behavior and stored-hash format
  (`pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>`) must not change; `accounts` hashing
  tests must pass unchanged after C1.

## Correction to the prior verification doc (honest scope, v3 §5)

`INTEGRATION_VERIFICATION_CERBERUS_WATERFALL.md` described the external delta as
"encryption, sandbox, promoted statistical guardian, and an evolved `config.py` +
hub spawn/rate-limit logic". C0's file-level diff **narrows** that: the in-repo hub
already carries the token-bucket + per-source spawn rate limiting (same lineage) and
additionally has `health_check()`, which the external tree lacks. The external
`config.py` is a pydantic-settings variant of the same fields, not a feature superset.
Neither is ported. The genuine external delta is listed under "take-theirs / merge" below.

## Matrix

| Module | Disposition | Evidence |
| --- | --- | --- |
| `__init__.py` (pkg root) | keep-ours | Ours exports the PAB-native surface incl. `agent`/`lockdown`/`spawn_constraints`; theirs is a smaller upstream export list. |
| `agent.py`, `lockdown.py`, `spawn_constraints.py`, `py.typed` | keep-ours (in-repo only) | Absent from external tree; PAB-native Q5 closure modules. |
| `config.py` | keep-ours | Ours: frozen dataclass + `from_env` + range validation + `get/set/reset_settings` (used by hub and tests). Theirs: pydantic-settings `BaseSettings` with 2 validators — same fields, new runtime dep, no feature gain. |
| `logging_config.py` | keep-ours | Public surface identical; diff is docstring/style only. |
| `main.py` | keep-ours | Theirs adds `__sovereign_execute__` (thirsty-lang app binding — application-specific, not workspace library surface). Ours keeps `DEMO_INPUTS` demo CLI. |
| `guardians/__init__.py` | keep-ours (updated exports only if needed) | Surface parity after 4d3400c removed their duplicate `*_guardian.py` files. |
| `guardians/base.py` | **merge** | Take theirs' optional `ThreatReport.metadata: dict[str, Any] \| None = None` field; keep ours' fail-closed invariant (non-blocking HIGH/CRITICAL rejected) and confidence bounds. |
| `guardians/heuristic.py`, `pattern.py`, `strict.py` | keep-ours | Public surface identical; diffs are style/docstrings. |
| `guardians/statistical.py` (theirs: `statistical_guardian.py`) | **merge** | Ours is the repaired port (upstream `_create_report` bug fixed, `should_block >= HIGH` fail-closed pairing). Theirs' 4d3400c promotion attaches `metadata` (computed_stats, anomalies, max/avg z) — take that enrichment into ours. |
| `hub/__init__.py`, `hub/coordinator.py` | keep-ours | Ours has `health_check()` + `_fields` structured-logging helper; token-bucket + per-source rate limiting present in BOTH trees (same lineage). No external feature absent from ours. |
| `security/__init__.py` | **merge (exports)** | Add `encryption` + `sandbox` exports; replace the "Deferred (not ported)" docstring note — C1 completes that declared deferral. |
| `security/modules/__init__.py` | keep-ours (docstring update) | One-line docstring; "stdlib-only subset" wording becomes stale after C1. |
| `security/modules/audit_logger.py` | **merge** | Ours: HMAC-signed entries, `verify_log_integrity`, context manager, `AuditMetrics`. Theirs adds only 3 thin wrappers — `log_rate_limit`, `log_config_change`, `log_guardian_spawned` (event types already exist in ours' `AuditEventType`). Take the 3 wrappers. |
| `security/modules/auth.py` | **keep-ours (FROZEN)** | Theirs is the upstream original: bcrypt dep, naive `datetime.now()`, `except Exception`, and a password-reuse check that tests hash *membership* instead of verifying candidate against previous hashes (bug). Ours is the hardened rebuild (PBKDF2-600k, constant-time verify, aware UTC, fixed reuse check). `accounts` contract frozen. |
| `security/modules/encryption.py` | **take-theirs (adapted)** | New module (absent in ours; deferral documented in ours' `security/__init__.py`). Adaptations required: explicit `key_dir` (upstream defaults to `/var/lib/cerberus/keys` and mkdirs at import-adjacent init — unacceptable library default, wrong on Windows), aware-UTC datetimes with naive-on-load coercion, strict typing, `cryptography>=42.0` declared in `packages/cerberus/pyproject.toml`. `keys.json` schema kept upstream-compatible. |
| `security/modules/input_validation.py` | keep-ours | Ours covers all 9 attack categories incl. `PROMPT_INJECTION` and `JAILBREAK` (table-driven `_compile`); theirs is the same coverage organized as per-category `_check_*` methods. No category theirs has that ours lacks. |
| `security/modules/monitoring.py` | keep-ours | Ours adds `check_stale_alerts`; theirs has no extra surface. |
| `security/modules/rate_limiter.py` | **merge (reimplemented, not copied)** | Theirs' only extra surface, `cleanup_expired`, is a STUB: `with self.lock: pass` under a comment "For now, we'll keep all limiters" — fake functionality (v3 §29). Not ported as-is. Ours gains a REAL `cleanup_expired(max_age_seconds)` with last-access tracking (ours' per-source `_limiters` map currently grows unbounded — genuine hygiene gap). |
| `security/modules/rbac.py` | keep-ours | Theirs adds a `require_permission` *decorator*; ours already has a raising `RBACManager.require_permission(user_id, permission)` method — same name, different shape; adopting both would collide. No PAB consumer needs the decorator form. Recorded omission. |
| `security/modules/sandbox.py` | **take-theirs (adapted)** | New module (deferral documented in ours). Adaptations: exception chaining (`raise ... from e`), strict typing, honest-scope docstring — in-process `AgentSandbox`/`PluginSandbox` are best-effort restriction helpers, NOT isolation boundaries (regex blocklist is bypassable; POSIX rlimits are process-wide and a no-op on Windows); `execute_code` (subprocess) and `ContainerSandbox` (Docker, fail-closed when absent) are the isolation forms. Consequential execution still routes only through the canonical `ExecutionGate`. |
| `security/modules/threat_detector.py` | keep-ours | Same signature data; ours ships signatures as a typed module constant, theirs builds them in `_load_default_signatures`. No signature theirs has that ours lacks (verified by surface + targeted read). |

## Out of scope (external repo content not under `src/cerberus`)

`src/core/integrated_specs/*` (thirsty-lang sovereign bindings), `web/`, cPanel deploy
config: application/deployment surfaces of the standalone bot, not part of the guard
framework reconciliation. Untouched.

## C1 execution scope derived from this matrix

1. `guardians/base.py`: add optional `metadata` field to `ThreatReport`.
2. `guardians/statistical.py`: attach statistical metadata to reports.
3. `security/modules/audit_logger.py`: add 3 convenience wrappers.
4. `security/modules/rate_limiter.py`: real `cleanup_expired` with last-access tracking.
5. New `security/modules/encryption.py` + `security/modules/sandbox.py` (adapted ports).
6. `security/__init__.py` + `modules/__init__.py` export/docstring updates;
   `packages/cerberus/pyproject.toml` gains `cryptography>=42.0`; `uv.lock` regenerated.
7. New tests: `test_cerberus_encryption.py`, `test_cerberus_sandbox.py`; extensions to
   guardians/security tests for items 1-4.

Acceptance (from the corrected plan): `uv run pytest packages/cerberus packages/accounts`
green; strict mypy green; ruff clean; `accounts` hashing tests byte-identical behavior;
the `cerberus` import stays single-sourced (no external distribution installed).

## Session isolation note (v3 §5 — concurrent lane)

At C0 time, another agent's work is in flight in this working tree: commit `0ab1bbae`
plus staged-but-uncommitted `packages/thirstys-standard-v3q/**` files and an unstaged
root `pyproject.toml` edit declaring that package as a workspace member; `uv lock
--check` currently FAILS repo-wide because of that in-flight manifest edit (not this
lane). C0/C1 commits therefore use explicit pathspecs only, `pre-commit` runs scoped
`--files` (not `--all-files`), and the C1 `uv.lock` regeneration is performed with the
foreign root-manifest edit temporarily stashed so the committed lock matches the
committed manifest exactly. The foreign edit is restored immediately after.
