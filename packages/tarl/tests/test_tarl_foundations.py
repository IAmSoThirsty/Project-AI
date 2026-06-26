"""Unit tests for tarl foundations: spec, policy, core, diagnostics."""

from __future__ import annotations

import pytest

from tarl import (
    ALLOWED_VERDICTS,
    TARL,
    TARL_VERSION,
    DiagnosticBatch,
    Location,
    Severity,
    TarlDecision,
    TarlError,
    TarlPolicy,
    TarlVerdict,
    allow_policy,
    deny_policy,
    make_decision,
    make_diagnostic,
    make_tarl,
)

# ---------------------------------------------------------------------------
# spec: TarlDecision + TarlVerdict
# ---------------------------------------------------------------------------


def test_tarl_decision_frozen() -> None:
    d = make_decision(verdict="allow", reason="ok")
    with pytest.raises((AttributeError, Exception)):  # frozen raises on set
        d.verdict = TarlVerdict.DENY  # type: ignore[misc]


def test_tarl_decision_is_terminal_for_deny() -> None:
    d = make_decision(verdict="deny", reason="bad")
    assert d.is_terminal() is True
    assert d.is_deny() is True
    assert d.is_allow() is False


def test_tarl_decision_is_terminal_for_escalate() -> None:
    d = make_decision(verdict="escalate", reason="human")
    assert d.is_terminal() is True
    assert d.is_escalate() is True


def test_tarl_decision_allow_is_not_terminal() -> None:
    d = make_decision(verdict="allow", reason="ok")
    assert d.is_terminal() is False
    assert d.is_allow() is True


def test_make_decision_accepts_enum_or_string() -> None:
    d1 = make_decision(verdict=TarlVerdict.ALLOW, reason="x")
    d2 = make_decision(verdict="allow", reason="x")
    assert d1.verdict is d2.verdict is TarlVerdict.ALLOW


def test_make_decision_rejects_unknown_verdict_string() -> None:
    with pytest.raises(TarlError, match="verdict"):
        make_decision(verdict="maybe", reason="x")


def test_make_decision_rejects_empty_reason() -> None:
    with pytest.raises(TarlError, match="reason"):
        make_decision(verdict="allow", reason="")


def test_make_decision_rejects_non_dict_metadata() -> None:
    with pytest.raises(TarlError, match="metadata"):
        make_decision(verdict="allow", reason="x", metadata="not a dict")  # type: ignore[arg-type]


def test_allowed_verdicts_includes_required_set() -> None:
    for v in ("allow", "deny", "escalate"):
        assert v in ALLOWED_VERDICTS


# ---------------------------------------------------------------------------
# policy: TarlPolicy
# ---------------------------------------------------------------------------


def test_policy_constructs_with_valid_inputs() -> None:
    p = TarlPolicy("allow-all", lambda _ctx: make_decision(verdict="allow", reason="x"))
    assert p.name == "allow-all"


def test_policy_rejects_empty_name() -> None:
    with pytest.raises(TarlError, match="name"):
        TarlPolicy("", lambda _ctx: make_decision(verdict="allow", reason="x"))


def test_policy_rejects_non_callable_rule() -> None:
    with pytest.raises(TarlError, match="callable"):
        TarlPolicy("bad", "not-callable")  # type: ignore[arg-type]


def test_policy_evaluate_returns_decision() -> None:
    p = TarlPolicy("p", lambda _ctx: make_decision(verdict="deny", reason="x"))
    result = p.evaluate({"k": "v"})
    assert result.verdict is TarlVerdict.DENY


def test_policy_evaluate_rejects_non_dict_context() -> None:
    p = TarlPolicy("p", lambda _ctx: make_decision(verdict="allow", reason="x"))
    with pytest.raises(TarlError, match="context"):
        p.evaluate("not a dict")  # type: ignore[arg-type]


def test_policy_evaluate_wraps_rule_exception() -> None:
    def bad_rule(_ctx: dict[str, object]) -> TarlDecision:
        raise ValueError("nope")

    p = TarlPolicy("bad", bad_rule)
    with pytest.raises(TarlError, match="raised"):
        p.evaluate({})


def test_policy_evaluate_rejects_non_decision_return() -> None:
    def bad_rule(_ctx: dict[str, object]) -> object:
        return "not a decision"

    p = TarlPolicy("bad", bad_rule)  # type: ignore[arg-type]
    with pytest.raises(TarlError, match="non-TarlDecision"):
        p.evaluate({})


def test_allow_policy_always_allows() -> None:
    p = allow_policy("default")
    result = p.evaluate({"any": "context"})
    assert result.verdict is TarlVerdict.ALLOW


def test_deny_policy_always_denies() -> None:
    p = deny_policy("block", reason="not allowed")
    result = p.evaluate({"any": "context"})
    assert result.verdict is TarlVerdict.DENY
    assert result.reason == "not allowed"


# ---------------------------------------------------------------------------
# core: TARL + make_tarl
# ---------------------------------------------------------------------------


def test_tarl_version_constant() -> None:
    assert TARL_VERSION == "2.0"


def test_make_tarl_validates_inputs() -> None:
    t = make_tarl(
        intent="read",
        scope="files",
        authority="cap-1",
        constraints=("read-only",),
    )
    assert isinstance(t, TARL)
    assert t.intent == "read"
    assert t.constraints == ("read-only",)


def test_make_tarl_accepts_list_constraints() -> None:
    t = make_tarl(
        intent="read",
        scope="files",
        authority="cap-1",
        constraints=["read-only", "no-network"],
    )
    assert isinstance(t.constraints, tuple)
    assert t.constraints == ("read-only", "no-network")


def test_make_tarl_rejects_empty_intent() -> None:
    with pytest.raises(ValueError, match="intent"):
        make_tarl(intent="", scope="x", authority="x")


def test_make_tarl_rejects_non_str_constraint() -> None:
    with pytest.raises(ValueError, match="constraint"):
        make_tarl(intent="x", scope="x", authority="x", constraints=(42,))  # type: ignore[arg-type]


def test_tarl_canonical_sorts_constraints() -> None:
    t = make_tarl(
        intent="x",
        scope="x",
        authority="x",
        constraints=("z", "a", "m"),
    )
    canonical = t.canonical()
    assert canonical["constraints"] == ["a", "m", "z"]


def test_tarl_hash_is_deterministic_regardless_of_input_order() -> None:
    t1 = make_tarl(
        intent="x",
        scope="x",
        authority="x",
        constraints=("a", "b", "c"),
    )
    t2 = make_tarl(
        intent="x",
        scope="x",
        authority="x",
        constraints=("c", "b", "a"),
    )
    assert t1.hash() == t2.hash()


def test_tarl_hash_is_sha256_hex() -> None:
    import re

    t = make_tarl(intent="x", scope="x", authority="x")
    assert re.fullmatch(r"[0-9a-f]{64}", t.hash())


# ---------------------------------------------------------------------------
# diagnostics: Diagnostic + DiagnosticBatch
# ---------------------------------------------------------------------------


def test_make_diagnostic_accepts_enum_or_string() -> None:
    d1 = make_diagnostic(severity=Severity.ERROR, message="x")
    d2 = make_diagnostic(severity="error", message="x")
    assert d1.severity is d2.severity is Severity.ERROR


def test_make_diagnostic_rejects_unknown_severity() -> None:
    with pytest.raises(ValueError, match="severity"):
        make_diagnostic(severity="fatal", message="x")


def test_make_diagnostic_rejects_empty_message() -> None:
    with pytest.raises(ValueError, match="message"):
        make_diagnostic(severity=Severity.ERROR, message="")


def test_diagnostic_batch_aggregates() -> None:
    batch = DiagnosticBatch()
    batch.add(make_diagnostic(severity="error", message="e1"))
    batch.add(make_diagnostic(severity="warning", message="w1"))
    batch.add(make_diagnostic(severity="info", message="i1"))
    assert len(batch.diagnostics) == 3
    assert batch.has_errors is True
    assert len(batch.errors) == 1
    assert len(batch.warnings) == 1


def test_diagnostic_batch_without_errors() -> None:
    batch = DiagnosticBatch()
    batch.add(make_diagnostic(severity="warning", message="w1"))
    assert batch.has_errors is False


def test_diagnostic_batch_rejects_non_diagnostic() -> None:
    batch = DiagnosticBatch()
    with pytest.raises(TypeError):
        batch.add("not a diagnostic")  # type: ignore[arg-type]


def test_diagnostic_with_location() -> None:
    loc = Location(file="x.py", line=10, column=5)
    d = make_diagnostic(
        severity=Severity.ERROR,
        message="bad",
        code="E001",
        location=loc,
    )
    assert d.location is loc
    assert d.location and d.location.file == "x.py"


def test_diagnostic_batch_to_json() -> None:
    loc = Location(file="x.py", line=10)
    batch = DiagnosticBatch()
    batch.add(make_diagnostic(severity="error", message="e", code="E1", location=loc))
    batch.add(make_diagnostic(severity="warning", message="w"))
    result = batch.to_json()
    assert len(result) == 2
    assert result[0]["severity"] == "error"
    assert result[0]["code"] == "E1"
    assert result[0]["location"]["file"] == "x.py"
    assert result[1]["severity"] == "warning"
    assert "code" not in result[1]  # no code set


def test_severity_includes_required_levels() -> None:
    for s in ("error", "warning", "info", "hint"):
        assert s in {sv.value for sv in Severity}
