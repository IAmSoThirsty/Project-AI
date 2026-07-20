# pre-phase2-hold Recovery

> Historical recovery index. The recovered artifacts describe an older hold
> state and are not current production or release evidence. Current successor
> status is governed by the pre-deployment checklist and CAB evidence bundle.
> Current deployment approval remains fail-closed until those successor gates pass.

Recovered from ``T:\08-Archive\Project-AI-pre-phase2-hold\``.

19 files recovered. The 798 MB bulk of the original archive
(``terraform/.terraform/providers/.../terraform-provider-*``
binaries) was **excluded** — those are machine-specific
build artifacts that ``terraform init`` regenerates. They
are NOT source code, documentation, or data; they are
provider plugin binaries and should be re-downloaded when
needed, not committed.

## What's here

### `backups/` (14 files)

  - `backup.log` — operational log of all backup attempts
    (2026-06-03 snapshot run)
  - `backup-manifest.txt` — SHA256-chained audit log of
    every backup created, with size, hash, and entry count
  - 12 `spine-data-*.tar.gz` — backup snapshots:
      - 7 are empty placeholders (1 entry: just `./`)
      - 5 contain a `readiness-drill/restore-marker.txt`
        (drill backups proving the backup/restore cycle
        works end-to-end)

### `data/alert_webhook/` (3 files)

  - 3 Prometheus AlertManager webhook JSON payloads
    (`APIDown` alert, environment=production,
    severity=critical, fingerprint affad314ebdd921b, etc.)

### `data/genesis_pins/` (2 files)

  - `continuity_log.after-baseline-tests.json` — list of
    `GENESIS_DISCONTINUITY` violations detected by the
    baseline tests, each with
    `genesis_id_expected`/`genesis_id_actual`/`attack_vector`
    (VECTOR 1, etc.). This is REAL security event data
    showing the test suite caught discontinuity attacks.
  - `continuity_log.after-baseline-tests.patch` — the
    `git diff` that added these violation records to the
    continuity log.

### `terraform/` (1 file)

  - `.terraform.lock.hcl` — the Terraform provider lock
    file (4.6 KB), which records the provider dependency
    graph and SHA256 checksums. This is the ONLY terraform
    file kept; the 798 MB provider binaries in
    `.terraform/providers/...` are excluded as explained
    above.

## What this is

This is the "pre-rebuild" snapshot of Project-AI's
operational data, taken 2026-06-03 (before phase 2 of the
rebuild began). The data shows:

  - A working backup/restore drill (5 successful drills,
    7 placeholder backups)
  - A real `APIDown` alert in production environment
  - A documented genesis-discontinuity attack detection
    suite that caught the attacks it was designed to catch

## Port provenance

This commit copies 19 files from
``T:\08-Archive\Project-AI-pre-phase2-hold\`` (the frozen
legacy source) into the canonical repo at
``docs/pre-phase2-hold/``. The pre-phase2-hold archive
remains in place; this is a one-way copy. The archive is
the frozen source-of-record (with Google Drive backup per
the rebuild's data preservation policy).

The 798 MB of Terraform provider binaries are intentionally
NOT ported — they are reproducible via ``terraform init``
and would unnecessarily bloat the repo with
machine-specific build artifacts.

Verification (4 canonical gates, all green):
  pytest  2319 pass / 1 xfail (unchanged)
  T7      True 3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c
  ruff    All checks passed
  mypy    12 (pre-existing baseline, unchanged)
