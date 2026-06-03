"""Phase 4 execution router silent-bypass hardening tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core import execution_router
from app.core.evidence_bundle import EvidenceBundleValidator, get_evidence_store
from app.core.governance_observability import get_collector


class _Waterfall:
    def filter(self, context):
        return SimpleNamespace(allowed=True, reason="ok", context=dict(context))


class _InvariantEngine:
    def validate(self, context):
        return None


class _Forge:
    def process(self, payload):
        return {"success": True}


class _RecordingGate:
    def __init__(self):
        self.calls = 0
        self.contexts = []

    def execute(self, domain, action, context, executor_fn):
        self.calls += 1
        self.contexts.append(dict(context))
        return True, executor_fn(context)


class _StateRegister:
    def __init__(self, temporal_context=None, exc=None):
        self.temporal_context = temporal_context or {
            "session_id": "sess-1",
            "continuity_hash_verified": True,
        }
        self.exc = exc

    def get_temporal_context(self):
        if self.exc is not None:
            raise self.exc
        return self.temporal_context


@pytest.fixture(autouse=True)
def clear_receipts():
    get_collector().clear()
    get_evidence_store()._bundles.clear()
    yield
    get_collector().clear()
    get_evidence_store()._bundles.clear()


def _install_router_harness(monkeypatch):
    gate = _RecordingGate()
    monkeypatch.setattr(execution_router, "get_waterfall_filter", lambda: _Waterfall())
    monkeypatch.setattr(execution_router, "liara_ttl_check", lambda context: None)
    monkeypatch.setattr(execution_router, "get_liara_context", lambda: {})
    monkeypatch.setattr(execution_router, "get_invariant_engine", lambda: _InvariantEngine())
    monkeypatch.setattr(execution_router, "get_execution_gate", lambda: gate)
    monkeypatch.setattr(execution_router, "Forge", _Forge)
    _set_runtime(monkeypatch)
    _set_state(monkeypatch)
    _set_tarl(monkeypatch)
    return gate


def _set_runtime(monkeypatch, *, exc=None, verdict="allow", reason="runtime ok"):
    import app.governance.runtime_enforcer as runtime_enforcer

    class Runtime:
        def enforce(self, context):
            if exc is not None:
                raise exc
            return SimpleNamespace(verdict=verdict, reason=reason)

    if exc is not None and verdict == "lookup":
        def get_runtime_enforcer():
            raise exc
    else:
        def get_runtime_enforcer():
            return Runtime()

    monkeypatch.setattr(runtime_enforcer, "get_runtime_enforcer", get_runtime_enforcer)


def _set_state(monkeypatch, *, temporal_context=None, exc=None):
    monkeypatch.setattr(
        execution_router,
        "get_state_register",
        lambda: _StateRegister(temporal_context=temporal_context, exc=exc),
    )


def _set_tarl(
    monkeypatch,
    *,
    trust_score=0.72,
    trust_exc=None,
    adv_flags=None,
    adv_exc=None,
):
    import app.core.tarl_operational_extensions as tarl_extensions

    class TrustScoringEngine:
        def calculate_trust_score(self, entity, factors):
            if trust_exc is not None:
                raise trust_exc
            return trust_score, "trust ok"

    class AdversarialPatternRegistry:
        def detect_patterns(self, input_text):
            if adv_exc is not None:
                raise adv_exc
            return list(adv_flags or [])

    monkeypatch.setattr(tarl_extensions, "TrustScoringEngine", TrustScoringEngine)
    monkeypatch.setattr(
        tarl_extensions,
        "AdversarialPatternRegistry",
        AdversarialPatternRegistry,
    )


def _executor_counter():
    calls = {"count": 0}

    def executor(context):
        calls["count"] += 1
        return {"executed": True}

    return calls, executor


def _latest_bundle():
    return get_evidence_store().latest()


def _latest_observation():
    return get_collector().get_latest(1)[0]


def _assert_latest_bundle_valid(expected_outcome):
    bundle_dict = _latest_bundle()
    assert bundle_dict["final_outcome"] == expected_outcome
    assert bundle_dict["final_outcome"] != "BYPASS_RECORDED"

    writer_bundle = SimpleNamespace(**bundle_dict)
    writer_bundle.to_json = lambda: "{}"
    ok, errors = EvidenceBundleValidator().validate(writer_bundle)
    assert ok, errors


def test_runtime_enforcer_exception_denies_without_executor_or_gate(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_runtime(monkeypatch, exc=RuntimeError("runtime lookup offline"), verdict="lookup")
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute("tests", "get_status", {}, executor)

    assert not ok
    assert "RuntimeEnforcer failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
    _assert_latest_bundle_valid("DENY")
    obs = _latest_observation()
    assert obs["final_outcome"] == "DENY"
    assert obs["metadata"]["failure_source"] == "runtime_enforcer"
    assert obs["metadata"]["bypass_recorded"] is True


def test_runtime_enforcer_enforce_exception_denies_without_executor(monkeypatch):
    _install_router_harness(monkeypatch)
    _set_runtime(monkeypatch, exc=RuntimeError("enforce offline"))
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute("tests", "inspect_status", {}, executor)

    assert not ok
    assert "RuntimeEnforcer failed closed" in reason
    assert calls["count"] == 0
    _assert_latest_bundle_valid("DENY")


def test_runtime_enforcer_explicit_deny_behavior_remains_unchanged(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_runtime(monkeypatch, verdict="deny", reason="denied by RuntimeEnforcer")
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute("tests", "get_status", {}, executor)

    assert not ok
    assert reason == "RuntimeEnforcer denied: denied by RuntimeEnforcer"
    assert calls["count"] == 0
    assert gate.calls == 0
    assert _latest_bundle() is None


def test_state_register_exception_denies_mutating_without_executor(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_state(monkeypatch, exc=RuntimeError("state offline"))
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute(
        "tests",
        "write_data",
        {"user_id": "alice"},
        executor,
    )

    assert not ok
    assert "StateRegister failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
    _assert_latest_bundle_valid("DENY")


def test_state_register_exception_read_only_diagnostic_records_degraded_path(
    monkeypatch,
):
    gate = _install_router_harness(monkeypatch)
    _set_state(monkeypatch, exc=RuntimeError("state offline"))
    calls, executor = _executor_counter()

    ok, result = execution_router.execute(
        "tests",
        "get_status",
        {"user_id": "alice", "is_mutating_action": False},
        executor,
    )

    assert ok
    assert result == {"executed": True}
    assert calls["count"] == 1
    assert gate.calls == 1
    ctx = gate.contexts[-1]
    assert ctx["_temporal_unavailable"] is True
    assert ctx["_router_bypass_records"][-1]["failure_source"] == "state_register"
    _assert_latest_bundle_valid("DEGRADED_READ_ONLY")
    obs = _latest_observation()
    assert obs["metadata"]["non_authoritative_warning"] is True


def test_state_register_no_active_session_remains_explicit_context(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_state(monkeypatch, temporal_context={"error": "No active session"})
    calls, executor = _executor_counter()

    ok, _ = execution_router.execute("tests", "get_status", {}, executor)

    assert ok
    assert calls["count"] == 1
    assert gate.contexts[-1]["_temporal"] == {"error": "No active session"}
    assert "_temporal_unavailable" not in gate.contexts[-1]


def test_state_register_mutability_classification_failure_fails_closed(
    monkeypatch,
):
    import app.core.degraded_mode as degraded_mode

    gate = _install_router_harness(monkeypatch)
    _set_state(monkeypatch, exc=RuntimeError("state offline"))
    monkeypatch.setattr(
        degraded_mode,
        "classify_action_mutability",
        lambda action, context: (_ for _ in ()).throw(RuntimeError("classifier down")),
    )
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute(
        "tests",
        "get_status",
        {"is_mutating_action": False},
        executor,
    )

    assert not ok
    assert "StateRegister failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
    _assert_latest_bundle_valid("DENY")


def test_trust_scoring_failure_denies_payload_bearing_execution(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_tarl(monkeypatch, trust_exc=RuntimeError("trust offline"))
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute(
        "tests",
        "get_status",
        {"is_mutating_action": False, "payload": "meaningful user input"},
        executor,
    )

    assert not ok
    assert "Trust/adversarial context failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
    _assert_latest_bundle_valid("DENY")


def test_adversarial_registry_failure_denies_mutating_execution(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_tarl(monkeypatch, adv_exc=RuntimeError("adversarial scan offline"))
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute(
        "tests",
        "write_data",
        {"user_id": "alice"},
        executor,
    )

    assert not ok
    assert "Trust/adversarial context failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
    _assert_latest_bundle_valid("DENY")


def test_trust_failure_read_only_diagnostic_records_degraded_markers(
    monkeypatch,
):
    gate = _install_router_harness(monkeypatch)
    _set_tarl(monkeypatch, trust_exc=RuntimeError("trust offline"))
    calls, executor = _executor_counter()

    ok, _ = execution_router.execute(
        "tests",
        "inspect_status",
        {"is_mutating_action": False},
        executor,
    )

    assert ok
    assert calls["count"] == 1
    ctx = gate.contexts[-1]
    assert ctx["_trust_score_unavailable"] is True
    assert ctx["_adversarial_flags"] == []
    assert ctx["_router_bypass_records"][-1]["failure_source"] == (
        "trust_adversarial_context"
    )
    _assert_latest_bundle_valid("DEGRADED_READ_ONLY")


def test_partial_trust_adversarial_failure_preserves_successful_signal(
    monkeypatch,
):
    gate = _install_router_harness(monkeypatch)
    _set_tarl(monkeypatch, trust_score=0.81, adv_exc=RuntimeError("scan offline"))
    calls, executor = _executor_counter()

    ok, _ = execution_router.execute(
        "tests",
        "get_status",
        {"is_mutating_action": False},
        executor,
    )

    assert ok
    assert calls["count"] == 1
    ctx = gate.contexts[-1]
    assert ctx["_trust_score"] == 0.81
    assert "_trust_score_unavailable" not in ctx
    assert ctx["_adversarial_flags_unavailable"] is True
    assert ctx["_router_bypass_records"][-1]["failed_components"] == [
        "adversarial_pattern_registry"
    ]
    _assert_latest_bundle_valid("DEGRADED_READ_ONLY")


def test_successful_router_path_injects_temporal_trust_and_adversarial_context(
    monkeypatch,
):
    gate = _install_router_harness(monkeypatch)
    _set_tarl(monkeypatch, trust_score=0.9, adv_flags=[{"pattern_id": "p1"}])
    calls, executor = _executor_counter()

    ok, _ = execution_router.execute("tests", "get_status", {}, executor)

    assert ok
    assert calls["count"] == 1
    ctx = gate.contexts[-1]
    assert ctx["_temporal"]["continuity_hash_verified"] is True
    assert ctx["_trust_score"] == 0.9
    assert ctx["_adversarial_flags"] == [{"pattern_id": "p1"}]


def test_evidence_emission_failure_prevents_degraded_continuation(monkeypatch):
    gate = _install_router_harness(monkeypatch)
    _set_state(monkeypatch, exc=RuntimeError("state offline"))
    monkeypatch.setattr(
        execution_router,
        "_emit_router_precheck_receipt",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("receipt down")),
        raising=False,
    )
    calls, executor = _executor_counter()

    ok, reason = execution_router.execute(
        "tests",
        "get_status",
        {"is_mutating_action": False},
        executor,
    )

    assert not ok
    assert "receipt emission failed closed" in reason
    assert calls["count"] == 0
    assert gate.calls == 0
