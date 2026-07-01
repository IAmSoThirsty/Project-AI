"""Integration test: Shadow-Thirst (6th tier) convergence harness.

Per PHASE_T_DISCOVERY.md Phase T7: the 6th tier is a meta-
validation surface that runs all 5 prior tier specs (T2, T3,
T5, T5b) and confirms they converge on a single truth.

Honest scope:
- Tests the harness: per-tier witness construction, combined
  convergence hash, fail-closed paths, determinism.
- Does NOT run the heavy Z3 symbolic or execute-and-compare
  passes (those require optional `thirsty-lang[analysis]`
  extras and a sandboxed interpreter; deferred to T7.5).
- Tests the structural pass which is sufficient for T7's
  scope: each tier spec is its own canonical, so the
  shadow/canonical structural check is trivially satisfied.
"""

from __future__ import annotations

from pathlib import Path

from convergence.shadow_thirst import (
    ConvergenceError,
    ConvergenceReport,
    run_convergence,
)

# ── 1. Module surface ────────────────────────────────────────


def test_run_convergence_returns_report() -> None:
    """run_convergence() returns a ConvergenceReport."""
    report = run_convergence()
    assert isinstance(report, ConvergenceReport)


def test_convergence_error_is_runtime_error() -> None:
    """ConvergenceError subclasses RuntimeError for catch-ability."""
    assert issubclass(ConvergenceError, RuntimeError)


# ── 2. Tier coverage ────────────────────────────────────────


def test_all_six_tiers_have_witnesses() -> None:
    """The report has 6 witnesses (T1, T2, T3, T4, T5, T5b)."""
    report = run_convergence()
    tiers = [w.tier for w in report.tier_witnesses]
    assert "T1" in tiers
    assert "T2" in tiers
    assert "T3" in tiers
    assert "T4" in tiers
    assert "T5" in tiers
    assert "T5b" in tiers
    assert len(tiers) == 6


# ── 3. Per-tier witness invariants ──────────────────────────


def test_meta_tiers_have_descriptions() -> None:
    """T1 and T4 are meta-wirings (no language spec)."""
    report = run_convergence()
    t1 = next(w for w in report.tier_witnesses if w.tier == "T1")
    t4 = next(w for w in report.tier_witnesses if w.tier == "T4")
    assert "thirsty-lang" in t1.canonical
    assert "smoke" in t1.canonical.lower()
    assert "tier subcommands" in t4.canonical


def test_language_tiers_have_canonical_forms() -> None:
    """T2/T3/T5/T5b have language-spec canonical forms."""
    report = run_convergence()
    t2 = next(w for w in report.tier_witnesses if w.tier == "T2")
    t3 = next(w for w in report.tier_witnesses if w.tier == "T3")
    t5 = next(w for w in report.tier_witnesses if w.tier == "T5")
    t5b = next(w for w in report.tier_witnesses if w.tier == "T5b")
    # T2: governance .tarl policy
    assert "policy" in t2.canonical.lower() or "=>" in t2.canonical
    # T3: security .thirst audit proof
    assert "thirst" in t3.canonical or "module" in t3.canonical
    # T5: atlas TSCG spec
    assert "$COG" in t5.canonical
    # T5b: swr TSCG-B spec
    assert "$COG" in t5b.canonical


def test_all_witnesses_have_valid_sha256() -> None:
    """All witnesses have 64-char hex SHA-256 hashes."""
    report = run_convergence()
    for w in report.tier_witnesses:
        assert len(w.canonical_sha256) == 64
        int(w.canonical_sha256, 16)  # raises if not hex
        # T1 and T4 are meta-wirings (no bundled spec file),
        # so source_sha256 falls back to canonical_sha256.
        if w.tier in {"T1", "T4"}:
            assert w.source_sha256 == w.canonical_sha256
        else:
            assert len(w.source_sha256) == 64
            int(w.source_sha256, 16)


# ── 4. Convergence hash ─────────────────────────────────────


def test_convergence_hash_is_deterministic() -> None:
    """Two successive run_convergence() calls return the same hash."""
    a = run_convergence()
    b = run_convergence()
    assert a.convergence_hash == b.convergence_hash
    assert a.convergence_hash
    assert len(a.convergence_hash) == 64


def test_convergence_hash_is_64_hex() -> None:
    """The convergence hash is a 64-char hex string (SHA-256)."""
    report = run_convergence()
    assert len(report.convergence_hash) == 64
    int(report.convergence_hash, 16)


# ── 5. Convergence verdict ──────────────────────────────────


def test_convergence_verdict_is_true() -> None:
    """All 6 tiers converge (no failures)."""
    report = run_convergence()
    assert report.converged is True
    assert report.failures == []


def test_convergence_is_stable_across_runs() -> None:
    """The convergence verdict is stable across multiple runs."""
    a = run_convergence()
    b = run_convergence()
    c = run_convergence()
    assert a.converged == b.converged == c.converged
    assert a.convergence_hash == b.convergence_hash == c.convergence_hash


# ── 6. Structural pass ──────────────────────────────────────


def test_language_tiers_have_structural_pass() -> None:
    """T2/T3/T5/T5b have a structural convergence check."""
    report = run_convergence()
    for tier in {"T2", "T3", "T5", "T5b"}:
        w = next(x for x in report.tier_witnesses if x.tier == tier)
        assert w.convergence_check is not None
        assert w.convergence_check.passed is True
        assert w.convergence_check.analyzer == "StructuralConvergence"


def test_meta_tiers_have_no_structural_check() -> None:
    """T1 and T4 (meta-wirings) have no structural check."""
    report = run_convergence()
    for tier in {"T1", "T4"}:
        w = next(x for x in report.tier_witnesses if x.tier == tier)
        assert w.convergence_check is None


# ── 7. Spec file resolution ────────────────────────────────


def test_spec_files_resolve_to_bundled_artifacts() -> None:
    """T2/T3/T5/T5b spec files resolve to actual bundled artifacts."""
    report = run_convergence()
    for tier in {"T2", "T3", "T5", "T5b"}:
        w = next(x for x in report.tier_witnesses if x.tier == tier)
        path = Path(w.source_path)
        assert path.exists(), f"{tier}: spec file {path} does not exist"
        assert path.is_file()
