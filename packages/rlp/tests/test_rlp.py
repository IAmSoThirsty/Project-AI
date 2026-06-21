from __future__ import annotations

from collections.abc import Callable

import pytest
import rlp.rlp as implementation

from rlp import RLP, RLPDenied


def test_public_interface_is_experimental() -> None:
    assert RLP.__module__ == "rlp.rlp"
    assert issubclass(RLPDenied, Exception)


def test_embedded_invariant_suite() -> None:
    tests: list[Callable[[], None]] = [
        value
        for name, value in sorted(vars(implementation).items())
        if name.startswith("test_") and callable(value)
    ]
    assert len(tests) >= 13
    for test in tests:
        test()


def test_audit_and_debt_boundaries() -> None:
    clock = implementation.Clock()
    audit = implementation.AuditLog(clock)
    entry = audit.append("TEST", {"ok": True})
    assert audit.verify()
    entry.payload["ok"] = False
    assert not audit.verify()

    debt = implementation.LegitimacyDebt()
    debt.add("governor", clock(), "reason", 1.25)
    assert debt.total("governor") == 1.25
    assert debt.dossier("governor")[0].reason == "reason"


def test_reviewer_registry_lifecycle() -> None:
    clock = implementation.Clock()
    audit = implementation.AuditLog(clock)
    registry = implementation.ReviewerRegistry(["a", "b", "c"], audit, clock)
    assert registry.eligible_ids() == ["a", "b", "c"]
    registry.add("d", 0.6)
    assert registry.record("d").credibility == 0.6
    registry.record_votes("hold", {"a": True, "b": False})
    summary = registry.anchor("hold", ground_truth=True, governor_desired=False)
    assert summary["a"]["correct"] is True
    assert registry.dossier("b")["wrong"] == 1
    registry.remove("d")
    assert not registry.exists("d")
    with pytest.raises(RLPDenied, match="already anchored"):
        registry.anchor("hold", ground_truth=True, governor_desired=False)


def test_sealed_gate_validation_and_failure_result() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        implementation.SealedGate("domain", 1, {})
    gate = implementation.SealedGate(
        "domain", 1, {"probe": "expected"}, {"probe": "reasoning_quality"}, created_at=0.0
    )
    assert gate.is_stale(implementation.PROBE_MAX_AGE + 1)
    with pytest.raises(ValueError, match="non-empty"):
        gate.refresh({}, {}, 1.0)
    gate.refresh({"probe": "expected"}, {"probe": "reasoning_quality"}, 1.0)
    result = gate.evaluate(lambda _: "wrong", "seed")
    assert not result.passed
    assert result.dimension_scores["reasoning_quality"] == 0.0


def test_rlp_constructor_and_domain_rejections() -> None:
    with pytest.raises(ValueError, match="need >="):
        RLP("governor", "governed", ["one"], {})
    with pytest.raises(ValueError, match="may not be reviewers"):
        RLP("governor", "governed", ["governor", "a", "b"], {})
    engine, _ = implementation._build()
    with pytest.raises(RLPDenied, match="unknown domain"):
        engine._domain("missing")
    with pytest.raises(RLPDenied, match="unknown reviewer"):
        engine.mint_reviewer_token("missing", "action")


def test_token_rejection_and_safe_halt_recovery() -> None:
    engine, _ = implementation._build()
    token = engine._mint("subject", "operate", 1)
    forged = implementation.CapabilityToken(
        token.subject, token.action, token.level, token.nonce, "0" * 64
    )
    with pytest.raises(RLPDenied, match="hash mismatch"):
        engine._check_token(forged, "operate", 1)
    inactive = implementation.CapabilityToken.mint("subject", "operate", 1, "inactive")
    with pytest.raises(RLPDenied, match="not active"):
        engine._check_token(inactive, "operate", 1)
    with pytest.raises(RLPDenied, match="token action"):
        engine._check_token(token, "different", 1)
    with pytest.raises(RLPDenied, match="token level"):
        engine._check_token(token, "operate", 2)

    engine.safe_halt("test")
    assert engine.state.status == implementation.SystemStatus.SAFE_HALT
    reviewers = [
        engine.mint_reviewer_token(reviewer, "clear_safe_halt") for reviewer in ("rev_a", "rev_b")
    ]
    engine.clear_safe_halt(reviewers)
    assert engine.state.status == implementation.SystemStatus.NOMINAL
    with pytest.raises(RLPDenied, match="not in SAFE_HALT"):
        engine.clear_safe_halt(reviewers)
