"""Unit tests for tarl.parser, tarl.validate, tarl.compiler, tarl.runtime, tarl.config."""

from __future__ import annotations

import pytest
from tarl.compiler import CompiledTarl

from tarl import (
    DEFAULT_ALLOWED_AUTHORITIES,
    TARL,
    TarlCompileError,
    TarlConfig,
    TarlConfigError,
    TarlParseError,
    TarlPolicy,
    TarlRuntime,
    TarlRuntimeError,
    TarlVerdict,
    allow_policy,
    allowed_authorities,
    compile_record,
    config_from_mapping,
    default_compile_policy,
    deny_policy,
    format_tarl,
    is_valid,
    make_config,
    make_tarl,
    parse,
    parse_mapping,
    validate,
    validate_with_authorities,
)

# ---------------------------------------------------------------------------
# parser.parse
# ---------------------------------------------------------------------------


def test_parse_minimal() -> None:
    record = parse("INTENT: read\nSCOPE: /var/log\nAUTHORITY: cap-1\n")
    assert record.intent == "read"
    assert record.scope == "/var/log"
    assert record.authority == "cap-1"
    assert record.constraints == ()


def test_parse_with_constraints() -> None:
    record = parse(
        "INTENT: delete\n"
        "SCOPE: /tmp\n"
        "AUTHORITY: cap-1\n"
        "CONSTRAINTS:\n"
        "  - read-only\n"
        "  - no-network\n"
    )
    assert record.constraints == ("read-only", "no-network")


def test_parse_with_version() -> None:
    record = parse("INTENT: x\nSCOPE: x\nAUTHORITY: x\nVERSION: 2.0\n")
    assert record.version == "2.0"


def test_parse_rejects_non_string() -> None:
    with pytest.raises(TarlParseError, match="text"):
        parse(123)  # type: ignore[arg-type]


def test_parse_rejects_missing_required_key() -> None:
    with pytest.raises(TarlParseError, match="intent"):
        parse("SCOPE: x\nAUTHORITY: x\n")


def test_parse_rejects_unknown_key() -> None:
    with pytest.raises(TarlParseError, match="unknown key"):
        parse("INTENT: x\nSCOPE: x\nAUTHORITY: x\nFOO: bar\n")


def test_parse_rejects_empty_value() -> None:
    with pytest.raises(TarlParseError, match="empty value"):
        parse("INTENT: \nSCOPE: x\nAUTHORITY: x\n")


def test_parse_rejects_empty_constraint() -> None:
    with pytest.raises(TarlParseError, match="empty constraint"):
        parse("INTENT: x\nSCOPE: x\nAUTHORITY: x\nCONSTRAINTS:\n  - \n")


def test_parse_rejects_unsupported_section() -> None:
    with pytest.raises(TarlParseError, match="unsupported section"):
        parse("INTENT: x\nSCOPE: x\nAUTHORITY: x\nRANDOM:\n  - foo\n")


def test_parse_rejects_missing_colon() -> None:
    with pytest.raises(TarlParseError, match="missing colon"):
        parse("INTENT: x\nSCOPE: x\nAUTHORITY just text\n")


def test_format_round_trip() -> None:
    record = make_tarl(
        intent="read",
        scope="/var/log",
        authority="cap-1",
        constraints=("read-only",),
    )
    text = format_tarl(record)
    parsed = parse(text)
    assert parsed.canonical() == record.canonical()


def test_parse_mapping_validates() -> None:
    record = parse_mapping({"intent": "x", "scope": "y", "authority": "z"})
    assert record.intent == "x"
    assert record.authority == "z"


def test_parse_mapping_rejects_non_str_intent() -> None:
    with pytest.raises(TarlParseError, match="intent"):
        parse_mapping({"intent": 42, "scope": "y", "authority": "z"})


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------


def test_validate_valid_record() -> None:
    record = make_tarl(
        intent="x",
        scope="x",
        authority="system",
    )
    batch = validate(record)
    assert not batch.has_errors


def test_validate_rejects_unknown_authority() -> None:
    record = make_tarl(intent="x", scope="x", authority="evil")
    batch = validate(record)
    assert batch.has_errors
    assert any("authority" in d.message for d in batch.errors)


def test_validate_with_explicit_authorities() -> None:
    record = make_tarl(intent="x", scope="x", authority="custom")
    batch = validate_with_authorities(record, ["custom"])
    assert not batch.has_errors


def test_is_valid_helper() -> None:
    record = make_tarl(intent="x", scope="x", authority="system")
    assert is_valid(record) is True


def test_validate_detects_empty_intent() -> None:
    # Construct raw TARL bypassing make_tarl (which would reject empty).
    record = TARL(intent="", scope="x", authority="x", constraints=())
    batch = validate(record)
    assert batch.has_errors
    assert any("intent" in d.message for d in batch.errors)


def test_validate_detects_empty_constraint() -> None:
    record = make_tarl(intent="x", scope="x", authority="x", constraints=("",))
    batch = validate(record)
    assert batch.has_errors


def test_default_allowed_authorities_includes_legacy() -> None:
    for auth in ("Cerberus", "CodexDeus"):
        assert auth in DEFAULT_ALLOWED_AUTHORITIES


def test_allowed_authorities_with_extras() -> None:
    extras = allowed_authorities(
        make_tarl(intent="x", scope="x", authority="x"),
        extras=("custom-1", "custom-2"),
    )
    assert "custom-1" in extras
    assert "custom-2" in extras
    assert "Cerberus" in extras  # default still present


# ---------------------------------------------------------------------------
# compiler
# ---------------------------------------------------------------------------


def test_compile_record_valid() -> None:
    record = make_tarl(intent="x", scope="x", authority="system")
    policy = allow_policy("default")
    compiled = compile_record(record, policy)
    assert isinstance(compiled, CompiledTarl)
    assert compiled.policy_name == "default"
    assert compiled.record_hash == record.hash()


def test_compile_record_rejects_invalid_authority() -> None:
    record = make_tarl(intent="x", scope="x", authority="evil")
    policy = allow_policy("default")
    with pytest.raises(TarlCompileError, match="validation"):
        compile_record(record, policy)


def test_compile_record_rejects_non_tarl() -> None:
    with pytest.raises(TarlCompileError, match="record"):
        compile_record("not a TARL", allow_policy("default"))  # type: ignore[arg-type]


def test_compile_record_rejects_non_policy() -> None:
    record = make_tarl(intent="x", scope="x", authority="system")
    with pytest.raises(TarlCompileError, match="policy"):
        compile_record(record, "not a policy")  # type: ignore[arg-type]


def test_compiled_canonical_is_json_serializable() -> None:
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, allow_policy("default"))
    canonical = compiled.canonical
    assert "record" in canonical
    assert "policy_name" in canonical
    assert canonical["policy_name"] == "default"


def test_default_compile_policy_returns_compiler() -> None:
    c = default_compile_policy()
    assert c is not None
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = c.compile(record, allow_policy("default"))
    assert compiled.record_hash == record.hash()


# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------


def test_runtime_execute_compiled() -> None:
    runtime = TarlRuntime()
    record = make_tarl(intent="x", scope="x", authority="system")
    policy = allow_policy("default")
    runtime.add_policy(policy)
    compiled = compile_record(record, policy)
    decision = runtime.execute(compiled, {"any": "context"})
    assert decision.verdict is TarlVerdict.ALLOW
    assert len(runtime.audit_log) == 1


def test_runtime_rejects_non_compiled() -> None:
    runtime = TarlRuntime()
    with pytest.raises(TarlRuntimeError, match="compiled"):
        runtime.execute("not compiled", {})  # type: ignore[arg-type]


def test_runtime_rejects_non_mapping_context() -> None:
    runtime = TarlRuntime()
    runtime.add_policy(allow_policy("default"))
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, allow_policy("default"))
    with pytest.raises(TarlRuntimeError, match="context"):
        runtime.execute(compiled, "not mapping")  # type: ignore[arg-type]


def test_runtime_detects_missing_policy() -> None:
    runtime = TarlRuntime()
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, allow_policy("never-registered"))
    with pytest.raises(TarlRuntimeError, match="no policy registered"):
        runtime.execute(compiled, {})


def test_runtime_caches_repeated_evaluations() -> None:
    runtime = TarlRuntime()
    policy = allow_policy("default")
    runtime.add_policy(policy)
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, policy)
    ctx = {"k": "v"}
    d1 = runtime.execute(compiled, ctx)
    d2 = runtime.execute(compiled, ctx)
    assert d1 is d2
    assert len(runtime.cache) == 1
    # Audit log only records first execution
    assert len(runtime.audit_log) == 1


def test_runtime_audit_records_capture_metadata() -> None:
    runtime = TarlRuntime()
    policy = deny_policy("block", reason="explicit")
    runtime.add_policy(policy)
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, policy)
    decision = runtime.execute(compiled, {"any": "ctx"})
    assert decision.verdict is TarlVerdict.DENY
    audit = runtime.audit_log[0]
    assert audit.verdict is TarlVerdict.DENY
    assert audit.policy_name == "block"
    assert audit.reason == "explicit"
    assert audit.compiled_hash == record.hash()


def test_runtime_detects_tampered_record() -> None:
    """Runtime detects when CompiledTarl.record_hash no longer matches record.hash().

    Simulates tampering by constructing a CompiledTarl whose record_hash
    was computed from a DIFFERENT record than the one stored.
    """
    runtime = TarlRuntime()
    policy = allow_policy("default")
    runtime.add_policy(policy)
    original_record = make_tarl(intent="x", scope="x", authority="system")
    compile_record(original_record, policy)
    # Build a tampered compiled record: keep the original record but lie
    # about the hash.
    tampered = CompiledTarl(
        record=original_record,
        policy_name=policy.name,
        record_hash="tampered-hash",
    )
    with pytest.raises(TarlRuntimeError, match="hash mismatch"):
        runtime.execute(tampered, {})


def test_runtime_add_policy_validates() -> None:
    runtime = TarlRuntime()
    with pytest.raises(TarlRuntimeError, match="policy"):
        runtime.add_policy("not a policy")  # type: ignore[arg-type]


def test_runtime_execute_chain_returns_all_decisions() -> None:
    runtime = TarlRuntime()
    allow_pol = allow_policy("allow")
    deny_pol = deny_policy("deny")
    runtime.add_policy(allow_pol)
    runtime.add_policy(deny_pol)
    rec1 = make_tarl(intent="x", scope="x", authority="system")
    rec2 = make_tarl(intent="y", scope="y", authority="system")
    compiled_list = [
        compile_record(rec1, allow_pol),
        compile_record(rec2, deny_pol),
    ]
    # Use distinct contexts so the cache doesn't conflate them.
    decisions = runtime.execute_chain(compiled_list, {"v": 1})
    # Second call should also use distinct context to avoid cache hits.
    decisions_b = runtime.execute_chain([compiled_list[0], compiled_list[1]], {"v": 2})
    assert len(decisions) == 2
    assert decisions[0].verdict is TarlVerdict.ALLOW
    assert decisions[1].verdict is TarlVerdict.DENY
    assert len(decisions_b) == 2
    assert decisions_b[0].verdict is TarlVerdict.ALLOW
    assert decisions_b[1].verdict is TarlVerdict.DENY


def test_runtime_clear_cache() -> None:
    runtime = TarlRuntime()
    policy = allow_policy("default")
    runtime.add_policy(policy)
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = compile_record(record, policy)
    runtime.execute(compiled, {})
    assert len(runtime.cache) == 1
    runtime.clear_cache()
    assert len(runtime.cache) == 0


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------


def test_make_config_defaults() -> None:
    cfg = make_config()
    assert isinstance(cfg, TarlConfig)
    assert cfg.cache_size == 128
    assert cfg.audit_enabled is True


def test_make_config_rejects_negative_cache_size() -> None:
    with pytest.raises(TarlConfigError, match="cache_size"):
        make_config(cache_size=-1)


def test_make_config_rejects_negative_audit_max() -> None:
    with pytest.raises(TarlConfigError, match="audit_max"):
        make_config(audit_max_records=-1)


def test_make_config_rejects_negative_timeout() -> None:
    with pytest.raises(TarlConfigError, match="policy_timeout"):
        make_config(policy_timeout_ms=-1)


def test_make_config_rejects_non_bool_audit() -> None:
    with pytest.raises(TarlConfigError, match="audit_enabled"):
        make_config(audit_enabled="yes")  # type: ignore[arg-type]


def test_make_config_rejects_bool_as_int() -> None:
    with pytest.raises(TarlConfigError, match="cache_size"):
        make_config(cache_size=True)


def test_config_canonical_is_dict() -> None:
    cfg = make_config()
    canonical = cfg.canonical
    assert canonical["cache_size"] == 128
    assert canonical["audit_enabled"] is True


def test_config_from_mapping_validates_keys() -> None:
    with pytest.raises(TarlConfigError, match="unknown config key"):
        config_from_mapping({"unknown_key": 1})


def test_config_from_mapping_validates_values() -> None:
    with pytest.raises(TarlConfigError):
        config_from_mapping({"cache_size": -1})


def test_config_from_mapping_uses_defaults() -> None:
    cfg = config_from_mapping({})
    assert cfg.cache_size == 128


# ---------------------------------------------------------------------------
# Compiler protocol + structural conformance
# ---------------------------------------------------------------------------


def test_compiler_protocol_structural_conformance() -> None:
    """A class implementing compile(record, policy) satisfies Compiler Protocol."""

    class MyCompiler:
        def compile(self, record: TARL, policy: TarlPolicy) -> CompiledTarl:
            return CompiledTarl(
                record=record,
                policy_name=policy.name,
                record_hash=record.hash(),
                compiled_at="custom/v1",
            )

    c: object = MyCompiler()
    record = make_tarl(intent="x", scope="x", authority="system")
    compiled = c.compile(record, allow_policy("default"))  # type: ignore[attr-defined]
    assert compiled.compiled_at == "custom/v1"
