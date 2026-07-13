"""Integration test: Shadow-Thirst (T7) convergence harness.

Per PHASE_T_DISCOVERY.md Phase T7: `convergence.shadow_thirst.run_convergence()`
is the meta-validation surface that loads the T2 (governance), T3 (security),
T5 (atlas), and T5b (swr) language-tier specs plus the T1/T4 meta-wirings, and
asserts they converge on a single combined SHA-256 (the convergence hash).

This is the one test surface that actually calls `run_convergence()`
end-to-end against the real sibling packages (governance, security, atlas,
swr) rather than mocking their loaders, since the harness's whole purpose is
cross-package integration.

Honest scope:
- Tests `run_convergence()` end-to-end against the real bundled tier specs.
- Tests `TierWitness` / `ConvergenceReport` field invariants (SHA-256 shape,
  witness count, tier ordering, deterministic convergence hash).
- Tests the fail-closed paths: `_witness_loader_tier` raises `ConvergenceError`
  on an unimportable loader module and on a missing spec file, rather than
  silently skipping the tier.
- Does NOT test the Z3 symbolic or execute-and-compare passes — both are
  explicitly out of T7's scope (deferred to T7.5 per PHASE_T_DISCOVERY.md)
  and are not implemented in `shadow_thirst.py`.
- Does NOT re-test the individual tier loaders' own internals (governance's
  TARL bridge, security's proof-obligation extractor, atlas/swr's tscg
  loaders) — those have their own dedicated integration tests
  (`test_governance_tarl_bridge_integration.py`,
  `test_security_proof_obligations_integration.py`,
  `test_atlas_tscg_spec_integration.py`, `test_swr_tscg_b_spec_integration.py`).
"""

from __future__ import annotations

import pytest
from convergence.shadow_thirst import (
    ConvergenceError,
    ConvergenceReport,
    TierWitness,
    _witness_loader_tier,
    _witness_meta_tier,
    run_convergence,
)


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


class TestRunConvergenceEndToEnd:
    def test_converges_against_real_sibling_packages(self) -> None:
        report = run_convergence()

        assert isinstance(report, ConvergenceReport)
        assert report.converged is True, report.failures
        assert report.failures == []

    def test_witness_order_and_tier_labels(self) -> None:
        report = run_convergence()

        # T1 (meta) first, then the T2/T3/T5/T5b language-tier specs in
        # declaration order, then T4 (meta) last — matches run_convergence()'s
        # append order: T1, loop over _TIER_SOURCES, T4.
        assert [w.tier for w in report.tier_witnesses] == ["T1", "T2", "T3", "T5", "T5b", "T4"]

    def test_every_witness_has_valid_sha256_fields(self) -> None:
        report = run_convergence()

        for witness in report.tier_witnesses:
            assert isinstance(witness, TierWitness)
            assert _is_sha256(witness.canonical_sha256), witness.tier
            assert _is_sha256(witness.source_sha256), witness.tier
            assert witness.canonical, witness.tier

    def test_language_tier_witnesses_carry_a_passed_structural_check(self) -> None:
        report = run_convergence()

        language_tiers = {"T2", "T3", "T5", "T5b"}
        checked = {w.tier for w in report.tier_witnesses if w.convergence_check is not None}
        assert checked == language_tiers
        for witness in report.tier_witnesses:
            if witness.convergence_check is not None:
                assert witness.convergence_check.passed is True

    def test_meta_tier_witnesses_have_no_structural_check(self) -> None:
        report = run_convergence()

        meta_witnesses = [w for w in report.tier_witnesses if w.tier in {"T1", "T4"}]
        assert len(meta_witnesses) == 2
        for witness in meta_witnesses:
            assert witness.convergence_check is None
            assert witness.source_path == "(meta-wiring: no bundled spec file)"

    def test_convergence_hash_is_deterministic(self) -> None:
        first = run_convergence()
        second = run_convergence()

        assert first.convergence_hash == second.convergence_hash
        assert _is_sha256(first.convergence_hash)

    def test_convergence_hash_matches_concatenation_of_witness_hashes(self) -> None:
        import hashlib

        report = run_convergence()
        expected = hashlib.sha256(
            "".join(w.canonical_sha256 for w in report.tier_witnesses).encode("utf-8")
        ).hexdigest()

        assert report.convergence_hash == expected


class TestMetaTierWitness:
    def test_meta_witness_is_self_consistent(self) -> None:
        witness = _witness_meta_tier("T1", "workspace dep: thirsty-lang==0.8.1 + 15-test smoke")

        assert witness.tier == "T1"
        assert witness.canonical == "workspace dep: thirsty-lang==0.8.1 + 15-test smoke"
        assert witness.source_sha256 == witness.canonical_sha256
        assert _is_sha256(witness.canonical_sha256)
        assert witness.convergence_check is None


class TestFailClosedPaths:
    def test_unimportable_loader_module_raises_convergence_error(self) -> None:
        with pytest.raises(ConvergenceError, match="cannot import loader"):
            _witness_loader_tier(
                "T2",
                "governance.this_module_does_not_exist_xyz",
                "project_ai_governance.tarl",
                "evaluate_policy",
                False,
            )

    def test_unknown_tier_raises_convergence_error(self) -> None:
        with pytest.raises(ConvergenceError, match="unknown tier"):
            _witness_loader_tier(
                "T9",
                "governance.tarl_bridge",
                "project_ai_governance.tarl",
                "evaluate_policy",
                False,
            )

    def test_missing_spec_file_raises_convergence_error(self) -> None:
        # governance.tarl_bridge is a real, importable loader, but pointed at
        # a spec filename that does not exist next to it: the harness must
        # fail closed (raise) rather than silently produce an empty witness.
        with pytest.raises(ConvergenceError, match="does not exist"):
            _witness_loader_tier(
                "T2",
                "governance.tarl_bridge",
                "this_spec_file_does_not_exist.tarl",
                "evaluate_policy",
                False,
            )
