"""Unit tests for temporal dataclasses + activities (Phase I1)."""

from __future__ import annotations

import pytest

from temporal import (
    ActivityError,
    RetryPolicy,
    SecurityAgentRequest,
    SecurityAgentResult,
    TemporalValidationError,
    TriumvirateRequest,
    TriumvirateResult,
    new_correlation_id,
    run_activity,
    run_security_agent_scan,
    run_triumvirate_pipeline,
)

# ---------------------------------------------------------------------------
# TriumvirateRequest
# ---------------------------------------------------------------------------


def test_triumvirate_request_minimal() -> None:
    req = TriumvirateRequest(input_data="hello")
    assert req.input_data == "hello"
    assert req.timeout_seconds == 300
    assert req.max_retries == 3


def test_triumvirate_request_with_context() -> None:
    req = TriumvirateRequest(
        input_data="x",
        context={"k": "v"},
        timeout_seconds=10,
        max_retries=1,
    )
    assert req.context == {"k": "v"}
    assert req.timeout_seconds == 10


def test_triumvirate_request_validates_timeout() -> None:
    with pytest.raises(TemporalValidationError, match="timeout_seconds"):
        TriumvirateRequest(input_data="x", timeout_seconds=0)


def test_triumvirate_request_validates_timeout_type() -> None:
    with pytest.raises(TemporalValidationError, match="timeout_seconds"):
        TriumvirateRequest(input_data="x", timeout_seconds="300")  # type: ignore[arg-type]


def test_triumvirate_request_validates_max_retries() -> None:
    with pytest.raises(TemporalValidationError, match="max_retries"):
        TriumvirateRequest(input_data="x", max_retries=-1)


def test_triumvirate_request_validates_empty_input() -> None:
    with pytest.raises(TemporalValidationError, match="input_data"):
        TriumvirateRequest(input_data="")


def test_triumvirate_request_validates_max_retries_bool() -> None:
    with pytest.raises(TemporalValidationError, match="max_retries"):
        TriumvirateRequest(input_data="x", max_retries=True)


# ---------------------------------------------------------------------------
# TriumvirateResult
# ---------------------------------------------------------------------------


def test_triumvirate_result_success() -> None:
    res = TriumvirateResult(success=True, output={"k": "v"})
    assert res.success is True
    assert res.output == {"k": "v"}


def test_triumvirate_result_failure() -> None:
    res = TriumvirateResult(success=False, error="oops")
    assert res.success is False
    assert res.error == "oops"


def test_triumvirate_result_validates_success_type() -> None:
    with pytest.raises(TemporalValidationError, match="success must be bool"):
        TriumvirateResult(success="true")  # type: ignore[arg-type]


def test_triumvirate_result_rejects_success_with_error() -> None:
    with pytest.raises(TemporalValidationError, match="must not have error"):
        TriumvirateResult(success=True, error="oops")


def test_triumvirate_result_requires_error_on_failure() -> None:
    with pytest.raises(TemporalValidationError, match="must have an error"):
        TriumvirateResult(success=False)


def test_triumvirate_result_validates_duration() -> None:
    with pytest.raises(TemporalValidationError, match="duration_ms"):
        TriumvirateResult(success=True, duration_ms=-1.0)


# ---------------------------------------------------------------------------
# SecurityAgentRequest / Result
# ---------------------------------------------------------------------------


def test_security_agent_request_minimal() -> None:
    req = SecurityAgentRequest(agent_id="agent-1", target="/etc/passwd", operation="scan")
    assert req.agent_id == "agent-1"
    assert req.target == "/etc/passwd"
    assert req.operation == "scan"
    assert req.correlation_id  # auto-generated


def test_security_agent_request_validates_agent_id() -> None:
    with pytest.raises(TemporalValidationError, match="agent_id"):
        SecurityAgentRequest(agent_id="", target="/x", operation="scan")


def test_security_agent_request_validates_target() -> None:
    with pytest.raises(TemporalValidationError, match="target"):
        SecurityAgentRequest(agent_id="a", target="", operation="scan")


def test_security_agent_request_validates_operation() -> None:
    with pytest.raises(TemporalValidationError, match="operation must be one of"):
        SecurityAgentRequest(agent_id="a", target="/x", operation="hack")


def test_security_agent_request_allowed_operations() -> None:
    for op in ("scan", "verify", "audit", "remediate"):
        req = SecurityAgentRequest(agent_id="a", target="/x", operation=op)
        assert req.operation == op


def test_security_agent_result_no_findings() -> None:
    res = SecurityAgentResult(agent_id="agent-1", success=True)
    assert res.agent_id == "agent-1"
    assert res.success is True
    assert res.findings == ()


def test_security_agent_result_with_findings() -> None:
    res = SecurityAgentResult(agent_id="a", success=True, findings=({"severity": "low"},))
    assert len(res.findings) == 1


def test_security_agent_result_validates_finding_type() -> None:
    with pytest.raises(TemporalValidationError, match="findings\\[0\\]"):
        SecurityAgentResult(
            agent_id="a",
            success=True,
            findings=("not a dict",),  # type: ignore[arg-type]
        )


def test_security_agent_result_rejects_success_with_error() -> None:
    with pytest.raises(TemporalValidationError, match="must not have error"):
        SecurityAgentResult(agent_id="a", success=True, error="oops")


# ---------------------------------------------------------------------------
# RetryPolicy
# ---------------------------------------------------------------------------


def test_retry_policy_defaults() -> None:
    p = RetryPolicy()
    assert p.max_attempts == 3
    assert p.initial_interval_ms == 100
    assert p.backoff_coefficient == 2.0
    assert p.max_interval_ms == 60_000


def test_retry_policy_validates_max_attempts() -> None:
    with pytest.raises(TemporalValidationError, match="max_attempts"):
        RetryPolicy(max_attempts=0)


def test_retry_policy_validates_backoff() -> None:
    with pytest.raises(TemporalValidationError, match="backoff_coefficient"):
        RetryPolicy(backoff_coefficient=0.5)


def test_retry_policy_validates_intervals() -> None:
    with pytest.raises(TemporalValidationError, match="initial_interval_ms"):
        RetryPolicy(initial_interval_ms=-1)
    with pytest.raises(TemporalValidationError, match="max_interval_ms"):
        RetryPolicy(max_interval_ms=-1)


# ---------------------------------------------------------------------------
# new_correlation_id
# ---------------------------------------------------------------------------


def test_new_correlation_id_is_uuid() -> None:
    cid = new_correlation_id()
    assert isinstance(cid, str)
    assert len(cid) == 36  # UUID4 format


def test_new_correlation_id_unique() -> None:
    ids = {new_correlation_id() for _ in range(100)}
    assert len(ids) == 100  # all unique


# ---------------------------------------------------------------------------
# run_triumvirate_pipeline
# ---------------------------------------------------------------------------


def test_run_triumvirate_pipeline_str_input() -> None:
    req = TriumvirateRequest(input_data="hello")
    res = run_triumvirate_pipeline(req)
    assert res.success is True
    assert res.correlation_id is not None
    assert res.duration_ms is not None
    assert res.duration_ms >= 0
    assert res.output is not None
    assert res.output["input_echo"] == "hello"
    assert res.output["pipeline_stages"] == [
        "ingest",
        "validate",
        "transform",
        "emit",
    ]


def test_run_triumvirate_pipeline_dict_input() -> None:
    req = TriumvirateRequest(input_data={"a": 1, "b": 2})
    res = run_triumvirate_pipeline(req)
    assert res.success is True
    assert res.output is not None
    assert res.output["input_keys"] == ["a", "b"]


def test_run_triumvirate_pipeline_with_context() -> None:
    req = TriumvirateRequest(input_data="x", context={"alpha": "v1", "beta": "v2"})
    res = run_triumvirate_pipeline(req)
    assert res.success is True
    assert res.output is not None
    assert res.output["context_keys"] == ["alpha", "beta"]


def test_run_triumvirate_pipeline_skip_validation() -> None:
    # With skip_validation, can pass a problematic request (but here input
    # must still be truthy). Just verify skip_validation flag works.
    req = TriumvirateRequest(input_data="ok", skip_validation=True)
    res = run_triumvirate_pipeline(req)
    assert res.success is True


# ---------------------------------------------------------------------------
# run_security_agent_scan
# ---------------------------------------------------------------------------


def test_run_security_agent_scan_no_findings(tmp_path) -> None:
    target = tmp_path / "safe.py"
    target.write_text("value = 1\n", encoding="utf-8")
    req = SecurityAgentRequest(agent_id="agent-1", target=str(target), operation="scan")
    res = run_security_agent_scan(req)
    assert isinstance(res, SecurityAgentResult)
    assert res.agent_id == "agent-1"
    assert res.success is True
    assert res.findings == ()


def test_run_security_agent_scan_unavailable_target_fails_closed() -> None:
    req = SecurityAgentRequest(agent_id="agent-1", target="/missing", operation="scan")
    res = run_security_agent_scan(req)
    assert res.success is False
    assert res.error == "scan did not complete: target_unavailable"


def test_run_security_agent_scan_invalid_request() -> None:
    with pytest.raises(ActivityError, match="must be SecurityAgentRequest"):
        run_security_agent_scan("not a request")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# run_activity wrapper
# ---------------------------------------------------------------------------


def test_run_activity_validates_callable() -> None:
    req = TriumvirateRequest(input_data="x")
    with pytest.raises(ActivityError, match="must be callable"):
        run_activity("not a function", req)  # type: ignore[arg-type]


def test_run_activity_validates_request_type() -> None:
    def my_activity(req: TriumvirateRequest) -> TriumvirateResult:
        return TriumvirateResult(success=True)

    with pytest.raises(ActivityError, match="must be TriumvirateRequest"):
        run_activity(my_activity, "not a request")  # type: ignore[arg-type]


def test_run_activity_returns_result() -> None:
    req = TriumvirateRequest(input_data="x")

    def my_activity(r: TriumvirateRequest) -> TriumvirateResult:
        return TriumvirateResult(success=True, output={"k": "v"})

    res = run_activity(my_activity, req)
    assert res.success is True
    assert res.output == {"k": "v"}


def test_run_activity_retries_on_activity_error() -> None:
    req = TriumvirateRequest(input_data="x", max_retries=3)
    attempts = {"n": 0}

    def flaky(r: TriumvirateRequest) -> TriumvirateResult:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ActivityError("flaky")
        return TriumvirateResult(success=True)

    res = run_activity(flaky, req, policy=RetryPolicy(max_attempts=5))
    assert res.success is True
    assert attempts["n"] == 3


def test_run_activity_exhausts_retries() -> None:
    req = TriumvirateRequest(input_data="x")

    def always_fails(r: TriumvirateRequest) -> TriumvirateResult:
        raise ActivityError("nope")

    with pytest.raises(ActivityError, match="nope"):
        run_activity(always_fails, req, policy=RetryPolicy(max_attempts=2))


def test_run_activity_default_policy_used_when_none() -> None:
    req = TriumvirateRequest(input_data="x")

    def my_activity(r: TriumvirateRequest) -> TriumvirateResult:
        return TriumvirateResult(success=True)

    res = run_activity(my_activity, req)  # no policy
    assert res.success is True


def test_run_activity_rejects_non_result_return() -> None:
    req = TriumvirateRequest(input_data="x")

    def bad_activity(r: TriumvirateRequest) -> object:
        return "not a TriumvirateResult"

    with pytest.raises(ActivityError, match="expected TriumvirateResult"):
        run_activity(bad_activity, req)  # type: ignore[arg-type]


def test_run_activity_timeout_override() -> None:
    req = TriumvirateRequest(input_data="x", timeout_seconds=10)

    def my_activity(r: TriumvirateRequest) -> TriumvirateResult:
        return TriumvirateResult(success=True)

    res = run_activity(my_activity, req, timeout_seconds=5)
    assert res.success is True


def test_run_activity_with_default_pipeline() -> None:
    """End-to-end: run_activity wraps run_triumvirate_pipeline."""
    req = TriumvirateRequest(input_data="end-to-end")
    res = run_activity(run_triumvirate_pipeline, req)
    assert res.success is True
    assert res.output is not None
    assert res.output["input_echo"] == "end-to-end"
